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
    try:
        await init_database(bot)
        await load_cogs(bot)
        await set_status(bot)
        print_banner(bot, guild_count=len(bot.guilds))
        write_bot_stats(bot)
        write_commands(bot)
        asyncio.create_task(run_emoji_sync(bot))
        asyncio.create_task(run_slash_sync(bot))
    except Exception:
        logging.error("Startup", "Unhandled exception in on_ready:", exc_info=True)
        raise
    finally:
        # Make sure no status rotation work is left dangling if anything above
        # failed before rotation was scheduled.
        if getattr(bot, "_status_rotation_task", None) is None:
            _maybe_schedule_rotation_safely(bot)


def _maybe_schedule_rotation_safely(bot) -> None:
    """Best-effort fallback that schedules rotation only when nothing else did.

    This keeps the legacy ``on_ready`` path from leaving an unconsumed coroutine
    in the event loop if ``set_status`` was changed later.
    """
    if getattr(bot, "_status_rotation_task", None) is None:
        try:
            from events.startup.status import start_status_rotation as _start_rotation_sync
            if callable(_start_rotation_sync):
                _start_rotation_sync(bot)
        except Exception:
            logging.warning("Startup", "Failed to schedule fallback status rotation.")
