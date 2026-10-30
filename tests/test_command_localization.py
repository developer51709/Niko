"""Discord receives the catalogue's German and Spanish command wording.

Discord only localizes application commands when the payload sent on sync has
``name_localizations`` / ``description_localizations``. These checks build real
discord.py objects and read the payload the bot would upload.
"""

from __future__ import annotations

import sys
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _bot() -> commands.Bot:
    return commands.Bot(command_prefix="!", intents=discord.Intents.none())


def test_slash_group_options_are_localized():
    from utils.command_localization import apply_command_localizations

    from cogs.utility.sticky import StickyCog

    bot = _bot()
    # Hybrid commands keep their slash counterpart on ``app_command``.
    group = StickyCog.sticky.app_command
    bot.tree.add_command(group)
    apply_command_localizations(bot.tree)

    payload = group.to_dict(bot.tree)
    assert payload["description_localizations"]["de"]
    assert payload["description_localizations"]["es-ES"]
    assert payload["description_localizations"]["es-419"]

    subcommand = payload["options"][0]
    assert subcommand["description_localizations"]["de"]

    option = subcommand["options"][0]
    assert option["description_localizations"]["de"]
    assert option["description_localizations"]["es-ES"]


def test_context_menu_names_are_localized():
    from utils.command_localization import apply_command_localizations

    async def callback(interaction: discord.Interaction, message: discord.Message) -> None:
        raise NotImplementedError

    callback.__module__ = "cogs.utility.translate"
    menu = app_commands.ContextMenu(
        name="Translate", callback=callback, type=discord.AppCommandType.message
    )

    bot = _bot()
    bot.tree.add_command(menu)
    apply_command_localizations(bot.tree)

    payload = menu.to_dict(bot.tree)
    assert payload["name_localizations"]["de"] == "Übersetzen"
    assert payload["name_localizations"]["es-ES"] == "Traducir"
    # Discord has no description field for context menus.
    assert "description_localizations" not in payload


def test_commands_without_a_catalogue_are_left_alone():
    from utils.command_localization import apply_command_localizations

    async def callback(interaction: discord.Interaction) -> None:
        raise NotImplementedError

    callback.__module__ = "not_a_cog_module"
    command = app_commands.Command(
        name="lonely", description="No catalogue here", callback=callback
    )

    bot = _bot()
    bot.tree.add_command(command)
    assert apply_command_localizations(bot.tree) == 0
    # discord.py keeps its own payload builder, so nothing was replaced.
    assert command.to_dict(bot.tree)["name"] == "lonely"
    assert "name_localizations" not in command.to_dict(bot.tree)


def test_localizations_are_applied_only_once():
    from utils.command_localization import apply_command_localizations

    async def callback(interaction: discord.Interaction) -> None:
        raise NotImplementedError

    callback.__module__ = "cogs.utility.sticky"
    command = app_commands.Command(name="ping", description="Check latency", callback=callback)

    bot = _bot()
    bot.tree.add_command(command)
    assert apply_command_localizations(bot.tree) == 1
    assert apply_command_localizations(bot.tree) == 0
    assert command.to_dict(bot.tree)["description_localizations"]["de"]
