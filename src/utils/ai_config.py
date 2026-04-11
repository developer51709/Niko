import json
import os
from typing import Union, Optional
from utils import logging

AI_CONFIG_FILE = "data/ai_config.json"

DEFAULT_CONFIG = {
    "personality": "cafe",
    "enabled": "True",
}


# ----------------------------------------------------
# Internal helpers
# ----------------------------------------------------

def _load_all() -> dict:
    """Load the entire config file, creating it if missing."""
    if not os.path.exists(AI_CONFIG_FILE):
        os.makedirs(os.path.dirname(AI_CONFIG_FILE), exist_ok=True)
        with open(AI_CONFIG_FILE, "w") as f:
            json.dump({}, f, indent=4)
        return {}

    try:
        with open(AI_CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error("ai_config", f"Failed to load AI config: {e}")
        return {}


def _save_all(data: dict) -> None:
    """Write the entire config file to disk."""
    try:
        with open(AI_CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logging.error("ai_config", f"Failed to save AI config: {e}")


def get_personality(ctx):
    if ctx and ctx.guild:
        guild_id = ctx.guild.id
        personality = get_ai_config(guild_id, "personality")
        if personality:
            return personality
    return "normal"


# ----------------------------------------------------
# Public API
# ----------------------------------------------------

def get_ai_config(guild_id: int, key: Optional[str] = None) -> Union[dict, str, bool, None]:
    """
    Get the AI config for a guild.
    - If key is None → return full dict
    - If key is provided → return value or None
    """
    all_data = _load_all()

    guild_id = str(guild_id)

    # Create default config if missing
    if guild_id not in all_data:
        all_data[guild_id] = DEFAULT_CONFIG.copy()
        _save_all(all_data)

    cfg = all_data[guild_id]

    if key is None:
        return cfg

    return cfg.get(key)


def set_ai_config(guild_id: int, key: str, value: Union[str, bool, int, dict]) -> None:
    """
    Set a single config key for a guild.
    """
    all_data = _load_all()
    guild_id = str(guild_id)

    # Ensure guild config exists
    if guild_id not in all_data:
        all_data[guild_id] = DEFAULT_CONFIG.copy()

    all_data[guild_id][key] = value

    _save_all(all_data)