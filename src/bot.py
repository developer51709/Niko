import asyncio
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
from utils.interaction_endpoint import install_interaction_endpoint
from utils.interaction_priority import install_interaction_priority
from utils.proxy_manager import WebshareProxyManager
from utils.discord_proxy import DiscordProxyManager
from utils import analytics, logging
from utils.i18n import get_lang
from utils.maintenance import check_interaction as check_maintenance_interaction
from utils import handoff
from events.on_ready import handle_ready
from events.on_message import handle_message
import database
import api_server
from config.status import STATUS_DEVICE

# ── Update preflight ────────────────────────────────────────────────────────
# The updater imports this file in a throwaway interpreter before it replaces the
# running process (see webapp.updates._probe_bot). Reaching the end of the
# imports is all that probe needs: if the new bot core could not import, the
# update is rolled back while the old process is still serving, instead of the
# restarted process dying with the dashboard's port already handed over.
if os.getenv("NIKO_IMPORT_PROBE"):
    raise SystemExit(0)

# ── Config ───────────────────────────────────────────────────────────────────
TOKEN         = os.getenv("DISCORD_BOT_TOKEN")
DATABASE_PATH = "data/database.db"
DEBUG_MODE    = os.getenv("DEBUG_MODE", "").lower() in ("true", "1", "yes")
SUPERVISED    = os.getenv("NIKO_SUPERVISED", "").strip() == "1"

#: Supervisor lifecycle reporter, created only in supervised mode.  Keeping it
#: at module scope lets the on_ready callback report readiness after the full
#: startup chain has run, not merely when Discord's gateway is connected.
_reporter = None
_heartbeat_task = None

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
bot.cxn: "database.SQLitePool | database.MongoPool | database.remote.RemotePool | None" = None
#: Set when the startup chain has finished (successfully or not).  Optional
#: work such as Lavalink node discovery waits for this so probing public nodes
#: cannot compete with cog loading, caches and the dashboard on a slow host.
bot.startup_complete = asyncio.Event()

# ── REST egress failover ─────────────────────────────────────────────────────
# Webshare is the only egress fallback: it arms itself the moment Discord
# globally rate limits this IP and disables itself once the direct IP recovers.
WEBSHARE_API_KEY = os.getenv("WEBSHARE_API_KEY")
bot.proxy_manager: WebshareProxyManager | None = WebshareProxyManager(WEBSHARE_API_KEY)
# Optional Discord REST egress through registered Cloudflare workers. The hook
# is installed now so registry changes at startup take effect before login, and
# the manager stays disabled until the owner enables routing.
bot.discord_proxy = DiscordProxyManager()
bot.discord_proxy.attach(bot)
if WEBSHARE_API_KEY and bot.proxy_manager.attach(bot):
    logging.info("ProxyManager", "Webshare proxy failover armed.")


# ── Slash-command blacklist gate ─────────────────────────────────────────────
async def _slash_gate(interaction: discord.Interaction) -> bool:
    """Blacklist, owner maintenance, then abuse: cheapest answers first.

    A command the owner paused is answered with the maintenance notice and never
    counted as a command attempt, so a paused cog does not push ordinary members
    toward the abuse limit.
    """
    if not await check_interaction_blacklist(interaction):
        return False
    if not await check_maintenance_interaction(interaction):
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
bot.tree.interaction_check = _slash_gate


# ── Events ───────────────────────────────────────────────────────────────────
def _report(event: str, **fields) -> None:
    """Send a lifecycle event when running under the supervisor."""
    reporter = _reporter
    if reporter is not None:
        reporter.send(event, **fields)


async def _heartbeat_loop(reporter, interval: float = 3.0) -> None:
    """Heartbeat from the bot loop so a blocked loop is visible to the supervisor."""
    try:
        while True:
            await asyncio.sleep(interval)
            if not reporter.heartbeat():
                return
    except asyncio.CancelledError:
        raise


async def _report_readiness() -> None:
    """Send the supervisor what this child can and cannot serve right now."""
    from supervisor_readiness import evaluate

    snapshot = await evaluate(bot)
    state = snapshot["state"]
    if state == "not_ready":
        _report(
            "readiness_failed",
            reason="; ".join(snapshot["reasons"]),
            checks=snapshot["checks"],
        )
    else:
        _report(state, reasons=snapshot["reasons"], checks=snapshot["checks"])


