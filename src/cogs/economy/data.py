# economy.py — premium Niko economy cog
#
# Adds image-card driven balance/profile/work/daily/leaderboard, a job ladder
# with XP/levels, a tiered bank with daily interest, an expanded shop with
# usable consumables and upgrades, a weekly lottery, transaction history and
# an achievement system.
#
# Backwards-compat: the legacy `get_user_economy_data(user_id)` and
# `save_economy_data()` API is preserved, so blackjack/slots/roulette/gambling
# cogs continue to work without modification.
#
# Note: The economy system now uses the bot's database (SQLite or MongoDB) instead of JSON files.

from __future__ import annotations

import asyncio
import datetime
import json
import os
import random
import time
import uuid
from io import BytesIO

import discord
from discord.ext import commands, tasks

from utils import logging as log
from utils.paginator import PaginatedView, paginate
from utils.i18n import make_flat_msg
from utils.locales import load_locales
from utils.prefix_manager import resolve_prefix
from config.emojis import get_emoji
from config.links import WEBSITE
from .seasons import season_open, season_open_key
from utils.economy_jobs import (
    JOBS, DEFAULT_JOB, get_job,
    SHOP_ITEMS, get_item, shop_loading_row_counts,
    BANK_TIERS, bank_info, bank_cap, bank_name, bank_rate, max_bank_tier,
    xp_to_next, total_xp_for_level, level_from_total_xp, add_xp,
    LOTTERY_TICKET_PRICE, LOTTERY_DRAW_INTERVAL, LOTTERY_HOUSE_RAKE, LOTTERY_BASE_POT,
    COOLDOWN_DAILY, COOLDOWN_WORK, COOLDOWN_CRIME, COOLDOWN_ROB,
)
from utils.locales import load_locales
from utils.image.economy_card import (
    render_balance_card, render_reward_card, render_leaderboard_card,
    fetch_avatar_bytes,
    ACCENT_GOLD, ACCENT_GREEN, ACCENT_RED,
)

# ── Bilingual messages ───────────────────────────────────────────────────────
MESSAGES = load_locales("cogs.economy", "data")


msg = make_flat_msg(MESSAGES)

# Niko's own emojis are filled into catalogue `{cross}`-style tokens here, so a
# re-uploaded emoji id never has to be baked into every translation file.
_LOCALE_EMOJI = {
    "cross": get_emoji("cross"),
    "tick":  get_emoji("tick"),
    "lock":  get_emoji("lock"),
}


def locale_t(table: dict):
    """Return ``t(lang, key, **kwargs)`` bound to one loaded catalogue table.

    Economy replies are built from ids and numbers, so a language code is the
    natural first argument: every view already knows the guild it belongs to.

    Usage::

        from utils.locales import load_locales

        T = locale_t(load_locales("cogs.economy", "bank"))
    """

    def t(lang: str, key: str, **kwargs) -> str:
        text = table.get(lang, {}).get(key) or table["en"].get(key, key)
        for name, value in _LOCALE_EMOJI.items():
            token = "{" + name + "}"
            if token in text:
                text = text.replace(token, value)
        return text.format(**kwargs) if kwargs else text

    return t


# The shop catalogue also drives the placeholder shop card shown while the real
# one renders, so the loading layout speaks the same language as the panel.
_SHOP_T = locale_t(load_locales("cogs.economy", "shop"))


async def _reply(ctx, view=None, *, ephemeral: bool = False, allowed_mentions=None):
    """Send a view through an interaction or a prefix context.

    Every economy command runs as both a slash and a prefix command, so each
    reply used to be written twice. Routing them through one helper means a
    localised string can never drift between the two paths.
    """
    kwargs = {}
    if ephemeral:
        kwargs["ephemeral"] = True
    if allowed_mentions is not None:
        kwargs["allowed_mentions"] = allowed_mentions
    if getattr(ctx, "interaction", None):
        return await ctx.interaction.followup.send(view=view, **kwargs)
    return await ctx.send(view=view, **kwargs)


# ── Prefix resolver (used by tip text in cards) ──────────────────────────────
async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    """Return the primary prefix for this context, honouring a dynamic prefix."""
    return await resolve_prefix(bot, ctx_or_interaction)


# ── Default user shape ──────────────────────────────────────────────────────
def _default_user() -> dict:
    return {
        # money
        "balance":       100,
        "bank":          0,
        "net_worth":     100,
        "leaderboard_private": 0,
        "total_earned":  100,
        "total_spent":   0,
        # career
        "xp":            0,
        "level":         0,
        "job":           DEFAULT_JOB,
        "times_worked":  0,
        # bank
        "bank_tier":     0,
        "last_interest": 0,
        # streaks / cooldowns
        "daily_streak":  0,
        "last_daily":    0,
        "last_work":     0,
        "last_crime":    0,
        "last_rob":      0,
        "last_heist":    0,
        "last_slots":    0,
        "last_blackjack": 0,
        "last_roulette": 0,
        "last_casino":   0,
        "last_gamble":   0,
        "last_bet":      0,
        "last_race":     0,
        "last_fight":    0,
        "last_duel":     0,
        # inventory: dict[item_id, count]
        "inventory":     {},
        # one-shot effects pending consumption
        "effects":       {},   # e.g. {"work_cooldown_half": True, "crime_boost": 1, "rob_shield": 1, "lottery_boost": 1}
        # lottery
        "lottery_tickets": 0,
        # lifetime lottery counters, so a weekly ticket reset never erases what
        # a member has bought or won (see the lottery badges below)
        "lottery_tickets_bought": 0,
        "lottery_wins": 0,
        # top.gg voting (see cogs/economy/voting.py)
        "votes":            0,
        "vote_streak":      0,
        "best_vote_streak": 0,
        "last_vote":        0,
        # transaction log (most recent first, capped)
        "transactions":  [],
        # achievements (list of ids)
        "achievements":  [],
        # per-season baselines for the seasonal badges:
        # {achievement_id: {"window": "YYYY-MM-DD", "value": int}}
        "season_progress": {},
    }


