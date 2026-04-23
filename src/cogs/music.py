"""
Music System — Niko's Cozy Café Jukebox
────────────────────────────────────────
Premium feature set:
  • Gap-free playback via wavelink AutoPlayMode.partial (queue auto-advances
    natively — no manual track switching = no audio gaps on commands)
  • Three-state loop: off → track → queue (uses wavelink QueueMode natively)
  • Spotipy-powered Spotify URL support (track / album / playlist) — far more
    reliable than the previous raw-OAuth client. Runs in a thread executor so
    the event loop never blocks. Silently disabled when SPOTIFY_CLIENT_ID /
    SPOTIFY_CLIENT_SECRET are absent.
  • Last.fm autoplay fallback when the user-built queue runs dry
  • Premium queue management: shuffle, move, remove, jump, clear, history
  • Now-playing card with album art + 12-button control panel
      Row 1: Prev · Pause/Resume · Skip · Stop
      Row 2: Loop (cycle) · Shuffle · Vol − · Vol +
      Row 3: Queue (ephemeral paginated) · Autoplay · Open Track (link)
  • Paginated queue command (10 / page) using shared cv2 PaginatedView
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

IDLE_TIMEOUT     = 300       # seconds before auto-disconnect on empty queue
HISTORY_LEN      = 25        # tracks kept in per-guild history deque
QUEUE_PAGE_SIZE  = 10        # tracks shown per page in .queue
MAX_SPOTIFY_LOAD = 100       # tracks resolved from a single Spotify album/playlist

SOURCE_COLOURS = {
    "youtube":    discord.Colour(0xFF0000),
    "soundcloud": discord.Colour(0xFF5500),
    "spotify":    discord.Colour(0x1DB954),
    "default":    discord.Colour(0x5865F2),
}

_SPOTIFY_TRACK_RE    = re.compile(r"open\.spotify\.com/(?:[a-z]{2}(?:-[A-Z]{2})?/)?track/([A-Za-z0-9]+)")
_SPOTIFY_ALBUM_RE    = re.compile(r"open\.spotify\.com/(?:[a-z]{2}(?:-[A-Z]{2})?/)?album/([A-Za-z0-9]+)")
_SPOTIFY_PLAYLIST_RE = re.compile(r"open\.spotify\.com/(?:[a-z]{2}(?:-[A-Z]{2})?/)?playlist/([A-Za-z0-9]+)")

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
            "queue_title":                "Queue",
            "shuffle_ok":                 "Queue shuffled.",
            "shuffle_nothing":            "Nothing in the queue to shuffle.",
            "clear_ok":                   "Cleared **{n}** track(s) from the queue.",
            "clear_nothing":              "The queue is already empty.",
            "remove_ok":                  "Removed **{title}** from the queue.",
            "remove_oob":                 "That position is out of range.",
            "move_ok":                    "Moved **{title}** to position **{to}**.",
            "move_oob":                   "Both positions must be within the queue.",
            "jump_ok":                    "Jumped to **{title}**.",
            "jump_oob":                   "That position is out of range.",
            "history_empty":              "No tracks have played yet.",
            "history_title":              "Recently Played",
            "volume_nothing":             "There is no active player.",
            "volume_set":                 "Volume set to **{vol}%**.",
            "disconnect_nothing":         "I am not connected to a voice channel.",
            "disconnect_ok":              "Disconnected from the voice channel.",
            "autoplay_on":                "Autoplay enabled — I'll queue similar tracks automatically.",
            "autoplay_off":               "Autoplay disabled.",
            "autoplay_unavailable":       "Autoplay is not configured (no Last.fm API key).",
            "loop_off":                   "Loop disabled.",
            "loop_track":                 "Looping the current track.",
            "loop_queue":                 "Looping the entire queue.",
            "spotify_disabled":           "Spotify support is not configured.",
            "spotify_resolving":          "Resolving Spotify link…",
            "spotify_fail":               "Couldn't resolve that Spotify link.",
            "added_one":                  "Added **{title}** to the queue.",
            "added_many":                 "Added **{n}** tracks to the queue.",
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
            "resume_nothing":             "Nichts zum Fortsetzen.",
            "resume_ok":                  "Wiedergabe fortgesetzt.",
            "skip_nothing":               "Nichts zum Überspringen.",
            "skip_ok":                    "Übersprungen.",
            "stop_nothing":               "Nichts zum Stoppen.",
            "stop_ok":                    "Wiedergabe gestoppt und Warteschlange geleert.",
            "queue_empty":                "Die Warteschlange ist leer.",
            "queue_title":                "Warteschlange",
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
            "volume_nothing":             "Kein aktiver Player.",
            "volume_set":                 "Lautstärke auf **{vol}%** gesetzt.",
            "disconnect_nothing":         "Ich bin nicht mit einem Sprachkanal verbunden.",
            "disconnect_ok":              "Vom Sprachkanal getrennt.",
            "autoplay_on":                "Autoplay aktiviert — ich füge automatisch ähnliche Tracks hinzu.",
            "autoplay_off":               "Autoplay deaktiviert.",
            "autoplay_unavailable":       "Autoplay ist nicht konfiguriert (kein Last.fm-API-Schlüssel).",
            "loop_off":                   "Loop deaktiviert.",
            "loop_track":                 "Aktuellen Track in Schleife.",
            "loop_queue":                 "Gesamte Warteschlange in Schleife.",
            "spotify_disabled":           "Spotify-Unterstützung ist nicht konfiguriert.",
            "spotify_resolving":          "Spotify-Link wird aufgelöst…",
            "spotify_fail":               "Der Spotify-Link konnte nicht aufgelöst werden.",
            "added_one":                  "**{title}** zur Warteschlange hinzugefügt.",
            "added_many":                 "**{n}** Tracks zur Warteschlange hinzugefügt.",
        },
    },
    "cafe": {
        "en": {
            "not_in_voice":               "hey bestie, hop into a voice channel first ☕💿",
            "get_player_not_in_voice":    "you're not in a voice channel, i can't serve music there 😭☕",
            "music_player_status_title":  "Café Music Player ☕",
            "music_not_connected":        "hmm… not plugged into any music server, like a café with no playlist 😭",
            "music_connected":            "yesss, all hooked up and ready for cozy tracks ☕✨",
            "play_not_found":             "couldn't find that song, like a drink that's not on the menu 😭",
            "pause_nothing":              "nothing playing to pause 😭",
            "pause_ok":                   "pausing the cozy vibes for a sec 🌿☕",
            "resume_nothing":             "nothing to resume 😭",
            "resume_ok":                  "back to the warm café vibes 🎶☕",
            "skip_nothing":               "what should i skip… the silence? 😭",
            "skip_ok":                    "next on the menu 🍰✨",
            "stop_nothing":               "nothing to stop, the speakers are already quiet 🌙",
            "stop_ok":                    "okay, stopping everything and clearing the queue ☕💛",
            "queue_empty":                "the queue is emptier than a café after closing 😭",
            "queue_title":                "Cozy Queue ☕",
            "shuffle_ok":                 "queue shuffled like a fresh deck of café cards 🃏✨",
            "shuffle_nothing":            "nothing in the queue to shuffle 😭",
            "clear_ok":                   "cleared **{n}** track(s) — fresh slate ☕✨",
            "clear_nothing":              "the queue is already empty, bestie 😭",
            "remove_ok":                  "yeeted **{title}** from the queue 🍂",
            "remove_oob":                 "that position doesn't exist in the queue 😭",
            "move_ok":                    "scooted **{title}** to position **{to}** ☕",
            "move_oob":                   "both positions need to actually be in the queue 😭",
            "jump_ok":                    "jumped straight to **{title}** ✨",
            "jump_oob":                   "that position doesn't exist in the queue 😭",
            "history_empty":              "no tracks have played yet, the café just opened ☕",
            "history_title":              "Recently Brewed ☕",
            "volume_nothing":             "no active player 😭",
            "volume_set":                 "volume set to **{vol}%** — café mood adjusted ✨",
            "disconnect_nothing":         "i'm not even in a voice channel 😭",
            "disconnect_ok":              "leaving the vc with a soft barista wave ☕🌿",
            "autoplay_on":                "autoplay is on! i'll keep the vibes going with similar tracks 🎶✨",
            "autoplay_off":               "autoplay off — queue it yourself, bestie 🍵",
            "autoplay_unavailable":       "autoplay isn't set up (no Last.fm key) 😭",
            "loop_off":                   "loop off, moving on through the menu 🍵",
            "loop_track":                 "this track on repeat like a cozy café playlist 🔁☕",
            "loop_queue":                 "looping the whole queue, endless cozy hours 🔁✨",
            "spotify_disabled":           "spotify support isn't set up right now 😭",
            "spotify_resolving":          "brewing that spotify link… ☕",
            "spotify_fail":               "couldn't resolve that spotify link 😭",
            "added_one":                  "**{title}** added to the queue ☕✨",
            "added_many":                 "**{n}** tracks added to the queue ☕✨",
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
            "queue_title":                "Cozy Warteschlange ☕",
            "shuffle_ok":                 "warteschlange gemischt wie ein frisches kartendeck 🃏✨",
            "shuffle_nothing":            "nichts in der warteschlange zum mischen 😭",
            "clear_ok":                   "**{n}** track(s) entfernt — frische tasse ☕✨",
            "clear_nothing":              "die warteschlange ist bereits leer 😭",
            "remove_ok":                  "**{title}** aus der warteschlange entfernt 🍂",
            "remove_oob":                 "diese position existiert nicht in der warteschlange 😭",
            "move_ok":                    "**{title}** an position **{to}** verschoben ☕",
            "move_oob":                   "beide positionen müssen in der warteschlange sein 😭",
            "jump_ok":                    "gesprungen zu **{title}** ✨",
            "jump_oob":                   "diese position existiert nicht in der warteschlange 😭",
            "history_empty":              "es wurden noch keine tracks gespielt, das café hat gerade erst geöffnet ☕",
            "history_title":              "Kürzlich Gebrüht ☕",
            "volume_nothing":             "kein aktiver player 😭",
            "volume_set":                 "lautstärke auf **{vol}%** — café-stimmung angepasst ✨",
            "disconnect_nothing":         "ich bin gar nicht im sprachkanal 😭",
            "disconnect_ok":              "ich verlasse den vc wie ein leiser barista-wink ☕🌿",
            "autoplay_on":                "autoplay an! ich halte die vibes mit ähnlichen tracks am laufen 🎶✨",
            "autoplay_off":               "autoplay aus — füg selbst hinzu, liebchen 🍵",
            "autoplay_unavailable":       "autoplay ist nicht eingerichtet (kein Last.fm-Schlüssel) 😭",
            "loop_off":                   "loop aus, weiter zum nächsten track 🍵",
            "loop_track":                 "dieser track läuft auf repeat wie eine cozy café-playlist 🔁☕",
            "loop_queue":                 "die ganze warteschlange läuft in schleife, endlose cozy stunden 🔁✨",
            "spotify_disabled":           "spotify-unterstützung ist nicht eingerichtet 😭",
            "spotify_resolving":          "löse den spotify-link auf… ☕",
            "spotify_fail":               "spotify-link konnte nicht aufgelöst werden 😭",
            "added_one":                  "**{title}** zur warteschlange hinzugefügt ☕✨",
            "added_many":                 "**{n}** tracks zur warteschlange hinzugefügt ☕✨",
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

def _fmt_dur(ms: Optional[int]) -> str:
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


def _src_badge(track: wavelink.Playable) -> str:
    source = (track.source or "").lower()
    if "youtube" in source:
        return f"{get_emoji('youtube')} YouTube"
    if "soundcloud" in source:
        return f"{get_emoji('soundcloud')} SoundCloud"
    if "spotify" in source:
        return f"{get_emoji('spotify')} Spotify"
    return "🎵 Music"


# ──────────────────────────────────────────────────
#  SPOTIFY CLIENT (spotipy, run in executor)
# ──────────────────────────────────────────────────

class _SpotifyClient:
    """Thin async wrapper around spotipy's sync client."""

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
                    title  = track.get("name") or "Unknown"
                    queries.append(f"{artist} - {title}")
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


