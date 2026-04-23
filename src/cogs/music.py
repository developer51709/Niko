"""
Music System — Niko's Cozy Café Jukebox
────────────────────────────────────────
Premium feature set:
  • cv2 Now-Playing cards with album artwork + 3-row control panel
      Row 1: Prev · Pause/Resume · Skip · Stop
      Row 2: Loop (cycle) · Shuffle · Vol − · Vol +
      Row 3: Queue (ephemeral paginated) · Autoplay · Open Track (link)
  • Live progress bar — background task refreshes the NP card every 10s
  • Three-state loop (off / track / queue) using wavelink QueueMode natively
  • Premium queue management: shuffle, move, remove, jump, clearqueue, history
  • Spotipy-powered Spotify URL support (track / album / playlist) — runs sync
    API in a thread executor so the event loop never blocks. Resolves up to
    100 tracks per album/playlist via paginated requests.
      Requires: SPOTIFY_CLIENT_ID + SPOTIFY_CLIENT_SECRET (silently disabled
      when absent)
  • Last.fm autoplay fallback when the queue runs dry
      Requires: LASTFM_API_KEY (silently disabled when absent)
  • Multi-source: YouTube (default), SoundCloud (sc:), direct URLs
  • Personality-aware text (normal / café modes, EN / DE)
"""

import asyncio
import os
import re
import time as _time
from collections import deque
from typing import Optional

import aiohttp
import discord
import wavelink
from discord import MediaGalleryItem, UnfurledMediaItem
from discord.ext import commands

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    _SPOTIPY_AVAILABLE = True
except Exception:
    _SPOTIPY_AVAILABLE = False

from config.emojis import get_emoji
from utils import logging as log
from utils.ai_config import get_personality
from utils.paginator import PaginatedView, paginate

# ──────────────────────────────────────────────────
#  CONSTANTS
# ──────────────────────────────────────────────────

IDLE_TIMEOUT     = 300     # seconds before auto-disconnect on empty queue
HISTORY_LEN      = 25      # tracks kept in per-guild history deque
QUEUE_PAGE_SIZE  = 10      # tracks per page in .queue
MAX_SPOTIFY_LOAD = 100     # tracks resolved from a single album/playlist
NP_REFRESH_SECS  = 10      # how often to refresh the NP card progress bar

SOURCE_COLOURS = {
    "youtube":    discord.Colour(0xFF0000),
    "soundcloud": discord.Colour(0xFF5500),
    "spotify":    discord.Colour(0x1DB954),
    "default":    discord.Colour(0x5865F2),
}

_LOOP_LABELS = {
    wavelink.QueueMode.normal:   "Loop",
    wavelink.QueueMode.loop:     "Loop: Track",
    wavelink.QueueMode.loop_all: "Loop: Queue",
}
_LOOP_NEXT = {
    wavelink.QueueMode.normal:   wavelink.QueueMode.loop,
    wavelink.QueueMode.loop:     wavelink.QueueMode.loop_all,
    wavelink.QueueMode.loop_all: wavelink.QueueMode.normal,
}

_SPOTIFY_TRACK_RE    = re.compile(r"open\.spotify\.com/(?:[a-z]{2}(?:-[A-Z]{2})?/)?track/([A-Za-z0-9]+)")
_SPOTIFY_ALBUM_RE    = re.compile(r"open\.spotify\.com/(?:[a-z]{2}(?:-[A-Z]{2})?/)?album/([A-Za-z0-9]+)")
_SPOTIFY_PLAYLIST_RE = re.compile(r"open\.spotify\.com/(?:[a-z]{2}(?:-[A-Z]{2})?/)?playlist/([A-Za-z0-9]+)")

# ──────────────────────────────────────────────────
#  PERSONALITY MESSAGES
# ──────────────────────────────────────────────────

