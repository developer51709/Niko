# Niko Listens: Last.fm Cards and Server Boards

- Date: 2026-11-08
- Version: 2.29.0
- Tags: lastfm, music, cards, accounts, commands, added

`.fm` now answers with what you are playing. A new Last.fm cog draws every answer as a card — now playing, your library at a glance, charts for any period, one artist or album beside your own playcount, and a scrobble history with album art — and turns the server into a music board: who listens to an artist, who holds the crown for each one, and how closely two members' taste overlaps. Linking goes through Last.fm's own approval page with a callback on the website, so Niko never asks for a password.

## Highlights

### One Card per Question
Four directions, four shapes. Now playing is the large one: sleeve, title, artist, album, a red dot while the track is live, and the last scrobble in the same frame when it is not. The overview puts your scrobble total and top artists, albums and tracks for a period side by side. A chart is a ranked board with proportion bars, so the shape of a top ten reads before the numbers do. An artist or album card puts your own playcount above the global listeners and scrobbles.

### A Server, Ranked by Taste
`/fm whoknows` ranks this server's listeners of one artist, `/fm crowns` shows the artists a member listens to more than anyone else here — a crown needs at least two listeners and a lead worth keeping — and `/fm taste` measures how closely two members' libraries overlap. Niko indexes the artists it sees while serving the cards, so the boards belong to the people who actually use the bot instead of to whoever joined first.

### Link Without a Password
`/fm link` opens Last.fm's own approval page behind a **Connect Last.fm** button. Approving it sends the member back to `/api/lastfm/callback` on the website, which exchanges the approval for a session key and stores it against the account Last.fm names — the username is never typed, so a key can never be attached to an account it was not granted for. Nothing but a session key touches Niko, and `/fm unlink` forgets it.

### Slow Hosts Still Look Loaded
A card takes a moment to draw, so each command posts an animated placeholder first and edits it into the real image. The placeholders are generated at build time from the same layout constants as the cards — including the Last.fm wordmark — so nothing jumps, grows or moves when the finished card replaces the skeleton.

## Changes

### added
- `.fm` — now playing for you or any member, with sleeve, artist, album and a link to the track
- `.fm overview` — scrobble total, member-since date and top artists, albums and tracks for a period
- `.fm chart` — a ranked board of an artist, album or track top ten, with a period picker under the card
- `.fm nowplaying` — the same card for slash users, because Discord does not register a group's parent command
- `.fm artist` and `.fm album` — global listeners and scrobbles beside your own playcount
- `.fm recent` — now playing pinned above the last scrobbles, with album art and how long ago each one played
- `.fm whoknows`, `.fm crowns` and `.fm taste` — the server's own music boards
- `.fm link` — Last.fm's approval page, a website callback at `/api/lastfm/link` and `/api/lastfm/callback`, and the `session_key` column behind a verified link
- `.fm unlink` and `.fm update` — forget the linked account, or index more of a library for the server boards
- Five animated loading cards generated into the site's assets for the now playing, overview, chart, recent and detail shapes
- A rendered card for every answer: a 980px PNG built on the bot and posted through a media gallery

### improved
- Cards keep one 48px gutter and fixed title bands, so a long artist name clips instead of pushing the numbers off the card
- The Last.fm wordmark, album sleeves and proportion bars are drawn from the site's own assets, so a listing reads at a glance
- The period picker re-renders the card in place, so changing the window never posts a second message
- Wording in English, German, Spanish and French, including every command description
- Ranked rows compare against the largest value on the card, not against each other's column widths

### fixed
- `.fm recent` listed scrobbles without their sleeves — the artwork for each row is now downloaded before the card is drawn
- The scrobble card would have crashed on discord.py 2.7, where `MediaGalleryItem` sits at `discord.` rather than `discord.ui.`
- Last.fm API errors were retried, which lost the error code that tells a rate limit apart from an approval that was already used

## Chart data

```json
{
  "type": "metrics",
  "title": "The Listening Suite",
  "data": [
    {
      "label": "Commands",
      "value": "12",
      "detail": "one `.fm` group",
      "color": "#4a7fb5"
    },
    {
      "label": "Card shapes",
      "value": "5",
      "detail": "now playing to detail",
      "color": "#66866f"
    },
    {
      "label": "Board commands",
      "value": "3",
      "detail": "whoknows, crowns, taste",
      "color": "#d96545"
    }
  ]
}
```
