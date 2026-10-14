"""Durable registry for owner-registered full-copy standby instances.

The registry is deliberately MongoDB-only: local SQLite files disappear on
stateless web-service restarts and would make standby registration unreliable.
"""

from __future__ import annotations


_COLLECTION = "standby_instances"
# The primary publishes its own public origin here so a standby opened directly
# still knows which instance owns the registry and can forward changes to it.
_PRIMARY_COLLECTION = "standby_primary"
_PRIMARY_ID = "primary"


def _collection(bot, name: str = _COLLECTION):
    pool = getattr(bot, "cxn", None)
    if pool is None or getattr(pool, "db_type", None) != "mongodb" or not hasattr(pool, "collection"):
        raise RuntimeError(
            "Standby registration requires the shared MongoDB database (MONGODB_URL); "
            "local SQLite storage is not durable on Render web services."
        )
    return pool.collection(name)


async def init_standby_registry(bot):
    """Ensure unique standby URLs and return all persisted registry entries."""
    collection = _collection(bot)
    # Preserve the established index definition for existing installations.
    await collection.create_index("url", unique=True, name="standby_instances_url_unique")
    return await list_standbys(bot)


async def list_standbys(bot):
    """Return public registry fields from the durable shared collection."""
    collection = _collection(bot)
    cursor = collection.find({}, {"_id": 0, "id": 1, "name": 1, "url": 1, "created_at": 1})
    return await cursor.sort("created_at", 1).to_list(length=None)


async def add_standby(bot, item: dict):
    """Atomically insert a verified standby and return the refreshed registry."""
    collection = _collection(bot)
    document = dict(item)
    document["_id"] = document["id"]
    try:
        await collection.insert_one(document)
    except Exception as exc:
        if getattr(exc, "code", None) == 11000:
            raise ValueError("This standby URL is already registered.") from exc
        raise
    return await list_standbys(bot)


async def remove_standby(bot, standby_id: str):
    """Remove one standby by its stable id and return the updated registry."""
    collection = _collection(bot)
    result = await collection.delete_one({"_id": standby_id})
    if result.deleted_count == 0:
        raise KeyError(standby_id)
    return await list_standbys(bot)


async def record_primary_origin(bot, url: str) -> bool:
    """Publish the main instance's public origin for standby instances."""
    collection = _collection(bot, _PRIMARY_COLLECTION)
    await collection.update_one({"_id": _PRIMARY_ID}, {"$set": {"url": url}}, upsert=True)
    return True


async def announced_primary_origin(bot) -> str | None:
    """Return the origin the main instance announced, or None when unset."""
    collection = _collection(bot, _PRIMARY_COLLECTION)
    document = await collection.find_one({"_id": _PRIMARY_ID}, {"url": 1})
    if not isinstance(document, dict):
        return None
    url = document.get("url")
    return url if isinstance(url, str) and url.startswith("https://") else None
