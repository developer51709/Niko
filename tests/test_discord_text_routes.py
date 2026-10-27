"""Tests for shared Discord text mention resolution API."""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import discord

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import app
from webapp import discord_api, runtime, staff  # noqa: E402
from webapp.routes import discord_text_routes as routes


class FakeGuild:
    id = 123

    def get_channel(self, channel_id):
        return None

    def get_role(self, role_id):
        return None

    def get_member(self, user_id):
        return None

    async def fetch_member(self, user_id):
        if user_id != 456:
            raise LookupError(user_id)
        return SimpleNamespace(display_name="Server Nickname", name="username")

    async def fetch_roles(self):
        return [SimpleNamespace(id=789, name="Moderators")]


class FakeBot:
    loop = SimpleNamespace(is_running=lambda: True)

    def __init__(self):
        self.guild = FakeGuild()

    def get_guild(self, guild_id):
        return self.guild if guild_id == 123 else None

    async def fetch_channel(self, channel_id):
        if channel_id != 321:
            raise LookupError(channel_id)
        return SimpleNamespace(
            name="help-desk", guild=SimpleNamespace(id=123)
        )


def _run_on_loop(awaitable):
    return asyncio.run(awaitable)


def test_discord_text_endpoint_resolves_uncached_mentions(monkeypatch):
    bot = FakeBot()
    monkeypatch.setattr(routes, "_discord_bot", bot)
    monkeypatch.setattr(routes._server, "run_on_bot_loop", _run_on_loop)

    response = app.test_client().post(
        "/api/discord/text",
        json={"guild_id": "123", "text": "<@456> <#321> <@&789>"},
    )

    assert response.status_code == 200
    assert response.get_json()["mention_names"] == {
        "user": {"456": "Server Nickname"},
        "channel": {"321": "help-desk"},
        "role": {"789": "Moderators"},
    }


def test_discord_text_endpoint_uses_discord_api_when_bot_cache_misses(monkeypatch):
    bot = FakeBot()
    monkeypatch.setattr(routes, "_discord_bot", bot)
    monkeypatch.setattr(routes._server, "run_on_bot_loop", _run_on_loop)
    monkeypatch.setattr(routes._server, "DISCORD_BOT_TOKEN", "test-token")

    class FakeResponse:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    def fake_get(url, **kwargs):
        if url.endswith("/users/999"):
            return FakeResponse({"id": "999", "global_name": "Fetched User"})
        if url.endswith("/channels/888"):
            return FakeResponse({"id": "888", "name": "fetched-channel", "guild_id": "123"})
        raise AssertionError(f"Unexpected Discord API URL: {url}")

    monkeypatch.setattr(discord_api.req, "get", fake_get)
    response = app.test_client().post(
        "/api/discord/text",
        json={"guild_id": "123", "text": "<@999> <#888>"},
    )

    assert response.status_code == 200
    assert response.get_json()["mention_names"] == {
        "user": {"999": "Fetched User"},
        "channel": {"888": "fetched-channel"},
        "role": {},
    }


def test_transcript_endpoint_resolves_message_author_profiles(monkeypatch):
    """The web transcript gets avatars and names for its message authors."""
    from webapp.routes import transcript_routes

    messages = [
        {"timestamp": "2026-10-15 15:03:00 UTC", "author": "Soren", "author_id": 101, "content": "hello"},
        {"timestamp": "2026-10-15 15:04:00 UTC", "author": "Soren", "author_id": 101, "content": "again"},
    ]

    class FakeCxn:
        async def fetchrow(self, *_args):
            return {
                "transcript_id": "test",
                "guild_id": 1,
                "channel_id": 2,
                "channel_name": "ticket",
                "opener_id": 101,
                "category": "General",
                "claimed_by": None,
                "message_count": len(messages),
                "messages": messages,
                "created_at": "2026-10-15 15:00:00 UTC",
            }

    monkeypatch.setattr(transcript_routes, "_discord_bot", SimpleNamespace(cxn=FakeCxn()))
    monkeypatch.setattr(transcript_routes, "run_on_bot_loop", _run_on_loop)
    monkeypatch.setattr(
        transcript_routes,
        "_resolve_transcript_mentions",
        lambda guild_id, msgs: {"user": {}, "channel": {}, "role": {}},
    )
    calls = {}

    def fake_profiles(guild_id, text, author_ids):
        calls.update(guild_id=guild_id, text=text, author_ids=list(author_ids))
        return {"101": {"id": "101", "display_name": "Soren", "username": "soren", "avatar_url": None}}

    monkeypatch.setattr(transcript_routes, "resolve_discord_user_profiles", fake_profiles)

    response = app.test_client().get("/api/transcript/test")

    assert response.status_code == 200
    assert calls == {"guild_id": 1, "text": "", "author_ids": [101, 101]}
    assert response.get_json()["author_profiles"]["101"]["display_name"] == "Soren"


