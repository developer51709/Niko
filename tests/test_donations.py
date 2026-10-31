"""Donations and the premium gift checkout.

Both flows move real money, so the tests concentrate on the two things that
break silently: crediting a payment twice (webhook + poller, retried callback,
restart) and letting a browser pick a price, a term, or a server it has no
claim to.
"""

import asyncio
import functools
import re
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import utils.donations as donations  # noqa: E402
import utils.premium as premium  # noqa: E402
from cogs.donations.cog import DonationCog  # noqa: E402


# ── A synchronous SQLite pool that speaks the bot's `$1` placeholders ────────

class SqlitePool:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(
            """
            CREATE TABLE donors (
                user_id        INTEGER PRIMARY KEY,
                total_donated  REAL    DEFAULT 0,
                last_donation  TEXT,
                last_track_id  TEXT
            );
            CREATE TABLE donation_invoices (
                order_id       TEXT PRIMARY KEY,
                track_id       TEXT UNIQUE,
                user_id        INTEGER NOT NULL,
                amount         REAL NOT NULL,
                currency       TEXT NOT NULL DEFAULT 'USD',
                pay_currency   TEXT,
                pay_link       TEXT,
                status         TEXT NOT NULL DEFAULT 'Waiting',
                channel_id     INTEGER,
                created_at     TEXT NOT NULL DEFAULT (datetime('now')),
                paid_at        TEXT
            );
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
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return asyncio.run(fn(*args, **kwargs))
    return wrapper


class Sent:
    def __init__(self):
        self.views = []

    async def send(self, **kwargs):
        self.views.append(kwargs)


class FakeBot:
    """Only the surface the donation cog touches."""

    def __init__(self, cxn, *, cogs=None, guild=None, channel=None, user=None):
        self.cxn = cxn
        self.cogs = cogs or {}
        self._guild = guild
        self._channel = channel
        self.sent = Sent()
        self.user = user or SimpleNamespace(id=7, send=self.sent.send)

    def get_cog(self, name):
        return self.cogs.get(name)

    def get_guild(self, guild_id):
        return self._guild

    def get_channel(self, channel_id):
        return self._channel

    async def fetch_user(self, user_id):
        return self.user


async def _invoice(pool, *, track_id="track-1", amount=5.0, channel_id=None):
    bot = SimpleNamespace(cxn=pool)
    await donations.save_invoice(
        bot,
        order_id=f"donation_7_{track_id}",
        track_id=track_id,
        user_id=7,
        amount=amount,
        currency="USD",
        pay_currency="USDT",
        pay_link="",
        channel_id=channel_id,
    )


# ── Exactly-once crediting ──────────────────────────────────────────────────

def test_a_repeated_callback_confirms_a_donation_once(pool):
    async def run():
        await _invoice(pool)
        bot = SimpleNamespace(cxn=pool)
        first, first_new = await donations.confirm_invoice(bot, "track-1")
        second, second_new = await donations.confirm_invoice(bot, "track-1")
        return first, first_new, second, second_new

    first, first_new, second, second_new = asyncio.run(run())
    assert first_new is True
    assert second_new is False
    assert first["status"] == "Paid"
    assert second["status"] == "Paid"


def test_a_later_expired_callback_cannot_unpay_an_invoice(pool):
    async def run():
        await _invoice(pool)
        bot = SimpleNamespace(cxn=pool)
        await donations.confirm_invoice(bot, "track-1")
        await donations.update_invoice_status(bot, "track-1", "Expired")
        return await donations.get_invoice(bot, track_id="track-1")

    assert asyncio.run(run())["status"] == "Paid"


def test_the_poller_sees_invoices_it_never_held_in_memory(pool):
    async def run():
        await _invoice(pool)
        bot = SimpleNamespace(cxn=pool)
        return await donations.get_pending_invoices(bot)

    pending = asyncio.run(run())
    assert [row["track_id"] for row in pending] == ["track-1"]


def test_the_pending_invoice_query_is_understood_by_the_mongo_parser():
    """The SQLite test pool accepts `IN (...)`, the Mongo pool's parser must too.

    It did not: every 45-second poll logged "Cannot parse WHERE condition" and
    the poller never saw a pending invoice.
    """
    from database import _ConditionParser

    class RecordingPool:
        async def fetch(self, query, *args):
            self.query = query
            return []

    pool = RecordingPool()
    asyncio.run(donations.get_pending_invoices(SimpleNamespace(cxn=pool)))

    where = re.search(r"WHERE\s+(.+)$", pool.query, re.S).group(1)
    assert _ConditionParser([]).parse(where) == {
        "status": {"$in": ["Waiting", "Paying", "Confirming"]}
    }


def test_the_cog_credits_and_messages_a_donation_once(pool):
    async def run():
        await _invoice(pool, channel_id=99)
        cog = DonationCog.__new__(DonationCog)
        cog.bot = FakeBot(pool, channel=Sent(), user=SimpleNamespace(id=7, send=Sent().send))
        cog.bot.cogs = {"DonationCog": cog}
        first = await cog._on_payment_confirmed("track-1")
        second = await cog._on_payment_confirmed("track-1")
        total = await donations.get_total_donated(cog.bot, 7)
        return first, second, total

    first, second, total = asyncio.run(run())
    assert first is True
    assert second is False
    assert total == 5.0


def test_a_webhook_confirmation_reaches_the_donor_table(pool, monkeypatch):
    from webapp import donations as web_donations
    from webapp import runtime

    async def run():
        await _invoice(pool)
        cog = DonationCog.__new__(DonationCog)
        cog.bot = FakeBot(pool, user=SimpleNamespace(id=7, send=Sent().send))
        cog.bot.cogs = {"DonationCog": cog}
        monkeypatch.setattr(runtime, "_discord_bot", cog.bot)
        invoice, confirmed = await web_donations._confirm_donation_from_webhook(
            "track-1", {"status": "paid"}
        )
        again, again_confirmed = await web_donations._confirm_donation_from_webhook(
            "track-1", {"status": "paid"}
        )
        total = await donations.get_total_donated(cog.bot, 7)
        return invoice, confirmed, again, again_confirmed, total

    invoice, confirmed, again, again_confirmed, total = asyncio.run(run())
    assert confirmed is True
    assert again_confirmed is False
    assert invoice["status"] == "Paid"
    assert again["status"] == "Paid"
    assert total == 5.0


def test_donation_totals_count_paid_invoices_only(pool):
    async def run():
        bot = SimpleNamespace(cxn=pool)
        await _invoice(pool, track_id="track-1", amount=5.0)
        await _invoice(pool, track_id="track-2", amount=10.0)
        await donations.confirm_invoice(bot, "track-1")
        await donations.add_donor(bot, 7, 5.0, "USDT", "track-1")
        return await donations.get_donation_totals(bot)

    totals = asyncio.run(run())
    assert totals == {"total_cents": 500, "donation_count": 1, "donor_count": 1}


# ── The provider client ────────────────────────────────────────────────────

class _Response:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status = status

    async def json(self, content_type=None):
        return self._payload


class _Request:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self._response

    async def __aexit__(self, *exc):
        return False


class _Session:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def get(self, url, headers=None):
        return _Request(self._response)


def test_a_white_label_status_is_normalised(monkeypatch):
    from cogs.donations import oxapay

    monkeypatch.setattr(
        oxapay.aiohttp,
        "ClientSession",
        lambda **kwargs: _Session(_Response({"data": {"track_id": "t1", "status": "waiting"}})),
    )
    result = asyncio.run(oxapay.OxaPayClient("key").check_white_label("t1"))
    assert result == {"success": True, "status": "Waiting", "data": {"track_id": "t1", "status": "waiting"}}


def test_a_broken_v1_lookup_falls_back_to_the_legacy_inquiry(monkeypatch):
    from cogs.donations import oxapay

    monkeypatch.setattr(
        oxapay.aiohttp, "ClientSession", lambda **kwargs: _Session(_Response({}, status=503))
    )

    async def legacy(self, track_id):
        return {"success": True, "status": "Paid", "data": {"status": "Paid"}}

    monkeypatch.setattr(oxapay.OxaPayClient, "check_payment", legacy)
    result = asyncio.run(oxapay.OxaPayClient("key").check_white_label("t1"))
    assert result["status"] == "Paid"


# ── Gift checkout is separate from the purchase checkout ────────────────────

def _response(view, *args):
    """Call a view that returns either a response or ``(response, status)``."""
    result = view(*args)
    if isinstance(result, tuple):
        return result[1], result[0].get_json()
    return result.status_code, result.get_json()


def _gift_route(monkeypatch, pool, *, member=True, managed=(), months=1, guild_id="42",
                user_id="7", pay_currency="USDT", network=None):
    from flask import session

    from webapp.routes import premium_routes

    guild = SimpleNamespace(
        id=int(guild_id),
        name="Test server",
        owner_id=7,
        icon=None,
        member_count=10,
        get_member=lambda uid: SimpleNamespace(id=uid) if member else None,
    )
    bot = SimpleNamespace(
        cxn=pool,
        guilds=[guild],
        get_guild=lambda gid: guild if int(gid) == int(guild_id) else None,
        get_user=lambda uid: None,
        get_cog=lambda name: None,
    )
    captured = {}

    class FakeClient:
        def __init__(self, key):
            self.key = key

        async def create_white_label(self, **kwargs):
            captured.update(kwargs)
            return {
                "success": True,
                "trackId": "track-gift",
                "data": {
                    "address": "TQraad2MBFgYUYhTFYeXS5jVpaLZuBwr3w",
                    "pay_amount": 45.01,
                    "pay_currency": "usdt",
                    "expired_at": 1734514150,
                    "qr_code": "https://example.com/qr.png",
                },
            }

    monkeypatch.setattr(premium_routes, "_discord_bot", bot)
    monkeypatch.setattr(premium_routes, "_billing_bot", lambda: bot)
    monkeypatch.setattr(premium_routes, "managed_guild_ids", lambda: set(managed))
    monkeypatch.setattr(premium_routes, "merchant_key", lambda: "merchant-key")
    monkeypatch.setattr(premium_routes, "public_base_url", lambda: "https://niko.test")
    monkeypatch.setattr(premium_routes, "OxaPayClient", FakeClient)
    monkeypatch.setattr(
        premium_routes, "run_on_bot_loop", lambda awaitable, timeout=8: asyncio.run(awaitable)
    )

    body = {"guild_id": guild_id, "months": months, "pay_currency": pay_currency}
    if network is not None:
        body["network"] = network
    with premium_routes.app.test_request_context(json=body):
        session["user"] = {"id": user_id}
        payload = premium_routes.api_premium_gift_checkout.__wrapped__.__wrapped__()
    # Flask accepts ``(body, status)`` from a view, so normalise the pair.
    if isinstance(payload, tuple):
        response, status = payload
    else:
        response, status = payload, payload.status_code
    return status, response.get_json(), captured


def test_a_gift_uses_the_gift_page_and_costs_the_term(monkeypatch, pool):
    status, payload, captured = _gift_route(monkeypatch, pool, months=3)

    assert status == 200
    assert captured["amount"] == premium.PREMIUM_PRICE_CENTS * 3 / 100
    assert payload["months"] == 3
    assert payload["amount_cents"] == premium.PREMIUM_PRICE_CENTS * 3
    assert payload["status_url"] == f"/api/premium/gift/orders/{payload['order_id']}"
    payment = asyncio.run(premium.get_payment(pool, order_id=payload["order_id"]))
    assert payment["kind"] == premium.KIND_GIFT
    assert payment["months"] == 3


def test_gifting_needs_membership_not_manage_server(monkeypatch, pool):
    status, _, captured = _gift_route(monkeypatch, pool, member=True, managed=())
    assert status == 200
    assert captured["amount"] == premium.PREMIUM_PRICE_CENTS / 100

    refused, _, captured = _gift_route(monkeypatch, pool, member=False, managed=("42",))
    assert refused == 403
    assert captured == {}


def test_a_gift_term_that_is_not_offered_is_refused(monkeypatch, pool):
    status, _, captured = _gift_route(monkeypatch, pool, months=7)
    assert status == 400
    assert captured == {}


def test_the_purchase_checkout_refuses_to_start_a_gift(monkeypatch, pool):
    from flask import session

    from webapp.routes import premium_routes

    bot = SimpleNamespace(cxn=pool, get_guild=lambda gid: SimpleNamespace(id=int(gid), name="x"))
    monkeypatch.setattr(premium_routes, "_discord_bot", bot)
    monkeypatch.setattr(premium_routes, "merchant_key", lambda: "merchant-key")

    with premium_routes.app.test_request_context(
        json={"guild_id": "42", "kind": "gift", "pay_currency": "USDT"}
    ):
        session["user"] = {"id": "7"}
        status, body = _response(premium_routes.api_premium_checkout.__wrapped__.__wrapped__)
    assert status == 400
    assert "gift" in body["error"].lower()


def test_the_purchase_checkout_needs_manage_server(monkeypatch, pool):
    from flask import session

    from webapp.routes import premium_routes

    guild = SimpleNamespace(id=42, name="x", get_member=lambda uid: SimpleNamespace(id=uid))
    bot = SimpleNamespace(
        cxn=pool,
        get_guild=lambda gid: guild,
        guilds=[guild],
        get_user=lambda uid: None,
        get_cog=lambda name: None,
    )
    captured = {}

    class FakeClient:
        def __init__(self, key):
            pass

        async def create_white_label(self, **kwargs):  # pragma: no cover - must not run
            captured.update(kwargs)
            return {"success": True, "trackId": "t", "data": {}}

    monkeypatch.setattr(premium_routes, "_discord_bot", bot)
    monkeypatch.setattr(premium_routes, "_billing_bot", lambda: bot)
    monkeypatch.setattr(premium_routes, "merchant_key", lambda: "merchant-key")
    monkeypatch.setattr(premium_routes, "managed_guild_ids", lambda: set())
    monkeypatch.setattr(premium_routes, "OxaPayClient", FakeClient)
    monkeypatch.setattr(
        premium_routes, "run_on_bot_loop", lambda awaitable, timeout=8: asyncio.run(awaitable)
    )

    with premium_routes.app.test_request_context(
        json={"guild_id": "42", "pay_currency": "USDT"}
    ):
        session["user"] = {"id": "7"}
        status, _ = _response(premium_routes.api_premium_checkout.__wrapped__.__wrapped__)
    assert status == 403
    assert captured == {}


def test_a_purchase_order_cannot_be_read_as_a_gift(monkeypatch, pool):
    from flask import session

    from webapp.routes import premium_routes

    async def run():
        await premium.record_payment(
            pool,
            order_id="premium_purchase_1",
            track_id="track-1",
            guild_id=42,
            payer_id=7,
            kind=premium.KIND_PURCHASE,
            months=1,
            amount_cents=premium.PREMIUM_PRICE_CENTS,
            currency="USD",
            pay_currency="USDT",
        )

    asyncio.run(run())
    bot = SimpleNamespace(
        cxn=pool,
        get_guild=lambda gid: None,
        get_user=lambda uid: None,
        get_cog=lambda name: None,
    )
    monkeypatch.setattr(premium_routes, "_discord_bot", bot)
    monkeypatch.setattr(premium_routes, "_billing_bot", lambda: bot)
    monkeypatch.setattr(
        premium_routes, "run_on_bot_loop", lambda awaitable, timeout=8: asyncio.run(awaitable)
    )

    with premium_routes.app.test_request_context():
        session["user"] = {"id": "7"}
        status, _ = _response(premium_routes.api_premium_gift_order.__wrapped__, "premium_purchase_1")
    assert status == 404


# ── Order ids must fit OxaPay's limit ───────────────────────────────────────

def test_order_ids_fit_the_providers_50_character_limit():
    """OxaPay rejects longer ids, which failed every purchase and every gift.

    The old form was ``premium_purchase_<19-digit guild>_<32 hex>`` — 69
    characters — so checkout could not start at all.
    """
    from cogs.donations.oxapay import MAX_ORDER_ID_LENGTH, build_order_id

    order_id = build_order_id("premium", "purchase", "123456789012345678")
    assert len(order_id) <= MAX_ORDER_ID_LENGTH
    assert order_id.startswith("premium_purchase_123456789012345678_")

    donation_id = build_order_id("donation", "123456789012345678")
    assert len(donation_id) <= MAX_ORDER_ID_LENGTH
    assert donation_id.startswith("donation_123456789012345678_")

    # A longer stem keeps a random tail instead of overflowing the limit.
    long_id = build_order_id("x" * 80)
    assert len(long_id) == MAX_ORDER_ID_LENGTH
    assert long_id.rsplit("_", 1)[1]

    # Ids are the primary key of the payment row, so they must stay unique.
    assert build_order_id("donation", "7") != build_order_id("donation", "7")


def test_gift_checkout_sends_the_provider_a_short_order_id(monkeypatch, pool):
    status, payload, captured = _gift_route(
        monkeypatch, pool, guild_id="123456789012345678", user_id="123456789012345678"
    )

    assert status == 200
    assert captured["order_id"] == payload["order_id"]
    assert len(captured["order_id"]) <= 50
    assert captured["network"] == "Tron"


def test_every_offered_currency_has_a_network():
    """OxaPay rejects a white-label payment that does not name a network."""
    from cogs.donations.oxapay import networks_for, resolve_network
    from webapp.routes import premium_routes

    for code in premium_routes.CRYPTO_CURRENCIES:
        assert networks_for(code), code
    for code in donations.CRYPTO_CURRENCIES:
        assert networks_for(code), code

    # The first option is the fallback for a caller that does not choose.
    assert resolve_network("usdt", None) == "Tron"
    assert resolve_network("USDT", "Ethereum") == "Ethereum"
    # Base carries ETH, not USDT, so it must be refused rather than guessed.
    assert resolve_network("USDT", "Base") is None
    assert resolve_network("NOPE", None) is None


def test_the_chosen_network_reaches_the_provider(monkeypatch, pool):
    status, _, captured = _gift_route(monkeypatch, pool, network="Ethereum")
    assert status == 200
    assert captured["network"] == "Ethereum"


def test_a_network_the_coin_cannot_use_is_refused(monkeypatch, pool):
    status, _, captured = _gift_route(monkeypatch, pool, network="Base")
    assert status == 400
    assert captured == {}


def test_no_payment_is_requested_without_a_network():
    from cogs.donations.oxapay import OxaPayClient

    async def run():
        return await OxaPayClient("merchant-key").create_white_label(
            amount=15,
            pay_currency="USDT",
            network="",
            description="Niko Premium subscription",
            order_id="premium_purchase_1",
        )

    result = asyncio.run(run())
    assert result["success"] is False
    assert "network" in result["message"].lower()
