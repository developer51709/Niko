"""
Automated Webshare proxy failover for Discord global rate limits.

When Discord globally rate limits the bot's IP (429 with the
``X-RateLimit-Global`` header), the manager immediately fetches a proxy from
the Webshare API and routes the bot's HTTP client through it.  Both REST
requests and gateway websocket reconnects pick the proxy up through
``client.http.proxy`` — discord.py already applies that attribute on every
request and websocket connect.

While the proxy is active a background task performs exactly one tiny
*unproxied* request to Discord's gateway endpoint every 10 minutes.  The
moment that probe confirms the direct IP is no longer rate limited (any
non-429 response), the proxy is disabled again so the Webshare 1 GB/month
bandwidth allowance is only consumed while it is genuinely needed.

Webshare is optional; owner-registered standby instances can independently arm
this failover without requiring a Webshare API key.
"""

from __future__ import annotations

import asyncio
import json
import os
import random
import time

import aiohttp
import requests

from utils import logging

# ── Config ───────────────────────────────────────────────────────────────────
WEBSHARE_API_KEY_ENV = "WEBSHARE_API_KEY"
PROXY_LIST_URL = "https://proxy.webshare.io/api/v2/proxy/list/"
GATEWAY_PROBE_URL = "https://discord.com/api/v10/gateway"

# Webshare's list API requires a ``mode``: "direct" returns a usable
# ``proxy_address``/``port``/credentials per proxy (what this failover needs),
# while "backbone" plans (e.g. residential ``pool_filter``) route everything
# through ``p.webshare.io`` on one of these ports (username/password auth).
_BACKBONE_ADDRESS = "p.webshare.io"
_BACKBONE_PORTS = {80, 1080, 3128}
_BACKBONE_PORT_MIN, _BACKBONE_PORT_MAX = 9999, 19999
_BACKBONE_PORT_FALLBACK = 80

VERIFY_INTERVAL_SECONDS = 600      # probe the direct IP every 10 minutes
PROXY_CACHE_TTL_SECONDS = 3600     # refetch the Webshare list after 1 hour
_FETCH_TIMEOUT_SECONDS = 10
_PAGE_SIZE = 100


