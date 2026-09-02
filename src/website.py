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
from urllib.parse import urlencode
from functools import wraps
from flask import (
    Flask, send_from_directory, session,
    redirect, request, jsonify, url_for
)
import requests as req

# ── Constants ────────────────────────────────────────────────────────────────

DISCORD_CLIENT_ID     = "1520558530472448170"
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "")
DISCORD_BOT_TOKEN     = os.environ.get("DISCORD_BOT_TOKEN", "")
DISCORD_API           = "https://discord.com/api/v10"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")
ECONOMY_DIR  = os.path.join(DATA_DIR, "economy_data")
BOT_STATS    = os.path.join(DATA_DIR, "bot_stats.json")
AICFG        = os.path.join(DATA_DIR, "ai_config.json")
LEVELS_JSON  = os.path.join(DATA_DIR, "levels.json.migrated")
LEVELCFG_JSON = os.path.join(DATA_DIR, "level_config.json.migrated")
DATABASE_PATH = os.path.join(DATA_DIR, "database.db")

MANAGE_GUILD_PERM = 0x20
ADMINISTRATOR_PERM = 0x8

# ── App setup ────────────────────────────────────────────────────────────────

WEB_DIST_DIR = os.path.join(os.path.dirname(__file__), "website", "dist")
app = Flask(__name__, static_folder=WEB_DIST_DIR, static_url_path="")
app.secret_key = os.environ.get("SESSION_SECRET", secrets.token_hex(32))
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"]   = True
app.config["SESSION_COOKIE_HTTPONLY"] = True

_discord_bot = None
_member_metadata_cache: dict[str, tuple[float, dict[str, dict]]] = {}

# ── Helpers ──────────────────────────────────────────────────────────────────

def oauth_enabled() -> bool:
    return bool(DISCORD_CLIENT_SECRET)


def configure_bot(bot) -> None:
    """Give the API access to the live bot for guild and runtime config sync."""
    global _discord_bot
    _discord_bot = bot


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


def get_runtime_level_config(guild_id: str) -> dict:
    """Read leveling settings through the live leveling cog when available."""
    if _discord_bot is not None:
        leveling = _discord_bot.get_cog("Leveling")
        if leveling is not None and hasattr(leveling, "_guild_cfg"):
            try:
                return run_on_bot_loop(leveling._guild_cfg(int(guild_id)))
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
                "       level_up_channel, level_up_message, level_roles "
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
                }
            conn.close()
        except Exception:
            conn.close()

    return level_cfg or load_json(LEVELCFG_JSON, {}).get(guild_id, {})


