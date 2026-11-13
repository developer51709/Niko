"""Routes for the experimental Discord Activity music panel.

The panel is served at ``/activity`` on any host and at ``/`` on the Activity
subdomain, because Discord's URL mapping always points at the root of its
target. Its API lives under ``/api/activity/`` so the dashboard split forwards
it to the process that owns the live bot, exactly like the other live routes.
"""

from flask import Response, jsonify, request, send_from_directory

from .. import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

import hashlib
import logging
import os

from .. import config, runtime
from ..music_activity import (
    ACTIVITY_DIR,
    issue_artwork_token,
    issue_session,
    page_response,
    read_artwork_token,
    read_session,
)

log = logging.getLogger(__name__)


def _authenticated_user() -> int | None:
    header = (request.headers.get("Authorization") or "").strip()
    if not header.lower().startswith("bearer "):
        return None
    return read_session(header[7:].strip())


def _music_cog():
    getter = getattr(runtime._discord_bot, "get_cog", None)
    return getter("MusicSystem") if getter else None


def _guild_arguments() -> tuple[int | None, int | None]:
    """Guild and channel ids from the body (control) or query (state)."""
    body = request.get_json(silent=True) if request.method == "POST" else None
    body = body if isinstance(body, dict) else {}
    guild = str(body.get("guild_id") or request.args.get("guild_id") or "").strip()
    channel = str(body.get("channel_id") or request.args.get("channel_id") or "").strip()
    if not guild.isdigit():
        return None, None
    return int(guild), int(channel) if channel.isdigit() else None


def _snapshot(guild_id: int, user_id: int, channel_id: int | None) -> dict:
    cog = _music_cog()
    if cog is None:
        return {"ok": False, "error": "bot_unavailable"}
    try:
        snapshot = runtime.run_on_bot_loop(
            cog.activity_snapshot(guild_id, user_id, channel_id), timeout=8,
        )
    except RuntimeError:
        return {"ok": False, "error": "bot_unavailable"}
    except Exception:
        log.exception("The music Activity could not read the player")
        return {"ok": False, "error": "bot_unavailable"}
    # Discord's proxy cannot load third-party image hosts from the Activity, so
    # the panel draws artwork from this origin instead. The URL carries a signed
    # token because an <img> request cannot send the panel's bearer header.
    if not isinstance(snapshot, dict):
        return {"ok": False, "error": "bot_unavailable"}
    track = snapshot.get("track")
    if snapshot.get("ok") and isinstance(track, dict) and track.get("artwork"):
        # Discord and the browser cache an image by its URL, so a stable URL kept
        # showing the previous song's cover. The track digest changes with the
        # song and keeps the signed token (which only identifies the member and
        # guild) untouched.
        version = hashlib.sha1(
            "|".join(
                str(track.get(key) or "")
                for key in ("uri", "title", "author", "artwork")
            ).encode()
        ).hexdigest()[:12]
        snapshot["artwork_url"] = (
            "/api/activity/artwork?token="
            f"{issue_artwork_token(user_id, guild_id)}&v={version}"
        )
    return snapshot


@app.route("/activity")
@app.route("/activity/")
def activity_panel():
    if not runtime.oauth_enabled():
        return Response(
            "The music Activity needs Discord OAuth: set DISCORD_CLIENT_SECRET.",
            status=503,
            mimetype="text/plain",
        )
    return page_response()


@app.route("/activity/sdk.js")
def activity_sdk():
    """The Embedded App SDK, bundled locally.

    Discord's proxy sandboxes the page and blocks scripts from hosts that have
    no URL mapping, so the SDK cannot come from a CDN. It is served from this
    origin, which the root mapping already covers.
    """
    return send_from_directory(
        ACTIVITY_DIR, "discord-sdk.js", mimetype="application/javascript",
        max_age=3600,
    )


@app.route("/activity/assets/<path:name>")
def activity_asset(name):
    """Hashed Vite output: the React app and the site stylesheet it imports."""
    return send_from_directory(
        os.path.join(ACTIVITY_DIR, "dist", "assets"), name,
        max_age=3600,
    )


@app.route("/activity/fonts/<path:name>")
def activity_font(name):
    """Self-hosted brand fonts: the Activity's iframe may not load Google Fonts."""
    return send_from_directory(
        os.path.join(ACTIVITY_DIR, "fonts"), name,
        mimetype="font/woff2", max_age=86400,
    )


