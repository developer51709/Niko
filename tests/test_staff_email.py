"""The staff mailbox must stay within its two addresses and its two roles.

These pin the access rule the hidden page depends on — the owner reaches both
addresses, a Head Admin reaches only the admin one, and every other role gets
none — plus Mailgun's signature and the shape of what is sent and stored,
because those endpoints answer an unsigned machine rather than a session. The
last group covers the delivery events, which are the only read receipt there is.
"""

import asyncio
import hashlib
import hmac
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest  # noqa: E402

from webapp import staff_email  # noqa: E402


class FakePool:
    """Enough of the shared pool to store messages, threads, and addresses."""

    def __init__(self):
        self.stored = {}  # message_id -> message row
        self.events = {}  # event_id -> event row
        self.addresses = {}  # local -> address book row
        self.staff = []  # staff_members rows
        self.statements = []

    async def fetch(self, query, *args):
        q = " ".join(query.split())
        upper = q.upper()
        if "FROM STAFF_EMAIL_EVENTS" in upper:
            rows = [row for row in self.events.values() if row["message_id"] == args[0]]
            rows.sort(key=lambda row: row["occurred_at"], reverse=True)
            return rows[: int(args[1])]
        if "FROM STAFF_EMAILS WHERE THREAD_ID" in upper:
            rows = [
                row for row in self.stored.values()
                if (row.get("thread_id") or row["message_id"]) == args[0]
            ]
            rows.sort(key=lambda row: row["created_at"], reverse="DESC" in upper)
            return rows[: int(args[1])]
        if "FROM STAFF_EMAILS WHERE MAILBOX IN" in upper:
            allowed = set(args[:-1])
            rows = [row for row in self.stored.values() if row["mailbox"] in allowed]
            rows.sort(key=lambda row: row["created_at"], reverse=True)
            return rows[: int(args[-1])]
        if "FROM STAFF_EMAILS WHERE MAILBOX" in upper and "SENDER_ADDRESS" in upper:
            rows = [
                row for row in self.stored.values()
                if row["mailbox"] == args[0]
                and args[1] in (row["sender_address"], row["recipient_address"])
                and row["created_at"] >= args[2]
            ]
            rows.sort(key=lambda row: row["created_at"], reverse=True)
            return rows[: int(args[3])]
        if "FROM STAFF_EMAIL_ADDRESSES" in upper:
            if "WHERE USER_ID" in upper:
                return [row for row in self.addresses.values() if int(row["user_id"]) == int(args[0])]
            return list(self.addresses.values())
        if "FROM STAFF_MEMBERS" in upper:
            return list(self.staff)
        return []

    async def fetchrow(self, query, *args):
        q = " ".join(query.split())
        upper = q.upper()
        if "FROM STAFF_EMAIL_EVENTS" in upper:
            return self.events.get(args[0])
        if "FROM STAFF_EMAILS WHERE PROVIDER_ID = $1 OR MESSAGE_ID" in upper:
            for row in self.stored.values():
                if args[0] in (row.get("provider_id"), row["message_id"]) or row["message_id"] == args[2]:
                    return row
            return None
        if "FROM STAFF_EMAILS WHERE MESSAGE_ID" in upper:
            return self.stored.get(args[0])
        if "FROM STAFF_EMAILS WHERE PROVIDER_ID" in upper:
            return next((row for row in self.stored.values() if row.get("provider_id") == args[0]), None)
        if "FROM STAFF_EMAIL_ADDRESSES WHERE LOCAL" in upper:
            return self.addresses.get(args[0])
        if "FROM STAFF_MEMBERS WHERE USER_ID" in upper:
            return next((row for row in self.staff if int(row["user_id"]) == int(args[0])), None)
        return self.stored.get(args[0])

    async def execute(self, query, *args):
        self.statements.append((query, args))
        q = " ".join(query.split()).upper()
        if q.startswith("INSERT INTO STAFF_EMAILS"):
            self.stored[args[0]] = {
                "message_id": args[0],
                "thread_id": args[12],
                "mailbox": args[1],
                "direction": args[2],
                "sender_address": args[3],
                "sender_name": args[4],
                "recipient_address": args[5],
                "subject": args[6],
                "body": args[7],
                "provider_id": args[8],
                "read_at": args[10],
                "created_at": args[11],
                "attachments": args[13],
            }
        elif q.startswith("INSERT INTO STAFF_EMAIL_ADDRESSES"):
            self.addresses[args[0]] = {
                "local": args[0],
                "user_id": args[1],
                "address": args[2],
                "display_name": args[3],
                "discord_username": args[4],
                "status": args[5],
                "redirect_to": args[6],
                "created_at": args[7],
                "retired_at": args[8],
            }
        elif q.startswith("UPDATE STAFF_EMAIL_ADDRESSES"):
            row = self.addresses.get(args[7])
            if row is not None:
                row.update(
                    user_id=args[0],
                    address=args[1],
                    display_name=args[2],
                    discord_username=args[3],
                    status=args[4],
                    redirect_to=args[5],
                    retired_at=args[6],
                )
        elif q.startswith("INSERT INTO STAFF_EMAIL_EVENTS"):
            self.events[args[0]] = {
                "event_id": args[0],
                "message_id": args[1],
                "mailbox": args[2],
                "event": args[3],
                "recipient": args[4],
                "reason": args[5],
                "severity": args[6],
                "occurred_at": args[7],
            }
        elif q.startswith("UPDATE STAFF_EMAILS SET STATUS"):
            self.stored[args[5]].update(
                status=args[0],
                delivered_at=args[1],
                opened_at=args[2],
                opened_count=args[3],
                last_event_at=args[4],
            )
        elif q.startswith("UPDATE STAFF_EMAILS SET READ_AT"):
            if args[1] in self.stored:
                self.stored[args[1]]["read_at"] = args[0]
        return "OK"


