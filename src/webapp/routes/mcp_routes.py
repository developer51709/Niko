"""Owner MCP server and its staff-page configuration route."""

from flask import jsonify, session

from utils import logging

from .. import mcp_server
from .. import server as _server

app = _server.app
require_auth = _server.require_auth
require_csrf = _server.require_csrf
_current_staff_role = _server._current_staff_role


@app.route("/mcp", methods=["GET", "POST", "DELETE"], strict_slashes=False)
def mcp_endpoint():
    """The remote MCP endpoint used by Freebuff and other MCP clients."""
    return mcp_server.handle_http()


@app.route("/api/staff/mcp")
@require_auth
def api_staff_mcp():
    """Owner-only connection and key metadata for the MCP Server page.

    The key itself is never returned here. Only the prefix and creation/use
    timestamps are exposed so the page can identify the active key without
    keeping a copy of it in the browser or database.
    """
    if _current_staff_role() != "owner":
        return jsonify({"error": "The MCP server is restricted to the bot owner."}), 403
    response = jsonify(mcp_server.staff_payload())
    # The payload names the key prefix and its use times, so do not let a shared
    # browser cache retain one owner's metadata after sign-out.
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/api/staff/mcp/key", methods=["POST"])
@require_auth
@require_csrf
def api_staff_mcp_rotate_key():
    """Generate a new owner key and replace the stored hash immediately.

    The raw key is returned exactly once. The page keeps it in memory until it
    is dismissed; neither the response nor the database record is ever served
    again after that.
    """
    if _current_staff_role() != "owner":
        return jsonify({"error": "The MCP server is restricted to the bot owner."}), 403
    user = session.get("user") or {}
    actor_id = str(user.get("id") or "") or None
    actor_name = user.get("global_name") or user.get("username") or None
    try:
        result = mcp_server.rotate_key(actor_id, actor_name)
    except Exception as exc:
        # Keep the response generic, but leave a server-side trace so a database
        # or bot-loop failure is diagnosable without exposing internals to the
        # browser or logging the generated key.
        logging.warning(
            "MCP",
            f"Owner key rotation failed: {type(exc).__name__}: {exc}",
        )
        return jsonify({"error": "The MCP key could not be rotated."}), 503
    response = jsonify({"ok": True, **result})
    # The raw key is in this one response. Keep it out of browser and proxy
    # caches; the page holds it only until the owner dismisses it.
    response.headers["Cache-Control"] = "no-store"
    return response
