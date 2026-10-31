"""Support-server referrals.

A referral link is the website's ``/discord?ref=<user id>`` page. Clicking it does
not hand out a Discord invite: the site adds the visitor to the support server
through **their own Discord account** (OAuth2 ``guilds.join``), and that is what
makes the referral verifiable.

Discord exposes no identity on a plain invite join — all a bot can see is an
invite's use counter — so per-member invites were the only way to tell who
brought whom, and a guild may only hold so many invites. Adding the member with
their own token instead means:

* one invite exists in the guild (the public one) no matter how many members
  share a link, so a large server never runs into the invite cap;
* the join is tied to the account that authorized it, so the referrer is a fact
  rather than a guess from timing or click counts;
* nobody can claim somebody else's join. Credit only lands when Discord itself
  adds that account, only for an account that was not already in the server, and
  only the first time it is added.

The coins are paid by ``cogs.economy.referrals``; this module decides who earned
them.
"""

from __future__ import annotations

import time

import discord
from discord.http import Route

from config.ids import SUPPORT_GUILD
from utils import logging


def _pool(bot):
    return getattr(bot, "cxn", None)


def _guild(bot) -> discord.Guild | None:
    return bot.get_guild(SUPPORT_GUILD)


async def _existing_member(guild: discord.Guild, user_id: int):
    """The member already in the guild, or ``None``.

    The gateway cache answers for anyone already seen; a miss is confirmed with
    the API so a stale cache cannot make an existing member look new (which would
    pay a referrer for somebody who was already here).
    """
    member = guild.get_member(user_id)
    if member is not None:
        return member
    try:
        return await guild.fetch_member(user_id)
    except discord.NotFound:
        return None


async def add_support_member(bot, user_id: int, access_token: str) -> bool:
    """Add *user_id* to the support server using their own OAuth2 token.

    discord.py does not wrap ``PUT /guilds/{id}/members/{id}``, so the route is
    called directly. Discord refuses the request when the token was issued
    without ``guilds.join`` (the site then asks the member to authorize again) or
    when Niko lacks Create Invite, and both are reported as a plain ``False``.
    """
    guild = _guild(bot)
    if guild is None or not access_token:
        return False
    try:
        await bot.http.request(
            Route(
                "PUT",
                "/guilds/{guild_id}/members/{user_id}",
                guild_id=guild.id,
                user_id=int(user_id),
            ),
            json={"access_token": access_token},
        )
    except (discord.Forbidden, discord.HTTPException) as exc:
        logging.warning("Referrals", f"Could not add {user_id} to the support server: {exc}")
        return False
    return True


async def join_with_referral(bot, user_id: int, referrer_id: int, access_token: str) -> dict:
    """Add a referred member and pay the referrer, once.

    ``status`` is one of ``joined`` (they are in the server; ``credited`` says
    whether this click paid somebody), ``already_member`` (nothing to attribute),
    ``not_added`` (Discord refused the add), or ``unavailable`` (no guild or
    database on this process).
    """
    guild = _guild(bot)
    pool = _pool(bot)
    if guild is None or pool is None:
        return {"status": "unavailable"}
    try:
        user_id = int(user_id)
        referrer_id = int(referrer_id)
    except (TypeError, ValueError):
        return {"status": "unavailable"}
    if user_id <= 0 or referrer_id <= 0:
        return {"status": "unavailable"}

    if await _existing_member(guild, user_id) is not None:
        return {"status": "already_member"}
    if not await add_support_member(bot, user_id, access_token):
        return {"status": "not_added"}
    # Clicking your own link still joins you; it just pays nobody.
    if referrer_id == user_id:
        return {"status": "joined"}

    seen = await pool.fetchrow(
        "SELECT referrer_id FROM support_referral_joins WHERE member_id = ?", user_id
    )
    if seen is not None:
        return {"status": "joined"}

    # The claim row is written before the payout so two simultaneous clicks for
    # the same member cannot both pay.
    await pool.execute(
        "INSERT OR IGNORE INTO support_referral_joins (member_id, referrer_id, joined_at, reward) "
        "VALUES (?, ?, ?, 0)",
        user_id, referrer_id, int(time.time()),
    )

    from cogs.economy.referrals import pay_referral

    result = await pay_referral(bot, referrer_id, user_id)
    if result is None:
        # The account could not be credited, so the join is not counted either:
        # the ledger only holds paid referrals.
        await pool.execute(
            "DELETE FROM support_referral_joins WHERE member_id = ? AND reward = 0", user_id
        )
        return {"status": "joined"}
    await pool.execute(
        "UPDATE support_referral_joins SET reward = ? WHERE member_id = ?",
        int(result["reward"]), user_id,
    )
    return {"status": "joined", "credited": True, "referrer_id": referrer_id, **result}


async def referral_standing(bot, user_id: int) -> dict:
    """What one member's link has brought in, for the dashboard card."""
    pool = _pool(bot)
    standing = {"invited": 0, "coins": 0, "recent": []}
    if pool is None:
        return standing
    try:
        total = await pool.fetchrow(
            "SELECT COUNT(*) AS invited, COALESCE(SUM(reward), 0) AS coins "
            "FROM support_referral_joins WHERE referrer_id = ?",
            int(user_id),
        )
        rows = await pool.fetch(
            "SELECT member_id, joined_at, reward FROM support_referral_joins "
            "WHERE referrer_id = ? ORDER BY joined_at DESC LIMIT 5",
            int(user_id),
        )
    except Exception as exc:
        logging.error("Referrals", f"Could not read referrals for {user_id}: {exc}")
        return standing
    if total is not None:
        standing["invited"] = int(total.get("invited") or 0)
        standing["coins"] = int(total.get("coins") or 0)
    standing["recent"] = [
        {
            "member_id": str(row.get("member_id")),
            "joined_at": int(row.get("joined_at") or 0),
            "reward": int(row.get("reward") or 0),
        }
        for row in rows or []
    ]
    return standing
