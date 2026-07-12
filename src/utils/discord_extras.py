"""
discord_extras.py
─────────────────
Shared utilities for undocumented / lightly-documented Discord API features.

All helpers are safe to call — they swallow HTTPException so callers can
fire-and-forget without wrapping every call in try/except.

Available:
  burst_react(bot, channel_id, message_id, emoji)    — super/burst reaction
  set_voice_status(bot, channel_id, status)          — VC header status text
  forward_message(bot, target_ch, source_ch, msg_id) — native message forward
  stage_become_speaker(bot, guild_id, channel_id)    — bot speaks on Stage
"""

from __future__ import annotations

import urllib.parse

import discord
from discord.http import Route


async def burst_react(
    bot: discord.Client,
    channel_id: int,
    message_id: int,
    emoji: str,
) -> None:
    """Send a Nitro-style burst/super reaction.

    Bot accounts can send burst reactions without owning Nitro.
    emoji: plain unicode (e.g. "⭐") or custom "name:id" string.
    """
    encoded = urllib.parse.quote(emoji, safe="")
    route = Route(
        "PUT",
        "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
        channel_id=channel_id,
        message_id=message_id,
        emoji=encoded,
    )
    try:
        await bot.http.request(route, params={"burst": "true"})
    except discord.HTTPException:
        pass


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


async def forward_message(
    bot: discord.Client,
    target_channel_id: int,
    source_channel_id: int,
    message_id: int,
    content: str | None = None,
) -> discord.Message | None:
    """Forward a message to another channel using Discord's native forward feature.

    Uses message_reference type=1 (forward), added by Discord in 2024.
    type=0 is the existing reply; type=1 is a forward that shows the original.
    Returns the new Message object on success, None on failure.
    """
    route = Route(
        "POST",
        "/channels/{channel_id}/messages",
        channel_id=target_channel_id,
    )
    payload: dict = {
        "message_reference": {
            "type": 1,
            "message_id": str(message_id),
            "channel_id": str(source_channel_id),
        }
    }
    if content:
        payload["content"] = content[:2000]
    try:
        data = await bot.http.request(route, json=payload)
        state = bot._connection  # type: ignore[attr-defined]
        return discord.Message(state=state, channel=bot.get_channel(target_channel_id), data=data)  # type: ignore
    except discord.HTTPException:
        return None


async def stage_become_speaker(
    bot: discord.Client,
    guild_id: int,
    channel_id: int,
) -> None:
    """Make the bot a speaker on a Stage channel.

    The bot must already be in the Stage channel. Sends a request-to-speak
    timestamp and immediately suppresses=False to grant speaker status.
    """
    import datetime
    try:
        await bot.http.edit_my_voice_state(
            guild_id,
            channel_id=channel_id,
            suppress=False,
            request_to_speak_timestamp=datetime.datetime.utcnow().isoformat(),
        )
    except discord.HTTPException:
        pass
