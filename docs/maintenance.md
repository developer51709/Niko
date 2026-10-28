# Maintenance Guide

## Updating the Bot
To pull the latest changes:
```bash
git pull origin main
pip install -r requirements.txt
```
Restart the bot process after updating.

## Backing Up Data
- **JSON Data**: Regularly back up the `data/` folder.

## Discord API proxy workers

`proxy-worker/` is an optional Cloudflare Worker that relays Discord REST requests from Cloudflare's Worker egress instead of the bot host's shared IP. It deploys the same way as `nsfw-api/`: Cloudflare's Workers Builds Git integration can build the folder on every push, or run `wrangler deploy` from `proxy-worker/`. Create an `AUTH_TOKEN` secret on every worker and set the same value as `PROXY_WORKER_TOKEN` on the bot. Multiple workers may be registered; Niko rotates through them per request.

The owner controls it from **Staff workspace → Discord proxy**. Registering a worker verifies a fresh HMAC challenge and stores the registration in the `proxy_workers` MongoDB collection; the routing switch lives in `proxy_worker_settings`. Registration and routing fail closed without MongoDB, and routing stays off until the owner enables it. Enabling routing sends Discord REST traffic (including dashboard and OAuth calls) through the workers first. A failed or unreachable worker falls through to the next worker, then to the existing direct/Webshare path, so the bot does not lose its normal egress.

The relay only accepts HTTPS `discord.com`/`discordapp.com` API paths. Each request is HMAC-signed with a timestamp and nonce, expires after 60 seconds and cannot be replayed. Worker telemetry is in memory per isolate: 15 minutes of 5-second latency buckets, request and status totals, the latest requests and the latest errors. Request bodies and responses are not stored. Webhook and interaction tokens are redacted from paths before they reach the dashboard feed. Multipart attachment uploads stay on the bot's direct route. Only REST traffic is relayed; the long-lived Discord gateway WebSocket stays on the bot's own connection because a Worker cannot proxy that socket.

## Web requests share the bot's egress

Login and dashboard calls to Discord go through `discord_request` in `src/webapp/discord_api.py`, which sends the bot's own `User-Agent` and, while a Webshare proxy is active, the same proxy discord.py uses. Discord answers every request through Cloudflare, and that edge challenges plain `python-requests` traffic from a datacenter IP — so a mismatch breaks the OAuth token exchange (a POST, so it is challenged first) and dashboard reads while the bot itself keeps answering commands. A Cloudflare interstitial is retried over the bot's active Webshare proxy when one is configured; otherwise the original response is returned to the caller, which reports the real failure instead of a `500`. A response is only treated as a Cloudflare block when Cloudflare's own interstitial proves it: a `cf-mitigated` header, its numeric `error code: 10xx` access denial, or its block/challenge page body. `CF-Ray` and `Server: cloudflare` are present on every Discord response — including plain 200s, Discord's own 429 rate limits, and its JSON API errors — so a status code plus those headers is never a block. Without an interstitial the response is Discord's own answer and is passed through untouched, which keeps a rate limit from being reported as a ban and from moving traffic away from an egress that is working. Cloudflare's status then decides the recovery, because its edge rate limit and its access denial are not the same event. A **429** interstitial (`Error 1015`, the `cf-error-details` rate-limit page) is a throttle: it is what the first REST calls after a restart look like, Discord answers the same call over the Webshare egress a second later, and the instance keeps its own route and its own gateway — the proxy manager owns that recovery. A **403/503** interstitial (a `cf-mitigated` challenge or an `error code: 10xx` access denial) is a real block, and that is what arms the proxy rotation. The startup and recovery probes present the bot's own identity for the same reason — `discord.py`'s `User-Agent`, and the proxy discord.py is egressing through when one is active — because Cloudflare challenges a bare `python-requests` client from a datacenter IP, which would report a block the bot itself never sees.

## Guild blacklist lockdown

The feature switch behind a guild blacklist lives in `src/utils/guild_lockdown.py`. Blacklisting a server is a sequence of ordered, independent steps, and each one reports its own outcome to the staff dashboard:

