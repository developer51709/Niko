"""
Music System — Last.fm autoplay helper.

Fetches "similar tracks" for a seed track via the Last.fm API. Requires
LASTFM_API_KEY (silently disabled when absent).
"""

import aiohttp

from utils.music.constants import _LASTFM_URL


async def lastfm_similar(api_key: str, artist: str, title: str) -> list[tuple[str, str]]:
    """
    Returns up to 10 (artist, title) tuples of tracks similar to the given one.
    """
    params = {
        "method":      "track.getSimilar",
        "artist":      artist,
        "track":       title,
        "api_key":     api_key,
        "format":      "json",
        "limit":       "10",
        "autocorrect": "1",
    }
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(_LASTFM_URL, params=params, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status != 200:
                    return []
                data = await r.json()
        tracks = data.get("similartracks", {}).get("track", [])
        return [(t["artist"]["name"], t["name"]) for t in tracks if isinstance(t, dict)]
    except Exception:
        return []