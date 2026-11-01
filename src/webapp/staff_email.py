"""Niko's own-domain staff mailbox, sent and received from the dashboard.

The owner and Head Admins share one private inbox page that is never linked from
the public site. Addresses live on the site's own domain — ``owner@`` and
``admin@`` — so a partner or applicant can write to Niko directly and the reply
comes back from the same address instead of from somebody's personal inbox.

Two directions, one provider (Mailgun):

* outbound is one form POST to the domain's ``/v3/<domain>/messages`` endpoint,
  authenticated with ``MAILGUN_API_KEY``;
* inbound arrives as a Route ``forward()`` post, which already carries the
  parsed plain text, so there is nothing to fetch back. Mailgun signs every
  such post with the account's webhook signing key, and the endpoint checks
  that signature before storing anything. A domain without MX records and a
  route yet simply never delivers, and the page says so.

Only two addresses are staff mailboxes, and a role reaches only the ones its
job needs: the owner sees both, a Head Admin sees the admin address.
"""

from __future__ import annotations

import hashlib
import hmac
import html
import json
import logging
import os
import re
import time
import uuid
from datetime import datetime, timezone
from email.utils import parseaddr, parsedate_to_datetime
from urllib.parse import urlparse

import requests as req
from bs4 import BeautifulSoup

from . import runtime

log = logging.getLogger(__name__)

API_KEY_ENV = "MAILGUN_API_KEY"
WEBHOOK_KEY_ENV = "MAILGUN_WEBHOOK_SIGNING_KEY"
REGION_ENV = "MAILGUN_REGION"
DOMAIN_ENV = "STAFF_EMAIL_DOMAIN"
FROM_NAME_ENV = "STAFF_EMAIL_FROM_NAME"

# Mailgun is regional: a key for an EU domain only works against the EU host.
API_BASES = {"us": "https://api.mailgun.net", "eu": "https://api.eu.mailgun.net"}

# Mailgun re-posts a delivery it could not hand over, and says not to police the
# clock too hard. Replays are harmless anyway: the message id is the dedupe key.
SIGNATURE_TOLERANCE_SECONDS = 24 * 60 * 60

MAX_BODY_CHARS = 200_000
MAX_SUBJECT_CHARS = 300
PREVIEW_CHARS = 180

# The addresses themselves. ``roles`` is the whole access rule: the owner sees
# every mailbox, a Head Admin reaches the admin address and nothing else.
MAILBOXES: tuple[dict, ...] = (
    {"local": "owner", "label": "Owner", "roles": ("owner",)},
    {"local": "admin", "label": "Admin", "roles": ("owner", "head_admin")},
)

_MAILBOX_BY_LOCAL = {mailbox["local"]: mailbox for mailbox in MAILBOXES}

_ADDRESS_RE = re.compile(r"^[^@\s,;<>]+@[^@\s,;<>]+\.[^@\s,;<>]+$")


class StaffEmailError(Exception):
    """A failure whose message is safe to show a staff member."""


class StaffEmailUnavailable(StaffEmailError):
    """The mailbox cannot be reached right now (bot offline, no provider key)."""


# ── Addresses and access ──────────────────────────────────────────────────────


def email_domain() -> str:
    """The domain the mailboxes live on.

    ``STAFF_EMAIL_DOMAIN`` wins, then the configured ``PUBLIC_URL`` host, and a
    deployment that has set neither still gets Niko's canonical domain. The
    request host is deliberately not used: a mailbox identity has to match the
    domain verified with the mail provider, and the sandbox host it is previewed
    on cannot receive mail.
    """
    override = (os.environ.get(DOMAIN_ENV) or "").strip().lstrip("@").lower()
    if override:
        return override
    try:
        host = urlparse((os.environ.get("PUBLIC_URL") or "").strip()).hostname or ""
    except ValueError:
        host = ""
    host = host.strip().lower()
    if host.startswith("www."):
        host = host[4:]
    return host or "niko.sryze.cc"


def from_name() -> str:
    return (os.environ.get(FROM_NAME_ENV) or "Niko").strip() or "Niko"


def mailboxes_for(role: str | None) -> list[dict]:
    """Every mailbox a staff role may read, newest role first in ``MAILBOXES``."""
    domain = email_domain()
    return [
        {"local": mailbox["local"], "label": mailbox["label"], "address": f"{mailbox['local']}@{domain}"}
        for mailbox in MAILBOXES
        if role and role in mailbox["roles"]
    ]


def mailbox_locals(role: str | None) -> tuple[str, ...]:
    return tuple(mailbox["local"] for mailbox in mailboxes_for(role))


