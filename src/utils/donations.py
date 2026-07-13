"""
Donation database helpers.
Used by the donations cog and by userinfo badge lookup.
"""


async def is_supporter(bot, user_id: int) -> bool:
    """Return True if user_id has at least one confirmed donation."""
    if not getattr(bot, "cxn", None):
        return False
    try:
        row = await bot.cxn.fetchrow(
            "SELECT 1 FROM donors WHERE user_id = $1", user_id
        )
        return row is not None
    except Exception:
        return False


async def add_donor(bot, user_id: int, amount: float, currency: str, track_id: str) -> None:
    """Insert or update a donor record after a confirmed payment."""
    if not getattr(bot, "cxn", None):
        return
    await bot.cxn.execute(
        """
        INSERT INTO donors (user_id, total_donated, last_donation, last_track_id)
        VALUES ($1, $2, datetime('now'), $3)
        ON CONFLICT(user_id) DO UPDATE SET
            total_donated = total_donated + $2,
            last_donation  = datetime('now'),
            last_track_id  = $3
        """,
        user_id, amount, track_id,
    )


async def get_total_donated(bot, user_id: int) -> float:
    """Return the total USD donated by user_id, or 0.0."""
    if not getattr(bot, "cxn", None):
        return 0.0
    try:
        row = await bot.cxn.fetchrow(
            "SELECT total_donated FROM donors WHERE user_id = $1", user_id
        )
        return float(row["total_donated"]) if row else 0.0
    except Exception:
        return 0.0
