import asyncio
import base64
import json
import os
import time
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch
from urllib.parse import urlsplit

import requests

from utils.proxy_manager import WebshareProxyManager
from utils.standby_failover import _dispatch_web_request, _handle_client, _is_allowed_discord_api_url, control_proof, is_discord_relay_url, relay_proof, secret_key, verification_proof
from utils.standby_manager import StandbyFailoverManager
from webapp import app
from webapp import server as server_routes
from webapp import standby_routes as standby_routes
from webapp.standby_routes import _is_own_origin, _sync_standby_manager, _verification_matches


class FakeWriter:
    def __init__(self):
        self.data = bytearray()
        self.closed = False

    def write(self, value):
        self.data.extend(value)

    async def drain(self):
        return None

    def close(self):
        self.closed = True

    async def wait_closed(self):
        return None


class FakeRawHeaders:
    def __init__(self, cookies=()):
        self.cookies = list(cookies)

    def getlist(self, name):
        return list(self.cookies) if name == "Set-Cookie" else []


def fake_upstream(status_code=200, content=b"{}", headers=None, cookies=()):
    """A ``requests.Response`` stand-in with the attributes the routes read."""
    return type("Upstream", (), {
        "status_code": status_code,
        "content": content,
        "ok": 200 <= status_code < 400,
        "text": content.decode("utf-8", "replace"),
        "headers": dict(headers or {}),
        "raw": SimpleNamespace(headers=FakeRawHeaders(cookies)),
        "json": lambda self: json.loads(self.content.decode("utf-8") or "{}"),
        "close": lambda self: None,
    })()


def blocked_upstream():
    """Return a Cloudflare-blocked Discord response, as the REST client sees it."""
    response = fake_upstream(
        status_code=403,
        content=b"Attention Required!",
        headers={"Server": "cloudflare", "CF-Ray": "abc"},
    )
    response.text = "Attention Required!"
    return response


def configured_manager():
    """Return a manager whose signed relay could actually be sent."""
    manager = StandbyFailoverManager()
    manager.set_standbys(["https://standby.example"], ["east"])
    manager.active_origin = "https://standby.example"
    return manager


def relay_secrets():
    return patch.dict(os.environ, {"DISCORD_BOT_TOKEN": "token", "SESSION_SECRET": "session"})


def owner_dashboard_client():
    """Return a test client signed in as the bot owner with a valid CSRF token."""
    from config.ids import OWNER_IDS

    client = app.test_client()
    with client.session_transaction() as session:
        session["user"] = {"id": str(next(iter(OWNER_IDS)))}
        session["access_token"] = "test-token"
        session["token_exp"] = time.time() + 3600
        session["csrf_token"] = "test-csrf"
    return client


