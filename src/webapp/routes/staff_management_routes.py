"""Owner-only staff roster and role management APIs."""

import logging

from config.ids import OWNER_IDS
from flask import jsonify, request, session

from .. import server as _server

app = _server.app
require_auth = _server.require_auth
require_csrf = _server.require_csrf
run_on_bot_loop = _server.run_on_bot_loop
_current_staff_role = _server._current_staff_role
_discord_bot = None
log = logging.getLogger(__name__)

_ACTIONS = {"assign", "demote", "suspend", "lift"}


def _roles() -> list[dict]:
    return [
        {"key": key, "label": label}
        for key, label in _server.STAFF_ROLES.items()
    ]


def _require_owner():
    if _current_staff_role() != "owner":
        return jsonify({"error": "Staff management is restricted to the bot owner."}), 403
    if _discord_bot is None:
        return jsonify({"error": "The Discord bot is not available."}), 503
    return None


@app.route("/api/staff/members")
@require_auth
def api_staff_members():
    error = _require_owner()
    if error:
        return error
    try:
        members = _server._load_staff_management_rows()
    except Exception:
        log.exception("Could not load the staff roster")
        return jsonify({"error": "The staff roster could not be loaded."}), 503
    return jsonify({"members": members, "roles": _roles(), "count": len(members)})


@app.route("/api/staff/members/<user_id>/manage", methods=["POST"])
@require_auth
@require_csrf
def api_manage_staff_member(user_id):
    error = _require_owner()
    if error:
        return error
    if not str(user_id).isdigit():
        return jsonify({"error": "Choose a valid Discord user ID."}), 400
    target_id = int(user_id)
    if target_id in OWNER_IDS:
        return jsonify({"error": "Owner accounts cannot be suspended or demoted through the staff roster."}), 403

    body = request.get_json(silent=True) or {}
    action = str(body.get("action") or "").strip().lower()
    role_key = str(body.get("role") or "").strip()
    reason = str(body.get("reason") or "").strip()
    if action not in _ACTIONS:
        return jsonify({"error": "Choose assign, demote, suspend, or lift."}), 400
    if action == "assign" and role_key not in _server.STAFF_ROLES:
        return jsonify({"error": "Choose a valid staff role."}), 400
    if action == "suspend" and len(reason) < 5:
        return jsonify({"error": "Add a short reason for the suspension."}), 400
    if len(reason) > 1000:
        return jsonify({"error": "The reason must be 1,000 characters or fewer."}), 400

    actor_id = int(session["user"]["id"])

    async def apply():
        from cogs.staff.records import set_staff_role, set_staff_suspension

        if action == "assign":
            return await set_staff_role(
                _discord_bot, target_id, role_key, actor_id, reason=reason,
            )
        if action == "demote":
            return await set_staff_role(
                _discord_bot, target_id, None, actor_id,
                reason=reason or "Staff role removed by the owner",
            )
        if action == "suspend":
            return await set_staff_suspension(
                _discord_bot, target_id, True, actor_id, reason=reason,
            )
        return await set_staff_suspension(
            _discord_bot, target_id, False, actor_id, reason=reason,
        )

    try:
        status = run_on_bot_loop(apply())
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409
    except Exception:
        log.exception("Could not update staff member %s", target_id)
        return jsonify({
            "error": "The staff update could not be completed. Refresh the roster and verify both the record and Discord role.",
        }), 502
    return jsonify({"ok": True, "status": status or "former"})