def _migrate_user(data: dict) -> dict:
    """Fill in any missing fields and convert legacy shapes in-place."""
    defaults = _default_user()
    for k, v in defaults.items():
        if k not in data:
            data[k] = v if not isinstance(v, (dict, list)) else (dict(v) if isinstance(v, dict) else list(v))

    # legacy inventory was a list of item ids
    inv = data.get("inventory")
    if isinstance(inv, list):
        counts: dict[str, int] = {}
        for it in inv:
            if not isinstance(it, str):
                continue
            counts[it] = counts.get(it, 0) + 1
        data["inventory"] = counts
    elif not isinstance(inv, dict):
        data["inventory"] = {}

    # A stored baseline blob that is not a mapping (legacy or hand-edited row)
    # would break the seasonal reads, so it is replaced rather than trusted.
    if not isinstance(data.get("season_progress"), dict):
        data["season_progress"] = {}

    # always recompute net worth on access
    data["net_worth"] = int(data.get("balance", 0)) + int(data.get("bank", 0))
    return data


# ── Achievements ────────────────────────────────────────────────────────────
# Every entry carries:
#   name / emoji / description  how the badge is presented in the bot and web
#   icon                        optional logo key; a badge that carries one is
#                               drawn with that logo instead of its emoji
#   season                      optional event window; the badge only unlocks
#                               while it is open (see cogs/economy/seasons.py)
#   season_measure              how a seasonal badge is measured inside its
#                               window ("hold" / "gain" / "reach"); see the
#                               seasonal measurement note below
#   test(data)                  whether the badge is earned
#   progress(data)              (current, target) for the dashboard bars
#   reward                      coins paid ONCE, the moment the badge unlocks
#
# The reward is why this table is data instead of prose: the balance is
# credited exactly when the id joins ``data["achievements"]``, and that stored
# id list is what stops a second payout on the next save.
#
# Seasonal measurement. A badge with a ``season`` carries a ``season_measure``
# that says how its metric is allowed to reach its target:
#
#   "hold"   the metric is a live state ("hold 25,000 in your vault"): the badge
#            is earned by showing that state while the event is on, because that
#            is what the condition means. Progress reads the state itself, and
#            the state is never read outside the window.
#   "gain"   the metric is a lifetime accumulator ("spend 5,000 during the
#            event"): only what accumulated after the window opened counts, so a
#            spending spree from another month cannot buy the badge.
#   "reach"  the metric is a monotonic milestone ("reach career level 25"): the
#            target has to be crossed after the window opened. An account
#            already past it has to gain one more step during the event, which
#            keeps a long-standing member's badge reachable instead of dead.
#
# The two window measures read a baseline — the metric's value when the current
# window opened — from ``ensure_season_baselines``, keyed by the window's opening
# date so next year's event starts from zero instead of inheriting this year.

# ── top.gg logo ─────────────────────────────────────────────────────────────
# Voting badges show the listing site's own logo, registered as an application
# emoji at startup (``utils/emoji_sync.py``). Until that first sync has run,
# ``config.emojis`` still holds the placeholder id, so every renderer falls
# back to the badge's unicode emoji rather than printing a broken mention.
_TOPGG_PLACEHOLDER = "<:topgg:0>"


def topgg_emoji() -> str | None:
    """The live top.gg application emoji, or ``None`` before the first sync."""
    emoji = get_emoji("topgg")
    return emoji if emoji and emoji != _TOPGG_PLACEHOLDER else None


def achievement_icon(meta: dict) -> str:
    """The icon a badge is drawn with — a logo for voting badges, else its emoji."""
    if meta.get("icon") == "topgg":
        return topgg_emoji() or meta["emoji"]
    return meta["emoji"]


#: Badge names, ``<achievement_id>.name``, per language. The English names in
#: ``ACHIEVEMENTS`` stay the fallback and keep a badge routable by its key.
ACHIEVEMENT_NAMES = load_locales("cogs.economy", "achievements")


def achievement_name(achievement_id: str, meta: dict, lang: str = "en") -> str:
    """The badge's name in *lang*, falling back to its English name."""
    key = f"{achievement_id}.name"
    return (
        ACHIEVEMENT_NAMES.get(lang, {}).get(key)
        or ACHIEVEMENT_NAMES["en"].get(key)
        or meta.get("name", achievement_id)
    )


def achievement_label(meta: dict, achievement_id: str | None = None,
                      lang: str = "en") -> str:
    """``"Week of Votes <logo>"``, the string an unlock announcement prints."""
    name = achievement_name(achievement_id, meta, lang) if achievement_id else meta["name"]
    return f"{name} {achievement_icon(meta)}"


def net_worth(data: dict) -> int:
    """The wallet plus the vault.

    ``_migrate_user`` keeps a stored total up to date, but a raw database row
    carries only the two halves — worth badges read them directly so they can be
    measured from either shape.
    """
    return int(data.get("balance", 0)) + int(data.get("bank", 0))


