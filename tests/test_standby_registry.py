import asyncio
import unittest
from types import SimpleNamespace

from utils.standby_registry import (
    add_standby,
    announced_primary_origin,
    init_standby_registry,
    list_standbys,
    record_primary_origin,
    remove_standby,
)


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows

    def sort(self, field, direction):
        self.rows.sort(key=lambda row: row[field], reverse=direction < 0)
        return self

    async def to_list(self, length=None):
        return list(self.rows)


class DuplicateKeyError(Exception):
    code = 11000


class FakeCollection:
    def __init__(self, existing_index=None):
        self.documents = {}
        self.existing_index = existing_index
        self.created_indexes = []

    async def create_index(self, field, unique=False, name=None):
        requested = (field, unique, name)
        self.created_indexes.append(requested)
        if self.existing_index is not None and self.existing_index != requested:
            raise RuntimeError("Conflicting index definition.")
        self.existing_index = requested
        return name

    def find(self, query, projection):
        return FakeCursor([
            {key: value for key, value in item.items() if projection.get(key)}
            for item in self.documents.values()
        ])

    async def insert_one(self, document):
        if any(item["url"].casefold() == document["url"].casefold() for item in self.documents.values()):
            raise DuplicateKeyError("duplicate URL")
        self.documents[document["_id"]] = dict(document)

    async def delete_one(self, query):
        deleted = self.documents.pop(query["_id"], None)
        return SimpleNamespace(deleted_count=1 if deleted else 0)

    async def update_one(self, query, update, upsert=False):
        document = self.documents.setdefault(query["_id"], {"_id": query["_id"]})
        document.update(update.get("$set", {}))
        return SimpleNamespace(modified_count=1, upserted_id=None)

    async def find_one(self, query, projection=None):
        document = self.documents.get(query["_id"])
        if document is None:
            return None
        if projection:
            return {key: value for key, value in document.items() if projection.get(key)}
        return dict(document)


class FakePool:
    db_type = "mongodb"

    def __init__(self, collection, primary=None):
        self._collections = {"standby_instances": collection}
        if primary is not None:
            self._collections["standby_primary"] = primary

    def collection(self, name):
        if name not in self._collections:
            raise AssertionError(f"Unexpected collection: {name}")
        return self._collections[name]


class StandbyRegistryTests(unittest.TestCase):
    def test_registry_refuses_ephemeral_sqlite_storage(self):
        bot = SimpleNamespace(cxn=SimpleNamespace(db_type="sqlite"))
        with self.assertRaisesRegex(RuntimeError, "requires the shared MongoDB database"):
            asyncio.run(list_standbys(bot))

    def test_registry_uses_existing_unique_url_index(self):
        collection = FakeCollection(existing_index=("url", True, "standby_instances_url_unique"))
        bot = SimpleNamespace(cxn=FakePool(collection))

        async def scenario():
            await init_standby_registry(bot)
            self.assertEqual(
                [("url", True, "standby_instances_url_unique")],
                collection.created_indexes,
            )
            item = {
                "id": "standby-1",
                "name": "east",
                "url": "https://standby.example",
                "created_at": 10,
            }
            await add_standby(bot, item)
            with self.assertRaisesRegex(ValueError, "already registered"):
                await add_standby(bot, {**item, "id": "standby-2"})

        asyncio.run(scenario())

    def test_registry_uses_durable_collection_across_bot_instances(self):
        collection = FakeCollection()
        primary = SimpleNamespace(cxn=FakePool(collection))
        restarted_primary = SimpleNamespace(cxn=FakePool(collection))
        item = {"id": "standby-1", "name": "east", "url": "https://standby.example", "created_at": 10}

        async def scenario():
            await init_standby_registry(primary)
            rows = await add_standby(primary, item)
            self.assertEqual([item], rows)
            self.assertEqual([item], await list_standbys(restarted_primary))
            await remove_standby(restarted_primary, "standby-1")
            self.assertEqual([], await list_standbys(primary))

        asyncio.run(scenario())

    def test_primary_announces_its_origin_for_standby_instances(self):
        instances = FakeCollection()
        announced = FakeCollection()
        bot = SimpleNamespace(cxn=FakePool(instances, announced))

        async def scenario():
            self.assertIsNone(await announced_primary_origin(bot))
            await record_primary_origin(bot, "https://niko.example")
            self.assertEqual("https://niko.example", await announced_primary_origin(bot))
            await record_primary_origin(bot, "https://niko.example:8443")
            self.assertEqual("https://niko.example:8443", await announced_primary_origin(bot))
            # A standby only forwards management to a public HTTPS origin.
            await record_primary_origin(bot, "http://insecure.example")
            self.assertIsNone(await announced_primary_origin(bot))
            # Announcing is not a standby registration.
            self.assertEqual([], await list_standbys(bot))

        asyncio.run(scenario())

    def test_registry_duplicate_url_is_rejected(self):
        bot = SimpleNamespace(cxn=FakePool(FakeCollection()))
        item = {"id": "standby-1", "name": "east", "url": "https://standby.example", "created_at": 10}

        async def scenario():
            await add_standby(bot, item)
            with self.assertRaisesRegex(ValueError, "already registered"):
                await add_standby(bot, {**item, "id": "standby-2"})

        asyncio.run(scenario())


if __name__ == "__main__":
    unittest.main()
