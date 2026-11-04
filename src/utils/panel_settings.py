"""Owner-level display settings for the panels posted in the support servers.

The status panel is redrawn from the bot process every 30 seconds while its
toggle is flipped from the staff dashboard, which runs in that same process.
Both halves therefore read one boolean: the flag lives in ``panel_settings`` (a
row per flag) and is mirrored into a small cache here, so a flip shows on the
panel's next refresh and a restart reads the row back. The row is in the
database rather than on disk on purpose — production has no persistent disk.

Only *display* choices belong here. Anything that changes what the bot does is
kept by the feature that reads it.
"""

from __future__ import annotations

from utils import logging

#: The settings table both backends understand; see ``events/startup/database.py``.
TABLE = "panel_settings"

#: Every flag this module owns, with the value used when no row is stored.
DEFAULTS: dict[str, bool] = {"status_panel_translation_card": False}

_cache: dict[str, bool] | None = None
_loaded = False


def _read() -> dict[str, bool]:
    """The cached flags. Never touches the database, so a redraw stays cheap."""
    global _cache
    if _cache is None:
        _cache = dict(DEFAULTS)
    return _cache


def _truthy(value) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


async def load(bot) -> None:
    """Read every flag from the database once, at startup."""
    global _cache, _loaded
    _cache = dict(DEFAULTS)
    _loaded = True
    pool = getattr(bot, "cxn", None)
    if pool is None:
        logging.warning("Panel", "Database unavailable — panel display settings use their defaults.")
        return
    try:
        rows = await pool.fetch(f"SELECT key, value FROM {TABLE}")
    except Exception as exc:
        logging.warning("Panel", f"Could not read panel display settings: {exc}")
        return
    for row in rows:
        key = str(row.get("key") or "")
        if key in DEFAULTS:
            _cache[key] = _truthy(row.get("value"))
    enabled = [key for key, value in _cache.items() if value]
    if enabled:
        logging.info("Panel", f"Panel display settings loaded: {', '.join(enabled)}.")


async def ensure_loaded(bot) -> None:
    """Load on first use, for a process that never ran the startup path."""
    if not _loaded:
        await load(bot)


def snapshot() -> dict[str, bool]:
    return dict(_read())


def show_translation_card() -> bool:
    """Whether the support servers' status panel draws the translation card."""
    return bool(_read()["status_panel_translation_card"])


async def set_flag(key: str, enabled: bool, actor=None, bot=None) -> dict[str, bool]:
    """Store one display flag, then update the cache the panels read.

    The row is written first: if the database refuses the change the cache is
    left alone, so the dashboard never reports a card that would disappear on
    the next restart.
    """
    if key not in DEFAULTS:
        raise ValueError(f"{key} is not a panel display setting.")
    pool = getattr(bot, "cxn", None)
    if pool is None:
        raise RuntimeError("The database is not available.")

    if enabled:
        # Delete-then-insert instead of an upsert: both backends accept those
        # two statements, and only one owner can flip a switch at a time.
        await pool.execute(f"DELETE FROM {TABLE} WHERE key = $1", key)
        await pool.execute(f"INSERT INTO {TABLE} (key, value) VALUES ($1, $2)", key, "1")
    else:
        await pool.execute(f"DELETE FROM {TABLE} WHERE key = $1", key)

    _read()[key] = bool(enabled)
    logging.info("Panel", f"{key} turned {'on' if enabled else 'off'} by {actor}.")
    return snapshot()


async def set_translation_card(enabled: bool, actor=None, bot=None) -> dict[str, bool]:
    """Show or hide the translation card on the support servers' status panel."""
    return await set_flag("status_panel_translation_card", enabled, actor, bot)
