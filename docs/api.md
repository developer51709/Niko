# Niko API

The API is served by the bot process on the same origin as the React dashboard.
`src/api_server.py` starts the Flask server in a daemon thread before Discord
connects. This means the preview, dashboard, and bot cannot drift into separate
services or require a second workflow.

## Run and build

```bash
npm run build
python3 src/bot.py
```

The bot serves port `5000` (or the `PORT` environment value). The React source
is in `web/`; the generated browser files are in `src/website/dist/`.
Set `DISCORD_CLIENT_SECRET` in the environment to enable the OAuth-protected
dashboard routes. Without it, public pages and public API endpoints still work,
but admin login intentionally remains unavailable.

## Endpoints

### Public

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Process and build health check |
| GET | `/api/botstats` | Public server, member, command, and uptime stats |
| GET | `/api/commands` | Live command registry; accepts `?category=` |

### Authentication

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/auth/login` | Starts Discord OAuth |
| GET | `/auth/callback` | Completes OAuth and creates the session |
| GET | `/auth/status` | Returns login state |
| GET | `/auth/logout` | Clears the session |

### Authenticated server data

All `/api/guild/<guild_id>/*` endpoints require a Discord session, Manage Server
permission for that guild, and the bot being present in the guild. This check is
performed server-side; the frontend must not be treated as the security boundary.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/guilds` | Mutual manageable guilds |
| GET | `/api/guild/<id>/overview` | Economy, moderation, and leveling summary |
| GET | `/api/guild/<id>/economy` | Economy leaderboard |
| GET | `/api/guild/<id>/levels` | XP leaderboard |
| GET | `/api/guild/<id>/config` | Moderation, AI, and leveling config |
| POST | `/api/guild/<id>/config/automod` | Update allowed AutoMod flags |
| POST | `/api/guild/<id>/config/ai` | Update AI enabled state and personality |

POST requests use JSON and return `{ "ok": true }` on success. The API only
accepts the documented configuration keys and converts booleans/numbers before
persisting them.

## Adding an endpoint

Keep API work in `src/website.py` until it needs a separate domain module. Add
the route before the static catch-all, use `@require_auth` and
`@require_guild_access` for private guild data, validate request JSON, and return
explicit error responses. Update `web/src/api.ts`, `web/src/types.ts`, and this
file together.