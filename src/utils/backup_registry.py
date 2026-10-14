"""Durable storage for owner-registered standby proxy instances.

The registry is deliberately MongoDB-only: local SQLite files disappear on
stateless web-service restarts and would make standby registration unreliable.
"""

from __future__ import annotations


_COLLECTION = "backup_instances"


def _collection(bot):
    pool = getattr(bot, "cxn", None)
    if pool is None or getattr(pool, "db_type", None) != "mongodb" or not hasattr(pool, "collection"):
        raise RuntimeError(
            "Standby registration requires the shared MongoDB database (MONGODB_URL); "
            "local SQLite storage is not durable on Render web services."
        )
    return pool.collection(_COLLECTION)


async def init_backup_registry(bot):
    """Ensure unique standby URLs and return all persisted registry entries."""
    collection = _collection(bot)
    # Keep the established index definition. Existing deployments have this
    # named unique index on `url`; changing its key to url_key makes MongoDB
    # reject startup with IndexKeySpecsConflict.
    await collection.create_index("url", unique=True, name="backup_instances_url_unique")
    return await list_backups(bot)


async def list_backups(bot):
    """Return public registry fields from the durable shared collection."""
    collection = _collection(bot)
    cursor = collection.find({}, {"_id": 0, "id": 1, "name": 1, "url": 1, "created_at": 1})
    return await cursor.sort("created_at", 1).to_list(length=None)


async def add_backup(bot, item: dict):
    """Atomically insert a verified backup and return the refreshed registry."""
    collection = _collection(bot)
    document = dict(item)
    document["_id"] = document["id"]
    try:
        await collection.insert_one(document)
    except Exception as exc:
        # Avoid coupling callers to a driver exception type; only translate
        # duplicate-key failures and preserve operational errors as failures.
        if getattr(exc, "code", None) == 11000:
            raise ValueError("This backup URL is already registered.") from exc
        raise
    return await list_backups(bot)


async def remove_backup(bot, backup_id: str):
    """Remove one standby by its stable id and return the updated registry."""
    collection = _collection(bot)
    result = await collection.delete_one({"_id": backup_id})
    if result.deleted_count == 0:
        raise KeyError(backup_id)
    return await list_backups(bot)
