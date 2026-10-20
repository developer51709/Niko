"""The member guild list has to leave over the bot's own egress.

The reported bug: while Webshare failover was active, ``/dashboard/servers``
listed no servers at all. The route read ``/users/@me/guilds`` with a bare
``requests`` client from the Flask thread, so the call left over the
deployment's own IP - the address Discord was already limiting or challenging,
which is exactly why the bot had moved to a proxy. ``api_guilds`` then turned
that failure into ``[]``, and the page rendered an empty server list.

These tests pin the fix: the list is fetched on the bot's event loop through the
bot's REST session, so it inherits the bot's proxy and proxy-worker routing, and
a failed read is reported as an error instead of an empty list.

Run with:  python -m pytest tests/test_member_guilds_egress.py -v
"""

import asyncio
import json
import sys
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from webapp import app, dashboard_routes, server  # noqa: E402

USER_AGENT = "DiscordBot (https://niko.sryze.cc, 2.7.1)"
PROXY = "http://user:pass@p.webshare.io:80"
GUILDS = [{"id": "111", "name": "Owned server", "owner": True, "permissions": "0"}]


class FakeResponse:
    """The slice of an aiohttp response the fetch reads."""

    def __init__(self, status, body):
        self.status = status
        self._body = body

    async def text(self, encoding="utf-8"):
        return self._body

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class FakeSession:
    """Stands in for discord.py's aiohttp session."""

    def __init__(self, responses, on_request=None):
        self.responses = list(responses)
        self.calls = []
        self.threads = []
        self.on_request = on_request

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        self.threads.append(threading.get_ident())
        if self.on_request is not None:
            self.on_request(len(self.calls))
        item = self.responses.pop(0) if len(self.responses) > 1 else self.responses[0]
        if isinstance(item, BaseException):
            raise item
        status, body = item
        return FakeResponse(status, body)


def http_with(session, proxy=None):
    return SimpleNamespace(
        user_agent=USER_AGENT,
        proxy=proxy,
        proxy_auth=None,
        _HTTPClient__session=session,
    )


def run_fetch(session, proxy=None):
    """Run the bot-loop fetch coroutine against a fake session."""
    with mock.patch.object(server, "_discord_bot", SimpleNamespace(http=http_with(session, proxy))):
        return asyncio.run(server._member_guilds_via_bot("user-token"))


def start_loop(testcase):
    """Start a bot-like event loop in its own thread; returns (loop, thread id)."""
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=loop.run_forever, daemon=True)
    thread.start()

    def stop():
        loop.call_soon_threadsafe(loop.stop)
        thread.join(timeout=5)
        loop.close()

    testcase.addCleanup(stop)
    return loop, thread.ident


