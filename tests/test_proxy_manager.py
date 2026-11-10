"""Global rate limits and Cloudflare throttles arm the Webshare proxy.

A global limit follows the egress IP, so the recovery is a different IP: the
manager has to notice the limit from any of the signals Discord leaves behind
(the ``X-RateLimit-Scope`` header, the older ``X-RateLimit-Global`` header, or
the body's ``global`` field that discord.py itself reads), arm the proxy, and —
when a limit arrives on a proxy that is already active — rotate to a fresh one
instead of reusing the limited IP.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import aiohttp
import pytest

from discord.utils import MISSING

from utils.proxy_manager import (
    WebshareProxyManager,
    is_global_rate_limit,
    login_block_reason,
    login_with_failover,
)

DISCORD_URL = "https://discord.com/api/v10/users/@me"
PROXY_ONE = {"username": "user-one", "password": "pass-one", "proxy_address": "10.0.0.1", "port": 80}
PROXY_TWO = {"username": "user-two", "password": "pass-two", "proxy_address": "10.0.0.2", "port": 80}
CLOUDFLARE_THROTTLE_PAGE = (
    "<html><head><title>Attention Required! | Cloudflare</title></head>"
    "<body>error code: 1015</body></html>"
)


class FakeResponse:
    def __init__(self, status, headers=None, payload=None, body=None):
        self.status = status
        self.headers = headers or {}
        raw = body if body is not None else (json.dumps(payload) if payload is not None else "")
        self._body = raw if isinstance(raw, bytes) else str(raw).encode()

    async def text(self, encoding="utf-8"):
        return self._body.decode(encoding, errors="replace")

    def release(self):
        return None


class FakeSession:
    """An aiohttp session whose every request answers with one response."""

    def __init__(self, response):
        self.response = response
        self.calls = []

    async def _request(self, method, url, **kwargs):
        self.calls.append(kwargs.get("proxy"))
        return self.response


class ProxyFailSession:
    """A session whose proxied requests fail at the connection."""

    def __init__(self):
        self.proxied_calls = 0

    async def _request(self, method, url, **kwargs):
        if kwargs.get("proxy"):
            self.proxied_calls += 1
            raise aiohttp.ClientConnectionError("proxy refused the connection")
        return FakeResponse(200)


class FakeHTTP:
    def __init__(self, session):
        self._HTTPClient__session = session
        self.proxy = None
        self.proxy_auth = None
        self.user_agent = "DiscordBot (https://discord.com, 2.7.1)"


def _attach(session, proxies=None):
    """A proxy manager armed on a bot whose session answers through ``session``.

    The proxy list is pre-seeded the way the startup prefetch leaves it, so no
    Webshare API call happens in a test.
    """
    http = FakeHTTP(session)
    manager = WebshareProxyManager("test-key")
    assert manager.attach(SimpleNamespace(http=http))
    manager._proxies = [dict(proxy) for proxy in (proxies if proxies is not None else [PROXY_ONE])]
    manager._proxies_fetched_at = time.monotonic()
    return manager, http, session


def test_the_scope_header_alone_arms_the_proxy():
    async def scenario():
        session = FakeSession(FakeResponse(429, {"X-RateLimit-Scope": "global"}, {"retry_after": 0.5}))
        manager, http, _ = _attach(session)

        await session._request("GET", DISCORD_URL)

        assert manager.enabled
        assert http.proxy == "http://user-one:pass-one@10.0.0.1:80"
        await manager.close()

    asyncio.run(scenario())


def test_the_legacy_global_header_alone_arms_the_proxy():
    async def scenario():
        session = FakeSession(FakeResponse(429, {"X-RateLimit-Global": "true"}, {"retry_after": 0.5}))
        manager, http, _ = _attach(session)

        await session._request("GET", DISCORD_URL)

        assert manager.enabled
        assert http.proxy is not None
        await manager.close()

    asyncio.run(scenario())


def test_a_body_only_global_limit_arms_the_proxy():
    async def scenario():
        # discord.py reads the global flag from the body, so a limit that only
        # appears there is still a global limit and still has to move egress.
        session = FakeSession(FakeResponse(429, {}, {"retry_after": 0.5, "global": True}))
        manager, http, _ = _attach(session)

        await session._request("GET", DISCORD_URL)

        assert manager.enabled
        assert http.proxy is not None
        await manager.close()

    asyncio.run(scenario())


def test_a_per_route_rate_limit_leaves_the_direct_ip_alone():
    async def scenario():
        session = FakeSession(FakeResponse(429, {"X-RateLimit-Scope": "user"}, {"retry_after": 0.5}))
        manager, http, _ = _attach(session)

        await session._request("GET", DISCORD_URL)

        assert not manager.enabled
        assert http.proxy is None
        await manager.close()

    asyncio.run(scenario())


def test_a_cloudflare_throttle_arms_the_proxy():
    async def scenario():
        # "Error 1015" is the edge throttling this IP, so the proxy manager
        # arms or rotates the proxy to clear it.
        session = FakeSession(FakeResponse(429, {"Server": "cloudflare"}, body=CLOUDFLARE_THROTTLE_PAGE))
        manager, http, _ = _attach(session)

        await session._request("GET", DISCORD_URL)

        assert manager.enabled
        assert http.proxy is not None
        await manager.close()

    asyncio.run(scenario())


def test_a_cloudflare_json_answer_is_not_a_throttle():
    async def scenario():
        # Discord's own 429 arrives through Cloudflare too; only Cloudflare's page
        # or its cf-mitigated header may be treated as an interstitial.
        session = FakeSession(
            FakeResponse(429, {"Server": "cloudflare"},
                         {"message": "You are being rate limited.", "retry_after": 0.5})
        )
        manager, http, _ = _attach(session)

        await session._request("GET", DISCORD_URL)

        assert not manager.enabled
        assert http.proxy is None
        await manager.close()

    asyncio.run(scenario())


def test_a_limit_burst_rotates_once_and_then_moves_on():
    async def scenario():
        session = FakeSession(FakeResponse(429, {"X-RateLimit-Scope": "global"}, {"retry_after": 0.5}))
        manager, http, _ = _attach(session)

        await session._request("GET", DISCORD_URL)
        assert manager._active_proxy["proxy_address"] == "10.0.0.1"

        # A second proxy becomes available, exactly as the next prefetch would.
        manager._proxies = [dict(PROXY_ONE), dict(PROXY_TWO)]

        # The same limit event: rotating once is the recovery, rotating on every
        # 429 in the burst would only burn through the proxy list.
        await session._request("GET", DISCORD_URL)
        assert manager._active_proxy["proxy_address"] == "10.0.0.1"

        # A later limit means this proxy's IP is the limited one now.
        manager._rotated_at = 0.0
        await session._request("GET", DISCORD_URL)
        assert manager._active_proxy["proxy_address"] == "10.0.0.2"
        assert http.proxy == "http://user-two:pass-two@10.0.0.2:80"
        await manager.close()

    asyncio.run(scenario())


def test_a_dead_proxy_rotates_instead_of_failing_every_request():
    async def scenario():
        session = ProxyFailSession()
        manager, http, _ = _attach(session, proxies=[PROXY_ONE, PROXY_TWO])

        await manager.enable()
        limited = manager._active_proxy

        with pytest.raises(aiohttp.ClientConnectionError):
            await session._request("GET", DISCORD_URL, proxy=http.proxy)

        assert manager._active_proxy is not limited
        assert manager._active_proxy["proxy_address"] != limited["proxy_address"]
        await manager.close()

    asyncio.run(scenario())


def test_a_global_limit_on_another_host_does_not_touch_the_proxy():
    async def scenario():
        session = FakeSession(FakeResponse(429, {"X-RateLimit-Scope": "global"}, {"retry_after": 0.5}))
        manager, http, _ = _attach(session)

        await session._request("GET", "https://example.test/thing")

        assert not manager.enabled
        assert http.proxy is None
        await manager.close()

    asyncio.run(scenario())


def test_a_failing_reaction_never_breaks_the_request():
    async def scenario():
        session = FakeSession(FakeResponse(429, {"X-RateLimit-Scope": "global"}, {"retry_after": 0.5}))
        manager, http, _ = _attach(session)

        async def explode(response):
            raise RuntimeError("monitoring is broken")

        manager.handle_rate_limit = explode
        response = await session._request("GET", DISCORD_URL)

        assert response.status == 429
        assert "monitoring is broken" in manager._last_error
        await manager.close()

    asyncio.run(scenario())


def test_the_body_is_still_readable_after_the_global_check():
    async def scenario():
        response = FakeResponse(429, {"X-RateLimit-Scope": "global"}, {"retry_after": 0.5, "global": True})

        assert await is_global_rate_limit(response) is True
        # aiohttp caches the body, so discord.py's own json_or_text still sees it.
        assert json.loads(await response.text())["global"] is True

    asyncio.run(scenario())


# ── Login egress ──────────────────────────────────────────────────────────────
# discord.py builds its HTTP session inside login(), so the request hook above
# never sees the login request.  A shared hosting IP that Cloudflare bans
# answers it with a 1015 page, and without this the process died and the
# supervisor restarted it into the same block forever.


class FakeLoginFailure(Exception):
    """The shape of ``discord.HTTPException`` that login failover reads."""

    def __init__(self, status, body="", headers=None):
        self.status = status
        self.text = body
        self.response = FakeResponse(status, headers or {}, body=body)
        super().__init__(f"{status}: {' '.join(body.split())[:60]}")


class LoginSession:
    """The discord.py session the failed attempt created."""

    def __init__(self):
        self.closed = False

    async def _request(self, method, url, **kwargs):
        return FakeResponse(200)

    async def close(self):
        self.closed = True


class LoginHTTP(FakeHTTP):
    """A client HTTP object that records the retry's session reset."""

    def __init__(self):
        super().__init__(LoginSession())
        # discord.py's static_login() reuses this across logins, so closing a
        # session closes it too — the retry has to be given a fresh one.
        self.connector = "the shared connector"
        self.closed = 0
        self.cleared = 0

    async def close(self):
        self.closed += 1
        self.connector = "a closed connector"
        await self._HTTPClient__session.close()

    def clear(self):
        self.cleared += 1
        self._HTTPClient__session = None


