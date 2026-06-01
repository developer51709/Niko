"""
Startup — data-file writers.
Writes bot_stats.json and commands.json after cogs are loaded.
"""

import os
import json
import datetime

from utils import logging


def write_bot_stats(bot):
    try:
        os.makedirs("data", exist_ok=True)
        user_count = sum(g.member_count or 0 for g in bot.guilds)
        payload = {
            "guild_count":   len(bot.guilds),
            "guild_ids":     [g.id for g in bot.guilds],
            "user_count":    user_count,
            "command_count": 76,
            "version":       "1.0",
            "uptime_since":  datetime.datetime.utcnow().isoformat(),
        }
        with open("data/bot_stats.json", "w") as f:
            json.dump(payload, f)
    except Exception as exc:
        logging.error("Startup", f"Could not write bot_stats.json: {exc}")


def write_commands(bot):
    CATEGORY_MAP = {
        "Economy":     "economy",
        "Casino":      "fun",
        "Music":       "music",
        "Leveling":    "leveling",
        "Moderation":  "moderation",
        "Automod":     "moderation",
        "Admin":       "moderation",
        "Logging":     "moderation",
        "AI":          "ai",
        "Fun":         "fun",
        "Roleplay":    "fun",
        "Utility":     "utility",
        "Info":        "utility",
        "Help":        "utility",
        "System":      "utility",
        "Voicemaster": "utility",
        "Notifier":    "utility",
        "Reminders":   "utility",
        "Tags":        "utility",
        "Giveaway":    "community",
        "Tickets":     "community",
        "Onboarding":  "community",
        "Social":      "community",
        "Polls":       "community",
        "Suggestions": "community",
        "Starboard":   "community",
        "Birthdays":   "community",
        "Highlights":  "community",
    }

    try:
        from discord import app_commands
        commands_data = []

        def process_cmd(cmd, parent_name=None):
            cog = getattr(cmd, "binding", None)
            cog_name = type(cog).__name__ if cog else "Utility"
            category = CATEGORY_MAP.get(cog_name, "utility")
            name = f"{parent_name} {cmd.name}" if parent_name else cmd.name
            commands_data.append({
                "name":        name,
                "description": getattr(cmd, "description", "") or "",
                "category":    category,
            })
            if isinstance(cmd, app_commands.Group):
                for sub in cmd.commands:
                    process_cmd(sub, parent_name=cmd.name)

        for cmd in bot.tree.get_commands():
            process_cmd(cmd)

        commands_data.sort(key=lambda x: (x["category"], x["name"]))

        os.makedirs("data", exist_ok=True)
        with open("data/commands.json", "w") as f:
            json.dump(commands_data, f)

        try:
            stats_path = "data/bot_stats.json"
            if os.path.exists(stats_path):
                with open(stats_path) as f:
                    stats = json.load(f)
                stats["command_count"] = len(commands_data)
                with open(stats_path, "w") as f:
                    json.dump(stats, f)
        except Exception:
            pass

        logging.success("Startup", f"Exported {len(commands_data)} command(s) to data/commands.json")
    except Exception as exc:
        logging.error("Startup", f"Could not write commands.json: {exc}")
