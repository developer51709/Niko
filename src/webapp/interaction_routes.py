"""Discord's HTTP interactions endpoint.

This is the *Interactions Endpoint URL* from the Developer Portal.  Discord POSTs
a slash command, button, select, modal or autocomplete here and expects the
callback in the response body, which means the answer is produced inside this
process instead of by an outbound request to Discord's API (see
``utils.interaction_endpoint``).  Discord makes the two delivery methods mutually
exclusive, so the endpoint has to answer *every* interaction once it is
configured — ``docs/maintenance.md`` describes the switch and what to do when it
has to be turned back off.

The route is public by necessity: Discord has no session cookie.  The Ed25519
signature over the raw body is what proves the caller is Discord, so the body is
verified before anything is decoded or dispatched, and an unsigned or stale
request is answered with 401 without touching the bot.
"""

import json

from flask import Response, jsonify, request

from utils import interaction_endpoint as _interactions
from utils import logging

from . import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

_INTERACTION_PING = 1


def _json_body(payload: dict, status: int) -> Response:
    """Return a body exactly as written: Discord compares the bytes it asked for."""
    return Response(json.dumps(payload).encode("utf-8"), status=status, content_type="application/json")


@app.route("/api/discord/interactions", methods=["POST"])
def api_discord_interactions():
    """Answer one interaction in the body of Discord's own request."""
    raw = request.get_data(cache=True)

    key = _interactions.public_key()
    if not key:
        logging.error(
            "Interactions",
            "Rejected an interaction: no public key is configured. Set DISCORD_PUBLIC_KEY to the "
            "application's Public Key from the Developer Portal.",
        )
        return jsonify({"error": "The interactions endpoint has no configured public key."}), 503

    signature = request.headers.get("X-Signature-Ed25519", "")
    timestamp = request.headers.get("X-Signature-Timestamp", "")
    if not _interactions.verify_signature(key, signature, timestamp, raw):
        # Discord's documented rejection for a bad signature, and the only answer
        # that is allowed to skip the PING/interaction distinction.
        return jsonify({"error": "invalid request signature"}), 401

    try:
        payload = json.loads(raw)
    except ValueError:
        return jsonify({"error": "invalid interaction payload"}), 400
    if not isinstance(payload, dict):
        return jsonify({"error": "invalid interaction payload"}), 400

    # Saving the endpoint URL in the portal makes Discord send one type 1 PING,
    # which has to come back as a type 1 PONG or the URL is refused.
    if payload.get("type") == _INTERACTION_PING:
        return _json_body({"type": 1}, 200)

    bot = _discord_bot
    if bot is None:
        logging.error("Interactions", "Rejected an interaction: the Discord bot is not attached to the web app.")
        return jsonify({"error": "The Discord bot is not available."}), 503

    # The endpoint may be reached on a process that started before the endpoint
    # was armed (or in a test), and capture is idempotent.
    _interactions.install_capture()

    try:
        body = _interactions.handle_interaction(bot, payload)
    except RuntimeError as exc:
        logging.error("Interactions", f"Rejected an interaction: {exc}")
        return jsonify({"error": "The Discord bot is not running."}), 503
    except Exception as exc:
        logging.error("Interactions", f"Interaction {payload.get('id')} could not be dispatched: {exc}")
        return jsonify({"error": "The interaction could not be dispatched."}), 500

    if body is None:
        # Nothing was captured inside the budget, so the handler's own callback
        # request still goes out over REST: 202 with no body is Discord's
        # documented acknowledgement for exactly that case.  Reaching here is the
        # one symptom that matters — the log line names the interaction.
        return Response(b"", status=202)

    return Response(body.payload, status=200, content_type=body.content_type)
