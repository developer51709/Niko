"""Owner-only maintenance controls for cogs and individual commands.

The state itself lives in :mod:`utils.maintenance`, which the bot's invocation
gates and startup loader read too. This module only exposes it to the staff
dashboard and writes through the same helpers, so the website and Discord can
never disagree about what is paused.
"""

import importlib
import logging
import sys

from flask import jsonify, request, session

from utils import maintenance

from .. import server as _server
from ..api_maintenance import api_targets

app = _server.app
require_auth = _server.require_auth
require_csrf = _server.require_csrf
run_on_bot_loop = _server.run_on_bot_loop
_current_staff_role = _server._current_staff_role
_discord_bot = None
log = logging.getLogger(__name__)


#: Whether this build has already re-read the module from disk. The route
#: module itself is recreated by every dashboard rebuild, so this is once per
#: update — not once per request.
_refreshed = False


def _state():
    """The maintenance module the files on disk describe.

    An update writes ``src/utils`` first and then rebuilds the dashboard, but a
    rebuild only re-imports ``webapp.*``. ``from utils import maintenance``
    resolves through the ``utils`` package attribute, so it keeps returning the
    module this process imported at startup: a pulled change to the snapshot
    stayed on disk until the bot was restarted, which is downtime a
    dashboard-only change should not cost.

    Reloading in place is what makes it land: the module object stays the same,
    so the bot's gates keep their reference to it, while the functions behind
    ``snapshot()`` are the new ones. The pause cache is carried across the
    reload, so API gates keep enforcing pauses while the dashboard is rebuilt.
    """
    global _refreshed
    module = maintenance
    if _refreshed:
        return module
    _refreshed = True
    previous_cache = getattr(module, "_cache", None)
    previous_loaded = bool(getattr(module, "_loaded", False))
    try:
        # A previous update may have dropped the entry while the package
        # attribute kept the module alive; reload needs the entry back.
        sys.modules.setdefault(module.__name__, module)
        reloaded = importlib.reload(module)
        # Reloading resets module globals, including the pause cache. Hand the
        # old cache back so the API gate keeps enforcing API pauses during the
        # rebuild instead of answering normally until the next explicit load.
        if previous_cache is not None:
            reloaded._cache = previous_cache
            reloaded._loaded = previous_loaded
        else:
            reloaded._loaded = False
        return reloaded
    except Exception:
        log.exception("Could not re-read the maintenance module; using the loaded copy")
        return module


class UnknownTarget(LookupError):
    """The requested cog or command does not exist on this bot."""


class RefusedTarget(RuntimeError):
    """The target cannot be toggled from the dashboard."""


def _api_targets() -> list[dict]:
    return api_targets(app)


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
    state = _state()

    async def read():
        # The toggles are cached from the database at startup; this only matters
        # if the dashboard is opened before that first load finished.
        await state.ensure_loaded(_discord_bot)
        return state.snapshot(_discord_bot, _api_targets())

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

    if kind not in ("cog", "command", "api"):
        return jsonify({"error": "Choose whether to pause a cog, command, or API."}), 400
    if not key or len(key) > 160:
        return jsonify({"error": "Choose a cog or command to pause."}), 400

    state = _state()
    if len(reason) > state.MAX_REASON:
        return jsonify({"error": f"The reason must be {state.MAX_REASON} characters or fewer."}), 400

    actor = session["user"]["id"]
    actor_name = session["user"].get("global_name") or session["user"].get("username")

    async def apply():
        current = state.snapshot(_discord_bot, _api_targets())
        previous = state.entry(kind, key)
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
        elif kind == "command" and not any(command["name"] == key for command in current["commands"]):
            raise UnknownTarget(key)
        elif kind == "api" and not any(api["endpoint"] == key for api in current["apis"]):
            raise UnknownTarget(key)

        await state.set_maintenance(kind, key, enabled, reason, actor, _discord_bot)
        linked_report = (previous or {}).get("report_code")
        if not enabled and linked_report:
            # A manual resume has to reach the report too, or the owner's report
            # page would keep showing the pause switch as on and the public
            # incident would keep calling the target paused.
            try:
                from utils.error_reports import set_error_report_maintenance

                await set_error_report_maintenance(
                    linked_report, False, kind, key, actor, actor_name, _discord_bot,
                )
            except Exception:
                log.exception("Could not clear the report link for %s", key)
        if kind == "cog":
            # The status page reads these rows, so the reason shows up there in
            # the same breath as it starts answering in Discord.
            state.apply_to_cog_status(_discord_bot)
        log.info(
            "Maintenance %s %s by %s (%s)",
            "paused" if enabled else "resumed", key, actor, reason or "no reason given",
        )
        return state.snapshot(_discord_bot, _api_targets())

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