def test_discord_text_endpoint_rejects_invalid_or_oversized_requests():
    client = app.test_client()

    assert client.post("/api/discord/text", json={"text": 42}).status_code == 400
    assert client.post(
        "/api/discord/text", json={"guild_id": "not-a-snowflake", "text": "hi"}
    ).status_code == 400
    assert client.post(
        "/api/discord/text", json={"text": "x" * 20001}
    ).status_code == 413


def test_public_discord_user_profile_endpoint_fetches_live_member_data(monkeypatch):
    user = SimpleNamespace(
        name="user-name",
        global_name="Global Name",
        display_avatar=SimpleNamespace(url="https://cdn.example/avatar.png"),
        banner=None,
        accent_color=SimpleNamespace(value=0x12ABEF),
        primary_guild=SimpleNamespace(
            tag="NIKO", badge=SimpleNamespace(url="https://cdn.example/guild-badge.png")
        ),
        avatar_decoration=SimpleNamespace(
            url="https://cdn.example/decoration.png", is_animated=lambda: False
        ),
        avatar_decoration_sku_id=987,
        public_flags=SimpleNamespace(value=(1 << 0) | (1 << 9)),
    )
    member = SimpleNamespace(
        _user=user,
        display_name="Server Nickname",
        nick="Server Nickname",
    )
    guild = SimpleNamespace(
        get_member=lambda user_id: member if user_id == 456 else None,
        fetch_member=lambda user_id: asyncio.sleep(0, result=member),
    )
    bot = SimpleNamespace(
        loop=SimpleNamespace(is_running=lambda: True),
        guilds=[guild],
        get_guild=lambda guild_id: guild if guild_id == 123 else None,
        fetch_user=lambda user_id: asyncio.sleep(0, result=user),
    )
    monkeypatch.setattr(routes, "_discord_bot", bot)
    monkeypatch.setattr(routes._server, "run_on_bot_loop", _run_on_loop)

    response = app.test_client().get("/api/discord/users/456")

    assert response.status_code == 200
    assert response.get_json()["display_name"] == "Global Name"
    assert response.get_json()["guild_nick"] == "Server Nickname"
    profile = response.get_json()
    assert profile["avatar_url"] == "https://cdn.example/avatar.png"
    assert profile["banner_url"] is None
    assert profile["banner_color"] == "#12abef"
    assert profile["guild_tag"] == "NIKO"
    assert profile["guild_badge_url"] == "https://cdn.example/guild-badge.png"
    assert profile["avatar_decoration_url"] == "https://cdn.example/decoration.png"
    assert profile["avatar_decoration_sku_id"] == 987
    assert profile["badges"] == ["staff", "early_supporter"]
    assert app.test_client().get("/api/discord/users/not-an-id").status_code == 400


def _presence_user():
    """The profile-only fields a user object carries in the gateway cache."""
    return SimpleNamespace(
        name="user-name",
        global_name="Global Name",
        display_avatar=SimpleNamespace(url="https://cdn.example/avatar.png"),
        banner=None,
        accent_color=None,
        primary_guild=None,
        avatar_decoration=None,
        avatar_decoration_sku_id=None,
        public_flags=None,
    )


def _presence_bot(members, user):
    """A bot whose guilds each cache one of ``members`` for user 456."""
    guilds = [
        SimpleNamespace(
            get_member=lambda user_id, cached=member: cached if user_id == 456 else None,
            fetch_member=lambda user_id, cached=member: asyncio.sleep(0, result=cached),
        )
        for member in members
    ]
    return SimpleNamespace(
        loop=SimpleNamespace(is_running=lambda: True),
        guilds=guilds,
        get_guild=lambda guild_id: None,
        fetch_user=lambda user_id: asyncio.sleep(0, result=user),
    )


