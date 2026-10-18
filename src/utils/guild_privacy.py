"""Per-guild privacy for server tag popups.

A server can ask Niko not to reveal its identity in the server-tag popups shown
on the website and in ticket transcripts. The tag itself stays visible — the
popup just shows Discord's "Private Server" state instead of the server's name,
icon, description, member counts, and invite.
"""

from __future__ import annotations

import database

_DEFAULT = {"private": False}


async def get_guild_privacy(guild_id: int, pool=None) -> dict:
    """Return a guild's server-tag privacy settings, defaulting to public."""
    pool = pool or database._shared_pool
    if pool is None:
        return dict(_DEFAULT)
    try:
        row = await pool.fetchrow(
            "SELECT private_server FROM guild_privacy WHERE guild_id = $1",
            int(guild_id),
        )
    except Exception:
        # An installation that has not run the startup migration yet is public.
        return dict(_DEFAULT)
    if not row:
        return dict(_DEFAULT)
    return {"private": bool(row.get("private_server"))}


async def set_guild_privacy(guild_id: int, private: bool, pool=None) -> dict:
    """Persist a guild's server-tag privacy setting."""
    pool = pool or database._shared_pool
    if pool is None:
        raise RuntimeError("The primary database is unavailable.")
    await pool.execute(
        "INSERT OR REPLACE INTO guild_privacy (guild_id, private_server) VALUES ($1, $2)",
        int(guild_id),
        1 if private else 0,
    )
    return {"private": bool(private)}
