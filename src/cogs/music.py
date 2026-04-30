"""
Music System — Niko's Cozy Café Jukebox
────────────────────────────────────────
Features:
  • cv2 Now-Playing cards with album artwork (MediaGallery)
  • Interactive control panel (pause/resume, skip, stop, loop, volume ±10)
  • Multi-source playback: YouTube (default), SoundCloud (sc: prefix), direct URLs
  • Spotify URL support — resolves tracks, albums, playlists → YouTube search
      Requires: SPOTIFY_CLIENT_ID + SPOTIFY_CLIENT_SECRET env vars (silently
      disabled when absent)
  • Autoplay via Last.fm "similar tracks" when the queue runs dry
      Requires: LASTFM_API_KEY env var (silently disabled when absent)
  • Personality-aware text (normal / café modes, EN / DE)

Known Issues:
  • When using spotify track links in the play command it always fails (the plan is to switch to spotipy for the spotify api in a future version)
  • The now playing progress bar does not update unless someone presses the pause button
"""

import asyncio
import base64
import os
import re
import time as _time
from collections import deque

import aiohttp
import discord
import wavelink
from discord import MediaGalleryItem, UnfurledMediaItem, app_commands
from discord.ext import commands

from config.emojis import get_emoji
from utils import logging as log
from utils.ai_config import get_personality

# ──────────────────────────────────────────────────
#  CONSTANTS
# ──────────────────────────────────────────────────

IDLE_TIMEOUT   = 300       # seconds before auto-disconnect on empty queue
HISTORY_LEN    = 10        # tracks kept in per-guild history deque
MAX_QUEUE_SHOW = 10        # tracks shown in .queue list

SOURCE_COLOURS = {
    "youtube":    discord.Colour(0xFF0000),
    "soundcloud": discord.Colour(0xFF5500),
    "spotify":    discord.Colour(0x1DB954),
    "default":    discord.Colour(0x5865F2),
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
            "spotify_disabled":           "Spotify-Unterstützung ist nicht konfiguriert.",
            "spotify_resolving":          "Spotify-Link wird aufgelöst…",
            "spotify_fail":               "Der Spotify-Link konnte nicht aufgelöst werden.",
        },
        "es": {
            "not_in_voice":               "Necesitas estar en un canal de voz primero.",
            "get_player_not_in_voice":    "Necesitas estar en un canal de voz para usar comandos de música.",
            "music_player_status_title":  "Estado del Reproductor de Música",
            "music_not_connected":        "No conectado a ningún servidor de música.",
            "music_connected":            "Conectado a un servidor de música y listo.",
            "play_not_found":             "No pude encontrar esa canción.",
            "pause_nothing":              "No hay nada reproduciéndose ahora mismo.",
            "pause_ok":                   "Pausado.",
            "resume_nothing":             "No hay nada que reanudar.",
            "resume_ok":                  "Reanudado.",
            "skip_nothing":               "No hay nada que saltar.",
            "skip_ok":                    "Saltado.",
            "stop_nothing":               "No hay nada que detener.",
            "stop_ok":                    "Reproducción detenida y cola limpiada.",
            "queue_empty":                "La cola está vacía actualmente.",
            "queue_header":               "**Cola Actual:**",
            "volume_nothing":             "No hay un reproductor activo.",
            "volume_set":                 "Volumen ajustado a **{vol}%**.",
            "disconnect_nothing":         "No estoy conectado a ningún canal de voz.",
            "disconnect_ok":              "Desconectado del canal de voz.",
            "autoplay_on":                "Autoplay activado — añadiré canciones similares automáticamente.",
            "autoplay_off":               "Autoplay desactivado.",
            "autoplay_unavailable":       "Autoplay no está configurado (sin clave de API de Last.fm).",
            "loop_on":                    "Loop activado — repitiendo la canción actual.",
            "loop_off":                   "Loop desactivado.",
            "spotify_disabled":           "El soporte para Spotify no está configurado.",
            "spotify_resolving":          "Resolviendo el enlace de Spotify…",
            "spotify_fail":               "No pude resolver ese enlace de Spotify.",
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
            "spotify_disabled":           "spotify-unterstützung ist nicht eingerichtet 😭",
            "spotify_resolving":          "löse den spotify-link auf… ☕",
            "spotify_fail":               "spotify-link konnte nicht aufgelöst werden 😭",
        },
        "es": {
            "not_in_voice":               "ey amix, tienes que entrar a un canal de voz primero ☕💿",
            "get_player_not_in_voice":    "todavía no estás en un canal de voz, no puedo servir música allí 😭☕",
            "music_player_status_title":  "Reproductor del Café ☕",
            "music_not_connected":        "hmm… no conectado a ningún servidor de música, como un café sin música 😭",
            "music_connected":            "yesss, conectado y listo para servir tracks acogedores ☕✨",
            "play_not_found":             "no encontré esa canción, como una bebida que no está en el menú 😭",
            "pause_nothing":              "no hay nada reproduciéndose para pausar, solo aire silencioso del café 😭",
            "pause_ok":                   "pausando los vibes un momento 🌿☕",
            "resume_nothing":             "no hay nada pausado para reanudar 😭",
            "resume_ok":                  "trayendo los vibes calentitos del café de vuelta 🎶☕",
            "skip_nothing":               "¿saltar qué… el silencio? la playlist está vacía 😭",
            "skip_ok":                    "saltando al siguiente sabor del menú 🍰✨",
            "stop_nothing":               "nada que detener, los altavoces ya están en silencio 🌙",
            "stop_ok":                    "vale vale, deteniendo todo y limpiando la bandeja ☕💛",
            "queue_empty":                "la cola está más vacía que un café a la hora de cierre 😭",
            "queue_header":               "☕ **cola acogedora actual:**",
            "volume_nothing":             "no hay reproductor activo, no se está preparando música 😭",
            "volume_set":                 "volumen a **{vol}%** — ajustando el ambiente del café ✨",
            "disconnect_nothing":         "ni siquiera estoy en un canal de voz ahora mismo 😭",
            "disconnect_ok":              "me voy con un suave saludito de barista, ¡nos vemos pronto! ☕🌿",
            "autoplay_on":                "¡autoplay activado! mantendré los vibes con canciones similares 🎶✨",
            "autoplay_off":               "autoplay apagado — añádelas tú, amix 🍵",
            "autoplay_unavailable":       "autoplay no está configurado (sin clave de Last.fm) 😭",
            "loop_on":                    "repitiendo esta canción como una playlist acogedora del café 🔁☕",
            "loop_off":                   "loop apagado, pasando a la siguiente canción 🍵",
            "spotify_disabled":           "el soporte para spotify no está configurado ahora mismo 😭",
            "spotify_resolving":          "preparando ese enlace de spotify… ☕",
            "spotify_fail":               "no pude resolver ese enlace de spotify 😭",
        },
    },
}


