"""Twitch Helix access using application (client-credentials) credentials.

Twitch is the one social platform in the notifier that needs real credentials,
so the same ``TWITCH_CLIENT_ID``/``TWITCH_CLIENT_SECRET`` pair that authorises
new-stream announcements is also used for the public team-profile cards.  That
shared, non-decorative use is what justifies asking a self-hoster to configure
the app credentials at all.

The module is synchronous on purpose: the Flask web process calls it directly
and the notifier runs it through ``asyncio.to_thread`` so both surfaces share
one implementation and one cached app token.
"""

from __future__ import annotations

import os
import re
import threading
import time

import requests

_HELIX = "https://api.twitch.tv/helix"
_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
_TIMEOUT = 10

# Twitch app tokens live ~60 days; refresh a minute early so a cached token can
# never expire in the middle of a request.
_TOKEN_LOCK = threading.Lock()
_TOKEN_CACHE: dict = {"value": "", "expires_at": 0.0}


def credentials() -> tuple[str, str]:
    """Return the configured (client_id, client_secret) pair, if any."""
    return (
        os.environ.get("TWITCH_CLIENT_ID", "").strip(),
        os.environ.get("TWITCH_CLIENT_SECRET", "").strip(),
    )


def credentials_configured() -> bool:
    """True when both halves of the application credential are present."""
    client_id, client_secret = credentials()
    return bool(client_id and client_secret)


def access_token() -> str | None:
    """Return a cached app access token, minting one when needed."""
    client_id, client_secret = credentials()
    if not client_id or not client_secret:
        return None
    with _TOKEN_LOCK:
        cached = str(_TOKEN_CACHE.get("value") or "")
        if cached and time.time() < float(_TOKEN_CACHE.get("expires_at") or 0):
            return cached
        try:
            response = requests.post(
                _TOKEN_URL,
                params={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "grant_type": "client_credentials",
                },
                timeout=_TIMEOUT,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception:
            return None
        token = str(payload.get("access_token") or "")
        if not token:
            return None
        expires_in = float(payload.get("expires_in") or 0)
        _TOKEN_CACHE["value"] = token
        _TOKEN_CACHE["expires_at"] = time.time() + max(60.0, expires_in - 60.0)
        return token


def _helix(path: str, **params):
    """GET a Helix endpoint and return its ``data`` list, or ``None``."""
    client_id, _ = credentials()
    token = access_token()
    if not token:
        return None
    try:
        response = requests.get(
            f"{_HELIX}{path}",
            headers={"Client-Id": client_id, "Authorization": f"Bearer {token}"},
            params=params,
            timeout=_TIMEOUT,
        )
        if response.status_code != 200:
            return None
        return response.json().get("data") or []
    except Exception:
        return None


def normalize_login(value: str) -> str:
    """Reduce a login, @handle, or twitch.tv URL to a bare login name."""
    text = (value or "").strip()
    lowered = text.lower()
    for prefix in ("https://", "http://"):
        if lowered.startswith(prefix):
            text = text[len(prefix):]
            lowered = text.lower()
    if lowered.startswith("www."):
        text = text[4:]
        lowered = text.lower()
    if lowered.startswith("twitch.tv/"):
        text = text[len("twitch.tv/"):]
    text = text.lstrip("@").split("/")[0].split("?")[0]
    return text if re.fullmatch(r"[A-Za-z0-9_]{1,25}", text) else ""


def thumbnail_url(raw: str | None) -> str | None:
    """Swap Twitch's ``{width}x{height}`` placeholder for a usable size."""
    if not raw:
        return None
    return raw.replace("{width}", "1280").replace("{height}", "720")


def fetch_channel(login: str) -> dict | None:
    """Return the Helix user record for a login, or ``None``."""
    login = normalize_login(login)
    if not login:
        return None
    users = _helix("/users", login=login)
    if not users:
        return None
    return users[0]


def fetch_live_stream(login: str) -> dict | None:
    """Return the live-stream record for a login when the channel is live."""
    login = normalize_login(login)
    if not login:
        return None
    streams = _helix("/streams", user_login=login)
    return streams[0] if streams else None


def fetch_latest_video(user_id: str) -> dict | None:
    """Return the most recent archived broadcast for a numeric user id."""
    if not user_id:
        return None
    videos = _helix("/videos", user_id=user_id, first=1, type="archive")
    return videos[0] if videos else None


def validate_twitch_login(login: str) -> bool:
    """True when Twitch confirms the channel exists."""
    return fetch_channel(login) is not None


def fetch_latest_twitch(login: str) -> dict | None:
    """Notifier payload for the newest Twitch activity on a channel.

    Prefers a live stream and falls back to the latest archived broadcast so a
    channel that is offline does not silently produce no notifications.
    """
    login = normalize_login(login)
    channel = fetch_channel(login)
    if channel is None:
        return None

    stream = fetch_live_stream(login)
    if stream:
        title = stream.get("title") or "Live now"
        return {
            "id": f"stream:{stream.get('id')}",
            "url": f"https://www.twitch.tv/{channel.get('login') or login}",
            "title": title,
            "text": title,
            "thumbnail": thumbnail_url(stream.get("thumbnail_url")),
        }

    video = fetch_latest_video(str(channel.get("id") or ""))
    if not video:
        return None
    title = video.get("title") or "New broadcast"
    return {
        "id": f"video:{video.get('id')}",
        "url": video.get("url") or f"https://www.twitch.tv/{channel.get('login') or login}",
        "title": title,
        "text": title,
        "thumbnail": thumbnail_url(video.get("thumbnail_url")),
    }
