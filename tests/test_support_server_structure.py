import asyncio
import json
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import aiosqlite
import discord
from discord.ext import commands

sys.path.insert(0, "src")

from cogs.staff import staff as staff_module
from cogs.staff.staff import StaffCog, _panel_channel_key, _save_support_panel_record, _save_voice_master_settings, _send_support_panels, _staff_rules_panel, _support_log_channels
from cogs.staff.support_server import CHANNEL_SPECS, CHANNEL_TOPICS, HELP_FORUM_TAGS, ROLE_SPECS, _create_stage_channel, _everyone_channel_overwrite, _move_channel_to_category_top, _sync_stage_category, assign_join_roles, assign_support_roles, create_support_invite, get_support_invite, persist_support_ids
from cogs.automod import mrbeast_scam
from database import MongoPool, SQLitePool


class SupportServerStructureTests(unittest.TestCase):
    def test_blueprint_contains_requested_channels_roles_and_descriptions(self):
        self.assertTrue({"owner", "staff", "supporter", "member", "announcements_ping", "events_ping", "community_ping", "polls_ping"} <= ROLE_SPECS.keys())
        self.assertEqual(ROLE_SPECS["owner"][0], "Niko Owner")
        self.assertTrue({"events", "event_chat", "polls", "help", "tickets", "logs", "automod_logs", "scam_review"} <= CHANNEL_SPECS.keys())
        self.assertEqual(CHANNEL_SPECS["help"][2], "forum")
        self.assertEqual(CHANNEL_SPECS["event_voice"][2], "stage")
        self.assertIn("giveaways", CHANNEL_SPECS)
        self.assertEqual(CHANNEL_SPECS["giveaways"][0], CHANNEL_SPECS["events"][0])
        self.assertTrue(all(name.istitle() or name == "Logs" for name in {spec[0] for spec in CHANNEL_SPECS.values()}))
        category_sizes = {}
        for category, _name, _kind, _staff_only in CHANNEL_SPECS.values():
            category_sizes[category] = category_sizes.get(category, 0) + 1
        self.assertTrue(all(size >= 3 for size in category_sizes.values()), category_sizes)
        self.assertEqual({tag.name for tag in HELP_FORUM_TAGS}, {"Bug", "Setup", "Account", "Feature request", "Solved"})
        self.assertTrue(all(not any(char.isupper() for char in category if char.isalpha()) for category in ()))
        self.assertEqual(CHANNEL_SPECS["polls"][0], CHANNEL_SPECS["announcements"][0])
        self.assertEqual(CHANNEL_SPECS["staff_rules"][0], "Staff")
        self.assertEqual(CHANNEL_SPECS["logs"][0], "Logs")
        self.assertEqual(CHANNEL_SPECS["member_logs"][0], "Logs")
        self.assertEqual(CHANNEL_SPECS["message_logs"][0], "Logs")
        self.assertEqual(CHANNEL_SPECS["channel_logs"][0], "Logs")
        self.assertEqual(set(CHANNEL_TOPICS), {key for key, spec in CHANNEL_SPECS.items() if spec[2] not in {"voice", "stage"}})
        self.assertNotIn("event_voice", CHANNEL_TOPICS)
        self.assertTrue(all(CHANNEL_TOPICS[key].strip() for key in CHANNEL_TOPICS))
        self.assertTrue(all(CHANNEL_SPECS[key][3] for key in ("staff_announcements", "staff_rules", "staff_chat", "staff_voice", "scam_review")))

    def test_poll_channel_is_read_only_for_members(self):
        overwrite = _everyone_channel_overwrite("polls", staff_only=False)
        self.assertFalse(overwrite.send_messages)
        self.assertTrue(overwrite.view_channel)
        self.assertTrue(overwrite.read_message_history)
        self.assertTrue(_everyone_channel_overwrite("announcements", False).send_messages is False)

    def test_stage_channel_speaking_is_limited_to_staff(self):
        self.assertFalse(_everyone_channel_overwrite("event_voice", False).speak)
        self.assertTrue(_everyone_channel_overwrite("general", False).speak)

    def test_stage_creation_uses_no_disallowed_permission_or_topic_arguments(self):
        async def check():
            guild = SimpleNamespace(create_stage_channel=AsyncMock(return_value="created"))
            result = await _create_stage_channel(guild, "Community Stage", SimpleNamespace(id=2))
            self.assertEqual(result, "created")
            kwargs = guild.create_stage_channel.await_args.kwargs
            self.assertEqual(set(kwargs), {"category", "reason"})
            self.assertNotIn("overwrites", kwargs)
            self.assertNotIn("topic", kwargs)
        asyncio.run(check())

    def test_stage_reconciliation_never_edits_channel_overwrites(self):
        async def check():
            category = SimpleNamespace(id=10)
            channel = SimpleNamespace(category_id=5, edit=AsyncMock())
            await _sync_stage_category(channel, category)
            channel.edit.assert_awaited_once_with(
                category=category,
                reason="Move Niko Stage into its configured category",
            )
            channel.category_id = category.id
            channel.edit.reset_mock()
            await _sync_stage_category(channel, category)
            channel.edit.assert_not_awaited()
        asyncio.run(check())

    def test_staff_rules_channel_is_moved_to_top_of_category(self):
        async def check():
            channel = SimpleNamespace(id=1, position=7, edit=AsyncMock())
            siblings = [SimpleNamespace(id=2, position=3), SimpleNamespace(id=3, position=5)]
            category = SimpleNamespace(channels=[*siblings, channel])
            await _move_channel_to_category_top(channel, category)
            channel.edit.assert_awaited_once_with(
                position=3,
                reason="Keep staff guidelines at the top of the staff category",
            )
        asyncio.run(check())

    def test_configure_support_systems_saves_distinct_log_channel_ids(self):
        async def check():
            import utils.onboarding.config as onboarding_config
            import utils.onboarding.utils as onboarding_utils
            import utils.tickets.utils as ticket_utils
            import cogs.logging.formatters as log_formatters

            saved = {}
            async def get_onboarding(_guild_id):
                return SimpleNamespace()
            async def update_onboarding(_guild_id, _config):
                return None
            async def load_logs():
                return {}
            async def save_logs(guild_id, config):
                saved.update(config)
            pool = SimpleNamespace(db_type="sqlite", fetchrow=AsyncMock(return_value={"guild_id": 1}))
            ticket_config = SimpleNamespace(panel_title="", panel_description="", panel_categories=[], support_roles=[], panel_channel_id=None, panel_message_id=None)
            channels = {"logs": 11, "automod_logs": 12, "member_logs": 13, "message_logs": 14, "channel_logs": 15, "scam_review": 16, "voice_join": 17, "tickets": 18, "welcome": 19}
            roles = {key: value for key, value in zip(("member", "staff", "head_admin", "moderator", "head_support", "support"), range(21, 27))}
            guild = SimpleNamespace(id=1, get_channel=lambda channel_id: SimpleNamespace(id=channel_id, category_id=20))
            bot = SimpleNamespace(cxn=object(), get_cog=lambda _name: None)
            with patch.object(onboarding_utils, "get_config", new=get_onboarding), \
                 patch.object(onboarding_utils, "update_config", new=update_onboarding), \
                 patch.object(onboarding_config, "_pool", return_value=pool), \
                 patch.object(ticket_utils, "get_ticket_config", return_value=ticket_config), \
                 patch.object(ticket_utils, "async_update_ticket_config", new=AsyncMock(return_value=True)), \
                 patch.object(log_formatters, "_load_log_config", new=load_logs), \
                 patch.object(log_formatters, "_save_guild_log_config", new=save_logs), \
                 patch("cogs.automod.mrbeast_scam.set_review_channel", new=AsyncMock()), \
                 patch.object(staff_module, "_save_voice_master_settings", new=AsyncMock()):
                await staff_module._configure_support_systems(bot, guild, roles, channels)
            self.assertEqual({key: saved[key] for key in ("moderation", "automod", "members", "messages", "channels")}, {
                "moderation": 11, "automod": 12, "members": 13, "messages": 14, "channels": 15,
            })
        asyncio.run(check())

    def test_support_log_groups_have_separate_destinations(self):
        channels = {"logs": 11, "automod_logs": 12, "member_logs": 13, "message_logs": 14, "channel_logs": 15}
        self.assertEqual(_support_log_channels(channels), {
            "moderation": 11, "automod": 12, "members": 13, "messages": 14, "channels": 15,
        })

    def test_staff_rules_panel_is_a_multi_section_cv2_handbook(self):
        view = _staff_rules_panel()
        text = "\n".join(item.content for item in view.walk_children() if isinstance(item, discord.ui.TextDisplay))
        self.assertIn("Our purpose", text)
        self.assertIn("Member support", text)
        self.assertIn("Moderation & safety", text)
        self.assertIn("Confidentiality & representation", text)
        self.assertIn("Team conduct", text)
        self.assertGreaterEqual(sum(isinstance(item, discord.ui.Separator) for item in view.walk_children()), 1)

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

    def test_support_setup_upserts_all_existing_sqlite_rows(self):
        async def check():
            connection = await aiosqlite.connect(":memory:")
            await connection.executescript("""
                CREATE TABLE support_server_config (
                    guild_id INTEGER PRIMARY KEY, role_ids TEXT, channel_ids TEXT,
                    invite_url TEXT, updated_at TEXT
                );
                CREATE TABLE support_server_panels (
                    guild_id INTEGER, panel_key TEXT, channel_id INTEGER,
                    message_id INTEGER, updated_at TEXT, PRIMARY KEY (guild_id, panel_key)
                );
                CREATE TABLE voicemaster_settings (
                    guild_id INTEGER PRIMARY KEY, join_channel_id INTEGER, category_id INTEGER,
                    default_name TEXT, default_limit INTEGER, default_bitrate INTEGER
                );
            """)
            await connection.commit()
            pool = SQLitePool(connection)
            guild_id = staff_module.SUPPORT_GUILD
            bot = SimpleNamespace(cxn=pool)
            guild = SimpleNamespace(id=guild_id, get_channel=lambda _: SimpleNamespace(id=31, create_invite=AsyncMock(return_value=SimpleNamespace(url="https://discord.gg/sqlite"))))

            await persist_support_ids(bot, guild, {"staff": 12}, {"welcome": 21})
            invite = await create_support_invite(bot, guild, {"welcome": 31, "general": 32})
            original_review_channel = mrbeast_scam.SCAM_REVIEW_CHANNEL
            await mrbeast_scam.set_review_channel(bot, 41)
            mrbeast_scam.SCAM_REVIEW_CHANNEL = original_review_channel
            await _save_support_panel_record(pool, guild_id, "welcome", 31, 51)
            await _save_support_panel_record(pool, guild_id, "welcome", 32, 52)
            await _save_voice_master_settings(pool, guild_id, 61, 62)
            await _save_voice_master_settings(pool, guild_id, 63, 64)

            config = await pool.fetchrow("SELECT role_ids, channel_ids, invite_url FROM support_server_config WHERE guild_id = $1", guild_id)
            panel = await pool.fetchrow("SELECT channel_id, message_id FROM support_server_panels WHERE guild_id = $1 AND panel_key = $2", guild_id, "welcome")
            voice = await pool.fetchrow("SELECT join_channel_id, category_id FROM voicemaster_settings WHERE guild_id = $1", guild_id)
            self.assertEqual(json.loads(config["role_ids"]), {"staff": 12})
            self.assertEqual(json.loads(config["channel_ids"]), {"welcome": 21, "scam_review": 41})
            self.assertEqual(config["invite_url"], invite)
            self.assertEqual((panel["channel_id"], panel["message_id"]), (32, 52))
            self.assertEqual((voice["join_channel_id"], voice["category_id"]), (63, 64))
            await connection.close()

        asyncio.run(check())

    def test_send_support_panels_updates_ticket_message_config(self):
        async def check():
            import cogs.tickets.views as ticket_views
            import cogs.voicemaster.cog as voice_cog_module
            import utils.tickets.utils as ticket_utils

            class FakeForumChannel(discord.ForumChannel):
                pass

            ticket_cfg = SimpleNamespace(panel_channel_id=None, panel_message_id=None)
            message = SimpleNamespace(id=9876, channel=SimpleNamespace(id=8765))
            class FakeTicketPanelView:
                def __init__(self, guild_id, cfg):
                    self.guild_id = guild_id
                    self.cfg = cfg
            class FakeVoiceMasterInterface:
                pass
            channels = {key: index for index, key in enumerate(("status", "rules", "staff_rules", "staff_announcements", "welcome", "roles", "tickets", "voice_panel", "help"), 100)}
            pool = SimpleNamespace(fetchrow=AsyncMock(return_value=None), execute=AsyncMock())
            panel_calls = []
            class FlexibleGuild:
                id = 44
                def get_channel(self, channel_id):
                    if channel_id == channels["help"]:
                        forum = object.__new__(FakeForumChannel)
                        forum.id = channel_id
                        forum.create_thread = AsyncMock(return_value=SimpleNamespace(message=SimpleNamespace(pin=AsyncMock()), thread=SimpleNamespace(id=7788, edit=AsyncMock())))
                        return forum
                    if channel_id == channels["tickets"]:
                        return SimpleNamespace(id=channel_id, send=AsyncMock(return_value=message), get_partial_message=lambda _: SimpleNamespace(delete=AsyncMock()))
                    return SimpleNamespace(id=channel_id, send=AsyncMock(return_value=message), get_partial_message=lambda _: SimpleNamespace(delete=AsyncMock()))
                def get_thread(self, _thread_id):
                    return None
            bot = SimpleNamespace(
                cxn=pool,
                add_view=Mock(),
            )
            async def update_config(guild_id, cfg):
                panel_calls.append((guild_id, cfg.panel_channel_id, cfg.panel_message_id))
                return True
            with patch.object(ticket_views, "TicketPanelView", FakeTicketPanelView), \
                 patch.object(voice_cog_module, "VoiceMasterInterface", FakeVoiceMasterInterface), \
                 patch.object(ticket_utils, "get_ticket_config", return_value=ticket_cfg), \
                 patch.object(ticket_utils, "async_update_ticket_config", new=update_config), \
                 patch("cogs.staff.owner._collect_status", new=AsyncMock(return_value={})), \
                 patch("cogs.staff.owner._build_status_panel", return_value=object()), \
                 patch("cogs.staff.owner._build_rules_panel", return_value=object()), \
                 patch("cogs.staff.staff._staff_rules_panel", return_value=object()), \
                 patch.object(staff_module, "SupportPingPanel", return_value=object()), \
                 patch("cogs.staff.staff._support_api_pause", new=AsyncMock()):
                await _send_support_panels(
                    bot,
                    FlexibleGuild(),
                    {},
                    channels,
                )
            self.assertEqual(ticket_cfg.panel_channel_id, message.channel.id)
            self.assertEqual(ticket_cfg.panel_message_id, message.id)
            self.assertEqual(panel_calls, [(44, message.channel.id, message.id)])

        asyncio.run(check())

    def test_panel_channel_default_is_resolved_at_call_time(self):
        self.assertEqual(_panel_channel_key("welcome"), "welcome")
        self.assertEqual(_panel_channel_key("tickets", "support"), "support")

    def test_support_role_sync_assigns_owner_role_to_configured_owner(self):
        async def check():
            from config.ids import OWNER_IDS
            owner_id = next(iter(OWNER_IDS))
            owner_role = SimpleNamespace(id=77)
            base_role = SimpleNamespace(id=78)
            staff_role = SimpleNamespace(id=79)
            member = SimpleNamespace(id=owner_id, roles=[], add_roles=AsyncMock())
            async def fetch_members(limit=None):
                yield member
            guild = SimpleNamespace(
                members=[member],
                fetch_members=fetch_members,
                get_role=lambda role_id: {77: owner_role, 78: base_role, 79: staff_role}.get(role_id),
            )
            pool = SimpleNamespace(fetch=AsyncMock(return_value=[]))
            bot = SimpleNamespace(cxn=pool, user=SimpleNamespace(id=999))
            with patch("utils.donations.is_supporter", new=AsyncMock(return_value=False)):
                await assign_support_roles(bot, guild, {"owner": 77, "member": 78, "staff": 79})
            member.add_roles.assert_awaited()
            assigned_ids = {role.id for call in member.add_roles.await_args_list for role in call.args}
            self.assertTrue({base_role.id, owner_role.id, staff_role.id} <= assigned_ids)
        asyncio.run(check())

    def test_joining_configured_bot_owner_gets_owner_role(self):
        async def check():
            from config.ids import OWNER_IDS
            owner_id = next(iter(OWNER_IDS))
            owner_role = SimpleNamespace(id=77)
            member_role = SimpleNamespace(id=78)
            member = SimpleNamespace(
                id=owner_id,
                guild=SimpleNamespace(id=staff_module.SUPPORT_GUILD, get_role=lambda role_id: {77: owner_role, 78: member_role}.get(role_id)),
                roles=[],
                add_roles=AsyncMock(),
            )
            bot = SimpleNamespace(cxn=None)
            await assign_join_roles(bot, member, {"owner": 77, "member": 78})
            assigned_ids = {role.id for call in member.add_roles.await_args_list for role in call.args}
            self.assertTrue({owner_role.id, member_role.id} <= assigned_ids)
        asyncio.run(check())

    def test_mongodb_support_config_upserts_accept_conflict_assignments(self):
        class Collection:
            def __init__(self):
                self.update_one = AsyncMock(return_value=SimpleNamespace(upserted_id=None))

        class Database:
            def __init__(self):
                self.collections = {}

            def __getitem__(self, name):
                return self.collections.setdefault(name, Collection())

        class Client:
            def __init__(self):
                self.database = Database()

            def __getitem__(self, _name):
                return self.database

        async def check():
            client = Client()
            pool = MongoPool(client, "test")
            guild_id = staff_module.SUPPORT_GUILD
            await pool.execute(
                "INSERT INTO support_server_config (guild_id, role_ids, channel_ids, updated_at) VALUES ($1, $2, $3, datetime('now')) "
                "ON CONFLICT (guild_id) DO UPDATE SET role_ids = $4, channel_ids = $5, updated_at = datetime('now')",
                guild_id, '{"staff":1}', '{"welcome":2}', '{"staff":3}', '{"welcome":4}',
            )
            config_calls = client.database["support_server_config"].update_one.await_args_list
            self.assertEqual(config_calls[0].args[0], {"_id": guild_id})
            self.assertEqual(config_calls[1].args[1]["$set"]["role_ids"], '{"staff":3}')
            self.assertEqual(config_calls[1].args[1]["$set"]["channel_ids"], '{"welcome":4}')
            self.assertIn("updated_at", config_calls[1].args[1]["$set"])

            await pool.execute(
                "INSERT INTO support_server_panels (guild_id, panel_key, channel_id, message_id, updated_at) VALUES ($1, $2, $3, $4, datetime('now')) "
                "ON CONFLICT (guild_id, panel_key) DO UPDATE SET channel_id = $5, message_id = $6, updated_at = datetime('now')",
                guild_id, "welcome", 31, 51, 32, 52,
            )
            panel_calls = client.database["support_server_panels"].update_one.await_args_list
            self.assertEqual(panel_calls[0].args[0], {"_id": f"{guild_id}_welcome"})
            self.assertEqual(panel_calls[1].args[1]["$set"]["channel_id"], 32)
            self.assertEqual(panel_calls[1].args[1]["$set"]["message_id"], 52)
            self.assertIn("updated_at", panel_calls[1].args[1]["$set"])

        asyncio.run(check())

    def test_invite_reader_uses_saved_database_url(self):
        async def check():
            pool = SimpleNamespace(fetchrow=AsyncMock(return_value={"invite_url": "https://discord.gg/saved"}))
            self.assertEqual(await get_support_invite(SimpleNamespace(cxn=pool)), "https://discord.gg/saved")
        asyncio.run(check())


if __name__ == "__main__":
    unittest.main()
