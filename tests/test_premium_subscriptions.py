"""Premium subscriptions, billing storage, and the AI moderation client.

The subscription term is the money-critical part of premium: renewing early
must add paid days instead of shortening them, a repeated OxaPay callback must
not grant a second month, and a lapsed term must stop the fal.ai calls. These
tests run the real SQL used by ``utils.premium`` against an in-memory SQLite
database, so a column rename or a bad placeholder fails here instead of in
production.
"""

import asyncio
import functools
import hashlib
import hmac
import json
import re
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import utils.premium as premium  # noqa: E402
from utils import nsfw_api  # noqa: E402


# ── A synchronous SQLite pool that speaks the bot's `$1` placeholders ────────

class SqlitePool:
    """Minimal stand-in for the bot's async pool, backed by SQLite."""

    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(
            """
            CREATE TABLE premium_subscriptions (
                guild_id        INTEGER PRIMARY KEY,
                plan            TEXT NOT NULL DEFAULT 'premium_monthly',
                status          TEXT NOT NULL DEFAULT 'active',
                price_cents     INTEGER NOT NULL DEFAULT 1500,
                currency        TEXT NOT NULL DEFAULT 'USD',
                started_at      TEXT NOT NULL DEFAULT (datetime('now')),
                expires_at      TEXT NOT NULL,
                auto_renew      INTEGER NOT NULL DEFAULT 1,
                source          TEXT NOT NULL DEFAULT 'purchase',
                gifted_by       INTEGER,
                gifted_by_name  TEXT,
                owner_id        INTEGER,
                reminder_sent_at TEXT,
                updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE premium_payments (
                order_id       TEXT PRIMARY KEY,
                track_id       TEXT UNIQUE,
                guild_id       INTEGER NOT NULL,
                payer_id       INTEGER NOT NULL,
                kind           TEXT NOT NULL DEFAULT 'purchase',
                months         INTEGER NOT NULL DEFAULT 1,
                amount_cents   INTEGER NOT NULL DEFAULT 1500,
                currency       TEXT NOT NULL DEFAULT 'USD',
                pay_currency   TEXT,
                address        TEXT,
                pay_amount     REAL,
                qr_code        TEXT,
                status         TEXT NOT NULL DEFAULT 'Waiting',
                issue_status   TEXT,
                issue_note     TEXT,
                resolved_by    INTEGER,
                resolved_at    TEXT,
                created_at     TEXT NOT NULL DEFAULT (datetime('now')),
                paid_at        TEXT,
                expires_at     INTEGER
            );
            """
        )

    @staticmethod
    def _convert(query: str) -> str:
        order = iter(range(1, 100))
        return re.sub(r"\$\d+", lambda _match: "?", query)

    async def execute(self, query, *args):
        self.conn.execute(self._convert(query), args)
        self.conn.commit()

    async def fetchrow(self, query, *args):
        row = self.conn.execute(self._convert(query), args).fetchone()
        return dict(row) if row else None

    async def fetch(self, query, *args):
        return [dict(row) for row in self.conn.execute(self._convert(query), args).fetchall()]

    async def fetchval(self, query, *args):
        row = self.conn.execute(self._convert(query), args).fetchone()
        return row[0] if row else None


@pytest.fixture
def pool():
    return SqlitePool()