def _presence_member(user, *, global_name="Global Name", status="offline", activities=()):
    return SimpleNamespace(
        _user=user,
        nick="Server Nickname",
        global_name=global_name,
        status=SimpleNamespace(name=status),
        activities=list(activities),
    )


def test_public_discord_user_profile_reads_the_richest_presence_across_guilds(monkeypatch):
    """Presence is cached per guild, so the popup reads the richest copy.

    The guild that received a member's presence is not necessarily the first one
    the bot caches, so reading ``guilds[0]`` alone showed an active member as
    offline while the staff cards showed their live custom status.
    """
    user = _presence_user()
    custom = SimpleNamespace(type=SimpleNamespace(name="custom"), state="Writing docs", emoji=None)
    quiet = _presence_member(user, status="offline")
    active = _presence_member(user, status="idle", activities=[custom])
    monkeypatch.setattr(routes, "_discord_bot", _presence_bot([quiet, active], user))
    monkeypatch.setattr(routes._server, "run_on_bot_loop", _run_on_loop)

    profile = app.test_client().get("/api/discord/users/456").get_json()

    assert profile["status"] == "idle"
    assert profile["custom_status"]["text"] == "Writing docs"


def test_custom_status_with_only_an_emoji_does_not_show_the_placeholder_text():
    """An emoji-only custom status shows the emoji and no text.

    Discord omits ``state`` for an emoji-only status, so discord.py stores the
    literal placeholder "Custom Status" in both ``state`` and ``name``. The
    popup used to render that placeholder beside the emoji.
    """
    activity = discord.CustomActivity(name="Custom Status", emoji="\U0001f319")
    member = SimpleNamespace(activities=[activity])

    status = routes._custom_status(member)

    assert status["text"] is None
    assert status["emoji_name"] == "\U0001f319"


def test_profile_popup_endpoint_returns_no_text_for_an_emoji_only_status(monkeypatch):
    """The popup payload carries the emoji alone, with no placeholder text."""
    user = _presence_user()
    activity = discord.CustomActivity(name="Custom Status", emoji="\U0001f319")
    member = _presence_member(user, status="online", activities=[activity])
    monkeypatch.setattr(routes, "_discord_bot", _presence_bot([member], user))
    monkeypatch.setattr(routes._server, "run_on_bot_loop", _run_on_loop)

    profile = app.test_client().get("/api/discord/users/456").get_json()

    assert profile["custom_status"]["text"] is None
    assert profile["custom_status"]["emoji_name"] == "\U0001f319"


def test_staff_cards_drop_the_custom_status_placeholder_text(monkeypatch):
    """The staff card and the popup share one text normaliser."""
    user = _presence_user()
    activity = discord.CustomActivity(name="Custom Status", emoji="\U0001f319")
    member = _presence_member(user, status="online", activities=[activity])
    bot = _presence_bot([member], user)
    monkeypatch.setattr(runtime, "_discord_bot", bot)
    monkeypatch.setattr(runtime, "run_on_bot_loop", _run_on_loop)

    identity = staff._staff_identity("456")

    assert identity["custom_status"]["text"] is None
    assert identity["custom_status"]["emoji"]["value"] == "\U0001f319"


def _tagged_profile_user(primary_guild):
    user = _presence_user()
    user.primary_guild = primary_guild
    return user


def _tagged_profile_bot(members, user, guild=None):
    return SimpleNamespace(
        loop=SimpleNamespace(is_running=lambda: True),
        guilds=members,
        cxn=None,
        get_guild=lambda guild_id: guild if guild_id == 123 else None,
        fetch_guild=lambda guild_id: asyncio.sleep(0, result=guild),
        fetch_user=lambda user_id: asyncio.sleep(0, result=user),
    )


