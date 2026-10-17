"""Economy — top.gg vote rewards, streaks and multipliers.

A vote arrives from top.gg's webhook (``src/webapp/economy_routes.py``) and is
handed to :func:`record_vote`, which owns every rule about what a vote is
worth:

* a duplicate webhook inside ``VOTE_COOLDOWN`` pays nothing and is reported as
  ``already_voted``, so the caller can skip the thank-you DM;
* consecutive votes inside ``VOTE_STREAK_WINDOW`` build a streak, and the
  streak scales both the vote payout and daily/work earnings;
* weekend votes pay double, matching top.gg's own weekend bonus.

The rules live in :func:`apply_vote`, which mutates a user dict and is free of
database and Discord access, so the streak and duplicate behaviour is testable
on its own. The reward is credited through the economy cog so the in-memory
cache and the database stay in step.
"""

from __future__ import annotations

import time

import discord
from discord.ext import commands

from config.links import TOPGG_VOTE_URL
from utils import logging as log
from utils.economy_jobs import (
    VOTE_BASE_REWARD,
    VOTE_COOLDOWN,
    VOTE_STREAK_WINDOW,
    VOTE_WEEKEND_MULTIPLIER,
    vote_earnings_multiplier,
    vote_reward_multiplier,
)
from .data import ACCENT_GOLD, _check_achievements, _info_view, _log_tx, topgg_emoji


#: Heading every voting card with the listing site's own logo: the logo is an
#: application emoji registered at startup, so a pre-sync boot keeps the ballot
#: emoji until the real id lands in the emoji config.
VOTE_ICON = "🗳️"


def _vote_title(text: str) -> str:
    return f"# {topgg_emoji() or VOTE_ICON} {text}"


def _as_int(value) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def vote_standing(data: dict) -> dict:
    """Read-only view of a member's voting state, for the bot and the web UI."""
    streak = _as_int(data.get("vote_streak"))
    last_vote = _as_int(data.get("last_vote"))
    next_vote_at = last_vote + VOTE_COOLDOWN if last_vote else 0
    return {
        "votes": _as_int(data.get("votes")),
        "streak": streak,
        "best_streak": _as_int(data.get("best_vote_streak")),
        "last_vote": last_vote,
        "next_vote_at": next_vote_at,
        "can_vote": int(time.time()) >= next_vote_at,
        "reward_multiplier": round(vote_reward_multiplier(streak), 2),
        "earnings_multiplier": round(vote_earnings_multiplier(streak), 2),
        "vote_url": TOPGG_VOTE_URL,
    }


def apply_vote(data: dict, *, now: int | None = None, weekend: bool = False) -> dict:
    """Apply one vote to ``data`` in place and describe what it was worth.

    The caller is responsible for persisting ``data``. Returns a result dict
    with ``status`` set to ``"recorded"`` or ``"already_voted"``.
    """
    current = int(now if now is not None else time.time())
    last_vote = _as_int(data.get("last_vote"))
    streak = _as_int(data.get("vote_streak"))

    if last_vote and current - last_vote < VOTE_COOLDOWN:
        # top.gg retries deliveries; a second webhook for the same vote must
        # not pay out again or extend the streak.
        return {
            "status": "already_voted",
            "reward": 0,
            "votes": _as_int(data.get("votes")),
            "streak": streak,
            "reward_multiplier": round(vote_reward_multiplier(streak), 2),
            "earnings_multiplier": round(vote_earnings_multiplier(streak), 2),
            "weekend": bool(weekend),
            "next_vote_at": last_vote + VOTE_COOLDOWN,
            "unlocked": [],
        }

    streak = streak + 1 if last_vote and current - last_vote <= VOTE_STREAK_WINDOW else 1
    reward = int(VOTE_BASE_REWARD * vote_reward_multiplier(streak))
    if weekend:
        reward = int(reward * VOTE_WEEKEND_MULTIPLIER)

    data["votes"] = _as_int(data.get("votes")) + 1
    data["vote_streak"] = streak
    data["best_vote_streak"] = max(_as_int(data.get("best_vote_streak")), streak)
    data["last_vote"] = current
    data["balance"] = _as_int(data.get("balance")) + reward
    data["total_earned"] = _as_int(data.get("total_earned")) + reward
    _log_tx(data, "vote", reward, f"top.gg vote · streak {streak}")
    unlocked = _check_achievements(data, now=current)

    return {
        "status": "recorded",
        "reward": reward,
        "votes": data["votes"],
        "streak": streak,
        "reward_multiplier": round(vote_reward_multiplier(streak), 2),
        "earnings_multiplier": round(vote_earnings_multiplier(streak), 2),
        "weekend": bool(weekend),
        "next_vote_at": current + VOTE_COOLDOWN,
        "unlocked": unlocked,
    }


