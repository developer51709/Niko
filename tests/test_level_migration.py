"""Leveling import offered in the join DM.

The import reaches into two public leaderboard endpoints, so these checks pin the
pagination, the response shapes, the XP conversion (Niko stores progress inside
the current level, MEE6 reports a lifetime total) and the rule that an import
never pushes a member who is already further along in Niko back down.
"""

import asyncio
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import discord

from cogs.leveling import migration
from cogs.leveling.cog import Leveling

BOT_ID = 999


def xp_for_level(level):
    """Niko's per-level requirement, as the bound cog method sees it."""
    return Leveling.get_xp_for_level(None, level)


class FakeResponse:
    def __init__(self, status, payload):
        self.status = status
        self._payload = payload

    async def json(self, content_type=None):
        return self._payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return False


class FakeSession:
    closed = False

    def __init__(self, pages, status=200):
        self._pages = list(pages)
        self._status = status
        self.requests = []
        self.headers = []

    def get(self, url, params=None, headers=None, timeout=None):
        self.requests.append((url, dict(params or {})))
        self.headers.append(headers)
        payload = self._pages.pop(0) if self._pages else {}
        return FakeResponse(self._status, payload)


class FakeMember:
    def __init__(self, member_id):
        self.id = member_id


class FakeGuild:
    def __init__(self, member_ids):
        self.id = 42
        self._members = {member_id: FakeMember(member_id) for member_id in member_ids}

    def get_member(self, member_id):
        return self._members.get(int(member_id))


MEE6 = migration.PROVIDERS["mee6"]["bot_id"]
AMARIBOT = migration.PROVIDERS["amaribot"]["bot_id"]
LURKR = migration.PROVIDERS["lurkr"]["bot_id"]


def with_key(key):
    """Set (or blank) the deployment-wide AmariBot key for one check."""
    return mock.patch.dict(os.environ, {migration.AMARIBOT_KEY_ENV: key})


class DetectionTests(unittest.TestCase):
    def test_detects_a_supported_leveling_bot(self):
        self.assertEqual(migration.detect_provider(FakeGuild([MEE6, 1])), "mee6")
        self.assertEqual(migration.detect_provider(FakeGuild([LURKR])), "lurkr")

    def test_amaribot_is_only_offered_without_a_key(self):
        with with_key(""):
            self.assertIsNone(migration.detect_provider(FakeGuild([AMARIBOT])))
        with with_key("amari-key"):
            self.assertEqual(migration.detect_provider(FakeGuild([AMARIBOT])), "amaribot")

    def test_mee6_still_wins_when_both_are_present(self):
        with with_key("amari-key"):
            self.assertEqual(
                migration.detect_provider(FakeGuild([AMARIBOT, MEE6])), "mee6")

    def test_ignores_servers_without_one(self):
        with with_key("amari-key"):
            self.assertIsNone(migration.detect_provider(FakeGuild([1, 2, 3])))
            self.assertIsNone(migration.detect_provider(None))

    def test_settings_link_points_at_the_guilds_leveling_page(self):
        self.assertTrue(migration.settings_url(42).endswith("/dashboard/42/leveling"))


class ProgressConversionTests(unittest.TestCase):
    xp_for_level = staticmethod(xp_for_level)

    def convert(self, level, xp, *, cumulative):
        return migration.import_progress(
            level, xp, cumulative=cumulative, xp_for_level=self.xp_for_level)

    def test_mee6_lifetime_xp_is_reduced_to_the_current_level(self):
        # MEE6 uses the same per-level curve; the completed levels are spent.
        spent = sum(self.xp_for_level(level) for level in range(5))
        self.assertEqual(self.convert(5, spent + 40, cumulative=True), (5, 40))

    def test_lurkr_progress_is_already_in_level(self):
        self.assertEqual(self.convert(5, 40, cumulative=False), (5, 40))

    def test_amaribot_uses_the_same_lifetime_xp_as_mee6(self):
        spent = sum(self.xp_for_level(level) for level in range(5))
        self.assertTrue(migration.PROVIDERS["amaribot"]["cumulative_xp"])
        self.assertEqual(self.convert(5, spent + 40, cumulative=True), (5, 40))

    def test_leftover_progress_is_clamped_to_the_level(self):
        self.assertEqual(
            self.convert(5, 10 ** 9, cumulative=False),
            (5, self.xp_for_level(5) - 1),
        )

    def test_import_never_moves_someone_backwards(self):
        self.assertTrue(migration.imported_wins(6, 0, None))
        self.assertTrue(migration.imported_wins(6, 0, (5, 99)))
        self.assertTrue(migration.imported_wins(6, 50, (6, 10)))
        self.assertFalse(migration.imported_wins(6, 10, (6, 50)))
        self.assertFalse(migration.imported_wins(5, 99, (6, 0)))


