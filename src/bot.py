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
from utils.abuse_detection import record_request, strike_notice
from utils.gateway import patch_identify
from utils.proxy_manager import WebshareProxyManager
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

# ── Proxy failover ───────────────────────────────────────────────────────────
# This manager can use Webshare and/or owner-registered, credential-verified
# standby proxies. Standby mode never starts another Discord gateway client.
WEBSHARE_API_KEY = os.getenv("WEBSHARE_API_KEY")
bot.proxy_manager: WebshareProxyManager | None = WebshareProxyManager(WEBSHARE_API_KEY)
if WEBSHARE_API_KEY and bot.proxy_manager.attach(bot):
    logging.info("ProxyManager", "Webshare proxy failover armed.")


# ── Slash-command blacklist gate ─────────────────────────────────────────────
async def _slash_blacklist_check(interaction: discord.Interaction) -> bool:
    if not await check_interaction_blacklist(interaction):
        return False
    abuse = await record_request(interaction.user.id, reason="spamming commands")
    if abuse.get("abuse"):
        try:
            await interaction.response.send_message(strike_notice(abuse), ephemeral=True)
        except discord.HTTPException:
            pass
        return False
    return True


# CommandTree.interaction_check is an override hook, not a decorator. Assign
# the bound-instance callback explicitly so every application command passes
# through the blacklist gate.
bot.tree.interaction_check = _slash_blacklist_check


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
        if bot.proxy_manager is not None:
            try:
                await bot.proxy_manager.close()
            except Exception:
                pass
        try:
            await bot.close()
        except Exception:
            pass

    async def main():
        if os.getenv("BACKUP_MODE", "").lower() in {"1", "true", "yes"}:
            from utils.backup_proxy import serve_backup_proxy

            server = await serve_backup_proxy(
                os.getenv("BACKUP_PROXY_HOST", "0.0.0.0"),
                int(os.getenv("PORT", os.getenv("BACKUP_PROXY_PORT", "10000"))),
                os.getenv("BACKUP_TLS_CERT") or None,
                os.getenv("BACKUP_TLS_KEY") or None,
                os.getenv("DISCORD_BOT_TOKEN", ""),
                os.getenv("SESSION_SECRET", ""),
            )
            logging.info("Backup", "Standby proxy online; this instance will not connect to Discord.")
            async with server:
                await server.serve_forever()
            return

        if not TOKEN:
            logging.error(
                "Startup",
                "Missing bot token.\n\nSet DISCORD_BOT_TOKEN in the environment variables."
            )
            return

        logging.info("Startup", "Starting bot...")

        # Load registered standbys before the gateway login attempt. Waiting
        # until on_ready is too late when the production egress IP is blocked.
        if os.getenv("MONGODB_URL"):
            try:
                bot.cxn = await database.create_pool(DATABASE_PATH)
                from webapp.backup_routes import initialize_backup_registry

                await initialize_backup_registry(bot)
            except Exception as e:
                logging.warning("ProxyManager", f"Could not preload standby instances: {e}")

        start_api_server(bot)
        logging.info("Startup", "Dashboard API started alongside the bot.")

        device_choice = STATUS_DEVICE
        patch_identify(device_choice)

        if bot.proxy_manager is not None:
            await bot.proxy_manager.prefetch()
            await bot.proxy_manager.check_direct_egress()

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