async def _probe_node(session, node, sem):
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
    def __init__(self, cog, guild_id, paused):
        super().__init__(
            label="Resume" if paused else "Pause",
            style=discord.ButtonStyle.success if paused else discord.ButtonStyle.secondary,
            emoji=get_emoji("icon_play") if paused else get_emoji("icon_pause"),
        )
        self.cog, self.guild_id = cog, guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if player:
            await player.pause(not player.paused)
        await self.cog._update_np_message(interaction.guild)


class _SkipBtn(discord.ui.Button):
    def __init__(self, cog, guild_id):
        super().__init__(label="Skip", style=discord.ButtonStyle.primary, emoji=get_emoji('icon_skip'))
        self.cog, self.guild_id = cog, guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if player and player.playing:
            await player.skip(force=True)
        # NP refresh happens on TrackStart — no manual update here


class _StopBtn(discord.ui.Button):
    def __init__(self, cog, guild_id):
        super().__init__(label="Stop", style=discord.ButtonStyle.danger, emoji=get_emoji("icon_stop"))
        self.cog, self.guild_id = cog, guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if player:
            player.queue.mode = wavelink.QueueMode.normal
            player.queue.clear()
            await player.stop()
        await self.cog._update_np_message(interaction.guild)


class _PrevBtn(discord.ui.Button):
    def __init__(self, cog, guild_id, enabled):
        super().__init__(
            label="Prev",
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("icon_rewind"),
            disabled=not enabled,
        )
        self.cog, self.guild_id = cog, guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        state = self.cog._state(self.guild_id)
        history: deque = state["history"]
        if not player or not history:
            return
        prev_track = history.pop()
        if player.current:
            player.queue.put_at(0, player.current)
        await player.play(prev_track)


