"""Database-backed guild prefix configuration."""

import json

import database

DEFAULT_PREFIXES = ["."]


def _pool(pool=None):
    return pool or database._shared_pool


def _decode_prefixes(value):
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, ValueError):
            return DEFAULT_PREFIXES.copy()
    if isinstance(value, list) and all(isinstance(prefix, str) for prefix in value):
        return value
    return DEFAULT_PREFIXES.copy()


async def get_prefixes(guild_id: int, pool=None) -> list[str]:
    """Return configured prefixes, falling back to the default prefix."""
    pool = _pool(pool)
    if pool is None:
        return DEFAULT_PREFIXES.copy()
    row = await pool.fetchrow(
        "SELECT prefixes FROM prefix_config WHERE guild_id = $1",
        int(guild_id),
    )
    return _decode_prefixes(row.get("prefixes")) if row else DEFAULT_PREFIXES.copy()


async def set_prefixes(guild_id: int, prefixes: list[str], pool=None) -> list[str]:
    """Replace a guild's configured prefixes and return the stored list."""
    pool = _pool(pool)
    cleaned = list(dict.fromkeys(prefix for prefix in prefixes if isinstance(prefix, str)))
    if pool is None:
        raise RuntimeError("The primary database is unavailable.")
    await pool.execute(
        "INSERT OR REPLACE INTO prefix_config (guild_id, prefixes) VALUES ($1, $2)",
        int(guild_id),
        cleaned,
    )
    return cleaned


async def add_prefix(guild_id: int, prefix: str, pool=None) -> list[str]:
    prefixes = await get_prefixes(guild_id, pool)
    if prefix not in prefixes:
        prefixes.append(prefix)
    return await set_prefixes(guild_id, prefixes, pool)


async def remove_prefix(guild_id: int, prefix: str, pool=None) -> list[str]:
    prefixes = await get_prefixes(guild_id, pool)
    if prefix in prefixes:
        prefixes.remove(prefix)
    return await set_prefixes(guild_id, prefixes, pool)


async def reset_prefixes(guild_id: int, pool=None) -> list[str]:
    return await set_prefixes(guild_id, DEFAULT_PREFIXES.copy(), pool)


async def dynamic_prefix(bot, message):
    """Async command-prefix callable used by discord.py."""
    if not message.guild:
        return DEFAULT_PREFIXES.copy()
    return await get_prefixes(message.guild.id, getattr(bot, "cxn", None))
