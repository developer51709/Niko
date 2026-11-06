"""The database child and the bot-side client that talks to it.

The child is the only process that owns a pool.  These tests run its real
aiohttp application in-process: once over the legacy SQLite backend (the
supported legacy path) and once over an in-memory stand-in for MongoDB (the
JSON document path), so no external database is needed.
"""

from __future__ import annotations

import asyncio
import time

import aiohttp
import aiosqlite
import pytest
from aiohttp import web

import db_child
from database import SQLitePool
from database.remote import DatabaseRequestError, DatabaseRoute, RemotePool


async def _serve(app: web.Application):
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = int(site._server.sockets[0].getsockname()[1])
    return runner, port


def _result(**fields):
    class _Result:
        pass

    result = _Result()
    for key, value in {
        "matched_count": 0,
        "modified_count": 0,
        "upserted_id": None,
        "deleted_count": 0,
        "inserted_id": None,
        **fields,
    }.items():
        setattr(result, key, value)
    return result


class _FakeCursor:
    def __init__(self, documents):
        self._documents = list(documents)

    def sort(self, keys):
        for key, direction in reversed(list(keys)):
            self._documents.sort(
                key=lambda document: document.get(key) or 0, reverse=int(direction) < 0
            )
        return self

    def skip(self, count):
        self._documents = self._documents[int(count):]
        return self

    def limit(self, count):
        self._documents = self._documents[: int(count)]
        return self

    async def to_list(self, length=None):
        return [dict(document) for document in self._documents]


class _FakeCollection:
    """The motor subset the child and the client proxy use."""

    def __init__(self):
        self.documents: dict = {}

    @staticmethod
    def _matches(document: dict, filter_doc: dict | None) -> bool:
        return all(
            document.get(key) == value for key, value in (filter_doc or {}).items()
        )

    @staticmethod
    def _project(document: dict, projection) -> dict:
        if not projection:
            return dict(document)
        return {key: document.get(key) for key in projection if key in document}

    def find(self, filter_doc=None, projection=None):
        return _FakeCursor(
            [
                self._project(document, projection)
                for document in self.documents.values()
                if self._matches(document, filter_doc)
            ]
        )

    async def find_one(self, filter_doc=None, projection=None):
        for document in self.documents.values():
            if self._matches(document, filter_doc):
                return self._project(document, projection)
        return None

    async def insert_one(self, document):
        self.documents[document["_id"]] = dict(document)
        return _result(inserted_id=document["_id"])

    async def replace_one(self, filter_doc, replacement, upsert=False):
        key = filter_doc["_id"]
        existed = key in self.documents
        if not existed and not upsert:
            return _result()
        self.documents[key] = {"_id": key, **replacement}
        return _result(
            matched_count=1 if existed else 0,
            modified_count=1 if existed else 0,
            upserted_id=None if existed else key,
        )

    async def update_one(self, filter_doc, update, upsert=False):
        for document in self.documents.values():
            if not self._matches(document, filter_doc):
                continue
            for key, value in (update.get("$set") or {}).items():
                document[key] = value
            for key, value in (update.get("$inc") or {}).items():
                document[key] = int(document.get(key) or 0) + int(value)
            return _result(matched_count=1, modified_count=1)
        return _result()

    async def delete_one(self, filter_doc):
        for key, document in list(self.documents.items()):
            if self._matches(document, filter_doc):
                del self.documents[key]
                return _result(deleted_count=1)
        return _result()

    async def delete_many(self, filter_doc):
        keys = [
            key
            for key, document in self.documents.items()
            if self._matches(document, filter_doc)
        ]
        for key in keys:
            del self.documents[key]
        return _result(deleted_count=len(keys))

    async def count_documents(self, filter_doc):
        return sum(
            1 for document in self.documents.values() if self._matches(document, filter_doc)
        )

    async def create_index(self, keys, **options):
        return str(options.get("name") or "index")


class _FakeDatabase:
    def __init__(self, name: str, store: dict):
        self.name = name
        self._store = store

    def __getitem__(self, name: str) -> _FakeCollection:
        return self._store.setdefault(f"{self.name}.{name}", _FakeCollection())


class _FakeClient:
    def __init__(self, store: dict):
        self._store = store

    def __getitem__(self, name: str) -> _FakeDatabase:
        return _FakeDatabase(name, self._store)


class _FakeMongoPool:
    db_type = "mongodb"

    def __init__(self):
        self._store: dict = {}
        self.client = _FakeClient(self._store)

    def collection(self, name: str) -> _FakeCollection:
        return self.client["discord_bot"][name]


