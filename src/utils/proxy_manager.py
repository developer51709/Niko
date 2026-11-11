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

A proxy Cloudflare answers with ``Error 1015`` is *banned around*, not rotated
past once: that block follows the proxy's own IP, so the manager records the
endpoint and never selects it again for the rest of the ban window.  Without
that memory rotation was random over the whole list — the same banned proxy
came back around, every burst re-tried the IP Cloudflare had just refused, and
the console repeated one failure with no progress behind it.  When every proxy
the plan offers is blocked the manager says so once and stopsrotating instead of looping through them.

A block is only charged to the proxy whose address Cloudflare refused.  The
block page names it when it can, and when it does not the proxy is asked what
address it egresses from (``_probe_egress``); a mismatch or an unanswered check
keeps the proxy in rotation, so a clean endpoint is never blacklisted for a
refusal that was not its own.

That record is also written to ``data/proxy_bans.json``: the supervisor restarts
the bot child when a blocked login kills it, and a fresh process used to forget
which proxies had just been refused, so every restart walked back onto the same
two banned IPs.  A blocked login now walks the whole available list in one
process (``login_with_failover`` sizes its attempts from the proxies that are
left) and skips whatever earlier processes already found blocked.


The login request is the one Discord call the request hook cannot watch —
discord.py builds its session inside ``login()`` — so ``login_with_failover``
reads the block from the login exception, arms the proxy, and retries in the
same process instead of dying into a restart loop that repeats the block.

Interaction callbacks are deliberately *not* this manager's problem: Discord
never counts them against the global limit, and
``utils.interaction_priority`` keeps them from queueing behind it.

discord.py reads ``http.proxy`` for its own REST calls, but not for webhook
executions: its webhook adapter takes the raw aiohttp session and passes
``proxy=None``, so the logging cog's webhook entries left the host's own IP and
were answered with Cloudflare's ``Error 1015`` while every other call was
already proxied. The session hook therefore gives a Discord API request that
carries no proxy of its own the armed one; CDN downloads keep the direct route
so the Webshare allowance is only spent on the calls the IP is banned for.