MESSAGES = {
    "normal": {
        "en": {
            "not_in_voice":               "You need to be in a voice channel first.",
            "get_player_not_in_voice":    "You need to be in a voice channel to use music commands.",
            "music_player_status_title":  "Music Player Status",
            "music_not_connected":        "Not connected to any music servers.",
            "music_connected":            "Connected to a music server and ready.",
            "play_not_found":             "I couldn't find that track.",
            "pause_nothing":              "There is nothing playing right now.",
            "pause_ok":                   "Paused.",
            "resume_nothing":             "There is nothing to resume.",
            "resume_ok":                  "Resumed.",
            "skip_nothing":               "There is nothing to skip.",
            "skip_ok":                    "Skipped.",
            "stop_nothing":               "There is nothing to stop.",
            "stop_ok":                    "Stopped playback and cleared the queue.",
            "queue_empty":                "The queue is currently empty.",
            "queue_header":               "**Current Queue:**",
            "volume_nothing":             "There is no active player.",
            "volume_set":                 "Volume set to **{vol}%**.",
            "disconnect_nothing":         "I am not connected to a voice channel.",
            "disconnect_ok":              "Disconnected from the voice channel.",
            "autoplay_on":                "Autoplay enabled — I'll queue similar tracks automatically.",
            "autoplay_off":               "Autoplay disabled.",
            "autoplay_unavailable":       "Autoplay is not configured (no Last.fm API key).",
            "loop_on":                    "Loop enabled — repeating the current track.",
            "loop_off":                   "Loop disabled.",
            "loop_track":                 "Looping the current track.",
            "loop_queue":                 "Looping the entire queue.",
            "shuffle_ok":                 "Queue shuffled.",
            "shuffle_nothing":            "Nothing in the queue to shuffle.",
            "clear_ok":                   "Removed **{n}** track(s) from the queue.",
            "clear_nothing":              "The queue is already empty.",
            "remove_ok":                  "Removed **{title}** from the queue.",
            "remove_oob":                 "That position is out of range.",
            "move_ok":                    "Moved **{title}** to position **{to}**.",
            "move_oob":                   "Both positions must be within the queue.",
            "jump_ok":                    "Jumped to **{title}**.",
            "jump_oob":                   "That position is out of range.",
            "history_empty":              "No tracks have been played yet.",
            "history_title":              "Recently Played",
            "queue_title":                "Queue",
            "added_one":                  "Added **{title}** to the queue.",
            "added_many":                 "Added **{n}** tracks to the queue.",
            "spotify_disabled":           "Spotify support is not configured.",
            "spotify_resolving":          "Resolving Spotify link…",
            "spotify_fail":               "Couldn't resolve that Spotify link.",
        },
        "de": {
            "not_in_voice":               "Du musst zuerst einem Sprachkanal beitreten.",
            "get_player_not_in_voice":    "Du musst in einem Sprachkanal sein, um Musikbefehle zu nutzen.",
            "music_player_status_title":  "Musik-Player-Status",
            "music_not_connected":        "Mit keinem Musikserver verbunden.",
            "music_connected":            "Mit einem Musikserver verbunden und bereit.",
            "play_not_found":             "Ich konnte diesen Track nicht finden.",
            "pause_nothing":              "Es läuft gerade nichts.",
            "pause_ok":                   "Pausiert.",
            "resume_nothing":             "Es gibt nichts zum Fortsetzen.",
            "resume_ok":                  "Fortgesetzt.",
            "skip_nothing":               "Es gibt nichts zum Überspringen.",
            "skip_ok":                    "Übersprungen.",
            "stop_nothing":               "Es gibt nichts zu stoppen.",
            "stop_ok":                    "Wiedergabe gestoppt und Warteschlange geleert.",
            "queue_empty":                "Die Warteschlange ist derzeit leer.",
            "queue_header":               "**Aktuelle Warteschlange:**",
            "volume_nothing":             "Es gibt keinen aktiven Player.",
            "volume_set":                 "Lautstärke auf **{vol}%** gesetzt.",
            "disconnect_nothing":         "Ich bin mit keinem Sprachkanal verbunden.",
            "disconnect_ok":              "Vom Sprachkanal getrennt.",
            "autoplay_on":                "Autoplay aktiviert — ich füge automatisch ähnliche Tracks hinzu.",
            "autoplay_off":               "Autoplay deaktiviert.",
            "autoplay_unavailable":       "Autoplay ist nicht konfiguriert (kein Last.fm-API-Schlüssel).",
            "loop_on":                    "Loop aktiviert — der aktuelle Track wird wiederholt.",
            "loop_off":                   "Loop deaktiviert.",
            "loop_track":                 "Aktuellen Track in Schleife.",
            "loop_queue":                 "Gesamte Warteschlange in Schleife.",
            "shuffle_ok":                 "Warteschlange gemischt.",
            "shuffle_nothing":            "Nichts in der Warteschlange zum Mischen.",
            "clear_ok":                   "**{n}** Track(s) aus der Warteschlange entfernt.",
            "clear_nothing":              "Die Warteschlange ist bereits leer.",
            "remove_ok":                  "**{title}** aus der Warteschlange entfernt.",
            "remove_oob":                 "Diese Position ist außerhalb des Bereichs.",
            "move_ok":                    "**{title}** zu Position **{to}** verschoben.",
            "move_oob":                   "Beide Positionen müssen innerhalb der Warteschlange liegen.",
            "jump_ok":                    "Gesprungen zu **{title}**.",
            "jump_oob":                   "Diese Position ist außerhalb des Bereichs.",
            "history_empty":              "Es wurden noch keine Tracks gespielt.",
            "history_title":              "Zuletzt Gespielt",
            "queue_title":                "Warteschlange",
            "added_one":                  "**{title}** zur Warteschlange hinzugefügt.",
            "added_many":                 "**{n}** Tracks zur Warteschlange hinzugefügt.",
            "spotify_disabled":           "Spotify-Unterstützung ist nicht konfiguriert.",
            "spotify_resolving":          "Spotify-Link wird aufgelöst…",
            "spotify_fail":               "Der Spotify-Link konnte nicht aufgelöst werden.",
        },
    },
    "cafe": {
        "en": {
            "not_in_voice":               "hey bestie, you gotta hop into a voice channel first ☕💿",
            "get_player_not_in_voice":    "you're not in a voice channel yet, i can't serve music there 😭☕",
            "music_player_status_title":  "Café Music Player ☕",
            "music_not_connected":        "hmm… not connected to any music servers, like a café with no music 😭",
            "music_connected":            "yesss, connected and ready to pour some cozy tracks ☕✨",
            "play_not_found":             "i couldn't find that song, like a drink that's not on the menu 😭",
            "pause_nothing":              "there's nothing playing to pause, just quiet café air rn 😭",
            "pause_ok":                   "pausing the vibes for a moment 🌿☕",
            "resume_nothing":             "there's nothing paused to resume 😭",
            "resume_ok":                  "bringing the warm café vibes back on 🎶☕",
            "skip_nothing":               "skip what… the silence? the playlist is empty 😭",
            "skip_ok":                    "skipping to the next flavor on the menu 🍰✨",
            "stop_nothing":               "nothing to stop, the speakers are already quiet 🌙",
            "stop_ok":                    "okay okay, stopping everything and clearing the tray ☕💛",
            "queue_empty":                "the queue is emptier than a café at closing time 😭",
            "queue_header":               "☕ **current cozy queue:**",
            "volume_nothing":             "no active player, no music brewing yet 😭",
            "volume_set":                 "volume set to **{vol}%** — adjusting the café ambiance ✨",
            "disconnect_nothing":         "i'm not even in a voice channel rn 😭",
            "disconnect_ok":              "leaving like a soft barista wave, see you soon ☕🌿",
            "autoplay_on":                "autoplay is on! i'll keep the vibes going with similar tracks 🎶✨",
            "autoplay_off":               "autoplay off — queue it yourself, bestie 🍵",
            "autoplay_unavailable":       "autoplay isn't set up (no Last.fm key) 😭",
            "loop_on":                    "looping this track on repeat like a cozy café playlist 🔁☕",
            "loop_off":                   "loop off, moving on to the next track 🍵",
            "loop_track":                 "this track is on repeat now ☕🔂",
            "loop_queue":                 "looping the whole queue like a cozy café playlist 🔁☕",
            "shuffle_ok":                 "shuffled the queue like a fresh deck of menu cards ✨",
            "shuffle_nothing":            "nothing in the queue to shuffle 😭",
            "clear_ok":                   "wiped **{n}** track(s) off the queue ☕",
            "clear_nothing":              "the queue is already empty, bestie 🌙",
            "remove_ok":                  "took **{title}** off the menu ☕",
            "remove_oob":                 "that spot doesn't exist in the queue 😭",
            "move_ok":                    "moved **{title}** to spot **{to}** ✨",
            "move_oob":                   "those spots are out of range 😭",
            "jump_ok":                    "jumped straight to **{title}** ☕✨",
            "jump_oob":                   "that spot doesn't exist 😭",
            "history_empty":              "no tracks brewed yet today 🌿",
            "history_title":              "Recently Brewed ☕",
            "queue_title":                "Cozy Queue ☕",
            "added_one":                  "added **{title}** to the queue ☕✨",
            "added_many":                 "added **{n}** tracks to the queue ☕✨",
            "spotify_disabled":           "spotify support isn't set up right now 😭",
            "spotify_resolving":          "brewing that spotify link… ☕",
            "spotify_fail":               "couldn't resolve that spotify link 😭",
        },
        "de": {
            "not_in_voice":               "hey liebchen, du musst erst in einen Sprachkanal gehen ☕💿",
            "get_player_not_in_voice":    "du bist noch in keinem Sprachkanal, ich kann dort keine musik servieren 😭☕",
            "music_player_status_title":  "Café-Musik-Player ☕",
            "music_not_connected":        "hmm… mit keinem musikserver verbunden, wie ein café ohne musik 😭",
            "music_connected":            "yesss, verbunden und bereit für cozy tracks ☕✨",
            "play_not_found":             "ich konnte den song nicht finden, wie ein drink der nicht auf der karte steht 😭",
            "pause_nothing":              "es läuft nichts zum pausieren 😭",
            "pause_ok":                   "pausiere kurz die vibes 🌿☕",
            "resume_nothing":             "es gibt nichts fortzusetzen 😭",
            "resume_ok":                  "die warmen café-vibes laufen wieder 🎶☕",
            "skip_nothing":               "was soll ich skippen… die stille? 😭",
            "skip_ok":                    "zum nächsten track auf der karte 🍰✨",
            "stop_nothing":               "nichts zu stoppen, die lautsprecher sind schon ruhig 🌙",
            "stop_ok":                    "okay, stoppe alles und leere die warteschlange ☕💛",
            "queue_empty":                "die warteschlange ist leerer als ein café nach feierabend 😭",
            "queue_header":               "☕ **aktuelle cozy-warteschlange:**",
            "volume_nothing":             "kein aktiver player 😭",
            "volume_set":                 "lautstärke auf **{vol}%** — café-stimmung angepasst ✨",
            "disconnect_nothing":         "ich bin gar nicht im sprachkanal 😭",
            "disconnect_ok":              "ich verlasse den vc wie ein leiser barista-wink ☕🌿",
            "autoplay_on":                "autoplay an! ich halte die vibes mit ähnlichen tracks am laufen 🎶✨",
            "autoplay_off":               "autoplay aus — füg selbst hinzu, liebchen 🍵",
            "autoplay_unavailable":       "autoplay ist nicht eingerichtet (kein Last.fm-Schlüssel) 😭",
            "loop_on":                    "dieser track läuft auf repeat wie eine cozy café-playlist 🔁☕",
            "loop_off":                   "loop aus, weiter zum nächsten track 🍵",
            "loop_track":                 "dieser track läuft jetzt in dauerschleife ☕🔂",
            "loop_queue":                 "die ganze warteschlange läuft in schleife wie eine cozy café-playlist 🔁☕",
            "shuffle_ok":                 "warteschlange neu gemischt wie ein frischer kartendeck ✨",
            "shuffle_nothing":            "nichts in der warteschlange zum mischen 😭",
            "clear_ok":                   "**{n}** track(s) von der warteschlange weggewischt ☕",
            "clear_nothing":              "die warteschlange ist schon leer, liebchen 🌙",
            "remove_ok":                  "**{title}** von der karte genommen ☕",
            "remove_oob":                 "diesen platz gibt's in der warteschlange nicht 😭",
            "move_ok":                    "**{title}** zu platz **{to}** verschoben ✨",
            "move_oob":                   "diese plätze sind außerhalb des bereichs 😭",
            "jump_ok":                    "direkt zu **{title}** gesprungen ☕✨",
            "jump_oob":                   "diesen platz gibt's nicht 😭",
            "history_empty":              "heute noch keine tracks gebrüht 🌿",
            "history_title":              "Zuletzt Gebrüht ☕",
            "queue_title":                "Cozy Warteschlange ☕",
            "added_one":                  "**{title}** zur warteschlange hinzugefügt ☕✨",
            "added_many":                 "**{n}** tracks zur warteschlange hinzugefügt ☕✨",
            "spotify_disabled":           "spotify-unterstützung ist nicht eingerichtet 😭",
            "spotify_resolving":          "löse den spotify-link auf… ☕",
            "spotify_fail":               "spotify-link konnte nicht aufgelöst werden 😭",
        },
    },
}


