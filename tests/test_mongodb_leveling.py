"""Regression tests for MongoDB-backed leveling persistence."""

import asyncio
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from database import MongoPool


class FakeCursor:
    def __init__(self, rows=None):
        self.rows = rows or []

    async def to_list(self, length=None):
        return list(self.rows)


class FakeCollection:
    def __init__(self):
        self.deleted_filters = []
        self.replacements = []
        self.find_filters = []
        self.documents = {}

    def find(self, filter_dict, projection=None):
        self.find_filters.append(filter_dict)
        return FakeCursor()

    async def delete_many(self, filter_dict):
        self.deleted_filters.append(filter_dict)

    async def replace_one(self, filter_dict, document, upsert=False):
        self.replacements.append((filter_dict, document, upsert))
        if upsert:
            self.documents[filter_dict["_id"]] = document


class FakeDatabase(dict):
    def __getitem__(self, collection_name):
        return self.setdefault(collection_name, FakeCollection())


class FakeClient:
    def __init__(self):
        self.database = FakeDatabase()

    def __getitem__(self, database_name):
        return self.database


def make_pool():
    client = FakeClient()
    return MongoPool(client, "test"), client.database


class SeededCollection(FakeCollection):
    """FakeCollection that also serves the documents it holds."""

    def __init__(self, docs=None):
        super().__init__()
        self.documents = {doc.get("_id"): doc for doc in docs or []}

    def find(self, filter_dict, projection=None):
        self.find_filters.append(filter_dict)
        doc = self.documents.get(filter_dict.get("_id"))
        return FakeCursor([doc] if doc else [])


class SingleRowCxn:
    """Stand-in for the bot pool that always returns one prepared config row."""

    def __init__(self, row):
        self.row = row

    async def fetchrow(self, _query, *_args):
        return self.row


def level_config_row(level_roles):
    return {
        "_id": 555,
        "guild_id": 555,
        "xp_enabled": 1,
        "xp_multiplier": 1.0,
        "xp_cooldown": 0,
        "level_up_channel": None,
        "level_up_message": None,
        "level_roles": level_roles,
        "xp_excluded_channels": json.dumps([]),
        "xp_vc_enabled": 0,
    }


def read_leveling_cfg(row):
    """Run the cog's own config read against a prepared row."""
    from cogs.leveling.cog import Leveling

    cog = object.__new__(Leveling)
    cog.bot = SimpleNamespace(cxn=SingleRowCxn(row))
    return asyncio.run(cog._guild_cfg(555))


class MongoLevelingTests(unittest.TestCase):
    def test_compound_level_lookup_filters_by_guild_and_user(self):
        pool, _ = make_pool()

        # Exercise actual SELECT translation rather than removed internal
        # helpers, asserting the resulting native query uses the compound key.
        collection = pool.collection("levels")
        asyncio.run(pool.fetch("SELECT * FROM levels WHERE guild_id = $1 AND user_id = $2", 123, 456))
        self.assertEqual(collection.find_filters, [{"_id": "123_456"}])

    def test_level_save_uses_guild_and_user_composite_document_id(self):
        pool, database = make_pool()

        asyncio.run(pool.execute(
            "INSERT OR REPLACE INTO levels "
            "(guild_id, user_id, xp, level) VALUES ($1, $2, $3, $4)",
            123, 456, 0, 7,
        ))

        self.assertEqual(database["levels"].replacements, [(
            {"_id": "123_456"},
            {
                "guild_id": 123,
                "user_id": 456,
                "xp": 0,
                "level": 7,
                "_id": "123_456",
            },
            True,
        )])

    def test_legacy_user_only_key_is_not_deleted_by_current_scoped_write(self):
        pool, database = make_pool()
        collection = database["levels"]
        collection.documents = {"456": {"_id": "456", "guild_id": 999, "user_id": 456}}
        asyncio.run(pool.execute(
            "INSERT OR REPLACE INTO levels "
            "(guild_id, user_id, xp, level) VALUES ($1, $2, $3, $4)",
            123, 456, 0, 7,
        ))
        self.assertIn("456", collection.documents)
        self.assertEqual(collection.documents["456"]["guild_id"], 999)


class MongoLevelConfigReadTests(unittest.TestCase):
    """A saved reward must survive the read that follows it.

    MongoDB decodes the JSON columns on read while SQLite hands them over as
    text. The cog called ``json.loads`` unconditionally, so on MongoDB the
    parsed dict raised, the ``except`` branch set the mapping to ``{}``, and a
    reward added in the dashboard disappeared on the next page load (and never
    granted its role).
    """

    def test_mongo_decodes_the_level_roles_column(self):
        client = FakeClient()
        stored = json.dumps({"5": 123456789012345678})
        client.database["level_config"] = SeededCollection([level_config_row(stored)])
        pool = MongoPool(client, "test")

        row = asyncio.run(pool.fetchrow(
            "SELECT * FROM level_config WHERE guild_id = $1", 555
        ))

        self.assertIsInstance(row["level_roles"], dict)

    def test_mongo_backed_level_roles_are_read_back(self):
        client = FakeClient()
        client.database["level_config"] = SeededCollection([level_config_row(
            json.dumps({"5": 123456789012345678, "10": 987654321098765432})
        )])
        pool = MongoPool(client, "test")
        row = asyncio.run(pool.fetchrow(
            "SELECT * FROM level_config WHERE guild_id = $1", 555
        ))

        cfg = read_leveling_cfg(row)

        self.assertEqual(cfg["level_roles"], {
            "5": 123456789012345678,
            "10": 987654321098765432,
        })

    def test_sqlite_text_level_roles_are_still_parsed(self):
        from database import Row

        row = Row(level_config_row(json.dumps({"7": 123456789012345678})))

        cfg = read_leveling_cfg(row)

        self.assertEqual(cfg["level_roles"], {"7": 123456789012345678})

    def test_unreadable_level_roles_fall_back_to_empty(self):
        cfg = read_leveling_cfg(level_config_row("not json"))

        self.assertEqual(cfg["level_roles"], {})


if __name__ == "__main__":
    unittest.main()