class BotSessionFetchTests(unittest.TestCase):
    def test_the_list_uses_the_bots_session_and_the_members_token(self):
        session = FakeSession([(200, json.dumps(GUILDS))])
        guilds = run_fetch(session)

        self.assertEqual(GUILDS, guilds)
        url, kwargs = session.calls[0]
        self.assertTrue(url.endswith("/users/@me/guilds"))
        # The member's OAuth token, not the bot token: this lists their servers.
        self.assertEqual("Bearer user-token", kwargs["headers"]["Authorization"])
        self.assertEqual(USER_AGENT, kwargs["headers"]["User-Agent"])

    def test_the_bots_proxy_carries_the_request(self):
        session = FakeSession([(200, json.dumps(GUILDS))])
        run_fetch(session, proxy=PROXY)

        self.assertEqual(PROXY, session.calls[0][1]["proxy"])

    def test_no_proxy_is_forced_when_the_bot_egresses_directly(self):
        session = FakeSession([(200, json.dumps(GUILDS))])
        run_fetch(session, proxy=None)

        self.assertNotIn("proxy", session.calls[0][1])

    def test_a_refused_request_retries_over_the_proxy_the_hook_armed(self):
        http = http_with(FakeSession([(403, "Attention Required!"), (200, json.dumps(GUILDS))]))

        def arm_proxy(attempt):
            # The rate-limit hook arms Webshare while handling the block; the
            # retry has to read the new egress instead of reusing the old IP.
            if attempt == 1:
                http.proxy = PROXY

        http._HTTPClient__session.on_request = arm_proxy
        with mock.patch.object(server, "_discord_bot", SimpleNamespace(http=http)):
            self.assertEqual(GUILDS, asyncio.run(server._member_guilds_via_bot("user-token")))

        calls = http._HTTPClient__session.calls
        self.assertEqual(2, len(calls))
        self.assertNotIn("proxy", calls[0][1])
        self.assertEqual(PROXY, calls[1][1]["proxy"])

    def test_a_global_rate_limit_waits_for_its_retry_after(self):
        session = FakeSession([
            (429, json.dumps({"message": "You are being rate limited.", "retry_after": 2.5, "global": True})),
            (200, json.dumps(GUILDS)),
        ])
        delays = []

        async def fake_sleep(delay):
            delays.append(delay)

        with mock.patch.object(server.asyncio, "sleep", fake_sleep):
            self.assertEqual(GUILDS, run_fetch(session))

        self.assertEqual([2.5], delays)
        self.assertEqual(2, len(session.calls))

    def test_a_refused_proxy_connection_retries_over_the_rotated_proxy(self):
        http = http_with(FakeSession([OSError("proxy refused the connection"), (200, json.dumps(GUILDS))]))

        def rotate(attempt):
            # The request hook rotates onto another Webshare endpoint.
            if attempt == 1:
                http.proxy = PROXY

        http._HTTPClient__session.on_request = rotate
        delays = []

        async def fake_sleep(delay):
            delays.append(delay)

        with mock.patch.object(server, "_discord_bot", SimpleNamespace(http=http)), mock.patch.object(
            server.asyncio, "sleep", fake_sleep
        ):
            self.assertEqual(GUILDS, asyncio.run(server._member_guilds_via_bot("user-token")))

        self.assertEqual([1.0], delays)
        self.assertEqual(PROXY, http._HTTPClient__session.calls[1][1]["proxy"])

    def test_a_dead_connection_is_an_error_not_an_empty_list(self):
        session = FakeSession([OSError("proxy refused the connection")])

        with mock.patch.object(server.asyncio, "sleep", mock.AsyncMock()):
            with self.assertRaises(server.DiscordEgressError) as raised:
                run_fetch(session)

        self.assertIn("request failed", str(raised.exception))
        self.assertEqual(2, len(session.calls))

    def test_a_refused_request_without_recovery_is_an_error_not_an_empty_list(self):
        session = FakeSession([(403, "Attention Required!")])

        with self.assertRaises(server.DiscordEgressError) as raised:
            run_fetch(session)

        self.assertIn("403", str(raised.exception))
        self.assertEqual(2, len(session.calls))

    def test_an_expired_token_is_not_retried(self):
        session = FakeSession([(401, json.dumps({"message": "401: Unauthorized"}))])

        with self.assertRaises(server.DiscordEgressError):
            run_fetch(session)

        self.assertEqual(1, len(session.calls))

    def test_a_challenge_page_with_a_200_status_is_not_a_server_list(self):
        session = FakeSession([(200, "<!DOCTYPE html><html>Just a moment...</html>")])

        with self.assertRaises(server.DiscordEgressError):
            run_fetch(session)

    def test_an_unexpected_payload_shape_is_not_a_server_list(self):
        session = FakeSession([(200, json.dumps({"message": "401: Unauthorized"}))])

        with self.assertRaises(server.DiscordEgressError):
            run_fetch(session)