async def record_vote(bot, user_id, *, weekend: bool = False) -> dict:
    """Apply and persist a vote for ``user_id``. Must run on the bot loop."""
    cog = bot.get_cog("EconomyCog")
    if cog is None:
        raise RuntimeError("The economy cog is not loaded.")
    account_id = int(user_id)
    data = await cog.get_user_economy_data(account_id)
    result = apply_vote(data, weekend=weekend)
    if result["status"] == "recorded":
        await cog.save_user_economy_data(account_id)
    return result


def vote_dm_view(result: dict) -> discord.ui.LayoutView:
    """Build the thank-you DM for a recorded vote."""
    streak = _as_int(result.get("streak"))
    body = [
        f"You voted for **Niko** on top.gg and earned **{_as_int(result.get('reward')):,}** 🪙.",
        f"Vote streak: **{streak}** · vote reward **x{result.get('reward_multiplier', 1)}**"
        f" · earnings bonus **x{result.get('earnings_multiplier', 1)}**",
    ]
    if result.get("weekend"):
        body.append("-# Weekend votes pay double — thanks for the extra push!")
    unlocked = result.get("unlocked") or []
    if unlocked:
        body.append("**New achievements** " + ", ".join(unlocked))
    body.append(f"-# Vote again in 12 hours to keep the streak alive: {TOPGG_VOTE_URL}")
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=_vote_title("Thank you for voting!")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="\n".join(body)),
        accent_colour=ACCENT_GOLD,
    ))
    return view


async def send_vote_thanks(bot, user_id, result: dict) -> bool:
    """Send the thank-you DM. Best effort: a closed inbox is not a failure."""
    try:
        user = bot.get_user(int(user_id))
        if user is None:
            user = await bot.fetch_user(int(user_id))
        if user is None:
            return False
        await user.send(view=vote_dm_view(result))
        return True
    except Exception as exc:
        log.error("Economy", f"Could not send the vote thank-you DM to {user_id}: {exc}")
        return False


class VoteMixin:
    """The ``/vote`` command: the listing link, streaks and multipliers."""

    @commands.hybrid_command(
        name="vote",
        aliases=["upvote"],
        description="Vote for Niko on top.gg for coins and a streak bonus",
        help="{ 'en': 'vote for Niko on top.gg 🗳️✨', 'de': 'stimme für Niko auf top.gg', 'es': 'vota por Niko en top.gg 🗳️✨' }",
    )
    async def vote(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        data = await self.get_user_economy_data(ctx.author.id)
        standing = vote_standing(data)
        lines = [
            f"**Rewards** — every vote pays **{VOTE_BASE_REWARD:,}** 🪙, doubled on weekends.",
            f"**Your streak** — **{standing['streak']}** votes in a row"
            f" (best **{standing['best_streak']}**).",
            f"**Multipliers** — vote payout **x{standing['reward_multiplier']}**,"
            f" daily/work earnings **x{standing['earnings_multiplier']}**.",
            f"**Total votes** — **{standing['votes']}**.",
        ]
        if standing["can_vote"]:
            lines.append(f"Vote again any time — one vote every 12 hours counts.")
        else:
            remaining = max(0, standing["next_vote_at"] - int(time.time()))
            hours, rest = divmod(remaining, 3600)
            minutes = rest // 60
            lines.append(f"Next countable vote in **{hours}h {minutes}m**.")
        lines.append(f"[Vote on top.gg]({standing['vote_url']})")

        view = _info_view(f"{topgg_emoji() or VOTE_ICON} Vote for Niko", "\n".join(lines))
        if ctx.interaction:
            await ctx.interaction.followup.send(view=view)
        else:
            await ctx.send(view=view)