class FetchTests(unittest.TestCase):
    def test_mee6_pages_from_zero_until_an_empty_page(self):
        first = [
            {"id": str(user_id), "level": 3, "xp": 120}
            for user_id in range(1, 1001)
        ]
        # The second page is shorter than requested because MEE6 capped it; it
        # must not end the import while more rows are still available.
        second = [
            {"id": str(user_id), "level": 4, "xp": 5}
            for user_id in range(1001, 1076)
        ]
        session = FakeSession([
            {"players": first},
            {"players": second},
            {"players": []},
        ])
        with mock.patch.dict(migration.PROVIDERS["mee6"], {"delay": 0}):
            rows = asyncio.run(migration.fetch_leaderboard(42, "mee6", session))

        self.assertEqual(len(rows), 1075)
        self.assertEqual(rows[-1], {"user_id": 1075, "level": 4, "xp": 5})
        self.assertEqual(
            [params["page"] for _, params in session.requests], [0, 1, 2])
        self.assertEqual(session.requests[0][1]["limit"], 1000)
        self.assertIn("/leaderboard/42", session.requests[0][0])

    def test_lurkr_pages_from_one_without_a_limit(self):
        session = FakeSession([
            {"levels": [{"userId": "7", "level": 2, "xp": 15}]},
        ])
        rows = asyncio.run(migration.fetch_leaderboard(42, "lurkr", session))

        self.assertEqual(rows, [{"user_id": 7, "level": 2, "xp": 15}])
        self.assertEqual(session.requests[0][1], {"page": 1})
        self.assertIn("api.lurkr.gg/v2/levels/42", session.requests[0][0])

    def test_amaribot_sends_the_key_and_reads_exp_from_page_one(self):
        session = FakeSession([
            {"data": [{"id": "7", "level": 3, "exp": 475}], "count": 1,
             "total_count": 1},
            {"data": []},
        ])
        with with_key("amari-key"), mock.patch.dict(
            migration.PROVIDERS["amaribot"], {"delay": 0}
        ):
            rows = asyncio.run(migration.fetch_leaderboard(42, "amaribot", session))

        self.assertEqual(rows, [{"user_id": 7, "level": 3, "xp": 475}])
        self.assertEqual(session.requests[0][1], {"page": 1, "limit": 1000})
        self.assertEqual(session.headers[0], {"Authorization": "amari-key"})
        self.assertIn("amaribot.com/api/v1/guild/leaderboard/42", session.requests[0][0])

    def test_a_keyless_provider_sends_no_authorization(self):
        session = FakeSession([{"levels": []}])
        asyncio.run(migration.fetch_leaderboard(42, "lurkr", session))
        self.assertIsNone(session.headers[0])

    def test_broken_rows_are_dropped(self):
        session = FakeSession([
            {"levels": [
                {"userId": None, "level": 1, "xp": 1},
                {"userId": "abc", "level": 1, "xp": 1},
                {"userId": "9", "level": "3", "xp": None},
            ]},
        ])
        self.assertEqual(
            asyncio.run(migration.fetch_leaderboard(42, "lurkr", session)),
            [{"user_id": 9, "level": 3, "xp": 0}],
        )

    def test_a_refused_leaderboard_is_reported_not_raised_raw(self):
        session = FakeSession([{}], status=401)
        with self.assertRaises(migration.LeaderboardUnavailable) as caught:
            asyncio.run(migration.fetch_leaderboard(42, "mee6", session))
        self.assertEqual(caught.exception.status, 401)


