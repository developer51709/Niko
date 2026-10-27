"""Security tests for owner-only official Niko team recruitment APIs."""

import asyncio
import sys
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config.ids import OWNER_IDS
from webapp import app
from webapp import server as server_routes
from webapp import auth, runtime, staff  # noqa: E402
from webapp import runtime  # noqa: E402
from webapp.routes import team_recruitment_routes as routes


class StaffIdentityFallbackTests(unittest.TestCase):
    def test_staff_identity_fetches_user_when_standby_cache_is_empty(self):
        fetched_ids = []

        class FakeBot:
            guilds = []

            def get_user(self, user_id):
                return None

            async def fetch_user(self, user_id):
                fetched_ids.append(user_id)
                return SimpleNamespace(
                    global_name="Team Display Name",
                    name="team_handle",
                    display_avatar=SimpleNamespace(url="https://cdn.example/staff-avatar.png"),
                )

        with patch.object(runtime, "_discord_bot", FakeBot()), patch.object(
            runtime, "run_on_bot_loop", side_effect=lambda awaitable: asyncio.run(awaitable)
        ), patch.dict(staff._staff_user_identity_cache, {}, clear=True):
            first_identity = staff._staff_identity("123456789")
            second_identity = staff._staff_identity("123456789")

        self.assertEqual([123456789], fetched_ids)
        for identity in (first_identity, second_identity):
            self.assertEqual("Team Display Name", identity["name"])
            self.assertEqual("team_handle", identity["username"])
            self.assertEqual("https://cdn.example/staff-avatar.png", identity["avatar_url"])


