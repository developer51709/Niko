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

## Standby proxy failover

A standby instance is not a second bot process: it serves an authenticated TLS CONNECT proxy and never connects to Discord. When the primary sees a Discord global HTTP 429, its proxy manager can route requests and gateway reconnects through a registered standby. The primary retains ownership of all Discord gateway state.

1. Create a Render Web Service for the standby and use the same start command as production (`python src/bot.py`). Set `BACKUP_MODE=true` and copy the production environment variables to this service. No separate certificate/key files or extra port configuration are needed: Render terminates public HTTPS and provides the service `PORT`; backup mode binds there and speaks HTTP behind Render. Leave `BACKUP_TLS_CERT` and `BACKUP_TLS_KEY` unset on Render. For self-hosted deployments, these remain optional as a pair; when supplied they enable direct TLS on the listener.
2. The copied production `DISCORD_BOT_TOKEN` and `SESSION_SECRET` are used only to derive challenge/proxy proofs; the standby process does not start Discord, dashboard or its own database connection. It will not consume the bot token to log in.
3. Once deployed, use the Render service's HTTPS origin in the production Staff workspace → Backups form and select **Verify & add standby**. The proxy defaults to `PORT` (Render's assigned service port) or `BACKUP_PROXY_PORT`/10000 outside Render; `BACKUP_PROXY_HOST` defaults to `0.0.0.0`. `/health` reports readiness.
4. Sign in to the production staff dashboard as the bot owner, open **Staff workspace → Backups**, enter a label and the standby HTTPS origin, then choose **Verify & add standby**. Registration uses a fresh nonce and rejects the standby unless its HMAC proof matches the production bot token **and** session secret. Secrets are never sent in the challenge or returned to the browser. Only public HTTPS origins resolving to public IPs are accepted.
5. Standby registrations are stored in the shared MongoDB database (`backup_instances` collection), not local JSON or SQLite files. This is required for Render web services without a persistent disk and allows restarts or multiple instances to see the same registry. Configure a durable MongoDB deployment with `MONGODB_URL` (and `MONGODB_DATABASE` if desired) on the primary. The primary fails closed for registration and will not use local SQLite as a registry fallback. Removing an instance from the owner-only dashboard immediately removes it from future failover attempts.

The backup proxy requires Basic proxy authentication derived from both production secrets and only permits CONNECT to Discord domains on port 443. For Render, the primary connects to the Render HTTPS origin; Render terminates TLS before proxy HTTP reaches the standby process. Self-hosted mode with certificate/key configured still uses a direct `https://` proxy connection. Keep the backup host and its secrets private, and use the same production session secret (not a new per-instance value). Do not place standby registry JSON files on either Render instance; the MongoDB registry is the source of truth.

**Render limitation:** managed HTTPS ingress is not documented as supporting opaque HTTP CONNECT tunnels. Registration challenge and `/health` are ordinary HTTP requests and work through that ingress, but verify an authenticated CONNECT tunnel end-to-end on the deployed service before relying on Render as a failover proxy. If Render rejects or buffers CONNECT, use a provider that explicitly exposes public TCP/TLS proxy ports; copying environment variables alone cannot work around a platform ingress limitation.

## Monitoring
- Check the console logs for errors.
- Ensure the bot process is kept alive using a process manager like PM2 or systemd (if not on Replit).
- On Replit, use the "Workflows" or "Logs" tab to monitor status.

## Troubleshooting
- **Rate Limits**: If the bot is being rate-limited by Discord, check if you are performing too many actions (like webhook creations) in a short period.
- **Dependency Issues**: Run `pip install --upgrade -r requirements.txt` to ensure all libraries are up to date.