def async_test(fn):
    """Run one coroutine test without a pytest-asyncio dependency."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return asyncio.run(fn(*args, **kwargs))
    return wrapper


# ── Term math ───────────────────────────────────────────────────────────────

def test_a_new_term_runs_for_one_month():
    now = datetime(2026, 10, 20, 12, 0, 0)
    expires = premium.parse_ts(premium.next_expiry(None, 1, now=now))
    assert expires == now + timedelta(days=premium.PREMIUM_MONTH_DAYS)


def test_renewing_early_adds_days_to_the_current_term():
    now = datetime(2026, 10, 20, 12, 0, 0)
    current = (now + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
    expires = premium.parse_ts(premium.next_expiry(current, 1, now=now))
    assert expires == now + timedelta(days=10 + premium.PREMIUM_MONTH_DAYS)


def test_renewing_a_lapsed_term_starts_from_now():
    now = datetime(2026, 10, 20, 12, 0, 0)
    lapsed = (now - timedelta(days=40)).strftime("%Y-%m-%d %H:%M:%S")
    expires = premium.parse_ts(premium.next_expiry(lapsed, 1, now=now))
    assert expires == now + timedelta(days=premium.PREMIUM_MONTH_DAYS)


def test_a_subscription_is_only_active_inside_its_term():
    now = datetime(2026, 10, 20, 12, 0, 0)
    active = {"status": "active", "expires_at": (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")}
    lapsed = {"status": "active", "expires_at": (now - timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S")}
    cancelled = {"status": "cancelled", "expires_at": active["expires_at"]}
    assert premium.subscription_is_active(active, now)
    assert not premium.subscription_is_active(lapsed, now)
    assert not premium.subscription_is_active(cancelled, now)
    assert not premium.subscription_is_active(None, now)


def test_days_remaining_never_goes_negative():
    now = datetime(2026, 10, 20, 12, 0, 0)
    row = {"expires_at": (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")}
    assert premium.days_remaining(row, now) == 0
    row = {"expires_at": (now + timedelta(days=2, hours=1)).strftime("%Y-%m-%d %H:%M:%S")}
    assert premium.days_remaining(row, now) == 2


def test_reminder_fires_once_inside_the_window():
    now = datetime(2026, 10, 20, 12, 0, 0)
    soon = {
        "status": "active",
        "expires_at": (now + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
        "reminder_sent_at": None,
    }
    far = {
        "status": "active",
        "expires_at": (now + timedelta(days=12)).strftime("%Y-%m-%d %H:%M:%S"),
        "reminder_sent_at": None,
    }
    assert premium.reminder_due(soon, now)
    assert not premium.reminder_due(far, now)
    assert not premium.reminder_due({**soon, "reminder_sent_at": "2026-10-19 12:00:00"}, now)


def test_price_is_fifteen_dollars_a_month():
    assert premium.PREMIUM_PRICE_CENTS == 1500
    assert premium.price_label() == "$15.00 USD"


# ── Storage ─────────────────────────────────────────────────────────────────

@async_test
async def test_granting_a_subscription_stores_the_term(pool):
    row = await premium.activate_subscription(pool, guild_id=42, months=1, payer_id=7)
    assert row["status"] == "active"
    assert row["price_cents"] == 1500
    assert premium.subscription_is_active(row)
    assert await premium.get_subscription(pool, 42) is not None


@async_test
async def test_renewal_extends_the_existing_row(pool):
    first = await premium.activate_subscription(pool, guild_id=42, months=1)
    second = await premium.activate_subscription(pool, guild_id=42, months=1)
    assert premium.parse_ts(second["expires_at"]) == premium.parse_ts(first["expires_at"]) + timedelta(
        days=premium.PREMIUM_MONTH_DAYS
    )
    assert second["started_at"] == first["started_at"]


@async_test
async def test_gift_stores_the_gifter_and_clears_the_reminder(pool):
    await premium.activate_subscription(pool, guild_id=42, months=1)
    await premium.mark_reminder_sent(pool, 42)
    row = await premium.activate_subscription(
        pool, guild_id=42, months=1, source=premium.KIND_GIFT, gifted_by=99, gifted_by_name="Gifter"
    )
    assert row["source"] == premium.KIND_GIFT
    assert row["gifted_by"] == 99
    assert row["gifted_by_name"] == "Gifter"
    assert row["reminder_sent_at"] is None


@async_test
async def test_a_cancelled_subscription_is_not_premium(pool):
    await premium.activate_subscription(pool, guild_id=42, months=1)
    await premium.set_subscription_status(pool, 42, premium.STATUS_CANCELLED)
    assert not await premium.is_premium(pool, 42)


@async_test
async def test_expire_lapsed_marks_only_past_terms(pool):
    past = (premium.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    future = (premium.utcnow() + timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
    await pool.execute(
        "INSERT INTO premium_subscriptions (guild_id, expires_at) VALUES ($1, $2)", 1, past
    )
    await pool.execute(
        "INSERT INTO premium_subscriptions (guild_id, expires_at) VALUES ($1, $2)", 2, future
    )
    changed = await premium.expire_lapsed(pool)
    assert [int(row["guild_id"]) for row in changed] == [1]
    assert (await premium.get_subscription(pool, 1))["status"] == premium.STATUS_EXPIRED
    assert (await premium.get_subscription(pool, 2))["status"] == premium.STATUS_ACTIVE


@async_test
async def test_only_subscriptions_inside_the_reminder_window_are_returned(pool):
    now = premium.utcnow()
    soon = (now + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
    far = (now + timedelta(days=20)).strftime("%Y-%m-%d %H:%M:%S")
    await pool.execute("INSERT INTO premium_subscriptions (guild_id, expires_at) VALUES ($1, $2)", 1, soon)
    await pool.execute("INSERT INTO premium_subscriptions (guild_id, expires_at) VALUES ($1, $2)", 2, far)
    due = await premium.subscriptions_due_for_reminder(pool)
    assert [int(row["guild_id"]) for row in due] == [1]
    await premium.mark_reminder_sent(pool, 1)
    assert await premium.subscriptions_due_for_reminder(pool) == []


@async_test
async def test_a_paid_payment_is_only_confirmed_once(pool):
    await premium.record_payment(
        pool,
        order_id="premium_purchase_42_abc",
        track_id="track-1",
        guild_id=42,
        payer_id=7,
        months=1,
        amount_cents=1500,
        pay_currency="USDT",
        address="TQraad2MBFgYUYhTFYeXS5jVpaLZuBwr3w",
        pay_amount=15.01,
        qr_code="https://example.com/qr.png",
        expires_at=1734514150,
    )
    payment, first = await premium.confirm_payment(pool, "track-1")
    assert first and payment["paid_at"]
    again, second = await premium.confirm_payment(pool, "track-1")
    assert not second
    assert again["status"] == "Paid"


@async_test
async def test_staff_notes_are_stored_on_the_payment(pool):
    await premium.record_payment(
        pool, order_id="order-1", track_id="track-1", guild_id=42, payer_id=7
    )
    await premium.resolve_payment(pool, order_id="order-1", status="resolved", note="Refunded", staff_id=1)
    payment = await premium.get_payment(pool, order_id="order-1")
    assert payment["issue_status"] == "resolved"
    assert payment["issue_note"] == "Refunded"
    assert payment["resolved_by"] == 1


@async_test
async def test_a_note_saves_without_deciding_anything(pool):
    await premium.record_payment(
        pool, order_id="order-2", track_id="track-2", guild_id=42, payer_id=7
    )
    await premium.save_payment_note(pool, order_id="order-2", note="Waiting on the payer")
    payment = await premium.get_payment(pool, order_id="order-2")
    assert payment["issue_note"] == "Waiting on the payer"
    assert payment["issue_status"] is None
    assert payment["resolved_at"] is None


@async_test
async def test_a_decision_can_be_undone_without_touching_the_payment(pool):
    await premium.record_payment(
        pool, order_id="order-3", track_id="track-3", guild_id=42, payer_id=7
    )
    await premium.resolve_payment(
        pool, order_id="order-3", status="resolved", note="Refunded", staff_id=1
    )
    # ``status=None`` is the undo: the decision and its stamp go, the note and
    # the provider's state stay.
    await premium.resolve_payment(pool, order_id="order-3", status=None, note="Refunded")
    payment = await premium.get_payment(pool, order_id="order-3")
    assert payment["issue_status"] is None
    assert payment["resolved_by"] is None
    assert payment["resolved_at"] is None
    assert payment["issue_note"] == "Refunded"
    assert payment["status"] == "Waiting"


def _staff_billing_call(monkeypatch, pool, body):
    """POST the owner billing decision route with auth and CSRF bypassed."""
    from flask import session

    from webapp.routes import premium_routes

    bot = SimpleNamespace(
        cxn=pool,
        get_guild=lambda guild_id: None,
        get_user=lambda user_id: None,
        get_cog=lambda name: None,
    )
    monkeypatch.setattr(premium_routes, "_billing_bot", lambda: bot)
    monkeypatch.setattr(premium_routes, "_require_owner", lambda: None)
    monkeypatch.setattr(premium_routes, "_user_id", lambda: 1)
    monkeypatch.setattr(
        premium_routes, "run_on_bot_loop", lambda awaitable, timeout=8: asyncio.run(awaitable)
    )

    with premium_routes.app.test_request_context(json=body):
        session["user"] = {"id": "1"}
        result = premium_routes.api_staff_resolve_payment.__wrapped__.__wrapped__("order-4")
    if isinstance(result, tuple):
        response, status = result
    else:
        response, status = result, 200
    return status, response.get_json()


def test_the_route_saves_a_note_without_deciding(monkeypatch, pool):
    asyncio.run(premium.record_payment(
        pool, order_id="order-4", track_id="track-4", guild_id=42, payer_id=7
    ))

    status, payload = _staff_billing_call(monkeypatch, pool, {"note": "Checked the quote"})

    assert status == 200
    assert payload["issue_status"] is None
    payment = asyncio.run(premium.get_payment(pool, order_id="order-4"))
    assert payment["issue_note"] == "Checked the quote"
    assert payment["issue_status"] is None


def test_the_route_resolves_and_undoes(monkeypatch, pool):
    asyncio.run(premium.record_payment(
        pool, order_id="order-4", track_id="track-4", guild_id=42, payer_id=7
    ))

    status, payload = _staff_billing_call(
        monkeypatch, pool, {"status": "resolved", "note": "Refunded"}
    )
    assert status == 200 and payload["issue_status"] == "resolved"
    resolved = asyncio.run(premium.get_payment(pool, order_id="order-4"))
    assert resolved["issue_status"] == "resolved"
    assert resolved["resolved_at"] is not None

    status, payload = _staff_billing_call(
        monkeypatch, pool, {"status": "clear", "note": "Refunded"}
    )
    assert status == 200 and payload["issue_status"] is None
    undone = asyncio.run(premium.get_payment(pool, order_id="order-4"))
    assert undone["issue_status"] is None
    assert undone["resolved_at"] is None
    assert undone["issue_note"] == "Refunded"


def test_the_route_refuses_an_unknown_decision(monkeypatch, pool):
    asyncio.run(premium.record_payment(
        pool, order_id="order-4", track_id="track-4", guild_id=42, payer_id=7
    ))

    status, payload = _staff_billing_call(monkeypatch, pool, {"status": "paid"})

    assert status == 400
    assert "choose" in payload["error"].lower()
    payment = asyncio.run(premium.get_payment(pool, order_id="order-4"))
    assert payment["issue_status"] is None


# ── fal.ai NSFW client ─────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "payload,expected",
    [
        # The live fal-ai/imageutils/nsfw schema (checked against the model's
        # API reference); nsfw_score is the older alias.
        ({"nsfw_probability": 0.97}, 0.97),
        ({"nsfw_probability": 0.12}, 0.12),
        ({"nsfw_score": 0.97}, 0.97),
        ({"nsfw": True}, 1.0),
        ({"nsfw": False}, 0.0),
        ({"label": "sfw"}, None),
        (None, None),
    ],
)
def test_fal_scores_are_parsed(payload, expected):
    assert nsfw_api.score_from_payload(payload) == expected


def test_the_threshold_decides_a_hit(monkeypatch):
    monkeypatch.delenv("NSFW_THRESHOLD", raising=False)
    assert nsfw_api._is_hit(0.86)
    assert not nsfw_api._is_hit(0.84)
    assert not nsfw_api._is_hit(None)
    monkeypatch.setenv("NSFW_THRESHOLD", "0.5")
    assert nsfw_api._is_hit(0.6)
    monkeypatch.setenv("NSFW_THRESHOLD", "not-a-number")
    assert nsfw_api._is_hit(0.9)


def test_the_filter_is_unconfigured_without_a_fal_key(monkeypatch):
    monkeypatch.delenv("FAL_KEY", raising=False)
    monkeypatch.delenv("FAL_API_KEY", raising=False)
    assert not nsfw_api.api_configured()


def test_an_attachment_is_classified_by_url():
    """The model is given the CDN URL, so image bytes never pass through us."""
    attachment = SimpleNamespace(
        content_type="image/png",
        filename="shot.png",
        size=1024,
        url="https://cdn.discordapp.com/attachments/1/2/shot.png",
    )
    message = SimpleNamespace(attachments=[attachment])
    assert nsfw_api._pick_attachments(message) == [attachment]


# ── OxaPay webhook signature ───────────────────────────────────────────────

def test_checkout_ignores_a_client_supplied_price(monkeypatch, pool):
    """The browser may choose a currency, never the amount or the term."""
    from flask import session

    from webapp.routes import premium_routes

    guild = SimpleNamespace(
        id=42, name="Test server", owner_id=7, get_member=lambda user_id: SimpleNamespace(id=user_id)
    )
    bot = SimpleNamespace(
        cxn=pool,
        guilds=[guild],
        get_guild=lambda guild_id: guild if int(guild_id) == 42 else None,
        get_user=lambda user_id: None,
    )
    captured = {}

    class FakeClient:
        def __init__(self, key):
            self.key = key

        async def create_white_label(self, **kwargs):
            captured.update(kwargs)
            return {
                "success": True,
                "trackId": "track-price",
                "data": {
                    "address": "TQraad2MBFgYUYhTFYeXS5jVpaLZuBwr3w",
                    "pay_amount": 15.01,
                    "pay_currency": "usdt",
                    "expired_at": 1734514150,
                    "qr_code": "https://example.com/qr.png",
                },
            }

    monkeypatch.setattr(premium_routes, "_discord_bot", bot)
    monkeypatch.setattr(premium_routes, "_billing_bot", lambda: bot)
    monkeypatch.setattr(premium_routes, "managed_guild_ids", lambda: {"42"})
    monkeypatch.setattr(premium_routes, "merchant_key", lambda: "merchant-key")
    monkeypatch.setattr(premium_routes, "public_base_url", lambda: "https://niko.test")
    monkeypatch.setattr(premium_routes, "OxaPayClient", FakeClient)
    monkeypatch.setattr(
        premium_routes, "run_on_bot_loop", lambda awaitable, timeout=8: asyncio.run(awaitable)
    )

    with premium_routes.app.test_request_context(
        json={"guild_id": "42", "pay_currency": "USDT", "amount": 0.01, "months": 12}
    ):
        session["user"] = {"id": "7"}
        response = premium_routes.api_premium_checkout.__wrapped__.__wrapped__()

    payload = response.get_json()
    assert captured["amount"] == 15.0
    assert captured["pay_currency"] == "USDT"
    assert captured["callback_url"] == "https://niko.test/api/premium/webhook"
    assert payload["amount_cents"] == 1500
    payment = asyncio.run(premium.get_payment(pool, order_id=payload["order_id"]))
    assert payment["amount_cents"] == 1500
    assert payment["months"] == 1
    assert payment["address"] == "TQraad2MBFgYUYhTFYeXS5jVpaLZuBwr3w"


def test_the_webhook_rejects_a_bad_signature(monkeypatch):
    from webapp.routes import premium_routes

    monkeypatch.setattr(premium_routes, "merchant_key", lambda: "merchant-key")
    client = premium_routes.app.test_client()
    body = json.dumps({"status": "paid", "track_id": "track-1"}).encode()
    response = client.post("/api/premium/webhook", data=body, headers={"HMAC": "nope"})
    assert response.status_code == 401


def test_the_webhook_accepts_a_valid_signature_and_updates_status(monkeypatch):
    from webapp.routes import premium_routes

    key = "merchant-key"
    monkeypatch.setattr(premium_routes, "merchant_key", lambda: key)
    calls = []

    async def fake_update(pool, track_id, status):
        calls.append((track_id, status))

    monkeypatch.setattr(premium_routes.billing, "update_payment_status", fake_update)
    monkeypatch.setattr(premium_routes, "_billing_bot", lambda: SimpleNamespace(cxn=object()))
    # The route schedules the write on the bot's loop; tests run it inline.
    monkeypatch.setattr(
        premium_routes, "run_on_bot_loop", lambda awaitable, timeout=8: asyncio.run(awaitable)
    )

    body = json.dumps({"status": "Waiting", "track_id": "track-9"}).encode()
    signature = hmac.new(key.encode(), body, hashlib.sha512).hexdigest()
    response = premium_routes.app.test_client().post(
        "/api/premium/webhook", data=body, headers={"HMAC": signature}
    )
    assert response.status_code == 200
    assert calls == [("track-9", "Waiting")]
