"""Echo message persistence and its warning-to-blacklist ladder."""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import aiosqlite
import discord

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import database  # noqa: E402
from config.emojis import get_emoji  # noqa: E402
from config.ids import SUPPORT_GUILD  # noqa: E402
from database import SQLitePool  # noqa: E402
from cogs.utility import echo as echo_module  # noqa: E402
from cogs.utility.echo import (  # noqa: E402
    _echo_button_view,
    _info_view,
    _report_guidelines_view,
)
from utils import echo_reports  # noqa: E402
from utils.moderation.manager import BlacklistManager  # noqa: E402

SCHEMA = """
CREATE TABLE echo_messages (
    echo_id TEXT PRIMARY KEY, message_id INTEGER NOT NULL UNIQUE,
    guild_id INTEGER NOT NULL, channel_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL, content TEXT NOT NULL,
    truncated INTEGER NOT NULL DEFAULT 0, created_at REAL NOT NULL,
    removed_at REAL
);
CREATE TABLE echo_reports (
    report_id TEXT PRIMARY KEY, echo_id TEXT NOT NULL,
    reporter_id INTEGER NOT NULL, reason TEXT,
    status TEXT NOT NULL DEFAULT 'pending', created_at REAL NOT NULL,
    reviewed_by INTEGER, reviewed_at REAL
);
CREATE TABLE echo_warnings (
    warning_id TEXT PRIMARY KEY, user_id INTEGER NOT NULL,
    report_id TEXT NOT NULL UNIQUE, reason TEXT, created_at REAL NOT NULL
);
CREATE TABLE blacklist_users (
    id INTEGER PRIMARY KEY, reason TEXT, timestamp REAL, added_by INTEGER,
    expires_at REAL, status TEXT NOT NULL DEFAULT 'active',
    appeal_id TEXT, appealable INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE blacklist_appeals (
    appeal_id TEXT PRIMARY KEY, user_id INTEGER NOT NULL, guild_id INTEGER,
    status TEXT NOT NULL DEFAULT 'pending', created_at REAL NOT NULL
);
"""


async def _pool() -> SQLitePool:
    conn = await aiosqlite.connect(":memory:")
    await conn.executescript(SCHEMA)
    await conn.commit()
    return SQLitePool(conn)


def _assert_no_mentions(value):
    assert value.everyone is False
    assert value.users is False
    assert value.roles is False
    assert value.replied_user is False


def test_the_echo_button_is_a_persistent_info_icon_without_a_label():
    view = _echo_button_view("echo-1")
    buttons = [item for item in view.children if isinstance(item, discord.ui.Button)]
    assert len(buttons) == 1
    assert buttons[0].label is None
    assert str(buttons[0].emoji) == get_emoji("question")
    assert buttons[0].custom_id == "echo:info:echo-1"

    info = _info_view({
        "echo_id": "echo-1", "message_id": 900, "guild_id": 10,
        "channel_id": 11, "author_id": 20, "content": "hello",
        "truncated": False, "created_at": time.time(), "removed_at": None,
    })
    info_text = "\n".join(
        item.content for item in info.walk_children()
        if isinstance(item, discord.ui.TextDisplay)
    )
    assert "# Echoed message" not in info_text
    assert "Guild:" not in info_text
    assert "Channel:" not in info_text
    assert "Reports:" not in info_text
    report_buttons = [
        item for item in info.walk_children()
        if isinstance(item, discord.ui.Button) and item.custom_id == "echo:report:echo-1"
    ]
    assert len(report_buttons) == 1


def test_echo_send_disables_mentions():
    async def exercise():
        pool = await _pool()
        ctx = _Context()
        reporter = echo_module.EchoReporter(SimpleNamespace(cxn=pool))
        try:
            await reporter.send(ctx, "@everyone hello")

            assert len(ctx.messages) == 1
            _assert_no_mentions(ctx.messages[0]["allowed_mentions"])
            echo_id = ctx.messages[0]["view"].children[0].custom_id.rsplit(":", 1)[-1]
            echo = await echo_reports.get_echo_message(pool, echo_id)
            assert echo["message_id"] == 900
        finally:
            await pool._db.close()

    asyncio.run(exercise())


