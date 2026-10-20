"""Regression tests for the live (polling) economy leaderboard.

The public board refreshes itself every few seconds, so the endpoint must stay
cheap to call: identities and the viewer's guild list are cached, while the
standings themselves -- and the privacy decision behind them -- stay fresh. Rows
also carry a stable opaque key so the browser can animate a member who moves
rank instead of re-rendering the whole list.
"""

import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import app
from webapp import leaderboard_cache
from webapp import public_routes as routes
from webapp import server as server_routes


class Avatar:
    url = "https://cdn.example/avatar.png"


class User:
    name = "cafe_user"
    global_name = "Cafe User"
    display_name = "Cafe User"
    display_avatar = Avatar()


class CallCountingBot:
    """A bot stub that records how often each identity lookup happens."""

    guilds = []

    def __init__(self, known_ids):
        self.known_ids = set(known_ids)
        self.lookups = []

    def get_user(self, user_id):
        self.lookups.append(user_id)
        return User() if user_id in self.known_ids else None

    async def fetch_user(self, user_id):
        return User()


def leaderboard_client(rows, *, viewer=None, bot=None):
    client = app.test_client()
    if viewer:
        with client.session_transaction() as session:
            session["user"] = {"id": viewer}
            session["access_token"] = "test-token"
    patches = [
        patch.object(routes, "get_runtime_leaderboard_page", return_value=(rows, len(rows))),
        patch.object(routes, "_current_staff_role", return_value=None),
        patch.object(routes, "_discord_bot", bot),
        patch.object(routes, "run_on_bot_loop", side_effect=lambda task: asyncio.run(task)),
    ]
    for active_patch in patches:
        active_patch.start()
    return client, patches


def stop_patches(patches):
    for active_patch in reversed(patches):
        active_patch.stop()


class LeaderboardRowKeyTests(unittest.TestCase):
    def setUp(self):
        leaderboard_cache.reset()

    def test_row_keys_are_stable_across_polls_and_distinct_per_profile(self):
        rows = [
            {"user_id": "123", "net_worth": 900, "leaderboard_private": True},
            {"user_id": "456", "net_worth": 800, "leaderboard_private": False},
        ]
        client, patches = leaderboard_client(rows)
        try:
            first = client.get("/api/economy/leaderboard").get_json()["entries"]
            second = client.get("/api/economy/leaderboard").get_json()["entries"]
        finally:
            stop_patches(patches)

        self.assertEqual([entry["key"] for entry in first], [entry["key"] for entry in second])
        self.assertNotEqual(first[0]["key"], first[1]["key"])
        for entry, user_id in zip(first, ("123", "456")):
            self.assertNotEqual(entry["key"], user_id)
            self.assertNotIn(user_id, entry["key"])

    def test_private_profiles_keep_their_key_while_moving_rank(self):
        """A private row still animates, without ever naming the member."""

        def rows_for_order(order):
            return [
                {"user_id": user_id, "net_worth": worth, "leaderboard_private": True}
                for user_id, worth in order
            ]

        client, patches = leaderboard_client(rows_for_order([("123", 900), ("456", 800)]))
        try:
            before = client.get("/api/economy/leaderboard").get_json()["entries"]
        finally:
            stop_patches(patches)
        leaderboard_cache.reset()

        client, patches = leaderboard_client(rows_for_order([("456", 950), ("123", 900)]))
        try:
            after = client.get("/api/economy/leaderboard").get_json()["entries"]
        finally:
            stop_patches(patches)

        moved = next(entry for entry in after if entry["key"] == before[1]["key"])
        self.assertEqual(moved["rank"], 1)
        self.assertTrue(moved["private"])
        self.assertIsNone(moved["display_name"])


class LeaderboardPollingCostTests(unittest.TestCase):
    def setUp(self):
        leaderboard_cache.reset()

    def test_identity_lookups_are_reused_between_polls(self):
        rows = [
            {"user_id": "123", "net_worth": 900, "leaderboard_private": False},
            {"user_id": "456", "net_worth": 800, "leaderboard_private": False},
        ]
        bot = CallCountingBot({123, 456})
        client, patches = leaderboard_client(rows, bot=bot)
        try:
            for _ in range(3):
                entries = client.get("/api/economy/leaderboard").get_json()["entries"]
                self.assertEqual([entry["display_name"] for entry in entries], ["Cafe User", "Cafe User"])
        finally:
            stop_patches(patches)

        self.assertEqual(sorted(bot.lookups), [123, 456])

    def test_identity_cache_expires_so_renames_show_up(self):
        rows = [{"user_id": "123", "net_worth": 900, "leaderboard_private": False}]
        bot = CallCountingBot({123})
        client, patches = leaderboard_client(rows, bot=bot)
        try:
            client.get("/api/economy/leaderboard")
            with patch.object(leaderboard_cache, "IDENTITY_TTL", 0):
                client.get("/api/economy/leaderboard")
        finally:
            stop_patches(patches)

        self.assertEqual(bot.lookups, [123, 123])

    def test_viewer_guild_list_is_fetched_once_for_repeated_polls(self):
        rows = [{"user_id": "123", "net_worth": 900, "leaderboard_private": True}]
        bot = CallCountingBot({123})
        guild_calls = []

        def fake_guilds(_endpoint, _token):
            guild_calls.append(1)
            return [{"id": "777"}]

        client, patches = leaderboard_client(rows, viewer="900", bot=bot)
        try:
            with patch.object(server_routes, "ensure_access_token", return_value=True), patch.object(
                server_routes, "discord_get", side_effect=fake_guilds
            ):
                for _ in range(3):
                    self.assertEqual(client.get("/api/economy/leaderboard").status_code, 200)
        finally:
            stop_patches(patches)

        self.assertEqual(len(guild_calls), 1)

    def test_standings_are_not_cached_between_polls(self):
        reads = []

        def read_page(_offset, _limit):
            reads.append(1)
            worth = 100 + len(reads)
            return ([{"user_id": "123", "net_worth": worth, "leaderboard_private": False}], 1)

        client, patches = leaderboard_client([])
        try:
            routes.get_runtime_leaderboard_page.side_effect = read_page
            first = client.get("/api/economy/leaderboard").get_json()["entries"][0]["net_worth"]
            second = client.get("/api/economy/leaderboard").get_json()["entries"][0]["net_worth"]
        finally:
            stop_patches(patches)

        self.assertEqual(len(reads), 2)
        self.assertNotEqual(first, second)

    def test_polled_responses_are_not_cached_by_intermediaries(self):
        client, patches = leaderboard_client([])
        try:
            response = client.get("/api/economy/leaderboard")
        finally:
            stop_patches(patches)

        self.assertEqual(response.status_code, 200)
        cache_control = response.headers.get("Cache-Control", "")
        self.assertIn("no-store", cache_control)
        self.assertEqual(response.headers.get("Pragma"), "no-cache")


if __name__ == "__main__":
    unittest.main()
