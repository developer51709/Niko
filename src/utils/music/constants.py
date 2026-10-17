"""
Music System — shared constants.
Kept separate from the cog so the music utilities stay importable without
loading any Discord cog code.
"""

import discord

# ──────────────────────────────────────────────────
#  TIMING / SIZE CONSTANTS
# ──────────────────────────────────────────────────

IDLE_TIMEOUT      = 300       # seconds before auto-disconnect on empty queue
HISTORY_LEN       = 10        # tracks kept in per-guild history deque
MAX_QUEUE_SHOW    = 10        # tracks shown in .queue list
GHOST_QUEUE_LEN   = 5         # autoplay suggestions pre-resolved per guild (ghost queue)
_MAX_CONNECT_NODES = 3        # Lavalink nodes to keep in the pool (load-balanced + failover)

_PROBE_TIMEOUT    = 3.0       # node health probe timeout (seconds)
_CONNECT_TIMEOUT  = 20.0      # wavelink Pool.connect timeout (seconds)
_MAX_PROBERS      = 8         # concurrent node probes at startup

SOURCE_COLOURS = {
    "youtube":    discord.Colour(0xFF0000),
    "soundcloud": discord.Colour(0xFF5500),
    "spotify":    discord.Colour(0x1DB954),
    "default":    discord.Colour(0x5865F2),
}

_LASTFM_URL = "https://ws.audioscrobbler.com/2.0/"