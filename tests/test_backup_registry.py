import asyncio
import unittest
from types import SimpleNamespace

from utils.backup_registry import add_backup, init_backup_registry, list_backups, remove_backup


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
    def __init__(self):
        self.documents = {}

    async def create_index(self, field, unique=False, name=None):
        return name

    def find(self, query, projection):
        return FakeCursor([
            {key: value for key, value in item.items() if projection.get(key)}
            for item in self.documents.values()
        ])

    async def insert_one(self, document):
        if any(item["url_key"] == document["url_key"] for item in self.documents.values()):
            raise DuplicateKeyError("duplicate URL")
        self.documents[document["_id"]] = dict(document)

    async def delete_one(self, query):
        deleted = self.documents.pop(query["_id"], None)
        return SimpleNamespace(deleted_count=1 if deleted else 0)


class FakePool:
    db_type = "mongodb"

    def __init__(self, collection):
        self._collection = collection

    def collection(self, name):
        if name != "backup_instances":
            raise AssertionError(f"Unexpected collection: {name}")
        return self._collection


class BackupRegistryTests(unittest.TestCase):
    def test_registry_refuses_ephemeral_sqlite_storage(self):
        bot = SimpleNamespace(cxn=SimpleNamespace(db_type="sqlite"))
        with self.assertRaisesRegex(RuntimeError, "requires the shared MongoDB database"):
            asyncio.run(list_backups(bot))

    def test_registry_uses_durable_collection_across_bot_instances(self):
        collection = FakeCollection()
        primary = SimpleNamespace(cxn=FakePool(collection))
        restarted_primary = SimpleNamespace(cxn=FakePool(collection))
        item = {"id": "backup-1", "name": "east", "url": "https://backup.example", "created_at": 10}

        async def scenario():
            await init_backup_registry(primary)
            rows = await add_backup(primary, item)
            self.assertEqual([item], rows)
            self.assertEqual([item], await list_backups(restarted_primary))
            await remove_backup(restarted_primary, "backup-1")
            self.assertEqual([], await list_backups(primary))

        asyncio.run(scenario())

    def test_registry_duplicate_url_is_rejected(self):
        collection = FakeCollection()
        bot = SimpleNamespace(cxn=FakePool(collection))
        item = {"id": "backup-1", "name": "east", "url": "https://backup.example", "created_at": 10}

        async def scenario():
            await add_backup(bot, item)
            with self.assertRaisesRegex(ValueError, "already registered"):
                await add_backup(bot, {**item, "id": "backup-2"})

        asyncio.run(scenario())


if __name__ == "__main__":
    unittest.main()
