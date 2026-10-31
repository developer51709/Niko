"""Staff lifecycle tests: suspension, demotion retention, and profile privacy."""

import asyncio
import re
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import cogs.staff.records as staff_cog  # noqa: E402
import utils.data_removal as removal  # noqa: E402
from config.ids import OWNER_IDS, SUPPORT_GUILD  # noqa: E402
from webapp import app  # noqa: E402
from webapp import auth, database, runtime, staff  # noqa: E402
from webapp import server as server_routes  # noqa: E402
from webapp.routes import staff_management_routes as management_routes  # noqa: E402


class SqlitePool:
    """Small async wrapper over an in-memory SQLite staff roster."""

    def __init__(self, rows=True):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        if rows:
            self.conn.execute(
                """
                CREATE TABLE staff_members (
                    user_id INTEGER PRIMARY KEY,
                    role TEXT NOT NULL,
                    assigned_by INTEGER NOT NULL,
                    assigned_at REAL NOT NULL,
                    public_name TEXT,
                    public_bio TEXT,
                    public_avatar_url TEXT,
                    public_banner_url TEXT,
                    public_links TEXT,
                    public_visible INTEGER NOT NULL DEFAULT 1,
                    staff_status TEXT NOT NULL DEFAULT 'active',
                    status_reason TEXT,
                    status_changed_by INTEGER,
                    status_changed_at REAL
                )
                """
            )
            self.conn.commit()

    @staticmethod
    def _convert(query):
        return re.sub(r"\$\d+", "?", query)

    async def execute(self, query, *args):
        self.conn.execute(self._convert(query), args)
        self.conn.commit()

    async def fetch(self, query, *args):
        return [
            dict(row)
            for row in self.conn.execute(self._convert(query), args).fetchall()
        ]

    async def fetchrow(self, query, *args):
        row = self.conn.execute(self._convert(query), args).fetchone()
        return dict(row) if row else None

    async def fetchval(self, query, *args):
        row = self.conn.execute(self._convert(query), args).fetchone()
        return row[0] if row else None


def _seed(pool, user_id=10, role="moderator", status="active", visible=1):
    pool.conn.execute(
        "INSERT INTO staff_members (user_id, role, assigned_by, assigned_at, "
        "public_name, public_bio, public_avatar_url, public_banner_url, public_links, "
        "public_visible, staff_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            user_id, role, 99, 1700000000, "Test Staff", "A long public bio.",
            "https://cdn.example/avatar.png", "https://cdn.example/banner.png",
            '[{"type":"github","url":"https://github.com/example"}]', visible, status,
        ),
    )
    pool.conn.commit()


def _bot(pool, guild=None):
    return SimpleNamespace(cxn=pool, get_guild=lambda guild_id: guild)


def test_suspension_blocks_access_and_lift_restores_the_stored_role():
    async def check():
        pool = SqlitePool()
        _seed(pool)
        bot = _bot(pool)

        assert await staff_cog.get_staff_role(bot, 10) == "moderator"
        assert await staff_cog.set_staff_suspension(
            bot, 10, True, 99, reason="Potential staff guideline breach",
        ) == "suspended"

        row = pool.conn.execute(
            "SELECT role, staff_status, status_reason, public_bio FROM staff_members WHERE user_id = 10"
        ).fetchone()
        assert row["role"] == "moderator"
        assert row["staff_status"] == "suspended"
        assert row["status_reason"] == "Potential staff guideline breach"
        assert row["public_bio"] == "A long public bio."
        assert await staff_cog.get_staff_role(bot, 10) is None

        # Changing the role during an investigation must not silently lift it.
        assert await staff_cog.set_staff_role(bot, 10, "support", 99) == "suspended"
        assert await staff_cog.get_staff_role(bot, 10) is None

        assert await staff_cog.set_staff_suspension(bot, 10, False, 99) == "active"
        assert await staff_cog.get_staff_role(bot, 10) == "support"

    asyncio.run(check())


def test_website_staff_authorization_denies_suspended_and_former_records(monkeypatch):
    from flask import session as flask_session

    pool = SqlitePool()
    _seed(pool, user_id=10, role="moderator", status="suspended")
    _seed(pool, user_id=11, role="support", status="former")
    _seed(pool, user_id=12, role="head_support", status="active")
    monkeypatch.setattr(
        runtime, "_discord_bot", SimpleNamespace(cxn=pool, guilds=[]),
    )
    monkeypatch.setattr(runtime, "run_on_bot_loop", lambda awaitable: asyncio.run(awaitable))
    monkeypatch.setattr(database, "sqlite_connect", lambda: None)

    with app.test_request_context("/"):
        flask_session["user"] = {"id": "10"}
        assert staff._current_staff_role() is None
        flask_session["user"] = {"id": "11"}
        assert staff._current_staff_role() is None
        flask_session["user"] = {"id": "12"}
        assert staff._current_staff_role() == "head_support"


