# Niko Discord Bot

## Overview

Niko is a Discord bot with a cozy café personality, bilingual EN/DE support, and a full feature set including economy, leveling, music, moderation, roleplay, info, and AI utility commands. All cogs reside under `src/cogs/`.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Discord.py with Cogs pattern**: Modular cog system under `src/cogs/`. All 50+ cogs load on startup.
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
- **Trilingual EN/DE/ES**: Every cog has a `MESSAGES` dict with `normal`/`cafe` personalities and `en`/`de`/`es` languages. `get_lang(ctx)` checks `guild.preferred_locale` (returns `"de"` if locale starts with `de`, `"es"` if starts with `es`, else `"en"`). 4-level fallback in `msg()` so missing es keys gracefully fall back to en.
- **Hybrid (slash + prefix) commands**: Several commands use `commands.hybrid_command` so they work both as `!play` and `/play`. Slash sync runs as a background task on startup via `_run_slash_sync()` in `bot.py`. NOTE: hybrid command `description=` must be ≤100 chars; the longer trilingual JSON string lives in `help=`. `music.play` has a `_play_autocomplete` that ytsearches with a 30s in-memory cache.
- **Personality**: `PERSONALITY = "cafe"` across all cogs for cozy café-themed text.

### Rate Limiting (`src/utils/ratelimit.py`)
- Async rolling-window `RateLimiter(max_calls, per_seconds)` with `try_acquire(key)` returning `True` if allowed.
- Three shared instances:
  - `log_channel_limiter` (4 / 5 s per `(guild_id, channel_id)`) — used in `logging_cog.log_event` to throttle bursts.
  - `welcome_limiter` (3 / 5 s per `guild_id`) — used in `onboarding.on_member_join` for the welcome message send.
  - `role_assign_limiter` (5 / 5 s per `guild_id`) — used in `onboarding.on_member_join` before each autorole assignment, with `discord.HTTPException` try/except.

### Event-Loop Hygiene
- AI calls (`generate_reply_*`) run via `loop.run_in_executor(None, generate_reply, ...)` in `src/bot.py`, so the underlying `requests.*` calls in `utils/ai_*` do not block.
- Cog-level `requests.*` calls converted to `await asyncio.to_thread(requests.get, ...)`: `cuteanimals.py` (cuteanimal/cat/dog), `nsfw.py` (rule34/gelbooru), and the `realbooru` command's `search_realbooru` / `get_post_details` helpers.
- `WebhookHandler.emit` in `src/utils/logging.py` offloads `requests.post` to a 2-worker `ThreadPoolExecutor` so logging never blocks the event loop.

### Critical Design Notes
- Do NOT use `discord.TextChannel | None` union type hints — use `= None` default instead.
- The `edit` tool can fail with "did not appear verbatim" for files with special chars (é, ü, ☕). Use the `write` tool to fully rewrite such files.
- `discord.ui.LayoutView` and `discord.ui.View` cannot be mixed in the same message send.
- `discord.ui.Section` requires an accessory — if no image, use a plain `TextDisplay` as fallback.

### Emoji System — Application Emojis
- All bot emojis are registered as **Application Emojis** (owned by the bot itself, not any guild). No emoji server needed.
- `src/utils/emoji_sync.py` handles the full lifecycle:
  1. Parses `src/config/emojis.py` to find all `<:name:id>` / `<a:name:id>` references
  2. Downloads each image to `src/assets/emojis/` (cached — skips if already on disk)
  3. Fetches the bot's existing application emojis via `bot.fetch_application_emojis()`
  4. Uploads any missing ones via `bot.create_application_emoji()`
  5. Rewrites `src/config/emojis.py` with the live application-emoji IDs
- Runs automatically in the background on every `on_ready` (non-blocking)
- Dev commands (developer-only, accessible in any guild):
  - `.syncemojis` — manual re-sync with a stats report
  - `.appemojis` — paginated list of all registered application emojis
  - `.emojistatus` — diff between config emojis and registered application emojis