def mailbox_allowed(role: str | None, local: str) -> bool:
    return str(local or "").strip().lower() in mailbox_locals(role)


def provider_configured() -> bool:
    return bool((os.environ.get(API_KEY_ENV) or "").strip())


def missing_settings() -> list[str]:
    """Env var names the operator still has to set, for the unconfigured notice."""
    missing = []
    if not provider_configured():
        missing.append(API_KEY_ENV)
    if not _signing_key():
        missing.append(WEBHOOK_KEY_ENV)
    return missing


def mailbox_for_address(address: str, domain: str | None = None) -> str | None:
    """The mailbox local part a delivered address belongs to, if it is ours."""
    _, bare = parseaddr(str(address or ""))
    bare = (bare or str(address or "")).strip().lower()
    if "@" not in bare:
        return None
    local, _, host = bare.rpartition("@")
    if domain and host != domain.strip().lower():
        return None
    return local if local in _MAILBOX_BY_LOCAL else None


# ── Storage ───────────────────────────────────────────────────────────────────


def _pool():
    bot = runtime._discord_bot
    if bot is None or not getattr(bot, "cxn", None):
        raise StaffEmailUnavailable("The staff mailbox is unavailable while the bot is offline.")
    return bot.cxn


def _run(awaitable, timeout: float = 10):
    try:
        return runtime.run_on_bot_loop(awaitable, timeout=timeout)
    except StaffEmailError:
        raise
    except Exception as exc:
        log.warning("StaffEmail: database call failed: %s", exc)
        raise StaffEmailUnavailable("The staff mailbox could not be read right now.") from exc


def _serialize(row: dict, preview: bool = False) -> dict:
    body = str(row.get("body") or "")
    message = {
        "message_id": str(row.get("message_id") or ""),
        "mailbox": str(row.get("mailbox") or ""),
        "direction": str(row.get("direction") or "inbound"),
        "from_address": str(row.get("sender_address") or ""),
        "from_name": row.get("sender_name") or None,
        "to_address": str(row.get("recipient_address") or ""),
        "subject": str(row.get("subject") or ""),
        "created_at": float(row.get("created_at") or 0),
        "read": row.get("read_at") is not None,
    }
    if preview:
        flat = " ".join(body.split())
        message["preview"] = flat[:PREVIEW_CHARS] + ("…" if len(flat) > PREVIEW_CHARS else "")
    else:
        message["body"] = body
    return message


def list_messages(role: str | None, limit: int = 80) -> list[dict]:
    locals_ = mailbox_locals(role)
    if not locals_:
        return []
    placeholders = ", ".join(f"${index + 1}" for index in range(len(locals_)))
    query = (
        "SELECT message_id, mailbox, direction, sender_address, sender_name, "
        "recipient_address, subject, body, read_at, created_at FROM staff_emails "
        f"WHERE mailbox IN ({placeholders}) ORDER BY created_at DESC LIMIT ${len(locals_) + 1}"
    )

    async def read():
        return await _pool().fetch(query, *locals_, max(1, min(int(limit), 200)))

    return [_serialize(row, preview=True) for row in (_run(read()) or [])]


def open_message(role: str | None, message_id: str) -> dict | None:
    """One message in full, marking an unread delivery as read on the way out."""
    async def read():
        pool = _pool()
        row = await pool.fetchrow(
            "SELECT message_id, mailbox, direction, sender_address, sender_name, "
            "recipient_address, subject, body, read_at, created_at FROM staff_emails "
            "WHERE message_id = $1",
            message_id,
        )
        if row is None or str(row.get("mailbox") or "") not in mailbox_locals(role):
            return None
        if row.get("read_at") is None:
            await pool.execute(
                "UPDATE staff_emails SET read_at = $1 WHERE message_id = $2", time.time(), message_id
            )
            row["read_at"] = time.time()
        return row

    stored = _run(read())
    return _serialize(stored) if stored else None


async def _insert(row: dict) -> dict:
    """Store one message, keeping the provider's ID as the dedupe key."""
    await _pool().execute(
        "INSERT INTO staff_emails (message_id, mailbox, direction, sender_address, "
        "sender_name, recipient_address, subject, body, provider_id, staff_user_id, "
        "read_at, created_at) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)",
        row["message_id"],
        row["mailbox"],
        row["direction"],
        row["sender_address"],
        row.get("sender_name"),
        row["recipient_address"],
        row["subject"],
        row["body"],
        row.get("provider_id"),
        row.get("staff_user_id"),
        row.get("read_at"),
        row["created_at"],
    )
    return row


# ── Sending ───────────────────────────────────────────────────────────────────


