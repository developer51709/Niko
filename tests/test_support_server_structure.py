import asyncio
import json
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import aiosqlite
import discord
from discord.ext import commands

sys.path.insert(0, "src")

from cogs.staff import staff as staff_module
from cogs.staff.staff import StaffCog
from cogs.staff.support_server import CHANNEL_SPECS, CHANNEL_TOPICS, ROLE_SPECS, create_support_invite, get_support_invite, persist_support_ids
from database import SQLitePool


class SupportServerStructureTests(unittest.TestCase):
    def test_blueprint_contains_requested_channels_roles_and_descriptions(self):
        self.assertTrue({"staff", "supporter", "member", "announcements_ping", "events_ping", "community_ping", "polls_ping"} <= ROLE_SPECS.keys())
        self.assertTrue({"events", "event_chat", "polls", "help", "tickets", "logs", "automod_logs", "scam_review"} <= CHANNEL_SPECS.keys())
        self.assertEqual(CHANNEL_SPECS["help"][2], "forum")
        self.assertEqual(set(CHANNEL_TOPICS), {key for key, spec in CHANNEL_SPECS.items() if spec[2] != "voice"})
        self.assertTrue(all(CHANNEL_TOPICS[key].strip() for key in CHANNEL_TOPICS))
        self.assertTrue(all(CHANNEL_SPECS[key][3] for key in ("staff_announcements", "staff_rules", "staff_chat", "staff_voice", "scam_review")))

    def test_support_commands_are_private_and_owner_only(self):
        async def check():
            bot = commands.Bot(command_prefix=".", intents=discord.Intents.none())
            await bot.add_cog(StaffCog(bot))
            group = bot.get_command("staff")
            for name in ("supportsetup", "supportupdate"):
                command = group.get_command(name)
                self.assertTrue(command.hidden)
                self.assertTrue(command.checks)
            await bot.close()
        asyncio.run(check())

    def test_confirmed_rebuild_runs_full_orchestration_after_dm_and_preflight(self):
        async def check():
            author = SimpleNamespace(id=123, send=AsyncMock(return_value=SimpleNamespace(edit=AsyncMock())))
            bot = SimpleNamespace()
            response = SimpleNamespace(edit=AsyncMock())
            async def send(*, view=None, **kwargs):
                if view is not None:
                    confirm = next(item for item in view.walk_children() if isinstance(item, discord.ui.Button) and item.label == "Rebuild server")
                    interaction = SimpleNamespace(user=author, response=SimpleNamespace(edit_message=AsyncMock()))
                    await confirm.callback(interaction)
                    self.assertNotIn("content", interaction.response.edit_message.await_args.kwargs)
                return response
            ctx = SimpleNamespace(author=author, bot=bot, guild=SimpleNamespace(id=staff_module.SUPPORT_GUILD), send=send)
            cog = SimpleNamespace(bot=bot)
            operations = []
            async def preflight(guild): operations.append("preflight")
            async def reconcile(guild, *, destructive=False):
                operations.append("reconcile")
                self.assertTrue(destructive)
                return ({"staff": 1}, {"welcome": 2})
            async def persist(*args): operations.append("persist")
            async def invite(*args): operations.append("invite"); return "https://discord.gg/fresh"
            async def configure(*args): operations.append("configure")
            async def panels(*args, **kwargs): operations.append("panels")
            async def roles(*args): operations.append("roles")
            with patch.object(discord.ui.LayoutView, "wait", new=AsyncMock(return_value=False)), \
                 patch.object(staff_module, "_is_owner_user", return_value=True), \
                 patch.object(staff_module, "bot_member_preflight", new=preflight), \
                 patch.object(staff_module, "reconcile_structure", new=reconcile), \
                 patch.object(staff_module, "persist_support_ids", new=persist), \
                 patch.object(staff_module, "create_support_invite", new=invite), \
                 patch.object(staff_module, "_configure_support_systems", new=configure), \
                 patch.object(staff_module, "_send_support_panels", new=panels), \
                 patch.object(staff_module, "assign_support_roles", new=roles):
                await StaffCog.support_setup.callback(cog, ctx)
            self.assertEqual(operations, ["preflight", "reconcile", "persist", "invite", "configure", "panels", "roles"])
            author.send.assert_awaited()
            self.assertIn("rebuilt", author.send.return_value.edit.await_args.kwargs["content"].lower())
        asyncio.run(check())

    def test_dm_failure_stops_before_destructive_work(self):
        async def check():
            author = SimpleNamespace(id=123, send=AsyncMock(side_effect=discord.Forbidden(response=SimpleNamespace(status=403, reason="Forbidden"), message="DM disabled")))
            response = SimpleNamespace(edit=AsyncMock())
            async def send(*, view=None, **kwargs):
                if view is not None:
                    confirm = next(item for item in view.walk_children() if isinstance(item, discord.ui.Button) and item.label == "Rebuild server")
                    await confirm.callback(SimpleNamespace(user=author, response=SimpleNamespace(edit_message=AsyncMock())))
                return response
            ctx = SimpleNamespace(author=author, bot=SimpleNamespace(), guild=SimpleNamespace(id=staff_module.SUPPORT_GUILD), send=send)
            cog = SimpleNamespace(bot=ctx.bot)
            with patch.object(discord.ui.LayoutView, "wait", new=AsyncMock(return_value=False)), \
                 patch.object(staff_module, "_is_owner_user", return_value=True), \
                 patch.object(staff_module, "bot_member_preflight", new=AsyncMock()) as preflight, \
                 patch.object(staff_module, "reconcile_structure", new=AsyncMock()) as reconcile:
                await StaffCog.support_setup.callback(cog, ctx)
            preflight.assert_not_awaited()
            reconcile.assert_not_awaited()
            view = response.edit.await_args.kwargs["view"]
            display = next(component for component in view.walk_children() if isinstance(component, discord.ui.TextDisplay))
            self.assertIn("not started", display.content)
        asyncio.run(check())

    def test_invite_refresh_persists_url_and_preserves_existing_ids(self):
        async def check():
            pool = SimpleNamespace(fetchrow=AsyncMock(return_value={"role_ids": '{"staff":12}', "channel_ids": '{"polls":44}'}), execute=AsyncMock())
            channel = SimpleNamespace(id=11, create_invite=AsyncMock(return_value=SimpleNamespace(url="https://discord.gg/current")))
            guild = SimpleNamespace(id=staff_module.SUPPORT_GUILD, get_channel=lambda _: channel)
            url = await create_support_invite(SimpleNamespace(cxn=pool), guild, {"welcome": 11, "general": 22})
            self.assertEqual(url, "https://discord.gg/current")
            args = pool.execute.await_args.args
            self.assertEqual(json.loads(args[2]), {"staff": 12})
            self.assertEqual(json.loads(args[3]), {"polls": 44, "welcome": 11, "general": 22})
            self.assertEqual(args[4], url)
            pool.execute.assert_awaited_once()
        asyncio.run(check())

    def test_persist_support_ids_updates_existing_sqlite_record(self):
        async def check():
            connection = await aiosqlite.connect(":memory:")
            await connection.execute(
                "CREATE TABLE support_server_config (guild_id INTEGER PRIMARY KEY, role_ids TEXT, channel_ids TEXT, updated_at TEXT)"
            )
            await connection.commit()
            pool = SQLitePool(connection)
            bot = SimpleNamespace(cxn=pool)
            guild = SimpleNamespace(id=staff_module.SUPPORT_GUILD)

            await persist_support_ids(bot, guild, {"staff": 12}, {"welcome": 21})
            await persist_support_ids(bot, guild, {"staff": 13}, {"welcome": 22, "rules": 23})

            row = await pool.fetchrow(
                "SELECT role_ids, channel_ids FROM support_server_config WHERE guild_id = $1",
                guild.id,
            )
            self.assertEqual(json.loads(row["role_ids"]), {"staff": 13})
            self.assertEqual(json.loads(row["channel_ids"]), {"welcome": 22, "rules": 23})
            await connection.close()

        asyncio.run(check())

    def test_invite_reader_uses_saved_database_url(self):
        async def check():
            pool = SimpleNamespace(fetchrow=AsyncMock(return_value={"invite_url": "https://discord.gg/saved"}))
            self.assertEqual(await get_support_invite(SimpleNamespace(cxn=pool)), "https://discord.gg/saved")
        asyncio.run(check())


if __name__ == "__main__":
    unittest.main()
