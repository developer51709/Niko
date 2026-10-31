"""Spotify URL resolution — no network, just payload handling.

Two lookup methods exist because Spotify's 2026 API no longer lets a
client-credentials token read a public playlist: the Web API is used when
credentials are configured (tracks and albums still resolve there), and the
public embed page's ``__NEXT_DATA__`` payload is the fallback that keeps
playlist links working at all.

Spotify also moved playlist contents from ``/playlists/{id}/tracks`` to
``/playlists/{id}/items``, renaming the ``track`` field to ``item``; both API
shapes must keep resolving.
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import utils.music.spotify as spotify
from utils.music.spotify import SpotifyClient, _normalize_spotify_reference


def _client(payload, *, credentials=True):
    client = SpotifyClient("client-id", "client-secret") if credentials else SpotifyClient()

    async def fake_get(_path):
        return payload

    async def no_embed(_kind, _spotify_id):
        raise AssertionError("embed page must not be fetched when the API answers")

    client._get = fake_get  # type: ignore[assignment]
    spotify._fetch_embed_html = no_embed  # type: ignore[assignment]
    return client


def _embed_html(entity):
    """Minimal embed document carrying the ``__NEXT_DATA__`` payload."""
    payload = {"props": {"pageProps": {"state": {"data": {"entity": entity}}}}}
    return (
        "<html><body><script id=\"__NEXT_DATA__\" type=\"application/json\">"
        + json.dumps(payload)
        + "</script></body></html>"
    )


def _embed_client(html, *, credentials=False):
    client = SpotifyClient("client-id", "client-secret") if credentials else SpotifyClient()

    async def fake_get(_path):
        return None  # API refuses (403 / omitted items)

    async def fake_embed(_kind, _spotify_id):
        return html

    client._get = fake_get  # type: ignore[assignment]
    spotify._fetch_embed_html = fake_embed  # type: ignore[assignment]
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

TRACK_ENTITY = {
    "type": "track",
    "uri": "spotify:track:4cOdK2wGLETKBW3PvgPWqT",
    "name": "Never Gonna Give You Up",
    "title": "Never Gonna Give You Up",
    "artists": [{"name": "Rick Astley", "uri": "spotify:artist:0gxyHStUsqpMadRV0Di1Qt"}],
}

PLAYLIST_ENTITY = {
    "type": "playlist",
    "name": "Today's Top Hits",
    "subtitle": "Spotify",
    "trackList": [
        {"uri": "spotify:track:1", "title": "Loser", "subtitle": "Tame Impala", "entityType": "track"},
        {"uri": "spotify:track:2", "title": "Housewife", "subtitle": "Tate McRae", "entityType": "track"},
        # Podcast episodes are queued by neither method.
        {"uri": "spotify:episode:3", "title": "Episode", "subtitle": "Show", "entityType": "episode"},
        {"uri": "spotify:track:4", "title": "", "subtitle": "Nobody", "entityType": "track"},
    ],
}

ALBUM_ENTITY = {
    "type": "album",
    "name": "OK Computer",
    "subtitle": "Radiohead",
    "trackList": [
        {"uri": "spotify:track:1", "title": "Airbag", "subtitle": "Radiohead", "entityType": "track"},
        {"uri": "spotify:track:2", "title": "Paranoid Android", "subtitle": "Radiohead", "entityType": "track"},
    ],
}


# ── Web API path ─────────────────────────────────────────────────────────

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


def test_album_tracks_resolve_from_the_api():
    payload = {"items": [{"name": "Airbag", "artists": [{"name": "Radiohead"}]}]}
    assert asyncio.run(_client(payload).resolve_album("al")) == ["Radiohead - Airbag"]


def test_track_resolves_from_the_api():
    payload = {"name": "Creep", "artists": [{"name": "Radiohead"}]}
    assert asyncio.run(_client(payload).resolve_track("tr")) == "Radiohead - Creep"


# ── Embed fallback (no credentials, or the API refuses) ──────────────────

def test_a_refused_api_call_falls_back_to_the_embed_page():
    client = _embed_client(_embed_html(PLAYLIST_ENTITY), credentials=True)
    assert asyncio.run(client.resolve_playlist("pl")) == [
        "Tame Impala - Loser",
        "Tate McRae - Housewife",
    ]


def test_a_playlist_without_credentials_resolves_from_the_embed_page():
    client = _embed_client(_embed_html(PLAYLIST_ENTITY))
    assert asyncio.run(client.resolve_playlist("pl")) == [
        "Tame Impala - Loser",
        "Tate McRae - Housewife",
    ]


def test_an_album_without_credentials_resolves_from_the_embed_page():
    client = _embed_client(_embed_html(ALBUM_ENTITY))
    assert asyncio.run(client.resolve_album("al")) == [
        "Radiohead - Airbag",
        "Radiohead - Paranoid Android",
    ]


def test_a_single_track_resolves_from_the_embed_page():
    client = _embed_client(_embed_html(TRACK_ENTITY))
    assert asyncio.run(client.resolve_track("tr")) == "Rick Astley - Never Gonna Give You Up"


def test_a_track_without_artists_still_queues():
    entity = {"type": "track", "name": "Untitled", "artists": []}
    client = _embed_client(_embed_html(entity))
    assert asyncio.run(client.resolve_track("tr")) == "Unknown - Untitled"


def test_an_unreadable_embed_page_returns_nothing():
    for html in ("<html></html>", None, "<script id=\"__NEXT_DATA__\">{not json</script>"):
        client = _embed_client(html)
        assert asyncio.run(client.resolve_track("tr")) is None
        assert asyncio.run(client.resolve_playlist("pl")) == []


def test_an_album_page_never_falls_back_to_the_album_title():
    """An album link must not queue the album name as if it were a song."""
    entity = {"type": "album", "name": "OK Computer", "subtitle": "Radiohead", "trackList": []}
    client = _embed_client(_embed_html(entity))
    assert asyncio.run(client.resolve_album("al")) == []


def test_empty_or_missing_api_payload_still_falls_back():
    client = _embed_client(_embed_html(PLAYLIST_ENTITY), credentials=True)
    assert asyncio.run(client.resolve_playlist("pl")) == [
        "Tame Impala - Loser",
        "Tate McRae - Housewife",
    ]


# ── Credentials ──────────────────────────────────────────────────────────

def test_a_blocked_api_is_skipped_instead_of_retried_for_every_link():
    """Once the API refuses, links go straight to the embed page."""
    client = _embed_client(_embed_html(TRACK_ENTITY), credentials=True)
    client._api_down_until = float("inf")

    async def must_not_call(_path):
        raise AssertionError("a blocked API must not be called again")

    client._get = must_not_call  # type: ignore[assignment]
    assert asyncio.run(client.resolve_track("tr")) == "Rick Astley - Never Gonna Give You Up"


def test_credentials_are_trimmed_and_optional():
    assert SpotifyClient(" id ", " secret ").has_credentials
    assert not SpotifyClient().has_credentials
    assert not SpotifyClient("id", "  ").has_credentials


def test_spotify_references_normalise():
    assert (
        _normalize_spotify_reference("spotify:track:4uLU6hMCjMI75M1A2tKUQC")
        == "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"
    )
    url = "https://open.spotify.com/intl-de/album/4aawyAB9vmqN3uQ7FjRGTy?si=x"
    assert _normalize_spotify_reference(url) == url
    assert _normalize_spotify_reference("https://example.com/playlist/1") is None
