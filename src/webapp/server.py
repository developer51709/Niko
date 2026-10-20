"""
Niko Dashboard — Flask web server
──────────────────────────────────
Routes:
  GET  /                        → React landing page
  GET  /dashboard               → React dashboard
  GET  /auth/login              → redirect to Discord OAuth
  GET  /auth/callback           → handle OAuth code exchange
  GET  /auth/logout             → clear session
  GET  /auth/status             → JSON: authenticated + user info

  GET  /api/botstats            → public bot stats (no auth required)
  GET  /api/me                  → current user (auth required)
  GET  /api/guilds              → mutual guilds (auth required)
  GET  /api/guild/<id>/overview → guild overview stats (auth required)
  GET  /api/guild/<id>/levels   → level leaderboard (auth required)
  GET  /api/guild/<id>/config   → full guild config (auth required)
  POST /api/guild/<id>/config/automod → save automod settings (auth required)
  POST /api/guild/<id>/config/ai      → save AI settings (auth required)
  POST /api/guild/<id>/config/leveling → save leveling settings (auth required)
  POST /api/guild/<id>/config/server → save server settings (auth required)
"""

import os
import json
import glob
import time
import secrets
import traceback
import sqlite3
import asyncio
import base64
import hashlib
import hmac
import uuid
import sys
from html import escape
from urllib.parse import urlencode, quote, urlparse
from flask import Response
from functools import wraps
from flask import (
    Flask, send_from_directory, session,
    redirect, request, jsonify, url_for
)
import requests as req

from utils.donations import (
    add_donor,
    confirm_invoice,
    create_donation_token,
    get_invoice,
    donation_link,
    get_pending_invoices,
    save_invoice,
    update_invoice_status,
    verify_donation_token,
)
from cogs.donations.oxapay import OxaPayClient
from config.ids import OWNER_IDS
from cogs.staff.staff import STAFF_ROLES
from utils.ai.config import get_ai_config, set_ai_config
from . import leaderboard_cache

# ── Constants ────────────────────────────────────────────────────────────────

DISCORD_CLIENT_ID     = os.environ.get("DISCORD_CLIENT_ID", "1520558530472448170")
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "")
DISCORD_BOT_TOKEN     = os.environ.get("DISCORD_BOT_TOKEN", "")
DISCORD_API           = "https://discord.com/api/v10"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")
ECONOMY_DIR  = os.path.join(DATA_DIR, "economy_data")
BOT_STATS    = os.path.join(DATA_DIR, "bot_stats.json")
AI_CONFIG_DATABASE_SENTINEL_LEGACY        = os.path.join(DATA_DIR, "ai_config.json")
AI_CONFIG_DATABASE_SENTINEL = AI_CONFIG_DATABASE_SENTINEL_LEGACY  # compatibility alias; AI reads/writes are database-backed
LEVELS_JSON  = os.path.join(DATA_DIR, "levels.json.migrated")
LEVELCFG_JSON = os.path.join(DATA_DIR, "level_config.json.migrated")
DATABASE_PATH = os.path.join(DATA_DIR, "database.db")
OXAPAY_KEY = os.environ.get("OXAPAY_API_KEY", "")

MANAGE_GUILD_PERM = 0x20
ADMINISTRATOR_PERM = 0x8

# ── App setup ────────────────────────────────────────────────────────────────

WEB_DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "website", "dist")
app = Flask(__name__, static_folder=WEB_DIST_DIR, static_url_path="")
app.secret_key = os.environ.get("SESSION_SECRET", secrets.token_hex(32))
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"]   = True
app.config["SESSION_COOKIE_HTTPONLY"] = True

_discord_bot = None
_WEB_STARTED_AT = time.time()
_member_metadata_cache: dict[str, tuple[float, dict[str, dict]]] = {}
_staff_user_identity_cache: dict[str, tuple[float, dict[str, str | None]]] = {}
_STAFF_USER_IDENTITY_CACHE_TTL = 600

# ── Helpers ──────────────────────────────────────────────────────────────────

def oauth_enabled() -> bool:
    return bool(DISCORD_CLIENT_SECRET)


def configure_bot(bot) -> None:
    """Give the API access to the live bot for guild and runtime config sync.

    Every route module snapshots the shared names when it is imported (see the
    ``globals().update`` at the top of ``webapp/*_routes.py``), so each one owns
    its own ``_discord_bot`` that the assignment above cannot reach. The bot is
    therefore handed to each of them here.

    The modules are discovered rather than listed by hand. A hand-kept list has
    to be edited whenever a route module is added, and its failure mode is
    silent: ``webapp.notifier_routes`` was left off it and served its imported
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


def _serialize_level_config(config) -> dict:
    """Keep Discord snowflake IDs exact when sending leveling data to JS."""
    serialized = dict(config or {})
    channel_id = serialized.get("level_up_channel")
    if channel_id is not None:
        serialized["level_up_channel"] = str(channel_id)
    return serialized


def get_runtime_level_config(guild_id: str) -> dict:
    """Read leveling settings through the live leveling cog when available."""
    if _discord_bot is not None:
        leveling = _discord_bot.get_cog("Leveling")
        if leveling is not None and hasattr(leveling, "_guild_cfg"):
            try:
                return _serialize_level_config(run_on_bot_loop(leveling._guild_cfg(int(guild_id))))
            except Exception:
                pass

    # Fallback for a web-only process or a bot that is still starting.
    level_cfg = {}
    conn = sqlite_connect()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT xp_enabled, xp_multiplier, xp_cooldown, "
                "       level_up_channel, level_up_message, level_roles, "
                "       card_accent, card_bg_top, card_bg_bottom "
                "FROM level_config WHERE guild_id = ?",
                (int(guild_id),),
            )
            row = cur.fetchone()
            if row:
                level_cfg = {
                    "xp_enabled": bool(row[0]),
                    "xp_multiplier": row[1],
                    "xp_cooldown": row[2],
                    "level_up_channel": str(row[3]) if row[3] else None,
                    "level_up_message": row[4],
                    "level_roles": json.loads(row[5] or "{}"),
                    "card_accent": json.loads(row[6]) if row[6] else None,
                    "card_bg_top": json.loads(row[7]) if row[7] else None,
                    "card_bg_bottom": json.loads(row[8]) if row[8] else None,
                }
            conn.close()
        except Exception:
            conn.close()

    return _serialize_level_config(level_cfg or load_json(LEVELCFG_JSON, {}).get(guild_id, {}))


# Only the primary's own owner-control plane (standby and proxy-worker
# management) stays local. The standby's own service routes (/health and
# /internal/standby/*) are proxied together with the rest of the application so
# the public production domain exposes the complete active instance rather than
# a trimmed subset of it.
_STANDBY_LOCAL_PATHS = ("/api/staff/standbys", "/api/staff/proxy-workers")
_STANDBY_HOP_BY_HOP_HEADERS = {
    "connection", "content-encoding", "content-length", "keep-alive", "proxy-authenticate",
    "proxy-authorization", "te", "trailer", "transfer-encoding", "upgrade", "set-cookie",
}
# The browser's Host names the production deployment, not the standby. Forwarding
# it upstream hands the standby's own edge a hostname that belongs to this
# deployment, so that edge answers the relay itself and the production URL serves
# nothing. The relay therefore addresses the standby by its registered origin and
# passes the public host and scheme through X-Forwarded-*, where the standby's
# public_base_url() already reads them.
_STANDBY_REQUEST_EXCLUDED_HEADERS = {
    "connection", "content-length", "transfer-encoding", "proxy-authorization", "proxy-connection",
    "host",
}


@app.before_request
def route_to_active_standby():
    """Serve the complete web application from the standby while it owns the gateway."""
    manager = getattr(_discord_bot, "standby_failover", None) if _discord_bot is not None else None
    origin = getattr(manager, "active_origin", None) if manager is not None else None
    if not origin or origin not in getattr(manager, "origins", ()):
        return None
    if any(request.path == path or request.path.startswith(path + "/") for path in _STANDBY_LOCAL_PATHS):
        return None

    target = f"{origin.rstrip('/')}{request.path}"
    if request.query_string:
        target += f"?{request.query_string.decode('latin-1')}"
    headers = {
        name: value
        for name, value in request.headers.items()
        if name.lower() not in _STANDBY_REQUEST_EXCLUDED_HEADERS
    }
    # requests derives Host from the target URL, so the standby's own edge can
    # route the relayed request while its application still builds OAuth
    # callbacks, redirects, and cookies for the production URL.
    headers["X-Forwarded-Host"] = request.headers.get("X-Forwarded-Host") or request.host
    headers["X-Forwarded-Proto"] = request.headers.get("X-Forwarded-Proto") or request.scheme
    forwarded_for = request.headers.get("X-Forwarded-For") or request.remote_addr
    if forwarded_for:
        headers["X-Forwarded-For"] = forwarded_for
    try:
        upstream = req.request(
            request.method,
            target,
            headers=headers,
            data=request.get_data(cache=True),
            timeout=(3, 35),
            allow_redirects=False,
        )
    except req.RequestException:
        return jsonify({"error": "The active standby backend is temporarily unavailable."}), 503

    response = Response(upstream.content, status=upstream.status_code)
    raw_headers = getattr(getattr(upstream, "raw", None), "headers", None)
    set_cookies = raw_headers.getlist("Set-Cookie") if raw_headers is not None else []
    for name, value in upstream.headers.items():
        if name.lower() not in _STANDBY_HOP_BY_HOP_HEADERS:
            response.headers[name] = value
    for cookie in set_cookies:
        response.headers.add("Set-Cookie", cookie)
    close_upstream = getattr(upstream, "close", None)
    if close_upstream is not None:
        close_upstream()
    return response


@app.route("/health")
def api_health_local():
    """Report this instance's liveness while it owns the gateway directly."""
    return jsonify({
        "ok": True,
        "service": "niko-backend",
        "gateway": "active",
        "active_standby": None,
        "uptime_seconds": max(0, int(time.time() - _WEB_STARTED_AT)),
    })


