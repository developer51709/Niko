"""The level-up announcement can carry a picture, like welcome and goodbye.

Servers set one URL and Discord renders it under the message, so the picture is
part of the same Components-V2 announcement rather than a second message.
"""

import asyncio
from types import SimpleNamespace
from unittest import mock

import discord

from cogs.leveling.cog import Leveling


def _cog(cfg):
    cog = object.__new__(Leveling)
    cog.bot = SimpleNamespace(dispatch=lambda *args, **kwargs: None)
    cog.get_xp_for_level = lambda level: 10

    async def guild_cfg(_guild_id):
        return dict(cfg)

    async def get_user_data(_guild_id, _user_id):
        return {"xp": 0, "level": 0}

    async def save_user_data(*_args):
        return None

    cog._guild_cfg = guild_cfg
    cog._get_user_data = get_user_data
    cog._save_user_data = save_user_data
    return cog


def _world(cfg):
    channel = SimpleNamespace(id=900, send=mock.AsyncMock())
    guild = SimpleNamespace(
        id=111,
        name="Test server",
        get_channel=lambda channel_id: channel if channel_id == channel.id else None,
        get_role=lambda role_id: None,
    )
    member = SimpleNamespace(id=42, mention="<@42>", add_roles=mock.AsyncMock())
    return guild, member, channel


def _container(view) -> discord.ui.Container:
    return view.children[0]


def test_the_announcement_shows_the_configured_image():
    guild, member, channel = _world(None)
    cfg = {"level_up_channel": channel.id, "level_up_image": "https://cdn.example/banner.png"}
    cog = _cog(cfg)

    asyncio.run(cog._grant_xp(guild, member, 999, cfg))

    channel.send.assert_awaited_once()
    items = _container(channel.send.await_args.kwargs["view"]).children
    galleries = [item for item in items if isinstance(item, discord.ui.MediaGallery)]
    assert len(galleries) == 1
    assert galleries[0].items[0].media.url == "https://cdn.example/banner.png"
    # The picture sits under the text, after a separator, like the greetings.
    assert isinstance(items[0], discord.ui.TextDisplay)
    assert isinstance(items[1], discord.ui.Separator)


def test_a_text_only_announcement_has_no_gallery():
    guild, member, channel = _world(None)
    cfg = {"level_up_channel": channel.id, "level_up_image": None}
    cog = _cog(cfg)

    asyncio.run(cog._grant_xp(guild, member, 999, cfg))

    items = _container(channel.send.await_args.kwargs["view"]).children
    assert not any(isinstance(item, discord.ui.MediaGallery) for item in items)


def test_a_blank_image_is_not_sent_as_a_gallery():
    guild, member, channel = _world(None)
    cfg = {"level_up_channel": channel.id, "level_up_image": "   "}
    cog = _cog(cfg)

    asyncio.run(cog._grant_xp(guild, member, 999, cfg))

    items = _container(channel.send.await_args.kwargs["view"]).children
    assert not any(isinstance(item, discord.ui.MediaGallery) for item in items)


class _Response:
    """The bare response an HTTPException needs for its status."""

    status = 400
    reason = "Bad Request"


def _rejected_media() -> discord.HTTPException:
    return discord.HTTPException(
        _Response(), {"code": 40062, "message": "Invalid media"},
    )


def test_a_rejected_image_falls_back_to_the_text_announcement(monkeypatch):
    guild, member, channel = _world(None)
    cfg = {"level_up_channel": channel.id, "level_up_image": "https://cdn.example/broken"}
    cog = _cog(cfg)
    warned = mock.Mock()
    monkeypatch.setattr("cogs.leveling.cog.log.warning", warned)
    # Discord refuses the message that carries the picture, not the channel.
    channel.send = mock.AsyncMock(side_effect=[_rejected_media(), None])

    asyncio.run(cog._grant_xp(guild, member, 999, cfg))

    assert channel.send.await_count == 2
    first = _container(channel.send.await_args_list[0].kwargs["view"]).children
    assert any(isinstance(item, discord.ui.MediaGallery) for item in first)
    second = _container(channel.send.await_args_list[1].kwargs["view"]).children
    assert not any(isinstance(item, discord.ui.MediaGallery) for item in second)
    assert isinstance(second[0], discord.ui.TextDisplay)
    warned.assert_called_once()
    assert "https://cdn.example/broken" in warned.call_args.args[1]


def test_a_rejected_message_without_an_image_is_not_retried(monkeypatch):
    guild, member, channel = _world(None)
    cfg = {"level_up_channel": channel.id, "level_up_image": None}
    cog = _cog(cfg)
    channel.send = mock.AsyncMock(side_effect=[_rejected_media()])

    asyncio.run(cog._grant_xp(guild, member, 999, cfg))

    channel.send.assert_awaited_once()


# ── The dashboard's read and write paths ──────────────────────────────────

class _Cxn:
    """The half of the database pool the config helpers use."""

    def __init__(self, row=None):
        self.row = row
        self.executed = []

    async def fetchrow(self, _query, *_args):
        return self.row

    async def execute(self, query, *args):
        self.executed.append((query, args))


def _saved_row(**overrides):
    row = {
        "xp_enabled": 1,
        "xp_multiplier": 1.0,
        "xp_cooldown": 0,
        "level_up_channel": None,
        "level_up_message": None,
        "level_up_image": None,
        "level_roles": {},
        "xp_excluded_channels": [],
        "xp_vc_enabled": 0,
        "card_accent": None,
        "card_bg_top": None,
        "card_bg_bottom": None,
    }
    row.update(overrides)
    return row


def test_saving_the_config_writes_the_image_column():
    cog = object.__new__(Leveling)
    cog.bot = SimpleNamespace(cxn=_Cxn())
    cfg = {"xp_enabled": True, "level_up_image": "https://cdn.example/banner.png"}

    asyncio.run(cog._save_guild_cfg(111, cfg))

    query, args = cog.bot.cxn.executed[0]
    assert "level_up_image" in query
    assert "https://cdn.example/banner.png" in args


def test_the_config_read_returns_the_saved_image():
    cog = object.__new__(Leveling)
    cog.bot = SimpleNamespace(cxn=_Cxn(_saved_row(level_up_image="https://cdn.example/banner.png")))

    assert asyncio.run(cog._guild_cfg(111))["level_up_image"] == "https://cdn.example/banner.png"


def test_a_server_without_an_image_reads_as_none():
    cog = object.__new__(Leveling)
    cog.bot = SimpleNamespace(cxn=_Cxn(_saved_row()))

    assert asyncio.run(cog._guild_cfg(111))["level_up_image"] is None


def test_the_dashboard_payload_carries_the_image():
    from webapp.database import _serialize_level_config

    payload = _serialize_level_config({
        "level_up_channel": 900,
        "level_up_image": "https://cdn.example/banner.png",
    })

    assert payload["level_up_image"] == "https://cdn.example/banner.png"
    assert payload["level_up_channel"] == "900"
