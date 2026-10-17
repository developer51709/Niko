# Database Migration to MongoDB

- Date: 2026-09-03
- Version: 2.7.0
- Tags: database, mongodb, migration, infrastructure

Every major system has been migrated from SQLite to MongoDB. The migration covered economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and the blacklist — with a custom interpreter that translates SQLite-style writes to MongoDB operations.

## Highlights

### Full MongoDB Migration
Economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and blacklist now all store data in MongoDB instead of SQLite.

### Slash Command Sync Safeguard
A new check prevents redundant Discord API calls when all commands are already registered, reducing rate-limit issues on startup.

### Proxy Integration
A new proxy manager reduces downtime on shared hosting environments by routing API requests through a proxy layer.

## Changes

### migrated
- Economy system — balances, banks, jobs, achievements, inventory
- Leveling system — XP, levels, role rewards, card customization
- Moderation system — warnings, mutes, automod config
- Ticket system — panels, transcripts, support roles
- Birthday system — dates, channels, messages
- AFK system — status, timestamps
- Sticky messages — content, channels
- Blacklist — users, words, filters

### added
- MongoDB interpreter that translates SQLite-style writes to proper MongoDB operations
- Proxy manager for shared hosting reliability
- Slash command sync safeguard to prevent redundant API calls
- Context menu command support in the sync utility

### fixed
- MongoDB interpreter not translating all SQLite write patterns correctly
- Economy interest calculation after migration
- Birthday system data persistence
- Several database connection issues across various cogs
- Leveling database initialization issue

## Chart data

```json
{
  "type": "donut",
  "title": "Systems Migrated to MongoDB",
  "centerLabel": "8 systems",
  "data": [
    {
      "label": "Economy",
      "value": 1,
      "color": "#d96545"
    },
    {
      "label": "Leveling",
      "value": 1,
      "color": "#66866f"
    },
    {
      "label": "Moderation",
      "value": 1,
      "color": "#4a7fb5"
    },
    {
      "label": "Tickets",
      "value": 1,
      "color": "#c9a84c"
    },
    {
      "label": "Birthdays",
      "value": 1,
      "color": "#b07cc6"
    },
    {
      "label": "AFK",
      "value": 1,
      "color": "#e0976e"
    },
    {
      "label": "Sticky Msgs",
      "value": 1,
      "color": "#7ca898"
    },
    {
      "label": "Blacklist",
      "value": 1,
      "color": "#8c918e"
    }
  ]
}
```

## Commits
- c07f9b1 Fixed the MongoDB interpreter to properly translate all SQLite database writes
- 0d3aca5 Migrated the blacklist to the main database
- 954ebac Migrated the birthday system to the main database
- 5013d54 Migrated the warns and mutes to use the main database
- f29c217 Migrated the afk system to the main database
- 5732b48 Migrated the sticky messages to use the main database
- b0524f1 Migrated the ticket system to the main database
- 70e6d7a Fixed the sync util to support context commands and slash groups
- 2c01817 Added a safeguard to prevent slash command syncs when all commands are already present
- 121afcf Added a proxy integration to reduce downtime on shared hosting
- 9f2f1fd Fixed several database issues across various cogs
