"""Client for optional Cloudflare Discord API proxy workers.

A worker receives the complete Discord REST request as a signed envelope and
performs it from Cloudflare's Worker egress. The bot keeps its normal
direct/standby/Webshare path as the fallback, so proxy workers stay optional.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from contextvars import ContextVar
from http import HTTPStatus
from urllib.parse import urlsplit

import requests

from utils import logging

SERVICE = "niko-discord-proxy"
_TOKEN_ENV = "PROXY_WORKER_TOKEN"
_MAX_BODY_BYTES = 8 * 1024 * 1024
_MAX_RESPONSE_BYTES = 12 * 1024 * 1024
_DISCORD_API_HOSTS = ("discord.com", "discordapp.com")
# Each request task gets its own value, so parallel requests cannot report a
# worker's result for one call against another call's direct fallback.
_RELAYED = ContextVar("discord_proxy_relayed", default=False)


def proxy_worker_token() -> str:
    """The shared worker secret, or an empty string when the feature is off."""
    return os.environ.get(_TOKEN_ENV, "").strip()


def is_discord_api_url(url: str) -> bool:
    """Return True only for HTTPS Discord REST API targets a worker may relay."""
    try:
        parts = urlsplit(url)
        port = parts.port
    except (TypeError, ValueError):
        return False
    if parts.scheme != "https" or parts.username or parts.password or port is not None:
        return False
    hostname = (parts.hostname or "").lower().rstrip(".")
    if not hostname:
        return False
    if hostname not in _DISCORD_API_HOSTS and not hostname.endswith(tuple(f".{host}" for host in _DISCORD_API_HOSTS)):
        return False
    if parts.fragment or not parts.path.startswith("/api/"):
        return False
    return True


def verification_proof(token: str, nonce: str) -> str:
    """Challenge proof the worker returns for the owner dashboard."""
    return hmac.new(
        token.encode(),
        f"niko-proxy-worker-verification:{nonce}".encode(),
        hashlib.sha256,
    ).hexdigest()


def relay_proof(token: str, timestamp: str, nonce: str, method: str, url: str, headers: dict, body: bytes) -> str:
    """Authenticate the complete outbound Discord request."""
    canonical = json.dumps(
        [
            timestamp,
            nonce,
            method.upper(),
            url,
            sorted(headers.items()),
            hashlib.sha256(body).hexdigest(),
        ],
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()
    return hmac.new(token.encode(), b"niko-discord-proxy-relay:" + canonical, hashlib.sha256).hexdigest()


class UnsupportedProxyPayload(Exception):
    """A request the relay cannot represent (multipart uploads, for example)."""


def _status_reason(status: int) -> str:
    """HTTP reason phrase for constructed responses (discord.py formats it)."""
    try:
        return HTTPStatus(status).phrase
    except ValueError:
        return "Unknown Status"


class _RelayedAiohttpResponse:
    """Minimal aiohttp response contract consumed by discord.py."""

    def __init__(self, status: int, headers: dict, body: bytes):
        from multidict import CIMultiDict

        self.status = status
        self.reason = _status_reason(status)
        self.headers = CIMultiDict(headers)
        self._body = body

    async def text(self, encoding: str = "utf-8") -> str:
        return self._body.decode(encoding, errors="replace")

    def release(self) -> None:
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        self.release()


class DiscordProxyManager:
    """Routes Discord REST requests through registered proxy workers."""

    def __init__(self, token: str | None = None):
        self.token = proxy_worker_token() if token is None else token
        self.workers: list[dict] = []
        self.enabled = False
        self.http = None
        self.index = 0
        self.total_requests = 0
        self.total_failures = 0
        self.last_error: str | None = None
        self.last_worker: str | None = None
        self.last_used_at: float | None = None
        self._hooked_session = None
        self._wrapped_http = None
        self._recent_errors: list[dict] = []
        self._probe_cache: tuple[float, dict] | None = None

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    def attach(self, bot) -> bool:
        """Install the request hook. Safe to call again after login."""
        self.http = bot.http
        if not self.token:
            return False
        # discord.py creates its aiohttp session inside static_login. Wrapping
        # HTTPClient.request installs the hook on that new session before the
        # login call itself, so a blocked host does not have to burn a Webshare
        # request just to reach /users/@me.
        if self._wrapped_http is not self.http:
            self._install_request_installer()
        session = self._current_session()
        if session is not None and session is not self._hooked_session:
            self._install_hook(session)
        return True

    def _install_request_installer(self) -> None:
        http = self.http
        original_request = http.request
        manager = self

        async def wrapped_request(*args, **kwargs):
            session = manager._current_session()
            if session is not None and session is not manager._hooked_session:
                manager._install_hook(session)
            return await original_request(*args, **kwargs)

        http.request = wrapped_request
        self._wrapped_http = http

    def _current_session(self):
        if self.http is None:
            return None
        session = getattr(self.http, "_HTTPClient__session", None)
        if session is not None and hasattr(session, "_request"):
            return session
        return None

    def _install_hook(self, session) -> None:
        original_request = session._request
        manager = self

        async def hooked_request(method, url, **kwargs):
            if manager._should_proxy(str(url)):
                try:
                    response = await manager.relay_aiohttp(original_request, method, str(url), kwargs)
                except UnsupportedProxyPayload:
                    # Multipart uploads stay on the bot's normal route.
                    pass
                except Exception as exc:
                    manager.last_error = f"Discord proxy worker relay failed ({type(exc).__name__})."
                    logging.warning("DiscordProxy", manager.last_error)
                else:
                    _RELAYED.set(True)
                    return response
            _RELAYED.set(False)
            return await original_request(method, url, **kwargs)

        session._request = hooked_request
        self._hooked_session = session

    def set_workers(self, rows: list[dict], enabled: bool) -> None:
        """Replace the in-memory registry used by the request hook."""
        workers = []
        for row in rows or []:
            try:
                worker_id = str(row["id"])
                name = str(row["name"])
                url = str(row["url"]).rstrip("/")
            except (KeyError, TypeError, ValueError):
                continue
            if not url.startswith("https://"):
                continue
            workers.append({
                "id": worker_id,
                "name": name,
                "url": url,
                "created_at": row.get("created_at"),
            })
        self.workers = workers
        self._probe_cache = None
        self.enabled = bool(enabled and workers and self.token)
        if not self.workers:
            self.index = 0
        else:
            self.index %= len(self.workers)

    def _should_proxy(self, url: str) -> bool:
        return bool(self.token and self.enabled and self.workers and is_discord_api_url(url))

    def can_relay(self, url: str) -> bool:
        """Public check used by the dashboard's synchronous Discord client."""
        return self._should_proxy(url)

    def request_was_relayed(self) -> bool:
        """Whether the response the caller just received came from a worker.

        The rate-limit monitor wraps this hook, so it asks after the response is
        returned. A direct fallback (multipart, worker down) must still be able
        to arm the normal Webshare recovery, while a worker's own 429 belongs to
        the worker's rotating egress and must not spend Webshare bandwidth.
        """
        return bool(_RELAYED.get())

    def status(self) -> dict:
        return {
            "enabled": self.enabled,
            "token_configured": bool(self.token),
            "worker_count": len(self.workers),
            "total_requests": self.total_requests,
            "total_failures": self.total_failures,
            "last_error": self.last_error,
            "last_worker": self.last_worker,
            "last_used_at": self.last_used_at,
            "recent_errors": list(self._recent_errors),
        }

    # ── Signed envelopes ──────────────────────────────────────────────────────
    def _signed_envelope(self, worker: dict, method: str, url: str, headers: dict, body: bytes) -> tuple[str, dict]:
        if not self.token:
            raise RuntimeError("PROXY_WORKER_TOKEN is not configured.")
        timestamp, nonce = str(int(time.time())), secrets.token_hex(32)
        clean_headers = {str(name): str(value) for name, value in headers.items()}
        proof = relay_proof(self.token, timestamp, nonce, method, url, clean_headers, body)
        return f"{worker['url'].rstrip('/')}/internal/proxy", {
            "method": method.upper(),
            "url": url,
            "headers": clean_headers,
            "body": base64.b64encode(body).decode("ascii"),
            "timestamp": timestamp,
            "nonce": nonce,
            "proof": proof,
        }

    @staticmethod
    def _prepare_request(method: str, url: str, kwargs: dict):
        """Serialize an aiohttp request into the bytes a worker can replay."""
        if kwargs.get("files") or kwargs.get("form"):
            raise UnsupportedProxyPayload("multipart requests stay on the direct route")
        data = kwargs.get("data")
        if data is not None and not isinstance(data, (str, bytes, bytearray, dict, list, tuple)):
            raise UnsupportedProxyPayload("unsupported request body")
        request_kwargs = {key: kwargs[key] for key in ("params", "data", "json", "headers") if key in kwargs}
        prepared = requests.Request(method.upper(), url, **request_kwargs).prepare()
        body = prepared.body or b""
        if isinstance(body, str):
            body = body.encode()
        elif isinstance(body, (bytes, bytearray)):
            body = bytes(body)
        else:
            raise UnsupportedProxyPayload("unsupported request body")
        if len(body) > _MAX_BODY_BYTES:
            raise UnsupportedProxyPayload("request body is too large to relay")
        return prepared, dict(prepared.headers), body

    def _next_worker(self) -> dict:
        worker = self.workers[self.index % len(self.workers)]
        self.index = (self.index + 1) % len(self.workers)
        return worker

    # ── Async relay (discord.py) ──────────────────────────────────────────────
    async def relay_aiohttp(self, original_request, method: str, url: str, kwargs: dict):
        prepared, headers, body = self._prepare_request(method, url, kwargs)
        errors = []
        for _ in range(len(self.workers)):
            worker = self._next_worker()
            relay_url, envelope = self._signed_envelope(worker, method, prepared.url, headers, body)
            started = time.monotonic()
            try:
                relay = await original_request(
                    "POST",
                    relay_url,
                    json=envelope,
                    timeout=35,
                    allow_redirects=False,
                )
                async with relay:
                    if relay.status != 200:
                        detail = (await relay.text())[:160]
                        raise RuntimeError(f"worker returned HTTP {relay.status}: {detail}")
                    result = await relay.json()
                status = int(result["status"])
                response_body = base64.b64decode(result["body"], validate=True)
                if len(response_body) > _MAX_RESPONSE_BYTES:
                    raise RuntimeError("worker response is too large")
                self._record_success(worker, int((time.monotonic() - started) * 1000))
                return _RelayedAiohttpResponse(status, result.get("headers") or {}, response_body)
            except Exception as exc:
                message = f"{worker['name']} did not relay the request ({type(exc).__name__})."
                errors.append(message)
                self._record_failure(worker, message)
        raise RuntimeError(errors[-1] if errors else "No proxy worker is configured.")

    # ── Standalone aiohttp relay (profile/setname fallbacks) ──────────────────
    async def relay_or_request(self, session, method: str, url: str, **kwargs):
        """Relay one call from a caller-owned aiohttp session, or run it direct.

        Some admin commands build their own session so they can send Discord's
        browser headers. They still belong on the worker egress when routing is
        enabled; an unsupported body or unreachable worker falls back to the
        session's normal request path.
        """
        if self._should_proxy(url):
            try:
                return await self.relay_aiohttp(session._request, method, url, kwargs)
            except UnsupportedProxyPayload:
                pass
            except Exception as exc:
                self.last_error = f"Discord proxy worker relay failed ({type(exc).__name__})."
                logging.warning("DiscordProxy", self.last_error)
        return await session.request(method, url, **kwargs)

    # ── Sync relay (dashboard/OAuth requests) ─────────────────────────────────
    def request_via_worker(self, method: str, url: str, kwargs: dict):
        """Run one Discord request through a worker from a Flask request thread."""
        prepared, headers, body = self._prepare_request(method, url, kwargs)
        errors = []
        for _ in range(len(self.workers)):
            worker = self._next_worker()
            relay_url, envelope = self._signed_envelope(worker, method, prepared.url, headers, body)
            started = time.monotonic()
            try:
                with requests.Session() as session:
                    session.trust_env = False
                    relay = session.post(
                        relay_url,
                        json=envelope,
                        timeout=(4, 35),
                        allow_redirects=False,
                    )
                if relay.status_code != 200:
                    raise RuntimeError(f"worker returned HTTP {relay.status_code}")
                result = relay.json()
                status = int(result["status"])
                response_body = base64.b64decode(result["body"], validate=True)
                if len(response_body) > _MAX_RESPONSE_BYTES:
                    raise RuntimeError("worker response is too large")
                response = requests.Response()
                response.status_code = status
                response.reason = _status_reason(status)
                response.headers.update(result.get("headers") or {})
                response._content = response_body
                response.url = prepared.url
                response.request = prepared
                response.encoding = requests.utils.get_encoding_from_headers(response.headers)
                self._record_success(worker, int((time.monotonic() - started) * 1000))
                return response
            except Exception as exc:
                message = f"{worker['name']} did not relay the request ({type(exc).__name__})."
                errors.append(message)
                self._record_failure(worker, message)
        raise RuntimeError(errors[-1] if errors else "No proxy worker is configured.")

    # ── Telemetry ─────────────────────────────────────────────────────────────
    def _record_success(self, worker: dict, latency_ms: int) -> None:
        self.total_requests += 1
        self.last_error = None
        self.last_worker = worker.get("name")
        self.last_used_at = time.time()
        logging.debug("DiscordProxy", f"{worker.get('name')} relayed a Discord request in {latency_ms} ms.")

    def _record_failure(self, worker: dict, message: str) -> None:
        self.total_failures += 1
        self.last_error = message
        self.last_worker = worker.get("name")
        self.last_used_at = time.time()
        self._recent_errors.insert(0, {
            "at": int(time.time() * 1000),
            "worker": worker.get("name"),
            "message": message[:240],
        })
        del self._recent_errors[25:]

    def probe_worker_sync(self, worker: dict) -> dict | None:
        base = str(worker.get("url", "")).rstrip("/")
        if not base.startswith("https://"):
            return None
        # ``/stats`` is also the health document, so one short request covers a
        # healthy worker. Only an authenticated telemetry failure falls back to
        # the public health endpoint, which keeps the 3-second dashboard poll
        # well inside the bot-loop timeout even when a worker is unreachable.
        try:
            with requests.Session() as session:
                session.trust_env = False
                stats_error = None
                try:
                    stats_response = session.get(
                        f"{base}/stats",
                        headers={"Authorization": f"Bearer {self.token}"},
                        timeout=3,
                        allow_redirects=False,
                    )
                except (requests.RequestException, ValueError) as exc:
                    return None
                if stats_response.status_code == 200:
                    try:
                        stats = stats_response.json()
                    except ValueError:
                        return None
                    if isinstance(stats, dict) and stats.get("service") == SERVICE:
                        stats["checked_at"] = int(time.time() * 1000)
                        return stats
                    return None
                stats_error = f"Telemetry returned HTTP {stats_response.status_code}."
                health_response = session.get(f"{base}/health", timeout=3, allow_redirects=False)
                if health_response.status_code != 200:
                    return None
                health = health_response.json()
                if not isinstance(health, dict) or health.get("service") != SERVICE:
                    return None
                health["stats_error"] = stats_error
                health["checked_at"] = int(time.time() * 1000)
                return health
        except (requests.RequestException, ValueError, TypeError, AttributeError):
            return None

    async def probe_all(self) -> dict[str, dict | None]:
        """Probe every worker in parallel, with a small cache for 3-second polls."""
        if self._probe_cache is not None and time.monotonic() - self._probe_cache[0] < 2:
            return self._probe_cache[1]
        workers = list(self.workers)
        results = await asyncio.gather(*(asyncio.to_thread(self.probe_worker_sync, worker) for worker in workers))
        payload = {
            str(worker.get("id")): result
            for worker, result in zip(workers, results)
        }
        self._probe_cache = (time.monotonic(), payload)
        return payload