def get_lang(ctx: commands.Context) -> str:
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
    return "en"


def msg(ctx: commands.Context, key: str, **kwargs) -> str:
    personality = get_personality(ctx)
    lang        = get_lang(ctx)
    base        = MESSAGES.get(personality, {})
    text        = base.get(lang, {}).get(key)
    if text is None:
        text = base.get("en", {}).get(key)
    if text is None:
        text = MESSAGES["normal"].get(lang, {}).get(key)
    if text is None:
        text = MESSAGES["normal"]["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text


# ──────────────────────────────────────────────────
#  UTILITY — duration + progress bar
# ──────────────────────────────────────────────────

def _fmt_dur(ms: int) -> str:
    if ms is None or ms < 0:
        return "0:00"
    s = ms // 1000
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _progress_bar(pos_ms: int, total_ms: int, width: int = 14) -> str:
    pct    = min(pos_ms / max(total_ms, 1), 1.0)
    filled = round(pct * width)
    bar    = "█" * filled + "░" * (width - filled)
    return f"`[{bar}]` {_fmt_dur(pos_ms)} / {_fmt_dur(total_ms)}"


def _source_colour(track: wavelink.Playable) -> discord.Colour:
    src = (track.source or "").lower()
    if "youtube" in src:
        return SOURCE_COLOURS["youtube"]
    if "soundcloud" in src:
        return SOURCE_COLOURS["soundcloud"]
    return SOURCE_COLOURS["default"]


# ──────────────────────────────────────────────────
#  SPOTIFY CLIENT
# ──────────────────────────────────────────────────

class _SpotifyClient:
    """
    Spotipy-backed Spotify resolver.
    Sync API calls are pushed to a thread executor so the event loop never
    blocks. Resolves up to MAX_SPOTIFY_LOAD tracks per album/playlist via
    paginated requests (50 per page).
    """

    def __init__(self, client_id: str, client_secret: str):
        auth_mgr = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret,
        )
        # requests_timeout to avoid hanging the executor thread forever
        self._sp = spotipy.Spotify(auth_manager=auth_mgr, requests_timeout=10, retries=2)

    async def _run(self, fn, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: fn(*args, **kwargs))

    async def resolve_track(self, track_id: str) -> Optional[str]:
        try:
            data = await self._run(self._sp.track, track_id)
        except Exception as e:
            log.warning("Spotify", f"track lookup failed: {e}")
            return None
        if not data:
            return None
        artist = data["artists"][0]["name"] if data.get("artists") else "Unknown"
        return f"{artist} - {data['name']}"

    async def resolve_album(self, album_id: str) -> list[str]:
        queries: list[str] = []
        try:
            offset = 0
            while len(queries) < MAX_SPOTIFY_LOAD:
                data = await self._run(
                    self._sp.album_tracks, album_id, limit=50, offset=offset
                )
                if not data:
                    break
                items = data.get("items", [])
                if not items:
                    break
                for item in items:
                    if not item:
                        continue
                    artist = item["artists"][0]["name"] if item.get("artists") else "Unknown"
                    queries.append(f"{artist} - {item['name']}")
                if len(items) < 50:
                    break
                offset += 50
        except Exception as e:
            log.warning("Spotify", f"album lookup failed: {e}")
        return queries[:MAX_SPOTIFY_LOAD]

    async def resolve_playlist(self, playlist_id: str) -> list[str]:
        queries: list[str] = []
        try:
            offset = 0
            while len(queries) < MAX_SPOTIFY_LOAD:
                data = await self._run(
                    self._sp.playlist_items,
                    playlist_id,
                    limit=50,
                    offset=offset,
                    additional_types=("track",),
                )
                if not data:
                    break
                items = data.get("items", [])
                if not items:
                    break
                for item in items:
                    track = item.get("track") if item else None
                    if not track:
                        continue
                    artist = track["artists"][0]["name"] if track.get("artists") else "Unknown"
                    queries.append(f"{artist} - {track['name']}")
                if len(items) < 50:
                    break
                offset += 50
        except Exception as e:
            log.warning("Spotify", f"playlist lookup failed: {e}")
        return queries[:MAX_SPOTIFY_LOAD]


