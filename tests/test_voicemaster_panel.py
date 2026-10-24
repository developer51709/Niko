import asyncio
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import aiosqlite
import discord

sys.path.insert(0, "src")

import cogs.voicemaster.cog as voicemaster_module
from config.ids import SUPPORT_GUILD
from cogs.voicemaster.cog import VoiceMaster, VoiceMasterChannelSelect, VoiceMasterInterface, VoiceMasterSetupView
from database import SQLitePool


class FakeResponse:
    def __init__(self):
        self.calls = []

    async def send_message(self, *args, **kwargs):
        self.calls.append((args, kwargs))

    @property
    def texts(self):
        texts = []
        for args, _kwargs in self.calls:
            for item in args:
                texts.append(str(item))
            view = _kwargs.get("view")
            if view is not None:
                for child in view.walk_children():
                    content = getattr(child, "content", None)
                    if content:
                        texts.append(content)
        return "\n".join(texts)


def _interaction(guild_id, *, owned=True, in_voice=True):
    channel = SimpleNamespace(id=22)
    user = SimpleNamespace(
        id=5,
        voice=SimpleNamespace(channel=channel) if in_voice else None,
    )
    cog = SimpleNamespace(
        is_channel_owner=AsyncMock(return_value=owned),
        lock_channel=AsyncMock(),
        unlock_channel=AsyncMock(),
        ghost_channel=AsyncMock(),
        unghost_channel=AsyncMock(),
        increase_limit=AsyncMock(),
        decrease_limit=AsyncMock(),
        claim_channel=AsyncMock(return_value=True),
        get_channel_info=AsyncMock(return_value=discord.ui.LayoutView()),
    )
    response = FakeResponse()
    interaction = SimpleNamespace(
        guild_id=guild_id,
        user=user,
        response=response,
        client=SimpleNamespace(get_cog=lambda _name: cog),
    )
    return interaction, cog


class VoiceMasterPanelTests(unittest.TestCase):
    def test_lock_works_outside_the_support_server(self):
        async def check():
            interaction, cog = _interaction(987654321)
            self.assertNotEqual(interaction.guild_id, SUPPORT_GUILD)
            await VoiceMasterInterface()._dispatch(interaction, "lock")
            cog.lock_channel.assert_awaited_once()
            self.assertNotIn("support server", interaction.response.texts.lower())
            self.assertIn("locked", interaction.response.texts.lower())

        asyncio.run(check())

    def test_non_owner_is_still_refused_outside_the_support_server(self):
        async def check():
            interaction, cog = _interaction(987654321, owned=False)
            await VoiceMasterInterface()._dispatch(interaction, "lock")
            cog.lock_channel.assert_not_awaited()
            self.assertIn("don't own", interaction.response.texts.lower())

        asyncio.run(check())

    def test_member_outside_voice_is_refused(self):
        async def check():
            interaction, cog = _interaction(987654321, in_voice=False)
            await VoiceMasterInterface()._dispatch(interaction, "increase_limit")
            cog.increase_limit.assert_not_awaited()
            self.assertIn("voice channel", interaction.response.texts.lower())

        asyncio.run(check())

    def test_support_server_panel_still_works(self):
        async def check():
            interaction, cog = _interaction(SUPPORT_GUILD)
            await VoiceMasterInterface()._dispatch(interaction, "unlock")
            cog.unlock_channel.assert_awaited_once()
            self.assertIn("unlocked", interaction.response.texts.lower())

        asyncio.run(check())


async def _setup_pool():
    connection = await aiosqlite.connect(":memory:")
    await connection.executescript("""
        CREATE TABLE voicemaster_settings (
            guild_id INTEGER PRIMARY KEY, join_channel_id INTEGER, category_id INTEGER,
            default_name TEXT, default_limit INTEGER, default_bitrate INTEGER
        );
    """)
    await connection.commit()
    return connection, SQLitePool(connection)


def _setup_cog(pool):
    cog = VoiceMaster.__new__(VoiceMaster)
    cog.bot = SimpleNamespace(cxn=pool)
    cog._settings_cache = {}
    return cog


def _setup_context(guild_id=55, user_id=5):
    return SimpleNamespace(
        guild=SimpleNamespace(id=guild_id),
        author=SimpleNamespace(id=user_id, mention=f"<@{user_id}>"),
        prefix=".",
    )


