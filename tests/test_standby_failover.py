import asyncio
import base64
import json
import time
import unittest
from unittest.mock import AsyncMock, patch

from utils.proxy_manager import WebshareProxyManager
from utils.standby_failover import _handle_client, _is_allowed_discord_api_url, control_proof, relay_proof, secret_key, verification_proof
from utils.standby_manager import StandbyFailoverManager
from webapp.standby_routes import _verification_matches


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

    def test_relay_url_allowlist_includes_oauth_and_rejects_untrusted_targets(self):
        self.assertTrue(_is_allowed_discord_api_url("https://discord.com/api/v10/users/@me"))
        self.assertTrue(_is_allowed_discord_api_url("https://discord.com/api/oauth2/token"))
        self.assertTrue(_is_allowed_discord_api_url("https://discord.com/api/oauth2/token?source=callback"))
        self.assertFalse(_is_allowed_discord_api_url("http://discord.com/api/oauth2/token"))
        self.assertFalse(_is_allowed_discord_api_url("https://discord.com.evil.example/api/oauth2/token"))
        self.assertFalse(_is_allowed_discord_api_url("https://discord.com:443/api/oauth2/token"))
        self.assertFalse(_is_allowed_discord_api_url("https://discord.com/api/admin"))
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


if __name__ == "__main__":
    unittest.main()
