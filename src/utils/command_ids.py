"""Application-command IDs, so a message can link a slash command.

Discord only turns ``</setup:1234567890>`` into a clickable command chip when the
message carries the command's snowflake — there is no way to mention a command by
name alone. Those IDs are assigned by Discord, so the only moment the bot learns
them is the payload :meth:`discord.app_commands.CommandTree.sync` returns (or a
follow-up :meth:`CommandTree.fetch_commands`).

This module keeps the name → ID map. :func:`remember`/:func:`save` are called by
the sync path, :func:`load` reads the persisted map back on boot, and
:func:`mention` (or :func:`replace_refs` for existing copy) renders the mention,
falling back to the old inline code block when the IDs are not known yet.

Subcommands use their top-level command's ID: Discord's own
``AppCommandGroup.mention`` does the same, so ``/leveling panel`` becomes
``</leveling panel:top-level-id>``.
"""

from __future__ import annotations

import json
import re

from discord.enums import AppCommandOptionType

from utils import logging

#: Key in the ``sync_state`` key/value table that holds the JSON map.
COMMAND_IDS_KEY = "application_command_ids"

#: The global map for this process. Empty until :func:`load`/`ensure` runs.
_MENTIONS: dict[str, int] = {}

#: Matches an inline-code command reference, e.g. ``/leveling panel``. Only
#: lowercase names, digits, spaces and hyphens are command names in this bot.
_REFERENCE = re.compile(r"`/([a-z0-9][a-z0-9 -]*)`")

_GROUP_TYPES = (
    AppCommandOptionType.subcommand,
    AppCommandOptionType.subcommand_group,
)


def _command_type(command):
    value = getattr(command, "type", None)
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def collect(commands) -> dict[str, int]:
    """Flatten a sync/fetch payload into ``{"name [sub]": top_level_id}``.

    Only chat-input commands can be mentioned; user and message context-menu
    commands are skipped because Discord has no mention format for them.
    """
    mapping: dict[str, int] = {}

    def walk(command, prefix: tuple[str, ...], top_id: int | None) -> None:
        if top_id is None:
            command_id = getattr(command, "id", None)
            if command_id is None:
                return
            # 1 is CHAT_INPUT; context menus (2/3) have no command mention.
            if _command_type(command) not in (None, 1):
                return
            top_id = int(command_id)
        mapping[" ".join((*prefix, command.name))] = top_id
        for option in getattr(command, "options", None) or ():
            if getattr(option, "type", None) in _GROUP_TYPES:
                walk(option, (*prefix, command.name), top_id)

    for command in commands or ():
        walk(command, (), None)
    return mapping


def known() -> dict[str, int]:
    """A copy of the map, for callers that need to inspect or test it."""
    return dict(_MENTIONS)


def remember(mapping: dict[str, int]) -> None:
    """Install a name → ID map for this process (used on load and by tests)."""
    _MENTIONS.clear()
    _MENTIONS.update({
        " ".join(str(name).split()): int(command_id)
        for name, command_id in (mapping or {}).items()
    })


def mention(name: str) -> str:
    """Render ``</name:id>``, or the old inline code block when unknown."""
    name = " ".join(str(name).split())
    command_id = _MENTIONS.get(name)
    if command_id:
        return f"</{name}:{command_id}>"
    return f"`/{name}`"


def replace_refs(text: str) -> str:
    """Turn every inline-code command reference in *text* into a mention.

    Localised copy still writes ``/automod`` because a translator should see the
    command name, not a snowflake; this turns those into links at render time
    and leaves anything unfamiliar exactly as written.
    """
    if not text or "`/" not in text:
        return text
    return _REFERENCE.sub(lambda match: mention(match.group(1)), text)


async def save(bot, commands) -> dict[str, int]:
    """Remember the IDs Discord returned and persist the global map."""
    mapping = collect(commands)
    if not mapping:
        return {}
    remember(mapping)

    if getattr(bot, "cxn", None) is None:
        return mapping
    try:
        value = json.dumps(mapping, sort_keys=True)
        await bot.cxn.execute(
            "INSERT INTO sync_state (key, value) VALUES ($1, $2) "
            "ON CONFLICT (key) DO UPDATE SET value = $3",
            COMMAND_IDS_KEY, value, value,
        )
    except Exception as exc:  # noqa: BLE001 - mentions are a nicety, never fatal
        logging.warning("CommandIDs", f"Could not store application command IDs: {exc}")
    return mapping


async def load(bot) -> dict[str, int]:
    """Read the persisted map back into this process."""
    if getattr(bot, "cxn", None) is None:
        return known()
    try:
        raw = await bot.cxn.fetchval(
            "SELECT value FROM sync_state WHERE key = $1", COMMAND_IDS_KEY
        )
        if raw:
            stored = json.loads(raw)
            if isinstance(stored, dict) and stored:
                remember(stored)
    except Exception as exc:  # noqa: BLE001
        logging.warning("CommandIDs", f"Could not read application command IDs: {exc}")
    return known()


async def ensure(bot) -> dict[str, int]:
    """Load the stored map, fetching it once if this deployment never saved one.

    A deployment that skips the slash sync (the fingerprint matched) still needs
    the IDs, and fetching them is a read — it does not spend the 200-per-day
    global overwrite budget a sync does.
    """
    mapping = await load(bot)
    if mapping:
        return mapping
    try:
        fetched = await bot.tree.fetch_commands()
    except Exception as exc:  # noqa: BLE001
        logging.warning("CommandIDs", f"Could not fetch application command IDs: {exc}")
        return {}
    logging.info("CommandIDs", f"Fetched {len(fetched or ())} application command(s) from Discord.")
    return await save(bot, fetched)
