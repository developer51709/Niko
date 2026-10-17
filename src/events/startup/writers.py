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
        command_count = getattr(bot, "_status_command_count", None)
        if command_count is None:
            try:
                command_count = len(list(bot.walk_commands())) + len(bot.tree.get_commands())
            except Exception:
                command_count = 76
        payload = {
            "guild_count":   len(bot.guilds),
            "guild_ids":     [g.id for g in bot.guilds],
            "user_count":    user_count,
            "command_count": command_count,
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
        from discord import Permissions, app_commands
        from discord.ext import commands
        commands_data = []
        hybrid_names = set()
        internal_cog_names = {"owner", "ownercog", "development", "staff", "staffcog"}

        def is_internal_cog(*values):
            """Keep owner/development-only commands out of public command data."""
            for value in values:
                if not value:
                    continue
                parts = str(value).lower()
                for separator in (".", "/", "\\\\", ":", "-"):
                    parts = parts.replace(separator, " ")
                if any(part.strip() in internal_cog_names for part in parts.split()):
                    return True
            return False

        def command_description(cmd):
            description = (
                getattr(cmd, "description", None)
                or getattr(cmd, "help", None)
                or getattr(getattr(cmd, "callback", None), "__doc__", None)
                or ""
            )
            if isinstance(description, dict):
                description = description.get("en") or next(iter(description.values()), "")
            return str(description or "").strip()

        permission_names = set(Permissions.VALID_FLAGS)

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
            required = set()
            default_permissions = getattr(cmd, "default_permissions", None)
            if default_permissions is not None:
                required.update(
                    name for name in permission_names
                    if bool(getattr(default_permissions, name, False))
                )

            # discord.py stores has_permissions/bot_has_permissions decorators
            # as predicate closures on command checks. Inspect the captured
            # permission mappings for both prefix and application commands.
            pending = list(getattr(cmd, "checks", ()) or ())
            visited = set()
            while pending:
                value = pending.pop()
                if id(value) in visited:
                    continue
                visited.add(id(value))
                if isinstance(value, dict):
                    required.update(
                        name for name, enabled in value.items()
                        if name in permission_names and bool(enabled)
                    )
                    pending.extend(value.values())
                elif isinstance(value, (tuple, list, set)):
                    pending.extend(value)
                elif callable(value):
                    for cell in getattr(value, "__closure__", ()) or ():
                        try:
                            pending.append(cell.cell_contents)
                        except ValueError:
                            continue
                    pending.extend((getattr(value, "__defaults__", None) or ()))
                    pending.extend((getattr(value, "__kwdefaults__", None) or {}).values())

            return [name.replace("_", " ").title() for name in sorted(required)]

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
            # Hidden commands are operator tooling (for example .dmpurge, which
            # only runs in DMs). They must never reach data/commands.json, which
            # is what the public commands page and the command counts read.
            if getattr(cmd, "hidden", False):
                return
            parameters = command_parameters(cmd)
            callback = getattr(cmd, "callback", None)
            commands_data.append({
                "name": name,
                "description": command_description(cmd),
                "category": CATEGORY_MAP.get(cog_name or "Utility", "utility"),
                "type": command_type,
                "cog": text_value(cog_name),
                "module": text_value(getattr(callback, "__module__", None)),
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
            if is_internal_cog(cog_name, getattr(getattr(cmd, "callback", None), "__module__", None)):
                continue
            if isinstance(cmd, (commands.HybridCommand, commands.HybridGroup)):
                hybrid_names.add(name)
                add_command(cmd, "hybrid", name, cog_name)
            else:
                add_command(cmd, "prefix", name, cog_name)

        def process_app_command(cmd, parent_name=None):
            name = f"{parent_name} {cmd.name}" if parent_name else cmd.name
            binding = getattr(cmd, "binding", None)
            cog_name = type(binding).__name__ if binding else "Utility"
            callback = getattr(cmd, "callback", None)
            if is_internal_cog(cog_name, getattr(callback, "__module__", None)):
                return
            if isinstance(cmd, app_commands.ContextMenu):
                context_type = getattr(getattr(cmd, "type", None), "name", "message")
                add_command(cmd, "context", name, cog_name, context_type)
            elif name not in hybrid_names:
                add_command(cmd, "slash", name, cog_name)

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

        internal_command_names = set()

        def collect_internal_command_names(command, qualified_name=None):
            binding = getattr(command, "binding", None) or getattr(command, "cog", None)
            callback = getattr(command, "callback", None)
            cog_name = getattr(command, "cog_name", None)
            if is_internal_cog(
                cog_name,
                type(binding).__name__ if binding is not None else None,
                getattr(callback, "__module__", None),
            ):
                name = qualified_name or getattr(command, "qualified_name", None) or getattr(command, "name", None)
                if name:
                    internal_command_names.add(str(name))
                    internal_command_names.add(str(getattr(command, "name", name)))

        try:
            for command in bot.walk_commands():
                collect_internal_command_names(command)
        except Exception:
            pass

        def collect_internal_app_names(command, parent_name=None):
            name = getattr(command, "name", None)
            if not name:
                return
            qualified_name = f"{parent_name} {name}" if parent_name else str(name)
            collect_internal_command_names(command, qualified_name)
            for child in getattr(command, "commands", []) or []:
                collect_internal_app_names(child, qualified_name)

        try:
            for command in bot.tree.get_commands():
                collect_internal_app_names(command)
        except Exception:
            pass

        legacy_internal_names = {
            "ownerhelp", "setpfp", "setbanner", "setusername", "setstatus", "setactivity",
            "load", "unload", "reload", "restart", "shutdown", "sync", "eval", "servers",
            "serverinvite", "announce", "dev01", "shardinfo", "shardstats", "shardhealth",
            "blacklist", "blacklist info", "blacklist reason", "blacklist add", "blacklist remove",
            "premium", "premium add", "premium remove", "premium list",
            "devhelp", "devload", "devunload", "devreload", "devping", "devlatency",
            "devuptime", "devmem", "devtasks", "devguild", "devchannels", "devroles",
            "devmembers", "deveval", "devexec", "devsay", "devshutdown", "syncemojis",
            "appemojis", "emojistatus", "staff", "staff help", "staff manage",
        }
        public_command_count = sum(
            1 for command in commands_data
            if command.get("name")
            and command.get("name") not in internal_command_names
            and str(command["name"]).lower() not in legacy_internal_names
        )
        bot._status_command_count = public_command_count

        os.makedirs("data", exist_ok=True)
        with open("data/commands.json", "w") as f:
            json.dump(commands_data, f)

        try:
            stats_path = "data/bot_stats.json"
            if os.path.exists(stats_path):
                with open(stats_path) as f:
                    stats = json.load(f)
                stats["command_count"] = public_command_count
                with open(stats_path, "w") as f:
                    json.dump(stats, f)
        except Exception:
            pass

        logging.success("Startup", f"Exported {len(commands_data)} command(s) to data/commands.json")
    except Exception as exc:
        logging.error("Startup", f"Could not write commands.json: {exc}")
