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
        from discord.ext import commands
        commands_data = []
        hybrid_names = set()

        def command_description(cmd):
            description = (
                getattr(cmd, "description", None)
                or getattr(cmd, "help", None)
                or getattr(getattr(cmd, "callback", None), "__doc__", None)
                or ""
            )
            if isinstance(description, dict):
                description = description.get("en") or next(iter(description.values()), "")
            return str(description).strip()

        def add_command(cmd, command_type, name, cog_name=None, context_type=None):
            commands_data.append({
                "name": name,
                "description": command_description(cmd),
                "category": CATEGORY_MAP.get(cog_name or "Utility", "utility"),
                "type": command_type,
                **({"context_type": context_type} if context_type else {}),
            })

        # Prefix and hybrid commands live on the bot rather than the app command
        # tree. Hybrid commands are emitted once with a type of "hybrid" so the
        # website can show both ways to invoke them without duplicating cards.
        for cmd in bot.walk_commands():
            cog = getattr(cmd, "binding", None)
            cog_name = getattr(cmd, "cog_name", None) or (type(cog).__name__ if cog else "Utility")
            name = getattr(cmd, "qualified_name", cmd.name)
            if isinstance(cmd, (commands.HybridCommand, commands.HybridGroup)):
                hybrid_names.add(name)
                add_command(cmd, "hybrid", name, cog_name)
            else:
                add_command(cmd, "prefix", name, cog_name)

        def process_app_command(cmd, parent_name=None):
            name = f"{parent_name} {cmd.name}" if parent_name else cmd.name
            if isinstance(cmd, app_commands.ContextMenu):
                context_type = getattr(getattr(cmd, "type", None), "name", "message")
                add_command(cmd, "context", name, type(getattr(cmd, "binding", None)).__name__ if getattr(cmd, "binding", None) else "Utility", context_type)
            elif name not in hybrid_names:
                binding = getattr(cmd, "binding", None)
                add_command(cmd, "slash", name, type(binding).__name__ if binding else "Utility")

            if isinstance(cmd, app_commands.Group):
                for sub in cmd.commands:
                    process_app_command(sub, parent_name=name)

        for cmd in bot.tree.get_commands():
            process_app_command(cmd)

        commands_data.sort(key=lambda x: (x["category"], x["type"], x["name"]))

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
