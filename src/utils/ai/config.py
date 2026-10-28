"""Guild AI settings, stored in the bot's shared database.

Previously every read opened a fresh SQLite connection, ran table migrations and
committed an ``INSERT OR IGNORE`` — up to seven times per AI message, on the
event loop — and ignored the pooled connection the rest of the bot uses, so
settings did not survive on MongoDB/Postgres deployments. Reads are now async,
cached per guild, and written once per change.
"""

from __future__ import annotations

import asyncio
import time
from typing import Optional, Union

from utils import logging

DEFAULT_CONFIG = {
    "personality": "cafe",
    "enabled": "True",
    "ai_name": "Niko",
    "ai_actions_experiment": "False",
    "better_context_experiment": "False",
    "multimodal_experiment": "False",
}
_BOOLEAN_FIELDS = {"enabled", "ai_actions_experiment", "better_context_experiment", "multimodal_experiment"}
_PERSONALITIES = {"cafe", "normal"}

#: How long a loaded guild config is trusted before it is read again. Saves
#: update the cache immediately, so a change is visible before this expires.
CACHE_TTL = 60.0

#: Name length the trigger matcher needs to avoid false positives ("niko" is
#: fine, "a" would wake the AI on every message). Kept in sync with the panel
#: and the dashboard.
MIN_AI_NAME_LENGTH = 3

_SELECT_COLUMNS = (
    "guild_id, personality, enabled, ai_name, "
    "ai_actions_experiment, better_context_experiment, multimodal_experiment"
)

_cache: dict[int, dict] = {}
_cache_at: dict[int, float] = {}
_cache_lock = asyncio.Lock()
_table_pool = None


def _pool():
    import database as database_module

    return getattr(database_module, "_shared_pool", None)


async def _ensure_table(pool) -> None:
    """Create the table once per process (MongoDB ignores DDL)."""
    global _table_pool
    if _table_pool is pool:
        return
    await pool.execute(
        "CREATE TABLE IF NOT EXISTS ai_config ("
        " guild_id INTEGER PRIMARY KEY,"
        " personality TEXT NOT NULL DEFAULT 'cafe',"
        " enabled INTEGER NOT NULL DEFAULT 1,"
        " ai_name TEXT NOT NULL DEFAULT 'Niko',"
        " ai_actions_experiment INTEGER NOT NULL DEFAULT 0,"
        " better_context_experiment INTEGER NOT NULL DEFAULT 0,"
        " multimodal_experiment INTEGER NOT NULL DEFAULT 0,"
        " updated_at TEXT NOT NULL DEFAULT (datetime('now'))"
        ")"
    )
    _table_pool = pool


def _as_bool_int(value) -> int:
    return int(value is True or str(value).lower() in {"true", "1", "yes", "on"})


def _row_get(row, name: str, default=None):
    """Read one column without assuming it exists.

    MongoDB is schemaless, so a document written before a column existed (or
    by the bare ``INSERT OR IGNORE ... (guild_id)`` used to create the very
    first row) simply has no such key.  Indexing it raised KeyError, which
    used to abort ``preload_all`` and with it the whole ``cogs.ai`` load.
    """
    try:
        value = row[name]
    except (KeyError, IndexError, TypeError):
        return default
    return default if value is None else value


def _as_flag(value, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"true", "1", "yes", "on"}


def _row_to_config(row) -> dict:
    """Normalise a database row (or dict) into the public config shape.

    Every field falls back to its default, so a partial row reads as an
    unconfigured guild instead of raising.
    """
    personality = _row_get(row, "personality", DEFAULT_CONFIG["personality"])
    if personality not in _PERSONALITIES:
        personality = DEFAULT_CONFIG["personality"]
    return {
        "personality": personality,
        "enabled": "True" if _as_flag(_row_get(row, "enabled"), True) else "False",
        "ai_name": str(_row_get(row, "ai_name", DEFAULT_CONFIG["ai_name"])) or "Niko",
        "ai_actions_experiment": "True" if _as_flag(_row_get(row, "ai_actions_experiment"), False) else "False",
        "better_context_experiment": "True" if _as_flag(_row_get(row, "better_context_experiment"), False) else "False",
        "multimodal_experiment": "True" if _as_flag(_row_get(row, "multimodal_experiment"), False) else "False",
    }


def _cached(guild_id: int) -> Optional[dict]:
    stamp = _cache_at.get(guild_id, 0.0)
    if stamp and time.monotonic() - stamp < CACHE_TTL:
        return _cache.get(guild_id)
    return None


async def load_config(
    guild_id: int,
    key: Optional[str] = None,
    *,
    fresh: bool = False,
) -> Union[dict, str, None]:
    """Return this guild's AI settings, reading the database at most once per TTL."""
    guild_id = int(guild_id)
    if not fresh:
        cached = _cached(guild_id)
        if cached is not None:
            return cached if key is None else cached.get(key)

    async with _cache_lock:
        if not fresh:
            cached = _cached(guild_id)
            if cached is not None:
                return cached if key is None else cached.get(key)
        config = await _read_or_default(guild_id)
        _cache[guild_id] = config
        _cache_at[guild_id] = time.monotonic()
    return config if key is None else config.get(key)


