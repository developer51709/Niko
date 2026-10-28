"""The gift page lists exactly the mutual servers the member is in.

The list used to be built from the gateway's member cache, so any server whose
members had not been chunked silently disappeared from the page even though the
member was in it and Niko was installed. It is now the member's own OAuth guild
list intersected with the guilds Niko is in, which is what "mutual" means.
"""

import asyncio
import sys
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from webapp import auth  # noqa: E402
from webapp.routes import premium_routes  # noqa: E402


class EmptyPool:
    """A database that has never seen a subscription."""

    async def fetchrow(self, *_args, **_kwargs):
        return None


def _guild(guild_id: int, name: str, *, member_cached: bool = True):
    """One guild as the gateway exposes it.

    ``member_cached=False`` is the real large-guild case: ``get_member`` only
    answers for members the gateway has actually chunked.
    """

    return SimpleNamespace(
        id=guild_id,
        name=name,
        icon=None,
        member_count=10,
        get_member=lambda user_id: SimpleNamespace(id=user_id) if member_cached else None,
    )


def _client() -> "object":
    client = premium_routes.app.test_client()
    with client.session_transaction() as session:
        session["user"] = {"id": "7", "username": "Tester"}
        session["access_token"] = "token"
        session["token_exp"] = time.time() + 3600
    return client


def _prepare(monkeypatch, *, joined, bot_guilds, guilds):
    by_id = {int(guild.id): guild for guild in guilds}
    bot = SimpleNamespace(
        cxn=EmptyPool(),
        guilds=list(guilds),
        get_guild=lambda guild_id: by_id.get(int(guild_id)),
    )
    monkeypatch.setattr(premium_routes, "_discord_bot", bot)
    monkeypatch.setattr(premium_routes, "_billing_bot", lambda: bot)
    monkeypatch.setattr(premium_routes, "member_guilds", lambda token: joined)
    monkeypatch.setattr(premium_routes, "bot_guild_ids", lambda: set(bot_guilds))
    monkeypatch.setattr(
        premium_routes, "run_on_bot_loop", lambda awaitable, timeout=8: asyncio.run(awaitable)
    )
    return _client()


def test_an_unchunked_guild_still_appears(monkeypatch):
    """The gateway member cache is not the membership list."""
    response = _prepare(
        monkeypatch,
        joined=[{"id": "1"}, {"id": "2"}],
        bot_guilds={"1", "2"},
        guilds=[_guild(1, "Small server"), _guild(2, "Big server", member_cached=False)],
    ).get("/api/premium/gift-targets")

    assert response.status_code == 200
    assert [guild["id"] for guild in response.get_json()["guilds"]] == ["2", "1"]


def test_only_mutual_guilds_are_listed(monkeypatch):
    """A guild the member is not in, or Niko is not in, is not a gift target."""
    response = _prepare(
        monkeypatch,
        joined=[{"id": "1"}, {"id": "3"}],
        bot_guilds={"1", "2"},
        guilds=[_guild(1, "Mutual"), _guild(2, "Niko only"), _guild(3, "Member only")],
    ).get("/api/premium/gift-targets")

    assert response.status_code == 200
    assert [guild["id"] for guild in response.get_json()["guilds"]] == ["1"]


def test_a_failed_member_read_is_reported_instead_of_an_empty_list(monkeypatch):
    """An egress failure must not look like "you are in no servers"."""
    client = _prepare(
        monkeypatch, joined=[], bot_guilds={"1"}, guilds=[_guild(1, "Mutual")]
    )

    def unavailable(token):
        raise auth.DiscordEgressError("Discord answered HTTP 403 for the server list.", status=403)

    monkeypatch.setattr(premium_routes, "member_guilds", unavailable)
    response = client.get("/api/premium/gift-targets")

    assert response.status_code == 503
    assert "error" in response.get_json()


def test_a_revoked_session_asks_for_a_new_login(monkeypatch):
    """A 401 is the session, not an outage, so the page can re-authenticate."""
    client = _prepare(monkeypatch, joined=[], bot_guilds=set(), guilds=[])

    def revoked(token):
        raise auth.DiscordEgressError("Discord answered HTTP 401.", status=401)

    monkeypatch.setattr(premium_routes, "member_guilds", revoked)
    response = client.get("/api/premium/gift-targets")

    assert response.status_code == 401
    assert response.get_json()["login_url"] == "/auth/login"
