# Leveling System Overview

Niko's leveling system rewards members for participating in your server with XP, level-ups, and beautiful image cards.

## How Leveling Works

### Earning XP
Members earn XP when they send messages in enabled channels. Each message earns a random amount of XP (15–25 base), multiplied by the server's XP multiplier.

### Level Progression
Each level requires more XP than the last, following a quadratic curve:

| Level | XP Required |
|-------|-------------|
| 1 | 155 |
| 5 | 475 |
| 10 | 1,100 |
| 25 | 4,475 |
| 50 | 15,100 |

### XP Formula
The XP needed for each level uses a quadratic formula:
```
XP for next level = 5 × level² + 50 × level + 100
```

This means early levels are quick to earn, but higher levels take progressively more effort.

## Commands

### Check Your Level
```
/leveling rank
/leveling rank @user
```

This renders a beautiful image card showing:
- Your avatar and display name
- Current level with a large level badge
- XP progress bar
- Server rank

### View Leaderboard
```
/leveling leaderboard
```

Shows a paginated image leaderboard of the top leveled members with avatars, levels, and XP. Use the ◀ and ▶ buttons to navigate pages.

### Open Management Panel
```
/leveling panel
```

Opens the interactive CV2 management panel for server admins. This panel has sections for:
- **Overview** — all settings at a glance
- **XP Settings** — toggle, multiplier, cooldown
- **Announcements** — level-up channel and custom message
- **Level Roles** — assign roles at specific levels
- **Card Style** — customise the colours used in level cards

## Configuration

### Enable/Disable Leveling
```
/leveling config toggle
```

### Set XP Multiplier
Adjust how fast members level:

```
/leveling config multiplier <value>
```

### Set Cooldown
Prevent XP spam with cooldowns:

```
/leveling config cooldown <seconds>
```

### Level Up Channel
Choose where level-up announcements appear:

```
/leveling config levelupchannel <channel>
```

### Custom Level Up Messages
Level-up announcements use a customisable template:

```
/leveling config
```

Use `{mention}`, `{level}`, `{name}`, and `{guild}` in your message.

## Level Rewards

### Level Roles
Assign roles at specific levels:

```
/leveling config levelrole <level> <role>
```

When a member reaches the configured level, the role is automatically assigned.

## Card Customisation

The `/leveling rank` and `/leveling leaderboard` commands render image cards with Pillow. Server admins can customise the colours through the management panel:

- **Accent Colour** — controls borders, level numbers, and the progress bar
- **Background Top** — gradient top colour
- **Background Bottom** — gradient bottom colour
- **Reset Colours** — restore café defaults

Each guild's colours are stored independently, so different servers can have unique card themes.

## Leveling Tips

1. **Enable in all channels**: More channels = more XP opportunities
2. **Set reasonable multipliers**: Don't make leveling too fast or slow
3. **Use cooldowns**: Prevent XP grinding abuse
4. **Celebrate milestones**: Level-up announcements build engagement
5. **Reward participation**: Leveling encourages activity
6. **Customise card colours**: Match your server's branding
