"""
Music System — shared utilities.

The music cog's helpers live here (outside cogs/) so they can be imported,
tested, and reused without loading any Discord command layer:
  • constants — timing / sizing constants and source colours
  • format    — duration, progress bar, source colour helpers
  • messages  — trilingual EN/DE/ES catalog (strings live in cogs/music/locales)
  • spotify   — Spotify URL/URI resolution client
  • autoplay  — Last.fm similar-track helper
  • nodes     — Lavalink node catalogue + probing
  • database  — dedicated secondary database (liked songs, playlists)
"""

from utils.music.constants import (
    GHOST_QUEUE_LEN,
    HISTORY_LEN,
    IDLE_TIMEOUT,
    MAX_QUEUE_SHOW,
    SOURCE_COLOURS,
    _CONNECT_TIMEOUT,
    _LASTFM_URL,
    _MAX_CONNECT_NODES,
    _MAX_PROBERS,
    _PROBE_TIMEOUT,
    _START_DISCOVERY_DELAY,
)
from utils.music.format import _fmt_dur, _progress_bar, _source_colour
from utils.music.messages import MESSAGES, msg
from utils.music.autoplay import clean_seed, lastfm_similar as _lastfm_similar
from utils.music.spotify import (
    _SPOTIFY_ALBUM_RE,
    _SPOTIFY_PLAYLIST_RE,
    _SPOTIFY_TRACK_RE,
    SpotifyClient as _SpotifyClient,
    _normalize_spotify_reference,
)
from utils.music.nodes import (
    _FALLBACK_NODES,
    find_responsive_nodes as _find_responsive_nodes,
    node_catalog as _node_catalog,
    node_identifier as _node_identifier,
)

__all__ = [
    "GHOST_QUEUE_LEN",
    "HISTORY_LEN",
    "IDLE_TIMEOUT",
    "MAX_QUEUE_SHOW",
    "SOURCE_COLOURS",
    "_CONNECT_TIMEOUT",
    "_LASTFM_URL",
    "_MAX_CONNECT_NODES",
    "_MAX_PROBERS",
    "_PROBE_TIMEOUT",
    "_START_DISCOVERY_DELAY",
    "_fmt_dur",
    "_progress_bar",
    "_source_colour",
    "MESSAGES",
    "msg",
    "_lastfm_similar",
    "_SPOTIFY_ALBUM_RE",
    "_SPOTIFY_PLAYLIST_RE",
    "_SPOTIFY_TRACK_RE",
    "_SpotifyClient",
    "_normalize_spotify_reference",
    "_FALLBACK_NODES",
    "_find_responsive_nodes",
    "_node_catalog",
    "_node_identifier",
]