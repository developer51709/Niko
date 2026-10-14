# economy.py — premium café economy cog
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
from utils.ai.config import get_personality
from utils.i18n import make_msg
from config.emojis import get_emoji
from utils.economy_jobs import (
    JOBS, DEFAULT_JOB, get_job,
    SHOP_ITEMS, get_item,
    BANK_TIERS, bank_info, bank_cap, bank_name, bank_rate, max_bank_tier,
    xp_to_next, total_xp_for_level, level_from_total_xp, add_xp,
    LOTTERY_TICKET_PRICE, LOTTERY_DRAW_INTERVAL, LOTTERY_HOUSE_RAKE, LOTTERY_BASE_POT,
    COOLDOWN_DAILY, COOLDOWN_WORK, COOLDOWN_CRIME, COOLDOWN_ROB,
)
from utils.image.economy_card import (
    render_balance_card, render_reward_card, render_leaderboard_card,
    fetch_avatar_bytes,
    ACCENT_GOLD, ACCENT_GREEN, ACCENT_RED,
)

# ── Bilingual messages ───────────────────────────────────────────────────────
MESSAGES = {
    "normal": {
        "en": {
            "daily_wait":     "You can only claim your daily reward once every 24 hours.",
            "daily_success":  "You claimed your daily reward of {reward} coins!",
            "work_wait":      "You can only work once every hour.",
            "work_success":   "You worked and earned {reward} coins!",
            "level_up":       "You leveled up! You are now level {level}.",
        },
        "de": {
            "daily_wait":     "Du kannst deine tägliche Belohnung nur alle 24 Stunden abholen.",
            "daily_success":  "Du hast deine tägliche Belohnung von {reward} Münzen abgeholt!",
            "work_wait":      "Du kannst nur einmal pro Stunde arbeiten.",
            "work_success":   "Du hast gearbeitet und {reward} Münzen verdient!",
            "level_up":       "Du bist aufgestiegen! Du bist jetzt Level {level}.",
        },
        "es": {
            "daily_wait":     "Solo puedes reclamar tu recompensa diaria una vez cada 24 horas.",
            "daily_success":  "¡Has reclamado tu recompensa diaria de {reward} monedas!",
            "work_wait":      "Solo puedes trabajar una vez cada hora.",
            "work_success":   "¡Trabajaste y ganaste {reward} monedas!",
            "level_up":       "¡Has subido de nivel! Ahora eres nivel {level}.",
        },
    },
}


msg = make_msg(MESSAGES)


# ── Prefix resolver (used by tip text in cards) ──────────────────────────────
async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    raw = bot.command_prefix
    if isinstance(raw, str):
        return raw
    if isinstance(raw, (list, tuple)):
        return raw[0]
    try:
        message = getattr(ctx_or_interaction, "message", None)
        if message is None and isinstance(ctx_or_interaction, discord.Interaction):
            message = ctx_or_interaction.message
        if message is None:
            return "."
        prefixes = raw(bot, message)
        if isinstance(prefixes, (list, tuple)) and prefixes:
            return prefixes[0]
    except Exception:
        pass
    return "."


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
        # top.gg voting (see cogs/economy/voting.py)
        "votes":            0,
        "vote_streak":      0,
        "best_vote_streak": 0,
        "last_vote":        0,
        # transaction log (most recent first, capped)
        "transactions":  [],
        # achievements (list of ids)
        "achievements":  [],
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

    # always recompute net worth on access
    data["net_worth"] = int(data.get("balance", 0)) + int(data.get("bank", 0))
    return data