| Step | Dashboard wording | What it does |
|------|-------------------|--------------|
| `database` | Saving to database… | writes the blacklist entry (owned by `src/utils/blacklist_manager.py`) |
| `social` | Pausing social notifs… | turns the server-wide notifier switch off, keeping every follow |
| `starboard` | Disabling starboard… | clears the saved starboard channel, keeping threshold, emoji and ignored channels |
| `polls` | Disabling polls… | marks every open poll `locked = 1` so votes are refused and the tally survives |
| `giveaways` | Disabling giveaways… | marks every active giveaway `locked = 1`: no entries, no draw |
| `notification` | Sending blacklist notification… | DMs the guild owner with the reason and the appeal link |

What each feature looked like beforehand is written to the `guild_feature_locks` table, which is what a lifted blacklist replays. Steps never abort each other: a step that fails is reported in the dashboard summary, logged, and the blacklist entry still stands.

The disabled state is held in the database — the cleared `starboard_config.channel_id`, `polls.locked`, `giveaways.locked`, `notifier_config.enabled` — so features stay off across a restart. `ensure_schema` creates the lock table and adds the `locked` columns, and the poll and giveaway cogs repeat the `ALTER TABLE` at startup so a database created before those columns existed is migrated.

Removing a blacklist (or approving an appeal) restores the saved starboard channel, unlocks the polls and giveaways, and retires the lock records. The notifier is the deliberate exception: its lock record is retired without replaying it, because a server turns its own announcements back on in the dashboard's Notifications tab. Blacklisted servers are also skipped by official staff broadcasts in `src/cogs/staff/owner.py`, which reports how many were skipped.

The staff API is `POST /api/staff/guilds/<guild_id>/blacklist` with `{action, reason}`, followed by `POST /api/staff/guilds/<guild_id>/blacklist/lockdown` with `{step}`, which answers `{ok, step, label, status, detail, blacklisted}`. The dashboard calls the lockdown route once per step so progress is visible per feature; the step keys and wording there are a contract with the Python list, held in `web/src/utils/guildBlacklist.ts` and covered by `tests/test_guild_lockdown.py`.

## Discord rate limits and egress

Three mechanisms keep the bot answerable while Discord is limiting it or refusing its egress. All of them log what they did: `Interactions` for an interaction answered in Discord's own request, `InteractionPriority` when the callback bypass is armed, and `ProxyManager` with the reason a proxy was applied (`Discord global rate limit` or `Cloudflare throttle (…)`).

### Discord's own request carries the callback

`src/utils/interaction_endpoint.py` answers interactions in the body of the request Discord makes to *us*, which takes the three-second callback off the egress path completely: no request has to leave the process to reply. It is armed by the **Interactions Endpoint URL** in the Developer Portal — `https://<public host>/api/discord/interactions`, served by `src/webapp/routes/interaction_routes.py` — together with the application's **Public Key** in `DISCORD_PUBLIC_KEY` (public information; the value is cached in `data/interaction_public_key` once fetched, so an outage that blocks egress does not disarm a running endpoint).

The two ways of receiving interactions are mutually exclusive, so saving that URL *is* the switch: Discord stops sending `INTERACTION_CREATE` over the gateway and POSTs every slash command, component, modal and autocomplete to the endpoint instead (`discord.py` logs its own warning about that at login). Clearing the URL in the portal returns delivery to the gateway, and until then the route is the only path an interaction can take, so the endpoint has to stay publicly reachable.

The route verifies Discord's Ed25519 signature — `X-Signature-Ed25519` over `X-Signature-Timestamp` plus the raw body — and answers the type 1 PING that saving the URL triggers with `{"type": 1}`. That handshake is inbound only, so the switch can be flipped while the host's IP is blocked by Cloudflare. `discord.py` always builds a callback as an outbound REST call, so the single function that does that (`AsyncWebhookAdapter.create_interaction_response`) is wrapped while an HTTP interaction is being handled: the body it would have sent is mirrored into the response, and the library is handed the callback response Discord would have returned. Nothing else changes — followups, `original_response()` edits and deletes still go out over REST through the proxy and the priority bypass above.

