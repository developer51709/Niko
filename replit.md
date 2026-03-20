# Niko Discord Bot

## Overview

Niko is a Discord bot with a cozy café personality, bilingual EN/DE support, and a full feature set including economy, leveling, music, moderation, roleplay, info, and AI utility commands. All cogs reside under `src/cogs/`.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Discord.py with Cogs pattern**: Modular cog system under `src/cogs/`. All 37+ cogs load on startup.
- All cogs live in `src/cogs/` (NOT a separate `cogs/` root directory).
- Logging via `utils/logging.py` custom logger (`from utils import logging as log`).

### UI / Response System
- **Components v2 (cv2) LayoutView**: All user-facing responses use `discord.ui.LayoutView` instead of `discord.Embed`.
  - Pattern: `view = discord.ui.LayoutView()` → `view.add_item(discord.ui.Container(discord.ui.TextDisplay(...)))` → `await ctx.send(view=view)`
  - Thumbnail accessory: wrap `TextDisplay` in `discord.ui.Section(..., accessory=discord.ui.Thumbnail(url))`
  - Images/GIFs: `view.add_item(discord.ui.MediaGallery(discord.ui.MediaGalleryItem(url=...)))`
  - Link buttons: `view.add_item(discord.ui.ActionRow(discord.ui.Button(style=discord.ButtonStyle.link, url=...)))`
  - Exception: `automod` command uses `discord.ui.View` + `discord.Embed` because it has interactive toggle buttons that edit the message.
- **Bilingual EN/DE**: Every cog has a `MESSAGES` dict with `normal`/`cafe` personalities and `en`/`de` languages. `get_lang(ctx)` checks `guild.preferred_locale`. 4-level fallback in `msg()`.
- **Personality**: `PERSONALITY = "cafe"` across all cogs for cozy café-themed text.

### Critical Design Notes
- Do NOT use `discord.TextChannel | None` union type hints — use `= None` default instead.
- The `edit` tool can fail with "did not appear verbatim" for files with special chars (é, ü, ☕). Use the `write` tool to fully rewrite such files.
- `discord.ui.LayoutView` and `discord.ui.View` cannot be mixed in the same message send.
- `discord.ui.Section` requires an accessory — if no image, use a plain `TextDisplay` as fallback.

### AI/LLM Integration
- **OpenAI API** via Replit integration (`python_openai_ai_integrations`)
- Memory stored in `memory.json` with `users`, `favorability`, `conversations` keys.

### Economy System
- **Per-user JSON files**: `economy_data/{user_id}.json`
- Starting balance: 100 coins
- Shop items: Coffee (50), Cake (120), Café Badge (300)
- Commands: balance, deposit, withdraw (supports "all"), daily, work, crime, rob, shop, buy, inventory, leaderboard, give, net_worth

### Leveling System
- XP stored in `data/levels.json` per guild/user
- Random 15–25 XP per message
- XP formula: `5 * level² + 50 * level + 100`
- Commands: `!level` / `!rank`, `!level-leaderboard` / `!lvl-lb`

### Moderation
- Mod log channel stored via `moderation_utils.py`
- AutoMod config (antispam, antilink, badwords, massmention, thresholds) via `!automod` interactive UI
- Commands: kick, ban, unban, warn, warnings, clearwarnings, mute, tempmute, unmute, clear, purge, slowmode, lock, unlock, nick, setmodlog, automod, badwords

### Music
- Lavalink-based music via wavelink
- Nodes loaded from AjieBlogs API on startup

## External Dependencies

### Discord API
- **discord.py**: Primary bot framework
- **Requires**: `DISCORD_BOT_TOKEN` environment secret

### System Libraries
- **psutil**: System resource monitoring
- **requests**: HTTP client

### Data Storage
- **Local filesystem**: JSON files only, no external database
  - `memory.json`: AI memory and favorability
  - `economy_data/*.json`: Per-user economy state
  - `data/levels.json`: Per-guild leveling data
  - `data/mod_config.json`: Per-guild moderation config
  - `data/warnings.json`: Per-guild warning records