class ApplyImportTests(unittest.TestCase):
    def make_cog(self, stored):
        class Cxn:
            async def fetch(self, _query, _guild_id):
                return [{"user_id": uid, "level": lvl, "xp": xp} for uid, (lvl, xp) in stored.items()]

        class FakeLeveling:
            get_xp_for_level = staticmethod(xp_for_level)

            def __init__(self):
                self.saved = []

            async def _save_user_data(self, guild_id, user_id, xp, level):
                self.saved.append((int(guild_id), int(user_id), xp, level))

        leveling = FakeLeveling()
        cog = object.__new__(migration.LevelMigration)
        cog.bot = SimpleNamespace(cxn=Cxn(), get_cog=lambda name: leveling)
        return cog, leveling

    def test_rows_imported_and_better_existing_rows_kept(self):
        cog, leveling = self.make_cog({2: (4, 20), 3: (9, 90)})
        rows = [
            {"user_id": 1, "level": 5, "xp": 40},
            {"user_id": 2, "level": 4, "xp": 99},
            {"user_id": 3, "level": 9, "xp": 5},
        ]

        imported, skipped = asyncio.run(
            cog._apply_import(42, rows, cumulative=False))

        self.assertEqual((imported, skipped), (2, 1))
        self.assertEqual(sorted(leveling.saved), [(42, 1, 40, 5), (42, 2, 99, 4)])

    def test_missing_leveling_cog_is_an_error(self):
        cog = object.__new__(migration.LevelMigration)
        cog.bot = SimpleNamespace(
            cxn=SimpleNamespace(fetch=None), get_cog=lambda name: None)
        with self.assertRaises(RuntimeError):
            asyncio.run(cog._apply_import(42, [], cumulative=False))


class _Recorder:
    def __init__(self, raise_forbidden=False):
        self.views = []
        self._raise_forbidden = raise_forbidden

    async def send(self, view=None, **kwargs):
        if self._raise_forbidden:
            raise discord.Forbidden(
                SimpleNamespace(status=403, reason="Forbidden"), "Cannot send messages to this user")
        self.views.append(view)


async def _entries(items):
    for item in items:
        yield item


class JoinDmTests(unittest.TestCase):
    def make_guild(self, member_ids, *, inviter=None, owner=None, audit_raises=None):
        guild = FakeGuild(member_ids)
        guild.name = "Test Server"
        guild.preferred_locale = "en"
        guild.owner = owner
        guild.owner_id = getattr(owner, "id", None)

        def audit_logs(**_kwargs):
            if audit_raises is not None:
                async def failing():
                    raise audit_raises
                    yield  # pragma: no cover
                return failing()
            entries = []
            if inviter is not None:
                entries.append(SimpleNamespace(
                    target=SimpleNamespace(id=BOT_ID), user=inviter))
            return _entries(entries)

        guild.audit_logs = audit_logs
        return guild

    def make_cog(self):
        bot = SimpleNamespace(
            id=BOT_ID,
            user=SimpleNamespace(
                id=BOT_ID,
                display_avatar=SimpleNamespace(url="https://example.test/avatar.png"),
            ),
        )
        return migration.LevelMigration(bot)

    def test_dm_offers_the_import_when_a_leveling_bot_is_present(self):
        inviter = _Recorder()
        cog = self.make_cog()
        asyncio.run(cog.on_guild_join(self.make_guild([MEE6], inviter=inviter)))

        self.assertEqual(len(inviter.views), 1)
        container = inviter.views[0].children[0]
        rows = [item for item in container.children if isinstance(item, discord.ui.ActionRow)]
        self.assertEqual(len(rows), 1)
        self.assertEqual(
            [button.label for button in rows[0].children],
            ["Import from MEE6", "No thanks"],
        )

    def test_dm_has_no_prompt_without_a_supported_bot(self):
        inviter = _Recorder()
        cog = self.make_cog()
        asyncio.run(cog.on_guild_join(self.make_guild([1, 2], inviter=inviter)))

        container = inviter.views[0].children[0]
        self.assertFalse([
            item for item in container.children if isinstance(item, discord.ui.ActionRow)
        ])
        self.assertIn("/dashboard/42/leveling", container.children[0].children[1].content)

    def test_amaribot_offer_appears_only_when_a_key_is_set(self):
        cog = self.make_cog()

        without_key = _Recorder()
        with with_key(""):
            asyncio.run(cog.on_guild_join(self.make_guild([AMARIBOT], inviter=without_key)))
        container = without_key.views[0].children[0]
        self.assertFalse([
            item for item in container.children if isinstance(item, discord.ui.ActionRow)
        ])

        with_key_recorder = _Recorder()
        with with_key("amari-key"):
            asyncio.run(cog.on_guild_join(self.make_guild([AMARIBOT], inviter=with_key_recorder)))
        rows = [
            item for item in with_key_recorder.views[0].children[0].children
            if isinstance(item, discord.ui.ActionRow)
        ]
        self.assertEqual(
            [button.label for button in rows[0].children],
            ["Import from AmariBot", "No thanks"],
        )

    def test_falls_back_to_the_owner_when_the_audit_log_is_unreadable(self):
        owner = _Recorder()
        cog = self.make_cog()
        guild = self.make_guild(
            [LURKR], owner=owner,
            audit_raises=discord.Forbidden(
                SimpleNamespace(status=403, reason="Forbidden"), "Missing permissions"),
        )
        # The audit-log fallback retries once before giving up.
        asyncio.run(cog.on_guild_join(guild))
        self.assertEqual(len(owner.views), 1)

    def test_a_closed_inbox_is_not_an_error(self):
        inviter = _Recorder(raise_forbidden=True)
        cog = self.make_cog()
        asyncio.run(cog.on_guild_join(self.make_guild([MEE6], inviter=inviter)))
        self.assertEqual(inviter.views, [])


