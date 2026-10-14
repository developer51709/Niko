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

## Monitoring
- Check the console logs for errors.
- Ensure the bot process is kept alive using a process manager like PM2 or systemd (if not on Replit).
- On Replit, use the "Workflows" or "Logs" tab to monitor status.

## Troubleshooting
- **Rate Limits**: If the bot is being rate-limited by Discord, check if you are performing too many actions (like webhook creations) in a short period.
- **Dependency Issues**: Run `pip install --upgrade -r requirements.txt` to ensure all libraries are up to date.
