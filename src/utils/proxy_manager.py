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
        self._backup_proxy_index = 0
        self._attached_bot_http = None
        self._hooked_session = None
        self._http_egress_blocked = False
        self._loop = None

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
                if response is None or not await manager._is_cloudflare_block(response):
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
        if "cloudflare" not in server and not ray_id:
            return False
        # A Cloudflare 429 with a Ray ID/server header is an explicit edge
        # response even when discord.py only surfaces the generic HTML shell.
        if status == 429:
            return True
        body = body.lower()
        return "cloudflare" in body or "attention required" in body or "access denied" in body

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
    async def _is_cloudflare_block(cls, response) -> bool:
        """Async HTTP response variant of the Cloudflare block detector."""
        status = getattr(response, "status", 0)
        headers = getattr(response, "headers", {})
        if status not in {403, 429, 503}:
            return False
        server = str(headers.get("Server", "")).lower()
        ray_id = str(headers.get("CF-Ray", ""))
        if "cloudflare" not in server and not ray_id:
            return False
        try:
            body = await response.text()
        except (AttributeError, RuntimeError, TypeError):
            body = ""
        return cls._cloudflare_signature(status, headers, str(body))

    def use_backup_proxy(self) -> bool:
        """Immediately arm the next registered standby for synchronous callers."""
        if not self._backup_proxy_urls:
            return False
        url = self._backup_proxy_urls[self._backup_proxy_index % len(self._backup_proxy_urls)]
        self._backup_proxy_index += 1
        if self.http is not None:
            self.http.proxy = url
            self.http.proxy_auth = None
        self._proxy_url = url
        self._active_proxy = None
        self.enabled = True
        self._http_egress_blocked = True
        logging.warning("ProxyManager", "Discord egress is blocked — routed through a registered standby instance.")
        self._ensure_verify_task()
        return True

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
        return self.enabled

    def set_backup_proxies(self, proxy_urls: list[str]) -> None:
        """Set authenticated standby proxy URLs registered by the bot owner."""
        self._backup_proxy_urls = [url for url in proxy_urls if isinstance(url, str) and url.startswith("https://")]
        self._backup_proxy_index = 0
        if self._proxy_url and self._proxy_url.startswith("https://") and self._proxy_url not in self._backup_proxy_urls:
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

            proxies = self._cached_proxies() if self.api_key and not force_backup else []
            if self.api_key and not force_backup and not proxies:
                try:
                    proxies = await asyncio.wait_for(
                        self._fetch_proxies(), timeout=_FETCH_TIMEOUT_SECONDS
                    )
                except Exception as exc:
                    logging.error("ProxyManager", f"Failed to fetch Webshare proxies: {exc}")
            if proxies:
                self._apply_proxy(random.choice(proxies))
                return
            if force_backup and self.enabled:
                self.disable()
            if self.use_backup_proxy():
                return
            logging.warning("ProxyManager", "No Webshare proxy or registered standby is available — staying on the direct IP.")

    def disable(self) -> None:
        """Drop the proxy and go back to the direct IP immediately."""
        if self.http is not None:
            self.http.proxy = None
            self.http.proxy_auth = None
        self.enabled = False
        self._proxy_url = None
        self._active_proxy = None

    def rotate(self) -> None:
        """Switch to another cached proxy (used when the active one errors)."""
        proxies = self._cached_proxies()
        if self._active_proxy is None and len(self._backup_proxy_urls) > 1:
            self._backup_proxy_index += 1
            url = self._backup_proxy_urls[self._backup_proxy_index % len(self._backup_proxy_urls)]
            self._proxy_url = url
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
        self._active_proxy = proxy
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
        """Probe the direct IP every 10 minutes until the limit has cleared."""
        while True:
            try:
                await asyncio.sleep(VERIFY_INTERVAL_SECONDS)
                if not self.enabled:
                    return
                if await self._probe_direct():
                    logging.success(
                        "ProxyManager",
                        "Direct IP confirmed no longer rate limited — proxy disabled.",
                    )
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