@pytest.fixture(autouse=True)
def fixed_domain(monkeypatch):
    monkeypatch.setenv(staff_email.DOMAIN_ENV, "niko.sryze.cc")
    monkeypatch.delenv(staff_email.API_KEY_ENV, raising=False)
    monkeypatch.delenv(staff_email.WEBHOOK_KEY_ENV, raising=False)
    monkeypatch.delenv(staff_email.REGION_ENV, raising=False)


@pytest.fixture
def pool(monkeypatch):
    fake = FakePool()
    monkeypatch.setattr(staff_email, "_pool", lambda: fake)
    monkeypatch.setattr(
        staff_email,
        "runtime",
        SimpleNamespace(
            run_on_bot_loop=lambda awaitable, timeout=10: asyncio.run(awaitable),
            _discord_bot=SimpleNamespace(cxn=fake),
        ),
    )
    # Each test starts with a fresh address book sync window.
    monkeypatch.setattr(staff_email, "_address_sync_at", 0.0)
    return fake


def sign(key: str, timestamp: str, token: str) -> str:
    return hmac.new(key.encode(), f"{timestamp}{token}".encode(), hashlib.sha256).hexdigest()


def delivery(**overrides) -> dict:
    timestamp = str(int(time.time()))
    token = "a" * 50
    payload = {
        "recipient": "admin@niko.sryze.cc",
        "from": "Partner Name <partner@example.com>",
        "subject": "Collaboration next month",
        "body-plain": "Hi Niko,\n\nWould you like to work together?\n\nThanks!",
        "timestamp": timestamp,
        "token": token,
        "signature": sign("signing-key", timestamp, token),
        "message-headers": json.dumps([
            ["Message-Id", "<CAF123@mail.example.com>"],
            ["Date", "Sat, 01 Nov 2026 09:15:00 +0000"],
            ["From", "Partner Name <partner@example.com>"],
        ]),
    }
    payload.update(overrides)
    return payload


# ── Who holds a mailbox ───────────────────────────────────────────────────────


def test_the_owner_reaches_every_shared_address():
    assert staff_email.mailbox_locals("owner") == ("owner", "admin", "support", "support-lead")
    assert [mailbox["address"] for mailbox in staff_email.mailboxes_for("owner")] == [
        "owner@niko.sryze.cc",
        "admin@niko.sryze.cc",
        "support@niko.sryze.cc",
        "support-lead@niko.sryze.cc",
    ]


def test_a_head_admin_reaches_the_admin_and_support_addresses():
    assert staff_email.mailbox_locals("head_admin") == ("admin", "support", "support-lead")
    assert staff_email.mailbox_allowed("head_admin", "admin")
    assert not staff_email.mailbox_allowed("head_admin", "owner")


def test_the_support_team_reaches_support_and_its_lead():
    assert staff_email.mailbox_locals("support") == ("support",)
    assert staff_email.mailbox_locals("head_support") == ("support", "support-lead")
    assert not staff_email.mailbox_allowed("support", "admin")
    assert not staff_email.mailbox_allowed("support", "owner")


@pytest.mark.parametrize("role", ["moderator", "graphic_designer", "event_coordinator", None])
def test_other_roles_hold_no_shared_mailbox(role):
    assert staff_email.mailboxes_for(role) == []
    assert staff_email.mailbox_locals(role) == ()


def test_the_domain_follows_the_public_url(monkeypatch):
    monkeypatch.delenv(staff_email.DOMAIN_ENV, raising=False)
    monkeypatch.setenv("PUBLIC_URL", "https://www.niko.sryze.cc")
    assert staff_email.email_domain() == "niko.sryze.cc"
    monkeypatch.setenv("PUBLIC_URL", "https://mail.example.org")
    assert staff_email.email_domain() == "mail.example.org"


def test_without_a_public_url_the_canonical_domain_is_used(monkeypatch):
    monkeypatch.delenv(staff_email.DOMAIN_ENV, raising=False)
    monkeypatch.delenv("PUBLIC_URL", raising=False)
    assert staff_email.email_domain() == "niko.sryze.cc"


def test_a_delivery_is_matched_by_its_local_part():
    assert staff_email.mailbox_for_address("Someone <ADMIN@Niko.Sryze.CC>", "niko.sryze.cc") == "admin"
    assert staff_email.mailbox_for_address("admin@niko.sryze.cc") == "admin"
    assert staff_email.mailbox_for_address("admin@example.com", "niko.sryze.cc") is None
    assert staff_email.mailbox_for_address("team@niko.sryze.cc", "niko.sryze.cc") is None
    assert staff_email.mailbox_for_address("", "niko.sryze.cc") is None


# ── Sending through Mailgun ───────────────────────────────────────────────────


