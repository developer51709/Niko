import asyncio
import base64
import json
import pathlib
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from cogs.admin import customization
from utils import discord_proxy
from utils.discord_proxy import DiscordProxyManager, _RelayedAiohttpResponse, is_discord_api_url
from utils.proxy_manager import WebshareProxyManager
from webapp import server as server_routes
from utils.proxy_worker_registry import (
    add_proxy_worker,
    init_proxy_worker_registry,
    list_proxy_workers,
    proxy_routing_enabled,
    remove_proxy_worker,
    set_proxy_routing_enabled,
)


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows

    def sort(self, field, direction):
        self.rows.sort(key=lambda row: row[field], reverse=direction < 0)
        return self

    async def to_list(self, length=None):
        return list(self.rows)


class DuplicateKeyError(Exception):
    code = 11000


class FakeCollection:
    def __init__(self):
        self.documents = {}
        self.created_indexes = []

    async def create_index(self, field, unique=False, name=None):
        self.created_indexes.append((field, unique, name))
        return name

    def find(self, query, projection):
        return FakeCursor([
            {key: value for key, value in item.items() if projection.get(key)}
            for item in self.documents.values()
        ])

    async def insert_one(self, document):
        if any(item["url"].casefold() == document["url"].casefold() for item in self.documents.values()):
            raise DuplicateKeyError("duplicate URL")
        self.documents[document["_id"]] = dict(document)

    async def delete_one(self, query):
        deleted = self.documents.pop(query["_id"], None)
        return SimpleNamespace(deleted_count=1 if deleted else 0)

    async def update_one(self, query, update, upsert=False):
        document = self.documents.setdefault(query["_id"], {"_id": query["_id"]})
        document.update(update.get("$set", {}))
        return SimpleNamespace(modified_count=1, upserted_id=None)

    async def find_one(self, query, projection=None):
        document = self.documents.get(query["_id"])
        if document is None:
            return None
        if projection:
            return {key: value for key, value in document.items() if projection.get(key)}
        return dict(document)


class FakePool:
    db_type = "mongodb"

    def __init__(self, collections=None):
        self._collections = collections or {}

    def collection(self, name):
        return self._collections.setdefault(name, FakeCollection())


class FakeRelayResponse:
    def __init__(self, payload, status=200):
        self.status = status
        self._payload = payload
        self._text = json.dumps(payload)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return None

    async def json(self):
        return self._payload

    async def text(self):
        return self._text


class FakeResponse:
    def __init__(self, status=200, content=b"{}", headers=None):
        self.status = status
        self.status_code = status
        self._content = content
        self.content = content
        self.headers = dict(headers or {})
        self.text = content.decode("utf-8", "replace")
        self.ok = 200 <= status < 400

    def json(self):
        return json.loads(self.text or "{}")

    def close(self):
        return None


class FakeProxyWorkers:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def can_relay(self, url):
        return True

    def request_via_worker(self, method, url, kwargs):
        self.calls.append((method, url, kwargs))
        if self.error:
            raise self.error
        return self.response


class FakeFailover:
    def cloudflare_interstitial(self, response):
        return None


class ProxyWorkerRegistryTests(unittest.TestCase):
    def test_registry_refuses_ephemeral_sqlite_storage(self):
        bot = SimpleNamespace(cxn=SimpleNamespace(db_type="sqlite"))
        with self.assertRaisesRegex(RuntimeError, "requires the shared MongoDB database"):
            asyncio.run(list_proxy_workers(bot))

    def test_registry_persists_workers_and_routing_switch(self):
        collection = FakeCollection()
        settings = FakeCollection()
        pool = FakePool({"proxy_workers": collection, "proxy_worker_settings": settings})
        bot = SimpleNamespace(cxn=pool)
        restarted = SimpleNamespace(cxn=pool)
        item = {"id": "worker-1", "name": "EU edge", "url": "https://proxy.example", "created_at": 10}

        async def scenario():
            await init_proxy_worker_registry(bot)
            self.assertEqual(
                [("url", True, "proxy_workers_url_unique")],
                collection.created_indexes,
            )
            self.assertFalse(await proxy_routing_enabled(bot))
            rows = await add_proxy_worker(bot, item)
            self.assertEqual([item], rows)
            self.assertEqual([item], await list_proxy_workers(restarted))
            with self.assertRaisesRegex(ValueError, "already registered"):
                await add_proxy_worker(bot, {**item, "id": "worker-2"})

            self.assertTrue(await set_proxy_routing_enabled(bot, True))
            self.assertTrue(await proxy_routing_enabled(restarted))
            await remove_proxy_worker(restarted, "worker-1")
            self.assertEqual([], await list_proxy_workers(bot))
            self.assertTrue(await proxy_routing_enabled(bot))

        asyncio.run(scenario())


