"""Regression tests for the public per-server leveling leaderboard.

`/leveling leaderboard` links to `/levels/<guild id>` instead of rendering
paginated images, so the page's API has to paginate on the server, hand out
only what an anonymous visitor may see, and say clearly when the bot is not in
the guild at all.
"""

import asyncio
import sqlite3
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import app
from webapp import public_routes as routes
from webapp.server import get_runtime_guild_level_page, level_xp_for_next


class Avatar:
    url = "https://cdn.example/avatar.png"


class Member:
    def __init__(self, user_id, name):
        self.id = user_id
        self.name = name
        self.global_name = name
        self.display_avatar = Avatar()


class Guild:
    id = 555
    name = "Cozy Corner"
    member_count = 42
    icon = None

    def __init__(self, members=None):
        self.members = members or []


class Bot:
    def __init__(self, guild):
        self.guild = guild
        self.guilds = [guild] if guild else []

    def get_guild(self, guild_id):
        if self.guild is None:
            return None
        return self.guild if int(guild_id) == self.guild.id else None

    def get_cog(self, _name):
        return None


def leaderboard_client(rows, *, bot, total=None):
    client = app.test_client()
    patches = [
        patch.object(
            routes,
            "get_runtime_guild_level_page",
            return_value=(rows, total if total is not None else len(rows)),
        ),
        patch.object(routes, "get_runtime_level_config", return_value={"xp_enabled": True}),
        patch.object(routes, "_discord_bot", bot),
        patch.object(routes, "run_on_bot_loop", side_effect=lambda task: asyncio.run(task)),
        # The shared runtime helpers live in `server`, so their lookups use that
        # module's own bot and loop bridge.
        patch("webapp.server._discord_bot", bot),
        patch("webapp.server.run_on_bot_loop", side_effect=lambda task: asyncio.run(task)),
    ]
    for active_patch in patches:
        active_patch.start()
    return client, patches


def stop_patches(patches):
    for active_patch in reversed(patches):
        active_patch.stop()


class GuildLeaderboardRouteTests(unittest.TestCase):
    def test_page_reports_guild_identity_and_ranked_progress(self):
        guild = Guild([Member(41, "Ada")])
        client, patches = leaderboard_client(
            [{"user_id": "41", "xp": 120, "level": 3}],
            bot=Bot(guild),
            total=27,
        )
        try:
            response = client.get("/api/levels/555?page=2")
        finally:
            stop_patches(patches)

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["guild"]["name"], "Cozy Corner")
        self.assertEqual(payload["guild"]["member_count"], 42)
        self.assertTrue(payload["leveling_enabled"])
        self.assertEqual(payload["total"], 27)
        self.assertEqual(payload["pages"], 2)

        entry = payload["entries"][0]
        # Page two starts after the twenty-five rows of page one.
        self.assertEqual(entry["rank"], 26)
        self.assertEqual(entry["display_name"], "Ada")
        self.assertEqual(entry["xp_for_next"], 295)
        # The public payload never carries the Discord id itself.
        self.assertNotIn("41", entry["key"])
        self.assertNotIn("user_id", entry)

    def test_unknown_guild_is_a_404_with_its_own_flag(self):
        client, patches = leaderboard_client([], bot=Bot(None))
        try:
            response = client.get("/api/levels/999")
        finally:
            stop_patches(patches)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.get_json()["unknown_guild"])

    def test_page_numbers_must_be_positive(self):
        client, patches = leaderboard_client([], bot=Bot(Guild()))
        try:
            response = client.get("/api/levels/555?page=0")
        finally:
            stop_patches(patches)

        self.assertEqual(response.status_code, 400)


class GuildLevelPageTests(unittest.TestCase):
    def test_reads_only_the_requested_page_in_rank_order(self):
        connection = sqlite3.connect(":memory:")
        connection.execute(
            "CREATE TABLE levels (guild_id INTEGER, user_id INTEGER, xp INTEGER, level INTEGER)"
        )
        connection.executemany(
            "INSERT INTO levels VALUES (?, ?, ?, ?)",
            [
                (555, 1, 10, 1),
                (555, 2, 90, 2),
                (555, 3, 40, 2),
                (777, 4, 999, 9),
            ],
        )

        with patch("webapp.server.sqlite_connect", return_value=connection), \
                patch("webapp.server._discord_bot", None):
            rows, total = get_runtime_guild_level_page("555", offset=0, limit=2)

        self.assertEqual(total, 3)
        self.assertEqual([row["user_id"] for row in rows], ["2", "3"])

    def test_xp_target_follows_the_leveling_curve(self):
        with patch("webapp.server._discord_bot", None):
            self.assertEqual(level_xp_for_next(3), 5 * 9 + 50 * 3 + 100)


if __name__ == "__main__":
    unittest.main()
