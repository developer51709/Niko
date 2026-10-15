"""Authenticated API relay and gateway failover for warm standby instances."""

from __future__ import annotations

import asyncio
import base64
import json
import os
import time

import requests

from utils import logging
from utils.standby_failover import control_proof, is_discord_relay_url, relay_proof, secret_key


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
        # True once a direct probe reached Discord, so the instance knows it can
        # serve the gateway itself rather than guessing from a failed request.
        self.direct_egress_verified = False
        self._hooked_session = None
        self._attached_http = None
        self._handoff_lock = asyncio.Lock()
        self._recovery_task = None
        self._recovery_interval = 600
        self._supervision_task = None
        # A restarted standby comes back warm and takes no gateway ownership on
        # its own, so the primary re-arms it on this cadence.
        self._supervision_interval = 15
        # How many unanswered supervision ticks a standby may miss before the
        # primary stops waiting and owns the gateway again.
        self._reclaim_grace_ticks = 4

    def attach(self, bot) -> bool:
        """Wrap static_login so the standby manager owns startup REST failover."""
        self.bot = bot
        self.http = bot.http
        if self._attached_http is self.http:
            session = getattr(self.http, "_HTTPClient__session", None)
            if session is not None and hasattr(session, "_request"):
                self._install_hook(session)
            return True

        original_login = self.http.static_login

        session = getattr(self.http, "_HTTPClient__session", None)
        if session is not None and hasattr(session, "_request"):
            self._install_hook(session)
        manager = self

        async def wrapped_static_login(token):
            original_request = manager.http.request

            async def wrapped_request(*args, **kwargs):
                # discord.py creates the aiohttp session at the start of
                # static_login, before it issues /users/@me.
                session = getattr(manager.http, "_HTTPClient__session", None)
                if session is not None and hasattr(session, "_request"):
                    manager._install_hook(session)
                return await original_request(*args, **kwargs)

            manager.http.request = wrapped_request
            try:
                data = await original_login(token)
            finally:
                manager.http.request = original_request

            session = getattr(manager.http, "_HTTPClient__session", None)
            if session is not None and hasattr(session, "_request"):
                manager._install_hook(session)
            return data

        wrapped_static_login._standby_original_login = original_login
        self.http.static_login = wrapped_static_login
        self._attached_http = self.http
        return True

    # Markers only Cloudflare's own challenge, block, or rate-limit pages carry.
    _CF_PAGE_MARKERS = (
        "cloudflare", "cf-error-details", "cf-wrapper", "attention required",
        "error code: 1015", "cf-chl", "just a moment",
    )

    @staticmethod
    def _is_discord_api_error(body: str) -> bool:
        """True for a Discord JSON API or rate-limit body (never a CF page)."""
        if not body.strip().startswith("{"):
            return False
        try:
            payload = json.loads(body)
        except ValueError:
            return False
        return isinstance(payload, dict) and ("message" in payload or "error" in payload)

    @staticmethod
    def is_cloudflare_block(response, body_fallback: str = "") -> bool:
        """Report whether a response came from Cloudflare's edge, not Discord.

        Discord serves *every* API response through Cloudflare, so
        ``Server: cloudflare`` and ``CF-Ray`` prove nothing on their own: a
        plain Discord 429 or JSON API error is not a block, and treating it as
        one reports a ban that never happened and relays traffic for no reason.
        Only an interstitial signature — an explicit ``cf-mitigated`` header or
        Cloudflare's own page body — counts as blocked.
        """
        status = getattr(response, "status", getattr(response, "status_code", 0))
        if status not in {403, 429, 503}:
            return False
        headers = getattr(response, "headers", {})
        # requests exposes ``text`` as a string property, while aiohttp
        # exposes it as an async method. Never invoke a callable here: doing so
        # can create an un-awaited coroutine. The aiohttp path reads the body
        # in _async_cloudflare_block and passes it as the fallback.
        body = getattr(response, "text", "")
        if callable(body) or not isinstance(body, str) or not body:
            body = body_fallback
        if not isinstance(body, str):
            body = ""
        if StandbyFailoverManager._is_discord_api_error(body):
            return False
        if str(headers.get("cf-mitigated", "")).strip():
            return True
        lowered = body.lower()
        if any(marker in lowered for marker in StandbyFailoverManager._CF_PAGE_MARKERS):
            return True
        # No body evidence: keep the previous heuristic, which only ever fires
        # on 429 where Cloudflare's edge answers before Discord does.
        header_signature = "cloudflare" in str(headers.get("Server", "")).lower() or bool(headers.get("CF-Ray"))
        return header_signature and status == 429

    def _install_hook(self, session) -> None:
        if session is self._hooked_session:
            return
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
                logging.warning("StandbyFailover", "Cloudflare block detected on Discord REST request.")
                manager.egress_blocked = True
                if not manager.auto_enabled:
                    return response
                selected = await manager.select_standby()
                if selected:
                    response.release()
                    if not await manager.handoff_to_standby():
                        logging.error("StandbyFailover", f"Cloudflare block detected; standby gateway handoff failed: {manager.last_error}")
                    try:
                        return await manager.relay_aiohttp(original_request, method, str(url), kwargs)
                    except Exception as exc:
                        manager.last_error = f"Standby API relay failed ({type(exc).__name__})."
                        logging.warning("StandbyFailover", manager.last_error)
                        return response

                if manager.auto_enabled:
                    logging.error("StandbyFailover", f"Cloudflare block detected; no standby is available: {manager.last_error}")
                proxy_manager = getattr(manager.bot, "proxy_manager", None)
                if proxy_manager is not None:
                    try:
                        await proxy_manager.enable()
                    except Exception as exc:
                        logging.warning("StandbyFailover", f"Webshare fallback failed ({type(exc).__name__}).")
                    proxy_url = getattr(manager.http, "proxy", None)
                    if proxy_url:
                        kwargs["proxy"] = proxy_url
                        proxy_auth = getattr(manager.http, "proxy_auth", None)
                        if proxy_auth is not None:
                            kwargs["proxy_auth"] = proxy_auth
                        response.release()
                        try:
                            return await original_request(method, url, **kwargs)
                        except Exception as exc:
                            manager.last_error = f"Webshare startup fallback failed ({type(exc).__name__})."
                            logging.error("StandbyFailover", manager.last_error)
                return response
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
        """Relay exactly the Discord hosts the standby is willing to forward."""
        return is_discord_relay_url(url)

    def relay_configured(self) -> bool:
        """Report whether a signed relay request could actually be sent now.

        A blocked direct request is only worth relaying when a standby origin is
        active and the relay secrets are present. Without them the original
        response is the only honest answer to return, so callers can keep their
        normal error handling instead of failing on a relay misconfiguration.
        """
        if not self.active_origin:
            return False
        return bool(os.getenv("DISCORD_BOT_TOKEN") and os.getenv("SESSION_SECRET"))

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

    async def standby_gateway_state(self, origin: str) -> str:
        """Report an instance's gateway state: ``active``, ``warm``, or ``unreachable``.

        A standby publishes this through its own ``/health`` endpoint, which is
        how the primary notices one that restarted without gateway ownership.
        """
        stats = await self.probe_standby(origin)
        if not stats:
            return "unreachable"
        return "active" if stats.get("gateway") == "active" else "warm"

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
        relay = await original_request("POST", relay_url, json=envelope, timeout=35, allow_redirects=False)
        async with relay:
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

    async def stand_down_standbys(self) -> int:
        """Tell every registered standby to release the gateway.

        Called once at startup, after this instance verified it can reach
        Discord directly: a standby left over from an earlier failover is still
        holding a gateway session, and two live sessions duplicate every event
        the bot handles. The caller must not use it while its own egress is
        blocked or unreachable — the standby then owns the only working gateway.
        """
        released = 0
        for standby_id in list(self.ids):
            try:
                if await self.control(standby_id, "relinquish"):
                    released += 1
            except Exception as exc:
                logging.warning("StandbyFailover", f"Standby stand-down failed: {type(exc).__name__}")
        return released

    def _ensure_recovery_task(self) -> None:
        if self._recovery_task is None or self._recovery_task.done():
            self._recovery_task = asyncio.create_task(self._recovery_loop())
        if self._supervision_task is None or self._supervision_task.done():
            self._supervision_task = asyncio.create_task(self._supervision_loop())

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
                self.egress_blocked = False
                self.last_changed_at = time.time()
                logging.success("StandbyFailover", "Primary gateway restored; standby returned to warm-ready state.")
                return
            except asyncio.CancelledError:
                return
            except requests.RequestException as exc:
                logging.warning("StandbyFailover", f"Primary egress recovery probe failed: {type(exc).__name__}")
            except Exception as exc:
                logging.warning("StandbyFailover", f"Standby recovery handoff failed: {type(exc).__name__}")

    async def _supervision_loop(self) -> None:
        """Re-arm the active standby when it restarts without its gateway.

        A restarted standby boots as a fresh warm process: it holds no gateway
        ownership, and nothing on that side can promote itself, so without this
        the bot stays offline after a standby restart. The primary already owns
        the authority to activate it, so it re-sends that signed handoff and
        leaves a standby that reports itself active untouched.
        """
        missed = 0
        while self.active_origin:
            try:
                await asyncio.sleep(self._supervision_interval)
                standby_id = self.status().get("active_standby_id")
                if not standby_id or standby_id not in self.ids:
                    continue
                origin = self.origins[self.ids.index(standby_id)]
                state = await self.standby_gateway_state(origin)
                if state == "active":
                    missed = 0
                    continue
                if state == "warm":
                    missed = 0
                    if await self.control(standby_id, "activate"):
                        logging.success("StandbyFailover", "Active standby restarted; gateway ownership re-armed.")
                    else:
                        logging.warning("StandbyFailover", "Active standby is warm and did not accept gateway ownership.")
                    continue
                # A restarting standby is unreachable for a few ticks and comes
                # back warm. One that never answers would leave the bot offline,
                # so the primary waits out the grace period and then owns the
                # gateway itself rather than staying passive forever.
                missed += 1
                if missed >= self._reclaim_grace_ticks:
                    await self._reclaim_gateway("The active standby did not come back")
                    return
            except asyncio.CancelledError:
                return
            except Exception as exc:
                logging.warning("StandbyFailover", f"Standby supervision failed: {type(exc).__name__}")

    async def _reclaim_gateway(self, reason: str) -> bool:
        """Take gateway ownership back from a standby that is not holding it."""
        standby_id = self.status().get("active_standby_id")
        if standby_id and standby_id in self.ids:
            try:
                await self.control(standby_id, "relinquish")
            except Exception:
                pass
        self.active_origin = None
        self.last_changed_at = time.time()
        handoff = getattr(self.bot, "gateway_handoff", None)
        if handoff is None:
            return False
        handoff.refresh_caches_on_ready = True
        await handoff.activate()
        logging.error("StandbyFailover", f"{reason}; this instance resumed gateway ownership.")
        return True

    async def check_direct_egress(self) -> bool:
        try:
            response = await asyncio.to_thread(requests.get, "https://discord.com/api/v10/gateway",
                                               timeout=10, allow_redirects=False)
        except requests.RequestException:
            self.direct_egress_verified = False
            return False
        if not self.is_cloudflare_block(response):
            # Direct egress answers normally, so any earlier block is over.
            self.egress_blocked = False
            self.direct_egress_verified = True
            return False
        self.direct_egress_verified = False
        self.egress_blocked = True
        if not self.auto_enabled:
            return False
        if not await self.select_standby():
            return False
        return await self.handoff_to_standby()


