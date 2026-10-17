"""Tests for shared Discord text mention resolution API."""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import app
from webapp import discord_text_routes as routes


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

    monkeypatch.setattr(routes._server.req, "get", fake_get)
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
    monkeypatch.setattr(routes._server, "_discord_bot", bot)
    monkeypatch.setattr(routes._server, "run_on_bot_loop", _run_on_loop)

    popup = app.test_client().get("/api/discord/users/456").get_json()
    staff = routes._server._staff_identity("456")

    assert popup["status"] == staff["status"] == "idle"
    assert popup["custom_status"]["text"] == staff["custom_status"]["text"] == "Writing docs"


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
