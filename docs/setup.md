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
Copy `env.example` from the repository root to `src/.env` (loaded by `src/bot.py`) or set the variables in whatever secret store your host provides. The template lists every variable, grouped and commented; the ones worth knowing about first are below.
- `DISCORD_BOT_TOKEN`: Your bot's secret token.
- `DISCORD_PUBLIC_KEY` *(optional)*: Your application's **Public Key** from the Developer Portal. Required by the Interactions Endpoint URL (see below); the bot also reads it from the application object when it is unset, and caches what it read.
- `DEVELOPMENT` *(optional)*: Set to `true`, `1`, `yes` or `on` for the public beta deployment. It selects the dedicated development status rotation in `src/config/status.py` and forces the command prefix to `!`, overriding server settings; leave unset or false for production behavior. Development instances also stop awarding XP and stop recording message activity (`src/config/environment.py`), so running one against production's MongoDB cannot overwrite live levels or double-count the dashboard.
- `COMMAND_PREFIX` *(optional)*: Force one command prefix across all servers and DMs, overriding per-server dashboard and `.prefix` settings. Leave unset to use each server's configured prefixes and the default prefix.
- `DISCORD_INTERACTION_BUDGET_SECONDS` *(optional)*: How long the interactions endpoint waits for a handler before answering Discord with `202` (default `2.0`, maximum `3.0`).
- `FAL_KEY` *(optional, required for premium image moderation)*: API key from [fal.ai](https://fal.ai/dashboard/keys). The **NSFW image filter** calls `fal-ai/imageutils/nsfw` and is a premium perk, so a guild only runs it while its subscription is active.
- `FAL_NSFW_URL` / `NSFW_THRESHOLD` *(optional)*: Override the model endpoint and the confidence threshold (`0.85` by default) for the image filter.
- `OXAPAY_API_KEY` *(optional, required for payments)*: OxaPay **Merchant API key** from Dashboard → Merchant → API Key. It powers the white-label crypto checkout used by both premium subscriptions and `/donate`, and signs the payment webhooks.
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