"""Startup — warm the guild AI settings cache.

Every AI reply reads the guild's settings. Without a warm cache the first
message in each guild after a restart pays a database round trip before any
generation can start, and the synchronous cosmetic readers (roleplay flavour,
dashboard config view) fall back to defaults until that happens.
"""

from utils import logging


async def preload_ai_config(bot):
    """Load every stored guild AI config into the in-process cache."""
    try:
        from utils.ai.config import preload_all

        loaded = await preload_all()
    except Exception as exc:  # noqa: BLE001 - startup must never abort on this
        logging.warning("AI", f"Could not warm the AI config cache: {exc}")
        return
    if loaded:
        logging.info("AI", f"Warmed AI settings for {loaded} guild(s)")
