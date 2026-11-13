"""Last.fm API client for the ``/fm`` commands.

The bot only needs the read half of Last.fm's API: a linked account's library,
its top artists/albums/tracks for a period, the few most recent scrobbles, and
one artist's or album's numbers. Everything goes through :class:`LastFmClient`
so the rate limit, the caching and the error wording stay in one place.

Three behaviours matter for a Discord bot:

* **The key is optional at import time.** A deployment without
  ``LASTFM_API_KEY`` still starts; commands answer with a clear notice instead
  of crashing the cog.
* **Last.fm allows roughly five requests a second.** The client reserves a slot
  before every request, so a ``whoknows`` refresh that fans out across several
  members cannot trip ``error 29``.
* **Answers are cached briefly.** A card that re-renders on a period change
  must not re-hit the API for a library that cannot have changed meaningfully
  in a minute, and Last.fm's own numbers are only as fresh as its cache anyway.

Payload shapes are normalised here (``playcount`` is always an ``int``, images
are always a URL or ``None``) so no caller has to remember which fields Last.fm
returns as strings.
"""

from __future__ import annotations

import asyncio
import hashlib
import time
from typing import Any, Awaitable, Callable
from urllib.parse import urlencode

import aiohttp

from utils import logging

API_URL = "https://ws.audioscrobbler.com/2.0/"

#: The page a member approves a web-auth request on.
AUTH_URL = "https://www.last.fm/api/auth/"


def api_signature(secret: str, params: dict[str, str]) -> str:
    """Last.fm's ``api_sig``: md5 of the sorted name/value pairs plus the secret.

    Last.fm signs every authenticated method this way. It is a public helper so
    the website's linking callback and the bot's client cannot drift apart on
    the one detail Last.fm will not forgive.
    """
    payload = "".join(f"{name}{params[name]}" for name in sorted(params))
    return hashlib.md5(f"{payload}{secret}".encode("utf-8")).hexdigest()


def auth_url(api_key: str, callback: str) -> str:
    """The Last.fm page that asks a member to approve this application."""
    return f"{AUTH_URL}?{urlencode({'api_key': api_key, 'cb': callback})}"

#: The periods Last.fm accepts, in the order the picker shows them. ``overall``
#: is first because it is the default a new member expects to see.
PERIODS: tuple[str, ...] = ("overall", "7day", "1month", "3month", "6month", "12month")

_PERIOD_LABELS: dict[str, str] = {
    "overall": "All time",
    "7day": "Last 7 days",
    "1month": "Last month",
    "3month": "Last 3 months",
    "6month": "Last 6 months",
    "12month": "Last year",
}

#: Last.fm's own placeholder cover when an entity has no artwork. It is the
#: same grey star for every entity, so it is treated as "no image".
_PLACEHOLDER_HASH = "2a96cbd8b46e442fc41c2b86b821562f"

#: Preferred image buckets, best first. Last.fm still returns all five for most
#: entities even though only the largest is useful to a card.
_IMAGE_SIZES = ("mega", "extralarge", "large", "medium", "small")

_MAX_CACHE = 512

_Transport = Callable[[str, dict], Awaitable[dict]]


def period_label(period: str | None) -> str:
    """Human wording for a Last.fm period key (``7day`` → ``Last 7 days``)."""
    return _PERIOD_LABELS.get(str(period or "").lower(), "All time")


class LastFmError(Exception):
    """A Last.fm request that could not answer.

    ``code`` is Last.fm's own error number when the API rejected the request
    (``6`` unknown user/artist, ``10`` bad key, ``26`` suspended, ``29`` rate
    limited), and ``None`` for transport failures and missing configuration.
    """

    def __init__(self, message: str, *, code: int | None = None):
        super().__init__(message)
        self.message = message
        self.code = code

    @property
    def unknown_user(self) -> bool:
        return self.code == 6

    @property
    def bad_key(self) -> bool:
        return self.code in (10, 26)

    @property
    def rate_limited(self) -> bool:
        return self.code == 29

    @property
    def auth_failed(self) -> bool:
        """The web-auth token was rejected, used already, or expired."""
        return self.code in (4, 9, 14, 15)


