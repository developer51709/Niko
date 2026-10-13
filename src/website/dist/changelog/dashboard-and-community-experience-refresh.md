# Dashboard & Community Experience Refresh

- Date: 2026-10-10
- Tags: dashboard, website, transcripts, moderation, staff, accessibility

A substantial platform update across Niko’s dashboard, public website, Discord integrations, and core bot systems. Guild admins get a redesigned server-profile editor and clearer analytics, while communities benefit from richer Discord-aware transcripts, expanded staff tools, and reliability improvements throughout moderation and data handling.

## Highlights

### Server Profile Studio
Guild admins can preview and edit Niko’s server-specific name, bio, font, color effects, avatar, and banner in one focused editor. Image changes are applied to the Discord guild profile, and the dashboard resolves current images from Discord’s CDN instead of storing copies.

### Discord-Aware Transcript Viewer
Transcript pages and HTML exports better reflect Discord conversations, including resolved user, role, and channel mentions, custom emoji, stickers, timestamps, media, and richer message layouts.

### A More Complete Public Experience
The responsive website adds refined navigation, expanded documentation and command references, public team profiles, staff application flows, and clearer support and policy destinations, with polished route metadata and social previews.

### More Resilient Bot Operations
Core bot updates improve database-backed persistence, moderation and automod workflows, ticket handling, staff tooling, and live dashboard statistics while tightening validation around server-scoped changes.

## Changes

### added
- Interactive server-profile preview and editors for guild-specific display name, bio, typography, color effects, avatar, and banner
- Discord guild-profile image updates with avatar and banner CDN URL resolution; profile image data is excluded from persisted profile records
- Server pulse analytics with recent message and member activity plus server layout counts
- Public team directory and staff profile pages with Discord-synced identity and editable public profile details
- Guild staff-opening management and Discord-verified application forms with role eligibility checks
- Shared Discord text resolver for user, channel, and role mentions in transcript views and exports
- Route-aware social metadata, generated preview artwork, and expanded public documentation and command pages
- Dashboard controls for server AI identity and configurable experimental AI features

### improved
- Dashboard and public navigation, responsive layouts, server settings, and profile editing flow
- Ticket transcript rendering and export fidelity for mentions, emoji, stickers, timestamps, attachments, and Discord message content
- Live public bot statistics and profile data sourced from the running bot and Discord where available
- Database-backed persistence and startup recovery across bot features, including moderation, economy, tickets, and community tools
- Automod reporting and review workflows, including scam-image detection and false-positive feedback
- Localization, request validation, access checks, and error handling across dashboard and bot interactions

### fixed
- Dashboard TypeScript errors in the server-profile editing state
- Stale CDN image previews and accidental profile-image re-uploads during text-only profile saves
- Transcript mention and rich-content rendering gaps across online pages and downloadable HTML
- Dashboard and bot reliability issues surfaced while improving server configuration and persistence
