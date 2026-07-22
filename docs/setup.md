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
Create a `src/.env` file (see `src/.env.example`) or set the following environment variables:
- `DISCORD_BOT_TOKEN`: Your bot's secret token.

### 4. Run the Bot
Run from the repository root:
```bash
python src/bot.py
```

---

Note:
> the bot will automatically handle the ai model installation on the first run and uses a lightweight model that uses less than 1GB of storage and should not require advanced hardware to run.

## Hosting on Replit
If you are using Replit, simply:
1. Import the repository.
2. Add your `DISCORD_BOT_TOKEN` to the Secrets tool.
3. Click the "Run" button.
4. The Agent will handle the environment setup.