ACHIEVEMENTS = {
    # ── Working ──────────────────────────────────────────────────────────
    "first_paycheck": {
        "name": "First Paycheck", "emoji": "💼", "reward": 250,
        "description": "Work your very first shift.",
        "test": lambda d: d["times_worked"] >= 1,
        "progress": lambda d: (d["times_worked"], 1),
    },
    "regular": {
        "name": "Shift Regular", "emoji": "🧾", "reward": 1_000,
        "description": "Clock in for 25 shifts.",
        "test": lambda d: d["times_worked"] >= 25,
        "progress": lambda d: (d["times_worked"], 25),
    },
    "shift_lead": {
        "name": "Shift Lead", "emoji": "📋", "reward": 5_000,
        "description": "Clock in for 100 shifts.",
        "test": lambda d: d["times_worked"] >= 100,
        "progress": lambda d: (d["times_worked"], 100),
    },
    "shift_50": {
        "name": "Shift Veteran", "emoji": "⏰", "reward": 2_500,
        "description": "Clock in for 50 shifts.",
        "test": lambda d: int(d.get("times_worked", 0)) >= 50,
        "progress": lambda d: (int(d.get("times_worked", 0)), 50),
    },
    "level_5": {
        "name": "Clocking In", "emoji": "☕", "reward": 1_000,
        "description": "Reach career level 5.",
        "test": lambda d: int(d.get("level", 0)) >= 5,
        "progress": lambda d: (int(d.get("level", 0)), 5),
    },
    "level_15": {
        "name": "Floor Lead", "emoji": "🗂️", "reward": 5_000,
        "description": "Reach career level 15.",
        "test": lambda d: int(d.get("level", 0)) >= 15,
        "progress": lambda d: (int(d.get("level", 0)), 15),
    },
    "level_30": {
        "name": "Corner Office", "emoji": "🏢", "reward": 15_000,
        "description": "Reach career level 30.",
        "test": lambda d: int(d.get("level", 0)) >= 30,
        "progress": lambda d: (int(d.get("level", 0)), 30),
    },
    # ── Banking ──────────────────────────────────────────────────────────
    "saver": {
        "name": "Tin-Jar Saver", "emoji": "🪙", "reward": 500,
        "description": "Keep 10,000 coins in the bank.",
        "test": lambda d: d["bank"] >= 10_000,
        "progress": lambda d: (d["bank"], 10_000),
    },
    "vault_keeper": {
        "name": "Vault Keeper", "emoji": "🏦", "reward": 5_000,
        "description": "Keep 100,000 coins in the bank.",
        "test": lambda d: d["bank"] >= 100_000,
        "progress": lambda d: (d["bank"], 100_000),
    },
    "bank_tier_2": {
        "name": "Steel Vault", "emoji": "🔐", "reward": 2_500,
        "description": "Upgrade your vault to the Steel Vault, tier 3.",
        "test": lambda d: int(d.get("bank_tier", 0)) >= 2,
        "progress": lambda d: (int(d.get("bank_tier", 0)), 2),
    },
    "bank_tier_top": {
        "name": "Diamond Vault", "emoji": "💠", "reward": 50_000,
        "description": "Reach the final vault tier, the Diamond Vault.",
        "test": lambda d: int(d.get("bank_tier", 0)) >= max_bank_tier(),
        "progress": lambda d: (int(d.get("bank_tier", 0)), max_bank_tier()),
    },
    "millionaire": {
        "name": "Millionaire", "emoji": "💰", "reward": 50_000,
        "description": "Reach a net worth of 1,000,000 coins.",
        "test": lambda d: d["net_worth"] >= 1_000_000,
        "progress": lambda d: (d["net_worth"], 1_000_000),
    },
    # ── Daily streak ─────────────────────────────────────────────────────
    "streak_7": {
        "name": "Week-long Habit", "emoji": "🔥", "reward": 1_000,
        "description": "Claim your daily reward 7 days in a row.",
        "test": lambda d: d["daily_streak"] >= 7,
        "progress": lambda d: (d["daily_streak"], 7),
    },
    "streak_14": {
        "name": "Two-Week Run", "emoji": "⏳", "reward": 2_500,
        "description": "Claim your daily reward 14 days in a row.",
        "test": lambda d: int(d.get("daily_streak", 0)) >= 14,
        "progress": lambda d: (int(d.get("daily_streak", 0)), 14),
    },
    "streak_30": {
        "name": "Daily Devotee", "emoji": "🌟", "reward": 10_000,
        "description": "Claim your daily reward 30 days in a row.",
        "test": lambda d: d["daily_streak"] >= 30,
        "progress": lambda d: (d["daily_streak"], 30),
    },
    "streak_60": {
        "name": "Dedicated Regular", "emoji": "💎", "reward": 25_000,
        "description": "Claim your daily reward 60 days in a row.",
        "test": lambda d: d["daily_streak"] >= 60,
        "progress": lambda d: (d["daily_streak"], 60),
    },
    "streak_90": {
        "name": "Economy Legend", "emoji": "🏆", "reward": 100_000,
        "description": "Claim your daily reward 90 days in a row.",
        "test": lambda d: d["daily_streak"] >= 90,
        "progress": lambda d: (d["daily_streak"], 90),
    },
    # ── Career and spending ──────────────────────────────────────────────
    "owner": {
        "name": "Business Owner", "emoji": "👑", "reward": 25_000,
        "description": "Reach the top of the job ladder.",
        "test": lambda d: d.get("job") == "owner",
        "progress": lambda d: (1 if d.get("job") == "owner" else 0, 1),
    },
    "gambler": {
        "name": "High Roller", "emoji": "🎰", "reward": 2_500,
        "description": "Spend 50,000 coins across the economy.",
        "test": lambda d: int(d.get("total_spent", 0)) >= 50_000,
        "progress": lambda d: (int(d.get("total_spent", 0)), 50_000),
    },
    "whale": {
        "name": "Casino Whale", "emoji": "🐋", "reward": 25_000,
        "description": "Spend 500,000 coins across the economy.",
        "test": lambda d: int(d.get("total_spent", 0)) >= 500_000,
        "progress": lambda d: (int(d.get("total_spent", 0)), 500_000),
    },
    "earner": {
        "name": "Big Earner", "emoji": "📈", "reward": 25_000,
        "description": "Earn 1,000,000 coins in total.",
        "test": lambda d: int(d.get("total_earned", 0)) >= 1_000_000,
        "progress": lambda d: (int(d.get("total_earned", 0)), 1_000_000),
    },
    "worth_1k": {
        "name": "Four Figures", "emoji": "🧮", "reward": 250,
        "description": "Reach a net worth of 1,000 coins.",
        "test": lambda d: net_worth(d) >= 1_000,
        "progress": lambda d: (net_worth(d), 1_000),
    },
    "worth_250k": {
        "name": "Quarter Million", "emoji": "💵", "reward": 15_000,
        "description": "Reach a net worth of 250,000 coins.",
        "test": lambda d: net_worth(d) >= 250_000,
        "progress": lambda d: (net_worth(d), 250_000),
    },
    "spend_10k": {
        "name": "Treat Yourself", "emoji": "🛍️", "reward": 500,
        "description": "Spend 10,000 coins across the economy.",
        "test": lambda d: int(d.get("total_spent", 0)) >= 10_000,
        "progress": lambda d: (int(d.get("total_spent", 0)), 10_000),
    },
    # ── top.gg voting ────────────────────────────────────────────────────
    # These carry "icon": "topgg", so they render with the listing site's logo
    # (the unicode emoji stays as the fallback for a pre-sync boot).
    "voter_first": {
        "name": "First Upvote", "emoji": "🗳️", "icon": "topgg", "reward": 500,
        "description": "Vote for Niko on top.gg once.",
        "test": lambda d: int(d.get("votes", 0)) >= 1,
        "progress": lambda d: (int(d.get("votes", 0)), 1),
    },
    "voter_regular": {
        "name": "Vote Regular", "emoji": "📬", "icon": "topgg", "reward": 2_500,
        "description": "Vote for Niko on top.gg 10 times.",
        "test": lambda d: int(d.get("votes", 0)) >= 10,
        "progress": lambda d: (int(d.get("votes", 0)), 10),
    },
    "voter_25": {
        "name": "Loyal Voter", "emoji": "🎖️", "icon": "topgg", "reward": 5_000,
        "description": "Vote for Niko on top.gg 25 times.",
        "test": lambda d: int(d.get("votes", 0)) >= 25,
        "progress": lambda d: (int(d.get("votes", 0)), 25),
    },
    "voter_devoted": {
        "name": "Ballot Stuffer", "emoji": "🧾", "icon": "topgg", "reward": 10_000,
        "description": "Vote for Niko on top.gg 50 times.",
        "test": lambda d: int(d.get("votes", 0)) >= 50,
        "progress": lambda d: (int(d.get("votes", 0)), 50),
    },
    "voter_legend": {
        "name": "Civic Legend", "emoji": "🏛️", "icon": "topgg", "reward": 50_000,
        "description": "Vote for Niko on top.gg 200 times.",
        "test": lambda d: int(d.get("votes", 0)) >= 200,
        "progress": lambda d: (int(d.get("votes", 0)), 200),
    },
    "vote_streak_7": {
        "name": "Week of Votes", "emoji": "🗓️", "icon": "topgg", "reward": 5_000,
        "description": "Keep a 7-vote streak on top.gg.",
        "test": lambda d: int(d.get("best_vote_streak", 0)) >= 7,
        "progress": lambda d: (int(d.get("best_vote_streak", 0)), 7),
    },
    "vote_streak_30": {
        "name": "Month of Votes", "emoji": "📅", "icon": "topgg", "reward": 25_000,
        "description": "Keep a 30-vote streak on top.gg.",
        "test": lambda d: int(d.get("best_vote_streak", 0)) >= 30,
        "progress": lambda d: (int(d.get("best_vote_streak", 0)), 30),
    },
    "vote_streak_100": {
        "name": "Unbroken Voter", "emoji": "🛡️", "icon": "topgg", "reward": 150_000,
        "description": "Keep a 100-vote streak on top.gg.",
        "test": lambda d: int(d.get("best_vote_streak", 0)) >= 100,
        "progress": lambda d: (int(d.get("best_vote_streak", 0)), 100),
    },
    # ── Lottery ──────────────────────────────────────────────────────────
    # ``lottery_tickets`` is reset by every draw, so these badges read the
    # lifetime counters instead: what a member has bought, and what they won.
    "lottery_first_ticket": {
        "name": "First Ticket", "emoji": "🎟️", "reward": 250,
        "description": "Buy your first lottery ticket.",
        "test": lambda d: int(d.get("lottery_tickets_bought", 0)) >= 1,
        "progress": lambda d: (int(d.get("lottery_tickets_bought", 0)), 1),
    },
    "lottery_tickets_25": {
        "name": "Ticket Stub", "emoji": "🎫", "reward": 1_000,
        "description": "Buy 25 lottery tickets.",
        "test": lambda d: int(d.get("lottery_tickets_bought", 0)) >= 25,
        "progress": lambda d: (int(d.get("lottery_tickets_bought", 0)), 25),
    },
    "lottery_tickets_100": {
        "name": "Regular Punter", "emoji": "💰", "reward": 5_000,
        "description": "Buy 100 lottery tickets.",
        "test": lambda d: int(d.get("lottery_tickets_bought", 0)) >= 100,
        "progress": lambda d: (int(d.get("lottery_tickets_bought", 0)), 100),
    },
    "lottery_tickets_500": {
        "name": "Pot Chaser", "emoji": "🎯", "reward": 25_000,
        "description": "Buy 500 lottery tickets.",
        "test": lambda d: int(d.get("lottery_tickets_bought", 0)) >= 500,
        "progress": lambda d: (int(d.get("lottery_tickets_bought", 0)), 500),
    },
    "lottery_win_first": {
        "name": "Lucky Winner", "emoji": "🍀", "reward": 2_500,
        "description": "Win the weekly lottery once.",
        "test": lambda d: int(d.get("lottery_wins", 0)) >= 1,
        "progress": lambda d: (int(d.get("lottery_wins", 0)), 1),
    },
    "lottery_wins_3": {
        "name": "Hat Trick", "emoji": "🎉", "reward": 10_000,
        "description": "Win the weekly lottery 3 times.",
        "test": lambda d: int(d.get("lottery_wins", 0)) >= 3,
        "progress": lambda d: (int(d.get("lottery_wins", 0)), 3),
    },
    "lottery_wins_10": {
        "name": "Jackpot Royalty", "emoji": "📣", "reward": 50_000,
        "description": "Win the weekly lottery 10 times.",
        "test": lambda d: int(d.get("lottery_wins", 0)) >= 10,
        "progress": lambda d: (int(d.get("lottery_wins", 0)), 10),
    },
    # ── Seasonal events ──────────────────────────────────────────────────
    # Each window is an inclusive MM-DD range in local time and repeats every
    # year. A seasonal badge is only evaluated while its window is open, and
    # everything it measures is measured *inside* that window, so it cannot be
    # collected — or prepared — off-season. See the measurement note above
    # the badge table for what each ``season_measure`` means.
    "spooky_vault": {
        "name": "Pumpkin Vault", "emoji": "🎃", "reward": 2_500,
        "description": "Hold 25,000 coins in your vault during the Halloween event (Oct 24 – Nov 1).",
        "season": {"label": "Halloween", "start": "10-24", "end": "11-01"},
        "season_measure": "hold",
        "test": lambda d: int(d.get("bank", 0)) >= 25_000,
        "progress": lambda d: (int(d.get("bank", 0)), 25_000),
    },
    "spooky_spender": {
        "name": "Trick or Treat", "emoji": "🍬", "reward": 1_500,
        "description": "Spend 5,000 coins during the Halloween event (Oct 24 – Nov 1).",
        "season": {"label": "Halloween", "start": "10-24", "end": "11-01"},
        "season_measure": "gain",
        "test": lambda d: int(d.get("total_spent", 0)) >= 5_000,
        "progress": lambda d: (int(d.get("total_spent", 0)), 5_000),
    },
    "winter_streak": {
        "name": "Winter Warmth", "emoji": "❄️", "reward": 5_000,
        "description": "Hold a 14-day daily streak during the winter event (Dec 15 – Jan 2).",
        "season": {"label": "Winter", "start": "12-15", "end": "01-02"},
        "season_measure": "hold",
        "test": lambda d: int(d.get("daily_streak", 0)) >= 14,
        "progress": lambda d: (int(d.get("daily_streak", 0)), 14),
    },
    "winter_shopper": {
        "name": "Holiday Shopper", "emoji": "🎁", "reward": 3_000,
        "description": "Spend 25,000 coins during the winter event (Dec 15 – Jan 2).",
        "season": {"label": "Winter", "start": "12-15", "end": "01-02"},
        "season_measure": "gain",
        "test": lambda d: int(d.get("total_spent", 0)) >= 25_000,
        "progress": lambda d: (int(d.get("total_spent", 0)), 25_000),
    },
    "new_year_level": {
        "name": "Midnight Ambition", "emoji": "🎆", "reward": 7_500,
        "description": "Reach career level 25 during the New Year event (Dec 31 – Jan 7).",
        "season": {"label": "New Year", "start": "12-31", "end": "01-07"},
        "season_measure": "reach",
        "test": lambda d: int(d.get("level", 0)) >= 25,
        "progress": lambda d: (int(d.get("level", 0)), 25),
    },
    "valentine_wallet": {
        "name": "Heart of Gold", "emoji": "💝", "reward": 5_000,
        "description": "Keep 50,000 coins in your wallet during the Valentine's event (Feb 10 – Feb 18).",
        "season": {"label": "Valentine's", "start": "02-10", "end": "02-18"},
        "season_measure": "hold",
        "test": lambda d: int(d.get("balance", 0)) >= 50_000,
        "progress": lambda d: (int(d.get("balance", 0)), 50_000),
    },
    "summer_streak": {
        "name": "Summer Streak", "emoji": "🌞", "reward": 5_000,
        "description": "Hold a 30-day daily streak during the summer event (Jun 20 – Sep 5).",
        "season": {"label": "Summer", "start": "06-20", "end": "09-05"},
        "season_measure": "hold",
        "test": lambda d: int(d.get("daily_streak", 0)) >= 30,
        "progress": lambda d: (int(d.get("daily_streak", 0)), 30),
    },
}