def get_lang(ctx: commands.Context) -> str:
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
        if str(ctx.guild.preferred_locale).lower().startswith("es"):
            return "es"
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
    _TOKEN_URL = "https://accounts.spotify.com/api/token"
    _API_URL   = "https://api.spotify.com/v1"

    def __init__(self, client_id: str, client_secret: str):
        self._id     = client_id
        self._secret = client_secret
        self._token: str | None = None
        self._exp: float = 0.0

    async def _token_headers(self) -> dict:
        if not self._token or _time.monotonic() >= self._exp - 60:
            creds = base64.b64encode(f"{self._id}:{self._secret}".encode()).decode()
            async with aiohttp.ClientSession() as s:
                async with s.post(
                    self._TOKEN_URL,
                    headers={"Authorization": f"Basic {creds}"},
                    data={"grant_type": "client_credentials"},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as r:
                    data = await r.json()
            self._token = data["access_token"]
            self._exp   = _time.monotonic() + data.get("expires_in", 3600)
        return {"Authorization": f"Bearer {self._token}"}

    async def _get(self, path: str) -> dict | None:
        try:
            headers = await self._token_headers()
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    f"{self._API_URL}/{path}",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as r:
                    return await r.json() if r.status == 200 else None
        except Exception:
            return None

    async def resolve_track(self, track_id: str) -> str | None:
        """Returns 'Artist - Title' search string."""
        data = await self._get(f"tracks/{track_id}")
        if not data:
            return None
        artist = data["artists"][0]["name"] if data.get("artists") else "Unknown"
        return f"{artist} - {data['name']}"

    async def resolve_album(self, album_id: str) -> list[str]:
        """Returns list of 'Artist - Title' search strings for all album tracks."""
        data = await self._get(f"albums/{album_id}/tracks?limit=50")
        if not data:
            return []
        queries = []
        for item in data.get("items", []):
            artist = item["artists"][0]["name"] if item.get("artists") else "Unknown"
            queries.append(f"{artist} - {item['name']}")
        return queries

    async def resolve_playlist(self, playlist_id: str) -> list[str]:
        """Returns list of 'Artist - Title' search strings (first 50 tracks)."""
        data = await self._get(f"playlists/{playlist_id}/tracks?limit=50")
        if not data:
            return []
        queries = []
        for item in data.get("items", []):
            track = item.get("track")
            if not track:
                continue
            artist = track["artists"][0]["name"] if track.get("artists") else "Unknown"
            queries.append(f"{artist} - {track['name']}")
        return queries


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
            state = self.cog._state(self.guild_id)
            state["loop"] = False
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
        # put current back at front of queue
        if player.current:
            player.queue.put_at(0, player.current)
        await player.play(prev_track)
        await self.cog._update_np_message(interaction.guild)


class _LoopBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild_id: int, loop: bool):
        super().__init__(
            label="Loop On" if loop else "Loop",
            style=discord.ButtonStyle.success if loop else discord.ButtonStyle.secondary,
            emoji=get_emoji("icon_loop"),
        )
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        state = self.cog._state(self.guild_id)
        state["loop"] = not state["loop"]
        await self.cog._update_np_message(interaction.guild)


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
    loop    = state.get("loop", False)
    autoplay = state.get("autoplay", False)
    history: deque = state.get("history", deque())
    vol     = player.volume if player else 100

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

    body = (
        f"### {status_icon} Now Playing\n"
        f"**{track.title}**\n"
        f"by {author_name}\n\n"
        f"{duration}\n\n"
        f"-# {src_badge} · Vol {vol}% · "
        f"{get_emoji('icon_loop') + ' Loop ' if loop else ''}{'📻 Autoplay ' if autoplay else ''}"
    ).rstrip(" · \n")

    # Build container items
    items: list = [
        discord.ui.TextDisplay(content=body),
    ]

    # Artwork thumbnail (if available)
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
            _LoopBtn(cog, guild.id, loop=loop),
            _AutoplayBtn(cog, guild.id, autoplay=autoplay, available=bool(cog._lastfm_key)),
            _VolDownBtn(cog, guild.id),
            _VolUpBtn(cog, guild.id),
        ),
    ]

    # Link button (separate ActionRow below the container — not inside)
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(*items, accent_colour=accent_color))
    if uri:
        view.add_item(discord.ui.ActionRow(
            discord.ui.Button(label="Open Track", style=discord.ButtonStyle.link, url=uri)
        ))
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

        # YouTube autocomplete cache: { lower_query: (monotonic_ts, [Choice, ...]) }
        self._autocomplete_cache: dict[str, tuple[float, list]] = {}

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

        # Wire the slash autocomplete callback to the /play search parameter
        try:
            self.play.autocomplete("search")(self._play_autocomplete)
        except Exception as exc:
            log.warning("Music", f"Could not attach play autocomplete: {exc}")

        bot.loop.create_task(self.startup_connect())

    def _state(self, guild_id: int) -> dict:
        if guild_id not in self._guild_states:
            self._guild_states[guild_id] = {
                "loop":       False,
                "autoplay":   False,
                "history":    deque(maxlen=HISTORY_LEN),
                "np_message": None,
                "last_track": None,
            }
        return self._guild_states[guild_id]

    # ─── NP MESSAGE UPDATE ────────────────────────

    async def _update_np_message(self, guild: discord.Guild):
        state   = self._state(guild.id)
        message: discord.Message | None = state.get("np_message")
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
        """Send (or update) the now-playing control panel."""
        state  = self._state(ctx.guild.id)
        old_msg: discord.Message | None = state.get("np_message")

        view = _build_np_view(player, ctx.guild, self)
        new_msg = await ctx.send(view=view)
        state["np_message"] = new_msg

        # Clean up the previous control panel quietly
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
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        player = payload.player
        if player is None:
            return

        guild_id = player.guild.id
        state    = self._state(guild_id)

        # Push finished track to history
        if payload.track:
            state["history"].append(payload.track)
            state["last_track"] = payload.track

        # Loop mode — replay the same track
        if state.get("loop") and payload.track:
            await player.play(payload.track)
            await self._update_np_message(player.guild)
            return

        # Queue has more tracks
        if not player.queue.is_empty:
            next_track = player.queue.get()
            await player.play(next_track)
            await self._update_np_message(player.guild)
            return

        # Queue exhausted — try autoplay via Last.fm
        if state.get("autoplay") and self._lastfm_key and payload.track:
            track      = payload.track
            artist_raw = track.author or ""
            title_raw  = track.title  or ""
            similars   = await _lastfm_similar(self._lastfm_key, artist_raw, title_raw)

            for similar_artist, similar_title in similars:
                query   = f"ytsearch:{similar_artist} - {similar_title}"
                results = await wavelink.Playable.search(query)
                if results:
                    nxt = results[0] if isinstance(results, list) else results
                    await player.play(nxt)
                    await self._update_np_message(player.guild)
                    return

        # Nothing more to play — idle grace period then disconnect
        await asyncio.sleep(IDLE_TIMEOUT)
        if player and not player.playing:
            try:
                await player.disconnect()
            except Exception:
                pass
            state["np_message"] = None

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

    async def _play_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        """Live YouTube search suggestions for the slash version of /play."""
        current = (current or "").strip()
        if len(current) < 2:
            return []
        # If the user already pasted a URL, just echo it back so they can submit.
        if current.startswith(("http://", "https://")):
            return [app_commands.Choice(name=current[:100], value=current[:100])]

        # Cheap in-memory cache to avoid hammering Lavalink for every keystroke.
        cache_key = current.lower()
        cached = self._autocomplete_cache.get(cache_key)
        now = _time.monotonic()
        if cached and now - cached[0] < 30:
            return cached[1]

        try:
            results = await asyncio.wait_for(
                wavelink.Playable.search(f"ytsearch:{current}"),
                timeout=2.5,
            )
        except (asyncio.TimeoutError, Exception):
            return []

        if not results:
            return []

        choices: list[app_commands.Choice[str]] = []
        for track in (results if isinstance(results, list) else [results])[:25]:
            label = track.title
            if getattr(track, "author", None):
                label = f"{track.title} — {track.author}"
            label = label[:100]
            value = (getattr(track, "uri", None) or track.title)[:100]
            choices.append(app_commands.Choice(name=label, value=value))

        self._autocomplete_cache[cache_key] = (now, choices)
        return choices

    @commands.hybrid_command(
        name="play", aliases=["p"],
        description="Play a song or add it to the queue",
        help="{ 'en': 'play a song or queue it up ☕🎶', 'de': 'spiele einen track ab', 'es': 'reproduce una canción o agrégala a la cola ☕🎶' }"
    )
    @app_commands.describe(search="Song name, YouTube/SoundCloud/Spotify URL, or sc:<query>")
    async def play(self, ctx: commands.Context, *, search: str):
        # Slash invocations need to defer because resolution can take >3s
        if ctx.interaction and not ctx.interaction.response.is_done():
            try:
                await ctx.defer()
            except Exception:
                pass
        player = await self.get_player(ctx)
        if not player:
            return

        # Handle Spotify URL feedback before long resolution
        is_spotify = "open.spotify.com" in search
        if is_spotify and not self._spotify:
            return await ctx.send(msg(ctx, "spotify_disabled"))

        if is_spotify:
            resolving = discord.ui.LayoutView()
            resolving.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### ☕ {msg(ctx, 'spotify_resolving')}"),
                accent_colour=SOURCE_COLOURS["spotify"],
            ))
            status_msg = await ctx.send(view=resolving)
        else:
            status_msg = None

        # Resolve to wavelink search strings
        searches = await self._resolve_query(search)

        if status_msg:
            try:
                await status_msg.delete()
            except Exception:
                pass

        if not searches:
            return await ctx.send(msg(ctx, "play_not_found" if not is_spotify else "spotify_fail"))

        queued_count = 0
        first_track  = None

        for i, query in enumerate(searches):
            results = await wavelink.Playable.search(query)
            if not results:
                continue

            track = results[0] if isinstance(results, list) else results
            if not player.playing and first_track is None:
                await player.play(track)
                first_track = track
            else:
                player.queue.put(track)
                queued_count += 1

        if first_track is None and queued_count == 0:
            return await ctx.send(msg(ctx, "play_not_found"))

        if queued_count:
            if not first_track:
                first_track = player.current
            # Multiple tracks added (album / playlist)
            multi = discord.ui.LayoutView()
            multi.add_item(discord.ui.Container(
                discord.ui.TextDisplay(
                    content=(
                        f"### ☕ Added {queued_count + 1} track{'s' if queued_count else ''} to the queue\n"
                        f"Now playing **{first_track.title}** + {queued_count} more queued."
                    )
                ),
                accent_colour=_source_colour(first_track),
            ))
            await ctx.send(view=multi)

        # Send / replace now-playing control panel
        if first_track and not queued_count:
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
        self._state(ctx.guild.id)["loop"] = False
        player.queue.clear()
        await player.stop()
        await ctx.send(msg(ctx, "stop_ok"))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="loop", aliases=["repeat"],
        help="{ 'en': 'toggle loop for the current track 🔁', 'de': 'wiederholt den aktuellen track' }"
    )
    async def loop(self, ctx: commands.Context):
        state = self._state(ctx.guild.id)
        state["loop"] = not state["loop"]
        key = "loop_on" if state["loop"] else "loop_off"
        await ctx.send(msg(ctx, key))
        await self._update_np_message(ctx.guild)

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

        lines = [msg(ctx, "queue_header")]
        for i, track in enumerate(player.queue, start=1):
            dur = _fmt_dur(track.length) if track.length else "?"
            lines.append(f"{i}. **{track.title}** — {track.author or 'Unknown'} `[{dur}]`")
            if i >= MAX_QUEUE_SHOW:
                remaining = len(player.queue) - MAX_QUEUE_SHOW
                if remaining > 0:
                    lines.append(f"\n*…and {remaining} more track{'s' if remaining > 1 else ''}*")
                break

        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="\n".join(lines)),
            accent_colour=discord.Colour(0x5865F2),
        ))
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
        state["np_message"] = None
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
