"""Database-backed owner key for the remote MCP server.

The key is created from the MCP Server staff page, not from an environment
variable. Only a salted PBKDF2-HMAC-SHA256 digest is stored, so a database
read cannot recover the bearer token. Rotating the key replaces the single
owner row; the MCP endpoint checks the row on every request, so the new key is
active immediately without restarting the bot.

The primary bot database is used when the live bot is available. A local
SQLite file is the development/test fallback, matching the error-report store.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import os
import secrets
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Any

#: A prefix makes the key recognisable in logs and lets the staff page show a
#: short identifier without storing anything that can recreate the key.
KEY_PREFIX = "niko_mcp_"
KEY_ID = "owner"

#: PBKDF2 cost. The key itself has 256 bits of entropy from ``secrets``; the KDF
#: makes a leaked hash expensive to test against guessed or reused tokens.
PBKDF2_ITERATIONS = 210_000
ALGORITHM = "pbkdf2_hmac_sha256"

TABLE = "mcp_api_key"
LOCAL_PATH = os.path.join("data", "mcp_keys.db")

_CREATE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE} (
    id              TEXT PRIMARY KEY,
    key_prefix      TEXT NOT NULL,
    key_hash        TEXT NOT NULL,
    salt            TEXT NOT NULL,
    iterations      INTEGER NOT NULL,
    created_at      TEXT NOT NULL,
    created_by      TEXT,
    created_by_name TEXT,
    last_used_at    TEXT
)
"""

_LOCAL_LOCK = threading.Lock()
_LOCAL_READY = False


def generate_key() -> str:
    """Return a new 256-bit owner key in the documented prefix format."""
    return KEY_PREFIX + secrets.token_urlsafe(32)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _hash(raw_key: str, salt: str, iterations: int) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        raw_key.encode("utf-8"),
        bytes.fromhex(salt),
        int(iterations),
    ).hex()


def _display_prefix(raw_key: str) -> str:
    return raw_key[: len(KEY_PREFIX) + 8]


def _value(row: Any, key: str, default=None):
    try:
        return row[key]
    except (KeyError, TypeError, IndexError):
        return default


def _public(row: Any | None) -> dict:
    """Return display metadata without any material that can verify the key."""
    if row is None:
        return {
            "configured": False,
            "key_prefix": None,
            "created_at": None,
            "created_by": None,
            "created_by_name": None,
            "last_used_at": None,
            "algorithm": ALGORITHM,
            "iterations": PBKDF2_ITERATIONS,
        }
    return {
        "configured": True,
        "key_prefix": str(_value(row, "key_prefix") or ""),
        "created_at": _value(row, "created_at"),
        "created_by": _value(row, "created_by"),
        "created_by_name": _value(row, "created_by_name"),
        "last_used_at": _value(row, "last_used_at"),
        "algorithm": ALGORITHM,
        "iterations": int(_value(row, "iterations") or PBKDF2_ITERATIONS),
    }


def empty_info() -> dict:
    """The unconfigured shape returned to the page and status tools."""
    return _public(None)


def _generated_row(created_by: str | None, created_by_name: str | None) -> tuple[str, dict]:
    raw_key = generate_key()
    salt = secrets.token_hex(16)
    now = _now()
    row = {
        "id": KEY_ID,
        "key_prefix": _display_prefix(raw_key),
        "key_hash": _hash(raw_key, salt, PBKDF2_ITERATIONS),
        "salt": salt,
        "iterations": PBKDF2_ITERATIONS,
        "created_at": now,
        "created_by": (created_by or None),
        "created_by_name": (created_by_name or None),
        "last_used_at": None,
    }
    return raw_key, row


def _local_connect() -> sqlite3.Connection:
    directory = os.path.dirname(LOCAL_PATH)
    if directory:
        os.makedirs(directory, exist_ok=True)
    connection = sqlite3.connect(LOCAL_PATH, timeout=5)
    connection.row_factory = sqlite3.Row
    return connection


def _ensure_local() -> None:
    global _LOCAL_READY
    with _LOCAL_LOCK:
        if _LOCAL_READY:
            return
        with _local_connect() as connection:
            connection.execute(_CREATE_SQL)
        _LOCAL_READY = True


def local_info() -> dict:
    _ensure_local()
    with _local_connect() as connection:
        row = connection.execute(
            f"SELECT key_prefix, created_at, created_by, created_by_name, last_used_at, iterations "
            f"FROM {TABLE} WHERE id = ?",
            (KEY_ID,),
        ).fetchone()
    return _public(row)


