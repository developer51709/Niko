"""
Startup handler for the Discord bot.
Moved from bot.py — all logic that runs once on on_ready lives here.
"""

import os
import re
import sys
import json
import asyncio
import datetime
import importlib

import colorama
import discord
from discord.ext import commands

import database
from utils import logging
from utils.emoji_sync import sync_application_emojis

# ─────────────────────────────────────────────────────────────────────────────
# ANSI helpers (mirrored from bot.py for the banner)
# ─────────────────────────────────────────────────────────────────────────────
_ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')

def _vis(s: str) -> int:
    return len(_ANSI_RE.sub('', s))


# ─────────────────────────────────────────────────────────────────────────────
# Database setup
# ─────────────────────────────────────────────────────────────────────────────
DATABASE_PATH = "data/database.db"


async def _create_tables(bot):
    if not bot.cxn:
        return

    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS voicemaster_settings (
            guild_id          INTEGER PRIMARY KEY,
            join_channel_id   INTEGER,
            category_id       INTEGER,
            default_name      TEXT DEFAULT '{user}''s Channel',
            default_limit     INTEGER DEFAULT 0,
            default_bitrate   INTEGER DEFAULT 64000,
            default_region    TEXT,
            interface_enabled INTEGER DEFAULT 1,
            auto_role         INTEGER,
            join_role         INTEGER
        )
    """)
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS voicemaster_channels (
            channel_id  INTEGER PRIMARY KEY,
            owner_id    INTEGER NOT NULL,
            guild_id    INTEGER NOT NULL,
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS follows (
            guild_id     INTEGER,
            platform     TEXT,
            username     TEXT,
            channel_id   INTEGER,
            template     TEXT,
            last_post_id TEXT,
            PRIMARY KEY  (guild_id, platform, username)
        )
    """)
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS youtube (
            channel_id TEXT PRIMARY KEY,
            last_video TEXT
        )
    """)
    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS youtube_history (
            channel_id TEXT,
            video_id   TEXT,
            PRIMARY KEY (channel_id, video_id)
        )
    """)

    await bot.cxn.execute("""
        INSERT OR IGNORE INTO youtube_history (channel_id, video_id)
        SELECT channel_id, last_video FROM youtube WHERE last_video IS NOT NULL
    """)

    try:
        cols = await bot.cxn.fetch("PRAGMA table_info(levels)")
        col_names = {row["name"] for row in cols}
        if cols and "guild_id" not in col_names:
            await bot.cxn.execute("ALTER TABLE levels RENAME TO levels_old")
            await bot.cxn.execute("""
                CREATE TABLE levels (
                    guild_id INTEGER,
                    user_id  INTEGER,
                    xp       INTEGER DEFAULT 0,
                    level    INTEGER DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            await bot.cxn.execute("DROP TABLE levels_old")
        else:
            await bot.cxn.execute("""
                CREATE TABLE IF NOT EXISTS levels (
                    guild_id INTEGER,
                    user_id  INTEGER,
                    xp       INTEGER DEFAULT 0,
                    level    INTEGER DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
    except Exception as e:
        logging.warning("DB", f"levels table migration warning: {e}")

    await bot.cxn.execute("""
        CREATE TABLE IF NOT EXISTS level_config (
            guild_id         INTEGER PRIMARY KEY,
            xp_enabled       INTEGER DEFAULT 1,
            xp_multiplier    REAL    DEFAULT 1.0,
            xp_cooldown      INTEGER DEFAULT 0,
            level_up_channel INTEGER,
            level_up_message TEXT,
            level_roles      TEXT
        )
    """)

    import sqlite3 as _sqlite3
    old_follows = "data/follows.db"
    if os.path.exists(old_follows):
        try:
            old_conn = _sqlite3.connect(old_follows)
            rows = old_conn.execute("SELECT * FROM follows").fetchall()
            for row in rows:
                await bot.cxn.execute(
                    "INSERT OR IGNORE INTO follows "
                    "(guild_id, platform, username, channel_id, template, last_post_id) "
                    "VALUES ($1, $2, $3, $4, $5, $6)",
                    row[0], row[1], row[2], row[3], row[4], row[5]
                )
            old_conn.close()
            os.rename(old_follows, old_follows + ".migrated")
            logging.success("DB", "Migrated follows.db → database.db")
        except Exception as e:
            logging.warning("DB", f"Could not migrate follows.db: {e}")

    logging.success("DB", "Database tables verified")


async def init_database(bot):
    logging.info("DB", f"Opening database: {DATABASE_PATH}")
    try:
        bot.cxn = await database.create_pool(DATABASE_PATH)
        logging.success("DB", "Database connection established")
        await _create_tables(bot)
    except Exception as e:
        logging.error("DB", f"Failed to open database: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Cog loader
# ─────────────────────────────────────────────────────────────────────────────
async def load_cogs(bot):
    logging.info("Startup", "Loading cogs...")

    for item in os.listdir("./src/cogs"):
        item_path = os.path.join("./src/cogs", item)

        if os.path.isfile(item_path) and item.endswith(".py") and item != "__init__.py":
            module_name = f"cogs.{item[:-3]}"
        elif os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "__init__.py")):
            module_name = f"cogs.{item}"
        else:
            continue

        try:
            module = importlib.import_module(module_name)

            if getattr(module, "DNL", False):
                reason = getattr(module, "DNL_REASON", "No reason provided")
                logging.warning("Startup", f"Skipped cog: {module_name} ({reason})")
                continue

            await bot.load_extension(module_name)
            logging.success("Startup", f"Loaded cog: {module_name}")

        except Exception as e:
            logging.error("Startup", f"Failed to load cog {module_name}: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Status setter
# ─────────────────────────────────────────────────────────────────────────────
async def set_status(bot):
    status_link = os.getenv("STATUS_LINK")
    if status_link:
        if not (status_link.startswith("http://") or status_link.startswith("https://")):
            status_link = f"https://{status_link}"
    else:
        status_link = "https://twitch.tv/niko"

    status = os.getenv("STATUS_MESSAGE")
    status_type = os.getenv("STATUS_TYPE", "playing").lower()

    if status:
        if status_type == "playing":
            activity = discord.Game(name=status)
        elif status_type == "streaming":
            activity = discord.Streaming(name=status, url=status_link)
        elif status_type == "listening":
            activity = discord.Activity(type=discord.ActivityType.listening, name=status)
        elif status_type == "watching":
            activity = discord.Activity(type=discord.ActivityType.watching, name=status)
        else:
            logging.warning("RPC", "Invalid status type. Defaulting to 'playing'.")
            activity = discord.Game(name=status)

        await bot.change_presence(activity=activity)


# ─────────────────────────────────────────────────────────────────────────────
# Banner printer
# ─────────────────────────────────────────────────────────────────────────────
def print_banner(bot, guild_count: int = 0):
    R  = colorama.Style.RESET_ALL
    M  = colorama.Fore.MAGENTA
    BR = colorama.Style.BRIGHT
    C  = colorama.Fore.CYAN
    W  = colorama.Fore.WHITE
    DM = colorama.Style.DIM

    IW = 55

    def bline(content: str = "") -> str:
        pad = max(0, IW - _vis(content))
        return f"{M}{BR}│{R}{content}{' ' * pad}{M}{BR}│{R}"

    def div(left: str = "├", right: str = "┤") -> str:
        return f"{M}{BR}{left}{'─' * IW}{right}{R}"

    art = [
        f"  {W}{BR} ███╗   ██╗ ██╗██╗  ██╗  ██████╗ {R}",
        f"  {W}{BR} ████╗  ██║ ██║██║ ██╔╝ ██╔═══██╗{R}",
        f"  {W}{BR} ██╔██╗ ██║ ██║█████╔╝  ██║   ██║{R}",
        f"  {W}{BR} ██║╚██╗██║ ██║██╔═██╗  ██║   ██║{R}",
        f"  {W}{BR} ██║ ╚████║ ██║██║  ██╗ ╚██████╔╝{R}",
        f"  {W}{BR} ╚═╝  ╚═══╝ ╚═╝╚═╝  ╚═╝  ╚═════╝ {R}",
    ]

    def irow(lk: str, lv: str, rk: str = "", rv: str = "") -> str:
        left = f"  {DM}{lk:<7}{R}  {W}{lv}{R}"
        if not rk:
            return bline(left)
        gap   = max(2, 30 - _vis(left))
        right = f"{' ' * gap}{DM}{rk:<8}{R}  {W}{rv}{R}"
        return bline(left + right)

    guild_str  = str(guild_count)
    user_count = f"{len(bot.users):,}"

    # Resolve AI_MODE from utils.ai.reply
    try:
        from utils.ai.reply import AI_MODE as ai_mode
    except Exception:
        ai_mode = "OPENAI"

    rows = [
        "",
        div("╭", "╮"),
        bline(),
        *[bline(a) for a in art],
        bline(),
        bline(f"  {C}a cozy cafe AI companion for Discord{R}"),
        bline(f"  {DM}bilingual  ·  modular  ·  33+ cogs{R}"),
        bline(),
        div(),
        bline(),
        irow("bot",     str(bot.user),  "servers", guild_str),
        irow("version", "1.0",          "users",   user_count),
        irow("model",   ai_mode,        "author",  "@n.y.x.e.n"),
        bline(),
        div("╰", "╯"),
        "",
    ]

    print("\n".join(rows))


# ─────────────────────────────────────────────────────────────────────────────
# Startup helpers
# ─────────────────────────────────────────────────────────────────────────────
def _write_bot_stats(bot):
    try:
        os.makedirs("data", exist_ok=True)
        user_count = sum(g.member_count or 0 for g in bot.guilds)
        payload = {
            "guild_count":   len(bot.guilds),
            "guild_ids":     [g.id for g in bot.guilds],
            "user_count":    user_count,
            "command_count": 76,
            "version":       "1.0",
            "uptime_since":  datetime.datetime.utcnow().isoformat(),
        }
        with open("data/bot_stats.json", "w") as f:
            json.dump(payload, f)
    except Exception as exc:
        logging.error("Startup", f"Could not write bot_stats.json: {exc}")


def _write_commands(bot):
    CATEGORY_MAP = {
        "Economy":     "economy",
        "Casino":      "fun",
        "Music":       "music",
        "Leveling":    "leveling",
        "Moderation":  "moderation",
        "Automod":     "moderation",
        "Admin":       "moderation",
        "Logging":     "moderation",
        "AI":          "ai",
        "Fun":         "fun",
        "Roleplay":    "fun",
        "Utility":     "utility",
        "Info":        "utility",
        "Help":        "utility",
        "System":      "utility",
        "Voicemaster": "utility",
        "Notifier":    "utility",
        "Reminders":   "utility",
        "Tags":        "utility",
        "Giveaway":    "community",
        "Tickets":     "community",
        "Onboarding":  "community",
        "Social":      "community",
        "Polls":       "community",
        "Suggestions": "community",
        "Starboard":   "community",
        "Birthdays":   "community",
        "Highlights":  "community",
    }

    try:
        from discord import app_commands
        commands_data = []

        def process_cmd(cmd, parent_name=None):
            cog = getattr(cmd, "binding", None)
            cog_name = type(cog).__name__ if cog else "Utility"
            category = CATEGORY_MAP.get(cog_name, "utility")
            name = f"{parent_name} {cmd.name}" if parent_name else cmd.name
            commands_data.append({
                "name":        name,
                "description": getattr(cmd, "description", "") or "",
                "category":    category,
            })
            if isinstance(cmd, app_commands.Group):
                for sub in cmd.commands:
                    process_cmd(sub, parent_name=cmd.name)

        for cmd in bot.tree.get_commands():
            process_cmd(cmd)

        commands_data.sort(key=lambda x: (x["category"], x["name"]))

        os.makedirs("data", exist_ok=True)
        with open("data/commands.json", "w") as f:
            json.dump(commands_data, f)

        try:
            stats_path = "data/bot_stats.json"
            if os.path.exists(stats_path):
                with open(stats_path) as f:
                    stats = json.load(f)
                stats["command_count"] = len(commands_data)
                with open(stats_path, "w") as f:
                    json.dump(stats, f)
        except Exception:
            pass

        logging.success("Startup", f"Exported {len(commands_data)} command(s) to data/commands.json")
    except Exception as exc:
        logging.error("Startup", f"Could not write commands.json: {exc}")


async def _run_slash_sync(bot):
    try:
        synced = await bot.tree.sync()
        logging.success("SlashSync", f"Synced {len(synced)} application command(s) globally.")
    except Exception as exc:
        logging.error("SlashSync", f"Startup slash sync failed: {exc}")


async def _run_emoji_sync(bot):
    try:
        await sync_application_emojis(bot)
    except Exception as exc:
        logging.error("EmojiSync", f"Startup emoji sync failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# Main handler — called by bot.py's @bot.event on_ready
# ─────────────────────────────────────────────────────────────────────────────
async def handle_ready(bot):
    logging.info("Startup", f"Niko is online as {bot.user}")
    await init_database(bot)
    await load_cogs(bot)
    await set_status(bot)
    print_banner(bot, guild_count=len(bot.guilds))
    _write_bot_stats(bot)
    _write_commands(bot)
    asyncio.create_task(_run_emoji_sync(bot))
    asyncio.create_task(_run_slash_sync(bot))
