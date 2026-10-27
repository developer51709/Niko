"""Niko Dashboard — Flask application.

This module is the composition root of the web application. It owns the Flask
instance, the request hooks that decide whether this instance answers a request
or relays it to the active standby, and the serving of the built SPA shell.

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

import requests as req
from flask import Flask, Response, jsonify, request, send_from_directory

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
from cogs.donations.oxapay import OxaPayClient
from cogs.staff.staff import STAFF_ROLES
from utils.ai.config import get_ai_config, set_ai_config
from utils.donations import get_invoice, save_invoice, update_invoice_status, verify_donation_token
from .config import ADMINISTRATOR_PERM, BOT_STATS, DISCORD_API, DISCORD_BOT_TOKEN, DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, ECONOMY_DIR, MANAGE_GUILD_PERM, OXAPAY_KEY, WEB_DIST_DIR
from flask import redirect, session
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
    manager = getattr(runtime._discord_bot, "standby_failover", None) if runtime._discord_bot is not None else None
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
