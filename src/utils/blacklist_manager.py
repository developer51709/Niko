"""
Blacklist Manager for Niko AI
Handles blacklist management for users and guilds.

This feature was added to prevent abuse of the AI features and to ensure that
the bot is not used for malicious purposes.

The blacklist is stored in a JSON file and loaded once on first instantiation.
A singleton pattern is used so callers can call `BlacklistManager()` cheaply
without re-reading disk on every check.

Each entry is stored as a dict:
    { "id": int, "reason": str | None, "timestamp": float, "added_by": int | None }

The legacy "list of plain ints" format is auto-migrated on first load.

This file only handles the storing and retrieving of blacklisted users and
guilds. The actual blacklist enforcement is in `bot.py` and `error_handler.py`.
"""

import json
import os
import time
from typing import List, Dict, Optional, Any

from utils import logging

BLACKLIST_FILE = "data/blacklist.json"


class BlacklistManager:
    """
    Singleton blacklist manager. The first call loads from disk; every
    subsequent `BlacklistManager()` returns the same cached instance.
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
        self._load()

    # -----------------------------
    # Persistence
    # -----------------------------
    def _load(self) -> None:
        try:
            with open(BLACKLIST_FILE, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            self._save()
            logging.info("blacklist_manager", "Blacklist file created because it did not exist.")
            return
        except json.JSONDecodeError:
            logging.error("blacklist_manager", "Blacklist file is corrupted. Recreating a clean one.")
            self._save()
            return

        self.blacklist["users"]  = self._migrate(data.get("users",  []))
        self.blacklist["guilds"] = self._migrate(data.get("guilds", []))

        # If anything was migrated from legacy plain-int format, persist now
        if any(isinstance(x, int) for x in data.get("users", [])) or \
           any(isinstance(x, int) for x in data.get("guilds", [])):
            self._save()
            logging.info("blacklist_manager", "Migrated legacy blacklist entries to new format.")

    def _migrate(self, raw: list) -> List[Dict[str, Any]]:
        """Accept either plain ints or full dicts and return the dict form."""
        out: List[Dict[str, Any]] = []
        seen: set = set()
        for item in raw:
            if isinstance(item, int):
                if item in seen:
                    continue
                seen.add(item)
                out.append({
                    "id":        item,
                    "reason":    None,
                    "timestamp": time.time(),
                    "added_by":  None,
                })
            elif isinstance(item, dict) and "id" in item:
                if item["id"] in seen:
                    continue
                seen.add(item["id"])
                out.append({
                    "id":        int(item["id"]),
                    "reason":    item.get("reason"),
                    "timestamp": float(item.get("timestamp", time.time())),
                    "added_by":  item.get("added_by"),
                })
        return out

    def _save(self) -> None:
        os.makedirs(os.path.dirname(BLACKLIST_FILE), exist_ok=True)
        with open(BLACKLIST_FILE, "w") as f:
            json.dump(self.blacklist, f, indent=4)
        logging.debug("blacklist_manager", "Blacklist saved to disk.")

    def reload(self) -> None:
        """Force a re-read from disk (useful after manual edits)."""
        self._load()

    # -----------------------------
    # Add operations
    # -----------------------------
    def add_user(
        self,
        user_id: int,
        *,
        reason: Optional[str] = None,
        added_by: Optional[int] = None,
    ) -> bool:
        """Add a user to the blacklist. Returns True if added (False if already there)."""
        if self.is_user_blacklisted(user_id):
            return False
        self.blacklist["users"].append({
            "id":        int(user_id),
            "reason":    reason,
            "timestamp": time.time(),
            "added_by":  added_by,
        })
        self._save()
        logging.info("blacklist_manager", f"User {user_id} added to blacklist (reason: {reason}).")
        return True

    def add_guild(
        self,
        guild_id: int,
        *,
        reason: Optional[str] = None,
        added_by: Optional[int] = None,
    ) -> bool:
        """Add a guild to the blacklist. Returns True if added (False if already there)."""
        if self.is_guild_blacklisted(guild_id):
            return False
        self.blacklist["guilds"].append({
            "id":        int(guild_id),
            "reason":    reason,
            "timestamp": time.time(),
            "added_by":  added_by,
        })
        self._save()
        logging.info("blacklist_manager", f"Guild {guild_id} added to blacklist (reason: {reason}).")
        return True

    # -----------------------------
    # Remove operations
    # -----------------------------
    def remove_user(self, user_id: int) -> bool:
        before = len(self.blacklist["users"])
        self.blacklist["users"] = [e for e in self.blacklist["users"] if e["id"] != user_id]
        if len(self.blacklist["users"]) == before:
            return False
        self._save()
        logging.info("blacklist_manager", f"User {user_id} removed from blacklist.")
        return True

    def remove_guild(self, guild_id: int) -> bool:
        before = len(self.blacklist["guilds"])
        self.blacklist["guilds"] = [e for e in self.blacklist["guilds"] if e["id"] != guild_id]
        if len(self.blacklist["guilds"]) == before:
            return False
        self._save()
        logging.info("blacklist_manager", f"Guild {guild_id} removed from blacklist.")
        return True

    # -----------------------------
    # Update reason
    # -----------------------------
    def update_user_reason(self, user_id: int, reason: Optional[str]) -> bool:
        for e in self.blacklist["users"]:
            if e["id"] == user_id:
                e["reason"] = reason
                self._save()
                return True
        return False

    def update_guild_reason(self, guild_id: int, reason: Optional[str]) -> bool:
        for e in self.blacklist["guilds"]:
            if e["id"] == guild_id:
                e["reason"] = reason
                self._save()
                return True
        return False

    # -----------------------------
    # Check operations
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
