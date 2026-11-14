"""Send official announcements to the support server.

Announcement content is supplied by the caller (the MCP tool), so no release
text or policy notice lives in the bot. Delivery always targets the support
server's ``announcements`` channel and can mention its ``announcements_ping``
role.
"""

from __future__ import annotations

import discord

from config.ids import SUPPORT_GUILD
from cogs.staff.support_server import get_support_ids
from utils.broadcast import DEFAULT_ACCENT, MAX_BODY, MAX_FOOTER, MAX_TITLE, build_broadcast_view


async def send_support_announcement(
    bot,
    *,
    title: str,
    body: str,
    footer: str | None = None,
    ping: bool = True,
    accent: str = DEFAULT_ACCENT,
) -> dict:
    """Post one CV2 announcement in the configured support announcements channel.

    ``ping`` defaults to the support server's announcements role. The role is
    looked up from the persisted support configuration rather than a hardcoded
    ID, and a missing channel or role raises an actionable error instead of
    posting silently without the expected ping.
    """
    title = str(title or "").strip()
    body = str(body or "").strip()
    footer = str(footer or "").strip()
    if not title:
        raise ValueError("Announcements need a title.")
    if len(title) > MAX_TITLE:
        raise ValueError(f"The title must be {MAX_TITLE} characters or fewer.")
    if not body:
        raise ValueError("Announcements need a message.")
    if len(body) > MAX_BODY:
        raise ValueError(f"The message must be {MAX_BODY} characters or fewer.")
    if len(footer) > MAX_FOOTER:
        raise ValueError(f"The footer must be {MAX_FOOTER} characters or fewer.")

    ids = await get_support_ids(bot)
    channel_id = (ids.get("channels") or {}).get("announcements")
    if not channel_id:
        raise RuntimeError(
            "The support announcements channel is not configured. "
            "Run `.staff supportupdate` in the support server."
        )

    role_id = (ids.get("roles") or {}).get("announcements_ping")
    if ping and not role_id:
        raise RuntimeError(
            "The announcements ping role is not configured. "
            "Run `.staff supportupdate` in the support server."
        )

    channel = bot.get_channel(int(channel_id))
    if channel is None:
        channel = await bot.fetch_channel(int(channel_id))

    mention = f"<@&{int(role_id)}>" if ping else None
    kwargs = {
        "view": build_broadcast_view(title, body, footer, accent, []),
        "allowed_mentions": (
            discord.AllowedMentions(
                roles=[discord.Object(id=int(role_id))], everyone=False, users=False,
            )
            if ping else discord.AllowedMentions.none()
        ),
    }
    if mention:
        kwargs["content"] = mention
    message = await channel.send(**kwargs)
    return {
        "message_id": message.id,
        "channel_id": int(channel_id),
        "guild_id": SUPPORT_GUILD,
        "pinged_role_id": int(role_id) if ping else None,
        "url": getattr(message, "jump_url", None),
    }