class MemberGuildsRoutingTests(unittest.TestCase):
    """``member_guilds`` is the sync seam the routes call."""

    def setUp(self):
        self._bot = server._discord_bot
        self.addCleanup(setattr, server, "_discord_bot", self._bot)

    def test_the_fetch_runs_on_the_bots_event_loop(self):
        loop, loop_thread = start_loop(self)
        session = FakeSession([(200, json.dumps(GUILDS))])
        server._discord_bot = SimpleNamespace(loop=loop, http=http_with(session, PROXY))

        self.assertEqual(GUILDS, server.member_guilds("user-token"))
        # The request was issued from the bot's loop thread, not Flask's thread.
        self.assertEqual([loop_thread], session.threads)
        self.assertNotEqual(threading.get_ident(), session.threads[0])
        self.assertEqual(PROXY, session.calls[0][1]["proxy"])

    def test_a_web_only_process_still_reads_the_list_directly(self):
        server._discord_bot = None
        with mock.patch.object(server, "discord_get", return_value=GUILDS) as direct:
            self.assertEqual(GUILDS, server.member_guilds("user-token"))
        direct.assert_called_once_with("/users/@me/guilds", "user-token")

    def test_a_bot_that_is_not_running_yet_reads_the_list_directly(self):
        loop = asyncio.new_event_loop()  # never started
        self.addCleanup(loop.close)
        server._discord_bot = SimpleNamespace(loop=loop, http=http_with(FakeSession([(200, "[]")])))

        with mock.patch.object(server, "discord_get", return_value=GUILDS) as direct:
            self.assertEqual(GUILDS, server.member_guilds("user-token"))
        direct.assert_called_once()


class GuildListRouteTests(unittest.TestCase):
    """``GET /api/guilds`` must not answer an empty list when the read fails."""

    def setUp(self):
        self._bot = server._discord_bot
        self._blacklist = dashboard_routes._load_blacklist_manager
        server._discord_bot = None
        self._member_guilds = dashboard_routes.member_guilds
        self.addCleanup(self._restore)

    def _restore(self):
        server._discord_bot = self._bot
        dashboard_routes.member_guilds = self._member_guilds
        dashboard_routes._load_blacklist_manager = self._blacklist

    def _client(self):
        client = app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": "42", "username": "Tester"}
            session["access_token"] = "token"
            session["token_exp"] = time.time() + 3600
        return client

    def test_a_failed_read_is_reported_as_an_error(self):
        def unavailable(token):
            raise server.DiscordEgressError("Discord answered HTTP 403 for the server list.")

        dashboard_routes.member_guilds = unavailable
        response = self._client().get("/api/guilds")

        self.assertEqual(503, response.status_code)
        payload = response.get_json()
        self.assertIsInstance(payload, dict)
        self.assertIn("could not be loaded", payload["error"])

    def test_a_successful_read_still_returns_the_list(self):
        dashboard_routes.member_guilds = lambda token: GUILDS
        response = self._client().get("/api/guilds")

        self.assertEqual(200, response.status_code)
        self.assertEqual(["111"], [guild["id"] for guild in response.get_json()])

    def test_the_route_reads_the_list_over_the_bots_proxy(self):
        """End to end: the page's own request goes through the bot's egress."""
        loop, loop_thread = start_loop(self)
        session = FakeSession([(200, json.dumps(GUILDS))])
        server._discord_bot = SimpleNamespace(
            loop=loop,
            http=http_with(session, PROXY),
            guilds=[SimpleNamespace(id=111)],
        )
        dashboard_routes._load_blacklist_manager = lambda: SimpleNamespace(
            get_guild_entry=lambda guild_id: None
        )

        response = self._client().get("/api/guilds")

        self.assertEqual(200, response.status_code)
        guilds = response.get_json()
        self.assertEqual(["111"], [guild["id"] for guild in guilds])
        self.assertTrue(guilds[0]["installed"])
        # Fetched on the bot's loop, over the bot's active proxy.
        self.assertEqual([loop_thread], session.threads)
        self.assertEqual(PROXY, session.calls[0][1]["proxy"])


if __name__ == "__main__":
    unittest.main()
