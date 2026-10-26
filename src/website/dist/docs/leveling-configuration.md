# Leveling Configuration Guide

Fine-tune the leveling system to match your server's needs.

## Basic Settings

### Enable/Disable
Toggle the entire leveling system on or off:

```
/leveling config toggle
```

When disabled, no XP is earned and level-up events don't fire.

### XP Multiplier
Adjust the rate at which members earn XP:

```
/leveling config multiplier <number>
```

- `1.0` = Normal speed
- `2.0` = Double speed
- `0.5` = Half speed

### XP Cooldown
Set a cooldown between XP gains from messages:

```
/leveling config cooldown <seconds>
```

Example: `/leveling config cooldown 60` gives 60 seconds between XP from messages.

## Announcements

### Level Up Channel
Set where level-up notifications are sent:

```
/leveling config levelupchannel <channel>
```

Placeholders in announcements:
- `{mention}` - Mention the member
- `{level}` - New level
- `{name}` - Display name
- `{guild}` - Server name

### Custom Level-Up Messages
Set a custom message template via the interactive panel:

```
/leveling panel
```

Navigate to **Announcements** and click **Edit Message**.

## Level Roles

### Assigning Roles
Give roles when members reach certain levels:

```
/leveling config levelrole <level> <role mention or id>
```

Example:
```
/leveling config levelrole 10 @Member
/leveling config levelrole 50 @Regular
/leveling config levelrole 100 @Veteran
```

You can also manage level roles from the interactive panel:

```
/leveling panel
```

Navigate to **Level Roles** to add or remove role assignments.

### Checking Progress
Members can check their stats with an image card:

```
/leveling rank
/leveling rank @user
```

## Card Customisation

The `/leveling rank` command renders a beautiful image card, and `/leveling leaderboard` links to the server's live leaderboard page. Server admins can customise the colours used by both through the management panel:

```
/leveling panel
```

Navigate to **Card Style** to edit:

- **Accent Colour** — used for borders, level numbers, and the progress bar (hex like `#d96545` or `ff5500`)
- **Background Top** — gradient top colour
- **Background Bottom** — gradient bottom colour
- **Reset Colours** — restore the default theme colours

Each server's colours are stored independently, so different servers can have unique card themes. Unless you pick your own colours, cards are drawn in the same graphite, steel and sage palette as the website, and a test keeps the two in sync. The public leaderboard page follows the website palette, so its rows stay readable in any theme.

## Resetting Leveling Data

To reset a member's leveling progress:

```
/leveling config resetuser <member>
```

> **Warning**: This permanently deletes that member's leveling progress!
