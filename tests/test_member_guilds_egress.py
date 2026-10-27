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

from webapp import app  # noqa: E402
from webapp import auth, discord_api, runtime  # noqa: E402
from webapp import config as webapp_config  # noqa: E402
from webapp.routes import dashboard_routes  # noqa: E402

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
    with mock.patch.object(runtime, "_discord_bot", SimpleNamespace(http=http_with(session, proxy))):
        return asyncio.run(auth._member_guilds_via_bot("user-token"))


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
        with mock.patch.object(runtime, "_discord_bot", SimpleNamespace(http=http)):
            self.assertEqual(GUILDS, asyncio.run(auth._member_guilds_via_bot("user-token")))

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

        with mock.patch.object(asyncio, "sleep", fake_sleep):
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

        with mock.patch.object(runtime, "_discord_bot", SimpleNamespace(http=http)), mock.patch.object(
            asyncio, "sleep", fake_sleep
        ):
            self.assertEqual(GUILDS, asyncio.run(auth._member_guilds_via_bot("user-token")))

        self.assertEqual([1.0], delays)
        self.assertEqual(PROXY, http._HTTPClient__session.calls[1][1]["proxy"])

    def test_a_dead_connection_is_an_error_not_an_empty_list(self):
        session = FakeSession([OSError("proxy refused the connection")])

        with mock.patch.object(asyncio, "sleep", mock.AsyncMock()):
            with self.assertRaises(auth.DiscordEgressError) as raised:
                run_fetch(session)

        self.assertIn("request failed", str(raised.exception))
        self.assertEqual(2, len(session.calls))

    def test_a_refused_request_without_recovery_is_an_error_not_an_empty_list(self):
        session = FakeSession([(403, "Attention Required!")])

        with self.assertRaises(auth.DiscordEgressError) as raised:
            run_fetch(session)

        self.assertIn("403", str(raised.exception))
        self.assertEqual(2, len(session.calls))

    def test_an_expired_token_is_not_retried(self):
        session = FakeSession([(401, json.dumps({"message": "401: Unauthorized"}))])

        with self.assertRaises(auth.DiscordEgressError):
            run_fetch(session)

        self.assertEqual(1, len(session.calls))

    def test_a_challenge_page_with_a_200_status_is_not_a_server_list(self):
        session = FakeSession([(200, "<!DOCTYPE html><html>Just a moment...</html>")])

        with self.assertRaises(auth.DiscordEgressError):
            run_fetch(session)

    def test_an_unexpected_payload_shape_is_not_a_server_list(self):
        session = FakeSession([(200, json.dumps({"message": "401: Unauthorized"}))])

        with self.assertRaises(auth.DiscordEgressError):
            run_fetch(session)


class MemberGuildsRoutingTests(unittest.TestCase):
    """``member_guilds`` is the sync seam the routes call."""

    def setUp(self):
        self._bot = runtime._discord_bot
        self.addCleanup(setattr, runtime, "_discord_bot", self._bot)

    def test_the_fetch_runs_on_the_bots_event_loop(self):
        loop, loop_thread = start_loop(self)
        session = FakeSession([(200, json.dumps(GUILDS))])
        runtime._discord_bot = SimpleNamespace(loop=loop, http=http_with(session, PROXY))

        self.assertEqual(GUILDS, auth.member_guilds("user-token"))
        # The request was issued from the bot's loop thread, not Flask's thread.
        self.assertEqual([loop_thread], session.threads)
        self.assertNotEqual(threading.get_ident(), session.threads[0])
        self.assertEqual(PROXY, session.calls[0][1]["proxy"])

    def test_a_web_only_process_still_reads_the_list_directly(self):
        runtime._discord_bot = None
        with mock.patch.object(discord_api, "discord_get", return_value=GUILDS) as direct:
            self.assertEqual(GUILDS, auth.member_guilds("user-token"))
        direct.assert_called_once_with("/users/@me/guilds", "user-token")

    def test_a_bot_that_is_not_running_yet_reads_the_list_directly(self):
        loop = asyncio.new_event_loop()  # never started
        self.addCleanup(loop.close)
        runtime._discord_bot = SimpleNamespace(loop=loop, http=http_with(FakeSession([(200, "[]")])))

        with mock.patch.object(discord_api, "discord_get", return_value=GUILDS) as direct:
            self.assertEqual(GUILDS, auth.member_guilds("user-token"))
        direct.assert_called_once()


