"""
Music System — Spotify URL / URI resolution.

Turns ``open.spotify.com`` links into YouTube search strings for tracks, albums
and playlists. Two lookup methods are needed, because neither covers everything
Spotify's Web API still permits:

  • Web API (client credentials) — official, but only when
    SPOTIFY_CLIENT_ID/SPOTIFY_CLIENT_SECRET are configured. Since February 2026
    a client-credentials token can no longer read another account's playlist
    contents: ``GET /playlists/{id}/items`` answers 403, or returns metadata
    with the ``items`` array omitted. Tracks and albums still resolve here.
  • Public embed page — no credentials at all. ``/embed/<kind>/<id>`` ships a
    ``__NEXT_DATA__`` payload that carries the track's name and artists, or an
    album/playlist's track list with each entry's artist. This is what keeps
    playlist links working.

The Web API is tried first when credentials exist, so an app that still has
access keeps returning canonical metadata; any refusal falls through to the
embed page instead of failing the command.
"""

import asyncio
import base64
import json
import re
import time as _time

import aiohttp

from utils import logging as log

_SPOTIFY_LOCALE = r"(?:embed/)?(?:(?:[a-z]{2}(?:-[A-Z]{2})?|intl-[a-z]{2})/)?"
_SPOTIFY_TRACK_RE    = re.compile(r"open\.spotify\.com/" + _SPOTIFY_LOCALE + r"track/([A-Za-z0-9]+)")
_SPOTIFY_ALBUM_RE    = re.compile(r"open\.spotify\.com/" + _SPOTIFY_LOCALE + r"album/([A-Za-z0-9]+)")
_SPOTIFY_PLAYLIST_RE = re.compile(r"open\.spotify\.com/" + _SPOTIFY_LOCALE + r"playlist/([A-Za-z0-9]+)")

# How long the Web API is skipped after it refuses a call for a non-transient
# reason (Development Mode / premium gating, rejected credentials). Without it
# every link pays a failing round trip before the embed fallback runs.
_API_COOLDOWN = 600.0

_EMBED_URL = "https://open.spotify.com/embed/{kind}/{spotify_id}"
# The embed page is a Next.js app; its server-rendered payload is the only
# metadata available without an access token.
_NEXT_DATA_RE = re.compile(
    r'<script[^>]*\bid="__NEXT_DATA__"[^>]*>(.*?)</script>', re.DOTALL
)
# Spotify answers a bare scripted request with a bot page; a browser UA gets
# the normal embed document.
_BROWSER_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

# Last failure written to the log, so a persistent problem (bad key, revoked
# access, blocked embed page) is reported once instead of on every /play.
_last_failure: str | None = None


def _report_failure(message: str) -> None:
    global _last_failure
    if message == _last_failure:
        return
    _last_failure = message
    log.warning("Music", f"Spotify lookup failed — {message}")


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


# ── Search-string helpers ────────────────────────────────────────────────

def _artist_title(track) -> str | None:
    """``'Artist - Title'`` for a Web API track object, or None."""
    if not isinstance(track, dict):
        return None
    name = str(track.get("name") or "").strip()
    if not name:
        return None
    artists = track.get("artists") or []
    artist = ""
    if artists and isinstance(artists[0], dict):
        artist = str(artists[0].get("name") or "").strip()
    return f"{artist or 'Unknown'} - {name}"


def _api_queries(items) -> list[str]:
    """Search strings from a Web API ``items`` array (album tracks or playlist
    entries — playlist entries wrap their track in ``item``, ``track`` before
    2026)."""
    queries: list[str] = []
    for entry in items or []:
        if not isinstance(entry, dict):
            continue
        track = entry.get("item") or entry.get("track") or entry
        query = _artist_title(track)
        if query:
            queries.append(query)
    return queries


def _entity_from_html(html: str | None) -> dict | None:
    """Pull the ``entity`` object out of an embed page's ``__NEXT_DATA__``."""
    match = _NEXT_DATA_RE.search(html or "")
    if not match:
        return None
    try:
        data = json.loads(match.group(1))
    except (TypeError, ValueError):
        return None
    entity = (
        data.get("props", {})
        .get("pageProps", {})
        .get("state", {})
        .get("data", {})
        .get("entity")
    )
    return entity if isinstance(entity, dict) else None


def _entity_queries(entity: dict | None, kind: str) -> list[str]:
    """Search strings from an embed entity.

    Albums and playlists carry a ``trackList`` of ``{title, subtitle}`` pairs,
    where ``subtitle`` is the artist and ``title`` the song. A track page puts
    the song in ``name``/``title`` with an ``artists`` array instead.
    """
    if not isinstance(entity, dict):
        return []

    queries: list[str] = []
    for item in entity.get("trackList") or []:
        if not isinstance(item, dict):
            continue
        if str(item.get("entityType") or "track").lower() != "track":
            continue
        title = str(item.get("title") or item.get("name") or "").strip()
        if not title:
            continue
        artist = str(item.get("subtitle") or "").strip() or "Unknown"
        queries.append(f"{artist} - {title}")
    if queries:
        return queries

    if kind == "track":
        name = str(entity.get("name") or entity.get("title") or "").strip()
        if not name:
            return []
        artists = [
            str(a.get("name")).strip()
            for a in entity.get("artists") or []
            if isinstance(a, dict) and a.get("name")
        ]
        return [f"{artists[0]} - {name}" if artists else f"Unknown - {name}"]
    return []