class _LoopBtn(discord.ui.Button):
    def __init__(self, cog, guild_id, mode: wavelink.QueueMode):
        is_on = mode != wavelink.QueueMode.normal
        super().__init__(
            label=_LOOP_LABELS[mode],
            style=discord.ButtonStyle.success if is_on else discord.ButtonStyle.secondary,
            emoji=get_emoji("icon_loop"),
        )
        self.cog, self.guild_id = cog, guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if not player:
            return
        player.queue.mode = _LOOP_NEXT[player.queue.mode]
        await self.cog._update_np_message(interaction.guild)


class _ShuffleBtn(discord.ui.Button):
    def __init__(self, cog, guild_id, enabled):
        super().__init__(
            label="Shuffle",
            style=discord.ButtonStyle.secondary,
            emoji="🔀",
            disabled=not enabled,
        )
        self.cog, self.guild_id = cog, guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if player and not player.queue.is_empty:
            player.queue.shuffle()
        await self.cog._update_np_message(interaction.guild)


class _AutoplayBtn(discord.ui.Button):
    def __init__(self, cog, guild_id, autoplay, available):
        super().__init__(
            label="Autoplay On" if (autoplay and available) else "Autoplay",
            style=discord.ButtonStyle.success if (autoplay and available) else discord.ButtonStyle.secondary,
            emoji="📻",
            disabled=not available,
        )
        self.cog, self.guild_id, self.available = cog, guild_id, available

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not self.available:
            return
        state = self.cog._state(self.guild_id)
        state["autoplay"] = not state["autoplay"]
        await self.cog._update_np_message(interaction.guild)


