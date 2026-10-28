"""Spotify URL resolution — no network, just payload handling.

Spotify moved playlist contents from ``/playlists/{id}/tracks`` (removed for
Development Mode apps in February 2026) to ``/playlists/{id}/items``, renaming
the ``track`` field to ``item``. Both shapes must keep resolving, otherwise
every Spotify playlist link silently queues nothing.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils.music.spotify import SpotifyClient, _normalize_spotify_reference


def _client(payload):
    client = SpotifyClient("client-id", "client-secret")

    async def fake_get(_path):
        return payload

    client._get = fake_get  # type: ignore[assignment]
    return client


NEW_SHAPE = {
    "items": [
        {"item": {"name": "Song A", "artists": [{"name": "Artist A"}]}},
        {"item": {"name": "Song B", "artists": [{"name": "Artist B"}]}},
        {"item": None},
        {"track": {"name": "Stale Field", "artists": [{"name": "Old"}]}},
    ]
}

OLD_SHAPE = {
    "items": [
        {"track": {"name": "Song A", "artists": [{"name": "Artist A"}]}},
        {"track": None},
    ]
}


def test_playlist_items_use_the_item_field():
    assert asyncio.run(_client(NEW_SHAPE).resolve_playlist("pl")) == [
        "Artist A - Song A",
        "Artist B - Song B",
        "Old - Stale Field",
    ]


def test_playlist_legacy_track_field_still_resolves():
    assert asyncio.run(_client(OLD_SHAPE).resolve_playlist("pl")) == [
        "Artist A - Song A"
    ]


def test_missing_artist_falls_back_to_unknown():
    payload = {"items": [{"item": {"name": "No Artist"}}]}
    assert asyncio.run(_client(payload).resolve_playlist("pl")) == [
        "Unknown - No Artist"
    ]


def test_unavailable_or_empty_payload_returns_nothing():
    assert asyncio.run(_client(None).resolve_playlist("pl")) == []
    assert asyncio.run(_client({}).resolve_playlist("pl")) == []


def test_spotify_references_normalise():
    assert (
        _normalize_spotify_reference("spotify:track:4uLU6hMCjMI75M1A2tKUQC")
        == "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"
    )
    url = "https://open.spotify.com/intl-de/album/4aawyAB9vmqN3uQ7FjRGTy?si=x"
    assert _normalize_spotify_reference(url) == url
    assert _normalize_spotify_reference("https://example.com/playlist/1") is None