def _api_key() -> str:
    key = (os.environ.get(API_KEY_ENV) or "").strip()
    if not key:
        raise StaffEmailUnavailable(
            f"Sending is not connected yet: set {API_KEY_ENV} and verify the domain with Mailgun."
        )
    return key


def _api_base() -> str:
    return API_BASES.get((os.environ.get(REGION_ENV) or "").strip().lower(), API_BASES["us"])


def normalize_recipient(value: str) -> str:
    """The bare address of a typed recipient, rejected if it is not one."""
    _, bare = parseaddr(str(value or "").strip())
    bare = (bare or "").strip()
    if not _ADDRESS_RE.match(bare):
        raise StaffEmailError("Enter a valid email address for the recipient.")
    return bare


def send_message(
    *,
    role: str | None,
    mailbox: str,
    recipient: str,
    subject: str,
    body: str,
    staff_user_id: int | None = None,
) -> dict:
    """Send one mail from a staff address and keep a copy in the inbox."""
    local = str(mailbox or "").strip().lower()
    if not mailbox_allowed(role, local):
        raise StaffEmailError("That address is not available to your role.")
    # Validate the draft before checking the provider: a mistyped address must
    # read as a mistyped address, not as "the mailbox is not connected".
    to_address = normalize_recipient(recipient)
    subject = " ".join(str(subject or "").split())[:MAX_SUBJECT_CHARS]
    body = str(body or "").strip()[:MAX_BODY_CHARS]
    if not subject:
        raise StaffEmailError("Add a subject before sending.")
    if not body:
        raise StaffEmailError("Write a message before sending.")
    api_key = _api_key()

    domain = email_domain()
    sender = f"{from_name()} {_MAILBOX_BY_LOCAL[local]['label']} <{local}@{domain}>"
    try:
        response = req.post(
            f"{_api_base()}/v3/{domain}/messages",
            auth=("api", api_key),
            data={"from": sender, "to": to_address, "subject": subject, "text": body},
            timeout=20,
        )
    except req.RequestException as exc:
        log.warning("StaffEmail: send failed: %s", exc)
        raise StaffEmailError("The mail provider could not be reached. Try again in a moment.") from exc

    if response.status_code >= 400:
        detail = ""
        try:
            detail = str((response.json() or {}).get("message") or "")
        except ValueError:
            detail = response.text[:200]
        log.warning("StaffEmail: provider rejected the message (%s): %s", response.status_code, detail)
        raise StaffEmailError(detail or "The mail provider rejected that message.")

    provider_id = None
    try:
        # Mailgun answers with an RFC message id wrapped in angle brackets.
        provider_id = str((response.json() or {}).get("id") or "").strip().strip("<>") or None
    except ValueError:
        provider_id = None

    row = {
        "message_id": f"out-{uuid.uuid4().hex}",
        "mailbox": local,
        "direction": "outbound",
        "sender_address": f"{local}@{domain}",
        "sender_name": from_name(),
        "recipient_address": to_address,
        "subject": subject,
        "body": body,
        "provider_id": provider_id,
        "staff_user_id": staff_user_id,
        "read_at": time.time(),
        "created_at": time.time(),
    }
    _run(_insert(row))
    return _serialize(row)


# ── Receiving ─────────────────────────────────────────────────────────────────


def _signing_key() -> str:
    return (os.environ.get(WEBHOOK_KEY_ENV) or "").strip()


def _field(payload, name: str) -> str:
    """One delivery field as text; Mailgun posts a form, not JSON."""
    if not payload:
        return ""
    getter = getattr(payload, "get", None)
    value = getter(name, "") if getter else ""
    if isinstance(value, (list, tuple)):
        value = value[0] if value else ""
    return str(value or "").strip()


def inbound_authorized(payload) -> bool:
    """Accept a delivery only when Mailgun's signature says it is Mailgun's.

    Mailgun signs ``timestamp + token`` with the account's webhook signing key
    (hex HMAC-SHA256) and sends the values and the digest as form fields. That
    key is not the API key, and it covers every domain on the account. Without
    it a delivery cannot be told apart from a forgery, so an unset key rejects
    instead of trusting whoever called.
    """
    key = _signing_key()
    if not key:
        return False
    timestamp = _field(payload, "timestamp")
    token = _field(payload, "token")
    signature = _field(payload, "signature")
    if not (timestamp and token and signature):
        return False
    try:
        if abs(time.time() - int(float(timestamp))) > SIGNATURE_TOLERANCE_SECONDS:
            return False
    except (TypeError, ValueError):
        return False
    expected = hmac.new(key.encode(), f"{timestamp}{token}".encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature.lower())