class FakeResponse:
    status_code = 200
    text = ""

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def test_an_unconfigured_mailbox_refuses_to_send(pool):
    with pytest.raises(staff_email.StaffEmailUnavailable) as excinfo:
        staff_email.send_message(role="owner", mailbox="admin", recipient="a@example.com", subject="Hi", body="Hello")
    assert "MAILGUN_API_KEY" in str(excinfo.value)
    assert pool.statements == []


def test_a_recipient_must_be_an_address():
    assert staff_email.normalize_recipient("Partner <partner@example.com>") == "partner@example.com"
    for value in ("", "not-an-address", "a@b", "two@example.com, three@example.com"):
        with pytest.raises(staff_email.StaffEmailError):
            staff_email.normalize_recipient(value)


def test_sending_posts_a_signed_form_to_the_domain(monkeypatch, pool):
    monkeypatch.setenv(staff_email.API_KEY_ENV, "key-123")
    calls = []

    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        return FakeResponse({"id": "<20261101.1.abcd@niko.sryze.cc>", "message": "Queued. Thank you."})

    monkeypatch.setattr(staff_email.req, "post", fake_post)

    message = staff_email.send_message(
        role="head_admin", mailbox="admin", recipient="partner@example.com", subject=" Re: hi ", body="Hello there"
    )

    url, kwargs = calls[0]
    assert url == "https://api.mailgun.net/v3/niko.sryze.cc/messages"
    assert kwargs["auth"] == ("api", "key-123")
    assert kwargs["data"]["from"] == "Niko Admin <admin@niko.sryze.cc>"
    assert kwargs["data"]["to"] == "partner@example.com"
    assert kwargs["data"]["subject"] == "Re: hi"
    assert kwargs["data"]["text"] == "Hello there"
    # A plain draft still goes out as a formatted letter.
    assert "Hello there" in kwargs["data"]["html"]
    assert kwargs["files"] is None
    assert message["message_id"] in pool.stored
    assert message["direction"] == "outbound"
    # provider_id is the eighth insert argument, with the angle brackets off.
    assert pool.statements[0][1][8] == "20261101.1.abcd@niko.sryze.cc"


def test_an_eu_domain_posts_to_the_eu_host(monkeypatch, pool):
    monkeypatch.setenv(staff_email.API_KEY_ENV, "key-123")
    monkeypatch.setenv(staff_email.REGION_ENV, "eu")
    seen = {}
    monkeypatch.setattr(
        staff_email.req,
        "post",
        lambda url, **kwargs: (seen.update(url=url), FakeResponse({"id": "<x@y>"}))[1],
    )
    staff_email.send_message(role="owner", mailbox="owner", recipient="a@example.com", subject="Hi", body="Body")
    assert seen["url"] == "https://api.eu.mailgun.net/v3/niko.sryze.cc/messages"


def test_the_owner_may_not_send_as_an_address_they_do_not_hold(monkeypatch, pool):
    monkeypatch.setenv(staff_email.API_KEY_ENV, "key-123")
    with pytest.raises(staff_email.StaffEmailError):
        staff_email.send_message(role="moderator", mailbox="admin", recipient="a@example.com", subject="Hi", body="Body")


# ── Receiving a signed delivery ───────────────────────────────────────────────


def test_a_signed_delivery_is_accepted_and_a_tampered_one_is_not(monkeypatch):
    monkeypatch.setenv(staff_email.WEBHOOK_KEY_ENV, "signing-key")
    payload = delivery()
    assert staff_email.webhook_authorized(payload)

    assert not staff_email.webhook_authorized(dict(payload, signature="0" * 64))
    assert not staff_email.webhook_authorized(dict(payload, token="b" * 50))
    assert not staff_email.webhook_authorized({})


def test_a_stale_delivery_is_rejected(monkeypatch):
    monkeypatch.setenv(staff_email.WEBHOOK_KEY_ENV, "signing-key")
    old = str(int(time.time()) - staff_email.SIGNATURE_TOLERANCE_SECONDS - 60)
    payload = delivery(timestamp=old, signature=sign("signing-key", old, "a" * 50))
    assert not staff_email.webhook_authorized(payload)


def test_without_a_signing_key_nothing_is_trusted(monkeypatch):
    assert not staff_email.webhook_authorized(delivery())


def test_a_delivery_lands_in_the_matching_mailbox(monkeypatch, pool):
    monkeypatch.setenv(staff_email.WEBHOOK_KEY_ENV, "signing-key")
    result = staff_email.receive_webhook(delivery())

    assert result["mailbox"] == "admin"
    row = pool.stored[result["stored"]]
    assert row["mailbox"] == "admin"
    assert row["direction"] == "inbound"
    assert row["sender_address"] == "partner@example.com"
    assert row["sender_name"] == "Partner Name"
    assert row["subject"] == "Collaboration next month"
    assert row["body"].startswith("Hi Niko,")
    assert row["read_at"] is None
    # The Date header wins over the post time.
    assert row["created_at"] == 1793524500.0


def test_a_retry_of_the_same_delivery_is_not_stored_twice(monkeypatch, pool):
    monkeypatch.setenv(staff_email.WEBHOOK_KEY_ENV, "signing-key")
    first = staff_email.receive_webhook(delivery())
    second = staff_email.receive_webhook(delivery())
    assert first["duplicate"] is False
    assert second["duplicate"] is True
    assert first["stored"] == second["stored"]
    assert len(pool.stored) == 1


