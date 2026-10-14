import asyncio
import base64
import unittest
from unittest.mock import patch

from utils.backup_proxy import (
    _allowed_host,
    _handle_client,
    backup_proxy_url,
    control_proof,
    proxy_password,
    secret_key,
    verification_proof,
)
from utils.proxy_manager import WebshareProxyManager
from webapp.backup_routes import _verification_matches


class FakeResponse:
    def __init__(self, status_code, headers, text):
        self.status_code = status_code
        self.status = status_code
        self.headers = headers
        self.text = text
        self.closed = False

    def close(self):
        self.closed = True

    async def release(self):
        self.closed = True


class FakeAiohttpResponse:
    def __init__(self, status, headers, body):
        self.status = status
        self.headers = headers
        self.body = body
        self.closed = False

    async def text(self):
        return self.body

    def release(self):
        self.closed = True


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

    def write_eof(self):
        return None


class BackupProxyTests(unittest.TestCase):
    def test_challenge_matches_only_when_both_secrets_match(self):
        key = secret_key("prod-token", "prod-session")
        nonce = "fresh-random-nonce-value-long-enough"
        expected = verification_proof(key, nonce)
        self.assertEqual(expected, verification_proof(secret_key("prod-token", "prod-session"), nonce))
        self.assertNotEqual(expected, verification_proof(secret_key("other-token", "prod-session"), nonce))
        self.assertNotEqual(expected, verification_proof(secret_key("prod-token", "other-session"), nonce))

    def test_registration_requires_exact_proof_from_both_production_secrets(self):
        nonce = "unique-registration-challenge-nonce"
        production_key = secret_key("production-token", "production-session")
        valid_proof = verification_proof(production_key, nonce)

        self.assertTrue(_verification_matches(production_key, nonce, valid_proof))
        self.assertFalse(
            _verification_matches(
                secret_key("different-token", "production-session"), nonce, valid_proof
            )
        )
        self.assertFalse(
            _verification_matches(
                secret_key("production-token", "different-session"), nonce, valid_proof
            )
        )
        self.assertFalse(_verification_matches(production_key, nonce, None))
        self.assertFalse(_verification_matches(production_key, nonce, ""))

    def test_health_endpoint_is_available_through_http_ingress(self):
        async def scenario():
            key = secret_key("token", "session")
            reader = asyncio.StreamReader()
            reader.feed_data(b"GET /health HTTP/1.1\r\nHost: standby.example\r\n\r\n")
            reader.feed_eof()
            writer = FakeWriter()
            await _handle_client(reader, writer, key)
            self.assertIn(b"200 OK", writer.data)
            self.assertIn(b'"service":"niko-backup-proxy"', writer.data)

        asyncio.run(scenario())

    def test_shared_listener_dispatches_web_api_and_preserves_proxy_handlers(self):
        from flask import Flask, jsonify

        web_app = Flask(__name__)

        @web_app.get("/api/test")
        def api_test():
            return jsonify({"served_by": "flask"})

        async def scenario():
            key = secret_key("token", "session")
            request = b"GET /api/test HTTP/1.1\r\nHost: standby.example\r\n\r\n"
            reader = asyncio.StreamReader()
            reader.feed_data(request)
            reader.feed_eof()
            writer = FakeWriter()
            await _handle_client(reader, writer, key, web_app=web_app)
            self.assertIn(b"HTTP/1.1 200 OK", writer.data)
            self.assertIn(b'"served_by":"flask"', writer.data)

        asyncio.run(scenario())

    def test_render_mode_starts_without_certificate_files(self):
        from utils.backup_proxy import serve_backup_proxy

        async def scenario():
            server = await serve_backup_proxy("127.0.0.1", 0, None, None, "token", "session")
            self.assertIsNotNone(server.sockets)
            server.close()
            await server.wait_closed()

        asyncio.run(scenario())

    def test_authenticated_control_endpoint_activates_standby_once(self):
        from utils import backup_proxy

        class Controller:
            def __init__(self):
                self.actions = []

            async def activate(self):
                self.actions.append("activate")

            async def relinquish(self):
                self.actions.append("relinquish")

        async def request(key, action, nonce, proof):
            body = __import__("json").dumps({"action": action, "nonce": nonce, "proof": proof}).encode()
            crlf = bytes((13, 10))
            raw = b"POST /internal/backup/control HTTP/1.1" + crlf + b"Content-Length: " + str(len(body)).encode() + crlf + crlf + body
            reader = asyncio.StreamReader()
            reader.feed_data(raw)
            reader.feed_eof()
            writer = FakeWriter()
            await _handle_client(reader, writer, key)
            return writer.data

        async def scenario():
            key = secret_key("token", "session")
            controller = Controller()
            backup_proxy._GATEWAY_CONTROLLER = controller
            backup_proxy._CONTROL_NONCES.clear()
            nonce = "gateway-handoff-test-nonce-00000001"
            proof = control_proof(key, "activate", nonce)
            response = await request(key, "activate", nonce, proof)
            self.assertIn(b"200 OK", response)
            self.assertEqual(["activate"], controller.actions)
            replay = await request(key, "activate", nonce, proof)
            self.assertIn(b"403", replay)
            self.assertEqual(["activate"], controller.actions)
            invalid = await request(key, "relinquish", "gateway-handoff-test-nonce-00000002", proof)
            self.assertIn(b"403", invalid)
            backup_proxy._GATEWAY_CONTROLLER = None
            backup_proxy._CONTROL_NONCES.clear()

        asyncio.run(scenario())

    def test_gateway_handoff_disconnects_shards_without_closing_client(self):
        from utils.gateway_failover import GatewayHandoff

        class Shard:
            def __init__(self):
                self.closed = False

            async def close(self):
                self.closed = True

        class Bot:
            def __init__(self):
                self._AutoShardedClient__shards = {0: Shard()}

            async def connect(self, reconnect=True):
                await asyncio.Event().wait()

        async def scenario():
            bot = Bot()
            handoff = GatewayHandoff(bot, active=True)
            supervisor = asyncio.create_task(handoff.run())
            await asyncio.sleep(0)
            shard = bot._AutoShardedClient__shards[0]
            await handoff.relinquish()
            self.assertTrue(shard.closed)
            self.assertFalse(bot._AutoShardedClient__shards)
            self.assertFalse(handoff.active.is_set())
            self.assertFalse(handoff.stopping)
            handoff.stopping = True
            supervisor.cancel()
            await asyncio.gather(supervisor, return_exceptions=True)

        asyncio.run(scenario())

    def test_primary_reclaims_only_after_standby_relinquishes(self):
        from types import SimpleNamespace
        from utils.gateway_failover import GatewayHandoff

        async def scenario():
            events = []

            class Bot:
                _AutoShardedClient__shards = {}

                async def connect(self, reconnect=True):
                    events.append("primary-connect")
                    handoff.mark_connected()

            async def control(backup_id, action):
                events.append(f"standby-{action}")
                return True

            bot = Bot()
            handoff = GatewayHandoff(bot)
            bot.gateway_handoff = handoff
            manager = WebshareProxyManager(None)
            manager.http = type("Http", (), {"proxy": "https://backup.example", "proxy_auth": None})()
            manager._backup_proxy_urls = ["https://niko-backup:pass@backup.example.org"]
            manager._backup_proxy_ids = ["standby-1"]
            manager._proxy_url = manager._backup_proxy_urls[0]
            manager.enabled = True
            manager._bot = bot
            manager._probe_direct = lambda: asyncio.sleep(0, result=True)
            manager.control_backup = control
            manager._verify_interval = 0
            handoff.active.clear()
            supervisor = asyncio.create_task(handoff.run())
            await manager._verify_loop()
            await asyncio.sleep(0)
            self.assertEqual(["standby-relinquish", "primary-connect"], events)
            self.assertTrue(handoff.connected.is_set())
            self.assertFalse(manager.enabled)
            handoff.stopping = True
            supervisor.cancel()
            await asyncio.gather(supervisor, return_exceptions=True)

        asyncio.run(scenario())

    def test_economy_cache_refresh_discards_stale_entries(self):
        from events.startup.economy import preload_economy_cache

        class Cog:
            def __init__(self):
                self.economy_data = {"stale": {"balance": 100}}
                self.primed = False

            async def prime_cache(self):
                self.primed = True
                self.economy_data["fresh"] = {"balance": 50}

        async def scenario():
            cog = Cog()
            await preload_economy_cache(type("Bot", (), {"get_cog": lambda self, name: cog})())
            self.assertTrue(cog.primed)
            self.assertNotIn("stale", cog.economy_data)
            self.assertIn("fresh", cog.economy_data)

        asyncio.run(scenario())

    def test_proxy_url_requires_https_origin(self):
        self.assertTrue(backup_proxy_url("https://backup.example.org", secret_key("a", "b")).startswith("https://niko-backup:"))
        with self.assertRaises(ValueError):
            backup_proxy_url("http://backup.example.org", secret_key("a", "b"))
        with self.assertRaises(ValueError):
            backup_proxy_url("https://backup.example.org/path", secret_key("a", "b"))

    def test_connect_is_allowlisted_to_discord_tls(self):
        self.assertEqual(("discord.com", 443), _allowed_host("discord.com:443"))
        self.assertEqual(("gateway.discord.gg", 443), _allowed_host("gateway.discord.gg:443"))
        self.assertIsNone(_allowed_host("example.org:443"))
        self.assertIsNone(_allowed_host("discord.com:80"))
        self.assertIsNone(_allowed_host("127.0.0.1:443"))

    def test_verify_challenge_returns_proof_but_not_credentials(self):
        async def scenario():
            key = secret_key("token-secret", "session-secret")
            nonce = "N" * 40
            body = (f'{{"nonce":"{nonce}"}}').encode()
            request = (b"POST /internal/backup/verify HTTP/1.1\r\nContent-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body)
            reader = asyncio.StreamReader()
            reader.feed_data(request)
            reader.feed_eof()
            writer = FakeWriter()
            await _handle_client(reader, writer, key)
            response = writer.data.decode()
            self.assertIn(verification_proof(key, nonce), response)
            self.assertNotIn("token-secret", response)
            self.assertNotIn("session-secret", response)
        asyncio.run(scenario())

    def test_authenticated_proxy_disallows_non_discord_connect_targets(self):
        async def scenario():
            key = secret_key("token", "session")
            auth = base64.b64encode(f"niko-backup:{proxy_password(key)}".encode())
            request = b"CONNECT example.org:443 HTTP/1.1\r\nProxy-Authorization: Basic " + auth + b"\r\n\r\n"
            reader = asyncio.StreamReader()
            reader.feed_data(request)
            reader.feed_eof()
            writer = FakeWriter()
            await _handle_client(reader, writer, key)
            self.assertIn(b"403", writer.data)
        asyncio.run(scenario())

    def test_cloudflare_denial_is_detected_only_with_explicit_edge_signature(self):
        manager = WebshareProxyManager(None)
        blocked = FakeResponse(403, {"Server": "cloudflare", "CF-Ray": "test-ray"}, "Attention Required! Cloudflare")
        generic_edge_429 = FakeResponse(429, {"CF-Ray": "test-ray"}, "<!doctype html>")
        ordinary_forbidden = FakeResponse(403, {"Server": "gunicorn"}, "Forbidden")
        ordinary_rate_limit = FakeResponse(429, {"Server": "discord"}, "Too Many Requests")
        self.assertTrue(manager.is_cloudflare_block(blocked))
        self.assertTrue(manager.is_cloudflare_block(generic_edge_429))
        self.assertFalse(manager.is_cloudflare_block(ordinary_forbidden))
        self.assertFalse(manager.is_cloudflare_block(ordinary_rate_limit))

    def test_requests_style_probe_detects_cloudflare_html_429_without_status_alias(self):
        async def scenario():
            manager = WebshareProxyManager(None)
            manager.http = type("Http", (), {"proxy": None, "proxy_auth": None})()
            manager.set_backup_proxies(["https://niko-backup:pass@backup.example.org"])
            response = type("RequestsResponse", (), {
                "status_code": 429,
                "headers": {},
                "text": "<!doctype html><div id=\"cf-error-details\">Cloudflare Ray ID: test-ray</div>",
            })()
            with patch("utils.proxy_manager.requests.get", return_value=response), patch.object(manager, "_probe_backup", return_value={"service": "niko-backup-proxy"}), patch.object(manager, "_ensure_verify_task"):
                self.assertTrue(await manager.check_direct_egress())
            self.assertTrue(manager.enabled)
            self.assertEqual(manager._backup_proxy_urls[0], manager.http.proxy)

        asyncio.run(scenario())

    def test_gateway_login_retry_detaches_failed_session_connector(self):
        async def scenario():
            manager = WebshareProxyManager(None)
            manager.set_backup_proxies(["https://niko-backup:pass@backup.example.org"])
            http = type("Http", (), {
                "_HTTPClient__session": None,
                "proxy": None,
                "proxy_auth": None,
                "user_agent": "test-agent",
                "connector": object(),
            })()
            manager.http = http
            manager._current_session = lambda: getattr(http, "_HTTPClient__session", None)
            bot = type("Bot", (), {"http": http})()
            challenge_body = "<!doctype html><div id=\"cf-error-details\"><span>Cloudflare Ray ID: test-ray</span></div>"
            original_error = type("HttpError", (Exception,), {})("429 Too Many Requests")
            original_error.response = FakeAiohttpResponse(429, {}, challenge_body)
            original_error.text = challenge_body
            sessions = []

            class Session:
                def __init__(self, connector):
                    self.connector = connector
                    self.closed = False
                    self.detached = False
                    self._request = lambda *args, **kwargs: None

                def detach(self):
                    self.detached = True
                    self.connector = None

                async def close(self):
                    self.closed = True

            async def static_login(token):
                session = Session(http.connector)
                http._HTTPClient__session = session
                sessions.append(session)
                if len(sessions) == 1:
                    raise original_error
                if sessions[1].connector is None:
                    raise RuntimeError("Session is closed")
                return {"id": "bot-user"}

            http.static_login = static_login
            with patch.object(manager, "_probe_backup", return_value={"service": "niko-backup-proxy"}), patch.object(manager, "_ensure_verify_task"):
                manager.attach(bot)
                result = await http.static_login("secret-token")

            self.assertEqual({"id": "bot-user"}, result)
            self.assertTrue(sessions[0].detached)
            self.assertTrue(sessions[0].closed)
            self.assertIs(http.connector, sessions[1].connector)

        asyncio.run(scenario())

    def test_gateway_login_retries_cloudflare_html_429_through_standby(self):
        async def scenario():
            manager = WebshareProxyManager(None)
            manager.set_backup_proxies(["https://niko-backup:pass@backup.example.org"])
            failed_response = FakeAiohttpResponse(429, {}, "")
            session = None
            close_calls = []
            detach_calls = []

            def detach_session():
                session.detached = True
                detach_calls.append(True)

            async def close_session():
                session.closed = True
                close_calls.append(True)

            http = type("Http", (), {
                "_HTTPClient__session": None,
                "proxy": None,
                "proxy_auth": None,
                "user_agent": "test-agent",
            })()
            manager.http = http
            manager._current_session = lambda: getattr(http, "_HTTPClient__session", None)
            bot = type("Bot", (), {"http": http})()
            challenge_body = "<!doctype html><div id=\"cf-error-details\"><span>Cloudflare Ray ID: test-ray</span><div class=\"cf-wrapper\"></div></div>"
            original_error = type("HttpError", (Exception,), {})(
                f"429 Too Many Requests (error code: 0): {challenge_body}"
            )
            original_error.response = failed_response
            original_error.text = challenge_body
            attempts = []

            async def static_login(token):
                nonlocal session
                session = type("Session", (), {"_request": None, "closed": False, "detached": False})()
                session.detach = detach_session
                session.close = close_session
                http._HTTPClient__session = session
                attempts.append((token, http.proxy))
                if len(attempts) == 1:
                    raise original_error
                return {"id": "bot-user"}

            http.static_login = static_login
            with patch.object(manager, "_probe_backup", return_value={"service": "niko-backup-proxy"}), patch.object(manager, "_ensure_verify_task"):
                self.assertTrue(manager.attach(bot))
                result = await http.static_login("secret-token")

            self.assertEqual({"id": "bot-user"}, result)
            self.assertEqual(2, len(attempts))
            self.assertIsNone(attempts[0][1])
            self.assertEqual(manager._backup_proxy_urls[0], attempts[1][1])
            self.assertEqual([True], close_calls)
            self.assertEqual([True], detach_calls)
            self.assertTrue(manager.enabled)

        asyncio.run(scenario())

    def test_web_discord_api_retries_cloudflare_block_through_standby(self):
        from webapp import server

        manager = WebshareProxyManager(None)
        manager.http = type("Http", (), {"proxy": None, "proxy_auth": None})()
        manager.set_backup_proxies(["https://niko-backup:pass@backup.example.org"])
        bot = type("Bot", (), {"proxy_manager": manager})()
        responses = [
            FakeResponse(403, {"Server": "cloudflare", "CF-Ray": "test-ray"}, "Cloudflare access denied"),
            FakeResponse(200, {}, "ok"),
        ]
        calls = []

        def fake_get(url, **kwargs):
            calls.append((url, kwargs))
            return responses.pop(0)

        with patch.object(server, "_discord_bot", bot), patch.object(server.req, "get", side_effect=fake_get):
            response = server.discord_request("GET", "https://discord.com/api/v10/users/@me")

        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(calls))
        self.assertIn("proxies", calls[1][1])
        self.assertEqual(manager._proxy_url, calls[1][1]["proxies"]["https"])

    def test_manager_selects_healthy_standby_before_webshare(self):
        async def scenario():
            manager = WebshareProxyManager("api-key")
            manager.http = type("Http", (), {"proxy": None, "proxy_auth": None})()
            manager.set_backup_proxies(["https://niko-backup:pass@backup.example.org"], ["standby-1"])
            with patch.object(manager, "_probe_backup", return_value=True), patch.object(manager, "_ensure_verify_task"), patch.object(manager, "_fetch_proxies") as fetch:
                await manager.enable()
            self.assertEqual("https://niko-backup:pass@backup.example.org", manager.http.proxy)
            self.assertEqual("standby-1", manager.status()["active_backup_id"])
            fetch.assert_not_called()
        asyncio.run(scenario())

    def test_manager_uses_webshare_when_no_standby_is_healthy(self):
        async def scenario():
            manager = WebshareProxyManager("api-key")
            manager.http = type("Http", (), {"proxy": None, "proxy_auth": None})()
            manager.set_backup_proxies(["https://niko-backup:pass@backup.example.org"], ["standby-1"])
            proxy = {"username": "u", "password": "p", "proxy_address": "proxy.example", "port": 80}
            with patch.object(manager, "_probe_backup", return_value=None), patch.object(manager, "_cached_proxies", return_value=[proxy]), patch.object(manager, "_ensure_verify_task"):
                await manager.enable()
            self.assertTrue(manager.enabled)
            self.assertTrue(manager.status()["using_webshare"])
            self.assertEqual("auto", manager.status()["mode"])
            self.assertEqual(1, manager.status()["webshare_fallback_count"])
        asyncio.run(scenario())

    def test_manual_backup_activation_requires_healthy_registered_id(self):
        async def scenario():
            manager = WebshareProxyManager(None)
            manager.http = type("Http", (), {"proxy": None, "proxy_auth": None})()
            manager.set_backup_proxies(["https://niko-backup:pass@backup.example.org"], ["standby-1"])
            with patch.object(manager, "_probe_backup", return_value={"service": "niko-backup-proxy"}), patch.object(manager, "_ensure_verify_task"):
                self.assertTrue(await manager.activate_backup_async("standby-1"))
                self.assertFalse(await manager.activate_backup_async("unknown"))
            self.assertEqual("standby-1", manager.status()["active_backup_id"])
        asyncio.run(scenario())

    def test_backup_health_exposes_counters_but_not_proxy_credentials(self):
        async def scenario():
            from utils import backup_proxy
            backup_proxy._STATS.update({"total_tunnels": 7, "active_tunnels": 2, "bytes_in": 1024, "bytes_out": 2048})
            reader = asyncio.StreamReader()
            reader.feed_data(b"GET /health HTTP/1.1\r\nHost: standby.example\r\n\r\n")
            reader.feed_eof()
            writer = FakeWriter()
            await _handle_client(reader, writer, secret_key("token", "session"))
            response = writer.data.decode()
            self.assertIn('"total_tunnels":7', response)
            self.assertIn('"bytes_in":1024', response)
            self.assertNotIn("niko-backup:", response)
        asyncio.run(scenario())

    def test_manual_backup_route_can_override_direct_off_mode(self):
        manager = WebshareProxyManager(None)
        manager.http = type("Http", (), {"proxy": None, "proxy_auth": None})()
        manager.set_backup_proxies(["https://niko-backup:pass@backup.example.org"], ["standby-1"])
        manager._backup_mode = "off"
        with patch.object(manager, "_ensure_verify_task"):
            self.assertTrue(manager.activate_backup("standby-1"))
        self.assertEqual("standby-1", manager.status()["active_backup_id"])
        self.assertEqual("standby", manager.status()["mode"])

    def test_force_backup_respects_direct_off_mode(self):
        async def scenario():
            manager = WebshareProxyManager("api-key")
            manager.http = type("Http", (), {"proxy": None, "proxy_auth": None})()
            manager._backup_mode = "off"
            with patch.object(manager, "_probe_backup") as probe, patch.object(manager, "_fetch_proxies") as fetch:
                await manager.enable(force_backup=True)
            probe.assert_not_called()
            fetch.assert_not_called()
            self.assertFalse(manager.enabled)

        asyncio.run(scenario())

    def test_manual_backup_can_activate_when_direct_off_mode(self):
        async def scenario():
            manager = WebshareProxyManager(None)
            manager.http = type("Http", (), {"proxy": None, "proxy_auth": None})()
            manager.set_backup_proxies(["https://niko-backup:pass@backup.example.org"], ["standby-1"])
            manager._backup_mode = "off"
            with patch.object(manager, "_probe_backup", return_value={"service": "niko-backup-proxy"}), patch.object(manager, "_ensure_verify_task"):
                self.assertTrue(await manager.activate_backup_async("standby-1"))
            self.assertTrue(manager.enabled)
            self.assertEqual("standby-1", manager.status()["active_backup_id"])

        asyncio.run(scenario())

    def test_manager_falls_back_to_registered_standby(self):
        async def scenario():
            manager = WebshareProxyManager(None)
            manager.http = type("Http", (), {"proxy": None, "proxy_auth": None})()
            manager.set_backup_proxies(["https://niko-backup:pass@backup.example.org"], ["standby-1"])
            with patch.object(manager, "_probe_backup", return_value=True), patch.object(manager, "_ensure_verify_task"):
                await manager.enable()
            self.assertEqual("https://niko-backup:pass@backup.example.org", manager.http.proxy)
            self.assertTrue(manager.enabled)
            await manager.enable(force_backup=True)
            self.assertEqual("https://niko-backup:pass@backup.example.org", manager.http.proxy)
            manager.disable()
            self.assertIsNone(manager.http.proxy)
        asyncio.run(scenario())


if __name__ == "__main__":
    unittest.main()
