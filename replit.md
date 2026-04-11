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
  - Interactive buttons/selects CAN be added to a LayoutView via `ActionRow` — subclass `discord.ui.Button` and use `self.view` in callback.
  - Exception: `automod` command uses `discord.ui.View` + `discord.Embed` because it predates the cv2 interactive pattern.
- **Pagination**: `from utils.paginator import PaginatedView, paginate` — shared cv2 paginator used by leaderboards and dev inspection commands. `paginate(lines, per_page)` chunks a list of strings; `PaginatedView(title, pages, icon_url)` renders with ◀ / ▶ nav buttons.
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
- Random 15–25 XP per message (with optional per-guild multiplier and cooldown)
- XP formula: `5 * level² + 50 * level + 100`
- Per-guild config in `data/level_config.json`: `xp_enabled`, `xp_multiplier`, `xp_cooldown`, `level_up_channel`, `level_roles`
- Automatic role assignment on level-up (`level_roles` dict: `{level: role_id}`)
- Commands: `!level` / `!rank`, `!level-leaderboard` / `!lvl-lb`
- **`!levelpanel`** (aliases: `!lvlpanel`, `!lp`) — interactive cv2 management panel with 4 sections:
  - **Overview** — all leveling settings at a glance
  - **XP Settings** — toggle XP, edit multiplier + cooldown via modal
  - **Announcements** — set level-up channel (ephemeral ChannelSelect) + custom level-up message with `{mention}` `{level}` `{name}` `{guild}` placeholders (modal); reset to default
  - **Level Roles** — add (two-step: modal → ephemeral RoleSelect) / remove (ephemeral Select of current assignments)
- **Custom level-up messages**: stored as `level_up_message` in `data/level_config.json`; falls back to the café MESSAGES table if not set
- Config group: `!levelconfig` → subcommands: `toggle`, `multiplier`, `cooldown`, `levelupchannel`, `levelrole`, `resetuser`

### Moderation
- Mod log channel stored via `moderation_utils.py`
- AutoMod config (antispam, antilink, badwords, massmention, thresholds) via `!automod` interactive dashboard
  - Dashboard sections: Overview, Message Filter, Anti-Nuke, Anti-Raid, Ext. App Raid, Whitelist
  - All sections use cv2 LayoutView; toggle buttons + modals for all thresholds
- **AutoMod Whitelist**: Users and roles exempt from all automod checks
  - Dashboard "Whitelist" section has ➕/➖ buttons that open ephemeral `UserSelect`/`RoleSelect` dropdowns
  - `whitelist_users` / `whitelist_roles` stored in `data/modconfig.json` per guild
  - Also manageable via `!whitelist add/remove user/role` text commands
  - `is_whitelisted()` check runs at the top of every `on_message` handler
- Full bilingual EN/DE `MESSAGES` table covering all commands in `moderation.py`
- Commands: kick, ban, unban, warn, warnings, clearwarnings, mute, tempmute, unmute, clear, purge, slowmode, lock, unlock, nick, setmodlog, automod, badwords, whitelist

### External App Raid Protection (`automod.py`)
- Detects raids driven by external tools (selfbots, raid apps) by tracking `on_interaction` events from recently-joined members
- Config: `antiraid_ext` — `interaction_threshold`, `interaction_window`, `join_age_limit`, `raider_action`, `operator_action`
- **Operator identification**: snapshots invite use counts on every `on_member_join`, then diffs against the current counts at detection time to find which invite saw the biggest spike and who created it
- Invite cache populated on `on_ready`, `on_invite_create`, `on_invite_delete`, and every join event
- Response: punishes raiding accounts (kick/ban), then takes separate action on the identified operator (notify/kick/ban)
- Dashboard: "Ext. App Raid" section with toggle + threshold modal accessible from `!automod`

### Giveaway System
- Tables: `giveaways` (message_id, channel_id, guild_id, prize, winners_count, end_time, ended, host_id) and `participants` (message_id, user_id) in `data/database.db` via `bot.cxn`
- Persistent across restarts: `GiveawayPersistentView` registered via `bot.add_view()` in `cog_load` — only the two main-message buttons have fixed `custom_id`s (`giveaway_system_join`, `giveaway_system_manage`)
- Active giveaway messages show **Join** + **Manage** buttons. Manage opens an ephemeral management panel (host or server admin only) containing: End Giveaway, Select Random, and Participants buttons
- Management panel buttons are NOT persistent (ephemeral, created fresh per click); they use `interaction.response.edit_message` to update the panel in-place
- Participants button edits the ephemeral panel to a `PaginatedView` (15 per page, ◀/▶ nav)
- Ended messages use `_build_ended_view()` (LayoutView, no buttons); `end_giveaway()` edits the original public message
- Full bilingual EN/DE + normal/cafe personality MESSAGES table; `msg(ctx_or_interaction, key)` and `_guild_msg(guild, key)` helpers for task callbacks
- Commands: `.giveaway start <duration> <winners> <prize>`, `.giveaway reroll <message_id>`
- Background task (`check_giveaways`) fires every 15 s

### Persistent Views (Tickets & Onboarding)
- All persistent interactive components have `custom_id` set so Discord can re-dispatch interactions after restarts
  - `OpenTicketBtn`: `custom_id=f"open_ticket_{guild_id}"`
  - `CloseTicketBtn`: `custom_id="ticket_close"`
  - `DeleteTicketBtn`: `custom_id="ticket_delete"`
  - `AgreeButton` (onboarding): `custom_id=f"rules_agree_{guild_id}"`
  - `RoleMenuSelect` (onboarding): `custom_id=f"role_menu_select_{guild_id}"`
- View registration moved to `setup()` functions (not `on_ready`) since cogs load inside bot's `on_ready`
- Onboarding: `load_all_configs()` in `onboarding_config.py` iterates all guild JSON files to re-register views

### Music
- Lavalink-based music via wavelink
- Nodes loaded from AjieBlogs API on startup

## External Dependencies

### Discord API
- **discord.py**: Primary bot framework
- **Requires**: `DISCORD_BOT_TOKEN` environment secret

### AI Integration
- **OpenAI** via Replit's built-in OpenAI integration (`AI_INTEGRATIONS_OPENAI_API_KEY`, `AI_INTEGRATIONS_OPENAI_BASE_URL`)
- Local TinyLlama model is lazy-loaded only if `USE_OPENAI = False` in `bot.py`

### System Libraries
- **psutil**: System resource monitoring
- **requests**: HTTP client
- **beautifulsoup4**: HTML parsing for notifier cog (Twitter/TikTok scraping)
- **deep-translator**: Google Translate API wrapper for translate_context cog
- **langdetect**: Language detection for translator utility

### Data Storage
- **Local filesystem**: JSON files only, no external database
  - `memory.json`: AI memory and favorability
  - `economy_data/*.json`: Per-user economy state
  - `data/levels.json`: Per-guild leveling data
  - `data/mod_config.json`: Per-guild moderation config
  - `data/warnings.json`: Per-guild warning records

## Migration Notes (Replit Import)
- Removed top-level model loading from `bot.py` (was downloading 600MB TinyLlama on every start)
- `utils/ai_local.py` now lazy-loads the local model only when actually called
- Replaced incompatible `googletrans` with `deep-translator` + `langdetect` to avoid httpx version conflicts
- All 33 cogs load successfully on startup
