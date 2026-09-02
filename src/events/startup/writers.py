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

        permission_names = (
            "administrator", "manage_guild", "manage_channels", "manage_roles",
            "manage_messages", "moderate_members", "kick_members", "ban_members",
            "mention_everyone", "manage_webhooks", "manage_nicknames",
        )

        def text_value(value):
            return str(value).strip() if value is not None else ""

        def parameter_metadata(parameter):
            name = getattr(parameter, "display_name", None) or getattr(parameter, "name", None)
            if not name:
                return None
            annotation = getattr(parameter, "annotation", None)
            type_name = getattr(getattr(parameter, "type", None), "name", None)
            if not type_name and annotation is not None:
                type_name = getattr(annotation, "__name__", None) or text_value(annotation)
            return {
                "name": text_value(name),
                "description": text_value(getattr(parameter, "description", None)),
                "required": bool(getattr(parameter, "required", False)),
                "type": type_name or "string",
            }

        def command_parameters(cmd):
            params = getattr(cmd, "parameters", None)
            if params is None:
                params = getattr(cmd, "clean_params", {}).values()
            return [item for item in (parameter_metadata(param) for param in params) if item]

        def command_permissions(cmd):
            permissions = getattr(cmd, "default_permissions", None)
            if permissions is None:
                return []
            return [name.replace("_", " ").title() for name in permission_names if bool(getattr(permissions, name, False))]

        def command_aliases(cmd):
            aliases = getattr(cmd, "aliases", None)
            return [text_value(alias) for alias in (aliases or []) if text_value(alias)]

        def command_usage(cmd, command_type, name, parameters):
            if command_type == "context":
                return name
            prefix = "/" if command_type in {"slash", "hybrid"} else "."
            usage = f"{prefix}{name}"
            for parameter in parameters:
                marker = f"<{parameter['name']}>" if parameter["required"] else f"[{parameter['name']}]"
                usage += f" {marker}"
            return usage

        def add_command(cmd, command_type, name, cog_name=None, context_type=None, subcommands=None):
            parameters = command_parameters(cmd)
            commands_data.append({
                "name": name,
                "description": command_description(cmd),
                "category": CATEGORY_MAP.get(cog_name or "Utility", "utility"),
                "type": command_type,
                "aliases": command_aliases(cmd),
                "parameters": parameters,
                "permissions": command_permissions(cmd),
                "usage": command_usage(cmd, command_type, name, parameters),
                "subcommands": list(subcommands or []),
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
                child_names = [getattr(sub, "name", "") for sub in cmd.commands if getattr(sub, "name", "")]
                # Update the group record after recursion so its expandable
                # detail view can list the same children Discord exposes.
                for record in reversed(commands_data):
                    if record["name"] == name and record["type"] == "slash":
                        record["subcommands"] = child_names
                        break
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
