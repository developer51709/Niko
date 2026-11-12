"""Owner controls for the honeypot: hits, IP bans, and the autoban guard.

Hits are written by the decoy routes through :mod:`webapp.security`, which keeps
the data in MongoDB (or the local JSON fallback). This module only reads that
store and changes bans or settings; the request guard in
:mod:`webapp.security_guard` is what makes a ban apply everywhere.
"""

from __future__ import annotations

import logging

from flask import jsonify, request, session

from .. import security
from .. import server as _server

app = _server.app
require_auth = _server.require_auth
require_csrf = _server.require_csrf
_current_staff_role = _server._current_staff_role
log = logging.getLogger(__name__)


def _require_owner():
    if _current_staff_role() != "owner":
        return jsonify({"error": "The honeypot page is restricted to the bot owner."}), 403
    return None


def _json_body():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return None
    return body


@app.route("/api/owner/honeypot")
@require_auth
def api_owner_honeypot():
    """Persisted hits, active bans, and the autoban settings."""
    error = _require_owner()
    if error:
        return error
    try:
        limit = int(request.args.get("limit") or 250)
    except (TypeError, ValueError):
        limit = 250
    return jsonify(security.snapshot(limit=limit))


@app.route("/api/owner/honeypot/ban", methods=["POST"])
@require_auth
@require_csrf
def api_owner_honeypot_ban():
    """Ban one address from the website, APIs, and every subdomain."""
    error = _require_owner()
    if error:
        return error
    body = _json_body()
    if body is None:
        return jsonify({"error": "Send a JSON object with the address to ban."}), 400
    try:
        security.ban_ip(
            str(body.get("ip") or ""),
            reason=str(body.get("reason") or ""),
            actor=str((session.get("user") or {}).get("id") or ""),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        log.exception("Could not ban an address from the honeypot page")
        return jsonify({"error": "The ban could not be saved."}), 502
    return jsonify(security.snapshot())


@app.route("/api/owner/honeypot/unban", methods=["POST"])
@require_auth
@require_csrf
def api_owner_honeypot_unban():
    error = _require_owner()
    if error:
        return error
    body = _json_body()
    if body is None:
        return jsonify({"error": "Send a JSON object with the address to unban."}), 400
    try:
        security.unban_ip(str(body.get("ip") or ""))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        log.exception("Could not unban an address from the honeypot page")
        return jsonify({"error": "The ban could not be removed."}), 502
    return jsonify(security.snapshot())


@app.route("/api/owner/honeypot/settings", methods=["POST"])
@require_auth
@require_csrf
def api_owner_honeypot_settings():
    """Turn the autoban guard on or off and set its thresholds."""
    error = _require_owner()
    if error:
        return error
    body = _json_body()
    if body is None:
        return jsonify({"error": "Send a JSON object with the guard settings."}), 400
    try:
        security.update_settings(body)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        log.exception("Could not save the autoban settings")
        return jsonify({"error": "The autoban settings could not be saved."}), 502
    return jsonify(security.snapshot())
