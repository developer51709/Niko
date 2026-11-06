"""Owner-only API for the bot's live console log.

The page this feeds is part of the staff workspace.  Under the supervisor every
process writes its own append-only archive, split again by level, so one
process's burst cannot push another's lines out and a DEBUG flood cannot push
the ERROR lines away either.  A direct run has no archive and keeps the
in-memory ring, which is filled by :mod:`utils.logging` in this process.

Nothing here asks the host for anything: the same records that colour the
terminal are written to the archive (or kept in memory), and this route hands
the new ones to the owner's browser.

Log lines can contain operational detail, so the route is restricted to the
configured owner rather than to staff in general.
"""

import os

from flask import jsonify, request

from .. import server as _server

app = _server.app
require_auth = _server.require_auth
_current_staff_role = _server._current_staff_role


_shared_store = None

#: The process the page asked for, as it appears in the archive directory name.
_PROCESS_ALIASES = {"dashboard": "web", "api": "web"}


def _log_buffer():
    """The console this process should serve, or ``None`` when it has none.

    Under the supervisor every process appends to the shared archive, so the
    page keeps its history when a child restarts and also sees the supervisor's
    own lines.  A direct run has no archive and keeps the in-memory ring, which
    is filled by ``utils.logging`` in this process.

    Imported lazily: the Flask app can be rebuilt on its own, and importing
    ``utils.logging`` at module load would run its root-handler setup in any
    process that serves the API without the bot behind it.
    """
    global _shared_store
    if (os.environ.get("NIKO_LOG_STORE") or "").strip():
        if _shared_store is None:
            try:
                from log_store import store_from_environment

                _shared_store = store_from_environment()
            except Exception:
                _shared_store = None
        if _shared_store is not None:
            return _shared_store
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


def _text_arg(name: str, default: str) -> str:
    value = (request.args.get(name) or "").strip()
    return value or default


def _process_arg() -> str:
    name = _text_arg("process", "all").lower()
    return _PROCESS_ALIASES.get(name, name)


def _level_arg() -> str:
    name = _text_arg("level", "DEBUG").upper()
    # "All levels" is every level file, not the INFO default.
    return "DEBUG" if name == "ALL" else name


def _memory_snapshot(buffer, since: str, limit: int, process: str, level: str) -> dict:
    """Serve the in-memory ring with the archive's response shape.

    A direct run has one process and one ring; the page still sends a process
    and level, so they are applied here.  Ids are namespaced and the cursor is
    prefixed, which keeps a cursor from one source from being mistaken for the
    other's.
    """
    from log_store import level_weight

    try:
        offset = max(0, int(since.rsplit(":", 1)[-1]))
    except (TypeError, ValueError):
        offset = 0
    snapshot = buffer.snapshot(offset, limit)
    threshold = level_weight(level)
    lines = []
    for entry in snapshot.get("lines", []):
        owner = entry.get("process") or "bot"
        owner = _PROCESS_ALIASES.get(owner, owner)
        if process not in ("", "all") and owner != process:
            continue
        if level_weight(entry.get("level")) < threshold:
            continue
        lines.append({**entry, "id": f"memory:{entry.get('id')}", "process": owner})
    return {
        "lines": lines,
        "head": f"memory:{snapshot.get('head', 0)}",
        "next": f"memory:{snapshot.get('next', 0)}",
        "first": None,
        "token": f"memory:{snapshot.get('token', '')}",
        "capacity": int(snapshot.get("capacity") or 0),
        "noise_capacity": int(snapshot.get("noise_capacity") or 0),
        "truncated": bool(snapshot.get("truncated")),
        "reset": bool(snapshot.get("reset")),
        "has_more": int(snapshot.get("next", 0)) < int(snapshot.get("head", 0)),
    }


def _empty_payload() -> dict:
    return {
        "lines": [],
        "head": "",
        "next": "",
        "first": None,
        "token": "",
        "capacity": 0,
        "noise_capacity": 0,
        "truncated": False,
        "reset": False,
        "has_more": False,
        "unavailable": True,
    }


@app.route("/api/owner/logs")
@require_auth
def api_owner_logs():
    """Lines added after ``since``, for the live console to append.

    ``since`` is the opaque cursor from the previous response.  ``process``
    (``all`` or one archive directory) and ``level`` (a minimum) pick which of
    the independent buffers this view reads; the archive merges only those, so
    the page never downloads a process or level it is not showing.  ``reset``
    means the cursor belongs to buffers that no longer exist: the page clears
    itself and starts again.
    """
    if _current_staff_role() != "owner":
        return jsonify({"error": "The live log is restricted to the bot owner."}), 403

    buffer = _log_buffer()
    if buffer is None:
        payload = _empty_payload()
    else:
        since = _text_arg("since", "")
        limit = _int_arg("limit", 2000)
        process = _process_arg()
        level = _level_arg()
        try:
            from log_store import LogArchive
        except Exception:
            LogArchive = None  # type: ignore[assignment,misc]
        if LogArchive is not None and isinstance(buffer, LogArchive):
            payload = buffer.snapshot(
                processes=process,
                min_level=level,
                since=since,
                limit=limit,
            )
        else:
            payload = _memory_snapshot(buffer, since, limit, process, level)

    # A proxy must never answer a poll from its cache: the cursor in the query
    # would make every owner see whichever lines reached it first.
    response = jsonify(payload)
    response.headers["Cache-Control"] = "no-store"
    return response
