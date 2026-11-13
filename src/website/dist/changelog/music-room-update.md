# The Music Room: DJs, Shared Playlists and a Real Player

- Date: 2026-11-13
- Version: 2.30.0
- Tags: music, playlists, dj, activity, lastfm, commands, added

Music is now a shared room instead of one person's queue. A DJ role decides who may skip, stop and change the volume; collaborative playlists let a server build a queue together; the now-playing panel's **Open Player** button launches a Discord Activity with the controls in it; and members who link Last.fm can opt in to scrobbling the tracks they request.

## Highlights

### Everyone Gets a Turn
`.dj role @role` names the role that may skip, go back, stop, loop, change autoplay or move the volume. Pause and resume stay open to everyone in the channel, so a DJ stepping away never locks the room. `.dj` shows the current role, `.dj clear` hands playback back to the server, and Manage Server always keeps the controls.

### A Queue the Server Builds
`.playlist create <name>` starts a shared list, `.playlist add <name>` drops the current track in, and `.playlist play <name>` queues it. The owner can `.playlist share @member <name>` so others add and remove tracks, `.playlist show` prints the numbered list, and `.playlist remove <index> <name>` takes one out. Lists belong to their server.

### The Player Leaves Discord
The **Open Player** button on the now-playing panel launches a Discord Activity: artwork, track, artist, a live progress bar, the queue and the controls in one window. It is served from the `activities` subdomain, and every action re-checks membership, the voice channel and the DJ role against the bot — the panel never trusts the ids it is handed.

### Scrobbles You Actually Heard
Members with a linked Last.fm account turn scrobbling on with `.scrobble on`. Only the tracks they request are scrobbled, and a track counts once real playback passes Last.fm's rule — thirty seconds long and half its length or four minutes played — so pausing for ten minutes no longer earns a play. `.scrobble off` stops it again.

## Changes

### added
- `.dj`, `.dj role @role` and `.dj clear` — a per-server DJ role for skip, previous, stop, loop, autoplay and volume
- `.playlist` and `.pl` — list this server's shared playlists with their track counts and owners
- `.playlist create`, `.playlist add`, `.playlist show`, `.playlist remove`, `.playlist share`, `.playlist delete` and `.playlist play` — collaborative lists owned by one member and edited by the people they share them with
- A Discord Activity control panel launched from the now-playing panel's **Open Player** button, served from the `activities` subdomain with a short-lived signed panel session
- Activity controls for skip, previous, pause/resume, stop, loop, autoplay and volume, each checked against the bot's live guild and voice state
- `.scrobble on` and `.scrobble off` — opt-in Last.fm scrobbling for the tracks a member requests, using the linked account's session key
- `track.updateNowPlaying` and `track.scrobble` writes signed with `LASTFM_API_SECRET`
- Per-guild playlist tables and a `music_scrobble_optins` table in the music database

### improved
- Scrobbling measures actual playback progress from Lavalink's player updates instead of the wall clock, so paused or stalled time never counts toward a play
- Only natural finishes scrobble; skipped, replaced and failed tracks are ignored
- The Activity and its API answer from the bot's cached guild state instead of trusting guild or channel ids sent by the client
- Playlist playback reuses the normal `/play` resolver, its 50-track cap and its rate-limit pacing
- DJ checks use the same rule on commands, the now-playing panel and the Activity, and managers always bypass them
- Wording in English, German, Spanish and French for every DJ, playlist and scrobbling message and command description

### fixed
- A track paused for minutes could scrobble without being heard, because listened time was measured with the wall clock
- The `activities` subdomain was rejected as unknown even though Discord's Activity URL mapping pointed at it

## Chart data

```json
{
  "type": "metrics",
  "title": "The Shared Queue",
  "data": [
    {
      "label": "Playlist commands",
      "value": "8",
      "detail": "one `.playlist` group",
      "color": "#4a7fb5"
    },
    {
      "label": "DJ commands",
      "value": "3",
      "detail": "set, show, clear",
      "color": "#66866f"
    },
    {
      "label": "Panel controls",
      "value": "7",
      "detail": "skip to volume",
      "color": "#d96545"
    }
  ]
}
```
