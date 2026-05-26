"""
Niko Dashboard — Flask web server
──────────────────────────────────
Routes:
  GET  /                        → landing page
  GET  /dashboard               → dashboard SPA (redirects to dashboard.html)
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

MANAGE_GUILD_PERM = 0x20  # Discord permission bit

# ── App setup ────────────────────────────────────────────────────────────────

app = Flask(__name__, static_folder="website", static_url_path="")
app.secret_key = os.environ.get("SESSION_SECRET", secrets.token_hex(32))
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"]   = True

# ── Helpers ──────────────────────────────────────────────────────────────────

def oauth_enabled() -> bool:
    return bool(DISCORD_CLIENT_SECRET)


def redirect_uri() -> str:
    domain = os.environ.get("REPLIT_DEV_DOMAIN", "localhost:5000")
    return f"https://{domain}/auth/callback"


def load_json(path: str, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}


def save_json(path: str, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def bot_guild_ids() -> set:
    """Return the set of guild IDs the bot is currently in."""
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
        if "user" not in session:
            return jsonify({
                "error": "Not authenticated",
                "login_url": "/auth/login",
            }), 401
        return f(*args, **kwargs)
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

    state = secrets.token_urlsafe(16)
    session["oauth_state"] = state

    params = "&".join([
        f"client_id={DISCORD_CLIENT_ID}",
        f"redirect_uri={redirect_uri()}",
        "response_type=code",
        "scope=identify%20guilds",
        f"state={state}",
        "prompt=none",
    ])
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
    session["token_exp"]    = time.time() + token_data.get("expires_in", 604800)

    return redirect("/dashboard.html")


@app.route("/auth/logout")
def auth_logout():
    session.clear()
    return redirect("/")


@app.route("/auth/status")
def auth_status():
    if "user" not in session:
        return jsonify({
            "authenticated":   False,
            "oauth_available": oauth_enabled(),
        })
    return jsonify({
        "authenticated":   True,
        "oauth_available": True,
        "user":            session["user"],
    })


# ── Public API ───────────────────────────────────────────────────────────────

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
    return jsonify(result)


@app.route("/api/guild/<guild_id>/overview")
@require_auth
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
def api_guild_levels(guild_id):
    return jsonify(_get_levels(guild_id))


@app.route("/api/guild/<guild_id>/config")
@require_auth
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
    if "spam_threshold" in body:
        data[guild_id]["spam_threshold"] = int(body["spam_threshold"])
    if "max_mentions" in body:
        data[guild_id]["max_mentions"] = int(body["max_mentions"])

    save_json(MODCFG, data)
    return jsonify({"ok": True})


@app.route("/api/guild/<guild_id>/config/ai", methods=["POST"])
@require_auth
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
    return send_from_directory("website", "index.html")


@app.route("/dashboard")
def dashboard_redirect():
    return redirect("/dashboard.html")


@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory("website", path)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