class DiscordProxyManagerTests(unittest.TestCase):
    def test_only_discord_api_urls_are_eligible(self):
        self.assertTrue(is_discord_api_url("https://discord.com/api/v10/users/@me"))
        self.assertTrue(is_discord_api_url("https://ptb.discord.com/api/v9/gateway"))
        self.assertTrue(is_discord_api_url("https://discordapp.com/api/oauth2/token"))
        self.assertFalse(is_discord_api_url("http://discord.com/api/v10/users/@me"))
        self.assertFalse(is_discord_api_url("https://cdn.discordapp.com/avatars/1/2.png"))
        self.assertFalse(is_discord_api_url("https://discord.com/api.evil.example/users/@me"))
        self.assertFalse(is_discord_api_url("https://user:pass@discord.com/api/v10/users/@me"))
        self.assertFalse(is_discord_api_url("https://discord.com:8443/api/v10/users/@me"))
        self.assertFalse(is_discord_api_url("https://discord.com/api/v10/users/@me#fragment"))

    def test_manager_relays_a_signed_request(self):
        manager = DiscordProxyManager("test-token")
        manager.set_workers([{"id": "worker-1", "name": "EU edge", "url": "https://proxy.example"}], True)
        self.assertTrue(manager.can_relay("https://discord.com/api/v10/users/@me"))
        calls = []

        async def original_request(method, url, **kwargs):
            calls.append((method, url, kwargs))
            return FakeRelayResponse({
                "status": 200,
                "headers": {"content-type": "application/json"},
                "body": base64.b64encode(b'{"id": "1"}').decode(),
            })

        async def scenario():
            response = await manager.relay_aiohttp(
                original_request,
                "GET",
                "https://discord.com/api/v10/users/@me",
                {"headers": {"Authorization": "Bot token"}},
            )
            self.assertEqual(200, response.status)
            self.assertEqual('{"id": "1"}', await response.text())
            self.assertEqual(1, manager.total_requests)
            self.assertEqual("EU edge", manager.last_worker)

        asyncio.run(scenario())
        self.assertEqual(1, len(calls))
        self.assertEqual("POST", calls[0][0])
        self.assertEqual("https://proxy.example/internal/proxy", calls[0][1])
        envelope = calls[0][2]["json"]
        self.assertEqual("GET", envelope["method"])
        self.assertEqual("https://discord.com/api/v10/users/@me", envelope["url"])
        self.assertEqual(32 * 2, len(envelope["nonce"]))
        self.assertTrue(envelope["proof"])

    def test_manager_falls_back_to_the_next_worker(self):
        manager = DiscordProxyManager("test-token")
        manager.set_workers([
            {"id": "worker-1", "name": "Primary edge", "url": "https://primary.example"},
            {"id": "worker-2", "name": "Secondary edge", "url": "https://secondary.example"},
        ], True)
        seen = []

        async def original_request(method, url, **kwargs):
            seen.append(url)
            if "primary.example" in url:
                return FakeRelayResponse({"error": "unavailable"}, status=503)
            return FakeRelayResponse({
                "status": 204,
                "headers": {},
                "body": "",
            })

        async def scenario():
            response = await manager.relay_aiohttp(
                original_request,
                "POST",
                "https://discord.com/api/v10/channels/1/messages",
                {"data": "{}", "headers": {"Content-Type": "application/json"}},
            )
            self.assertEqual(204, response.status)

        asyncio.run(scenario())
        self.assertEqual(
            ["https://primary.example/internal/proxy", "https://secondary.example/internal/proxy"],
            seen,
        )
        self.assertEqual(1, manager.total_failures)
        self.assertEqual(1, manager.total_requests)
        self.assertIn("Primary edge", manager.status()["recent_errors"][0]["message"])

    def test_relayed_error_responses_keep_discords_reason_phrase(self):
        from discord.errors import Forbidden

        response = _RelayedAiohttpResponse(
            403,
            {"content-type": "application/json"},
            b'{"message":"Missing Access","code":50001}',
        )
        error = Forbidden(response, {"message": "Missing Access", "code": 50001})
        self.assertEqual("Forbidden", response.reason)
        self.assertIn("403 Forbidden", str(error))

    def test_disabled_manager_leaves_requests_alone(self):
        manager = DiscordProxyManager("test-token")
        manager.set_workers([{"id": "worker-1", "name": "EU edge", "url": "https://proxy.example"}], False)
        self.assertFalse(manager.can_relay("https://discord.com/api/v10/users/@me"))
        self.assertFalse(manager.enabled)

    def test_standalone_aiohttp_calls_use_the_worker_and_fall_back_direct(self):
        class Session:
            def __init__(self):
                self.direct = []

            async def _request(self, method, url, **kwargs):
                return FakeRelayResponse({
                    "status": 200,
                    "headers": {"content-type": "application/json"},
                    "body": base64.b64encode(b'{"ok":true}').decode(),
                })

            async def request(self, method, url, **kwargs):
                self.direct.append((method, url))
                return SimpleNamespace(status=200, text=lambda: "{}")

        manager = DiscordProxyManager("test-token")
        manager.set_workers([{"id": "worker-1", "name": "EU edge", "url": "https://proxy.example"}], True)
        session = Session()

        async def scenario():
            response = await manager.relay_or_request(
                session, "PATCH", "https://discord.com/api/v10/users/@me", data='{"bio":"hi"}'
            )
            self.assertEqual(200, response.status)
            self.assertEqual([], session.direct)

            manager.set_workers([], True)
            direct = await manager.relay_or_request(
                session, "PATCH", "https://discord.com/api/v10/users/@me", data='{"bio":"hi"}'
            )
            self.assertEqual(200, direct.status)
            self.assertEqual([("PATCH", "https://discord.com/api/v10/users/@me")], session.direct)

        asyncio.run(scenario())


