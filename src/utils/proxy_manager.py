"""
Automated Webshare proxy failover for Discord global rate limits.

When Discord globally rate limits the bot's IP the manager immediately fetches a
proxy from the Webshare API and routes the bot's HTTP client through it.  Both
REST requests and gateway websocket reconnects pick the proxy up through
``client.http.proxy`` — discord.py already applies that attribute on every
request and websocket connect.

A global limit is recognised from every signal Discord leaves behind, because
relying on one of them is what let the limit pass unnoticed: the
``X-RateLimit-Scope: global`` header, the older ``X-RateLimit-Global`` header,
and the ``"global": true`` field of the 429 body (which is the only signal
discord.py itself reads).  A Cloudflare ``Error 1015`` throttle is the same
recovery — Discord answers it over a different egress IP — so the manager arms
the proxy for that too.  While a proxy is already active, another global limit
rotates to a different proxy instead of reusing the IP that is being limited.

Interaction callbacks are deliberately *not* this manager's problem: Discord
never counts them against the global limit, and
``utils.interaction_priority`` keeps them from queueing behind it.

While the proxy is active a background task performs exactly one tiny
*unproxied* request to Discord's gateway endpoint every 10 minutes.  The
moment that probe confirms the direct IP is no longer rate limited (any
non-429 response), the proxy is disabled again so the Webshare 1 GB/month
bandwidth allowance is only consumed while it is genuinely needed.

Webshare proxy failover is independent of standby backend failover.
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
ROTATE_COOLDOWN_SECONDS = 20       # at most one rotation per limit burst
_FETCH_TIMEOUT_SECONDS = 10
_PAGE_SIZE = 100


class _RelayedAiohttpResponse:
    """Minimal aiohttp response contract needed by discord.py HTTPClient."""

    def __init__(self, status: int, headers: dict, body: bytes):
        from multidict import CIMultiDict

        self.status = status
        self.headers = CIMultiDict(headers)
        self._body = body

    async def text(self, encoding: str = "utf-8") -> str:
        return self._body.decode(encoding, errors="replace")

    def release(self) -> None:
        return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        self.release()


def _header_is_true(value) -> bool:
    """Whether a rate-limit flag header is set.

    Discord sends ``true`` and discord.py reads the same fact from the body, so a
    present-but-false flag has to stay false rather than counting as a limit.
    """
    if value is None:
        return False
    return str(value).strip().lower() not in {"", "0", "false", "none"}


async def _read_response_text(response) -> str:
    """Read a response body without consuming it for the caller.

    aiohttp caches what it reads, so discord.py's own ``json_or_text`` still sees
    the full body afterwards.  A response object without an async ``text`` (or one
    that fails to read) simply yields no body rather than raising.
    """
    text = getattr(response, "text", None)
    if not callable(text):
        return ""
    try:
        return await text()
    except Exception:
        return ""


async def is_global_rate_limit(response) -> bool:
    """Whether a 429 hit the application-wide limit rather than one bucket.

    ``X-RateLimit-Scope: global`` is the current header, ``X-RateLimit-Global``
    the older one, and a 429 body carrying ``"global": true`` is what discord.py
    itself treats as global.  Any of the three counts, so a limit that only shows
    up in one of them still arms the proxy.
    """
    if getattr(response, "status", None) != 429:
        return False
    headers = getattr(response, "headers", None) or {}
    if str(headers.get("X-RateLimit-Scope", "")).strip().lower() == "global":
        return True
    if _header_is_true(headers.get("X-RateLimit-Global")):
        return True
    body = (await _read_response_text(response)).strip()
    if not body.startswith("{"):
        return False
    try:
        payload = json.loads(body)
    except ValueError:
        return False
    return isinstance(payload, dict) and bool(payload.get("global"))


async def cloudflare_throttle(response) -> str | None:
    """Cloudflare's own interstitial signature on a 429, or None.

    Discord serves every response through Cloudflare, so ``Server: cloudflare``
    and ``CF-Ray`` prove nothing on their own.  Only Cloudflare's block/challenge
    page — or its ``cf-mitigated`` header, or a numeric ``error code: 10xx`` — is a
    throttle, and that is the event a different egress IP clears.  A 429 is a
    throttle rather than a denied egress, which is why the standby manager leaves
    its recovery to this proxy failover.
    """
    if getattr(response, "status", None) != 429:
        return None
    from utils.standby_manager import StandbyFailoverManager

    body = await _read_response_text(response)
    return StandbyFailoverManager.cloudflare_interstitial(response, body)


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
        self._mode = "auto"
        self._last_error: str | None = None
        self._attached_bot_http = None
        self._hooked_session = None
        self._loop = None
        self._verify_interval = VERIFY_INTERVAL_SECONDS
        self._rotated_at = 0.0

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    def attach(self, bot) -> bool:
        """Bind to the bot's HTTP client and install the global-429 hook.

        Synchronous on purpose so it can run at import time in ``bot.py``.
        The standby manager exclusively wraps ``static_login`` and installs
        this manager's request hook after the aiohttp session is created.
        Returns True when proxy failover is armed.
        """
        if not self.api_key:
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
        # StandbyFailoverManager exclusively owns static_login so it can
        # prioritize standby handoff before falling back to this proxy manager.
        # It attaches its aiohttp hook during static_login; attach again after
        # login to install this manager's hook for subsequent requests.
        self._attached_bot_http = bot.http
        logging.info("ProxyManager", "Global rate-limit failover armed.")
        return True

    def _redact_proxy_credentials(self, message: str) -> str:
        """Remove embedded proxy usernames/passwords from client error text."""
        from urllib.parse import urlsplit

        for proxy_url in {self._proxy_url}:
            if not proxy_url:
                continue
            parts = urlsplit(proxy_url)
            if parts.hostname:
                safe_authority = parts.hostname
                if parts.port is not None:
                    safe_authority += f":{parts.port}"
                message = message.replace(proxy_url, f"{parts.scheme}://{safe_authority}")
        return message

    def _current_session(self):
        """The discord aiohttp session, or None while it does not exist yet."""
        if self.http is None:
            return None
        session = getattr(self.http, "_HTTPClient__session", None)
        if session is not None and hasattr(session, "_request"):
            return session
        return None

    def _install_hook(self, session) -> None:
        """Wrap Discord requests to detect rate limits and apply configured routing."""
        original_request = session._request
        manager = self

        async def hooked_request(method, url, **kwargs):
            try:
                resp = await original_request(method, url, **kwargs)
            except Exception as exc:
                # A proxy that cannot be reached would otherwise keep every
                # request failing until the 10-minute recovery probe runs.
                if manager.enabled and kwargs.get("proxy") and isinstance(exc, (aiohttp.ClientError, OSError)):
                    try:
                        manager.rotate(reason="The active Webshare proxy refused the connection", immediate=True)
                    except Exception:
                        # The caller has to see the connection error it actually hit.
                        pass
                raise
            if manager._should_monitor(str(url)):
                try:
                    await manager.handle_rate_limit(resp)
                except Exception as exc:
                    # Monitoring must never turn a Discord response into a bot
                    # error: the caller still gets the response it asked for.
                    manager._last_error = str(exc)[:240]
                    logging.warning("ProxyManager", f"Rate-limit handling failed: {exc}")
            return resp

        session._request = hooked_request
        self._hooked_session = session

    async def handle_rate_limit(self, response) -> None:
        """Move egress to Webshare when Discord or Cloudflare limits this IP.

        Called for every Discord response, so the two checks are cheap: they only
        read a body on a 429, and an ordinary 200 returns immediately.
        """
        if await is_global_rate_limit(response):
            await self._arm_for_limit("Discord global rate limit")
            return
        throttle = await cloudflare_throttle(response)
        if throttle:
            await self._arm_for_limit(f"Cloudflare throttle ({throttle})")

    async def _arm_for_limit(self, reason: str) -> None:
        """Use a proxy for a limited direct IP, or a fresh one while proxied.

        The limit follows the egress IP, so a limit that arrives while a proxy is
        already active means that proxy's IP is the limited one: rotating keeps
        the bot off it without ever falling back to the direct IP.
        """
        if not self.api_key or self.http is None:
            return
        if self.enabled and self._active_proxy is not None:
            self.rotate(reason=reason)
            return
        await self.enable(reason=reason)

    def _should_monitor(self, url: str) -> bool:
        from urllib.parse import urlsplit

        hostname = (urlsplit(url).hostname or "").lower().rstrip(".")
        return hostname == "discord.com" or hostname.endswith((".discord.com", ".discordapp.com"))

    async def _enable_webshare(self, reason: str | None = None) -> bool:
        if not self.api_key or self.http is None:
            return False
        proxies = self._cached_proxies()
        if not proxies:
            try:
                proxies = await asyncio.wait_for(self._fetch_proxies(), timeout=_FETCH_TIMEOUT_SECONDS)
            except Exception as exc:
                self._last_error = str(exc)[:240]
                logging.error("ProxyManager", f"Failed to fetch Webshare proxies: {exc}")
                return False
        if not proxies:
            self._last_error = "No usable Webshare proxies were returned."
            return False
        self._apply_proxy(random.choice(proxies), reason=reason or "Discord global rate limit")
        self._rotated_at = time.monotonic()
        self._last_error = None
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

    # ── Webshare proxy controls ────────────────────────────────────────────────
    async def enable(self, reason: str | None = None) -> None:
        """Fetch and activate a Webshare proxy after a Discord global rate limit."""
        self._loop = asyncio.get_running_loop()
        if self.http is None:
            return
        if self.enabled and self._active_proxy is not None:
            return
        async with self._lock:
            if self.enabled and self._active_proxy is not None:
                return
            if await self._enable_webshare(reason):
                return
            logging.warning("ProxyManager", "No Webshare proxy is available — staying on the direct IP.")

    def disable(self) -> None:
        """Drop the Webshare proxy and restore direct egress."""
        if self.http is not None:
            self.http.proxy = None
            self.http.proxy_auth = None
        self.enabled = False
        self._proxy_url = None
        self._active_proxy = None

    def rotate(self, reason: str = "The active Webshare proxy is limited", immediate: bool = False) -> None:
        """Switch to another cached proxy (one that is limited, blocked or down).

        Rate-limited egress arrives in bursts, so rotations are spaced out: one
        fresh IP per limit event is the recovery, and rotating on every 429 in the
        same burst would only burn through the proxy list.  A proxy that cannot be
        connected to is the exception — it is retried immediately, because the
        request that found it has already failed.
        """
        if self._active_proxy is None:
            return
        if not immediate and time.monotonic() - self._rotated_at < ROTATE_COOLDOWN_SECONDS:
            return
        # Compare endpoints rather than object identity: a refreshed Webshare list
        # holds new dicts for the same proxies, and rotating onto the IP that is
        # being limited would recover nothing.
        active = (self._active_proxy.get("proxy_address"), self._active_proxy.get("port"))
        candidates = [
            proxy for proxy in self._cached_proxies()
            if (proxy.get("proxy_address"), proxy.get("port")) != active
        ]
        if not candidates:
            return
        self._apply_proxy(random.choice(candidates), reason=reason)
        self._rotated_at = time.monotonic()

    def _apply_proxy(self, proxy: dict, reason: str = "Discord global rate limit") -> None:
        self._proxy_url = (
            f"http://{proxy['username']}:{proxy['password']}"
            f"@{proxy['proxy_address']}:{proxy['port']}"
        )
        self._last_error = None
        self._active_proxy = proxy
        if self.http is not None:
            self.http.proxy = self._proxy_url
            self.http.proxy_auth = None
        self.enabled = True
        logging.warning(
            "ProxyManager",
            f"{reason} — routed through Webshare proxy "
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
        """Disable Webshare once direct Discord egress has recovered."""
        while True:
            try:
                await asyncio.sleep(self._verify_interval)
                if not self.enabled:
                    return
                if await self._probe_direct():
                    self.disable()
                    logging.success("ProxyManager", "Direct Discord egress restored; Webshare proxy disabled.")
                    return
            except asyncio.CancelledError:
                return
            except Exception as exc:
                logging.warning("ProxyManager", f"Direct egress probe failed: {exc}")

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