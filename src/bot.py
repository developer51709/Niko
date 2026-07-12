import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from the src directory
load_dotenv(Path(__file__).parent / ".env")

import discord
from discord.ext import commands

from utils.prefix_manager import dynamic_prefix
from utils.blacklist import check_interaction_blacklist
from utils.gateway import patch_identify
from utils import logging
from events.on_ready import handle_ready
from events.on_message import handle_message
import database

# ── Config ───────────────────────────────────────────────────────────────────
TOKEN         = os.getenv("DISCORD_BOT_TOKEN")
DATABASE_PATH = "data/database.db"
DEBUG_MODE    = os.getenv("DEBUG_MODE", "").lower() in ("true", "1", "yes")

# ── Intents ──────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.presences       = True
intents.members         = True
intents.moderation      = True

# ── Sharding ─────────────────────────────────────────────────────────────────
_shard_count = int(os.getenv("SHARD_COUNT", "0")) or None   # None → Discord auto-determines

# ── Bot ───────────────────────────────────────────────────────────────────────
bot = commands.AutoShardedBot(
    command_prefix=dynamic_prefix,
    intents=intents,
    shard_count=_shard_count,
)
bot.remove_command("help")
bot.cxn: database.SQLitePool | None = None


# ── Slash-command blacklist gate ─────────────────────────────────────────────
@bot.tree.interaction_check
async def _slash_blacklist_check(interaction: discord.Interaction) -> bool:
    return await check_interaction_blacklist(interaction)


# ── Events ───────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    await handle_ready(bot)


@bot.event
async def on_message(msg: discord.Message):
    await handle_message(bot, msg)


# ── Entry-point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not TOKEN:
        logging.error(
            "Startup",
            "Missing bot token.\n\nSet DISCORD_BOT_TOKEN in the environment variables."
        )
        exit(1)

    logging.info("Startup", "Starting bot...")

    device_choice = os.getenv("STATUS_DEVICE", "normal").lower()
    patch_identify(device_choice)

    try:
        bot.run(str(TOKEN), log_handler=None)
    except Exception as e:
        logging.error("Startup", f"Error connecting to Discord: {e}")