@app.route("/internal/standby/<path:path>", methods=["GET", "POST"])
def api_internal_standby_unavailable(path):
    """Standby relay endpoints only answer while a standby owns the gateway."""
    return jsonify({"error": "No active standby instance is receiving standby relay requests."}), 503


@app.after_request
def prevent_dynamic_cache(response):
    """Never let auth or dashboard API responses become stale in production."""
    if request.path.startswith("/api/") or request.path.startswith("/auth/"):
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"
    return response


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
    stats = load_json(BOT_STATS, {})
    return {str(g) for g in stats.get("guild_ids", [])}


def sqlite_connect():
    """Open a short-lived read/write connection to the bot's SQLite database."""
    try:
        return sqlite3.connect(DATABASE_PATH, timeout=5)
    except Exception:
        return None


def _normalize_economy_row(row) -> dict:
    """Convert an economy database row into the dashboard response shape."""
    balance = int(row.get("balance", 0) or 0)
    bank = int(row.get("bank", 0) or 0)
    try:
        leaderboard_private = bool(int(row.get("leaderboard_private", 0) or 0))
    except (TypeError, ValueError):
        leaderboard_private = bool(row.get("leaderboard_private", False))
    achievements = row.get("achievements", [])
    if isinstance(achievements, str):
        try:
            achievements = json.loads(achievements or "[]")
        except (TypeError, ValueError):
            achievements = []
    return {
        "user_id": str(row.get("user_id")),
        "balance": balance,
        "bank": bank,
        "net_worth": balance + bank,
        "leaderboard_private": leaderboard_private,
        "level": int(row.get("level", 0) or 0),
        "job": row.get("job") or "barista",
        "daily_streak": int(row.get("daily_streak", 0) or 0),
        "achievements": len(achievements) if isinstance(achievements, (list, tuple, set, dict)) else 0,
        "total_earned": int(row.get("total_earned", 0) or 0),
    }


def _member_metadata_from_guild(guild, user_ids: set[str]) -> dict[str, dict]:
    """Build identity metadata without crossing the Discord event loop."""
    if guild is None or not user_ids:
        return {}
    metadata = {}
    for member in getattr(guild, "members", []):
        member_id = str(member.id)
        if member_id not in user_ids:
            continue
        avatar = getattr(member, "display_avatar", None)
        metadata[member_id] = {
            "display_name": getattr(member, "global_name", None) or getattr(getattr(member, "_user", None), "global_name", None) or getattr(member, "name", None),
            "username": getattr(member, "name", None),
            "avatar_url": str(avatar.url) if avatar is not None else None,
        }
    return metadata


def get_runtime_member_metadata(guild_id: str, user_ids: set[str]) -> dict[str, dict]:
    """Return display names and avatars for cached members in a guild."""
    if not user_ids or _discord_bot is None:
        return {}

    async def read_members():
        return _member_metadata_from_guild(
            _discord_bot.get_guild(int(guild_id)),
            user_ids,
        )

    try:
        return run_on_bot_loop(read_members())
    except Exception:
        return {}


def get_discord_member_metadata(guild_id: str, user_ids: set[str]) -> dict[str, dict]:
    """Fetch guild member identity data when Flask runs without the bot object."""
    if not user_ids or not DISCORD_BOT_TOKEN:
        return {}

    cached = _member_metadata_cache.get(str(guild_id))
    if cached and time.time() - cached[0] < 60:
        return {user_id: cached[1][user_id] for user_id in user_ids if user_id in cached[1]}

    members = {}
    after = None
    for _ in range(100):
        params = {"limit": 1000}
        if after:
            params["after"] = after
        try:
            response = discord_request(
                "GET",
                f"{DISCORD_API}/guilds/{guild_id}/members",
                headers={"Authorization": f"Bot {DISCORD_BOT_TOKEN}"},
                params=params,
                timeout=8,
            )
            response.raise_for_status()
            batch = response.json()
        except Exception:
            break
        if not isinstance(batch, list):
            break

        for member in batch:
            discord_user = member.get("user", {})
            member_id = str(discord_user.get("id", ""))
            if not member_id:
                continue
            guild_avatar = member.get("avatar")
            user_avatar = discord_user.get("avatar")
            if guild_avatar:
                avatar_url = f"https://cdn.discordapp.com/guilds/{guild_id}/users/{member_id}/avatars/{guild_avatar}.png?size=64"
            elif user_avatar:
                extension = "gif" if str(user_avatar).startswith("a_") else "png"
                avatar_url = f"https://cdn.discordapp.com/avatars/{member_id}/{user_avatar}.{extension}?size=64"
            else:
                avatar_url = None
            members[member_id] = {
                "display_name": discord_user.get("global_name") or discord_user.get("username"),
                "username": discord_user.get("username"),
                "avatar_url": avatar_url,
            }

        if len(batch) < 1000:
            break
        after = str(batch[-1].get("user", {}).get("id", ""))
        if not after:
            break

    _member_metadata_cache[str(guild_id)] = (time.time(), members)
    return {user_id: members[user_id] for user_id in user_ids if user_id in members}


def get_member_metadata(guild_id: str, user_ids: set[str]) -> dict[str, dict]:
    """Use the live bot cache first, then the bot-token API fallback."""
    if _discord_bot is not None:
        metadata = get_runtime_member_metadata(guild_id, user_ids)
        if metadata:
            return metadata
    return get_discord_member_metadata(guild_id, user_ids)


