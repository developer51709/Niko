"""
discord_extras.py
─────────────────
Shared utilities for undocumented / lightly-documented Discord API features.

All helpers are safe to call — they swallow HTTPException so callers can
fire-and-forget without wrapping every call in try/except.

Available:
  set_voice_status(bot, channel_id, status)          — VC header status text
"""

from __future__ import annotations

import discord


async def set_voice_status(
    bot: discord.Client,
    channel_id: int,
    status: str | None,
) -> None:
    """Set (or clear) the text status shown in the voice channel list header.

    Requires MANAGE_CHANNELS or the bot being in that channel.
    Pass status=None or "" to clear the status.
    Discord limit: ~500 characters.
    """
    try:
        await bot.http.edit_voice_channel_status(status or "", channel_id=channel_id)
    except discord.HTTPException:
        pass