def _season_state(data: dict) -> dict:
    """The stored per-season baselines, created on demand."""
    state = data.get("season_progress")
    if not isinstance(state, dict):
        state = {}
        data["season_progress"] = state
    return state


def _season_tracks_change(meta: dict) -> bool:
    """Whether a seasonal badge must be earned *again* inside each window."""
    return (meta.get("season_measure") or "hold") in ("gain", "reach")


def _season_requirement(meta: dict, baseline: int, target: int) -> int:
    """How much the metric has to gain inside the window."""
    if meta.get("season_measure") == "reach":
        # A milestone wants the remaining shortfall; an account already past it
        # still has to take one step during the event rather than collect free.
        return max(1, int(target) - int(baseline))
    return max(1, int(target))


def ensure_season_baselines(data: dict, *, now=None) -> None:
    """Record the value each open seasonal window starts from.

    Called before an economy command acts on the account, so a window's baseline
    is the value it opened with rather than the value left over after the
    action. A baseline is written once per window: a new occurrence gets a new
    key, and an account that has not acted inside the window yet simply has no
    baseline and therefore no in-window progress to claim.
    """
    state = _season_state(data)
    for achievement_id, meta in ACHIEVEMENTS.items():
        if not meta.get("season") or not _season_tracks_change(meta):
            continue
        key = season_open_key(meta, now)
        if key is None:
            continue
        entry = state.get(achievement_id)
        if isinstance(entry, dict) and str(entry.get("window") or "") == key:
            continue
        try:
            value = int(meta["progress"](data)[0])
        except Exception:
            continue
        state[achievement_id] = {"window": key, "value": value}