@bot.event
async def on_ready():
    # READY means the gateway shards are connected; it does not mean the
    # database, cogs and startup chain are ready to serve traffic.
    _report(
        "gateway_ready",
        shard_count=int(getattr(bot, "shard_count", 0) or 0),
        ready_shards=len(getattr(bot, "shards", None) or {}),
    )
    try:
        # A reconnect can replace discord.py's aiohttp session; re-attaching is
        # idempotent and keeps worker routing available on the new session.
        proxy = getattr(bot, "discord_proxy", None)
        if proxy is not None:
            proxy.attach(bot)
        # The staff analytics tab reads these counters, so the periodic writer
        # starts before startup finishes and is idempotent across reconnects.
        analytics.start_flush_task(bot)
        # Readiness is reported only after the whole startup chain has run.
        # Everything in on_ready (presence, command feed, stats, caches) is part
        # of booting, and a failure in it surfaces through handle_ready's
        # recorded errors.  Until this returns the supervisor treats the child
        # as starting: it does not expect heartbeats, only that the process is
        # still alive, and its startup window is what bounds a hung boot.
        await handle_ready(bot)
        if _reporter is not None:
            await _report_readiness()
    except Exception as e:
        logging.error("on_ready", f"An error occurred: {e}")
        _report("readiness_failed", reason=f"on_ready failed: {type(e).__name__}: {e}")
    finally:
        # Optional startup work (Lavalink discovery) waits for this marker; it
        # is set even when the chain failed so music still comes up afterwards.
        bot.startup_complete.set()


# ── Usage analytics ──────────────────────────────────────────────────────────
# Counters are aggregate only (command, invocation kind, guild language). The
# staff dashboard renders them as daily charts; nothing here can fail a command.
async def _record_usage(command, kind, source) -> None:
    try:
        analytics.record_command(
            getattr(command, "qualified_name", None) or getattr(command, "name", ""),
            kind,
            get_lang(source),
            getattr(source, "guild_id", None),
        )
    except Exception as e:
        logging.debug("Analytics", f"Could not record {kind} command usage: {e}")


@bot.event
async def on_command_completion(ctx: commands.Context):
    await _record_usage(ctx.command, "prefix", ctx)


@bot.event
async def on_app_command_completion(interaction: discord.Interaction, command):
    kind = "context" if isinstance(command, discord.app_commands.ContextMenu) else "slash"
    await _record_usage(command, kind, interaction)


@bot.event
async def on_message(msg: discord.Message):
    try:
        await handle_message(bot, msg)
    except Exception as e:
        logging.error("on_message", f"An error occurred: {e}")


