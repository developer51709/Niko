"""The maintenance snapshot lists every kind of command the bot exposes.

``CommandTree.walk_commands()`` defaults to chat input commands, so the user and
message context menus used to be missing from the dashboard and could not be
paused from it. The page also needs to know which kind a row is, or it draws a
slash in front of a context menu.
"""

import sys
from pathlib import Path
from types import SimpleNamespace

import discord

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils import maintenance  # noqa: E402


class _PlayCog:
    """A cog class whose module names the extension, like the real loader."""


_PlayCog.__module__ = "cogs.fun.play"


class _FakeAppCommand:
    def __init__(self, name, module):
        self.name = name
        self.qualified_name = name
        self.binding = None
        self.callback = SimpleNamespace(__module__=module)


class _FakeTree:
    """The slice of CommandTree the snapshot uses, with its type buckets."""

    def __init__(self, buckets):
        self._buckets = buckets

    def walk_commands(self, *, type):
        return iter(self._buckets.get(type, ()))


def _bot():
    prefix = SimpleNamespace(qualified_name="play", cog=_PlayCog(), commands=[])
    return SimpleNamespace(
        commands=[prefix],
        cogs={},
        cog_status=[
            {"name": "cogs.fun.play", "label": "Play", "state": "loaded", "commands": 1},
            {"name": "cogs.utility", "label": "Utility", "state": "loaded", "commands": 0},
        ],
        tree=_FakeTree({
            discord.AppCommandType.chat_input: [
                    _FakeAppCommand("play", "cogs.fun.play"),
                    _FakeAppCommand("avatar", "cogs.utility.avatars"),
                ],
                discord.AppCommandType.user: [
                    _FakeAppCommand("Roleplay", "cogs.fun.roleplay"),
                ],
                discord.AppCommandType.message: [
                    _FakeAppCommand("Translate", "cogs.utility.translate"),
                ],
            }),
    )


def _rows():
    return {row["name"]: row for row in maintenance._command_rows(_bot())}


def test_context_menus_are_listed_and_attributed_to_their_cog():
    rows = _rows()

    assert rows["Roleplay"]["kind"] == "context"
    assert rows["Roleplay"]["cog"] == "cogs.fun"
    assert rows["Translate"]["kind"] == "context"
    assert rows["Translate"]["cog"] == "cogs.utility"
    assert rows["Translate"]["cog_label"] == "Utility"


def test_a_hybrid_command_is_listed_once_and_keeps_both_invocation_styles():
    rows = _rows()

    assert list(rows).count("play") == 1
    # Both trees register it, and the page needs to know that: calling a hybrid
    # command a slash command hides that the prefix still works.
    assert rows["play"]["kind"] == "hybrid"
    assert rows["avatar"]["kind"] == "slash"


def test_the_snapshot_carries_the_kind_and_a_paused_context_menu():
    bot = _bot()
    maintenance._cache = {"cogs": {}, "commands": {"Translate": {"reason": "localising", "since": 10, "by": "1"}}}

    snapshot = maintenance.snapshot(bot)
    rows = {row["name"]: row for row in snapshot["commands"]}

    assert rows["Translate"]["maintenance"] is True
    assert rows["Translate"]["reason"] == "localising"
    assert rows["Translate"]["kind"] == "context"
    # The gate resolves a context menu by the same name the dashboard writes.
    assert maintenance.find_block("Translate", extension="cogs.utility")[1] == "Translate"