class FakeLoginClient:
    """A bot whose ``login()`` raises the queued failures before succeeding."""

    def __init__(self, manager, failures):
        self.proxy_manager = manager
        self.http = manager.http
        self.failures = list(failures)
        self.logins = 0

    async def login(self, token):
        self.logins += 1
        if self.failures:
            raise self.failures.pop(0)


def _login_manager(proxies=None):
    http = LoginHTTP()
    manager = WebshareProxyManager("test-key")
    assert manager.attach(SimpleNamespace(http=http))
    manager._proxies = [dict(proxy) for proxy in (proxies if proxies is not None else [PROXY_ONE])]
    manager._proxies_fetched_at = time.monotonic()
    return manager, http


def test_a_cloudflare_blocked_login_retries_through_webshare():
    async def scenario():
        manager, http = _login_manager()
        block = FakeLoginFailure(429, CLOUDFLARE_THROTTLE_PAGE, {"Server": "cloudflare"})
        client = FakeLoginClient(manager, [block])

        await login_with_failover(client, "token", delays=(0,))

        assert client.logins == 2
        assert manager.enabled
        assert http.proxy == "http://user-one:pass-one@10.0.0.1:80"
        # The failed attempt's session has to be released, because the retry
        # creates a new one and only a new one carries the proxy.
        assert (http.closed, http.cleared) == (1, 1)
        # aiohttp closes the connector with the session, and discord.py only
        # rebuilds one when it has none — otherwise the retry fails with
        # "Session is closed" before it reaches Discord.
        assert http.connector is MISSING
        await manager.close()

    asyncio.run(scenario())


