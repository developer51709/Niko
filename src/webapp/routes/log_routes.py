"""Owner-only API for the bot's live console log.

The page this feeds is part of the staff workspace, and the buffer itself is
filled by :mod:`utils.logging` in the process the bot runs in. Nothing here
reads a log file or asks the host for anything: the same records that colour the
terminal are kept in memory, and this route hands the new ones to the owner's
browser.

Log lines can contain operational detail, so the route is restricted to the
configured owner rather than to staff in general.
"""

from flask import jsonify, request

from .. import server as _server

app = _server.app
require_auth = _server.require_auth
_current_staff_role = _server._current_staff_role


def _log_buffer():
    """The running bot's buffer, or ``None`` when this process has none.

    Imported lazily: the Flask app can be rebuilt on its own, and importing
    ``utils.logging`` at module load would run its root-handler setup in any
    process that serves the API without the bot behind it.
    """
    try:
        from utils import logging as bot_logging

        return getattr(bot_logging, "log_buffer", None)
    except Exception:
        return None


def _int_arg(name: str, default: int) -> int:
    try:
        return max(0, int(request.args.get(name, default)))
    except (TypeError, ValueError):
        return default


@app.route("/api/owner/logs")
@require_auth
def api_owner_logs():
    """Lines added after ``since``, for the live console to append.

    ``since`` is the id of the last line the page holds. The response carries
    ``next`` (the cursor to send back), ``head`` (the newest id), and ``reset``
    when that cursor belongs to a buffer that no longer exists — the page then
    clears itself and starts from the current process's first line.
    """
    if _current_staff_role() != "owner":
        return jsonify({"error": "The live log is restricted to the bot owner."}), 403

    buffer = _log_buffer()
    if buffer is None:
        payload = {
            "lines": [],
            "head": 0,
            "next": 0,
            "first": None,
            "token": "",
            "capacity": 0,
            "noise_capacity": 0,
            "truncated": False,
            "reset": False,
            "unavailable": True,
        }
    else:
        payload = buffer.snapshot(_int_arg("since", 0), _int_arg("limit", 2000))

    # A proxy must never answer a poll from its cache: the cursor in the query
    # would make every owner see whichever lines reached it first.
    response = jsonify(payload)
    response.headers["Cache-Control"] = "no-store"
    return response
