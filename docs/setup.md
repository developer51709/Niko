# Self-Hosting Setup Guide

## Prerequisites
- Python 3.10+
- A Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
- (Optional) PostgreSQL database if persistent storage is required beyond JSON files.

## Steps

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file or set the following environment variables:
- `DISCORD_TOKEN`: Your bot's secret token.
- `DATABASE_URL`: (If applicable) Your database connection string.

### 4. Run the Bot
```bash
python main.py
```

## Hosting on Replit
If you are using Replit, simply:
1. Import the repository.
2. Add your `DISCORD_TOKEN` to the Secrets tool.
3. Click the "Run" button.
4. The Agent will handle the environment setup.