class _VolDownBtn(discord.ui.Button):
    def __init__(self, cog, guild_id):
        super().__init__(label="Vol −", style=discord.ButtonStyle.secondary, emoji="🔉")
        self.cog, self.guild_id = cog, guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if player:
            await player.set_volume(max(0, player.volume - 10))
        await self.cog._update_np_message(interaction.guild)


class _VolUpBtn(discord.ui.Button):
    def __init__(self, cog, guild_id):
        super().__init__(label="Vol +", style=discord.ButtonStyle.secondary, emoji="🔊")
        self.cog, self.guild_id = cog, guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if player:
            await player.set_volume(min(100, player.volume + 10))
        await self.cog._update_np_message(interaction.guild)


class _QueuePeekBtn(discord.ui.Button):
    """Opens an ephemeral paginated queue view."""
    def __init__(self, cog, guild_id, enabled):
        super().__init__(
            label="Queue",
            style=discord.ButtonStyle.secondary,
            emoji="📜",
            disabled=not enabled,
        )
        self.cog, self.guild_id = cog, guild_id

    async def callback(self, interaction: discord.Interaction):
        player: wavelink.Player = interaction.guild.voice_client
        if not player or player.queue.is_empty:
            await interaction.response.send_message(
                "The queue is empty.", ephemeral=True
            )
            return
        lines = []
        for i, track in enumerate(player.queue, start=1):
            dur = _fmt_dur(track.length) if track.length else "?"
            title = (track.title or "Unknown")[:55]
            artist = (track.author or "Unknown")[:30]
            lines.append(f"`{i:>2}.` **{title}** — {artist} `[{dur}]`")
        pages = paginate(lines, per_page=QUEUE_PAGE_SIZE)
        view = PaginatedView(
            title=f"☕ Up Next · {len(player.queue)} track(s)",
            pages=pages,
        )
        await interaction.response.send_message(view=view, ephemeral=True)


# ──────────────────────────────────────────────────
#  NOW-PLAYING CARD BUILDER
# ──────────────────────────────────────────────────

