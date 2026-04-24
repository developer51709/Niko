"""
Blacklist Manager for Niko AI
Handles blacklist management for users and guilds

This feature was added to prevent abuse of the AI features and to ensure that the bot is not used for malicious purposes.

The blacklist is stored in a JSON file and is loaded when the bot starts. The blacklist can be updated by the bot owner using the `blacklist` command located in the owner cog.

This file only handles the storing and retrieving of blacklisted users, guilds, and channels. 
The actual blacklist checks are handled in the error_handler cog.
"""

import json
import os
from typing import List, Dict, Union
from utils import logging

BLACKLIST_FILE = "data/blacklist.json"


class BlacklistManager:
    def __init__(self):
        # Default structure
        self.blacklist: Dict[str, List[int]] = {
            "users": [],
            "guilds": []
        }

        # Load blacklist from file
        try:
            with open(BLACKLIST_FILE, "r") as f:
                data = json.load(f)

                # Ensure required keys exist
                self.blacklist["users"] = data.get("users", [])
                self.blacklist["guilds"] = data.get("guilds", [])

        except FileNotFoundError:
            # Create file if missing
            self._save()
            logging.info("blacklist_manager", "Blacklist file created because it did not exist.")
        except json.JSONDecodeError:
            logging.error("blacklist_manager", "Blacklist file is corrupted. Recreating a clean one.")
            self._save()

    # -----------------------------
    # Internal save helper
    # -----------------------------
    def _save(self) -> None:
        """Write the current blacklist to disk."""
        os.makedirs(os.path.dirname(BLACKLIST_FILE), exist_ok=True)
        with open(BLACKLIST_FILE, "w") as f:
            json.dump(self.blacklist, f, indent=4)
        logging.debug("blacklist_manager", "Blacklist saved to disk.")

    # -----------------------------
    # Add operations
    # -----------------------------
    def add_user(self, user_id: int) -> bool:
        """Add a user to the blacklist. Returns True if added."""
        if user_id not in self.blacklist["users"]:
            self.blacklist["users"].append(user_id)
            self._save()
            logging.info("blacklist_manager", f"User {user_id} added to blacklist.")
            return True
        return False

    def add_guild(self, guild_id: int) -> bool:
        """Add a guild to the blacklist. Returns True if added."""
        if guild_id not in self.blacklist["guilds"]:
            self.blacklist["guilds"].append(guild_id)
            self._save()
            logging.info("blacklist_manager", f"Guild {guild_id} added to blacklist.")
            return True
        return False

    # -----------------------------
    # Remove operations
    # -----------------------------
    def remove_user(self, user_id: int) -> bool:
        """Remove a user from the blacklist. Returns True if removed."""
        if user_id in self.blacklist["users"]:
            self.blacklist["users"].remove(user_id)
            self._save()
            logging.info("blacklist_manager", f"User {user_id} removed from blacklist.")
            return True
        return False

    def remove_guild(self, guild_id: int) -> bool:
        """Remove a guild from the blacklist. Returns True if removed."""
        if guild_id in self.blacklist["guilds"]:
            self.blacklist["guilds"].remove(guild_id)
            self._save()
            logging.info("blacklist_manager", f"Guild {guild_id} removed from blacklist.")
            return True
        return False

    # -----------------------------
    # Check operations
    # -----------------------------
    def is_user_blacklisted(self, user_id: int) -> bool:
        """Check if a user is blacklisted."""
        return user_id in self.blacklist["users"]

    def is_guild_blacklisted(self, guild_id: int) -> bool:
        """Check if a guild is blacklisted."""
        return guild_id in self.blacklist["guilds"]

    # -----------------------------
    # Retrieval
    # -----------------------------
    def get_blacklisted_users(self) -> List[int]:
        return self.blacklist["users"]

    def get_blacklisted_guilds(self) -> List[int]:
        return self.blacklist["guilds"]