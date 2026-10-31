"""Owner-only Lavalink pool controls.

The pool has two sources, and this page is the only place they are managed:

* the hardcoded catalogue in ``config/lavalink.py`` — read-only here, because
  it is committed source;
* private nodes saved by the owner — stored in the music database so their
  passwords are never committed or hardcoded, and applied to the live pool
  without restarting the bot.
"""

import logging
import re

from .. import server as _server

globals().update({name: value for name, value in vars(_server).items() if not name.startswith("__")})

from utils.music.nodes import node_catalog, node_identifier

log = logging.getLogger(__name__)

_HOST_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$")
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")


def _require_owner():
    if _current_staff_role() != "owner":
        return jsonify({"error": "Lavalink node management is restricted to the bot owner."}), 403
    if _discord_bot is None:
        return jsonify({"error": "The Discord bot is not available."}), 503
    return None


def _music_cog():
    getter = getattr(_discord_bot, "get_cog", None)
    return getter("MusicSystem") if getter else None


def _parse_node(body):
    """Validate an owner-supplied node. Nothing is normalised silently."""
    host = str(body.get("host") or "").strip().lower()
    if not host or len(host) > 253 or not _HOST_RE.match(host) or ".." in host:
        raise ValueError("Enter a node hostname or IP address without a scheme or path.")
    try:
        port = int(body.get("port"))
    except (TypeError, ValueError):
        raise ValueError("Enter the node's port number.") from None
    if not 1 <= port <= 65535:
        raise ValueError("The port must be between 1 and 65535.")
    password = body.get("password")
    password = "" if password is None else str(password)
    if not password or len(password) > 200:
        raise ValueError("Enter the node's password (1–200 characters).")
    if password != password.strip() or _CONTROL_RE.search(password):
        raise ValueError("The password cannot contain leading, trailing, or control whitespace.")
    label = str(body.get("label") or "").strip()
    if len(label) > 60:
        raise ValueError("Keep the label to 60 characters or fewer.")
    return host, port, password, bool(body.get("secure")), label


async def _load():
    """Catalogue rows plus the live pool, merged into one owner-facing list."""
    from utils.music.database import MusicDatabase

    db = MusicDatabase()
    if not await db.ensure(_discord_bot):
        raise RuntimeError("The music database is not available.")
    private = await db.lavalink_nodes()
    catalog = node_catalog(private)

    cog = _music_cog()
    pool = cog.pool_snapshot() if cog is not None else {"nodes": [], "connected": 0, "target": 3}
    live = {row["identifier"]: row for row in pool["nodes"]}

    rows = []
    for node in catalog:
        identifier = node_identifier(node)
        state = live.get(identifier) or {}
        rows.append({
            "identifier": identifier,
            "host": node["host"],
            "port": int(node["port"]),
            "secure": bool(node.get("secure")),
            "label": node.get("label") or "",
            "source": "private" if node.get("private") else "static",
            "status": state.get("status", "not connected"),
            "players": int(state.get("players") or 0),
            "heartbeat": float(state.get("heartbeat") or 0),
        })

    # A node in the pool but not in the catalogue is left over from an edit that
    # has not been applied yet; showing it beats a silently missing entry.
    known = {row["identifier"] for row in rows}
    for identifier, state in live.items():
        if identifier in known:
            continue
        host, _, port = identifier.rpartition(":")
        rows.append({
            "identifier": identifier,
            "host": host,
            "port": int(port) if port.isdigit() else 0,
            "secure": False,
            "label": "",
            "source": "orphan",
            "status": state.get("status", "not connected"),
            "players": int(state.get("players") or 0),
            "heartbeat": float(state.get("heartbeat") or 0),
        })

    private_count = sum(1 for node in catalog if node.get("private"))
    return {
        "nodes": rows,
        "connected": int(pool.get("connected") or 0),
        "target": int(pool.get("target") or 0) + private_count,
        "private_count": private_count,
        "static_count": len(catalog) - private_count,
    }


async def _apply():
    cog = _music_cog()
    if cog is None:
        raise RuntimeError("The music system is not loaded yet.")
    await cog.apply_lavalink_changes()


@app.route("/api/staff/lavalink")
@require_auth
def api_staff_lavalink():
    error = _require_owner()
    if error:
        return error
    try:
        return jsonify(run_on_bot_loop(_load(), timeout=20))
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        log.exception("Could not read the Lavalink pool")
        return jsonify({"error": "The Lavalink pool could not be read."}), 503


@app.route("/api/staff/lavalink/nodes", methods=["POST"])
@require_auth
@require_csrf
def api_add_lavalink_node():
    error = _require_owner()
    if error:
        return error
    try:
        host, port, password, secure, label = _parse_node(request.get_json(silent=True) or {})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    actor = int(session["user"]["id"])

    async def save():
        from utils.music.database import MusicDatabase

        db = MusicDatabase()
        if not await db.ensure(_discord_bot):
            raise RuntimeError("The music database is not available.")
        return await db.save_lavalink_node(
            host=host, port=port, password=password, secure=secure,
            label=label, added_by=actor,
        )

    try:
        identifier = run_on_bot_loop(save())
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        log.exception("Could not save private Lavalink node %s:%s", host, port)
        return jsonify({"error": "The private node could not be saved."}), 502

    # An unreachable node is still a valid save — it may be the owner's own
    # server coming up — so the result reports whether it joined the pool now.
    try:
        run_on_bot_loop(_apply(), timeout=60)
        applied = True
    except Exception:
        log.exception("Could not apply Lavalink changes after adding %s", identifier)
        applied = False
    return jsonify({"ok": True, "identifier": identifier, "applied": applied})


@app.route("/api/staff/lavalink/nodes/<path:identifier>", methods=["DELETE"])
@require_auth
@require_csrf
def api_remove_lavalink_node(identifier):
    error = _require_owner()
    if error:
        return error

    async def remove():
        from utils.music.database import MusicDatabase

        db = MusicDatabase()
        if not await db.ensure(_discord_bot):
            raise RuntimeError("The music database is not available.")
        removed = await db.remove_lavalink_node(identifier)
        if removed:
            cog = _music_cog()
            if cog is not None:
                await cog.apply_lavalink_changes()
        return removed

    try:
        removed = run_on_bot_loop(remove(), timeout=60)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        log.exception("Could not remove private Lavalink node %s", identifier)
        return jsonify({"error": "The private node could not be removed."}), 502
    if not removed:
        return jsonify({"error": "That private node is not on file."}), 404
    return jsonify({"ok": True})


@app.route("/api/staff/lavalink/apply", methods=["POST"])
@require_auth
@require_csrf
def api_apply_lavalink_changes():
    error = _require_owner()
    if error:
        return error
    try:
        run_on_bot_loop(_apply(), timeout=60)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        log.exception("Could not apply Lavalink changes")
        return jsonify({"error": "The pool could not be rescanned."}), 502
    return jsonify({"ok": True})
