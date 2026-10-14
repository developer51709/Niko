"""HTTPS API relay and gateway-control listener for warm standby backend instances."""
from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import os
import ssl
import time
from urllib.parse import urlsplit

_STATS = {"started_at": time.time(), "total_api_requests": 0, "failed_api_requests": 0}
_RELAY_NONCES: set[str] = set()
_MAX_RELAY_NONCES = 4096
_MAX_RELAY_BODY = 8 * 1024 * 1024
_MAX_RELAY_PAYLOAD = 12 * 1024 * 1024
_DISCORD_API_ORIGIN = "https://discord.com/api/v10/"
_CONTROL_NONCES: set[str] = set()
_MAX_CONTROL_NONCES = 2048
_GATEWAY_CONTROLLER = None
_CONTROL_LOCK = asyncio.Lock()

_MAX_HEADERS = 16 * 1024


def secret_key(bot_token: str, session_secret: str) -> bytes:
    return hashlib.sha256(bot_token.encode() + b"\0" + session_secret.encode()).digest()


def verification_proof(key: bytes, nonce: str) -> str:
    return hmac.new(key, b"niko-standby-verification:" + nonce.encode(), hashlib.sha256).hexdigest()


def relay_proof(key: bytes, timestamp: str, nonce: str, method: str, url: str, headers: dict, body: bytes) -> str:
    """Authenticate the complete outbound Discord API request."""
    canonical = json.dumps(
        [timestamp, nonce, method.upper(), url, sorted(headers.items()), hashlib.sha256(body).hexdigest()],
        separators=(",", ":"),
    ).encode()
    return hmac.new(key, b"niko-standby-api-relay:" + canonical, hashlib.sha256).hexdigest()


async def _read_limited_body(reader: asyncio.StreamReader, headers: dict, maximum: int) -> bytes:
    try:
        length = int(headers.get("content-length", "0"))
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid content length.") from exc
    if length < 0 or length > maximum or "transfer-encoding" in headers:
        raise ValueError("Invalid request body size.")
    return await asyncio.wait_for(reader.readexactly(length), timeout=10) if length else b""


