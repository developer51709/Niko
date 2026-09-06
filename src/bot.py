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
from api_server import start_api_server
from config.status import STATUS_DEVICE

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
bot.cxn: database.SQLitePool | database.MongoPool | None = None


# ── Slash-command blacklist gate ─────────────────────────────────────────────
@bot.tree.interaction_check
async def _slash_blacklist_check(interaction: discord.Interaction) -> bool:
    return await check_interaction_blacklist(interaction)


# ── Events ───────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    try:
        await handle_ready(bot)
    except Exception as e:
        logging.error("on_ready", f"An error occurred: {e}")


@bot.event
async def on_message(msg: discord.Message):
    try:
        await handle_message(bot, msg)
    except Exception as e:
        logging.error("on_message", f"An error occurred: {e}")


# ── Entry-point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import asyncio
    import signal

    async def _shutdown(signal_name: str):
        logging.info("Shutdown", f"Received {signal_name}, closing bot...")
        try:
            await bot.close()
        except Exception:
            pass

    async def main():
        if not TOKEN:
            logging.error(
                "Startup",
                "Missing bot token.\n\nSet DISCORD_BOT_TOKEN in the environment variables."
            )
            return

        logging.info("Startup", "Starting bot...")

        start_api_server(bot)
        logging.info("Startup", "Dashboard API started alongside the bot.")

        device_choice = STATUS_DEVICE
        patch_identify(device_choice)

        loop = asyncio.get_running_loop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(_shutdown(s.name)))
            except NotImplementedError:
                # Windows or unsupported loop may raise here; ignore
                pass

        try:
            await bot.start(str(TOKEN))
        except Exception as e:
            logging.error("Startup", f"Error connecting to Discord: {e}")
        finally:
            try:
                await bot.close()
            except Exception:
                pass

    asyncio.run(main())