def test_demotion_retains_the_profile_and_hides_the_role():
    async def check():
        pool = SqlitePool()
        _seed(pool)
        bot = _bot(pool)

        assert await staff_cog.set_staff_role(
            bot, 10, None, 99, reason="Stepped down",
        ) == "former"
        row = pool.conn.execute(
            "SELECT role, staff_status, public_bio, public_banner_url, public_links, public_visible "
            "FROM staff_members WHERE user_id = 10"
        ).fetchone()
        assert row["role"] == "moderator"
        assert row["staff_status"] == "former"
        assert row["public_bio"] == "A long public bio."
        assert row["public_banner_url"] == "https://cdn.example/banner.png"
        assert "github.com/example" in row["public_links"]
        assert row["public_visible"] == 1
        assert await staff_cog.get_staff_role(bot, 10) is None

        # Rehiring keeps the retained public profile instead of replacing the row.
        assert await staff_cog.set_staff_role(bot, 10, "head_support", 99) == "active"
        row = pool.conn.execute(
            "SELECT role, staff_status, public_bio FROM staff_members WHERE user_id = 10"
        ).fetchone()
        assert row["role"] == "head_support"
        assert row["staff_status"] == "active"
        assert row["public_bio"] == "A long public bio."
        assert await staff_cog.get_staff_role(bot, 10) == "head_support"

    asyncio.run(check())


def test_suspension_removes_and_lift_restores_official_discord_roles():
    async def check():
        pool = SqlitePool()
        _seed(pool)

        shared = SimpleNamespace(id=1)
        moderator = SimpleNamespace(id=2)
        head_admin = SimpleNamespace(id=3)
        role_map = {"staff": "1", "moderator": "2", "head_admin": "3"}

        class Member:
            def __init__(self):
                self.roles = [shared, moderator]
                self.removed = []
                self.added = []
                self.guild = None

            async def remove_roles(self, *roles, reason):
                self.removed.extend(role.id for role in roles)
                for role in roles:
                    if role in self.roles:
                        self.roles.remove(role)

            async def add_roles(self, *roles, reason):
                self.added.extend(role.id for role in roles)
                for role in roles:
                    if role not in self.roles:
                        self.roles.append(role)

        member = Member()
        guild = SimpleNamespace(
            id=SUPPORT_GUILD,
            get_role=lambda role_id: {"1": shared, "2": moderator, "3": head_admin}.get(str(role_id)),
            get_member=lambda user_id: member,
        )
        member.guild = guild
        bot = _bot(pool, guild)
        with patch.object(
            staff_cog, "get_support_ids", new=AsyncMock(return_value={"roles": role_map}),
        ):
            await staff_cog.set_staff_suspension(bot, 10, True, 99, reason="Investigation")
            assert set(member.removed) == {1, 2}
            assert member.added == []

            await staff_cog.set_staff_suspension(bot, 10, False, 99)
            assert set(member.added) == {1, 2}

    asyncio.run(check())


def test_public_roster_hides_suspended_and_former_profiles(monkeypatch):
    pool = SqlitePool()
    _seed(pool, user_id=101, role="moderator", status="active", visible=1)
    _seed(pool, user_id=102, role="support", status="active", visible=0)
    _seed(pool, user_id=103, role="head_support", status="suspended", visible=1)
    _seed(pool, user_id=104, role="graphic_designer", status="former", visible=1)

    monkeypatch.setattr(
        runtime, "_discord_bot", SimpleNamespace(cxn=pool, guilds=[]),
    )
    monkeypatch.setattr(runtime, "run_on_bot_loop", lambda awaitable: asyncio.run(awaitable))
    monkeypatch.setattr(database, "sqlite_connect", lambda: None)
    monkeypatch.setattr(
        staff,
        "_staff_identity",
        lambda user_id: {
            "id": str(user_id), "name": f"Staff {user_id}", "username": None,
            "avatar_url": None, "status": "offline", "status_label": "Offline",
            "activities": [], "custom_status": None, "activity": None,
        },
    )

    public = staff._load_staff_rows()
    ids = {member["id"] for member in public}
    assert "101" in ids
    assert "102" not in ids  # member hid their own listing
    assert "103" not in ids  # suspended access is hidden
    assert "104" not in ids  # former staff profile is retained but hidden

    management = staff._load_staff_management_rows()
    managed = {member["id"]: member for member in management}
    assert managed["103"]["staff_status"] == "suspended"
    assert managed["104"]["staff_status"] == "former"
    assert managed["104"]["profile_visible"] is True
    assert managed["104"]["visible"] is False

    hidden = staff._load_staff_rows()
    assert all(member["staff_status"] == "active" for member in hidden)