class StandbyFailoverTests(unittest.TestCase):
    def test_registration_proof_requires_both_production_secrets(self):
        key = secret_key("production-token", "production-session")
        nonce = "unique-standby-registration-challenge"
        proof = verification_proof(key, nonce)

        self.assertTrue(_verification_matches(key, nonce, proof))
        self.assertFalse(_verification_matches(secret_key("other-token", "production-session"), nonce, proof))
        self.assertFalse(_verification_matches(secret_key("production-token", "other-session"), nonce, proof))
        self.assertFalse(_verification_matches(key, nonce, None))

    def test_relay_url_allows_any_discord_api_path_but_rejects_untrusted_targets(self):
        self.assertTrue(_is_allowed_discord_api_url("https://discord.com/api/v10/users/@me"))
        self.assertTrue(_is_allowed_discord_api_url("https://discord.com/api/oauth2/token"))
        self.assertTrue(_is_allowed_discord_api_url("https://discord.com/api/oauth2/token?source=callback"))
        self.assertTrue(_is_allowed_discord_api_url("https://discord.com/api/v11/new-endpoint"))
        self.assertTrue(_is_allowed_discord_api_url("https://discord.com/experiments"))
        self.assertFalse(_is_allowed_discord_api_url("http://discord.com/api/oauth2/token"))
        self.assertFalse(_is_allowed_discord_api_url("https://discord.com.evil.example/api/oauth2/token"))
        self.assertFalse(_is_allowed_discord_api_url("https://discord.com:443/api/oauth2/token"))
        self.assertFalse(_is_allowed_discord_api_url("https://discord.com/api/oauth2/token#fragment"))

    def test_oauth_relay_endpoint_accepts_signed_discord_token_exchange(self):
        async def scenario():
            key = secret_key("token", "session")
            request_body = b"client_id=id&grant_type=authorization_code"
            request_headers = {"Content-Type": "application/x-www-form-urlencoded"}
            timestamp = str(int(time.time()))
            nonce = "oauth-relay-nonce-000000000000000000"
            url = "https://discord.com/api/oauth2/token"
            proof = relay_proof(key, timestamp, nonce, "POST", url, request_headers, request_body)
            envelope = {
                "method": "POST",
                "url": url,
                "headers": request_headers,
                "body": base64.b64encode(request_body).decode("ascii"),
                "timestamp": timestamp,
                "nonce": nonce,
                "proof": proof,
            }
            encoded = json.dumps(envelope, separators=(",", ":")).encode()
            reader = asyncio.StreamReader()
            reader.feed_data(encoded)
            reader.feed_eof()
            writer = FakeWriter()

            async def mock_to_thread(call, *args, **kwargs):
                self.assertEqual("forward", call.__name__)
                return {"status": 200, "headers": {"content-type": "application/json"}, "body": "e30="}

            import utils.standby_failover as standby_failover
            previous_stats = standby_failover._STATS.copy()
            standby_failover._RELAY_NONCES.clear()
            with patch("utils.standby_failover.asyncio.to_thread", side_effect=mock_to_thread):
                await standby_failover._relay_discord_request(reader, writer, {"content-length": str(len(encoded))}, key)
            self.assertIn(b"HTTP/1.1 200 OK", writer.data)
            self.assertIn(b'"status":200', writer.data)
            standby_failover._STATS.update(previous_stats)
            standby_failover._RELAY_NONCES.clear()

        asyncio.run(scenario())

    def test_health_identifies_standby_backend(self):
        async def scenario():
            reader = asyncio.StreamReader()
            reader.feed_data(b"GET /health HTTP/1.1\r\nHost: standby.example\r\n\r\n")
            reader.feed_eof()
            writer = FakeWriter()
            await _handle_client(reader, writer, secret_key("token", "session"))
            self.assertIn(b'"service":"niko-standby-backend"', writer.data)
            self.assertNotIn(b"proxy", writer.data.lower())

        asyncio.run(scenario())

    def test_authenticated_gateway_control_rejects_replayed_nonce(self):
        from utils import standby_failover

        class Controller:
            def __init__(self):
                self.actions = []

            async def activate(self):
                self.actions.append("activate")

            async def relinquish(self):
                self.actions.append("relinquish")

        async def send_request(key, nonce, proof):
            body = json.dumps({"action": "activate", "nonce": nonce, "proof": proof}).encode()
            raw = (
                b"POST /internal/standby/control HTTP/1.1\r\nContent-Length: "
                + str(len(body)).encode()
                + b"\r\n\r\n"
                + body
            )
            reader = asyncio.StreamReader()
            reader.feed_data(raw)
            reader.feed_eof()
            writer = FakeWriter()
            await _handle_client(reader, writer, key)
            return writer.data

        async def scenario():
            key = secret_key("token", "session")
            controller = Controller()
            standby_failover._GATEWAY_CONTROLLER = controller
            standby_failover._CONTROL_NONCES.clear()
            nonce = "standby-control-nonce-00000000000001"
            proof = control_proof(key, "activate", nonce)
            self.assertIn(b"200 OK", await send_request(key, nonce, proof))
            self.assertIn(b"403", await send_request(key, nonce, proof))
            self.assertEqual(["activate"], controller.actions)
            standby_failover._GATEWAY_CONTROLLER = None
            standby_failover._CONTROL_NONCES.clear()

        asyncio.run(scenario())

    def test_standby_manager_is_the_only_static_login_wrapper(self):
        class HTTP:
            _HTTPClient__session = None

            async def static_login(self, token):
                return token

        class Bot:
            http = HTTP()

        bot = Bot()
        original_login = bot.http.static_login
        standby = StandbyFailoverManager()
        standby.attach(bot)
        standby_login = bot.http.static_login

        proxy = WebshareProxyManager("test-key")
        proxy.attach(bot)

        self.assertIs(bot.http.static_login, standby_login)
        self.assertIsNot(bot.http.static_login, original_login)

    def test_static_login_detects_initial_cloudflare_block_and_selects_standby(self):
        class Response:
            def __init__(self, status, headers=None, text=""):
                self.status = status
                self.headers = headers or {}
                self._text = text
                self.released = False

            async def text(self):
                return self._text

            def release(self):
                self.released = True

        class Session:
            async def _request(self, method, url, **kwargs):
                return Response(403, {"Server": "cloudflare", "CF-Ray": "cloudflare-ray"}, "Attention Required!")

        class HTTP:
            _HTTPClient__session = None

            async def request(self, *args, **kwargs):
                return await self._HTTPClient__session._request(*args, **kwargs)

            async def static_login(self, token):
                self._HTTPClient__session = Session()
                response = await self.request("GET", "https://discord.com/api/v10/users/@me")
                return response.status

        class Bot:
            def __init__(self):
                self.http = HTTP()
                self.proxy_manager = None

        async def scenario():
            bot = Bot()
            manager = StandbyFailoverManager()
            manager.attach(bot)
            manager.select_standby = AsyncMock(return_value=True)
            manager.handoff_to_standby = AsyncMock(return_value=True)
            manager.relay_aiohttp = AsyncMock(return_value=Response(200))

            self.assertEqual(200, await bot.http.static_login("token"))
            manager.select_standby.assert_awaited_once_with()
            manager.handoff_to_standby.assert_awaited_once_with()
            manager.relay_aiohttp.assert_awaited_once()
            self.assertTrue(manager.egress_blocked)

        asyncio.run(scenario())

    def test_cloudflare_hook_prefers_standby_and_uses_proxy_only_if_unavailable(self):
        class Response:
            def __init__(self, status, headers=None, text=""):
                self.status = status
                self.headers = headers or {}
                self._text = text
                self.released = False

            async def text(self):
                return self._text

            def release(self):
                self.released = True

        class Session:
            def __init__(self, http):
                self.http = http
                self.calls = []

            async def _request(self, method, url, **kwargs):
                self.calls.append(kwargs.get("proxy"))
                if kwargs.get("proxy"):
                    return Response(200)
                return Response(403, {"Server": "cloudflare", "CF-Ray": "cloudflare-ray"}, "Attention Required!")

        class Proxy:
            def __init__(self, http):
                self.http = http
                self.enable_calls = 0

            async def enable(self):
                self.enable_calls += 1
                self.http.proxy = "http://proxy.example"

        async def scenario():
            http = type("HTTP", (), {"proxy": None, "proxy_auth": None})()
            bot = type("Bot", (), {"http": http})()
            manager = StandbyFailoverManager()
            manager.bot = bot
            manager.http = http
            proxy = Proxy(http)
            bot.proxy_manager = proxy
            session = Session(http)
            manager._install_hook(session)

            manager.set_standbys(["https://east.example"], ["east"])
            manager.select_standby = AsyncMock(return_value=True)
            manager.handoff_to_standby = AsyncMock(return_value=True)
            manager.relay_aiohttp = AsyncMock(return_value=Response(200))
            relayed = await session._request("GET", "https://discord.com/api/v10/users/@me")
            self.assertEqual(200, relayed.status)
            manager.select_standby.assert_awaited_once_with()
            manager.relay_aiohttp.assert_awaited_once()
            self.assertEqual(0, proxy.enable_calls)

            manager.active_origin = None
            manager.select_standby = AsyncMock(return_value=False)
            manager.relay_aiohttp = AsyncMock(return_value=Response(200))
            session.calls.clear()
            proxied = await session._request("GET", "https://discord.com/api/v10/users/@me")
            self.assertEqual(200, proxied.status)
            manager.select_standby.assert_awaited_once_with()
            self.assertEqual(1, proxy.enable_calls)
            self.assertEqual([None, "http://proxy.example"], session.calls)
            manager.relay_aiohttp.assert_not_awaited()

        asyncio.run(scenario())

    def test_aiohttp_relay_awaits_request_before_entering_response_context(self):
        class RelayResponse:
            status = 200

            def __init__(self):
                self.entered = False
                self.exited = False

            async def __aenter__(self):
                self.entered = True
                return self

            async def __aexit__(self, *exc):
                self.exited = True

            async def json(self):
                return {"status": 204, "headers": {"X-Relay": "ok"}, "body": ""}

        async def scenario():
            manager = StandbyFailoverManager()
            manager.active_origin = "https://standby.example"
            relay_response = RelayResponse()
            request_calls = []

            async def original_request(method, url, **kwargs):
                request_calls.append((method, url, kwargs))
                return relay_response

            with patch.object(manager, "_signed_envelope", return_value=(
                "https://standby.example/internal/standby/discord", {"proof": "signed"}
            )):
                response = await manager.relay_aiohttp(
                    original_request, "GET", "https://discord.com/api/v10/users/@me", {}
                )

            self.assertEqual(204, response.status)
            self.assertEqual({"X-Relay": "ok"}, dict(response.headers))
            self.assertTrue(relay_response.entered)
            self.assertTrue(relay_response.exited)
            self.assertEqual(1, len(request_calls))
            self.assertEqual("POST", request_calls[0][0])
            self.assertEqual("https://standby.example/internal/standby/discord", request_calls[0][1])

        asyncio.run(scenario())

    def test_static_cloudflare_check_uses_requests_text_property(self):
        response = type("Response", (), {
            "status_code": 403,
            "headers": {"Server": "cloudflare", "CF-Ray": "abc"},
            "text": "Attention Required!",
        })()

        self.assertTrue(StandbyFailoverManager.is_cloudflare_block(response))

    def test_discord_rate_limit_is_not_reported_as_a_cloudflare_block(self):
        # Discord answers through Cloudflare, so ``CF-Ray`` is present on every
        # response. A plain rate limit is Discord's own answer, not a block, and
        # reporting it as one produced "Cloudflare ban" logs that never happened.
        rate_limited = fake_upstream(
            status_code=429,
            content=b'{"message":"You are being rate limited."}',
            headers={"Server": "cloudflare", "CF-Ray": "abc", "Content-Type": "application/json"},
        )
        rate_limited.text = '{"message":"You are being rate limited.","retry_after":2.5,"global":false}'
        forbidden = fake_upstream(
            status_code=403,
            content=b'{"message":"Missing Permissions","code":50013}',
            headers={"Server": "cloudflare", "CF-Ray": "abc"},
        )
        forbidden.text = '{"message":"Missing Permissions","code":50013}'

        self.assertFalse(StandbyFailoverManager.is_cloudflare_block(rate_limited))
        self.assertFalse(StandbyFailoverManager.is_cloudflare_block(forbidden))
        # A real interstitial still is one.
        self.assertTrue(StandbyFailoverManager.is_cloudflare_block(blocked_upstream()))

    def test_discord_answers_without_an_interstitial_are_never_a_block(self):
        # The production regression: every Discord response carries ``CF-Ray`` and
        # ``Server: cloudflare``, so a 429 whose body is not a Cloudflare page was
        # reported as a ban and tried to move traffic off a working egress. Only
        # an interstitial makes a block.
        def upstream(status_code, text, headers=None):
            response = fake_upstream(status_code=status_code, content=text.encode(), headers=headers)
            response.text = text
            return response

        cf_headers = {"Server": "cloudflare", "CF-Ray": "abc"}
        for status_code, text in (
            (429, ""),
            (429, "Too Many Requests"),
            (503, ""),
            (403, "Forbidden"),
            (429, "{\"message\":\"You are being rate limited.\",\"retry_after\":1.0}"),
        ):
            with self.subTest(status=status_code, body=text[:20]):
                self.assertFalse(
                    StandbyFailoverManager.is_cloudflare_block(upstream(status_code, text, cf_headers))
                )

        challenged = upstream(403, "", dict(cf_headers, **{"cf-mitigated": "challenge"}))
        denied = upstream(403, "error code: 1020", cf_headers)
        page = upstream(403, "<html><title>Attention Required!</title>", cf_headers)
        for response in (challenged, denied, page):
            self.assertTrue(StandbyFailoverManager.is_cloudflare_block(response))
        # Cloudflare's edge answers a rate-limited request with the same error page,
        # so a 429 is a throttle and must not be reported as a denied egress.
        throttled = upstream(429, '<html><div class="cf-error-details">Error 1015</div></html>', cf_headers)
        self.assertFalse(StandbyFailoverManager.is_cloudflare_block(throttled))
        # It is still Cloudflare's own page, which is what the REST hook routes
        # through the proxy egress instead of handing the gateway to a standby.
        self.assertTrue(StandbyFailoverManager.cloudflare_interstitial(throttled) is not None)

    def test_discord_rate_limit_keeps_the_instance_on_its_own_egress(self):
        class Response:
            def __init__(self, status, headers=None, text=""):
                self.status = status
                self.headers = headers or {}
                self._text = text

            async def text(self):
                return self._text

            def release(self):
                return None

        class Session:
            async def _request(self, method, url, **kwargs):
                return Response(429, {"Server": "cloudflare", "CF-Ray": "cloudflare-ray"}, "")

        async def scenario():
            manager = StandbyFailoverManager()
            manager.bot = SimpleNamespace(proxy_manager=None)
            manager.http = SimpleNamespace(proxy=None, proxy_auth=None)
            manager.set_standbys(["https://standby.example"], ["east"])
            manager.egress_blocked = True
            session = Session()
            manager._install_hook(session)
            manager.select_standby = AsyncMock(return_value=True)
            manager.handoff_to_standby = AsyncMock(return_value=True)

            response = await session._request("GET", "https://discord.com/api/v10/users/@me")

            self.assertEqual(429, response.status)
            manager.select_standby.assert_not_awaited()
            manager.handoff_to_standby.assert_not_awaited()
            self.assertIsNone(manager.active_origin)
            # Discord answering at all proves this instance is not blocked, so a
            # stale "Cloudflare ban" state is cleared instead of carried forward.
            self.assertFalse(manager.egress_blocked)

        asyncio.run(scenario())

    def test_discord_request_uses_the_bots_egress(self):
        manager = StandbyFailoverManager()
        http = SimpleNamespace(user_agent="DiscordBot (https://example.invalid, 2.7.1)", proxy="http://proxy.example:8080")
        client = Mock(return_value=fake_upstream(status_code=200, content=b"{}"))

        with patch.object(
            server_routes, "_discord_bot", SimpleNamespace(http=http, standby_failover=manager)
        ), patch.object(server_routes.req, "get", client):
            server_routes.discord_request(
                "GET", "https://discord.com/api/v10/users/@me", headers={"Authorization": "Bearer token"}
            )

        kwargs = client.call_args.kwargs
        self.assertEqual("DiscordBot (https://example.invalid, 2.7.1)", kwargs["headers"]["User-Agent"])
        # Discord answers this deployment's own egress once it carries the bot's
        # identity, so the proxy is the fallback for a blocked attempt rather than
        # the default route for every browser call.
        self.assertNotIn("proxies", kwargs)
        self.assertEqual("Bearer token", kwargs["headers"]["Authorization"])

    def test_blocked_browser_request_retries_over_the_bots_proxy(self):
        manager = StandbyFailoverManager()
        http = SimpleNamespace(user_agent="DiscordBot (https://example.invalid, 2.7.1)", proxy="http://proxy.example:8080")
        direct = blocked_upstream()
        direct.close = Mock()
        proxied = fake_upstream(status_code=200, content=b'{"id":"1"}', headers={"Content-Type": "application/json"})
        client = Mock(side_effect=[direct, proxied])

        with patch.object(
            server_routes, "_discord_bot", SimpleNamespace(http=http, standby_failover=manager)
        ), patch.object(server_routes.req, "get", client):
            response = server_routes.discord_request("GET", "https://discord.com/api/v10/users/@me")

        self.assertIs(proxied, response)
        self.assertNotIn("proxies", client.call_args_list[0].kwargs)
        self.assertEqual(
            {"http": "http://proxy.example:8080", "https": "http://proxy.example:8080"},
            client.call_args_list[1].kwargs["proxies"],
        )
        direct.close.assert_called_once_with()

    def test_team_membership_check_uses_the_bots_egress_when_a_proxy_is_active(self):
        """The production report: ``/api/team-recruitment/membership`` answered 503.

        The membership lookup went out as a bare requests client from this host, so
        Cloudflare's edge refused it exactly when the bot had already moved its own
        traffic to Webshare — team applications then could not check support server
        membership at all. It shares the bot's egress now.
        """
        from webapp import team_recruitment_routes as routes

        http = SimpleNamespace(user_agent="DiscordBot (https://example.invalid, 2.7.1)", proxy="http://proxy.example:8080")
        manager = StandbyFailoverManager()

        def call(url, **kwargs):
            if kwargs.get("proxies"):
                return fake_upstream(status_code=200, content=b'{"user":{"id":"1"}}', headers={"Content-Type": "application/json"})
            return blocked_upstream()

        client = owner_dashboard_client()
        with patch.object(server_routes, "_current_user_blacklist_entry", return_value=None), patch.object(
            server_routes, "_discord_bot", SimpleNamespace(http=http, standby_failover=manager)
        ), patch.object(routes, "DISCORD_BOT_TOKEN", "bot-token"), patch.object(server_routes.req, "get", side_effect=call):
            response = client.get("/api/team-recruitment/membership")

        self.assertEqual(200, response.status_code)
        self.assertEqual({"member": True}, response.get_json())

    def test_oauth_token_exchange_retries_over_the_bots_proxy(self):
        """Login has no failover of its own: a blocked token exchange is retried."""
        from webapp import auth_routes

        http = SimpleNamespace(user_agent="DiscordBot (https://example.invalid, 2.7.1)", proxy="http://proxy.example:8080")
        manager = StandbyFailoverManager()
        token_body = b'{"access_token":"token","refresh_token":"refresh","expires_in":3600}'

        def post(url, **kwargs):
            if kwargs.get("proxies"):
                return fake_upstream(status_code=200, content=token_body, headers={"Content-Type": "application/json"})
            return blocked_upstream()

        client = app.test_client()
        with client.session_transaction() as session:
            session["oauth_state"] = "callback-state"
        with patch.object(server_routes, "_discord_bot", SimpleNamespace(http=http, standby_failover=manager)), patch.object(
            server_routes.req, "post", side_effect=post
        ), patch.object(auth_routes, "discord_get", return_value={"id": "1", "username": "user"}):
            response = client.get("/auth/callback?code=abc&state=callback-state")

        self.assertEqual(302, response.status_code)
        self.assertEqual("/dashboard", response.headers["Location"])

    def test_blocked_discord_request_without_a_configured_relay_stays_a_block(self):
        # The production outage: a Cloudflare block was relayed even though no
        # standby origin was active, and the relay misconfiguration surfaced as
        # a 500 from every request that touched the Discord API.
        manager = StandbyFailoverManager()
        blocked = blocked_upstream()
        manager.request_via_standby = Mock(side_effect=AssertionError("relay must not be attempted"))
        self.assertFalse(manager.relay_configured())

        with patch.object(server_routes, "_discord_bot", SimpleNamespace(standby_failover=manager)), patch.object(
            server_routes.req, "get", return_value=blocked
        ):
            response = server_routes.discord_request("GET", "https://discord.com/api/v10/users/@me")

        self.assertIs(blocked, response)
        manager.request_via_standby.assert_not_called()

    def test_blocked_discord_request_returns_the_block_when_the_relay_fails(self):
        manager = configured_manager()
        blocked = blocked_upstream()
        manager.request_via_standby = Mock(side_effect=RuntimeError("Standby API relay is not configured."))

        with relay_secrets(), patch.object(
            server_routes, "_discord_bot", SimpleNamespace(standby_failover=manager)
        ), patch.object(server_routes.req, "get", return_value=blocked):
            response = server_routes.discord_request("GET", "https://discord.com/api/v10/users/@me")

        self.assertIs(blocked, response)
        self.assertEqual("Standby API relay failed (RuntimeError).", manager.last_error)

    def test_blocked_discord_request_returns_the_relayed_response_when_configured(self):
        manager = configured_manager()
        blocked = blocked_upstream()
        relayed = fake_upstream(status_code=200, content=b'{"id":"1"}')
        manager.request_via_standby = Mock(return_value=relayed)

        with relay_secrets(), patch.object(
            server_routes, "_discord_bot", SimpleNamespace(standby_failover=manager)
        ), patch.object(server_routes.req, "get", return_value=blocked):
            response = server_routes.discord_request("GET", "https://discord.com/api/v10/users/@me")

        self.assertIs(relayed, response)
        self.assertTrue(manager.relay_configured())

    def test_auth_callback_redirects_a_failed_token_exchange_instead_of_returning_500(self):
        from webapp import auth_routes

        client = app.test_client()
        # No standby origin is active, so the request stays on this instance and
        # the callback exercises its own token-exchange error handling.
        manager = StandbyFailoverManager()
        manager.request_via_standby = Mock(side_effect=AssertionError("relay must not be attempted"))

        def callback(post):
            with client.session_transaction() as session:
                session["oauth_state"] = "callback-state"
            # The deployed instance has both relay secrets but no standby origin
            # registered, which is exactly how the 500 was reached.
            with relay_secrets(), patch.object(
                server_routes, "_discord_bot", SimpleNamespace(standby_failover=manager)
            ), patch.object(auth_routes.req, "post", post):
                return client.get("/auth/callback?code=abc&state=callback-state")

        # A Cloudflare block must be answered directly, not relayed without a
        # standby origin — that misconfiguration is what produced the 500.
        blocked = callback(Mock(return_value=blocked_upstream()))
        self.assertEqual(302, blocked.status_code)
        self.assertIn("error=token_exchange_failed", blocked.headers["Location"])
        manager.request_via_standby.assert_not_called()

        # Unreachable Discord is a failed login too, not a server error.
        unreachable = callback(Mock(side_effect=requests.RequestException("blocked")))
        self.assertEqual(302, unreachable.status_code)
        self.assertIn("error=token_exchange_failed", unreachable.headers["Location"])

    def test_cloudflare_edge_rate_limit_keeps_the_instance_on_its_own_egress(self):
        """The production report: a 429 on the first REST call after a restart.

        Cloudflare's edge throttles that call (its own ``cf-error-details`` page),
        the Webshare egress answers the retry, and the instance keeps its own route:
        no standby selection, no gateway handoff, no "Cloudflare ban" state, and no
        error about standbys being unavailable.
        """

        class Response:
            def __init__(self, status, headers=None, text=""):
                self.status = status
                self.headers = headers or {}
                self._text = text
                self.released = False

            async def text(self):
                return self._text

            def release(self):
                self.released = True

        class Session:
            def __init__(self):
                self.calls = []

            async def _request(self, method, url, **kwargs):
                self.calls.append(kwargs.get("proxy"))
                if kwargs.get("proxy"):
                    return Response(200, {"Content-Type": "application/json"}, '{"id":"1"}')
                return Response(
                    429,
                    {"Server": "cloudflare", "CF-Ray": "abc", "Retry-After": "60"},
                    '<html><div class="cf-error-details">Error 1015 — you are being rate limited</div></html>',
                )

        class Proxy:
            def __init__(self, http):
                self.http = http
                self.enable_calls = 0

            async def enable(self):
                self.enable_calls += 1
                self.http.proxy = "http://proxy.example"

        async def scenario():
            http = SimpleNamespace(
                proxy=None,
                proxy_auth=None,
                user_agent="DiscordBot (https://example.invalid, 2.7.1)",
            )
            manager = StandbyFailoverManager()
            manager.bot = SimpleNamespace(http=http, proxy_manager=Proxy(http))
            manager.http = http
            manager.set_standbys(["https://standby.example"], ["east"])
            session = Session()
            manager._install_hook(session)
            manager.select_standby = AsyncMock(return_value=False)
            manager.handoff_to_standby = AsyncMock(return_value=True)

            response = await session._request("GET", "https://discord.com/api/v10/users/@me")

            self.assertEqual(200, response.status)
            self.assertEqual([None, "http://proxy.example"], session.calls)
            self.assertEqual(1, manager.bot.proxy_manager.enable_calls)
            manager.select_standby.assert_not_awaited()
            manager.handoff_to_standby.assert_not_awaited()
            self.assertIsNone(manager.active_origin)
            # A throttle leaves no "Cloudflare ban" state behind.
            self.assertFalse(manager.egress_blocked)

        asyncio.run(scenario())

    def test_egress_probe_uses_the_bots_own_identity(self):
        # Cloudflare challenges a plain ``python-requests`` client from a
        # datacenter IP, so the probe must present the bot's own User-Agent and
        # egress or it reports a block while the bot is answering normally.
        async def scenario():
            manager = StandbyFailoverManager()
            manager.http = SimpleNamespace(
                user_agent="DiscordBot (https://example.invalid, 2.7.1)",
                proxy="http://proxy.example:8080",
            )
            healthy = type("Response", (), {"status_code": 200, "headers": {}, "text": "{}"})()
            client = Mock(return_value=healthy)

            with patch("utils.standby_manager.requests.get", client):
                self.assertFalse(await manager.check_direct_egress())

            self.assertEqual("https://discord.com/api/v10/gateway", client.call_args.args[0])
            self.assertEqual(
                "DiscordBot (https://example.invalid, 2.7.1)",
                client.call_args.kwargs["headers"]["User-Agent"],
            )
            self.assertEqual(
                {"http": "http://proxy.example:8080", "https": "http://proxy.example:8080"},
                client.call_args.kwargs["proxies"],
            )
            self.assertTrue(manager.direct_egress_verified)

        asyncio.run(scenario())

    def test_async_cloudflare_check_awaits_aiohttp_text_method(self):
        class Response:
            status = 403
            headers = {"Server": "cloudflare", "CF-Ray": "abc"}

            async def text(self):
                return "Attention Required!"

        async def scenario():
            self.assertTrue(await StandbyFailoverManager()._async_cloudflare_block(Response()))

        asyncio.run(scenario())

    def test_manager_selects_healthy_full_backend(self):
        async def scenario():
            manager = StandbyFailoverManager()
            manager.set_standbys(["https://east.example"], ["standby-east"])
            with patch.object(manager, "probe_standby", return_value={"service": "niko-standby-backend"}):
                self.assertTrue(await manager.activate_standby("standby-east"))
                self.assertFalse(await manager.activate_standby("unknown"))
            self.assertEqual("standby-east", manager.status()["active_standby_id"])
            self.assertEqual("standby", manager.status()["mode"])

        asyncio.run(scenario())

    def test_active_standby_routes_general_backend_requests(self):
        manager = SimpleNamespace(
            active_origin="https://standby.example",
            origins=["https://standby.example"],
        )
        upstream = type("Upstream", (), {
            "status_code": 202,
            "content": b'{"handled_by":"standby"}',
            "headers": {"Content-Type": "application/json", "X-Backend": "standby"},
            "close": lambda self: None,
        })()
        with patch.object(server_routes, "_discord_bot", SimpleNamespace(standby_failover=manager)), patch.object(
            server_routes.req, "request", return_value=upstream
        ) as request_upstream:
            with app.test_client() as client:
                response = client.post(
                    "/api/guild/123/config/server?view=full",
                    json={"name": "Cafe"},
                    headers={"Host": "production.example", "X-CSRF-Token": "csrf-token"},
                )

        self.assertEqual(202, response.status_code)
        self.assertEqual({"handled_by": "standby"}, response.get_json())
        self.assertEqual("standby", response.headers["X-Backend"])
        args, kwargs = request_upstream.call_args
        self.assertEqual("POST", args[0])
        self.assertEqual("https://standby.example/api/guild/123/config/server?view=full", args[1])
        forwarded_headers = {name.lower(): value for name, value in kwargs["headers"].items()}
        self.assertEqual("application/json", forwarded_headers["content-type"])
        self.assertEqual("csrf-token", forwarded_headers["x-csrf-token"])
        # The production host must not reach the standby's own edge, which owns
        # only its registered origin; it travels in X-Forwarded-Host instead.
        self.assertNotIn("host", forwarded_headers)
        self.assertEqual("production.example", forwarded_headers["x-forwarded-host"])
        self.assertEqual(b'{"name": "Cafe"}', kwargs["data"])
        self.assertFalse(kwargs["allow_redirects"])

    def test_active_standby_routes_frontend_and_static_assets(self):
        manager = SimpleNamespace(
            active_origin="https://standby.example",
            origins=["https://standby.example"],
        )
        upstream = type("Upstream", (), {
            "status_code": 200,
            "content": b"standby frontend asset",
            "headers": {"Content-Type": "text/javascript", "Cache-Control": "public, max-age=60"},
            "close": lambda self: None,
        })()
        with patch.object(server_routes, "_discord_bot", SimpleNamespace(standby_failover=manager)), patch.object(
            server_routes.req, "request", return_value=upstream
        ) as request_upstream:
            with app.test_client() as client:
                response = client.get("/assets/app.js?v=123")

        self.assertEqual(200, response.status_code)
        self.assertEqual(b"standby frontend asset", response.data)
        self.assertEqual("text/javascript", response.headers["Content-Type"])
        self.assertEqual("https://standby.example/assets/app.js?v=123", request_upstream.call_args.args[1])
        self.assertFalse(request_upstream.call_args.kwargs["allow_redirects"])

    def test_standby_relay_addresses_the_registered_origin_not_the_production_host(self):
        """The production host is bound to the primary, so relaying it 404s upstream."""
        manager = SimpleNamespace(
            active_origin="https://standby.example",
            origins=["https://standby.example"],
        )
        upstream = type("Upstream", (), {
            "status_code": 200,
            "content": b"<html>standby frontend</html>",
            "headers": {"Content-Type": "text/html"},
            "close": lambda self: None,
        })()
        with patch.object(server_routes, "_discord_bot", SimpleNamespace(standby_failover=manager)), patch.object(
            server_routes.req, "request", return_value=upstream
        ) as request_upstream:
            with app.test_client() as client:
                response = client.get(
                    "/",
                    headers={"Host": "production.example", "X-Forwarded-Proto": "https"},
                )

        self.assertEqual(200, response.status_code)
        self.assertEqual(b"<html>standby frontend</html>", response.data)
        self.assertEqual("https://standby.example/", request_upstream.call_args.args[1])
        forwarded = {name.lower(): value for name, value in request_upstream.call_args.kwargs["headers"].items()}
        self.assertNotIn("host", forwarded)
        self.assertEqual("production.example", forwarded["x-forwarded-host"])
        self.assertEqual("https", forwarded["x-forwarded-proto"])

    def test_standby_listener_shows_the_production_host_to_the_application(self):
        """A relayed request keeps the production host for OAuth callbacks and cookies."""
        seen = {}

        def application(environ, start_response):
            seen["host"] = environ["HTTP_HOST"]
            seen["scheme"] = environ["wsgi.url_scheme"]
            start_response("200 OK", [("Content-Type", "text/html")])
            return [b"ok"]

        _dispatch_web_request(
            application,
            "GET",
            "/",
            {"host": "standby.example", "x-forwarded-host": "production.example", "x-forwarded-proto": "https"},
            b"",
        )
        self.assertEqual("production.example", seen["host"])
        self.assertEqual("https", seen["scheme"])

        _dispatch_web_request(application, "GET", "/", {"host": "standby.example"}, b"")
        self.assertEqual("standby.example", seen["host"])

    def test_standby_service_routes_are_exposed_through_the_production_url(self):
        manager = SimpleNamespace(
            active_origin="https://standby.example",
            origins=["https://standby.example"],
        )
        upstream = type("Upstream", (), {
            "status_code": 200,
            "content": b'{"ok":true,"service":"niko-standby-backend"}',
            "headers": {"Content-Type": "application/json"},
            "close": lambda self: None,
        })()
        with patch.object(server_routes, "_discord_bot", SimpleNamespace(standby_failover=manager)), patch.object(
            server_routes.req, "request", return_value=upstream
        ) as request_upstream:
            with app.test_client() as client:
                health_response = client.get("/health")
                verify_response = client.post("/internal/standby/verify", json={"nonce": "n" * 32})

        self.assertEqual(200, health_response.status_code)
        self.assertEqual("niko-standby-backend", health_response.get_json()["service"])
        self.assertEqual(200, verify_response.status_code)
        self.assertEqual(
            ["https://standby.example/health", "https://standby.example/internal/standby/verify"],
            [call.args[1] for call in request_upstream.call_args_list],
        )

    def test_no_active_standby_answers_health_locally_and_relay_with_503(self):
        manager = SimpleNamespace(active_origin=None, origins=["https://standby.example"])
        with patch.object(server_routes, "_discord_bot", SimpleNamespace(standby_failover=manager)), patch.object(
            server_routes.req, "request"
        ) as request_upstream:
            with app.test_client() as client:
                health_response = client.get("/health")
                relay_response = client.post("/internal/standby/verify", json={"nonce": "n" * 32})

        self.assertEqual(200, health_response.status_code)
        self.assertEqual("niko-backend", health_response.get_json()["service"])
        self.assertEqual(503, relay_response.status_code)
        request_upstream.assert_not_called()

    def test_active_standby_route_remains_available_for_control_api(self):
        manager = SimpleNamespace(
            active_origin="https://standby.example",
            origins=["https://standby.example"],
        )
        with patch.object(server_routes, "_discord_bot", SimpleNamespace(standby_failover=manager)), patch.object(
            server_routes.req, "request"
        ) as request_upstream:
            with app.test_client() as client:
                response = client.get("/api/staff/standbys")

        self.assertNotEqual(503, response.status_code)
        request_upstream.assert_not_called()

    def test_active_standby_failure_returns_503_instead_of_stale_primary_data(self):
        manager = SimpleNamespace(
            active_origin="https://standby.example",
            origins=["https://standby.example"],
        )
        with patch.object(server_routes, "_discord_bot", SimpleNamespace(standby_failover=manager)), patch.object(
            server_routes.req, "request", side_effect=requests.RequestException("unavailable")
        ):
            with app.test_client() as client:
                response = client.get("/api/team")

        self.assertEqual(503, response.status_code)
        self.assertEqual("The active standby backend is temporarily unavailable.", response.get_json()["error"])

    def test_webshare_proxy_configuration_is_not_part_of_standby_control(self):
        manager = StandbyFailoverManager()
        manager.set_standbys(["https://east.example"], ["standby-east"])
        manager.active_origin = "https://east.example"

        self.assertTrue(manager.select_failover("auto"))
        self.assertEqual("https://east.example", manager.active_origin)
        with self.assertRaisesRegex(ValueError, "auto or off"):
            manager.select_failover("webshare")
        self.assertTrue(manager.select_failover("off"))
        self.assertIsNone(manager.active_origin)
        self.assertEqual("off", manager.status()["mode"])

    def test_primary_and_standby_agree_on_every_relayable_discord_host(self):
        for url in (
            "https://discord.com/api/v10/users/@me",
            "https://ptb.discord.com/api/v10/users/@me",
            "https://cdn.discordapp.com/attachments/1/2/file.png",
        ):
            self.assertTrue(is_discord_relay_url(url), url)
            self.assertTrue(StandbyFailoverManager._should_relay(url), url)
            self.assertTrue(_is_allowed_discord_api_url(url), url)
        for url in (
            "https://discord.com.evil.example/api/v10/users/@me",
            "https://evildiscord.com/api/v10/users/@me",
            "https://cdn.discordapp.com.evil.example/file.png",
            "http://cdn.discordapp.com/file.png",
            "https://cdn.discordapp.com",
        ):
            self.assertFalse(is_discord_relay_url(url), url)
            self.assertFalse(StandbyFailoverManager._should_relay(url), url)
            self.assertFalse(_is_allowed_discord_api_url(url), url)

    def test_direct_egress_probe_tracks_the_block_state_both_ways(self):
        async def scenario():
            manager = StandbyFailoverManager()
            healthy = type("Response", (), {"status_code": 200, "headers": {}, "text": "{}"})()
            blocked = type("Response", (), {
                "status_code": 403,
                "headers": {"Server": "cloudflare", "CF-Ray": "abc"},
                "text": "Attention Required!",
            })()

            with patch("utils.standby_manager.requests.get", return_value=blocked):
                self.assertFalse(await manager.check_direct_egress())
            self.assertTrue(manager.egress_blocked)
            # A block is not proof the instance can serve the gateway itself.
            self.assertFalse(manager.direct_egress_verified)

            with patch("utils.standby_manager.requests.get", return_value=healthy):
                self.assertFalse(await manager.check_direct_egress())
            self.assertFalse(manager.egress_blocked)
            self.assertTrue(manager.direct_egress_verified)

            with patch("utils.standby_manager.requests.get", side_effect=requests.RequestException("offline")):
                self.assertFalse(await manager.check_direct_egress())
            self.assertFalse(manager.direct_egress_verified)

        asyncio.run(scenario())

    def test_gateway_restore_clears_the_blocked_flag(self):
        class Handoff:
            def __init__(self):
                self.activated = 0
                self.refresh_caches_on_ready = False
                self.connected = asyncio.Event()

            async def activate(self):
                self.activated += 1
                self.connected.set()

            async def relinquish(self):
                return None

        async def scenario():
            manager = StandbyFailoverManager()
            manager.set_standbys(["https://standby.example"], ["standby-east"])
            manager.active_origin = "https://standby.example"
            manager.egress_blocked = True
            manager._recovery_interval = 0
            handoff = Handoff()
            manager.bot = SimpleNamespace(gateway_handoff=handoff)
            manager.control = AsyncMock(return_value=True)
            healthy = type("Response", (), {"status_code": 200, "headers": {}, "text": "{}"})()

            with patch("utils.standby_manager.requests.get", return_value=healthy):
                await asyncio.wait_for(manager._recovery_loop(), timeout=10)

            self.assertIsNone(manager.active_origin)
            self.assertFalse(manager.egress_blocked)
            self.assertEqual(1, handoff.activated)

        asyncio.run(scenario())

    def test_passive_standby_returns_blocked_responses_without_failing_over(self):
        class Response:
            def __init__(self, status, headers=None, text=""):
                self.status = status
                self.headers = headers or {}
                self._text = text

            async def text(self):
                return self._text

            def release(self):
                return None

        class Session:
            async def _request(self, method, url, **kwargs):
                return Response(403, {"Server": "cloudflare", "CF-Ray": "cloudflare-ray"}, "Attention Required!")

        async def scenario():
            manager = StandbyFailoverManager()
            manager.bot = SimpleNamespace(proxy_manager=None)
            manager.http = SimpleNamespace(proxy=None, proxy_auth=None)
            manager.set_standbys(["https://standby.example", "https://self.example"], ["east", "self"])
            # bot.py turns automatic failover off in STANDBY_MODE: a standby only
            # accepts signed handoff commands.
            manager.select_failover("off")
            session = Session()
            manager._install_hook(session)
            manager.select_standby = AsyncMock(return_value=True)
            manager.handoff_to_standby = AsyncMock(return_value=True)

            response = await session._request("GET", "https://discord.com/api/v10/users/@me")

            self.assertEqual(403, response.status)
            manager.select_standby.assert_not_awaited()
            manager.handoff_to_standby.assert_not_awaited()
            self.assertIsNone(manager.active_origin)

        asyncio.run(scenario())

    def test_registry_sync_skips_entries_it_cannot_use(self):
        http = SimpleNamespace(_HTTPClient__session=None, static_login=AsyncMock())
        bot = SimpleNamespace(http=http)
        _sync_standby_manager(bot, [
            {"id": "good", "name": "East", "url": "https://east.example", "created_at": 1},
            {"id": "insecure", "name": "Broken", "url": "http://insecure.example", "created_at": 2},
            {"name": "No id", "url": "https://west.example", "created_at": 3},
        ])

        self.assertEqual(["good"], bot.standby_failover.ids)
        self.assertEqual(["https://east.example"], bot.standby_failover.origins)

    def test_standby_registration_rejects_this_servers_own_origin(self):
        with app.test_request_context("/api/staff/standbys", headers={"Host": "niko.example"}):
            self.assertTrue(_is_own_origin("https://niko.example"))
            # An explicit default port is still the same origin.
            self.assertTrue(_is_own_origin("https://niko.example:443"))
            self.assertFalse(_is_own_origin("https://standby.example"))
            # A standby on the same host but another port stays allowed.
            self.assertFalse(_is_own_origin("https://niko.example:8443"))

    def test_standby_sends_standby_management_to_the_main_instance(self):
        """A standby never writes registry changes itself; the primary owns them."""
        manager = StandbyFailoverManager()
        manager.select_failover = Mock()
        bot = SimpleNamespace(standby_failover=manager)
        upstream = fake_upstream(
            status_code=201,
            content=b'{"ok":true,"standby":{"id":"east"}}',
            headers={"Content-Type": "application/json"},
            cookies=["session=refreshed; Path=/; Secure"],
        )
        client = owner_dashboard_client()

        with patch.dict(os.environ, {"STANDBY_MODE": "true", "STANDBY_PRIMARY_URL": "https://primary.example"}), patch.object(
            server_routes, "_current_user_blacklist_entry", return_value=None
        ), patch.object(standby_routes, "_discord_bot", bot), patch.object(
            standby_routes.requests, "request", return_value=upstream
        ) as forwarded, patch.object(standby_routes, "run_on_bot_loop") as runner:
            response = client.post(
                "/api/staff/standbys",
                json={"name": "East", "url": "https://east.example"},
                headers={"X-CSRF-Token": "test-csrf"},
            )

        self.assertEqual(201, response.status_code)
        self.assertEqual({"ok": True, "standby": {"id": "east"}}, response.get_json())
        self.assertEqual(["session=refreshed; Path=/; Secure"], response.headers.getlist("Set-Cookie"))
        args, kwargs = forwarded.call_args
        self.assertEqual("POST", args[0])
        self.assertEqual("https://primary.example/api/staff/standbys", args[1])
        headers = {name.lower(): value for name, value in kwargs["headers"].items()}
        self.assertEqual("1", headers["x-niko-standby-control"])
        self.assertEqual("test-csrf", headers["x-csrf-token"])
        self.assertNotIn("host", headers)
        # The main instance must resolve the change against its own origin, not
        # against the standby origin this request arrived on.
        self.assertEqual("primary.example", headers["x-forwarded-host"])
        self.assertEqual("https", headers["x-forwarded-proto"])
        self.assertEqual(b'{"name": "East", "url": "https://east.example"}', kwargs["data"])
        # Nothing was added to the standby's own registry or failover targets.
        runner.assert_not_called()
        manager.select_failover.assert_not_called()
        self.assertEqual([], manager.origins)

    def test_standby_sends_failover_control_to_the_main_instance(self):
        manager = StandbyFailoverManager()
        manager.select_failover = Mock()
        bot = SimpleNamespace(standby_failover=manager)
        upstream = fake_upstream(content=b'{"ok":true}', headers={"Content-Type": "application/json"})
        client = owner_dashboard_client()

        with patch.dict(os.environ, {"STANDBY_MODE": "true", "STANDBY_PRIMARY_URL": "https://primary.example"}), patch.object(
            server_routes, "_current_user_blacklist_entry", return_value=None
        ), patch.object(standby_routes, "_discord_bot", bot), patch.object(
            standby_routes.requests, "request", return_value=upstream
        ) as forwarded:
            response = client.post(
                "/api/staff/standbys/failover",
                json={"action": "mode", "mode": "auto"},
                headers={"X-CSRF-Token": "test-csrf"},
            )

        self.assertEqual(200, response.status_code)
        self.assertEqual("https://primary.example/api/staff/standbys/failover", forwarded.call_args.args[1])
        # Re-arming automatic failover belongs to the main instance; the standby
        # must never promote itself or hand its gateway to another instance.
        manager.select_failover.assert_not_called()
        manager.origins = []

    def test_forwarded_standby_management_authenticates_on_the_main_instance(self):
        """The forwarded request is a valid production request, not a stripped one.

        The standby forwards a browser call it received; the main instance has to
        accept it with the same session, CSRF token, and production host, and the
        standby has to hand that answer straight back to the browser.
        """
        manager = StandbyFailoverManager()
        manager.probe_all = Mock(return_value={})
        bot = SimpleNamespace(standby_failover=manager)
        client = owner_dashboard_client()
        seen = {}

        def dispatch(method, url, headers=None, data=None, **kwargs):
            forwarded_headers = {name.lower(): value for name, value in (headers or {}).items()}
            # Replay exactly what the standby sent, as the production instance.
            # The session cookie travels the way a browser sends it: the test
            # client keeps cookies in a jar, so it is re-set from the header the
            # standby forwarded.
            replay = app.test_client()
            for pair in forwarded_headers.get("cookie", "").split(";"):
                name, _, value = pair.strip().partition("=")
                if name and value:
                    replay.set_cookie(name, value)
            with patch.dict(os.environ, {"STANDBY_MODE": "false"}), patch.object(
                standby_routes, "announced_primary_origin", Mock(return_value=None)
            ), patch.object(
                standby_routes, "list_standbys", Mock(return_value=[])
            ), patch.object(
                standby_routes, "_current_staff_role", return_value="owner"
            ), patch.object(standby_routes, "run_on_bot_loop", side_effect=lambda awaitable: awaitable):
                replayed = replay.open(
                    urlsplit(url).path,
                    method=method,
                    headers={
                        "X-CSRF-Token": forwarded_headers.get("x-csrf-token", ""),
                        "X-Forwarded-Host": forwarded_headers.get("x-forwarded-host", ""),
                        "X-Forwarded-Proto": forwarded_headers.get("x-forwarded-proto", ""),
                    },
                )
            seen["status"] = replayed.status_code
            seen["url"] = url
            upstream = requests.Response()
            upstream.status_code = replayed.status_code
            upstream._content = replayed.data
            upstream.headers.update(dict(replayed.headers))
            upstream.raw = None
            return upstream

        with patch.dict(os.environ, {"STANDBY_MODE": "true", "STANDBY_PRIMARY_URL": "https://primary.example"}), patch.object(
            server_routes, "_current_user_blacklist_entry", return_value=None
        ), patch.object(standby_routes, "_discord_bot", bot), patch.object(
            standby_routes.requests, "request", side_effect=dispatch
        ):
            response = client.get("/api/staff/standbys")

        self.assertEqual("https://primary.example/api/staff/standbys", seen["url"])
        self.assertEqual(200, seen["status"])
        self.assertEqual(200, response.status_code)
        self.assertEqual({"standbys": [], "failover": manager.status()}, response.get_json())

    def test_standby_uses_the_announced_main_instance_origin(self):
        manager = StandbyFailoverManager()
        bot = SimpleNamespace(standby_failover=manager)
        upstream = fake_upstream(headers={"Content-Type": "application/json"})
        client = owner_dashboard_client()

        with patch.dict(os.environ, {"STANDBY_MODE": "true"}, clear=False), patch.dict(
            os.environ, {"STANDBY_PRIMARY_URL": "", "PUBLIC_URL": ""}, clear=False
        ), patch.object(
            server_routes, "_current_user_blacklist_entry", return_value=None
        ), patch.object(standby_routes, "_discord_bot", bot), patch.object(
            standby_routes, "announced_primary_origin", Mock(return_value=None)
        ), patch.object(
            standby_routes, "run_on_bot_loop", return_value="https://primary.example"
        ), patch.object(standby_routes.requests, "request", return_value=upstream) as forwarded:
            response = client.get("/api/staff/standbys")

        self.assertEqual(200, response.status_code)
        self.assertEqual("https://primary.example/api/staff/standbys", forwarded.call_args.args[1])

    def test_standby_without_a_known_main_instance_refuses_management(self):
        manager = StandbyFailoverManager()
        bot = SimpleNamespace(standby_failover=manager)
        client = owner_dashboard_client()

        with patch.dict(os.environ, {
            "STANDBY_MODE": "true", "STANDBY_PRIMARY_URL": "", "PUBLIC_URL": "",
        }, clear=False), patch.object(
            server_routes, "_current_user_blacklist_entry", return_value=None
        ), patch.object(standby_routes, "_discord_bot", bot), patch.object(
            standby_routes, "announced_primary_origin", Mock(return_value=None)
        ), patch.object(
            standby_routes, "run_on_bot_loop", return_value=None
        ), patch.object(standby_routes.requests, "request") as forwarded:
            response = client.get("/api/staff/standbys")

        self.assertEqual(503, response.status_code)
        self.assertIn("STANDBY_PRIMARY_URL", response.get_json()["error"])
        forwarded.assert_not_called()

    def test_standby_never_forwards_management_to_a_request_supplied_host(self):
        """A crafted forwarded host must not become the forwarding target."""
        bot = SimpleNamespace(standby_failover=StandbyFailoverManager())
        client = owner_dashboard_client()

        with patch.dict(os.environ, {
            "STANDBY_MODE": "true", "STANDBY_PRIMARY_URL": "", "PUBLIC_URL": "",
        }, clear=False), patch.object(
            server_routes, "_current_user_blacklist_entry", return_value=None
        ), patch.object(standby_routes, "_discord_bot", bot), patch.object(
            standby_routes, "announced_primary_origin", Mock(return_value=None)
        ), patch.object(
            standby_routes, "run_on_bot_loop", return_value=None
        ), patch.object(standby_routes.requests, "request") as forwarded:
            response = client.get(
                "/api/staff/standbys",
                headers={"X-Forwarded-Host": "attacker.example", "X-Forwarded-Proto": "https"},
            )

        self.assertEqual(503, response.status_code)
        forwarded.assert_not_called()

    def test_standby_does_not_relay_an_already_forwarded_management_request(self):
        bot = SimpleNamespace(standby_failover=StandbyFailoverManager())
        client = owner_dashboard_client()

        with patch.dict(os.environ, {"STANDBY_MODE": "true", "STANDBY_PRIMARY_URL": "https://primary.example"}), patch.object(
            server_routes, "_current_user_blacklist_entry", return_value=None
        ), patch.object(standby_routes, "_discord_bot", bot), patch.object(
            standby_routes.requests, "request"
        ) as forwarded:
            response = client.get("/api/staff/standbys", headers={"X-Niko-Standby-Control": "1"})

        self.assertEqual(503, response.status_code)
        self.assertIn("already being forwarded", response.get_json()["error"])
        forwarded.assert_not_called()

    def test_primary_keeps_standby_management_local(self):
        """Without STANDBY_MODE the registry owner answers in place."""
        manager = StandbyFailoverManager()
        bot = SimpleNamespace(standby_failover=manager)
        client = owner_dashboard_client()

        manager.probe_all = Mock(return_value={})
        with patch.dict(os.environ, {"STANDBY_MODE": "false", "STANDBY_PRIMARY_URL": "https://primary.example"}), patch.object(
            server_routes, "_current_user_blacklist_entry", return_value=None
        ), patch.object(standby_routes, "_discord_bot", bot), patch.object(
            standby_routes, "_current_staff_role", return_value="owner"
        ), patch.object(
            standby_routes, "list_standbys", Mock(return_value=[])
        ), patch.object(
            standby_routes, "run_on_bot_loop", side_effect=lambda awaitable: awaitable
        ), patch.object(standby_routes.requests, "request") as forwarded:
            response = client.get("/api/staff/standbys")

        self.assertEqual(200, response.status_code)
        self.assertEqual({"standbys": [], "failover": manager.status()}, response.get_json())
        forwarded.assert_not_called()

    def test_standby_sync_never_arms_failover_targets(self):
        http = SimpleNamespace(_HTTPClient__session=None, static_login=AsyncMock())
        manager = StandbyFailoverManager()
        manager.set_standbys(["https://old.example"], ["old"])
        manager.active_origin = "https://old.example"
        bot = SimpleNamespace(http=http, standby_failover=manager)

        with patch.dict(os.environ, {"STANDBY_MODE": "true"}):
            _sync_standby_manager(bot, [
                {"id": "east", "name": "East", "url": "https://east.example", "created_at": 1},
            ])

        # The standby must not relay Discord REST traffic to itself or to any
        # other standby instance.
        self.assertEqual([], manager.origins)
        self.assertEqual([], manager.ids)
        self.assertIsNone(manager.active_origin)

    def test_sync_still_arms_the_main_instance(self):
        http = SimpleNamespace(_HTTPClient__session=None, static_login=AsyncMock())
        bot = SimpleNamespace(http=http, standby_failover=StandbyFailoverManager())

        with patch.dict(os.environ, {"STANDBY_MODE": "false"}):
            _sync_standby_manager(bot, [
                {"id": "east", "name": "East", "url": "https://east.example", "created_at": 1},
            ])

        self.assertEqual(["https://east.example"], bot.standby_failover.origins)
        self.assertEqual(["east"], bot.standby_failover.ids)

    def test_standby_health_reports_whether_it_holds_the_gateway(self):
        async def scenario():
            from utils import standby_failover

            class Controller:
                def __init__(self):
                    self.active = asyncio.Event()

            async def health():
                reader = asyncio.StreamReader()
                reader.feed_data(b"GET /health HTTP/1.1\r\nHost: standby.example\r\n\r\n")
                reader.feed_eof()
                writer = FakeWriter()
                await _handle_client(reader, writer, secret_key("token", "session"))
                return writer.data

            controller = Controller()
            previous = standby_failover._GATEWAY_CONTROLLER
            try:
                standby_failover._GATEWAY_CONTROLLER = controller
                self.assertIn(b'"gateway":"standby"', await health())
                controller.active.set()
                self.assertIn(b'"gateway":"active"', await health())
            finally:
                standby_failover._GATEWAY_CONTROLLER = previous

        asyncio.run(scenario())

    def test_standby_gateway_state_distinguishes_warm_from_active(self):
        async def scenario():
            manager = StandbyFailoverManager()
            with patch.object(manager, "probe_standby", return_value={"service": "niko-standby-backend"}):
                self.assertEqual("warm", await manager.standby_gateway_state("https://east.example"))
            with patch.object(manager, "probe_standby", return_value={
                "service": "niko-standby-backend", "gateway": "active",
            }):
                self.assertEqual("active", await manager.standby_gateway_state("https://east.example"))
            with patch.object(manager, "probe_standby", return_value=None):
                self.assertEqual("unreachable", await manager.standby_gateway_state("https://east.example"))

        asyncio.run(scenario())

    def test_primary_rearms_a_standby_that_restarted_warm(self):
        async def scenario():
            manager = StandbyFailoverManager()
            manager.set_standbys(["https://east.example"], ["standby-east"])
            manager.active_origin = "https://east.example"
            manager._supervision_interval = 0
            actions = []

            async def state(origin):
                manager.active_origin = None
                return "warm"

            async def control(standby_id, action):
                actions.append((standby_id, action))
                return True

            manager.standby_gateway_state = state
            manager.control = control
            await asyncio.wait_for(manager._supervision_loop(), timeout=10)
            self.assertEqual([("standby-east", "activate")], actions)

        asyncio.run(scenario())

    def test_primary_leaves_an_active_standby_alone(self):
        async def scenario():
            manager = StandbyFailoverManager()
            manager.set_standbys(["https://east.example"], ["standby-east"])
            manager.active_origin = "https://east.example"
            manager._supervision_interval = 0
            control = AsyncMock(return_value=True)

            async def state(origin):
                manager.active_origin = None
                return "active"

            manager.standby_gateway_state = state
            manager.control = control
            await asyncio.wait_for(manager._supervision_loop(), timeout=10)
            control.assert_not_awaited()

        asyncio.run(scenario())

    def test_primary_takes_the_gateway_back_when_the_standby_never_returns(self):
        class Handoff:
            def __init__(self):
                self.activated = 0
                self.refresh_caches_on_ready = False

            async def activate(self):
                self.activated += 1

        async def scenario():
            manager = StandbyFailoverManager()
            manager.set_standbys(["https://east.example"], ["standby-east"])
            manager.active_origin = "https://east.example"
            manager._supervision_interval = 0
            manager._reclaim_grace_ticks = 2
            handoff = Handoff()
            manager.bot = SimpleNamespace(gateway_handoff=handoff)
            manager.standby_gateway_state = AsyncMock(return_value="unreachable")
            manager.control = AsyncMock(return_value=False)

            await asyncio.wait_for(manager._supervision_loop(), timeout=10)

            self.assertIsNone(manager.active_origin)
            self.assertEqual(1, handoff.activated)
            self.assertTrue(handoff.refresh_caches_on_ready)
            manager.control.assert_awaited_once_with("standby-east", "relinquish")

        asyncio.run(scenario())

    def test_primary_stands_down_standbys_before_it_connects_itself(self):
        async def scenario():
            manager = StandbyFailoverManager()
            manager.set_standbys(
                ["https://east.example", "https://west.example"], ["standby-east", "standby-west"]
            )
            manager.control = AsyncMock(return_value=True)
            self.assertEqual(2, await manager.stand_down_standbys())
            self.assertEqual(
                [
                    (("standby-east", "relinquish"), {}),
                    (("standby-west", "relinquish"), {}),
                ],
                manager.control.await_args_list,
            )

        asyncio.run(scenario())

    def test_standby_supervision_starts_with_the_failover_supervisor(self):
        async def scenario():
            manager = StandbyFailoverManager()
            manager.active_origin = "https://east.example"
            manager._ensure_recovery_task()
            for task in (manager._recovery_task, manager._supervision_task):
                self.assertIsNotNone(task)
                self.assertFalse(task.done())
            for task in (manager._recovery_task, manager._supervision_task):
                task.cancel()
            await asyncio.gather(manager._recovery_task, manager._supervision_task, return_exceptions=True)

        asyncio.run(scenario())


if __name__ == "__main__":
    unittest.main()
