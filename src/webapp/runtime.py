"""Process-level runtime state: the live bot reference, the bot-loop bridge,
JSON files, and the public origin."""

import asyncio
import json
import os
import sys
import time
from flask import request, url_for
from . import config


_discord_bot = None

#: The bot's public identity, as the dashboard's config and favicon need it.
#: The dashboard child has no gateway, so it asks the bot child; a short cache
#: keeps that from becoming a request on every page and favicon hit.
_IDENTITY_FIELDS = (
    "bot_avatar_url",
    "bot_name",
    "bot_display_name",
    "bot_discriminator",
    "bot_verified",
)
_IDENTITY_TTL = 15.0
_IDENTITY_MISS_TTL = 3.0
_identity_cache: tuple[float, dict] | None = None
_identity_route = None

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


def request_host() -> str:
    """The host the visitor asked for, honouring a proxy that rewrites ``Host``.

    A reverse proxy may forward the internal address as ``Host`` and the public
    name in ``X-Forwarded-Host``; subdomain routing and the origins built for
    provider callbacks both need the name the visitor used.
    """
    forwarded = (request.headers.get("X-Forwarded-Host") or "").split(",")[0].strip()
    return forwarded or request.host


def public_base_url() -> str:
    """Return the externally reachable origin used by provider callbacks."""
    explicit = os.environ.get("PUBLIC_URL")
    if explicit:
        return explicit.rstrip("/")
    domain = os.environ.get("REPLIT_DEV_DOMAIN")
    if domain:
        return f"https://{domain}".rstrip("/")
    forwarded_proto = request.headers.get("X-Forwarded-Proto", request.scheme)
    return f"{forwarded_proto}://{request_host()}".rstrip("/")


def redirect_uri() -> str:
    """The one callback address Discord knows this site by.

    ``DISCORD_REDIRECT_URI`` wins when it is set. Otherwise the address is the
    host the visitor is on — which stops working the moment sections live on
    their own subdomains: ``https://dash.example.com/auth/callback`` is not a
    registered callback for the application, and Discord refuses the sign-in
    before it starts. The site's canonical origin is used instead, so there is
    one callback to register no matter where the visitor pressed the button.
    The shared session cookie carries the sign-in back to the section they
    started from (``/auth/callback`` redirects there).
    """
    explicit = os.environ.get("DISCORD_REDIRECT_URI")
    if explicit:
        return explicit
    canonical = config.canonical_origin()
    if config.SUBDOMAIN_ROUTING and canonical:
        return f"{canonical}/auth/callback"
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


def _user_identity(user) -> dict:
    """The fields the website prints for the bot, from a Discord user object."""
    if user is None:
        return {}
    try:
        avatar = str(user.display_avatar.url)
    except Exception:
        avatar = None
    name = str(getattr(user, "name", "") or "") or None
    display_name = str(getattr(user, "display_name", "") or "") or name
    discriminator = str(getattr(user, "discriminator", "") or "") or None
    flags = getattr(user, "public_flags", None)
    try:
        flag_value = int(getattr(flags, "value", flags) or 0)
    except (TypeError, ValueError):
        flag_value = 0
    return {
        "bot_avatar_url": avatar,
        "bot_name": name,
        "bot_display_name": display_name,
        "bot_discriminator": discriminator,
        # Bit 16 is Discord's verified-bot tick, drawn beside the bot's name.
        "bot_verified": bool(flag_value & (1 << 16)),
    }


def _identity_from_bot_child() -> dict:
    """Ask the bot child's own /api/config for the live identity.

    The split dashboard deliberately has no gateway object, but the bot child
    does.  Reading its loopback API is what keeps the navbar avatar and the
    favicon live without forwarding the whole public config (which must keep
    answering while the bot restarts).
    """
    if (os.environ.get("NIKO_SUPERVISED") or "").strip() != "1":
        return {}
    global _identity_route
    try:
        import requests
        from web_bridge import BotRoute

        if _identity_route is None:
            _identity_route = BotRoute()
        port = _identity_route.port()
        if not port:
            return {}
        response = requests.get(f"http://127.0.0.1:{port}/api/config", timeout=2.0)
        if response.status_code != 200:
            return {}
        payload = response.json()
    except Exception:
        # A restarted bot child gets a new port; drop the old one so the next
        # lookup asks the supervisor instead of retrying a dead address.
        if _identity_route is not None:
            _identity_route.invalidate()
        return {}
    if not isinstance(payload, dict):
        return {}
    return {field: payload.get(field) for field in _IDENTITY_FIELDS if field in payload}


def public_bot_identity() -> dict:
    """The bot's name, avatar and verified badge for this process.

    A process with the gateway reads its user directly.  The dashboard child
    asks the bot child, and if that child is restarting it falls back to the
    identity recorded in ``data/bot_stats.json`` when the bot last became ready.
    """
    global _identity_cache
    bot = _discord_bot
    if bot is not None:
        return _user_identity(getattr(bot, "user", None))

    now = time.monotonic()
    if _identity_cache is not None:
        cached_at, cached = _identity_cache
        ttl = _IDENTITY_TTL if cached else _IDENTITY_MISS_TTL
        if now - cached_at < ttl:
            return dict(cached)

    identity = _identity_from_bot_child()
    if not identity:
        stats = load_json(config.BOT_STATS, {})
        identity = {
            field: stats.get(field)
            for field in _IDENTITY_FIELDS
            if stats.get(field) is not None
        }
    _identity_cache = (now, identity)
    return dict(identity)


def bot_guild_ids() -> set:
    """Return the set of guild IDs the bot is currently in.

    The live gateway cache is authoritative whenever it has entries. It is
    empty in one real case though: a dashboard served before the gateway has
    finished its first READY. Trusting only the cache there reported every
    guild as "Niko is not installed", so fall back to the guild list the bot
    records in ``data/bot_stats.json`` at startup.
    """
    if _discord_bot is not None:
        cached = {str(guild.id) for guild in getattr(_discord_bot, "guilds", [])}
        if cached:
            return cached
    stats = load_json(config.BOT_STATS, {})
    return {str(g) for g in stats.get("guild_ids", [])}
