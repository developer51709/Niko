"""Support-server announcements sent by the MCP owner tool."""

from __future__ import annotations

import asyncio
import base64
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import discord
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils import announcements  # noqa: E402

# A 1x1 transparent PNG, enough for the magic-byte check and a real attachment.
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9ZcWQAAAAASUVORK5CYII="
)


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


def test_announcement_attaches_images_as_a_broadcast_style_gallery(monkeypatch):
    channel = FakeChannel()
    _config(monkeypatch, {"announcements": 444}, {"announcements_ping": 555})

    result = asyncio.run(announcements.send_support_announcement(
        _bot(channel),
        title="Release with art",
        body="The new artwork is attached.",
        images=[{
            "data": base64.b64encode(PNG).decode("ascii"),
            "filename": "release.png",
            "spoiler": True,
        }],
    ))

    sent = channel.sent[0]
    assert len(sent["files"]) == 1
    filename = sent["files"][0].filename
    assert filename.startswith("release-")
    assert filename.endswith(".png")

    gallery = next(
        item for item in sent["view"].walk_children()
        if isinstance(item, discord.ui.MediaGallery)
    )
    assert gallery.items[0].media.url == f"attachment://{filename}"
    assert gallery.items[0].spoiler is True
    assert result["image_count"] == 1


def test_announcement_accepts_a_base64_data_uri(monkeypatch):
    channel = FakeChannel()
    _config(monkeypatch, {"announcements": 444}, {"announcements_ping": 555})

    asyncio.run(announcements.send_support_announcement(
        _bot(channel),
        title="Data URI",
        body="Image bytes can arrive as a data URI.",
        images=[{"data": f"data:image/png;base64,{base64.b64encode(PNG).decode('ascii')}"}],
    ))

    assert channel.sent[0]["files"][0].filename.endswith(".png")


def test_announcement_accepts_the_maximum_image_count(monkeypatch):
    channel = FakeChannel()
    _config(monkeypatch, {"announcements": 444}, {"announcements_ping": 555})
    encoded = base64.b64encode(PNG).decode("ascii")

    result = asyncio.run(announcements.send_support_announcement(
        _bot(channel),
        title="Ten images",
        body="The gallery is full.",
        images=[{"data": encoded} for _ in range(10)],
    ))

    assert result["image_count"] == 10
    assert len(channel.sent[0]["files"]) == 10


def test_announcement_rejects_more_than_ten_images(monkeypatch):
    _config(monkeypatch, {"announcements": 444}, {"announcements_ping": 555})
    encoded = base64.b64encode(PNG).decode("ascii")

    with pytest.raises(ValueError, match="up to 10 images"):
        asyncio.run(announcements.send_support_announcement(
            _bot(FakeChannel()), title="Too many", body="Eleven images.",
            images=[{"data": encoded} for _ in range(11)],
        ))


def test_announcement_rejects_an_image_over_the_per_image_limit(monkeypatch):
    monkeypatch.setattr(announcements, "MAX_MEDIA_BYTES", len(PNG) - 1)
    _config(monkeypatch, {"announcements": 444}, {"announcements_ping": 555})

    with pytest.raises(ValueError, match=r"Image 1 is larger than"):
        asyncio.run(announcements.send_support_announcement(
            _bot(FakeChannel()), title="Too large", body="One oversized image.",
            images=[{"data": base64.b64encode(PNG).decode("ascii")}],
        ))


def test_announcement_rejects_images_over_the_total_limit(monkeypatch):
    monkeypatch.setattr(announcements, "MAX_TOTAL_MEDIA_BYTES", len(PNG) * 2 - 1)
    _config(monkeypatch, {"announcements": 444}, {"announcements_ping": 555})
    encoded = base64.b64encode(PNG).decode("ascii")

    with pytest.raises(ValueError, match=r"must total .* MiB or less"):
        asyncio.run(announcements.send_support_announcement(
            _bot(FakeChannel()), title="Too large", body="Two images over the total.",
            images=[{"data": encoded}, {"data": encoded}],
        ))


def test_announcement_rejects_invalid_or_unsupported_images(monkeypatch):
    _config(monkeypatch, {"announcements": 444}, {"announcements_ping": 555})

    with pytest.raises(ValueError, match="not valid base64"):
        asyncio.run(announcements.send_support_announcement(
            _bot(FakeChannel()), title="Title", body="Body",
            images=[{"data": "not base64"}],
        ))

    with pytest.raises(ValueError, match="PNG, JPEG, GIF, or WebP"):
        asyncio.run(announcements.send_support_announcement(
            _bot(FakeChannel()), title="Title", body="Body",
            images=[{"data": base64.b64encode(b"not an image").decode("ascii")}],
        ))

    with pytest.raises(ValueError, match="spoiler must be true or false"):
        asyncio.run(announcements.send_support_announcement(
            _bot(FakeChannel()), title="Title", body="Body",
            images=[{
                "data": base64.b64encode(PNG).decode("ascii"),
                "spoiler": "false",
            }],
        ))


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