class CustomizationProxyTests(unittest.TestCase):
    class _Response:
        status = 200

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return None

        async def text(self):
            return "{}"

    class _Session:
        def __init__(self, owner):
            self.owner = owner

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return None

        def patch(self, *args, **kwargs):
            raise AssertionError("the proxy manager should have handled this request")

        def request(self, *args, **kwargs):
            raise AssertionError("the proxy manager should have handled this request")

    def test_profile_updates_use_the_worker_when_routing_is_enabled(self):
        class Manager:
            def __init__(self):
                self.calls = []

            async def relay_or_request(self, session, method, url, **kwargs):
                self.calls.append((method, url, kwargs))
                return CustomizationProxyTests._Response()

        manager = Manager()
        with patch.object(customization.aiohttp, "ClientSession", return_value=self._Session(self)):
            success, attempts = asyncio.run(customization.try_patch_with_fallbacks(
                ["https://discord.com/api/v10/users/@me"],
                "token",
                {"bio": "hello"},
                proxy_manager=manager,
            ))

        self.assertTrue(success)
        self.assertEqual(200, attempts[0]["status_code"])
        self.assertEqual("PATCH", manager.calls[0][0])
        self.assertEqual("https://discord.com/api/v10/users/@me", manager.calls[0][1])


class DiscordProxyDashboardIntegrationTests(unittest.TestCase):
    def test_dashboard_discord_request_prefers_a_worker(self):
        proxied = FakeResponse(content=b'{"id":"1"}', headers={"Content-Type": "application/json"})
        proxy = FakeProxyWorkers(response=proxied)
        bot = SimpleNamespace(http=None, standby_failover=FakeFailover(), discord_proxy=proxy)

        with patch.object(server_routes, "_discord_bot", bot), patch.object(server_routes.req, "get") as direct:
            response = server_routes.discord_request("GET", "https://discord.com/api/v10/users/@me")

        self.assertIs(proxied, response)
        direct.assert_not_called()
        self.assertEqual("https://discord.com/api/v10/users/@me", proxy.calls[0][1])

    def test_dashboard_discord_request_falls_back_when_no_worker_can_relay(self):
        direct_response = FakeResponse(content=b'{"id":"2"}')
        proxy = FakeProxyWorkers(error=RuntimeError("workers unavailable"))
        bot = SimpleNamespace(http=None, standby_failover=FakeFailover(), discord_proxy=proxy)

        with patch.object(server_routes, "_discord_bot", bot), patch.object(
            server_routes.req, "get", return_value=direct_response
        ) as direct:
            response = server_routes.discord_request("GET", "https://discord.com/api/v10/users/@me")

        self.assertIs(direct_response, response)
        direct.assert_called_once()


