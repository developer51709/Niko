# UwU Lock Rebuilt & Starboard Persistence

- Date: 2026-09-25
- Version: 2.11.0
- Tags: uwulock, starboard, database, fun, social

The UwU Lock command has been completely rebuilt around the main database with immediate webhook reposts, reliable message transforms, and full Starboard integration — with proper author attribution that persists cleanly across restarts.

## Highlights

### Instant Webhook Transforms
Locked users' messages are now deleted and immediately reposted via a shared per-channel webhook with their display name and avatar, including attachments, embeds, and stickers, with thread support and a guard against double-processing.

### Real Author on the Starboard
When a uwu-ified webhook message is starred, the Starboard resolves the original author from persistent attribution and renders their name, avatar, and original timestamp — not the webhook — in a clean Section with Thumbnail layout.

### Survives Restarts
Both UwU Lock rules and Starboard configuration now live in the main database, loaded on startup via cog_load with automatic migration from the legacy JSON files and stale-webhook healing.

## Changes

### added
- Main-database tables uwulock_config and uwulock_messages for lock rules and author attribution
- Main-database tables starboard_config and starboard_messages for channel, threshold, emoji and post mappings
- Automatic migration of legacy data/uwulock.json and data/starboard.json into the primary database with .migrated backups
- Per-channel webhook reuse with stale-webhook detection via fetch and shared-webhook protection on removal
- Thread-aware webhook sending with AllowedMentions.none and wait:true repost handling
- UwU attribution storage (author name, avatar, original timestamp) for every transformed message
- Starboard Section + Thumbnail rendering for uwu-locked messages with correct original author credit
- Explicit UwU lock hook in events.on_message before AI triggers with a 2,000-entry dedup guard and fallback listener

### improved
- UwU Lock now deletes the original message immediately instead of queuing for a background task
- Attachment, embed, and sticker handling with text truncation and text-only fallback on send failure
- Permission checks for Manage Messages and Manage Webhooks with localized failure messaging
- Starboard reaction handling now distinguishes webhook reposts via database attribution
- Starboard message edits and sends now use AllowedMentions.none for cleaner output
- Webhook Channel resolution for threads via parent channel with robust create_webhook flow

### fixed
- UwU Lock not creating the webhook or showing any sign it saw the message
- Webhook created but original message not deleted and no new message sent
- UwU transforms silently failing due to queue delay and background-task errors
- Starboard not displaying correct author for uwu-locked webhook messages
- Starboard and UwU Lock losing all state after a restart despite being stored
- Stale or deleted webhooks leaving lock rules in a broken state

### migrated
- UwU Lock from data/uwulock.json file storage to the primary database
- Starboard configuration and starred post IDs from data/starboard.json to the primary database

## Chart data

```json
{
  "type": "metrics",
  "title": "Release At a Glance",
  "data": [
    {
      "label": "Added",
      "value": "8",
      "detail": "new persistence features",
      "color": "#66866f"
    },
    {
      "label": "Improved",
      "value": "6",
      "detail": "reliability upgrades",
      "color": "#4a7fb5"
    },
    {
      "label": "Fixed",
      "value": "6",
      "detail": "workflow bugs",
      "color": "#d96545"
    }
  ]
}
```