# ──────────────────────────────────────────────────
#  LAST.FM AUTOPLAY
# ──────────────────────────────────────────────────

_LASTFM_URL = "https://ws.audioscrobbler.com/2.0/"


async def _lastfm_similar(api_key: str, artist: str, title: str) -> list[tuple[str, str]]:
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


# ──────────────────────────────────────────────────
#  LAVALINK NODE DISCOVERY
# ──────────────────────────────────────────────────

_AJIE_ALL        = "https://lavalink-list.ajieblogs.eu.org/All"
_PROBE_TIMEOUT   = 3.0
_CONNECT_TIMEOUT = 20.0
_MAX_PROBERS     = 8


async def _fetch_node_list() -> list[dict]:
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(_AJIE_ALL, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return []
                data = await r.json(content_type=None)
                return [n for n in data if n.get("version", "v4") == "v4"]
    except Exception:
        return []


async def _probe_node(
    session: aiohttp.ClientSession,
    node: dict,
    sem: asyncio.Semaphore,
) -> tuple[dict, float] | None:
    host   = node["host"]
    port   = node["port"]
    scheme = "https" if node.get("secure") else "http"
    url    = f"{scheme}://{host}:{port}/version"
    async with sem:
        try:
            t0 = _time.monotonic()
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=_PROBE_TIMEOUT), ssl=False) as r:
                if r.status == 200:
                    return (node, (_time.monotonic() - t0) * 1000)
        except Exception:
            pass
    return None


async def _find_responsive_nodes(nodes: list[dict]) -> list[dict]:
    sem = asyncio.Semaphore(_MAX_PROBERS)
    async with aiohttp.ClientSession() as s:
        results = await asyncio.gather(
            *[_probe_node(s, n, sem) for n in nodes],
            return_exceptions=True,
        )
    alive = [r for r in results if r and not isinstance(r, BaseException)]
    alive.sort(key=lambda x: x[1])
    if alive:
        summary = ", ".join(f"{n['host']}:{n['port']} ({lat:.0f}ms)" for n, lat in alive[:4])
        log.info("Lavalink", f"{len(alive)}/{len(nodes)} nodes responsive — {summary}")
    else:
        log.warning("Lavalink", f"No nodes responded out of {len(nodes)} tried.")
    return [n for n, _ in alive]


# ──────────────────────────────────────────────────
#  CONTROL PANEL — cv2 Button classes
# ──────────────────────────────────────────────────

class _PauseResumeBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild_id: int, paused: bool):
        super().__init__(
            label="Resume" if paused else "Pause",
            style=discord.ButtonStyle.success if paused else discord.ButtonStyle.secondary,
            emoji=get_emoji("icon_play") if paused else get_emoji("icon_pause"),
        )
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if player:
            await player.pause(not player.paused)
        await self.cog._update_np_message(interaction.guild)


class _SkipBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild_id: int):
        super().__init__(label="Skip", style=discord.ButtonStyle.primary, emoji=get_emoji('icon_skip'))
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if player and player.playing:
            await player.skip(force=True)
        await self.cog._update_np_message(interaction.guild)


class _StopBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild_id: int):
        super().__init__(label="Stop", style=discord.ButtonStyle.danger, emoji=get_emoji("icon_stop"))
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if player:
            try:
                player.queue.mode = wavelink.QueueMode.normal
            except Exception:
                pass
            player.queue.clear()
            await player.stop()
        await self.cog._update_np_message(interaction.guild)


class _PrevBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild_id: int, enabled: bool):
        super().__init__(
            label="Prev",
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("icon_rewind"),
            disabled=not enabled,
        )
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        state = self.cog._state(self.guild_id)
        history: deque = state["history"]
        if not player or not history:
            return
        prev_track = history.pop()
        # Put current back at front of queue so it plays after prev_track ends
        if player.current:
            try:
                player.queue.put_at(0, player.current)
            except Exception:
                player.queue.put(player.current)
        # Mark this as a loop-style replay so on_track_end skips history-push
        state["_skip_history_once"] = True
        await player.play(prev_track)
        await self.cog._update_np_message(interaction.guild)


class _LoopBtn(discord.ui.Button):
    """Three-state loop cycle: normal → loop (track) → loop_all (queue) → normal."""

    def __init__(self, cog: "MusicSystem", guild_id: int, mode: wavelink.QueueMode):
        label = _LOOP_LABELS.get(mode, "Loop")
        style = (
            discord.ButtonStyle.secondary
            if mode == wavelink.QueueMode.normal
            else discord.ButtonStyle.success
        )
        super().__init__(label=label, style=style, emoji=get_emoji("icon_loop"))
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if player:
            current_mode = player.queue.mode
            player.queue.mode = _LOOP_NEXT.get(current_mode, wavelink.QueueMode.normal)
        await self.cog._update_np_message(interaction.guild)


class _ShuffleBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild_id: int, enabled: bool):
        super().__init__(
            label="Shuffle",
            style=discord.ButtonStyle.secondary,
            emoji="🔀",
            disabled=not enabled,
        )
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if player and not player.queue.is_empty:
            try:
                player.queue.shuffle()
            except Exception:
                pass
        await self.cog._update_np_message(interaction.guild)


class _QueueBtn(discord.ui.Button):
    """Opens the current queue as an ephemeral paginated view."""

    def __init__(self, cog: "MusicSystem", guild_id: int, enabled: bool):
        super().__init__(
            label="Queue",
            style=discord.ButtonStyle.secondary,
            emoji="📜",
            disabled=not enabled,
        )
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        player: wavelink.Player = interaction.guild.voice_client
        if not player or player.queue.is_empty:
            return await interaction.response.send_message(
                "The queue is currently empty.", ephemeral=True
            )
        lines = []
        for i, track in enumerate(player.queue, start=1):
            dur = _fmt_dur(track.length) if track.length else "?"
            lines.append(f"`{i:>2}.` **{track.title[:60]}** — {(track.author or 'Unknown')[:30]} `[{dur}]`")
        pages = paginate(lines, per_page=QUEUE_PAGE_SIZE)
        view  = PaginatedView(title=f"Queue · {len(player.queue)} track(s)", pages=pages)
        await interaction.response.send_message(view=view, ephemeral=True)