class _FakeResponse:
    def __init__(self, recorder):
        self._recorder = recorder

    async def edit_message(self, view=None, **_kwargs):
        self._recorder.messages.append(view)

    async def send_message(self, content=None, **_kwargs):
        self._recorder.messages.append(content)


class FakeInteraction:
    def __init__(self):
        self.messages = []
        self.response = _FakeResponse(self)

    async def edit_original_response(self, view=None, **_kwargs):
        self.messages.append(view)


class MigrateFlowTests(unittest.TestCase):
    def make_cog(self, stored=None):
        saved = []

        class Cxn:
            async def fetch(self, _query, _guild_id):
                return [
                    {"user_id": uid, "level": lvl, "xp": xp}
                    for uid, (lvl, xp) in (stored or {}).items()
                ]

        class FakeLeveling:
            get_xp_for_level = staticmethod(xp_for_level)

            async def _save_user_data(self, guild_id, user_id, xp, level):
                saved.append((int(user_id), level, xp))

        bot = SimpleNamespace(cxn=Cxn(), get_cog=lambda _name: FakeLeveling())
        cog = migration.LevelMigration(bot)
        cog._session = FakeSession([
            {"levels": [
                {"userId": "1", "level": 4, "xp": 30},
                {"userId": "2", "level": 2, "xp": 0},
            ]},
            {"levels": []},
        ])
        self.saved = saved
        return cog

    def test_clicking_import_writes_the_rows_and_reports_the_result(self):
        cog = self.make_cog()
        interaction = FakeInteraction()
        guild = SimpleNamespace(id=42, name="Test Server", preferred_locale="en")

        asyncio.run(cog.migrate(interaction, guild, "lurkr"))

        self.assertEqual(sorted(self.saved), [(1, 4, 30), (2, 2, 0)])
        self.assertEqual(len(interaction.messages), 2)  # progress, then result
        result = interaction.messages[-1].children[0].children[0].content
        self.assertIn("Imported **2** members from Lurkr", result)
        self.assertFalse(cog._running)

    def test_a_second_click_cannot_start_a_parallel_import(self):
        cog = self.make_cog()
        cog._running.add((42, "lurkr"))
        interaction = FakeInteraction()
        guild = SimpleNamespace(id=42, name="Test Server", preferred_locale="en")

        asyncio.run(cog.migrate(interaction, guild, "lurkr"))

        self.assertEqual(self.saved, [])
        self.assertIn("already running", interaction.messages[0])

    def test_an_unreadable_leaderboard_is_reported(self):
        cog = self.make_cog()
        cog._session = FakeSession([{}], status=401)
        interaction = FakeInteraction()
        guild = SimpleNamespace(id=42, name="Test Server", preferred_locale="en")

        asyncio.run(cog.migrate(interaction, guild, "lurkr"))

        self.assertEqual(self.saved, [])
        result = interaction.messages[-1].children[0].children[0].content
        self.assertIn("/dashboard/42/leveling", result)
        self.assertFalse(cog._running)

    def test_a_rejected_amaribot_key_is_explained(self):
        cog = self.make_cog()
        cog._session = FakeSession([{}], status=401)
        interaction = FakeInteraction()
        guild = SimpleNamespace(id=42, name="Test Server", preferred_locale="en")

        with with_key("stale-key"):
            asyncio.run(cog.migrate(interaction, guild, "amaribot"))

        self.assertEqual(self.saved, [])
        result = interaction.messages[-1].children[0].children[0].content
        self.assertIn("AMARIBOT_API_KEY", result)
        self.assertFalse(cog._running)


class LocaleTests(unittest.TestCase):
    def test_welcome_strings_render_in_every_language(self):
        for code in ("en", "de", "es", "fr"):
            guild = SimpleNamespace(preferred_locale=code)
            text = migration.msg(
                guild, "detected", bot="MEE6")
            self.assertIn("MEE6", text)
            self.assertIn("dashboard", migration.settings_url(42))
            self.assertTrue(migration.msg(guild, "migrate_button", bot="Lurkr"))


if __name__ == "__main__":
    unittest.main()