def test_a_login_block_rotates_off_the_proxy_that_is_limited():
    async def scenario():
        manager, http = _login_manager(proxies=[PROXY_ONE, PROXY_TWO])
        await manager.enable()
        limited = manager._active_proxy["proxy_address"]
        block = FakeLoginFailure(429, CLOUDFLARE_THROTTLE_PAGE, {"Server": "cloudflare"})
        client = FakeLoginClient(manager, [block])

        await login_with_failover(client, "token", delays=(0,))

        assert manager.enabled
        # The active proxy is the limited IP on a login block, so the retry has
        # to use a different one rather than repeating the same request.
        assert manager._active_proxy["proxy_address"] != limited
        assert manager._active_proxy["proxy_address"] in {"10.0.0.1", "10.0.0.2"}
        assert http.proxy == (
            f"http://{manager._active_proxy['username']}:{manager._active_proxy['password']}"
            f"@{manager._active_proxy['proxy_address']}:80"
        )
        await manager.close()

    asyncio.run(scenario())


def test_a_blocked_login_without_a_usable_proxy_raises_the_real_error():
    async def scenario():
        manager, http = _login_manager(proxies=[])
        manager._proxies = []
        manager._proxies_fetched_at = 0.0

        async def no_proxies():
            return []

        manager._fetch_proxies = no_proxies
        block = FakeLoginFailure(429, CLOUDFLARE_THROTTLE_PAGE, {"Server": "cloudflare"})
        client = FakeLoginClient(manager, [block])

        with pytest.raises(FakeLoginFailure) as raised:
            await login_with_failover(client, "token", delays=(0,))

        assert raised.value is block
        assert client.logins == 1
        assert not manager.enabled
        assert http.proxy is None
        await manager.close()

    asyncio.run(scenario())


