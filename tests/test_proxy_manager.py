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

from utils.proxy_manager import WebshareProxyManager, is_global_rate_limit

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
        # "Error 1015" is the edge throttling this IP, and the standby manager
        # deliberately leaves that recovery to the proxy.
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
