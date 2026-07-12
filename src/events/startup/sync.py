"""
Startup — background sync tasks.
Runs slash-command sync and emoji sync as fire-and-forget tasks.
"""

from utils import logging
from utils.emoji_sync import sync_application_emojis


async def run_slash_sync(bot):
    try:
        synced = await bot.tree.sync()
        logging.success("SlashSync", f"Synced {len(synced)} application command(s) globally.")
    except Exception as exc:
        logging.error("SlashSync", f"Startup slash sync failed: {exc}")


async def run_emoji_sync(bot):
    try:
        await sync_application_emojis(bot)
    except Exception as exc:
        logging.error("EmojiSync", f"Startup emoji sync failed: {exc}")
