"""Authenticated API relay and gateway failover for warm standby instances."""

from __future__ import annotations

import asyncio
import base64
import json
import os
import time
from urllib.parse import urlsplit

import requests

from utils import logging
from utils.standby_failover import relay_proof, secret_key, control_proof


class _RelayedAiohttpResponse:
    """Minimal aiohttp response contract consumed by discord.py."""

    def __init__(self, status: int, headers: dict, body: bytes):
        from multidict import CIMultiDict

        self.status = status
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


class StandbyFailoverManager:
    """Routes Discord REST requests over HTTPS and coordinates gateway ownership."""

    def __init__(self):
        self.bot = None
        self.http = None
        self.origins: list[str] = []
        self.ids: list[str] = []
        self.index = 0
        self.active_origin: str | None = None
        self.auto_enabled = True
        self.last_error: str | None = None
        self.last_changed_at = time.time()
        self.failover_count = 0
        self.egress_blocked = False
        self._hooked_session = None
        self._handoff_lock = asyncio.Lock()
        self._recovery_task = None
        self._recovery_interval = 600

    def attach(self, bot) -> bool:
        self.bot = bot
        self.http = bot.http
        session = getattr(self.http, "_HTTPClient__session", None)
        if session is not None and hasattr(session, "_request"):
            self._install_hook(session)
        else:
            original_login = self.http.static_login
            manager = self

            async def wrapped_login(token):
                try:
                    data = await original_login(token)
                except Exception as exc:
                    response = getattr(exc, "response", None)
                    body = getattr(exc, "text", "")
                    if response is None or not await manager.is_cloudflare_block(response, body):
                        raise
                    manager.egress_blocked = True
                    if not manager.auto_enabled:
                        raise

                    await manager.select_standby()
                    # Preserve discord.py's connector by detaching it before
                    # retrying the initial /users/@me call through standby.
                    failed_session = getattr(manager.http, "_HTTPClient__session", None)
                    if failed_session is not None and not failed_session.closed:
                        failed_session.detach()
                        await failed_session.close()
                    data = await original_login(token)
                    await manager.handoff_to_standby()
                session = getattr(manager.http, "_HTTPClient__session", None)
                if session is not None:
                    manager._install_hook(session)
                return data

            self.http.static_login = wrapped_login
        return True

    @staticmethod
    def is_cloudflare_block(response, body_fallback: str = "") -> bool:
        status = getattr(response, "status", getattr(response, "status_code", 0))
        if status not in {403, 429, 503}:
            return False
        headers = getattr(response, "headers", {})
        body = getattr(response, "text", "")
        if callable(body):
            try:
                body = body()
                if hasattr(body, "__await__"):
                    return False
            except Exception:
                body = ""
        if not isinstance(body, str) or not body:
            body = body_fallback
        body = body.lower()
        header_signature = "cloudflare" in str(headers.get("Server", "")).lower() or bool(headers.get("CF-Ray"))
        body_signature = any(tag in body for tag in ("cloudflare", "cf-error-details", "cf-wrapper", "attention required"))
        return (header_signature or body_signature) if status == 429 else (header_signature and body_signature)

    def _install_hook(self, session) -> None:
        original_request = session._request
        manager = self

        async def hooked_request(method, url, **kwargs):
            if manager.active_origin and manager._should_relay(str(url)):
                try:
                    return await manager.relay_aiohttp(original_request, method, str(url), kwargs)
                except Exception as exc:
                    manager.last_error = f"Standby API relay failed ({type(exc).__name__})."
                    logging.warning("StandbyFailover", manager.last_error)
            response = await original_request(method, url, **kwargs)
            if manager._should_relay(str(url)) and await manager._async_cloudflare_block(response):
                manager.egress_blocked = True
                if not manager.auto_enabled:
                    return response
                await manager.select_standby()
                if manager.active_origin:
                    response.release()
                    await manager.handoff_to_standby()
                    try:
                        return await manager.relay_aiohttp(original_request, method, str(url), kwargs)
                    except Exception as exc:
                        manager.last_error = f"Standby API relay failed ({type(exc).__name__})."
                        logging.warning("StandbyFailover", manager.last_error)
            return response

        session._request = hooked_request
        self._hooked_session = session

    async def _async_cloudflare_block(self, response) -> bool:
        status = getattr(response, "status", 0)
        if status not in {403, 429, 503}:
            return False
        body = ""
        try:
            body = await response.text()
        except Exception:
            pass
        return self.is_cloudflare_block(response, body)

    @staticmethod
    def _should_relay(url: str) -> bool:
        parts = urlsplit(url)
        host = (parts.hostname or "").lower()
        return parts.scheme == "https" and (host == "discord.com" or host.endswith((".discord.com", ".discordapp.com")))

    def set_standbys(self, origins: list[str], ids: list[str] | None = None) -> None:
        entries = [(ids[i] if ids and i < len(ids) else str(i), url) for i, url in enumerate(origins)
                   if isinstance(url, str) and url.startswith("https://")]
        self.ids = [entry[0] for entry in entries]
        self.origins = [entry[1].rstrip("/") for entry in entries]
        self.index = 0
        if self.active_origin not in self.origins:
            self.active_origin = None

    async def probe_standby(self, origin: str) -> dict | None:
        def probe():
            with requests.Session() as session:
                session.trust_env = False
                response = session.get(f"{origin.rstrip('/')}/health", timeout=(3, 5), allow_redirects=False)
                payload = response.json()
                if response.status_code == 200 and payload.get("service") == "niko-standby-backend":
                    return payload
                return None
        try:
            return await asyncio.to_thread(probe)
        except (requests.RequestException, ValueError, TypeError, AttributeError):
            return None

    async def probe_all(self) -> dict[str, dict | None]:
        results = await asyncio.gather(*(self.probe_standby(origin) for origin in self.origins))
        return dict(zip(self.ids, results))

    async def select_standby(self, standby_id: str | None = None) -> bool:
        if not self.origins:
            self.last_error = "No standby instances are registered."
            return False
        if standby_id is not None:
            try:
                self.index = self.ids.index(standby_id)
            except ValueError:
                return False
            candidates = [self.index]
        else:
            candidates = [(self.index + offset) % len(self.origins) for offset in range(len(self.origins))]
        for index in candidates:
            if await self.probe_standby(self.origins[index]):
                self.index = index
                self.active_origin = self.origins[index]
                self.last_error = None
                self.last_changed_at = time.time()
                self.failover_count += 1
                return True
        self.last_error = "No registered standby passed its health check."
        return False

    def select_failover(self, mode: str) -> bool:
        """Select automatic standby failover or force direct routing."""
        if mode not in {"auto", "off"}:
            raise ValueError("Standby failover mode must be auto or off.")
        self.auto_enabled = mode == "auto"
        if mode == "off":
            self.active_origin = None
        self.last_error = None
        self.last_changed_at = time.time()
        return True

    def status(self) -> dict:
        standby_id = self.ids[self.origins.index(self.active_origin)] if self.active_origin in self.origins else None
        return {
            "mode": "standby" if self.active_origin else "auto" if self.auto_enabled else "off",
            "enabled": self.active_origin is not None,
            "active_standby_id": standby_id,
            "standby_count": len(self.origins),
            "last_error": self.last_error,
            "last_changed_at": self.last_changed_at,
            "failover_count": self.failover_count,
            "egress_blocked": self.egress_blocked,
        }

    def _signed_envelope(self, method: str, url: str, headers: dict, body: bytes) -> tuple[str, dict]:
        token, session_secret = os.getenv("DISCORD_BOT_TOKEN", ""), os.getenv("SESSION_SECRET", "")
        if not token or not session_secret or not self.active_origin:
            raise RuntimeError("Standby API relay is not configured.")
        timestamp, nonce = str(int(time.time())), os.urandom(32).hex()
        clean_headers = {str(k): str(v) for k, v in headers.items()}
        proof = relay_proof(secret_key(token, session_secret), timestamp, nonce, method, url, clean_headers, body)
        return f"{self.active_origin}/internal/standby/discord", {
            "method": method.upper(), "url": url, "headers": clean_headers,
            "body": base64.b64encode(body).decode("ascii"), "timestamp": timestamp, "nonce": nonce, "proof": proof,
        }

    def request_via_standby(self, method: str, url: str, kwargs: dict):
        request_kwargs = {k: kwargs[k] for k in ("params", "data", "json", "headers") if k in kwargs}
        prepared = requests.Request(method.upper(), url, **request_kwargs).prepare()
        raw_body = prepared.body or b""
        if isinstance(raw_body, str):
            raw_body = raw_body.encode()
        relay_url, envelope = self._signed_envelope(method, prepared.url, prepared.headers, raw_body)
        relay = requests.post(relay_url, json=envelope, timeout=35, allow_redirects=False)
        relay.raise_for_status()
        result = relay.json()
        response = requests.Response()
        response.status_code = int(result["status"])
        response.headers.update(result["headers"])
        response._content = base64.b64decode(result["body"], validate=True)
        response.url = prepared.url
        response.request = prepared
        response.encoding = requests.utils.get_encoding_from_headers(response.headers)
        return response

    async def relay_aiohttp(self, original_request, method: str, url: str, kwargs: dict):
        data = kwargs.get("data")
        body = data.encode() if isinstance(data, str) else (data or b"")
        headers = dict(kwargs.get("headers", {}))
        if "json" in kwargs:
            headers.setdefault("Content-Type", "application/json")
            body = json.dumps(kwargs["json"], separators=(",", ":")).encode()
        relay_url, envelope = self._signed_envelope(method, url, headers, body)
        async with original_request("POST", relay_url, json=envelope, timeout=35, allow_redirects=False) as relay:
            if relay.status != 200:
                raise RuntimeError(f"Standby relay returned HTTP {relay.status}.")
            result = await relay.json()
        return _RelayedAiohttpResponse(int(result["status"]), result["headers"], base64.b64decode(result["body"], validate=True))

    async def control(self, standby_id: str, action: str) -> bool:
        if action not in {"activate", "relinquish"} or standby_id not in self.ids:
            return False
        i = self.ids.index(standby_id)
        token, session_secret = os.getenv("DISCORD_BOT_TOKEN", ""), os.getenv("SESSION_SECRET", "")
        if not token or not session_secret:
            return False
        key = secret_key(token, session_secret)
        nonce = os.urandom(32).hex()
        payload = {"action": action, "nonce": nonce, "proof": control_proof(key, action, nonce)}
        try:
            response = await asyncio.to_thread(requests.post, f"{self.origins[i]}/internal/standby/control",
                                               json=payload, timeout=12, allow_redirects=False)
            return response.status_code == 200 and response.json().get("ok") is True
        except (requests.RequestException, ValueError, AttributeError):
            return False

    async def handoff_to_standby(self) -> bool:
        standby_id = self.status().get("active_standby_id")
        handoff = getattr(self.bot, "gateway_handoff", None)
        if not standby_id or handoff is None:
            return False
        async with self._handoff_lock:
            if handoff.active.is_set():
                await handoff.relinquish()
            if await self.control(standby_id, "activate"):
                self._ensure_recovery_task()
                return True
            self.last_error = "Standby did not accept gateway handoff."
            await handoff.activate()
            return False

    async def activate_standby(self, standby_id: str) -> bool:
        if not await self.select_standby(standby_id):
            self.last_error = "Standby health check failed."
            return False
        self.last_changed_at = time.time()
        return True

    async def rotate_standby(self) -> bool:
        if not self.origins:
            self.last_error = "No standby instances are registered."
            return False
        current = self.status().get("active_standby_id")
        start = (self.ids.index(current) + 1) % len(self.ids) if current in self.ids else self.index
        for offset in range(len(self.origins)):
            i = (start + offset) % len(self.origins)
            if await self.probe_standby(self.origins[i]):
                self.index = i
                self.active_origin = self.origins[i]
                self.last_changed_at = time.time()
                self.failover_count += 1
                return True
        self.last_error = "No healthy standby is available."
        return False

    def _ensure_recovery_task(self) -> None:
        if self._recovery_task is None or self._recovery_task.done():
            self._recovery_task = asyncio.create_task(self._recovery_loop())

    async def _recovery_loop(self) -> None:
        """Return gateway ownership to primary after its direct egress recovers."""
        while self.active_origin:
            try:
                await asyncio.sleep(self._recovery_interval)
                response = await asyncio.to_thread(
                    requests.get,
                    "https://discord.com/api/v10/gateway",
                    timeout=10,
                    allow_redirects=False,
                )
                if self.is_cloudflare_block(response):
                    continue
                standby_id = self.status().get("active_standby_id")
                handoff = getattr(self.bot, "gateway_handoff", None)
                if not standby_id or handoff is None:
                    continue
                if not await self.control(standby_id, "relinquish"):
                    continue
                handoff.refresh_caches_on_ready = True
                await handoff.activate()
                try:
                    await asyncio.wait_for(handoff.connected.wait(), timeout=45)
                except asyncio.TimeoutError:
                    await handoff.relinquish()
                    if await self.control(standby_id, "activate"):
                        logging.warning("StandbyFailover", "Primary gateway reconnect failed; standby retained gateway ownership.")
                        continue
                    handoff.refresh_caches_on_ready = True
                    await handoff.activate()
                    logging.warning("StandbyFailover", "Standby could not resume gateway ownership after primary timeout.")
                    continue
                self.active_origin = None
                self.last_changed_at = time.time()
                logging.success("StandbyFailover", "Primary gateway restored; standby returned to warm-ready state.")
                return
            except asyncio.CancelledError:
                return
            except requests.RequestException as exc:
                logging.warning("StandbyFailover", f"Primary egress recovery probe failed: {type(exc).__name__}")
            except Exception as exc:
                logging.warning("StandbyFailover", f"Standby recovery handoff failed: {type(exc).__name__}")

    async def check_direct_egress(self) -> bool:
        try:
            response = await asyncio.to_thread(requests.get, "https://discord.com/api/v10/gateway",
                                               timeout=10, allow_redirects=False)
        except requests.RequestException:
            return False
        if not self.is_cloudflare_block(response):
            return False
        self.egress_blocked = True
        if not self.auto_enabled:
            return False
        if not await self.select_standby():
            return False
        return await self.handoff_to_standby()


