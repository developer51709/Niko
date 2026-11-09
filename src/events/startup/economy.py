"""
Startup — reset the economy account cache.

The economy cog caches the accounts its commands are working with, capped to the
most recently used ones (``EconomyCog.get_user_economy_data``). It used to warm
that cache with every row of ``economy_users`` on boot, so an in-memory
leaderboard was complete before anyone ran a command. The leaderboard is the
website's now — it reads the table itself — and the warm-up cost ~15 KB of memory
per member with saved data (plus a query per member), which is why this step only
drops anything cached before the database was reachable.
"""

from utils import logging


async def preload_economy_cache(bot):
    """Drop economy accounts cached before the database was reachable."""
    cog = bot.get_cog("EconomyCog")
    if cog is None:
        logging.warning("Economy", "EconomyCog not loaded; skipping economy cache reset.")
        return
    try:
        # Nothing is warmed here any more: accounts are loaded by the commands
        # that need them and evicted once they go idle. Clearing first keeps a
        # partial first pass from outliving the database becoming reachable.
        cog.economy_data.clear()
        used = getattr(cog, "_account_used", None)
        if used is not None:
            used.clear()
    except Exception as exc:
        logging.error("Economy", f"Failed to reset economy cache: {exc}")
