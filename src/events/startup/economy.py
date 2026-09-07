"""
Startup — preload economy user data into the in-memory cache.

The leaderboard ranks members from the economy cog's in-memory cache, which is
populated lazily as members use economy commands. This step warms that cache
from the database on boot so every member with saved economy data shows up on
the leaderboard immediately, even before they interact with an economy command
after a restart.
"""

from utils import logging


async def preload_economy_cache(bot):
    """Populate the economy cog's cache with all users from the database."""
    cog = bot.get_cog("EconomyCog")
    if cog is None:
        logging.warning("Economy", "EconomyCog not loaded; skipping economy cache warm-up.")
        return
    try:
        await cog.prime_cache()
    except Exception as exc:
        logging.error("Economy", f"Failed to warm up economy cache: {exc}")