def seasonal_progress(
    meta: dict,
    data: dict,
    *,
    now=None,
    achievement_id: str | None = None,
) -> tuple[int, int] | None:
    """``(current, target)`` for a seasonal badge, measured inside its window.

    ``None`` for a badge that carries no season, so callers can fall back to the
    plain progress bar. A badge whose window is closed reports ``(0, target)``:
    a seasonal badge cannot be advanced, or even prepared, off-season.
    """
    if not meta.get("season"):
        return None
    try:
        value, target = meta["progress"](data)
    except Exception:
        return None
    value, target = max(0, int(value)), max(1, int(target))
    if season_open_key(meta, now) is None:
        return (0, target)
    if not _season_tracks_change(meta):
        # "hold": the live state *is* the progress while the event is on.
        return (min(value, target), target)

    key = season_open_key(meta, now)
    entry = _season_state(data).get(achievement_id or str(meta.get("name") or ""))
    if not isinstance(entry, dict) or str(entry.get("window") or "") != key:
        # No baseline for this occurrence: there is no in-window gain on record.
        return (0, max(1, target))
    try:
        baseline = int(entry.get("value"))
    except (TypeError, ValueError):
        return (0, max(1, target))
    required = _season_requirement(meta, baseline, target)
    return (max(0, min(value - baseline, required)), required)


