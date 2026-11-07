# Niko API

The API and the React dashboard are served through the supervisor
(`src/supervisor.py`), which owns the public origin and starts the dashboard in
its own child by default (`src/web_child.py`); live-bot routes are bridged to
the bot child over loopback. The database runs in its own child
(`src/db_child.py`) and is reached only over its authenticated loopback API. With
`--no-split-web` (or `NIKO_SPLIT_WEB=0`) the combined child returns:
`src/api_server.py` starts the Flask server in a daemon thread inside
`src/bot.py`. Either way, the preview, dashboard, and bot share one deployment
and one origin.

## Run and build

```bash
npm run build
python3 src/supervisor.py
```

The supervisor serves port `5000` (or the `PORT` environment value). Starting
`src/bot.py` directly still works for local debugging, but it bypasses the
supervisor and prints a warning. The React source is in `web/`; the generated
browser files are in `src/website/dist/`.
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
| GET | `/bot/favicon.svg` | The website favicon: the bot's avatar on the app icon's rounded tile, inlined from a 128px CDN copy; redirects to the build's `/favicon.svg` when there is no avatar |

`/api/commands` returns the registry the bot writes at startup. A command's
`description`, and each entry in `parameters[].description`, is a
`{locale: text}` map taken from the cogs' `locales/commands` namespace, so the
website can render the visitor's language; a command with no catalogue entry
falls back to a plain string. Commands owned by private cogs never appear.

The interactions endpoint is public for the same reason it exists: Discord has
no session. The Ed25519 signature over the raw body is what proves the caller is
Discord, and a request without it is answered `401`. It is the *Interactions
Endpoint URL* of the Developer Portal (`docs/maintenance.md`), so an interaction
never has to be answered by an outbound request to Discord's API.

## Developer API (v1)

The developer API is versioned in the URL and lives beside the website's own
routes. Its documented surface is `/api/v1/*`. A deployment that serves the API
from an API subdomain also exposes the same handlers at `/v1/*`; the `/api`
segment is omitted there. Unversioned aliases are not supported.

Every v1 endpoint returns user data and requires a developer key. The website's
internal leaderboard, profile, team, and transcript routes are not a substitute:
they accept only the site's own same-origin fetches (or a developer key where a
key is supplied), so a crawler cannot read them directly. Transcripts are
first-party only and are never available through an API key.

Access is invite-only. A developer joins the support server, opens a ticket,
and is approved by the bot owner. The owner grants scopes per Discord account in
**Dashboard → Developer portal → Access management**. A key can only carry a
subset of that account's grants; the endpoint decorator checks the key's scopes
on every request, so narrowing either the account or the key immediately takes
effect.

Bot integrations can additionally register an **application** with their bot
user / Application ID. Registration requires a screenshot of the Discord
Developer Portal's General Information page with the account profile menu open,
and the owner reviews it manually. A key may be bound to one approved
application. Its effective scopes are the intersection of the key scopes, the
application's owner-approved scopes, and the developer account's grants. Warn
endpoints and application webhooks require an app-bound key.

Keys are created in the Developer portal and shown once. Niko stores a peppered
SHA-256 hash and a short display prefix, never the raw secret. The developer must
accept the current developer policies in `/developers/policies` before their
first key can be created. The policy version is `2`; accepting an older version
requires accepting the current text again.

| Method | Path | Required scope | Purpose |
| --- | --- | --- | --- |
| GET | `/api/v1/economy/leaderboard` | `economy:read` | Global economy leaderboard; `?page=` and `?page_size=` |
| GET | `/api/v1/guilds/<guild_id>/levels` | `levels:read` | Server leveling leaderboard; alias `/api/v1/levels/<guild_id>` |
| GET | `/api/v1/users/<user_id>` | `users:read` | Discord profile for one user ID |
| GET | `/api/v1/users/<user_id>/economy` | `economy:read` | One user's economy profile |
| GET | `/api/v1/guilds/<guild_id>/members/<user_id>/level` | `levels:read` | One member's XP and level |
| PUT | `/api/v1/guilds/<guild_id>/members/<user_id>/level` | `levels:write` | Replace XP and level for one member |
| GET | `/api/v1/guilds/<guild_id>/warns` | `warns:read` | Guild warning cases; `?user_id=`, `?page=`, `?page_size=` |
| GET | `/api/v1/guilds/<guild_id>/members/<user_id>/warns` | `warns:read` | All warning cases for one member |
| POST | `/api/v1/guilds/<guild_id>/members/<user_id>/warns` | `warns:write` | Create a warning case (`reason`, optional `moderator_id`) |
| DELETE | `/api/v1/guilds/<guild_id>/warns/<warn_id>` | `warns:write` | Delete one warning case |
| DELETE | `/api/v1/guilds/<guild_id>/members/<user_id>/warns` | `warns:write` | Clear all warning cases for one member |
| GET | `/api/v1/blacklist` | `blacklist:read` | Blacklist records; `?type=users\|guilds\|all` |
| POST | `/api/v1/blacklist` | `blacklist:write` | Add/remove a blacklist entry (trusted apps only) |