def test_the_report_button_shows_guidelines_with_confirm_and_cancel():
    view = _report_guidelines_view("echo-1")
    text = "\n".join(
        item.content for item in view.walk_children()
        if isinstance(item, discord.ui.TextDisplay)
    )
    buttons = {
        item.custom_id: item for item in view.walk_children()
        if isinstance(item, discord.ui.Button)
    }

    assert "Reporting guidelines" in text
    assert "confidential" in text
    assert set(buttons) == {"echo:confirm:echo-1", "echo:cancel:echo-1"}
    assert buttons["echo:confirm:echo-1"].label == "Confirm"
    assert buttons["echo:cancel:echo-1"].label == "Cancel"


def test_confirming_a_report_edits_the_ephemeral_message_and_posts_to_staff():
    async def exercise():
        pool = await _pool()
        await echo_reports.record_echo_message(
            pool, echo_id="echo-1", message_id=900, guild_id=10, channel_id=11,
            author_id=20, content="reported content", truncated=False,
        )
        channel = SimpleNamespace(send=AsyncMock())
        interaction = _Interaction(21)
        reporter = echo_module.EchoReporter(SimpleNamespace(cxn=pool))
        reporter._reports_channel = AsyncMock(return_value=channel)
        try:
            await reporter._submit_report(interaction, "echo-1")

            report = await pool.fetchrow(
                "SELECT status FROM echo_reports WHERE echo_id = $1 AND reporter_id = $2",
                "echo-1", 21,
            )
            assert report["status"] == "pending"
            channel.send.assert_awaited_once()
            _assert_no_mentions(channel.send.await_args.kwargs["allowed_mentions"])
            assert len(interaction.response.edits) == 1
            _assert_no_mentions(interaction.response.edits[0]["allowed_mentions"])
            result = interaction.response.edits[0]["view"]
            text = "\n".join(
                item.content for item in result.walk_children()
                if isinstance(item, discord.ui.TextDisplay)
            )
            assert "Report submitted" in text
        finally:
            await pool._db.close()

    asyncio.run(exercise())


def test_report_and_cancel_do_not_create_a_report():
    async def exercise():
        pool = await _pool()
        await echo_reports.record_echo_message(
            pool, echo_id="echo-1", message_id=900, guild_id=10, channel_id=11,
            author_id=20, content="reported content", truncated=False,
        )
        reporter = echo_module.EchoReporter(SimpleNamespace(cxn=pool))
        try:
            report = _Interaction(21)
            report.data = {"custom_id": "echo:report:echo-1"}
            await reporter.on_interaction(report)
            _assert_no_mentions(report.response.edits[0]["allowed_mentions"])
            buttons = {
                item.custom_id for item in report.response.edits[0]["view"].walk_children()
                if isinstance(item, discord.ui.Button)
            }
            assert buttons == {"echo:confirm:echo-1", "echo:cancel:echo-1"}

            cancel = _Interaction(21)
            cancel.data = {"custom_id": "echo:cancel:echo-1"}
            await reporter.on_interaction(cancel)
            _assert_no_mentions(cancel.response.edits[0]["allowed_mentions"])
            buttons = {
                item.custom_id for item in cancel.response.edits[0]["view"].walk_children()
                if isinstance(item, discord.ui.Button)
            }
            assert buttons == {"echo:report:echo-1"}

            count = await pool.fetchval(
                "SELECT COUNT(*) FROM echo_reports WHERE echo_id = $1", "echo-1",
            )
            assert count == 0
        finally:
            await pool._db.close()

    asyncio.run(exercise())


def test_an_echo_message_report_and_warning_are_persisted_once():
    async def exercise():
        pool = await _pool()
        echo = await echo_reports.record_echo_message(
            pool,
            echo_id="echo-1",
            message_id=900,
            guild_id=10,
            channel_id=11,
            author_id=20,
            content="hello",
            truncated=False,
        )
        assert echo["echo_id"] == "echo-1"
        assert (await echo_reports.get_echo_message(pool, "echo-1"))["author_id"] == 20

        report, created = await echo_reports.create_echo_report(
            pool, echo_id="echo-1", reporter_id=21,
        )
        assert created is True
        duplicate, created_again = await echo_reports.create_echo_report(
            pool, echo_id="echo-1", reporter_id=21,
        )
        assert created_again is False
        assert duplicate["report_id"] == report["report_id"]

        resolved = await echo_reports.resolve_echo_report(
            pool, report["report_id"], status="valid", reviewer_id=30,
        )
        assert resolved["status"] == "valid"
        assert await echo_reports.resolve_echo_report(
            pool, report["report_id"], status="invalid", reviewer_id=30,
        ) is None

        assert await echo_reports.add_echo_warning(
            pool, user_id=20, report_id=report["report_id"], reason="policy",
        ) == 1
        # The same valid report cannot double-count a warning.
        assert await echo_reports.add_echo_warning(
            pool, user_id=20, report_id=report["report_id"], reason="policy",
        ) == 1
        assert await echo_reports.warning_count(pool, 20) == 1

        await echo_reports.mark_echo_removed(pool, "echo-1")
        assert (await echo_reports.get_echo_message(pool, "echo-1"))["removed_at"] is not None
        await pool._db.close()

    asyncio.run(exercise())


