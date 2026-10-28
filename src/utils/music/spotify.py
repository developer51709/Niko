"""
Music System — Spotify URL / URI resolution.

Resolves tracks, albums, and playlists → YouTube search strings using the
Spotify Web API with client-credentials auth. Requires SPOTIFY_CLIENT_ID and
SPOTIFY_CLIENT_SECRET (silently disabled when absent).
"""

import asyncio
import base64
import re
import time as _time

import aiohttp

_SPOTIFY_LOCALE = r"(?:embed/)?(?:(?:[a-z]{2}(?:-[A-Z]{2})?|intl-[a-z]{2})/)?"
_SPOTIFY_TRACK_RE    = re.compile(r"open\.spotify\.com/" + _SPOTIFY_LOCALE + r"track/([A-Za-z0-9]+)")
_SPOTIFY_ALBUM_RE    = re.compile(r"open\.spotify\.com/" + _SPOTIFY_LOCALE + r"album/([A-Za-z0-9]+)")
_SPOTIFY_PLAYLIST_RE = re.compile(r"open\.spotify\.com/" + _SPOTIFY_LOCALE + r"playlist/([A-Za-z0-9]+)")


def _normalize_spotify_reference(raw: str) -> str | None:
    """Convert a Spotify URI or short reference into a canonical
    ``open.spotify.com/<type>/<id>`` URL. Returns None if it is not a
    recognised Spotify reference."""
    q = raw.strip()
    m = re.match(r"^spotify:(?:track|album|playlist):([A-Za-z0-9]+)(?:.*)$", q)
    if m:
        kind = "track" if q.startswith("spotify:track:") else ("album" if q.startswith("spotify:album:") else "playlist")
        return f"https://open.spotify.com/{kind}/{m.group(1)}"
    for kind in ("track", "album", "playlist"):
        if re.search(r"open\.spotify\.com/" + _SPOTIFY_LOCALE + kind + r"/([A-Za-z0-9]+)", q):
            return q  # already a web URL the *_RE patterns can parse
    return None


class SpotifyClient:
    """Thin async client for the Spotify Web API (client-credentials flow)."""

    _TOKEN_URL = "https://accounts.spotify.com/api/token"
    _API_URL   = "https://api.spotify.com/v1"

    def __init__(self, client_id: str, client_secret: str):
        self._id     = client_id
        self._secret = client_secret
        self._token: str | None = None
        self._exp: float = 0.0

    async def _token_headers(self) -> dict:
        """Fetch (and cache) a client-credentials token with one retry."""
        if not self._token or _time.monotonic() >= self._exp - 60:
            creds = base64.b64encode(f"{self._id}:{self._secret}".encode()).decode()
            last_error: Exception | None = None
            for attempt in range(2):
                try:
                    async with aiohttp.ClientSession() as s:
                        async with s.post(
                            self._TOKEN_URL,
                            headers={"Authorization": f"Basic {creds}"},
                            data={"grant_type": "client_credentials"},
                            timeout=aiohttp.ClientTimeout(total=10),
                        ) as r:
                            if r.status == 200:
                                data = await r.json(content_type=None)
                                self._token = data["access_token"]
                                self._exp   = _time.monotonic() + data.get("expires_in", 3600)
                            elif r.status in (429, 500, 502, 503):
                                last_error = RuntimeError(f"Spotify token endpoint HTTP {r.status}")
                                await asyncio.sleep(1 + attempt)
                            else:
                                last_error = RuntimeError(
                                    f"Spotify token endpoint HTTP {r.status} — check SPOTIFY_CLIENT_ID/SECRET"
                                )
                except Exception as exc:
                    last_error = exc
                    await asyncio.sleep(1)
                if self._token:
                    break
            if not self._token:
                raise RuntimeError(f"Could not obtain Spotify token: {last_error}")
        return {"Authorization": f"Bearer {self._token}"}

    async def _get(self, path: str) -> dict | None:
        """GET a Spotify API path with retries on transient failures and one
        forced token refresh when the API rejects our credentials."""
        for attempt in range(2):
            try:
                headers = await self._token_headers()
                async with aiohttp.ClientSession() as s:
                    async with s.get(
                        f"{self._API_URL}/{path}",
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as r:
                        if r.status == 200:
                            return await r.json(content_type=None)
                        if r.status == 401:
                            # Credentials may have been invalidated — refresh once.
                            self._token = None
                            self._exp   = 0.0
                            continue
                        if r.status == 403:
                            # Forbidden is a scope/plan limit, not a bad token:
                            # refreshing would only burn another request.
                            return None
                        if r.status in (429, 500, 502, 503):
                            await asyncio.sleep(1)
                            continue
                        return None
            except Exception:
                await asyncio.sleep(1)
        return None

    async def resolve_track(self, track_id: str) -> str | None:
        """Returns 'Artist - Title' search string."""
        data = await self._get(f"tracks/{track_id}")
        if not data:
            return None
        artist = data["artists"][0]["name"] if data.get("artists") else "Unknown"
        return f"{artist} - {data['name']}"

    async def resolve_album(self, album_id: str) -> list[str]:
        """Returns list of 'Artist - Title' search strings for all album tracks."""
        data = await self._get(f"albums/{album_id}/tracks?limit=50")
        if not data:
            return []
        queries = []
        for item in data.get("items", []):
            artist = item["artists"][0]["name"] if item.get("artists") else "Unknown"
            queries.append(f"{artist} - {item['name']}")
        return queries

    async def resolve_playlist(self, playlist_id: str) -> list[str]:
        """Returns list of 'Artist - Title' search strings (first 50 tracks).

        Spotify removed ``/playlists/{id}/tracks`` for Development Mode apps in
        February 2026; ``/items`` is its replacement and returns each track
        under ``item`` instead of ``track``. Older payloads are still read so a
        deployment with grandfathered access keeps working.
        """
        data = await self._get(f"playlists/{playlist_id}/items?limit=50")
        if not data:
            return []
        queries = []
        for entry in data.get("items", []):
            # ``item`` is the current field, ``track`` the pre-2026 one.
            track = entry.get("item") or entry.get("track")
            if not isinstance(track, dict):
                continue  # removed track, deleted episode, …
            name = track.get("name")
            if not name:
                continue
            artists = track.get("artists") or []
            artist = artists[0].get("name") if artists and isinstance(artists[0], dict) else "Unknown"
            queries.append(f"{artist} - {name}")
        return queries