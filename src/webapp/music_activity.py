"""Server half of the experimental Discord Activity music panel.

The Activity runs in an iframe on ``discord.com`` and is served through
Discord's URL mapping, so the site's session cookie cannot carry identity into
it: third-party cookies are partitioned, and the mapped origin is not the
site's own. Identity is proved the way Discord documents instead — the
Embedded App SDK's ``authorize`` returns a one-time code, the server exchanges
it for the member's token, and the panel gets a short-lived signed session
that its API calls carry back.

Guild and channel IDs from the client are lookup keys, never proof: every
request resolves the member and the voice channel through the bot's own cache
before anything is read or changed.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time

from flask import Response, current_app

ACTIVITY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "activity")

#: The Vite build served to Discord. Rebuild it with `npm run build:activity`.
PAGE_PATH = os.path.join(ACTIVITY_DIR, "dist", "activity", "index.html")

#: How long an opened player may keep polling. The Activity is reopened from the
#: now-playing panel, so a session only has to outlive one listening session.
SESSION_TTL = 6 * 60 * 60


def page_html(client_id: str) -> str:
    """The panel document with the OAuth client id filled in."""
    with open(PAGE_PATH, "r", encoding="utf-8") as handle:
        return handle.read().replace("__CLIENT_ID__", str(client_id or ""))


def page_response() -> Response:
    """Serve the panel, never cached: it carries a build-coupled client id."""
    from . import config

    response = Response(page_html(config.DISCORD_CLIENT_ID), mimetype="text/html")
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Robots-Tag"] = "noindex"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


def _secret() -> bytes:
    key = current_app.secret_key
    return key if isinstance(key, bytes) else str(key or "").encode()


def _sign(payload: str) -> str:
    return hmac.new(_secret(), payload.encode(), hashlib.sha256).hexdigest()


def issue_session(user_id: int) -> str:
    """A bearer value the panel sends with every API call."""
    encoded = _encode({"u": int(user_id), "exp": int(time.time()) + SESSION_TTL})
    return f"{encoded}.{_sign(encoded)}"


def _encode(payload: dict) -> str:
    raw = json.dumps(payload, separators=(",", ":"))
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def _decode(encoded: str) -> dict | None:
    try:
        payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


#: Artwork is loaded by an ``<img>`` tag, which cannot carry the panel's bearer
#: header. The state gives the panel a signed URL for the current member instead,
#: stable for an hour so the browser can cache the image.
ARTWORK_TTL = 60 * 60


def issue_artwork_token(user_id: int, guild_id: int, *, issued_at: int | None = None) -> str:
    """A token an ``<img>`` URL can carry to fetch one guild's current artwork."""
    now = int(time.time()) if issued_at is None else int(issued_at)
    expires = (now // ARTWORK_TTL + 1) * ARTWORK_TTL
    encoded = _encode({"u": int(user_id), "g": int(guild_id), "exp": expires})
    return f"{encoded}.{_sign(encoded)}"


def read_artwork_token(token: str) -> tuple[int, int] | None:
    """The member and guild an artwork token was issued for, or ``None``."""
    encoded, _, signature = (token or "").partition(".")
    if not encoded or not signature:
        return None
    if not hmac.compare_digest(_sign(encoded), signature):
        return None
    payload = _decode(encoded)
    if not payload:
        return None
    if int(payload.get("exp") or 0) < time.time():
        return None
    user_id, guild_id = payload.get("u"), payload.get("g")
    if not isinstance(user_id, int) or isinstance(user_id, bool):
        return None
    if not isinstance(guild_id, int) or isinstance(guild_id, bool):
        return None
    return user_id, guild_id


def read_session(token: str) -> int | None:
    """The member id a panel session belongs to, or ``None`` when it is not ours."""
    encoded, _, signature = (token or "").partition(".")
    if not encoded or not signature:
        return None
    if not hmac.compare_digest(_sign(encoded), signature):
        return None
    try:
        payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    if int(payload.get("exp") or 0) < time.time():
        return None
    user_id = payload.get("u")
    if isinstance(user_id, bool):
        return None
    if isinstance(user_id, int):
        return user_id
    return int(user_id) if str(user_id).isdigit() else None
