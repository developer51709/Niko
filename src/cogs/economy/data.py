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
    "cafe": {
        "en": {
            "daily_wait":     "patience, bestie! your daily treats aren't ready yet ☕🍰",
            "daily_success":  "yesss! you got your daily {reward} coins. go buy something cute! 🍬✨",
            "work_wait":      "you're working too hard! take a coffee break ☕💤",
            "work_success":   "good job! you worked a shift and earned {reward} coins for the tip jar 🍯✨",
            "level_up":       "level up! you're now level {level} ✨ keep grinding bestie",
        },
        "de": {
            "daily_wait":     "Geduld, Liebes! Deine täglichen Leckereien sind noch nicht fertig ☕🍰",
            "daily_success":  "yesss! Du hast deine täglichen {reward} Münzen bekommen 🍬✨",
            "work_wait":      "Du arbeitest zu hart! Mach eine Kaffeepause ☕💤",
            "work_success":   "Gute Arbeit! Du hast eine Schicht gearbeitet und {reward} Münzen verdient 🍯✨",
            "level_up":       "Aufstieg! Du bist jetzt Level {level} ✨",
        },
        "es": {
            "daily_wait":     "¡paciencia, amix! tus delicias diarias aún no están listas ☕🍰",
            "daily_success":  "¡yesss! recibiste tus {reward} monedas diarias 🍬✨",
            "work_wait":      "¡estás trabajando demasiado! tómate un descanso ☕💤",
            "work_success":   "¡buen trabajo! ganaste {reward} monedas para el bote de propinas 🍯✨",
            "level_up":       "¡subiste de nivel! ahora eres nivel {level} ✨",
        },
    },
}


def get_lang(ctx) -> str:
    if ctx and getattr(ctx, "guild", None) and getattr(ctx.guild, "preferred_locale", None):
        loc = str(ctx.guild.preferred_locale).lower()
        if loc.startswith("de"):
            return "de"
        if loc.startswith("es"):
            return "es"
    return "en"


def msg(ctx, key: str, **kwargs) -> str:
    personality = get_personality(ctx)
    lang = get_lang(ctx)
    text = MESSAGES.get(personality, {}).get(lang, {}).get(key)
    if text is None:
        text = MESSAGES["normal"].get(lang, {}).get(key, key)
    return text.format(**kwargs) if kwargs else text


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
ACHIEVEMENTS = {
    "first_paycheck": {"name": "First Paycheck",   "emoji": "💼", "test": lambda d: d["times_worked"] >= 1},
    "regular":        {"name": "Café Regular",     "emoji": "☕", "test": lambda d: d["times_worked"] >= 25},
    "shift_lead":     {"name": "Shift Lead",       "emoji": "📋", "test": lambda d: d["times_worked"] >= 100},
    "saver":          {"name": "Tin-Jar Saver",    "emoji": "🪙", "test": lambda d: d["bank"] >= 10_000},
    "vault_keeper":   {"name": "Vault Keeper",     "emoji": "🏦", "test": lambda d: d["bank"] >= 100_000},
    "millionaire":    {"name": "Millionaire",      "emoji": "💰", "test": lambda d: d["net_worth"] >= 1_000_000},
    "streak_7":       {"name": "Week-long Habit",  "emoji": "🔥", "test": lambda d: d["daily_streak"] >= 7},
    "streak_30":      {"name": "Café Devotee",     "emoji": "🌟", "test": lambda d: d["daily_streak"] >= 30},
    "owner":          {"name": "Café Owner",       "emoji": "👑", "test": lambda d: d.get("job") == "owner"},
}


def _check_achievements(data: dict) -> list[str]:
    """Return a list of newly-unlocked achievement names (mutates `data`)."""
    earned = set(data.get("achievements", []))
    newly = []
    for aid, meta in ACHIEVEMENTS.items():
        if aid in earned:
            continue
        try:
            if meta["test"](data):
                earned.add(aid)
                newly.append(meta["name"] + " " + meta["emoji"])
        except Exception:
            continue
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


# ── Small layout helpers ────────────────────────────────────────────────────
ACCENT_BROWN = discord.Colour(0xC8853F)


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
