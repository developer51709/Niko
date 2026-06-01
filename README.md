<div align="center">

![Niko Banner](banner.png)

# ☕ Niko Discord Bot
*A cozy, trilingual café-themed companion for your server*

---

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![discord.py](https://img.shields.io/badge/discord.py-2.3-5865F2?style=for-the-badge&logo=discord&logoColor=white)
![OpenAI](https://img.shields.io/badge/Powered_by-OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

</div>

---

## 🔗 Links

| | |
|---|---|
| **Bot Invite** | [Add Niko to your server](https://discord.com/oauth2/authorize?client_id=1484653109576732692&permissions=8&scope=bot%20applications.commands) |
| **Website** | [niko bot website](https://nikodiscordbot.developer51709.repl.co) |
| **Support Server** | [dsc.gg/astral-haven](https://dsc.gg/astral-haven) |
| **GitHub** | [developer51709/Niko](https://github.com/developer51709/Niko) |

---

## 🌸 Overview

Niko is a warm, trilingual (EN / DE / ES) Discord bot with a cozy café personality. She is powered by OpenAI for natural conversation, remembers past interactions per user, and brings a lo-fi aesthetic to any community. With 20+ cog groups and 76 slash commands, Niko covers everything from a premium economy system and Lavalink music to moderation, giveaways, ticketing, social media notifiers, and more — all wrapped in an interactive Components v2 UI.

**Current stats:** 55 servers · 1,342 users · 76 slash commands

---

## ✨ Feature Highlights

### 🧠 AI & Personality
- **OpenAI-powered chat** — mention Niko to start a conversation; she adapts her tone based on your favorability score and past memory
- **Trilingual** — responds in English, German, or Spanish; auto-detects language
- **Multi-personality** — *café* (warm bestie) and *normal* modes, configurable per server
- **AI image generation** — `/imagine` produces images in-channel
- **AI debugging system** — automated error reporting and one-click AI-assisted fixes

### 💰 Premium Economy
- **PIL image cards** — beautiful wallet, reward, and leaderboard cards rendered server-side
- **Job ladder** — 8 tiers from Barista → Café Owner, each with unique pay, XP, and cooldowns
- **Tiered bank** — 5 vault tiers (Tin Jar → Diamond Vault) with daily compound interest
- **Shop system** — consumables (XP boosts, shields), upgrades (vault keys), collectibles
- **Weekly lottery** — ticket-based with a rolling jackpot
- **Achievements** — 15+ unlockable badges based on milestones and activity
- **Crime & rob** — risk-based side income with item defenses
- **Transaction log** — full history of every credit and debit

### ⭐ Leveling
- Per-message XP with configurable multiplier and cooldown
- Per-guild settings: XP toggle, announcement channel, custom level-up messages
- Role rewards at configurable thresholds
- `!levelpanel` interactive CV2 management panel

### 🎵 Music
- **Lavalink / wavelink** — high-quality, gap-free audio playback
- YouTube, Spotify, and direct URL support
- Three-state loop (off / track / queue), queue shuffle, volume control
- Live now-playing card with progress bar and interactive buttons
- Last.fm autoplay top-up for endless continuous listening

### 🛡️ Moderation
- Full toolset: kick, ban, mute, tempmute, warn, purge, slowmode, lock
- **AutoMod dashboard** — anti-spam, anti-link, bad words, mass mention, external app raid protection
- Whitelist system to exempt trusted users and roles
- Mod-log channel with rich event embeds

### 🎉 Community
- **Giveaways** — CV2 setup wizard with join requirements (account age, server age, roles, booster)
- **Tickets** — persistent per-guild ticket system with category and support-role config
- **Polls** — live multi-option polls with real-time vote counts
- **Suggestions** — board with admin approve/deny workflow
- **Starboard** — auto-mirror starred messages
- **Tags** — per-guild custom text snippets
- **Birthdays** — daily birthday announcement task
- **Highlights** — keyword-based DM notifications
- **Reminders** — personal scheduled DM reminders
- **Social notifiers** — YouTube, Twitter/X, TikTok, Bluesky, Reddit feed subscriptions

### 🎰 Casino
Blackjack, Slots, Roulette — all with PIL image cards and full economy integration

### 🌐 Website & Dashboard
- Public landing page with bilingual toggle (EN/DE)
- Full command documentation page
- Dashboard prototype (Discord OAuth integration coming soon)

---

## 📁 Project Structure

```
src/
├── bot.py                  # Entry point — loads cogs, syncs slash commands, event loop
├── website.py              # Flask static server for the website
│
├── cogs/                   # Modular feature groups (each is a discord.py Cog)
│   ├── admin/              # Admin tools, prefix management
│   ├── ai/                 # AI chat, memory, favorability, image generation
│   ├── automod/            # AutoMod dashboard, raid protection
│   ├── casino/             # Blackjack, Slots, Roulette, mini-games
│   ├── economy/            # Balance, jobs, bank, shop, lottery, achievements
│   ├── fun/                # Roleplay, memes, animals, AFK, snipe
│   ├── giveaway/           # CV2 giveaway setup with join requirements
│   ├── help/               # Dynamic help system
│   ├── info/               # Serverinfo, userinfo, avatar
│   ├── leveling/           # XP, levels, leaderboard, level panel
│   ├── logging/            # Event logger (join/leave/edit/delete)
│   ├── moderation/         # Kick, ban, warn, mute, purge, mod-log
│   ├── music/              # Lavalink/wavelink music player
│   ├── notifier/           # Social media feed subscriptions
│   ├── onboarding/         # Verification, captcha, role assignment
│   ├── social/             # Polls, suggestions, starboard, tags, highlights
│   ├── system/             # Error handler, AI debugging reporter
│   ├── tickets/            # Persistent ticket system
│   ├── utility/            # Reminders, birthdays, translate, define
│   └── voicemaster/        # Dynamic voice channel creation
│
├── utils/                  # Shared utility modules
│   ├── ai/                 # OpenAI client, memory, config, debugging, actions
│   ├── image/              # PIL economy card renderer
│   ├── onboarding/         # Captcha generation, config, utils
│   ├── social/             # Platform scrapers (YouTube, Twitter, TikTok, Bluesky, Reddit)
│   ├── tickets/            # Ticket config and helpers
│   ├── emoji_sync.py       # Application emoji download/upload/sync
│   ├── i18n.py             # Trilingual message system with 4-level fallback
│   ├── logging.py          # Custom coloured terminal logger
│   ├── paginator.py        # Shared PaginatedView for CV2 lists
│   ├── ratelimit.py        # Async rolling-window rate limiter
│   └── blacklist_manager.py
│
├── config/                 # Bot configuration (emojis, AI config, etc.)
│
├── website/                # Static website served by website.py
│   ├── index.html          # Landing page (EN/DE bilingual)
│   ├── dashboard.html      # Dashboard prototype
│   ├── docs/index.html     # Full command documentation
│   ├── styles.css          # Shared café dark aesthetic
│   ├── tos.html
│   └── privacy.html
│
└── data/                   # Persistent storage (JSON + SQLite)
    ├── database.db         # Giveaway data (SQLite)
    ├── levels.json
    ├── level_config.json
    ├── mod_config.json
    ├── warnings.json
    ├── ticket_config.json
    ├── reminders.json
    ├── tags.json
    ├── birthdays.json
    ├── highlights.json
    ├── polls.json
    ├── suggestions.json
    ├── starboard.json
    └── economy_data/       # Per-user economy profiles (JSON)
```

---

## 🚀 Setup

1. Add your `DISCORD_BOT_TOKEN` to environment secrets
2. Start the **Discord Bot** workflow — cogs load automatically, slash commands sync globally on first run
3. Optionally start the **Start the website** workflow to serve the landing page
4. In your server, use `!levelpanel` and `!automod` to configure per-guild settings interactively

**Requirements:** Python 3.10+, discord.py 2.3, wavelink, Flask, Pillow, OpenAI (via Replit integration)

---

## 📜 Commands (summary)

> Full interactive documentation: **[docs page](https://nikodiscordbot.developer51709.repl.co/docs)**

| Category | Key Commands |
|---|---|
| **Economy** | `/balance` `/daily` `/work` `/job` `/shop` `/bank` `/lottery` `/pay` `/crime` `/rob` |
| **Leveling** | `/level` `/level-leaderboard` `/levelpanel` `/levelconfig` |
| **Music** | `/play` `/nowplaying` `/queue` `/skip` `/stop` `/loop` `/shuffle` `/volume` |
| **Casino** | `/blackjack` `/slots` `/roulette` `/connectfour` `/tictactoe` |
| **Moderation** | `/kick` `/ban` `/warn` `/mute` `/purge` `/automod` `/whitelist` |
| **Giveaways** | `/giveaway start/end/reroll/list` |
| **Tickets** | `/ticket panel/config` `/close` `/delete` |
| **Community** | `/poll` `/suggest` `/starboard` `/tag` `/birthday` `/highlight` `/notifier` |
| **AI & Chat** | `@Niko` `/favor` `/memory` `/imagine` `/translate` `/define` |
| **Fun** | `/hug` `/pat` `/boop` `/meme` `/cat` `/afk` `/snipe` |
| **Utility** | `/remind` `/serverinfo` `/userinfo` `/avatar` `/prefix` |
| **Admin** | `/reload` `/sync` `/emojisync` `/onboarding` `/voicemaster` |

---

## 🎨 UI System

All user-facing responses use **discord.ui.LayoutView (Components v2)** featuring:
- **Containers** with colour accents per context
- **Text displays** and section separators
- **Media galleries** for image card rendering (economy, casino)
- **Action rows** with buttons (music controls, ticket actions, paginator arrows)
- **Paginated views** for leaderboards and command lists

---

<div align="center">

*Niko — making your Discord server cozier, one cup at a time ☕*

*Built by [@n.y.x.e.n](https://github.com/developer51709)*

</div>
