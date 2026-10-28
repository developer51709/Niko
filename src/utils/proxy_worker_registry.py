"""Durable registry for optional Discord API proxy workers.

This registry is MongoDB-only: a proxy registration is shared by every instance
and must survive stateless web-service restarts. The routing
switch is stored beside the registrations so a restart cannot silently start
sending Discord traffic through a worker the owner turned off.
"""

from __future__ import annotations

_COLLECTION = "proxy_workers"
_SETTINGS_COLLECTION = "proxy_worker_settings"
_SETTINGS_ID = "settings"


def _collection(bot, name: str = _COLLECTION):
    pool = getattr(bot, "cxn", None)
    if pool is None or getattr(pool, "db_type", None) != "mongodb" or not hasattr(pool, "collection"):
        raise RuntimeError(
            "Discord proxy worker registration requires the shared MongoDB database (MONGODB_URL); "
            "local SQLite storage is not durable on stateless web services."
        )
    return pool.collection(name)


async def init_proxy_worker_registry(bot):
    """Ensure unique worker URLs and return every persisted registration."""
    collection = _collection(bot)
    await collection.create_index("url", unique=True, name="proxy_workers_url_unique")
    return await list_proxy_workers(bot)


async def list_proxy_workers(bot):
    """Return public proxy-worker fields from the durable collection."""
    collection = _collection(bot)
    cursor = collection.find({}, {"_id": 0, "id": 1, "name": 1, "url": 1, "created_at": 1})
    return await cursor.sort("created_at", 1).to_list(length=None)


async def add_proxy_worker(bot, item: dict):
    """Atomically insert a verified worker and return the refreshed registry."""
    collection = _collection(bot)
    document = dict(item)
    document["_id"] = document["id"]
    try:
        await collection.insert_one(document)
    except Exception as exc:
        if getattr(exc, "code", None) == 11000:
            raise ValueError("This proxy worker URL is already registered.") from exc
        raise
    return await list_proxy_workers(bot)


async def remove_proxy_worker(bot, worker_id: str):
    """Remove one worker by id and return the updated registry."""
    collection = _collection(bot)
    result = await collection.delete_one({"_id": worker_id})
    if result.deleted_count == 0:
        raise KeyError(worker_id)
    return await list_proxy_workers(bot)


async def proxy_routing_enabled(bot) -> bool:
    """Whether the owner has switched Discord traffic onto the workers."""
    collection = _collection(bot, _SETTINGS_COLLECTION)
    document = await collection.find_one({"_id": _SETTINGS_ID}, {"enabled": 1})
    return bool(isinstance(document, dict) and document.get("enabled"))


async def set_proxy_routing_enabled(bot, enabled: bool) -> bool:
    """Persist the owner's routing switch."""
    collection = _collection(bot, _SETTINGS_COLLECTION)
    await collection.update_one(
        {"_id": _SETTINGS_ID},
        {"$set": {"enabled": bool(enabled)}},
        upsert=True,
    )
    return bool(enabled)
