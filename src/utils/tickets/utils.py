from __future__ import annotations
from typing import Dict, List, Optional
import json

from .config import TicketConfig

# ── In-memory cache for sync callers (UI __init__ methods) ────────────────
# The cache is populated on first access from the database and kept in sync
# by the async update function.  This lets TicketPanelView.__init__ and
# similar synchronous code paths work without blocking on I/O.

_ticket_configs: Dict[int, TicketConfig] = {}
_cache_loaded = False


def _populate_cache_from_db() -> None:
    """Populate the sync cache from the database (blocking, safe at import time)."""
    global _ticket_configs, _cache_loaded
    if _cache_loaded:
        return
    try:
        import asyncio
        from database import _shared_pool

        pool = _shared_pool
        if pool is None:
            # Database not initialised yet — will be loaded later via async path
            _cache_loaded = True
            return

        # Use a new event loop for the blocking call if needed
        try:
            loop = asyncio.get_running_loop()
            # We're inside an async context — can't block here. Skip.
            # The async load_all_tickets() will populate the cache instead.
            return
        except RuntimeError:
            pass

        loop = asyncio.new_event_loop()
        try:
            rows = loop.run_until_complete(
                pool.fetch("SELECT * FROM ticket_config")
            )
            for row in rows:
                gid = row.get("guild_id")
                if gid is None:
                    continue
                cfg = TicketConfig(
                    guild_id=gid,
                    panel_title=row.get("panel_title"),
                    panel_description=row.get("panel_description"),
                    panel_color=row.get("panel_color"),
                    panel_image=row.get("panel_image"),
                    panel_categories=row.get("panel_categories") or [],
                    panel_channel_id=row.get("panel_channel_id"),
                    panel_message_id=row.get("panel_message_id"),
                    support_roles=row.get("support_roles") or [],
                    open_tickets=row.get("open_tickets") or [],
                )
                _ticket_configs[gid] = cfg
        finally:
            loop.close()
    except Exception:
        pass
    _cache_loaded = True


def _row_to_config(row) -> TicketConfig:
    """Convert a database row dict to a TicketConfig."""
    return TicketConfig(
        guild_id=row.get("guild_id", 0),
        panel_title=row.get("panel_title"),
        panel_description=row.get("panel_description"),
        panel_color=row.get("panel_color"),
        panel_image=row.get("panel_image"),
        panel_categories=row.get("panel_categories") or [],
        panel_channel_id=row.get("panel_channel_id"),
        panel_message_id=row.get("panel_message_id"),
        support_roles=row.get("support_roles") or [],
        open_tickets=row.get("open_tickets") or [],
    )


def get_ticket_config(guild_id: int) -> TicketConfig:
    """Get ticket config for a guild (sync — reads from cache)."""
    _populate_cache_from_db()
    cfg = _ticket_configs.get(guild_id)
    if cfg is None:
        cfg = TicketConfig(guild_id=guild_id)
        _ticket_configs[guild_id] = cfg
    return cfg


def update_ticket_config(guild_id: int, cfg: TicketConfig) -> None:
    """Update ticket config in cache and persist to database (sync wrapper)."""
    _ticket_configs[guild_id] = cfg
    _save_to_db_sync(guild_id, cfg)


def _save_to_db_sync(guild_id: int, cfg: TicketConfig) -> None:
    """Persist config to database synchronously."""
    try:
        import asyncio
        from database import _shared_pool

        pool = _shared_pool
        if pool is None:
            return

        try:
            loop = asyncio.get_running_loop()
            # Inside async context — schedule instead of blocking
            asyncio.ensure_future(_async_save_config(guild_id, cfg))
            return
        except RuntimeError:
            pass

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(_async_save_config(guild_id, cfg))
        finally:
            loop.close()
    except Exception:
        pass


async def _async_save_config(guild_id: int, cfg: TicketConfig) -> None:
    """Persist config to database asynchronously."""
    from database import _shared_pool

    pool = _shared_pool
    if pool is None:
        return

    await pool.execute(
        "INSERT INTO ticket_config "
        "(guild_id, panel_title, panel_description, panel_color, panel_image, "
        "panel_categories, panel_channel_id, panel_message_id, support_roles, open_tickets) "
        "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) "
        "ON CONFLICT (guild_id) DO UPDATE SET "
        "panel_title = $2, panel_description = $3, panel_color = $4, panel_image = $5, "
        "panel_categories = $6, panel_channel_id = $7, panel_message_id = $8, "
        "support_roles = $9, open_tickets = $10",
        guild_id,
        cfg.panel_title,
        cfg.panel_description,
        cfg.panel_color,
        cfg.panel_image,
        cfg.panel_categories or [],
        cfg.panel_channel_id,
        cfg.panel_message_id,
        cfg.support_roles or [],
        cfg.open_tickets or [],
    )


async def load_all_tickets() -> Dict[int, TicketConfig]:
    """Async loader — populates the sync cache from the database."""
    global _ticket_configs, _cache_loaded
    from database import _shared_pool

    pool = _shared_pool
    if pool is None:
        _cache_loaded = True
        return _ticket_configs

    try:
        rows = await pool.fetch("SELECT * FROM ticket_config")
        for row in rows:
            gid = row.get("guild_id")
            if gid is None:
                continue
            _ticket_configs[gid] = _row_to_config(row)
    except Exception:
        pass
    _cache_loaded = True
    return _ticket_configs


def get_all_ticket_configs() -> List[TicketConfig]:
    """Return all cached ticket configs (sync)."""
    _populate_cache_from_db()
    return list(_ticket_configs.values())


def find_open_ticket(guild_id: int, channel_id: int) -> Optional[dict]:
    """Return the open-ticket entry for a given channel, or None."""
    cfg = get_ticket_config(guild_id)
    for t in cfg.open_tickets:
        if t.get("channel_id") == channel_id:
            return t
    return None
