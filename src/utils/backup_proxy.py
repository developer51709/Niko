"""TLS CONNECT proxy service used by a standby Niko deployment.

A backup never logs in to Discord. It only serves authenticated CONNECT tunnels
for Discord hosts after proving it has the production bot token and Flask
session secret.
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
from urllib.parse import urlsplit

_ALLOWED_SUFFIXES = (".discord.com", ".discordapp.com", ".discord.gg", ".discord.media", ".discordapp.net")
_ALLOWED_EXACT = {"discord.com", "discordapp.com", "discord.gg", "discord.media", "discordapp.net"}
_MAX_HEADERS = 16 * 1024


def secret_key(bot_token: str, session_secret: str) -> bytes:
    return hashlib.sha256(bot_token.encode() + b"\0" + session_secret.encode()).digest()


def verification_proof(key: bytes, nonce: str) -> str:
    return hmac.new(key, b"niko-backup-verification:" + nonce.encode(), hashlib.sha256).hexdigest()


def proxy_password(key: bytes) -> str:
    return hmac.new(key, b"niko-backup-proxy", hashlib.sha256).hexdigest()


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


async def _pipe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        while chunk := await reader.read(64 * 1024):
            writer.write(chunk)
            await writer.drain()
    except (ConnectionError, asyncio.CancelledError):
        pass
    finally:
        try:
            writer.write_eof()
        except (AttributeError, OSError, RuntimeError):
            pass


async def _handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    key: bytes,
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

        if method == "GET" and target in ("/", "/health"):
            await _write_response(writer, 200, {"ok": True, "service": "niko-backup-proxy"})
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
            await _write_response(writer, 404, {"error": "Not found."})
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
        await asyncio.gather(_pipe(reader, upstream_writer), _pipe(upstream_reader, writer))
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
    server = await asyncio.start_server(
        lambda r, w: _handle_client(r, w, key), host, port, ssl=context,
        limit=_MAX_HEADERS + 1,
    )
    return server
