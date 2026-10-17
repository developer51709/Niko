"""Async database-backed storage for bot-wide premium users."""
from __future__ import annotations


class PremiumManager:
    """Read and update premium grants in the bot's primary database."""

    @staticmethod
    def _require_pool(pool):
        if pool is None:
            raise RuntimeError("The primary database is not available")
        return pool

    @classmethod
    async def is_premium(cls, pool, user_id: int) -> bool:
        """Return whether *user_id* has been granted premium."""
        pool = cls._require_pool(pool)
        return await pool.fetchval(
            "SELECT user_id FROM premium_users WHERE user_id = $1", int(user_id)
        ) is not None

    @classmethod
    async def add(cls, pool, user_id: int) -> bool:
        """Grant premium; return False when the user already has it."""
        pool = cls._require_pool(pool)
        user_id = int(user_id)
        if await cls.is_premium(pool, user_id):
            return False
        await pool.execute(
            "INSERT OR IGNORE INTO premium_users (user_id) VALUES ($1)", user_id
        )
        return True

    @classmethod
    async def remove(cls, pool, user_id: int) -> bool:
        """Revoke premium; return False when the user had no grant."""
        pool = cls._require_pool(pool)
        user_id = int(user_id)
        if not await cls.is_premium(pool, user_id):
            return False
        await pool.execute(
            "DELETE FROM premium_users WHERE user_id = $1", user_id
        )
        return True

    @classmethod
    async def list_users(cls, pool) -> list[int]:
        """Return all premium user IDs."""
        pool = cls._require_pool(pool)
        rows = await pool.fetch("SELECT user_id FROM premium_users ORDER BY user_id")
        return [int(row["user_id"]) for row in rows]
