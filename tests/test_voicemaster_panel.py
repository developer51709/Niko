import asyncio
import json
import string
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import aiosqlite
import discord
from discord.ext import commands

sys.path.insert(0, "src")

import cogs.voicemaster.cog as voicemaster_module
from config.ids import SUPPORT_GUILD
from cogs.voicemaster import messages as vm_messages
from utils.locales import load_locales

#: Command wording lives in the ``commands`` namespace every cog shares.
COMMAND_CATALOGUE = load_locales("cogs.voicemaster", "commands")
from cogs.voicemaster.cog import VoiceMaster, VoiceMasterChannelSelect, VoiceMasterInterface, VoiceMasterSetupView
from database import SQLitePool


def _view_text(view) -> str:
    """Every text display and button label rendered by a components v2 view."""
    parts = []
    for child in view.walk_children():
        text = getattr(child, "content", None) or getattr(child, "label", None)
        if text:
            parts.append(str(text))
    return "\n".join(parts)


def _localized_ctx(locale: str, *, user_id: int = 5):
    """A command context whose guild prefers ``locale``."""
    ctx = SimpleNamespace(
        guild=SimpleNamespace(id=55, preferred_locale=locale),
        author=SimpleNamespace(
            id=user_id,
            voice=SimpleNamespace(channel=SimpleNamespace(id=22)),
        ),
        replies=[],
    )

    async def reply(*, view=None, **_kwargs):
        ctx.replies.append(view)

    ctx.reply = reply
    return ctx


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


class VoiceMasterLocalizationTests(unittest.TestCase):
    def test_german_spanish_and_french_translations_are_resolved(self):
        self.assertEqual(vm_messages.text("de", "locked"), "Sprachkanal gesperrt.")
        self.assertEqual(vm_messages.text("es", "locked"), "Canal de voz bloqueado.")
        self.assertEqual(vm_messages.text("fr", "locked"), "Salon vocal verrouillé.")

    def test_an_unsupported_language_falls_back_to_english(self):
        # Italian ships no catalogue, so it takes the English wording.
        self.assertEqual(vm_messages.text("it", "locked"), "Voice channel locked.")

    def test_an_unknown_key_falls_back_to_the_key_itself(self):
        self.assertEqual(vm_messages.text("de", "not_a_real_key"), "not_a_real_key")

    def test_every_language_translates_every_key(self):
        english = set(vm_messages.MESSAGES["en"])
        for lang in ("de", "es"):
            self.assertEqual(
                english - set(vm_messages.MESSAGES[lang]), set(),
                f"{lang} is missing translations",
            )

    def test_translations_keep_the_english_placeholders(self):
        def fields(template):
            return {
                name for _, name, _, _ in string.Formatter().parse(template) if name
            }

        for key, template in vm_messages.MESSAGES["en"].items():
            for lang in ("de", "es"):
                self.assertEqual(
                    fields(vm_messages.MESSAGES[lang][key]),
                    fields(template),
                    f"{lang}:{key} changes the placeholders",
                )

    def test_the_control_panel_renders_in_the_requested_language(self):
        german = _view_text(VoiceMasterInterface("de"))
        spanish = _view_text(VoiceMasterInterface("es"))

        self.assertIn("den Sprachkanal", german)
        self.assertIn("el canal de voz", spanish)
        # The command names stay literal so the legend still matches the buttons.
        self.assertIn("`Lock`", german)
        self.assertIn("`Lock`", spanish)

    def test_panel_actions_reply_in_the_interaction_language(self):
        async def check():
            interaction, cog = _interaction(987654321)
            interaction.guild = SimpleNamespace(
                id=987654321, preferred_locale="de-DE"
            )

            await VoiceMasterInterface()._dispatch(interaction, "lock")

            cog.lock_channel.assert_awaited_once()
            self.assertIn("Sprachkanal gesperrt", interaction.response.texts)

        asyncio.run(check())

    def test_commands_reply_in_the_guild_language(self):
        async def check():
            cog = VoiceMaster.__new__(VoiceMaster)
            cog.bot = SimpleNamespace()
            cog.is_channel_owner = AsyncMock(return_value=True)
            cog.lock_channel = AsyncMock()
            ctx = _localized_ctx("es-ES")

            await VoiceMaster.lock.callback(cog, ctx)

            self.assertIn("Canal de voz bloqueado", _view_text(ctx.replies[-1]))

        asyncio.run(check())

    def test_command_errors_are_localized_too(self):
        async def check():
            cog = VoiceMaster.__new__(VoiceMaster)
            cog.bot = SimpleNamespace()
            cog.is_channel_owner = AsyncMock(return_value=False)
            ctx = _localized_ctx("de-DE")

            await VoiceMaster.lock.callback(cog, ctx)

            self.assertIn("Du besitzt diesen Sprachkanal nicht", _view_text(ctx.replies[-1]))

        asyncio.run(check())

    def test_the_setup_prompt_follows_the_guild_language(self):
        ctx = _localized_ctx("de-DE")

        view = VoiceMasterSetupView(
            object(), ctx, SimpleNamespace(mention="<#1>")
        )
        text = _view_text(view)

        self.assertIn("VoiceMaster Einrichtung", text)
        self.assertIn("Neuen Kanal erstellen", text)
        self.assertIn("Vorhandenen Kanal verwenden", text)
        self.assertIn("VoiceMaster verwendet derzeit", text)

    def test_the_channel_picker_labels_follow_the_guild_language(self):
        ctx = _localized_ctx("es-ES")
        channel = _fake_voice_channel(
            402, "Hangout", SimpleNamespace(id=401, name="Lounge")
        )

        select = VoiceMasterChannelSelect(object(), ctx, [channel])

        self.assertEqual(select.placeholder, "Selecciona el canal de voz a usar...")
        self.assertEqual(select.options[0].description, "Categoría: Lounge")

    def test_the_setup_confirmation_follows_the_guild_language(self):
        view = voicemaster_module._setup_success_view(
            SimpleNamespace(mention="<#302>"),
            SimpleNamespace(name="Lounge"),
            ".",
            SimpleNamespace(guild=SimpleNamespace(id=1, preferred_locale="es")),
        )

        text = _view_text(view)

        self.assertIn("Configuración de VoiceMaster completada", text)
        self.assertIn("Canal de entrada", text)
        self.assertIn("Categoría", text)

    def test_the_channel_card_labels_follow_the_guild_language(self):
        async def check():
            cog = VoiceMaster.__new__(VoiceMaster)
            cog.bot = SimpleNamespace(
                cxn=SimpleNamespace(fetchval=AsyncMock(return_value=None))
            )
            channel = SimpleNamespace(
                id=22,
                name="Lounge",
                members=[],
                user_limit=0,
                bitrate=64000,
                rtc_region=None,
                guild=SimpleNamespace(
                    get_member=lambda _id: None, default_role=object()
                ),
                overwrites_for=lambda _role: SimpleNamespace(
                    connect=True, view_channel=True
                ),
            )
            ctx = SimpleNamespace(
                guild=SimpleNamespace(id=1, preferred_locale="de")
            )

            text = _view_text(await cog.get_channel_info(channel, ctx))

            self.assertIn("Mitglieder", text)
            self.assertIn("Kein Limit", text)
            self.assertIn("Automatisch", text)
            self.assertIn("Offen", text)

        asyncio.run(check())


