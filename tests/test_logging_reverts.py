"""Profile-picture archiving, revert snapshots and the restore buttons.

A replaced avatar's CDN URL expires a day or two after the change, so the log
entry has to carry the bytes instead of a link. And a restore button keeps
working after a restart only because the state it needs lives in the database,
not in the custom id the button carries.
"""

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import discord
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import database  # noqa: E402
from cogs.logging import cog as logging_cog  # noqa: E402
from cogs.logging import formatters, revert  # noqa: E402

GUILD_ID = 111


# ── Fakes ──────────────────────────────────────────

class _FakeRole:
    """A role-shaped overwrite target: hashable, with an id and a mention."""

    def __init__(self, role_id):
        self.id = role_id
        self.mention = f"<@&{role_id}>"


class _FakeTextChannel:
    """Stands in for discord.TextChannel in the channel-update listener."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class _EmptyAudit:
    def __aiter__(self):
        return self

    async def __anext__(self):
        raise StopAsyncIteration


class _Guild:
    id = GUILD_ID
    name = "Test server"
    default_role = SimpleNamespace(id=1, mention="@everyone")
    member_count = 42
    premium_subscription_count = 2
    premium_tier = 1
    roles = []

    def __init__(self):
        self.created_role = None

    def audit_logs(self, **_kwargs):
        return _EmptyAudit()

    def get_channel(self, channel_id):
        return None

    def get_role(self, role_id):
        return None

    def get_member(self, user_id):
        return None

    async def create_role(self, **kwargs):
        self.created_role = kwargs

        class _Role(SimpleNamespace):
            async def edit(self, **edit_kwargs):
                self.position = edit_kwargs.get("position", self.position)

        role = _Role(
            id=8,
            name=kwargs["name"],
            mention="<@&8>",
            colour=kwargs["colour"],
            position=0,
            permissions=kwargs["permissions"],
        )
        self.roles.append(role)
        return role


class _Snapshots:
    """The handful of SQL statements the snapshot store issues."""

    def __init__(self):
        self.rows = {}

    async def execute(self, query, *args):
        statement = " ".join(query.split())
        if statement.startswith("INSERT"):
            snapshot_id, guild_id, kind, payload, created_at = args
            self.rows[snapshot_id] = {
                "guild_id": guild_id, "kind": kind,
                "payload": payload, "created_at": created_at,
            }
        elif statement.startswith("DELETE"):
            if "snapshot_id = $1" in statement:
                self.rows.pop(args[0], None)
            else:
                cutoff = args[0]
                self.rows = {
                    key: row for key, row in self.rows.items()
                    if row["created_at"] >= cutoff
                }

    async def fetchrow(self, _query, *args):
        return self.rows.get(args[0])


@pytest.fixture
def snapshots():
    store = _Snapshots()
    with mock.patch.object(database, "_shared_pool", store, create=True):
        yield store


class _Asset:
    def __init__(self, url, data=b"\x89PNG-bytes", error=None):
        self.url = url
        self._data = data
        self._error = error

    async def read(self):
        if self._error is not None:
            raise self._error
        return self._data


def _user(*, avatar=None, guild_avatar=None, member_id=42, name="tester",
          global_name=None, banner=None, default_avatar=None):
    return SimpleNamespace(
        id=member_id,
        name=name,
        global_name=global_name,
        mention=f"<@{member_id}>",
        __str__=lambda _self: "tester#0001",
        guild=_Guild(),
        avatar=avatar,
        banner=banner,
        guild_avatar=guild_avatar,
        default_avatar=default_avatar,
        display_avatar=SimpleNamespace(url="https://cdn.example/current.png"),
        roles=[],
        nick=None,
        premium_since=None,
        timed_out_until=None,
    )


def _cog():
    cog = logging_cog.ServerLogger(SimpleNamespace(user=SimpleNamespace(id=999)))
    cog.log_event = mock.AsyncMock()
    return cog


def _call(cog):
    """The last log entry: its title/body (positional) and its options."""
    call = cog.log_event.await_args
    data = dict(call.kwargs)
    if len(call.args) > 2:
        data["title"] = call.args[2]
    if len(call.args) > 3:
        data["body"] = call.args[3]
    return SimpleNamespace(**data)


def _notice_text(interaction):
    """The single TextDisplay of an ephemeral notice reply."""
    view = interaction.followup.calls[-1][1]["view"]
    return view.children[0].children[0].content


# ── Archived profile pictures ─────────────────────

class TestProfilePictures:
    def test_a_global_picture_change_archives_both_pictures(self):
        cog = _cog()
        before = _user(avatar=_Asset("https://cdn.example/old.png"))
        after = _user(avatar=_Asset("https://cdn.example/new.png"))

        # A global change reaches the bot as a user update: the member in a
        # member update shares its user object, so it never shows the diff.
        asyncio.run(cog.on_user_update(before, after))

        cog.log_event.assert_awaited_once()
        call = _call(cog)
        assert call.title == "Avatar Updated"
        assert call.guild.id == GUILD_ID
        assert "Global profile picture" in call.body
        assert [file.filename for file in call.files] == [
            "profile-picture-before.png", "profile-picture-after.png"]
        # The gallery shows the uploaded bytes, so the file chips are skipped.
        assert call.file_components is False
        assert [item[0] for item in call.media_urls] == [
            "attachment://profile-picture-before.png",
            "attachment://profile-picture-after.png",
        ]
        assert call.media_urls[0][1] == "Before — Global profile picture"

    def test_a_server_picture_change_is_its_own_entry(self):
        cog = _cog()
        before = _user(guild_avatar=_Asset("https://cdn.example/old-server.png"))
        after = _user(guild_avatar=_Asset("https://cdn.example/new-server.webp"))

        asyncio.run(cog.on_member_update(before, after))

        cog.log_event.assert_awaited_once()
        call = _call(cog)
        assert call.title == "Server Avatar Updated"
        # The archived file keeps the source format in its name.
        assert [file.filename for file in call.files] == [
            "server-profile-picture-before.png",
            "server-profile-picture-after.webp",
        ]

    def test_both_pictures_changing_produces_an_entry_each(self):
        cog = _cog()
        before = _user(
            avatar=_Asset("https://cdn.example/old.png"),
            guild_avatar=_Asset("https://cdn.example/old-server.png"),
        )
        after = _user(
            avatar=_Asset("https://cdn.example/new.png"),
            guild_avatar=_Asset("https://cdn.example/new-server.png"),
        )

        asyncio.run(cog.on_user_update(before, after))
        asyncio.run(cog.on_member_update(before, after))

        titles = [call.kwargs["title"] for call in cog.log_event.await_args_list]
        assert titles == ["Avatar Updated", "Server Avatar Updated"]
        assert all(call.kwargs["category"] == "members" for call in cog.log_event.await_args_list)

    def test_an_unchanged_picture_logs_nothing(self):
        cog = _cog()
        before = _user(avatar=_Asset("https://cdn.example/same.png"))
        after = _user(avatar=_Asset("https://cdn.example/same.png"))

        asyncio.run(cog.on_user_update(before, after))

        cog.log_event.assert_not_awaited()

    def test_a_failed_download_falls_back_to_links(self):
        cog = _cog()
        before = _user(avatar=_Asset("https://cdn.example/old.png", error=OSError("gone")))
        after = _user(avatar=_Asset("https://cdn.example/new.png"))

        asyncio.run(cog.on_user_update(before, after))

        call = _call(cog)
        # Only the picture that could not be downloaded is linked; the other is
        # still archived, so the entry survives the CDN expiry either way.
        assert [file.filename for file in call.files] == ["profile-picture-after.png"]
        assert "https://cdn.example/old.png" in call.body
        assert call.media_urls == [
            "https://cdn.example/old.png",
            ("attachment://profile-picture-after.png", "After — Global profile picture"),
        ]

    def test_the_entry_does_not_explain_the_attachments(self):
        cog = _cog()
        before = _user(avatar=_Asset("https://cdn.example/old.png"))
        after = _user(avatar=_Asset("https://cdn.example/new.png"))

        asyncio.run(cog.on_user_update(before, after))

        call = _call(cog)
        assert "attached to this entry" not in call.body
        assert "expires their old links" not in call.body

    def test_a_removed_picture_shows_the_default_avatar(self):
        cog = _cog()
        # Discord draws a default avatar for an account without one, so the
        # entry must not leave the "after" side blank.
        before = _user(avatar=_Asset("https://cdn.example/old.png"))
        after = _user(avatar=None, default_avatar=_Asset("https://cdn.example/default.png"))

        asyncio.run(cog.on_user_update(before, after))

        call = _call(cog)
        assert [file.filename for file in call.files] == [
            "profile-picture-before.png", "profile-picture-after.png"]
        assert call.media_urls[-1][1] == "After — Global profile picture"
        assert "**After:**" not in call.body

    def test_a_first_picture_uses_the_default_as_the_before_image(self):
        cog = _cog()
        before = _user(avatar=None, default_avatar=_Asset("https://cdn.example/default.png"))
        after = _user(avatar=_Asset("https://cdn.example/new.png"))

        asyncio.run(cog.on_user_update(before, after))

        call = _call(cog)
        assert len(call.files) == 2
        assert call.media_urls[0][1] == "Before — Global profile picture"
        assert "**Before:**" not in call.body

    def test_an_unarchived_default_avatar_is_shown_without_a_dead_link_line(self):
        cog = _cog()
        # The default picture has a permanent CDN URL, so a failed download
        # still shows it — and the entry does not print a link the reader can
        # already see.
        before = _user(avatar=_Asset("https://cdn.example/old.png"))
        after = _user(avatar=None, default_avatar=_Asset("https://cdn.example/default.png",
                                                        error=OSError("offline")))

        asyncio.run(cog.on_user_update(before, after))

        call = _call(cog)
        assert "https://cdn.example/default.png" in call.media_urls
        assert "https://cdn.example/default.png" not in call.body
        assert "**After:**" not in call.body

    def test_a_removed_server_picture_shows_the_global_picture(self):
        cog = _cog()
        before = _user(guild_avatar=_Asset("https://cdn.example/old-server.png"))
        # A member without a per-server picture shows the global one there.
        after = _user()

        asyncio.run(cog.on_member_update(before, after))

        call = _call(cog)
        assert call.title == "Server Avatar Updated"
        assert "https://cdn.example/current.png" in call.media_urls

    def test_an_oversized_picture_is_not_uploaded(self):
        cog = _cog()
        before = _user(avatar=_Asset("https://cdn.example/huge.gif", data=b"x" * 10))
        after = _user(avatar=_Asset("https://cdn.example/new.png", data=b"ok"))

        with mock.patch.object(logging_cog, "MAX_ARCHIVED_AVATAR_BYTES", 4):
            asyncio.run(cog.on_user_update(before, after))

        call = _call(cog)
        assert [file.filename for file in call.files] == ["profile-picture-after.png"]
        assert call.media_urls[0] == "https://cdn.example/huge.gif"

    def test_the_same_change_dispatched_twice_is_logged_once(self):
        cog = _cog()
        before = _user(avatar=_Asset("https://cdn.example/old.png"))
        after = _user(avatar=_Asset("https://cdn.example/new.png"))

        # Discord dispatches one profile edit once per shared server.
        asyncio.run(cog.on_user_update(before, after))
        asyncio.run(cog.on_user_update(_user(avatar=_Asset("https://cdn.example/old.png")), after))

        cog.log_event.assert_awaited_once()

    def test_a_global_name_change_is_logged(self):
        cog = _cog()
        before = _user(name="tester", global_name="Old Name")
        after = _user(name="tester", global_name="New Name")

        asyncio.run(cog.on_user_update(before, after))

        cog.log_event.assert_awaited_once()
        call = _call(cog)
        assert call.title == "Username Updated"
        assert "**Display Name:** `Old Name` → `New Name`" in call.body
        assert "Username:" not in call.body

    def test_a_username_change_is_logged(self):
        cog = _cog()
        before = _user(name="tester")
        after = _user(name="renamed")

        asyncio.run(cog.on_user_update(before, after))

        call = _call(cog)
        assert "**Username:** `tester` → `renamed`" in call.body

    def test_a_banner_change_has_its_own_entry(self):
        cog = _cog()
        before = _user(banner=_Asset("https://cdn.example/old-banner.png"))
        after = _user(banner=_Asset("https://cdn.example/new-banner.png"))

        asyncio.run(cog.on_user_update(before, after))

        call = _call(cog)
        assert call.title == "Profile Banner Updated"
        assert [file.filename for file in call.files] == [
            "profile-banner-before.png", "profile-banner-after.png"]


# ── Snapshot store ────────────────────────────────

class TestSnapshotStore:
    def test_a_saved_snapshot_round_trips(self, snapshots):
        snapshot_id = asyncio.run(revert.save_snapshot(
            GUILD_ID, "role", {"name": "Moderator", "colour": 1193046}))

        assert len(snapshot_id) == 12
        state = asyncio.run(revert.load_snapshot(snapshot_id))
        assert state["guild_id"] == GUILD_ID
        assert state["kind"] == "role"
        assert state["payload"] == {"name": "Moderator", "colour": 1193046}

    def test_dropping_a_snapshot_makes_it_unusable(self, snapshots):
        snapshot_id = asyncio.run(revert.save_snapshot(GUILD_ID, "channel", {"name": "#1"}))
        asyncio.run(revert.drop_snapshot(snapshot_id))

        assert asyncio.run(revert.load_snapshot(snapshot_id)) is None

    def test_without_a_database_there_is_no_snapshot(self):
        with mock.patch.object(database, "_shared_pool", None, create=True):
            assert asyncio.run(revert.save_snapshot(GUILD_ID, "role", {})) is None

    def test_a_role_snapshot_carries_everything_a_restore_needs(self):
        role = SimpleNamespace(
            name="Moderator",
            colour=discord.Colour(0x123456),
            hoist=True,
            mentionable=False,
            permissions=discord.Permissions(manage_messages=True),
            position=3,
        )

        payload = revert.role_snapshot(role)

        assert payload["name"] == "Moderator"
        assert payload["colour"] == 0x123456
        assert payload["hoist"] is True
        assert payload["mentionable"] is False
        assert payload["position"] == 3
        assert discord.Permissions(payload["permissions"]).manage_messages

    def test_a_channel_snapshot_carries_its_overwrites(self):
        role = _FakeRole(7)
        overwrite = discord.PermissionOverwrite(send_messages=False, view_channel=True)
        channel = SimpleNamespace(
            name="general",
            type=discord.ChannelType.text,
            category=None,
            position=2,
            topic="hello",
            nsfw=False,
            slowmode_delay=5,
            bitrate=None,
            user_limit=0,
            overwrites={role: overwrite},
        )

        # The real overwrite keys are discord.Role objects, which a fake cannot
        # be, so the role check is pointed at the fake for this snapshot.
        with mock.patch.object(revert.discord, "Role", _FakeRole):
            payload = revert.channel_snapshot(channel)

        assert payload["type"] == "text"
        assert payload["topic"] == "hello"
        assert payload["slowmode_delay"] == 5
        assert len(payload["overwrites"]) == 1
        entry = payload["overwrites"][0]
        assert entry["target_type"] == "role"
        assert entry["target_id"] == 7
        restored = revert._overwrite_from(entry)
        assert restored.send_messages is False
        assert restored.view_channel is True


# ── Buttons ───────────────────────────────────────

class _Response:
    def __init__(self):
        self.deferred = None

    async def defer(self, **kwargs):
        self.deferred = kwargs


class _Followup:
    def __init__(self):
        self.calls = []

    async def send(self, *args, **kwargs):
        self.calls.append((args, kwargs))


class _Interaction:
    def __init__(self, guild, *, manage_roles=True, manage_channels=True):
        self.guild = guild
        self.user = SimpleNamespace(
            id=5,
            mention="<@5>",
            guild_permissions=discord.Permissions(
                manage_roles=manage_roles, manage_channels=manage_channels),
        )
        self.response = _Response()
        self.followup = _Followup()
        self.client = SimpleNamespace(get_cog=lambda _name: None)


class TestButtons:
    def test_every_revert_kind_gets_a_button(self):
        for kind, expected, prefix in (
            ("role", "Restore Role", "log:role-restore:"),
            ("channel", "Restore Channel", "log:channel-restore:"),
            ("channel-update", "Revert Changes", "log:channel-revert:"),
        ):
            buttons = formatters._build_action_buttons(
                "Role Deleted", GUILD_ID, 7, None, (kind, "0123456789ab"))
            assert buttons[0].item.label == expected
            assert buttons[0].item.custom_id.startswith(prefix)

    def test_a_restore_button_encodes_only_the_snapshot(self):
        button = revert.RestoreRoleButton("0123456789ab")
        assert button.item.custom_id == "log:role-restore:0123456789ab"
        match = button.template.fullmatch(button.item.custom_id)
        rebuilt = asyncio.run(
            revert.RestoreRoleButton.from_custom_id(None, None, match))
        assert rebuilt.snapshot_id == "0123456789ab"

    def test_restoring_a_role_recreates_it_from_the_snapshot(self, snapshots):
        role = SimpleNamespace(
            name="Moderator",
            colour=discord.Colour(0x123456),
            hoist=True,
            mentionable=False,
            permissions=discord.Permissions(manage_messages=True),
            position=3,
        )
        snapshot_id = asyncio.run(revert.save_snapshot(
            GUILD_ID, "role", revert.role_snapshot(role)))
        guild = _Guild()
        interaction = _Interaction(guild)

        asyncio.run(revert.RestoreRoleButton(snapshot_id).callback(interaction))

        assert guild.created_role["name"] == "Moderator"
        assert guild.created_role["colour"] == discord.Colour(0x123456)
        assert guild.created_role["permissions"].manage_messages is True
        assert interaction.response.deferred == {"ephemeral": True}
        assert "Restored" in _notice_text(interaction)
        # The snapshot is consumed, so a second click cannot duplicate the role.
        assert asyncio.run(revert.load_snapshot(snapshot_id)) is None

    def test_a_restore_needs_the_matching_permission(self, snapshots):
        snapshot_id = asyncio.run(revert.save_snapshot(
            GUILD_ID, "role", revert.role_snapshot(SimpleNamespace(
                name="x", colour=discord.Colour(0), hoist=False, mentionable=False,
                permissions=discord.Permissions(), position=0))))
        guild = _Guild()
        interaction = _Interaction(guild, manage_roles=False)

        asyncio.run(revert.RestoreRoleButton(snapshot_id).callback(interaction))

        assert guild.created_role is None
        assert "Manage Roles" in _notice_text(interaction)

    def test_an_expired_snapshot_is_refused(self, snapshots):
        guild = _Guild()
        interaction = _Interaction(guild)

        asyncio.run(revert.RestoreChannelButton("deadbeef1234").callback(interaction))

        assert "no longer available" in _notice_text(interaction)

    def test_a_snapshot_from_another_guild_is_refused(self, snapshots):
        snapshot_id = asyncio.run(revert.save_snapshot(
            GUILD_ID + 1, "role", {"name": "x"}))
        guild = _Guild()
        interaction = _Interaction(guild)

        asyncio.run(revert.RestoreRoleButton(snapshot_id).callback(interaction))

        assert guild.created_role is None
        assert asyncio.run(revert.load_snapshot(snapshot_id)) is not None

    def test_reverting_a_channel_restores_settings_and_overwrites(self, snapshots):
        channel = SimpleNamespace(
            id=50, name="general", mention="<#50>", edits=[], permissions=[],
        )

        async def edit(**kwargs):
            channel.edits.append(kwargs)

        async def set_permissions(target, overwrite=None, reason=None):
            channel.permissions.append((target, overwrite))

        channel.edit = edit
        channel.set_permissions = set_permissions

        role = SimpleNamespace(id=7, mention="<@&7>")
        guild = _Guild()
        guild.get_channel = lambda channel_id: channel if channel_id == 50 else None
        guild.get_role = lambda role_id: role if role_id == 7 else None

        # An overwrite that did not exist before the edit is deleted, not re-created.
        snapshot_id = asyncio.run(revert.save_snapshot(
            GUILD_ID, "channel-update",
            {"channel_id": 50,
             "before": {"name": "old-general", "topic": None},
             "overwrites": [{"target_type": "role", "target_id": 7,
                             "allow": None, "deny": None}]}))

        asyncio.run(revert.RevertChannelButton(snapshot_id).callback(_Interaction(guild)))

        assert channel.edits[0]["name"] == "old-general"
        assert channel.edits[0]["topic"] is None
        assert channel.permissions == [(role, None)]
        assert asyncio.run(revert.load_snapshot(snapshot_id)) is None


# ── The listeners hand a snapshot to their entries ──

class TestListenerSnapshots:
    def test_a_deleted_role_is_logged_with_a_restore_snapshot(self, snapshots):
        cog = _cog()
        role = SimpleNamespace(
            id=7, name="Moderator", colour=discord.Colour(0x123456), hoist=True,
            mentionable=False, permissions=discord.Permissions(manage_messages=True),
            position=3, guild=_Guild(),
        )

        asyncio.run(cog.on_guild_role_delete(role))

        call = _call(cog)
        assert call.title == "Role Deleted"
        assert "Restore Role" in call.body
        kind, snapshot_id = call.revert
        assert kind == "role"
        state = asyncio.run(revert.load_snapshot(snapshot_id))
        assert state["payload"]["name"] == "Moderator"

    def test_a_deleted_channel_is_logged_with_a_restore_snapshot(self, snapshots):
        cog = _cog()
        channel = SimpleNamespace(
            id=50, name="general", mention="#general", guild=_Guild(),
            type=discord.ChannelType.text, category=None, position=2,
            topic="hello", nsfw=False, slowmode_delay=0, bitrate=None,
            user_limit=0, overwrites={},
        )

        asyncio.run(cog.on_guild_channel_delete(channel))

        call = _call(cog)
        assert call.title == "Channel Deleted"
        assert "Restore Channel" in call.body
        kind, snapshot_id = call.revert
        assert kind == "channel"
        state = asyncio.run(revert.load_snapshot(snapshot_id))
        assert state["payload"]["name"] == "general"
        assert state["payload"]["topic"] == "hello"

    def test_a_channel_edit_is_logged_with_a_revert_snapshot(self, snapshots):
        cog = _cog()
        before = _FakeTextChannel(
            id=50, name="old-name", guild=_Guild(),
            category=None, topic="before", slowmode_delay=0, nsfw=False,
            overwrites={}, position=0, mention="#old-name",
        )
        after = _FakeTextChannel(
            id=50, name="new-name", guild=_Guild(),
            category=None, topic="after", slowmode_delay=0, nsfw=False,
            overwrites={}, position=0, mention="#new-name",
        )

        # The listener's own type check decides whether topic and slowmode are
        # compared at all, so the fake stands in for a text channel here.
        with mock.patch.object(logging_cog.discord, "TextChannel", _FakeTextChannel):
            asyncio.run(cog.on_guild_channel_update(before, after))

        call = _call(cog)
        assert call.title == "Channel Updated"
        assert "Revert Changes" in call.body
        kind, snapshot_id = call.revert
        assert kind == "channel-update"
        state = asyncio.run(revert.load_snapshot(snapshot_id))
        assert state["payload"]["before"] == {"name": "old-name", "topic": "before"}


# ── Registration and voice detail ─────────────────

def test_the_buttons_are_registered_for_old_entries():
    bot = SimpleNamespace(add_view=mock.Mock())
    cog = logging_cog.ServerLogger(bot)

    asyncio.run(cog.cog_load())

    assert bot.add_view.call_count == 1


def test_a_voice_mute_is_logged_as_a_state_change():
    cog = _cog()
    channel = SimpleNamespace(id=3, mention="<#3>")
    member = SimpleNamespace(id=42, mention="<@42>", guild=_Guild(),
                             __str__=lambda _self: "tester#0001")
    before = SimpleNamespace(channel=channel, self_mute=False, self_deaf=False,
                             self_stream=None, self_video=None, mute=False, deaf=False)
    after = SimpleNamespace(channel=channel, self_mute=True, self_deaf=False,
                            self_stream=None, self_video=None, mute=False, deaf=False)

    asyncio.run(cog.on_voice_state_update(member, before, after))

    call = _call(cog)
    assert call.title == "Voice State Updated"
    assert "Self Mute" in call.body
    assert "muted" in call.body


def test_a_voice_update_without_a_state_change_logs_nothing():
    cog = _cog()
    channel = SimpleNamespace(id=3, mention="<#3>")
    member = SimpleNamespace(id=42, mention="<@42>", guild=_Guild(),
                             __str__=lambda _self: "tester#0001")
    state = SimpleNamespace(channel=channel, self_mute=False, self_deaf=False,
                            self_stream=None, self_video=None, mute=False, deaf=False)

    asyncio.run(cog.on_voice_state_update(member, state, state))

    cog.log_event.assert_not_awaited()


# ── Voice quick actions ───────────────────────────

class _VoiceResponse:
    def __init__(self):
        self.messages = []

    async def send_message(self, content=None, **kwargs):
        self.messages.append((content, kwargs))


class _VoiceMember:
    def __init__(self, *, in_channel=True, muted=False):
        self.id = 42
        self.voice = SimpleNamespace(
            channel=SimpleNamespace(id=3, mention="<#3>") if in_channel else None)
        self.moved_to = "unchanged"
        self.muted = muted
        self.edits = []

    async def move_to(self, channel, *, reason=None):
        self.moved_to = channel

    async def edit(self, *, mute, reason=None):
        self.edits.append({"mute": mute, "reason": reason})
        self.muted = mute

    def __str__(self):
        return "tester#0001"


def _voice_interaction(member, **permissions):
    guild = SimpleNamespace(get_member=lambda _id: member)
    return SimpleNamespace(
        client=SimpleNamespace(get_guild=lambda _gid: guild),
        user=SimpleNamespace(id=5, guild_permissions=discord.Permissions(**permissions)),
        response=_VoiceResponse(),
    )


def _button_labels(view):
    """Every button label in a rendered view, however the rows are nested."""
    labels = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == 2 and "label" in node:
                labels.append(node["label"])
            for child in node.get("components", []):
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(view.to_components())
    return labels


def test_voice_entries_get_disconnect_and_mute_actions():
    buttons = formatters._build_action_buttons("Voice Join", GUILD_ID, 42)

    assert [type(button) for button in buttons] == [
        formatters.VoiceMuteButton, formatters.VoiceDisconnectButton]
    assert [button.label for button in buttons] == ["Server Mute", "Disconnect"]


def test_a_server_muted_entry_offers_the_unmute_action():
    buttons = formatters._build_action_buttons(
        "Voice State Updated", GUILD_ID, 42,
        body="**Member:** <@42>\n**Server Mute:** `server-muted`")

    assert buttons[0].label == "Server Unmute"
    assert buttons[0].unmute is True


def test_a_voice_leave_entry_has_no_disconnect_button():
    buttons = formatters._build_action_buttons("Voice Leave", GUILD_ID, 42)

    # The member is already out of voice; only the mute that follows them into
    # the next session makes sense.
    assert [type(button) for button in buttons] == [formatters.VoiceMuteButton]


def test_a_voice_log_view_carries_the_voice_buttons():
    view = formatters._build_log_view(
        "voice", "Voice State Updated", "**Server Mute:** `server-muted`", GUILD_ID,
        target_id=42)

    assert _button_labels(view) == ["Server Unmute", "Disconnect"]


def test_disconnect_moves_the_member_out_of_voice():
    member = _VoiceMember()
    interaction = _voice_interaction(member, move_members=True)

    asyncio.run(formatters.VoiceDisconnectButton(GUILD_ID, member.id).callback(interaction))

    assert member.moved_to is None
    assert "Disconnected" in interaction.response.messages[-1][0]


def test_disconnect_explains_when_the_member_is_not_in_voice():
    member = _VoiceMember(in_channel=False)
    interaction = _voice_interaction(member, move_members=True)

    asyncio.run(formatters.VoiceDisconnectButton(GUILD_ID, member.id).callback(interaction))

    assert member.moved_to == "unchanged"
    assert "not in a voice channel" in interaction.response.messages[-1][0]


def test_disconnect_needs_the_move_permission():
    member = _VoiceMember()
    interaction = _voice_interaction(member, move_members=False)

    asyncio.run(formatters.VoiceDisconnectButton(GUILD_ID, member.id).callback(interaction))

    assert member.moved_to == "unchanged"
    assert "permission" in interaction.response.messages[-1][0]


def test_the_mute_button_toggles_the_voice_state_both_ways():
    member = _VoiceMember()
    interaction = _voice_interaction(member, mute_members=True)

    asyncio.run(formatters.VoiceMuteButton(GUILD_ID, member.id).callback(interaction))
    assert member.edits[-1]["mute"] is True

    asyncio.run(formatters.VoiceMuteButton(GUILD_ID, member.id, unmute=True).callback(interaction))
    assert member.edits[-1]["mute"] is False