### AI/LLM Integration
- **OpenAI API** via Replit integration (`python_openai_ai_integrations`)
- Memory stored in `memory.json` with `users`, `favorability`, `conversations` keys.

### AI Debugging System
- `src/utils/ai_debugging.py` — automatic error reporting + AI-assisted fixes
- On unexpected command errors, posts to `AI_DEBUG_CHANNEL` (set as env var) with full traceback
- Buttons: **AI Debug** (explains root cause) → **Fix with AI** (rewrites cog, reloads it, saves backup) → **Revert Fix** (restores backup)
- Backups stored in `data/ai_debug_backups/`

### Economy System (Premium rewrite)
- **Per-user JSON files**: `data/economy_data/{user_id}.json`; lottery state in `data/economy_data/_lottery.json` (loader skips files starting with `_`).
- Auto-migration: legacy `inventory: list[str]` is converted to `inventory: dict[item_id, count]` on load. All defaults backfilled by `_migrate_user`.
- **Image cards** rendered with PIL in `src/utils/image/economy_card.py` (`render_balance_card`, `render_reward_card`, `render_leaderboard_card`). All renders run via `asyncio.to_thread`. Cards use a brown/gold/cream café aesthetic with stat chips, XP bar, and a stylised coffee-cup glyph as avatar fallback. Color emoji is intentionally kept out of PIL output (DejaVu fallback can't render them) — emojis live in surrounding LayoutView text instead.
- **Components-V2**: every reply is a `discord.ui.LayoutView` with a `Container` + `MediaGallery` (for cards) or `TextDisplay` blocks (for info). Helpers: `_card_view`, `_info_view`, `ACCENT_BROWN = 0xC8853F`.
- **Jobs ladder** (`src/utils/economy_jobs.py` `JOBS`): barista → server → pastry chef → barback → shift manager → general manager → owner. Each job has `min_level`, `min_pay`/`max_pay`, `xp_per_shift`, `cooldown`, emoji, description.
- **XP / level math**: `xp_to_next(level) = 100 * (level + 1)^1.45`, helpers `total_xp_for_level`, `level_from_total_xp`, `add_xp(data, gained) -> (new_level, levels_gained, leveled)`.
- **Tiered bank** (`BANK_TIERS`): Tin Jar → Wooden Drawer → Iron Safe → Steel Vault → Diamond Vault. Each tier has a cap and a daily interest rate. `_apply_bank_interest` runs every 30 min via `tasks.loop`, gated on UTC date so each account gets at most one credit per UTC day.
- **Shop** (`SHOP_ITEMS`): three categories — `consumable` (one-shot effects: `work_cooldown_half`, `crime_boost`, `rob_shield`, `lottery_boost`, `xp_potion`), `upgrade` (`bank_tier_up`), `collectible` (display-only). `data["effects"]` dict holds pending one-shot consumables.
- **Weekly lottery**: `LOTTERY_DRAW_INTERVAL = 7 days`, `LOTTERY_TICKET_PRICE = 500`, `LOTTERY_HOUSE_RAKE = 5%`. Tickets stored on user; pot rolls over with rake if no entrants. Draw runs from `_tick_task`.
- **Achievements** (`ACHIEVEMENTS` dict): nine badges (first paycheck, regular, shift lead, saver, vault keeper, millionaire, 7-day streak, 30-day streak, owner). Newly unlocked badges appear in card footers.
- **Transactions**: every credit/debit logs to `data["transactions"]` (capped at 40, newest first) via `_log_tx(data, kind, amount, note)`.
- **Commands**: `balance`/`bal`/`wallet`, `profile`/`prof`/`stats`, `daily` (streak multiplier), `work`, `job` (group: `list`, `info`, `apply`, `quit`), `crime`, `rob`, `pay`/`give`, `leaderboard`/`lb`/`top` (image card, top 10 with avatars), `shop [category]`, `buy`, `sell`, `use`, `inventory`/`inv`/`bag`, `bank` (group: `deposit`, `withdraw`, `upgrade`), `lottery`/`lotto` (group: `info`, `buy`), `transactions`/`tx`/`history`, `networth`/`nw`.
- **Backwards compatibility**: `EconomyCog.get_user_economy_data(user_id)` and `save_economy_data()` are preserved exactly so blackjack/slots/roulette/gambling cogs that read `user_data["balance"]` continue to work without changes.

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
- Tables: `giveaways` (message_id, channel_id, guild_id, prize, winners_count, end_time, ended, host_id, **requirements TEXT**) and `participants` (message_id, user_id) in `data/database.db` via `bot.cxn`. ALTER TABLE migration in `cog_load` adds `requirements` column to existing DBs.
- Persistent across restarts: `GiveawayPersistentView` registered via `bot.add_view()` in `cog_load` — only the two main-message buttons have fixed `custom_id`s (`giveaway_system_join`, `giveaway_system_manage`)
- Active giveaway messages show **Join** + **Manage** buttons. Manage opens an ephemeral management panel (host or server admin only) containing: End Giveaway, Select Random, and Participants buttons
- Management panel buttons are NOT persistent (ephemeral, created fresh per click); they use `interaction.response.edit_message` to update the panel in-place
- Participants button edits the ephemeral panel to a `PaginatedView` (15 per page, ◀/▶ nav)
- Ended messages use `_build_ended_view()` (LayoutView, no buttons); `end_giveaway()` edits the original public message
- Full bilingual EN/DE + normal/cafe personality MESSAGES table; `msg(ctx_or_interaction, key)` and `_guild_msg(guild, key)` helpers for task callbacks
- **Setup panel**: `.giveaway start` now opens an interactive `_GiveawaySetupView` (LayoutView) in-channel — modals for Prize/Duration/Winners/AccountAge/ServerAge, ChannelSelect, RoleSelect, Boost toggle, Clear Roles, Start, Cancel. Per-button `host_id` interaction check (no `view.interaction_check`).
- **Join requirements** persisted as JSON (`{min_account_age_days, min_server_age_days, required_role_ids[], require_boost}`); enforced in the Join button via `_check_member_meets_reqs`. Helper `_requirements_summary` renders them on the giveaway embed.
- Other commands: `.giveaway reroll <message_id>`
- Background task (`check_giveaways`) fires every 15 s

### Tickets (Restructured — `ticket` hybrid group)
- Single `ticket` hybrid group in `src/cogs/tickets.py` with admin sub-commands and in-ticket sub-commands.
- **Admin sub-commands** (require Manage Channels): `setup <category>`, `panel [channel]`, `category add/remove/list <name>`, `support add/remove/list <role>`.
- **In-ticket sub-commands** (run inside an open ticket channel): `add <user>`, `remove <user>`, `rename <name>`, `claim`, `transcript`, `close`, `delete`.
- Per-guild config in `data/ticket_config.json` via `src/utils/ticket_config.py` — adds `support_roles` (list of role IDs) and `claimed_by` (per-channel claimer map).
- `src/utils/ticket_utils.py` exposes `find_open_ticket(guild, user)` for the open-ticket guard and lazy-loads via `_loaded` flag.
- Trilingual EN/DE/ES MESSAGES table with normal/cafe personalities throughout.
- Persistent ticket buttons (`OpenTicketBtn`, `CloseTicketBtn`, `DeleteTicketBtn`) keep their `custom_id`s — see Persistent Views section.

### Reminders (`src/cogs/reminders.py`)
- Personal reminders backed by `data/reminders.json`. Background task fires due reminders by DM (channel fallback).
- Commands: `reminder add <duration> <text>`, `reminder list`, `reminder remove <id>`, `reminder clear`.
- Trilingual EN/DE/ES + normal/cafe MESSAGES.

### Tags (`src/cogs/tags.py`)
- Per-guild custom text snippets stored in `data/tags.json`.
- Commands: `tag <name>` (show), `tag create <name> <content>`, `tag edit <name> <content>`, `tag delete <name>`, `tag list`, `tag info <name>`.

### Birthdays (`src/cogs/birthdays.py`)
- Per-guild birthday store in `data/birthdays.json`. Daily background task announces birthdays in the configured channel.
- Commands: `birthday set <MM-DD>`, `birthday remove`, `birthday upcoming`, `birthday list`, `birthday channel <#channel>`.

### Highlights (`src/cogs/highlights.py`)
- Per-user keyword DM notifications stored in `data/highlights.json`. `on_message` listener checks for keyword matches and DMs the user a context snippet.
- Commands: `highlight add <word>`, `highlight remove <word>`, `highlight list`, `highlight clear`.

### Polls (`src/cogs/polls.py`)
- Multi-option polls (2–10 options) with live vote buttons. Stored in `data/polls.json`; persistent view registered on cog load.
- Commands: `poll create <question> | <opt1> | <opt2> ...`, `poll close <message_id>`, `poll results <message_id>`.

### Suggestions (`src/cogs/suggestions.py`)
- Per-guild suggestion channel + voting buttons. Admins can approve/deny via in-message buttons. Stored in `data/suggestions.json`.
- Commands: `suggest <text>`, `suggestion channel <#channel>`, `suggestion approve <id> [reason]`, `suggestion deny <id> [reason]`.

### Starboard (`src/cogs/starboard.py`)
- Auto-mirrors messages reaching the configured ⭐ threshold to a starboard channel. Tracks original→starboard message mapping in `data/starboard.json`.
- Commands: `starboard channel <#channel>`, `starboard threshold <n>`, `starboard emoji <emoji>`, `starboard ignore <#channel>`, `starboard config`.

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
- Lavalink-based music via wavelink (3.4.1), nodes loaded from AjieBlogs API on startup
- **Voice-connect logic restored & frozen**: `get_player`, `startup_connect`, `_fetch_node_list`, `_probe_node`, `_find_responsive_nodes` are the known-working version — DO NOT modify them
- **Gap-free playback**: `player.autoplay = wavelink.AutoPlayMode.partial` is set when `play` is invoked → wavelink advances the queue natively. `on_wavelink_track_end` no longer calls `player.play()` (no double-trigger / audio gap)
- **Three-state loop** via native `wavelink.QueueMode` (normal → loop → loop_all). The `_LoopBtn` and `!loop` command cycle through; `!loopqueue/lq` toggles loop_all directly
- **Spotipy** (`spotipy`): sync API wrapped in `loop.run_in_executor`. Resolves track / album / playlist (up to 100 items, paginated 50 at a time). Silently disabled if `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` are absent
- **Last.fm autoplay top-up**: when autoplay is on and the queue is about to dry, `_topup_autoplay()` queues 5 similar tracks via Last.fm before wavelink reaches an empty queue. Requires `LASTFM_API_KEY`
- **Premium queue management commands**: `play/p`, `pause`, `resume`, `skip/sk`, `stop`, `queue/q` (paginated), `shuffle/sh`, `clearqueue/cq/qclear`, `remove/rm <pos>`, `move/mv <from> <to>`, `jump/skipto <pos>`, `history/hist`, `loop/repeat`, `loopqueue/lq`, `autoplay/ap`, `nowplaying/np`, `volume/vol`, `disconnect/dc/leave`, `musicstatus`. Note: `clear` was renamed to `clearqueue` to avoid collision with moderation's `clear` (purge messages)
- **Now-playing card** (cv2 LayoutView): album art + 3 button rows
  - Row 1: Prev · Pause/Resume · Skip · Stop
  - Row 2: Loop (cycle, label shows current mode) · Shuffle · Vol − · Vol +
  - Row 3: Queue (opens ephemeral PaginatedView) · Autoplay · Open Track (link)
- **NP live refresh**: per-guild background task `_np_refresh_loop` edits the NP message every 10s while a track plays so the progress bar advances on its own. Started in `_send_np`, cancelled on disconnect / idle timeout. Skips edits while paused
- **`on_wavelink_track_start`** listener re-renders the NP card the moment wavelink advances to a new track
- History stored in per-guild `deque(maxlen=25)`; loop replays and Prev-button replays use a `_skip_history_once` flag so they don't pollute history

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
- All 50+ cogs load successfully on startup
