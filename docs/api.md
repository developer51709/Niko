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
| POST | `/api/discord/interactions` | Discord's interactions endpoint; the callback is returned in the response body |
| GET | `/api/premium/plans` | Plan price, perks, currencies, and enabled payment methods |
| POST | `/api/premium/webhook` | OxaPay white-label callback, verified with the HMAC-SHA512 merchant signature |
| POST | `/api/donations/webhook` | OxaPay donation callback, verified the same way |
| GET | `/bot/card.svg` | Live SVG profile card for the README; accepts `?theme=dark\|light` and `?accent=RRGGBB`, and is served `no-store` so every load shows current figures |

The interactions endpoint is public for the same reason it exists: Discord has
no session. The Ed25519 signature over the raw body is what proves the caller is
Discord, and a request without it is answered `401`. It is the *Interactions
Endpoint URL* of the Developer Portal (`docs/maintenance.md`), so an interaction
never has to be answered by an outbound request to Discord's API.

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
performed server-side; the frontend must not be treated as the security boundary. The overview activity series contains daily aggregate message, join, and leave totals; it does not include message content or member identifiers.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/guilds` | Mutual manageable guilds |
| GET | `/api/guild/<id>/overview` | Moderation, leveling, server totals, and 14-day activity summary |
| GET | `/api/guild/<id>/levels` | XP leaderboard |
| GET | `/api/guild/<id>/config` | Moderation, AI, leveling, and server config |
| GET | `/api/guild/<id>/resources` | Available text channels and roles for dashboard selectors |
| GET/POST | `/api/guild/<id>/boosters` | Read or update boost announcements and personal booster-role settings |
| GET/POST | `/api/guild/<id>/applications` | List or create staff role openings |
| POST | `/api/guild/<id>/applications/<application_id>/status` | Close or reopen an opening without changing its link or submissions |
| GET | `/api/guild/<id>/applications/<application_id>/submissions` | Review applicant responses |
| GET | `/api/applications/<guild_id>` | List open roles for a verified server member |
| GET | `/api/applications/<guild_id>/<application_id>` | Load an eligible application form |
| POST | `/api/applications/<guild_id>/<application_id>/submit` | Submit one application per Discord user and opening |
| POST | `/api/guild/<id>/config/automod` | Update allowed AutoMod flags |
| POST | `/api/guild/<id>/config/ai` | Update AI enabled state and personality |
| POST | `/api/guild/<id>/config/leveling` | Update leveling controls |
| POST | `/api/guild/<id>/config/server` | Update prefixes, onboarding, logging, and ticket settings |
| GET | `/api/premium/guild/<id>` | Premium subscription state and perks for one managed server |
| GET | `/api/premium/guilds` | Servers the signed-in member can upgrade, with premium state |
| POST | `/api/premium/checkout` | Start a one-month white-label purchase; returns the crypto address, amount, and QR code |
| GET | `/api/premium/orders/<order_id>` | Poll a checkout and the guild's resulting term |
| GET | `/api/premium/gift-targets` | Mutual servers the signed-in member belongs to, with premium state |
| POST | `/api/premium/gift/checkout` | Start a gift for 1, 3, 6, or 12 months on a server the payer belongs to |
| GET | `/api/premium/gift/orders/<order_id>` | Poll a gift and the recipient's resulting term |
| GET | `/api/donations/meta` | Presets, currencies, totals, and goal for the donation page |
| POST | `/api/donations/invoice` | Create a white-label donation quote from a signed `/donate` token |
| GET | `/api/donations/<order_id>` | Donation payment status, reconciled with the provider while open |

The premium checkout stores nothing the browser sends about money: the price,
currency, and month length come from `utils/premium.py`. Buying and gifting are
separate endpoints — the purchase route only accepts `purchase` and always
charges one month, while the gift route requires membership instead of Manage
Server and only accepts the offered terms. An OxaPay callback is the only thing
that extends a term, and `confirm_payment` makes a repeated callback a no-op, so
a retried provider notification cannot add a second month. Donations are
credited through a single locked confirmation, so a webhook retry and the
bot's poller can never both count the same payment.

POST requests use JSON and return `{ "ok": true }` on success. The API only
accepts the documented configuration keys and converts booleans/numbers before
persisting them. Staff application submissions require a Discord-authenticated
session and are checked against current guild membership using the bot; each
application/user pair is unique in the database.

### Data removal

Data removal requests require a Discord session. Server requests also require
the caller to be the current owner, or the owner recorded when Niko left the
server. Submissions require the CSRF token from `/auth/status`. Nothing is
deleted until the bot owner approves the request in the owner-only queue.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/privacy/data-removal` | Own requests plus the account/server targets the caller can prove they own |
| POST | `/api/privacy/data-removal` | Submit a scoped account or server deletion request |
| DELETE | `/api/privacy/data-removal/<request_id>` | Withdraw a pending request |
| GET | `/api/staff/data-removal` | Owner-only review queue |
| POST | `/api/staff/data-removal/<request_id>/review` | Approve (run the scoped deletion) or deny a request |

### Owner operations

The bot owner can manage optional Discord proxy workers. These routes require a
staff session with the owner role; mutations also need the CSRF token returned
by `/auth/status`.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/staff/proxy-workers` | Worker health, latency buckets, recent requests/errors, and aggregate usage |
| POST | `/api/staff/proxy-workers` | Verify and register a proxy worker |
| DELETE | `/api/staff/proxy-workers/<id>` | Remove a proxy worker |
| POST | `/api/staff/proxy-workers/routing` | Persist the owner's routing switch |
| GET | `/api/staff/billing` | Recent payments, active subscriptions, revenue totals, and gateway state |
| POST | `/api/staff/billing/payments/<order_id>/resolve` | Flag a payment for follow-up or mark it resolved with a note |
| POST | `/api/staff/billing/subscriptions/<guild_id>` | Grant, extend, or cancel a server's subscription |

## Adding an endpoint

The Flask app entrypoint is `src/webapp/__init__.py`; shared setup and helpers
live in `src/webapp/server.py` and its sibling helper modules, and routes are
grouped in focused modules under `src/webapp/routes/`, such as
`dashboard_routes.py` and `auth_routes.py`. Add new routes
to the relevant module, keep static fallback routing last, use `@require_auth`
and `@require_guild_access` for private guild data, validate request JSON, and
return explicit error responses. Update `web/src/api.ts`, `web/src/types.ts`,
and this file together.
