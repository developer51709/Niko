"""Process-level runtime state: the live bot reference, the bot-loop bridge,
JSON files, and the public origin."""

import asyncio
import json
import os
import sys
from flask import request, url_for
from . import config


_discord_bot = None

# Delivery jobs (staff broadcasts) outlive the request that starts them, so the
# futures are kept referenced until they finish. Losing the reference would let
# the garbage collector cancel a run halfway through a broadcast.
_background_jobs: set = set()


def oauth_enabled() -> bool:
    return bool(config.DISCORD_CLIENT_SECRET)


def configure_bot(bot) -> None:
    """Give the API access to the live bot for guild and runtime config sync.

    Every route module snapshots the shared names when it is imported (see the
    ``globals().update`` at the top of a ``webapp/routes/*_routes.py`` module), so each one owns
    its own ``_discord_bot`` that the assignment above cannot reach. The bot is
    therefore handed to each of them here.

    The modules are discovered rather than listed by hand. A hand-kept list has
    to be edited whenever a route module is added, and its failure mode is
    silent: ``webapp.routes.notifier_routes`` was left off it and served its imported
    ``_discord_bot = None`` forever, so the whole Notifications tab answered
    ``503 The Discord bot is not available.`` A module imported after this call
    reads the bot that is already assigned above when it snapshots, so sweeping
    the loaded modules is enough.
    """
    global _discord_bot
    _discord_bot = bot
    for module_name, module in list(sys.modules.items()):
        if not module_name.startswith("webapp.") or module is None:
            continue
        if hasattr(module, "_discord_bot"):
            module._discord_bot = bot


def run_on_bot_loop(awaitable, timeout: float = 8):
    """Run a bot-cog coroutine from Flask's worker thread.

    The dashboard is served by Flask in a separate thread, so reading through
    the bot's own pool must be scheduled onto the Discord event loop. This
    keeps the dashboard and the running bot on the same source of truth.
    """
    if _discord_bot is None or not _discord_bot.loop.is_running():
        raise RuntimeError("The Discord bot is not running.")
    future = asyncio.run_coroutine_threadsafe(awaitable, _discord_bot.loop)
    return future.result(timeout=timeout)


def schedule_on_bot_loop(awaitable):
    """Queue a coroutine on the bot loop without blocking the Flask worker."""
    if _discord_bot is None or not _discord_bot.loop.is_running():
        raise RuntimeError("The Discord bot is not running.")
    future = asyncio.run_coroutine_threadsafe(awaitable, _discord_bot.loop)
    _background_jobs.add(future)
    future.add_done_callback(_background_jobs.discard)
    return future


def public_base_url() -> str:
    """Return the externally reachable origin used by provider callbacks."""
    explicit = os.environ.get("PUBLIC_URL") or os.environ.get("DONATION_SITE_URL")
    if explicit:
        return explicit.rstrip("/")
    domain = os.environ.get("REPLIT_DEV_DOMAIN")
    if domain:
        return f"https://{domain}".rstrip("/")
    forwarded_host = request.headers.get("X-Forwarded-Host")
    host = forwarded_host or request.host
    forwarded_proto = request.headers.get("X-Forwarded-Proto", request.scheme)
    return f"{forwarded_proto}://{host}".rstrip("/")


def redirect_uri() -> str:
    explicit = os.environ.get("DISCORD_REDIRECT_URI")
    if explicit:
        return explicit
    domain = os.environ.get("REPLIT_DEV_DOMAIN")
    if domain:
        return f"https://{domain}/auth/callback"
    return url_for("auth_callback", _external=True)


def load_json(path: str, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}


def save_json(path: str, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    temporary = f"{path}.tmp"
    with open(temporary, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(temporary, path)


def bot_guild_ids() -> set:
    """Return the set of guild IDs the bot is currently in.

    The live gateway cache is authoritative whenever it has entries. It is
    empty in two real cases though: a dashboard served before the gateway has
    finished its first READY, and a standby process, which never connects a
    gateway at all. Trusting only the cache there reported every guild as
    "Niko is not installed", so fall back to the guild list the bot records in
    ``data/bot_stats.json`` at startup.
    """
    if _discord_bot is not None:
        cached = {str(guild.id) for guild in getattr(_discord_bot, "guilds", [])}
        if cached:
            return cached
    stats = load_json(config.BOT_STATS, {})
    return {str(g) for g in stats.get("guild_ids", [])}