def test_profile_payload_carries_the_public_server_tag_details(monkeypatch):
    user = _tagged_profile_user(
        SimpleNamespace(id=123, tag="MOON", badge=SimpleNamespace(url="https://cdn.example/tag.png"))
    )
    member = _presence_member(user)
    guild = SimpleNamespace(
        id=123,
        name="The Gamer Nation",
        icon=SimpleNamespace(url="https://cdn.example/icon.png"),
        banner=None,
        description="Roleplay and gaming",
        member_count=72,
        approximate_presence_count=33,
        created_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
        vanity_url="https://discord.gg/gamernation",
        invites=None,
        members=[member],
        get_member=lambda user_id: member if user_id == 456 else None,
        fetch_member=lambda user_id: asyncio.sleep(0, result=member),
    )
    async def public(guild_id):
        return {"private": False}

    monkeypatch.setattr(routes, "_discord_bot", _tagged_profile_bot([guild], user, guild))
    monkeypatch.setattr(routes, "_guild_privacy", public)
    monkeypatch.setattr(routes._server, "run_on_bot_loop", _run_on_loop)

    server = app.test_client().get("/api/discord/users/456").get_json()["server_tag"]

    assert server["available"] is True
    assert server["private"] is False
    assert server["tag"] == "MOON"
    assert server["badge_url"] == "https://cdn.example/tag.png"
    assert server["name"] == "The Gamer Nation"
    assert server["icon_url"] == "https://cdn.example/icon.png"
    assert server["description"] == "Roleplay and gaming"
    assert server["online_count"] == 33
    assert server["member_count"] == 72
    assert server["invite_url"] == "https://discord.gg/gamernation"
    assert server["created_at"] == int(datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp())
    # A signed-out visitor is never treated as a member, so the popup offers Join.
    assert server["viewer_is_member"] is False


def test_profile_payload_hides_a_private_servers_details(monkeypatch):
    user = _tagged_profile_user(SimpleNamespace(id=123, tag="MOON", badge=None))
    member = _presence_member(user)
    guild = SimpleNamespace(
        id=123,
        name="The Gamer Nation",
        icon=SimpleNamespace(url="https://cdn.example/icon.png"),
        banner=None,
        description="Roleplay and gaming",
        member_count=72,
        created_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
        vanity_url="https://discord.gg/gamernation",
        invites=None,
        members=[member],
        get_member=lambda user_id: member if user_id == 456 else None,
        fetch_member=lambda user_id: asyncio.sleep(0, result=member),
    )
    async def private(guild_id):
        return {"private": True}

    monkeypatch.setattr(routes, "_discord_bot", _tagged_profile_bot([guild], user, guild))
    monkeypatch.setattr(routes, "_guild_privacy", private)
    monkeypatch.setattr(routes._server, "run_on_bot_loop", _run_on_loop)

    server = app.test_client().get("/api/discord/users/456").get_json()["server_tag"]

    assert server == {
        "id": "123",
        "tag": "MOON",
        "badge_url": None,
        "available": True,
        "private": True,
        "viewer_is_member": False,
    }


def test_profile_payload_reports_membership_for_the_signed_in_viewer(monkeypatch):
    user = _tagged_profile_user(SimpleNamespace(id=123, tag="MOON", badge=None))
    member = _presence_member(user)
    viewer = SimpleNamespace(id=789)
    guild = SimpleNamespace(
        id=123,
        name="The Gamer Nation",
        icon=None,
        banner=None,
        description=None,
        member_count=72,
        approximate_presence_count=33,
        created_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
        vanity_url=None,
        # A normal invite must not turn into a Join button: Discord only offers
        # Join for a vanity invite.
        invites=lambda: asyncio.sleep(0, result=[SimpleNamespace(code="not-a-vanity")]),
        features=[],
        members=[member, viewer],
        get_member=lambda user_id: member if user_id == 456 else viewer if user_id == 789 else None,
        fetch_member=lambda user_id: asyncio.sleep(0, result=member if user_id == 456 else viewer if user_id == 789 else None),
    )
    async def public(guild_id):
        return {"private": False}

    monkeypatch.setattr(routes, "_discord_bot", _tagged_profile_bot([guild], user, guild))
    monkeypatch.setattr(routes, "_guild_privacy", public)
    monkeypatch.setattr(routes._server, "run_on_bot_loop", _run_on_loop)

    with app.test_client() as client:
        with client.session_transaction() as flask_session:
            flask_session["user"] = {"id": "789"}
        server = client.get("/api/discord/users/456").get_json()["server_tag"]

    assert server["available"] is True
    assert server["viewer_is_member"] is True
    assert "invite_url" not in server


def test_profile_payload_reports_a_server_niko_is_not_in(monkeypatch):
    user = _tagged_profile_user(SimpleNamespace(id=123, tag="MOON", badge=None))
    member = _presence_member(user)

    monkeypatch.setattr(routes, "_discord_bot", _tagged_profile_bot([], user, None))
    monkeypatch.setattr(routes._server, "run_on_bot_loop", _run_on_loop)

    server = app.test_client().get("/api/discord/users/456").get_json()["server_tag"]

    assert server["available"] is False
    assert server["private"] is False
    assert "name" not in server
    assert "invite_url" not in server


