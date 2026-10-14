import asyncio
import base64
import json
import os
import time
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import requests

from utils.proxy_manager import WebshareProxyManager
from utils.standby_failover import _dispatch_web_request, _handle_client, _is_allowed_discord_api_url, control_proof, is_discord_relay_url, relay_proof, secret_key, verification_proof
from utils.standby_manager import StandbyFailoverManager
from webapp import app
from webapp import server as server_routes
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
                return Response(429, {"CF-Ray": "cloudflare-ray"}, "Cloudflare error 1015")

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
                return Response(429, {"CF-Ray": "cloudflare-ray"}, "Cloudflare error 1015")

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

            with patch("utils.standby_manager.requests.get", return_value=healthy):
                self.assertFalse(await manager.check_direct_egress())
            self.assertFalse(manager.egress_blocked)

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
                return Response(429, {"CF-Ray": "cloudflare-ray"}, "Cloudflare error 1015")

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

            self.assertEqual(429, response.status)
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

    def test_standby_instance_cannot_rearm_automatic_failover(self):
        from config.ids import OWNER_IDS
        from webapp import standby_routes as routes

        bot = SimpleNamespace(standby_failover=StandbyFailoverManager())
        client = app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": str(next(iter(OWNER_IDS)))}
            session["access_token"] = "test-token"
            session["token_exp"] = time.time() + 3600
            session["csrf_token"] = "test-csrf"

        def control(payload, standby_mode):
            # select_failover is synchronous, so mode changes must not be sent to
            # the bot-loop coroutine runner (that raised and answered 503).
            with patch.dict(os.environ, {"STANDBY_MODE": standby_mode}), patch.object(
                server_routes, "_current_user_blacklist_entry", return_value=None
            ), patch.object(routes, "_current_staff_role", return_value="owner"), patch.object(
                routes, "_discord_bot", bot
            ), patch.object(routes, "run_on_bot_loop") as runner:
                response = client.post(
                    "/api/staff/standbys/failover",
                    json=payload,
                    headers={"X-CSRF-Token": "test-csrf"},
                )
            runner.assert_not_called()
            return response

        refused = control({"action": "mode", "mode": "auto"}, "true")
        self.assertEqual(403, refused.status_code)
        self.assertIn("never initiates failover", refused.get_json()["error"])
        self.assertEqual(200, control({"action": "mode", "mode": "off"}, "true").status_code)
        self.assertEqual(200, control({"action": "mode", "mode": "auto"}, "").status_code)


if __name__ == "__main__":
    unittest.main()
