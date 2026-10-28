"""AI image tools: free generation, its rate limit, and the retired /edit.

Image generation is free to run, which is exactly why the cooldown matters:
without it one member can exhaust the shared public provider for everyone. These
tests also pin the provider failure paths, because a raw HTTP error used to
reach the user as a broken or empty embed.
"""

import asyncio
import io
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.ai import images  # noqa: E402


class _Response:
    def __init__(self, *, status=200, body=b"\x89PNG", text=""):
        self.status = status
        self._body = body
        self._text = text

    async def read(self):
        return self._body

    async def text(self):
        return self._text

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _Session:
    """Stands in for aiohttp.ClientSession and records the requested URL."""

    requested: list[str] = []
    response: _Response = _Response()
    error: Exception | None = None

    def __init__(self, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def get(self, url, params=None):
        type(self).requested.append(url)
        type(self).params = params
        if type(self).error is not None:
            raise type(self).error
        return type(self).response


@pytest.fixture
def cog():
    return images.AiImageTools(SimpleNamespace())


@pytest.fixture(autouse=True)
def provider(monkeypatch):
    _Session.requested = []
    _Session.response = _Response()
    _Session.error = None
    monkeypatch.setattr(images.aiohttp, "ClientSession", _Session)
    return _Session


def test_the_prompt_is_url_encoded(cog):
    async def run():
        return await cog.generate_image("a red cat & a dog/in a hat")

    image, error = asyncio.run(run())
    assert error is None
    assert isinstance(image, io.BytesIO)
    assert image.getvalue() == b"\x89PNG"
    url = _Session.requested[0]
    assert url.startswith("https://image.pollinations.ai/prompt/")
    assert " " not in url and "&" not in url
    assert url.endswith("a%20red%20cat%20%26%20a%20dog%2Fin%20a%20hat")
    assert _Session.params["seed"] >= 1


def test_a_provider_error_becomes_a_friendly_message(cog):
    _Session.response = _Response(status=502, body=b"", text="upstream down")

    async def run():
        return await cog.generate_image("cat")

    image, error = asyncio.run(run())
    assert image is None
    assert "busy" in error.lower()


def test_an_empty_body_is_an_error(cog):
    _Session.response = _Response(body=b"")

    async def run():
        return await cog.generate_image("cat")

    image, error = asyncio.run(run())
    assert image is None
    assert "empty" in error.lower()


def test_a_network_failure_is_caught(cog):
    _Session.error = RuntimeError("connection reset")

    async def run():
        return await cog.generate_image("cat")

    image, error = asyncio.run(run())
    assert image is None
    assert "could not be reached" in error.lower()


def test_generation_is_rate_limited_per_user(cog):
    command = cog.generate
    cooldown = command._buckets._cooldown
    assert cooldown.rate == 1
    assert cooldown.per == images.USER_COOLDOWN
    assert command._buckets._type is images.commands.BucketType.user
    assert images.USER_COOLDOWN >= 1


def test_edit_is_retired_and_hidden(cog):
    sent = {}

    class Ctx:
        prefix = "."
        author = SimpleNamespace(id=1)

        async def reply(self, **kwargs):
            sent.update(kwargs)

    assert cog.edit.hidden is True
    asyncio.run(cog.edit.callback(cog, Ctx(), prompt="make it blue"))

    view = sent["view"]
    texts = [
        item.content
        for container in view.children
        for item in getattr(container, "children", [])
        if hasattr(item, "content")
    ]
    body = "\n".join(texts).lower()
    assert "removed" in body or "retired" in body
    assert "cost" in body or "charged" in body
    assert "suggestion" in body

    buttons = [
        item
        for container in view.children
        for row in getattr(container, "children", [])
        for item in getattr(row, "children", [])
        if hasattr(item, "url")
    ]
    assert buttons and buttons[0].url.endswith("/discord")


def test_setmodlog_is_gone():
    from cogs.moderation.commands import Moderation

    assert not hasattr(Moderation, "setmodlog")
    assert hasattr(Moderation, "badwords")