class _Response:
    def __init__(self):
        self.done = False
        self.messages = []
        self.edits = []

    def is_done(self):
        return self.done

    async def send_message(self, **kwargs):
        self.messages.append(kwargs)
        self.done = True

    async def edit_message(self, **kwargs):
        self.edits.append(kwargs)
        self.done = True


class _Followup:
    def __init__(self):
        self.messages = []

    async def send(self, **kwargs):
        self.messages.append(kwargs)


class _InteractionMessage:
    def __init__(self):
        self.edits = []

    async def edit(self, **kwargs):
        self.edits.append(kwargs)


class _Interaction:
    def __init__(self, user_id):
        self.guild = SimpleNamespace(id=SUPPORT_GUILD)
        self.user = SimpleNamespace(id=user_id)
        self.response = _Response()
        self.followup = _Followup()
        self.message = _InteractionMessage()
        self.data = {}


class _PartialMessage:
    def __init__(self):
        self.deleted = False

    async def delete(self):
        self.deleted = True


class _Channel:
    def __init__(self):
        self.partial = _PartialMessage()
        self.message_id = None

    def get_partial_message(self, message_id):
        self.message_id = message_id
        return self.partial


class _User:
    def __init__(self):
        self.messages = []

    async def send(self, **kwargs):
        self.messages.append(kwargs)


class _Context:
    def __init__(self):
        self.guild = SimpleNamespace(id=10)
        self.channel = SimpleNamespace(id=11)
        self.author = SimpleNamespace(id=20)
        self.messages = []

    async def send(self, **kwargs):
        self.messages.append(kwargs)
        return SimpleNamespace(id=900)


async def _report_fixture():
    pool = await _pool()
    await echo_reports.record_echo_message(
        pool, echo_id="echo-1", message_id=900, guild_id=10, channel_id=11,
        author_id=20, content="reported content", truncated=False,
    )
    report, _ = await echo_reports.create_echo_report(
        pool, echo_id="echo-1", reporter_id=21,
    )
    return pool, report


def test_invalid_staff_review_keeps_the_echo_and_creates_no_warning():
    async def exercise():
        pool, report = await _report_fixture()
        channel, user = _Channel(), _User()
        bot = SimpleNamespace(
            cxn=pool,
            get_channel=lambda channel_id: channel,
            get_user=lambda user_id: user,
        )
        interaction = _Interaction(30)
        reporter = echo_module.EchoReporter(bot)
        reporter._is_staff = AsyncMock(return_value=True)
        blacklist = SimpleNamespace(apply_warning_blacklist=AsyncMock())
        try:
            with patch.object(echo_module, "BlacklistManager", lambda: blacklist):
                await reporter._review(interaction, f"invalid:{report['report_id']}")

            assert (await echo_reports.get_echo_report(pool, report["report_id"]))["status"] == "invalid"
            assert await echo_reports.warning_count(pool, 20) == 0
            assert channel.partial.deleted is False
            assert user.messages == []
            blacklist.apply_warning_blacklist.assert_not_awaited()
            assert "invalid" in interaction.response.messages[0]["content"]
            _assert_no_mentions(interaction.response.messages[0]["allowed_mentions"])
            assert len(interaction.message.edits) == 1
            _assert_no_mentions(interaction.message.edits[0]["allowed_mentions"])
        finally:
            await pool._db.close()

    asyncio.run(exercise())