def get_runtime_economy_rows(guild_id: str | None = None) -> list[dict] | None:
    """Read economy data from the live bot database.

    Economy profiles are global by user ID, so guild pages intersect them with
    the selected guild's cached Discord members before calculating totals.
    """
    query = (
        "SELECT user_id, balance, bank, level, job, daily_streak, "
        "achievements, total_earned, leaderboard_private FROM economy_users"
    )
    if _discord_bot is not None and hasattr(_discord_bot, "cxn"):
        async def read_from_bot():
            rows = await _discord_bot.cxn.fetch(query)
            normalized = [_normalize_economy_row(row) for row in rows]
            if guild_id is None:
                return normalized
            guild = _discord_bot.get_guild(int(guild_id))
            if guild is None:
                return []
            member_ids = {str(member.id) for member in getattr(guild, "members", [])}
            scoped = [row for row in normalized if row["user_id"] in member_ids]
            metadata = _member_metadata_from_guild(
                guild,
                {row["user_id"] for row in scoped},
            )
            return [{**row, **metadata.get(row["user_id"], {})} for row in scoped]

        try:
            return run_on_bot_loop(read_from_bot())
        except Exception:
            pass

    conn = sqlite_connect()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        rows = [_normalize_economy_row(dict(zip(columns, raw))) for raw in cursor.fetchall()]
        if guild_id is not None:
            metadata = get_member_metadata(guild_id, {row["user_id"] for row in rows})
            return [
                {**row, **metadata[row["user_id"]]}
                for row in rows
                if row["user_id"] in metadata
            ]
        return rows
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def get_runtime_leaderboard_page(offset: int, limit: int) -> tuple[list[dict], int] | None:
    """Read one top-worth leaderboard page, with a strict database-side bound."""
    offset = max(0, int(offset))
    limit = max(1, min(int(limit), 100))
    pool = getattr(_discord_bot, "cxn", None) if _discord_bot is not None else None
    if pool is not None:
        async def read_page():
            page = await pool.fetch(
                "SELECT user_id, balance, bank, leaderboard_private "
                "FROM economy_users ORDER BY net_worth DESC, user_id ASC LIMIT $1 OFFSET $2",
                limit, offset,
            )
            count = await pool.fetchval("SELECT COUNT(*) FROM economy_users")
            return page, int(count or 0)
        try:
            rows, total = run_on_bot_loop(read_page())
            return [_normalize_economy_row(row) for row in rows], total
        except Exception:
            return None

    conn = sqlite_connect()
    if conn is None:
        return None
    try:
        cursor = conn.execute(
            "SELECT user_id, balance, bank, leaderboard_private FROM economy_users "
            "ORDER BY net_worth DESC, user_id ASC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        columns = [column[0] for column in cursor.description]
        rows = [_normalize_economy_row(dict(zip(columns, raw))) for raw in cursor.fetchall()]
        total = conn.execute("SELECT COUNT(*) FROM economy_users").fetchone()[0]
        return rows, int(total or 0)
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def get_mutual_leaderboard_identity_ids(target_user_ids: set[str]) -> set[str] | None:
    """Resolve target identities visible to the signed-in viewer via mutual guilds.

    Fail closed on membership uncertainty: unavailable Discord auth or guild
    data never makes private profiles visible to a broader audience.
    """
    viewer = session.get("user") or {}
    if not viewer.get("id") or not target_user_ids:
        return set()
    if not ensure_access_token():
        return set()
    # The leaderboard polls, so the viewer's guild list is reused for a few
    # seconds instead of spending a Discord OAuth call on every refresh.
    viewer_guild_ids = leaderboard_cache.cached_viewer_guilds(str(viewer["id"]))
    if viewer_guild_ids is None:
        try:
            viewer_guild_ids = {
                str(guild["id"])
                for guild in discord_get("/users/@me/guilds", session.get("access_token", ""))
                if guild.get("id")
            }
        except Exception:
            return None
        leaderboard_cache.store_viewer_guilds(str(viewer["id"]), viewer_guild_ids)
    if not viewer_guild_ids or _discord_bot is None:
        return set()

    async def find_mutual_members():
        visible = set()
        for guild in _discord_bot.guilds:
            if str(guild.id) not in viewer_guild_ids:
                continue
            for user_id in target_user_ids - visible:
                try:
                    if guild.get_member(int(user_id)) is not None:
                        visible.add(user_id)
                except (TypeError, ValueError):
                    continue
        return visible

    try:
        return run_on_bot_loop(find_mutual_members())
    except Exception:
        return None


def _load_blacklist_manager():
    """Load the shared blacklist cache on the bot loop when needed."""
    from utils.blacklist_manager import BlacklistManager

    manager = BlacklistManager()
    if not manager._loaded and _discord_bot is not None:
        run_on_bot_loop(manager._ensure_loaded())
    return manager


def _current_user_blacklist_entry():
    user_id = session.get("user", {}).get("id")
    if not user_id:
        return None
    return _load_blacklist_manager().get_user_entry(int(user_id))


def require_auth(f):
    """Require a signed-in, non-blacklisted user for dashboard API access."""
    @wraps(f)
    def _inner(*args, **kwargs):
        if not ensure_access_token():
            return jsonify({
                "error": "Not authenticated",
                "login_url": "/auth/login",
            }), 401
        try:
            entry = _current_user_blacklist_entry()
        except Exception:
            return jsonify({"error": "Account access could not be verified."}), 503
        if entry:
            return jsonify({
                "error": "This Discord account is blacklisted from the dashboard.",
                "blacklisted": True,
                "scope": "user",
                "reason": entry.get("reason") or "No reason provided.",
            }), 403
        return f(*args, **kwargs)
    return _inner


def require_dashboard_auth(f):
    """Authenticate a dashboard status check while allowing it to report a ban."""
    @wraps(f)
    def _inner(*args, **kwargs):
        if not ensure_access_token():
            return jsonify({"error": "Not authenticated", "login_url": "/auth/login"}), 401
        try:
            entry = _current_user_blacklist_entry()
        except Exception:
            return jsonify({"error": "Account access could not be verified."}), 503
        return jsonify({
            "blacklisted": bool(entry),
            "reason": (entry.get("reason") or "No reason provided.") if entry else None,
        })
    return _inner


def ensure_access_token() -> bool:
    """Keep the OAuth session usable across Discord's short-lived access token."""
    if "user" not in session:
        return False
    expires_at = float(session.get("token_exp", 0))
    if session.get("access_token") and time.time() < expires_at - 30:
        return True

    refresh_token = session.get("refresh_token")
    if not refresh_token or not oauth_enabled():
        session.clear()
        return False
    try:
        response = discord_request(
            "POST",
            f"{DISCORD_API}/oauth2/token",
            data={
                "client_id": DISCORD_CLIENT_ID,
                "client_secret": DISCORD_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        response.raise_for_status()
        token_data = response.json()
        session["access_token"] = token_data["access_token"]
        session["refresh_token"] = token_data.get("refresh_token", refresh_token)
        session["token_exp"] = time.time() + token_data.get("expires_in", 604800)
        return True
    except Exception:
        session.clear()
        return False


def require_csrf(f):
    """Require the token issued with auth status for browser mutations."""
    @wraps(f)
    def _inner(*args, **kwargs):
        if not session.get("csrf_token") or request.headers.get("X-CSRF-Token") != session["csrf_token"]:
            return jsonify({"error": "Invalid request token. Refresh the dashboard and try again."}), 403
        return f(*args, **kwargs)
    return _inner


def managed_guild_ids() -> set[str]:
    """Return manageable mutual guilds, cached briefly in the signed session."""
    cached_at = session.get("managed_guilds_at", 0)
    cached_ids = session.get("managed_guild_ids")
    if cached_ids is not None and time.time() - cached_at < 300:
        # This cache is populated from OAuth-manageable guilds that were
        # confirmed mutual when /api/guilds ran. Do not intersect it with the
        # gateway cache again here: guilds can populate asynchronously and
        # temporarily disappear from that cache while the owner switches tabs.
        return {str(guild_id) for guild_id in cached_ids}

    if not ensure_access_token():
        return set()
    token = session.get("access_token", "")
    if not token:
        return set()
    try:
        # Same egress as /api/guilds, so a guild page stays reachable while the
        # bot is egressing over its proxy and this host's own IP is blocked.
        all_guilds = member_guilds(token)
    except Exception:
        # Keep a recently OAuth-verified authorization decision through a
        # transient Discord API failure instead of turning it into a false 403.
        cached_ids = session.get("managed_guild_ids")
        if cached_ids is not None and time.time() - session.get("managed_guilds_at", 0) < 300:
            return {str(guild_id) for guild_id in cached_ids}
        return set()

    present = bot_guild_ids()
    manageable = []
    for guild in all_guilds:
        try:
            permissions = int(guild.get("permissions", 0))
        except (TypeError, ValueError):
            permissions = 0
        if (
            bool(permissions & (MANAGE_GUILD_PERM | ADMINISTRATOR_PERM))
            or bool(guild.get("owner"))
        ) and str(guild["id"]) in present:
            manageable.append(str(guild["id"]))
    session["managed_guild_ids"] = manageable
    session["managed_guilds_at"] = time.time()
    return set(manageable)


def require_guild_access(f):
    """Protect a guild route from cross-server reads and writes."""
    @wraps(f)
    def _inner(guild_id, *args, **kwargs):
        if str(guild_id) not in managed_guild_ids():
            return jsonify({"error": "You do not have Manage Server access to this guild."}), 403
        try:
            guild_entry = _load_blacklist_manager().get_guild_entry(int(guild_id))
        except Exception:
            return jsonify({"error": "Guild access could not be verified."}), 503
        if guild_entry:
            return jsonify({
                "error": "This server is blacklisted from using the dashboard.",
                "blacklisted": True,
                "scope": "guild",
                "guild_id": str(guild_id),
                "reason": guild_entry.get("reason") or "No reason provided.",
            }), 403
        return f(guild_id, *args, **kwargs)
    return _inner


def _discord_egress_proxies(http) -> dict | None:
    """The proxy the bot's HTTP client egresses through, mapped for ``requests``.

    discord.py applies ``HTTPClient.proxy`` to every REST call (Webshare proxy
    failover sets it), so a request made from the web process has to use the
    same route or it can be blocked while the bot itself stays responsive.
    """
    proxy = getattr(http, "proxy", None)
    if not isinstance(proxy, str) or not proxy:
        return None
    return {"http": proxy, "https": proxy}


def discord_request(method: str, url: str, **kwargs):
    """Make Discord REST calls the way the bot itself does.

    Discord answers every request through Cloudflare, and that edge challenges
    plain ``python-requests`` traffic from a datacenter IP — the OAuth token
    exchange is a POST, so it is challenged before any dashboard call. The bot's
    own ``User-Agent`` therefore travels with every call. When proxy workers are
    enabled they are the first attempt, followed by the deployment's own egress;
    that is the identity Discord answers for this bot, while the Webshare proxy
    is another datacenter IP the same edge also refuses. When a direct attempt
    comes back as a Cloudflare interstitial the call is relayed to a standby
    when one is configured, then retried over the bot's active proxy. Every
    browser path that touches Discord goes through here, so login, the dashboard
    and the membership checks all share the bot's egress instead of sending a
    bare client from this host.

    A blocked response is only relayed when a signed relay can actually be sent.
    Without an active standby origin and the relay secrets, the Discord response is
    returned untouched so the caller keeps its own error handling instead of
    surfacing a relay misconfiguration as a server error.
    """
    http = getattr(_discord_bot, "http", None) if _discord_bot is not None else None
    headers = dict(kwargs.get("headers") or {})
    user_agent = getattr(http, "user_agent", None)
    if isinstance(user_agent, str) and user_agent:
        headers.setdefault("User-Agent", user_agent)
    if headers:
        kwargs["headers"] = headers
    manager = getattr(_discord_bot, "standby_failover", None) if _discord_bot is not None else None
    proxy_workers = getattr(_discord_bot, "discord_proxy", None) if _discord_bot is not None else None
    if proxy_workers is not None and proxy_workers.can_relay(url):
        try:
            proxied = proxy_workers.request_via_worker(method, url, kwargs)
        except Exception as exc:
            app.logger.warning("Discord proxy worker failed for %s %s: %s", method, url, exc)
        else:
            if manager is None or manager.cloudflare_interstitial(proxied) is None:
                return proxied
            proxied.close()
    response = getattr(req, method.lower())(url, **kwargs)
    if manager is None or manager.cloudflare_interstitial(response) is None:
        return response

    proxies = _discord_egress_proxies(http)
    app.logger.warning(
        "Discord %s %s answered HTTP %s with Cloudflare signatures (relay_configured=%s proxy=%s): %.200s",
        method, url, getattr(response, "status_code", 0), manager.relay_configured(),
        bool(proxies), getattr(response, "text", "") or "",
    )
    # A standby owns this instance's egress while it holds the gateway, so the
    # signed relay keeps its precedence.
    if manager.relay_configured():
        try:
            relayed = manager.request_via_standby(method, url, kwargs)
        except Exception as exc:
            manager.last_error = f"Standby API relay failed ({type(exc).__name__})."
            app.logger.warning("Standby relay failed for %s %s: %s", method, url, exc)
        else:
            response.close()
            return relayed
    # Browser paths have no failover of their own, so fall back to the egress
    # discord.py itself already switched to before reporting the block.
    if proxies is not None and "proxies" not in kwargs:
        try:
            proxied = getattr(req, method.lower())(url, proxies=proxies, **kwargs)
        except req.RequestException as exc:
            app.logger.warning("Discord %s %s failed over the Webshare egress: %s", method, url, exc)
        else:
            if manager.cloudflare_interstitial(proxied) is None:
                response.close()
                return proxied
            proxied.close()
    return response


def discord_get(endpoint: str, token: str):
    """GET a Discord API endpoint using a Bearer token."""
    r = discord_request(
        "GET",
        f"{DISCORD_API}{endpoint}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=8,
    )
    r.raise_for_status()
    return r.json()


# ── Member guild list ────────────────────────────────────────────────────────
# One guild-list fetch has to fit inside a dashboard request, so the retry only
# exists to pick up the proxy the rate-limit hook has just armed.
_MEMBER_GUILDS_REQUEST_TIMEOUT = 6
_MEMBER_GUILDS_ATTEMPTS = 2
_MEMBER_GUILDS_RETRY_CAP = 3.0


class DiscordEgressError(RuntimeError):
    """Discord could not be reached over the bot's own REST egress."""


def _member_guilds_retry_delay(body: str) -> float:
    """How long a limited guild-list request should wait before retrying."""
    try:
        payload = json.loads(body)
    except (TypeError, ValueError):
        return 1.0
    retry_after = payload.get("retry_after") if isinstance(payload, dict) else None
    try:
        delay = float(retry_after)
    except (TypeError, ValueError):
        return 1.0
    return min(max(delay, 0.5), _MEMBER_GUILDS_RETRY_CAP)


async def _member_guilds_via_bot(token: str) -> list:
    """Ask Discord for the member's guilds over the bot's own REST session.

    The session is the one discord.py uses for the bot's own calls, so the
    request inherits its egress: the active Webshare proxy after a global limit,
    the proxy-worker hook installed on the session, and the rate-limit monitor
    that arms that proxy. The member's OAuth token travels as the bearer instead
    of the bot token, because this lists the servers *they* can manage.
    """
    http = getattr(_discord_bot, "http", None) if _discord_bot is not None else None
    session = getattr(http, "_HTTPClient__session", None) if http is not None else None
    if session is None:
        raise DiscordEgressError("The bot's Discord connection is not ready yet.")

    url = f"{DISCORD_API}/users/@me/guilds"
    user_agent = getattr(http, "user_agent", None)
    last_status = 0

    for attempt in range(_MEMBER_GUILDS_ATTEMPTS):
        headers = {"Authorization": f"Bearer {token}"}
        if isinstance(user_agent, str) and user_agent:
            headers["User-Agent"] = user_agent
        kwargs = {"headers": headers, "timeout": _MEMBER_GUILDS_REQUEST_TIMEOUT}

        # Read the proxy on every attempt: the rate-limit hook arms Webshare
        # while a blocked response is being handled, so the retry leaves over
        # the new egress instead of the IP Discord just refused.
        proxy = getattr(http, "proxy", None)
        if isinstance(proxy, str) and proxy:
            kwargs["proxy"] = proxy
        proxy_auth = getattr(http, "proxy_auth", None)
        if proxy_auth is not None:
            kwargs["proxy_auth"] = proxy_auth

        try:
            async with session.get(url, **kwargs) as response:
                status = int(getattr(response, "status", 0) or 0)
                body = await response.text()
        except OSError as exc:
            # A proxy that refuses the connection is rotated by the request
            # hook, so one retry leaves over the replacement egress.
            if attempt + 1 >= _MEMBER_GUILDS_ATTEMPTS:
                raise DiscordEgressError(
                    f"The server list request failed ({type(exc).__name__})."
                ) from exc
            await asyncio.sleep(1.0)
            continue

        if 300 > status >= 200:
            try:
                guilds = json.loads(body)
            except ValueError as exc:
                raise DiscordEgressError("Discord returned an unreadable server list.") from exc
            if not isinstance(guilds, list):
                raise DiscordEgressError("Discord returned an unexpected server list.")
            return guilds

        last_status = status
        # A refused or limited response is what the failover is for; anything
        # else (an expired token, a 500) will not improve on a retry.
        if status not in {403, 429} or attempt + 1 >= _MEMBER_GUILDS_ATTEMPTS:
            break
        await asyncio.sleep(_member_guilds_retry_delay(body))

    raise DiscordEgressError(
        f"Discord answered HTTP {last_status or 'no status'} for the server list."
    )


def member_guilds(token: str) -> list:
    """The guilds the signed-in member can manage, read the way the bot reads.

    ``/dashboard/servers`` used to ask Discord from this Flask thread with a bare
    ``requests`` client, so the call left over the deployment's own IP - the very
    address that was limited or Cloudflare-challenged when Webshare failover
    armed. The list came back empty and the page listed no servers at all while
    the bot itself was healthy.

    Fetching on the bot's event loop over its REST session puts the call on the
    bot's egress instead of a separate one, which is what "proxied with the bot"
    means: whichever route the bot's own REST calls take, this list takes too.
    """
    bot = _discord_bot
    loop = getattr(bot, "loop", None) if bot is not None else None
    if bot is None or loop is None or not loop.is_running():
        # A web-only process has no bot loop or session to borrow.
        return discord_get("/users/@me/guilds", token)
    return run_on_bot_loop(_member_guilds_via_bot(token), timeout=18)


# ── OAuth routes ─────────────────────────────────────────────────────────────









# ── Staff and public team API ────────────────────────────────────────────────

STAFF_PRIORITY = {"owner": 100, "head_admin": 90, "graphic_designer": 80, "head_support": 70, "moderator": 60, "support": 50}


def _presence_members(user_id: str, bot=None) -> list:
    """Every cached member for a user, richest live presence first.

    Discord presence is cached on each ``Member`` and can differ by guild. The
    first guild in ``bot.guilds`` is not guaranteed to be the guild where a
    member's activity was received, which previously made some roles (notably
    Head Admins) appear without Spotify/custom status data. Both the staff cards
    and the Discord profile popups read presence through this one list so the
    two surfaces always agree. Route modules that snapshot their own bot pass it
    explicitly.
    """
    bot = _discord_bot if bot is None else bot
    members = []
    if bot is not None:
        for guild in getattr(bot, "guilds", ()) or ():
            try:
                candidate = guild.get_member(int(user_id))
            except (AttributeError, TypeError, ValueError):
                continue
            if candidate is not None:
                members.append(candidate)

    def presence_score(candidate) -> tuple[int, int, int]:
        raw_status = getattr(candidate, "status", "offline")
        status = getattr(raw_status, "name", None) or str(raw_status)
        status = status.rsplit(".", 1)[-1].lower()
        try:
            activities = getattr(candidate, "activities", ()) or ()
        except Exception:
            activities = ()
        has_custom = any(type(item).__name__.lower() == "customactivity" for item in activities)
        # Prefer activity/custom-status data, then an active presence, and keep
        # the guild order as a stable tie-breaker.
        return (int(bool(activities)), int(has_custom), int(status != "offline"))

    return sorted(members, key=presence_score, reverse=True)


def _presence_member(user_id: str, bot=None):
    """The cached member carrying a user's richest live presence, or ``None``."""
    members = _presence_members(user_id, bot)
    return members[0] if members else None


_CUSTOM_STATUS_PLACEHOLDER = "custom status"


def custom_status_text(activity) -> str | None:
    """The text of a custom status, or ``None`` when it only carries an emoji.

    Discord omits ``state`` from an emoji-only custom status, and discord.py
    then fills both ``state`` and ``name`` with the literal placeholder
    "Custom Status". Rendering either one as the text wrote that placeholder
    into the profile popup beside the emoji instead of showing the emoji alone.
    """
    for attribute in ("state", "name"):
        value = getattr(activity, attribute, None)
        text = str(value).strip() if value is not None else ""
        if text and text.casefold() != _CUSTOM_STATUS_PLACEHOLDER:
            return text
    return None


def _staff_identity(user_id: str) -> dict:
    """Resolve a staff member's global identity and the richest live presence."""
    ordered_members = _presence_members(user_id)
    member = ordered_members[0] if ordered_members else None
    user = member or (_discord_bot.get_user(int(user_id)) if _discord_bot is not None else None)
    cached_identity = None
    if user is None:
        cached_identity_entry = _staff_user_identity_cache.get(str(user_id))
        if cached_identity_entry and time.time() - cached_identity_entry[0] < _STAFF_USER_IDENTITY_CACHE_TTL:
            cached_identity = cached_identity_entry[1]
        elif _discord_bot is not None:
            try:
                # A warm standby may have no gateway-populated user cache.
                # Resolve identity through Discord REST without taking gateway
                # ownership, then cache it to avoid polling Discord every 5s.
                user = run_on_bot_loop(_discord_bot.fetch_user(int(user_id)))
                avatar = getattr(user, "display_avatar", None)
                cached_identity = {
                    "name": getattr(user, "global_name", None) or getattr(user, "name", None),
                    "username": getattr(user, "name", None),
                    "avatar_url": str(avatar.url) if avatar is not None else None,
                }
                _staff_user_identity_cache[str(user_id)] = (time.time(), cached_identity)
            except Exception:
                user = None
    activities = []
    custom_status = None
    seen_activities = set()
    def serialize_emoji(emoji):
        if emoji is None:
            return None
        emoji_id = getattr(emoji, "id", None)
        emoji_name = getattr(emoji, "name", None) or str(emoji)
        return {
            "kind": "custom" if emoji_id else "unicode",
            "value": str(emoji_id) if emoji_id else emoji_name,
            "name": emoji_name,
            "animated": bool(getattr(emoji, "animated", False)),
        }

    for presence_member in ordered_members:
        for activity in getattr(presence_member, "activities", ()) or ():
            activity_type = getattr(getattr(activity, "type", None), "name", None) or str(getattr(activity, "type", "")).rsplit(".", 1)[-1].lower()
            class_name = type(activity).__name__.lower()

            if class_name == "customactivity" or activity_type in {"custom", "customstatus", "custom_activity"}:
                if custom_status is None:
                    custom_status = {
                        "text": custom_status_text(activity),
                        "emoji": serialize_emoji(getattr(activity, "emoji", None)),
                    }
                continue

            # discord.py exposes Spotify and Streaming as dedicated activity
            # classes with attributes that differ from the generic Activity class.
            activity_key = (class_name, getattr(activity, "name", None), getattr(activity, "title", None), getattr(activity, "state", None), getattr(activity, "url", None))
            if activity_key in seen_activities:
                continue
            seen_activities.add(activity_key)

            if class_name == "spotify":
                # The track window drives the progress bar on the profile card.
                # discord.py raises when the presence omits timestamps, so both
                # bounds are read defensively.
                try:
                    track_start = getattr(activity, "start", None)
                    track_end = getattr(activity, "end", None)
                except KeyError:
                    track_start = track_end = None
                activities.append({
                    "kind": "spotify",
                    "type": "listening",
                    "name": "Spotify",
                    "details": getattr(activity, "title", None),
                    "state": getattr(activity, "artist", None),
                    "url": getattr(activity, "track_url", None),
                    "platform": "Spotify",
                    "image_url": getattr(activity, "album_cover_url", None),
                    "start": track_start.isoformat() if track_start else None,
                    "end": track_end.isoformat() if track_end else None,
                })
                continue
            if class_name == "streaming":
                activities.append({
                    "kind": "streaming",
                    "type": "streaming",
                    "name": getattr(activity, "game", None) or getattr(activity, "name", None) or "Live stream",
                    "details": getattr(activity, "platform", None),
                    "state": None,
                    "url": getattr(activity, "url", None),
                    "platform": getattr(activity, "platform", None),
                    "image_url": None,
                })
                continue

            name = getattr(activity, "name", None)
            if name:
                activities.append({
                    "kind": "activity",
                    "type": activity_type,
                    "name": name,
                    "details": getattr(activity, "details", None),
                    "state": getattr(activity, "state", None),
                    "url": getattr(activity, "url", None),
                    "platform": None,
                    "image_url": None,
                })
    raw_status = getattr(member, "status", "offline") if member is not None else "offline"
    # discord.py may expose this as a Status enum (``Status.online``) or a
    # string depending on the cached object/version. Keep the API stable for
    # the frontend by returning the normalized enum value.
    status = getattr(raw_status, "name", None) or str(raw_status)
    status = status.rsplit(".", 1)[-1].lower()
    return {
        "id": str(user_id),
        # Use the global Discord display name, never a guild nickname from
        # whichever guild was checked first.
        "name": getattr(member, "global_name", None) or getattr(getattr(member, "_user", None), "global_name", None) or getattr(user, "global_name", None) or getattr(user, "name", None) or (cached_identity or {}).get("name") or f"Staff member {user_id}",
        "username": getattr(user, "name", None) or (cached_identity or {}).get("username"),
        "avatar_url": str(getattr(getattr(user, "display_avatar", None), "url", "")) or (cached_identity or {}).get("avatar_url"),
        "status": status,
        "status_label": {"online": "Online", "idle": "Idle", "dnd": "Do Not Disturb", "offline": "Offline"}.get(status, status.title()),
        "activities": activities,
        "custom_status": custom_status,
        # Keep the first activity for older clients while the richer fields
        # above are consumed by the current Team page.
        "activity": activities[0]["name"] if activities else None,
    }


def _staff_role_label(role: str) -> str:
    """Turn the persisted role key into the public label without frontend role logic."""
    return STAFF_ROLES.get(role, role.replace("_", " ").strip().title() or "Staff")


def _normalize_public_links(raw) -> list[dict]:
    """Return safe public profile links from the stored JSON value."""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (TypeError, ValueError):
            return []
    if not isinstance(raw, list):
        return []
    links = []
    for link in raw[:10]:
        if not isinstance(link, dict):
            continue
        link_type = str(link.get("type", "")).strip()
        url = str(link.get("url", "")).strip()
        parsed = urlparse(url)
        if link_type and parsed.scheme in {"http", "https"} and parsed.netloc:
            links.append({"type": link_type, "label": str(link.get("label") or link_type.title()), "url": url})
    return links


def _staff_row(row) -> dict:
    role = str(row.get("role"))
    identity = _staff_identity(str(row.get("user_id")))
    return {
        **identity,
        "role": role,
        "role_label": "Owner" if role == "owner" else _staff_role_label(role),
        "bio": row.get("public_bio"),
        # Names and avatars always come from Discord; profile presentation is
        # staff-customizable on the website.
        "public_banner_url": row.get("public_banner_url"),
        "public_links": _normalize_public_links(row.get("public_links")),
        "visible": bool(row.get("public_visible", 1)),
    }


def _load_staff_rows() -> list[dict]:
    """Load every persisted staff role and enrich it with live Discord data.

    Staff roles live in the bot's active database pool. Do not fall back to
    SQLite only when the pool returns an empty list: a web process can have a
    local SQLite file with only the owner seed row while the active deployment
    stores the other roles elsewhere. We also isolate malformed rows so one
    legacy record cannot hide the rest of the roster.
    """
    columns = (
        "user_id", "role", "public_name", "public_bio", "public_avatar_url",
        "public_banner_url", "public_links", "public_visible",
    )
    by_id: dict[str, dict] = {}

    def add_raw(raw) -> None:
        try:
            row = dict(raw)
            user_id = str(row.get("user_id", "")).strip()
            role = str(row.get("role", "")).strip()
            if not user_id or not role:
                return
            # Only configured staff roles should be public. Keep the owner seed
            # in the same roster as database-backed roles.
            if role not in STAFF_ROLES and role != "owner":
                return
            item = _staff_row({**row, "user_id": user_id, "role": role})
            by_id[user_id] = item
        except (TypeError, ValueError, KeyError):
            # A single old/incomplete record must not suppress other roles.
            return

    if _discord_bot is not None and getattr(_discord_bot, "cxn", None):
        async def read_staff():
            return await _discord_bot.cxn.fetch(
                "SELECT user_id, role, public_name, public_bio, public_avatar_url, "
                "public_banner_url, public_links, public_visible FROM staff_members"
            )
        try:
            for row in run_on_bot_loop(read_staff()):
                add_raw(row)
        except Exception:
            # The local fallback below still allows public roster pages to work
            # while the bot pool is reconnecting.
            pass

    # Also read the local store and merge it instead of using it as an
    # all-or-nothing fallback. This covers web-only processes and prevents the
    # owner seed row from masking other staff roles.
    conn = sqlite_connect()
    try:
        if conn:
            raw_rows = conn.execute(
                "SELECT user_id, role, public_name, public_bio, public_avatar_url, "
                "public_banner_url, public_links, public_visible FROM staff_members"
            ).fetchall()
            for raw in raw_rows:
                add_raw(dict(zip(columns, raw)))
    except sqlite3.Error:
        pass
    finally:
        if conn:
            conn.close()

    for user_id in OWNER_IDS:
        user_id = str(user_id)
        if user_id not in by_id:
            add_raw({"user_id": user_id, "role": "owner", "public_visible": 1})

    return sorted(
        (row for row in by_id.values() if row["visible"]),
        key=lambda item: -STAFF_PRIORITY.get(item["role"], 40),
    )


def _current_staff_role() -> str | None:
    user_id = str(session.get("user", {}).get("id", ""))
    if not user_id:
        return None
    try:
        numeric_user_id = int(user_id)
        if numeric_user_id in OWNER_IDS:
            return "owner"
    except (TypeError, ValueError):
        return None

    
    # Staff authorization must use the same live database as the bot. The
    # previous SQLite-only lookup denied valid staff on Mongo/live-pool setups.
    if _discord_bot is not None and getattr(_discord_bot, "cxn", None):
        async def read_role():
            return await _discord_bot.cxn.fetchrow(
                "SELECT role FROM staff_members WHERE user_id = $1", int(user_id)
            )
        try:
            row = run_on_bot_loop(read_role())
            if row and row.get("role"):
                return str(row["role"])
        except Exception:
            pass

    conn = sqlite_connect()
    try:
        row = conn.execute("SELECT role FROM staff_members WHERE user_id = ?", (int(user_id),)).fetchone() if conn else None
        return str(row[0]) if row and row[0] else None
    except (TypeError, ValueError, sqlite3.Error):
        return None
    finally:
        if conn:
            conn.close()












# ── Public API ───────────────────────────────────────────────────────────────

_INTERNAL_COMMAND_COGS = {"owner", "ownercog", "development", "staff", "staffcog"}

# Older command registries predate the ``cog`` and ``module`` fields. Keep the
# current private command names here so those records cannot leak while the
# bot has not yet rewritten data/commands.json.
_LEGACY_INTERNAL_COMMAND_NAMES = {
    "ownerhelp", "setpfp", "setbanner", "setusername", "setstatus", "setactivity",
    "load", "unload", "reload", "restart", "shutdown", "sync", "eval", "servers",
    "serverinvite", "announce", "dev01", "shardinfo", "shardstats", "shardhealth",
    "blacklist", "blacklist info", "blacklist reason", "blacklist add", "blacklist remove",
    "premium", "premium add", "premium remove", "premium list",
    "devhelp", "devload", "devunload", "devreload", "devping", "devlatency",
    "devuptime", "devmem", "devtasks", "devguild", "devchannels", "devroles",
    "devmembers", "deveval", "devexec", "devsay", "devshutdown", "syncemojis",
    "appemojis", "emojistatus", "staff", "staff help", "staff manage",
}


def _is_internal_command(*values) -> bool:
    """Identify commands owned by private owner/development cogs."""
    for value in values:
        if not value:
            continue
        parts = str(value).lower()
        for separator in (".", "/", "\\", ":", "-"):
            parts = parts.replace(separator, " ")
        if any(part.strip() in _INTERNAL_COMMAND_COGS for part in parts.split()):
            return True
    return False


def _live_internal_command_names() -> set[str]:
    """Collect private command names for filtering older registry files."""
    if _discord_bot is None:
        return set()

    names: set[str] = set()

    def add_if_internal(command, qualified_name: str | None = None) -> None:
        binding = getattr(command, "binding", None) or getattr(command, "cog", None)
        callback = getattr(command, "callback", None)
        cog_name = getattr(command, "cog_name", None)
        if _is_internal_command(
            cog_name,
            type(binding).__name__ if binding is not None else None,
            getattr(callback, "__module__", None),
        ):
            command_name = qualified_name or getattr(command, "qualified_name", None) or getattr(command, "name", None)
            if command_name:
                names.add(str(command_name))
                names.add(str(getattr(command, "name", command_name)))

    try:
        for command in _discord_bot.walk_commands():
            add_if_internal(command)
    except Exception:
        pass

    def visit_application_command(command, parent_name: str | None = None) -> None:
        command_name = getattr(command, "name", None)
        if not command_name:
            return
        qualified_name = f"{parent_name} {command_name}" if parent_name else str(command_name)
        add_if_internal(command, qualified_name)
        for child in getattr(command, "commands", []) or []:
            visit_application_command(child, qualified_name)

    try:
        tree = getattr(_discord_bot, "tree", None)
        for command in tree.get_commands() if tree is not None else []:
            visit_application_command(command)
    except Exception:
        pass

    return names


def _description_value(value):
    """Normalise a command help value into a locale map or plain text.

    Command records can store help as a real dict, or as a serialised map
    written in Python literal syntax, e.g.
    "{ 'en': 'Reset XP.', 'de': 'XP zurücksetzen.' }". In both cases we
    return a real ``{locale: text}`` object so the website can pick the
    visitor's language. Anything else passes through untouched.
    """
    if isinstance(value, dict):
        cleaned = {str(k): str(v) for k, v in value.items() if k and v}
        return cleaned if cleaned else ""
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("{"):
            try:
                parsed = json.loads(text.replace("'", '"'))
            except Exception:
                parsed = None
            if isinstance(parsed, dict):
                cleaned = {str(k): str(v) for k, v in parsed.items() if k and v}
                if cleaned:
                    return cleaned
        return value
    return str(value) if value else ""










# ── Auth-gated API ───────────────────────────────────────────────────────────










def _get_levels(guild_id: str) -> list:
    """Fetch level data from the bot's live database, regardless of backend."""
    if _discord_bot is not None and hasattr(_discord_bot, "cxn"):
        async def read_from_bot():
            pool = _discord_bot.cxn
            numeric_guild_id = int(guild_id)

            if getattr(pool, "db_type", None) == "mongodb" and hasattr(pool, "collection"):
                # Older Mongo records may have received the guild ID as text.
                # Read both representations, then sort after coercion so mixed
                # BSON numeric/string values cannot hide real level data.
                documents = await pool.collection("levels").find({
                    "$or": [
                        {"guild_id": numeric_guild_id},
                        {"guild_id": str(numeric_guild_id)},
                        {"_id": {"$regex": rf"^{numeric_guild_id}_"}},
                    ]
                }).to_list(length=None)
                rows = []
                for document in documents:
                    row = dict(document)
                    stored_guild_id = row.get("guild_id")
                    document_id = row.get("_id")
                    if isinstance(document_id, str) and "_" in document_id:
                        composite_guild_id, composite_user_id = document_id.split("_", 1)
                        if stored_guild_id is None:
                            stored_guild_id = composite_guild_id
                        if row.get("user_id") is None:
                            row["user_id"] = composite_user_id
                    if str(stored_guild_id) != str(numeric_guild_id):
                        continue
                    rows.append(row)

                def as_int(value) -> int:
                    try:
                        return int(value or 0)
                    except (TypeError, ValueError):
                        try:
                            return int(float(value))
                        except (TypeError, ValueError):
                            return 0

                rows.sort(
                    key=lambda row: (as_int(row.get("level")), as_int(row.get("xp"))),
                    reverse=True,
                )
                rows = rows[:25]
            else:
                rows = await pool.fetch(
                    "SELECT user_id, xp, level FROM levels "
                    "WHERE guild_id = $1 ORDER BY level DESC, xp DESC LIMIT 25",
                    numeric_guild_id,
                )

            def as_int(value) -> int:
                try:
                    return int(value or 0)
                except (TypeError, ValueError):
                    try:
                        return int(float(value))
                    except (TypeError, ValueError):
                        return 0

            normalized = [
                {
                    "user_id": str(row.get("user_id")),
                    "xp": as_int(row.get("xp")),
                    "level": as_int(row.get("level")),
                }
                for row in rows
                if row.get("user_id") is not None
            ]
            guild = _discord_bot.get_guild(numeric_guild_id)
            metadata = _member_metadata_from_guild(
                guild,
                {row["user_id"] for row in normalized},
            )
            return [{**row, **metadata.get(row["user_id"], {})} for row in normalized]

        try:
            return run_on_bot_loop(read_from_bot())
        except Exception:
            pass

    conn = sqlite_connect()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT user_id, xp, level FROM levels "
                "WHERE guild_id = ? ORDER BY level DESC, xp DESC LIMIT 25",
                (int(guild_id),),
            )
            rows = [
                {"user_id": str(row[0]), "xp": row[1], "level": row[2]}
                for row in cur.fetchall()
            ]
            conn.close()
            metadata = get_member_metadata(guild_id, {row["user_id"] for row in rows})
            rows = [{**row, **metadata.get(row["user_id"], {})} for row in rows]
            return rows
        except Exception:
            conn.close()

    # JSON fallback (migrated snapshot)
    data = load_json(LEVELS_JSON, {})
    guild = data.get(guild_id, {})
    rows  = [{"user_id": uid, "xp": v.get("xp", 0), "level": v.get("level", 0)}
             for uid, v in guild.items()]
    rows.sort(key=lambda x: x["xp"], reverse=True)
    metadata = get_member_metadata(guild_id, {row["user_id"] for row in rows})
    rows = [{**row, **metadata.get(row["user_id"], {})} for row in rows]
    return rows[:25]




def _serialize_onboarding_config(cfg) -> dict:
    """Return onboarding values with exact Discord IDs for the dashboard."""
    from dataclasses import asdict
    serialized = asdict(cfg)
    for field in (
        "welcome_channel", "rules_channel", "rules_role_id", "rules_message_id",
        "captcha_channel_id", "captcha_panel_message_id",
    ):
        if serialized.get(field) is not None:
            serialized[field] = str(serialized[field])
    for field in ("autorole_ids", "bot_autorole_ids", "captcha_add_role_ids", "captcha_remove_role_ids"):
        if serialized.get(field) is not None:
            serialized[field] = [str(value) for value in serialized[field]]
    return serialized


def _serialize_ticket_config(cfg) -> dict:
    """Return the editable ticket settings without internal open-ticket state."""
    guild = _discord_bot.get_guild(int(cfg.guild_id)) if _discord_bot is not None else None
    tickets = []
    for ticket in (cfg.open_tickets or []):
        if not isinstance(ticket, dict):
            continue
        channel_id = str(ticket.get("channel_id", ""))
        channel = _discord_bot.get_channel(int(channel_id)) if _discord_bot is not None and channel_id.isdigit() else None
        opener_id = str(ticket.get("opener_id", ""))
        opener = guild.get_member(int(opener_id)) if guild is not None and opener_id.isdigit() else None
        tickets.append({
            **ticket,
            "channel_id": channel_id,
            "opener_id": opener_id,
            "message_id": str(ticket["message_id"]) if ticket.get("message_id") else None,
            "claimed_by": str(ticket["claimed_by"]) if ticket.get("claimed_by") else None,
            "channel_name": getattr(channel, "name", None),
            "opener_name": getattr(opener, "display_name", None),
        })
    return {
        "panel_title": cfg.panel_title,
        "panel_description": cfg.panel_description,
        "panel_color": cfg.panel_color,
        "panel_image": cfg.panel_image,
        "panel_categories": list(cfg.panel_categories or []),
        "panel_channel_id": str(cfg.panel_channel_id) if cfg.panel_channel_id else None,
        "panel_message_id": str(cfg.panel_message_id) if cfg.panel_message_id else None,
        "support_roles": [str(role_id) for role_id in (cfg.support_roles or [])],
        "open_tickets": tickets,
    }


def _profile_row_to_dict(row) -> dict:
    if not row:
        return {"display_name": None, "bio": None, "avatar_url": None, "banner_url": None, "name_font_id": None, "name_effect_id": 2, "name_colors": []}
    colors = row.get("name_colors")
    try:
        colors = json.loads(colors) if colors else []
    except (TypeError, ValueError):
        colors = []
    return {
        "display_name": row.get("display_name"),
        "bio": row.get("bio"),
        "avatar_url": None,
        "banner_url": None,
        "name_font_id": row.get("name_font_id"),
        "name_effect_id": row.get("name_effect_id") or 2,
        "name_colors": colors,
    }


def _discord_guild_profile_assets(guild_id: str) -> dict:
    """Resolve profile images from Discord instead of retaining uploaded copies."""
    guild_int = int(guild_id)
    if DISCORD_BOT_TOKEN:
        try:
            response = discord_request(
                "GET",
                f"{DISCORD_API}/guilds/{guild_int}/members/@me",
                headers={"Authorization": f"Bot {DISCORD_BOT_TOKEN}"},
                timeout=8,
            )
            if response.status_code == 200:
                payload = response.json()
                user = payload.get("user") or {}
                bot_id = str(user.get("id") or getattr(getattr(_discord_bot, "user", None), "id", ""))
                avatar_hash = payload.get("avatar")
                banner_hash = payload.get("banner")
                avatar_ext = "gif" if str(avatar_hash or "").startswith("a_") else "png"
                banner_ext = "gif" if str(banner_hash or "").startswith("a_") else "png"
                return {
                    "avatar_url": f"https://cdn.discordapp.com/guilds/{guild_int}/users/{bot_id}/avatars/{avatar_hash}.{avatar_ext}?size=512" if avatar_hash and bot_id else None,
                    "banner_url": f"https://cdn.discordapp.com/guilds/{guild_int}/users/{bot_id}/banners/{banner_hash}.{banner_ext}?size=1024" if banner_hash and bot_id else None,
                }
        except Exception:
            pass

    guild = _discord_bot.get_guild(guild_int) if _discord_bot is not None else None
    member = getattr(guild, "me", None) if guild else None
    avatar = getattr(getattr(member, "guild_avatar", None), "url", None)
    banner = getattr(getattr(member, "guild_banner", None), "url", None)
    return {"avatar_url": str(avatar) if avatar else None, "banner_url": str(banner) if banner else None}


def _global_profile_assets() -> dict:
    """Resolve Niko's global (application-wide) avatar and banner.

    The per-guild profile is what a server sets for itself; until a server sets
    one, the dashboard shows Niko's global identity instead. Each image is
    resolved independently: the live bot user is authoritative, and a REST
    ``/users/@me`` read fills in whichever field the cached user object does not
    carry (the gateway payload only includes a banner when one is set).
    """
    user = getattr(_discord_bot, "user", None) if _discord_bot is not None else None
    avatar_url = None
    banner_url = None
    if user is not None:
        avatar_url = str(getattr(getattr(user, "display_avatar", None), "url", "") or "") or None
        banner_url = str(getattr(getattr(user, "banner", None), "url", "") or "") or None

    if (avatar_url and banner_url) or not DISCORD_BOT_TOKEN:
        return {"avatar_url": avatar_url, "banner_url": banner_url}

    try:
        response = discord_request(
            "GET",
            f"{DISCORD_API}/users/@me",
            headers={"Authorization": f"Bot {DISCORD_BOT_TOKEN}"},
            timeout=8,
        )
        if response.status_code == 200:
            payload = response.json()
            user_id = str(payload.get("id") or getattr(user, "id", "") or "")
            avatar_hash = payload.get("avatar")
            banner_hash = payload.get("banner")
            if not avatar_url and avatar_hash and user_id:
                extension = "gif" if str(avatar_hash).startswith("a_") else "png"
                avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.{extension}?size=512"
            if not banner_url and banner_hash and user_id:
                extension = "gif" if str(banner_hash).startswith("a_") else "png"
                banner_url = f"https://cdn.discordapp.com/banners/{user_id}/{banner_hash}.{extension}?size=1024"
    except Exception:
        pass

    return {"avatar_url": avatar_url, "banner_url": banner_url}


def _get_runtime_guild_profile(guild_id: str) -> dict:
    """Read profile text/style from storage and images directly from Discord."""
    assets = _discord_guild_profile_assets(guild_id)
    async def read_from_bot():
        if _discord_bot is None or not getattr(_discord_bot, "cxn", None):
            return None
        return await _discord_bot.cxn.fetchrow(
            "SELECT display_name, bio, name_font_id, name_effect_id, name_colors "
            "FROM guild_profiles WHERE guild_id = $1",
            int(guild_id),
        )

    if _discord_bot is not None and getattr(_discord_bot, "cxn", None):
        try:
            row = run_on_bot_loop(read_from_bot())
            if row:
                return {**_profile_row_to_dict(row), **assets}
        except Exception:
            pass

    conn = sqlite_connect()
    if conn is not None:
        try:
            row = conn.execute(
                "SELECT display_name, bio, name_font_id, name_effect_id, name_colors "
                "FROM guild_profiles WHERE guild_id = ?",
                (int(guild_id),),
            ).fetchone()
            if row:
                return {**_profile_row_to_dict(dict(zip(
                    ("display_name", "bio", "name_font_id", "name_effect_id", "name_colors"), row
                ))), **assets}
        except sqlite3.Error:
            pass
        finally:
            conn.close()

    guild = _discord_bot.get_guild(int(guild_id)) if _discord_bot is not None else None
    member = getattr(guild, "me", None) if guild is not None else None
    return {
        "display_name": getattr(member, "display_name", None) if member else None,
        "bio": None,
        **assets,
        "name_font_id": None,
        "name_effect_id": 2,
        "name_colors": [],
    }


def _save_runtime_guild_profile(guild_id: int, profile: dict) -> None:
    """Write a complete profile row through whichever database is active."""
    async def save_to_bot():
        await _discord_bot.cxn.execute(
            "INSERT OR REPLACE INTO guild_profiles "
            "(guild_id, display_name, bio, name_font_id, name_effect_id, name_colors, updated_at) "
            "VALUES ($1, $2, $3, $4, $5, $6, datetime('now'))",
            guild_id,
            profile.get("display_name"),
            profile.get("bio"),
            profile.get("name_font_id"),
            profile.get("name_effect_id"),
            json.dumps(profile.get("name_colors") or []),
        )

    if _discord_bot is not None and getattr(_discord_bot, "cxn", None):
        run_on_bot_loop(save_to_bot())
        return

    conn = sqlite_connect()
    if conn is None:
        raise RuntimeError("The bot database is unavailable.")
    try:
        conn.execute(
            "INSERT OR REPLACE INTO guild_profiles "
            "(guild_id, display_name, bio, name_font_id, name_effect_id, name_colors, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, datetime('now'))",
            (
                guild_id,
                profile.get("display_name"),
                profile.get("bio"),
                profile.get("name_font_id"),
                profile.get("name_effect_id"),
                json.dumps(profile.get("name_colors") or []),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def _get_runtime_server_config(guild_id: str) -> dict:
    """Read all server-management settings from their existing owners."""
    from utils.prefix_manager import get_prefixes
    from utils.guild_privacy import get_guild_privacy
    from utils.onboarding.config import load_config
    from cogs.logging.formatters import _load_log_config, _guild_config
    from utils.tickets.utils import get_ticket_config

    onboarding = run_on_bot_loop(load_config(int(guild_id)))
    logging_data = run_on_bot_loop(_load_log_config())
    logging_config = _guild_config(logging_data, int(guild_id))
    for category, channel_id in logging_config.items():
        if category != "disabled" and channel_id is not None:
            logging_config[category] = str(channel_id)
    return {
        "prefixes": run_on_bot_loop(
            get_prefixes(int(guild_id), getattr(_discord_bot, "cxn", None))
        ),
        "onboarding": _serialize_onboarding_config(onboarding),
        "logging": logging_config,
        "tickets": _serialize_ticket_config(get_ticket_config(int(guild_id))),
        "profile": _get_runtime_guild_profile(guild_id),
        # Whether the server tag popups in transcripts hide this server.
        "privacy": run_on_bot_loop(
            get_guild_privacy(int(guild_id), getattr(_discord_bot, "cxn", None))
        ),
        # Niko's own identity, so the customization tab can show what a server
        # inherits until it uploads its own avatar or banner.
        "global_profile": _global_profile_assets(),
    }


def _guild_resource_ids(guild_id: int) -> tuple[set[str] | None, set[str] | None]:
    """Return valid channel and role IDs from the live Discord guild."""
    if _discord_bot is None:
        return None, None
    guild = _discord_bot.get_guild(guild_id)
    if guild is None:
        return set(), set()
    return (
        {str(channel.id) for channel in guild.text_channels},
        {str(role.id) for role in guild.roles if not role.is_default()},
    )


async def _refresh_ticket_panel(guild_id: int) -> None:
    """Refresh a configured ticket panel after dashboard edits."""
    from utils.tickets.utils import get_ticket_config
    from cogs.tickets.views import TicketPanelView

    guild = _discord_bot.get_guild(guild_id) if _discord_bot is not None else None
    cfg = get_ticket_config(guild_id)
    if guild is None or not cfg.panel_channel_id or not cfg.panel_message_id:
        return
    channel = guild.get_channel(cfg.panel_channel_id)
    if channel is None:
        return
    try:
        message = await channel.fetch_message(cfg.panel_message_id)
        await message.edit(view=TicketPanelView(guild_id, cfg))
    except Exception:
        pass


async def _refresh_captcha_panel(
    guild_id: int,
    previous_channel_id: int | None = None,
    previous_message_id: int | None = None,
) -> None:
    """Post or update the public Verify panel in its configured channel."""
    from utils.onboarding.config import load_config, save_config
    from cogs.onboarding.views import CaptchaPanelView

    guild = _discord_bot.get_guild(guild_id) if _discord_bot is not None else None
    cfg = await load_config(guild_id)
    if guild is None:
        raise RuntimeError("The selected server is not available to the bot.")
    if not cfg.captcha_channel_id:
        if previous_channel_id and previous_message_id:
            previous_channel = guild.get_channel(previous_channel_id)
            if previous_channel is not None:
                try:
                    previous_message = await previous_channel.fetch_message(previous_message_id)
                    await previous_message.delete()
                except Exception:
                    pass
        cfg.captcha_panel_message_id = None
        await save_config(guild_id, cfg)
        return
    channel = guild.get_channel(cfg.captcha_channel_id)
    if channel is None:
        raise RuntimeError("The configured verification panel channel is unavailable.")

    panel_view = CaptchaPanelView(guild_id)
    message = None
    if previous_channel_id == cfg.captcha_channel_id and previous_message_id:
        try:
            message = await channel.fetch_message(previous_message_id)
            await message.edit(view=panel_view)
        except Exception:
            message = None
    if message is None:
        message = await channel.send(view=panel_view)
        if previous_channel_id and previous_message_id and previous_channel_id != channel.id:
            previous_channel = guild.get_channel(previous_channel_id)
            if previous_channel is not None:
                try:
                    previous_message = await previous_channel.fetch_message(previous_message_id)
                    await previous_message.delete()
                except Exception:
                    pass

    cfg.captcha_channel_id = channel.id
    cfg.captcha_panel_message_id = message.id
    await save_config(guild_id, cfg)
    _discord_bot.add_view(panel_view, message_id=message.id)








def _read_moderation_config_sync(guild_id: str) -> dict:
    """Read moderation config from the bot's database file (SQLite only).

    Used only when the live bot object is unavailable; MongoDB deployments
    always resolve through the running bot instead.
    """
    conn = sqlite_connect()
    if conn is None:
        return {}
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT data FROM moderation_config WHERE guild_id = ?",
            (int(guild_id),),
        )
        row = cur.fetchone()
        if row and row[0]:
            try:
                data = json.loads(row[0])
                if isinstance(data, dict):
                    return data
            except (TypeError, ValueError):
                pass
        return {}
    except sqlite3.Error:
        return {}
    finally:
        conn.close()


def get_runtime_moderation_config(guild_id: str) -> dict:
    """Read the live ModerationUtils config so the dashboard and cog agree."""
    if _discord_bot is not None:
        moderation = _discord_bot.get_cog("ModerationUtils")
        if moderation is not None:
            return moderation.get_guild_config(int(guild_id))
    return _read_moderation_config_sync(guild_id)














def _donation_bot():
    if _discord_bot is None or not getattr(_discord_bot, "cxn", None):
        raise RuntimeError("The bot database is unavailable.")
    return _discord_bot


async def _confirm_donation_from_webhook(track_id: str, payload: dict):
    bot = _donation_bot()
    invoice, newly_confirmed = await confirm_invoice(bot, track_id, payload)
    if invoice is not None and newly_confirmed:
        donation_cog = bot.get_cog("DonationCog")
        if donation_cog is not None:
            await donation_cog._on_payment_confirmed(track_id, dict(invoice))
    return invoice, newly_confirmed








# ── Transcript endpoints ─────────────────────────────────────────────────────





# ── Static file serving ──────────────────────────────────────────────────────





def serve_spa_shell():
    """Serve generated route metadata HTML, falling back to the React shell."""
    route = request.path.strip("/")
    route_html = os.path.join(WEB_DIST_DIR, route, "index.html") if route else ""
    if route_html and os.path.isfile(route_html):
        return send_from_directory(WEB_DIST_DIR, f"{route}/index.html")
    return send_from_directory(WEB_DIST_DIR, "index.html")











def _svg_wrap(body: str, width: int, height: int):
    """Wrap SVG body markup in a complete, embeddable image response.

    The card markup names the Plus Jakarta Sans / Space Mono webfonts, so the
    document imports them; wsrv.nl rasterizes the external stylesheet when it
    converts a card to PNG for Discord.
    """
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        '<style>'
        '@import url("https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&amp;family=Space+Mono:wght@400;700&amp;display=swap");'
        '</style>'
        f'{body}</svg>'
    )
    return Response(svg, mimetype="image/svg+xml")

def _hex_color(val, fallback):
    """Validate and return a hex color string, stripping # if present."""
    val = str(val).lstrip("#")
    if len(val) == 6 and all(c in "0123456789ABCDEFabcdef" for c in val):
        return val
    return fallback


def _int_param(val, default=0):
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def _format_num(n):
    n = int(n)
    if abs(n) >= 1_000_000_000:
        return "{:.2f}B".format(n / 1_000_000_000)
    if abs(n) >= 1_000_000:
        return "{:.2f}M".format(n / 1_000_000)
    if abs(n) >= 10_000:
        return "{:.1f}K".format(n / 1_000)
    return "{:,}".format(n)


def _safe(text):
    """Escape XML special characters."""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ── SVG Card Routes ─────────────────────────────────────────────────────────────

def _db_query(sql, params=None):
    """Synchronous SQLite query helper for card routes."""
    import sqlite3
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    try:
        cur = db.execute(sql, params or ())
        return [dict(row) for row in cur.fetchall()]
    except Exception:
        return []
    finally:
        db.close()


def _db_fetchone(sql, params=None):
    """Synchronous SQLite fetchone helper."""
    rows = _db_query(sql, params)
    return rows[0] if rows else None


def _get_guild_card_colors(guild_id):
    """Return (accent_hex, bg_top_hex, bg_bot_hex) for a guild's level config."""
    row = _db_fetchone(
        "SELECT card_accent, card_bg_top, card_bg_bottom FROM level_config WHERE guild_id = ?",
        (int(guild_id),),
    )
    if row:
        def _parse(val, default):
            if not val:
                return default
            try:
                import json
                rgb = json.loads(val) if isinstance(val, str) else val
                if isinstance(rgb, (list, tuple)) and len(rgb) >= 3:
                    return f"{int(rgb[0]):02X}{int(rgb[1]):02X}{int(rgb[2]):02X}"
            except Exception:
                pass
            return default
        return (_parse(row.get("card_accent"), "D5D9DF"),
                _parse(row.get("card_bg_top"), "111316"),
                _parse(row.get("card_bg_bottom"), "050607"))
    # A guild without custom card colours gets the website theme palette.
    return ("D5D9DF", "111316", "050607")


def _get_user_economy(user_id):
    """Fetch economy data for a user."""
    return _db_fetchone("SELECT * FROM economy_users WHERE user_id = ?", (int(user_id),))



















def static_proxy(path):
    requested = os.path.join(WEB_DIST_DIR, path)
    if os.path.isfile(requested):
        return send_from_directory(WEB_DIST_DIR, path)
    return send_from_directory(WEB_DIST_DIR, "index.html")


@app.errorhandler(404)
def spa_not_found(error):
    """Keep browser navigations inside the SPA while preserving API 404s."""
    if request.path.startswith("/api/") or request.path.startswith("/auth/"):
        return jsonify({"error": "Not found"}), 404
    if request.accept_mimetypes.accept_html:
        return send_from_directory(WEB_DIST_DIR, "index.html")
    return error