While the proxy is active a background task performs exactly one tiny
*unproxied* request to Discord's gateway endpoint every 10 minutes.  The
moment that probe confirms the direct IP is no longer rate limited (any
non-429 response), the proxy is disabled again so the Webshare 1 GB/month
bandwidth allowance is only consumed while it is genuinely needed.
"""

from __future__ import annotations

import asyncio
import json
import os
import random
import time
from pathlib import Path

import aiohttp
import requests

from utils import logging
from utils.cloudflare import blocked_egress_ip, interstitial_signature

# ── Config ───────────────────────────────────────────────────────────────────
WEBSHARE_API_KEY_ENV = "WEBSHARE_API_KEY"
PROXY_LIST_URL = "https://proxy.webshare.io/api/v2/proxy/list/"
GATEWAY_PROBE_URL = "https://discord.com/api/v10/gateway"
#: An address echo service the egress check asks what IP it saw.  Discord's own
#: block page does not always print ``Your IP``, so when it stays silent the
#: same question is put to the proxy itself through this plain-text endpoint.
EGRESS_PROBE_URL = "https://checkip.amazonaws.com"
_EGRESS_PROBE_TIMEOUT = 5.0

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
#: How long a proxy Cloudflare blocked (or that refused the connection) is kept
#: out of rotation.  Long enough that the bot never loops on a banned IP during
#: a burst, short enough that a long-lived process can retry an endpoint
#: Cloudflare has since forgiven without needing a restart.
PROXY_BAN_TTL_SECONDS = 3600
#: Where the blocked-proxy record survives a restart.  The supervisor restarts
#: the bot child when a blocked login ends it, and a process that starts with an
#: empty memory tries the same refused IPs again.
PROXY_BANS_PATH = Path(__file__).resolve().parents[2] / "data" / "proxy_bans.json"
_FETCH_TIMEOUT_SECONDS = 10
_PAGE_SIZE = 100


class _RelayedAiohttpResponse:
    """Minimal aiohttp response contract needed by discord.py HTTPClient."""

    def __init__(self, status: int, headers: dict, body: bytes):
        from http import HTTPStatus
        from multidict import CIMultiDict

        self.status = status
        try:
            self.reason = HTTPStatus(status).phrase
        except ValueError:
            self.reason = "Unknown Status"
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


async def _probe_egress(session, proxy_url: str) -> str | None:
    """The address ``proxy_url`` egresses from, or None when it cannot say.

    This is the check that keeps a clean proxy out of the blocked list.  A
    Cloudflare block belongs to an IP; the only way to know whether that IP is
    the proxy's is to ask a service outside Discord which address it saw the
    request arrive from.  A matching answer means the block really is that
    proxy's; a different one means the request never left through the proxy;
    no answer means there is no verdict and the block is not charged to anyone.
    """
    from ipaddress import ip_address

    try:
        timeout = aiohttp.ClientTimeout(total=_EGRESS_PROBE_TIMEOUT)
        async with session.get(EGRESS_PROBE_URL, proxy=proxy_url, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            text = (await resp.read()).decode("utf-8", "replace").strip()
    except Exception:
        return None
    try:
        return str(ip_address(text))
    except ValueError:
        return None


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


def login_block_reason(error) -> str | None:
    """Why a ``bot.login()`` failure means "move egress", or None.

    Login is the one Discord request the session hook cannot see: discord.py
    builds its own aiohttp session inside ``login()``, so a shared hosting IP
    that Cloudflare has throttled (``Error 1015``) fails the very first request
    (``GET /users/@me``) before any proxy is armed.  The block is read from the
    exception instead — its ``response`` carries Cloudflare's status and
    headers, its ``text`` the page — and any 429 (Cloudflare throttle or plain
    Discord rate limit) is the same recovery because both follow the egress IP.

    A JSON Discord error, a connection error or a bad token is *not* a block:
    a different IP would not fix any of them, so those keep the real failure.
    """
    status = getattr(error, "status", None)
    if status not in (403, 429, 503):
        return None
    response = getattr(error, "response", None)
    body = getattr(error, "text", "") or ""
    signature = interstitial_signature(response, body)
    if signature:
        return _cloudflare_reason(signature, blocked_egress_ip(body))
    if status == 429:
        return "Discord rate limit"
    return None


def _cloudflare_reason(signature: str, egress: str | None) -> str:
    """``Cloudflare throttle (...)`` naming the address Cloudflare refused.

    The address is what makes a block attributable: without it a log line says a
    proxy is banned but not whether the request actually left through it.
    """
    detail = f"{signature}, egress {egress}" if egress else signature
    return f"Cloudflare throttle ({detail})"


def _login_block_egress(error) -> str | None:
    """The address Cloudflare refused on a blocked login, when its page says so."""
    return blocked_egress_ip(getattr(error, "text", "") or "")


async def cloudflare_throttle(response) -> str | None:
    """Cloudflare's own interstitial signature on a 429, or None.

    Discord serves every response through Cloudflare, so ``Server: cloudflare``
    and ``CF-Ray`` prove nothing on their own.  Only Cloudflare's block/challenge
    page — or its ``cf-mitigated`` header, or a numeric ``error code: 10xx`` — is a
    throttle, and that is the event a different egress IP clears.
    """
    if getattr(response, "status", None) != 429:
        return None

    body = await _read_response_text(response)
    return interstitial_signature(response, body)


#: The hosts Discord's API answers on.  ``cdn.discordapp.com`` is deliberately
#: not one of them: images are not what the egress IP is banned for, and the
#: Webshare allowance is measured in gigabytes.
_DISCORD_API_HOSTS = {
    "discord.com",
    "discordapp.com",
    "canary.discord.com",
    "ptb.discord.com",
}


def _is_discord_api_url(url: str) -> bool:
    """Whether ``url`` is a Discord API call, as opposed to a CDN download."""
    from urllib.parse import urlsplit

    parts = urlsplit(url)
    hostname = (parts.hostname or "").lower().rstrip(".")
    return hostname in _DISCORD_API_HOSTS and parts.path.startswith("/api/")


def _live_session(http):
    """discord.py's aiohttp session, or None before ``static_login`` makes one."""
    session = getattr(http, "_HTTPClient__session", None)
    if session is not None and hasattr(session, "_request"):
        return session
    return None


