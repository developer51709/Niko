"""
Economy catalogs and helpers.

Centralizes the JOB ladder, the SHOP_ITEMS catalog, the BANK tier table
and the XP/level math used by `cogs/economy.py`.

Everything here is plain data + pure functions so it can be safely imported
from cogs and image renderers without circular deps.
"""

from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────
# Career / job ladder
#
# Each job entry:
#   name            display name
#   emoji           glyph used in image cards & text
#   min_level       career level required to apply
#   min_pay/max_pay random reward range per shift (cash)
#   xp_per_shift    base XP awarded per shift
#   cooldown        seconds between shifts (defaults to 3600 if missing)
#   description     short blurb shown in `job info`
# ──────────────────────────────────────────────────────────────────────────

JOBS: dict[str, dict] = {
    "barista": {
        "name": "Barista",
        "emoji": "☕",
        "min_level": 0,
        "min_pay": 80,
        "max_pay": 220,
        "xp_per_shift": 12,
        "cooldown": 3600,
        "description": "Pour cozy lattes for the regulars and earn steady tips.",
    },
    "baker": {
        "name": "Baker",
        "emoji": "🥐",
        "min_level": 5,
        "min_pay": 180,
        "max_pay": 380,
        "xp_per_shift": 18,
        "cooldown": 3600,
        "description": "Bake fresh croissants before sunrise. The smell sells itself.",
    },
    "manager": {
        "name": "Shift Manager",
        "emoji": "📋",
        "min_level": 15,
        "min_pay": 320,
        "max_pay": 620,
        "xp_per_shift": 28,
        "cooldown": 3600,
        "description": "Run the floor, train the new hires, count the till.",
    },
    "trader": {
        "name": "Café Trader",
        "emoji": "📈",
        "min_level": 30,
        "min_pay": 450,
        "max_pay": 1100,
        "xp_per_shift": 42,
        "cooldown": 3600,
        "description": "Trade coffee bean futures from the back office.",
    },
    "owner": {
        "name": "Café Owner",
        "emoji": "👑",
        "min_level": 50,
        "min_pay": 800,
        "max_pay": 2200,
        "xp_per_shift": 60,
        "cooldown": 3600,
        "description": "It's your café now. Take a cut of everything.",
    },
}

DEFAULT_JOB = "barista"


def get_job(job_id: str | None) -> dict:
    """Return the job dict for the given id (always returns *something*)."""
    return JOBS.get((job_id or DEFAULT_JOB).lower(), JOBS[DEFAULT_JOB])


# ──────────────────────────────────────────────────────────────────────────
# Shop catalog
#
# Categories:
#   consumable  → one-shot effect, removed on use
#   upgrade     → permanent upgrade (e.g. bank tier), removed on use
#   collectible → cosmetic, kept in inventory, shown on profile
#
# Effects (applied by the `use` command):
#   work_cooldown_half    halves the next work cooldown
#   crime_boost           +25 percentage points on next crime success
#   rob_shield            blocks the next rob attempt against you
#   lottery_boost         doubles the next lottery ticket purchase
#   bank_tier_up          advances bank tier by 1 (capped at top tier)
#   xp_potion             +75 bonus XP immediately
# ──────────────────────────────────────────────────────────────────────────

SHOP_ITEMS: dict[str, dict] = {
    # ── Consumables ────────────────────────────────────────────────
    "espresso_shot": {
        "name": "Espresso Shot",
        "emoji": "☕",
        "category": "consumable",
        "price": 250,
        "sell": 90,
        "min_level": 0,
        "effect": "work_cooldown_half",
        "description": "Cuts your next work cooldown in half. Wakey wakey.",
    },
    "lockpick": {
        "name": "Lockpick",
        "emoji": "🔓",
        "category": "consumable",
        "price": 800,
        "sell": 280,
        "min_level": 3,
        "effect": "crime_boost",
        "description": "+25% crime success on your next attempt. Don't get caught.",
    },
    "rob_shield": {
        "name": "Tip Jar Lock",
        "emoji": "🛡️",
        "category": "consumable",
        "price": 1200,
        "sell": 400,
        "min_level": 5,
        "effect": "rob_shield",
        "description": "Blocks the next attempted robbery against you.",
    },
    "lucky_charm": {
        "name": "Lucky Charm",
        "emoji": "🍀",
        "category": "consumable",
        "price": 1500,
        "sell": 500,
        "min_level": 8,
        "effect": "lottery_boost",
        "description": "Doubles your next lottery ticket purchase.",
    },
    "xp_potion": {
        "name": "Career Brew",
        "emoji": "🧪",
        "category": "consumable",
        "price": 2000,
        "sell": 700,
        "min_level": 2,
        "effect": "xp_potion",
        "description": "Instantly gain 75 career XP.",
    },
    # ── Upgrades ───────────────────────────────────────────────────
    "vault_upgrade": {
        "name": "Vault Upgrade",
        "emoji": "🏦",
        "category": "upgrade",
        "price": 7500,
        "sell": 2500,
        "min_level": 4,
        "effect": "bank_tier_up",
        "description": "Promotes your bank to the next tier. Higher cap, more interest.",
    },
    # ── Collectibles ───────────────────────────────────────────────
    "regular_badge": {
        "name": "Café Regular Badge",
        "emoji": "🎖️",
        "category": "collectible",
        "price": 5000,
        "sell": 1500,
        "min_level": 0,
        "description": "Show everyone you're a regular here.",
    },
    "golden_mug": {
        "name": "Golden Mug",
        "emoji": "🏆",
        "category": "collectible",
        "price": 25000,
        "sell": 8000,
        "min_level": 10,
        "description": "A gleaming gold-plated mug for your shelf.",
    },
    "diamond_croissant": {
        "name": "Diamond Croissant",
        "emoji": "💎",
        "category": "collectible",
        "price": 100000,
        "sell": 30000,
        "min_level": 25,
        "description": "A diamond-encrusted croissant. Pure flex, zero calories.",
    },
}