def test_a_rejected_token_does_not_move_egress():
    async def scenario():
        manager, http = _login_manager()
        # A bad token is not an egress problem: another IP cannot fix it, so the
        # real LoginFailure reaches the caller instead of burning a proxy.
        rejected = FakeLoginFailure(401, '{"message": "401: Unauthorized", "code": 0}')
        client = FakeLoginClient(manager, [rejected])

        with pytest.raises(FakeLoginFailure):
            await login_with_failover(client, "token", delays=(0,))

        assert client.logins == 1
        assert not manager.enabled
        assert http.closed == 0
        await manager.close()

    asyncio.run(scenario())


def test_a_discord_rate_limited_login_still_moves_egress():
    async def scenario():
        manager, http = _login_manager()
        limited = FakeLoginFailure(429, '{"message": "You are being rate limited.", "retry_after": 0.5}')
        client = FakeLoginClient(manager, [limited])

        await login_with_failover(client, "token", delays=(0,))

        assert client.logins == 2
        assert manager.enabled
        await manager.close()

    asyncio.run(scenario())


def test_login_block_reason_reads_the_interstitial_not_the_status_alone():
    page = FakeLoginFailure(429, CLOUDFLARE_THROTTLE_PAGE, {"Server": "cloudflare"})
    assert login_block_reason(page) == "Cloudflare throttle (error code: 1015)"

    challenged = FakeLoginFailure(403, "blocked", {"cf-mitigated": "challenge"})
    assert login_block_reason(challenged) == "Cloudflare throttle (cf-mitigated: challenge)"

    # Server errors and JSON Discord answers are not blocks.
    assert login_block_reason(FakeLoginFailure(500, "Internal Server Error")) is None
    assert login_block_reason(FakeLoginFailure(403, '{"message": "Forbidden", "code": 50001}')) is None
    assert login_block_reason(RuntimeError("no response at all")) is None