def test_public_discord_user_profile_re_reads_presence_on_every_request(monkeypatch):
    """A popup polls this endpoint, so every response reports the current status.

    The payload is rebuilt from the gateway's member cache on each request
    rather than frozen at the moment the popup was first opened.
    """
    user = _presence_user()
    member = _presence_member(user, status="online")
    monkeypatch.setattr(routes, "_discord_bot", _presence_bot([member], user))
    monkeypatch.setattr(routes._server, "run_on_bot_loop", _run_on_loop)
    client = app.test_client()

    assert client.get("/api/discord/users/456").get_json()["status"] == "online"
    member.status = SimpleNamespace(name="dnd")
    assert client.get("/api/discord/users/456").get_json()["status"] == "dnd"


def test_profile_popup_and_staff_cards_share_one_presence_lookup(monkeypatch):
    """The two surfaces read one presence, so they can never disagree."""
    user = _presence_user()
    custom = SimpleNamespace(type=SimpleNamespace(name="custom"), state="Writing docs", emoji=None)
    quiet = _presence_member(user, status="offline")
    active = _presence_member(user, status="idle", activities=[custom])
    bot = _presence_bot([quiet, active], user)
    monkeypatch.setattr(routes, "_discord_bot", bot)
    # The route reaches the loop through the shared namespace; the staff helper
    # the card is built from reads it from `runtime`.
    monkeypatch.setattr(routes._server, "run_on_bot_loop", _run_on_loop)
    monkeypatch.setattr(runtime, "_discord_bot", bot)
    monkeypatch.setattr(runtime, "run_on_bot_loop", _run_on_loop)

    popup = app.test_client().get("/api/discord/users/456").get_json()
    card = staff._staff_identity("456")

    assert popup["status"] == card["status"] == "idle"
    assert popup["custom_status"]["text"] == card["custom_status"]["text"] == "Writing docs"


def test_profile_badges_list_every_public_flag_discord_draws():
    # staff | hypesquad_bravery | early_supporter | bot_http_interactions
    flags = SimpleNamespace(value=(1 << 0) | (1 << 6) | (1 << 9) | (1 << 19))

    assert routes._profile_badges(SimpleNamespace(public_flags=flags), None) == [
        "staff", "hypesquad_bravery", "early_supporter", "supports_commands",
    ]


def test_profile_badges_skip_flags_without_a_badge():
    # MFA-enabled and verified e-mail are private settings, not badges.
    flags = SimpleNamespace(value=(1 << 4) | (1 << 5))

    assert routes._profile_badges(SimpleNamespace(public_flags=flags), None) == []


def test_profile_badges_combine_user_and_member_flags():
    user = SimpleNamespace(public_flags=SimpleNamespace(value=1 << 0))
    member = SimpleNamespace(public_flags=1 << 14)

    assert routes._profile_badges(user, member) == ["staff", "bug_hunter_level_2"]


def test_profile_badges_add_the_boosting_tier_for_a_long_streak():
    since = datetime.now(timezone.utc) - timedelta(days=300)
    member = SimpleNamespace(public_flags=0, premium_since=since)

    assert routes._boosting_badge(member) == "boosting_9_months"
    assert routes._profile_badges(None, member) == ["boosting_9_months"]


def test_profile_badges_skip_boosting_for_a_short_or_absent_streak():
    assert routes._boosting_badge(SimpleNamespace(premium_since=None)) is None
    assert routes._boosting_badge(None) is None
    # Boosting for a few weeks has no tier yet.
    assert routes._boosting_badge(
        SimpleNamespace(premium_since=datetime.now(timezone.utc) - timedelta(days=20))
    ) is None


def test_discord_text_endpoint_keeps_empty_resolutions_without_bot_loop(monkeypatch):
    monkeypatch.setattr(
        routes, "_discord_bot", SimpleNamespace(loop=SimpleNamespace(is_running=lambda: False))
    )
    response = app.test_client().post(
        "/api/discord/text",
        json={"guild_id": "123", "text": "<@456> <#321> <@&789>"},
    )

    assert response.status_code == 200
    assert response.get_json()["mention_names"] == {
        "user": {}, "channel": {}, "role": {}
    }
