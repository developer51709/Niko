"""Regression tests for MongoDB-backed leveling persistence."""

import asyncio
import sys
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from database import MongoPool


class FakeCollection:
    def __init__(self):
        self.deleted_filters = []
        self.replacements = []

    async def delete_many(self, filter_dict):
        self.deleted_filters.append(filter_dict)

    async def replace_one(self, filter_dict, document, upsert=False):
        self.replacements.append((filter_dict, document, upsert))


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


def test_compound_level_lookup_filters_by_guild_and_user():
    pool, _ = make_pool()

    filter_dict = pool._build_mongo_filter(
        "guild_id = $1 AND user_id = $2",
        (123, 456),
    )

    assert filter_dict == {"guild_id": 123, "user_id": 456}


def test_level_document_id_is_scoped_to_guild_and_user():
    pool, _ = make_pool()

    assert pool._document_id(
        "levels",
        {"guild_id": 123, "user_id": 456},
    ) == "123_456"


def test_level_save_replaces_legacy_user_only_key():
    pool, database = make_pool()

    asyncio.run(pool.execute(
        "INSERT OR REPLACE INTO levels "
        "(guild_id, user_id, xp, level) VALUES ($1, $2, $3, $4)",
        123, 456, 0, 7,
    ))

    collection = database["levels"]
    assert collection.deleted_filters == [{
        "guild_id": 123,
        "user_id": 456,
        "_id": {"$ne": "123_456"},
    }]
    assert collection.replacements == [(
        {"_id": "123_456"},
        {
            "guild_id": 123,
            "user_id": 456,
            "xp": 0,
            "level": 7,
            "_id": "123_456",
        },
        True,
    )]