def test_data_deletion_clears_the_public_staff_profile_but_not_the_role():
    async def check():
        pool = SqlitePool()
        _seed(pool, user_id=10, role="moderator", status="former")
        with patch.object(removal, "_delete_music_data", new=AsyncMock()):
            result = await removal.execute_account_deletion(pool, 10)

        row = pool.conn.execute(
            "SELECT role, staff_status, public_name, public_bio, public_avatar_url, "
            "public_banner_url, public_links, public_visible FROM staff_members WHERE user_id = 10"
        ).fetchone()
        assert row["role"] == "moderator"
        assert row["staff_status"] == "former"
        for field in ("public_name", "public_bio", "public_avatar_url", "public_banner_url", "public_links"):
            assert row[field] is None, field
        assert row["public_visible"] == 0
        assert "staff_members:public_profile" in result["removed"]
        assert result["preserved"]

    asyncio.run(check())


def _signed_in_client():
    client = app.test_client()
    with client.session_transaction() as session:
        session["user"] = {"id": "99"}
        session["access_token"] = "test-token"
        session["token_exp"] = 9999999999
        session["csrf_token"] = "test-csrf"
    return client


def test_staff_management_api_is_owner_only_and_records_the_action(monkeypatch):
    client = _signed_in_client()
    monkeypatch.setattr(auth, "_current_user_blacklist_entry", lambda: None)

    monkeypatch.setattr(management_routes, "_current_staff_role", lambda: "head_admin")
    assert client.get("/api/staff/members").status_code == 403

    monkeypatch.setattr(management_routes, "_current_staff_role", lambda: "owner")
    monkeypatch.setattr(management_routes, "_discord_bot", SimpleNamespace())
    monkeypatch.setattr(
        management_routes,
        "run_on_bot_loop",
        lambda awaitable: asyncio.run(awaitable),
    )
    monkeypatch.setattr(
        server_routes,
        "_load_staff_management_rows",
        lambda: [{
            "id": "10", "name": "Staff Ten", "role": "moderator",
            "role_label": "Moderator", "staff_status": "active",
            "staff_status_label": "Active", "visible": True,
        }],
    )

    listed = client.get("/api/staff/members")
    assert listed.status_code == 200
    payload = listed.get_json()
    assert payload["members"][0]["id"] == "10"
    assert any(role["key"] == "moderator" for role in payload["roles"])

    suspend = AsyncMock(return_value="suspended")
    with patch.object(staff_cog, "set_staff_suspension", new=suspend):
        response = client.post(
            "/api/staff/members/10/manage",
            json={"action": "suspend", "reason": "Safety investigation"},
            headers={"X-CSRF-Token": "test-csrf"},
        )
    assert response.status_code == 200
    assert response.get_json()["status"] == "suspended"
    suspend.assert_awaited_once()
    assert suspend.await_args.args[1:4] == (10, True, 99)

    short_reason = client.post(
        "/api/staff/members/10/manage",
        json={"action": "suspend", "reason": "x"},
        headers={"X-CSRF-Token": "test-csrf"},
    )
    assert short_reason.status_code == 400


def test_owner_accounts_cannot_be_managed_through_the_roster(monkeypatch):
    client = _signed_in_client()
    monkeypatch.setattr(auth, "_current_user_blacklist_entry", lambda: None)
    monkeypatch.setattr(management_routes, "_current_staff_role", lambda: "owner")
    monkeypatch.setattr(management_routes, "_discord_bot", SimpleNamespace())
    owner_id = next(iter(OWNER_IDS))
    response = client.post(
        f"/api/staff/members/{owner_id}/manage",
        json={"action": "demote"},
        headers={"X-CSRF-Token": "test-csrf"},
    )
    assert response.status_code == 403
