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

The system is opt-in: without a ``WEBSHARE_API_KEY`` environment variable it
stays completely dormant and nothing is patched.
"""

from __future__ import annotations

import asyncio
import os
import random
import time

import aiohttp

from utils import logging

# ── Config ───────────────────────────────────────────────────────────────────
WEBSHARE_API_KEY_ENV = "WEBSHARE_API_KEY"
PROXY_LIST_URL = "https://proxy.webshare.io/api/v2/proxy/list/"
GATEWAY_PROBE_URL = "https://discord.com/api/v10/gateway"

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

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    def attach(self, bot) -> bool:
        """Bind to the bot's HTTP client and install the global-429 hook.

        Synchronous on purpose so it can run at import time in ``bot.py``.
        discord.py creates its aiohttp session lazily inside ``static_login``
        (i.e. during ``bot.start``), so when the session does not exist yet
        this wraps ``static_login`` and installs the hook the moment the real
        session is created.  Returns True when the failover is armed.
        """
        if not self.api_key:
            return False

        self.http = bot.http
        try:
            self._user_agent = bot.http.user_agent
        except Exception:
            pass

        session = self._current_session()
        if session is not None:
            self._install_hook(session)
            logging.info("ProxyManager", "Global rate-limit failover armed (Webshare).")
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
            data = await original_static_login(token)
            try:
                session = manager._current_session()
                if session is not None:
                    manager._install_hook(session)
                    logging.info(
                        "ProxyManager", "Global rate-limit failover armed (Webshare)."
                    )
            except Exception as exc:
                logging.error(
                    "ProxyManager", f"Could not install the failover hook: {exc}"
                )
            return data

        bot.http.static_login = wrapped_static_login
        logging.info("ProxyManager", "Global rate-limit failover armed (Webshare).")
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
        """Wrap the session so a global 429 enables the proxy immediately."""
        original_request = session._request
        manager = self

        async def hooked_request(method, url, **kwargs):
            resp = await original_request(method, url, **kwargs)
            try:
                if (
                    resp.status == 429
                    and resp.headers.get("X-RateLimit-Global")
                    and manager._should_monitor(str(url))
                ):
                    # discord.py will sleep + retry this request after we
                    # return; enable the proxy first so that retry goes
                    # through the proxy instead of the rate-limited IP.
                    await manager.enable()
            except Exception:
                pass
            return resp

        session._request = hooked_request

    def _should_monitor(self, url: str) -> bool:
        return "discord.com" in url or "discordapp.com" in url

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
    async def enable(self) -> None:
        """Fetch a Webshare proxy and route the bot through it (idempotent)."""
        if not self.api_key or self.http is None:
            return
        if self.enabled and self._proxy_url:
            return
        async with self._lock:
            if self.enabled and self._proxy_url:
                return

            proxies = self._cached_proxies()
            if not proxies:
                try:
                    proxies = await asyncio.wait_for(
                        self._fetch_proxies(), timeout=_FETCH_TIMEOUT_SECONDS
                    )
                except Exception as exc:
                    logging.error("ProxyManager", f"Failed to fetch Webshare proxies: {exc}")
                    return
            if not proxies:
                logging.warning(
                    "ProxyManager",
                    "No valid Webshare proxies available — staying on the direct IP.",
                )
                return

            self._apply_proxy(random.choice(proxies))

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
        """Query the Webshare proxy list and cache the valid proxies."""
        session = self._ensure_session()
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Accept": "application/json",
        }
        async with session.get(
            f"{PROXY_LIST_URL}?page=1&page_size={_PAGE_SIZE}",
            headers=headers,
        ) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Webshare API returned HTTP {resp.status}")
            data = await resp.json()

        results = [
            p
            for p in data.get("results", [])
            if p.get("valid")
            and p.get("proxy_address")
            and p.get("username")
            and p.get("password")
        ]
        self._proxies = results
        self._proxies_fetched_at = time.monotonic()
        logging.info("ProxyManager", f"Fetched {len(results)} valid Webshare proxies.")
        return results

    # ── Verification loop ─────────────────────────────────────────────────────
    def _ensure_verify_task(self) -> None:
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