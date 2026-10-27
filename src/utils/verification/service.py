"""What happens when verification succeeds or fails, for every mode.

The three modes differ only in how the member proves they are human. Everything
after that — which roles are added and removed, what the audit log says, and
whether a failure kicks — has to be identical, so it lives here rather than
being copied into the button, the DM listener, and the website route.

Callers own the messages. This module returns what happened so each surface can
render it in its own shape: a CV2 reply in Discord, a page in the browser.
"""

import discord

from utils import logging as bot_logging
from utils.onboarding.config import load_config


def get_guild(bot, guild_id: int):
    """The guild, or ``None`` when the bot is not in it any more."""
    if bot is None:
        return None
    try:
        return bot.get_guild(int(guild_id))
    except (TypeError, ValueError):
        return None


async def complete(bot, guild_id: int, user_id: int, *, source: str = "captcha") -> dict:
    """Apply a guild's verification outcome and log it.

    Returns a dict with ``ok``, ``guild``, ``member``, ``applied``, ``removed``
    and a ``problem`` of ``"guild"`` or ``"member"`` when the roles could not be
    applied (the bot left, or the member did). A missing guild or member is not
    an error — the member still proved they are human — so ``ok`` stays true and
    the caller can say what went wrong.
    """
    guild = get_guild(bot, guild_id)
    if guild is None:
        return {"ok": True, "guild": None, "member": None, "applied": [], "removed": [], "problem": "guild"}
    member = guild.get_member(int(user_id))
    if member is None:
        return {"ok": True, "guild": guild, "member": None, "applied": [], "removed": [], "problem": "member"}

    cfg = await load_config(guild.id)
    applied: list[str] = []
    removed: list[str] = []

    for role_id in cfg.captcha_add_role_ids or []:
        role = guild.get_role(int(role_id))
        if role is None or role in member.roles:
            continue
        try:
            await member.add_roles(role, reason="Captcha verification passed")
            applied.append(role.name)
        except discord.Forbidden:
            pass

    for role_id in cfg.captcha_remove_role_ids or []:
        role = guild.get_role(int(role_id))
        if role is None or role not in member.roles:
            continue
        try:
            await member.remove_roles(role, reason="Captcha verification passed")
            removed.append(role.name)
        except discord.Forbidden:
            pass

    logger = bot.get_cog("ServerLogger") if bot is not None else None
    if logger is not None:
        try:
            await logger.log_event(
                guild, "captcha", "Captcha Passed",
                (
                    f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                    f"**Result:** Passed\n"
                    f"**Method:** {source}\n"
                    f"**Roles Added:** {', '.join(applied) if applied else 'None'}\n"
                    f"**Roles Removed:** {', '.join(removed) if removed else 'None'}"
                ),
                target_id=member.id,
            )
        except Exception as error:  # logging must never fail a verification
            bot_logging.warning("Verification", f"Could not log a passed verification: {error}")

    return {"ok": True, "guild": guild, "member": member, "applied": applied, "removed": removed, "problem": None}


async def fail(bot, guild_id: int, user_id: int, *, kick: bool, source: str = "captcha") -> dict:
    """Record a failed verification and kick when the server asked for it.

    Returns ``{"kicked": bool, "guild": guild|None}``; a kick the bot is not
    allowed to perform is reported as not kicked rather than raised.
    """
    guild = get_guild(bot, guild_id)
    kicked = False
    member = guild.get_member(int(user_id)) if guild is not None else None
    if kick and member is not None:
        try:
            await member.kick(reason="Failed captcha verification (3 wrong attempts)")
            kicked = True
        except (discord.Forbidden, discord.HTTPException):
            kicked = False

    logger = bot.get_cog("ServerLogger") if bot is not None and guild is not None else None
    if logger is not None:
        title = "Captcha Kicked" if kicked else "Captcha Failed"
        try:
            await logger.log_event(
                guild, "captcha", title,
                (
                    f"**User:** <@{int(user_id)}> (ID: `{int(user_id)}`)\n"
                    f"**Result:** {'Failed all 3 attempts and kicked' if kicked else 'Failed all 3 attempts'}\n"
                    f"**Method:** {source}"
                ),
                target_id=int(user_id), action_key=title,
            )
        except Exception as error:
            bot_logging.warning("Verification", f"Could not log a failed verification: {error}")

    return {"kicked": kicked, "guild": guild}