async def _read_or_default(guild_id: int) -> dict:
    pool = _pool()
    if pool is None:
        # No database yet (tests, CLI, very early startup): use the last good
        # copy, else defaults. Never silently disables a guild that had settings.
        return dict(_cache.get(guild_id) or DEFAULT_CONFIG)
    try:
        await _ensure_table(pool)
        row = await pool.fetchrow(
            f"SELECT {_SELECT_COLUMNS} FROM ai_config WHERE guild_id = $1", guild_id
        )
        if row is None:
            # Write the defaults explicitly: on MongoDB the column DEFAULTs do
            # not exist, so a row inserted with only `guild_id` would come back
            # without a personality and every later read failed.
            await pool.execute(
                "INSERT OR IGNORE INTO ai_config (guild_id, personality, enabled,"
                " ai_name, ai_actions_experiment, better_context_experiment,"
                " multimodal_experiment) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                guild_id,
                DEFAULT_CONFIG["personality"],
                _as_bool_int(DEFAULT_CONFIG["enabled"]),
                DEFAULT_CONFIG["ai_name"],
                _as_bool_int(DEFAULT_CONFIG["ai_actions_experiment"]),
                _as_bool_int(DEFAULT_CONFIG["better_context_experiment"]),
                _as_bool_int(DEFAULT_CONFIG["multimodal_experiment"]),
            )
            return dict(DEFAULT_CONFIG)
        return _row_to_config(row)
    except Exception as error:  # noqa: BLE001 - a config read must never break a reply
        logging.error("ai_config", f"Failed to read AI config for guild {guild_id}: {error}")
        return dict(_cache.get(guild_id) or DEFAULT_CONFIG)


async def save_config(
    guild_id: int,
    key: str,
    value: Union[str, bool, int, dict],
) -> dict:
    """Validate and persist one setting, then refresh the cache."""
    if key not in DEFAULT_CONFIG:
        raise ValueError(f"Unsupported AI config key: {key}")
    guild_id = int(guild_id)

    if key in _BOOLEAN_FIELDS:
        value = "True" if _as_bool_int(value) else "False"
    elif key == "personality":
        if value not in _PERSONALITIES:
            raise ValueError("Personality must be cafe or normal.")
    elif key == "ai_name":
        raw = str(value).strip()
        if len(raw) < MIN_AI_NAME_LENGTH:
            raise ValueError(
                f"The AI name needs at least {MIN_AI_NAME_LENGTH} characters."
            )
        value = raw[:32]

    config = dict(await load_config(guild_id, fresh=True))
    config[key] = value

    pool = _pool()
    if pool is None:
        raise RuntimeError("Database pool is not available.")
    await _ensure_table(pool)
    await pool.execute(
        "INSERT OR REPLACE INTO ai_config (guild_id, personality, enabled, ai_name,"
        " ai_actions_experiment, better_context_experiment, multimodal_experiment)"
        " VALUES ($1, $2, $3, $4, $5, $6, $7)",
        guild_id,
        config["personality"] if config["personality"] in _PERSONALITIES else "cafe",
        _as_bool_int(config["enabled"]),
        str(config["ai_name"])[:32] or "Niko",
        _as_bool_int(config["ai_actions_experiment"]),
        _as_bool_int(config["better_context_experiment"]),
        _as_bool_int(config["multimodal_experiment"]),
    )
    _cache[guild_id] = config
    _cache_at[guild_id] = time.monotonic()
    return config


async def preload_all() -> int:
    """Warm the cache for every guild that has settings (startup)."""
    pool = _pool()
    if pool is None:
        return 0
    try:
        await _ensure_table(pool)
        rows = await pool.fetch(f"SELECT {_SELECT_COLUMNS} FROM ai_config")
    except Exception as error:  # noqa: BLE001
        logging.warning("ai_config", f"Could not preload AI settings: {error}")
        return 0
    now = time.monotonic()
    loaded = 0
    for row in rows:
        # One malformed document must not abort warming the rest.
        try:
            guild_id = int(row["guild_id"])
            config = _row_to_config(row)
        except (KeyError, TypeError, ValueError) as error:
            logging.warning("ai_config", f"Skipping malformed AI config row: {error}")
            continue
        _cache[guild_id] = config
        _cache_at[guild_id] = now
        loaded += 1
    return loaded


def invalidate(guild_id: Optional[int] = None) -> None:
    if guild_id is None:
        _cache_at.clear()
        return
    _cache_at.pop(int(guild_id), None)


def cached_config(guild_id: int) -> dict:
    """Cache-only read for code that cannot await (cosmetic personality lookups)."""
    return dict(_cache.get(int(guild_id)) or DEFAULT_CONFIG)


def get_personality(ctx) -> str:
    """The cached personality for a command context.

    Sync on purpose: roleplay flavour text calls this from sync helpers. The
    cache is warmed at startup (`preload_all`) and on every AI config change.
    """
    try:
        if not ctx or not ctx.guild:
            return "normal"
        personality = cached_config(ctx.guild.id).get("personality")
    except Exception:
        return "normal"
    return personality if personality in _PERSONALITIES else "normal"
