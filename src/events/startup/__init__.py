"""
Startup module — centralizes all on_ready event handlers.
Modular functions for database, cogs, status, syncing, and data export.
"""

from .database import init_database
from .loader import load_cogs
from .status import set_status
from .banner import print_banner
from .sync import run_slash_sync, run_emoji_sync
from .writers import write_bot_stats, write_commands

__all__ = [
    "init_database",
    "load_cogs",
    "set_status",
    "print_banner",
    "run_slash_sync",
    "run_emoji_sync",
    "write_bot_stats",
    "write_commands",
]
