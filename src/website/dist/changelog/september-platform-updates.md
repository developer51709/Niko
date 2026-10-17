# September Platform Updates

- Date: 2026-09-21
- Version: 2.9.0
- Tags: dashboard, ai, tickets, music, website

A broad set of public improvements landed across Niko: richer ticket transcripts, a multimodal AI experiment, more reliable music playback, a redesigned dashboard experience, persistent giveaways and suggestions, and a refreshed public website with dynamic social previews.

## Highlights

### More Natural AI Conversations
The new opt-in Multimodal Conversation experiment can understand image attachments and transcribe voice messages before generating a reply, while safely falling back to text when media processing is unavailable.

### Richer Ticket Transcripts
Transcript pages and HTML downloads now render Discord custom emojis, stickers, and dynamic timestamps such as <t:1788800225:f> in a more faithful format.

### Dashboard & Website Refresh
Dashboard navigation and mobile layouts were refined, documentation was expanded, and public routes now receive route-specific Open Graph cards generated during the build.

### Reliable Long-Running Features
Giveaways and suggestions now restore their state from the main database at startup, while music nodes are rescanned periodically to keep playback available.

## Changes

### added
- Opt-in Multimodal Conversation AI experiment for image understanding and voice-message transcription
- Official update notification system with a configurable server notification channel
- Discord custom emoji and sticker rendering in ticket transcript pages and HTML downloads
- Dynamic Discord timestamp rendering in ticket transcripts
- Persistent suggestion configuration and voting buttons restored from the main database
- Automatic hourly Lavalink node rescans with a hardcoded fallback node catalog
- Additional economy SVG card API endpoints
- Community Policy page on the public website
- Route-specific Open Graph metadata and generated social preview cards

### improved
- Dashboard navigation consistency and mobile layout
- Dashboard page layout and visual polish
- Music connection reliability, autoplay, Spotify playback, and node recovery
- Giveaway persistence and startup restoration for MongoDB-backed data
- Onboarding setup handling and configuration persistence
- Poll command design and interaction flow
- Ticket transcript HTML download formatting
- Economy image-card font rendering, SVG output, and emoji support
- Documentation pages and public website frontend

### fixed
- Giveaways losing their live buttons after a restart or extended runtime
- Suggestion buttons and configuration not surviving process restarts
- Ticket transcript rendering for custom media and dynamic timestamps
- Lavalink connection failures and stale music nodes
- Broken SVG card and SVG endpoint output
- Status panel polling noise and retired image-model defaults

## Chart data

```json
{
  "type": "metrics",
  "title": "Release At a Glance",
  "data": [
    {
      "label": "Added",
      "value": "9",
      "detail": "new capabilities",
      "color": "#66866f"
    },
    {
      "label": "Improved",
      "value": "9",
      "detail": "upgraded systems",
      "color": "#4a7fb5"
    },
    {
      "label": "Fixed",
      "value": "6",
      "detail": "reliability issues",
      "color": "#d96545"
    }
  ]
}
```

## Commits
- ac102df Fixed the Open Graph image cards
- 33aaf12 Added dynamic Open Graph tags to the website
- 3153e28 Rebuilt the frontend
- bab665e Added a new Lavalink node
- ee44a5e Improved the music cog
- bc61e34 Released the new Multimodal Conversation AI experiment
- c46af7d Fixed the suggestion system persistence
- 25703ca Added a broadcast system for official updates and announcements
- 265bdb2 Added dynamic timestamp rendering inside ticket transcripts
- d8005db Added custom emoji and sticker rendering to ticket transcripts
- e561d84 Fixed the dashboards navbar
- a0bab78 Improved the dashboards mobile layout
- fb2f5aa Patched giveaway persistence for MongoDB compatibility
- d77779e Fixed several dashboard flaws
- b8e06a5 Improved the dashboard pages
- 3708207 Patched issues in the giveaway and onboarding cogs
- d58bb37 Redesigned the poll command
- bb523e3 Added a Community Policy page
- 5b34c7c Updated the documentation pages
- 3a52fc2 Added new economy card API endpoints
- df3ea25 Fixed an issue in the SVG endpoints
- 39b7340 Fixed an error in the SVG cards
- 9e3483e Replaced HTML entities with valid XML numeric character references in economy cards
