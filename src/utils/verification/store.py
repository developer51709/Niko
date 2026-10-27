"""Storage for web verification challenges.

The bot hands a member a link; the match happens in the browser, which is a
different thread (and, after a failover, a different process) from the one that
created the link. The challenge therefore lives in the database, not in memory:
the token is an opaque random string, and only the row behind it knows the
answer, the attempt count, and when it expires.

A row is single-use. It is deleted the moment it is answered correctly, so a
token cannot be replayed to re-run the role changes.
"""

import secrets
import time

COLLECTION = "verification_challenges"

TABLE = "verification_challenges"

# Long enough to switch to a browser and read a captcha, short enough that a
# leaked link is not a standing invitation.
DEFAULT_TTL_SECONDS = 30 * 60

# The same three attempts the DM challenge gives before the member fails.
MAX_ATTEMPTS = 3


class VerificationUnavailable(RuntimeError):
    """The bot database is not reachable, so no challenge can be checked."""


def _pool(pool):
    if pool is None:
        raise VerificationUnavailable("The bot database is unavailable.")
    return pool


def _is_mongo(pool) -> bool:
    return getattr(pool, "db_type", None) == "mongodb" and hasattr(pool, "collection")


def new_token() -> str:
    """An unguessable handle for one challenge."""
    return secrets.token_urlsafe(32)


async def create(pool, guild_id: int, user_id: int, code: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> dict:
    """Store a challenge and return the record, including its token."""
    pool = _pool(pool)
    now = time.time()
    record = {
        "token": new_token(),
        "guild_id": int(guild_id),
        "user_id": int(user_id),
        "code": str(code),
        "attempts": 0,
        "created_at": now,
        "expires_at": now + max(60, int(ttl_seconds)),
    }
    # One live challenge per member: asking for a new link supersedes the old
    # one instead of leaving several valid links in old ephemeral messages.
    await _delete_for_user(pool, user_id)
    if _is_mongo(pool):
        document = {**record, "_id": record["token"]}
        await pool.collection(COLLECTION).insert_one(document)
    else:
        await pool.execute(
            f"INSERT INTO {TABLE} (token, guild_id, user_id, code, attempts, created_at, expires_at) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7)",
            record["token"], record["guild_id"], record["user_id"],
            record["code"], record["attempts"], record["created_at"], record["expires_at"],
        )
    return record


async def get(pool, token: str) -> dict | None:
    """The live challenge behind a token, or ``None`` if it is gone or expired."""
    pool = _pool(pool)
    if not isinstance(token, str) or not token:
        return None
    if _is_mongo(pool):
        document = await pool.collection(COLLECTION).find_one({"_id": token})
        record = dict(document) if document else None
    else:
        row = await pool.fetchrow(f"SELECT * FROM {TABLE} WHERE token = $1", token)
        record = dict(row) if row is not None else None
    if not record:
        return None
    if float(record.get("expires_at") or 0) <= time.time():
        await consume(pool, token)
        return None
    record.pop("_id", None)
    return record


async def record_failure(pool, token: str, new_code: str) -> int:
    """Count one wrong answer, rotate the code, and return the new attempt count."""
    pool = _pool(pool)
    if _is_mongo(pool):
        await pool.collection(COLLECTION).update_one(
            {"_id": token},
            {"$inc": {"attempts": 1}, "$set": {"code": new_code}},
        )
        document = await pool.collection(COLLECTION).find_one({"_id": token})
        return int((document or {}).get("attempts") or 0)
    await pool.execute(
        f"UPDATE {TABLE} SET attempts = attempts + 1, code = $1 WHERE token = $2",
        new_code, token,
    )
    attempts = await pool.fetchval(f"SELECT attempts FROM {TABLE} WHERE token = $1", token)
    return int(attempts or 0)


async def consume(pool, token: str) -> None:
    """Delete a challenge, whether it was answered, expired, or abandoned."""
    pool = _pool(pool)
    if _is_mongo(pool):
        await pool.collection(COLLECTION).delete_one({"_id": token})
    else:
        await pool.execute(f"DELETE FROM {TABLE} WHERE token = $1", token)


async def _delete_for_user(pool, user_id: int) -> None:
    if _is_mongo(pool):
        await pool.collection(COLLECTION).delete_many({"user_id": int(user_id)})
    else:
        await pool.execute(f"DELETE FROM {TABLE} WHERE user_id = $1", int(user_id))


async def purge_expired(pool) -> int:
    """Drop rows nobody can use any more. Safe to call at any time."""
    pool = _pool(pool)
    now = time.time()
    if _is_mongo(pool):
        result = await pool.collection(COLLECTION).delete_many({"expires_at": {"$lt": now}})
        return int(getattr(result, "deleted_count", 0) or 0)
    before = await pool.fetchval(f"SELECT COUNT(*) FROM {TABLE} WHERE expires_at < $1", now)
    await pool.execute(f"DELETE FROM {TABLE} WHERE expires_at < $1", now)
    return int(before or 0)