def seasonal_earned(
    meta: dict,
    data: dict,
    *,
    now=None,
    achievement_id: str | None = None,
) -> bool:
    """Whether a seasonal badge is earned inside its own window.

    False while the window is closed, and false for an account that has not met
    the window's requirement yet, which is what makes a seasonal badge
    impossible to bank off-season.
    """
    if season_open_key(meta, now) is None:
        return False
    try:
        if not meta["test"](data):
            return False
    except Exception:
        return False
    progress = seasonal_progress(meta, data, now=now, achievement_id=achievement_id)
    if progress is None:
        return False
    current, target = progress
    return current >= target


def achievement_progress(
    meta: dict,
    data: dict,
    *,
    now=None,
    achievement_id: str | None = None,
) -> tuple[int, int]:
    """Return a clamped ``(current, target)`` pair for a badge progress bar.

    A seasonal badge is measured inside its window only (see
    :func:`seasonal_progress`); ``now`` pins the moment for a caller that
    already knows it, and ``achievement_id`` names the badge whose window
    progress is being read.
    """
    seasonal = seasonal_progress(meta, data, now=now, achievement_id=achievement_id)
    if seasonal is not None:
        return seasonal
    try:
        current, target = meta["progress"](data)
    except Exception:
        return (0, 1)
    target = max(1, int(target))
    return (max(0, min(int(current), target)), target)


def _check_achievements(data: dict, *, now=None, lang: str = "en") -> list[str]:
    """Unlock newly earned badges, pay their rewards, list what changed.

    Returns display strings (``"Shift Lead 📋 (+5,000 🪙)"``) so existing
    callers keep working by joining the list into a message. Rewards are
    credited here rather than in the command handlers so every path that
    earns a badge — work, daily, gambling, shopping — pays it exactly once.

    A seasonal badge needs its event to be open *and* its target met inside
    that window, so neither old progress nor an off-season state can collect
    it. ``now`` lets a caller that already knows the moment it is acting on (a
    vote timestamp, a test) pin that decision.
    """
    ensure_season_baselines(data, now=now)
    earned = set(data.get("achievements", []))
    newly = []
    for aid, meta in ACHIEVEMENTS.items():
        if aid in earned:
            continue
        if meta.get("season"):
            if not seasonal_earned(meta, data, now=now, achievement_id=aid):
                continue
        else:
            if not season_open(meta, now):
                continue
            try:
                if not meta["test"](data):
                    continue
            except Exception:
                continue
        earned.add(aid)
        label = achievement_label(meta, aid, lang)
        reward = int(meta.get("reward", 0))
        if reward > 0:
            data["balance"] = int(data.get("balance", 0)) + reward
            data["total_earned"] = int(data.get("total_earned", 0)) + reward
            _log_tx(data, "achievement", reward, achievement_name(aid, meta, lang))
            label += f" (+{reward:,} 🪙)"
        newly.append(label)
    data["achievements"] = sorted(earned)
    return newly


# ── Transaction log ─────────────────────────────────────────────────────────
def _log_tx(data: dict, kind: str, amount: int, note: str = ""):
    txs = data.setdefault("transactions", [])
    txs.insert(0, {
        "ts":     int(time.time()),
        "kind":   kind,
        "amount": int(amount),
        "note":   note[:80],
    })
    del txs[40:]  # cap


# ── Lottery state file ──────────────────────────────────────────────────────
LOTTERY_FILE = "data/economy_data/_lottery.json"


