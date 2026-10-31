"""Niko Dashboard — Flask application.

This module is the composition root of the web application. It owns the Flask
instance, the request hooks shared by every route, and the serving of the built
SPA shell.

Everything else lives in a sibling module:

* ``config``       — environment, paths, and permission bits
* ``runtime``      — the live bot reference and the bot-loop bridge
* ``auth``         — session and OAuth guards, member guild list
* ``discord_api``  — Discord REST over the bot's own egress
* ``database``     — economy, leveling, and member identity reads
* ``staff``        — staff presence, identity, and roster rows
* ``guilds``       — guild profiles, dashboard config, Discord panel refreshes
* ``commands``     — the bot's command registry
* ``donations``    — donation webhook helpers
* ``social``       — landing-page counts and link-preview contexts
* ``routes/``      — the Flask route modules

The block after the application is a deliberate re-export surface: every module
in ``routes/`` imports this module and then copies its namespace with
``globals().update(vars(_server))``. A name dropped from there breaks a route
module with a NameError at call time, so names a route reaches for are kept even
though this file no longer uses them itself. This module's own code reads the
bot through ``runtime`` instead, like every other module does.
"""

import os
import secrets
import time

from flask import Flask, jsonify, request, send_from_directory

from . import runtime, social

# ── Shared namespace ──────────────────────────────────────────────────────────
# Re-exported for the route modules' snapshot (see the module docstring),
# grouped by the module that owns each name. Keep this list complete when a
# helper moves out of this file.
from urllib.parse import quote, urlencode, urlparse
import base64
import glob
import hashlib
import hmac
import json
import sqlite3
import uuid
import requests as req
from cogs.donations.oxapay import OxaPayClient
from cogs.staff.records import STAFF_ROLES
from utils.ai.config import cached_config as cached_ai_config
from utils.ai.config import save_config as save_ai_config
from utils.donations import get_invoice, save_invoice, update_invoice_status, verify_donation_token
from .config import ADMINISTRATOR_PERM, BOT_STATS, DISCORD_API, DISCORD_BOT_TOKEN, DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, ECONOMY_DIR, MANAGE_GUILD_PERM, OXAPAY_KEY, WEB_DIST_DIR
from flask import Response, redirect, session
from .auth import _current_user_blacklist_entry, _load_blacklist_manager, ensure_access_token, get_mutual_leaderboard_identity_ids, managed_guild_ids, member_guilds, require_auth, require_csrf, require_dashboard_auth, require_guild_access
from .commands import _LEGACY_INTERNAL_COMMAND_NAMES, _description_value, _is_internal_command, _live_internal_command_names
from .database import _get_levels, _normalize_economy_row, _serialize_level_config, get_runtime_economy_rows, get_runtime_guild_level_page, get_runtime_leaderboard_page, get_runtime_level_config, get_runtime_member_metadata, level_xp_for_next, sqlite_connect
from .discord_api import discord_get, discord_request
from .donations import _confirm_donation_from_webhook, _donation_bot
from .guilds import _discord_guild_profile_assets, _get_runtime_guild_profile, _get_runtime_server_config, _guild_resource_ids, _read_moderation_config_sync, _refresh_captcha_panel, _refresh_ticket_panel, _save_runtime_guild_profile, _serialize_ticket_config, get_runtime_moderation_config
from .runtime import _discord_bot, bot_guild_ids, configure_bot, load_json, oauth_enabled, public_base_url, redirect_uri, run_on_bot_loop, save_json, schedule_on_bot_loop
from .social import render_site_shell
from .staff import STAFF_PRIORITY, _current_staff_role, _load_staff_management_rows, _load_staff_rows, _presence_member, _staff_role_label, _staff_row, custom_status_text

# ── Flask application ─────────────────────────────────────────────────────────

app = Flask(__name__, static_folder=WEB_DIST_DIR, static_url_path="")
app.secret_key = os.environ.get("SESSION_SECRET", secrets.token_hex(32))
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"]   = True
app.config["SESSION_COOKIE_HTTPONLY"] = True

# ── Instance state ────────────────────────────────────────────────────────────

_WEB_STARTED_AT = time.time()

@app.route("/health")
def api_health_local():
    """Report this instance's liveness."""
    return jsonify({
        "ok": True,
        "service": "niko-backend",
        "gateway": "active",
        "uptime_seconds": max(0, int(time.time() - _WEB_STARTED_AT)),
    })


@app.after_request
def prevent_dynamic_cache(response):
    """Never let auth or dashboard API responses become stale in production."""
    if request.path.startswith("/api/") or request.path.startswith("/auth/"):
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"
    return response


def serve_spa_shell():
    """Every public SPA route is the same shell with its own metadata."""
    return social.render_site_shell()


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
        return social.render_site_shell()
    return error
