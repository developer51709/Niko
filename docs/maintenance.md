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

Login and dashboard calls to Discord go through `discord_request` in `src/webapp/server.py`, which sends the bot's own `User-Agent` and, while a Webshare proxy is active, the same proxy discord.py uses. Discord answers every request through Cloudflare, and that edge challenges plain `python-requests` traffic from a datacenter IP — so a mismatch breaks the OAuth token exchange (a POST, so it is challenged first) and dashboard reads while the bot itself keeps answering commands. A Cloudflare interstitial is only relayed when an active standby origin and the relay secrets are both present; otherwise the original response is returned to the caller, which reports the real failure instead of a `500`. A response is only treated as a Cloudflare block when Cloudflare's own interstitial proves it: a `cf-mitigated` header, its numeric `error code: 10xx` access denial, or its block/challenge page body. `CF-Ray` and `Server: cloudflare` are present on every Discord response — including plain 200s, Discord's own 429 rate limits, and its JSON API errors — so a status code plus those headers is never a block. Without an interstitial the response is Discord's own answer and is passed through untouched, which keeps a rate limit from being reported as a ban and from moving traffic away from an egress that is working. A lone interstitial is still retried once over the instance's own egress before anything else happens: Discord serves every request through Cloudflare, so one challenged or throttled route is routine while the instance's REST traffic is fine — the first REST call after a restart has done exactly that, with a healthy session seconds later. Only two consecutive interstitials mark the egress blocked and justify a failover, and the retry honours a bounded `Retry-After`. The startup and recovery probes present the bot's own identity for the same reason — `discord.py`'s `User-Agent`, and the proxy discord.py is egressing through when one is active — because Cloudflare challenges a bare `python-requests` client from a datacenter IP, which would report a block the bot itself never sees.

### Where standby management runs

Only the primary owns the standby registry and the failover control plane. **Staff workspace → Standby instances** therefore always answers on the primary: while a standby owns the gateway the primary relays the rest of the dashboard to it but keeps `/api/staff/standbys*` local.

If that path is opened on a standby origin directly, the standby forwards the request to the primary instead of applying it locally, and answers `503` with an explicit error when it cannot reach it. The primary's origin is taken from `STANDBY_PRIMARY_URL`, then `PUBLIC_URL`, then the origin the main instance announces in the shared `standby_primary` collection (written at startup from `PUBLIC_URL`/`DONATION_SITE_URL`/`DISCORD_REDIRECT_URI` and refreshed on every successful registration). Never from request headers — a forwarded host is attacker-controlled, and trusting it would let a crafted request make a standby ship the owner's session to another origin. Set `STANDBY_PRIMARY_URL` on a standby deployment that has no other way to name production. A standby also refuses a request that already carries the `X-Niko-Standby-Control` marker, so a misconfigured standby chain cannot loop.

Applying a management change on a standby is not just a stale view: `activate`/`rotate` install a routing target on the manager that answered, which would point that instance at itself or at another standby. For the same reason a standby never loads registry entries as failover targets, so it can never relay Discord REST traffic to a standby.

### Restarting the instance that owns the gateway

A restarted process always boots warm: it holds no gateway ownership, and a standby never promotes itself. The primary therefore supervises the standby it activated — it reads the `gateway` field of the standby's `/health` every 15 seconds and re-sends the signed activation whenever that instance answers `standby` (its normal state right after a restart), so the bot reconnects on its own within seconds of the restart finishing. An instance that is still starting answers nothing and is checked again on the next tick.

If the standby never comes back, the primary waits out a short grace period (~60 seconds) and then resumes gateway ownership itself, so an unreachable or deleted standby cannot leave the bot offline. The same applies at primary startup: when this instance is about to connect directly it first tells every registered standby to release the gateway, which prevents two live gateway sessions after a primary restart.

## Monitoring
- Check the console logs for errors.
- Ensure the bot process is kept alive using a process manager like PM2 or systemd (if not on Replit).
- On Replit, use the "Workflows" or "Logs" tab to monitor status.

## Troubleshooting
- **Rate Limits**: If the bot is being rate-limited by Discord, check if you are performing too many actions (like webhook creations) in a short period.
- **Dependency Issues**: Run `pip install --upgrade -r requirements.txt` to ensure all libraries are up to date.