def test_mail_for_another_address_is_ignored(monkeypatch, pool):
    monkeypatch.setenv(staff_email.WEBHOOK_KEY_ENV, "signing-key")
    result = staff_email.receive_webhook(delivery(recipient="hello@example.com", to="hello@example.com"))
    assert "ignored" in result
    assert pool.stored == {}


def test_an_html_only_delivery_still_gets_readable_text(monkeypatch, pool):
    monkeypatch.setenv(staff_email.WEBHOOK_KEY_ENV, "signing-key")
    payload = delivery(**{"body-plain": "", "stripped-text": "", "body-html": "<p>Hello <b>there</b></p>"})
    result = staff_email.receive_webhook(payload)
    body = pool.stored[result["stored"]]["body"]
    assert "Hello" in body and "there" in body and "<" not in body


# ── Delivery events and read receipts ────────────────────────────────────────

SENT_ID = "20261101.1.abcd@niko.sryze.cc"


def sent_message(monkeypatch, pool, recipient="partner@example.com"):
    """Send one mail through a stubbed provider and return the stored copy."""
    monkeypatch.setenv(staff_email.API_KEY_ENV, "key-123")
    monkeypatch.setattr(staff_email.req, "post", lambda url, **kwargs: FakeResponse({"id": f"<{SENT_ID}>"}))
    return staff_email.send_message(
        role="owner", mailbox="admin", recipient=recipient, subject="Hello", body="Body"
    )


def event(kind: str, **overrides) -> dict:
    """A current webhook post: JSON, one event, signature nested."""
    timestamp = str(int(time.time()))
    token = "c" * 50
    data = {
        "id": f"evt-{kind}",
        "event": kind,
        "timestamp": time.time(),
        "recipient": "partner@example.com",
        "message": {"headers": {"message-id": f"<{SENT_ID}>"}},
    }
    data.update(overrides)
    return {
        "signature": {
            "timestamp": timestamp,
            "token": token,
            "signature": sign("signing-key", timestamp, token),
        },
        "event-data": data,
    }


def test_the_events_webhook_takes_either_post_shape(monkeypatch):
    monkeypatch.setenv(staff_email.WEBHOOK_KEY_ENV, "signing-key")
    # Current JSON webhook (signature nested) and legacy form post (flat).
    assert staff_email.webhook_authorized(event("delivered"))
    assert staff_email.webhook_authorized(delivery())

    tampered = event("delivered")
    tampered["signature"]["signature"] = "0" * 64
    assert not staff_email.webhook_authorized(tampered)
    assert not staff_email.webhook_authorized({"signature": {"timestamp": "1"}, "event-data": {}})


def test_delivery_and_opens_move_the_message_forward(monkeypatch, pool):
    monkeypatch.setenv(staff_email.WEBHOOK_KEY_ENV, "signing-key")
    message = sent_message(monkeypatch, pool)
    assert message["status"] == "sent"

    staff_email.record_events(event("accepted"))
    staff_email.record_events(event("delivered"))
    staff_email.record_events(event("opened", id="evt-open-1"))
    counts = staff_email.record_events(event("opened", id="evt-open-2"))

    assert counts == {"received": 1, "stored": 1, "linked": 1, "duplicate": 0, "ignored": 0}
    opened = staff_email.open_message("owner", message["message_id"])
    assert opened["status"] == "opened"
    assert opened["opened_count"] == 2
    assert opened["opened_at"] and opened["delivered_at"]
    assert [row["event"] for row in opened["events"]] == ["opened", "opened", "delivered", "accepted"]


def test_a_late_delivery_does_not_undo_an_open(monkeypatch, pool):
    monkeypatch.setenv(staff_email.WEBHOOK_KEY_ENV, "signing-key")
    message = sent_message(monkeypatch, pool)
    staff_email.record_events(event("opened"))
    staff_email.record_events(event("delivered", id="evt-late"))
    assert pool.stored[message["message_id"]]["status"] == "opened"


def test_a_click_counts_as_a_read(monkeypatch, pool):
    monkeypatch.setenv(staff_email.WEBHOOK_KEY_ENV, "signing-key")
    message = sent_message(monkeypatch, pool)
    staff_email.record_events(event("clicked"))
    assert staff_email.open_message("owner", message["message_id"])["status"] == "opened"


def test_a_bounce_keeps_the_reason(monkeypatch, pool):
    monkeypatch.setenv(staff_email.WEBHOOK_KEY_ENV, "signing-key")
    message = sent_message(monkeypatch, pool)
    failure = event(
        "permanent_fail",
        **{"delivery-status": {"code": 550, "description": "Mailbox does not exist"}},
    )
    staff_email.record_events(failure)
    opened = staff_email.open_message("owner", message["message_id"])
    assert opened["status"] == "failed"
    assert opened["events"][0]["reason"] == "Mailbox does not exist"
    assert opened["events"][0]["severity"] == "550"


def test_a_retried_event_is_not_a_second_open(monkeypatch, pool):
    monkeypatch.setenv(staff_email.WEBHOOK_KEY_ENV, "signing-key")
    sent_message(monkeypatch, pool)
    first = staff_email.record_events(event("opened"))
    second = staff_email.record_events(event("opened"))
    assert first["stored"] == 1 and first["linked"] == 1
    assert second == {"received": 1, "stored": 0, "linked": 0, "duplicate": 1, "ignored": 0}
    assert len(pool.events) == 1


