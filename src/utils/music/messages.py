"""
Music System — user-facing messages (EN / DE / ES). Lives in utils/music so
the message catalog stays independent of the Discord command layer.
"""

from utils.i18n import make_msg

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
}

# ── Liked songs / favorites (added on top of the original catalog) ──────────
MESSAGES["normal"]["en"].update({
    "like_on":              "Liked **{title}** ♥",
    "like_off":             "Removed **{title}** from your likes.",
    "like_nothing":         "There's nothing playing to like.",
    "liked_header":         "**Your Liked Songs:**",
    "liked_empty":          "You haven't liked any songs yet — play something and use `.like` or the ♥ button on the music panel.",
    "unlike_ok":            "Removed **{title}** from your likes.",
    "unlike_nothing":       "You don't have any liked songs.",
    "unlike_invalid":       "That's not a valid like number — check `.liked`.",
    "likes_cleared":        "Cleared all {count} liked songs.",
})
MESSAGES["normal"]["de"].update({
    "like_on":              "**{title}** geliked ♥",
    "like_off":             "**{title}** aus deinen Likes entfernt.",
    "like_nothing":         "Es läuft gerade nichts zum Liken.",
    "liked_header":         "**Deine gelikten Songs:**",
    "liked_empty":          "Du hast noch keine Songs geliked — spiel etwas ab und nutze `.like` oder den ♥-Button im Musik-Panel.",
    "unlike_ok":            "**{title}** aus deinen Likes entfernt.",
    "unlike_nothing":       "Du hast keine gelikten Songs.",
    "unlike_invalid":       "Das ist keine gültige Like-Nummer — schau bei `.liked` nach.",
    "likes_cleared":        "{count} gelikte Songs gelöscht.",
})
MESSAGES["normal"]["es"].update({
    "like_on":              "**{title}** añadida a tus favoritos ♥",
    "like_off":             "**{title}** eliminada de tus favoritos.",
    "like_nothing":         "No hay nada reproduciéndose para dar like.",
    "liked_header":         "**Tus Canciones Favoritas:**",
    "liked_empty":          "Aún no has dado like a ninguna canción — reproduce algo y usa `.like` o el botón ♥ del panel de música.",
    "unlike_ok":            "**{title}** eliminada de tus favoritos.",
    "unlike_nothing":       "No tienes canciones favoritas.",
    "unlike_invalid":       "Ese no es un número de like válido — revisa `.liked`.",
    "likes_cleared":        "Se eliminaron {count} canciones favoritas.",
})


# Playback was accepted by the node but never actually started streaming.
MESSAGES["normal"]["en"].update({
    "music_start_failed": "I couldn't start playback on the music server — please try `.play` again.",
    "music_db_error":      "Couldn't reach the music database right now — try again in a moment.",
    "music_playlist_capped": "Only the first {count} tracks were added — playlists are capped to keep the queue manageable.",
})
MESSAGES["normal"]["de"].update({
    "music_start_failed": "Die Wiedergabe konnte nicht gestartet werden — bitte versuche es mit `.play` noch einmal.",
    "music_db_error":      "Die Musik-Datenbank ist gerade nicht erreichbar — versuche es gleich noch einmal.",
    "music_playlist_capped": "Nur die ersten {count} Titel wurden hinzugefügt — Playlists sind begrenzt, damit die Warteschlange übersichtlich bleibt.",
})
MESSAGES["normal"]["es"].update({
    "music_start_failed": "No se pudo iniciar la reproducción en el servidor de música — inténtalo de nuevo con `.play`.",
    "music_db_error":      "No se pudo acceder a la base de datos de música — inténtalo de nuevo en un momento.",
    "music_playlist_capped": "Solo se añadieron las primeras {count} canciones — las listas tienen un límite para mantener la cola manejable.",
})

msg = make_msg(MESSAGES)