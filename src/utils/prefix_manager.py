"""Database-backed guild prefix configuration."""

import inspect
import json
from types import SimpleNamespace

import database

DEFAULT_PREFIXES = ["."]

# Used when nothing else resolves a prefix: an unknown guild, an unreadable
# message, or a prefix callable that raised.
FALLBACK_PREFIX = "."


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


def _prefix_target(target):
    """Return a message-like object a prefix callable can read ``.guild`` from.

    ``command_prefix`` is called with a message by discord.py, so instruction
    text resolves the prefix the same way: a context or interaction lends its
    message, and a bare guild (``on_guild_join``) is wrapped so the callable
    still sees ``.guild``. ``None`` means there is nothing to ask.
    """
    message = getattr(target, "message", None)
    if message is not None:
        return message
    guild = getattr(target, "guild", None)
    if guild is None and hasattr(target, "members"):
        guild = target  # the guild itself, as on_guild_join hands over
    if guild is None:
        return None
    return SimpleNamespace(guild=guild)


async def resolve_prefix(bot, ctx_or_interaction) -> str:
    """Resolve the primary prefix to show in a command's help text.

    ``command_prefix`` may be a string, a list, or a callable - and this bot
    uses the async :func:`dynamic_prefix`, so the result has to be awaited.
    Calling it without awaiting both skipped the guild's configured prefix and
    left a coroutine to be garbage collected ("coroutine 'dynamic_prefix' was
    never awaited"), so every caller goes through here instead.
    """
    raw = getattr(bot, "command_prefix", None)
    if isinstance(raw, str):
        return raw
    if isinstance(raw, (list, tuple)):
        return raw[0] if raw else FALLBACK_PREFIX
    if not callable(raw):
        return FALLBACK_PREFIX

    target = _prefix_target(ctx_or_interaction)
    if target is None:
        return FALLBACK_PREFIX

    try:
        prefixes = raw(bot, target)
        # A sync prefix callable returns the result; an async one returns a
        # coroutine that only resolves the guild's prefix once awaited.
        if inspect.isawaitable(prefixes):
            prefixes = await prefixes
    except Exception:
        return FALLBACK_PREFIX

    if isinstance(prefixes, str):
        return prefixes
    if isinstance(prefixes, (list, tuple)) and prefixes:
        return prefixes[0]
    return FALLBACK_PREFIX
