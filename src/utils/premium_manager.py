"""
PremiumManager — flat JSON store for bot-wide premium users.

File: data/premium_users.json
Schema: {"users": [<user_id_int>, ...]}

All methods are synchronous and safe to call from any coroutine
via asyncio.to_thread if needed, but the file is tiny so blocking
I/O is negligible.
"""
from __future__ import annotations

import json
import os

_FILE = "data/premium_users.json"


def _load() -> dict:
    if not os.path.exists(_FILE):
        return {"users": []}
    try:
        with open(_FILE) as f:
            data = json.load(f)
        if "users" not in data:
            data["users"] = []
        return data
    except Exception:
        return {"users": []}


def _save(data: dict) -> None:
    os.makedirs("data", exist_ok=True)
    with open(_FILE, "w") as f:
        json.dump(data, f, indent=2)


class PremiumManager:

    @staticmethod
    def is_premium(user_id: int) -> bool:
        """Return True if *user_id* has been granted premium."""
        return user_id in _load()["users"]

    @staticmethod
    def add(user_id: int) -> bool:
        """
        Grant premium to *user_id*.
        Returns True if the user was newly added, False if already present.
        """
        data = _load()
        if user_id in data["users"]:
            return False
        data["users"].append(user_id)
        _save(data)
        return True

    @staticmethod
    def remove(user_id: int) -> bool:
        """
        Revoke premium from *user_id*.
        Returns True if removed, False if they were not in the list.
        """
        data = _load()
        if user_id not in data["users"]:
            return False
        data["users"].remove(user_id)
        _save(data)
        return True

    @staticmethod
    def list_users() -> list[int]:
        """Return a list of all premium user IDs."""
        return list(_load()["users"])

