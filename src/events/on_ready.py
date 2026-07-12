"""
Startup handler for the Discord bot.
Orchestrates all startup tasks via modular imports from events.startup.
"""

import asyncio

from utils import logging
from events.startup import (
    init_database,
    load_cogs,
    set_status,
    print_banner,
    run_slash_sync,
    run_emoji_sync,
    write_bot_stats,
    write_commands,
)


async def handle_ready(bot):
    logging.info("Startup", f"Niko is online as {bot.user}")
    await init_database(bot)
    await load_cogs(bot)
    await set_status(bot)
    print_banner(bot, guild_count=len(bot.guilds))
    write_bot_stats(bot)
    write_commands(bot)
    asyncio.create_task(run_emoji_sync(bot))
    asyncio.create_task(run_slash_sync(bot))