def _discord_missing():
    """discord.py's ``MISSING`` sentinel, imported only when a retry needs it.

    This module stays importable without discord for the dashboard and the
    tests; the sentinel is only needed to make ``static_login`` rebuild the
    connector it shares with the session that was just closed.
    """
    from discord.utils import MISSING

    return MISSING


#: Attempts a blocked login makes when it cannot consult the proxy list, and the
#: floor when it can — ``_login_attempts`` adds one attempt per available proxy.
#: The waits between attempts follow.
#: Transport failures that prove the proxy itself could not be used.  A read
#: timeout or a dropped response is just as likely to be Discord's side, and
#: banning a proxy for one of those takes a working egress out of rotation.
PROXY_CONNECTION_ERRORS = (
    aiohttp.ClientProxyConnectionError,
    aiohttp.ClientHttpProxyError,
)

LOGIN_ATTEMPTS = 3
#: Webshare's datacenter addresses get blocked in numbers, so a start that is
#: blocked on its first proxy has to be able to walk the whole list instead of
#: dying after two and repeating those two IPs on the next restart.
LOGIN_ATTEMPTS_MAX = 12
LOGIN_RETRY_DELAYS = (2.0, 5.0)


def _proxy_connection_failure(error, manager) -> bool:
    """Whether a login failed because the armed proxy could not be reached.

    That failure carries no response to read, so it has no Cloudflare signature
    to classify — but the recovery is the same one the request hook applies to a
    connection error mid-run: the proxy is dead, so move to another one.
    """
    return (
        manager is not None
        and getattr(manager, "enabled", False)
        and isinstance(error, PROXY_CONNECTION_ERRORS)
    )


def _login_attempts(manager) -> int:
    """How many logins a blocked start may spend before giving up.

    One attempt per proxy the plan still offers, so a blocked start finds out
    whether *any* Webshare address works instead of dying after two and walking
    back onto the same pair on the next restart.  ``LOGIN_ATTEMPTS`` is the floor
    for a manager that cannot report its list.
    """
    available = getattr(manager, "_unbanned_proxies", None)
    if not callable(available):
        return LOGIN_ATTEMPTS
    try:
        count = len(available())
    except Exception:
        return LOGIN_ATTEMPTS
    return max(LOGIN_ATTEMPTS, min(LOGIN_ATTEMPTS_MAX, 1 + count))


async def login_with_failover(
    client,
    token: str,
    *,
    attempts: int | None = None,
    delays: tuple[float, ...] = LOGIN_RETRY_DELAYS,
) -> None:
    """Log ``client`` in, moving to Webshare egress when its IP is blocked.

    ``client.login()`` builds discord.py's aiohttp session itself, so the request
    hook cannot see the login request.  A shared hosting IP that Cloudflare has
    banned (``Error 1015``) therefore answers that first request with its block
    page and no proxy is ever armed — which is the restart loop where the bot
    dies, restarts, and repeats the same blocked login forever.  Catching the
    block on the exception keeps the same process and retries on a working
    egress.  Any other failure (a bad token, a connection error, a JSON Discord
    error) is not an egress problem and is re-raised untouched.

    A blocked start walks the proxy list rather than spending two attempts and
    exiting: each retry retires the proxy that was refused and rotates onto one
    that has not been tried, so one restart is enough to learn whether any
    Webshare address works instead of the supervisor restarting into the same
    two banned IPs.
    """
    manager = getattr(client, "proxy_manager", None)
    total = _login_attempts(manager) if attempts is None else attempts
    for attempt in range(1, max(1, total) + 1):
        try:
            await client.login(token)
            return
        except Exception as exc:
            reason = login_block_reason(exc)
            if reason is None and _proxy_connection_failure(exc, manager):
                reason = "The Webshare proxy refused the connection"
            if reason is None or manager is None or attempt >= total:
                raise
            logging.warning(
                "ProxyManager",
                f"{reason} blocked the Discord login — retrying through "
                f"Webshare (attempt {attempt} of {total}).",
            )
            if not await manager.failover_login(exc, reason=reason):
                raise
            # login() created this attempt's session; release it so the retry
            # opens a clean one that carries the new proxy.  A failure before
            # that point has no session to release.
            if _live_session(client.http) is not None:
                await client.http.close()
                client.http.clear()
                # aiohttp closes the connector together with its session, and
                # discord.py only builds a new one when it has none: leave the
                # closed connector in place and the retry's session is born
                # closed, so it fails with "Session is closed" before it ever
                # reaches Discord.
                client.http.connector = _discord_missing()
            await asyncio.sleep(delays[min(attempt - 1, len(delays) - 1)] if delays else 0.0)


