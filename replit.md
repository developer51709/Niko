# Niko Discord Bot

## Overview

Niko is a Discord bot designed with a cozy café personality, offering bilingual support (EN/DE). Its comprehensive feature set includes an economy system, leveling, music playback, moderation tools, roleplay commands, general information, and AI-powered utilities. The project aims to provide a robust and engaging Discord experience, leveraging AI for interactive and dynamic responses.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Discord.py with Cogs pattern**: Modular design with all cogs located under `src/cogs/`.
- **Logging**: Custom logging implemented via `utils/logging.py`.

### UI / Response System
- **Components v2 (cv2) LayoutView**: All user-facing responses utilize `discord.ui.LayoutView` for structured and interactive UI elements, including containers, text displays, media galleries, and action rows with buttons.
- **Pagination**: A shared `PaginatedView` utility handles pagination for lists and leaderboards.
- **Trilingual Support (EN/DE/ES)**: Messages are managed through a `MESSAGES` dict per cog, supporting different personalities and languages with a 4-level fallback mechanism.
- **Hybrid Commands**: Supports both slash and prefix commands, with slash command synchronization handled on startup.
- **Personality**: Consistent "cafe" personality applied across all cogs.

### Rate Limiting
- Utilizes an asynchronous rolling-window `RateLimiter` for throttling events such as log messages, welcome messages, and role assignments to prevent abuse and API rate limits.

### Event-Loop Hygiene
- AI calls and long-running I/O operations (e.g., `requests.*`) are offloaded to a thread pool executor (`loop.run_in_executor` or `asyncio.to_thread`) to prevent blocking the event loop.

### Emoji System
- **Application Emojis**: All emojis are managed as bot-owned application emojis, eliminating the need for external emoji servers. A `src/utils/emoji_sync.py` utility automates the download, upload, and ID synchronization of these emojis.

### AI/LLM Integration
- **OpenAI API**: Integrated via Replit's built-in `python_openai_ai_integrations`.
- **Memory Management**: AI conversation memory, user favorability, and past interactions are stored in `memory.json`.

### AI Debugging System
- An automated AI debugging system (`src/utils/ai_debugging.py`) provides error reporting to a designated channel, AI-assisted explanations of root causes, and one-click fixes with rollback capabilities.

### Economy System
- **Data Storage**: User economy data is stored in individual JSON files (`data/economy_data/{user_id}.json`).
- **Image Cards**: Visual balance, reward, and leaderboard cards are rendered using PIL with a consistent café aesthetic.
- **Jobs System**: A tiered job ladder with associated pay, XP, and cooldowns.
- **XP / Leveling**: Custom XP calculation and leveling system with helpers for XP conversion.
- **Tiered Bank**: Features tiered bank accounts with caps and daily interest, applied via a scheduled task.
- **Shop**: In-game shop with consumables, upgrades, and collectibles.
- **Weekly Lottery**: A recurring lottery system with ticket purchases and prize rolls.
- **Achievements**: Unlockable badges based on user progression and activity.
- **Transactions**: Logs all economic credits and debits for user history.

### Leveling System
- **XP Storage**: XP data is stored per guild and user in `data/levels.json`.
- **XP Gain**: Random XP gain per message with configurable multipliers and cooldowns.
- **Configurable Settings**: Per-guild settings for XP enablement, multipliers, cooldowns, level-up channels, and role rewards are stored in `data/level_config.json`.
- **Interactive Management Panel**: A `!levelpanel` command provides an interactive CV2-based interface for managing all leveling settings.
- **Custom Level-up Messages**: Supports custom messages with placeholders.

### Moderation
- **Mod Log**: Events are logged to a configurable moderation channel.
- **AutoMod**: An interactive `!automod` dashboard allows configuration of anti-spam, anti-link, bad words, mass mention filters, and various thresholds.
- **AutoMod Whitelist**: Exempts specified users and roles from automod checks.
- **External App Raid Protection**: Detects and mitigates raids by external tools through `on_interaction` event monitoring, identifying operators, and taking punitive action.

### Giveaway System
- **Database Integration**: Giveaway and participant data are stored in `data/database.db`.
- **Persistence**: Giveaways are persistent across bot restarts through `PersistentView` registration.
- **Interactive Setup**: A CV2-based setup panel guides users through creating giveaways with various requirements.
- **Join Requirements**: Configurable requirements for participating in giveaways (e.g., account age, server age, roles, boosting status).

### Tickets
- **Hybrid Command Group**: `ticket` hybrid group in `src/cogs/tickets.py` with admin and in-ticket sub-commands.
- **Configurability**: Per-guild configuration for ticket categories and support roles stored in `data/ticket_config.json`.
- **Persistent Buttons**: Uses persistent view components for opening, closing, and deleting tickets.

### Other Core Features
- **Reminders**: Personal reminders stored in `data/reminders.json` with background task processing.
- **Tags**: Per-guild custom text snippets stored in `data/tags.json`.
- **Birthdays**: Per-guild birthday storage in `data/birthdays.json` with daily announcements.
- **Highlights**: Per-user keyword-based DM notifications stored in `data/highlights.json`.
- **Polls**: Multi-option polls with live voting, persistent views, and storage in `data/polls.json`.
- **Suggestions**: Per-guild suggestion system with voting and admin approval/denial, stored in `data/suggestions.json`.
- **Starboard**: Automatically mirrors starred messages to a designated channel, tracking in `data/starboard.json`.

### Persistent Views
- Key interactive components (e.g., ticket buttons, onboarding agreement buttons, role menus) have fixed `custom_id`s for persistence across restarts.

### Music
- **Lavalink Integration**: Uses `wavelink` for Lavalink-based music playback, with nodes loaded from AjieBlogs API.
- **Gap-free Playback**: Utilizes `wavelink.AutoPlayMode.partial` for seamless queue progression.
- **Looping**: Supports three-state looping (normal, loop current, loop queue) via native `wavelink.QueueMode`.
- **Spotify Integration**: Resolves Spotify tracks, albums, and playlists (requires API keys).
- **Last.fm Autoplay Top-up**: Automatically queues similar tracks from Last.fm when the queue is nearly empty for continuous playback (requires API key).
- **Now-playing Card**: CV2 LayoutView displaying track information with interactive control buttons and live progress bar updates.

## External Dependencies

### Discord API
- **discord.py**: Core framework for Discord bot interactions.

### AI Integration
- **OpenAI API**: For AI-powered responses and utilities.

### System Libraries
- **psutil**: For system resource monitoring.
- **requests**: HTTP client for external API calls.
- **beautifulsoup4**: For web scraping (e.g., for notifier cog).
- **deep-translator**: For translation services.
- **langdetect**: For language detection.

### Data Storage
- **Local Filesystem (JSON files)**:
    - `memory.json`: AI memory.
    - `economy_data/*.json`: Economy data.
    - `data/levels.json`: Leveling data.
    - `data/mod_config.json`: Moderation configuration.
    - `data/warnings.json`: Warning records.
    - `data/ticket_config.json`: Ticket system configuration.
    - `data/reminders.json`: User reminders.
    - `data/tags.json`: Custom tags.
    - `data/birthdays.json`: Birthday data.
    - `data/highlights.json`: Keyword highlights.
    - `data/polls.json`: Poll data.
    - `data/suggestions.json`: Suggestions data.
    - `data/starboard.json`: Starboard data.
- **SQLite Database (`data/database.db`)**: For giveaway system data.