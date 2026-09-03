"""
Blacklist Manager for Niko AI
Handles blacklist management for users and guilds.

This feature was added to prevent abuse of the AI features and to ensure that
the bot is not used for malicious purposes.

The blacklist is stored in the main database (`blacklist_users` /
`blacklist_guilds` tables). A singleton pattern is used so callers can call
`BlacklistManager()` cheaply. Hot-path reads (message/interaction checks) stay
synchronous against an in-memory cache that is loaded from the database once
at startup and kept in sync by the async write methods.

Each entry is stored as a dict:
    { "id": int, "reason": str | None, "timestamp": float, "added_by": int | None }

Legacy data in `data/blacklist.json` is migrated to the database by
`events/startup/database.py` on first boot.

This file only handles the storing and retrieving of blacklisted users and
guilds. The actual blacklist enforcement is in `bot.py` and `error_handler.py`.
"""

import time
from typing import List, Dict, Optional, Any

import database as database_module
from utils import logging

# Legacy file — only read by the startup migration now.
BLACKLIST_FILE = "data/blacklist.json"


class BlacklistManager:
    """
    Singleton blacklist manager. Reads hit an in-memory cache (loaded from the
    database via `await BlacklistManager().load()`), writes go through to the
    database and update the cache.
    """

    _instance: "Optional[BlacklistManager]" = None

    def __new__(cls) -> "BlacklistManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        # entry shape: {"id": int, "reason": str|None, "timestamp": float, "added_by": int|None}
        self.blacklist: Dict[str, List[Dict[str, Any]]] = {
            "users":  [],
            "guilds": [],
        }
        self._loaded = False

    # -----------------------------
    # Persistence
    # -----------------------------
    @staticmethod
    def _pool():
        return getattr(database_module, "_shared_pool", None)

    @staticmethod
    def _entry_to_row(entry: Dict[str, Any]) -> tuple:
        return (int(entry["id"]), entry.get("reason"), entry.get("timestamp"), entry.get("added_by"))

    @staticmethod
    def _row_to_entry(row) -> Dict[str, Any]:
        return {
            "id":        int(row["id"]),
            "reason":    row.get("reason"),
            "timestamp": float(row["timestamp"]) if row.get("timestamp") is not None else time.time(),
            "added_by":  row.get("added_by"),
        }

    async def load(self) -> None:
        """Load all blacklist entries from the database into the cache."""
        pool = self._pool()
        if pool is None:
            logging.warning("blacklist_manager", "Database pool not available; blacklist cache stays empty.")
            self._loaded = True
            return

        try:
            user_rows  = await pool.fetch("SELECT id, reason, timestamp, added_by FROM blacklist_users")
            guild_rows = await pool.fetch("SELECT id, reason, timestamp, added_by FROM blacklist_guilds")
        except Exception as e:
            logging.error("blacklist_manager", f"Failed to load blacklist from database: {e}")
            self._loaded = True
            return

        self.blacklist["users"]  = [self._row_to_entry(r) for r in user_rows]
        self.blacklist["guilds"] = [self._row_to_entry(r) for r in guild_rows]
        self._loaded = True
        logging.debug(
            "blacklist_manager",
            f"Loaded {len(self.blacklist['users'])} users and {len(self.blacklist['guilds'])} guilds from database.",
        )

    async def _ensure_loaded(self) -> None:
        if not self._loaded:
            await self.load()

    async def reload(self) -> None:
        """Force a re-read from the database (useful after manual edits)."""
        await self.load()

    # -----------------------------
    # Add operations
    # -----------------------------
    async def add_user(
        self,
        user_id: int,
        *,
        reason: Optional[str] = None,
        added_by: Optional[int] = None,
    ) -> bool:
        """Add a user to the blacklist. Returns True if added (False if already there)."""
        await self._ensure_loaded()
        if self.is_user_blacklisted(user_id):
            return False
        entry = {
            "id":        int(user_id),
            "reason":    reason,
            "timestamp": time.time(),
            "added_by":  added_by,
        }
        pool = self._pool()
        if pool is not None:
            try:
                await pool.execute(
                    "INSERT OR IGNORE INTO blacklist_users (id, reason, timestamp, added_by) VALUES ($1, $2, $3, $4)",
                    *self._entry_to_row(entry),
                )
            except Exception as e:
                logging.error("blacklist_manager", f"Failed to save blacklisted user {user_id}: {e}")
                return False
        self.blacklist["users"].append(entry)
        logging.info("blacklist_manager", f"User {user_id} added to blacklist (reason: {reason}).")
        return True

    async def add_guild(
        self,
        guild_id: int,
        *,
        reason: Optional[str] = None,
        added_by: Optional[int] = None,
    ) -> bool:
        """Add a guild to the blacklist. Returns True if added (False if already there)."""
        await self._ensure_loaded()
        if self.is_guild_blacklisted(guild_id):
            return False
        entry = {
            "id":        int(guild_id),
            "reason":    reason,
            "timestamp": time.time(),
            "added_by":  added_by,
        }
        pool = self._pool()
        if pool is not None:
            try:
                await pool.execute(
                    "INSERT OR IGNORE INTO blacklist_guilds (id, reason, timestamp, added_by) VALUES ($1, $2, $3, $4)",
                    *self._entry_to_row(entry),
                )
            except Exception as e:
                logging.error("blacklist_manager", f"Failed to save blacklisted guild {guild_id}: {e}")
                return False
        self.blacklist["guilds"].append(entry)
        logging.info("blacklist_manager", f"Guild {guild_id} added to blacklist (reason: {reason}).")
        return True

    # -----------------------------
    # Remove operations
    # -----------------------------
    async def remove_user(self, user_id: int) -> bool:
        await self._ensure_loaded()
        before = len(self.blacklist["users"])
        self.blacklist["users"] = [e for e in self.blacklist["users"] if e["id"] != user_id]
        if len(self.blacklist["users"]) == before:
            return False
        pool = self._pool()
        if pool is not None:
            try:
                await pool.execute("DELETE FROM blacklist_users WHERE id = $1", int(user_id))
            except Exception as e:
                logging.error("blacklist_manager", f"Failed to remove blacklisted user {user_id}: {e}")
                return False
        logging.info("blacklist_manager", f"User {user_id} removed from blacklist.")
        return True

    async def remove_guild(self, guild_id: int) -> bool:
        await self._ensure_loaded()
        before = len(self.blacklist["guilds"])
        self.blacklist["guilds"] = [e for e in self.blacklist["guilds"] if e["id"] != guild_id]
        if len(self.blacklist["guilds"]) == before:
            return False
        pool = self._pool()
        if pool is not None:
            try:
                await pool.execute("DELETE FROM blacklist_guilds WHERE id = $1", int(guild_id))
            except Exception as e:
                logging.error("blacklist_manager", f"Failed to remove blacklisted guild {guild_id}: {e}")
                return False
        logging.info("blacklist_manager", f"Guild {guild_id} removed from blacklist.")
        return True

    # -----------------------------
    # Update reason
    # -----------------------------
    async def update_user_reason(self, user_id: int, reason: Optional[str]) -> bool:
        await self._ensure_loaded()
        entry = self.get_user_entry(user_id)
        if entry is None:
            return False
        pool = self._pool()
        if pool is not None:
            try:
                await pool.execute(
                    "UPDATE blacklist_users SET reason = $1 WHERE id = $2",
                    reason,
                    int(user_id),
                )
            except Exception as e:
                logging.error("blacklist_manager", f"Failed to update reason for user {user_id}: {e}")
                return False
        entry["reason"] = reason
        return True

    async def update_guild_reason(self, guild_id: int, reason: Optional[str]) -> bool:
        await self._ensure_loaded()
        entry = self.get_guild_entry(guild_id)
        if entry is None:
            return False
        pool = self._pool()
        if pool is not None:
            try:
                await pool.execute(
                    "UPDATE blacklist_guilds SET reason = $1 WHERE id = $2",
                    reason,
                    int(guild_id),
                )
            except Exception as e:
                logging.error("blacklist_manager", f"Failed to update reason for guild {guild_id}: {e}")
                return False
        entry["reason"] = reason
        return True

    # -----------------------------
    # Check operations (sync — hot path)
    # -----------------------------
    def is_user_blacklisted(self, user_id: int) -> bool:
        return any(e["id"] == user_id for e in self.blacklist["users"])

    def is_guild_blacklisted(self, guild_id: int) -> bool:
        return any(e["id"] == guild_id for e in self.blacklist["guilds"])

    # -----------------------------
    # Lookup
    # -----------------------------
    def get_user_entry(self, user_id: int) -> Optional[Dict[str, Any]]:
        for e in self.blacklist["users"]:
            if e["id"] == user_id:
                return e
        return None

    def get_guild_entry(self, guild_id: int) -> Optional[Dict[str, Any]]:
        for e in self.blacklist["guilds"]:
            if e["id"] == guild_id:
                return e
        return None

    # -----------------------------
    # Retrieval — backward-compatible plain-int lists
    # -----------------------------
    def get_blacklisted_users(self) -> List[int]:
        return [e["id"] for e in self.blacklist["users"]]

    def get_blacklisted_guilds(self) -> List[int]:
        return [e["id"] for e in self.blacklist["guilds"]]

    # New: full entries
    def get_user_entries(self) -> List[Dict[str, Any]]:
        return list(self.blacklist["users"])

    def get_guild_entries(self) -> List[Dict[str, Any]]:
        return list(self.blacklist["guilds"])