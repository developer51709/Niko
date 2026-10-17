# Twitch Live Alerts and a Dashboard Tab for Social Notifications

- Date: 2026-10-16
- Tags: dashboard, notifier, social, twitch, added

Twitch joins the social notifier, so a stream going live is announced in your channel through the same application credentials the team profile cards use — and every server now has a Notifications tab in the dashboard, where an account can be added by pasting a profile link, pointed at its own channel, ping role and custom message, tested, paused or resumed. The poll loop behind it got cheaper and more honest too: one request per creator no matter how many servers follow them, and an account that keeps failing is paused automatically instead of being retried forever.

## Highlights

### A Notifications Tab Per Server
Dashboard → your server → Notifications shows every followed account as a card with its channel, ping role, custom message and health, plus Send test, Pause, Resume and Remove — no slash command needed.

### Twitch Streams Go Live in Your Channel
Twitch is a first-class notifier platform: a channel going live gets a live alert, and when it is offline Niko falls back to its newest broadcast, thumbnail included. Public channel data is read through an application (client-credentials) token from TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET — no user login, and the same credentials power the Twitch profile cards on the team page.

### Paste a Link, Niko Does the Rest
Pasting a profile URL pre-selects the platform, and the account is validated against the real platform API before anything is stored. A re-added account is updated rather than duplicated, and the newest post is seeded silently so a new follow never dumps a back catalogue.

### Feeds That Go Quiet Now Say So
Each account records its last check and its consecutive failures. After five failed checks it is paused automatically and the channel is told once, with the command to resume it, instead of retrying a dead channel every five minutes.

## Changes

### added
- A per-server Notifications dashboard tab backed by /api/guild/<id>/notifier, sharing the cog's own platform validators so a follow added in the browser behaves exactly like one added in Discord
- Twitch as a notifier platform: a stream going live is announced as a live alert and falls back to the newest broadcast when the channel is offline, plus a Twitch button in the notifier setup panel
- TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET environment variables for Twitch app access, documented in the self-hosting guide and the notifier docs
- .notifier pause and .notifier resume for a single account, and a health line on .notifier list showing failed checks and the last check time
- A server-wide announcement switch with a default channel and default ping role, used by accounts that do not set their own
- Custom announcement messages with {account}, {platform}, {title} and {url} placeholders, validated before they are stored

### improved
- The poll loop groups followed accounts by platform and handle, so several servers following the same creator cost one API request per cycle with a bounded number of requests in flight
- A failed check now resets on success and counts toward an automatic pause, so a deleted channel or blocked IP no longer looks like a working feed
- Follow storage moved into utils/social/follows, giving the cog, the slash commands and the dashboard one validated source of truth with per-server limits enforced in both places
- The Twitch credentials that authenticate the notifier are the same application credentials the team profile cards use, so one Twitch app registration covers both features