def test_a_legacy_form_event_is_understood(monkeypatch, pool):
    monkeypatch.setenv(staff_email.WEBHOOK_KEY_ENV, "signing-key")
    message = sent_message(monkeypatch, pool)
    timestamp = str(int(time.time()))
    token = "d" * 50
    counts = staff_email.record_events({
        "event": "delivered",
        "id": "legacy-1",
        "timestamp": timestamp,
        "token": token,
        "signature": sign("signing-key", timestamp, token),
        "recipient": "partner@example.com",
        "message-headers": json.dumps([["Message-Id", f"<{SENT_ID}>"]]),
    })
    assert counts["linked"] == 1
    assert staff_email.open_message("owner", message["message_id"])["status"] == "delivered"


def test_events_about_other_domains_are_ignored(monkeypatch, pool):
    monkeypatch.setenv(staff_email.WEBHOOK_KEY_ENV, "signing-key")
    foreign = staff_email.record_events(event(
        "delivered",
        id="evt-foreign",
        recipient="someone@example.com",
        message={"headers": {"message-id": "<other@elsewhere.example>"}},
    ))
    assert foreign["ignored"] == 1
    assert pool.events == {}

    # A delivery to one of our addresses is still worth keeping, even when the
    # message it names is not one this page holds.
    kept = staff_email.record_events(event(
        "stored",
        id="evt-inbound",
        recipient="admin@niko.sryze.cc",
        message={"headers": {"message-id": "<inbound@elsewhere.example>"}},
    ))
    assert kept["stored"] == 1
    assert pool.events["evt-inbound"]["message_id"] is None
    assert pool.events["evt-inbound"]["mailbox"] == "admin"


def test_a_batch_of_events_is_all_kept(monkeypatch, pool):
    monkeypatch.setenv(staff_email.WEBHOOK_KEY_ENV, "signing-key")
    sent_message(monkeypatch, pool)
    first = event("delivered")
    first["event-data"] = [
        {"id": "batch-1", "event": "accepted", "timestamp": time.time(), "recipient": "partner@example.com", "message": {"headers": {"message-id": f"<{SENT_ID}>"}}},
        {"id": "batch-2", "event": "delivered", "timestamp": time.time(), "recipient": "partner@example.com", "message": {"headers": {"message-id": f"<{SENT_ID}>"}}},
    ]
    counts = staff_email.record_events(first)
    assert counts["received"] == 2 and counts["linked"] == 2


def test_without_a_signing_key_no_event_is_trusted(monkeypatch):
    assert not staff_email.webhook_authorized(event("delivered"))


# ── Private staff addresses ───────────────────────────────────────────────────


def staff_record(pool, user_id=42, role="support", status="active"):
    pool.staff.append({"user_id": user_id, "role": role, "staff_status": status})
    return pool.staff[-1]


def discord_identity(monkeypatch, username, name):
    monkeypatch.setattr(
        staff_email, "_staff_identity", lambda user_id: {"username": username, "name": name}
    )


def stub_provider(monkeypatch):
    """Send every provider call through a recorder instead of the network."""
    sent = []

    def fake_post(url, **kwargs):
        sent.append(kwargs["data"])
        return FakeResponse({"id": "<autoreply@niko.sryze.cc>"})

    monkeypatch.setattr(staff_email.req, "post", fake_post)
    monkeypatch.setenv(staff_email.API_KEY_ENV, "key-123")
    return sent


def mail_headers(pairs) -> str:
    return json.dumps([[name, value] for name, value in pairs])


def test_a_staff_member_gets_a_private_address_from_their_username(monkeypatch, pool):
    staff_record(pool)
    discord_identity(monkeypatch, "Ava.Support", "Ava")
    staff_email.sync_addresses(force=True)

    row = pool.addresses["ava.support"]
    assert row["user_id"] == 42
    assert row["status"] == "active"
    assert row["display_name"] == "Ava"

    boxes = staff_email.mailboxes_for("support", "42")
    assert [box["local"] for box in boxes] == ["support", "ava.support"]
    assert boxes[1]["address"] == "ava.support@niko.sryze.cc"
    assert boxes[1]["kind"] == "personal"
    # The address answers under the member's Discord display name.
    assert boxes[1]["sender_name"] == "Ava"
    # And it belongs to one member only.
    assert staff_email.mailbox_locals("support", "99") == ("support",)


def test_a_private_address_is_readable_only_by_its_owner(monkeypatch, pool):
    staff_record(pool)
    discord_identity(monkeypatch, "ava", "Ava")
    staff_email.sync_addresses(force=True)

    result = staff_email.receive_webhook(delivery(recipient="ava@niko.sryze.cc", to="ava@niko.sryze.cc"))
    assert result["mailbox"] == "ava"

    assert staff_email.open_message("support", result["stored"], "42") is not None
    assert staff_email.open_message("support", result["stored"], "99") is None
    assert staff_email.list_messages("support", "99") == []


def test_an_address_never_takes_one_that_is_already_issued(monkeypatch, pool):
    staff_record(pool, user_id=42)
    staff_record(pool, user_id=43)
    monkeypatch.setattr(
        staff_email,
        "_staff_identity",
        lambda user_id: {"username": "ava", "name": f"Ava {user_id}"},
    )
    staff_email.sync_addresses(force=True)
    assert sorted(pool.addresses) == ["ava", "ava-2"]


