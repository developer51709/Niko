"""The about card: live figures, and the creator shared with /creator.

/about used to name a developer in a hardcoded string while /creator opened a
different account by id, so the two cards could disagree. These tests pin the
shared id, the live numbers the card reports, and the regenerated emoji the
website button uses.
"""

import asyncio
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import discord

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.info import _about  # noqa: E402
from config import emojis, ids  # noqa: E402


def _text(view):
    """Every text component in a rendered view, in document order."""
    chunks = []

    def walk(node):
        if isinstance(node, dict):
            content = node.get("content")
            if isinstance(content, str):
                chunks.append(content)
            for child in node.get("components", []):
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(view.to_components())
    return "\n".join(chunks)


class _Ctx:
    guild = SimpleNamespace(preferred_locale=None)

    def __init__(self):
        self.sent = []

    async def send(self, content=None, **kwargs):
        self.sent.append({"content": content, **kwargs})


def _creator():
    return SimpleNamespace(
        id=_about.CREATOR_ID,
        display_name="soren",
        mention=f"<@{_about.CREATOR_ID}>",
        avatar=None,
    )


def _bot(creator=None, *, command_count=0):
    return SimpleNamespace(
        user=SimpleNamespace(id=1520558530472448170, avatar=None),
        guilds=[SimpleNamespace(member_count=10), SimpleNamespace(member_count=5)],
        commands={"one": object(), "two": object()},
        get_user=lambda user_id: creator if creator and user_id == _about.CREATOR_ID else None,
        start_time=time.time() - 2 * 3600 - 30 * 60,
        _status_command_count=command_count,
    )


def _about_body(creator=None, **kwargs):
    cog = _about.AboutMixin()
    cog.bot = _bot(creator, **kwargs)
    ctx = _Ctx()
    # The commands are hybrid_command objects, so the mixin's own coroutine is
    # reached through their callback.
    asyncio.run(cog.about.callback(cog, ctx))
    return ctx.sent[-1]["view"]


def test_the_creator_id_comes_from_the_owner_set():
    assert _about.CREATOR_ID in ids.OWNER_IDS


def test_about_names_the_same_account_the_creator_command_opens():
    view = _about_body(_creator())

    assert f"soren (<@{_about.CREATOR_ID}>)" in _text(view)


def test_both_cards_accept_the_same_creator_lookup():
    cog = _about.AboutMixin()
    cog.bot = _bot(_creator())
    ctx = _Ctx()

    asyncio.run(cog.creator.callback(cog, ctx))

    creator_text = _text(ctx.sent[-1]["view"])
    assert "soren" in creator_text
    assert f"`{_about.CREATOR_ID}`" in creator_text


def test_the_about_card_reports_live_figures():
    body = _text(_about_body(_creator()))

    assert "**Servers:** 2" in body
    assert "**Members:** 15" in body
    # The status-panel count is authoritative when it exists; 0 means it was
    # never written, so the live command registry answers instead.
    assert "**Commands:** 2" in body
    assert "**Uptime:** 2h 30m" in body
    assert "discord.py 2.7" in body


def test_the_about_card_prefers_the_written_command_count():
    body = _text(_about_body(_creator(), command_count=323))

    assert "**Commands:** 323" in body


def test_a_cached_creator_costs_no_api_call():
    creator = _creator()
    bot = SimpleNamespace(get_user=lambda _id: creator)

    assert asyncio.run(_about.resolve_creator(bot)) is creator


def test_a_missing_creator_falls_back_to_the_api():
    creator = _creator()

    async def fetch(_id):
        return creator

    bot = SimpleNamespace(get_user=lambda _id: None, fetch_user=fetch)

    assert asyncio.run(_about.resolve_creator(bot)) is creator


def test_a_failed_lookup_leaves_the_cards_usable():
    async def fetch(_id):
        raise discord.NotFound(
            SimpleNamespace(status=404, reason="Not Found", headers={}),
            "Unknown User",
        )

    bot = SimpleNamespace(get_user=lambda _id: None, fetch_user=fetch)

    assert asyncio.run(_about.resolve_creator(bot)) is None
    # With no account to show, /creator answers instead of raising.
    cog = _about.AboutMixin()
    cog.bot = bot
    ctx = _Ctx()
    asyncio.run(cog.creator.callback(cog, ctx))
    assert "try again" in ctx.sent[-1]["content"]


def _button_emoji(view, label):
    """The emoji names on every button with ``label``."""
    names = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == 2 and node.get("label") == label:
                names.append((node.get("emoji") or {}).get("name"))
            for child in node.get("components", []):
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(view.to_components())
    return names


def test_the_website_button_uses_the_generated_website_emoji():
    # The name stays "website": the old application emoji is deleted by hand, so
    # the startup sync simply uploads the new globe art under the same name.
    assert emojis.get_emoji("globe") is None
    assert "<:website:" in emojis.get_emoji("website")
    # The art is the generator's 128px single-ink tile, not the old 48px earth.
    assert (ROOT / "src" / "assets" / "emojis" / "website.png").exists()
    assert not (ROOT / "src" / "assets" / "emojis" / "globe.png").exists()

    assert _button_emoji(_about_body(_creator()), "Website") == ["website"]