def test_valid_staff_review_deletes_the_echo_warns_and_dms_the_sender():
    async def exercise():
        pool, report = await _report_fixture()
        channel, user = _Channel(), _User()
        bot = SimpleNamespace(
            cxn=pool,
            get_channel=lambda channel_id: channel,
            get_user=lambda user_id: user,
        )
        interaction = _Interaction(30)
        reporter = echo_module.EchoReporter(bot)
        reporter._is_staff = AsyncMock(return_value=True)
        blacklist_result = {
            "warning_count": 1, "blacklisted": False, "permanent": False,
            "appealable": True, "expires_at": None,
        }
        blacklist = SimpleNamespace(
            apply_warning_blacklist=AsyncMock(return_value=blacklist_result),
        )
        try:
            with patch.object(echo_module, "BlacklistManager", lambda: blacklist):
                await reporter._review(interaction, f"valid:{report['report_id']}")

            stored_report = await echo_reports.get_echo_report(pool, report["report_id"])
            stored_echo = await echo_reports.get_echo_message(pool, "echo-1")
            assert stored_report["status"] == "valid"
            assert stored_echo["removed_at"] is not None
            assert await echo_reports.warning_count(pool, 20) == 1
            assert channel.partial.deleted is True
            assert channel.message_id == 900
            assert len(user.messages) == 1
            blacklist.apply_warning_blacklist.assert_awaited_once()
            assert "Warning #1" in interaction.response.messages[0]["content"]
            _assert_no_mentions(interaction.response.messages[0]["allowed_mentions"])
            assert len(interaction.message.edits) == 1
            _assert_no_mentions(interaction.message.edits[0]["allowed_mentions"])
            _assert_no_mentions(user.messages[0]["allowed_mentions"])
        finally:
            await pool._db.close()

    asyncio.run(exercise())


def test_only_an_approved_appeal_makes_a_later_permanent_blacklist_non_appealable():
    async def exercise():
        pool = await _pool()
        previous_pool = database._shared_pool
        previous_manager = BlacklistManager._instance
        database._shared_pool = pool
        BlacklistManager._instance = None
        try:
            manager = BlacklistManager()
            await manager.load()
            await pool.execute(
                "INSERT INTO blacklist_appeals "
                "(appeal_id, user_id, guild_id, status, created_at) "
                "VALUES ($1, $2, NULL, 'pending', $3)",
                "appeal-1", 42, time.time(),
            )

            five = await manager.apply_warning_blacklist(42, 5, reason="policy")
            six = await manager.apply_warning_blacklist(42, 6, reason="policy")
            assert five["permanent"] is True
            assert five["appealable"] is True
            assert six["permanent"] is True
            assert six["appealable"] is True

            await pool.execute(
                "UPDATE blacklist_appeals SET status = 'approved' WHERE appeal_id = $1",
                "appeal-1",
            )
            seven = await manager.apply_warning_blacklist(42, 7, reason="policy")
            assert seven["permanent"] is True
            assert seven["appealable"] is False
            assert manager.get_user_entry(42)["appealable"] is False
        finally:
            database._shared_pool = previous_pool
            BlacklistManager._instance = previous_manager
            await pool._db.close()

    asyncio.run(exercise())


def test_warning_ladder_escalates_and_locks_a_post_appeal_warning():
    async def exercise():
        pool = await _pool()
        previous_pool = database._shared_pool
        previous_manager = BlacklistManager._instance
        database._shared_pool = pool
        BlacklistManager._instance = None
        try:
            manager = BlacklistManager()
            await manager.load()

            below = await manager.apply_warning_blacklist(42, 2, reason="policy")
            assert below["blacklisted"] is False
            assert manager.get_user_entry(42) is None

            three = await manager.apply_warning_blacklist(42, 3, reason="policy")
            entry = manager.get_user_entry(42)
            assert three["duration_seconds"] == 3 * 60 * 60
            assert abs(entry["expires_at"] - (time.time() + 3 * 60 * 60)) < 60

            four = await manager.apply_warning_blacklist(42, 4, reason="policy")
            entry = manager.get_user_entry(42)
            assert four["duration_seconds"] == 24 * 60 * 60
            assert abs(entry["expires_at"] - (time.time() + 24 * 60 * 60)) < 60

            five = await manager.apply_warning_blacklist(42, 5, reason="policy")
            entry = manager.get_user_entry(42)
            assert five["permanent"] is True
            assert five["appealable"] is True
            assert entry["expires_at"] is None

            # An appeal on record makes the next permanent blacklist final.
            await pool.execute(
                "INSERT INTO blacklist_appeals "
                "(appeal_id, user_id, guild_id, status, created_at) "
                "VALUES ($1, $2, NULL, 'approved', $3)",
                "appeal-1", 42, time.time(),
            )
            six = await manager.apply_warning_blacklist(42, 6, reason="policy")
            assert six["permanent"] is True
            assert six["appealable"] is False
            assert manager.get_user_entry(42)["appealable"] is False
        finally:
            database._shared_pool = previous_pool
            BlacklistManager._instance = previous_manager
            await pool._db.close()

    asyncio.run(exercise())
