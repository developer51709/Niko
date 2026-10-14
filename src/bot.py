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
from utils.standby_manager import StandbyFailoverManager
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

# ── REST egress failover ─────────────────────────────────────────────────────
# Standby owns startup login interception and falls back to Webshare only if
# no healthy standby can be selected.
WEBSHARE_API_KEY = os.getenv("WEBSHARE_API_KEY")
bot.proxy_manager: WebshareProxyManager | None = WebshareProxyManager(WEBSHARE_API_KEY)
bot.standby_failover = StandbyFailoverManager()
bot.standby_failover.attach(bot)
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
async def _refresh_handoff_caches(bot):
    """Refresh database-backed caches before the bot resumes serving events."""
    from events.startup.economy import preload_economy_cache
    from utils.blacklist_manager import BlacklistManager

    manager = BlacklistManager()
    manager._loaded = False
    await manager.reload()
    await preload_economy_cache(bot)


async def _on_gateway_ready(bot):
    handoff = getattr(bot, "gateway_handoff", None)
    if handoff is not None and handoff.refresh_caches_on_ready:
        await _refresh_handoff_caches(bot)
        handoff.refresh_caches_on_ready = False
    await handle_ready(bot)


@bot.event
async def on_ready():
    try:
        await _on_gateway_ready(bot)
        handoff = getattr(bot, "gateway_handoff", None)
        if handoff is not None:
            handoff.mark_connected()
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
        if not TOKEN:
            logging.error(
                "Startup",
                "Missing bot token.\n\nSet DISCORD_BOT_TOKEN in the environment variables."
            )
            return

        logging.info("Startup", "Starting bot...")

        standby_mode = os.getenv("STANDBY_MODE", "").lower() in {"1", "true", "yes"}
        from utils.gateway_failover import GatewayHandoff
        handoff = GatewayHandoff(bot, active=not standby_mode)
        bot.gateway_handoff = handoff

        # Load standby endpoints before Discord login so the wrapped
        # static_login can switch to a warm standby if egress is challenged.
        if not standby_mode and os.getenv("MONGODB_URL"):
            try:
                bot.cxn = await database.create_pool(DATABASE_PATH)
                from webapp.standby_routes import initialize_standby_registry
                await initialize_standby_registry(bot)
            except Exception as e:
                logging.warning("StandbyFailover", f"Could not preload standby instances: {e}")
        if not standby_mode and bot.proxy_manager is not None:
            bot.proxy_manager.attach(bot)

        if not standby_mode:
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
            # Login, initialize the shared database, and load all cogs before
            # gateway ownership is enabled, so the standby is warm on demand.
            await bot.login(str(TOKEN))
            from events.startup.database import init_database
            from events.startup.loader import load_cogs
            from events.startup.economy import preload_economy_cache
            await init_database(bot)
            await load_cogs(bot)
            await preload_economy_cache(bot)
            bot._pre_gateway_initialized = True
            if bot.proxy_manager is not None:
                if not standby_mode:
                    bot.proxy_manager.attach(bot)
                await bot.proxy_manager.prefetch()
            if standby_mode:
                from utils.standby_failover import serve_standby
                standby_manager = bot.standby_failover
                standby_manager.attach(bot)
                # A standby never initiates failover. It accepts signed handoff
                # commands only, so a blocked request there can neither promote
                # it nor hand its gateway to another registered instance.
                standby_manager.select_failover("off")
                from webapp import app as web_app, configure_bot
                configure_bot(bot)
                server = await serve_standby(
                    os.getenv("STANDBY_HOST", "0.0.0.0"),
                    int(os.getenv("PORT", os.getenv("STANDBY_PORT", "10000"))),
                    os.getenv("STANDBY_TLS_CERT") or None,
                    os.getenv("STANDBY_TLS_KEY") or None,
                    os.getenv("DISCORD_BOT_TOKEN", ""),
                    os.getenv("SESSION_SECRET", ""),
                    handoff,
                    web_app=web_app,
                )
                logging.info("StandbyFailover", "Standby backend is warm; gateway remains inactive until signed handoff.")
                async with server:
                    await handoff.run()
            else:
                if bot.standby_failover is not None:
                    await bot.standby_failover.check_direct_egress()
                await handoff.run()
        except Exception as e:
            logging.error("Startup", f"Error connecting to Discord: {e}")
        finally:
            try:
                await handoff.shutdown()
            except Exception:
                pass
            try:
                await bot.close()
            except Exception:
                pass

    asyncio.run(main())