# ── Achievements ────────────────────────────────────────────────────────────
# Every entry carries:
#   name / emoji / description  how the badge is presented in the bot and web
#   test(data)                  whether the badge is earned
#   progress(data)              (current, target) for the dashboard bars
#   reward                      coins paid ONCE, the moment the badge unlocks
#
# The reward is why this table is data instead of prose: the balance is
# credited exactly when the id joins ``data["achievements"]``, and that stored
# id list is what stops a second payout on the next save.
ACHIEVEMENTS = {
    # ── Working ──────────────────────────────────────────────────────────
    "first_paycheck": {
        "name": "First Paycheck", "emoji": "💼", "reward": 250,
        "description": "Work your very first shift at the café.",
        "test": lambda d: d["times_worked"] >= 1,
        "progress": lambda d: (d["times_worked"], 1),
    },
    "regular": {
        "name": "Café Regular", "emoji": "☕", "reward": 1_000,
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
    "millionaire": {
        "name": "Millionaire", "emoji": "💰", "reward": 50_000,
        "description": "Reach a net worth of 1,000,000 coins.",
        "test": lambda d: d["net_worth"] >= 1_000_000,
        "progress": lambda d: (d["net_worth"], 1_000_000),
    },
    # ── Daily streak ─────────────────────────────────────────────────────
    "streak_7": {
        "name": "Week-long Habit", "emoji": "🔥", "reward": 1_000,
        "description": "Claim your daily treats 7 days in a row.",
        "test": lambda d: d["daily_streak"] >= 7,
        "progress": lambda d: (d["daily_streak"], 7),
    },
    "streak_30": {
        "name": "Café Devotee", "emoji": "🌟", "reward": 10_000,
        "description": "Claim your daily treats 30 days in a row.",
        "test": lambda d: d["daily_streak"] >= 30,
        "progress": lambda d: (d["daily_streak"], 30),
    },
    "streak_60": {
        "name": "Dedicated Regular", "emoji": "💎", "reward": 25_000,
        "description": "Claim your daily treats 60 days in a row.",
        "test": lambda d: d["daily_streak"] >= 60,
        "progress": lambda d: (d["daily_streak"], 60),
    },
    "streak_90": {
        "name": "Economy Legend", "emoji": "🏆", "reward": 100_000,
        "description": "Claim your daily treats 90 days in a row.",
        "test": lambda d: d["daily_streak"] >= 90,
        "progress": lambda d: (d["daily_streak"], 90),
    },
    # ── Career and spending ──────────────────────────────────────────────
    "owner": {
        "name": "Café Owner", "emoji": "👑", "reward": 25_000,
        "description": "Reach the top of the job ladder.",
        "test": lambda d: d.get("job") == "owner",
        "progress": lambda d: (1 if d.get("job") == "owner" else 0, 1),
    },
    "gambler": {
        "name": "High Roller", "emoji": "🎰", "reward": 2_500,
        "description": "Spend 50,000 coins across the café.",
        "test": lambda d: int(d.get("total_spent", 0)) >= 50_000,
        "progress": lambda d: (int(d.get("total_spent", 0)), 50_000),
    },
    "whale": {
        "name": "Casino Whale", "emoji": "🐋", "reward": 25_000,
        "description": "Spend 500,000 coins across the café.",
        "test": lambda d: int(d.get("total_spent", 0)) >= 500_000,
        "progress": lambda d: (int(d.get("total_spent", 0)), 500_000),
    },
    "earner": {
        "name": "Big Earner", "emoji": "📈", "reward": 25_000,
        "description": "Earn 1,000,000 coins in total.",
        "test": lambda d: int(d.get("total_earned", 0)) >= 1_000_000,
        "progress": lambda d: (int(d.get("total_earned", 0)), 1_000_000),
    },
    # ── top.gg voting ────────────────────────────────────────────────────
    "voter_first": {
        "name": "First Upvote", "emoji": "🗳️", "reward": 500,
        "description": "Vote for Niko on top.gg once.",
        "test": lambda d: int(d.get("votes", 0)) >= 1,
        "progress": lambda d: (int(d.get("votes", 0)), 1),
    },
    "voter_regular": {
        "name": "Vote Regular", "emoji": "📬", "reward": 2_500,
        "description": "Vote for Niko on top.gg 10 times.",
        "test": lambda d: int(d.get("votes", 0)) >= 10,
        "progress": lambda d: (int(d.get("votes", 0)), 10),
    },
    "voter_devoted": {
        "name": "Ballot Stuffer", "emoji": "🧾", "reward": 10_000,
        "description": "Vote for Niko on top.gg 50 times.",
        "test": lambda d: int(d.get("votes", 0)) >= 50,
        "progress": lambda d: (int(d.get("votes", 0)), 50),
    },
    "voter_legend": {
        "name": "Civic Legend", "emoji": "🏛️", "reward": 50_000,
        "description": "Vote for Niko on top.gg 200 times.",
        "test": lambda d: int(d.get("votes", 0)) >= 200,
        "progress": lambda d: (int(d.get("votes", 0)), 200),
    },
    "vote_streak_7": {
        "name": "Week of Votes", "emoji": "🗓️", "reward": 5_000,
        "description": "Keep a 7-vote streak on top.gg.",
        "test": lambda d: int(d.get("best_vote_streak", 0)) >= 7,
        "progress": lambda d: (int(d.get("best_vote_streak", 0)), 7),
    },
    "vote_streak_30": {
        "name": "Month of Votes", "emoji": "📅", "reward": 25_000,
        "description": "Keep a 30-vote streak on top.gg.",
        "test": lambda d: int(d.get("best_vote_streak", 0)) >= 30,
        "progress": lambda d: (int(d.get("best_vote_streak", 0)), 30),
    },
    "vote_streak_100": {
        "name": "Unbroken Voter", "emoji": "🛡️", "reward": 150_000,
        "description": "Keep a 100-vote streak on top.gg.",
        "test": lambda d: int(d.get("best_vote_streak", 0)) >= 100,
        "progress": lambda d: (int(d.get("best_vote_streak", 0)), 100),
    },
}


def achievement_progress(meta: dict, data: dict) -> tuple[int, int]:
    """Return a clamped ``(current, target)`` pair for a badge progress bar."""
    try:
        current, target = meta["progress"](data)
    except Exception:
        return (0, 1)
    target = max(1, int(target))
    return (max(0, min(int(current), target)), target)


def _check_achievements(data: dict) -> list[str]:
    """Unlock newly earned badges, pay their rewards, list what changed.

    Returns display strings (``"Shift Lead 📋 (+5,000 🥐)"``) so existing
    callers keep working by joining the list into a message. Rewards are
    credited here rather than in the command handlers so every path that
    earns a badge — work, daily, gambling, shopping — pays it exactly once.
    """
    earned = set(data.get("achievements", []))
    newly = []
    for aid, meta in ACHIEVEMENTS.items():
        if aid in earned:
            continue
        try:
            if not meta["test"](data):
                continue
        except Exception:
            continue
        earned.add(aid)
        label = f"{meta['name']} {meta['emoji']}"
        reward = int(meta.get("reward", 0))
        if reward > 0:
            data["balance"] = int(data.get("balance", 0)) + reward
            data["total_earned"] = int(data.get("total_earned", 0)) + reward
            _log_tx(data, "achievement", reward, meta["name"])
            label += f" (+{reward:,} 🥐)"
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
            for key in ("inventory", "effects", "transactions", "achievements"):
                val = data.get(key)
                if isinstance(val, str):
                    try:
                        data[key] = json.loads(val)
                    except Exception:
                        data[key] = {} if key in ("inventory", "effects") else []
                elif val is None:
                    data[key] = {} if key in ("inventory", "effects") else []
                # else: already a dict/list (MongoDB mode), keep as-is
            return _migrate_user(data)
    except Exception as e:
        log.error("Economy", f"Error fetching user {user_id} from database: {e}")
    return None


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
        
        # Calculate net worth
        net_worth = int(data.get("balance", 0)) + int(data.get("bank", 0))
        
        await bot.cxn.execute("""
            INSERT OR REPLACE INTO economy_users (
                user_id, balance, bank, net_worth, leaderboard_private, total_earned, total_spent,
                xp, level, job, times_worked, bank_tier, last_interest,
                last_interest_day, daily_streak, last_daily, last_work,
                last_crime, last_rob, last_heist, last_slots, last_blackjack,
                last_roulette, last_casino, last_gamble, last_bet, last_race,
                last_fight, last_duel, inventory, effects, lottery_tickets,
                transactions, achievements, votes, vote_streak,
                best_vote_streak, last_vote
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
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
            transactions_json,
            achievements_json,
            # Vote state is written on every save, so it must be listed here:
            # INSERT OR REPLACE rewrites the whole row, and an omitted column
            # would silently reset the streak on the next economy command.
            int(data.get("votes", 0)),
            int(data.get("vote_streak", 0)),
            int(data.get("best_vote_streak", 0)),
            int(data.get("last_vote", 0))
        )
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
# transcripts), so economy containers are no longer their own café colour.
ACCENT_BROWN = discord.Colour(0xC8A882)


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
