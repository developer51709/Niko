"""Review-flow tests for server-managed staff applications."""

import asyncio
import contextlib
import sys
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import app
from webapp.routes import application_routes as routes
from webapp import server as server_routes
from webapp import auth  # noqa: E402

REVIEW_URL = "/api/guild/123/applications/abc/submissions/123/review"
SUBMISSIONS_URL = "/api/guild/123/applications/abc/submissions"
UPDATE_SQL = (
    "UPDATE staff_application_submissions SET review_status = $1, reviewed_by = $2, "
    "reviewed_at = datetime('now') WHERE application_id = $3 AND user_id = $4"
)
PENDING_FIRST_SQL = "CASE WHEN review_status = 'pending' THEN 0 ELSE 1 END"


class FakePool:
    """Answer the reads the review endpoints make and record every write."""

    def __init__(self, stored_status="pending"):
        self.stored_status = stored_status
        self.executed = []
        self.seen_queries = []

    async def fetchrow(self, query, *params):
        self.seen_queries.append(query)
        if "FROM staff_applications" in query:
            return {"id": "abc"}
        if query.startswith("SELECT review_status"):
            return {
                "review_status": self.stored_status,
                "reviewed_by": "42",
                "reviewed_at": "2026-10-14 12:00:00",
            }
        decided = self.stored_status != "pending"
        return {
            "user_id": "123",
            "review_status": self.stored_status,
            "reviewed_by": "42" if decided else None,
            "reviewed_at": "2026-10-14 12:00:00" if decided else None,
        }

    async def fetch(self, query, *params):
        self.seen_queries.append(query)
        return []

    async def execute(self, query, *params):
        self.executed.append((query, params))
        if query == UPDATE_SQL:
            self.stored_status = params[0]


class StaffApplicationReviewTests(unittest.TestCase):
    def signed_in_client(self, guild_ids=("123",)):
        client = app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": "4242"}
            session["access_token"] = "test-token"
            session["token_exp"] = time.time() + 3600
            session["csrf_token"] = "test-csrf"
        self.guild_ids = set(guild_ids)
        return client

    @contextlib.contextmanager
    def environment(self, pool):
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(auth, "_current_user_blacklist_entry", return_value=None))
            stack.enter_context(
                patch.object(auth, "managed_guild_ids", side_effect=lambda: self.guild_ids)
            )
            stack.enter_context(
                patch.object(
                    auth,
                    "_load_blacklist_manager",
                    return_value=SimpleNamespace(get_guild_entry=lambda guild_id: None),
                )
            )
            stack.enter_context(patch.object(routes, "_pool", return_value=pool))
            stack.enter_context(patch.object(routes, "_discord_bot", None))
            stack.enter_context(
                patch.object(routes, "run_on_bot_loop", side_effect=lambda awaitable: asyncio.run(awaitable))
            )
            yield

    def review(self, pool, status, guild_ids=("123",)):
        client = self.signed_in_client(guild_ids)
        with self.environment(pool):
            return client.post(
                REVIEW_URL,
                json={"status": status},
                headers={"X-CSRF-Token": "test-csrf"},
            )

    def test_approval_records_the_decision_with_the_previous_status(self):
        pool = FakePool(stored_status="pending")
        response = self.review(pool, "approved")

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertTrue(body["ok"])
        self.assertEqual(body["review_status"], "approved")
        self.assertEqual(body["previous_status"], "pending")
        self.assertFalse(body["unchanged"])
        self.assertEqual(body["reviewed_by"], "42")
        self.assertEqual(pool.executed, [(UPDATE_SQL, ("approved", "4242", "abc", "123"))])

    def test_denial_records_the_decision_without_touching_discord(self):
        pool = FakePool(stored_status="pending")
        response = self.review(pool, "denied")

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["review_status"], "denied")
        self.assertEqual(body["previous_status"], "pending")
        self.assertFalse(body["unchanged"])
        self.assertEqual(pool.executed, [(UPDATE_SQL, ("denied", "4242", "abc", "123"))])

    def test_a_revised_decision_overwrites_the_recorded_one(self):
        pool = FakePool(stored_status="approved")
        response = self.review(pool, "denied")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["previous_status"], "approved")
        self.assertFalse(response.get_json()["unchanged"])
        self.assertEqual(pool.executed, [(UPDATE_SQL, ("denied", "4242", "abc", "123"))])

    def test_repeating_a_recorded_decision_writes_nothing(self):
        pool = FakePool(stored_status="approved")
        response = self.review(pool, "approved")

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertTrue(body["unchanged"])
        self.assertEqual(body["previous_status"], "approved")
        self.assertEqual(body["reviewed_by"], "42")
        self.assertEqual(body["reviewed_at"], "2026-10-14 12:00:00")
        self.assertEqual(pool.executed, [])

    def test_unsupported_status_is_rejected(self):
        pool = FakePool(stored_status="pending")
        response = self.review(pool, "maybe")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(pool.executed, [])

    def test_a_manager_without_guild_access_cannot_review(self):
        pool = FakePool(stored_status="pending")
        response = self.review(pool, "approved", guild_ids=())

        self.assertEqual(response.status_code, 403)
        self.assertEqual(pool.executed, [])

    def test_response_queue_keeps_pending_responses_first(self):
        pool = FakePool(stored_status="pending")
        client = self.signed_in_client()
        with self.environment(pool):
            response = client.get(SUBMISSIONS_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["submissions"], [])
        queued = [query for query in pool.seen_queries if "FROM staff_application_submissions" in query]
        self.assertEqual(len(queued), 1)
        self.assertIn(PENDING_FIRST_SQL, queued[0])


if __name__ == "__main__":
    unittest.main()
