"""Last.fm account linking over last.fm's own web auth.

Discord cannot tell us who owns a Last.fm handle, and typing one in proves
nothing, so linking goes through the provider's web auth instead:

1. ``GET /api/lastfm/link`` sends the signed-in member to
   ``https://www.last.fm/api/auth/`` with this site's callback.
2. They approve the application and last.fm sends them back to
   ``/api/lastfm/callback?token=…``.
3. The token is exchanged for a session key (``auth.getSession``, signed with
   ``LASTFM_API_SECRET``), which is what proves the account is theirs. The handle
   and key are stored in ``lastfm_users`` and the member gets a small result
   page.

Both endpoints live under ``/api/`` so the dashboard child forwards them to the
bot child (``web_bridge``), which is the process holding the database pool. The
callback URI is fixed and configured on the last.fm application itself:
``https://<site>/api/lastfm/callback`` (or ``LASTFM_REDIRECT_URI``), so it never
depends on which host the member happened to start from.
"""

import os
import time

import requests
from flask import redirect

from cogs.lastfm import _store
from utils import logging
from utils.lastfm import API_URL, api_signature, auth_url as lastfm_auth_url
from .. import lastfm_page
from .. import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

LINK_PATH = "/api/lastfm/link"
CALLBACK_PATH = "/api/lastfm/callback"
ME_PATH = "/api/lastfm/me"

#: Where the pending approval travels between the two legs. It is in the signed
#: session cookie, not the URL: the callback has to be provably the answer to a
#: request this member started, or anybody could hand them a token of their own.
PENDING_KEY = "lastfm_link"
PENDING_MAX_AGE = 900


def _api_key() -> str:
    return (os.environ.get("LASTFM_API_KEY", "") or "").strip()


def _api_secret() -> str:
    return (os.environ.get("LASTFM_API_SECRET", "") or "").strip()


def _configured() -> bool:
    return bool(_api_key() and _api_secret())


def callback_uri() -> str:
    """The address last.fm sends the member back to, registered on the app."""
    explicit = (os.environ.get("LASTFM_REDIRECT_URI", "") or "").strip()
    if explicit:
        return explicit
    origin = config.canonical_origin() or public_base_url()
    return f"{origin.rstrip('/')}{CALLBACK_PATH}"


def _session_user_id() -> str:
    """The signed-in Discord id, or "" when nobody is signed in."""
    user = session.get("user") or {}
    user_id = str(user.get("id") or "").strip()
    return user_id if user_id.isdigit() else ""


class LinkError(Exception):
    """A linking failure with wording that is safe to show the member."""


def _exchange(token: str) -> dict:
    """Trade a web-auth token for the member's session key.

    Kept synchronous and local to the request: this is a single short call made
    while the member is looking at the page, so it does not need the bot's
    asyncio client (which lives on another loop).
    """
    signed = {"api_key": _api_key(), "method": "auth.getSession", "token": token}
    params = {
        **signed,
        "api_sig": api_signature(_api_secret(), signed),
        "format": "json",
    }
    response = requests.get(API_URL, params=params, timeout=10)
    if response.status_code >= 500:
        raise LinkError("Last.fm is having trouble right now. Try again in a minute.")
    try:
        payload = response.json()
    except ValueError:
        raise LinkError("Last.fm sent an answer this site could not read.")
    if not isinstance(payload, dict):
        raise LinkError("Last.fm sent an answer this site could not read.")
    code = payload.get("error")
    if code:
        try:
            code = int(code)
        except (TypeError, ValueError):
            code = None
        if code in (4, 9, 14, 15):
            raise LinkError(
                "That approval has expired or was already used. Start again from Discord."
            )
        if code in (10, 13, 26):
            raise LinkError("Last.fm rejected this site's application key.")
        raise LinkError("Last.fm refused to confirm that account.")
    session_data = payload.get("session") or {}
    username = str(session_data.get("name") or "").strip()
    session_key = str(session_data.get("key") or "").strip()
    if not username or not session_key:
        raise LinkError("Last.fm did not confirm that account.")
    return {"username": username, "session_key": session_key}


@app.route(LINK_PATH)
def lastfm_link_start():
    """Send the member to last.fm to approve this application."""
    if not _configured():
        return lastfm_page.error_page(
            "This deployment has not configured Last.fm linking yet "
            "(LASTFM_API_KEY and LASTFM_API_SECRET).",
            title="Last.fm linking is unavailable",
        ), 503

    user_id = _session_user_id()
    if not user_id:
        return redirect(f"/auth/login?next={quote(LINK_PATH)}")

    session[PENDING_KEY] = {"u": user_id, "t": int(time.time())}
    return redirect(lastfm_auth_url(_api_key(), callback_uri()))


@app.route(CALLBACK_PATH)
def lastfm_link_callback():
    """Finish the approval: store the handle the token proves."""
    token = (request.args.get("token") or "").strip()
    pending = session.pop(PENDING_KEY, None) or {}
    user_id = _session_user_id()

    if not user_id:
        # The session cookie did not survive the trip (or the member was signed
        # out meanwhile). Signing in re-runs this exact callback with the token.
        target = f"{CALLBACK_PATH}?token={quote(token)}" if token else LINK_PATH
        return redirect(f"/auth/login?next={quote(target)}")
    if not token:
        return lastfm_page.error_page("Last.fm did not send a linking token back."), 400
    if pending.get("u") != user_id:
        return lastfm_page.error_page(
            "This approval was not started from your account. Open /fm link in "
            "Discord and press connect again."
        ), 400
    if int(pending.get("t") or 0) + PENDING_MAX_AGE < time.time():
        return lastfm_page.error_page("This approval took too long to come back."), 400
    if not _configured():
        return lastfm_page.error_page(
            "Last.fm linking is not configured on this deployment.",
            title="Last.fm linking is unavailable",
        ), 503
    if _discord_bot is None or getattr(_discord_bot, "cxn", None) is None:
        return lastfm_page.error_page(
            "Niko's bot process is restarting, so the account could not be saved. "
            "Try again in a moment."
        ), 503

    try:
        linked = _exchange(token)
    except LinkError as exc:
        return lastfm_page.error_page(str(exc)), 400
    except Exception as exc:  # network, DNS, timeout
        logging.warning("Last.fm", f"Web auth exchange failed: {exc}")
        return lastfm_page.error_page("Last.fm did not answer the linking request."), 502

    try:
        run_on_bot_loop(
            _store.set_account(
                _discord_bot.cxn,
                int(user_id),
                linked["username"],
                session_key=linked["session_key"],
            )
        )
    except Exception as exc:
        logging.warning("Last.fm", f"Could not store the linked account: {exc}")
        return lastfm_page.error_page(
            "Niko could not save the link. Try again in a moment."
        ), 503

    return lastfm_page.linked_page(linked["username"])


@app.route(ME_PATH)
def lastfm_me():
    """Whether this member has linked an account, and how it was linked."""
    payload = {
        "authenticated": bool(_session_user_id()),
        "linked": False,
        "username": None,
        "verified": False,
        "oauth_available": _configured(),
    }
    if not payload["authenticated"]:
        return jsonify(payload)
    if _discord_bot is None or getattr(_discord_bot, "cxn", None) is None:
        return jsonify(payload)
    try:
        row = run_on_bot_loop(_store.get_account_row(_discord_bot.cxn, int(_session_user_id())))
    except Exception:
        row = None
    if row:
        payload["linked"] = True
        payload["username"] = row.get("username")
        payload["verified"] = bool(row.get("session_key"))
        payload["linked_at"] = row.get("linked_at")
    return jsonify(payload)