class _AutoplayBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild_id: int, autoplay: bool, available: bool):
        if not available:
            super().__init__(
                label="Autoplay",
                style=discord.ButtonStyle.secondary,
                emoji="📻",
                disabled=True,
            )
        else:
            super().__init__(
                label="Autoplay On" if autoplay else "Autoplay",
                style=discord.ButtonStyle.success if autoplay else discord.ButtonStyle.secondary,
                emoji="📻",
            )
        self.cog      = cog
        self.guild_id = guild_id
        self.available = available

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not self.available:
            return
        state = self.cog._state(self.guild_id)
        state["autoplay"] = not state["autoplay"]
        await self.cog._update_np_message(interaction.guild)


class _VolDownBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild_id: int):
        super().__init__(label="Vol -", style=discord.ButtonStyle.secondary, emoji="🔉")
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if player:
            new_vol = max(0, player.volume - 10)
            await player.set_volume(new_vol)
        await self.cog._update_np_message(interaction.guild)


class _VolUpBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild_id: int):
        super().__init__(label="Vol +", style=discord.ButtonStyle.secondary, emoji="🔊")
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if player:
            new_vol = min(100, player.volume + 10)
            await player.set_volume(new_vol)
        await self.cog._update_np_message(interaction.guild)


# ──────────────────────────────────────────────────
#  NOW-PLAYING CARD BUILDER
# ──────────────────────────────────────────────────

def _build_np_view(
    player:   wavelink.Player,
    guild:    discord.Guild,
    cog:      "MusicSystem",
    is_playing: bool = True,
) -> discord.ui.LayoutView:
    state   = cog._state(guild.id)
    track   = player.current if player else None
    autoplay = state.get("autoplay", False)
    history: deque = state.get("history", deque())
    vol     = player.volume if player else 100
    queue_filled = bool(player and not player.queue.is_empty)
    loop_mode = player.queue.mode if player else wavelink.QueueMode.normal

    if not track or not is_playing:
        # Idle / stopped card
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_stop')} Nothing Playing"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=f"-# Use `.play <song>` to queue something up."),
            accent_colour=discord.Colour(0x5865F2),
        ))
        return view

    # Track meta
    source       = (track.source or "").lower()
    accent_color = _source_colour(track)
    author_name  = track.author or "Unknown Artist"
    duration     = _progress_bar(player.position or 0, track.length or 0)
    uri          = track.uri or ""

    # Source badge
    if "youtube" in source:
        src_badge = f"{get_emoji('youtube')} YouTube"
    elif "soundcloud" in source:
        src_badge = f"{get_emoji('soundcloud')} SoundCloud"
    elif "spotify" in source:
        src_badge = f"{get_emoji('spotify')} Spotify"
    else:
        src_badge = "🎵 Music"

    status_icon = get_emoji("icon_pause") if player.paused else get_emoji("icon_play")

    # Footer status line
    foot_bits = [src_badge, f"Vol {vol}%"]
    if loop_mode == wavelink.QueueMode.loop:
        foot_bits.append(f"{get_emoji('icon_loop')} Track")
    elif loop_mode == wavelink.QueueMode.loop_all:
        foot_bits.append(f"{get_emoji('icon_loop')} Queue")
    if autoplay:
        foot_bits.append("📻 Autoplay")
    if queue_filled:
        foot_bits.append(f"📜 {len(player.queue)} queued")

    body = (
        f"### {status_icon} Now Playing\n"
        f"**{track.title}**\n"
        f"by {author_name}\n\n"
        f"{duration}\n\n"
        f"-# {' · '.join(foot_bits)}"
    )

    # Build container items
    items: list = [discord.ui.TextDisplay(content=body)]

    # Artwork thumbnail (if available)
    if track.artwork:
        items.insert(0, discord.ui.MediaGallery(
            MediaGalleryItem(media=UnfurledMediaItem(url=track.artwork))
        ))
        items.insert(1, discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))

    # Build link button row (only if track URL is present)
    link_row_items = []
    if uri:
        link_row_items.append(
            discord.ui.Button(label="Open Track", style=discord.ButtonStyle.link, url=uri)
        )

    items += [
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        # Row 1 — playback transport
        discord.ui.ActionRow(
            _PrevBtn(cog, guild.id, enabled=bool(history)),
            _PauseResumeBtn(cog, guild.id, paused=player.paused),
            _SkipBtn(cog, guild.id),
            _StopBtn(cog, guild.id),
        ),
        # Row 2 — loop / shuffle / volume
        discord.ui.ActionRow(
            _LoopBtn(cog, guild.id, mode=loop_mode),
            _ShuffleBtn(cog, guild.id, enabled=queue_filled),
            _VolDownBtn(cog, guild.id),
            _VolUpBtn(cog, guild.id),
        ),
        # Row 3 — queue / autoplay / link
        discord.ui.ActionRow(
            _QueueBtn(cog, guild.id, enabled=queue_filled),
            _AutoplayBtn(cog, guild.id, autoplay=autoplay, available=bool(cog._lastfm_key)),
            *link_row_items,
        ),
    ]

    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(*items, accent_colour=accent_color))
    return view


# ──────────────────────────────────────────────────
#  MUSIC COG
# ──────────────────────────────────────────────────