@app.after_request
def prevent_dynamic_cache(response):
    """Never let auth or dashboard API responses become stale in production."""
    if request.path.startswith("/api/") or request.path.startswith("/auth/"):
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"
    return response


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
    """Return the set of guild IDs the bot is currently in."""
    if _discord_bot is not None:
        return {str(guild.id) for guild in _discord_bot.guilds}
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
            "display_name": getattr(member, "display_name", None) or getattr(member, "name", None),
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
            response = req.get(
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
                "display_name": member.get("nick") or discord_user.get("global_name") or discord_user.get("username"),
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
        "achievements, total_earned FROM economy_users"
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


def require_auth(f):
    """Decorator: return 401 JSON if the session has no Discord user."""
    @wraps(f)
    def _inner(*args, **kwargs):
        if not ensure_access_token():
            return jsonify({
                "error": "Not authenticated",
                "login_url": "/auth/login",
            }), 401
        return f(*args, **kwargs)
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
        response = req.post(
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
    if cached_ids is not None and time.time() - cached_at < 60:
        return {str(guild_id) for guild_id in cached_ids}

    if not ensure_access_token():
        return set()
    token = session.get("access_token", "")
    if not token:
        return set()
    try:
        all_guilds = discord_get("/users/@me/guilds", token)
    except Exception:
        return set()

    present = bot_guild_ids()
    manageable = []
    for guild in all_guilds:
        permissions = int(guild.get("permissions", 0))
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
        return f(guild_id, *args, **kwargs)
    return _inner


def discord_get(endpoint: str, token: str):
    """GET a Discord API endpoint using a Bearer token."""
    r = req.get(
        f"{DISCORD_API}{endpoint}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=8,
    )
    r.raise_for_status()
    return r.json()


# ── OAuth routes ─────────────────────────────────────────────────────────────

@app.route("/auth/login")
def auth_login():
    if not oauth_enabled():
        return jsonify({
            "error": "Discord OAuth is not configured.",
            "hint": "Add DISCORD_CLIENT_SECRET to your Replit secrets to enable login.",
        }), 503

    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state
    next_path = request.args.get("next", "/dashboard")
    session["oauth_next"] = next_path if next_path.startswith("/") and not next_path.startswith("//") else "/dashboard"

    params = urlencode({
        "client_id": DISCORD_CLIENT_ID,
        "redirect_uri": redirect_uri(),
        "response_type": "code",
        "scope": "identify guilds",
        "state": state,
    })
    return redirect(f"https://discord.com/oauth2/authorize?{params}")


@app.route("/auth/callback")
def auth_callback():
    error = request.args.get("error")
    if error:
        return redirect("/?error=oauth_denied")

    if request.args.get("state") != session.pop("oauth_state", None):
        return redirect("/?error=invalid_state")

    code = request.args.get("code", "")
    if not code:
        return redirect("/?error=no_code")

    # Exchange code for access token
    token_resp = req.post(
        "https://discord.com/api/oauth2/token",
        data={
            "client_id":     DISCORD_CLIENT_ID,
            "client_secret": DISCORD_CLIENT_SECRET,
            "grant_type":    "authorization_code",
            "code":          code,
            "redirect_uri":  redirect_uri(),
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    if not token_resp.ok:
        return redirect("/?error=token_exchange_failed")

    token_data   = token_resp.json()
    access_token = token_data["access_token"]

    # Fetch user identity
    try:
        user = discord_get("/users/@me", access_token)
    except Exception:
        return redirect("/?error=user_fetch_failed")

    session["user"]         = user
    session["access_token"] = access_token
    session["refresh_token"] = token_data.get("refresh_token")
    session["token_exp"]    = time.time() + token_data.get("expires_in", 604800)

    return redirect(session.pop("oauth_next", "/dashboard"))


@app.route("/auth/logout")
def auth_logout():
    token = session.get("access_token")
    if token:
        try:
            req.post(
                f"{DISCORD_API}/oauth2/token/revoke",
                data={"client_id": DISCORD_CLIENT_ID, "client_secret": DISCORD_CLIENT_SECRET, "token": token},
                timeout=5,
            )
        except Exception:
            pass
    session.clear()
    return redirect("/")


@app.route("/auth/status")
def auth_status():
    if not ensure_access_token():
        return jsonify({
            "authenticated":   False,
            "oauth_available": oauth_enabled(),
        })
    session.setdefault("csrf_token", secrets.token_urlsafe(24))
    return jsonify({
        "authenticated":   True,
        "oauth_available": True,
        "user":            session["user"],
        "csrf_token":      session["csrf_token"],
    })


# ── Public API ───────────────────────────────────────────────────────────────

@app.route("/api/commands")
def api_commands():
    """Public endpoint — returns all bot commands from the JSON written by the bot on startup."""
    raw_commands = load_json("data/commands.json", [])
    valid_types = {"slash", "prefix", "hybrid", "context"}
    cmds = []
    for command in raw_commands if isinstance(raw_commands, list) else []:
        if not isinstance(command, dict) or not command.get("name"):
            continue
        normalized = {
            "name": str(command["name"]),
            "description": str(command.get("description") or ""),
            "category": str(command.get("category") or "utility"),
            "type": command.get("type") if command.get("type") in valid_types else "slash",
        }
        if command.get("context_type") in {"user", "message"}:
            normalized["context_type"] = command["context_type"]
        cmds.append(normalized)
    category = request.args.get("category", "").strip().lower()
    if category:
        cmds = [c for c in cmds if c.get("category") == category]
    return jsonify(cmds)


@app.route("/api/health")
def api_health():
    return jsonify({"ok": True, "service": "niko-api", "static_build": os.path.exists(os.path.join(WEB_DIST_DIR, "index.html"))})


@app.route("/api/config")
def api_public_config():
    return jsonify({
        "application_id": DISCORD_CLIENT_ID,
        "invite_url": (
            f"https://discord.com/oauth2/authorize?"
            f"{urlencode({'client_id': DISCORD_CLIENT_ID, 'permissions': '8', 'scope': 'bot applications.commands'})}"
        ),
        "oauth_available": oauth_enabled(),
    })


@app.route("/api/botstats")
def api_botstats():
    stats = load_json(BOT_STATS, {})
    econ_count = len(glob.glob(os.path.join(ECONOMY_DIR, "[0-9]*.json")))
    return jsonify({
        "guild_count":   stats.get("guild_count", 0),
        "user_count":    stats.get("user_count", 0),
        "command_count": stats.get("command_count", 76),
        "uptime_since":  stats.get("uptime_since", None),
        "version":       stats.get("version", "1.0"),
        "economy_users": econ_count,
    })


# ── Auth-gated API ───────────────────────────────────────────────────────────

@app.route("/api/me")
@require_auth
def api_me():
    return jsonify(session["user"])


@app.route("/api/me/overview")
@require_auth
def api_me_overview():
    """Return the signed-in user's personal Niko profile and economy snapshot."""
    user_id = str(session["user"].get("id", ""))
    profiles = get_runtime_economy_rows()
    if profiles is None:
        # Compatibility for older web-only installs while the DB is unavailable.
        profiles = []
        for filepath in glob.glob(os.path.join(ECONOMY_DIR, "[0-9]*.json")):
            data = load_json(filepath, {})
            if isinstance(data, dict):
                profiles.append(_normalize_economy_row({
                    "user_id": os.path.basename(filepath).replace(".json", ""),
                    **data,
                }))

    profiles.sort(key=lambda row: row["net_worth"], reverse=True)
    rank = next(
        (index + 1 for index, row in enumerate(profiles) if row["user_id"] == user_id),
        None,
    )
    profile = next((row for row in profiles if row["user_id"] == user_id), {})

    return jsonify({
        "balance": profile.get("balance", 0),
        "bank": profile.get("bank", 0),
        "net_worth": profile.get("net_worth", 0),
        "level": profile.get("level", 0),
        "job": profile.get("job", "barista"),
        "daily_streak": profile.get("daily_streak", 0),
        "achievements": profile.get("achievements", 0),
        "total_earned": profile.get("total_earned", 0),
        "economy_rank": rank,
        "economy_profiles": len(profiles),
    })


@app.route("/api/guilds")
@require_auth
def api_guilds():
    """Guilds the user can manage, annotated with Niko's install state."""
    token = session.get("access_token", "")
    try:
        all_guilds = discord_get("/users/@me/guilds", token)
    except Exception:
        return jsonify([])

    present = bot_guild_ids()
    result  = []
    for g in all_guilds:
        try:
            perms = int(g.get("permissions", 0))
        except (TypeError, ValueError):
            perms = 0
        is_admin = bool(perms & (MANAGE_GUILD_PERM | ADMINISTRATOR_PERM)) or bool(g.get("owner"))
        if is_admin:
            icon_hash = g.get("icon")
            icon_url  = (
                f"https://cdn.discordapp.com/icons/{g['id']}/{icon_hash}.webp?size=64"
                if icon_hash else None
            )
            installed = str(g["id"]) in present
            result.append({
                "id":       g["id"],
                "name":     g["name"],
                "icon_url": icon_url,
                "owner":    bool(g.get("owner")),
                "permissions": perms,
                "installed": installed,
                "invite_url": (
                    f"https://discord.com/oauth2/authorize?"
                    f"{urlencode({'client_id': DISCORD_CLIENT_ID, 'permissions': '8', 'scope': 'bot applications.commands', 'guild_id': g['id']})}"
                    if not installed else None
                ),
            })
    session["managed_guild_ids"] = [guild["id"] for guild in result if guild["installed"]]
    session["managed_guilds_at"] = time.time()
    return jsonify(result)


@app.route("/api/guild/<guild_id>/overview")
@require_auth
@require_guild_access
def api_guild_overview(guild_id):
    # ── Warnings ──────────────────────────────────────────────
    warns      = load_json("data/warns.json", {})
    guild_warns = warns.get(guild_id, {})
    warn_count = sum(len(v) for v in guild_warns.values())

    # ── Automod quick status ──────────────────────────────────
    modcfg   = get_runtime_moderation_config(guild_id)
    automod  = modcfg.get("automod", {})
    automod_on = any(automod.values()) if isinstance(automod, dict) else False

    # ── Level leaderboard (quick top-5) ──────────────────────
    top_levels = _get_levels(guild_id)[:5]

    return jsonify({
        "moderation": {
            "warn_count":     warn_count,
            "automod_active": automod_on,
        },
        "leveling": {
            "top": top_levels,
        },
    })



def _get_levels(guild_id: str) -> list:
    """Fetch level data from the same SQLite database the bot uses."""
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


@app.route("/api/guild/<guild_id>/levels")
@require_auth
@require_guild_access
def api_guild_levels(guild_id):
    return jsonify(_get_levels(guild_id))


def _serialize_onboarding_config(cfg) -> dict:
    """Return only JSON-safe onboarding values for the dashboard."""
    from dataclasses import asdict
    return asdict(cfg)


def _serialize_ticket_config(cfg) -> dict:
    """Return the editable ticket settings without internal open-ticket state."""
    return {
        "panel_title": cfg.panel_title,
        "panel_description": cfg.panel_description,
        "panel_color": cfg.panel_color,
        "panel_image": cfg.panel_image,
        "panel_categories": list(cfg.panel_categories or []),
        "panel_channel_id": str(cfg.panel_channel_id) if cfg.panel_channel_id else None,
        "panel_message_id": str(cfg.panel_message_id) if cfg.panel_message_id else None,
        "support_roles": [str(role_id) for role_id in (cfg.support_roles or [])],
    }


def _get_runtime_server_config(guild_id: str) -> dict:
    """Read all server-management settings from their existing owners."""
    from utils.prefix_manager import get_prefixes
    from utils.onboarding.config import load_config
    from cogs.logging.formatters import _load_log_config, _guild_config
    from utils.tickets.utils import get_ticket_config

    onboarding = run_on_bot_loop(load_config(int(guild_id)))
    logging_data = run_on_bot_loop(_load_log_config())
    return {
        "prefixes": list(get_prefixes(int(guild_id))),
        "onboarding": _serialize_onboarding_config(onboarding),
        "logging": _guild_config(logging_data, int(guild_id)),
        "tickets": _serialize_ticket_config(get_ticket_config(int(guild_id))),
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


@app.route("/api/guild/<guild_id>/config")
@require_auth
@require_guild_access
def api_guild_config(guild_id):
    modcfg  = get_runtime_moderation_config(guild_id)
    aicfg   = load_json(AICFG,  {}).get(str(guild_id), {})
    level_cfg = get_runtime_level_config(guild_id)

    try:
        server_cfg = _get_runtime_server_config(guild_id)
    except Exception as error:
        return jsonify({"error": f"Server settings are unavailable: {error}"}), 503

    return jsonify({
        "moderation": modcfg,
        "ai":         aicfg,
        "leveling":   level_cfg,
        "server":     server_cfg,
    })


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


@app.route("/api/guild/<guild_id>/resources")
@require_auth
@require_guild_access
def api_guild_resources(guild_id):
    guild = _discord_bot.get_guild(int(guild_id)) if _discord_bot is not None else None
    if guild is None:
        return jsonify({"channels": [], "roles": []})
    return jsonify({
        "channels": [
            {"id": str(channel.id), "name": channel.name}
            for channel in guild.text_channels
        ],
        "roles": [
            {"id": str(role.id), "name": role.name}
            for role in guild.roles
            if not role.is_default()
        ],
    })


@app.route("/api/guild/<guild_id>/config/automod", methods=["POST"])
@require_auth
@require_guild_access
@require_csrf
def api_save_automod(guild_id):
    body = request.get_json(silent=True) or {}
    moderation = _discord_bot.get_cog("ModerationUtils") if _discord_bot is not None else None
    if moderation is not None:
        guild_config = moderation.get_guild_config(int(guild_id))
    else:
        guild_config = _read_moderation_config_sync(guild_id)
        if not guild_config:
            guild_config = {}

    allowed_flags = {
        "antispam", "antilink", "badwords", "massmention",
        "antinuke", "antiraid", "antiraid_ext",
    }
    existing = guild_config.get("automod", {})
    for key in allowed_flags:
        if key in body.get("automod", {}):
            existing[key] = bool(body["automod"][key])
    guild_config["automod"] = existing

    integer_fields = {
        "spam_threshold": (1, 100),
        "spam_interval": (1, 3600),
        "max_mentions": (1, 100),
    }
    for key, (minimum, maximum) in integer_fields.items():
        if key in body:
            try:
                value = int(body[key])
            except (TypeError, ValueError):
                return jsonify({"error": f"{key} must be a whole number."}), 400
            if not minimum <= value <= maximum:
                return jsonify({"error": f"{key} must be between {minimum} and {maximum}."}), 400
            guild_config[key] = value

    nested_fields = {
        "antinuke": {
            "ban_threshold": (1, 100), "kick_threshold": (1, 100),
            "channel_delete_threshold": (1, 100), "role_delete_threshold": (1, 100),
            "interval": (1, 3600),
        },
        "antiraid": {"join_threshold": (1, 1000), "join_interval": (1, 3600)},
        "antiraid_ext": {
            "interaction_threshold": (1, 1000), "interaction_window": (1, 3600),
            "join_age_limit": (1, 86400), "ext_app_threshold": (1, 1000),
            "ext_app_window": (1, 3600),
        },
    }
    for section, fields in nested_fields.items():
        incoming = body.get(section)
        if not isinstance(incoming, dict):
            continue
        target = guild_config.setdefault(section, {})
        for key, (minimum, maximum) in fields.items():
            if key in incoming:
                try:
                    value = int(incoming[key])
                except (TypeError, ValueError):
                    return jsonify({"error": f"{section}.{key} must be a whole number."}), 400
                if not minimum <= value <= maximum:
                    return jsonify({"error": f"{section}.{key} must be between {minimum} and {maximum}."}), 400
                target[key] = value
        for key, choices in {
            "action": {"strip", "kick", "ban"},
            "raider_action": {"kick", "ban", "softban", "slowmode", "lockdown"},
            "operator_action": {"notify", "kick", "ban"},
            "ext_app_action": {"kick", "ban", "warn"},
        }.items():
            if key in incoming and incoming[key] in choices:
                target[key] = incoming[key]
        if section == "antiraid_ext" and "ext_app_detection" in incoming:
            target["ext_app_detection"] = bool(incoming["ext_app_detection"])

    if moderation is not None:
        moderation.config[str(guild_id)] = guild_config
        moderation.save_config(int(guild_id))
    else:
        # No live bot: persist through the SQLite dashboard connection.
        conn = sqlite_connect()
        if conn is None:
            return jsonify({"error": "The bot database is unavailable."}), 503
        try:
            conn.execute(
                "INSERT OR REPLACE INTO moderation_config (guild_id, data) VALUES (?, ?)",
                (int(guild_id), json.dumps(guild_config)),
            )
            conn.commit()
        except sqlite3.Error:
            conn.rollback()
            return jsonify({"error": "The moderation settings could not be saved."}), 500
        finally:
            conn.close()
    return jsonify({"ok": True, "config": guild_config})


@app.route("/api/guild/<guild_id>/config/server", methods=["POST"])
@require_auth
@require_guild_access
@require_csrf
def api_save_server(guild_id):
    """Persist prefixes, onboarding, logging, and ticket settings."""
    body = request.get_json(silent=True) or {}
    from utils.prefix_manager import add_prefix, reset_prefixes
    from utils.onboarding.config import load_config, save_config
    from cogs.logging.formatters import _load_log_config, _guild_config, _save_guild_log_config, CATEGORIES
    from utils.tickets.utils import get_ticket_config, update_ticket_config

    try:
        numeric_guild_id = int(guild_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid guild ID."}), 400

    prefixes = body.get("prefixes")
    if prefixes is not None:
        if not isinstance(prefixes, list):
            return jsonify({"error": "Prefixes must be a list."}), 400
        cleaned = []
        for prefix in prefixes:
            if not isinstance(prefix, str) or not prefix.strip() or len(prefix) > 10:
                return jsonify({"error": "Each prefix must be 1 to 10 characters."}), 400
            value = prefix.strip()
            if value not in cleaned:
                cleaned.append(value)
        if not cleaned:
            return jsonify({"error": "At least one prefix is required."}), 400
        reset_prefixes(numeric_guild_id)
        for prefix in cleaned:
            if prefix != ".":
                add_prefix(numeric_guild_id, prefix)

    channel_ids, role_ids = _guild_resource_ids(numeric_guild_id)
    if channel_ids == set() and role_ids == set():
        return jsonify({"error": "The selected server is not available to the bot."}), 503

    onboarding_data = body.get("onboarding")
    if onboarding_data is not None:
        if not isinstance(onboarding_data, dict):
            return jsonify({"error": "Onboarding settings must be an object."}), 400
        onboarding = run_on_bot_loop(load_config(numeric_guild_id))
        allowed = {
            "welcome_channel", "welcome_title", "welcome_description",
            "welcome_color", "welcome_image", "rules_channel", "rules_text",
            "rules_role_id", "autorole_ids", "captcha_enabled",
            "captcha_channel_id", "captcha_add_role_ids", "captcha_remove_role_ids",
            "captcha_kick_on_fail",
        }
        for key in set(onboarding_data) - allowed:
            return jsonify({"error": f"Unsupported onboarding field: {key}"}), 400
        id_fields = {
            "welcome_channel", "rules_channel", "rules_role_id",
            "captcha_channel_id",
        }
        for key, value in onboarding_data.items():
            if key in id_fields:
                if value in (None, ""):
                    setattr(onboarding, key, None)
                elif str(value).isdigit():
                    resource_ids = role_ids if key == "rules_role_id" else channel_ids
                    if resource_ids is not None and str(value) not in resource_ids:
                        return jsonify({"error": f"{key} does not belong to this server."}), 400
                    setattr(onboarding, key, int(value))
                else:
                    return jsonify({"error": f"{key} must be a valid Discord ID."}), 400
            elif key == "welcome_color":
                try:
                    color = int(str(value).replace("#", ""), 16) if value not in (None, "") else None
                except ValueError:
                    return jsonify({"error": "Welcome color must be a hexadecimal value."}), 400
                if color is not None and not 0 <= color <= 0xFFFFFF:
                    return jsonify({"error": "Welcome color must be a valid hexadecimal color."}), 400
                onboarding.welcome_color = color
            elif key in {"autorole_ids", "captcha_add_role_ids", "captcha_remove_role_ids"}:
                if not isinstance(value, list) or any(not str(item).isdigit() for item in value):
                    return jsonify({"error": f"{key} must contain valid Discord IDs."}), 400
                if role_ids is not None and any(str(item) not in role_ids for item in value):
                    return jsonify({"error": f"{key} contains a role from another server."}), 400
                setattr(onboarding, key, [int(item) for item in value])
            elif key in {"captcha_enabled", "captcha_kick_on_fail"}:
                setattr(onboarding, key, bool(value))
            else:
                if value is not None and len(str(value)) > (2000 if key in {"welcome_description", "rules_text"} else 200):
                    return jsonify({"error": f"{key} is too long."}), 400
                setattr(onboarding, key, value or None)
        run_on_bot_loop(save_config(numeric_guild_id, onboarding))

    logging_data = body.get("logging")
    if logging_data is not None:
        if not isinstance(logging_data, dict):
            return jsonify({"error": "Logging settings must be an object."}), 400
        current = run_on_bot_loop(_load_log_config())
        logging_cfg = _guild_config(current, numeric_guild_id)
        for category, value in logging_data.items():
            if category == "disabled":
                if not isinstance(value, list) or any(item not in CATEGORIES for item in value):
                    return jsonify({"error": "Logging disabled categories are invalid."}), 400
                logging_cfg[category] = list(dict.fromkeys(value))
            elif category in CATEGORIES:
                if value in (None, ""):
                    logging_cfg[category] = None
                elif str(value).isdigit():
                    if channel_ids is not None and str(value) not in channel_ids:
                        return jsonify({"error": f"{category} does not belong to this server."}), 400
                    logging_cfg[category] = int(value)
                else:
                    return jsonify({"error": f"{category} must be a valid channel ID."}), 400
            else:
                return jsonify({"error": f"Unsupported logging category: {category}"}), 400
        run_on_bot_loop(_save_guild_log_config(numeric_guild_id, logging_cfg))

    tickets_data = body.get("tickets")
    if tickets_data is not None:
        if not isinstance(tickets_data, dict):
            return jsonify({"error": "Ticket settings must be an object."}), 400
        tickets = get_ticket_config(numeric_guild_id)
        allowed = {
            "panel_title", "panel_description", "panel_color", "panel_image",
            "panel_categories", "panel_channel_id", "support_roles",
        }
        unknown = set(tickets_data) - allowed
        if unknown:
            return jsonify({"error": f"Unsupported ticket fields: {', '.join(sorted(unknown))}"}), 400
        if "panel_title" in tickets_data:
            value = tickets_data["panel_title"]
            if value is not None and len(str(value)) > 200:
                return jsonify({"error": "Ticket panel title is too long."}), 400
            tickets.panel_title = str(value).strip() if value else None
        if "panel_description" in tickets_data:
            value = tickets_data["panel_description"]
            if value is not None and len(str(value)) > 2000:
                return jsonify({"error": "Ticket panel description is too long."}), 400
            tickets.panel_description = str(value).strip() if value else None
        if "panel_color" in tickets_data:
            value = tickets_data["panel_color"]
            try:
                tickets.panel_color = int(str(value).replace("#", ""), 16) if value not in (None, "") else None
            except ValueError:
                return jsonify({"error": "Ticket panel color must be hexadecimal."}), 400
        if "panel_image" in tickets_data:
            value = tickets_data["panel_image"]
            tickets.panel_image = str(value).strip() if value else None
        if "panel_categories" in tickets_data:
            categories = tickets_data["panel_categories"]
            if not isinstance(categories, list) or any(not isinstance(item, str) or not item.strip() for item in categories):
                return jsonify({"error": "Ticket categories must be a list of names."}), 400
            tickets.panel_categories = list(dict.fromkeys(item.strip()[:80] for item in categories))[:25]
        if "panel_channel_id" in tickets_data:
            value = tickets_data["panel_channel_id"]
            if value in (None, ""):
                tickets.panel_channel_id = None
            elif str(value).isdigit():
                if channel_ids is not None and str(value) not in channel_ids:
                    return jsonify({"error": "Ticket panel channel does not belong to this server."}), 400
                tickets.panel_channel_id = int(value)
            else:
                return jsonify({"error": "Ticket panel channel must be a valid channel ID."}), 400
        if "support_roles" in tickets_data:
            roles = tickets_data["support_roles"]
            if not isinstance(roles, list) or any(not str(item).isdigit() for item in roles):
                return jsonify({"error": "Support roles must contain valid Discord IDs."}), 400
            if role_ids is not None and any(str(item) not in role_ids for item in roles):
                return jsonify({"error": "Support roles contains a role from another server."}), 400
            tickets.support_roles = list(dict.fromkeys(int(item) for item in roles))
        update_ticket_config(numeric_guild_id, tickets)
        if _discord_bot is not None:
            try:
                run_on_bot_loop(_refresh_ticket_panel(numeric_guild_id))
            except Exception:
                pass

    try:
        config = _get_runtime_server_config(guild_id)
    except Exception as error:
        return jsonify({"error": f"Settings saved, but could not reload them: {error}"}), 503
    return jsonify({"ok": True, "config": config})


@app.route("/api/guild/<guild_id>/config/ai", methods=["POST"])
@require_auth
@require_guild_access
@require_csrf
def api_save_ai(guild_id):
    body = request.get_json(silent=True) or {}
    data = load_json(AICFG, {})
    guild_id = str(guild_id)
    if guild_id not in data:
        data[guild_id] = {"personality": "cafe", "enabled": "True"}

    if body.get("personality") in ("cafe", "normal"):
        data[guild_id]["personality"] = body["personality"]
    if "enabled" in body:
        data[guild_id]["enabled"] = "True" if body["enabled"] else "False"
    for experiment in ("ai_actions_experiment", "better_context_experiment"):
        if experiment in body:
            data[guild_id][experiment] = "True" if body[experiment] else "False"

    save_json(AICFG, data)
    return jsonify({"ok": True, "config": data[guild_id]})


@app.route("/api/guild/<guild_id>/config/leveling", methods=["POST"])
@require_auth
@require_guild_access
@require_csrf
def api_save_leveling(guild_id):
    body = request.get_json(silent=True) or {}
    allowed_actions = {"xp_enabled", "xp_multiplier", "xp_cooldown", "level_up_channel", "level_up_message"}
    unknown = set(body) - allowed_actions
    if unknown:
        return jsonify({"error": f"Unsupported leveling fields: {', '.join(sorted(unknown))}"}), 400
    try:
        multiplier = float(body.get("xp_multiplier", 1.0))
        cooldown = int(body.get("xp_cooldown", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "XP multiplier and cooldown must be valid numbers."}), 400
    if not 0.1 <= multiplier <= 10:
        return jsonify({"error": "XP multiplier must be between 0.1 and 10."}), 400
    if not 0 <= cooldown <= 86400:
        return jsonify({"error": "XP cooldown must be between 0 and 86400 seconds."}), 400
    channel = body.get("level_up_channel") or None
    if channel is not None and not str(channel).isdigit():
        return jsonify({"error": "Level-up channel must be a valid channel ID."}), 400
    message = body.get("level_up_message")
    if message is not None and len(str(message)) > 1000:
        return jsonify({"error": "Level-up message must be 1000 characters or fewer."}), 400

    leveling = _discord_bot.get_cog("Leveling") if _discord_bot is not None else None
    if leveling is not None and hasattr(leveling, "_guild_cfg") and hasattr(leveling, "_save_guild_cfg"):
        try:
            current = run_on_bot_loop(leveling._guild_cfg(int(guild_id)))
            current.update({
                "xp_enabled": bool(body.get("xp_enabled", current.get("xp_enabled", True))),
                "xp_multiplier": multiplier,
                "xp_cooldown": cooldown,
                "level_up_channel": int(channel) if channel else None,
                "level_up_message": message,
            })
            run_on_bot_loop(leveling._save_guild_cfg(int(guild_id), current))
            return jsonify({"ok": True, "config": current})
        except Exception:
            return jsonify({"error": "The leveling settings could not be saved through the live bot."}), 503

    conn = sqlite_connect()
    if conn is None:
        return jsonify({"error": "The bot database is unavailable."}), 503
    try:
        conn.execute(
            "INSERT OR REPLACE INTO level_config "
            "(guild_id, xp_enabled, xp_multiplier, xp_cooldown, level_up_channel, level_up_message, level_roles) "
            "VALUES (?, ?, ?, ?, ?, ?, COALESCE((SELECT level_roles FROM level_config WHERE guild_id = ?), '{}'))",
            (
                int(guild_id), int(bool(body.get("xp_enabled", True))),
                multiplier, cooldown, int(channel) if channel else None, message,
                int(guild_id),
            ),
        )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        return jsonify({"error": "The leveling settings could not be saved."}), 500
    finally:
        conn.close()
    return jsonify({"ok": True, "config": get_runtime_level_config(guild_id)})


# ── Static file serving ──────────────────────────────────────────────────────

@app.route("/")
def root():
    return send_from_directory(WEB_DIST_DIR, "index.html")


@app.route("/dashboard")
def dashboard_redirect():
    return send_from_directory(WEB_DIST_DIR, "index.html")


def serve_spa_shell():
    """Serve the React shell for a client-side route on hard refresh."""
    return send_from_directory(WEB_DIST_DIR, "index.html")


@app.route("/commands")
@app.route("/docs")
@app.route("/privacy")
@app.route("/terms")
def public_spa_route():
    return serve_spa_shell()


@app.route("/commands/<path:path>")
@app.route("/docs/<path:path>")
@app.route("/privacy/<path:path>")
@app.route("/terms/<path:path>")
@app.route("/dashboard/<path:path>")
def nested_spa_route(path):
    return serve_spa_shell()


@app.route("/dashboard.html")
def legacy_dashboard_redirect():
    return redirect("/dashboard")


@app.route("/<path:path>")
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


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