class VoiceMasterCommandMetadataTests(unittest.TestCase):
    """The help entry the help menu and the dashboard commands page read."""

    def _commands(self):
        found = []

        def walk(command):
            found.append(command)
            for sub in getattr(command, "commands", []):
                walk(sub)

        for attribute in dir(VoiceMaster):
            command = getattr(VoiceMaster, attribute)
            if isinstance(command, commands.Command) and command.parent is None:
                walk(command)
        return found

    def _help_key(self, command):
        return f"{command.qualified_name.replace(' ', '.')}.help"

    def _parameters(self, command):
        params = getattr(command, "parameters", None)
        if params is None:
            params = getattr(command, "clean_params", {}).values()
        return [parameter for parameter in params if getattr(parameter, "name", None)]

    def test_every_command_help_has_all_three_languages(self):
        commands_seen = self._commands()
        self.assertTrue(commands_seen)

        for command in commands_seen:
            parsed = json.loads(str(command.help))
            self.assertEqual(set(parsed), {"en", "de", "es", "fr"}, command.qualified_name)
            self.assertTrue(all(parsed.values()), command.qualified_name)

    def test_every_command_help_matches_the_locale_catalog(self):
        for command in self._commands():
            key = self._help_key(command)
            self.assertIn(key, COMMAND_CATALOGUE["en"], command.qualified_name)
            parsed = json.loads(str(command.help))
            for lang in ("en", "de", "es", "fr"):
                self.assertEqual(
                    parsed[lang], COMMAND_CATALOGUE[lang][key],
                    f"{lang}:{key} drifted from the catalog",
                )

    def test_every_argument_has_a_description_for_the_commands_page(self):
        for command in self._commands():
            for parameter in self._parameters(command):
                self.assertTrue(
                    str(getattr(parameter, "description", "") or "").strip(),
                    f"{command.qualified_name} {parameter.name} has no description",
                )

    def test_the_help_menu_reads_the_localized_help(self):
        parsed = json.loads(str(VoiceMaster.lock.help))

        self.assertEqual(parsed["en"], "Lock your voice channel so nobody else can join")
        self.assertEqual(parsed["de"], "Sperrt deinen Sprachkanal für andere")
        self.assertIn("Bloquea", parsed["es"])


if __name__ == "__main__":
    unittest.main()
