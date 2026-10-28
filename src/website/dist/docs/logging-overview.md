# Logging System

Niko's logging system provides comprehensive server event logging across ten categories, each assignable to its own channel. Every log entry is a Discord container with structured details, moderator attribution from the audit log, and jump links where they help.

## Logging Categories

| Category | Events Logged |
|----------|--------------|
| **Moderation** | Kicks, bans, unbans, timeouts applied/removed, nickname changes by staff |
| **AutoMod** | Niko's own filters (spam, links, bad words, mass mentions, anti-nuke, anti-raid) and rules fired by Discord's native AutoMod |
| **Messages** | Message edits, message deletions (images inline, other attachments re-uploaded), bulk clears and purges |
| **Channels** | Channel and thread create/delete/update, permission overwrite changes, webhook changes, pinned and unpinned messages |
| **Members** | Joins, leaves, boosts, avatar updates, role changes and nickname changes |
| **Captcha** | Captcha passes, failures, and verification kicks |
| **Invites** | Invite creation and deletion, plus which invite each new member used |
| **Roles** | Role create, delete, update (name, colour, hoist, mentionable, permissions) |
| **Server** | Server name/description/verification/icon/banner changes, emoji and sticker changes, integrations, scheduled events |
| **Voice** | Voice channel joins, leaves, and moves |

## Configuration

Open the interactive panel:

```
.logging
```

Select a category from the dropdown, then use the buttons to set its channel, clear it, or toggle it on or off. `Set All to…` and `Clear All` act on every category at once and ask for confirmation first.

The same settings are available in the dashboard under **Server settings → Logging destinations**, where each category is a channel picker with an enabled switch. Dashboard changes take effect immediately and are announced in the previously configured log channels.

### View Current Status

```
.logging status
```

Shows every category, its assigned channel, and whether it is enabled.

### Permissions

`Manage Server` is required to open the panel, change a category, or run `logging status`. To post logs, Niko needs `View Channel` and `Send Messages` in the destination channel. `Manage Webhooks` is optional: when it is granted, entries are posted through a dedicated webhook so they do not count against the bot's message limits; without it, entries are posted as Niko.

## Log Format

All entries use Discord components v2 containers:

- **Title** — Event type (e.g. "Message Deleted", "Member Joined")
- **Body** — Structured details: mentions, channel references, IDs, timestamps and reasons
- **Moderator attribution** — read from the audit log, matched by target and recency
- **Jump links** — deleted/edited messages, pins and overwrite changes link to the affected message or channel
- **MediaGallery** — image attachments from deleted messages are embedded directly
- **Section + Thumbnail** — member entries show the member's avatar
- **Files** — non-image attachments from deleted messages are re-uploaded (capped at 5 files, 2 MB each)

## Member Logging

- **Member Joined** — Account age, join method (invite code, vanity URL, or unknown) and invite usage
- **Member Left** — Roles at the time of departure and how long they had been in the server
- **Kick / Ban** — A removed member is logged once as a kick or ban with the moderator and reason, never also as a plain leave
- **Server Boosted / Boost Removed** — Boost count and server tier
- **Avatar Updated** — Old and new avatar, with the new avatar as a thumbnail
- **Role Changes** — Roles added and removed
- **Nickname Changes** — Old and new nickname, attributed to the staff member who changed it

## Message Logging

- **Message Edited** — Before/after content with a jump link
- **Message Deleted** — Author, channel, content and attachments:
  - Image attachments render in a **MediaGallery**
  - Non-image attachments are uploaded alongside the entry
  - Messages with no text show "*No text content*"
- **Messages Bulk Deleted** — A purge is logged once with the message count and the top authors, not one entry per message

## Invite Tracking

Niko caches invite usage on startup and after each join:

- **Invite Used** — Which invite was used, by whom, and total uses
- **Vanity Invite Used** — Vanity URL joins
- **Unknown Join Method** — Joins with no matching invite (OAuth2, Server Discovery, deleted invite)
- **Invite Created/Deleted** — Invite lifecycle events

## Disabling Categories

A category can be disabled from the panel or the dashboard. A disabled category sends nothing even if a channel is assigned, so a channel can be kept configured while the category is muted.

## Delivery And Rate Limits

- Each entry goes to its category's channel; a category without a channel is skipped.
- Sends are rate limited per channel, so a raid or mass delete cannot flood a log channel.
- A webhook that was deleted in Discord is detected, replaced and re-persisted automatically.
- Threads, announcement channels and categories cannot own a webhook; entries there are posted as Niko instead of being dropped.
- The logging config is cached for 30 seconds, and a failed config read keeps the last good copy rather than silently muting every category.