# ── Normalisers ────────────────────────────────────────────────────────────

def _int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _text(value: Any) -> str:
    """Last.fm wraps some strings in ``{"#text": …}`` and others are bare."""
    if isinstance(value, dict):
        value = value.get("#text")
    return str(value or "").strip()


def image_url(images: Any) -> str | None:
    """The largest real artwork URL in a Last.fm ``image`` list."""
    if not images:
        return None
    by_size: dict[str, str] = {}
    for entry in images if isinstance(images, list) else []:
        if not isinstance(entry, dict):
            continue
        url = str(entry.get("#text") or "").strip()
        if not url or _PLACEHOLDER_HASH in url:
            continue
        by_size[str(entry.get("size") or "")] = url
    for size in _IMAGE_SIZES:
        if by_size.get(size):
            return by_size[size]
    return next(iter(by_size.values()), None)


def _items(container: Any, key: str) -> list[dict]:
    """The list under ``container[key][<singular>]`` as a plain list.

    Last.fm returns ``{"artist": {...}}`` instead of a list when an entity has
    exactly one child, which is the classic pagination bug in every Last.fm
    integration. Both shapes are flattened here.
    """
    if not isinstance(container, dict):
        return []
    value = container.get(key)
    if isinstance(value, dict):
        # A lone entity: Last.fm sends the object itself instead of a one-item
        # list. It is recognised by its own ``name`` before its nested lists
        # (``image`` is also a list) are mistaken for the entries.
        if "name" in value:
            return [value]
        inner: list[dict] = []
        for child in value.values():
            if isinstance(child, list):
                inner.extend(item for item in child if isinstance(item, dict))
        if inner:
            return inner
        return []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def _playcount(value: Any) -> int:
    return _int(_text(value) or value)


def _canonical(username: str | None) -> str:
    return str(username or "").strip()


