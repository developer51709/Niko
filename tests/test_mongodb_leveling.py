"""Regression tests for MongoDB-backed leveling persistence."""

import asyncio
import sys
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()