# Music Playback Fixes

- Date: 2026-10-31
- Version: 2.25.1
- Tags: music, lavalink, spotify, autoplay, fixed

Three playback failures are fixed: autoplay no longer stops when Last.fm has nothing to suggest, Spotify links resolve even without API credentials, and the node pool keeps the healthy Lavalink nodes instead of quietly collapsing onto one host.

## Highlights

### Autoplay Stops Stopping
When Last.fm has no neighbours for the seed track, autoplay now continues with the music provider's own related results and schedules a refill, so the queue keeps moving instead of ending the session. The log only reports a dead end when there is genuinely nothing playable.

### Spotify Without Credentials
Spotify links now resolve through the public embed page, so `/play` works with no `SPOTIFY_CLIENT_ID` or `SPOTIFY_CLIENT_SECRET` configured. When credentials do exist the Web API is still tried first, and a refusal — playlists answer `403` for client-credentials tokens since February 2026 — falls through instead of failing the command.

### Playlists That Finish Loading
Playlist expansion paces its Lavalink searches, widens the gap after a `429` instead of firing every track at once, and works to a 90-second budget, so a long playlist resolves while the first track is already playing. Resolving, progress and the added count are all edited into one message.

### The Node Pool Keeps Its Nodes
The health probe now asks the authenticated `/v4/info` endpoint and checks the reply is really Lavalink, which is the same endpoint wavelink connects to. It used to require an unauthenticated `/version` to answer `200`, so working nodes were marked failed and the pool fell back to the one host with the tightest rate limit.

## Changes

### fixed
- Autoplay ending the session when Last.fm returned no similar tracks
- Spotify track links resolving to nothing without API credentials
- Spotify playlist links failing to resolve
- Healthy Lavalink nodes rejected because `/version` answered `404` or `401`
- Lavalink nodes given a pool slot even though wavelink would refuse their certificate

### improved
- Autoplay falls back to the provider's related tracks and queues a refill
- Playlist expansion spaced at 0.35s per search, up to 3s after a `429`, inside a 90-second budget
- One status message carries resolving, progress and the added count instead of three separate messages

## Commits
- ffe0a0e Fixed the spotify playback
- 9ec80c0 Improved spotify playlist resolution
- 50f0c2d Fixed an issue with the music node connections
