"""Loopback-only relay for the Discord calls the dashboard child cannot make.

The dashboard runs in its own process since the supervisor split, so it no
longer inherits the bot's Discord HTTP client. A host whose own address
Cloudflare has banned for the Discord API therefore cannot exchange an OAuth
code, refresh a session, fetch the signed-in member or read a membership — the
bot keeps answering because its REST calls travel with the bot's own
``User-Agent`` and, when it is active, the Webshare proxy or proxy-worker route
that its failover armed. The dashboard child posts the call it wants made here
and the bot child makes it with exactly that egress, which is what "the
dashboard reaches Discord the way the bot does" has to mean once the two are
separate processes.

Only the bot child answers: a process with no bot has no egress to lend and
says so. The endpoint is authenticated with the supervisor's per-run
``NIKO_RELAY_TOKEN`` — a credential minted for this hop alone, deliberately not
``NIKO_INTERNAL_TOKEN``, which also opens updates and the database child — so it
cannot be driven from the public internet even in a deployment whose dashboard
is reachable directly, and a request that reaches the dashboard cannot borrow
the bot's loopback API beyond this one call.
"""

from .. import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

from utils import logging

TOKEN_ENV = "NIKO_RELAY_TOKEN"
TOKEN_HEADER = "X-Internal-Token"

#: The only request options the dashboard may pass through. A relay that
#: forwards arbitrary keyword arguments to ``requests`` is an open proxy; these
#: are the ones ``discord_request`` is called with.
RELAYED_KWARGS = ("headers", "params", "timeout", "data", "json", "allow_redirects")

#: Discord's API hosts. The relay exists for Discord's API and nothing else, so
#: a call to any other address is refused rather than forwarded.
DISCORD_API_PREFIXES = (
    "https://discord.com/api/",
    "https://discordapp.com/api/",
    "https://canary.discord.com/api/",
    "https://ptb.discord.com/api/",
)


def _authorized() -> bool:
    expected = (os.environ.get(TOKEN_ENV) or "").strip()
    provided = (request.headers.get(TOKEN_HEADER) or "").strip()
    return bool(expected) and bool(provided) and hmac.compare_digest(provided, expected)


@app.route("/api/internal/discord", methods=["POST"])
def internal_discord_request():
    if not _authorized():
        return jsonify({"error": "This endpoint is only for the bot child."}), 403
    if runtime._discord_bot is None:
        # The dashboard child holds the same route; without a gateway here there
        # is no bot session, proxy or client to take the call over.
        return jsonify({"error": "This process has no Discord egress."}), 503

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Expected a JSON request body."}), 400

    method = str(payload.get("method") or "GET").upper()
    url = str(payload.get("url") or "")
    if not url.startswith(DISCORD_API_PREFIXES):
        return jsonify({"error": "Only Discord API URLs are relayed."}), 400
    if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
        return jsonify({"error": f"Unsupported method {method}."}), 400

    options = payload.get("kwargs") if isinstance(payload.get("kwargs"), dict) else {}
    kwargs = {key: options[key] for key in RELAYED_KWARGS if key in options}
    try:
        response = discord_request(method, url, **kwargs)
    except Exception as exc:
        # The caller reports this as an unreachable Discord, not a server error.
        logging.warning("DiscordRelay", f"{method} {url} failed: {type(exc).__name__}: {exc}")
        return jsonify({"error": f"{type(exc).__name__}: {exc}"}), 502

    try:
        body = base64.b64encode(response.content or b"").decode("ascii")
        headers = {
            str(key): str(value)
            for key, value in (response.headers or {}).items()
            # Hop-by-hop headers describe the relay's own connection, and a
            # compressed body would have to stay compressed to keep them honest.
            if str(key).lower() not in {"content-encoding", "transfer-encoding", "connection"}
        }
    finally:
        try:
            response.close()
        except Exception:
            pass
    return jsonify({
        "status": int(getattr(response, "status_code", 0) or 0),
        "reason": str(getattr(response, "reason", "") or ""),
        "headers": headers,
        "body": body,
    })
