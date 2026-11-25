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
import pytest

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
    text = _text(_about_body(_creator()))

    assert "soren" in text


def test_the_about_card_names_the_developer_without_pinging_them():
    # A mention would ping the developer on every /about and show as
    # "unknown-user" in servers the account does not share with the bot.
    text = _text(_about_body(_creator()))

    assert f"<@{_about.CREATOR_ID}>" not in text
    assert "**Developer:** soren" in text


def test_a_failed_creator_lookup_does_not_fall_back_to_a_mention():
    async def fetch(_id):
        raise discord.NotFound(
            SimpleNamespace(status=404, reason="Not Found", headers={}),
            "Unknown User",
        )

    cog = _about.AboutMixin()
    cog.bot = SimpleNamespace(
        user=SimpleNamespace(id=1520558530472448170, avatar=None),
        guilds=[],
        commands={},
        get_user=lambda _id: None,
        fetch_user=fetch,
        start_time=time.time(),
    )
    ctx = _Ctx()
    asyncio.run(cog.about.callback(cog, ctx))

    text = _text(ctx.sent[-1]["view"])
    assert f"<@{_about.CREATOR_ID}>" not in text
    assert "**Developer:** Unavailable" in text


@pytest.fixture(autouse=True)
def _no_website_calls(monkeypatch):
    """Never let a test reach the public team API."""

    async def offline(_user_id):
        return None

    _about._staff_profile_cache.clear()
    monkeypatch.setattr(_about, "_fetch_staff_profile", offline)
    yield
    _about._staff_profile_cache.clear()


#: What `GET /api/team/<id>` returns for the creator's public profile.
_PROFILE = {
    "id": str(_about.CREATOR_ID),
    "name": "! Soren",
    "handle": "soren.xd",
    "avatar_url": "https://cdn.example/avatar.png",
    "role_label": "Owner",
    "bio": "Hi, I'm Soren, the creator and lead developer of Niko.",
    "visible": True,
    "card": {"accent": "EAF6FF"},
}


def _creator_card(profile=None, *, creator=None):
    """Render /creator with the staff profile the website would return."""
    _about._staff_profile_cache[_about.CREATOR_ID] = (time.monotonic(), profile)
    cog = _about.AboutMixin()
    cog.bot = _bot(_creator() if creator is None else creator)
    ctx = _Ctx()
    asyncio.run(cog.creator.callback(cog, ctx))
    return ctx.sent[-1]["view"]


def _buttons(view):
    """Every button component in a rendered view."""
    found = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == 2:
                found.append(node)
            for child in node.get("components", []):
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(view.to_components())
    return found


def test_both_cards_accept_the_same_creator_lookup():
    creator_text = _text(_creator_card(_PROFILE))
    about_text = _text(_about_body(_creator()))

    assert "soren" in creator_text
    assert "soren" in about_text


def test_the_creator_card_shows_the_public_staff_profile():
    text = _text(_creator_card(_PROFILE))

    assert f"**Role:** {_PROFILE['role_label']}" in text
    assert _PROFILE["bio"] in text
    # The footer opens the same public page the team directory links to.
    assert "[View staff profile](https://niko.sryze.cc/team/soren.xd)" in text


def test_the_creator_card_has_no_social_link_buttons():
    # The links live on the staff profile page, so the card only points there.
    assert _buttons(_creator_card(_PROFILE)) == []


def test_a_hidden_staff_profile_is_neither_shown_nor_linked():
    text = _text(_creator_card({**_PROFILE, "visible": False}))

    assert "soren" in text
    assert _PROFILE["role_label"] not in text
    assert _PROFILE["bio"] not in text
    # Linking to a hidden profile would only land the reader on a 404.
    assert "/team/" not in text


def test_a_missing_profile_still_renders_the_creator():
    text = _text(_creator_card(None))

    assert "soren" in text
    assert "/team/" not in text


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
    from utils.emoji_sync import asset_path_for

    assert asset_path_for("website").exists()
    assert not asset_path_for("globe").exists()

    assert _button_emoji(_about_body(_creator()), "Website") == ["website"]
