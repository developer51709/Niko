"""Persistent custom ids for the shop card and the avatar panel.

Both panels used to rely on a live view instance: once the bot restarted, the
buttons on already-posted messages stopped responding.  The shop buttons now
carry fixed ids registered at startup, and the avatar buttons carry the target
user id so the right person is resolved straight from the custom id.
"""

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

import discord

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.economy.commands import shop  # noqa: E402
from cogs.info import cog as info  # noqa: E402

SHOP_IDS = {"economy:shop:buy", "economy:shop:sell"}


class _Response:
    def __init__(self):
        self.kwargs = None

    async def send_message(self, **kwargs):
        self.kwargs = kwargs

    async def send(self, **kwargs):
        self.kwargs = kwargs


def _components(view):
    return repr(view.to_components())


# ── shop ──────────────────────────────────────────────────────────────────


def test_shop_buttons_use_stable_ids_and_a_persistent_view():
    view = shop._ShopActionView(SimpleNamespace())
    assert view.timeout is None
    assert view.is_persistent()
    buttons = [item for item in view.walk_children() if isinstance(item, discord.ui.Button)]
    assert {button.custom_id for button in buttons} == SHOP_IDS


def test_shop_buttons_open_a_private_checkout_for_the_clicker():
    class Cog:
        async def get_user_economy_data(self, user_id):
            assert user_id == 7
            return {"inventory": {}, "balance": 1000}

    view = shop._ShopActionView(Cog())
    interaction = SimpleNamespace(user=SimpleNamespace(id=7), response=_Response())
    asyncio.run(view._buy(interaction))
    assert interaction.response.kwargs["ephemeral"] is True
    assert isinstance(interaction.response.kwargs["view"], shop._ShopTransactionView)


# ── avatar ────────────────────────────────────────────────────────────────


def test_avatar_buttons_embed_the_target_user_id():
    row = info.AvatarButtons(4242)
    ids = [item.custom_id for item in row.walk_children()]
    assert ids == ["avatar:server:4242", "avatar:banner:4242"]


def test_avatar_templates_recover_the_user_id_after_a_restart():
    for button_cls, custom_id in (
        (info._ServerAvatarButton, "avatar:server:987654321"),
        (info._UserBannerButton, "avatar:banner:987654321"),
    ):
        match = button_cls(0).template.fullmatch(custom_id)
        assert match is not None
        item = asyncio.run(button_cls.from_custom_id(None, None, match))
        assert item.user_id == 987654321
        assert item.custom_id == custom_id


def test_server_avatar_button_resolves_the_member_from_its_custom_id():
    member = SimpleNamespace(guild_avatar=SimpleNamespace(url="https://cdn.example/server.png"))
    guild = SimpleNamespace(get_member=lambda user_id: member if user_id == 555 else None)
    interaction = SimpleNamespace(guild=guild, response=_Response())
    match = info._ServerAvatarButton(555).template.fullmatch("avatar:server:555")
    item = asyncio.run(info._ServerAvatarButton.from_custom_id(interaction, None, match))
    asyncio.run(item.callback(interaction))
    assert interaction.response.kwargs["ephemeral"] is True
    assert "https://cdn.example/server.png" in _components(interaction.response.kwargs["view"])


def test_user_banner_button_resolves_the_user_from_its_custom_id():
    user = SimpleNamespace(banner=SimpleNamespace(url="https://cdn.example/banner.png"))
    interaction = SimpleNamespace(
        client=SimpleNamespace(get_user=lambda user_id: user if user_id == 909 else None),
        response=_Response(),
    )
    match = info._UserBannerButton(909).template.fullmatch("avatar:banner:909")
    item = asyncio.run(info._UserBannerButton.from_custom_id(interaction, None, match))
    asyncio.run(item.callback(interaction))
    assert interaction.response.kwargs["ephemeral"] is True
    assert "https://cdn.example/banner.png" in _components(interaction.response.kwargs["view"])


def test_the_avatar_registry_registers_both_patterns_once():
    class Bot:
        def __init__(self):
            self.views = []

        def add_view(self, view, message_id=None):
            assert message_id is None
            self.views.append(view)

    bot = Bot()
    info.register_avatar_persistent_views(bot)
    assert len(bot.views) == 1
    assert bot.views[0].timeout is None
    assert bot.views[0].is_persistent()
