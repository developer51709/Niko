---
name: Dashboard OAuth pattern
description: How the Flask web dashboard handles Discord OAuth and graceful degradation
---

## Architecture
- Flask web server at `src/website.py`, static files at `src/website/`
- Discord OAuth2: client ID hardcoded (`1484653109576732692`), secret from `DISCORD_CLIENT_SECRET` env var
- `SESSION_SECRET` Replit secret signs the Flask session cookie
- Redirect URI computed from `REPLIT_DEV_DOMAIN` env var

## Graceful degradation
When `DISCORD_CLIENT_SECRET` is absent:
- `/auth/login` returns 503 JSON
- `/auth/status` returns `{"authenticated": false, "oauth_available": false}`
- Dashboard shows a clear "OAuth not configured — add DISCORD_CLIENT_SECRET" message
- All public API endpoints (`/api/botstats`) still work

## bot_stats.json
Written by `_write_bot_stats()` called in `on_ready`. Contains: `guild_count`, `guild_ids`, `user_count`, `command_count`, `version`, `uptime_since`. Web server reads this to serve `/api/botstats` and to determine which guilds the bot is in (for guild picker filtering).

**Why:** The bot (asyncpg) and web server (psycopg2/Flask) run as separate processes; JSON file is the simplest IPC for startup stats.

## Level data
PostgreSQL (`DATABASE_URL`) is the primary source via psycopg2. Falls back to `data/levels.json.migrated` and `data/level_config.json.migrated` if DB is unavailable.
