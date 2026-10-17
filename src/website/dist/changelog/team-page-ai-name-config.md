# Team Profiles & Custom AI Names

- Date: 2026-09-22
- Version: 2.10.0
- Tags: team, staff, dashboard, ai, website

Niko's public website now introduces the people behind the bot, while server owners can give their AI a custom name and manage its experimental capabilities from the dashboard.

## Highlights

### Meet the Niko Team
The new Team page showcases owners, developers, moderators, support staff, and other persisted staff roles with Discord-synced identities, presence, activities, bios, and profile pages.

### Choose Your AI's Name
Server administrators can configure the AI's display name from the dashboard or the AI configuration command. The chosen name is used for mention detection and reply identity in that server.

### Staff Public Listings
Staff members can customize their public bio, banner, and visibility while their name and avatar remain synchronized with Discord.

## Changes

### added
- Public Team page with persisted staff roles and linked staff profiles
- Discord-synced staff presence, current activities, Spotify, streaming, and custom status display
- Staff self-service controls for public bio, banner, and Team page visibility
- Configurable per-server AI name in the dashboard and AI configuration command
- Dashboard controls for AI Actions, Better Context, and Multimodal Conversation experiments
- Learn-more dialogs explaining each AI experiment

### improved
- Dashboard staff workspace navigation and responsive layout
- Team profile cards and profile-page activity presentation
- AI configuration persistence through the shared database
- Public page metadata and favicon handling during the website build

### fixed
- Team presence labels showing online staff as away
- Spotify and streaming activities being hidden behind custom statuses
- Staff profile updates being rejected for authorized owners
- Staff profile avatars being clipped by profile banners

## Chart data

```json
{
  "type": "metrics",
  "title": "Release At a Glance",
  "data": [
    {
      "label": "Team",
      "value": "1",
      "detail": "new public experience",
      "color": "#66866f"
    },
    {
      "label": "AI",
      "value": "4",
      "detail": "new configuration controls",
      "color": "#d96545"
    },
    {
      "label": "Profiles",
      "value": "3",
      "detail": "public staff controls",
      "color": "#4a7fb5"
    }
  ]
}
```
