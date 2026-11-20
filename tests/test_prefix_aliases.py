"""Short prefix aliases: ``.deposit`` stands in for ``/bank deposit``.

The bank group exists only to keep the slash tree inside Discord's 100-command
budget, so the prefix side gets a top-level shortcut. These checks pin what a
shortcut has to preserve: the same callback and parameters as the grouped
command, no new slash command, one public commands-page card with the short name
listed as an alias, no entry in the help's category lists, and a working
``.help deposit`` that shows the grouped command's wording.
"""

import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import discord
from discord.ext import commands

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.economy.commands.bank import BankMixin  # noqa: E402
from cogs.help.cog import HelpCog  # noqa: E402
from utils.command_locales import command_path, description_map  # noqa: E402
from utils.prefix_alias import (  # noqa: E402
    alias_of,
    hidden_from_lists,
    is_prefix_alias,
)

SHORTCUTS = (("deposit", "bank deposit"), ("withdraw", "bank withdraw"))


class BankHarness(BankMixin, commands.Cog):
    """The bank commands on their own, without the rest of the economy cog."""


def _bot() -> commands.Bot:
    bot = commands.Bot(command_prefix=".", intents=discord.Intents.none())
    # The built-in help command would collide with the HelpCog loaded below.
    bot.help_command = None
    asyncio.run(bot.add_cog(BankHarness(bot)))
    return bot


def _texts(view) -> str:
    """Every visible line of a Components v2 layout view."""
    out = []

    def walk(item):
        content = getattr(item, "content", None)
        if isinstance(content, str):
            out.append(content)
        for child in getattr(item, "children", None) or ():
            walk(child)

    walk(view)
    return "\n".join(out)


def test_the_short_names_run_the_grouped_commands():
    bot = _bot()

    for short, grouped in SHORTCUTS:
        alias = bot.get_command(short)
        target = bot.get_command(grouped)
        assert alias is not None, f".{short} is not registered"
        assert target is not None, f"/{grouped} is not registered"
        # One implementation, so the two invocations cannot drift apart.
        assert alias.callback is target.callback
        assert list(alias.clean_params) == ["amount"] == list(target.clean_params)
        assert alias.hidden is True
        assert alias_of(alias) == grouped
        assert is_prefix_alias(alias)


def test_the_slash_tree_does_not_grow():
    bot = _bot()

    assert [command.name for command in bot.tree.get_commands()] == ["bank"]
    assert sorted(command.qualified_name for command in bot.tree.walk_commands()) == [
        "bank",
        "bank deposit",
        "bank upgrade",
        "bank withdraw",
    ]


def test_the_shortcut_borrows_the_grouped_wording():
    bot = _bot()
    alias = bot.get_command("deposit")
    target = bot.get_command("bank deposit")

    assert command_path(alias) == "bank.deposit"
    # The locale lookup follows the grouped command, so .help deposit reads the
    # same catalogue text instead of an empty description of its own.
    assert description_map(alias) == description_map(target)
    assert description_map(alias).get("en")


def test_the_commands_page_keeps_one_card_and_lists_the_shortcut(tmp_path, monkeypatch):
    bot = _bot()
    monkeypatch.chdir(tmp_path)

    from events.startup.writers import write_commands

    write_commands(bot)
    rows = json.loads((tmp_path / "data" / "commands.json").read_text(encoding="utf-8"))
    names = [row["name"] for row in rows]

    # No extra prefix-only cards for the shortcuts.
    assert "deposit" not in names
    assert "withdraw" not in names

    grouped = next(row for row in rows if row["name"] == "bank deposit")
    assert grouped["type"] == "hybrid"
    assert "deposit" in grouped["aliases"]

    withdraw = next(row for row in rows if row["name"] == "bank withdraw")
    assert "withdraw" in withdraw["aliases"]


def test_help_hides_the_shortcut_from_lists_but_still_answers_for_it():
    bot = _bot()
    alias = bot.get_command("deposit")

    # Hidden, so the help's category lists skip it …
    assert alias.hidden is True
    # … but a shortcut is still a name members can type, so .help finds it.
    assert hidden_from_lists(alias) is False
    assert hidden_from_lists(bot.get_command("bank deposit")) is False

    async def secret(ctx):
        return None

    assert hidden_from_lists(commands.Command(secret, name="secret", hidden=True)) is True


def test_help_deposit_renders_the_grouped_description():
    bot = _bot()
    asyncio.run(bot.add_cog(HelpCog(bot)))
    help_cog = bot.get_cog("HelpCog")

    class Ctx:
        guild = SimpleNamespace(id=1, preferred_locale="en")
        author = SimpleNamespace(id=2)
        interaction = None

        async def send(self, *, view=None, **kwargs):
            self.view = view
            return SimpleNamespace(id=3)

    ctx = Ctx()
    asyncio.run(HelpCog.help.callback(help_cog, ctx, command_name="deposit"))
    rendered = _texts(ctx.view)

    expected = description_map(bot.get_command("bank deposit")).get("en")
    assert expected
    assert expected in rendered
    assert "deposit" in rendered


def test_leveling_rank_has_a_short_prefix_alias():
    from cogs.leveling.cog import Leveling

    alias = Leveling.rank
    target = Leveling.leveling_rank

    assert alias.name == "rank"
    assert alias.hidden is True
    assert alias.callback is target.callback
    assert alias_of(alias) == "leveling rank"
    assert list(alias.clean_params) == list(target.clean_params) == ["member"]
    # .help rank reads the grouped command's wording, in every language.
    assert command_path(alias) == "leveling.rank"
    assert description_map(alias) == description_map(target)
    assert description_map(alias).get("en")


def test_command_totals_do_not_count_the_shortcuts():
    bot = _bot()

    from webapp.status import _live_command_count

    before = _live_command_count(bot)
    for name in ("deposit", "withdraw"):
        assert bot.get_command(name) is not None
        bot.remove_command(name)

    # The status page's live total has to match the commands page, which counts
    # the grouped commands once and never the shortcuts: dropping the shortcuts
    # must leave the total unchanged because they were never in it.
    assert _live_command_count(bot) == before


def test_maintenance_pauses_the_shortcut_with_its_target():
    bot = _bot()

    from utils.maintenance import _command_rows, _maintenance_target

    target = bot.get_command("bank deposit")
    assert _maintenance_target(bot, bot.get_command("deposit")) is target

    # The dashboard lists the grouped command once, with no separate row for the
    # shortcut (a row whose toggle could never block anything on its own).
    rows = _command_rows(bot)
    names = [row["name"] for row in rows]
    assert "deposit" not in names
    assert "withdraw" not in names
    assert next(row for row in rows if row["name"] == "bank deposit")["kind"] == "hybrid"
