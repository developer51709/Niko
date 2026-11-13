# Music Activity — setup

The music control panel is an **experimental** Discord Activity. It is the page
behind the **Open Player** button on the now-playing panel: the button launches
the Activity in the voice channel (Discord's `LAUNCH_ACTIVITY` interaction), and
the Activity talks to the bot through `/api/activity/*`.

Activities are served inside Discord's proxy. Discord's **URL mapping only
supports the root prefix (`/`)**, so the panel has to live at the root of a
host, not under a path. This deployment already serves wildcard subdomains, so
it uses a dedicated `activities.` host.

## 1. DNS and environment

The wildcard record (`*.example.com`) already points at the service. No new DNS
record is required for `activities.example.com` as long as that wildcard is in
place and its certificate covers the label.

Set these in the bot's environment (see `env.example`):

| Variable | Value |
|---|---|
| `PUBLIC_URL` | The canonical apex, e.g. `https://example.com` |
| `SUBDOMAIN_ROUTING` | `true` (already required for the `dash.` host) |
| `MUSIC_ACTIVITY_ENABLED` | `true` — adds the Open Player button |
| `MUSIC_ACTIVITY_SUBDOMAIN` | `activities` (the default) |
| `MUSIC_ACTIVITY_ORIGIN` | Optional; only when the Activity is not on the derived host |

`https://activities.example.com/` then serves the panel, the hashed Vite
assets under `…/activity/assets/`, `…/activity/sdk.js`, its self-hosted fonts
and `/api/activity/*` is the control API. The panel is a second Vite entry
point (`web/activity/index.html`) that imports the site's own stylesheet, so
rebuild it with `npm run build:activity` whenever its source changes. Opening
the panel in a normal browser is safe: without Discord's iframe it shows
"open the player from Discord" and does nothing.

## 2. Discord Developer Portal

In [the Developer Portal](https://discord.com/developers/applications), open
**the same application as the bot** (the Activity and the bot must share an
application, because the now-playing button launches the app's Activity).

### Activities → Settings

- **Enable Activities**: on. Discord refuses to enable this until a URL mapping
  exists, so do step 3 first if the toggle is disabled.
- **Supported platforms**: Desktop and Mobile are enough; the panel is a plain
  web app.

### Activities → URL Mappings

Add exactly one mapping:

| Prefix | Target |
|---|---|
| `/` | `activities.example.com` |

Rules Discord enforces:

- The prefix must be `/` for an Activity's entry point, and the target must be
  a host name **without** a scheme, path or trailing slash. Do not enter
  `https://activities.example.com/`.
- Discord serves the Activity at
  `https://<application_id>.discordsays.com/`, and the `/` mapping forwards it
  to your target's root. Every relative path the panel requests (`/activity/…`,
  `/api/activity/…`) is forwarded to the same target host, so no second mapping
  is needed.
- If the Activity is on a host other than the subdomain, change both the target
  here and `MUSIC_ACTIVITY_ORIGIN`.

### OAuth2 → Redirects

Add `https://127.0.0.1` as a placeholder if it is not already present. The
Activity flow does not redirect there — the Embedded App SDK handles the return
— but Discord requires at least one redirect URI to be registered before
Activities can be enabled. Keep the site's real `/auth/callback` entry as well;
it is what the dashboard uses.

### Installation / Bot

The bot must be installed in the server with the **Use Activities** permission
(`USE_EXTERNAL_APPS` in the OAuth2 URL, shown as "Use Activities" in the
install screen) so members can start the Activity in a voice channel. The bot
also needs to be connected to that voice channel, because the panel controls the
guild's Lavalink player.

## 3. How the panel authenticates

1. The iframe loads `…/activity/sdk.js` — a locally bundled copy of
   `@discord/embedded-app-sdk` 2.4.0, because Discord's proxy blocks scripts
   from origins that have no URL mapping.
2. The SDK's `authorize` returns a one-time code for the scopes `identify` and
   `guilds`.
3. `POST /api/activity/token` exchanges the code server-side with
   `DISCORD_CLIENT_SECRET` and returns the access token (the SDK's
   `authenticate` needs it) plus a short-lived signed panel session.
4. Every panel API call sends that session as a bearer token. The server
   resolves the guild, the member and the voice channel through the bot's own
   cache; the `guild_id` and `channel_id` from the iframe are only lookup keys.
   A member outside the activity's voice channel is refused.
5. The site's session cookie is deliberately not used: it cannot cross into the
   Discord iframe, and a cookie-based API would be forgeable from a host page.

The panel's destructive controls follow the server's DJ role: skip, previous,
stop, loop, autoplay and volume are DJ-gated, while pause/resume stays open to
everyone, exactly like the now-playing panel and the text commands.

## 4. Verification checklist

1. `GET https://activities.example.com/` returns the panel HTML with
   `Content-Type: text/html`.
2. `GET https://activities.example.com/activity/sdk.js` returns JavaScript.
3. In Discord, start a track, press **Open Player**, and the Activity opens in
   the voice channel.
4. The panel lists the current track and channel; pause, skip and volume update
   both the panel and the channel's now-playing card.
5. As a member without the DJ role, the DJ-only buttons are disabled and the API
   answers `{"ok": false, "error": "dj_only"}`.