def _build_np_view(player, guild, cog, is_playing=True) -> discord.ui.LayoutView:
    state    = cog._state(guild.id)
    track    = player.current if player else None
    autoplay = state.get("autoplay", False)
    history: deque = state.get("history", deque())
    vol      = player.volume if player else 100
    q_mode   = player.queue.mode if player else wavelink.QueueMode.normal
    q_count  = len(player.queue) if player else 0

    if not track or not is_playing:
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_stop')} Nothing Playing"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content="-# Use `.play <song>` to queue something up."),
            accent_colour=discord.Colour(0x5865F2),
        ))
        return view

    accent_color = _source_colour(track)
    duration     = _progress_bar(player.position or 0, track.length or 0)
    src_badge    = _src_badge(track)
    status_icon  = get_emoji("icon_pause") if player.paused else get_emoji("icon_play")

    # Status chips
    chips = [f"{src_badge} · Vol {vol}%"]
    if q_mode == wavelink.QueueMode.loop:
        chips.append(f"{get_emoji('icon_loop')} Track")
    elif q_mode == wavelink.QueueMode.loop_all:
        chips.append(f"{get_emoji('icon_loop')} Queue")
    if autoplay:
        chips.append("📻 Autoplay")
    if q_count:
        chips.append(f"📜 +{q_count} queued")

    body = (
        f"### {status_icon} Now Playing\n"
        f"**{track.title}**\n"
        f"by {track.author or 'Unknown Artist'}\n\n"
        f"{duration}\n\n"
        f"-# {' · '.join(chips)}"
    )

    items: list = [discord.ui.TextDisplay(content=body)]
    if track.artwork:
        items.insert(0, discord.ui.MediaGallery(
            MediaGalleryItem(media=UnfurledMediaItem(url=track.artwork))
        ))
        items.insert(1, discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))

    items += [
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            _PrevBtn(cog, guild.id, enabled=bool(history)),
            _PauseResumeBtn(cog, guild.id, paused=player.paused),
            _SkipBtn(cog, guild.id),
            _StopBtn(cog, guild.id),
        ),
        discord.ui.ActionRow(
            _LoopBtn(cog, guild.id, mode=q_mode),
            _ShuffleBtn(cog, guild.id, enabled=q_count > 1),
            _VolDownBtn(cog, guild.id),
            _VolUpBtn(cog, guild.id),
        ),
        discord.ui.ActionRow(
            _QueuePeekBtn(cog, guild.id, enabled=q_count > 0),
            _AutoplayBtn(cog, guild.id, autoplay=autoplay, available=bool(cog._lastfm_key)),
        ),
    ]

    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(*items, accent_colour=accent_color))
    if track.uri:
        view.add_item(discord.ui.ActionRow(
            discord.ui.Button(label="Open Track", style=discord.ButtonStyle.link, url=track.uri)
        ))
    return view


# ──────────────────────────────────────────────────
#  MUSIC COG
# ──────────────────────────────────────────────────

