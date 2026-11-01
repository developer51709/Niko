"""The staff mailbox must stay within its two addresses and its two roles.

These pin the access rule the hidden page depends on — the owner reaches both
addresses, a Head Admin reaches only the admin one, and every other role gets
none — plus Mailgun's signature and the shape of what is sent and stored,
because that endpoint answers an unsigned machine rather than a session.
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
    """Enough of the shared pool to store and find a message by its id."""

    def __init__(self):
        self.stored = {}
        self.statements = []

    async def fetch(self, query, *args):
        return []

    async def fetchrow(self, query, *args):
        return self.stored.get(args[0])

    async def execute(self, query, *args):
        self.statements.append((query, args))
        if query.strip().upper().startswith("INSERT"):
            self.stored[args[0]] = {
                "message_id": args[0],
                "mailbox": args[1],
                "direction": args[2],
                "sender_address": args[3],
                "sender_name": args[4],
                "recipient_address": args[5],
                "subject": args[6],
                "body": args[7],
                "read_at": args[10],
                "created_at": args[11],
            }
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
        SimpleNamespace(run_on_bot_loop=lambda awaitable, timeout=10: asyncio.run(awaitable)),
    )
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


def test_the_owner_reaches_every_address():
    assert staff_email.mailbox_locals("owner") == ("owner", "admin")
    assert [mailbox["address"] for mailbox in staff_email.mailboxes_for("owner")] == [
        "owner@niko.sryze.cc",
        "admin@niko.sryze.cc",
    ]


def test_a_head_admin_reaches_only_the_admin_address():
    assert staff_email.mailbox_locals("head_admin") == ("admin",)
    assert staff_email.mailbox_allowed("head_admin", "admin")
    assert not staff_email.mailbox_allowed("head_admin", "owner")


@pytest.mark.parametrize("role", ["moderator", "support", "graphic_designer", "head_support", None])
def test_other_roles_hold_no_mailbox(role):
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
    assert kwargs["data"] == {
        "from": "Niko Admin <admin@niko.sryze.cc>",
        "to": "partner@example.com",
        "subject": "Re: hi",
        "text": "Hello there",
    }
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
    assert staff_email.inbound_authorized(payload)

    assert not staff_email.inbound_authorized(dict(payload, signature="0" * 64))
    assert not staff_email.inbound_authorized(dict(payload, token="b" * 50))
    assert not staff_email.inbound_authorized({})


def test_a_stale_delivery_is_rejected(monkeypatch):
    monkeypatch.setenv(staff_email.WEBHOOK_KEY_ENV, "signing-key")
    old = str(int(time.time()) - staff_email.SIGNATURE_TOLERANCE_SECONDS - 60)
    payload = delivery(timestamp=old, signature=sign("signing-key", old, "a" * 50))
    assert not staff_email.inbound_authorized(payload)


def test_without_a_signing_key_nothing_is_trusted(monkeypatch):
    assert not staff_email.inbound_authorized(delivery())


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