def _load_lottery() -> dict:
    if os.path.exists(LOTTERY_FILE):
        try:
            with open(LOTTERY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"pot": LOTTERY_BASE_POT, "next_draw": int(time.time()) + LOTTERY_DRAW_INTERVAL, "last_winner": None, "last_pot": 0}


def _save_lottery(state: dict) -> None:
    try:
        with open(LOTTERY_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as exc:
        log.error("Economy", f"Could not save lottery state: {exc}")


# ── Database helpers ────────────────────────────────────────────────────────
async def _get_user_from_db(bot, user_id: int) -> dict | None:
    """Get user economy data from database."""
    # Guard against non-integer user IDs (prevents fake record lookups)
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None
    try:
        row = await bot.cxn.fetchrow(
            "SELECT * FROM economy_users WHERE user_id = ?",
            user_id
        )
        if row:
            data = dict(row)
            # Deserialize JSON fields (handle both string and already-deserialized forms)
            for key in ("inventory", "effects", "season_progress", "transactions", "achievements"):
                val = data.get(key)
                if isinstance(val, str):
                    try:
                        data[key] = json.loads(val)
                    except Exception:
                        data[key] = {} if key in _JSON_DICT_FIELDS else []
                elif val is None:
                    data[key] = {} if key in _JSON_DICT_FIELDS else []
                # else: already a dict/list (MongoDB mode), keep as-is
            data = _migrate_user(data)
            # The window baseline has to be the value the account had *before*
            # the command that is about to run, so it is recorded here — on every
            # load — rather than when the action is already applied.
            ensure_season_baselines(data)
            return data
    except Exception as e:
        log.error("Economy", f"Error fetching user {user_id} from database: {e}")
    return None


# JSON columns that hold a mapping rather than a list.
_JSON_DICT_FIELDS = ("inventory", "effects", "season_progress")


async def _save_user_to_db(bot, user_id: int, data: dict) -> None:
    """Save user economy data to database."""
    # Guard against non-integer user IDs (prevents fake record creation)
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        log.error("Economy", f"Refusing to save economy data for non-integer user_id: {user_id!r}")
        return
    try:
        _migrate_user(data)
        
        # Serialize complex fields
        inventory_json = json.dumps(data.get("inventory", {}))
        effects_json = json.dumps(data.get("effects", {}))
        transactions_json = json.dumps(data.get("transactions", []))
        achievements_json = json.dumps(data.get("achievements", []))
        season_progress_json = json.dumps(data.get("season_progress", {}))
        
        # Calculate net worth
        net_worth = int(data.get("balance", 0)) + int(data.get("bank", 0))
        
        # The value list and the placeholders are built together: INSERT OR
        # REPLACE rewrites the whole row, so a column added to one side and not
        # the other would silently reset that field on the next command.
        values = [
            user_id,
            data.get("balance", 100),
            data.get("bank", 0),
            net_worth,
            int(bool(data.get("leaderboard_private", False))),
            data.get("total_earned", 100),
            data.get("total_spent", 0),
            data.get("xp", 0),
            data.get("level", 0),
            data.get("job", "barista"),
            data.get("times_worked", 0),
            data.get("bank_tier", 0),
            data.get("last_interest", 0),
            data.get("last_interest_day"),
            data.get("daily_streak", 0),
            data.get("last_daily", 0),
            data.get("last_work", 0),
            data.get("last_crime", 0),
            data.get("last_rob", 0),
            data.get("last_heist", 0),
            data.get("last_slots", 0),
            data.get("last_blackjack", 0),
            data.get("last_roulette", 0),
            data.get("last_casino", 0),
            data.get("last_gamble", 0),
            data.get("last_bet", 0),
            data.get("last_race", 0),
            data.get("last_fight", 0),
            data.get("last_duel", 0),
            inventory_json,
            effects_json,
            data.get("lottery_tickets", 0),
            int(data.get("lottery_tickets_bought", 0)),
            int(data.get("lottery_wins", 0)),
            transactions_json,
            achievements_json,
            season_progress_json,
            # Vote state is written on every save, so it must be listed here:
            # an omitted column would silently reset the streak on the next
            # economy command.
            int(data.get("votes", 0)),
            int(data.get("vote_streak", 0)),
            int(data.get("best_vote_streak", 0)),
            int(data.get("last_vote", 0)),
        ]
        await bot.cxn.execute(f"""
            INSERT OR REPLACE INTO economy_users (
                user_id, balance, bank, net_worth, leaderboard_private, total_earned, total_spent,
                xp, level, job, times_worked, bank_tier, last_interest,
                last_interest_day, daily_streak, last_daily, last_work,
                last_crime, last_rob, last_heist, last_slots, last_blackjack,
                last_roulette, last_casino, last_gamble, last_bet, last_race,
                last_fight, last_duel, inventory, effects, lottery_tickets,
                lottery_tickets_bought, lottery_wins,
                transactions, achievements, season_progress, votes, vote_streak,
                best_vote_streak, last_vote
            ) VALUES ({', '.join(['?'] * len(values))})
        """, *values)
    except Exception as e:
        log.error("Economy", f"Could not save user {user_id} to database: {e}")


async def _get_lottery_from_db(bot) -> dict:
    """Get lottery state from database."""
    try:
        row = await bot.cxn.fetchrow(
            "SELECT * FROM economy_lottery WHERE id = 1"
        )
        if row:
            # In MongoDB mode, row values are already their native types
            return {
                "pot": row.get("pot", LOTTERY_BASE_POT),
                "next_draw": row.get("next_draw", int(time.time()) + LOTTERY_DRAW_INTERVAL),
                "last_winner": row.get("last_winner"),
                "last_pot": row.get("last_pot", 0)
            }
    except Exception as e:
        log.error("Economy", f"Error fetching lottery from database: {e}")
    return {"pot": LOTTERY_BASE_POT, "next_draw": int(time.time()) + LOTTERY_DRAW_INTERVAL, "last_winner": None, "last_pot": 0}


async def _save_lottery_to_db(bot, state: dict) -> None:
    """Save lottery state to database."""
    try:
        await bot.cxn.execute("""
            UPDATE economy_lottery
            SET pot = ?, next_draw = ?, last_winner = ?, last_pot = ?
            WHERE id = 1
        """,
            state.get("pot", LOTTERY_BASE_POT),
            state.get("next_draw", int(time.time()) + LOTTERY_DRAW_INTERVAL),
            state.get("last_winner"),
            state.get("last_pot", 0)
        )
    except Exception as e:
        log.error("Economy", f"Could not save lottery to database: {e}")


async def _get_all_users_from_db(bot) -> dict:
    """Get all users from database for ranking."""
    try:
        rows = await bot.cxn.fetch("SELECT user_id, balance, bank FROM economy_users")
        return {str(row["user_id"]): {"balance": row["balance"], "bank": row["bank"]} for row in rows}
    except Exception as e:
        log.error("Economy", f"Error fetching all users from database: {e}")
    return {}


# ── Small layout helpers ────────────────────────────────────────────────────
# The brand accent every other Niko view uses (staff, support server, nitro,
# transcripts), so economy containers are no longer their own bespoke colour.
ACCENT_BROWN = discord.Colour(0xC8A882)


# Animated card-shaped placeholders generated by
# `scripts/generate_economy_loading_cards.py` and served from the public site.
# Each name is one of the economy image-card renderers below, so the loading
# card the member sees while a render is in flight has the same shape as the
# finished PNG that replaces it.
LOADING_CARD_TYPES = frozenset({"balance", "reward", "shop", "inventory", "leaderboard"})


def _loading_cards_base() -> str:
    """Origin that serves the generated loading cards.

    ``PUBLIC_URL`` names the site a deployment is reachable on, so a beta
    instance loads its own copy of the GIFs instead of production's. The
    canonical website is the fallback when the variable is unset or blank.
    """
    origin = os.environ.get("PUBLIC_URL", "").strip().rstrip("/")
    return f"{origin or WEBSITE}/assets/loading-cards/economy"


def _shop_loading_file(rows: int | None) -> str:
    """The shop loading GIF that matches a card with *rows* item rows.

    ``scripts/generate_economy_loading_cards.py`` writes ``shop.gif`` for the
    whole catalogue and ``shop-<rows>.gif`` for each category, so the
    placeholder is exactly as tall as the finished card and the edit that
    swaps them in does not resize the message. An unknown row count falls back
    to the next generated size that can hold it.
    """
    available = shop_loading_row_counts()
    largest = max(available)
    if rows is None:
        return "shop.gif"
    try:
        wanted = max(1, int(rows))
    except (TypeError, ValueError):
        return "shop.gif"
    if wanted >= largest:
        return "shop.gif"
    matched = next((count for count in available if count >= wanted), largest)
    return "shop.gif" if matched == largest else f"shop-{matched}.gif"


def _loading_card_view(
    card_type: str,
    *,
    lang: str = "en",
    rows: int | None = None,
    shop_controls: bool = False,
) -> discord.ui.LayoutView:
    """A remote animated loading card for *card_type*.

    The GIF is hosted by the public website rather than uploaded with the
    message, so the loading state costs no attachment and appears instantly.
    The finished card then replaces it in the same message (see
    ``EconomyCog._show_loading_card``).

    ``rows`` picks the shop GIF that is exactly as tall as the card about to
    be rendered, and ``shop_controls`` adds the Buy/Sell buttons in a disabled
    state, so the shop message keeps the same shape while it loads.
    """
    card_type = str(card_type).lower()
    if card_type not in LOADING_CARD_TYPES:
        raise ValueError(f"Unknown economy loading card type: {card_type!r}")
    file_name = f"{card_type}.gif"
    if card_type == "shop":
        file_name = _shop_loading_file(rows)
    view = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.MediaGallery(discord.MediaGalleryItem(
            media=f"{_loading_cards_base()}/{file_name}",
        )),
        accent_colour=ACCENT_BROWN,
    )
    if shop_controls:
        # Same hint and buttons as `_ShopActionView`, only disabled until the
        # card is ready — the layout does not jump when the card arrives.
        container.add_item(discord.ui.TextDisplay(content=_SHOP_T(lang, "hint_action")))
        container.add_item(discord.ui.ActionRow(
            discord.ui.Button(label=_SHOP_T(lang, "btn_buy"), style=discord.ButtonStyle.success, disabled=True),
            discord.ui.Button(label=_SHOP_T(lang, "btn_sell"), style=discord.ButtonStyle.secondary, disabled=True),
        ))
    view.add_item(container)
    return view


def _info_view(title: str, body: str, accent: discord.Colour = ACCENT_BROWN) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {title}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=body),
        accent_colour=accent,
    )
    view.add_item(container)
    return view


def _card_view(title: str, image_name: str, footer_lines: list[str], accent: discord.Colour = ACCENT_BROWN) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {title}"),
        discord.ui.MediaGallery(discord.MediaGalleryItem(media=f"attachment://{image_name}")),
        accent_colour=accent,
    )
    if footer_lines:
        container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        for line in footer_lines:
            container.add_item(discord.ui.TextDisplay(content=line))
    view.add_item(container)
    return view


def _fmt_remaining(seconds: int) -> str:
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m}m"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


# ─────────────────────────────────────────────────────────────────────────────
# Cog
# ─────────────────────────────────────────────────────────────────────────────



__all__ = [k for k in list(globals()) if not k.startswith("__")]