def local_rotate(created_by: str | None = None, created_by_name: str | None = None) -> dict:
    _ensure_local()
    raw_key, row = _generated_row(created_by, created_by_name)
    with _local_connect() as connection:
        connection.execute(
            f"INSERT OR REPLACE INTO {TABLE} "
            "(id, key_prefix, key_hash, salt, iterations, created_at, created_by, created_by_name, last_used_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                row["id"], row["key_prefix"], row["key_hash"], row["salt"],
                row["iterations"], row["created_at"], row["created_by"],
                row["created_by_name"], row["last_used_at"],
            ),
        )
    return {"key": raw_key, **_public(row)}


def local_verify(raw_key: str) -> bool:
    if not raw_key:
        return False
    _ensure_local()
    with _local_connect() as connection:
        row = connection.execute(
            f"SELECT key_hash, salt, iterations FROM {TABLE} WHERE id = ?",
            (KEY_ID,),
        ).fetchone()
        if row is None:
            return False
        expected = str(row["key_hash"] or "")
        actual = _hash(raw_key, str(row["salt"] or ""), int(row["iterations"] or PBKDF2_ITERATIONS))
        if not hmac.compare_digest(actual, expected):
            return False
        try:
            connection.execute(
                f"UPDATE {TABLE} SET last_used_at = ? WHERE id = ?",
                (_now(), KEY_ID),
            )
        except sqlite3.Error:
            pass  # The key is valid; a metadata write must not deny access.
    return True


async def _ensure_pool(bot) -> Any:
    pool = getattr(bot, "cxn", None)
    if pool is None:
        raise RuntimeError("The bot database is not available.")
    await pool.execute(_CREATE_SQL)
    return pool


async def info(bot=None) -> dict:
    if bot is None:
        return local_info()
    pool = await _ensure_pool(bot)
    row = await pool.fetchrow(
        f"SELECT key_prefix, created_at, created_by, created_by_name, last_used_at, iterations "
        f"FROM {TABLE} WHERE id = $1",
        KEY_ID,
    )
    return _public(row)


async def rotate(
    created_by: str | None = None,
    created_by_name: str | None = None,
    bot=None,
) -> dict:
    if bot is None:
        return local_rotate(created_by, created_by_name)
    pool = await _ensure_pool(bot)
    # Keep the KDF off the Discord event loop; a rotation is rare but should
    # never stall the gateway while the owner clicks the button.
    raw_key, row = await asyncio.to_thread(_generated_row, created_by, created_by_name)
    await pool.execute(
        f"INSERT OR REPLACE INTO {TABLE} "
        "(id, key_prefix, key_hash, salt, iterations, created_at, created_by, created_by_name, last_used_at) "
        "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
        row["id"], row["key_prefix"], row["key_hash"], row["salt"],
        row["iterations"], row["created_at"], row["created_by"],
        row["created_by_name"], row["last_used_at"],
    )
    return {"key": raw_key, **_public(row)}


async def verify(raw_key: str, bot=None) -> bool:
    if not raw_key:
        return False
    if bot is None:
        return local_verify(raw_key)
    pool = await _ensure_pool(bot)
    row = await pool.fetchrow(
        f"SELECT key_hash, salt, iterations FROM {TABLE} WHERE id = $1",
        KEY_ID,
    )
    if row is None:
        return False
    expected = str(_value(row, "key_hash") or "")
    salt = str(_value(row, "salt") or "")
    iterations = int(_value(row, "iterations") or PBKDF2_ITERATIONS)
    actual = await asyncio.to_thread(_hash, raw_key, salt, iterations)
    if not hmac.compare_digest(actual, expected):
        return False
    try:
        await pool.execute(
            f"UPDATE {TABLE} SET last_used_at = $1 WHERE id = $2",
            _now(),
            KEY_ID,
        )
    except Exception:
        # The key is valid; a metadata write must not deny access.
        pass
    return True


async def revoke(bot=None) -> bool:
    if bot is None:
        _ensure_local()
        with _local_connect() as connection:
            cursor = connection.execute(f"DELETE FROM {TABLE} WHERE id = ?", (KEY_ID,))
            return cursor.rowcount > 0
    pool = await _ensure_pool(bot)
    await pool.execute(f"DELETE FROM {TABLE} WHERE id = $1", KEY_ID)
    return True