class MusicSystem(commands.Cog):
    """Music system — gap-free playback, premium queue management, multi-source."""

    def __init__(self, bot: commands.Bot):
        self.bot         = bot
        self.connected   = False
        self._connecting = False

        # { guild_id: { autoplay, history, np_message, np_task } }
        self._guild_states: dict[int, dict] = {}

        # Spotify (spotipy) — optional
        sp_id     = os.environ.get("SPOTIFY_CLIENT_ID")
        sp_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        self._spotify: Optional[_SpotifyClient] = None
        if sp_id and sp_secret:
            if _SPOTIPY_AVAILABLE:
                try:
                    self._spotify = _SpotifyClient(sp_id, sp_secret)
                    log.debug("Music", "Spotify URL support enabled (spotipy).")
                except Exception as e:
                    log.warning("Music", f"Spotify init failed: {e}")
            else:
                log.warning("Music", "spotipy not installed — Spotify support disabled.")

        # Last.fm autoplay — optional
        self._lastfm_key: Optional[str] = os.environ.get("LASTFM_API_KEY")
        if self._lastfm_key:
            log.debug("Music", "Last.fm autoplay enabled.")

        bot.loop.create_task(self.startup_connect())

    def _state(self, guild_id: int) -> dict:
        if guild_id not in self._guild_states:
            self._guild_states[guild_id] = {
                "autoplay":   False,
                "history":    deque(maxlen=HISTORY_LEN),
                "np_message": None,
                "np_task":    None,
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

    async def _np_refresh_loop(self, guild: discord.Guild):
        """Background task: refresh the NP card every 10s while a track plays."""
        try:
            while True:
                await asyncio.sleep(10)
                player: wavelink.Player = guild.voice_client
                state = self._state(guild.id)
                if not player or not player.current or not state.get("np_message"):
                    return
                if player.playing and not player.paused:
                    await self._update_np_message(guild)
        except asyncio.CancelledError:
            pass

    def _start_np_refresh(self, guild: discord.Guild):
        state = self._state(guild.id)
        old: Optional[asyncio.Task] = state.get("np_task")
        if old and not old.done():
            old.cancel()
        state["np_task"] = self.bot.loop.create_task(self._np_refresh_loop(guild))

    async def _send_np(self, ctx: commands.Context, player: wavelink.Player):
        state   = self._state(ctx.guild.id)
        old_msg: Optional[discord.Message] = state.get("np_message")
        view    = _build_np_view(player, ctx.guild, self)
        new_msg = await ctx.send(view=view)
        state["np_message"] = new_msg
        self._start_np_refresh(ctx.guild)
        if old_msg:
            try:
                await old_msg.delete()
            except Exception:
                pass

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
        """Wavelink auto-advances the queue (AutoPlayMode.partial) — we just refresh UI."""
        player = payload.player
        if not player:
            return
        await self._update_np_message(player.guild)
        self._start_np_refresh(player.guild)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        player = payload.player
        if player is None:
            return

        guild_id = player.guild.id
        state    = self._state(guild_id)

        # Push finished track to history (skip if it was a loop replay)
        if payload.track and player.queue.mode != wavelink.QueueMode.loop:
            state["history"].append(payload.track)

        # If the queue is about to dry up AND Last.fm autoplay is on, top it up
        # (we do this proactively so wavelink's auto-advance keeps flowing seamlessly)
        if (
            state.get("autoplay")
            and self._lastfm_key
            and player.queue.is_empty
            and player.queue.mode == wavelink.QueueMode.normal
            and payload.track
        ):
            similars = await _lastfm_similar(
                self._lastfm_key,
                payload.track.author or "",
                payload.track.title or "",
            )
            for similar_artist, similar_title in similars[:5]:
                results = await wavelink.Playable.search(f"ytsearch:{similar_artist} - {similar_title}")
                if results:
                    nxt = results[0] if isinstance(results, list) else results
                    await player.queue.put_wait(nxt)

        # Idle disconnect — if nothing left to play, wait grace period then leave
        await asyncio.sleep(2)  # give wavelink a moment to advance the queue
        if player.playing or not player.queue.is_empty:
            return

        await asyncio.sleep(IDLE_TIMEOUT)
        if player and not player.playing and player.queue.is_empty:
            try:
                await player.disconnect()
            except Exception:
                pass
            state["np_message"] = None
            old_task: Optional[asyncio.Task] = state.get("np_task")
            if old_task and not old_task.done():
                old_task.cancel()

    # ─── SOURCE RESOLUTION ────────────────────────

    async def _resolve_query(self, query: str) -> Optional[list[str]]:
        q = query.strip()

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

        if q.lower().startswith("sc:"):
            return [f"scsearch:{q[3:].strip()}"]
        if q.lower().startswith("yt:"):
            return [f"ytsearch:{q[3:].strip()}"]
        if q.startswith("http://") or q.startswith("https://"):
            return [q]
        return [f"ytsearch:{q}"]

    # ─── PLAYER HELPER ────────────────────────────

    async def get_player(self, ctx: commands.Context) -> Optional[wavelink.Player]:
        if not ctx.author.voice:
            await ctx.send(msg(ctx, "get_player_not_in_voice"))
            return None
        channel = ctx.author.voice.channel
        player: Optional[wavelink.Player] = ctx.voice_client
        if player is None:
            player = await channel.connect(cls=wavelink.Player)
            # Critical for gap-free playback: wavelink auto-advances the queue
            player.autoplay = wavelink.AutoPlayMode.partial
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

        searches = await self._resolve_query(search)

        if status_msg:
            try:
                await status_msg.delete()
            except Exception:
                pass

        if not searches:
            return await ctx.send(msg(ctx, "play_not_found" if not is_spotify else "spotify_fail"))

        added_tracks: list[wavelink.Playable] = []
        was_idle = not player.playing

        for query in searches:
            try:
                results = await wavelink.Playable.search(query)
            except Exception:
                continue
            if not results:
                continue
            track = results[0] if isinstance(results, list) else results
            await player.queue.put_wait(track)
            added_tracks.append(track)

        if not added_tracks:
            return await ctx.send(msg(ctx, "play_not_found"))

        # Kick off playback if we were idle. Wavelink auto-advances after this.
        if was_idle and not player.playing:
            first = player.queue.get()
            await player.play(first)

        if len(added_tracks) > 1:
            multi = discord.ui.LayoutView()
            multi.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=(
                    f"### ☕ {msg(ctx, 'added_many', n=len(added_tracks))}\n"
                    f"-# Now playing **{(player.current or added_tracks[0]).title}**"
                )),
                accent_colour=_source_colour(added_tracks[0]),
            ))
            await ctx.send(view=multi)
        elif not was_idle:
            # Single track added to existing queue
            one = discord.ui.LayoutView()
            one.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=(
                    f"### ☕ {msg(ctx, 'added_one', title=added_tracks[0].title)}\n"
                    f"-# Position **{len(player.queue)}** in the queue"
                )),
                accent_colour=_source_colour(added_tracks[0]),
            ))
            await ctx.send(view=one)

        # Always show / refresh the now-playing card when starting fresh
        if was_idle:
            # Brief pause to let wavelink populate player.current
            await asyncio.sleep(0.3)
            await self._send_np(ctx, player)

    @commands.command(name="pause", help="{ 'en': 'pause the current track 🌿', 'de': 'pausiert den aktuellen track' }")
    async def pause(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or not player.playing:
            return await ctx.send(msg(ctx, "pause_nothing"))
        await player.pause(True)
        await ctx.send(msg(ctx, "pause_ok"))
        await self._update_np_message(ctx.guild)

    @commands.command(name="resume", help="{ 'en': 'resume the paused track ☕🎶', 'de': 'setzt den pausierten track fort' }")
    async def resume(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "resume_nothing"))
        await player.pause(False)
        await ctx.send(msg(ctx, "resume_ok"))
        await self._update_np_message(ctx.guild)

    @commands.command(name="skip", aliases=["sk"], help="{ 'en': 'skip to the next track 🍰', 'de': 'springt zum nächsten track' }")
    async def skip(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or not player.playing:
            return await ctx.send(msg(ctx, "skip_nothing"))
        await player.skip(force=True)
        await ctx.send(msg(ctx, "skip_ok"))

    @commands.command(name="stop", help="{ 'en': 'stop and clear the queue ☕', 'de': 'stoppt die wiedergabe' }")
    async def stop(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "stop_nothing"))
        player.queue.mode = wavelink.QueueMode.normal
        player.queue.clear()
        await player.stop()
        await ctx.send(msg(ctx, "stop_ok"))
        await self._update_np_message(ctx.guild)

    @commands.command(name="loop", aliases=["repeat"], help="{ 'en': 'cycle loop mode (off → track → queue) 🔁', 'de': 'wechselt loop-modus' }")
    async def loop(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "skip_nothing"))
        player.queue.mode = _LOOP_NEXT[player.queue.mode]
        key = {
            wavelink.QueueMode.normal:   "loop_off",
            wavelink.QueueMode.loop:     "loop_track",
            wavelink.QueueMode.loop_all: "loop_queue",
        }[player.queue.mode]
        await ctx.send(msg(ctx, key))
        await self._update_np_message(ctx.guild)

    @commands.command(name="loopqueue", aliases=["lq"], help="{ 'en': 'loop the entire queue 🔁', 'de': 'die ganze warteschlange in schleife' }")
    async def loopqueue(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "skip_nothing"))
        if player.queue.mode == wavelink.QueueMode.loop_all:
            player.queue.mode = wavelink.QueueMode.normal
            await ctx.send(msg(ctx, "loop_off"))
        else:
            player.queue.mode = wavelink.QueueMode.loop_all
            await ctx.send(msg(ctx, "loop_queue"))
        await self._update_np_message(ctx.guild)

    @commands.command(name="autoplay", aliases=["ap"], help="{ 'en': 'toggle Last.fm autoplay 📻', 'de': 'schaltet Last.fm-Autoplay um' }")
    async def autoplay(self, ctx: commands.Context):
        if not self._lastfm_key:
            return await ctx.send(msg(ctx, "autoplay_unavailable"))
        state = self._state(ctx.guild.id)
        state["autoplay"] = not state["autoplay"]
        await ctx.send(msg(ctx, "autoplay_on" if state["autoplay"] else "autoplay_off"))
        await self._update_np_message(ctx.guild)

    @commands.command(name="queue", aliases=["q"], help="{ 'en': 'show the current queue ☕📜', 'de': 'zeigt die warteschlange' }")
    async def queue(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(msg(ctx, "queue_empty"))

        lines: list[str] = []
        # Header line: now playing summary
        if player.current:
            lines.append(
                f"**▶ Now:** {player.current.title} — {player.current.author or 'Unknown'}\n"
            )
        for i, track in enumerate(player.queue, start=1):
            dur = _fmt_dur(track.length) if track.length else "?"
            title = (track.title or "Unknown")[:55]
            artist = (track.author or "Unknown")[:30]
            lines.append(f"`{i:>2}.` **{title}** — {artist} `[{dur}]`")

        pages = paginate(lines, per_page=QUEUE_PAGE_SIZE)
        title = f"{msg(ctx, 'queue_title')} · {len(player.queue)} track(s)"
        view = PaginatedView(title=title, pages=pages)
        await ctx.send(view=view)

    @commands.command(name="shuffle", aliases=["sh"], help="{ 'en': 'shuffle the queue 🔀', 'de': 'mische die warteschlange' }")
    async def shuffle(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(msg(ctx, "shuffle_nothing"))
        player.queue.shuffle()
        await ctx.send(msg(ctx, "shuffle_ok"))
        await self._update_np_message(ctx.guild)

    @commands.command(name="clearqueue", aliases=["cq", "qclear"], help="{ 'en': 'clear the queue (keeps current track) 🧹', 'de': 'leert die warteschlange' }")
    async def clearqueue(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(msg(ctx, "clear_nothing"))
        n = len(player.queue)
        player.queue.clear()
        await ctx.send(msg(ctx, "clear_ok", n=n))
        await self._update_np_message(ctx.guild)

    @commands.command(name="remove", aliases=["rm"], help="{ 'en': 'remove a track from the queue by position', 'de': 'entferne einen track per position' }")
    async def remove(self, ctx: commands.Context, position: int):
        player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(msg(ctx, "queue_empty"))
        idx = position - 1
        if idx < 0 or idx >= len(player.queue):
            return await ctx.send(msg(ctx, "remove_oob"))
        track = player.queue.get_at(idx)
        await ctx.send(msg(ctx, "remove_ok", title=track.title))
        await self._update_np_message(ctx.guild)

    @commands.command(name="move", aliases=["mv"], help="{ 'en': 'move a track from one queue position to another', 'de': 'verschiebe einen track' }")
    async def move(self, ctx: commands.Context, src: int, dst: int):
        player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(msg(ctx, "queue_empty"))
        si, di = src - 1, dst - 1
        n = len(player.queue)
        if si < 0 or si >= n or di < 0 or di >= n:
            return await ctx.send(msg(ctx, "move_oob"))
        track = player.queue.get_at(si)
        player.queue.put_at(di, track)
        await ctx.send(msg(ctx, "move_ok", title=track.title, to=dst))
        await self._update_np_message(ctx.guild)

    @commands.command(name="jump", aliases=["skipto"], help="{ 'en': 'jump straight to a track at a queue position', 'de': 'springe zu einer position' }")
    async def jump(self, ctx: commands.Context, position: int):
        player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(msg(ctx, "queue_empty"))
        idx = position - 1
        if idx < 0 or idx >= len(player.queue):
            return await ctx.send(msg(ctx, "jump_oob"))
        # Drop everything before the target, then skip the current track
        for _ in range(idx):
            player.queue.get()
        target = player.queue.peek(0)
        await player.skip(force=True)
        await ctx.send(msg(ctx, "jump_ok", title=target.title))

    @commands.command(name="history", aliases=["hist"], help="{ 'en': 'show recently played tracks ☕📜', 'de': 'zeigt zuletzt gespielte tracks' }")
    async def history(self, ctx: commands.Context):
        state = self._state(ctx.guild.id)
        history: deque = state.get("history", deque())
        if not history:
            return await ctx.send(msg(ctx, "history_empty"))
        lines = []
        # newest first
        for i, track in enumerate(reversed(list(history)), start=1):
            dur = _fmt_dur(track.length) if track.length else "?"
            title = (track.title or "Unknown")[:55]
            artist = (track.author or "Unknown")[:30]
            lines.append(f"`{i:>2}.` **{title}** — {artist} `[{dur}]`")
        pages = paginate(lines, per_page=QUEUE_PAGE_SIZE)
        view = PaginatedView(title=msg(ctx, "history_title"), pages=pages)
        await ctx.send(view=view)

    @commands.command(name="nowplaying", aliases=["np"], help="{ 'en': 'see whats brewing right now ☕🎵', 'de': 'zeigt den aktuellen track' }")
    async def nowplaying(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or (not player.playing and not player.paused):
            return await ctx.send(msg(ctx, "pause_nothing"))
        await self._send_np(ctx, player)

    @commands.command(name="volume", aliases=["vol"], help="{ 'en': 'set the playback volume ✨', 'de': 'passt die lautstärke an' }")
    async def volume(self, ctx: commands.Context, vol: int):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "volume_nothing"))
        vol = max(0, min(vol, 100))
        await player.set_volume(vol)
        await ctx.send(msg(ctx, "volume_set", vol=vol))
        await self._update_np_message(ctx.guild)

    @commands.command(name="disconnect", aliases=["dc", "leave"], help="{ 'en': 'have niko leave the voice channel ☕', 'de': 'trennt niko vom sprachkanal' }")
    async def disconnect(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "disconnect_nothing"))
        state = self._state(ctx.guild.id)
        state["np_message"] = None
        old_task: Optional[asyncio.Task] = state.get("np_task")
        if old_task and not old_task.done():
            old_task.cancel()
        await player.disconnect()
        await ctx.send(msg(ctx, "disconnect_ok"))

    @commands.command(name="musicstatus", help="{ 'en': 'check if niko is connected to a music server ☕', 'de': 'prüfe ob niko verbunden ist' }")
    async def music_status(self, ctx: commands.Context):
        sp_line = ""
        if self._spotify:
            sp_line += "\n-# 🎧 Spotify URL support enabled (spotipy)"
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