async def _relay_discord_request(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, headers: dict, key: bytes) -> None:
    """Validate and execute one signed REST request from the primary instance."""
    try:
        envelope = json.loads(await _read_limited_body(reader, headers, _MAX_RELAY_PAYLOAD))
        method, url = envelope.get("method"), envelope.get("url")
        request_headers, encoded_body = envelope.get("headers"), envelope.get("body", "")
        timestamp, nonce, proof = envelope.get("timestamp"), envelope.get("nonce"), envelope.get("proof")
        if not isinstance(method, str) or method.upper() not in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"}:
            raise ValueError
        if not isinstance(url, str) or not url.startswith(_DISCORD_API_ORIGIN) or "#" in url:
            raise ValueError
        if not isinstance(request_headers, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in request_headers.items()):
            raise ValueError
        if not isinstance(encoded_body, str) or len(encoded_body) > ((_MAX_RELAY_BODY + 2) // 3) * 4:
            raise ValueError
        request_body = base64.b64decode(encoded_body, validate=True) if encoded_body else b""
        if len(request_body) > _MAX_RELAY_BODY:
            raise ValueError
        if not isinstance(timestamp, str) or abs(int(time.time()) - int(timestamp)) > 60:
            raise ValueError
        if not isinstance(nonce, str) or not 32 <= len(nonce) <= 128:
            raise ValueError
        expected = relay_proof(key, timestamp, nonce, method, url, request_headers, request_body)
        if not isinstance(proof, str) or not hmac.compare_digest(proof, expected):
            await _write_response(writer, 403, {"error": "Invalid relay proof."})
            return
        if nonce in _RELAY_NONCES:
            await _write_response(writer, 403, {"error": "Relay request was already used."})
            return
        _RELAY_NONCES.add(nonce)
        if len(_RELAY_NONCES) > _MAX_RELAY_NONCES:
            _RELAY_NONCES.clear()
            _RELAY_NONCES.add(nonce)
    except (ValueError, TypeError, json.JSONDecodeError, asyncio.IncompleteReadError, asyncio.TimeoutError):
        await _write_response(writer, 400, {"error": "Invalid relay request."})
        return

    def forward():
        import requests
        safe_headers = {
            name: value for name, value in request_headers.items()
            if name.lower() not in {"host", "connection", "content-length", "transfer-encoding", "proxy-authorization", "proxy-connection"}
        }
        with requests.Session() as session:
            session.trust_env = False
            response = session.request(method.upper(), url, headers=safe_headers, data=request_body or None,
                                       timeout=(8, 25), allow_redirects=False)
        safe_response_headers = {
            name: value for name, value in response.headers.items()
            if name.lower() in {"content-type", "retry-after", "via", "date", "x-ratelimit-bucket",
                                "x-ratelimit-remaining", "x-ratelimit-reset", "x-ratelimit-reset-after",
                                "x-ratelimit-limit", "x-ratelimit-global", "x-ratelimit-scope", "cf-ray", "server"}
        }
        return {
            "status": response.status_code,
            "headers": safe_response_headers,
            "body": base64.b64encode(response.content).decode("ascii"),
        }

    try:
        result = await asyncio.to_thread(forward)
        _STATS["total_api_requests"] += 1
        await _write_response(writer, 200, result)
    except Exception:
        _STATS["failed_api_requests"] += 1
        await _write_response(writer, 502, {"error": "Discord API request failed."})



def control_proof(key: bytes, action: str, nonce: str) -> str:
    """Sign one gateway ownership command."""
    return hmac.new(key, f"niko-standby-control:{action}:{nonce}".encode(), hashlib.sha256).hexdigest()


def standby_origin(base_url: str) -> str:
    """Validate and return a public HTTPS origin for standby registration."""
    parts = urlsplit(base_url.rstrip("/"))
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
        raise ValueError("Standby URL must be an HTTPS origin without embedded credentials.")
    if parts.path not in ("", "/") or parts.query or parts.fragment:
        raise ValueError("Standby URL must be an HTTPS origin without a path, query, or fragment.")
    return f"https://{parts.netloc}"


async def _write_response(writer: asyncio.StreamWriter, status: int, body: dict) -> None:
    payload = json.dumps(body, separators=(",", ":")).encode()
    writer.write(
        f"HTTP/1.1 {status} {'OK' if status == 200 else 'Error'}\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(payload)}\r\nConnection: close\r\n\r\n".encode()
        + payload
    )
    await writer.drain()


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
                "service": "niko-standby-backend",
                "uptime_seconds": max(0, int(time.time() - _STATS["started_at"])),
                "total_api_requests": _STATS["total_api_requests"],
                "failed_api_requests": _STATS["failed_api_requests"],
            })
            return

        if method == "POST" and target == "/internal/standby/discord":
            await _relay_discord_request(reader, writer, headers, key)
            return

        if method == "POST" and target == "/internal/standby/control":
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

        if method == "POST" and target == "/internal/standby/verify":
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

        if method == "CONNECT":
            await _write_response(writer, 405, {"error": "CONNECT is not supported."})
            return
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
        response = await asyncio.to_thread(_dispatch_web_request, web_app, method, target, headers, body)
        writer.write(response)
        await writer.drain()
    except (asyncio.IncompleteReadError, asyncio.LimitOverrunError, UnicodeError, asyncio.TimeoutError, ConnectionError):
        pass
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except (ConnectionError, OSError):
            pass


async def serve_standby(
    host: str,
    port: int,
    certfile: str | None,
    keyfile: str | None,
    bot_token: str,
    session_secret: str,
    gateway_controller=None,
    web_app=None,
):
    """Bind the standby backend HTTPS relay and shared dashboard listener."""
    if not bot_token or not session_secret:
        raise RuntimeError("STANDBY_MODE requires the production DISCORD_BOT_TOKEN and SESSION_SECRET.")
    if bool(certfile) != bool(keyfile):
        raise RuntimeError("Configure both STANDBY_TLS_CERT and STANDBY_TLS_KEY, or neither when the platform terminates HTTPS.")
    context = None
    if certfile and keyfile:
        if not os.path.isfile(certfile) or not os.path.isfile(keyfile):
            raise RuntimeError("Configured STANDBY_TLS_CERT and STANDBY_TLS_KEY files must exist.")
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