def test_a_reserved_name_is_never_handed_out(monkeypatch, pool):
    staff_record(pool)
    discord_identity(monkeypatch, "support", "Support Impersonator")
    staff_email.sync_addresses(force=True)
    assert "support" not in pool.addresses
    assert pool.addresses["support-42"]["user_id"] == 42


# ── Suspended, departed, and renamed staff ────────────────────────────────────


def test_mail_to_a_suspended_address_is_answered_with_the_support_address(monkeypatch, pool):
    staff_record(pool, status="suspended")
    discord_identity(monkeypatch, "ava", "Ava")
    staff_email.sync_addresses(force=True)
    sent = stub_provider(monkeypatch)

    result = staff_email.receive_webhook(delivery(recipient="ava@niko.sryze.cc", to="ava@niko.sryze.cc"))

    assert result["mailbox"] == "ava"
    assert result["auto_reply"] == "suspended"
    assert result["stored"] in pool.stored  # the mail is kept for a possible return
    assert sent[0]["to"] == "partner@example.com"
    assert sent[0]["from"] == "Niko Support <support@niko.sryze.cc>"
    assert "ava@niko.sryze.cc" in sent[0]["text"]
    assert "support@niko.sryze.cc" in sent[0]["text"]
    assert sent[0]["h:Auto-Submitted"] == "auto-replied"


def test_departed_staff_are_told_they_left_rather_than_suspended(monkeypatch, pool):
    staff_record(pool, status="former")
    discord_identity(monkeypatch, "ava", "Ava")
    staff_email.sync_addresses(force=True)
    sent = stub_provider(monkeypatch)
    result = staff_email.receive_webhook(delivery(recipient="ava@niko.sryze.cc", to="ava@niko.sryze.cc"))
    assert result["auto_reply"] == "former"
    assert "left the Niko staff team" in sent[0]["text"]


def test_suspending_a_member_after_the_address_exists_switches_it_off(monkeypatch, pool):
    staff_record(pool)
    discord_identity(monkeypatch, "ava", "Ava")
    staff_email.sync_addresses(force=True)
    sent = stub_provider(monkeypatch)
    pool.staff[0]["staff_status"] = "suspended"

    result = staff_email.receive_webhook(delivery(recipient="ava@niko.sryze.cc", to="ava@niko.sryze.cc"))

    assert result["auto_reply"] == "suspended"
    assert pool.addresses["ava"]["status"] == "suspended"
    assert "paused" in sent[0]["text"]


def test_removing_the_record_turns_the_address_off(monkeypatch, pool):
    staff_record(pool)
    discord_identity(monkeypatch, "ava", "Ava")
    staff_email.sync_addresses(force=True)
    pool.staff.pop()
    staff_email.sync_addresses(force=True)
    assert pool.addresses["ava"]["status"] == "former"


def test_a_renamed_member_keeps_the_old_address_pointing_at_the_new_one(monkeypatch, pool):
    staff_record(pool)
    discord_identity(monkeypatch, "old.name", "Ava")
    staff_email.sync_addresses(force=True)

    discord_identity(monkeypatch, "new.name", "Ava")
    staff_email.sync_addresses(force=True)

    old = pool.addresses["old.name"]
    assert old["status"] == "redirect"
    assert old["redirect_to"] == "new.name@niko.sryze.cc"
    assert old["retired_at"] and pool.addresses["new.name"]["status"] == "active"

    sent = stub_provider(monkeypatch)
    result = staff_email.receive_webhook(delivery(recipient="old.name@niko.sryze.cc", to="old.name@niko.sryze.cc"))

    assert result["mailbox"] == "new.name"
    assert result["auto_reply"] == "redirect"
    assert "new.name@niko.sryze.cc" in sent[0]["text"]
    # The reply comes from support, and the mail itself waits in the new address.
    assert sent[0]["from"] == "Niko Support <support@niko.sryze.cc>"
    assert pool.stored[result["stored"]]["mailbox"] == "new.name"


def test_an_old_address_stops_pointing_at_the_new_one_after_a_month(monkeypatch, pool):
    staff_record(pool)
    discord_identity(monkeypatch, "old.name", "Ava")
    staff_email.sync_addresses(force=True)
    discord_identity(monkeypatch, "new.name", "Ava")
    staff_email.sync_addresses(force=True)
    pool.addresses["old.name"]["retired_at"] = time.time() - staff_email.ADDRESS_REDIRECT_SECONDS - 60
    staff_email.sync_addresses(force=True)
    assert pool.addresses["old.name"]["status"] == "expired"

    sent = stub_provider(monkeypatch)
    result = staff_email.receive_webhook(delivery(recipient="old.name@niko.sryze.cc", to="old.name@niko.sryze.cc"))

    assert result["auto_reply"] == "expired"
    assert "no longer in use" in sent[0]["text"]
    assert "support@niko.sryze.cc" in sent[0]["text"]
    assert "new.name@niko.sryze.cc" not in sent[0]["text"]


def test_the_auto_reply_never_answers_an_automatic_message(monkeypatch, pool):
    staff_record(pool, status="suspended")
    discord_identity(monkeypatch, "ava", "Ava")
    staff_email.sync_addresses(force=True)
    sent = stub_provider(monkeypatch)

    result = staff_email.receive_webhook(delivery(
        recipient="ava@niko.sryze.cc",
        to="ava@niko.sryze.cc",
        **{"message-headers": mail_headers([
            ("Message-Id", "<vacation@mail.example.com>"),
            ("Auto-Submitted", "auto-replied"),
        ])},
    ))

    assert result["auto_reply"] == "suppressed"
    assert sent == []


