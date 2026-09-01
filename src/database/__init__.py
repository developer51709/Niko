import json
import os
import re
from datetime import datetime, timezone
from typing import Optional, Union

import aiosqlite

DATETIME_COLUMNS = {"adopted_at"}
LIST_COLUMNS = {"roles"}


def _convert_query(query: str) -> str:
    return re.sub(r"\$\d+", "?", query)


def _serialize_args(args):
    out = []
    for arg in args:
        if isinstance(arg, list):
            out.append(json.dumps(arg))
        else:
            out.append(arg)
    return out


class Row(dict):
    def __getitem__(self, key):
        value = super().__getitem__(key)
        if key in LIST_COLUMNS:
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except Exception:
                    return []
            return value if value is not None else []
        if key in DATETIME_COLUMNS:
            if isinstance(value, str):
                try:
                    dt = datetime.fromisoformat(value)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt
                except Exception:
                    pass
        return value

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


def _make_row(cursor, raw_row):
    if raw_row is None:
        return None
    columns = [desc[0] for desc in cursor.description]
    return Row(zip(columns, raw_row))


class SQLitePool:
    def __init__(self, db: aiosqlite.Connection):
        self._db = db
        self.db_type = "sqlite"

    async def execute(self, query: str, *args):
        q = _convert_query(query)
        a = _serialize_args(args)
        await self._db.execute(q, a)
        await self._db.commit()

    async def fetchrow(self, query: str, *args):
        q = _convert_query(query)
        a = _serialize_args(args)
        async with self._db.execute(q, a) as cursor:
            raw = await cursor.fetchone()
            return _make_row(cursor, raw)

    async def fetch(self, query: str, *args):
        q = _convert_query(query)
        a = _serialize_args(args)
        async with self._db.execute(q, a) as cursor:
            rows = await cursor.fetchall()
            return [_make_row(cursor, r) for r in rows]

    async def fetchval(self, query: str, *args):
        q = _convert_query(query)
        a = _serialize_args(args)
        async with self._db.execute(q, a) as cursor:
            raw = await cursor.fetchone()
            if raw is None:
                return None
            return raw[0]

    async def fetchone(self, query: str, *args):
        return await self.fetchrow(query, *args)


class MongoPool:
    def __init__(self, client, db_name: str):
        self._client = client
        self._db = client[db_name]
        self.db_type = "mongodb"

    async def execute(self, query: str, *args):
        # MongoDB doesn't support raw SQL execution
        # This method is kept for compatibility but should not be used
        raise NotImplementedError("MongoDB does not support raw SQL execution")

    async def fetchrow(self, query: str, *args):
        # MongoDB specific implementation would go here
        # This is a placeholder for compatibility
        raise NotImplementedError("Use MongoDB specific methods instead")

    async def fetch(self, query: str, *args):
        # MongoDB specific implementation would go here
        raise NotImplementedError("Use MongoDB specific methods instead")

    async def fetchval(self, query: str, *args):
        # MongoDB specific implementation would go here
        raise NotImplementedError("Use MongoDB specific methods instead")

    async def fetchone(self, query: str, *args):
        return await self.fetchrow(query, *args)

    @property
    def client(self):
        return self._client

    @property
    def db(self):
        return self._db


async def create_pool(db_path: str) -> Union[SQLitePool, MongoPool]:
    # Check for MongoDB connection string in environment variables
    mongo_url = os.getenv("MONGODB_URL")
    
    if mongo_url:
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            
            # Extract database name from URL or use default
            db_name = os.getenv("MONGODB_DATABASE", "discord_bot")
            
            client = AsyncIOMotorClient(mongo_url)
            # Test connection
            await client.admin.command('ping')
            
            return MongoPool(client, db_name)
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}. Falling back to SQLite.")
    
    # Default to SQLite
    db = await aiosqlite.connect(db_path)
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return SQLitePool(db)