class DiscordProxyHookTests(unittest.TestCase):
    def test_attach_wraps_the_login_path_so_a_new_session_is_hooked(self):
        manager = DiscordProxyManager("test-token")
        manager.set_workers([{"id": "worker-1", "name": "EU edge", "url": "https://proxy.example"}], True)
        calls = []

        async def original_request(method, url, **kwargs):
            calls.append((method, url))
            return SimpleNamespace(status=200)

        class Session:
            async def _request(self, method, url, **kwargs):
                return SimpleNamespace(status=200)

        session = Session()
        raw_request = session._request
        http = SimpleNamespace(request=original_request, _HTTPClient__session=None)
        manager.attach(SimpleNamespace(http=http))

        async def scenario():
            http._HTTPClient__session = session
            await http.request("GET", "https://discord.com/api/v10/gateway")

        asyncio.run(scenario())
        self.assertIsNot(raw_request, session._request)
        self.assertEqual([("GET", "https://discord.com/api/v10/gateway")], calls)

    def test_hook_marks_only_worker_answers_and_reports_direct_fallbacks(self):
        manager = DiscordProxyManager("test-token")
        manager.set_workers([{"id": "worker-1", "name": "EU edge", "url": "https://proxy.example"}], True)
        session = SimpleNamespace()
        direct_calls = []

        async def original_request(method, url, **kwargs):
            direct_calls.append(url)
            return SimpleNamespace(status=200)

        async def scenario():
            session._request = original_request
            manager._install_hook(session)
            manager.relay_aiohttp = AsyncMock(return_value=SimpleNamespace(status=200))
            await session._request("GET", "https://discord.com/api/v10/users/@me")
            self.assertTrue(manager.request_was_relayed())
            self.assertEqual([], direct_calls)

            manager.relay_aiohttp = AsyncMock(side_effect=RuntimeError("worker down"))
            await session._request("GET", "https://discord.com/api/v10/users/@me")
            self.assertFalse(manager.request_was_relayed())
            self.assertEqual(["https://discord.com/api/v10/users/@me"], direct_calls)

        asyncio.run(scenario())

    def test_webshare_skips_only_responses_a_worker_actually_relayed(self):
        manager = WebshareProxyManager("webshare-key")
        manager.bot = SimpleNamespace(discord_proxy=SimpleNamespace(request_was_relayed=lambda: True))
        manager.handle_rate_limit = AsyncMock()
        session = SimpleNamespace()

        async def relayed_response(method, url, **kwargs):
            return SimpleNamespace(status=429, headers={})

        async def direct_response(method, url, **kwargs):
            return SimpleNamespace(status=429, headers={})

        async def scenario():
            session._request = relayed_response
            manager._install_hook(session)
            await session._request("GET", "https://discord.com/api/v10/gateway")
            manager.handle_rate_limit.assert_not_awaited()

            manager.bot.discord_proxy = SimpleNamespace(request_was_relayed=lambda: False)
            await session._request("GET", "https://discord.com/api/v10/gateway")
            manager.handle_rate_limit.assert_awaited_once()

        asyncio.run(scenario())


class ProbeTests(unittest.TestCase):
    class _Session:
        trust_env = True

        def __init__(self, owner):
            self.owner = owner

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return None

        def get(self, url, **kwargs):
            self.owner.calls.append((url, kwargs))
            if url.endswith("/stats"):
                return self.owner.stats_response
            return self.owner.health_response

    def test_probe_uses_stats_for_healthy_workers_and_health_as_a_fallback(self):
        manager = DiscordProxyManager("test-token")
        self.calls = []
        self.stats_response = FakeResponse(
            content=json.dumps({"service": "niko-discord-proxy", "totals": {"requests": 2}}).encode()
        )
        session = self._Session(self)
        with patch.object(discord_proxy.requests, "Session", return_value=session):
            stats = manager.probe_worker_sync({"url": "https://proxy.example"})
        self.assertEqual(2, stats["totals"]["requests"])
        self.assertEqual(1, len(self.calls))

        self.calls = []
        self.stats_response = FakeResponse(status=401, content=b'{"error":"Unauthorized"}')
        self.health_response = FakeResponse(
            content=json.dumps({"service": "niko-discord-proxy", "ready": True}).encode()
        )
        session = self._Session(self)
        with patch.object(discord_proxy.requests, "Session", return_value=session):
            health = manager.probe_worker_sync({"url": "https://proxy.example"})
        self.assertTrue(health["ready"])
        self.assertIn("HTTP 401", health["stats_error"])
        self.assertEqual(2, len(self.calls))


class ProxyWorkerSourceTests(unittest.TestCase):
    def test_worker_exposes_health_stats_verification_and_signed_relay(self):
        source = pathlib.Path(__file__).resolve().parents[1].joinpath("proxy-worker", "worker.js").read_text()
        for endpoint in ("/health", "/stats", "/internal/verify", "/internal/proxy"):
            self.assertIn(endpoint, source)
        self.assertIn("niko-proxy-worker-verification:", source)
        self.assertIn("niko-discord-proxy-relay:", source)
        self.assertIn("MAX_BODY_BYTES", source)
        self.assertIn("redactPath", source)
        self.assertIn("Only HTTPS Discord API URLs are allowed", source)


if __name__ == "__main__":
    unittest.main()