def test_the_child_heartbeats_while_the_pool_is_still_connecting(monkeypatch):
    """A cold MongoDB connect must not look like a hung child to the supervisor."""
    beats: list[float] = []
    events: list[str] = []

    class Reporter:
        def heartbeat(self) -> bool:
            beats.append(time.monotonic())
            return True

        def send(self, event, **fields):
            events.append(event)

    async def slow_pool(_path):
        await asyncio.sleep(0.15)
        raise RuntimeError("database is not reachable")

    monkeypatch.setenv(db_child.TOKEN_ENV, "test-token")
    monkeypatch.setattr(db_child.database, "create_pool", slow_pool)
    monkeypatch.setattr(db_child.bot_logging, "error", lambda *args, **kwargs: None)

    original = db_child._heartbeat_loop

    async def fast_heartbeat(reporter, interval=3.0):
        await original(reporter, interval=0.01)

    monkeypatch.setattr(db_child, "_heartbeat_loop", fast_heartbeat)

    assert asyncio.run(db_child._serve(Reporter())) == 1
    assert "readiness_failed" in events
    assert beats, "the child sent no heartbeat while create_pool was pending"


def test_legacy_sql_round_trips_through_the_database_child(tmp_path):
    async def scenario():
        connection = await aiosqlite.connect(tmp_path / "database.db")
        pool = SQLitePool(connection)
        await pool.execute(
            "CREATE TABLE settings (guild_id INTEGER PRIMARY KEY, roles TEXT, name TEXT)"
        )
        app = db_child.create_app(pool, "secret")
        runner, port = await _serve(app)
        remote = RemotePool(DatabaseRoute(port), "secret", "sqlite")
        try:
            await remote.execute(
                "INSERT INTO settings (guild_id, roles, name) VALUES ($1, $2, $3)",
                42,
                ["admin"],
                "Niko",
            )
            row = await remote.fetchrow(
                "SELECT guild_id, roles, name FROM settings WHERE guild_id = $1", 42
            )
            assert row is not None
            assert row["guild_id"] == 42
            # Row semantics survive the hop: JSON columns are parsed on access.
            assert row["roles"] == ["admin"]
            assert await remote.fetchval("SELECT name FROM settings WHERE guild_id = $1", 42) == "Niko"
            rows = await remote.fetch("SELECT guild_id FROM settings")
            assert [item["guild_id"] for item in rows] == [42]
            assert await remote.ping() == {"ok": True, "backend": "sqlite"}

            # The legacy child still refuses direct collection access on SQLite,
            # and the document API explains why instead of pretending to work.
            with pytest.raises(RuntimeError):
                remote.collection("settings")
            with pytest.raises(DatabaseRequestError) as excinfo:
                await remote.documents("settings").read()
            assert "MongoDB" in str(excinfo.value)

            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://127.0.0.1:{port}/db/health") as response:
                    assert response.status == 401
                async with session.get(
                    f"http://127.0.0.1:{port}/db/health",
                    headers={"X-Internal-Token": "wrong"},
                ) as response:
                    assert response.status == 401
        finally:
            await remote.close()
            await runner.cleanup()
            await connection.close()

    asyncio.run(scenario())


def test_json_documents_are_read_and_written_through_the_child():
    async def scenario():
        app = db_child.create_app(_FakeMongoPool(), "secret", base_database="discord_bot")
        runner, port = await _serve(app)
        remote = RemotePool(DatabaseRoute(port), "secret", "mongodb")
        try:
            documents = remote.documents("onboarding")
            created = await documents.write(
                {"_id": "g1", "welcome": "hi", "roles": ["admin"]}
            )
            assert created == {"id": "g1", "created": True}
            assert await documents.read_one({"_id": "g1"}) == {
                "_id": "g1",
                "welcome": "hi",
                "roles": ["admin"],
            }
            assert await documents.count() == 1

            replaced = await documents.write({"_id": "g1", "welcome": "hello"})
            assert replaced["created"] is False
            assert (await documents.read_one({"_id": "g1"}))["welcome"] == "hello"

            await documents.update({"_id": "g1"}, {"$inc": {"visits": 1}})
            assert (await documents.read_one({"_id": "g1"}))["visits"] == 1
            assert [doc["_id"] for doc in await documents.read(sort=[["_id", 1]])] == ["g1"]

            assert await documents.delete({"_id": "g1"}) == 1
            assert await documents.count() == 0

            # The proxy keeps the native-motor surface working over the hop.
            collection = remote.collection("onboarding")
            await collection.insert_one({"_id": "g2", "welcome": "hey"})
            assert (await collection.find_one({"_id": "g2"}))["welcome"] == "hey"
            assert [doc["_id"] async for doc in collection.find({})] == ["g2"]
            assert await collection.count_documents({}) == 1

            # A second database on the same cluster is reachable by name, and
            # nothing outside the managed prefix is.
            music = remote.database("discord_bot_music")
            await music.documents("music_playlists").write({"_id": "u1", "name": "mix"})
            assert await music.documents("music_playlists").count() == 1
            with pytest.raises(DatabaseRequestError):
                await remote.database("someone_elses_db").documents("x").count()
        finally:
            await remote.close()
            await runner.cleanup()

    asyncio.run(scenario())