def test_a_retried_delivery_does_not_send_the_auto_reply_again(monkeypatch, pool):
    staff_record(pool, status="suspended")
    discord_identity(monkeypatch, "ava", "Ava")
    staff_email.sync_addresses(force=True)
    sent = stub_provider(monkeypatch)
    payload = delivery(recipient="ava@niko.sryze.cc", to="ava@niko.sryze.cc")

    first = staff_email.receive_webhook(payload)
    second = staff_email.receive_webhook(payload)

    assert first["auto_reply"] == "suspended"
    assert second["duplicate"] is True and second["auto_reply"] == "skipped"
    assert len(sent) == 1


# ── Conversations ─────────────────────────────────────────────────────────────


def test_a_reply_joins_the_thread_it_answers(monkeypatch, pool):
    message = sent_message(monkeypatch, pool)

    reply = delivery(
        subject="Re: Hello",
        **{"message-headers": mail_headers([
            ("Message-Id", "<reply-1@mail.example.com>"),
            ("In-Reply-To", f"<{SENT_ID}>"),
            ("From", "Partner Name <partner@example.com>"),
        ])},
    )
    result = staff_email.receive_webhook(reply)

    assert pool.stored[result["stored"]]["thread_id"] == message["thread_id"]
    conversation = staff_email.open_message("owner", message["message_id"])["thread"]
    assert sorted(entry["message_id"] for entry in conversation) == sorted(
        [message["message_id"], result["stored"]]
    )


def test_a_reply_without_reply_headers_still_finds_the_conversation(monkeypatch, pool):
    message = sent_message(monkeypatch, pool)
    reply = delivery(
        subject="Re: Hello",
        **{"message-headers": mail_headers([
            ("Message-Id", "<reply-2@mail.example.com>"),
            ("From", "Partner Name <partner@example.com>"),
        ])},
    )
    result = staff_email.receive_webhook(reply)
    assert pool.stored[result["stored"]]["thread_id"] == message["thread_id"]


def test_an_unrelated_mail_opens_its_own_conversation(monkeypatch, pool):
    message = sent_message(monkeypatch, pool)
    result = staff_email.receive_webhook(delivery(
        subject="A different subject",
        **{"from": "Someone New <new@example.com>"},
    ))
    assert pool.stored[result["stored"]]["thread_id"] != message["thread_id"]


def test_replying_from_the_page_stays_in_the_conversation(monkeypatch, pool):
    message = sent_message(monkeypatch, pool)
    staff_email.receive_webhook(delivery(
        subject="Re: Hello",
        **{"message-headers": mail_headers([
            ("Message-Id", "<reply-3@mail.example.com>"),
            ("In-Reply-To", f"<{SENT_ID}>"),
            ("Date", "Sat, 01 Nov 2025 09:15:00 +0000"),
            ("From", "Partner Name <partner@example.com>"),
        ])},
    ))
    sent = stub_provider(monkeypatch)

    reply = staff_email.send_message(
        role="owner",
        mailbox="admin",
        recipient="partner@example.com",
        subject="Re: Hello",
        body="Sounds good.",
        thread_id=message["thread_id"],
    )

    assert reply["thread_id"] == message["thread_id"]
    # And the recipient's own mail client sees one thread too.
    assert sent[0]["h:In-Reply-To"] == f"<{SENT_ID}>"
    assert sent[0]["h:References"] == f"<{SENT_ID}>"
    conversation = staff_email.open_message("owner", message["message_id"])["thread"]
    assert len(conversation) == 3


# ── Signatures, formatting, and attachments ──────────────────────────────────


def stub_provider_calls(monkeypatch):
    """Every provider post in full, so files and fields can both be checked."""
    calls = []

    def fake_post(url, **kwargs):
        calls.append(kwargs)
        return FakeResponse({"id": "<sent@niko.sryze.cc>"})

    monkeypatch.setattr(staff_email.req, "post", fake_post)
    monkeypatch.setenv(staff_email.API_KEY_ENV, "key-123")
    return calls


def test_a_shared_address_carries_the_senders_own_signature(monkeypatch, pool):
    staff_record(pool)
    discord_identity(monkeypatch, "ava.support", "Ava Bell")
    staff_email.sync_addresses(force=True)
    calls = stub_provider_calls(monkeypatch)

    staff_email.send_message(
        role="support",
        mailbox="support",
        recipient="person@example.com",
        subject="Hello",
        body="Hi there",
        html_body="<p>Hi there</p>",
        staff_user_id=42,
    )

    data = calls[0]["data"]
    assert "<p>Hi there</p>" in data["html"]
    # The signature names the person writing, not just the shared address.
    assert "Ava Bell" in data["html"]
    assert "@ava.support" in data["html"]
    assert ">ava.support@niko.sryze.cc<" in data["html"]
    assert "mailto:ava.support@niko.sryze.cc" in data["html"]
    # It is a table with inline styling, because mail clients drop stylesheets.
    assert '<table role="presentation"' in data["html"]
    assert "border-right:3px solid" in data["html"]
    # The plain-text alternative carries the same details.
    assert "Ava Bell (@ava.support)" in data["text"]
    assert "ava.support@niko.sryze.cc" in data["text"]


