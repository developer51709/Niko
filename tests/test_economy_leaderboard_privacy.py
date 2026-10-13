"""Regression tests for global economy leaderboard pagination and privacy."""

import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import app
from webapp import public_routes as routes
from webapp.server import get_runtime_leaderboard_page
from cogs.economy.commands.leaderboard import LeaderboardMixin
from database import MongoPool


def leaderboard_client(rows, *, viewer=None, staff=None, mutual=None, bot=None):
    client = app.test_client()
    if viewer:
        with client.session_transaction() as session:
            session["user"] = {"id": viewer}
    patches = [
        patch.object(routes, "get_runtime_leaderboard_page", return_value=(rows, 45)),
        patch.object(routes, "_current_staff_role", return_value=staff),
        patch.object(routes, "get_mutual_leaderboard_identity_ids", return_value=mutual or set()),
        patch.object(routes, "_discord_bot", bot),
        patch.object(routes, "run_on_bot_loop", side_effect=lambda task: asyncio.run(task)),
    ]
    for active_patch in patches:
        active_patch.start()
    return client, patches


def stop_patches(patches):
    for active_patch in reversed(patches):
        active_patch.stop()


class EconomyLeaderboardPrivacyTests(unittest.TestCase):
    def test_mongodb_query_applies_bound_limit_and_offset_in_database(self):
        class Cursor:
            def __init__(self, docs):
                self.docs = docs
                self.skipped = 0
                self.limited = None

            def sort(self, fields):
                for field, direction in reversed(fields):
                    self.docs.sort(key=lambda doc: doc.get(field, 0), reverse=direction < 0)
                return self

            def skip(self, count):
                self.skipped = count
                return self

            def limit(self, count):
                self.limited = count
                return self

            async def to_list(self, length=None):
                end = None if self.limited is None else self.skipped + self.limited
                return self.docs[self.skipped:end]

        class Collection:
            def __init__(self):
                self.docs = [
                    {"_id": user_id, "user_id": user_id, "net_worth": worth}
                    for user_id, worth in [("1", 100), ("2", 80), ("3", 60), ("4", 40)]
                ]
                self.cursor = None

            def find(self, _filter, _projection):
                self.cursor = Cursor(self.docs.copy())
                return self.cursor

        class Database(dict):
            def __getitem__(self, name):
                return self.setdefault(name, Collection())

        class Client:
            def __init__(self):
                self.db = Database()

            def __getitem__(self, _name):
                return self.db

        pool = MongoPool(Client(), "test")
        rows = asyncio.run(pool.fetch(
            "SELECT user_id, balance, bank, leaderboard_private "
            "FROM economy_users ORDER BY net_worth DESC, user_id ASC LIMIT $1 OFFSET $2",
            2,
            1,
        ))

        self.assertEqual([row["user_id"] for row in rows], ["2", "3"])
        cursor = pool.db["economy_users"].cursor
        self.assertEqual(cursor.skipped, 1)
        self.assertEqual(cursor.limited, 2)

    def test_runtime_leaderboard_reads_only_requested_database_page(self):
        import sqlite3

        connection = sqlite3.connect(":memory:")
        connection.execute(
            "CREATE TABLE economy_users (user_id INTEGER, balance INTEGER, bank INTEGER, "
            "net_worth INTEGER, leaderboard_private INTEGER)"
        )
        connection.executemany(
            "INSERT INTO economy_users VALUES (?, ?, ?, ?, ?)",
            [(user_id, 100 - user_id, user_id, 100, 0) for user_id in range(1, 26)],
        )

        with patch("webapp.server.sqlite_connect", return_value=connection):
            rows, total = get_runtime_leaderboard_page(offset=20, limit=20)

        self.assertEqual(total, 25)
        self.assertEqual(len(rows), 5)
        self.assertEqual([row["user_id"] for row in rows], ["21", "22", "23", "24", "25"])

    def test_public_leaderboard_hides_all_identity_fields_for_private_profiles(self):
        rows = [
            {"user_id": "123", "net_worth": 900, "leaderboard_private": True},
            {"user_id": "456", "net_worth": 800, "leaderboard_private": False},
        ]
        client, patches = leaderboard_client(rows)
        try:
            response = client.get("/api/economy/leaderboard?page=2")
        finally:
            stop_patches(patches)

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["page"], 2)
        self.assertEqual(payload["total"], 45)
        self.assertEqual(payload["pages"], 3)
        self.assertEqual(payload["entries"][0], {
            "rank": 21,
            "net_worth": 900,
            "private": True,
            "username": None,
            "display_name": None,
            "avatar_url": None,
        })
        self.assertEqual(payload["entries"][1]["rank"], 22)

    def test_private_identity_is_returned_to_official_staff_and_mutual_guild_members(self):
        private_row = {"user_id": "123", "net_worth": 900, "leaderboard_private": True}

        class Avatar:
            url = "https://cdn.example/avatar.png"

        class User:
            name = "cafe_user"
            global_name = "Cafe User"
            display_name = "Cafe User"
            display_avatar = Avatar()

        class Bot:
            guilds = []

            @staticmethod
            def get_user(user_id):
                return User() if user_id == 123 else None

        access_cases = (
            {"viewer": "900", "staff": "moderator"},
            {"viewer": "900", "mutual": {"123"}},
        )
        for access in access_cases:
            with self.subTest(access=access):
                client, patches = leaderboard_client([private_row], bot=Bot(), **access)
                try:
                    entry = client.get("/api/economy/leaderboard").get_json()["entries"][0]
                finally:
                    stop_patches(patches)
                self.assertEqual(entry["username"], "cafe_user")
                self.assertEqual(entry["display_name"], "Cafe User")
                self.assertEqual(entry["avatar_url"], "https://cdn.example/avatar.png")

    def test_private_identity_stays_hidden_from_unrelated_signed_in_viewer(self):
        private_row = {"user_id": "123", "net_worth": 900, "leaderboard_private": True}
        client, patches = leaderboard_client([private_row], viewer="900", mutual=set())
        try:
            entry = client.get("/api/economy/leaderboard").get_json()["entries"][0]
        finally:
            stop_patches(patches)
        self.assertEqual(entry["rank"], 1)
        self.assertTrue(entry["private"])
        self.assertIsNone(entry["username"])
        self.assertIsNone(entry["display_name"])
        self.assertIsNone(entry["avatar_url"])

    def test_leaderboard_rejects_invalid_page_values(self):
        client, patches = leaderboard_client([])
        try:
            malformed = client.get("/api/economy/leaderboard?page=not-a-number")
            non_positive = client.get("/api/economy/leaderboard?page=0")
        finally:
            stop_patches(patches)
        self.assertEqual(malformed.status_code, 400)
        self.assertEqual(non_positive.status_code, 400)

    def test_discord_leaderboard_command_links_to_public_page_with_privacy_note(self):
        class Context:
            interaction = None

            async def send(self, *, view):
                self.view = view

        context = Context()
        asyncio.run(LeaderboardMixin.leaderboard.callback(LeaderboardMixin(), context))
        text = context.view.children[0].children[-1].content
        self.assertIn("private profiles stay ranked", text)
        self.assertIn("https://niko.sryze.cc/leaderboard", text)
