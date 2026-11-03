"""Owner-only maintenance controls for cogs and individual commands.

The state itself lives in :mod:`utils.maintenance`, which the bot's invocation
gates and startup loader read too. This module only exposes it to the staff
dashboard and writes through the same helpers, so the website and Discord can
never disagree about what is paused.
"""

import logging

from flask import jsonify, request, session

from utils import maintenance

from .. import server as _server

app = _server.app
require_auth = _server.require_auth
require_csrf = _server.require_csrf
run_on_bot_loop = _server.run_on_bot_loop
_current_staff_role = _server._current_staff_role
_discord_bot = None
log = logging.getLogger(__name__)


class UnknownTarget(LookupError):
    """The requested cog or command does not exist on this bot."""


class RefusedTarget(RuntimeError):
    """The target cannot be toggled from the dashboard."""


def _require_owner():
    if _current_staff_role() != "owner":
        return jsonify({"error": "Maintenance controls are restricted to the bot owner."}), 403
    if _discord_bot is None:
        return jsonify({"error": "The Discord bot is not available."}), 503
    return None


@app.route("/api/staff/maintenance")
@require_auth
def api_staff_maintenance():
    """Every cog and command with its current maintenance flags."""
    error = _require_owner()
    if error:
        return error
    async def read():
        # The toggles are cached from the database at startup; this only matters
        # if the dashboard is opened before that first load finished.
        await maintenance.ensure_loaded(_discord_bot)
        return maintenance.snapshot(_discord_bot)

    try:
        return jsonify(run_on_bot_loop(read()))
    except Exception:
        log.exception("Could not read the maintenance state")
        return jsonify({"error": "The maintenance state could not be read."}), 503


@app.route("/api/staff/maintenance", methods=["POST"])
@require_auth
@require_csrf
def api_set_staff_maintenance():
    """Pause or resume one cog or command, with an optional reason."""
    error = _require_owner()
    if error:
        return error

    body = request.get_json(silent=True) or {}
    kind = str(body.get("kind") or "").strip().lower()
    key = str(body.get("key") or "").strip()
    reason = str(body.get("reason") or "").strip()
    enabled = bool(body.get("enabled"))

    if kind not in ("cog", "command"):
        return jsonify({"error": "Choose whether to pause a cog or a command."}), 400
    if not key or len(key) > 160:
        return jsonify({"error": "Choose a cog or command to pause."}), 400
    if len(reason) > maintenance.MAX_REASON:
        return jsonify({"error": f"The reason must be {maintenance.MAX_REASON} characters or fewer."}), 400

    actor = session["user"]["id"]

    async def apply():
        current = maintenance.snapshot(_discord_bot)
        if kind == "cog":
            row = next((cog for cog in current["cogs"] if cog["name"] == key), None)
            if row is None:
                raise UnknownTarget(key)
            if row.get("declared"):
                raise RefusedTarget(
                    "This cog is paused by its own source code (MAINTENANCE or DNL). "
                    "Change the constant and restart the bot instead.",
                )
            if row.get("state") == "failed":
                raise RefusedTarget("This cog failed to load, so there is nothing to pause.")
        elif not any(command["name"] == key for command in current["commands"]):
            raise UnknownTarget(key)

        await maintenance.set_maintenance(kind, key, enabled, reason, actor, _discord_bot)
        if kind == "cog":
            # The status page reads these rows, so the reason shows up there in
            # the same breath as it starts answering in Discord.
            maintenance.apply_to_cog_status(_discord_bot)
        log.info(
            "Maintenance %s %s by %s (%s)",
            "paused" if enabled else "resumed", key, actor, reason or "no reason given",
        )
        return maintenance.snapshot(_discord_bot)

    try:
        snapshot = run_on_bot_loop(apply())
    except UnknownTarget:
        return jsonify({"error": "That cog or command no longer exists on the bot."}), 404
    except RefusedTarget as exc:
        return jsonify({"error": str(exc)}), 409
    except Exception:
        log.exception("Could not change the maintenance state for %s", key)
        return jsonify({"error": "The maintenance change could not be saved."}), 502

    return jsonify(snapshot)
