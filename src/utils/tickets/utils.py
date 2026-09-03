from __future__ import annotations
import asyncio
import json
from typing import Dict, List, Optional

from .config import TicketConfig

# ── In-memory cache ──────────────────────────────────────────────────────────
# Populated on cog setup via ``load_all_tickets()``.  All synchronous callers
# (view __init__, button callbacks) read from this cache; writes go both to
# cache *and* the database.

_ticket_configs: Dict[int, TicketConfig] = {}
_cache_loaded = False


# ── Helpers ──────────────────────────────────────────────────────────────────

def _row_to_config(row) -> TicketConfig:
    """Convert a database row/doc dict to a TicketConfig."""
    def _list(val):
        if isinstance(val, list):
            return val
        if isinstance(val, str):
            try:
                return json.loads(val)
            except Exception:
                return []
        return []

    return TicketConfig(
        guild_id=row.get("guild_id", 0),
        panel_title=row.get("panel_title"),
        panel_description=row.get("panel_description"),
        panel_color=row.get("panel_color"),
        panel_image=row.get("panel_image"),
        panel_categories=_list(row.get("panel_categories")),
        panel_channel_id=row.get("panel_channel_id"),
        panel_message_id=row.get("panel_message_id"),
        support_roles=_list(row.get("support_roles")),
        open_tickets=_list(row.get("open_tickets")),
    )


def _config_to_doc(cfg: TicketConfig) -> dict:
    """Convert a TicketConfig to a plain dict for MongoDB storage."""
    return {
        "guild_id": cfg.guild_id,
        "panel_title": cfg.panel_title,
        "panel_description": cfg.panel_description,
        "panel_color": cfg.panel_color,
        "panel_image": cfg.panel_image,
        "panel_categories": cfg.panel_categories or [],
        "panel_channel_id": cfg.panel_channel_id,
        "panel_message_id": cfg.panel_message_id,
        "support_roles": cfg.support_roles or [],
        "open_tickets": cfg.open_tickets or [],
    }


# ── Database operations (native collection access) ──────────────────────────

async def _save_config_to_db(guild_id: int, cfg: TicketConfig) -> bool:
    """Persist config to database using native collection access.

    Returns True on success, False on failure (with error logged).
    """
    from database import _shared_pool

    pool = _shared_pool
    if pool is None:
        return False

    doc = _config_to_doc(cfg)

    try:
        if pool.db_type == "mongodb":
            coll = pool.collection("ticket_config")
            await coll.update_one(
                {"_id": guild_id},
                {"$set": doc},
                upsert=True,
            )
        else:
            # SQLite path — use the existing SQL upsert
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
                json.dumps(cfg.panel_categories or []),
                cfg.panel_channel_id,
                cfg.panel_message_id,
                json.dumps(cfg.support_roles or []),
                json.dumps(cfg.open_tickets or []),
            )
        return True
    except Exception as e:
        import utils.logging as _log
        _log.error("Tickets", f"Failed to save ticket config for guild {guild_id}: {e}")
        return False


async def _load_configs_from_db() -> Dict[int, TicketConfig]:
    """Load all ticket configs from the database."""
    from database import _shared_pool

    pool = _shared_pool
    if pool is None:
        return {}

    configs: Dict[int, TicketConfig] = {}
    try:
        if pool.db_type == "mongodb":
            coll = pool.collection("ticket_config")
            cursor = coll.find({})
            async for doc in cursor:
                # MongoDB stores _id as the guild_id
                gid = doc.get("_id") or doc.get("guild_id")
                if gid is None:
                    continue
                doc["guild_id"] = gid
                configs[int(gid)] = _row_to_config(doc)
        else:
            rows = await pool.fetch("SELECT * FROM ticket_config")
            for row in rows:
                gid = row.get("guild_id")
                if gid is None:
                    continue
                configs[int(gid)] = _row_to_config(row)
    except Exception as e:
        import utils.logging as _log
        _log.warning("Tickets", f"Failed to load ticket configs: {e}")

    return configs


async def _config_exists_in_db(guild_id: int) -> bool:
    """Check if a ticket config exists in the database."""
    from database import _shared_pool

    pool = _shared_pool
    if pool is None:
        return False

    try:
        if pool.db_type == "mongodb":
            coll = pool.collection("ticket_config")
            doc = await coll.find_one({"_id": guild_id}, {"_id": 1})
            return doc is not None
        else:
            row = await pool.fetchval(
                "SELECT guild_id FROM ticket_config WHERE guild_id = $1",
                guild_id,
            )
            return row is not None
    except Exception:
        return False


# ── Public sync API (reads from cache) ───────────────────────────────────────

def get_ticket_config(guild_id: int) -> TicketConfig:
    """Get ticket config for a guild (sync — reads from cache)."""
    cfg = _ticket_configs.get(guild_id)
    if cfg is None:
        cfg = TicketConfig(guild_id=guild_id)
        _ticket_configs[guild_id] = cfg
    return cfg


def get_all_ticket_configs() -> List[TicketConfig]:
    """Return all cached ticket configs (sync)."""
    return list(_ticket_configs.values())


def find_open_ticket(guild_id: int, channel_id: int) -> Optional[dict]:
    """Return the open-ticket entry for a given channel, or None."""
    cfg = get_ticket_config(guild_id)
    for t in cfg.open_tickets:
        if t.get("channel_id") == channel_id:
            return t
    return None


# ── Sync update (fire-and-forget) ────────────────────────────────────────────

def update_ticket_config(guild_id: int, cfg: TicketConfig) -> None:
    """Update ticket config in cache and persist to database.

    This is the sync path used by view callbacks and non-async code.
    The DB write is fire-and-forget — errors are logged but not raised.
    """
    _ticket_configs[guild_id] = cfg

    # Try to schedule the async save
    try:
        loop = asyncio.get_running_loop()
        asyncio.ensure_future(_save_config_to_db(guild_id, cfg))
    except RuntimeError:
        # No running loop — use a blocking helper
        try:
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(_save_config_to_db(guild_id, cfg))
            finally:
                loop.close()
        except Exception:
            pass


# ── Async update (awaitable) ─────────────────────────────────────────────────

async def async_update_ticket_config(guild_id: int, cfg: TicketConfig) -> bool:
    """Update ticket config in cache and persist to database (async, awaitable).

    Returns True on success, False on failure.
    """
    _ticket_configs[guild_id] = cfg
    return await _save_config_to_db(guild_id, cfg)


# ── Async loader (cog setup) ─────────────────────────────────────────────────

async def load_all_tickets() -> Dict[int, TicketConfig]:
    """Load all ticket configs from database into the sync cache.

    Called once during cog setup.
    """
    global _ticket_configs, _cache_loaded

    _ticket_configs = await _load_configs_from_db()
    _cache_loaded = True
    return _ticket_configs
