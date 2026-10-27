"""Environment, filesystem, and permission constants for the web
application process."""

import os


DISCORD_CLIENT_ID     = os.environ.get("DISCORD_CLIENT_ID", "1520558530472448170")

DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "")

DISCORD_BOT_TOKEN     = os.environ.get("DISCORD_BOT_TOKEN", "")

DISCORD_API           = "https://discord.com/api/v10"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR     = os.path.join(PROJECT_ROOT, "data")

ECONOMY_DIR  = os.path.join(DATA_DIR, "economy_data")

BOT_STATS    = os.path.join(DATA_DIR, "bot_stats.json")

AI_CONFIG_DATABASE_SENTINEL_LEGACY        = os.path.join(DATA_DIR, "ai_config.json")

AI_CONFIG_DATABASE_SENTINEL = AI_CONFIG_DATABASE_SENTINEL_LEGACY  # compatibility alias; AI reads/writes are database-backed

LEVELS_JSON  = os.path.join(DATA_DIR, "levels.json.migrated")

LEVELCFG_JSON = os.path.join(DATA_DIR, "level_config.json.migrated")

DATABASE_PATH = os.path.join(DATA_DIR, "database.db")

OXAPAY_KEY = os.environ.get("OXAPAY_API_KEY", "")

MANAGE_GUILD_PERM = 0x20

ADMINISTRATOR_PERM = 0x8

WEB_DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "website", "dist")