Two details of the mirrored callback are worth knowing. A view sent with it still dispatches: a component callback that updates its message (a paginator arrow, a panel button) reports the id of the message it edits, and a callback that posts a *new* message is stored without a message id — the same fallback `discord.py` already uses for persistent views, and one its buttons survive because their `custom_id` is generated per instance. And a handler that answers without deferring keeps exactly the one outbound request it had before: `discord.py`'s `Context.send` asks for the original response after the callback so it can return the real message, so that GET replaces the callback POST rather than adding to it. Deferring first, as the slower commands already do, turns that into the followup they were making anyway.

The answer has to be inside Discord's three seconds, so the wait for a handler is capped at 2.0s by default and the rest of the window is the round trip to Discord. `DISCORD_INTERACTION_BUDGET_SECONDS` tunes that wait (at most 3.0s). A handler that misses the budget is acknowledged with Discord's documented empty `202` and its own callback request then goes out over REST as before, which `Interactions` logs with the interaction id; every such line is the one symptom worth investigating.

### Interaction callbacks never queue behind a global limit

Discord does not count the interaction endpoints against the application's global rate limit — `POST /interactions/{id}/{token}/callback`, plus the interaction webhook routes behind followups, original-response edits and deletes — and an interaction has to be answered within three seconds. `discord.py` nevertheless parks *every* request behind `HTTPClient._global_over` while a global 429 is being slept off, which is why a global limit hit elsewhere used to make menus and slash commands feel dead.

`src/utils/interaction_priority.py` wraps the client's `HTTPClient.request` and marks the request in flight when it is one of those routes, so the global gate steps aside for exactly them and every other request keeps waiting. The bypass lasts for one request: a panel post into a channel from the same handler is an ordinary channel write and still queues. With the interactions endpoint below armed, a first callback does not even reach the client — the bypass still covers the followup and edit routes, and every deployment that still receives interactions over the gateway.

Handlers already reply through the callback. For an interaction-based context, `discord.py`'s `Context.send`/`reply`/`defer` use the interaction response and then the interaction followup, so the 62 hybrid commands (slash + prefix), every app command and every component handler answer over the callback route; only a prefix-invoked command — which has no interaction at all — falls back to a channel message. Posting a *new* message into a channel (ticket panel, rules panel, role menu) is deliberately a channel write, because a panel has to live in the channel rather than in an ephemeral response.

### A limited IP moves egress to Webshare

`src/utils/proxy_manager.py` arms the Webshare proxy when the bot's own egress is limited, and disables it again once a tiny unproxied probe shows the direct IP is answering. A limit is recognised from every signal Discord leaves behind, because relying on one of them is what let a global limit pass unnoticed:

| Signal | Where it appears |
|--------|------------------|
| `X-RateLimit-Scope: global` | 429 header (current) |
| `X-RateLimit-Global: true` | 429 header (older) |
| `"global": true` | 429 body — the only signal `discord.py` itself reads |

A Cloudflare `Error 1015` throttle is the same recovery, because a different egress IP clears it too, so it arms or rotates the proxy as well. A plain Discord 429 arrives through Cloudflare as well, so only Cloudflare's own page or its `cf-mitigated` header counts as a throttle.

While a proxy is already active, another limit rotates to a different proxy instead of reusing the IP that is being limited — spaced out to one rotation per limit burst, since rotating on every 429 in the same burst only burns through the proxy list. A proxy that cannot be connected to is rotated immediately rather than retried, and the 10-minute recovery probe still returns the bot to the direct IP once that works.

## Monitoring
- Check the console logs for errors.
- Ensure the bot process is kept alive using a process manager like PM2 or systemd (if not on Replit).
- On Replit, use the "Workflows" or "Logs" tab to monitor status.

## Troubleshooting
- **Rate Limits**: If the bot is being rate-limited by Discord, check if you are performing too many actions (like webhook creations) in a short period. Commands and buttons still answer during a global limit — see **Discord rate limits and egress** — so a menu that does not respond is not a rate-limit symptom.
- **Dependency Issues**: Run `pip install --upgrade -r requirements.txt` to ensure all libraries are up to date.
