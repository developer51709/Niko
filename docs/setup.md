# Self-Hosting Setup Guide

## Prerequisites
- Python 3.10+
- A Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))

## Steps

### 1. Clone the Repository
```bash
git clone https://github.com/developer51709/Niko.git
cd Niko
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file or set the following environment variables:
- `DISCORD_BOT_TOKEN`: Your bot's secret token.
- `DISCORD_PUBLIC_KEY` *(optional)*: Your application's **Public Key** from the Developer Portal. Required by the Interactions Endpoint URL (see below); the bot also reads it from the application object when it is unset, and caches what it read.
- `DISCORD_INTERACTION_BUDGET_SECONDS` *(optional)*: How long the interactions endpoint waits for a handler before answering Discord with `202` (default `2.0`, maximum `3.0`).
- `NSFW_API_URL` *(optional)*: Base URL of your deployed [NSFW Image Filter API](../nsfw-api/README.md) (a Cloudflare Worker). Required to enable the AutoMod **NSFW image filter**.
- `NSFW_API_TOKEN` *(optional)*: Bearer token if you set the `AUTH_TOKEN` secret on the worker.
- `PROXY_WORKER_TOKEN` *(optional)*: Shared secret for the optional [Discord API proxy workers](../proxy-worker/README.md). Set the same value as each worker's `AUTH_TOKEN` secret. Proxy worker registration and routing require the shared MongoDB database (`MONGODB_URL`); without MongoDB they stay unavailable and the bot keeps its normal egress.
- `TOPGG_WEBHOOK_TOKEN` *(optional)*: The webhook authorization token from your top.gg listing. Required to credit vote rewards (coins, streaks and voting badges) and send the thank-you DM. Leave it unset to disable the vote webhook.
- `TWITCH_CLIENT_ID` / `TWITCH_CLIENT_SECRET` *(optional)*: Application credentials from a [Twitch developer app](https://dev.twitch.tv/console/apps). Used for the notifier's Twitch tracking and for Twitch profile cards on the team page. Leave them unset to disable Twitch support; every other notifier platform still works without credentials.

### 4. Run the Bot
```bash
python src/bot.py
```

### 5. Serve interactions from your own endpoint *(optional)*
Discord can POST every slash command, button, select and modal to this bot
instead of handing them over the gateway, and then expects the answer in that
same response. Nothing has to leave the process to reply, which keeps commands
and menus working when the host cannot reach Discord's API.

1. Make sure this deployment is reachable from the internet on a stable HTTPS
   URL — the same origin the dashboard is served from.
2. In the Developer Portal, open **General Information** and copy the
   **Public Key** into `DISCORD_PUBLIC_KEY`.
3. In the same page, set **Interactions Endpoint URL** to
   `https://<your public host>/api/discord/interactions`. Discord sends a PING
   to check it and keeps the URL only if the endpoint answers it.

Delivery is either the gateway or the endpoint, never both, so the endpoint then
answers every interaction. Followups, edits and deletes still go out to Discord
over REST. Clear the URL in the portal to return to gateway delivery.
`docs/maintenance.md` covers the response budget and the `202` fallback.

---

Note:
> the bot will automatically handle the ai model installation on the first run and uses a lightweight model that uses less than 1GB of storage and should not require advanced hardware to run.

## Hosting on Replit
If you are using Replit, simply:
1. Import the repository.
2. Add your `DISCORD_BOT_TOKEN` to the Secrets tool.
3. Click the "Run" button.
4. The Agent will handle the environment setup.