def get_item(item_id: str) -> dict | None:
    return SHOP_ITEMS.get((item_id or "").lower())


# ──────────────────────────────────────────────────────────────────────────
# Bank tiers
#
# Tier index → (cap, name, daily_interest_rate)
# Daily interest is applied to bank balance (capped at cap) once per UTC day.
# ──────────────────────────────────────────────────────────────────────────

BANK_TIERS: list[tuple[int, str, float]] = [
    (10_000,     "Tin Jar",       0.005),   # 0.5%/day
    (50_000,     "Wooden Chest",  0.0075),  # 0.75%
    (250_000,    "Steel Vault",   0.01),    # 1.0%
    (1_000_000,  "Crystal Safe",  0.0125),  # 1.25%
    (10_000_000, "Diamond Vault", 0.015),   # 1.5%
]


def bank_info(tier: int) -> tuple[int, str, float]:
    tier = max(0, min(tier, len(BANK_TIERS) - 1))
    return BANK_TIERS[tier]


def bank_cap(tier: int) -> int:
    return bank_info(tier)[0]


def bank_name(tier: int) -> str:
    return bank_info(tier)[1]


def bank_rate(tier: int) -> float:
    return bank_info(tier)[2]


def max_bank_tier() -> int:
    return len(BANK_TIERS) - 1


# ──────────────────────────────────────────────────────────────────────────
# XP / level math
#
# XP needed to advance from level N → N+1: 100 + 50*N
# So total XP for level N = sum_{i=0..N-1}(100 + 50*i) = 100N + 25N(N-1)
# ──────────────────────────────────────────────────────────────────────────


def xp_to_next(level: int) -> int:
    return 100 + 50 * max(0, level)


def total_xp_for_level(level: int) -> int:
    n = max(0, level)
    return 100 * n + 25 * n * (n - 1)


def level_from_total_xp(total_xp: int) -> int:
    """Inverse: highest L such that total_xp_for_level(L) <= total_xp."""
    if total_xp <= 0:
        return 0
    lvl = 0
    while total_xp_for_level(lvl + 1) <= total_xp:
        lvl += 1
        if lvl > 999:
            break
    return lvl


def add_xp(data: dict, gained: int) -> tuple[int, int, bool]:
    """
    Apply XP gain to a user data dict (mutates `xp` and `level`).
    Returns (new_level, levels_gained, did_level_up).
    """
    old_level = int(data.get("level", 0))
    new_total = int(data.get("xp", 0)) + max(0, int(gained))
    data["xp"] = new_total
    new_level = level_from_total_xp(new_total)
    data["level"] = new_level
    return new_level, max(0, new_level - old_level), new_level > old_level


# ──────────────────────────────────────────────────────────────────────────
# Lottery
# ──────────────────────────────────────────────────────────────────────────

LOTTERY_TICKET_PRICE = 200
LOTTERY_DRAW_INTERVAL = 7 * 86400      # 1 week
LOTTERY_HOUSE_RAKE   = 0.10            # 10% of pool stays as base for next round
LOTTERY_BASE_POT     = 5_000           # seed for the very first draw


# ──────────────────────────────────────────────────────────────────────────
# Cooldowns shared across commands (seconds)
# ──────────────────────────────────────────────────────────────────────────

COOLDOWN_DAILY  = 86400
COOLDOWN_WORK   = 3600
COOLDOWN_CRIME  = 3600
COOLDOWN_ROB    = 3600