@app.route("/api/activity/token", methods=["POST"])
def activity_token():
    """Exchange the SDK's one-time code for a panel session.

    The access token goes back to the iframe because the Embedded App SDK's
    ``authenticate`` needs it; nothing is stored server-side. The signed session
    is what the panel's own API calls use afterwards.
    """
    if not runtime.oauth_enabled():
        return jsonify({"error": "Discord OAuth is not configured on this bot."}), 503

    body = request.get_json(silent=True)
    code = str((body or {}).get("code") or "").strip() if isinstance(body, dict) else ""
    if not code:
        return jsonify({"error": "Missing Discord authorization code."}), 400

    try:
        token_response = discord_request(
            "POST",
            f"{config.DISCORD_API}/oauth2/token",
            data={
                "client_id": config.DISCORD_CLIENT_ID,
                "client_secret": config.DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
    except Exception as exc:
        log.warning("MusicActivity", f"Token exchange failed: {type(exc).__name__}: {exc}")
        return jsonify({"error": "Discord could not be reached."}), 502
    if not token_response.ok:
        return jsonify({"error": "Discord rejected the Activity sign-in."}), 401
    token_data = token_response.json()
    access_token = str(token_data.get("access_token") or "")
    if not access_token:
        return jsonify({"error": "Discord did not return a token."}), 401

    try:
        user = discord_get("/users/@me", access_token)
    except Exception:
        return jsonify({"error": "Discord could not confirm the account."}), 502
    user_id = str(user.get("id") or "")
    if not user_id.isdigit():
        return jsonify({"error": "Discord did not identify the account."}), 401

    return jsonify({
        "access_token": access_token,
        "session": issue_session(int(user_id)),
        "user": {
            "id": user_id,
            "name": user.get("global_name") or user.get("username") or "",
        },
    })


@app.route("/api/activity/artwork")
@app.route("/activity/artwork")
def activity_artwork():
    """Serve the current track's artwork from this origin.

    The Activity's iframe may only reach hosts Discord has mapped, and album
    artwork lives on YouTube/Spotify/CDN hosts, so the panel cannot draw the
    URL directly. This route fetches the track the bot is actually playing and
    streams it back; the signed token is stable for an hour so the browser can
    cache it between state polls.
    """
    claims = read_artwork_token(request.args.get("token") or "")
    if claims is None:
        return Response(status=401)
    user_id, guild_id = claims
    channel = str(request.args.get("channel_id") or "").strip()
    channel_id = int(channel) if channel.isdigit() else None

    cog = _music_cog()
    if cog is None:
        return Response(status=503)
    try:
        result = runtime.run_on_bot_loop(
            cog.activity_artwork(guild_id, user_id, channel_id), timeout=10,
        )
    except RuntimeError:
        return Response(status=503)
    except Exception:
        log.exception("The music Activity could not read the artwork")
        return Response(status=502)
    if not isinstance(result, dict) or not result.get("ok") or not result.get("data"):
        return Response(status=404)

    response = Response(
        result["data"],
        mimetype=str(result.get("content_type") or "image/jpeg"),
    )
    response.headers["Cache-Control"] = "private, max-age=300"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.route("/api/activity/state")
def activity_state():
    user_id = _authenticated_user()
    if user_id is None:
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    guild_id, channel_id = _guild_arguments()
    if guild_id is None:
        return jsonify({"ok": False, "error": "bad_guild"}), 400
    snapshot = _snapshot(guild_id, user_id, channel_id)
    if snapshot.get("error") == "bot_unavailable":
        return jsonify(snapshot), 503
    return jsonify(snapshot)


@app.route("/api/activity/playlist")
def activity_playlist():
    """One shared playlist's tracks, loaded when its Activity card opens."""
    user_id = _authenticated_user()
    if user_id is None:
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    guild_id, channel_id = _guild_arguments()
    name = str(request.args.get("name") or "").strip()
    if guild_id is None or not name:
        return jsonify({"ok": False, "error": "bad_request"}), 400

    cog = _music_cog()
    if cog is None:
        return jsonify({"ok": False, "error": "bot_unavailable"}), 503
    try:
        result = runtime.run_on_bot_loop(
            cog.activity_playlist(guild_id, user_id, channel_id, name),
            timeout=10,
        )
    except RuntimeError:
        return jsonify({"ok": False, "error": "bot_unavailable"}), 503
    except Exception:
        log.exception("The music Activity could not read a playlist")
        return jsonify({"ok": False, "error": "bot_unavailable"}), 502
    return jsonify(result)


@app.route("/api/activity/control", methods=["POST"])
def activity_control():
    user_id = _authenticated_user()
    if user_id is None:
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    guild_id, channel_id = _guild_arguments()
    if guild_id is None:
        return jsonify({"ok": False, "error": "bad_guild"}), 400

    cog = _music_cog()
    if cog is None:
        return jsonify({"ok": False, "error": "bot_unavailable"}), 503

    body = request.get_json(silent=True)
    body = body if isinstance(body, dict) else {}
    action = str(body.get("action") or "").strip().lower()
    if not action:
        return jsonify({"ok": False, "error": "missing_action"}), 400

    try:
        snapshot = runtime.run_on_bot_loop(
            cog.activity_control(guild_id, user_id, action, body.get("value"), channel_id),
            timeout=12,
        )
    except RuntimeError:
        return jsonify({"ok": False, "error": "bot_unavailable"}), 503
    except Exception:
        log.exception("The music Activity control failed")
        return jsonify({"ok": False, "error": "bot_unavailable"}), 502
    return jsonify(snapshot)
