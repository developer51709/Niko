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
  GET  /api/guild/<id>/economy  → economy leaderboard (auth required)
  GET  /api/guild/<id>/levels   → level leaderboard (auth required)
  GET  /api/guild/<id>/config   → full guild config (auth required)
  POST /api/guild/<id>/config/automod → save automod settings (auth required)
  POST /api/guild/<id>/config/ai      → save AI settings (auth required)
"""

import os
import json
import glob
import time
import secrets
import traceback
import sqlite3
from urllib.parse import urlencode
from functools import wraps
from flask import (
    Flask, send_from_directory, session,
    redirect, request, jsonify, url_for
)
import requests as req

# ── Constants ────────────────────────────────────────────────────────────────

DISCORD_CLIENT_ID     = "1484653109576732692"
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "")
DISCORD_API           = "https://discord.com/api/v10"

DATA_DIR     = "data"
ECONOMY_DIR  = os.path.join(DATA_DIR, "economy_data")
BOT_STATS    = os.path.join(DATA_DIR, "bot_stats.json")
MODCFG       = os.path.join(DATA_DIR, "modconfig.json")
AICFG        = os.path.join(DATA_DIR, "ai_config.json")
LEVELS_JSON  = os.path.join(DATA_DIR, "levels.json.migrated")
LEVELCFG_JSON = os.path.join(DATA_DIR, "level_config.json.migrated")
DATABASE_PATH = os.path.join(DATA_DIR, "database.db")

MANAGE_GUILD_PERM = 0x20  # Discord permission bit

# ── App setup ────────────────────────────────────────────────────────────────

WEB_DIST_DIR = os.path.join(os.path.dirname(__file__), "website", "dist")
app = Flask(__name__, static_folder=WEB_DIST_DIR, static_url_path="")
app.secret_key = os.environ.get("SESSION_SECRET", secrets.token_hex(32))
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"]   = True
app.config["SESSION_COOKIE_HTTPONLY"] = True

_discord_bot = None

# ── Helpers ──────────────────────────────────────────────────────────────────

def oauth_enabled() -> bool:
    return bool(DISCORD_CLIENT_SECRET)


def configure_bot(bot) -> None:
    """Give the API access to the live bot for guild and runtime config sync."""
    global _discord_bot
    _discord_bot = bot


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


def pg_connect():
    """Return a psycopg2 connection, or None if unavailable."""
    try:
        import psycopg2
        return psycopg2.connect(os.environ["DATABASE_URL"])
    except Exception:
        return None


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
        if (bool(permissions & MANAGE_GUILD_PERM) or bool(guild.get("owner"))) and str(guild["id"]) in present:
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
    cmds = load_json("data/commands.json", [])
    category = request.args.get("category", "").strip().lower()
    if category:
        cmds = [c for c in cmds if c.get("category") == category]
    return jsonify(cmds)


@app.route("/api/health")
def api_health():
    return jsonify({"ok": True, "service": "niko-api", "static_build": os.path.exists(os.path.join(WEB_DIST_DIR, "index.html"))})


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


@app.route("/api/guilds")
@require_auth
def api_guilds():
    """Guilds where the user has Manage Server AND the bot is present."""
    token = session.get("access_token", "")
    try:
        all_guilds = discord_get("/users/@me/guilds", token)
    except Exception:
        return jsonify([])

    present = bot_guild_ids()
    result  = []
    for g in all_guilds:
        perms = int(g.get("permissions", 0))
        is_admin = bool(perms & MANAGE_GUILD_PERM) or bool(g.get("owner"))
        if str(g["id"]) in present and is_admin:
            icon_hash = g.get("icon")
            icon_url  = (
                f"https://cdn.discordapp.com/icons/{g['id']}/{icon_hash}.webp?size=64"
                if icon_hash else None
            )
            result.append({
                "id":       g["id"],
                "name":     g["name"],
                "icon_url": icon_url,
            })
    session["managed_guild_ids"] = [guild["id"] for guild in result]
    session["managed_guilds_at"] = time.time()
    return jsonify(result)


@app.route("/api/guild/<guild_id>/overview")
@require_auth
@require_guild_access
def api_guild_overview(guild_id):
    # ── Economy snapshot ──────────────────────────────────────
    eco_files  = glob.glob(os.path.join(ECONOMY_DIR, "[0-9]*.json"))
    total_coins = 0
    top_eco    = []
    for fp in eco_files:
        d = load_json(fp)
        if not d:
            continue
        uid   = os.path.basename(fp).replace(".json", "")
        nw    = d.get("net_worth", 0)
        total_coins += nw
        top_eco.append({
            "user_id":     uid,
            "net_worth":   nw,
            "level":       d.get("level", 0),
            "job":         d.get("job", "barista"),
            "daily_streak": d.get("daily_streak", 0),
        })
    top_eco.sort(key=lambda x: x["net_worth"], reverse=True)

    # ── Warnings ──────────────────────────────────────────────
    warns      = load_json("data/warns.json", {})
    guild_warns = warns.get(guild_id, {})
    warn_count = sum(len(v) for v in guild_warns.values())

    # ── Automod quick status ──────────────────────────────────
    modcfg   = load_json(MODCFG, {}).get(guild_id, {})
    automod  = modcfg.get("automod", {})
    automod_on = any(automod.values()) if isinstance(automod, dict) else False

    # ── Level leaderboard (quick top-5) ──────────────────────
    top_levels = _get_levels(guild_id)[:5]

    return jsonify({
        "economy": {
            "total_coins": total_coins,
            "user_count":  len(eco_files),
            "top":         top_eco[:5],
        },
        "moderation": {
            "warn_count":     warn_count,
            "automod_active": automod_on,
        },
        "leveling": {
            "top": top_levels,
        },
    })


@app.route("/api/guild/<guild_id>/economy")
@require_auth
@require_guild_access
def api_guild_economy(guild_id):
    eco_files = glob.glob(os.path.join(ECONOMY_DIR, "[0-9]*.json"))
    rows = []
    for fp in eco_files:
        d = load_json(fp)
        if not d:
            continue
        uid = os.path.basename(fp).replace(".json", "")
        rows.append({
            "user_id":      uid,
            "balance":      d.get("balance", 0),
            "bank":         d.get("bank", 0),
            "net_worth":    d.get("net_worth", 0),
            "level":        d.get("level", 0),
            "job":          d.get("job", "barista"),
            "daily_streak": d.get("daily_streak", 0),
            "achievements": len(d.get("achievements", [])),
            "total_earned": d.get("total_earned", 0),
        })
    rows.sort(key=lambda x: x["net_worth"], reverse=True)
    return jsonify(rows[:25])


def _get_levels(guild_id: str) -> list:
    """Fetch level data for a guild — PostgreSQL first, JSON fallback."""
    conn = pg_connect()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT user_id, xp, level FROM levels "
                "WHERE guild_id = %s ORDER BY xp DESC LIMIT 25",
                (int(guild_id),),
            )
            rows = [{"user_id": str(r[0]), "xp": r[1], "level": r[2]}
                    for r in cur.fetchall()]
            conn.close()
            return rows
        except Exception:
            conn.close()

    # JSON fallback (migrated snapshot)
    data = load_json(LEVELS_JSON, {})
    guild = data.get(guild_id, {})
    rows  = [{"user_id": uid, "xp": v.get("xp", 0), "level": v.get("level", 0)}
             for uid, v in guild.items()]
    rows.sort(key=lambda x: x["xp"], reverse=True)
    return rows[:25]


@app.route("/api/guild/<guild_id>/levels")
@require_auth
@require_guild_access
def api_guild_levels(guild_id):
    return jsonify(_get_levels(guild_id))


@app.route("/api/guild/<guild_id>/config")
@require_auth
@require_guild_access
def api_guild_config(guild_id):
    modcfg  = load_json(MODCFG, {}).get(guild_id, {})
    aicfg   = load_json(AICFG,  {}).get(guild_id, {})

    # Level config — PostgreSQL first, JSON fallback
    level_cfg = {}
    conn = pg_connect()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT xp_enabled, xp_multiplier, xp_cooldown, "
                "       level_up_channel, level_up_message "
                "FROM level_config WHERE guild_id = %s",
                (int(guild_id),),
            )
            row = cur.fetchone()
            if row:
                level_cfg = {
                    "xp_enabled":       bool(row[0]),
                    "xp_multiplier":    row[1],
                    "xp_cooldown":      row[2],
                    "level_up_channel": str(row[3]) if row[3] else None,
                    "level_up_message": row[4],
                }
            conn.close()
        except Exception:
            conn.close()

    if not level_cfg:
        level_cfg = load_json(LEVELCFG_JSON, {}).get(guild_id, {})

    return jsonify({
        "moderation": modcfg,
        "ai":         aicfg,
        "leveling":   level_cfg,
    })


@app.route("/api/guild/<guild_id>/config/automod", methods=["POST"])
@require_auth
@require_guild_access
def api_save_automod(guild_id):
    body = request.get_json(silent=True) or {}
    data = load_json(MODCFG, {})
    if guild_id not in data:
        data[guild_id] = {}

    allowed_flags = {"antispam", "antilink", "badwords", "massmention", "antiraid_ext"}
    existing = data[guild_id].get("automod", {})
    for k in allowed_flags:
        if k in body:
            existing[k] = bool(body[k])
    data[guild_id]["automod"] = existing

    if "modlog_channel" in body:
        data[guild_id]["modlog_channel"] = body["modlog_channel"]
    try:
        if "spam_threshold" in body:
            data[guild_id]["spam_threshold"] = max(1, int(body["spam_threshold"]))
        if "max_mentions" in body:
            data[guild_id]["max_mentions"] = max(1, int(body["max_mentions"]))
    except (TypeError, ValueError):
        return jsonify({"error": "Threshold values must be positive whole numbers."}), 400

    save_json(MODCFG, data)
    return jsonify({"ok": True})


@app.route("/api/guild/<guild_id>/config/ai", methods=["POST"])
@require_auth
@require_guild_access
def api_save_ai(guild_id):
    body = request.get_json(silent=True) or {}
    data = load_json(AICFG, {})
    if guild_id not in data:
        data[guild_id] = {"personality": "cafe", "enabled": "True"}

    if body.get("personality") in ("cafe", "normal"):
        data[guild_id]["personality"] = body["personality"]
    if "enabled" in body:
        data[guild_id]["enabled"] = "True" if body["enabled"] else "False"

    save_json(AICFG, data)
    return jsonify({"ok": True})


# ── Static file serving ──────────────────────────────────────────────────────

@app.route("/")
def root():
    return send_from_directory(WEB_DIST_DIR, "index.html")


@app.route("/dashboard")
def dashboard_redirect():
    return send_from_directory(WEB_DIST_DIR, "index.html")


@app.route("/dashboard.html")
def legacy_dashboard_redirect():
    return redirect("/dashboard")


@app.route("/<path:path>")
def static_proxy(path):
    requested = os.path.join(WEB_DIST_DIR, path)
    if os.path.isfile(requested):
        return send_from_directory(WEB_DIST_DIR, path)
    return send_from_directory(WEB_DIST_DIR, "index.html")


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
