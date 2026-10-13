"""Regression tests for MongoDB-backed guild blacklist persistence."""

import asyncio
import sys
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

import database
from database import MongoPool
from utils.blacklist_manager import BlacklistManager


class FakeCollection:
    def __init__(self):
        self.documents = {}

    @staticmethod
    def _matches(document, filter_dict):
        for key, expected in filter_dict.items():
            if key == "$or":
                if not any(FakeCollection._matches(document, part) for part in expected):
                    return False
            elif isinstance(expected, dict):
                value = document.get(key)
                if "$ne" in expected and value == expected["$ne"]:
                    return False
                if "$lte" in expected and (value is None or value > expected["$lte"]):
                    return False
                if "$gt" in expected and (value is None or value <= expected["$gt"]):
                    return False
            elif document.get(key) != expected:
                return False
        return True

    async def update_one(self, filter_dict, update, upsert=False):
        key = filter_dict["_id"]
        existing = self.documents.get(key)
        if existing is not None:
            if "$setOnInsert" in update:
                return type("Result", (), {"upserted_id": None})()
            existing.update(update.get("$set", {}))
            return type("Result", (), {"upserted_id": None})()
        if upsert:
            values = update.get("$setOnInsert", update.get("$set", {}))
            self.documents[key] = {"_id": key, **values}
            return type("Result", (), {"upserted_id": key})()
        return type("Result", (), {"upserted_id": None})()

    async def delete_many(self, filter_dict):
        self.documents = {
            key: document
            for key, document in self.documents.items()
            if not self._matches(document, filter_dict)
        }

    async def update_many(self, filter_dict, update):
        for document in self.documents.values():
            if self._matches(document, filter_dict):
                document.update(update.get("$set", {}))

    def find(self, filter_dict, projection=None):
        selected = [
            dict(document)
            for document in self.documents.values()
            if self._matches(document, filter_dict)
        ]
        if projection:
            selected = [
                {key: value for key, value in document.items() if key in projection}
                for document in selected
            ]
        return FakeCursor(selected)


class FakeCursor:
    def __init__(self, documents):
        self.documents = documents

    def sort(self, _ordering):
        return self

    def limit(self, _count):
        return self

    async def to_list(self, length=None):
        return self.documents


class FakeDatabase(dict):
    def __getitem__(self, collection_name):
        return self.setdefault(collection_name, FakeCollection())


class FakeClient:
    def __init__(self):
        self.database = FakeDatabase()

    def __getitem__(self, _database_name):
        return self.database


def test_guild_blacklist_round_trips_through_mongo_pool():
    client = FakeClient()
    pool = MongoPool(client, "test")
    previous_pool = database._shared_pool
    previous_manager = BlacklistManager._instance
    database._shared_pool = pool
    BlacklistManager._instance = None

    async def exercise():
        manager = BlacklistManager()
        assert await manager.load() is None
        assert await manager.add_guild(123456, reason="abuse", added_by=42)

        stored = client.database["blacklist_guilds"].documents[123456]
        assert stored["id"] == 123456
        assert stored["reason"] == "abuse"
        assert stored["added_by"] == 42
        assert stored["status"] == "active"

        # An inactive historical row must be reactivated by a new add while
        # retaining unrelated Mongo document metadata.
        stored["status"] = "inactive"
        stored["audit_marker"] = "keep"
        manager.blacklist["guilds"] = []
        manager._loaded = False
        await manager.load()
        assert not manager.is_guild_blacklisted(123456)
        assert await manager.add_guild(123456, reason="reinstated", added_by=7)
        stored = client.database["blacklist_guilds"].documents[123456]
        assert stored["status"] == "active"
        assert stored["reason"] == "reinstated"
        assert stored["audit_marker"] == "keep"

        manager.blacklist["guilds"] = []
        manager._loaded = False
        await manager.load()
        assert manager.get_guild_entry(123456) == {
            "id": 123456,
            "reason": "reinstated",
            "timestamp": stored["timestamp"],
            "added_by": 7,
            "expires_at": None,
            "status": "active",
        }

        assert await manager.update_guild_reason(123456, "updated")
        assert stored["reason"] == "updated"
        assert await manager.remove_guild(123456)
        assert 123456 not in client.database["blacklist_guilds"].documents

    try:
        asyncio.run(exercise())
    finally:
        database._shared_pool = previous_pool
        BlacklistManager._instance = previous_manager