def test_a_private_address_does_not_repeat_the_signature(monkeypatch, pool):
    staff_record(pool)
    discord_identity(monkeypatch, "ava", "Ava Bell")
    staff_email.sync_addresses(force=True)
    calls = stub_provider_calls(monkeypatch)

    staff_email.send_message(
        role="support",
        mailbox="ava",
        recipient="person@example.com",
        subject="Hello",
        body="Hi there",
        html_body="<p>Hi there</p>",
        staff_user_id=42,
    )

    # Writing from their own address already identifies them.
    assert "border-right:3px solid" not in calls[0]["data"]["html"]
    assert calls[0]["data"]["text"] == "Hi there"


def test_composed_html_is_reduced_to_safe_formatting(monkeypatch, pool):
    staff_record(pool)
    discord_identity(monkeypatch, "ava", "Ava")
    staff_email.sync_addresses(force=True)
    calls = stub_provider_calls(monkeypatch)

    staff_email.send_message(
        role="support",
        mailbox="ava",
        recipient="person@example.com",
        subject="Meeting",
        body="Bold and a link",
        html_body=(
            '<p><b>Bold</b> and <a href="https://example.com">a link</a></p>'
            '<script>alert(1)</script>'
            '<a href="javascript:alert(1)">bad</a>'
            '<img src="x" onerror="alert(1)">'
        ),
        staff_user_id=42,
    )

    markup = calls[0]["data"]["html"]
    assert "<b>Bold</b>" in markup
    assert 'href="https://example.com"' in markup
    assert "<script" not in markup
    assert "javascript:" not in markup
    assert "<img" not in markup
    assert "onerror" not in markup


def test_a_draft_without_html_is_still_formatted(monkeypatch, pool):
    staff_record(pool)
    discord_identity(monkeypatch, "ava", "Ava")
    staff_email.sync_addresses(force=True)
    calls = stub_provider_calls(monkeypatch)

    staff_email.send_message(
        role="support",
        mailbox="ava",
        recipient="person@example.com",
        subject="Hello",
        body="Line one\nLine two",
        staff_user_id=42,
    )

    assert "Line one<br>Line two" in calls[0]["data"]["html"]


def test_attachments_are_passed_through_and_recorded(monkeypatch, pool):
    staff_record(pool)
    discord_identity(monkeypatch, "ava", "Ava")
    staff_email.sync_addresses(force=True)
    calls = stub_provider_calls(monkeypatch)

    message = staff_email.send_message(
        role="support",
        mailbox="ava",
        recipient="person@example.com",
        subject="Files",
        body="See attached",
        attachments=[
            {"filename": "../../brief.pdf", "content": b"%PDF-1.4", "content_type": "application/pdf"},
            {"filename": "image.png", "content": b"\x89PNG", "content_type": "image/png"},
        ],
        staff_user_id=42,
    )

    assert calls[0]["files"] == [
        ("attachment", ("brief.pdf", b"%PDF-1.4", "application/pdf")),
        ("attachment", ("image.png", b"\x89PNG", "image/png")),
    ]
    # Only the description of the files is kept, never their bytes.
    assert message["attachments"] == [
        {"name": "brief.pdf", "size": 8, "type": "application/pdf"},
        {"name": "image.png", "size": 4, "type": "image/png"},
    ]
    # Stored as JSON text next to the message, read back as a list.
    assert json.loads(pool.stored[message["message_id"]]["attachments"]) == message["attachments"]


def test_too_many_attachments_are_refused(monkeypatch, pool):
    staff_record(pool)
    discord_identity(monkeypatch, "ava", "Ava")
    staff_email.sync_addresses(force=True)
    calls = stub_provider_calls(monkeypatch)
    uploads = [
        {"filename": f"file-{index}.txt", "content": b"x", "content_type": "text/plain"}
        for index in range(staff_email.MAX_ATTACHMENTS + 1)
    ]

    with pytest.raises(staff_email.StaffEmailError) as excinfo:
        staff_email.send_message(
            role="support", mailbox="ava", recipient="person@example.com",
            subject="Files", body="See attached", attachments=uploads, staff_user_id=42,
        )
    assert "at most" in str(excinfo.value)
    assert calls == []


def test_attachment_total_size_is_capped(monkeypatch, pool):
    staff_record(pool)
    discord_identity(monkeypatch, "ava", "Ava")
    staff_email.sync_addresses(force=True)
    stub_provider_calls(monkeypatch)
    monkeypatch.setattr(staff_email, "MAX_ATTACHMENT_BYTES", 4)

    with pytest.raises(staff_email.StaffEmailError):
        staff_email.send_message(
            role="support", mailbox="ava", recipient="person@example.com", subject="Files",
            body="See attached", attachments=[{"filename": "a.bin", "content": b"12345"}],
            staff_user_id=42,
        )


def test_a_reply_cannot_be_sent_into_another_address_conversation(monkeypatch, pool):
    staff_record(pool)
    discord_identity(monkeypatch, "ava", "Ava")
    staff_email.sync_addresses(force=True)
    message = sent_message(monkeypatch, pool)
    monkeypatch.setenv(staff_email.API_KEY_ENV, "key-123")
    with pytest.raises(staff_email.StaffEmailError):
        staff_email.send_message(
            role="support",
            mailbox="ava",
            recipient="partner@example.com",
            subject="Hi",
            body="Body",
            staff_user_id=42,
            thread_id=message["thread_id"],
        )
