<div align="center">

![Niko](docs/assets/niko_banner_2.png)

# Niko

**The warm, capable Discord companion for communities that care.**

Moderation, music, progression, tickets, social feeds, and AI — in one polished Discord experience with a full web dashboard.

[Add Niko](https://discord.com/oauth2/authorize?client_id=1520558530472448170) ·
[Dashboard](https://niko.sryze.cc/dashboard) ·
[Support server](https://niko.sryze.cc/discord) ·
[Documentation](https://niko.sryze.cc/docs) ·
[Changelog](https://niko.sryze.cc/changelog)

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![discord.py 2.7+](https://img.shields.io/badge/discord.py-2.7%2B-5865F2?style=flat-square&logo=discord&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-API-000000?style=flat-square&logo=flask&logoColor=white)
![React 18](https://img.shields.io/badge/React-18-149ECA?style=flat-square&logo=react&logoColor=white)
![Vite 6](https://img.shields.io/badge/Vite-6-646CFF?style=flat-square&logo=vite&logoColor=white)

</div>

---

## Overview

Niko is a self-hosted Discord bot built for communities that want thoughtful moderation, engaging social features, and a dashboard that actually reflects how their server is doing. It runs as a single Python process: the bot, the Flask API, and the generated React dashboard share one deployment, one database, and one event loop.

The result is a companion that feels native to Discord — fast slash commands, polished Components v2 panels, live profile popouts, and transcripts that look like Discord's own — without giving up the control of self-hosting.

> **Quick start:** set `DISCORD_BOT_TOKEN`, run `python src/bot.py`, and open the dashboard on port `5000`.

---

## Highlights

### Moderation and safety
- Kick, ban, mute, tempmute, warn, purge, slowmode, and channel lockdown
- AutoMod for spam, invite links, blocked words, mass mentions, join raids, and external-app abuse
- Optional AI image filtering through a self-hostable Cloudflare Worker
- Moderation logs, case history, and per-server exemption lists

### Community and engagement
- Persistent ticket system with Discord-styled HTML transcripts
- Giveaways with account-age, server-age, role, and booster requirements
- Polls, suggestions, starboard, custom tags, birthdays, and reminders
- Social feed notifications for YouTube, Twitch, X, TikTok, Bluesky, and Reddit

### Music
- Lavalink/wavelink playback with queue, loop, shuffle, volume, and seek controls
- YouTube, Spotify, and direct URL support
- Live now-playing cards and Last.fm-powered autoplay

### Progression and economy
- Per-message XP, leveling curves, role rewards, and leaderboards
- Jobs, banking, daily streaks, shops, collectibles, crime, and robbery
- Weekly lottery and unlockable achievements with server-side image cards

### AI companion
- OpenAI-compatible chat with per-user memory and favorability
- Configurable identity and tone per server
- Image generation, translation, definitions, and AI-assisted error reports

### Dashboard and operations
- Discord OAuth dashboard for server settings, activity, and moderation insights
- Live command directory, documentation, changelog, and public profile cards
- Staff workspace for team applications, server notes, and standby management
- Interaction endpoint support, standby failover, and Discord-aware proxy recovery

---

## Tech stack

| Layer | Technology |
|---|---|
| Bot runtime | Python 3.10+, discord.py 2.7+ |
| Web API | Flask, served in the bot process |
| Dashboard | React 18, TypeScript, Vite 6 |
| Music | Lavalink / wavelink |
| AI | OpenAI-compatible API |
| Storage | MongoDB when configured, with SQLite/JSON fallbacks |
| Optional filter service | Cloudflare Workers (`nsfw-api/`) |

---

## Repository structure

```text
src/
├── bot.py                  # Bot entry point and gateway lifecycle
├── api_server.py           # Starts the Flask API beside the bot
├── cogs/                   # Feature modules (moderation, economy, music, ...)
├── webapp/                 # Flask routes, auth, cards, and shared web helpers
├── utils/                  # AI, music, tickets, image rendering, and integrations
├── events/                 # Gateway and startup event handlers
├── config/                 # Bot IDs, links, emojis, and runtime configuration
├── assets/                 # Fonts, badges, and generated emoji art
└── website/dist/           # Generated dashboard build (served by Flask)

web/                        # React + Vite dashboard source
docs/                       # Setup, API, dashboard, maintenance, and legal docs
tests/                      # pytest suite covering bot, API, and rendering behavior
nsfw-api/                   # Optional Cloudflare Worker for image classification
scripts/                    # Badge and emoji asset generation helpers
```

`src/website/dist/` is generated output. Edit `web/` and run the build rather than changing files under `dist/` directly.

---

## Getting started

### Prerequisites

- Python 3.10 or newer
- Node.js 20 or newer
- A Discord application with a bot user and the **Message Content**, **Server Members**, and **Presence** intents enabled

### 1. Install the Python dependencies

```bash
git clone https://github.com/developer51709/Niko.git
cd Niko
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure the environment

Set these variables in your hosting dashboard, shell, or a local `src/.env` file. `DISCORD_BOT_TOKEN` is required; the dashboard needs OAuth credentials.

| Variable | Required | Purpose |
|---|---|---|
| `DISCORD_BOT_TOKEN` | Yes | Bot token from the Discord Developer Portal |
| `DISCORD_CLIENT_SECRET` | For the dashboard | Enables Discord OAuth login |
| `SESSION_SECRET` | Recommended | Keeps dashboard sessions stable across restarts |
| `DISCORD_CLIENT_ID` | Optional | Defaults to Niko's application ID |
| `PUBLIC_URL` | Optional | Canonical public origin for OAuth and links |
| `PORT` | Optional | Web port, defaults to `5000` |
| `MONGODB_URL` | Optional | MongoDB connection; otherwise local storage is used |
| `MONGODB_DATABASE` | Optional | MongoDB database name |
| `DISCORD_PUBLIC_KEY` | Optional | Enables Discord's interactions endpoint |
| `NSFW_API_URL` / `NSFW_API_TOKEN` | Optional | Enables the AutoMod image filter |
| `TOPGG_WEBHOOK_TOKEN` | Optional | Enables top.gg vote rewards |

The full list, including Twitch and notification integrations, lives in [`docs/setup.md`](docs/setup.md).

### 3. Build the dashboard

```bash
npm install
npm run build
```

### 4. Run Niko

```bash
python src/bot.py
```

The API starts with the bot. The dashboard is available at `http://localhost:5000` (or your configured `PORT`), and the same process serves the generated site from `src/website/dist/`.

---

## Commands

| Area | Commands |
|---|---|
| Economy | `/balance` `/daily` `/work` `/job` `/shop` `/bank` `/lottery` `/pay` `/crime` `/rob` |
| Leveling | `/leveling rank` `/leveling leaderboard` `/leveling panel` `/leveling config` |
| Music | `/play` `/nowplaying` `/queue` `/skip` `/stop` `/loop` `/shuffle` `/volume` |
| Moderation | `/kick` `/ban` `/warn` `/mute` `/purge` `/automod` `/whitelist` |
| Giveaways | `/giveaway start` `/giveaway end` `/giveaway reroll` `/giveaway list` |
| Tickets | `/ticket panel` `/ticket config` `/close` `/delete` |
| Community | `/poll` `/suggest` `/starboard` `/tag` `/birthday` `/highlight` `/notifier` |
| AI | `@Niko` `/favor` `/memory` `/imagine` `/translate` `/define` |
| Fun | `/hug` `/pat` `/boop` `/meme` `/cat` `/afk` `/snipe` |
| Utility | `/remind` `/serverinfo` `/userinfo` `/avatar` `/prefix` |
| Admin | `/reload` `/sync` `/emojisync` `/onboarding` `/voicemaster` `/trigger` |

The dashboard's live command directory is the source of truth for the current build.

---

## Documentation

| Guide | What it covers |
|---|---|
| [Setup](docs/setup.md) | Environment variables, first run, and interactions endpoint |
| [API](docs/api.md) | Public and authenticated routes, plus endpoint conventions |
| [Dashboard](docs/dashboard.md) | Dashboard structure and server configuration |
| [Maintenance](docs/maintenance.md) | Updates, backups, proxy behavior, and standby failover |
| [AI providers](docs/ai-providers.md) | OpenAI-compatible provider configuration |
| [FAQ](docs/faq.md) | Common questions and troubleshooting |
| [Privacy policy](docs/privacy-policy.md) | What Niko stores and how it is used |
| [Terms of service](docs/terms-of-service.md) | Usage terms for the hosted deployment |

Public documentation, release notes, and the command reference are also available at [niko.sryze.cc](https://niko.sryze.cc).

---

## Security

Niko takes user privacy seriously. If you believe you have found a vulnerability, please report it privately:

1. Open a private security advisory at [github.com/developer51709/Niko/security/advisories/new](https://github.com/developer51709/Niko/security/advisories/new), or
2. Join the [support server](https://niko.sryze.cc/discord) and open a **Bug** post in `#community-help` or a private ticket from `#create-a-ticket`.

Include the affected endpoint or page, reproduction steps, and the impact. Please do not include real secrets or other people's private data. Valid reports are rewarded with the **Bug Bounty** role, because every vulnerability fixed is a potential future incident prevented.

The deployment also publishes [`/.well-known/security.txt`](https://niko.sryze.cc/.well-known/security.txt) and serves friendly decoy responses on commonly scanned secret paths rather than exposing real configuration.

---

## Development

Run the checks before opening a pull request:

```bash
pytest
npm run typecheck
npm run build
```

Guidelines:

- Keep changes focused and match the existing Python and React conventions.
- Add or update tests when behavior changes.
- Update `web/src/data/changelog.ts` for user-visible updates.
- Rebuild `src/website/dist/` when the frontend changes; do not edit generated assets by hand.
- Never commit tokens, `.env` files, or other credentials.

---

## Credits

Niko is built and maintained by [@sorenthedev](https://github.com/developer51709), with contributions from the Niko staff and community.

<div align="center">

**Built for communities that care.**

</div>
