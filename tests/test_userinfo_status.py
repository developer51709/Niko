"""/userinfo's status line: the live presence, the phone art, and its fallbacks.

Run with:  python -m pytest tests/test_userinfo_status.py -v
"""

import sys
from pathlib import Path
from types import SimpleNamespace

import discord
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.info import _users as info  # noqa: E402
from utils.emoji_sync import asset_path_for  # noqa: E402

PHONE_VARIANTS = ("status_online_mobile", "status_idle_mobile", "status_dnd_mobile")


def _member(status=discord.Status.offline, activities=(), mobile="offline",
            desktop="offline", web="offline"):
    return SimpleNamespace(
        id=7, status=status, activities=list(activities),
        mobile_status=mobile, desktop_status=desktop, web_status=web,
    )


def _ctx(cached=None):
    """A guild context whose cache holds ``cached``."""
    return SimpleNamespace(guild=SimpleNamespace(
        get_member=lambda user_id: cached if user_id == 7 else None,
    ))


@pytest.fixture
def emoji_tokens(monkeypatch):
    """Every emoji name resolves, so the tests are about which one is picked."""
    def fake(name):
        return f"<:{name}:1571270000000000000>"

    monkeypatch.setattr(info, "get_emoji", fake)


def test_a_phone_only_presence_uses_the_phone_art(emoji_tokens):
    """A slash call leaves the member's presence out; the cache has it."""
    phone = _member(status=discord.Status.dnd, mobile="dnd")
    stale = _member(status=discord.Status.offline)  # what the interaction carries

    emoji, text = info._status_line(_ctx(phone), stale)

    assert "status_dnd_mobile" in emoji
    assert text == "Do Not Disturb"


def test_a_desktop_session_keeps_the_round_dot(emoji_tokens):
    member = _member(status=discord.Status.dnd, mobile="dnd", desktop="online")

    emoji, _text = info._status_line(_ctx(member), member)

    assert "status_dnd_mobile" not in emoji
    assert "status_dnd" in emoji


def test_the_round_dot_stands_in_when_the_phone_art_is_missing(monkeypatch):
    def fake(name):
        if name.endswith("_mobile"):
            return None
        return f"<:{name}:1571270000000000000>"

    monkeypatch.setattr(info, "get_emoji", fake)
    phone = _member(status=discord.Status.idle, mobile="idle")

    emoji, text = info._status_line(_ctx(phone), phone)

    assert "status_idle" in emoji
    assert text == "Idle"


def test_an_unfilled_config_stub_is_never_sent(monkeypatch):
    """The config holds a placeholder id until the emoji sync uploads the art."""
    monkeypatch.setattr(info, "get_emoji", lambda name: f"<:{name}:9000001>")
    phone = _member(status=discord.Status.dnd, mobile="dnd")

    assert info._ready_emoji("status_dnd") is None
    emoji, _text = info._status_line(_ctx(phone), phone)
    assert emoji is None


def test_a_live_emoji_id_is_sent(monkeypatch):
    monkeypatch.setattr(info, "get_emoji", lambda name: f"<:{name}:1571270000000000000>")

    assert info._ready_emoji("status_dnd") == "<:status_dnd:1571270000000000000>"


def test_streaming_still_wins_on_a_phone(emoji_tokens):
    activity = discord.Streaming(name="Live", url="https://twitch.tv/niko")
    phone = _member(status=discord.Status.online, mobile="online", activities=[activity])

    emoji, text = info._status_line(_ctx(phone), phone)

    assert "status_streaming" in emoji
    assert text == "Streaming"


def test_every_phone_variant_is_configured_and_has_art():
    """A name with no config entry is an emoji nobody ever uploads."""
    for name in PHONE_VARIANTS:
        token = info.get_emoji(name)
        assert token and f":{name}:" in token, name
        assert asset_path_for(name).exists(), name
