# Roleplay, Music & Status Rotation

- Date: 2026-09-05
- Version: 2.5.0
- Tags: roleplay, music, status, social

The roleplay cog was completely rewritten to use nekos.best API GIFs with CV2 layout messages and a persistent 'hug back' button. The music cog was restructured with a ghost queue feature and fixed autoplay/Spotify playback. A status message rotation system was added with a configurable timer.

## Highlights

### Roleplay Rewrite
The roleplay cog now fetches SFW reaction GIFs from nekos.best, renders them in styled CV2 containers, and includes a 'hug back' button that persists across restarts. A single user context menu replaces individual action menus to stay under Discord's 15-command cap.

### Music Ghost Queue
A new ghost queue feature lets songs be queued even when nothing is currently playing. Autoplay and Spotify playback were also fixed.

### Status Rotation
The bot now rotates through configurable status messages on a timer (default 30s interval), with activity types and a VR device presence.

## Changes

### added
- Status message rotation with configurable interval and activity types
- Persistent status panel command for the support server (owner only)
- Roleplay block feature to prevent specific users from being targeted
- Ghost queue feature — queue songs even when nothing is playing
- User context menu for roleplay actions (replaces per-action menus)
- YouTube channel name validation for notification system

### improved
- Roleplay cog complete rewrite — nekos.best GIFs, CV2 layouts, persistent buttons
- Social media notification emoji formatting (Bluesky, Reddit, TikTok, Twitch icons)
- Music node connection system and autoplay reliability
- Spotify playback quality
- Music cog restructured with better error handling

### fixed
- Status rotator startup errors and activity conflicts
- on_ready event error handling and reliability
- Lavalink connection bug
- Roleplay prefix command handling
- Bluesky and Reddit notification delivery issues

## Commits
- 0c58178 Redesigned the roleplay cog
- 6c4ee09 Fixed the roleplay prefix commands
- f1f8591 Added a roleplay block feature
- e01e3e4 Added status message rotation
- 5e63e1d Added a persistent status panel
- ae7501a Restructured the music cog
- 526813e Added a new ghost queue feature to the music cog
- 6524da1 Improved the music node connection system, fixed the autoplay, and fixed the Spotify playback
- 4264677 Fixed a lavalink connection bug
- d62ead8 Improved the social media notification system's emojis
- 0f0305d Improved the social media notification formatting
- 42069d4 Added proper channel name validation to the YouTube notification system
