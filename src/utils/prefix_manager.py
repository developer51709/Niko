import json
import os
from utils import logging

PREFIX_FILE = "data/prefixes.json"
DEFAULT_PREFIXES = ["."]


def _load_all() -> dict:
    if not os.path.exists(PREFIX_FILE):
        os.makedirs(os.path.dirname(PREFIX_FILE), exist_ok=True)
        with open(PREFIX_FILE, "w") as f:
            json.dump({}, f, indent=4)
        return {}

    try:
        with open(PREFIX_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error("prefix_manager", f"Failed to load prefix file: {e}")
        return {}


def _save_all(data: dict):
    try:
        with open(PREFIX_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logging.error("prefix_manager", f"Failed to save prefix file: {e}")


def get_prefixes(guild_id: int):
    data = _load_all()
    gid = str(guild_id)

    if gid not in data:
        data[gid] = DEFAULT_PREFIXES.copy()
        _save_all(data)

    return data[gid]


def add_prefix(guild_id: int, prefix: str):
    data = _load_all()
    gid = str(guild_id)

    if gid not in data:
        data[gid] = DEFAULT_PREFIXES.copy()

    if prefix not in data[gid]:
        data[gid].append(prefix)

    _save_all(data)


def remove_prefix(guild_id: int, prefix: str):
    data = _load_all()
    gid = str(guild_id)

    if gid in data and prefix in data[gid]:
        data[gid].remove(prefix)

    _save_all(data)


def reset_prefixes(guild_id: int):
    data = _load_all()
    gid = str(guild_id)

    data[gid] = DEFAULT_PREFIXES.copy()
    _save_all(data)


def dynamic_prefix(bot, message):
    """Command-prefix callable for discord.py — returns list of prefixes for the guild."""
    if not message.guild:
        return ["."]
    return get_prefixes(message.guild.id)
