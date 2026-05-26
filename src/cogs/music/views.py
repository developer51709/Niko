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

# The original ajieblogs API (https://lavalink-list.ajieblogs.eu.org/All)
# stopped responding in early 2026 (returns 502 Bad Gateway / Cloudflare 403).
# The community now relies on DarrenOfficial/lavalink-list, whose markdown
# files we parse directly from raw.githubusercontent.com. We keep a small
# embedded fallback list of well-known public nodes so the music cog still
# works even if both upstreams are unreachable at startup.
_DN_SSL_RAW    = "https://raw.githubusercontent.com/DarrenOfficial/lavalink-list/master/docs/SSL/Lavalink-SSL.md"
_DN_NOSSL_RAW  = "https://raw.githubusercontent.com/DarrenOfficial/lavalink-list/master/docs/NoSSL/Lavalink-NonSSL.md"

_PROBE_TIMEOUT   = 3.0
_CONNECT_TIMEOUT = 20.0
_MAX_PROBERS     = 8

_FALLBACK_NODES: list[dict] = [
    # Last-known-good public v4 nodes (April 2026)
    {"host": "lavalinkv4.serenetia.com", "port": 443,   "password": "https://seretia.link/discord", "secure": True,  "version": "v4"},
    {"host": "lavalink.jirayu.net",      "port": 443,   "password": "youshallnotpass",              "secure": True,  "version": "v4"},
    {"host": "lava-v4.millohost.my.id",  "port": 443,   "password": "https://discord.gg/mjS5J2K3ep","secure": True,  "version": "v4"},
    {"host": "lavalink-v4.triniumhost.com", "port": 443,"password": "free",                         "secure": True,  "version": "v4"},
    {"host": "lavalinkv4.serenetia.com", "port": 80,    "password": "https://seretia.link/discord", "secure": False, "version": "v4"},
    {"host": "lavalink.jirayu.net",      "port": 13592, "password": "youshallnotpass",              "secure": False, "version": "v4"},
    {"host": "lavalink.triniumhost.com", "port": 4333,  "password": "free",                         "secure": False, "version": "v4"},
    {"host": "lavalink.triniumhost.com", "port": 2333,  "password": "kirito",                       "secure": False, "version": "v4"},
    {"host": "lava.g3v.co.uk",           "port": 9008,  "password": "lavalinklol",                  "secure": False, "version": "v4"},
    {"host": "n3.nexcloud.in",           "port": 2026,  "password": "nexcloud",                     "secure": False, "version": "v4"},
]


# Match a fenced ``bash``…`` block containing Host/Port/Password/Secure lines.
_DN_NODE_RE = re.compile(
    r"```bash\s*\n"
    r"\s*Host\s*:\s*(?P<host>\S+).*?\n"
    r"\s*Port\s*:\s*(?P<port>\d+).*?\n"
    r"\s*Password\s*:\s*(?P<password>.+?)\s*\n"
    r"\s*Secure\s*:\s*(?P<secure>[A-Za-z]+)\s*\n"
    r"```",
    re.IGNORECASE | re.DOTALL,
)


def _parse_dn_markdown(md: str, default_secure: bool) -> list[dict]:
    nodes: list[dict] = []
    for m in _DN_NODE_RE.finditer(md):
        host = m.group("host").strip()
        try:
            port = int(m.group("port").strip())
        except ValueError:
            continue
        # Strip surrounding quotes if present in the password field.
        password = m.group("password").strip().strip('"').strip("'")
        secure_raw = m.group("secure").strip().lower()
        secure = secure_raw in ("true", "yes", "1") if secure_raw else default_secure
        nodes.append({
            "host": host,
            "port": port,
            "password": password,
            "secure": secure,
            "version": "v4",
        })
    return nodes


async def _fetch_dn_source(session: aiohttp.ClientSession, url: str, default_secure: bool) -> list[dict]:
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status != 200:
                return []
            text = await r.text()
        return _parse_dn_markdown(text, default_secure)
    except Exception:
        return []


def _dedupe_nodes(nodes: list[dict]) -> list[dict]:
    seen: set[tuple[str, int, bool]] = set()
    unique: list[dict] = []
    for n in nodes:
        key = (n.get("host"), n.get("port"), bool(n.get("secure")))
        if key in seen:
            continue
        seen.add(key)
        unique.append(n)
    return unique


async def _fetch_node_list() -> list[dict]:
    try:
        async with aiohttp.ClientSession() as s:
            ssl_nodes, nossl_nodes = await asyncio.gather(
                _fetch_dn_source(s, _DN_SSL_RAW, default_secure=True),
                _fetch_dn_source(s, _DN_NOSSL_RAW, default_secure=False),
                return_exceptions=False,
            )
        nodes = _dedupe_nodes(list(ssl_nodes) + list(nossl_nodes))
        if nodes:
            log.info("Lavalink", f"Fetched {len(nodes)} v4 nodes from DarrenOfficial/lavalink-list.")
            return nodes
    except Exception as e:
        log.warning("Lavalink", f"Node list fetch failed: {e}")

    log.warning("Lavalink", "Falling back to embedded node list.")
    return list(_FALLBACK_NODES)


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


__all__ = [k for k in list(globals()) if not k.startswith("__")]
