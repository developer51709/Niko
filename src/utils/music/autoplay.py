"""
Music System — Last.fm autoplay helper.

Fetches "similar tracks" for a seed track via the Last.fm API. Requires
LASTFM_API_KEY (silently disabled when absent).

Two things this helper has to get right, because both used to make autoplay
look broken with no trace in the logs:

  • Seed cleanup. Lavalink reports YouTube metadata verbatim — author
    "Artist - Topic", title "Artist - Song (Official Video)" — and Last.fm only
    matches clean artist/track pairs. The seed is normalised before every
    lookup, with the raw pair retried as a fallback.
  • Failure visibility. Last.fm answers a rejected key with HTTP 403 and an
    error body, and rate limits the same way. Those failures are logged (once
    per distinct message, so a broken key cannot flood the log) instead of
    being indistinguishable from "this track has no similar tracks".
"""

import re

import aiohttp

from utils import logging as log
from utils.music.constants import _LASTFM_URL

_LIMIT = 10

# Upload noise YouTube wraps around the real title. Only bracketed segments made
# of these words are dropped — "(live)", "(remix)" and "(acoustic)" are part of
# the recording's identity and must survive.
_NOISE = re.compile(
    r"\b(?:official(?:\s+(?:music\s+)?video)?|official\s+audio|lyrics?|lyric\s+video|"
    r"audio|video|visuali[sz]er|hd|hq|4k|8k|remaster(?:ed)?|explicit|clean|"
    r"color\s*coded|m/v|mv)\b"
    r"|^(?:feat|ft|featuring|with)\b",
    re.IGNORECASE,
)
_BRACKETED = re.compile(r"[\(\[]\s*([^\)\]]*?)\s*[\)\]]")
_FEATURING = re.compile(r"\s+(?:feat\.?|ft\.?|featuring)\s+.*$", re.IGNORECASE)
# "Artist - Topic" / "ArtistVEVO" / "Artist Official" are upload channels, not
# artists, and Last.fm matches none of them. The lookbehind keeps a channel that
# is *just* "VEVO" from collapsing to an empty artist.
_CHANNEL_TAIL = re.compile(
    r"(?<=.)\s*[-–—]\s*topic$|(?<=.)\s*vevo$|\s+official$", re.IGNORECASE
)

# Last failure that was written to the log, so a persistent problem (bad key,
# rate limit) is reported once instead of on every track that ends.
_last_failure: str | None = None


def clean_seed(artist: str, title: str) -> tuple[str, str]:
    """Strip upload noise so Last.fm can match the seed track.

    "Rick Astley - Topic" / "Rick Astley - Never Gonna Give You Up (Official
    Video)" becomes ("Rick Astley", "Never Gonna Give You Up").
    """
    artist = (artist or "").strip()
    title = (title or "").strip()

    artist = _CHANNEL_TAIL.sub("", artist)
    artist = _FEATURING.sub("", artist)
    artist = re.sub(r"\s{2,}", " ", artist).strip(" -–—|:")

    title = _BRACKETED.sub(lambda m: "" if _NOISE.search(m.group(1)) else m.group(0), title)
    title = _FEATURING.sub("", title)
    title = re.sub(r"\s{2,}", " ", title).strip(" -–—|:")

    # YouTube titles usually repeat the artist ("Artist - Song"); Last.fm wants
    # the song alone when the artist is supplied separately.
    if artist and title.lower().startswith(artist.lower() + " - "):
        title = title[len(artist) + 3:].strip()

    return artist, title


def _report_failure(message: str) -> None:
    global _last_failure
    if message == _last_failure:
        return
    _last_failure = message
    log.warning("Autoplay", f"Last.fm request failed — {message}")


async def _fetch(params: dict) -> dict | None:
    """One Last.fm call. Returns the parsed body, or None after logging why."""
    global _last_failure
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                _LASTFM_URL, params=params, timeout=aiohttp.ClientTimeout(total=8)
            ) as response:
                if response.status != 200:
                    detail = (await response.text())[:160].replace("\n", " ")
                    _report_failure(f"HTTP {response.status}: {detail}")
                    return None
                # content_type=None: Last.fm labels JSON as text/javascript.
                data = await response.json(content_type=None)
    except Exception as exc:
        _report_failure(f"{type(exc).__name__}: {exc}")
        return None

    if not isinstance(data, dict):
        _report_failure("unexpected response body")
        return None
    if data.get("error"):
        _report_failure(f"error {data['error']}: {data.get('message', '')}".strip())
        return None

    _last_failure = None
    return data


def _pairs(data: dict) -> list[tuple[str, str]]:
    """Pull (artist, title) pairs out of a ``track.getSimilar`` response."""
    tracks = (data.get("similartracks") or {}).get("track") or []
    if isinstance(tracks, dict):
        # Last.fm collapses one-element arrays into a bare object.
        tracks = [tracks]

    pairs: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in tracks:
        if not isinstance(item, dict):
            continue
        artist = item.get("artist")
        artist = (artist.get("name") if isinstance(artist, dict) else artist) or ""
        name = item.get("name") or ""
        artist, name = str(artist).strip(), str(name).strip()
        if not artist or not name or (artist.lower(), name.lower()) in seen:
            continue
        seen.add((artist.lower(), name.lower()))
        pairs.append((artist, name))
        if len(pairs) >= _LIMIT:
            break
    return pairs


async def _get_similar(api_key: str, artist: str, title: str) -> list[tuple[str, str]] | None:
    """Look up similars for one artist/track pair.

    Returns None when the request itself failed, so the caller can stop instead
    of burning another call against the same broken key.
    """
    data = await _fetch({
        "method":      "track.getSimilar",
        "artist":      artist,
        "track":       title,
        "api_key":     api_key,
        "format":      "json",
        "limit":       str(_LIMIT),
        "autocorrect": "1",
    })
    return None if data is None else _pairs(data)


async def lastfm_similar(api_key: str, artist: str, title: str) -> list[tuple[str, str]]:
    """
    Returns up to 10 (artist, title) tuples of tracks similar to the given one.
    """
    raw = ((artist or "").strip(), (title or "").strip())
    for seed in dict.fromkeys((clean_seed(artist, title), raw)):
        if not seed[0] or not seed[1]:
            continue
        pairs = await _get_similar(api_key, *seed)
        if pairs is None:
            return []          # credential / transport failure — retrying won't help
        if pairs:
            return pairs
    return []