class LastFmClient:
    """Reads Last.fm's public API for one bot deployment.

    ``transport`` is the seam tests and the beta's fake feed use: an async
    callable ``(method, params) -> payload`` that replaces the HTTP request.
    """

    #: Seconds between two requests. Last.fm's documented limit is about five
    #: per second per key; the small gap keeps bursts under it.
    MIN_INTERVAL = 0.21

    def __init__(
        self,
        api_key: str = "",
        *,
        api_secret: str | None = None,
        transport: _Transport | None = None,
        clock: Callable[[], float] = time.monotonic,
        cache_ttl: float = 60.0,
    ):
        self.api_key = str(api_key or "").strip()
        self.api_secret = str(api_secret if api_secret is not None else "").strip()
        self._transport = transport
        self._clock = clock
        self._cache_ttl = float(cache_ttl)
        self._cache: dict[tuple, tuple[float, Any]] = {}
        self._lock = asyncio.Lock()
        self._last_call = 0.0
        self._session: aiohttp.ClientSession | None = None

    # ── availability ──────────────────────────────────────────────────
    @property
    def has_key(self) -> bool:
        return bool(self.api_key) or self._transport is not None

    @property
    def has_secret(self) -> bool:
        """Whether web auth (and the signed session exchange) can run."""
        return bool(self.api_key) and bool(self.api_secret)

    def auth_url(self, callback: str) -> str:
        """The Last.fm approval page for this application."""
        return auth_url(self.api_key, callback)

    async def get_session(self, token: str) -> dict:
        """Exchange a returned web-auth token for the member's session.

        This is the second half of last.fm's web auth: the first is the member
        approving the application at :func:`auth_url`, which sends them back to
        the site with a ``token``. The session key is what proves the member owns
        the account, so linking is a real verification instead of a typed name.
        """
        token = str(token or "").strip()
        if not token:
            raise LastFmError("Last.fm did not return a linking token.")
        if not self.has_secret:
            raise LastFmError(
                "Last.fm account linking needs LASTFM_API_SECRET on this bot."
            )
        signed = {"api_key": self.api_key, "method": "auth.getSession", "token": token}
        payload = await self._request(
            "auth.getSession",
            {"token": token, "api_sig": api_signature(self.api_secret, signed)},
        )
        session = payload.get("session") or {}
        username = _text(session.get("name"))
        key = _text(session.get("key"))
        if not username or not key:
            raise LastFmError("Last.fm did not confirm that account.")
        return {
            "username": username,
            "session_key": key,
            "subscriber": _int(session.get("subscriber")) == 1,
            "url": f"https://www.last.fm/user/{username}",
        }

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()
        self._session = None

    # ── scrobbling (signed writes) ────────────────────────────────────
    def _signed(self, method: str, params: dict) -> dict:
        """Add the signature Last.fm requires to an authenticated method.

        ``format`` is deliberately not part of the signed set: Last.fm signs
        only the method, the API key and the method's own parameters.
        """
        signed = {"method": method, "api_key": self.api_key, **params}
        return {**params, "api_sig": api_signature(self.api_secret, signed)}

    async def _post(self, method: str, params: dict) -> dict:
        """POST a write method; Last.fm rejects signed writes over GET."""
        payload = {
            "method": method,
            "api_key": self.api_key,
            "format": "json",
            **params,
        }
        last_error: Exception | None = None
        for attempt in (1, 2):
            await self._reserve_slot()
            try:
                session = await self._session_or_create()
                async with session.post(API_URL, data=payload) as response:
                    body = await response.text()
                    if response.status == 429:
                        raise LastFmError("Last.fm is rate limiting the bot.", code=29)
                    if response.status >= 500:
                        raise LastFmError(
                            f"Last.fm is having trouble (HTTP {response.status})."
                        )
                    try:
                        import json

                        result = json.loads(body or "{}")
                    except ValueError:
                        raise LastFmError("Last.fm sent a response the bot could not read.")
                return self._check(result)
            except LastFmError as exc:
                last_error = exc
                if exc.code is not None:
                    raise
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                last_error = exc
                logging.warning("Last.fm", f"{method} failed: {exc}")
            if attempt == 1:
                await asyncio.sleep(0.8)
        raise LastFmError(
            f"Last.fm did not answer ({last_error})." if last_error else "Last.fm did not answer."
        )

    async def update_now_playing(
        self,
        session_key: str,
        *,
        artist: str,
        title: str,
        album: str | None = None,
        duration: int | None = None,
    ) -> dict:
        """Tell Last.fm what the member's requested track is.

        This is the "now playing" half of scrobbling and is not counted as a
        play; :meth:`scrobble` is what adds the listen to their profile.
        """
        if not self.has_secret:
            raise LastFmError("Scrobbling needs LASTFM_API_SECRET on this bot.")
        if not str(session_key or "").strip():
            raise LastFmError("This member has not linked a Last.fm account.")
        params = {"sk": str(session_key).strip(), "artist": artist, "track": title}
        if album:
            params["album"] = album
        if duration:
            params["duration"] = str(int(duration))
        return await self._post("track.updateNowPlaying", self._signed("track.updateNowPlaying", params))

    async def scrobble(
        self,
        session_key: str,
        *,
        artist: str,
        title: str,
        timestamp: int,
        album: str | None = None,
        duration: int | None = None,
    ) -> dict:
        """Add one completed listen to the member's Last.fm profile."""
        if not self.has_secret:
            raise LastFmError("Scrobbling needs LASTFM_API_SECRET on this bot.")
        if not str(session_key or "").strip():
            raise LastFmError("This member has not linked a Last.fm account.")
        params = {
            "sk": str(session_key).strip(),
            "artist": artist,
            "track": title,
            "timestamp": str(int(timestamp)),
        }
        if album:
            params["album"] = album
        if duration:
            params["duration"] = str(int(duration))
        return await self._post("track.scrobble", self._signed("track.scrobble", params))

    async def _session_or_create(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=12),
            )
        return self._session

    # ── transport ─────────────────────────────────────────────────────
    async def _reserve_slot(self) -> None:
        """Claim the next allowed request time, then sleep until it arrives.

        The bookkeeping happens inside the lock but the request itself happens
        outside it, so several callers queue politely instead of serialising
        their downloads.
        """
        async with self._lock:
            now = self._clock()
            ready = max(now, self._last_call + self.MIN_INTERVAL)
            self._last_call = ready
        delay = ready - now
        if delay > 0:
            await asyncio.sleep(delay)

    async def _request(self, method: str, params: dict) -> dict:
        """One API call with a single retry for transient failures."""
        payload = {
            "method": method,
            "api_key": self.api_key,
            "format": "json",
            **params,
        }
        last_error: Exception | None = None
        for attempt in (1, 2):
            await self._reserve_slot()
            try:
                if self._transport is not None:
                    result = await self._transport(method, params)
                else:
                    session = await self._session_or_create()
                    async with session.get(API_URL, params=payload) as response:
                        body = await response.text()
                        if response.status == 429:
                            raise LastFmError(
                                "Last.fm is rate limiting the bot.",
                                code=29,
                            )
                        if response.status >= 500:
                            raise LastFmError(
                                f"Last.fm is having trouble (HTTP {response.status})."
                            )
                        try:
                            import json

                            result = json.loads(body or "{}")
                        except ValueError:
                            raise LastFmError("Last.fm sent a response the bot could not read.")
                return self._check(result)
            except LastFmError as exc:
                last_error = exc
                # Any answer Last.fm itself gave (a bad key, an expired token, an
                # unknown user, a rate limit) is final: retrying it only wastes
                # the member's time and hides the real error code.
                if exc.code is not None:
                    raise
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # network, DNS, timeout
                last_error = exc
                logging.warning("Last.fm", f"{method} failed: {exc}")
            if attempt == 1:
                await asyncio.sleep(0.8)
        raise LastFmError(
            f"Last.fm did not answer ({last_error})." if last_error else "Last.fm did not answer."
        )

    @staticmethod
    def _check(payload: Any) -> dict:
        if not isinstance(payload, dict):
            raise LastFmError("Last.fm sent a response the bot could not read.")
        error = payload.get("error")
        if error:
            try:
                code = int(error)
            except (TypeError, ValueError):
                code = None
            raise LastFmError(str(payload.get("message") or "Last.fm rejected the request."), code=code)
        return payload

    async def _call(
        self,
        method: str,
        *,
        ttl: float | None = None,
        **params,
    ) -> dict:
        """A cached API call. Params are ordered into the cache key."""
        if not self.has_key:
            raise LastFmError(
                "Last.fm is not configured on this bot (missing LASTFM_API_KEY)."
            )
        key = (method, tuple(sorted((k, str(v)) for k, v in params.items() if v is not None)))
        now = self._clock()
        cached = self._cache.get(key)
        if cached is not None and cached[0] > now:
            return cached[1]

        payload = await self._request(method, {k: v for k, v in params.items() if v is not None})
        if len(self._cache) >= _MAX_CACHE:
            # Drop expired entries first, then the one closest to expiry.
            for stale in [k for k, (expiry, _) in self._cache.items() if expiry <= now]:
                self._cache.pop(stale, None)
            if len(self._cache) >= _MAX_CACHE:
                self._cache.pop(min(self._cache, key=lambda k: self._cache[k][0]), None)
        self._cache[key] = (now + (self._cache_ttl if ttl is None else ttl), payload)
        return payload

    # ── user ──────────────────────────────────────────────────────────
    async def user_info(self, username: str) -> dict:
        """A linked account's headline numbers."""
        payload = await self._call("user.getinfo", user=_canonical(username))
        user = payload.get("user") or {}
        if not user:
            raise LastFmError("That Last.fm account could not be read.", code=6)
        registered_field = user.get("registered")
        registered = _int(
            registered_field.get("unixtime")
            if isinstance(registered_field, dict)
            else registered_field
        )
        return {
            "username": _text(user.get("name")) or _canonical(username),
            "real_name": _text(user.get("realname")),
            "url": _text(user.get("url")),
            "image": image_url(user.get("image")),
            "playcount": _int(user.get("playcount")),
            "artist_count": _int(user.get("artist_count")),
            "album_count": _int(user.get("album_count")),
            "track_count": _int(user.get("track_count")),
            "registered": registered or None,
            "country": _text(user.get("country")),
        }

    async def recent_tracks(self, username: str, limit: int = 10) -> dict:
        """The now-playing track (if any) plus the latest scrobbles."""
        payload = await self._call(
            "user.getrecenttracks",
            user=_canonical(username),
            limit=max(1, min(int(limit), 50)),
            extended=1,
            ttl=20.0,
        )
        container = payload.get("recenttracks") or {}
        tracks: list[dict] = []
        now_playing: dict | None = None
        for entry in _items(container, "track"):
            artist = entry.get("artist")
            if isinstance(artist, dict):
                artist_name = _text(artist.get("#text")) or _text(artist.get("name"))
            else:
                artist_name = _text(artist)
            item = {
                "title": _text(entry.get("name")),
                "artist": artist_name,
                "album": _text(entry.get("album")),
                "image": image_url(entry.get("image")),
                "url": _text(entry.get("url")),
                "now_playing": str((entry.get("@attr") or {}).get("nowplaying") or "").lower()
                == "true",
                "played_at": _int((entry.get("date") or {}).get("uts"))
                if isinstance(entry.get("date"), dict)
                else 0,
            }
            if item["now_playing"] and now_playing is None:
                now_playing = item
            else:
                tracks.append(item)
        # ``total`` lives on the wrapper's ``@attr`` map, not on the wrapper.
        attr = container.get("@attr") if isinstance(container.get("@attr"), dict) else {}
        return {
            "now_playing": now_playing,
            "tracks": tracks,
            "total": _int(attr.get("total")),
        }

    async def _top(
        self,
        method: str,
        key: str,
        singular: str,
        username: str,
        period: str,
        limit: int,
        page: int = 1,
    ) -> list[dict]:
        payload = await self._call(
            method,
            user=_canonical(username),
            period=period,
            limit=max(1, min(int(limit), 100)),
            page=max(1, int(page)),
        )
        container = payload.get(key) or {}
        rows: list[dict] = []
        for index, entry in enumerate(_items(container, singular), start=1 + (page - 1) * limit):
            artist = entry.get("artist")
            if isinstance(artist, dict):
                artist_name = _text(artist.get("name")) or _text(artist.get("#text"))
            else:
                artist_name = _text(artist)
            attr = entry.get("@attr")
            rank = _int(attr.get("rank")) if isinstance(attr, dict) else 0
            rows.append({
                "rank": rank or index,
                "name": _text(entry.get("name")),
                "artist": artist_name,
                "playcount": _playcount(entry.get("playcount")),
                "image": image_url(entry.get("image")),
                "url": _text(entry.get("url")),
            })
        return rows

    async def top_artists(self, username: str, *, period: str = "overall", limit: int = 10, page: int = 1) -> list[dict]:
        return await self._top(
            "user.gettopartists", "topartists", "artist", username, period, limit, page
        )

    async def top_albums(self, username: str, *, period: str = "overall", limit: int = 10, page: int = 1) -> list[dict]:
        return await self._top(
            "user.gettopalbums", "topalbums", "album", username, period, limit, page
        )

    async def top_tracks(self, username: str, *, period: str = "overall", limit: int = 10, page: int = 1) -> list[dict]:
        return await self._top(
            "user.gettoptracks", "toptracks", "track", username, period, limit, page
        )

    async def loved_tracks(self, username: str, *, limit: int = 10) -> list[dict]:
        payload = await self._call(
            "user.getlovedtracks",
            user=_canonical(username),
            limit=max(1, min(int(limit), 50)),
        )
        container = payload.get("lovedtracks") or {}
        rows: list[dict] = []
        for entry in _items(container, "track"):
            artist = entry.get("artist")
            artist_name = _text(artist.get("name")) if isinstance(artist, dict) else _text(artist)
            rows.append({
                "title": _text(entry.get("name")),
                "artist": artist_name,
                "url": _text(entry.get("url")),
                "image": image_url(entry.get("image")),
                "loved_at": _int((entry.get("date") or {}).get("uts"))
                if isinstance(entry.get("date"), dict)
                else 0,
            })
        return rows

    # ── artists and albums ────────────────────────────────────────────
    async def artist_info(self, artist: str, username: str | None = None) -> dict:
        """One artist, with the member's own playcount when *username* is given."""
        payload = await self._call(
            "artist.getinfo",
            artist=str(artist or "").strip(),
            username=_canonical(username) or None,
            autocorrect=1,
            ttl=900.0 if not username else 300.0,
        )
        info = payload.get("artist") or {}
        if not info:
            raise LastFmError("That artist could not be found on Last.fm.", code=6)
        stats = info.get("stats") or {}
        tags = info.get("tags") or {}
        tag_rows = tags.get("tag") if isinstance(tags, dict) else None
        if isinstance(tag_rows, dict):
            tag_rows = [tag_rows]
        return {
            "name": _text(info.get("name")),
            "url": _text(info.get("url")),
            "image": image_url(info.get("image")),
            "playcount": _int(stats.get("playcount")),
            "listeners": _int(stats.get("listeners")),
            "user_playcount": _int(info.get("userplaycount")) if username else None,
            "tags": [(_text(tag.get("name")) if isinstance(tag, dict) else _text(tag)) for tag in (tag_rows or [])][:5],
            "summary": _text(info.get("bio", {}).get("summary")).split("<a")[0].strip()
            if isinstance(info.get("bio"), dict)
            else "",
        }

    async def album_info(self, artist: str, album: str, username: str | None = None) -> dict:
        payload = await self._call(
            "album.getinfo",
            artist=str(artist or "").strip(),
            album=str(album or "").strip(),
            username=_canonical(username) or None,
            autocorrect=1,
            ttl=900.0 if not username else 300.0,
        )
        info = payload.get("album") or {}
        if not info:
            raise LastFmError("That album could not be found on Last.fm.", code=6)
        artist_field = info.get("artist")
        artist_name = _text(artist_field) if not isinstance(artist_field, dict) else _text(artist_field.get("name"))
        tracks = _items(info.get("tracks"), "track")
        return {
            "name": _text(info.get("name")),
            "artist": artist_name,
            "url": _text(info.get("url")),
            "image": image_url(info.get("image")),
            "playcount": _int(info.get("playcount")),
            "listeners": _int(info.get("listeners")),
            "user_playcount": _int(info.get("userplaycount")) if username else None,
            "track_count": len(tracks),
        }

    async def search_artists(self, query: str, *, limit: int = 6) -> list[dict]:
        """Artist name suggestions for a query that did not resolve exactly."""
        payload = await self._call(
            "artist.search",
            artist=str(query or "").strip(),
            limit=max(1, min(int(limit), 30)),
            ttl=900.0,
        )
        results = payload.get("results") or {}
        rows = []
        for entry in _items(results.get("artistmatches"), "artist"):
            rows.append({
                "name": _text(entry.get("name")),
                "listeners": _int(entry.get("listeners")),
                "image": image_url(entry.get("image")),
                "url": _text(entry.get("url")),
            })
        return rows
