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
- `DISCORD_TOKEN`: Your bot's secret token.
- `NSFW_API_URL` *(optional)*: Base URL of your deployed [NSFW Image Filter API](../nsfw-api/README.md) (a Cloudflare Worker). Required to enable the AutoMod **NSFW image filter**.
- `NSFW_API_TOKEN` *(optional)*: Bearer token if you set the `AUTH_TOKEN` secret on the worker.

### 4. Run the Bot
```bash
python bot.py
```

---

Note:
> the bot will automatically handle the ai model installation on the first run and uses a lightweight model that uses less than 1GB of storage and should not require advanced hardware to run.

## Hosting on Replit
If you are using Replit, simply:
1. Import the repository.
2. Add your `DISCORD_TOKEN` to the Secrets tool.
3. Click the "Run" button.
4. The Agent will handle the environment setup.