Send the key as `Authorization: Bearer <key>` or `X-API-Key: <key>`. Missing,
unknown, and revoked keys return `401`; a valid key without the endpoint's scope
returns `403`. The current version is `v1`, and breaking changes will use a new
path version with a migration window rather than silently changing `v1`.

Warn and blacklist endpoints require an app-bound key. For warnings, the bot
must share the requested guild with Niko, and Niko must also be in the guild.
The owner can grant `guilds:cross_server` to a trusted application to bypass
only the shared-guild check. `blacklist:read`, `blacklist:write`, and
`guilds:cross_server` are restricted scopes and cannot be created on a generic
key.

### Reviewed applications and webhooks

Applications and their screenshots live in the developer portal's own MongoDB
database (`<MONGODB_DATABASE>_developer_portal`, e.g.
`discord_bot_developer_portal`), beside the bot's database rather than in it,
like the music and error-report stores. Without `MONGODB_URL` the historical
`data/developer_applications.json` and `data/developer_application_screenshots/`
are used instead, and the first MongoDB use imports them. A bot user ID can be registered once.
Pending and approved applications are locked; a denied application can be
resubmitted by the same developer. Approval is manual and the owner selects the
final scopes. See `src/webapp/developer/applications.py`.

Approved applications can configure an HTTPS webhook endpoint in the portal.
Delivery is handled by `src/webapp/developer/webhooks.py`. Events are only sent
for guilds the application's bot currently shares with Niko, unless the app was
granted `guilds:cross_server`. Each event is signed with
`X-Niko-Signature: t=<unix>,v1=<hmac-sha256(secret, "<unix>.<raw body>")>`.
Warn events are emitted after the database write: `warn.created`,
`warn.deleted`, and `warns.cleared`. Delivery retries transient failures up to
three attempts (about 0, 2, and 6 seconds) with an 8-second timeout per request.
Webhook URLs must use HTTPS and resolve only to public addresses.

### Rate limits and automated abuse

Every external `/api/v1/*` and `/v1/*` request is limited by source IP before
authentication: **120 requests per 60 seconds per `request.remote_addr`**. The
window is shared by all callers behind the same IP, so a NAT or datacenter egress
address must coordinate its own traffic. Every limited response carries
`X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` (Unix
seconds). An exhausted window returns `429` with `Retry-After` and the standard
envelope with `code: "RATE_LIMITED"` plus `limit`, `remaining`, and
`retry_after`. Health, static assets, and the portal are not IP-limited.

Authenticated traffic is also reviewed for automated abuse. The detector looks
at one key doing at least 300 requests per minute, at least 80 errors per minute
when at least 80% of requests fail, one key seen from at least 12 distinct IPs
with at least 30 requests in five minutes, or at least 20 IP rate-limit blocks in
five minutes. Crossing a threshold suspends the developer account: the key that
triggered it and every other key owned by that developer are revoked. The access
grant record is kept, and `enabled` is derived as granted, not suspended.

A suspended key cannot authenticate for data. Suspended developers can still
open `GET /api/developer/me` to read `suspension` and `appeal` state, but every
other portal key and usage operation returns `403` with
`code: "ACCESS_SUSPENDED"`. `POST /api/developer/keys`, `DELETE
/api/developer/keys/<key_id>`, `POST /api/developer/agree`, and
`GET /api/developer/logs` are locked until the suspension is lifted. Lifting a
suspension does not restore revoked keys; the developer must create new ones.

### Errors and report codes

Every API failure uses the shared error-report envelope. The top-level `error`
string is retained for compatibility, and every failure adds a stable `code`,
a `docs` path, and an identical `X-Error-Code` header:

```json
{
  "error": "This key does not have the required permission.",
  "code": "SCOPE_REQUIRED",
  "docs": "/developers/scopes",
  "required_scope": "economy:read"
}
```

