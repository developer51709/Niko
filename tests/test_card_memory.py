"""Rendered command cards must not stay in memory once they are uploaded.

The economy, shop, level, Spotify and Last.fm cards are drawn for one reply and
never reused, and each one is a megabyte or more of RGBA before it is encoded.
``discord.File`` stubs out its stream's ``close`` so an upload retry can still
read the buffer, which means nothing frees the PNG unless the command does — the
memory is left to a garbage collection that a busy host may not get to.
"""

import asyncio
import sys
from io import BytesIO
from pathlib import Path

import discord
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils.image.cards import (  # noqa: E402
    edit_with_card,
    release_card,
    reply_with_card,
    send_card,
)


def _buffer() -> BytesIO:
    buffer = BytesIO(b"\x89PNG card bytes")
    buffer.seek(0)
    return buffer


class _Message:
    def __init__(self, *, fail: bool = False):
        self.fail = fail
        self.kwargs = None

    async def edit(self, **kwargs):
        self.kwargs = kwargs
        if self.fail:
            raise RuntimeError("Discord answered 500")
        return self


def test_releasing_a_card_file_closes_the_stream_behind_it():
    buffer = _buffer()
    card = discord.File(buffer, "balance.png")

    release_card(card)

    assert buffer.closed
    assert card.fp.closed


def test_a_bare_stream_can_be_released_too():
    buffer = _buffer()

    release_card(buffer)

    assert buffer.closed


def test_releasing_nothing_is_harmless():
    release_card(None)
    buffer = _buffer()
    release_card(buffer)
    release_card(buffer)  # a second release, e.g. from a nested finally, is fine
    assert buffer.closed


def test_the_card_is_freed_once_it_is_uploaded():
    buffer = _buffer()
    message = _Message()

    asyncio.run(
        edit_with_card(message, view=object(), buffer=buffer, filename="balance.png")
    )

    card = message.kwargs["attachments"][0]
    assert card.filename == "balance.png"
    assert buffer.closed and card.fp.closed


def test_a_failed_upload_still_frees_the_card():
    buffer = _buffer()

    with pytest.raises(RuntimeError):
        asyncio.run(
            edit_with_card(
                _Message(fail=True), view=object(), buffer=buffer, filename="shop.png"
            )
        )

    assert buffer.closed


@pytest.mark.parametrize(
    "module",
    [
        "src/cogs/economy/cog.py",
        "src/cogs/economy/commands/shop.py",
        "src/cogs/leveling/cog.py",
        "src/cogs/info/_spotify.py",
    ],
)
def test_each_card_command_uploads_through_the_releasing_helper(module):
    """Every card send goes through ``edit_with_card``, so none can be kept.

    A ``discord.File`` built here and handed to ``message.edit`` would upload
    fine and then hold its PNG until collection; the helper exists so that cannot
    happen by accident when a card is added.
    """
    source = (ROOT / module).read_text(encoding="utf-8")

    assert "discord.File(" not in source
    assert "edit_with_card(" in source


def test_send_card_accepts_whatever_route_the_caller_uses():
    buffer = _buffer()
    seen = {}

    async def send(card):
        seen["card"] = card
        return "sent"

    result = asyncio.run(send_card(send, buffer=buffer, filename="fx.gif"))

    assert result == "sent"
    assert seen["card"].filename == "fx.gif"
    assert buffer.closed


class _ReplyCtx:
    """A prefix context whose reply can be made to fail."""

    def __init__(self, *, reply_fails: bool = False):
        self.reply_fails = reply_fails
        self.calls = []

    async def reply(self, **kwargs):
        self.calls.append(("reply", kwargs))
        if self.reply_fails:
            raise RuntimeError("Unknown Message")
        return kwargs

    async def send(self, **kwargs):
        self.calls.append(("send", kwargs))
        return kwargs


def test_reply_with_card_frees_the_gif_after_a_reply():
    ctx = _ReplyCtx()
    buffer = _buffer()

    asyncio.run(reply_with_card(ctx, view=object(), buffer=buffer, filename="blur.gif"))

    assert [name for name, _ in ctx.calls] == ["reply"]
    assert buffer.closed


def test_reply_with_card_frees_the_gif_when_the_reply_falls_back():
    ctx = _ReplyCtx(reply_fails=True)
    buffer = _buffer()

    asyncio.run(reply_with_card(ctx, view=object(), buffer=buffer, filename="blur.gif"))

    assert [name for name, _ in ctx.calls] == ["reply", "send"]
    assert buffer.closed


@pytest.mark.parametrize(
    "module",
    [
        "src/cogs/utility/image_tools.py",
        "src/cogs/ai/images.py",
    ],
)
def test_the_image_commands_upload_through_the_releasing_helpers(module):
    """A filter or generated PNG is uploaded once and its buffer handed back."""
    source = (ROOT / module).read_text(encoding="utf-8")

    assert "discord.File(" not in source
    assert "send_card(" in source or "reply_with_card(" in source


def test_the_image_tools_release_the_gif_they_just_sent(monkeypatch):
    """The whole modal path: render, upload, and leave nothing behind."""
    from io import BytesIO as _BytesIO

    from PIL import Image

    from cogs.utility import image_tools as tools

    gif = _BytesIO()
    Image.new("RGBA", (40, 30), (10, 10, 10)).save(gif, format="GIF")
    gif.seek(0)

    async def fake_extract(message):
        source = _BytesIO()
        Image.new("RGB", (40, 30), (200, 200, 200)).save(source, format="PNG")
        source.seek(0)
        return source

    sent = {}

    class _Response:
        async def defer(self):
            return None

        async def send_message(self, **kwargs):
            sent.update(kwargs)
            return None

    class _Interaction:
        response = _Response()
        guild = None

    monkeypatch.setattr(tools, "extract_image_from_message", fake_extract)
    monkeypatch.setattr(tools, "process_image_animated", lambda raw, fn: gif)

    modal = tools.CaptionModal(None, object(), "top", "en")
    asyncio.run(modal.on_submit(_Interaction()))

    assert sent["file"].filename == "caption_top.gif"
    assert gif.closed


def test_the_emoji_cache_does_not_grow_without_bound(monkeypatch):
    """A caption can name any custom emoji; the cache keeps only recent ones."""
    from io import BytesIO as _BytesIO

    from PIL import Image

    from utils.image import pil_tools

    png = _BytesIO()
    Image.new("RGBA", (8, 8), (1, 2, 3)).save(png, format="PNG")
    payload = png.getvalue()

    class _Fetched:
        content = payload

    monkeypatch.setattr(pil_tools.requests, "get", lambda url, timeout: _Fetched())
    pil_tools._EMOJI_CACHE.clear()

    for index in range(pil_tools._EMOJI_CACHE_LIMIT + 25):
        pil_tools._load_image_from_url(f"https://cdn.example/emoji/{index}.png")

    assert len(pil_tools._EMOJI_CACHE) == pil_tools._EMOJI_CACHE_LIMIT
    pil_tools._EMOJI_CACHE.clear()


def test_the_lastfm_cards_are_released_by_the_reply_that_sends_them():
    from cogs.lastfm import cog as lastfm_cog

    source = Path(lastfm_cog.__file__).read_text(encoding="utf-8")

    # ``_reply`` owns every card delivery in the cog, so the release lives there
    # (the period picker re-renders on its own route and releases in turn).
    reply = source.split("async def _reply(", 1)[1].split("async def ", 1)[0]
    assert "release_card(file)" in reply
    assert source.count("release_card(file)") >= 2
