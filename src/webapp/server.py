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

from . import config, runtime, social

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
from config import links as bot_links
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
from .staff import STAFF_PRIORITY, _current_staff_role, _find_staff_member, _is_owner, _load_staff_management_rows, _load_staff_rows, _presence_member, _staff_role_label, _staff_row, custom_status_text

# ── Flask application ─────────────────────────────────────────────────────────

app = Flask(__name__, static_folder=WEB_DIST_DIR, static_url_path="")
app.secret_key = os.environ.get("SESSION_SECRET", secrets.token_hex(32))
# A new name for the session cookie, deliberately. The cookie used to be called
# "session" and was host-only; when the site started sharing it on the whole
# domain, browsers kept *both* — the old host-only one and the new domain one —
# and sent them together (`session=old; session=new`). Werkzeug reads the first,
# so the server saw an old session forever: sign-in stored its OAuth state in the
# domain cookie and every callback then read the stale one and answered
# "the sign-in link expired". A fresh name has no stale twin, and the old cookie
# is deleted on the way through auth (``auth_routes._drop_legacy_session_cookie``).
app.config["SESSION_COOKIE_NAME"]     = "niko_session"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# A Secure cookie is never sent back over plain HTTP, so an http deployment
# would sign in and lose the session on the very next request — the OAuth state
# included, which is what makes that failure read as "the link expired". The
# flag follows the site's own address: https, or nothing configured at all (the
# safe default), keeps it on; an explicitly http PUBLIC_URL turns it off.
app.config["SESSION_COOKIE_SECURE"]   = not config.canonical_origin().startswith("http://")
app.config["SESSION_COOKIE_HTTPONLY"] = True
# Sharing the cookie on the whole domain is what keeps a sign-in alive across
# the apex and a section subdomain. It is fixed at import from PUBLIC_URL — the
# canonical apex — because a cookie domain cannot depend on the host that
# happens to be answering; "" leaves cookies host-only.
app.config["SESSION_COOKIE_DOMAIN"] = config.session_cookie_domain()

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


@app.before_request
def route_section_subdomain():
    """Serve a section subdomain from the apex path it stands in for.

    On ``dash.example.com`` the visitor's ``/staff`` is the dashboard's
    ``/dashboard/staff``: the shell is told the prefix (see
    ``social.render_site_shell``) and the client applies it to every path it
    reads, so one build serves both the long and the short form. Anything under
    the long form is sent to the short one, which is what keeps old links, the
    dashboard's own ``/dashboard/...`` URLs and a visitor who types the prefix
    on a subdomain on the page they meant.

    A host the site does not serve at all (``foo.example.com`` under the site's
    own domain) is answered with the subdomain variant of the 404 page, and
    answered as a real 404 — there is no page behind it to come back to. Its
    API and sign-in endpoints keep working: the shell only needs them to render,
    and refusing them would turn a wrong host into a broken one.
    """
    host = runtime.request_host()
    prefix = config.subdomain_prefix(host)
    if prefix:
        if request.path == prefix or request.path.startswith(prefix + "/"):
            target = request.path[len(prefix):] or "/"
            if request.query_string:
                target = f"{target}?{request.query_string.decode('utf-8', 'replace')}"
            return redirect(target, code=301)
        return None
    # The bot's own assets (its README card and the favicon drawn by
    # `/bot/favicon.svg`) answer on every host, like the API and sign-in do.
    if config.unknown_subdomain(host) and not request.path.startswith(("/api/", "/auth/", "/bot/")):
        # The 404 page is still a page: its stylesheet, script and icons are
        # files this host ships, and only a path that is not one of them is the
        # page itself. The static route answers every single-segment path, so
        # existence — not the matched rule — is what tells the two apart.
        shipped = os.path.isfile(os.path.join(WEB_DIST_DIR, request.path.lstrip("/")))
        if not shipped:
            response = social.render_site_shell()
            response.status_code = 404
            return response
    return None


@app.after_request
def prevent_dynamic_cache(response):
    """Never let auth or dashboard API responses become stale in production.

    Translation catalogues are the one exception: they are public, carry an ETag
    per file, and are meant to be cached for a couple of minutes so a page does
    not re-download its strings on every navigation.
    """
    if request.path.startswith("/api/locales/"):
        return response
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


# Unhandled website and API exceptions become staff-retrievable JSON reports.
from .error_reporting import register_error_reporting  # noqa: E402
from .api_maintenance import register_api_maintenance  # noqa: E402

register_error_reporting(app)
register_api_maintenance(app)
