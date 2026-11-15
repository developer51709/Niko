"""Support-server announcements sent by the MCP owner tool."""

from __future__ import annotations

import asyncio
import base64
import sys
from datetime import timedelta
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


class FakeMessage:
    def __init__(self, message_id=9001, *, author_id=777, created_at=None, attachments=None):
        self.id = message_id
        self.jump_url = f"https://discord.com/channels/1/2/{message_id}"
        self.author = SimpleNamespace(id=author_id)
        self.created_at = created_at or discord.utils.utcnow()
        self.attachments = list(attachments or [])
        self.edits = []
        self.deleted = False

    async def edit(self, **kwargs):
        self.edits.append(kwargs)
        return self

    async def delete(self):
        self.deleted = True


class FakeChannel:
    def __init__(self):
        self.sent = []
        self.messages = {}

    async def send(self, **kwargs):
        self.sent.append(kwargs)
        return FakeMessage(9001)

    async def fetch_message(self, message_id):
        return self.messages[message_id]


def _bot(channel):
    return SimpleNamespace(
        user=SimpleNamespace(id=777),
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
    assert "content" not in sent
    container = sent["view"].children[0]
    assert container.accent_colour is None
    assert "<@&555>" not in container.children[2].content
    assert "<@&555>" in container.children[-1].content
    assert sent["allowed_mentions"].roles[0].id == 555
    assert sent["allowed_mentions"].everyone is False
    assert sent["allowed_mentions"].users is False
    assert result["message_id"] == 9001
    assert result["channel_id"] == 444
    assert result["guild_id"] == announcements.SUPPORT_GUILD
    assert result["pinged_role_id"] == 555
    assert result["message_url"] == "https://discord.com/channels/1/2/9001"
    assert result["url"] == result["message_url"]


def test_announcement_can_skip_the_ping(monkeypatch):
    channel = FakeChannel()
    _config(monkeypatch, {"announcements": 444}, {"announcements_ping": 555})

    result = asyncio.run(announcements.send_support_announcement(
        _bot(channel), title="Quiet update", body="No ping this time.", ping=False,
    ))

    sent = channel.sent[0]
    assert "content" not in sent
    text = "\n".join(
        item.content for item in sent["view"].walk_children()
        if isinstance(item, discord.ui.TextDisplay)
    )
    assert "<@&555>" not in text
    assert sent["view"].children[0].accent_colour is None
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
    assert sent["view"].children[0].accent_colour is None
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


def test_announcement_downloads_an_image_url_and_uploads_it(monkeypatch):
    channel = FakeChannel()
    _config(monkeypatch, {"announcements": 444}, {"announcements_ping": 555})
    download = AsyncMock(return_value=PNG)
    monkeypatch.setattr(announcements, "_download_image", download)

    result = asyncio.run(announcements.send_support_announcement(
        _bot(channel),
        title="URL image",
        body="The host downloads it first.",
        images=[{"url": "https://cdn.example/release.png?ex=123&hm=abc"}],
    ))

    download.assert_awaited_once_with("https://cdn.example/release.png?ex=123&hm=abc", 1)
    sent = channel.sent[0]
    assert len(sent["files"]) == 1
    assert sent["files"][0].filename.startswith("release-")
    assert result["image_count"] == 1


def test_announcement_rejects_unsupported_image_urls():
    with pytest.raises(ValueError, match="http or https"):
        asyncio.run(announcements._download_image("ftp://cdn.example/image.png", 1))


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

    with pytest.raises(ValueError, match="exactly one of data or url"):
        asyncio.run(announcements.send_support_announcement(
            _bot(FakeChannel()), title="Title", body="Body",
            images=[{
                "data": base64.b64encode(PNG).decode("ascii"),
                "url": "https://cdn.example/image.png",
            }],
        ))

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


def test_edit_announcement_preserves_existing_images_and_returns_url(monkeypatch):
    channel = FakeChannel()
    attachment = SimpleNamespace(id=11, filename="old-release.png")
    message = FakeMessage(9001, attachments=[attachment])
    channel.messages[9001] = message
    _config(monkeypatch, {"announcements": 444}, {"announcements_ping": 555})

    result = asyncio.run(announcements.edit_support_announcement(
        _bot(channel), message_id=9001, title="Fixed title", body="Corrected body.",
        footer="Official Niko update",
    ))

    edited = message.edits[0]
    assert edited["content"] is None
    assert edited["embed"] is None
    assert edited["attachments"] == [attachment]
    assert not edited["allowed_mentions"].roles
    gallery = next(
        item for item in edited["view"].walk_children()
        if isinstance(item, discord.ui.MediaGallery)
    )
    assert gallery.items[0].media.url == "attachment://old-release.png"
    assert result["edited"] is True
    assert result["message_url"] == "https://discord.com/channels/1/2/9001"
    assert result["image_count"] == 1


def test_edit_announcement_replaces_images_and_can_ping(monkeypatch):
    channel = FakeChannel()
    old_attachment = SimpleNamespace(id=11, filename="old-release.png")
    message = FakeMessage(9001, attachments=[old_attachment])
    channel.messages[9001] = message
    _config(monkeypatch, {"announcements": 444}, {"announcements_ping": 555})

    result = asyncio.run(announcements.edit_support_announcement(
        _bot(channel), message_id=9001, title="Fixed title", body="Corrected body.",
        images=[{"data": base64.b64encode(PNG).decode("ascii"), "filename": "new.png"}],
        ping=True,
    ))

    edited = message.edits[0]
    assert len(edited["attachments"]) == 1
    assert edited["attachments"][0].filename.startswith("new-")
    assert edited["allowed_mentions"].roles[0].id == 555
    gallery = next(
        item for item in edited["view"].walk_children()
        if isinstance(item, discord.ui.MediaGallery)
    )
    assert gallery.items[0].media.url.startswith("attachment://new-")
    assert result["pinged_role_id"] == 555
    assert result["image_count"] == 1


def test_delete_announcement_removes_a_recent_bot_message(monkeypatch):
    channel = FakeChannel()
    message = FakeMessage(9001)
    channel.messages[9001] = message
    _config(monkeypatch, {"announcements": 444}, {"announcements_ping": 555})

    result = asyncio.run(announcements.delete_support_announcement(
        _bot(channel), message_id=9001,
    ))

    assert message.deleted is True
    assert result["deleted"] is True
    assert result["message_id"] == 9001
    assert result["message_url"] == "https://discord.com/channels/1/2/9001"


def test_announcement_management_rejects_other_authors_and_old_messages(monkeypatch):
    channel = FakeChannel()
    other_author = FakeMessage(9001, author_id=999)
    channel.messages[9001] = other_author
    _config(monkeypatch, {"announcements": 444}, {"announcements_ping": 555})

    with pytest.raises(ValueError, match="Only Niko's own announcements"):
        asyncio.run(announcements.delete_support_announcement(
            _bot(channel), message_id=9001,
        ))

    old_message = FakeMessage(
        9002, created_at=discord.utils.utcnow() - timedelta(days=8),
    )
    channel.messages[9002] = old_message
    with pytest.raises(ValueError, match="last 7 days"):
        asyncio.run(announcements.delete_support_announcement(
            _bot(channel), message_id=9002,
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
