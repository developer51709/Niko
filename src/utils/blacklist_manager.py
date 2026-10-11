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
    { "id": int, "reason": str | None, "timestamp": float, "added_by": int | None, "expires_at": float | None }

Legacy data in `data/blacklist.json` is migrated to the database by
`events/startup/database.py` on first boot.

This file only handles the storing and retrieving of blacklisted users and
guilds. The actual blacklist enforcement is in `bot.py` and `error_handler.py`.
"""

import asyncio
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

        # entry shape includes expires_at (None for permanent entries).
        self._write_lock = asyncio.Lock()
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
            "expires_at": float(row["expires_at"]) if row.get("expires_at") is not None else None,
            "status": row.get("status"),
        }

    async def load(self) -> None:
        """Load all blacklist entries from the database into the cache."""
        pool = self._pool()
        if pool is None:
            logging.warning("blacklist_manager", "Database pool not available; blacklist cache stays empty.")
            self._loaded = True
            return

        try:
            await pool.execute("ALTER TABLE blacklist_users ADD COLUMN expires_at REAL")
        except Exception:
            pass  # Column already exists on the current schema.

        try:
            now = time.time()
            await pool.execute(
                "DELETE FROM blacklist_users WHERE status = 'active' AND expires_at IS NOT NULL AND expires_at <= $1",
                now,
            )
            await pool.execute("CREATE TABLE IF NOT EXISTS abuse_strikes (user_id INTEGER PRIMARY KEY, strikes INTEGER NOT NULL DEFAULT 0, updated_at REAL NOT NULL)")
            user_rows = await pool.fetch(
                "SELECT id, reason, timestamp, added_by, expires_at, status FROM blacklist_users WHERE status = 'active' OR status IS NULL"
            )
            guild_rows = await pool.fetch(
                "SELECT id, reason, timestamp, added_by, status FROM blacklist_guilds WHERE status = 'active' OR status IS NULL"
            )
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
        expires_at: Optional[float] = None,
    ) -> bool:
        """Add a user to the blacklist. Returns True if added (False if already there)."""
        await self._ensure_loaded()
        async with self._write_lock:
            return await self._add_user_locked(user_id, reason=reason, added_by=added_by, expires_at=expires_at)

    async def _add_user_locked(
        self,
        user_id: int,
        *,
        reason: Optional[str],
        added_by: Optional[int],
        expires_at: Optional[float],
    ) -> bool:
        if self.is_user_blacklisted(user_id):
            return False
        entry = {
            "id":        int(user_id),
            "reason":    reason,
            "timestamp": time.time(),
            "added_by":  added_by,
            "expires_at": expires_at,
        }
        pool = self._pool()
        if pool is None:
            logging.error("blacklist_manager", "Cannot add user to blacklist without a database pool.")
            return False
        try:
            await pool.execute(
                "DELETE FROM blacklist_users WHERE id = $1 AND status = 'active' AND expires_at IS NOT NULL AND expires_at <= $2",
                int(user_id), time.time(),
            )
            await pool.execute(
                "INSERT INTO blacklist_users (id, reason, timestamp, added_by, expires_at, status, appeal_id) VALUES ($1, $2, $3, $4, $5, 'active', NULL) ON CONFLICT(id) DO UPDATE SET reason = excluded.reason, timestamp = excluded.timestamp, added_by = excluded.added_by, expires_at = excluded.expires_at, status = 'active', appeal_id = NULL",
                int(user_id), reason, entry["timestamp"], added_by, expires_at,
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
        guild_id = int(guild_id)
        async with self._write_lock:
            if self.is_guild_blacklisted(guild_id):
                return False
            pool = self._pool()
            if pool is None:
                logging.error("blacklist_manager", "Cannot add guild to blacklist without a database pool.")
                return False
            entry = {
                "id": guild_id,
                "reason": reason,
                "timestamp": time.time(),
                "added_by": added_by,
            }
            try:
                await pool.execute(
                    "INSERT OR REPLACE INTO blacklist_guilds (id, reason, timestamp, added_by, status, appeal_id) VALUES ($1, $2, $3, $4, 'active', NULL)",
                    *self._entry_to_row(entry),
                )
                saved = await pool.fetchrow(
                    "SELECT id, reason, timestamp, added_by, status FROM blacklist_guilds WHERE id = $1",
                    guild_id,
                )
                if not saved:
                    logging.error("blacklist_manager", f"Guild {guild_id} blacklist write did not persist.")
                    return False
                if int(saved["id"]) != guild_id:
                    return False
                if self.is_guild_blacklisted(guild_id):
                    return False
                self.blacklist["guilds"].append(self._row_to_entry(saved))
            except Exception as e:
                logging.error("blacklist_manager", f"Failed to save blacklisted guild {guild_id}: {e}")
                return False
        logging.info("blacklist_manager", f"Guild {guild_id} added to blacklist (reason: {reason}).")
        return True

    # -----------------------------
    # Remove operations
    # -----------------------------
    async def remove_user(self, user_id: int) -> bool:
        await self._ensure_loaded()
        async with self._write_lock:
            before = len(self.blacklist["users"])
            updated = [e for e in self.blacklist["users"] if e["id"] != user_id]
            pool = self._pool()
            if pool is not None:
                try:
                    await pool.execute("DELETE FROM blacklist_users WHERE id = $1", int(user_id))
                except Exception as e:
                    logging.error("blacklist_manager", f"Failed to remove blacklisted user {user_id}: {e}")
                    return False
            elif len(updated) == before:
                return False
            self.blacklist["users"] = updated
        logging.info("blacklist_manager", f"User {user_id} removed from blacklist.")
        return True

    async def register_abuse_strike(self, user_id: int, *, reason: str) -> Dict[str, Any]:
        """Persist a strike and apply an escalating blacklist, permanently on strike three."""
        await self._ensure_loaded()
        async with self._write_lock:
            pool = self._pool()
            if pool is None:
                logging.error("blacklist_manager", "Cannot persist abuse strike without a database pool.")
                return {"strikes": 0, "blacklisted": False, "permanent": False, "expires_at": None}

            now = time.time()
            try:
                row = await pool.fetchrow("SELECT strikes FROM abuse_strikes WHERE user_id = $1", int(user_id))
                strikes = min(3, int(row["strikes"] if row else 0) + 1)
                await pool.execute(
                    "INSERT OR REPLACE INTO abuse_strikes (user_id, strikes, updated_at) VALUES ($1, $2, $3)",
                    int(user_id), strikes, now,
                )
                permanent = strikes >= 3
                duration_seconds = (60 * 60, 24 * 60 * 60)[strikes - 1] if strikes < 3 else None
                expires_at = now + duration_seconds if duration_seconds is not None else None
                blacklist_reason = f"Automated anti-abuse: {reason} (strike {strikes}/3)."
                await pool.execute(
                    "DELETE FROM blacklist_users WHERE id = $1 AND status = 'active' AND expires_at IS NOT NULL AND expires_at <= $2",
                    int(user_id), now,
                )
                existing = self.get_user_entry(user_id)
                if existing:
                    if existing.get("expires_at") is None:
                        return {"strikes": strikes, "blacklisted": False, "permanent": True, "expires_at": None}
                if existing:
                    await pool.execute(
                        "UPDATE blacklist_users SET reason = $1, timestamp = $2, added_by = NULL, expires_at = $3, status = 'active', appeal_id = NULL WHERE id = $4",
                        blacklist_reason, now, expires_at, int(user_id),
                    )
                    entry = {
                        "id": int(user_id),
                        "reason": blacklist_reason,
                        "timestamp": now,
                        "added_by": None,
                        "expires_at": expires_at,
                    }
                    self.blacklist["users"].append(entry)
                    added = True
                else:
                    added = await self._add_user_locked(
                        user_id,
                        reason=blacklist_reason,
                        added_by=None,
                        expires_at=expires_at,
                    )
                return {"strikes": strikes, "blacklisted": added, "permanent": permanent, "expires_at": expires_at}
            except Exception as e:
                logging.error("blacklist_manager", f"Failed to register abuse strike for user {user_id}: {e}")
                return {"strikes": 0, "blacklisted": False, "permanent": False, "expires_at": None}

    async def remove_guild(self, guild_id: int) -> bool:
        await self._ensure_loaded()
        guild_id = int(guild_id)
        async with self._write_lock:
            entry = self.get_guild_entry(guild_id)
            if entry is None:
                return False
            pool = self._pool()
            if pool is None:
                logging.error("blacklist_manager", "Cannot remove guild from blacklist without a database pool.")
                return False
            try:
                await pool.execute("DELETE FROM blacklist_guilds WHERE id = $1", guild_id)
                remaining = await pool.fetchrow(
                    "SELECT id FROM blacklist_guilds WHERE id = $1",
                    guild_id,
                )
                if remaining:
                    logging.error("blacklist_manager", f"Guild {guild_id} blacklist removal did not persist.")
                    return False
            except Exception as e:
                logging.error("blacklist_manager", f"Failed to remove blacklisted guild {guild_id}: {e}")
                return False
            self.blacklist["guilds"] = [
                item for item in self.blacklist["guilds"] if item["id"] != guild_id
            ]
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
        if pool is None:
            logging.error("blacklist_manager", "Cannot update guild blacklist without a database pool.")
            return False
        try:
            await pool.execute(
                "UPDATE blacklist_guilds SET reason = $1 WHERE id = $2",
                reason,
                int(guild_id),
            )
            saved = await pool.fetchrow(
                "SELECT reason FROM blacklist_guilds WHERE id = $1",
                int(guild_id),
            )
            if not saved or saved["reason"] != reason:
                logging.error("blacklist_manager", f"Guild {guild_id} blacklist reason update did not persist.")
                return False
        except Exception as e:
            logging.error("blacklist_manager", f"Failed to update reason for guild {guild_id}: {e}")
            return False
        entry["reason"] = reason
        return True

    # -----------------------------
    # Check operations (sync — hot path)
    # -----------------------------
    def is_user_blacklisted(self, user_id: int) -> bool:
        return self.get_user_entry(user_id) is not None

    def is_guild_blacklisted(self, guild_id: int) -> bool:
        return self.get_guild_entry(guild_id) is not None

    # -----------------------------
    # Lookup
    # -----------------------------
    def get_user_entry(self, user_id: int) -> Optional[Dict[str, Any]]:
        now = time.time()
        for e in self.blacklist["users"]:
            if e["id"] == user_id:
                expires_at = e.get("expires_at")
                if expires_at is not None and expires_at <= now:
                    self.blacklist["users"].remove(e)
                    return None
                return e
        return None

    def get_guild_entry(self, guild_id: int) -> Optional[Dict[str, Any]]:
        guild_id = int(guild_id)
        for e in self.blacklist["guilds"]:
            if e["id"] == guild_id:
                return e
        return None

    # -----------------------------
    # Retrieval — backward-compatible plain-int lists
    # -----------------------------
    def get_blacklisted_users(self) -> List[int]:
        active_entries = self.get_user_entries()
        return [e["id"] for e in active_entries]

    def get_blacklisted_guilds(self) -> List[int]:
        return [e["id"] for e in self.get_guild_entries()]

    # New: full entries
    def get_user_entries(self) -> List[Dict[str, Any]]:
        now = time.time()
        active = []
        for entry in self.blacklist["users"]:
            expires_at = entry.get("expires_at")
            if expires_at is None or expires_at > now:
                active.append(entry)
        self.blacklist["users"] = active
        return list(active)

    def get_guild_entries(self) -> List[Dict[str, Any]]:
        return list(self.blacklist["guilds"])
