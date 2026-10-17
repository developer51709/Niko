# Team Profiles Get Platform Cards and a Spotify Progress Bar

- Date: 2026-10-16
- Tags: team, profiles, notifier, twitch, added

Staff profiles now draw a real profile card for every supported platform instead of a bare link — GitHub, Bluesky, Twitch, YouTube, Reddit and X — the Spotify status keeps the custom-status card layout with a live track progress bar, and Twitch joins the notifier using the same application credentials those cards use, so the credentials earn their keep twice.

## Highlights

### Every Link Is a Profile Card
Find me elsewhere cards now show a platform badge, avatar, display name, handle, bio and headline stats for GitHub, Bluesky, Twitch, YouTube, Reddit and X. GitHub finally names itself instead of being an unlabelled card.

### Spotify Reads Like the Custom Status Card
A listening status uses the same card as a custom status, and adds a progress bar with elapsed and total track time that ticks in real time from Discord's track window.

### Twitch With Real Credentials
The notifier tracks Twitch channels going live and new broadcasts through an application (client-credentials) token from TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET, and the team profile cards reuse that same credentials-backed lookup.

## Changes

### added
- Team profile cards for Bluesky, Twitch, YouTube, Reddit and X, resolved server-side through /api/team/profile-card with a short cache so the public page cannot hammer third-party APIs
- A Twitch notifier platform that announces a channel going live and falls back to the newest broadcast, plus a Twitch button in the notifier setup panel
- TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET environment variables for Twitch app access, documented in the self-hosting guide and the notifier docs
- A progress bar with elapsed and total time on the Spotify status card, driven by the track start and end timestamps from Discord's presence

### improved
- The GitHub card carries a GitHub badge and label, and profile lookups it shares with the other platforms no longer depend on the visitor's browser CORS and rate limits
- X profiles are read from public endpoints instead of a paid API key, and Reddit falls back to its Atom feeds when its JSON API blocks a datacenter IP
