"""The bot's command registry the way the website shows it."""

import json
from . import runtime


_INTERNAL_COMMAND_COGS = {"owner", "ownercog", "development", "staff", "staffcog"}

# Older command registries predate the ``cog`` and ``module`` fields. Keep the
# current private command names here so those records cannot leak while the
# bot has not yet rewritten data/commands.json.
_LEGACY_INTERNAL_COMMAND_NAMES = {
    "ownerhelp", "setpfp", "setbanner", "setusername", "setstatus", "setactivity",
    "load", "unload", "reload", "restart", "shutdown", "sync", "eval", "servers",
    "serverinvite", "announce", "dev01", "shardinfo", "shardstats", "shardhealth",
    "blacklist", "blacklist info", "blacklist reason", "blacklist add", "blacklist remove",
    "premium", "premium add", "premium remove", "premium list",
    "devhelp", "devload", "devunload", "devreload", "devping", "devlatency",
    "devuptime", "devmem", "devtasks", "devguild", "devchannels", "devroles",
    "devmembers", "deveval", "devexec", "devsay", "devshutdown", "syncemojis",
    "replaceemojis", "appemojis", "emojistatus", "staff", "staff help", "staff manage",
}


def _is_internal_command(*values) -> bool:
    """Identify commands owned by private owner/development cogs."""
    for value in values:
        if not value:
            continue
        parts = str(value).lower()
        for separator in (".", "/", "\\", ":", "-"):
            parts = parts.replace(separator, " ")
        if any(part.strip() in _INTERNAL_COMMAND_COGS for part in parts.split()):
            return True
    return False


def _live_internal_command_names() -> set[str]:
    """Collect private command names for filtering older registry files."""
    if runtime._discord_bot is None:
        return set()

    names: set[str] = set()

    def add_if_internal(command, qualified_name: str | None = None) -> None:
        binding = getattr(command, "binding", None) or getattr(command, "cog", None)
        callback = getattr(command, "callback", None)
        cog_name = getattr(command, "cog_name", None)
        if _is_internal_command(
            cog_name,
            type(binding).__name__ if binding is not None else None,
            getattr(callback, "__module__", None),
        ):
            command_name = qualified_name or getattr(command, "qualified_name", None) or getattr(command, "name", None)
            if command_name:
                names.add(str(command_name))
                names.add(str(getattr(command, "name", command_name)))

    try:
        for command in runtime._discord_bot.walk_commands():
            add_if_internal(command)
    except Exception:
        pass

    def visit_application_command(command, parent_name: str | None = None) -> None:
        command_name = getattr(command, "name", None)
        if not command_name:
            return
        qualified_name = f"{parent_name} {command_name}" if parent_name else str(command_name)
        add_if_internal(command, qualified_name)
        for child in getattr(command, "commands", []) or []:
            visit_application_command(child, qualified_name)

    try:
        tree = getattr(runtime._discord_bot, "tree", None)
        for command in tree.get_commands() if tree is not None else []:
            visit_application_command(command)
    except Exception:
        pass

    return names


def _description_value(value):
    """Normalise a command help value into a locale map or plain text.

    Command records can store help as a real dict, or as a serialised map
    written in Python literal syntax, e.g.
    "{ 'en': 'Reset XP.', 'de': 'XP zurücksetzen.' }". In both cases we
    return a real ``{locale: text}`` object so the website can pick the
    visitor's language. Anything else passes through untouched.
    """
    if isinstance(value, dict):
        cleaned = {str(k): str(v) for k, v in value.items() if k and v}
        return cleaned if cleaned else ""
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("{"):
            try:
                parsed = json.loads(text.replace("'", '"'))
            except Exception:
                parsed = None
            if isinstance(parsed, dict):
                cleaned = {str(k): str(v) for k, v in parsed.items() if k and v}
                if cleaned:
                    return cleaned
        return value
    return str(value) if value else ""