class MusicSystem(commands.Cog):
    """Music system — artwork cards, control panel, multi-source, autoplay."""

    def __init__(self, bot: commands.Bot):
        self.bot        = bot
        self.connected  = False
        self._connecting = False

        # { guild_id: { loop, autoplay, history, np_message, last_track } }
        self._guild_states: dict[int, dict] = {}

        # Optional integrations — silently disabled if env vars are absent
        sp_id     = os.environ.get("SPOTIFY_CLIENT_ID")
        sp_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        self._spotify: _SpotifyClient | None = (
            _SpotifyClient(sp_id, sp_secret) if sp_id and sp_secret else None
        )
        if self._spotify:
            log.debug("Music", "Spotify URL support enabled.")

        self._lastfm_key: str | None = os.environ.get("LASTFM_API_KEY")
        if self._lastfm_key:
            log.debug("Music", "Last.fm autoplay enabled.")

        bot.loop.create_task(self.startup_connect())

    def _state(self, guild_id: int) -> dict:
        if guild_id not in self._guild_states:
            self._guild_states[guild_id] = {
                "autoplay":           False,
                "history":            deque(maxlen=HISTORY_LEN),
                "np_message":         None,
                "last_track":         None,
                "np_task":            None,
                "_skip_history_once": False,
            }
        return self._guild_states[guild_id]

    # ─── NP MESSAGE UPDATE ────────────────────────

    async def _update_np_message(self, guild: discord.Guild):
        state   = self._state(guild.id)
        message: Optional[discord.Message] = state.get("np_message")
        if not message:
            return
        player: wavelink.Player = guild.voice_client
        if not player:
            return
        view = _build_np_view(player, guild, self, is_playing=player.playing or player.paused)
        try:
            await message.edit(view=view)
        except discord.NotFound:
            state["np_message"] = None
        except Exception:
            pass

    async def _send_np(self, ctx: commands.Context, player: wavelink.Player):
        """Send (or replace) the now-playing control panel + start refresh task."""
        state  = self._state(ctx.guild.id)
        old_msg: Optional[discord.Message] = state.get("np_message")

        view = _build_np_view(player, ctx.guild, self)
        new_msg = await ctx.send(view=view)
        state["np_message"] = new_msg

        # Replace the previous control panel quietly
        if old_msg:
            try:
                await old_msg.delete()
            except Exception:
                pass

        # (Re)start the live progress-bar refresh task
        self._start_np_refresh(ctx.guild)

    def _start_np_refresh(self, guild: discord.Guild):
        """Spawn a per-guild background task that re-renders the NP card every NP_REFRESH_SECS."""
        state = self._state(guild.id)
        old_task: Optional[asyncio.Task] = state.get("np_task")
        if old_task and not old_task.done():
            old_task.cancel()
        state["np_task"] = self.bot.loop.create_task(self._np_refresh_loop(guild))

    async def _np_refresh_loop(self, guild: discord.Guild):
        try:
            while True:
                await asyncio.sleep(NP_REFRESH_SECS)
                state = self._state(guild.id)
                if not state.get("np_message"):
                    return
                player: wavelink.Player = guild.voice_client
                if not player or (not player.playing and not player.paused):
                    return
                # Only refresh when actively playing (skip on pause to save edits)
                if player.paused:
                    continue
                await self._update_np_message(guild)
        except asyncio.CancelledError:
            return
        except Exception as e:
            log.debug("Music", f"NP refresh loop ended: {e}")

    # ─── LAVALINK CONNECTION ──────────────────────

    async def startup_connect(self, *, retry_delay: float = 0):
        if self._connecting:
            return
        self._connecting = True
        if retry_delay:
            await asyncio.sleep(retry_delay)
        await self.bot.wait_until_ready()

        raw_nodes = await _fetch_node_list()
        if not raw_nodes:
            log.warning("Lavalink", "Could not fetch node list.")
            self._connecting = False
            return

        responsive = await _find_responsive_nodes(raw_nodes)
        if not responsive:
            log.warning("Lavalink", "No responsive nodes found. Music unavailable.")
            self._connecting = False
            return

        for node_info in responsive:
            host     = node_info["host"]
            port     = node_info["port"]
            password = node_info["password"]
            secure   = node_info.get("secure", False)
            uri      = f"{'https' if secure else 'http'}://{host}:{port}"
            try:
                node = wavelink.Node(uri=uri, password=password)
                await asyncio.wait_for(
                    wavelink.Pool.connect(nodes=[node], client=self.bot),
                    timeout=_CONNECT_TIMEOUT,
                )
                log.info("Lavalink", f"Connected to {host}:{port} (SSL={secure})")
                self.connected   = True
                self._connecting = False
                return
            except Exception:
                try:
                    await wavelink.Pool.close()
                except Exception:
                    pass

        log.warning("Lavalink", "All responsive nodes failed the wavelink handshake.")
        self._connecting = False

    # ─── WAVELINK EVENTS ──────────────────────────

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        log.info("Lavalink", f"Node '{payload.node.identifier}' ready (resumed={payload.resumed})")

    @commands.Cog.listener()
    async def on_wavelink_node_closed(self, node: wavelink.Node, disconnected: list):
        log.warning("Lavalink", f"Node '{node.identifier}' closed. Reconnecting in 10s…")
        self.connected = False
        self.bot.loop.create_task(self.startup_connect(retry_delay=10))

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload):
        # Refresh NP card so it switches to the new track immediately
        player = payload.player
        if player and player.guild:
            await self._update_np_message(player.guild)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        """
        With `player.autoplay = AutoPlayMode.partial`, wavelink advances the queue
        natively — we never call player.play() from here (gap-free playback).
        Our job: track history + top up via Last.fm before the queue dries.
        """
        player = payload.player
        if player is None:
            return

        guild_id = player.guild.id
        state    = self._state(guild_id)
        loop_mode = player.queue.mode

        # Push to history (skip on loop replays + Prev-button replays)
        if payload.track and loop_mode == wavelink.QueueMode.normal:
            if state.pop("_skip_history_once", False):
                pass  # consumed the skip flag — don't push
            else:
                state["history"].append(payload.track)
                state["last_track"] = payload.track

        # Top up via Last.fm autoplay BEFORE wavelink hits an empty queue
        if (
            state.get("autoplay")
            and self._lastfm_key
            and payload.track
            and loop_mode == wavelink.QueueMode.normal
            and len(player.queue) < 1
        ):
            await self._topup_autoplay(player, payload.track, count=5)

        # Idle grace period: if nothing left, schedule a disconnect check
        if loop_mode == wavelink.QueueMode.normal and player.queue.is_empty:
            await asyncio.sleep(IDLE_TIMEOUT)
            if player and not player.playing and player.queue.is_empty:
                try:
                    await player.disconnect()
                except Exception:
                    pass
                # Cancel NP refresh task
                task = state.get("np_task")
                if task and not task.done():
                    task.cancel()
                state["np_message"] = None
                state["np_task"]    = None

    async def _topup_autoplay(self, player: wavelink.Player, seed_track, count: int = 5):
        """Add up to `count` Last.fm-similar tracks to the queue."""
        if not self._lastfm_key:
            return
        artist = seed_track.author or ""
        title  = seed_track.title  or ""
        similars = await _lastfm_similar(self._lastfm_key, artist, title)
        added = 0
        for sim_artist, sim_title in similars:
            if added >= count:
                break
            try:
                results = await wavelink.Playable.search(f"ytsearch:{sim_artist} - {sim_title}")
            except Exception:
                continue
            if not results:
                continue
            track = results[0] if isinstance(results, list) else results
            try:
                player.queue.put(track)
                added += 1
            except Exception:
                continue
        if added:
            log.debug("Music", f"Autoplay topped up queue with {added} similar tracks")

    # ─── SOURCE RESOLUTION ────────────────────────

    async def _resolve_query(self, query: str) -> list[str] | None:
        """
        Returns a list of wavelink-ready search strings.
        Handles Spotify URLs (single track → 1 item; album/playlist → multiple).
        Returns None on unrecoverable failure.
        """
        q = query.strip()

        # ── Spotify ───────────────────────────────
        if "open.spotify.com" in q:
            if not self._spotify:
                return None

            m_track = _SPOTIFY_TRACK_RE.search(q)
            if m_track:
                search = await self._spotify.resolve_track(m_track.group(1))
                return [f"ytsearch:{search}"] if search else None

            m_album = _SPOTIFY_ALBUM_RE.search(q)
            if m_album:
                queries = await self._spotify.resolve_album(m_album.group(1))
                return [f"ytsearch:{s}" for s in queries] if queries else None

            m_playlist = _SPOTIFY_PLAYLIST_RE.search(q)
            if m_playlist:
                queries = await self._spotify.resolve_playlist(m_playlist.group(1))
                return [f"ytsearch:{s}" for s in queries] if queries else None

            return None

        # ── SoundCloud prefix ─────────────────────
        if q.lower().startswith("sc:"):
            return [f"scsearch:{q[3:].strip()}"]

        # ── YouTube prefix ────────────────────────
        if q.lower().startswith("yt:"):
            return [f"ytsearch:{q[3:].strip()}"]

        # ── Raw URL (YouTube, SoundCloud, etc.) ───
        if q.startswith("http://") or q.startswith("https://"):
            return [q]

        # ── Default: YouTube text search ──────────
        return [f"ytsearch:{q}"]

    # ─── PLAYER HELPER ────────────────────────────

    async def get_player(self, ctx: commands.Context) -> wavelink.Player | None:
        if not ctx.author.voice:
            await ctx.send(msg(ctx, "get_player_not_in_voice"))
            return None
        channel = ctx.author.voice.channel
        player  = ctx.voice_client
        if player is None:
            player = await channel.connect(cls=wavelink.Player)
        return player

    # ─── COMMANDS ─────────────────────────────────

    @commands.command(
        name="play", aliases=["p"],
        help="{ 'en': 'play a song or queue it up ☕🎶', 'de': 'spiele einen track ab' }"
    )
    async def play(self, ctx: commands.Context, *, search: str):
        player = await self.get_player(ctx)
        if not player:
            return

        # Enable native gap-free queue advancement
        try:
            player.autoplay = wavelink.AutoPlayMode.partial
        except Exception:
            pass

        # Spotify URL feedback before long resolution
        is_spotify = "open.spotify.com" in search
        if is_spotify and not self._spotify:
            return await ctx.send(msg(ctx, "spotify_disabled"))

        status_msg = None
        if is_spotify:
            resolving = discord.ui.LayoutView()
            resolving.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### ☕ {msg(ctx, 'spotify_resolving')}"),
                accent_colour=SOURCE_COLOURS["spotify"],
            ))
            status_msg = await ctx.send(view=resolving)

        # Resolve to wavelink search strings
        searches = await self._resolve_query(search)

        if status_msg:
            try:
                await status_msg.delete()
            except Exception:
                pass

        if not searches:
            return await ctx.send(msg(ctx, "play_not_found" if not is_spotify else "spotify_fail"))

        # Resolve every search string to a wavelink Playable
        added_tracks = []
        for query in searches:
            try:
                results = await wavelink.Playable.search(query)
            except Exception:
                continue
            if not results:
                continue
            track = results[0] if isinstance(results, list) else results
            added_tracks.append(track)

        if not added_tracks:
            return await ctx.send(msg(ctx, "play_not_found"))

        # Was the player idle before we added anything?
        was_idle = not player.playing and not player.paused

        # Push everything to the queue
        for t in added_tracks:
            try:
                await player.queue.put_wait(t)
            except Exception:
                player.queue.put(t)

        # Kick off playback if idle (wavelink will handle subsequent tracks)
        first_track = added_tracks[0]
        if was_idle and not player.playing:
            try:
                next_track = player.queue.get()
                await player.play(next_track)
            except Exception as e:
                log.warning("Music", f"Failed to start playback: {e}")

        # Feedback
        if len(added_tracks) == 1:
            if not was_idle:
                await ctx.send(msg(ctx, "added_one", title=first_track.title))
        else:
            await ctx.send(msg(ctx, "added_many", n=len(added_tracks)))

        # Send NP control panel only when we actually started playback now
        if was_idle:
            await self._send_np(ctx, player)

    @commands.command(
        name="pause",
        help="{ 'en': 'pause the current track 🌿', 'de': 'pausiert den aktuellen track' }"
    )
    async def pause(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or not player.playing:
            return await ctx.send(msg(ctx, "pause_nothing"))
        await player.pause(True)
        await ctx.send(msg(ctx, "pause_ok"))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="resume",
        help="{ 'en': 'resume the paused track ☕🎶', 'de': 'setzt den pausierten track fort' }"
    )
    async def resume(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "resume_nothing"))
        await player.pause(False)
        await ctx.send(msg(ctx, "resume_ok"))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="skip", aliases=["sk"],
        help="{ 'en': 'skip to the next track 🍰', 'de': 'springt zum nächsten track' }"
    )
    async def skip(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or not player.playing:
            return await ctx.send(msg(ctx, "skip_nothing"))
        await player.skip(force=True)
        await ctx.send(msg(ctx, "skip_ok"))

    @commands.command(
        name="stop",
        help="{ 'en': 'stop and clear the queue ☕', 'de': 'stoppt die wiedergabe' }"
    )
    async def stop(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "stop_nothing"))
        try:
            player.queue.mode = wavelink.QueueMode.normal
        except Exception:
            pass
        player.queue.clear()
        await player.stop()
        await ctx.send(msg(ctx, "stop_ok"))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="loop", aliases=["repeat"],
        help="{ 'en': 'cycle loop mode: off → track → queue → off 🔁', 'de': 'wechselt den loop-modus' }"
    )
    async def loop(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "stop_nothing"))
        new_mode = _LOOP_NEXT.get(player.queue.mode, wavelink.QueueMode.normal)
        player.queue.mode = new_mode
        if new_mode == wavelink.QueueMode.loop:
            await ctx.send(msg(ctx, "loop_track"))
        elif new_mode == wavelink.QueueMode.loop_all:
            await ctx.send(msg(ctx, "loop_queue"))
        else:
            await ctx.send(msg(ctx, "loop_off"))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="loopqueue", aliases=["lq"],
        help="{ 'en': 'toggle loop for the entire queue 🔁☕', 'de': 'wiederholt die gesamte warteschlange' }"
    )
    async def loopqueue(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "stop_nothing"))
        if player.queue.mode == wavelink.QueueMode.loop_all:
            player.queue.mode = wavelink.QueueMode.normal
            await ctx.send(msg(ctx, "loop_off"))
        else:
            player.queue.mode = wavelink.QueueMode.loop_all
            await ctx.send(msg(ctx, "loop_queue"))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="shuffle", aliases=["sh"],
        help="{ 'en': 'shuffle the queue 🔀☕', 'de': 'mischt die warteschlange' }"
    )
    async def shuffle(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(msg(ctx, "shuffle_nothing"))
        try:
            player.queue.shuffle()
        except Exception:
            return await ctx.send(msg(ctx, "shuffle_nothing"))
        await ctx.send(msg(ctx, "shuffle_ok"))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="clearqueue", aliases=["cq", "qclear"],
        help="{ 'en': 'clear the upcoming queue ☕', 'de': 'leert die warteschlange' }"
    )
    async def clearqueue(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(msg(ctx, "clear_nothing"))
        n = len(player.queue)
        player.queue.clear()
        await ctx.send(msg(ctx, "clear_ok", n=n))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="remove", aliases=["rm"],
        help="{ 'en': 'remove a track from the queue by position', 'de': 'entfernt einen track aus der warteschlange' }"
    )
    async def remove(self, ctx: commands.Context, position: int):
        player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(msg(ctx, "remove_oob"))
        if position < 1 or position > len(player.queue):
            return await ctx.send(msg(ctx, "remove_oob"))
        try:
            track = player.queue.get_at(position - 1)
        except Exception:
            return await ctx.send(msg(ctx, "remove_oob"))
        await ctx.send(msg(ctx, "remove_ok", title=track.title))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="move", aliases=["mv"],
        help="{ 'en': 'move a track from one queue position to another', 'de': 'verschiebt einen track' }"
    )
    async def move(self, ctx: commands.Context, frm: int, to: int):
        player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(msg(ctx, "move_oob"))
        size = len(player.queue)
        if frm < 1 or frm > size or to < 1 or to > size:
            return await ctx.send(msg(ctx, "move_oob"))
        try:
            track = player.queue.get_at(frm - 1)
            player.queue.put_at(to - 1, track)
        except Exception:
            return await ctx.send(msg(ctx, "move_oob"))
        await ctx.send(msg(ctx, "move_ok", title=track.title, to=to))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="jump", aliases=["skipto"],
        help="{ 'en': 'jump to a specific position in the queue', 'de': 'springt zu einer queue-position' }"
    )
    async def jump(self, ctx: commands.Context, position: int):
        player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(msg(ctx, "jump_oob"))
        if position < 1 or position > len(player.queue):
            return await ctx.send(msg(ctx, "jump_oob"))
        # Remove every track ahead of `position` so the next skip lands on it
        try:
            for _ in range(position - 1):
                player.queue.get_at(0)
            target = player.queue.get_at(0)
            await player.play(target)
        except Exception:
            return await ctx.send(msg(ctx, "jump_oob"))
        await ctx.send(msg(ctx, "jump_ok", title=target.title))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="history", aliases=["hist"],
        help="{ 'en': 'show recently played tracks ☕📜', 'de': 'zeigt zuletzt gespielte tracks' }"
    )
    async def history(self, ctx: commands.Context):
        state = self._state(ctx.guild.id)
        history: deque = state.get("history", deque())
        if not history:
            return await ctx.send(msg(ctx, "history_empty"))
        # Reverse so most recent comes first
        lines = []
        for i, track in enumerate(reversed(list(history)), start=1):
            dur = _fmt_dur(track.length) if track.length else "?"
            lines.append(f"`{i:>2}.` **{track.title[:60]}** — {(track.author or 'Unknown')[:30]} `[{dur}]`")
        pages = paginate(lines, per_page=QUEUE_PAGE_SIZE)
        view  = PaginatedView(title=msg(ctx, "history_title"), pages=pages)
        await ctx.send(view=view)

    @commands.command(
        name="autoplay", aliases=["ap"],
        help="{ 'en': 'toggle Last.fm autoplay 📻', 'de': 'schaltet Last.fm-Autoplay um' }"
    )
    async def autoplay(self, ctx: commands.Context):
        if not self._lastfm_key:
            return await ctx.send(msg(ctx, "autoplay_unavailable"))
        state = self._state(ctx.guild.id)
        state["autoplay"] = not state["autoplay"]
        key = "autoplay_on" if state["autoplay"] else "autoplay_off"
        await ctx.send(msg(ctx, key))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="queue", aliases=["q"],
        help="{ 'en': 'show the current queue ☕📜', 'de': 'zeigt die warteschlange' }"
    )
    async def queue(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(msg(ctx, "queue_empty"))

        lines = []
        if player.current:
            lines.append(f"▶︎ **{player.current.title[:60]}** — {(player.current.author or 'Unknown')[:30]}")
            lines.append("")
        for i, track in enumerate(player.queue, start=1):
            dur = _fmt_dur(track.length) if track.length else "?"
            lines.append(f"`{i:>2}.` **{track.title[:60]}** — {(track.author or 'Unknown')[:30]} `[{dur}]`")

        pages = paginate(lines, per_page=QUEUE_PAGE_SIZE)
        view  = PaginatedView(
            title=f"{msg(ctx, 'queue_title')} · {len(player.queue)} track(s)",
            pages=pages,
        )
        await ctx.send(view=view)

    @commands.command(
        name="nowplaying", aliases=["np"],
        help="{ 'en': 'see whats brewing right now ☕🎵', 'de': 'zeigt den aktuellen track' }"
    )
    async def nowplaying(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or (not player.playing and not player.paused):
            return await ctx.send(msg(ctx, "pause_nothing"))
        await self._send_np(ctx, player)

    @commands.command(
        name="volume", aliases=["vol"],
        help="{ 'en': 'set the playback volume ✨', 'de': 'passt die lautstärke an' }"
    )
    async def volume(self, ctx: commands.Context, vol: int):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "volume_nothing"))
        vol = max(0, min(vol, 100))
        await player.set_volume(vol)
        await ctx.send(msg(ctx, "volume_set", vol=vol))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="disconnect", aliases=["dc", "leave"],
        help="{ 'en': 'have niko leave the voice channel ☕', 'de': 'trennt niko vom sprachkanal' }"
    )
    async def disconnect(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "disconnect_nothing"))
        state = self._state(ctx.guild.id)
        # Cancel NP refresh task
        task = state.get("np_task")
        if task and not task.done():
            task.cancel()
        state["np_message"] = None
        state["np_task"]    = None
        await player.disconnect()
        await ctx.send(msg(ctx, "disconnect_ok"))

    @commands.command(
        name="musicstatus",
        help="{ 'en': 'check if niko is connected to a music server ☕', 'de': 'prüfe ob niko verbunden ist' }"
    )
    async def music_status(self, ctx: commands.Context):
        sp_line = ""
        if self._spotify:
            sp_line = "\n-# 🎧 Spotify URL support enabled"
        if self._lastfm_key:
            sp_line += "\n-# 📻 Last.fm autoplay available"

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {msg(ctx, 'music_player_status_title')}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    msg(ctx, "music_connected" if self.connected else "music_not_connected")
                    + sp_line
                    + f"\n-# {get_emoji('wavelink')} Powered by Wavelink"
                )
            ),
            accent_colour=discord.Colour(0x57F287) if self.connected else discord.Colour(0xED4245),
        )
        view.add_item(container)
        await ctx.send(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(MusicSystem(bot))