class WebshareProxyManager:
    """Applies/removes a Webshare proxy in reaction to global rate limits."""

    def __init__(self, api_key: str | None):
        self.api_key = api_key
        self.bot = None                 # set by attach; used to detect proxy workers
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
        # Endpoint -> wall-clock time it was blocked, so rotation can skip the
        # proxies that are already known to fail instead of picking at random.
        # Wall clock because the record outlives the process (see _load_bans).
        self._banned_proxies: dict[tuple, float] = {}
        self._load_bans()
        # Whether the "nothing is usable" message has been said, so a blocked
        # list does not turn every request into another warning line.
        self._shortage_reported = False

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    def attach(self, bot) -> bool:
        """Bind to the bot's HTTP client and install the global-429 hook.

        Synchronous on purpose so it can run at import time in ``bot.py``.
        Returns True when proxy failover is armed.
        """
        if not self.api_key:
            return False
        self.bot = bot
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
        # The session only exists once login starts, so ``attach`` is called again
        # after login to hook the live session for subsequent requests.
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
        return _live_session(self.http)

    def _install_hook(self, session) -> None:
        """Wrap Discord requests to detect rate limits and apply configured routing."""
        original_request = session._request
        manager = self

        async def hooked_request(method, url, **kwargs):
            manager._use_armed_proxy(str(url), kwargs)
            try:
                resp = await original_request(method, url, **kwargs)
            except Exception as exc:
                try:
                    await manager._note_proxy_failure(exc, kwargs.get("proxy"))
                except Exception:
                    # The caller has to see the connection error it actually hit.
                    pass
                raise
            if manager._should_monitor(str(url)) and not manager._discord_proxy_relayed():
                try:
                    await manager.handle_rate_limit(resp, proxy=kwargs.get("proxy"))
                except Exception as exc:
                    # Monitoring must never turn a Discord response into a bot
                    # error: the caller still gets the response it asked for.
                    manager._last_error = str(exc)[:240]
                    logging.warning("ProxyManager", f"Rate-limit handling failed: {exc}")
            return resp

        session._request = hooked_request
        self._hooked_session = session

    def _use_armed_proxy(self, url: str, kwargs: dict) -> None:
        """Give a Discord API request that has no proxy of its own the armed one.

        discord.py applies ``http.proxy`` in ``HTTPClient.request``, so its own
        REST calls are covered. Its webhook adapter does not go through there: it
        uses the aiohttp session directly with ``proxy=None``, which left every
        webhook execution — the logging cog's entries above all — on the host's
        own address, answering Cloudflare's ``Error 1015`` while the rest of the
        bot was proxied and rotating the proxy for a limit it had just failed to
        avoid.
        """
        if not self.enabled or self._proxy_url is None:
            return
        if kwargs.get("proxy"):
            return
        if not _is_discord_api_url(url):
            return
        kwargs["proxy"] = self._proxy_url

    async def failover_login(self, error, *, reason: str | None = None) -> bool:
        """Arm or rotate Webshare egress after a blocked login attempt.

        The same recovery as the request hook, driven from the exception a
        failed ``login()`` raised instead of from a response the hook saw.
        Returns True when a proxy is active for the retry.  ``reason`` lets the
        caller name a failure the exception cannot classify by itself, such as a
        proxy that refused the connection.

        A fresh proxy is armed by setting ``http.proxy``, which discord.py reads
        on every request and gateway websocket it opens — so the retried login
        and the connection that follows it both use the new egress.
        """
        reason = reason or login_block_reason(error)
        if reason is None or self.http is None:
            return False
        egress = _login_block_egress(error)
        if self.enabled and self._active_proxy is not None:
            # The active proxy's IP is the limited one (or the proxy is dead), so
            # a retry on it only repeats the failure; move to another proxy when
            # one is available, and say so, because retrying the same one is not
            # a recovery.  The refused endpoint is retired first, so rotation
            # cannot hand the retry the same blocked proxy back.
            before = self._proxy_key(self._active_proxy)
            if not await self._retire_active_proxy(reason, egress):
                # The refused address was not this proxy, so another proxy is not
                # the fix: stop rather than spend the rest of the list on it.
                return False
            if self._active_proxy is None:
                return False
            return self.enabled and self._proxy_key(self._active_proxy) != before
        await self.enable(reason=reason)
        return self.enabled

    async def handle_rate_limit(self, response, *, proxy: str | None = None) -> None:
        """Move egress to Webshare when Discord or Cloudflare limits this IP.

        Called for every Discord response, so the two checks are cheap: they only
        read a body on a 429, and an ordinary 200 returns immediately.  ``proxy``
        is the connection the request actually used, so a block is charged to the
        egress that earned it rather than to whatever proxy is armed.
        """
        if await is_global_rate_limit(response):
            await self._arm_for_limit("Discord global rate limit", via=proxy)
            return
        throttle = await cloudflare_throttle(response)
        if throttle:
            egress = blocked_egress_ip(await _read_response_text(response))
            await self._arm_for_limit(
                _cloudflare_reason(throttle, egress),
                via=proxy,
                blocked=True,
                egress=egress,
            )

    async def _arm_for_limit(
        self,
        reason: str,
        *,
        via: str | None = None,
        blocked: bool = False,
        egress: str | None = None,
    ) -> None:
        """Use a proxy for a limited direct IP, or a fresh one while proxied.

        The limit follows the egress IP, so a limit that arrives while a proxy is
        already active means that proxy's IP is the limited one: rotating keeps
        the bot off it without ever falling back to the direct IP.  ``via`` is
        the proxy that carried the limited request — without it a Cloudflare
        block on a direct request (a CDN fallback, say) would take a working
        proxy out of rotation for a block it had nothing to do with.  ``blocked``
        marks the IP-level Cloudflare throttle, which retires the proxy instead of
        merely rotating past it once.
        """
        if not self.api_key or self.http is None:
            return
        if self.enabled and self._active_proxy is not None:
            if via != self._proxy_url:
                # The block did not arrive through the armed proxy, so it says
                # nothing about it: the proxy stays exactly as it is.
                return
            if blocked:
                await self._retire_active_proxy(reason, egress)
            else:
                self.rotate(reason=reason)
            return
        await self.enable(reason=reason)

    def _should_monitor(self, url: str) -> bool:
        from urllib.parse import urlsplit

        hostname = (urlsplit(url).hostname or "").lower().rstrip(".")
        return hostname == "discord.com" or hostname.endswith((".discord.com", ".discordapp.com"))

    def _discord_proxy_relayed(self) -> bool:
        """Whether this exact response came from a proxy worker.

        A 429 answered through a worker belongs to that rotating egress, not to
        the shared hosting IP Webshare exists to rescue. Arming Webshare here
        would spend its bandwidth on traffic the worker already moved. A request
        that fell back to the direct route must still arm the normal recovery.
        """
        proxy = getattr(self.bot, "discord_proxy", None)
        checker = getattr(proxy, "request_was_relayed", None)
        if not callable(checker):
            return False
        try:
            return bool(checker())
        except Exception:
            return False

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
        usable = [proxy for proxy in proxies if not self._proxy_is_banned(proxy)]
        if not usable:
            self._last_error = (
                f"All {len(proxies)} Webshare proxies are blocked; the direct IP is the only egress left."
            )
            if not self._shortage_reported:
                self._shortage_reported = True
                logging.error(
                    "ProxyManager",
                    f"Every Webshare proxy ({len(proxies)}) is Cloudflare-blocked — not arming one.",
                )
            return False
        self._apply_proxy(random.choice(usable), reason=reason or "Discord global rate limit")
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
            # Say it once: a blocked direct IP asks for a proxy on every request,
            # and repeating this line per request is the flood, not the diagnosis.
            if not self._shortage_reported:
                self._shortage_reported = True
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
        same burst would only burn through the proxy list.  A proxy that is
        blocked (Cloudflare ``Error 1015``) or cannot be connected to is the
        exception — it is retired immediately, because the request that found it
        has already failed and trying it again cannot succeed.

        Rotation only ever lands on a proxy that is not known to be blocked: the
        point of rotating is to leave a failing egress behind, so returning to an
        endpoint Cloudflare is refusing is strictly worse than staying put.
        """
        if self._active_proxy is None:
            return
        if not immediate and time.monotonic() - self._rotated_at < ROTATE_COOLDOWN_SECONDS:
            return
        candidates = self._unbanned_proxies(exclude=self._active_proxy)
        if not candidates:
            self._report_no_alternatives()
            return
        self._apply_proxy(random.choice(candidates), reason=reason)
        self._rotated_at = time.monotonic()

    async def _note_proxy_failure(self, error, proxy_used) -> bool:
        """React to a request that failed at the transport, without guessing.

        Failing to *connect* to the proxy proves that endpoint is unusable, so it
        is retired and never handed out again.  Any other transport failure (a
        read timeout, a dropped response) can just as easily be Discord's side, so
        the request moves to another proxy while the one that failed stays in the
        list — banning it would spend a working egress on a guess.
        """
        if not self.enabled or not proxy_used:
            return False
        if not isinstance(error, (aiohttp.ClientError, OSError)):
            return False
        if isinstance(error, PROXY_CONNECTION_ERRORS):
            # Already proven unusable; there is nothing to verify with a probe.
            await self._retire_active_proxy(
                "The active Webshare proxy refused the connection", verify=False
            )
        else:
            self.rotate(reason="The active Webshare proxy dropped the request", immediate=True)
        return True

    async def _retire_active_proxy(
        self, reason: str, egress: str | None = None, *, verify: bool = True
    ) -> bool:
        """Stop using the active proxy and move to another one now.

        A Cloudflare block and a refused connection are facts about that exact
        endpoint, so the proxy is recorded as unusable before rotating away: the
        next limit must find a different one rather than the IP that just failed.
        ``egress`` is the address Cloudflare named, when it named one.

        Returns False when the block was provably *not* this proxy's: moving to
        another proxy cannot fix a block that belongs to some other address, so
        callers that retry on a fresh egress should stop instead of sweeping the
        list.  The proxy is still rotated off, just not blacklisted.
        """
        if self._active_proxy is None:
            return False
        attributable = await self._ban_if_attributable(
            self._active_proxy, reason, egress, verify=verify
        )
        self.rotate(reason=reason, immediate=True)
        return attributable

    async def _ban_if_attributable(
        self, proxy: dict, reason: str, egress: str | None, *, verify: bool
    ) -> bool:
        """Record ``proxy`` as blocked only when the block is provably its own.

        The address Cloudflare refused decides this: when the block page names
        it, that is the answer; when the page stays quiet, the proxy is asked
        what address it egresses from.  A different address means the request
        never left through the proxy, so the proxy is left in rotation — that is
        how a clean endpoint stops being marked banned for someone else's block.
        With no answer at all there is no verdict, and "no verdict" does not
        become a ban either: the proxy is moved off but stays in the list.

        Returns False only for a proven mismatch, where changing proxies cannot
        help because the refused address was never the proxy's.
        """
        address = (proxy.get("proxy_address") or "").strip().lower()
        seen = (egress or "").strip().lower()
        note = None
        if not seen and verify and self._proxy_url is not None:
            seen = (await _probe_egress(self._ensure_session(), self._proxy_url) or "").lower()
            note = f"egress confirmed {seen}" if seen == address else None
        where = f"{proxy.get('proxy_address')}:{proxy.get('port')}"
        if seen and address and seen != address:
            logging.warning(
                "ProxyManager",
                f"{reason} — the egress is {seen}, not {where}; Cloudflare refused an "
                f"address that is not this proxy, so it stays in rotation.",
            )
            return False
        if not seen and verify:
            logging.warning(
                "ProxyManager",
                f"{reason} — there is no egress address to check {where} against; "
                f"moving off it without blocking it.",
            )
            return True
        self._ban_proxy(proxy, reason, note=note)
        return True

    @staticmethod
    def _proxy_key(proxy: dict | None) -> tuple | None:
        """Identity of a proxy endpoint, stable across refreshed Webshare lists."""
        if not proxy:
            return None
        return (proxy.get("proxy_address"), proxy.get("port"), proxy.get("username"))

    def _proxy_is_banned(self, proxy: dict) -> bool:
        """Whether ``proxy`` was blocked recently enough to stay out of rotation."""
        key = self._proxy_key(proxy)
        if key is None:
            return False
        blocked_at = self._banned_proxies.get(key)
        if blocked_at is None:
            return False
        if time.time() - blocked_at >= PROXY_BAN_TTL_SECONDS:
            del self._banned_proxies[key]
            return False
        return True

    def _ban_proxy(self, proxy: dict, reason: str, note: str | None = None) -> None:
        """Record that Cloudflare (or the proxy itself) refuses this endpoint."""
        key = self._proxy_key(proxy)
        if key is None or key in self._banned_proxies:
            return
        self._banned_proxies[key] = time.time()
        self._save_bans()
        detail = f" ({note})" if note else ""
        logging.warning(
            "ProxyManager",
            f"{reason} — Webshare proxy {proxy.get('proxy_address')}:{proxy.get('port')} "
            f"will not be used again for {PROXY_BAN_TTL_SECONDS // 60} minutes{detail}.",
        )

    def _load_bans(self) -> None:
        """Restore the blocked endpoints an earlier process recorded.

        The supervisor restarts the bot child when a blocked login ends it, and
        without this the restarted child starts with an empty record: every
        restart walked back onto the IPs the previous one had just been refused
        by, which is the loop that made the block look permanent.
        """
        try:
            entries = json.loads(
                PROXY_BANS_PATH.read_text(encoding="utf-8")
            ).get("banned", [])
        except (OSError, ValueError, AttributeError):
            # No record yet, or one this process cannot read: it is a cache of
            # what failed, not state worth failing a start over.
            return
        now = time.time()
        for entry in entries:
            try:
                address, port, username, blocked_at = entry
                blocked_at = float(blocked_at)
            except (TypeError, ValueError):
                continue
            if now - blocked_at < PROXY_BAN_TTL_SECONDS:
                self._banned_proxies[(address, port, username)] = blocked_at

    def _save_bans(self) -> None:
        """Persist the blocked endpoints for the next process in this container."""
        now = time.time()
        entries = [
            [address, port, username, blocked_at]
            for (address, port, username), blocked_at in self._banned_proxies.items()
            if now - blocked_at < PROXY_BAN_TTL_SECONDS
        ]
        try:
            PROXY_BANS_PATH.parent.mkdir(parents=True, exist_ok=True)
            PROXY_BANS_PATH.write_text(json.dumps({"banned": entries}), encoding="utf-8")
        except OSError as exc:
            logging.warning(
                "ProxyManager",
                f"Could not record the blocked Webshare proxies: {exc}",
            )

    def _unbanned_proxies(self, exclude: dict | None = None) -> list[dict]:
        """Cached proxies that are neither blocked nor the one being replaced."""
        excluded = self._proxy_key(exclude)
        return [
            proxy for proxy in self._cached_proxies(allow_stale=True)
            if self._proxy_key(proxy) != excluded and not self._proxy_is_banned(proxy)
        ]

    def _report_no_alternatives(self) -> None:
        """Say once that every proxy is blocked, instead of looping over them.

        Repeating the message on every blocked request is the console flood this
        replaces; the state itself is already visible through ``_last_error``.
        """
        if self._shortage_reported:
            return
        self._shortage_reported = True
        active = self._active_proxy or {}
        self._last_error = "Every available Webshare proxy is blocked or unreachable."
        blocked = len(self._banned_proxies)
        detail = f"{blocked} blocked" if blocked else "no proxy list"
        logging.error(
            "ProxyManager",
            f"No unblocked Webshare proxy is left to rotate to ({detail}) — keeping "
            f"{active.get('proxy_address')}:{active.get('port')} rather than retrying a "
            f"proxy Cloudflare is refusing.",
        )

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
        self._shortage_reported = False
        logging.warning(
            "ProxyManager",
            f"{reason} — routed through Webshare proxy "
            f"{proxy['proxy_address']}:{proxy['port']}.",
        )
        self._ensure_verify_task()

    def _cached_proxies(self, *, allow_stale: bool = False) -> list[dict]:
        if (
            self._proxies
            and (
                allow_stale
                or time.monotonic() - self._proxies_fetched_at < PROXY_CACHE_TTL_SECONDS
            )
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