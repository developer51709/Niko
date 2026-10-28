"""Guild detection for the dashboard's "My servers" tab.

The reported bug: every guild the signed-in member administers was listed under
"Add Niko to a server" instead of "Manage a server", because install state was
read only from the live gateway cache. That cache is legitimately empty in a
dashboard served before the first READY, so the bot's recorded guild list has
to be the fallback.
"""

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from webapp import app  # noqa: E402
from webapp.routes import dashboard_routes  # noqa: E402
from webapp import server  # noqa: E402
from webapp import auth, discord_api, runtime  # noqa: E402
from webapp import config as webapp_config  # noqa: E402

# What Discord's `/users/@me/guilds` returns for the signed-in member: two guilds
# the bot is already in (one owned, one managed), one it is not in yet, and one
# the member does not administer.
FAKE_GUILDS = [
    {"id": "111", "name": "Owned server", "icon": None, "owner": True, "permissions": "0"},
    {"id": "222", "name": "Managed server", "icon": "abc", "permissions": str(webapp_config.MANAGE_GUILD_PERM)},
    {"id": "333", "name": "Invite Niko here", "icon": None, "permissions": str(webapp_config.MANAGE_GUILD_PERM)},
    {"id": "444", "name": "Not mine", "icon": None, "permissions": "0"},
]


class BotGuildIdTests(unittest.TestCase):
    """`bot_guild_ids` must never be empty just because no gateway is attached."""

    def setUp(self):
        self._stats_path = webapp_config.BOT_STATS
        self._bot = runtime._discord_bot
        handle, self._temp_path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(handle, "w") as file:
            json.dump({"guild_count": 2, "guild_ids": [111, 222]}, file)
        webapp_config.BOT_STATS = self._temp_path

    def tearDown(self):
        webapp_config.BOT_STATS = self._stats_path
        runtime._discord_bot = self._bot
        os.unlink(self._temp_path)

    def test_the_live_gateway_cache_wins_when_it_has_guilds(self):
        runtime._discord_bot = SimpleNamespace(guilds=[SimpleNamespace(id=333)])
        self.assertEqual(runtime.bot_guild_ids(), {"333"})

    def test_an_empty_gateway_cache_falls_back_to_the_recorded_guilds(self):
        # Before the first READY the bot object exists but holds no guilds.
        runtime._discord_bot = SimpleNamespace(guilds=[])
        self.assertEqual(runtime.bot_guild_ids(), {"111", "222"})

    def test_a_dashboard_without_a_bot_object_reads_the_recorded_guilds(self):
        runtime._discord_bot = None
        self.assertEqual(runtime.bot_guild_ids(), {"111", "222"})


class GuildListRouteTests(unittest.TestCase):
    """`GET /api/guilds` is what the My servers tab renders."""

    def setUp(self):
        self._stats_path = webapp_config.BOT_STATS
        self._bot = runtime._discord_bot
        handle, self._temp_path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(handle, "w") as file:
            json.dump({"guild_count": 2, "guild_ids": [111, 222]}, file)
        webapp_config.BOT_STATS = self._temp_path
        runtime._discord_bot = None
        # The route reads the list through ``member_guilds``; the fetch itself is
        # covered by tests/test_member_guilds_egress.py.
        self._member_guilds = dashboard_routes.member_guilds
        dashboard_routes.member_guilds = lambda token: FAKE_GUILDS

    def tearDown(self):
        webapp_config.BOT_STATS = self._stats_path
        runtime._discord_bot = self._bot
        dashboard_routes.member_guilds = self._member_guilds
        os.unlink(self._temp_path)

    def _client(self):
        client = app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": "42", "username": "Tester"}
            session["access_token"] = "token"
            session["token_exp"] = time.time() + 3600
        return client

    def test_installed_guilds_are_marked_installed(self):
        response = self._client().get("/api/guilds")
        self.assertEqual(response.status_code, 200)
        guilds = {guild["id"]: guild for guild in response.get_json()}
        # Only guilds the member administers are listed at all.
        self.assertEqual(sorted(guilds), ["111", "222", "333"])
        self.assertTrue(guilds["111"]["installed"])
        self.assertTrue(guilds["222"]["installed"])
        self.assertFalse(guilds["333"]["installed"])

    def test_only_uninstalled_guilds_carry_an_invite_url(self):
        guilds = {guild["id"]: guild for guild in self._client().get("/api/guilds").get_json()}
        self.assertIsNone(guilds["111"]["invite_url"])
        self.assertIsNone(guilds["222"]["invite_url"])
        self.assertIn("guild_id=333", guilds["333"]["invite_url"])


class GuildAccessTests(unittest.TestCase):
    """Guild pages stay reachable while the dashboard owns no gateway cache."""

    def setUp(self):
        self._stats_path = webapp_config.BOT_STATS
        self._bot = runtime._discord_bot
        handle, self._temp_path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(handle, "w") as file:
            json.dump({"guild_count": 2, "guild_ids": [111, 222]}, file)
        webapp_config.BOT_STATS = self._temp_path
        runtime._discord_bot = None

    def tearDown(self):
        webapp_config.BOT_STATS = self._stats_path
        runtime._discord_bot = self._bot
        os.unlink(self._temp_path)

    def test_managed_guilds_are_authorized_without_a_gateway_cache(self):
        from flask import session

        with app.test_request_context("/dashboard"):
            session["user"] = {"id": "42"}
            session["access_token"] = "token"
            session["token_exp"] = time.time() + 3600
            with mock.patch.object(discord_api, "discord_get", lambda endpoint, token: FAKE_GUILDS):
                self.assertEqual(auth.managed_guild_ids(), {"111", "222"})

    def test_a_guild_the_bot_is_not_in_is_refused(self):
        from flask import session

        with app.test_request_context("/dashboard"):
            session["user"] = {"id": "42"}
            session["access_token"] = "token"
            session["token_exp"] = time.time() + 3600
            with mock.patch.object(discord_api, "discord_get", lambda endpoint, token: FAKE_GUILDS):
                self.assertNotIn("333", auth.managed_guild_ids())


if __name__ == "__main__":
    unittest.main()
