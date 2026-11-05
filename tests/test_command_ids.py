"""Application-command IDs and the mentions built from them.

Discord only renders ``</setup:123>`` when the message carries the command's
snowflake, so the sync path has to remember the IDs it receives. These checks
cover the flattening (subcommands share their top-level ID), the persistence
round-trip, the fallback, and that the setup wizard renders mentions instead of
inline code in every language.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from discord.enums import AppCommandOptionType  # noqa: E402

from utils import command_ids  # noqa: E402


def _command(name, command_id, *, type=1, options=()):
    return SimpleNamespace(
        name=name, id=command_id, type=type, options=list(options),
        to_dict=lambda _tree=None: {"name": name, "type": type, "options": []},
    )


def _group(name, *, type=AppCommandOptionType.subcommand, options=()):
    return SimpleNamespace(name=name, id=None, type=type, options=list(options))


class _Cxn:
    def __init__(self, stored: str | None = None):
        self.stored = stored
        self.executed = []

    async def fetchval(self, _query, _key):
        return self.stored

    async def execute(self, _query, *args):
        self.executed.append(args)
        if len(args) >= 2:
            self.stored = args[1]

    def keys(self):
        return [args[0] for args in self.executed]


def test_collect_flattens_subcommands_onto_the_top_level_id():
    tree = [
        _command("leveling", 100, options=[
            _group("panel"),
            _group("rewards", type=AppCommandOptionType.subcommand_group, options=[
                _group("role"),
            ]),
        ]),
        _command("verify", 200, type=2),  # user context menu: not mentionable
    ]

    mapping = command_ids.collect(tree)

    assert mapping == {
        "leveling": 100,
        "leveling panel": 100,
        "leveling rewards": 100,
        "leveling rewards role": 100,
    }


def test_mention_falls_back_to_inline_code_when_the_id_is_unknown():
    command_ids.remember({"setup": 42})

    assert command_ids.mention("setup") == "</setup:42>"
    assert command_ids.mention("  setup  ") == "</setup:42>"
    assert command_ids.mention("automod") == "`/automod`"


def test_replace_refs_only_rewrites_known_command_references():
    command_ids.remember({"automod": 7, "leveling panel": 8})

    text = (
        "Use `/automod` now and `/leveling panel` later. "
        "`/not-a-command` and `code` stay as they are."
    )

    assert command_ids.replace_refs(text) == (
        "Use </automod:7> now and </leveling panel:8> later. "
        "`/not-a-command` and `code` stay as they are."
    )


def test_the_map_survives_a_restart_through_the_sync_state_table():
    tree = [_command("setup", 42), _command("automod", 43)]
    cxn = _Cxn()

    saved = asyncio.run(command_ids.save(SimpleNamespace(cxn=cxn), tree))
    assert saved == {"setup": 42, "automod": 43}
    assert command_ids.COMMAND_IDS_KEY in cxn.keys()
    assert json.loads(cxn.stored) == saved

    command_ids.remember({})
    loaded = asyncio.run(command_ids.load(SimpleNamespace(cxn=cxn)))
    assert loaded == {"setup": 42, "automod": 43}
    assert command_ids.mention("automod") == "</automod:43>"


def test_ensure_fetches_once_when_nothing_was_ever_stored():
    tree = [_command("setup", 42)]
    cxn = _Cxn()
    bot = SimpleNamespace(
        cxn=cxn,
        tree=SimpleNamespace(fetch_commands=lambda: _async(tree)),
    )
    command_ids.remember({})

    mapping = asyncio.run(command_ids.ensure(bot))

    assert mapping == {"setup": 42}
    assert json.loads(cxn.stored) == {"setup": 42}


def test_ensure_uses_the_stored_map_without_calling_discord():
    called = []

    async def fetch():
        called.append(True)
        return []

    cxn = _Cxn(stored=json.dumps({"setup": 42}))
    bot = SimpleNamespace(cxn=cxn, tree=SimpleNamespace(fetch_commands=fetch))
    command_ids.remember({})

    assert asyncio.run(command_ids.ensure(bot)) == {"setup": 42}
    assert called == []


def _async(value):
    async def return_value():
        return value
    return return_value()


def test_startup_sync_stores_the_ids_discord_returns():
    import events.startup.sync as startup_sync

    command = _command("setup", 42)

    class _Tree:
        def get_commands(self):
            return [command]

        async def fetch_commands(self):
            return [command]

        async def sync(self):
            return [command]

    cxn = _Cxn()
    bot = SimpleNamespace(tree=_Tree(), cxn=cxn)
    original = startup_sync.apply_command_localizations
    startup_sync.apply_command_localizations = lambda _tree: None
    try:
        asyncio.run(startup_sync.run_slash_sync(bot))
    finally:
        startup_sync.apply_command_localizations = original

    stored = {args[0]: args[1] for args in cxn.executed}
    assert json.loads(stored[command_ids.COMMAND_IDS_KEY]) == {"setup": 42}
    assert command_ids.mention("setup") == "</setup:42>"


def test_the_setup_wizard_renders_mentions_in_every_language():
    from cogs.setup import cog as setup_cog

    class _Guild:
        id = 99
        name = "Test Server"
        preferred_locale = "en"
        me = None

    languages = ("en", "de", "es", "fr")
    references = set()
    for language in languages:
        payload = json.loads(
            (ROOT / "src" / "cogs" / "setup" / "locales" / f"{language}.json")
            .read_text(encoding="utf-8")
        )
        references |= set(command_ids._REFERENCE.findall(json.dumps(payload)))

    command_ids.remember({name: 9000 + index for index, name in enumerate(sorted(references))})

    for language in languages:
        guild = _Guild()
        guild.preferred_locale = language
        for step in ("welcome", "automod", "ai", "done"):
            state = setup_cog.SetupState(step=step)
            wizard = setup_cog.SetupWizard(
                SimpleNamespace(user=SimpleNamespace(
                    display_avatar=SimpleNamespace(url="https://example.test/a.png"))),
                guild,
                SimpleNamespace(id=7),
                state,
            )
            body = "\n".join(_texts(wizard))
            assert "`/" not in body, f"{language}/{step} still renders inline command code"
        if language == "en":
            assert "</automod:" in _texts_text(setup_cog, guild, "automod")
            assert "</leveling panel:" in _texts_text(setup_cog, guild, "leveling")


def _texts_text(setup_cog, guild, step):
    state = setup_cog.SetupState(step=step)
    wizard = setup_cog.SetupWizard(
        SimpleNamespace(user=SimpleNamespace(
            display_avatar=SimpleNamespace(url="https://example.test/a.png"))),
        guild,
        SimpleNamespace(id=7),
        state,
    )
    return "\n".join(_texts(wizard))


def _texts(item) -> list[str]:
    out = []
    for child in getattr(item, "children", []) or []:
        if isinstance(child, str):
            continue
        content = getattr(child, "content", None)
        if isinstance(content, str):
            out.append(content)
        out.extend(_texts(child))
    return out