class GuildListRouteTests(unittest.TestCase):
    """``GET /api/guilds`` must not answer an empty list when the read fails."""

    def setUp(self):
        self._bot = runtime._discord_bot
        self._blacklist = dashboard_routes._load_blacklist_manager
        runtime._discord_bot = None
        self._member_guilds = dashboard_routes.member_guilds
        self.addCleanup(self._restore)

    def _restore(self):
        runtime._discord_bot = self._bot
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
            raise auth.DiscordEgressError("Discord answered HTTP 403 for the server list.")

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

    def test_a_revoked_session_asks_for_a_new_login_instead_of_blaming_discord(self):
        def revoked(token):
            raise auth.DiscordEgressError("Discord answered HTTP 401 for the server list.", status=401)

        dashboard_routes.member_guilds = revoked
        response = self._client().get("/api/guilds")

        self.assertEqual(401, response.status_code)
        payload = response.get_json()
        self.assertEqual("/auth/login", payload["login_url"])
        self.assertIn("session expired", payload["error"])

    def test_the_route_reads_the_list_over_the_bots_proxy(self):
        """End to end: the page's own request goes through the bot's egress."""
        loop, loop_thread = start_loop(self)
        session = FakeSession([(200, json.dumps(GUILDS))])
        runtime._discord_bot = SimpleNamespace(
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


class RejectedTokenRecoveryTests(unittest.TestCase):
    """A 401 mid-session is a token Discord revoked, not a Discord outage.

    The dashboard logged out of nowhere and every request then answered 401:
    the stored access token had been rotated away by another refresh while
    ``token_exp`` still said it was good for hours, so nothing ever replaced it.
    """

    def setUp(self):
        self._once = auth._member_guilds_once
        self._refresh = auth.ensure_access_token
        self.addCleanup(self._restore)

    def _restore(self):
        auth._member_guilds_once = self._once
        auth.ensure_access_token = self._refresh

    def test_a_rejected_token_reports_its_status(self):
        session = FakeSession([(401, json.dumps({"message": "401: Unauthorized"}))])

        with self.assertRaises(auth.DiscordEgressError) as raised:
            run_fetch(session)

        self.assertEqual(401, raised.exception.status)

    def test_a_revoked_token_is_refreshed_once_and_the_read_retried(self):
        from flask import session as flask_session

        tokens = []

        def once(token):
            tokens.append(token)
            if len(tokens) == 1:
                raise auth.DiscordEgressError(
                    "Discord answered HTTP 401 for the server list.", status=401
                )
            return GUILDS

        refreshes = []

        def refresh(force=False):
            refreshes.append(force)
            return True

        auth._member_guilds_once = once
        auth.ensure_access_token = refresh

        with app.test_request_context("/dashboard/servers"):
            flask_session["access_token"] = "fresh-token"
            self.assertEqual(GUILDS, auth.member_guilds("revoked-token"))

        # The retry left over the refreshed token, not the one Discord refused.
        self.assertEqual(["revoked-token", "fresh-token"], tokens)
        # Forced: the session clock still believed the old token was fresh.
        self.assertEqual([True], refreshes)

    def test_a_401_the_session_cannot_refresh_is_reported_once(self):
        calls = []

        def once(token):
            calls.append(token)
            raise auth.DiscordEgressError(
                "Discord answered HTTP 401 for the server list.", status=401
            )

        auth._member_guilds_once = once
        auth.ensure_access_token = lambda force=False: False

        with self.assertRaises(auth.DiscordEgressError) as raised:
            auth.member_guilds("revoked-token")

        self.assertEqual(1, len(calls))
        self.assertEqual(401, raised.exception.status)

    def test_an_egress_failure_does_not_spend_the_refresh_token(self):
        calls = []
        refreshes = []

        def once(token):
            calls.append(token)
            raise auth.DiscordEgressError(
                "Discord answered HTTP 403 for the server list.", status=403
            )

        auth._member_guilds_once = once
        auth.ensure_access_token = lambda force=False: refreshes.append(force) or True

        with self.assertRaises(auth.DiscordEgressError):
            auth.member_guilds("user-token")

        self.assertEqual(1, len(calls))
        self.assertEqual([], refreshes)


class ForcedTokenRefreshTests(unittest.TestCase):
    """``ensure_access_token(force=True)`` refreshes a clock-fresh token."""

    def _patch_token_exchange(self, seen):
        def fake_request(method, url, **kwargs):
            seen.append(kwargs["data"]["refresh_token"])
            response = mock.Mock()
            response.json.return_value = {
                "access_token": "new-token",
                "refresh_token": "rotated-token",
                "expires_in": 604800,
            }
            response.raise_for_status.return_value = None
            return response

        return mock.patch.object(discord_api, "discord_request", fake_request)

    def test_a_clock_fresh_token_is_left_alone_unless_forced(self):
        from flask import session as flask_session

        seen = []
        with app.test_request_context("/dashboard"):
            flask_session["user"] = {"id": "42"}
            flask_session["access_token"] = "stale-token"
            flask_session["refresh_token"] = "refresh-1"
            flask_session["token_exp"] = time.time() + 3600
            with self._patch_token_exchange(seen):
                self.assertTrue(auth.ensure_access_token())
                self.assertEqual("stale-token", flask_session["access_token"])

        self.assertEqual([], seen)

    def test_force_exchanges_the_refresh_token_even_while_the_clock_is_fresh(self):
        from flask import session as flask_session

        seen = []
        with app.test_request_context("/dashboard"):
            flask_session["user"] = {"id": "42"}
            flask_session["access_token"] = "stale-token"
            flask_session["refresh_token"] = "refresh-1"
            flask_session["token_exp"] = time.time() + 3600
            with self._patch_token_exchange(seen), mock.patch.object(
                webapp_config, "DISCORD_CLIENT_SECRET", "secret"
            ):
                self.assertTrue(auth.ensure_access_token(force=True))
                self.assertEqual("new-token", flask_session["access_token"])
                self.assertEqual("rotated-token", flask_session["refresh_token"])

        self.assertEqual(["refresh-1"], seen)


if __name__ == "__main__":
    unittest.main()