def test_the_retry_really_reaches_discord_after_dropping_the_blocked_session():
    """The production failure this path exists for, against the real client.

    A Cloudflare 1015 answers the first ``login()`` with its 429 page.  Closing
    that attempt's session also closes discord.py's shared connector, so unless
    the retry is handed a fresh one it dies with ``Session is closed`` before it
    ever reaches Discord — which is a restart loop with extra steps.
    """
    import discord
    from aiohttp import web

    page = (
        "<!doctype html><html><head><title>Access denied | discord.com used "
        "Cloudflare</title></head><body><div id=\"cf-error-details\">"
        "<h1>Error <span>1015</span></h1></div></body></html>"
    )
    user = {
        "id": "1", "username": "tester", "discriminator": "0", "avatar": None,
        "bot": True, "mfa_enabled": False, "verified": True, "email": None,
        "flags": 0, "global_name": None, "banner": None, "accent_color": None,
        "system": False,
    }
    application = {
        "id": "1", "name": "app", "description": "", "bot_public": True,
        "bot_require_code_grant": False, "verify_key": "x", "flags": 0, "summary": "",
        "team": None, "icon": None, "cover_image": None, "primary_sku_id": None,
        "slug": None, "guild_id": None, "rpc_origins": None,
        "terms_of_service_url": None, "privacy_policy_url": None, "install_params": None,
        "custom_install_url": None, "tags": [], "approximate_guild_count": None,
        "interactions_endpoint_url": None,
        "owner": {"id": "1", "username": "tester", "discriminator": "0", "avatar": None},
    }
    attempts = []

    def json_body(payload):
        return web.Response(
            body=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )

    async def users_me(_request):
        attempts.append("users/@me")
        if len(attempts) == 1:
            return web.Response(
                status=429, text=page, headers={"Server": "cloudflare"},
                content_type="text/html",
            )
        return json_body(user)

    class Manager:
        """A manager that only reports that a proxy is now armed."""

        enabled = False

        async def failover_login(self, error, *, reason=None):
            self.enabled = (reason or login_block_reason(error)) is not None
            return self.enabled

    async def application_info(_request):
        return json_body(application)

    async def scenario():
        app = web.Application()
        app.router.add_get("/api/v10/users/@me", users_me)
        app.router.add_get("/api/v10/oauth2/applications/@me", application_info)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", 0)
        await site.start()
        port = site._server.sockets[0].getsockname()[1]

        original_base = discord.http.Route.BASE
        discord.http.Route.BASE = f"http://127.0.0.1:{port}/api/v10"
        client = discord.Client(intents=discord.Intents.none())
        client.proxy_manager = Manager()
        try:
            await login_with_failover(client, "token", delays=(0,))

            assert attempts == ["users/@me", "users/@me"]
            assert client.user.id == 1
            assert client.http.connector is not MISSING
            assert not client.http._HTTPClient__session.closed
        finally:
            await client.http.close()
            discord.http.Route.BASE = original_base
            await runner.cleanup()

    asyncio.run(scenario())


def test_a_dead_proxy_on_the_login_retry_rotates_to_another_one():
    """A refusal has no response to classify, so the armed proxy is the signal."""

    async def scenario():
        manager, http = _login_manager(proxies=[PROXY_ONE, PROXY_TWO])
        await manager.enable()
        limited = manager._active_proxy["proxy_address"]
        client = FakeLoginClient(manager, [aiohttp.ClientOSError("proxy refused")])

        await login_with_failover(client, "token", delays=(0,))

        assert client.logins == 2
        assert manager._active_proxy["proxy_address"] != limited
        assert http.proxy is not None
        await manager.close()

    asyncio.run(scenario())


def test_a_dead_proxy_without_a_replacement_reports_the_real_error():
    async def scenario():
        manager, http = _login_manager(proxies=[PROXY_ONE])
        await manager.enable()
        failure = aiohttp.ClientOSError("proxy refused")
        client = FakeLoginClient(manager, [failure])

        with pytest.raises(aiohttp.ClientOSError) as raised:
            await login_with_failover(client, "token", delays=(0,))

        assert raised.value is failure
        assert client.logins == 1
        await manager.close()

    asyncio.run(scenario())
