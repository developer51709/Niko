"""TLS CONNECT proxy service used by a standby Niko deployment.

A standby logs in and preloads the production bot and cogs but holds its Discord
gateway closed until a signed handoff command activates it. It also serves
authenticated CONNECT tunnels for Discord hosts.
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import ipaddress
import json
import os
import ssl
import time
from urllib.parse import urlsplit

_STATS = {"started_at": time.time(), "total_tunnels": 0, "active_tunnels": 0, "bytes_in": 0, "bytes_out": 0}
_CONTROL_NONCES: set[str] = set()
_MAX_CONTROL_NONCES = 2048
_GATEWAY_CONTROLLER = None
_CONTROL_LOCK = asyncio.Lock()

_ALLOWED_SUFFIXES = (".discord.com", ".discordapp.com", ".discord.gg", ".discord.media", ".discordapp.net")
_ALLOWED_EXACT = {"discord.com", "discordapp.com", "discord.gg", "discord.media", "discordapp.net"}
_MAX_HEADERS = 16 * 1024


def secret_key(bot_token: str, session_secret: str) -> bytes:
    return hashlib.sha256(bot_token.encode() + b"\0" + session_secret.encode()).digest()


def verification_proof(key: bytes, nonce: str) -> str:
    return hmac.new(key, b"niko-backup-verification:" + nonce.encode(), hashlib.sha256).hexdigest()


def proxy_password(key: bytes) -> str:
    return hmac.new(key, b"niko-backup-proxy", hashlib.sha256).hexdigest()


def control_proof(key: bytes, action: str, nonce: str) -> str:
    """Sign one gateway ownership command."""
    return hmac.new(key, f"niko-backup-control:{action}:{nonce}".encode(), hashlib.sha256).hexdigest()


def backup_proxy_url(base_url: str, key: bytes) -> str:
    parts = urlsplit(base_url.rstrip("/"))
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
        raise ValueError("Backup URL must be an HTTPS origin without embedded credentials.")
    if parts.path not in ("", "/") or parts.query or parts.fragment:
        raise ValueError("Backup URL must be an HTTPS origin without a path, query, or fragment.")
    return f"https://niko-backup:{proxy_password(key)}@{parts.netloc}"


def _allowed_host(authority: str) -> tuple[str, int] | None:
    host, separator, port = authority.rpartition(":")
    if not separator or not port.isdigit():
        return None
    host = host.strip("[]").lower().rstrip(".")
    try:
        ipaddress.ip_address(host)
        return None
    except ValueError:
        pass
    if host not in _ALLOWED_EXACT and not any(host.endswith(suffix) for suffix in _ALLOWED_SUFFIXES):
        return None
    port_number = int(port)
    if port_number != 443:
        return None
    return host, port_number


async def _write_response(writer: asyncio.StreamWriter, status: int, body: dict) -> None:
    payload = json.dumps(body, separators=(",", ":")).encode()
    writer.write(
        f"HTTP/1.1 {status} {'OK' if status == 200 else 'Error'}\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(payload)}\r\nConnection: close\r\n\r\n".encode()
        + payload
    )
    await writer.drain()


async def _pipe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, byte_counter: str) -> None:
    try:
        while chunk := await reader.read(64 * 1024):
            _STATS[byte_counter] += len(chunk)
            writer.write(chunk)
            await writer.drain()
    except (ConnectionError, asyncio.CancelledError):
        pass
    finally:
        try:
            writer.write_eof()
        except (AttributeError, OSError, RuntimeError):
            pass


def _dispatch_web_request(web_app, method: str, target: str, headers: dict, body: bytes) -> bytes:
    """Dispatch one ordinary HTTP request to Flask and serialize its response."""
    from werkzeug.test import EnvironBuilder, run_wsgi_app

    host = headers.get("host", "localhost")
    scheme = "https" if headers.get("x-forwarded-proto", "").split(",", 1)[0].strip() == "https" else "http"
    forwarded_headers = {
        name: value for name, value in headers.items()
        if name.lower() not in {"host", "connection", "proxy-authorization", "proxy-connection", "content-length", "transfer-encoding"}
    }
    builder = EnvironBuilder(
        path=target,
        method=method,
        base_url=f"{scheme}://{host}",
        headers=forwarded_headers,
        data=body,
    )
    environ = builder.get_environ()
    app_iter, status, response_headers = run_wsgi_app(web_app, environ, buffered=True)
    payload = b"".join(app_iter)
    builder.close()

    status_code = int(status.split(" ", 1)[0])
    reason = status.partition(" ")[2] or "Unknown"
    serialized_headers = [
        (name, value) for name, value in response_headers
        if name.lower() not in {"connection", "content-length", "transfer-encoding"}
    ]
    serialized_headers.extend([
        ("Content-Length", str(len(payload))),
        ("Connection", "close"),
    ])
    response = bytearray(f"HTTP/1.1 {status_code} {reason}\r\n".encode("latin-1"))
    for name, value in serialized_headers:
        response.extend(f"{name}: {value}\r\n".encode("latin-1"))
    response.extend(b"\r\n")
    response.extend(payload)
    return bytes(response)


async def _handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    key: bytes,
    web_app=None,
) -> None:
    upstream_writer = None

    try:
        raw = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout=10)
        if len(raw) > _MAX_HEADERS:
            await _write_response(writer, 400, {"error": "Headers too large."})
            return
        lines = raw.decode("latin-1").split("\r\n")
        request_line = lines[0].split()
        if len(request_line) != 3:
            await _write_response(writer, 400, {"error": "Invalid request."})
            return
        method, target, _version = request_line
        headers = {}
        for line in lines[1:]:
            if ":" in line:
                name, value = line.split(":", 1)
                headers[name.strip().lower()] = value.strip()

        if method == "GET" and target == "/health":
            await _write_response(writer, 200, {
                "ok": True,
                "service": "niko-backup-proxy",
                "uptime_seconds": max(0, int(time.time() - _STATS["started_at"])),
                "total_tunnels": _STATS["total_tunnels"],
                "active_tunnels": _STATS["active_tunnels"],
                "bytes_in": _STATS["bytes_in"],
                "bytes_out": _STATS["bytes_out"],
            })
            return

        if method == "POST" and target == "/internal/backup/control":
            try:
                length = int(headers.get("content-length", "0"))
                if not 0 < length <= 1024:
                    raise ValueError
                body = json.loads(await asyncio.wait_for(reader.readexactly(length), timeout=3))
                action, nonce, proof = body.get("action"), body.get("nonce"), body.get("proof")
                if action not in {"activate", "relinquish"}:
                    raise ValueError
                if not isinstance(nonce, str) or not 32 <= len(nonce) <= 128:
                    raise ValueError
                expected = control_proof(key, action, nonce)
                if not isinstance(proof, str) or not hmac.compare_digest(proof, expected):
                    await _write_response(writer, 403, {"error": "Invalid control proof."})
                    return
            except (ValueError, TypeError, json.JSONDecodeError, asyncio.IncompleteReadError):
                await _write_response(writer, 400, {"error": "Invalid control request."})
                return
            controller = _GATEWAY_CONTROLLER
            if controller is None:
                await _write_response(writer, 503, {"error": "Standby gateway is not ready."})
                return
            async with _CONTROL_LOCK:
                if nonce in _CONTROL_NONCES:
                    await _write_response(writer, 403, {"error": "Control request was already used."})
                    return
                try:
                    if action == "activate":
                        await controller.activate()
                    else:
                        await controller.relinquish()
                except Exception:
                    await _write_response(writer, 503, {"error": "Gateway handoff failed."})
                    return
                _CONTROL_NONCES.add(nonce)
                if len(_CONTROL_NONCES) > _MAX_CONTROL_NONCES:
                    _CONTROL_NONCES.clear()
                    _CONTROL_NONCES.add(nonce)
            await _write_response(writer, 200, {"ok": True, "gateway": "active" if action == "activate" else "standby"})
            return

        if method == "POST" and target == "/internal/backup/verify":
            try:
                length = int(headers.get("content-length", "0"))
                if not 0 < length <= 512:
                    raise ValueError
                body = json.loads(await asyncio.wait_for(reader.readexactly(length), timeout=3))
                nonce = body.get("nonce")
                if not isinstance(nonce, str) or not 32 <= len(nonce) <= 128:
                    raise ValueError
            except (ValueError, TypeError, json.JSONDecodeError, asyncio.IncompleteReadError):
                await _write_response(writer, 400, {"error": "Invalid challenge."})
                return
            await _write_response(writer, 200, {"proof": verification_proof(key, nonce)})
            return

        if method != "CONNECT":
            if web_app is None:
                await _write_response(writer, 404, {"error": "Not found."})
                return
            if not target.startswith("/") or target.startswith("//") or "transfer-encoding" in headers:
                await _write_response(writer, 400, {"error": "Invalid HTTP request."})
                return
            try:
                content_length = int(headers.get("content-length", "0"))
                if content_length < 0 or content_length > 8 * 1024 * 1024:
                    raise ValueError
                body = await asyncio.wait_for(reader.readexactly(content_length), timeout=10) if content_length else b""
            except (ValueError, asyncio.IncompleteReadError, asyncio.TimeoutError):
                await _write_response(writer, 400, {"error": "Invalid HTTP request body."})
                return
            response = await asyncio.to_thread(
                _dispatch_web_request, web_app, method, target, headers, body
            )
            writer.write(response)
            await writer.drain()
            return
        auth = headers.get("proxy-authorization", "")

        try:
            scheme, encoded = auth.split(" ", 1)
            credentials = base64.b64decode(encoded, validate=True).decode()
            username, password = credentials.split(":", 1)
        except (ValueError, UnicodeDecodeError):
            username, password, scheme = "", "", ""
        if scheme.lower() != "basic" or username != "niko-backup" or not hmac.compare_digest(password, proxy_password(key)):
            writer.write(b"HTTP/1.1 407 Proxy Authentication Required\r\nProxy-Authenticate: Basic realm=\"Niko backup\"\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
            await writer.drain()
            return
        destination = _allowed_host(target)
        if destination is None:
            await _write_response(writer, 403, {"error": "CONNECT is restricted to Discord TLS endpoints."})
            return
        try:
            upstream_reader, upstream_writer = await asyncio.wait_for(
                asyncio.open_connection(*destination), timeout=8
            )
        except (OSError, asyncio.TimeoutError):
            await _write_response(writer, 502, {"error": "Discord endpoint is unavailable."})
            return
        writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        await writer.drain()
        _STATS["total_tunnels"] += 1
        _STATS["active_tunnels"] += 1
        try:
            await asyncio.gather(_pipe(reader, upstream_writer, "bytes_in"), _pipe(upstream_reader, writer, "bytes_out"))
        finally:
            _STATS["active_tunnels"] = max(0, _STATS["active_tunnels"] - 1)
    except (asyncio.IncompleteReadError, asyncio.LimitOverrunError, UnicodeError, asyncio.TimeoutError, ConnectionError):
        pass
    finally:
        if upstream_writer is not None:
            upstream_writer.close()
            try:
                await upstream_writer.wait_closed()
            except (ConnectionError, OSError):
                pass
        writer.close()
        try:
            await writer.wait_closed()
        except (ConnectionError, OSError):
            pass


async def serve_backup_proxy(
    host: str,
    port: int,
    certfile: str | None,
    keyfile: str | None,
    bot_token: str,
    session_secret: str,
    gateway_controller=None,
    web_app=None,
):
    """Bind a CONNECT proxy; Render terminates TLS when no cert is configured."""
    if not bot_token or not session_secret:
        raise RuntimeError("BACKUP_MODE requires the production DISCORD_BOT_TOKEN and SESSION_SECRET.")
    if bool(certfile) != bool(keyfile):
        raise RuntimeError("Configure both BACKUP_TLS_CERT and BACKUP_TLS_KEY, or neither when Render terminates HTTPS.")
    context = None
    if certfile and keyfile:
        if not os.path.isfile(certfile) or not os.path.isfile(keyfile):
            raise RuntimeError("Configured BACKUP_TLS_CERT and BACKUP_TLS_KEY files must exist.")
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    key = secret_key(bot_token, session_secret)
    global _GATEWAY_CONTROLLER
    _GATEWAY_CONTROLLER = gateway_controller
    server = await asyncio.start_server(
        lambda r, w: _handle_client(r, w, key, web_app=web_app), host, port, ssl=context,
        limit=_MAX_HEADERS + 1,
    )
    return server