# ── Entry-point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import signal

    # The supervisor is the supported entry point.  This path still works for
    # local debugging, but it owns the public port itself and has none of the
    # supervisor's health checks, restart policy, or last-good rollback.  A
    # handoff restart re-executes this file, so it stays quiet: the operator
    # already ran the supervisor (or chose this path) once.
    if not SUPERVISED and not os.getenv("NIKO_RESTART_FD"):
        logging.warning(
            "Startup",
            "Direct start detected: the supervisor is the main entry point.\n"
            "  Start Niko with: python3 src/supervisor.py\n"
            "  This path skips the supervisor's public port, /health and /ready, "
            "crash recovery, restart budget and last-good rollback. Use it only "
            "for local debugging; see docs/supervisor-part-2.md.",
        )

    # The supervisor (and some hosts) deliver SIGTERM more than once while the
    # process is still draining.  The second delivery must not repeat the log
    # line or run cleanup against half-closed resources.
    _shutdown_started = False

    async def _shutdown(signal_name: str):
        global _shutdown_started
        if _shutdown_started:
            return
        _shutdown_started = True
        logging.info("Shutdown", f"Received {signal_name}, closing bot...")
        _report("draining", reason=signal_name)
        # Persist the commands recorded since the last periodic flush.
        await analytics.stop_flush_task()
        # Client.close() does not unload cogs, so their HTTP sessions and
        # background tasks would outlive the loop and surface as "Unclosed
        # client session" / "Task exception was never retrieved".  Run the
        # normal unload hook while the loop can still await the cleanup.
        for cog in list(bot.cogs.values()):
            unload = getattr(cog, "cog_unload", None)
            if unload is None:
                continue
            try:
                result = unload()
                if asyncio.iscoroutine(result):
                    await result
            except Exception as exc:
                logging.debug(
                    "Shutdown",
                    f"{type(cog).__name__}.cog_unload failed: {exc}",
                )
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
        global _reporter, _heartbeat_task

        if SUPERVISED:
            from supervisor_protocol import ChildReporter, install_parent_death_signal

            _reporter = ChildReporter.from_environment()
            install_parent_death_signal()
            _report("process_started")
            _heartbeat_task = asyncio.create_task(
                _heartbeat_loop(_reporter), name="supervisor-heartbeat"
            )

        try:
            await _run()
        finally:
            task = _heartbeat_task
            _heartbeat_task = None
            if task is not None:
                task.cancel()
                try:
                    await task
                except (asyncio.CancelledError, Exception):
                    pass
            _report("stopped")

    async def _run():
        if not TOKEN:
            logging.error(
                "Startup",
                "Missing bot token.\n\nSet DISCORD_BOT_TOKEN in the environment variables."
            )
            _report("readiness_failed", reason="DISCORD_BOT_TOKEN is not set")
            return

        logging.info("Startup", "Starting bot...")

        # The database lives in its own child in the split layout.  Attaching
        # it before login means commands, caches and the proxy registry all see
        # the same pool, and restarting the bot never closes the database.
        # ``connect_remote_pool`` waits for the child to finish connecting.
        split_db = SUPERVISED and (os.getenv("NIKO_SPLIT_DB") or "").strip() == "1"
        if split_db:
            from database.remote import connect_remote_pool

            bot.cxn = await connect_remote_pool()
            # Modules without a bot reference (onboarding, tickets, AI memory)
            # resolve the shared pool through this module-level handle.
            database._shared_pool = bot.cxn
            logging.info(
                "Database",
                f"Attached to the database child ({bot.cxn.db_type}).",
            )
        elif os.getenv("MONGODB_URL"):
            try:
                bot.cxn = await database.create_pool(DATABASE_PATH)
            except Exception as e:
                logging.warning("Database", f"Could not connect the shared database before login: {e}")

        # Load the shared registry before Discord login so owner-managed proxy
        # workers are available for the first REST call. It is optional: without
        # MongoDB the bot keeps its normal egress.
        if bot.cxn is not None and getattr(bot.cxn, "db_type", None) == "mongodb":
            try:
                from webapp.routes.proxy_worker_routes import initialize_proxy_worker_registry
                await initialize_proxy_worker_registry(bot)
            except Exception as e:
                logging.warning("DiscordProxy", f"Could not preload proxy workers: {e}")
        if bot.discord_proxy is not None:
            bot.discord_proxy.attach(bot)
        if bot.proxy_manager is not None:
            bot.proxy_manager.attach(bot)

        # A supervised child binds only loopback and reports the ephemeral
        # port; the supervisor owns the public socket.  A direct process keeps
        # the historical inherited-socket / PORT behaviour unchanged.
        if SUPERVISED:
            api_server.start_api_server(bot, host="127.0.0.1", port=0)
            _report("api_listening", host="127.0.0.1", port=api_server.listening_port())
            logging.info(
                "Startup",
                f"Supervised dashboard API listening on 127.0.0.1:{api_server.listening_port()}",
            )
        elif handoff.adopt(bot):
            logging.info("Startup", "Dashboard API resumed on the inherited socket.")
        else:
            api_server.start_api_server(bot)
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
            await bot.login(str(TOKEN))
            # Slash commands, buttons, selects and modals answer through the
            # interaction callback, which Discord never counts against the global
            # rate limit. Installing this before the gateway connects keeps those
            # callbacks from queueing behind a global limit hit elsewhere.
            install_interaction_priority(bot)
            # Discord can deliver interactions to our own HTTP endpoint instead of
            # the gateway and take the callback in that response, which needs no
            # working egress. Resolving the application's public key here arms
            # the endpoint (POST /api/discord/interactions) before the first
            # interaction can arrive.
            await install_interaction_endpoint(bot)
            from events.startup.database import init_database
            from events.startup.loader import load_cogs
            from events.startup.economy import preload_economy_cache
            await init_database(bot)
            _report("db_ready", backend=getattr(getattr(bot, "cxn", None), "db_type", None))
            await load_cogs(bot)
            cogs = list(getattr(bot, "cog_status", None) or ())
            _report(
                "cogs_loaded",
                total=len(cogs),
                failed=sum(1 for cog in cogs if cog.get("state") == "failed"),
            )
            await preload_economy_cache(bot)
            # on_ready skips these three steps; they already ran before the
            # gateway connected.
            bot._pre_gateway_initialized = True
            if bot.discord_proxy is not None:
                # The registry is database-backed, so reload it once the pool is
                # live and hook the session discord.py created during login.
                if getattr(getattr(bot, "cxn", None), "db_type", None) == "mongodb":
                    try:
                        from webapp.routes.proxy_worker_routes import initialize_proxy_worker_registry
                        await initialize_proxy_worker_registry(bot)
                    except Exception as e:
                        logging.warning("DiscordProxy", f"Could not load proxy workers after login: {e}")
                bot.discord_proxy.attach(bot)
            if bot.proxy_manager is not None:
                bot.proxy_manager.attach(bot)
                await bot.proxy_manager.prefetch()
            await bot.connect()
        except Exception as e:
            logging.error("Startup", f"Error connecting to Discord: {e}")
        finally:
            try:
                await bot.close()
            except Exception:
                pass

    asyncio.run(main())