When a genuine server failure is recorded in the error-report system, the body
and `X-Error-Report` header also include a six-character `report_code`. Expected
client errors (invalid input, missing scopes, rate limits, 404s) are not
reported. API 404 and 405 responses return the same JSON envelope with
`NOT_FOUND` and `METHOD_NOT_ALLOWED` instead of Flask's HTML error page. See
`web/src/pages/developerDocsContent.tsx` for the complete stable-code table and
`src/webapp/api_errors.py` for the envelope implementation.

### Maintenance responses

An owner can pause an API endpoint without taking the whole site down. The gate
in `src/webapp/api_maintenance.py` applies to both `/api/v1/*` and `/v1/*` and
returns a linked error report when one exists:

```json
{
  "error": "This API is in maintenance mode.",
  "code": "API_MAINTENANCE",
  "docs": "/developers/maintenance",
  "maintenance": {
    "kind": "api",
    "key": "api_v1_economy_leaderboard",
    "label": "Economy leaderboard API",
    "reason": "Rebuilding the leaderboard cache",
    "since": 1762300000
  },
  "report_code": "ABC123"
}
```

The response is `503` with `Retry-After: 300`. `/api/health`, `/status`, static
assets, and the signed-in portal remain reachable. The public status timeline
lists active API maintenance alongside owner-published incidents.

### Suspension appeals

A suspension revokes keys and sends the developer a Discord DM stating that API
access is suspended. The DM includes a persistent `niko:developer:appeal` button
backed by `src/cogs/system/developer_appeals.py`; the button survives restarts
and opens a modal. A developer can submit **one appeal per suspension**. The
owner reviews it in the Developer portal, and both decisions send a follow-up
DM. An approval lifts the suspension and restores portal access, but the
revoked keys stay revoked. The approval DM links to
`https://niko.sryze.cc/developers/rate-limits`,
`https://niko.sryze.cc/developers/policies`, and Discord's rate-limit
documentation.

### Developer portal

The portal is the signed-in management surface. It does not expose other
developers' data unless the caller is the owner.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/developer/me` | Access, current policy version, scope catalogue, active key count, rate-limit state, suspension, and appeal status (available while suspended) |
| POST | `/api/developer/agree` | Accept the current developer policies |
| GET | `/api/developer/keys` | List the caller's keys (prefixes only) |
| POST | `/api/developer/keys` | Create a scoped key; returns the raw secret once |
| DELETE | `/api/developer/keys/<key_id>` | Revoke one of the caller's keys |
| GET | `/api/developer/logs` | The caller's API usage; owner may pass `?all=1` |
| GET | `/api/developer/access` | Owner-only developer access roster and scope catalogue |
| PUT | `/api/developer/access/<user_id>` | Owner-only grant or edit access, scopes, note, and enabled state |
| DELETE | `/api/developer/access/<user_id>` | Owner-only revoke access and all of that developer's keys |
| GET | `/api/developer/appeals` | Owner-only suspension appeal queue |
| POST | `/api/developer/appeals/<appeal_id>/review` | Owner-only approve or deny an appeal; approval lifts the suspension |
| GET | `/api/developer/applications` | Applications owned by the caller, plus scope/event catalogue |
| POST | `/api/developer/applications` | Submit a multipart application with a verification screenshot |
| GET | `/api/developer/applications/<application_id>/screenshot` | Serve an owned screenshot to its developer or the owner |
| DELETE | `/api/developer/applications/<application_id>` | Remove a denied application |
| PUT | `/api/developer/applications/<application_id>/webhook` | Save the URL, enabled state, and event selection |
| POST | `/api/developer/applications/<application_id>/webhook/test` | Deliver a signed test event |
| GET | `/api/developer/applications/review` | Owner-only review queue |
| POST | `/api/developer/applications/<application_id>/review` | Owner-only approve or deny an application |

`POST /api/developer/keys` accepts an optional `application_id` in its JSON
body. App-bound keys are limited to the application's approved scopes and the
developer's current grants; warn scopes are rejected on generic keys.

## Authentication

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

### Staff analytics

Any official staff session can read bot-wide aggregate analytics. The counters
begin at the first command the bot records and hold 90 days of daily history;
no user ID, guild ID, or message content is stored or returned.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/staff/analytics` | Live gateway figures, daily command usage, invocation mix, top commands, guild language census, growth, and economy totals; accepts `?days=7\|14\|30\|…\|90` |

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