def _setup_interaction(guild, *, user_id=5, manage_guild=True):
    response = SimpleNamespace(
        defer=AsyncMock(),
        edit_message=AsyncMock(),
        send_message=AsyncMock(),
    )
    interaction = SimpleNamespace(
        guild=guild,
        user=SimpleNamespace(id=user_id, mention=f"<@{user_id}>", guild_permissions=SimpleNamespace(manage_guild=manage_guild)),
        response=response,
    )
    interaction.edit_original_response = AsyncMock()
    return interaction


class _FakeVoiceChannel:
    """Stands in for `discord.VoiceChannel` in the select callback."""

    def __init__(self, channel_id, name, category):
        self.id = channel_id
        self.name = name
        self.category = category
        self.mention = f"<#{channel_id}>"


def _fake_voice_channel(channel_id, name, category):
    return _FakeVoiceChannel(channel_id, name, category)


class VoiceMasterSetupTests(unittest.TestCase):
    def test_create_option_builds_a_new_hub_and_saves_it(self):
        async def check():
            connection, pool = await _setup_pool()
            category = SimpleNamespace(id=301, name="Niko | VoiceMaster")
            channel = SimpleNamespace(id=302, mention="<#302>")
            guild = SimpleNamespace(
                id=55,
                create_category=AsyncMock(return_value=category),
                create_voice_channel=AsyncMock(return_value=channel),
            )
            cog = _setup_cog(pool)
            ctx = _setup_context()
            interaction = _setup_interaction(guild)

            await VoiceMasterSetupView(cog, ctx)._create_new_channel(interaction)

            guild.create_category.assert_awaited_once()
            self.assertEqual(guild.create_voice_channel.await_args.kwargs["category"], category)
            row = await pool.fetchrow("SELECT join_channel_id, category_id FROM voicemaster_settings WHERE guild_id = $1", 55)
            self.assertEqual((row["join_channel_id"], row["category_id"]), (302, 301))
            interaction.edit_original_response.assert_awaited_once()
            await connection.close()

        asyncio.run(check())

    def test_existing_channel_option_uses_the_selected_channel_and_its_category(self):
        async def check():
            connection, pool = await _setup_pool()
            category = SimpleNamespace(id=401, name="Lounge")
            channel = _fake_voice_channel(402, "Hangout", category)
            guild = SimpleNamespace(id=55, get_channel=lambda channel_id: channel if channel_id == 402 else None)
            cog = _setup_cog(pool)
            ctx = _setup_context()
            interaction = _setup_interaction(guild)
            select = VoiceMasterChannelSelect(cog, ctx, [channel])
            select._values = ["402"]

            with patch.object(voicemaster_module.discord, "VoiceChannel", _FakeVoiceChannel):
                await select.callback(interaction)

            row = await pool.fetchrow("SELECT join_channel_id, category_id FROM voicemaster_settings WHERE guild_id = $1", 55)
            self.assertEqual((row["join_channel_id"], row["category_id"]), (402, 401))
            interaction.edit_original_response.assert_awaited_once()
            await connection.close()

        asyncio.run(check())

    def test_select_options_list_guild_voice_channels(self):
        channel = _fake_voice_channel(402, "Hangout", SimpleNamespace(id=401, name="Lounge"))
        select = VoiceMasterChannelSelect(object(), _setup_context(), [channel])
        self.assertEqual([option.value for option in select.options], ["402"])
        self.assertIn("Lounge", select.options[0].description)

    def test_existing_option_without_channels_explains_itself(self):
        async def check():
            connection, pool = await _setup_pool()
            guild = SimpleNamespace(id=55, voice_channels=[])
            cog = _setup_cog(pool)
            interaction = _setup_interaction(guild)

            await VoiceMasterSetupView(cog, _setup_context())._choose_existing_channel(interaction)

            interaction.response.send_message.assert_awaited_once()
            self.assertTrue(interaction.response.send_message.await_args.kwargs["ephemeral"])
            await connection.close()

        asyncio.run(check())

    def test_setup_prompt_is_limited_to_the_invoking_member(self):
        async def check():
            connection, pool = await _setup_pool()
            view = VoiceMasterSetupView(_setup_cog(pool), _setup_context(user_id=5))
            other = _setup_interaction(SimpleNamespace(id=55), user_id=9)
            self.assertFalse(await view.interaction_check(other))
            other.response.send_message.assert_awaited_once()

            allowed = _setup_interaction(SimpleNamespace(id=55), user_id=5)
            self.assertTrue(await view.interaction_check(allowed))
            await connection.close()

        asyncio.run(check())


if __name__ == "__main__":
    unittest.main()
