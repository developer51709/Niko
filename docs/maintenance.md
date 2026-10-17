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

## Standby backend failover

A standby instance is a complete, warmed copy of the production bot backend and dashboard. It logs in with the production bot identity but holds no Discord gateway ownership until a signed handoff from the primary. Standby backend failover is separate from outbound proxying: Webshare remains the independently managed proxy service for egress routing.

1. Deploy a second backend service using the same start command as production (`python src/bot.py`). Set `STANDBY_MODE=true` and provide the production `DISCORD_BOT_TOKEN`, `SESSION_SECRET`, and shared MongoDB configuration. The standby loads the same cogs and database-backed caches but keeps its gateway inactive until it receives a signed handoff.
2. Bind its HTTP listener to `0.0.0.0` and the platform-provided `PORT`. Public HTTPS may be terminated by the hosting platform. For self-hosted deployments, configure `STANDBY_TLS_CERT` and `STANDBY_TLS_KEY` together to enable TLS directly on the listener.
3. The standby listener serves the complete Flask dashboard/API, authenticated standby registration and gateway-control endpoints, Discord API relay, and `/health`. Use the public HTTPS origin for registration; the listener is not an HTTP CONNECT proxy. While a standby owns the gateway the primary relays browser traffic to it on that registered origin and passes the public host along in `X-Forwarded-Host`/`X-Forwarded-Proto`, never as `Host`: the production hostname is bound to the primary deployment, so handing it to another deployment's edge makes that edge answer the relay with its own 404 and the production URL serves nothing. The standby applies the forwarded host to the Flask app, which keeps OAuth callbacks, absolute redirects, and session cookies on the production URL — the public domain cannot be moved to the standby because its Discord OAuth redirect URI is fixed.
4. Sign in to the production staff dashboard as the bot owner, open **Staff workspace → Standby instances**, enter a label and the standby HTTPS origin, then choose **Verify & add standby**. Registration uses a fresh nonce and rejects the standby unless its HMAC proof matches both the production bot token and session secret. Secrets are never sent in the challenge or returned to the browser. Only public HTTPS origins resolving to public IPs are accepted.
5. Standby registrations are stored in the shared MongoDB database (`standby_instances` collection), not local JSON or SQLite files. Configure a durable MongoDB deployment with `MONGODB_URL` (and `MONGODB_DATABASE` if desired) on both services. The primary fails closed for registration and will not use local SQLite as a registry fallback. Removing an instance from the owner-only dashboard removes it from future failover selection.

During a failover, the primary relays Discord REST traffic over the authenticated standby backend and transfers gateway ownership with signed control messages. Webshare proxy configuration and health remain independent; it is not selected or managed by standby failover. Keep standby service access restricted and use the same production session secret on both instances.

A standby never initiates failover: a blocked request on that instance cannot promote it or move its gateway to another registered instance, because only the primary arms automatic failover. Both ends of the relay also share one allowlist of Discord REST and CDN hosts, so a failover request is never refused by the standby and silently retried over the blocked direct egress. Registering the primary's own origin is rejected, since the primary would otherwise proxy every request to itself.

### Web requests share the bot's egress

Login and dashboard calls to Discord go through `discord_request` in `src/webapp/server.py`, which sends the bot's own `User-Agent` and, while a Webshare proxy is active, the same proxy discord.py uses. Discord answers every request through Cloudflare, and that edge challenges plain `python-requests` traffic from a datacenter IP — so a mismatch breaks the OAuth token exchange (a POST, so it is challenged first) and dashboard reads while the bot itself keeps answering commands. A Cloudflare interstitial is only relayed when an active standby origin and the relay secrets are both present; otherwise the original response is returned to the caller, which reports the real failure instead of a `500`. A response is only treated as a Cloudflare block when Cloudflare's own interstitial proves it: a `cf-mitigated` header, its numeric `error code: 10xx` access denial, or its block/challenge page body. `CF-Ray` and `Server: cloudflare` are present on every Discord response — including plain 200s, Discord's own 429 rate limits, and its JSON API errors — so a status code plus those headers is never a block. Without an interstitial the response is Discord's own answer and is passed through untouched, which keeps a rate limit from being reported as a ban and from moving traffic away from an egress that is working. Cloudflare's status then decides the recovery, because its edge rate limit and its access denial are not the same event. A **429** interstitial (`Error 1015`, the `cf-error-details` rate-limit page) is a throttle: it is what the first REST calls after a restart look like, Discord answers the same call over the Webshare egress a second later, and the instance keeps its own route and its own gateway — the proxy manager owns that recovery, and no standby is contacted. A **403/503** interstitial (a `cf-mitigated` challenge or an `error code: 10xx` access denial) is a real block, and that is what justifies a standby handoff before the proxy fallback. The startup and recovery probes present the bot's own identity for the same reason — `discord.py`'s `User-Agent`, and the proxy discord.py is egressing through when one is active — because Cloudflare challenges a bare `python-requests` client from a datacenter IP, which would report a block the bot itself never sees.

### Where standby management runs

Only the primary owns the standby registry and the failover control plane. **Staff workspace → Standby instances** therefore always answers on the primary: while a standby owns the gateway the primary relays the rest of the dashboard to it but keeps `/api/staff/standbys*` local.

