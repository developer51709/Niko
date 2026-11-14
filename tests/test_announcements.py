"""Support-server announcements sent by the MCP owner tool."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils import announcements  # noqa: E402


class FakeChannel:
    def __init__(self):
        self.sent = []

    async def send(self, **kwargs):
        self.sent.append(kwargs)
        return SimpleNamespace(id=9001, jump_url="https://discord.com/channels/1/2/9001")


def _bot(channel):
    return SimpleNamespace(
        get_channel=lambda channel_id: channel,
        fetch_channel=AsyncMock(side_effect=AssertionError("cached channel should be used")),
    )


def _config(monkeypatch, channels, roles):
    monkeypatch.setattr(
        announcements,
        "get_support_ids",
        AsyncMock(return_value={"channels": channels, "roles": roles}),
    )


def test_announcement_uses_the_support_channel_and_announcements_ping_role(monkeypatch):
    channel = FakeChannel()
    _config(monkeypatch, {"announcements": 444}, {"announcements_ping": 555})

    result = asyncio.run(announcements.send_support_announcement(
        _bot(channel), title="A new release", body="The details live here.",
        footer="Official Niko update",
    ))

    sent = channel.sent[0]
    assert sent["content"] == "<@&555>"
    assert sent["allowed_mentions"].roles[0].id == 555
    assert sent["allowed_mentions"].everyone is False
    assert sent["allowed_mentions"].users is False
    assert result["message_id"] == 9001
    assert result["channel_id"] == 444
    assert result["guild_id"] == announcements.SUPPORT_GUILD
    assert result["pinged_role_id"] == 555


def test_announcement_can_skip_the_ping(monkeypatch):
    channel = FakeChannel()
    _config(monkeypatch, {"announcements": 444}, {"announcements_ping": 555})

    result = asyncio.run(announcements.send_support_announcement(
        _bot(channel), title="Quiet update", body="No ping this time.", ping=False,
    ))

    sent = channel.sent[0]
    assert "content" not in sent
    assert not sent["allowed_mentions"].roles
    assert result["pinged_role_id"] is None


def test_missing_announcement_channel_is_actionable(monkeypatch):
    _config(monkeypatch, {}, {"announcements_ping": 555})

    with pytest.raises(RuntimeError, match="announcements channel is not configured"):
        asyncio.run(announcements.send_support_announcement(
            _bot(FakeChannel()), title="Title", body="Body",
        ))


def test_missing_announcements_ping_role_is_actionable(monkeypatch):
    _config(monkeypatch, {"announcements": 444}, {})

    with pytest.raises(RuntimeError, match="announcements ping role is not configured"):
        asyncio.run(announcements.send_support_announcement(
            _bot(FakeChannel()), title="Title", body="Body",
        ))