def _html_to_text(markup: str) -> str:
    if not markup:
        return ""
    try:
        text = BeautifulSoup(markup, "html.parser").get_text("\n")
    except Exception:
        text = re.sub(r"<[^>]+>", " ", markup)
    text = html.unescape(text)
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def _epoch(value) -> float:
    if isinstance(value, (int, float)) and value > 0:
        return float(value)
    text = str(value or "").strip()
    if not text:
        return time.time()
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.timestamp()
    except ValueError:
        return time.time()


def _headers(payload) -> dict:
    """The original MIME headers, posted as a JSON list of ``[name, value]``."""
    raw = _field(payload, "message-headers")
    if not raw:
        return {}
    try:
        pairs = json.loads(raw)
    except (TypeError, ValueError):
        return {}
    if not isinstance(pairs, list):
        return {}
    return {
        str(pair[0]).strip().lower(): str(pair[1])
        for pair in pairs
        if isinstance(pair, (list, tuple)) and len(pair) == 2
    }


def _sender_parts(payload) -> tuple[str, str | None]:
    name, address = parseaddr(_field(payload, "from") or _field(payload, "sender"))
    if not address:
        name, address = parseaddr(_headers(payload).get("from") or "")
    return (address or "").strip().lower(), (name or None)


def _message_body(payload) -> str:
    """The readable text of a delivery.

    Mailgun generates ``body-plain`` even for an HTML-only message, so that is
    tried first and the HTML is only parsed when it is missing — a rendered
    body is never trusted as markup downstream.
    """
    for name in ("body-plain", "stripped-text"):
        text = _field(payload, name)
        if text:
            return text
    getter = getattr(payload, "getlist", None)
    parts = getter("body-html") if getter else None
    if not parts:
        # A multipart form can repeat the key, which ``get`` collapses.
        parts = [part for part in (_field(payload, "body-html"), _field(payload, "stripped-html")) if part]
    return _html_to_text("\n".join(str(part) for part in parts or []))


def _delivery_key(payload, sender: str, subject: str, body: str) -> str:
    """A stable id for one delivered mail.

    Mailgun re-posts a delivery it could not hand over, so the key has to stay
    the same across attempts or a retry would show up as a second message. The
    original ``Message-Id`` is exactly that; a digest of the content is the
    fallback for a delivery that lost its headers.
    """
    header_id = (_headers(payload).get("message-id") or _field(payload, "Message-Id")).strip().strip("<>")
    if header_id:
        return header_id[:200]
    digest = hashlib.sha256(f"{sender}\n{subject}\n{body[:500]}".encode()).hexdigest()[:32]
    return f"digest-{digest}"


def _received_at(payload) -> float:
    """When the mail was sent, from its ``Date`` header, else the post time."""
    raw = _headers(payload).get("date")
    if raw:
        try:
            parsed = parsedate_to_datetime(raw)
        except (TypeError, ValueError):
            parsed = None
        if parsed is not None:
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.timestamp()
    return _epoch(_field(payload, "timestamp"))


def receive_webhook(payload, domain: str | None = None) -> dict:
    """Turn one route delivery into an inbox row. Returns what happened."""
    domain = (domain or email_domain()).strip().lower()
    # ``recipient`` is the address as it arrived over SMTP; ``to`` is the header
    # and may list several addresses with display names.
    candidates = [
        part.strip()
        for part in f"{_field(payload, 'recipient')},{_field(payload, 'to')}".split(",")
        if part.strip()
    ]
    mailbox = None
    for candidate in candidates:
        mailbox = mailbox_for_address(candidate, domain)
        if mailbox:
            break
    if not mailbox:
        return {"ignored": "No staff mailbox matches that recipient."}

    sender_address, sender_name = _sender_parts(payload)
    subject = " ".join(_field(payload, "subject").split())[:MAX_SUBJECT_CHARS] or "(no subject)"
    body = _message_body(payload)[:MAX_BODY_CHARS]
    key = _delivery_key(payload, sender_address, subject, body)

    row = {
        "message_id": f"in-{key}",
        "mailbox": mailbox,
        "direction": "inbound",
        "sender_address": sender_address or "unknown@sender",
        "sender_name": sender_name,
        "recipient_address": f"{mailbox}@{domain}",
        "subject": subject,
        "body": body,
        "provider_id": key,
        "staff_user_id": None,
        "read_at": None,
        "created_at": _received_at(payload),
    }

    async def store():
        pool = _pool()
        existing = await pool.fetchrow(
            "SELECT message_id FROM staff_emails WHERE message_id = $1", row["message_id"]
        )
        if existing:
            return False
        await _insert(row)
        return True

    stored = _run(store())
    return {"stored": row["message_id"], "duplicate": not stored, "mailbox": mailbox}
