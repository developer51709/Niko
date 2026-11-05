"""`/language` stores a server's choice and `get_lang` reads it first.

Discord only fills ``guild.preferred_locale`` when a server enables Community,
so the override is what lets every other server pick a language. These checks
cover the resolver, the store, and the command's place in the help menu.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from discord.ext import commands  # noqa: E402

from cogs.admin.language import LanguageConfig  # noqa: E402
from cogs.help.views import CATEGORY_COGS  # noqa: E402
from utils import guild_language  # noqa: E402
from utils.command_locales import command_texts  # noqa: E402
from utils.i18n import get_lang  # noqa: E402
from utils.locales import SUPPORTED_LANGUAGES  # noqa: E402


class FakePool:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.executed = []

    async def fetch(self, query, *args):
        self.query = query
        return self.rows

    async def execute(self, query, *args):
        self.executed.append((query, args))


def _guild(guild_id=1, locale=None):
    return SimpleNamespace(id=guild_id, preferred_locale=locale)


@pytest.fixture(autouse=True)
def _clean_cache():
    guild_language._cache.clear()
    yield
    guild_language._cache.clear()


def test_a_server_choice_wins_over_the_discord_locale():
    guild_language._cache[1] = "es"

    assert get_lang(_guild(1, "de-DE")) == "es"


def test_without_a_choice_discord_locale_and_english_apply():
    assert get_lang(_guild(1, "de-DE")) == "de"
    assert get_lang(_guild(1, None)) == "en"
    assert get_lang(None) == "en"


def test_load_reads_known_languages_and_skips_unknown_ones():
    pool = FakePool([
        {"guild_id": 1, "language": "de"},
        {"guild_id": 2, "language": "klingon"},
    ])

    asyncio.run(guild_language.load(SimpleNamespace(cxn=pool)))

    assert guild_language.language_for(1) == "de"
    assert guild_language.language_for(2) is None
    assert "guild_languages" in pool.query


def test_setting_a_language_writes_the_row_and_updates_the_cache():
    pool = FakePool()

    assert asyncio.run(guild_language.set_language(7, "FR", pool)) == "fr"

    query, args = pool.executed[0]
    assert "INSERT OR REPLACE INTO guild_languages" in query
    assert args == (7, "fr")
    assert get_lang(_guild(7, "de")) == "fr"


def test_clearing_a_language_returns_the_server_to_discord():
    pool = FakePool()
    guild_language._cache[7] = "fr"

    asyncio.run(guild_language.clear_language(7, pool))

    assert guild_language.language_for(7) is None
    assert get_lang(_guild(7, "de")) == "de"
    assert "DELETE FROM guild_languages" in pool.executed[0][0]


def test_an_unsupported_language_is_rejected_before_writing():
    pool = FakePool()

    with pytest.raises(ValueError):
        asyncio.run(guild_language.set_language(7, "xx", pool))

    assert pool.executed == []


def test_the_language_command_is_hybrid_and_listed_under_customization():
    cog = LanguageConfig(SimpleNamespace(cxn=None))
    commands_by_name = {command.name: command for command in cog.get_commands()}

    command = commands_by_name["language"]
    assert isinstance(command, commands.HybridCommand)
    assert "lang" in command.aliases
    assert "LanguageConfig" in CATEGORY_COGS["Customization"]


def test_the_language_command_is_translated():
    texts = command_texts("cogs.admin")

    assert texts.english("language.description")
    for language in ("en", "de", "es", "fr"):
        assert texts.language_map("language.description").get(language)
        assert texts.language_map("language.help").get(language)
        assert texts.language_map("language.args.language").get(language)


def test_every_shipped_language_can_be_chosen():
    from cogs.admin.language import LANGUAGE_CHOICES

    values = {choice.value for choice in LANGUAGE_CHOICES}

    assert set(SUPPORTED_LANGUAGES) <= values
    assert "auto" in values