# ── Embed lookup (no auth) ───────────────────────────────────────────────

async def _fetch_embed_html(kind: str, spotify_id: str) -> str | None:
    """Fetch the public embed document for a track/album/playlist."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                _EMBED_URL.format(kind=kind, spotify_id=spotify_id),
                headers={"User-Agent": _BROWSER_UA, "Accept-Language": "en"},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status != 200:
                    _report_failure(
                        f"embed page HTTP {response.status} for {kind} {spotify_id}"
                    )
                    return None
                return await response.text()
    except Exception as exc:  # aiohttp errors, timeouts, DNS, …
        _report_failure(f"embed page {type(exc).__name__}: {exc}")
        return None


class SpotifyClient:
    """Resolves Spotify references to YouTube search strings.

    Credentials are optional: without SPOTIFY_CLIENT_ID/SECRET (or when the Web
    API refuses the request) every lookup goes through the public embed page.
    """

    _TOKEN_URL = "https://accounts.spotify.com/api/token"
    _API_URL   = "https://api.spotify.com/v1"

    def __init__(self, client_id: str = "", client_secret: str = ""):
        # Whitespace pasted from the dashboard/env file is the usual cause of
        # an ``invalid_client`` from the token endpoint.
        self._id     = (client_id or "").strip()
        self._secret = (client_secret or "").strip()
        self._token: str | None = None
        self._exp: float = 0.0
        self._api_down_until: float = 0.0

    @property
    def has_credentials(self) -> bool:
        return bool(self._id and self._secret)

    @property
    def _api_usable(self) -> bool:
        """Whether a Web API call is worth attempting right now."""
        return self.has_credentials and _time.monotonic() >= self._api_down_until

    # ── Web API ──────────────────────────────────────────────────────────
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
                                detail = (await r.text())[:120].replace("\n", " ")
                                last_error = RuntimeError(
                                    f"Spotify token endpoint HTTP {r.status} ({detail}) — "
                                    "check SPOTIFY_CLIENT_ID/SECRET"
                                )
                except Exception as exc:
                    last_error = exc
                    await asyncio.sleep(1)
                if self._token:
                    break
            if not self._token:
                self._api_down_until = _time.monotonic() + _API_COOLDOWN
                _report_failure(str(last_error))
                raise RuntimeError(f"Could not obtain Spotify token: {last_error}")
        return {"Authorization": f"Bearer {self._token}"}

    async def _get(self, path: str) -> dict | None:
        """GET a Spotify API path with retries on transient failures and one
        forced token refresh when the API rejects our credentials."""
        for attempt in range(2):
            try:
                headers = await self._token_headers()
            except Exception:
                # _token_headers already reported the reason (and set the
                # cooldown); retrying here would only duplicate the log line.
                return None
            try:
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
                            if attempt:
                                _report_failure(f"Web API rejected the access token for {path}")
                            continue
                        if r.status in (429, 500, 502, 503):
                            await asyncio.sleep(1)
                            continue
                        # 403 = Development Mode / quota / premium restriction, not
                        # a bad token: refreshing would only burn another request.
                        detail = (await r.text())[:160].replace("\n", " ")
                        self._api_down_until = _time.monotonic() + _API_COOLDOWN
                        _report_failure(f"Web API HTTP {r.status} for {path}: {detail}")
                        return None
            except Exception as exc:
                _report_failure(f"Web API {type(exc).__name__} for {path}: {exc}")
                await asyncio.sleep(1)
        return None

    # ── Resolution ───────────────────────────────────────────────────────
    async def _embed(self, kind: str, spotify_id: str) -> dict | None:
        return _entity_from_html(await _fetch_embed_html(kind, spotify_id))

    async def resolve_track(self, track_id: str) -> str | None:
        """Returns 'Artist - Title' search string."""
        if self._api_usable:
            data = await self._get(f"tracks/{track_id}")
            query = _artist_title(data) if data else None
            if query:
                return query
        queries = _entity_queries(await self._embed("track", track_id), "track")
        return queries[0] if queries else None

    async def resolve_album(self, album_id: str) -> list[str]:
        """Returns list of 'Artist - Title' search strings for all album tracks."""
        if self._api_usable:
            data = await self._get(f"albums/{album_id}/tracks?limit=50")
            queries = _api_queries((data or {}).get("items"))
            if queries:
                return queries
        return _entity_queries(await self._embed("album", album_id), "album")

    async def resolve_playlist(self, playlist_id: str) -> list[str]:
        """Returns list of 'Artist - Title' search strings (up to 50 tracks).

        ``/items`` is the 2026 replacement for the removed ``/tracks`` endpoint,
        but a client-credentials token is never the playlist's owner, so it
        usually answers 403 or with ``items`` omitted; the embed page is what
        actually resolves public playlists.
        """
        if self._api_usable:
            data = await self._get(f"playlists/{playlist_id}/items?limit=50")
            queries = _api_queries((data or {}).get("items"))
            if queries:
                return queries
        return _entity_queries(await self._embed("playlist", playlist_id), "playlist")
