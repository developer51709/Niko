"""Regression tests for global economy leaderboard pagination and privacy."""

import asyncio
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import aiosqlite

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import app
from webapp.routes import dashboard_routes
from webapp.routes import public_routes as routes
from webapp import server as server_routes
from webapp import database, runtime  # noqa: E402
from webapp import auth, runtime  # noqa: E402
from webapp.server import get_runtime_leaderboard_page
from cogs.economy.commands.leaderboard import LeaderboardMixin
from database import MongoPool, SQLitePool


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

        with patch("webapp.database.sqlite_connect", return_value=connection):
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
        hidden_entry = payload["entries"][0]
        self.assertEqual(hidden_entry, {
            "key": hidden_entry["key"],
            "rank": 21,
            "net_worth": 900,
            "private": True,
            "username": None,
            "display_name": None,
            "avatar_url": None,
        })
        # The row key exists so the browser can animate a moving row, but it
        # must never be the Discord id it was derived from.
        self.assertIsInstance(hidden_entry["key"], str)
        self.assertNotEqual(hidden_entry["key"], "123")
        self.assertNotIn("123", hidden_entry["key"])
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

    def test_privacy_toggle_saves_through_the_bot_connection_pool(self):
        """The dashboard toggle must write through ``bot.cxn`` on either backend.

        Both pools renumber every ``$n`` placeholder separately, so a statement
        that binds one value for the ``ON CONFLICT`` clause fails on SQLite
        (binding count) and on MongoDB (missing SET argument), which is what
        users saw as "could not be saved".
        """

        class Result:
            def __init__(self, upserted_id):
                self.upserted_id = upserted_id

        class Collection:
            def __init__(self):
                self.docs = {}

            async def update_one(self, filter_dict, update, upsert=False):
                doc = self.docs.get(filter_dict["_id"])
                if doc is None:
                    doc = dict(update.get("$setOnInsert", {}))
                    doc.update(update.get("$set", {}))
                    self.docs[filter_dict["_id"]] = doc
                    return Result(upserted_id=filter_dict["_id"])
                doc.update(update.get("$set", {}))
                return Result(upserted_id=None)

        class Database(dict):
            def __getitem__(self, name):
                return self.setdefault(name, Collection())

        class MongoClient:
            def __init__(self):
                self.db = Database()

            def __getitem__(self, _name):
                return self.db

        def sqlite_backend():
            loop = asyncio.new_event_loop()
            connection = loop.run_until_complete(aiosqlite.connect(":memory:"))
            pool = SQLitePool(connection)
            loop.run_until_complete(pool.execute(
                "CREATE TABLE IF NOT EXISTS economy_users ("
                "user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 100, "
                "net_worth INTEGER DEFAULT 100, "
                "leaderboard_private INTEGER NOT NULL DEFAULT 0)"
            ))

            def read_value():
                rows = loop.run_until_complete(
                    pool.fetch("SELECT user_id, leaderboard_private FROM economy_users")
                )
                self.assertEqual(len(rows), 1)
                return int(rows[0]["leaderboard_private"])

            def close():
                loop.run_until_complete(connection.close())
                loop.close()

            return pool, (lambda task: loop.run_until_complete(task)), read_value, close

        def mongo_backend():
            pool = MongoPool(MongoClient(), "test")

            def read_value():
                documents = pool.collection("economy_users").docs
                self.assertEqual(len(documents), 1)
                return int(next(iter(documents.values()))["leaderboard_private"])

            return pool, asyncio.run, read_value, lambda: None

        for name, backend in (("sqlite", sqlite_backend), ("mongodb", mongo_backend)):
            with self.subTest(backend=name):
                pool, run_task, read_value, close = backend()

                class Bot:
                    cxn = pool

                    @staticmethod
                    def get_cog(_name):
                        return None

                client = app.test_client()
                with client.session_transaction() as session:
                    session["user"] = {"id": "424242"}
                    session["access_token"] = "test-token"
                    session["token_exp"] = time.time() + 3600
                    session["csrf_token"] = "test-csrf"

                try:
                    with patch.object(
                        auth, "_current_user_blacklist_entry", return_value=None
                    ), patch.object(dashboard_routes, "_discord_bot", Bot()), patch.object(
                        dashboard_routes, "run_on_bot_loop", side_effect=run_task
                    ):
                        hidden = client.post(
                            "/api/me/economy-privacy",
                            json={"leaderboard_private": True},
                            headers={"X-CSRF-Token": "test-csrf"},
                        )
                        self.assertEqual(hidden.status_code, 200, hidden.get_json())
                        self.assertEqual(
                            hidden.get_json(), {"ok": True, "leaderboard_private": True}
                        )
                        self.assertEqual(read_value(), 1)

                        visible = client.post(
                            "/api/me/economy-privacy",
                            json={"leaderboard_private": False},
                            headers={"X-CSRF-Token": "test-csrf"},
                        )
                        self.assertEqual(visible.status_code, 200, visible.get_json())
                        self.assertEqual(
                            visible.get_json(), {"ok": True, "leaderboard_private": False}
                        )
                        # The second save updates the existing profile in place.
                        self.assertEqual(read_value(), 0)
                finally:
                    close()

    def test_privacy_toggle_is_reflected_by_the_overview_after_a_reload(self):
        """Saving must persist: the Overview payload reloads the stored preference."""
        loop = asyncio.new_event_loop()
        connection = loop.run_until_complete(aiosqlite.connect(":memory:"))
        pool = SQLitePool(connection)
        loop.run_until_complete(pool.execute(
            "CREATE TABLE IF NOT EXISTS economy_users ("
            "user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 100, "
            "bank INTEGER DEFAULT 0, net_worth INTEGER DEFAULT 100, "
            "leaderboard_private INTEGER NOT NULL DEFAULT 0, "
            "total_earned INTEGER DEFAULT 100, level INTEGER DEFAULT 0, "
            "job TEXT DEFAULT 'barista', daily_streak INTEGER DEFAULT 0, "
            "achievements TEXT DEFAULT '[]')"
        ))

        class Bot:
            cxn = pool

            @staticmethod
            def get_cog(_name):
                return None

        client = app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": "424242"}
            session["access_token"] = "test-token"
            session["token_exp"] = time.time() + 3600
            session["csrf_token"] = "test-csrf"

        def run_task(task):
            return loop.run_until_complete(task)

        try:
            with patch.object(
                auth, "_current_user_blacklist_entry", return_value=None
            ), patch.object(runtime, "_discord_bot", Bot()), patch.object(
                runtime, "run_on_bot_loop", side_effect=run_task
            ), patch.object(dashboard_routes, "_discord_bot", Bot()), patch.object(
                dashboard_routes, "run_on_bot_loop", side_effect=run_task
            ):
                before = client.get("/api/me/overview").get_json()
                self.assertFalse(before["leaderboard_private"])

                saved = client.post(
                    "/api/me/economy-privacy",
                    json={"leaderboard_private": True},
                    headers={"X-CSRF-Token": "test-csrf"},
                )
                self.assertEqual(saved.status_code, 200, saved.get_json())
                self.assertTrue(client.get("/api/me/overview").get_json()["leaderboard_private"])

                cleared = client.post(
                    "/api/me/economy-privacy",
                    json={"leaderboard_private": False},
                    headers={"X-CSRF-Token": "test-csrf"},
                )
                self.assertEqual(cleared.status_code, 200, cleared.get_json())
                self.assertFalse(client.get("/api/me/overview").get_json()["leaderboard_private"])
        finally:
            loop.run_until_complete(connection.close())
            loop.close()

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
