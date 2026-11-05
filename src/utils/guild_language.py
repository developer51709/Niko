"""Per-server language overrides for the bot.

:func:`utils.i18n.get_lang` normally reads ``guild.preferred_locale``, which
Discord only sets when a server enables Community. Servers that never did were
stuck in English with no way to change it, so an explicit choice is stored in
``guild_languages`` and preferred over the Discord locale.

The lookup in ``get_lang`` is synchronous and on a hot path, so the table is
mirrored into a dict at startup and updated whenever a server changes its
language. The database is the source of truth; a restart reads it back.
"""

from __future__ import annotations

import database

from utils import logging
from utils.locales import SUPPORTED_LANGUAGES

#: The settings table both backends understand; see ``events/startup/database.py``.
TABLE = "guild_languages"

#: guild id → language code. Empty means every server follows Discord again.
_cache: dict[int, str] = {}


def _pool(pool=None):
    return pool or database._shared_pool


def _as_guild_id(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def language_for(guild_id) -> str | None:
    """The override stored for a server, or ``None`` when it follows Discord."""
    key = _as_guild_id(guild_id)
    return _cache.get(key) if key is not None else None


def normalize(code) -> str:
    """Lowercase a language code, raising for anything the bot does not ship."""
    value = str(code or "").strip().lower()
    if value not in SUPPORTED_LANGUAGES:
        raise ValueError(f"{value!r} is not a supported language")
    return value


async def load(bot) -> None:
    """Read every override once, at startup, before cogs load."""
    _cache.clear()
    pool = getattr(bot, "cxn", None)
    if pool is None:
        logging.warning("Language", "Database unavailable — servers follow Discord's language.")
        return
    try:
        rows = await pool.fetch(f"SELECT guild_id, language FROM {TABLE}")
    except Exception as exc:
        logging.warning("Language", f"Could not read server languages: {exc}")
        return
    for row in rows:
        code = str(row.get("language") or "").strip().lower()
        guild_id = _as_guild_id(row.get("guild_id"))
        if guild_id is None or code not in SUPPORTED_LANGUAGES:
            continue
        _cache[guild_id] = code
    if _cache:
        logging.info("Language", f"Loaded language overrides for {len(_cache)} server(s).")


async def set_language(guild_id: int, code: str, pool=None) -> str:
    """Store a server's language choice and update the lookup cache.

    The row is written first: a database failure leaves the cache untouched, so
    a reply never promises a language a restart would not keep.
    """
    guild_id = int(guild_id)
    code = normalize(code)
    pool = _pool(pool)
    if pool is None:
        raise RuntimeError("The primary database is unavailable.")
    await pool.execute(
        f"INSERT OR REPLACE INTO {TABLE} (guild_id, language) VALUES ($1, $2)",
        guild_id,
        code,
    )
    _cache[guild_id] = code
    return code


async def clear_language(guild_id: int, pool=None) -> None:
    """Drop a server's override so it follows Discord's locale again."""
    guild_id = int(guild_id)
    pool = _pool(pool)
    if pool is None:
        raise RuntimeError("The primary database is unavailable.")
    await pool.execute(f"DELETE FROM {TABLE} WHERE guild_id = $1", guild_id)
    _cache.pop(guild_id, None)