class WebshareProxyManager:
    """Applies/removes a Webshare proxy in reaction to global rate limits."""

    def __init__(self, api_key: str | None):
        self.api_key = api_key
        self.http = None                # discord HTTPClient (set by attach)
        self.enabled = False
        self._proxy_url: str | None = None
        self._active_proxy: dict | None = None
        self._proxies: list[dict] = []
        self._proxies_fetched_at = 0.0
        self._lock = asyncio.Lock()
        self._session: aiohttp.ClientSession | None = None
        self._verify_task: asyncio.Task | None = None
        self._user_agent = "DiscordBot (https://discord.com, 2.7.1)"
        self._backup_proxy_urls: list[str] = []
        self._backup_proxy_ids: list[str] = []
        self._backup_proxy_index = 0
        self._backup_mode = "auto"
        self._backup_last_error: str | None = None
        self._backup_last_changed_at = time.time()
        self._failover_count = 0
        self._webshare_fallback_count = 0
        self._attached_bot_http = None
        self._hooked_session = None
        self._http_egress_blocked = False
        self._loop = None
        self._bot = None
        self._handoff_lock = asyncio.Lock()
        self._verify_interval = VERIFY_INTERVAL_SECONDS

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    def attach(self, bot) -> bool:
        """Bind to the bot's HTTP client and install the global-429 hook.

        Synchronous on purpose so it can run at import time in ``bot.py``.
        discord.py creates its aiohttp session lazily inside ``static_login``
        (i.e. during ``bot.start``), so when the session does not exist yet
        this wraps ``static_login`` and installs the hook the moment the real
        session is created.  Returns True when the failover is armed.
        """
        if not self.api_key and not self._backup_proxy_urls:
            return False
        self.http = bot.http
        self._bot = bot
        current_session = self._current_session()
        if self._attached_bot_http is bot.http:
            if current_session is not None and current_session is not self._hooked_session:
                self._install_hook(current_session)
            return True

        try:
            self._user_agent = bot.http.user_agent
        except Exception:
            pass

        session = self._current_session()
        if session is not None:
            self._install_hook(session)
            self._attached_bot_http = bot.http
            logging.info("ProxyManager", "Global rate-limit failover armed.")
            return True

        try:
            original_static_login = bot.http.static_login
        except AttributeError as exc:
            logging.error(
                "ProxyManager", f"Could not reach the Discord HTTP client: {exc}"
            )
            self.http = None
            return False

        manager = self

        async def wrapped_static_login(token):
            try:
                data = await original_static_login(token)
            except Exception as exc:
                response = getattr(exc, "response", None)
                error_body = getattr(exc, "text", "")
                if response is None or not await manager._is_cloudflare_block(response, error_body):
                    raise
                manager._http_egress_blocked = True
                await manager.enable(force_backup=True)
                if not manager.enabled:
                    raise
                # static_login creates a new aiohttp session each time. Close
                # the failed session before retrying so the retry doesn't leak it.
                failed_session = manager._current_session()
                if failed_session is not None and not failed_session.closed:
                    await failed_session.close()
                logging.warning(
                    "ProxyManager",
                    "Discord gateway login was denied by Cloudflare; retrying through a registered standby.",
                )
                data = await original_static_login(token)
                await manager._handoff_to_standby()
            try:
                session = manager._current_session()
                if session is not None:
                    manager._install_hook(session)
                    if manager.enabled and manager._proxy_url:
                        bot.http.proxy = manager._proxy_url
                        bot.http.proxy_auth = None
                    manager._attached_bot_http = bot.http
                    logging.info(
                        "ProxyManager", "Global rate-limit failover armed."
                    )
            except Exception as exc:
                logging.error(
                    "ProxyManager", f"Could not install the failover hook: {exc}"
                )
            return data

        bot.http.static_login = wrapped_static_login
        self._attached_bot_http = bot.http
        logging.info("ProxyManager", "Global rate-limit failover armed.")
        return True

    def _current_session(self):
        """The discord aiohttp session, or None while it does not exist yet."""
        if self.http is None:
            return None
        session = getattr(self.http, "_HTTPClient__session", None)
        if session is not None and hasattr(session, "_request"):
            return session
        return None

    def _install_hook(self, session) -> None:
        """Wrap Discord requests to detect global rate limits and Cloudflare blocks."""
        original_request = session._request
        manager = self

        async def hooked_request(method, url, **kwargs):
            resp = await original_request(method, url, **kwargs)
            try:
                if manager._should_monitor(str(url)):
                    blocked = await manager._is_cloudflare_block(resp)
                    if blocked:
                        manager._http_egress_blocked = True
                        await manager.enable(force_backup=True)
                        if manager.enabled:
                            await manager._handoff_to_standby()
                            # A Cloudflare denial is not retried by discord.py.
                            # Retry this request once over the already-armed standby.
                            resp.release()
                            retry_kwargs = dict(kwargs)
                            retry_kwargs["proxy"] = manager._proxy_url
                            retry_kwargs["proxy_auth"] = None
                            return await original_request(method, url, **retry_kwargs)
                    elif resp.status == 429 and resp.headers.get("X-RateLimit-Global"):
                        # discord.py sleeps and retries this global rate limit.
                        await manager.enable()
            except Exception as exc:
                logging.warning("ProxyManager", f"Could not apply Discord egress failover: {exc}")
            return resp

        session._request = hooked_request
        self._hooked_session = session

    def _should_monitor(self, url: str) -> bool:
        from urllib.parse import urlsplit

        hostname = (urlsplit(url).hostname or "").lower().rstrip(".")
        return hostname == "discord.com" or hostname.endswith((".discord.com", ".discordapp.com"))

    @staticmethod
    def _cloudflare_signature(status: int, headers, body: str) -> bool:
        if status not in {403, 429, 503}:
            return False
        server = str(headers.get("Server", "")).lower()
        ray_id = str(headers.get("CF-Ray", ""))
        body = body.lower()
        header_signature = "cloudflare" in server or bool(ray_id)
        body_signature = any(
            marker in body
            for marker in ("cloudflare", "cf-error-details", "cf-wrapper", "attention required")
        )
        if status == 429:
            # Cloudflare challenge HTML can arrive with proxy-stripped headers;
            # require a Cloudflare header or recognizable challenge markup/body.
            return header_signature or body_signature
        return header_signature and body_signature

    @classmethod
    def is_cloudflare_block(cls, response) -> bool:
        """Recognize explicit Cloudflare access-denial responses, not arbitrary errors."""
        body = getattr(response, "text", "")
        if not isinstance(body, str):
            body = ""
        return cls._cloudflare_signature(
            getattr(response, "status_code", getattr(response, "status", 0)),
            getattr(response, "headers", {}),
            body,
        )

    @classmethod
    async def _is_cloudflare_block(cls, response, body_fallback: str = "") -> bool:
        """Async HTTP response variant of the Cloudflare block detector."""
        status = getattr(response, "status", getattr(response, "status_code", 0))
        headers = getattr(response, "headers", {})
        if status not in {403, 429, 503}:
            return False
        body = getattr(response, "text", "")
        if callable(body):
            try:
                body = body()
                if hasattr(body, "__await__"):
                    body = await body
            except (AttributeError, RuntimeError, TypeError):
                body = ""
        if not isinstance(body, str) or not body:
            body = body_fallback
        return cls._cloudflare_signature(status, headers, body)

    def use_backup_proxy(self, backup_id: str | None = None, *, manual: bool = False) -> bool:
        """Immediately arm a registered standby for synchronous callers."""
        if not self._backup_proxy_urls:
            return False
        if backup_id is not None:
            try:
                self._backup_proxy_index = self._backup_proxy_ids.index(backup_id)
            except ValueError:
                return False
        url = self._backup_proxy_urls[self._backup_proxy_index % len(self._backup_proxy_urls)]
        self._backup_proxy_index = (self._backup_proxy_index + 1) % len(self._backup_proxy_urls)
        if self.http is not None:
            self.http.proxy = url
            self.http.proxy_auth = None
        self._proxy_url = url
        self._active_proxy = None
        self.enabled = True
        self._backup_mode = "standby"
        self._backup_last_error = None
        self._backup_last_changed_at = time.time()
        self._failover_count += 1
        self._http_egress_blocked = True
        logging.warning("ProxyManager", "Discord egress is blocked — routed through a registered standby instance.")
        self._ensure_verify_task()
        return True

    def status(self) -> dict:
        """Return non-secret failover state for the owner settings page."""
        active_backup = None
        if self._proxy_url in self._backup_proxy_urls:
            active_backup = self._backup_proxy_ids[self._backup_proxy_urls.index(self._proxy_url)]
        return {
            "mode": self._backup_mode,
            "enabled": self.enabled,
            "active_backup_id": active_backup,
            "using_webshare": self.enabled and self._active_proxy is not None,
            "webshare_available": bool(self.api_key),
            "webshare_endpoint": (
                f"{self._active_proxy.get('proxy_address')}:{self._active_proxy.get('port')}"
                if self._active_proxy else None
            ),
            "standby_count": len(self._backup_proxy_urls),
            "last_error": self._backup_last_error,
            "last_changed_at": self._backup_last_changed_at,
            "failover_count": self._failover_count,
            "webshare_fallback_count": self._webshare_fallback_count,
            "egress_blocked": self._http_egress_blocked,
        }

    def activate_backup(self, backup_id: str) -> bool:
        """Manually route Discord traffic through one registered standby."""
        self._backup_mode = "standby"
        return self.use_backup_proxy(backup_id, manual=True)

    async def select_failover(self, mode: str) -> bool:
        """Owner control: choose automatic standby-first, direct, or Webshare."""
        if mode not in {"auto", "off", "webshare"}:
            raise ValueError("Unsupported failover mode.")
        self._backup_mode = mode
        self._backup_last_error = None
        self._backup_last_changed_at = time.time()
        if mode == "off":
            self.disable()
            self._backup_mode = "off"
            return True
        if mode == "auto":
            self.disable()
            self._backup_mode = "auto"
            return True
        if not self.api_key:
            self._backup_mode = "auto"
            return False
        self.disable()
        self._backup_mode = "webshare"
        return await self._enable_webshare()

    async def control_backup(self, backup_id: str, action: str) -> bool:
        """Send an authenticated gateway ownership command to a registered standby."""
        from utils.backup_proxy import control_proof

        if action not in {"activate", "relinquish"}:
            raise ValueError("Unsupported standby control action.")
        try:
            index = self._backup_proxy_ids.index(backup_id)
        except ValueError:
            return False
        from urllib.parse import urlsplit
        origin = urlsplit(self._backup_proxy_urls[index])
        base_url = f"{origin.scheme}://{origin.netloc}"
        # Derive control authentication from the same deployment secrets used
        # to verify the standby; never send either raw secret over the network.
        import os
        from utils.backup_proxy import secret_key
        token = os.getenv("DISCORD_BOT_TOKEN", "")
        session_secret = os.getenv("SESSION_SECRET", "")
        if not token or not session_secret:
            return False
        key = secret_key(token, session_secret)
        nonce = os.urandom(32).hex()
        payload = {"action": action, "nonce": nonce, "proof": control_proof(key, action, nonce)}
        try:
            response = await asyncio.to_thread(
                requests.post, f"{base_url}/internal/backup/control", json=payload,
                timeout=12, allow_redirects=False,
            )
            result = response.json()
            return response.status_code == 200 and result.get("ok") is True
        except (requests.RequestException, ValueError, AttributeError):
            return False

    async def _probe_backup(self, url: str) -> dict | None:
        """Read live health and traffic counters from a registered standby."""
        from urllib.parse import urlsplit

        origin = urlsplit(url)
        health_url = f"{origin.scheme}://{origin.netloc}/health"
        try:
            response = await asyncio.to_thread(requests.get, health_url, timeout=4, allow_redirects=False)
            payload = response.json()
            if response.status_code != 200 or payload.get("service") != "niko-backup-proxy":
                return None
            return payload
        except (requests.RequestException, ValueError, AttributeError):
            return None

    async def _enable_webshare(self) -> bool:
        if not self.api_key or self.http is None:
            return False
        proxies = self._cached_proxies()
        if not proxies:
            try:
                proxies = await asyncio.wait_for(self._fetch_proxies(), timeout=_FETCH_TIMEOUT_SECONDS)
            except Exception as exc:
                self._backup_last_error = str(exc)[:240]
                logging.error("ProxyManager", f"Failed to fetch Webshare proxies: {exc}")
                return False
        if not proxies:
            self._backup_last_error = "No usable Webshare proxies were returned."
            return False
        self._apply_proxy(random.choice(proxies))
        self._backup_mode = "webshare" if self._backup_mode != "auto" else "auto"
        self._backup_last_error = None
        self._webshare_fallback_count += 1
        return True

    async def activate_backup_async(self, backup_id: str) -> bool:
        """Manually probe then activate a specific standby."""
        try:
            index = self._backup_proxy_ids.index(backup_id)
        except ValueError:
            return False
        if not await self._probe_backup(self._backup_proxy_urls[index]):
            self._backup_last_error = "Standby health check failed."
            return False
        self._backup_mode = "standby"
        return self.use_backup_proxy(backup_id, manual=True)

    async def rotate_backup(self) -> bool:
        """Move to the next healthy standby, then use Webshare if needed."""
        active_backup_id = self.status()["active_backup_id"]
        active_index = self._backup_proxy_ids.index(active_backup_id) if active_backup_id in self._backup_proxy_ids else self._backup_proxy_index
        previous_mode = self._backup_mode
        self.disable()
        if self._backup_proxy_urls:
            for offset in range(1, len(self._backup_proxy_urls) + 1):
                index = (active_index + offset) % len(self._backup_proxy_urls)
                if await self._probe_backup(self._backup_proxy_urls[index]):
                    self._backup_mode = "auto"
                    self._backup_proxy_index = index
                    return self.use_backup_proxy(self._backup_proxy_ids[index])
        self._backup_mode = "auto"
        if self.api_key:
            return await self._enable_webshare()
        self._backup_mode = previous_mode
        self._backup_last_error = "No healthy standby or Webshare proxy is available."
        return False

    async def probe_backups(self) -> dict[str, dict | None]:
        """Return live health and usage results for all registered standbys."""
        results = await asyncio.gather(*(self._probe_backup(url) for url in self._backup_proxy_urls))
        return dict(zip(self._backup_proxy_ids, results))

    async def prefetch(self) -> None:
        """Fetch the Webshare proxy list once at startup (best effort).

        This makes the first rate-limit failover instant — no Webshare API
        round-trip is needed in the middle of a 429.
        """
        if not self.api_key:
            return
        try:
            proxies = await asyncio.wait_for(
                self._fetch_proxies(), timeout=_FETCH_TIMEOUT_SECONDS
            )
            if proxies:
                logging.info(
                    "ProxyManager",
                    f"Prefetched {len(proxies)} Webshare proxies — failover will be instant.",
                )
        except Exception as exc:
            logging.warning(
                "ProxyManager",
                f"Startup proxy prefetch failed (will retry on first rate limit): {exc}",
            )

    async def close(self) -> None:
        """Cancel the verification loop and release the helper session."""
        if self._verify_task is not None:
            self._verify_task.cancel()
            try:
                await self._verify_task
            except (asyncio.CancelledError, Exception):
                pass
            self._verify_task = None
        self.disable()
        if self._session is not None:
            await self._session.close()
            self._session = None

    # ── Proxy control ─────────────────────────────────────────────────────────
    def requests_proxy_kwargs(self) -> dict:
        """Return proxy kwargs for requests-based Discord OAuth/API calls."""
        if not self.enabled or not self._proxy_url:
            return {}
        return {"proxies": {"http": self._proxy_url, "https": self._proxy_url}}

    async def _handoff_to_standby(self) -> bool:
        """Relinquish primary gateway before requesting standby activation."""
        backup_id = self.status().get("active_backup_id")
        handoff = getattr(self._bot, "gateway_handoff", None)
        if not backup_id or handoff is None:
            return False
        async with self._handoff_lock:
            if handoff.active.is_set():
                await handoff.relinquish()
            if await self.control_backup(backup_id, "activate"):
                return True
            self._backup_last_error = "Healthy standby did not accept the gateway handoff."
            await handoff.activate()
            return False

    async def check_direct_egress(self) -> bool:
        """Probe Discord before gateway login and arm standby on a Cloudflare block."""
        self._loop = asyncio.get_running_loop()
        try:
            response = await asyncio.to_thread(
                requests.get,
                GATEWAY_PROBE_URL,
                timeout=_FETCH_TIMEOUT_SECONDS,
                allow_redirects=False,
            )
        except Exception as exc:
            logging.warning("ProxyManager", f"Direct Discord egress probe failed: {exc}")
            return False
        if not await self._is_cloudflare_block(response):
            return False
        self._http_egress_blocked = True
        await self.enable(force_backup=True)
        if self.enabled:
            await self._handoff_to_standby()
        return self.enabled

    def set_backup_proxies(self, proxy_urls: list[str], backup_ids: list[str] | None = None) -> None:
        """Set authenticated standby proxy URLs registered by the bot owner."""
        valid = [(backup_ids[index] if backup_ids and index < len(backup_ids) else str(index), url)
                 for index, url in enumerate(proxy_urls)
                 if isinstance(url, str) and url.startswith("https://")]
        self._backup_proxy_ids = [item[0] for item in valid]
        self._backup_proxy_urls = [item[1] for item in valid]
        self._backup_proxy_index = 0
        if self._proxy_url and self._proxy_url.startswith("https://") and self._proxy_url not in self._backup_proxy_urls:
            self.disable()
        if not self._backup_proxy_urls and self._backup_mode == "standby":
            self.disable()

    async def enable(self, *, force_backup: bool = False) -> None:
        """Route through Webshare or an authenticated standby after an egress block."""
        self._loop = asyncio.get_running_loop()
        if self.http is None:
            return
        if self.enabled and self._proxy_url and not force_backup:
            return
        async with self._lock:
            if self.enabled and self._proxy_url and not force_backup:
                return
            if self._backup_mode == "off":
                return
            if self._backup_mode == "standby" and self.enabled:
                return
            if self._backup_mode == "webshare":
                if await self._enable_webshare():
                    return
                return

            if self._backup_mode == "auto" or force_backup:
                start_index = self._backup_proxy_index
                for offset in range(len(self._backup_proxy_urls)):
                    index = (start_index + offset) % len(self._backup_proxy_urls)
                    if await self._probe_backup(self._backup_proxy_urls[index]):
                        self._backup_proxy_index = index
                        if self.use_backup_proxy():
                            return
                self._backup_last_error = "No registered standby passed its health check."
                self._backup_mode = "auto"
                if await self._enable_webshare():
                    self._backup_mode = "auto"
                    return
            logging.warning("ProxyManager", "No healthy standby or Webshare proxy is available — staying on the direct IP.")

    def disable(self) -> None:
        """Drop the proxy and go back to the direct IP immediately."""
        if self.http is not None:
            self.http.proxy = None
            self.http.proxy_auth = None
        self.enabled = False
        self._proxy_url = None
        self._active_proxy = None
        if self._backup_mode == "standby":
            self._backup_mode = "auto"

    def rotate(self) -> None:
        """Switch to another cached proxy (used when the active one errors)."""
        proxies = self._cached_proxies()
        if self._active_proxy is None and len(self._backup_proxy_urls) > 1:
            self._backup_proxy_index = (self._backup_proxy_index + 1) % len(self._backup_proxy_urls)
            url = self._backup_proxy_urls[self._backup_proxy_index]
            self._proxy_url = url
            self._backup_last_changed_at = time.time()
            self._failover_count += 1
            if self.http is not None:
                self.http.proxy = url
                self.http.proxy_auth = None
            return
        if len(proxies) > 1 and self._active_proxy is not None:
            candidates = [p for p in proxies if p is not self._active_proxy]
            if candidates:
                self._apply_proxy(random.choice(candidates))

    def _apply_proxy(self, proxy: dict) -> None:
        self._proxy_url = (
            f"http://{proxy['username']}:{proxy['password']}"
            f"@{proxy['proxy_address']}:{proxy['port']}"
        )
        self._backup_last_error = None
        self._backup_last_changed_at = time.time()
        self._active_proxy = proxy
        if self._backup_mode == "auto":
            self._backup_last_changed_at = time.time()
        if self.http is not None:
            self.http.proxy = self._proxy_url
            self.http.proxy_auth = None
        self.enabled = True
        logging.warning(
            "ProxyManager",
            f"Global rate limit detected — routed through Webshare proxy "
            f"{proxy['proxy_address']}:{proxy['port']}.",
        )
        self._ensure_verify_task()

    def _cached_proxies(self) -> list[dict]:
        if (
            self._proxies
            and time.monotonic() - self._proxies_fetched_at < PROXY_CACHE_TTL_SECONDS
        ):
            return self._proxies
        return []

    # ── Webshare API ──────────────────────────────────────────────────────────
    def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _fetch_proxies(self) -> list[dict]:
        """Query the Webshare proxy list and cache the valid proxies.

        Webshare requires the ``mode`` parameter on this endpoint, so the
        list is fetched in "direct" mode first (datacenter plans return a
        usable ``proxy_address``/``port``/credentials per proxy).  If Webshare
        rejects that — e.g. a residential plan that only supports backbone —
        the request is retried in "backbone" mode, where all connections go
        through ``p.webshare.io`` on a backbone port instead.
        """
        session = self._ensure_session()
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Accept": "application/json",
        }
        results: list[dict] = []
        for mode in ("direct", "backbone"):
            data = await self._request_proxy_list(session, headers, mode)
            if data is None:
                continue  # Webshare rejected this mode — try the other one
            results = self._usable_proxies(data, mode)
            if results:
                break

        self._proxies = results
        self._proxies_fetched_at = time.monotonic()
        logging.info("ProxyManager", f"Fetched {len(results)} valid Webshare proxies.")
        return results

    async def _request_proxy_list(self, session, headers, mode) -> dict | None:
        """GET one page of the Webshare proxy list for a connection mode.

        Returns the parsed JSON on success, or None when Webshare rejects the
        ``mode`` with a 400 (e.g. the plan requires backbone instead of
        direct).  Any other failure raises so the caller can log it.
        """
        url = f"{PROXY_LIST_URL}?mode={mode}&page=1&page_size={_PAGE_SIZE}"
        async with session.get(url, headers=headers) as resp:
            body = await resp.text()
            detail = body.strip()[:300]
            if resp.status == 400:
                logging.warning(
                    "ProxyManager",
                    f"Webshare rejected mode={mode} (HTTP 400): {detail}",
                )
                return None
            if resp.status != 200:
                raise RuntimeError(
                    f"Webshare API returned HTTP {resp.status}: {detail}"
                )
        try:
            return json.loads(body)
        except ValueError as exc:
            raise RuntimeError(
                f"Webshare API returned invalid JSON: {detail}"
            ) from exc

    def _usable_proxies(self, data: dict, mode: str) -> list[dict]:
        """The valid, connectable proxies from a Webshare list response."""
        usable: list[dict] = []
        for p in data.get("results", []):
            if not (p.get("valid") and p.get("username") and p.get("password")):
                continue
            if mode == "backbone":
                # Backbone entries carry no per-proxy address; everything
                # connects through p.webshare.io on a backbone port.
                p["proxy_address"] = _BACKBONE_ADDRESS
                p["port"] = self._backbone_port(p.get("port"))
                usable.append(p)
            elif p.get("proxy_address"):
                usable.append(p)
        return usable

    @staticmethod
    def _backbone_port(port) -> int:
        """A usable backbone-mode port for username/password auth."""
        try:
            port = int(port)
        except (TypeError, ValueError):
            return _BACKBONE_PORT_FALLBACK
        if port in _BACKBONE_PORTS or _BACKBONE_PORT_MIN <= port <= _BACKBONE_PORT_MAX:
            return port
        return _BACKBONE_PORT_FALLBACK

    # ── Verification loop ─────────────────────────────────────────────────────
    def _ensure_verify_task(self) -> None:
        if self._verify_task is not None and not self._verify_task.done():
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = self._loop
            if loop is None or not loop.is_running():
                return
            loop.call_soon_threadsafe(self._start_verify_task)
            return
        self._loop = loop
        self._start_verify_task()

    def _start_verify_task(self) -> None:
        if self._verify_task is None or self._verify_task.done():
            self._verify_task = asyncio.create_task(self._verify_loop())

    async def _verify_loop(self) -> None:
        """Probe direct egress periodically and coordinate gateway ownership return."""
        while True:
            try:
                await asyncio.sleep(self._verify_interval)
                if not self.enabled:
                    return
                handoff = getattr(self._bot, "gateway_handoff", None)
                if handoff is not None and not handoff.active.is_set():
                    if not await self._probe_direct():
                        continue
                    async with self._handoff_lock:
                        if handoff.active.is_set():
                            continue
                        backup_id = self.status().get("active_backup_id")
                        if not backup_id:
                            continue
                        if not await self.control_backup(backup_id, "relinquish"):
                            continue
                        handoff.refresh_caches_on_ready = True
                        await handoff.activate()
                        self.disable()
                        try:
                            await asyncio.wait_for(handoff.connected.wait(), timeout=45)
                        except asyncio.TimeoutError:
                            await handoff.relinquish()
                            if not await self.control_backup(backup_id, "activate"):
                                handoff.refresh_caches_on_ready = True
                                await handoff.activate()
                                logging.warning("ProxyManager", "Standby activation failed after primary timeout; continuing primary reconnect attempts.")
                                continue
                            self.use_backup_proxy(backup_id)
                            logging.warning("ProxyManager", "Direct egress probe passed but primary gateway could not connect; standby remains active.")
                            continue
                        logging.success("ProxyManager", "Primary gateway restored; standby returned to ready state.")
                        return
                elif handoff is None and await self._probe_direct():
                    self.disable()
                    return
            except asyncio.CancelledError:
                return
            except Exception as exc:
                logging.warning("ProxyManager", f"Gateway probe failed: {exc}")

    async def _probe_direct(self) -> bool:
        """One unproxied request to Discord's gateway endpoint.

        Returns True only when the direct IP provably got a non-429 answer,
        i.e. the global rate limit has cleared.  Any 429 (or network error)
        keeps the proxy enabled — the limit is only considered lifted when
        the probe can confirm it.
        """
        session = self._ensure_session()
        async with session.get(
            GATEWAY_PROBE_URL,
            headers={"User-Agent": self._user_agent},
            proxy=None,
        ) as resp:
            await resp.read()
            return resp.status < 400