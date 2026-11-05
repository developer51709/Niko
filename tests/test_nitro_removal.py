"""The old ``system/nitro.py`` cog is gone; its two useful menus moved home.

Everything else the file offered (``/vcstatus``, ``/forward``, ``/sticker``,
``/stage speak``) was a Nitro-era gimmick, so it was dropped. These checks pin
the two survivors to the cogs that own their subject matter and make sure the
old module stays deleted.
"""

from __future__ import annotations

import asyncio
import inspect
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.ai import chat  # noqa: E402
from cogs.economy.cog import EconomyCog  # noqa: E402
from utils import discord_extras  # noqa: E402
from utils.command_locales import CommandTexts  # noqa: E402


class _Tree:
    def __init__(self):
        self.added = []
        self.removed = []

    def add_command(self, command, *args, **kwargs):
        self.added.append(command)

    def remove_command(self, name, *, type=None):
        self.removed.append(name)


def test_the_nitro_module_is_deleted_and_no_longer_loaded():
    assert not (ROOT / "src" / "cogs" / "system" / "nitro.py").exists()

    import cogs.system as system

    assert not hasattr(system, "nitro")


def test_the_nitro_only_helpers_are_gone_but_voice_status_stays():
    # set_voice_status is still used by the music cog.
    assert inspect.iscoroutinefunction(discord_extras.set_voice_status)
    assert not hasattr(discord_extras, "forward_message")
    assert not hasattr(discord_extras, "stage_become_speaker")


def test_ask_niko_registers_on_the_ai_cog_and_unloads_cleanly():
    bot = SimpleNamespace(tree=_Tree())
    cog = chat.AICog(bot)

    assert [command.name for command in bot.tree.added] == ["☕ Ask Niko"]
    asyncio.run(cog.cog_unload())
    assert bot.tree.removed == ["☕ Ask Niko"]


def test_ask_niko_uses_the_ai_catalogue_in_every_language():
    texts = CommandTexts("cogs.ai").language_map("☕ Ask Niko.name")

    assert texts["en"] == "☕ Ask Niko"
    for language in ("de", "es", "fr"):
        assert texts.get(language), f"missing {language} name for Ask Niko"


def test_the_profile_menu_registers_on_the_economy_cog_and_unloads_cleanly():
    async def build_and_unload():
        bot = SimpleNamespace(tree=_Tree())
        # The economy cog starts its tick loop in __init__, so it needs a loop.
        cog = EconomyCog(bot)

        assert [command.name for command in bot.tree.added] == ["📊 User Profile"]
        assert inspect.iscoroutinefunction(cog.user_profile_context)

        cog.cog_unload()
        assert bot.tree.removed == ["📊 User Profile"]

    asyncio.run(build_and_unload())


def test_the_profile_card_text_lives_with_the_economy_catalogue():
    from utils.locales import load_locales

    currency = load_locales("cogs.economy", "currency")
    for key in ("profile_level", "profile_xp", "profile_wallet", "profile_bank",
                "profile_joined", "profile_account", "profile_unknown"):
        assert currency["en"].get(key), f"missing economy key {key}"

    texts = CommandTexts("cogs.economy").language_map("📊 User Profile.name")
    for language in ("en", "de", "es", "fr"):
        assert texts.get(language), f"missing {language} name for User Profile"
