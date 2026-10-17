# Economy Items, Leveling Cards & Subcommands

- Date: 2026-09-08
- Version: 2.8.0
- Tags: economy, leveling, shop, image-cards

The economy shop expanded with four new consumable items that affect gameplay — Rigged Coin, Streak Insurance, Double Down Token, and Lucky Horseshoe — plus daily streak milestone bonuses at 7, 14, 30, 60, and 90 days. The leveling system now renders rank cards and leaderboards as customizable image cards, and all leveling commands live under a single `/leveling` group with subcommands.

## Highlights

### New Shop Items
Four new consumables: Rigged Coin (60/40 coinflip odds), Streak Insurance (protects daily streak for one missed day), Double Down Token (1.5x gambling payout), and Lucky Horseshoe (+10% work reward).

### Leveling Image Cards
Rank cards and the leaderboard now render as styled images with avatar, level, XP bar, and rank. Server admins can customize the card accent color and background gradient.

### Leveling Subcommands
All leveling commands reorganized under `/leveling` with `rank`, `leaderboard`, `panel`, and `config` subcommands. The leaderboard now has interactive pagination buttons.

### Daily Streak Milestones
Hitting 7, 14, 30, 60, or 90-day daily streaks now awards bonus items from the shop (Espresso Shots, Lockpicks, Lucky Charms, Rob Shields) along with a coin bonus.

## Changes

### added
- Coinflip command with heads/tails call and double-or-nothing payout
- Rigged Coin shop item — gives 60/40 coinflip odds for one use
- Streak Insurance shop item — protects daily streak if you miss one day
- Double Down Token shop item — next gambling win pays 1.5x
- Lucky Horseshoe shop item — next work reward gets +10%
- Daily streak milestone bonuses at 7/14/30/60/90 days with item rewards
- Image card rendering for `/leveling rank` with customizable accent and background
- Image card rendering for the leveling leaderboard
- Inventory display as an image card in the shop command
- Twemoji emoji rendering in economy card images
- Pagination buttons (◀ ▶) on the leveling leaderboard
- Card customization fields in the database: card_accent, card_bg_top, card_bg_bottom

### improved
- Leveling commands restructured as `/leveling rank`, `leaderboard`, `panel`, `config` subcommands
- Shop command visual layout with better font rendering on economy image cards
- Crime and rob commands now check for gambling_boost effect for 1.5x payout
- HTML download format for ticket transcripts
- Dashboard UI refinements

### fixed
- Command name conflicts between leveling and other cogs
- Missing import in leveling cog after image card addition
- Duplicate command alias in leveling system
- Command name conflict in the gambling cog

## Chart data

```json
{
  "type": "bar",
  "title": "New Shop Items & Their Effects",
  "data": [
    {
      "label": "Rigged Coin",
      "value": 3000,
      "color": "#c9a84c"
    },
    {
      "label": "Streak Insurance",
      "value": 4000,
      "color": "#4a7fb5"
    },
    {
      "label": "Double Down Token",
      "value": 5000,
      "color": "#d96545"
    },
    {
      "label": "Lucky Horseshoe",
      "value": 2500,
      "color": "#66866f"
    }
  ]
}
```

## Commits
- 41d86fb Expanded the gambling and economy system
- bd6a09c Added image cards to the leveling system
- 5307bb1 Moved the leveling commands to the levels subcommand
- dafd224 Added an image card to the inventory command
- 49fc83b Added emoji rendering to the shop command
- 0aca6ba Improved the shop command
- 30c9735 Added better font rendering to the economy system image cards
- 2b96835 Fixed a command name conflict
- 158ad8f Fixed a command name conflict in the gambling cog
- d465598 Fixed a missing import
- 1f24ffb Fixed a duplicate command alias