If that path is opened on a standby origin directly, the standby forwards the request to the primary instead of applying it locally, and answers `503` with an explicit error when it cannot reach it. The primary's origin is taken from `STANDBY_PRIMARY_URL`, then `PUBLIC_URL`, then the origin the main instance announces in the shared `standby_primary` collection (written at startup from `PUBLIC_URL`/`DONATION_SITE_URL`/`DISCORD_REDIRECT_URI` and refreshed on every successful registration). Never from request headers — a forwarded host is attacker-controlled, and trusting it would let a crafted request make a standby ship the owner's session to another origin. Set `STANDBY_PRIMARY_URL` on a standby deployment that has no other way to name production. A standby also refuses a request that already carries the `X-Niko-Standby-Control` marker, so a misconfigured standby chain cannot loop.

Applying a management change on a standby is not just a stale view: `activate`/`rotate` install a routing target on the manager that answered, which would point that instance at itself or at another standby. For the same reason a standby never loads registry entries as failover targets, so it can never relay Discord REST traffic to a standby.

### Restarting the instance that owns the gateway

A restarted process always boots warm: it holds no gateway ownership, and a standby never promotes itself. The primary therefore supervises the standby it activated — it reads the `gateway` field of the standby's `/health` every 15 seconds and re-sends the signed activation whenever that instance answers `standby` (its normal state right after a restart), so the bot reconnects on its own within seconds of the restart finishing. An instance that is still starting answers nothing and is checked again on the next tick.

If the standby never comes back, the primary waits out a short grace period (~60 seconds) and then resumes gateway ownership itself, so an unreachable or deleted standby cannot leave the bot offline. The same applies at primary startup: when this instance is about to connect directly it first tells every registered standby to release the gateway, which prevents two live gateway sessions after a primary restart.

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

`src/utils/interaction_endpoint.py` answers interactions in the body of the request Discord makes to *us*, which takes the three-second callback off the egress path completely: no request has to leave the process to reply. It is armed by the **Interactions Endpoint URL** in the Developer Portal — `https://<public host>/api/discord/interactions`, served by `src/webapp/interaction_routes.py` — together with the application's **Public Key** in `DISCORD_PUBLIC_KEY` (public information; the value is cached in `data/interaction_public_key` once fetched, so an outage that blocks egress does not disarm a running endpoint).

The two ways of receiving interactions are mutually exclusive, so saving that URL *is* the switch: Discord stops sending `INTERACTION_CREATE` over the gateway and POSTs every slash command, component, modal and autocomplete to the endpoint instead (`discord.py` logs its own warning about that at login). Clearing the URL in the portal returns delivery to the gateway, and until then the route is the only path an interaction can take, so the endpoint has to stay publicly reachable.

The route verifies Discord's Ed25519 signature — `X-Signature-Ed25519` over `X-Signature-Timestamp` plus the raw body — and answers the type 1 PING that saving the URL triggers with `{"type": 1}`. That handshake is inbound only, so the switch can be flipped while the host's IP is blocked by Cloudflare. `discord.py` always builds a callback as an outbound REST call, so the single function that does that (`AsyncWebhookAdapter.create_interaction_response`) is wrapped while an HTTP interaction is being handled: the body it would have sent is mirrored into the response, and the library is handed the callback response Discord would have returned. Nothing else changes — followups, `original_response()` edits and deletes still go out over REST through the proxy and the priority bypass above.

Two details of the mirrored callback are worth knowing. A view sent with it still dispatches: a component callback that updates its message (a paginator arrow, a panel button) reports the id of the message it edits, and a callback that posts a *new* message is stored without a message id — the same fallback `discord.py` already uses for persistent views, and one its buttons survive because their `custom_id` is generated per instance. And a handler that answers without deferring keeps exactly the one outbound request it had before: `discord.py`'s `Context.send` asks for the original response after the callback so it can return the real message, so that GET replaces the callback POST rather than adding to it. Deferring first, as the slower commands already do, turns that into the followup they were making anyway.

The answer has to be inside Discord's three seconds, so the wait for a handler is capped at 2.0s by default and the rest of the window is the round trip — including the standby relay, whose upstream read timeout is three seconds as well. `DISCORD_INTERACTION_BUDGET_SECONDS` tunes that wait (at most 3.0s). A handler that misses the budget is acknowledged with Discord's documented empty `202` and its own callback request then goes out over REST as before, which `Interactions` logs with the interaction id; every such line is the one symptom worth investigating. While a standby owns the gateway the POST is relayed like any other web request, so the interaction is dispatched by the instance holding the live command tree.

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

A Cloudflare `Error 1015` throttle is the same recovery, because a different egress IP clears it too, so it arms or rotates the proxy as well; the standby manager deliberately leaves that event to this path. A plain Discord 429 arrives through Cloudflare as well, so only Cloudflare's own page or its `cf-mitigated` header counts as a throttle.

While a proxy is already active, another limit rotates to a different proxy instead of reusing the IP that is being limited — spaced out to one rotation per limit burst, since rotating on every 429 in the same burst only burns through the proxy list. A proxy that cannot be connected to is rotated immediately rather than retried, and the 10-minute recovery probe still returns the bot to the direct IP once that works.

## Monitoring
- Check the console logs for errors.
- Ensure the bot process is kept alive using a process manager like PM2 or systemd (if not on Replit).
- On Replit, use the "Workflows" or "Logs" tab to monitor status.

## Troubleshooting
- **Rate Limits**: If the bot is being rate-limited by Discord, check if you are performing too many actions (like webhook creations) in a short period. Commands and buttons still answer during a global limit — see **Discord rate limits and egress** — so a menu that does not respond is not a rate-limit symptom.
- **Dependency Issues**: Run `pip install --upgrade -r requirements.txt` to ensure all libraries are up to date.