class TeamRecruitmentAuthorizationTests(unittest.TestCase):
    def test_eligibility_questions_are_staged_and_do_not_reveal_age_threshold(self):
        questions = routes._eligibility_questions()
        age_question = next(question for question in questions if question["id"] == "niko_age")
        self.assertNotIn("16", age_question["prompt"])
        self.assertEqual(
            [question["id"] for question in questions],
            ["eligibility_guidelines", "eligibility_confidentiality", "niko_age", "eligibility_availability"],
        )
        for role_key in routes.TEAM_ROLE_APPLICATIONS:
            combined = routes._opening_questions(role_key)
            self.assertEqual(combined[:len(questions)], questions)
            self.assertEqual(routes._application_id(role_key), f"team-{role_key}")

    def test_eligibility_validator_enforces_policy_without_showing_it_in_question(self):
        answers = {
            "eligibility_guidelines": "yes",
            "eligibility_confidentiality": "yes",
            "niko_age": "16",
            "eligibility_availability": "yes",
        }
        self.assertTrue(routes._is_eligible_answer_set(answers))
        self.assertTrue(routes._valid_eligibility(answers))
        answers["niko_age"] = "15"
        self.assertFalse(routes._valid_eligibility(answers))
        answers["niko_age"] = "16"
        answers["eligibility_guidelines"] = "no"
        self.assertFalse(routes._valid_eligibility(answers))

    def test_decision_messages_are_components_v2_and_role_specific(self):
        for role_key, next_steps in routes.APPROVAL_NEXT_STEPS.items():
            with self.subTest(role=role_key):
                view = routes._review_dm_view(role_key, "approved")
                self.assertIsInstance(view, routes.discord.ui.LayoutView)
                container = view.children[0]
                self.assertIsInstance(container, routes.discord.ui.Container)
                content = container.children[0].content
                self.assertIn("Welcome to the Niko team", content)
                self.assertIn(routes._role_label(role_key), content)
                self.assertTrue(all(step in content for step in next_steps))

        denied = routes._review_dm_view("moderator", "denied")
        denied_content = denied.children[0].children[0].content
        self.assertIn("won’t be moving forward", denied_content)
        self.assertIn("Please don’t be discouraged", denied_content)

    def test_review_assigns_role_sends_dm_then_saves_the_decision(self):
        events = []
        saved_updates = []

        class FakeRole:
            id = 123
            name = "Moderator"

        class FakeMember:
            def __init__(self):
                self.roles = []

            async def add_roles(self, role, *, reason):
                self.roles.append(role)
                events.append(("role", role.name, reason))

            async def remove_roles(self, role, *, reason):
                self.roles.remove(role)
                events.append(("rollback", role.name, reason))

        member = FakeMember()
        role = FakeRole()

        class FakeGuild:
            roles = [role]

            def get_role(self, role_id):
                return role if role_id == role.id else None

            def get_member(self, user_id):
                return member

        class FakeUser:
            async def send(self, *, view):
                events.append(("dm", view))

        class FakeBot:
            def get_user(self, user_id):
                self.requested_user_id = user_id
                return FakeUser()

            def get_guild(self, guild_id):
                return FakeGuild()

        class FakePool:
            async def fetchrow(self, query, *params):
                if "staff_members" in query:
                    return None
                return {"user_id": params[-1]}

            async def execute(self, query, *params):
                saved_updates.append(params)
                events.append(("saved", params))

        client = app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": str(next(iter(OWNER_IDS)))}
            session["access_token"] = "test-token"
            session["token_exp"] = time.time() + 3600
            session["csrf_token"] = "test-csrf"

        with patch.object(auth, "_current_user_blacklist_entry", return_value=None), patch.object(
            routes, "_pool", return_value=FakePool()
        ), patch.object(routes, "_discord_bot", FakeBot()), patch.object(
            routes, "run_on_bot_loop", side_effect=lambda awaitable: asyncio.run(awaitable)
        ):
            response = client.post(
                "/api/staff/team-recruitment/team-moderator/submissions/123/review",
                json={"status": "approved"},
                headers={"X-CSRF-Token": "test-csrf"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["review_status"], "approved")
        self.assertTrue(response.get_json()["dm_sent"])
        self.assertEqual(len([event for event in events if event[0] == "dm"]), 1)
        self.assertEqual(len(saved_updates), 3)
        self.assertEqual(saved_updates[0][0], "moderator")
        self.assertEqual(saved_updates[0][1], next(iter(OWNER_IDS)))
        self.assertEqual(saved_updates[1][0], 123)
        self.assertEqual(saved_updates[2][0], "approved")
        self.assertEqual([event[0] for event in events], ["role", "saved", "saved", "saved", "dm"])
        self.assertIn(role, member.roles)

    def test_review_keeps_approval_when_decision_dm_fails(self):
        events = []

        class FakeRole:
            id = 123
            name = "Moderator"

        class FakeMember:
            def __init__(self):
                self.roles = []

            async def add_roles(self, role, *, reason):
                self.roles.append(role)
                events.append("role-added")

            async def remove_roles(self, role, *, reason):
                self.roles.remove(role)
                events.append("role-removed")

        member = FakeMember()
        role = FakeRole()

        class FakeGuild:
            roles = [role]

            def get_role(self, role_id):
                return role if role_id == role.id else None

            def get_member(self, user_id):
                return member

        class FakeUser:
            async def send(self, *, view):
                events.append("dm-failed")
                raise routes.discord.Forbidden(response=None, message="DMs disabled")

        class FakeBot:
            cxn = object()

            def get_user(self, user_id):
                return FakeUser()

            def get_guild(self, guild_id):
                return FakeGuild()

        class FakePool:
            async def fetchrow(self, query, *params):
                if "staff_members" in query:
                    return None
                return {"user_id": params[-1]}

            async def execute(self, query, *params):
                events.append("staff-saved" if "staff_members" in query else "review-saved")

        client = app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": str(next(iter(OWNER_IDS)))}
            session["access_token"] = "test-token"
            session["token_exp"] = time.time() + 3600
            session["csrf_token"] = "test-csrf"

        with patch.object(auth, "_current_user_blacklist_entry", return_value=None), patch.object(
            routes, "_pool", return_value=FakePool()
        ), patch.object(routes, "_discord_bot", FakeBot()), patch.object(
            routes, "run_on_bot_loop", side_effect=lambda awaitable: asyncio.run(awaitable)
        ):
            response = client.post(
                "/api/staff/team-recruitment/team-moderator/submissions/123/review",
                json={"status": "approved"},
                headers={"X-CSRF-Token": "test-csrf"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertTrue(body["ok"])
        self.assertEqual(body["review_status"], "approved")
        self.assertEqual(body["previous_status"], "pending")
        self.assertFalse(body["unchanged"])
        self.assertFalse(body["dm_sent"])
        self.assertFalse(body["role_revoked"])
        self.assertEqual(events, ["role-added", "staff-saved", "staff-saved", "review-saved", "dm-failed"])
        self.assertIn(role, member.roles)

    def test_staff_persistence_failure_rolls_back_new_discord_role(self):
        events = []

        class FakeRole:
            id = 123
            name = "Moderator"

        class FakeMember:
            def __init__(self):
                self.roles = []

            async def add_roles(self, role, *, reason):
                self.roles.append(role)
                events.append("role-added")

            async def remove_roles(self, role, *, reason):
                self.roles.remove(role)
                events.append("role-removed")

        member = FakeMember()
        role = FakeRole()

        class FakeGuild:
            roles = [role]

            def get_role(self, role_id):
                return role if role_id == role.id else None

            def get_member(self, user_id):
                return member

        class FakeBot:
            cxn = object()

            def get_guild(self, guild_id):
                return FakeGuild()

        class FakePool:
            async def fetchrow(self, query, *params):
                if "staff_members" in query:
                    return None
                return {"user_id": params[-1]}

            async def execute(self, query, *params):
                if "staff_members" in query:
                    events.append("staff-write-failed")
                    raise RuntimeError("database unavailable")
                events.append("review-saved")

        client = app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": str(next(iter(OWNER_IDS)))}
            session["access_token"] = "test-token"
            session["token_exp"] = time.time() + 3600
            session["csrf_token"] = "test-csrf"

        with patch.object(auth, "_current_user_blacklist_entry", return_value=None), patch.object(
            routes, "_pool", return_value=FakePool()
        ), patch.object(routes, "_discord_bot", FakeBot()), patch.object(
            routes, "run_on_bot_loop", side_effect=lambda awaitable: asyncio.run(awaitable)
        ):
            response = client.post(
                "/api/staff/team-recruitment/team-moderator/submissions/123/review",
                json={"status": "approved"},
                headers={"X-CSRF-Token": "test-csrf"},
            )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(events, ["role-added", "staff-write-failed", "role-removed"])
        self.assertEqual(member.roles, [])

    def test_approval_saves_staff_role_through_shared_pool(self):
        events = []

        class FakeRole:
            id = 123
            name = "Moderator"

        class FakeMember:
            roles = []

            async def add_roles(self, role, *, reason):
                self.roles.append(role)

        member = FakeMember()
        role = FakeRole()

        class FakeGuild:
            roles = [role]

            def get_role(self, role_id):
                return role if role_id == role.id else None

            def get_member(self, user_id):
                return member

        class FakeUser:
            async def send(self, *, view):
                events.append("dm")

        class FakeBot:
            def get_guild(self, guild_id):
                return FakeGuild()

            def get_user(self, user_id):
                return FakeUser()

        class FakePool:
            async def fetchrow(self, query, *params):
                if "staff_members" in query:
                    return None
                return {"user_id": params[-1]}

            async def execute(self, query, *params):
                events.append((query, params))

        client = app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": str(next(iter(OWNER_IDS)))}
            session["access_token"] = "test-token"
            session["token_exp"] = time.time() + 3600
            session["csrf_token"] = "test-csrf"

        with patch.object(auth, "_current_user_blacklist_entry", return_value=None), patch.object(
            routes, "_pool", return_value=FakePool()
        ), patch.object(routes, "_discord_bot", FakeBot()), patch.object(
            routes, "run_on_bot_loop", side_effect=lambda awaitable: asyncio.run(awaitable)
        ):
            response = client.post(
                "/api/staff/team-recruitment/team-moderator/submissions/123/review",
                json={"status": "approved"},
                headers={"X-CSRF-Token": "test-csrf"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [event[0] if isinstance(event, tuple) else event for event in events],
            [
                "UPDATE staff_members SET role = $1, assigned_by = $2, assigned_at = $3, staff_status = $4, status_reason = NULL, status_changed_by = $5, status_changed_at = $6 WHERE user_id = $7",
                "INSERT OR IGNORE INTO staff_members (user_id, role, assigned_by, assigned_at, staff_status, status_changed_by, status_changed_at) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                "UPDATE staff_team_submissions SET review_status = $1, reviewed_by = $2, reviewed_at = datetime('now') WHERE opening_id = $3 AND user_id = $4",
                "dm",
            ],
        )
        self.assertEqual(events[0][1][0], "moderator")
        self.assertIn(role, member.roles)

    def test_review_rolls_back_new_role_when_decision_dm_fails(self):
        events = []

        class FakeRole:
            id = 123
            name = "Moderator"

        class FakeMember:
            roles = []

            async def add_roles(self, role, *, reason):
                self.roles.append(role)
                events.append("role-added")

            async def remove_roles(self, role, *, reason):
                self.roles.remove(role)
                events.append("role-removed")

        member = FakeMember()
        role = FakeRole()

        class FakeGuild:
            roles = [role]

            def get_role(self, role_id):
                return role if role_id == role.id else None

            def get_member(self, user_id):
                return member

        class FakeUser:
            async def send(self, *, view):
                raise routes.discord.Forbidden(response=None, message="DMs disabled")

        class FakeBot:
            def get_user(self, user_id):
                return FakeUser()

            def get_guild(self, guild_id):
                return FakeGuild()

        class FakePool:
            async def fetchrow(self, query, *params):
                if "staff_members" in query:
                    return None
                return {"user_id": params[-1]}

            async def execute(self, query, *params):
                events.append("saved")

        client = app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": str(next(iter(OWNER_IDS)))}
            session["access_token"] = "test-token"
            session["token_exp"] = time.time() + 3600
            session["csrf_token"] = "test-csrf"

        with patch.object(auth, "_current_user_blacklist_entry", return_value=None), patch.object(
            routes, "_pool", return_value=FakePool()
        ), patch.object(routes, "_discord_bot", FakeBot()), patch.object(
            routes, "run_on_bot_loop", side_effect=lambda awaitable: asyncio.run(awaitable)
        ):
            response = client.post(
                "/api/staff/team-recruitment/team-moderator/submissions/123/review",
                json={"status": "approved"},
                headers={"X-CSRF-Token": "test-csrf"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["review_status"], "approved")
        self.assertFalse(response.get_json()["dm_sent"])
        self.assertEqual(events[:3], ["role-added", "saved", "saved"])
        self.assertNotIn("role-removed", events)
        self.assertIn(role, member.roles)

    def test_review_denial_does_not_assign_a_team_role(self):
        events = []

        class FakeUser:
            async def send(self, *, view):
                events.append("dm")

        class FakeBot:
            def get_user(self, user_id):
                return FakeUser()

            def get_guild(self, guild_id):
                raise AssertionError("Denials must not look up or assign a staff role")

        class FakePool:
            async def fetchrow(self, query, *params):
                if "staff_members" in query:
                    return None
                return {"user_id": params[-1]}

            async def execute(self, query, *params):
                events.append("saved")

        client = app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": str(next(iter(OWNER_IDS)))}
            session["access_token"] = "test-token"
            session["token_exp"] = time.time() + 3600
            session["csrf_token"] = "test-csrf"

        with patch.object(auth, "_current_user_blacklist_entry", return_value=None), patch.object(
            routes, "_pool", return_value=FakePool()
        ), patch.object(routes, "_discord_bot", FakeBot()), patch.object(
            routes, "run_on_bot_loop", side_effect=lambda awaitable: asyncio.run(awaitable)
        ):
            response = client.post(
                "/api/staff/team-recruitment/team-moderator/submissions/123/review",
                json={"status": "denied"},
                headers={"X-CSRF-Token": "test-csrf"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(events, ["saved", "dm"])

    def test_review_denial_revokes_a_previous_approval(self):
        events = []

        class FakeRole:
            id = 123
            name = "Moderator"

        role = FakeRole()

        class FakeMember:
            roles = [role]

            async def remove_roles(self, one, *, reason):
                self.roles.remove(one)
                events.append("role-removed")

        member = FakeMember()

        class FakeGuild:
            roles = [role]

            def get_role(self, role_id):
                return role if role_id == role.id else None

            def get_member(self, user_id):
                return member

        class FakeUser:
            async def send(self, *, view):
                events.append("dm")

        class FakeBot:
            def get_guild(self, guild_id):
                return FakeGuild()

            def get_user(self, user_id):
                return FakeUser()

        class FakePool:
            async def fetchrow(self, query, *params):
                return {"user_id": params[1], "review_status": "approved"}

            async def execute(self, query, *params):
                events.append((query, params))

        client = app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": str(next(iter(OWNER_IDS)))}
            session["access_token"] = "test-token"
            session["token_exp"] = time.time() + 3600
            session["csrf_token"] = "test-csrf"

        with patch.object(auth, "_current_user_blacklist_entry", return_value=None), patch.object(
            routes, "_pool", return_value=FakePool()
        ), patch.object(routes, "_discord_bot", FakeBot()), patch.object(
            routes, "run_on_bot_loop", side_effect=lambda awaitable: asyncio.run(awaitable)
        ):
            response = client.post(
                "/api/staff/team-recruitment/team-moderator/submissions/123/review",
                json={"status": "denied"},
                headers={"X-CSRF-Token": "test-csrf"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["review_status"], "denied")
        self.assertEqual(body["previous_status"], "approved")
        self.assertFalse(body["unchanged"])
        self.assertTrue(body["role_revoked"])
        self.assertNotIn(role, member.roles)
        self.assertEqual([event for event in events if isinstance(event, str)], ["role-removed", "dm"])
        statements = [event[0] for event in events if isinstance(event, tuple)]
        self.assertIn(
            "UPDATE staff_members SET staff_status = $1, status_reason = $2, status_changed_by = $3, status_changed_at = $4 WHERE user_id = $5 AND role = $6",
            statements,
        )
        self.assertIn(
            "UPDATE staff_team_submissions SET review_status = $1, reviewed_by = $2, reviewed_at = datetime('now') WHERE opening_id = $3 AND user_id = $4",
            statements,
        )

    def test_repeating_a_recorded_decision_changes_nothing(self):
        events = []

        class FakeBot:
            def get_guild(self, guild_id):
                raise AssertionError("A repeated decision must not touch the Discord role")

            def get_user(self, user_id):
                raise AssertionError("A repeated decision must not send another DM")

        class FakePool:
            async def fetchrow(self, query, *params):
                return {"user_id": params[1], "review_status": "approved"}

            async def execute(self, *args, **kwargs):
                events.append("saved")

        client = app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": str(next(iter(OWNER_IDS)))}
            session["access_token"] = "test-token"
            session["token_exp"] = time.time() + 3600
            session["csrf_token"] = "test-csrf"

        with patch.object(auth, "_current_user_blacklist_entry", return_value=None), patch.object(
            routes, "_pool", return_value=FakePool()
        ), patch.object(routes, "_discord_bot", FakeBot()), patch.object(
            routes, "run_on_bot_loop", side_effect=lambda awaitable: asyncio.run(awaitable)
        ):
            response = client.post(
                "/api/staff/team-recruitment/team-moderator/submissions/123/review",
                json={"status": "approved"},
                headers={"X-CSRF-Token": "test-csrf"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertTrue(body["unchanged"])
        self.assertEqual(body["previous_status"], "approved")
        self.assertIsNone(body["dm_sent"])
        self.assertFalse(body["role_revoked"])
        self.assertEqual(events, [])

    def test_guild_administrator_cannot_manage_or_review_team_recruitment(self):
        endpoints = [
            ("get", "/api/staff/team-recruitment", None),
            ("post", "/api/staff/team-recruitment/opening/status", {"status": "closed"}),
            ("get", "/api/staff/team-recruitment/opening/submissions", None),
            (
                "post",
                "/api/staff/team-recruitment/opening/submissions/123/review",
                {"status": "approved"},
            ),
        ]

        def unexpected_database_access():
            raise AssertionError("A non-owner reached official recruitment data")

        with patch.object(auth, "_current_user_blacklist_entry", return_value=None), patch.object(
            routes, "_pool", side_effect=unexpected_database_access
        ):
            client = app.test_client()
            with client.session_transaction() as session:
                # Guild administrator claims must not grant owner-only authority.
                session["user"] = {
                    "id": "999999999999999999",
                    "guild_permissions": ["ADMINISTRATOR"],
                }
                session["access_token"] = "test-token"
                session["token_exp"] = time.time() + 3600
                session["csrf_token"] = "test-csrf"

            for method, path, payload in endpoints:
                with self.subTest(method=method, path=path):
                    response = getattr(client, method)(
                        path,
                        json=payload,
                        headers={"X-CSRF-Token": "test-csrf"} if method == "post" else None,
                    )
                    self.assertEqual(response.status_code, 403)
                    self.assertIn("owner", response.get_json()["error"].lower())

def test_suspended_staff_cannot_be_reapproved_until_the_hold_is_lifted():
    """An old application must not restore a role while a suspension is active."""
    writes = []

    class FakePool:
        async def fetchrow(self, query, *params):
            if "staff_members" in query:
                return {"staff_status": "suspended"}
            return {"user_id": params[-1], "review_status": "pending"}

        async def execute(self, *args, **kwargs):
            writes.append(args)

    class FakeBot:
        def get_guild(self, guild_id):
            raise AssertionError("A suspended applicant must not receive a role")

    client = app.test_client()
    with client.session_transaction() as session:
        session["user"] = {"id": str(next(iter(OWNER_IDS)))}
        session["access_token"] = "test-token"
        session["token_exp"] = time.time() + 3600
        session["csrf_token"] = "test-csrf"

    with patch.object(auth, "_current_user_blacklist_entry", return_value=None), patch.object(
        routes, "_pool", return_value=FakePool()
    ), patch.object(routes, "_discord_bot", FakeBot()), patch.object(
        routes, "run_on_bot_loop", side_effect=lambda awaitable: asyncio.run(awaitable)
    ):
        response = client.post(
            "/api/staff/team-recruitment/team-moderator/submissions/123/review",
            json={"status": "approved"},
            headers={"X-CSRF-Token": "test-csrf"},
        )

    assert response.status_code == 409
    assert "suspended" in response.get_json()["error"].lower()
    assert writes == []


if __name__ == "__main__":
    unittest.main()
