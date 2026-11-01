"""Niko's own-domain staff mailbox, sent and received from the dashboard.

The owner and Head Admins share one private inbox page that is never linked from
the public site. Addresses live on the site's own domain — ``owner@`` and
``admin@`` — so a partner or applicant can write to Niko directly and the reply
comes back from the same address instead of from somebody's personal inbox.

Two directions, one provider (Mailgun):

* outbound is one form POST to the domain's ``/v3/<domain>/messages`` endpoint,
  authenticated with ``MAILGUN_API_KEY``. A composed mail goes out with a
  formatted HTML part and any attached files beside its plain text, and mail
  sent from a shared address carries the sender's own signature;
* inbound arrives as a Route ``forward()`` post, which already carries the
  parsed plain text, so there is nothing to fetch back. A domain without MX
  records and a route yet simply never delivers, and the page says so.
* what happened to a sent mail comes back through the events webhook: Mailgun
  posts one request per delivery, open, click, bounce or complaint, and that is
  the only place a read receipt can come from. Those events are stored beside
  the message they belong to and roll its state forward.

Mailgun signs both machine endpoints with the account's webhook signing key,
and each checks that signature before storing anything.

Addresses come in two kinds. The shared ones belong to a job — ``owner@``,
``admin@``, ``support@`` and ``support-lead@`` — and a role reaches only the
ones its job needs. Every other staff member gets a private address minted from
their Discord username, shown under their Discord display name, and only that
member can read it.

That private address follows the staff record. A suspension or a departure
turns the address into one that still answers but no longer delivers: it tells
the sender that this address cannot receive mail any more and points them at
``support@`` instead. A Discord rename moves the address, and the old one keeps
answering for a month with the new address so people writing to the old one are
not stranded.

Replies are kept together: a delivery is filed into the thread of the mail it
answers (from ``In-Reply-To``/``References``, or the subject as a fallback), and
a reply sent from the page carries the same headers so the conversation stays
together in the recipient's mail client too.
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
MAX_EVENTS_SHOWN = 25

# Event kinds Mailgun posts, and the state each leaves the message in. Mailgun
# renamed a few of these over the years and still sends both families, so the
# old ``*_fail`` webhook names map onto the same states as the new ``failed``.
EVENT_STATUS = {
    "accepted": "accepted",
    "stored": "accepted",
    "delivered": "delivered",
    "opened": "opened",
    "clicked": "opened",  # a click is proof the mail was read
    "unsubscribed": "unsubscribed",
    "complained": "complained",
    "rejected": "failed",
    "dropped": "failed",
    "failed": "failed",
    "permanent_fail": "failed",
    "temporary_fail": "retrying",
}

# How far along a message is. A late "delivered" must never undo an "opened",
# and a bounce outranks everything: it is the state worth acting on.
STATUS_RANK = {
    "accepted": 1,
    "retrying": 1,
    "delivered": 2,
    "opened": 3,
    "unsubscribed": 4,
    "complained": 5,
    "failed": 5,
}

# The shared addresses, and the roles that read them. ``roles`` is the whole
# access rule for these: the owner holds every one, a Head Admin holds the
# admin mailbox and the support ones, and the support team reads support@.
SHARED_MAILBOXES: tuple[dict, ...] = (
    {"local": "owner", "label": "Owner", "roles": ("owner",)},
    {"local": "admin", "label": "Admin", "roles": ("owner", "head_admin")},
    {"local": "support", "label": "Support", "roles": ("owner", "head_admin", "head_support", "support")},
    {"local": "support-lead", "label": "Support Lead", "roles": ("owner", "head_admin", "head_support")},
)

MAILBOXES = SHARED_MAILBOXES  # older imports read this name

_SHARED_BY_LOCAL = {mailbox["local"]: mailbox for mailbox in SHARED_MAILBOXES}

# A personal address is minted from a Discord username, so a name that would
# shadow a real mailbox or an address every mail system expects to exist is
# never handed out.
RESERVED_LOCALS = frozenset(_SHARED_BY_LOCAL) | {
    "abuse", "postmaster", "hostmaster", "webmaster", "root", "noreply", "no-reply", "donotreply",
}

# A renamed staff member keeps their previous address answering for this long.
ADDRESS_REDIRECT_SECONDS = 30 * 24 * 60 * 60

# Reconciling the staff roster with the address book costs a Discord lookup per
# member, so the page asks once a minute rather than on every request.
ADDRESS_SYNC_SECONDS = 60

# Address states that belong to a current staff record (as opposed to a
# ``redirect`` left behind by a rename, or one that has run its month out).
ADDRESS_LIVE_STATES = ("active", "suspended", "former")

# How many messages of one conversation the reader sends at once.
THREAD_MAX_MESSAGES = 40

# How far back the subject fallback looks for the conversation a mail answers.
THREAD_SUBJECT_WINDOW = 30 * 24 * 60 * 60

_ADDRESS_RE = re.compile(r"^[^@\s,;<>]+@[^@\s,;<>]+\.[^@\s,;<>]+$")

# A sanitized Discord username is the local part: ``john.doe`` stays as it is,
# anything a mail system would balk at becomes a dash.
_LOCAL_SANITIZE_RE = re.compile(r"[^a-z0-9._-]+")
_LOCAL_COLLAPSE_RE = re.compile(r"[._-]{2,}")


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


def address_for(local: str, domain: str | None = None) -> str:
    return f"{local}@{domain or email_domain()}"


def local_part(username: str) -> str:
    """A Discord username as an address local part, or ``""`` if nothing is left."""
    cleaned = _LOCAL_SANITIZE_RE.sub("-", str(username or "").strip().lower())
    cleaned = _LOCAL_COLLAPSE_RE.sub("-", cleaned).strip("._-")
    return cleaned[:64]


def mailboxes_for(role: str | None, user_id: int | str | None = None) -> list[dict]:
    """Every address a staff member may read.

    The shared mailboxes follow the role. The personal one is an own row in the
    address book, and is only ever returned for the member it belongs to.
    """
    domain = email_domain()
    mailboxes = [
        {
            "local": mailbox["local"],
            "label": mailbox["label"],
            "address": f"{mailbox['local']}@{domain}",
            "kind": "shared",
            "sender_name": f"{from_name()} {mailbox['label']}",
        }
        for mailbox in SHARED_MAILBOXES
        if role and role in mailbox["roles"]
    ]
    if role and user_id is not None:
        for row in personal_addresses(user_id):
            mailboxes.append({
                "local": str(row.get("local") or ""),
                "label": str(row.get("display_name") or row.get("local") or "Your address"),
                "address": str(row.get("address") or address_for(str(row.get("local") or ""))),
                "kind": "personal",
                "sender_name": str(row.get("display_name") or from_name()),
            })
    return [mailbox for mailbox in mailboxes if mailbox["local"]]


def mailbox_locals(role: str | None, user_id: int | str | None = None) -> tuple[str, ...]:
    return tuple(mailbox["local"] for mailbox in mailboxes_for(role, user_id))


def mailbox_allowed(role: str | None, local: str, user_id: int | str | None = None) -> bool:
    return str(local or "").strip().lower() in mailbox_locals(role, user_id)


def mailbox_sender_name(role: str | None, local: str, user_id: int | str | None = None) -> str:
    for mailbox in mailboxes_for(role, user_id):
        if mailbox["local"] == local:
            return mailbox.get("sender_name") or from_name()
    return from_name()


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


def support_address(domain: str | None = None) -> str:
    """Where the lifecycle auto-replies send people instead."""
    return address_for("support", domain)


def local_for_address(address: str, domain: str | None = None) -> str | None:
    """The local part of a delivered address when it is on our domain."""
    _, bare = parseaddr(str(address or ""))
    bare = (bare or str(address or "")).strip().lower()
    if "@" not in bare:
        return None
    local, _, host = bare.rpartition("@")
    if domain and host != domain.strip().lower():
        return None
    return local or None


def mailbox_for_address(address: str, domain: str | None = None) -> str | None:
    """The shared mailbox local part a delivered address belongs to."""
    local = local_for_address(address, domain)
    return local if local in _SHARED_BY_LOCAL else None


def resolve_recipient(address: str, domain: str | None = None) -> dict | None:
    """Which mailbox a delivered address belongs to, shared or personal.

    A personal address is answered from the address book, which is what makes a
    suspended member's address and a renamed member's old one recognisable long
    after the staff record moved on.
    """
    local = local_for_address(address, domain)
    if not local:
        return None
    shared = _SHARED_BY_LOCAL.get(local)
    if shared:
        return {"local": local, "kind": "shared", "status": "active", "user_id": None, "redirect_to": None}
    row = address_record(local)
    if not row:
        return None
    return {
        "local": local,
        "kind": "personal",
        "status": str(row.get("status") or "active"),
        "user_id": int(row.get("user_id") or 0) or None,
        "redirect_to": str(row.get("redirect_to") or "") or None,
        "display_name": str(row.get("display_name") or "") or None,
    }


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


# ── The address book ──────────────────────────────────────────────────────────
#
# One row per address on the domain: the staff member it belongs to, the
# Discord username it was minted from, their display name, and what has become
# of it. The row outlives the staff role on purpose — that is what lets a
# suspended member's address answer with a pointer at support instead of
# bouncing into a void.

_ADDRESS_COLUMNS = (
    "local, user_id, address, display_name, discord_username, status, "
    "redirect_to, created_at, retired_at"
)

_address_sync_at = 0.0


def _address_state(status) -> str:
    """A known address state, with a legacy/blank one read as active."""
    value = str(status or "active").strip().lower()
    return value if value in ("active", "suspended", "former", "redirect", "expired") else "active"


async def _read_addresses(local: str | None = None) -> list[dict]:
    pool = _pool()
    if local:
        row = await pool.fetchrow(
            f"SELECT {_ADDRESS_COLUMNS} FROM staff_email_addresses WHERE local = $1", local
        )
        return [row] if row else []
    return await pool.fetch(f"SELECT {_ADDRESS_COLUMNS} FROM staff_email_addresses") or []


async def _read_addresses_for_user(user_id: int) -> list[dict]:
    return await _pool().fetch(
        f"SELECT {_ADDRESS_COLUMNS} FROM staff_email_addresses WHERE user_id = $1", int(user_id)
    ) or []


async def _insert_address(row: dict) -> None:
    await _pool().execute(
        "INSERT INTO staff_email_addresses (local, user_id, address, display_name, "
        "discord_username, status, redirect_to, created_at, retired_at) "
        "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
        row["local"],
        int(row["user_id"]),
        row["address"],
        row.get("display_name"),
        row.get("discord_username"),
        _address_state(row.get("status")),
        row.get("redirect_to"),
        float(row["created_at"]),
        row.get("retired_at"),
    )


async def _update_address(row: dict) -> None:
    await _pool().execute(
        "UPDATE staff_email_addresses SET user_id = $1, address = $2, display_name = $3, "
        "discord_username = $4, status = $5, redirect_to = $6, retired_at = $7 WHERE local = $8",
        int(row["user_id"]),
        row["address"],
        row.get("display_name"),
        row.get("discord_username"),
        _address_state(row.get("status")),
        row.get("redirect_to"),
        row.get("retired_at"),
        row["local"],
    )


def address_record(local: str) -> dict | None:
    """One address book entry, or ``None`` when the local part is not issued."""
    local = str(local or "").strip().lower()
    if not local:
        return None
    try:
        rows = _run(_read_addresses(local))
    except StaffEmailError:
        return None
    return rows[0] if rows else None


def personal_addresses(user_id: int | str) -> list[dict]:
    """The addresses a staff member currently reads."""
    try:
        rows = _run(_read_addresses_for_user(int(user_id)))
    except (StaffEmailError, TypeError, ValueError):
        return []
    return [row for row in rows or [] if _address_state(row.get("status")) == "active"]


def _staff_roles() -> dict:
    """The roster's role keys, imported lazily so this module stays light."""
    try:
        from cogs.staff.records import STAFF_ROLES
    except Exception:  # pragma: no cover - only a broken install
        return {}
    return STAFF_ROLES


def _staff_identity(user_id: int | str) -> dict:
    """The Discord username and display name behind a staff record."""
    try:
        from . import staff as staff_directory

        return staff_directory._staff_identity(str(user_id)) or {}
    except Exception:
        return {}


async def _read_staff_records() -> list[dict]:
    pool = _pool()
    try:
        return await pool.fetch("SELECT user_id, role, staff_status FROM staff_members") or []
    except Exception as exc:
        if "staff_status" not in str(exc).lower():
            raise
        return await pool.fetch("SELECT user_id, role FROM staff_members") or []


def _staff_records() -> list[dict] | None:
    """The roster, or ``None`` when it could not be read at all.

    An empty list is a real answer (nobody holds a role), and is what lets the
    sync retire the address of a record that was deleted rather than demoted.
    """
    try:
        return _run(_read_staff_records()) or []
    except Exception:
        # The address book does not depend on the roster being readable right
        # now: the addresses that already exist keep working, and the next
        # sync fixes them up.
        log.warning("StaffEmail: staff roster could not be read while syncing addresses")
        return None


async def _read_live_staff_state(user_id: int) -> dict | None:
    pool = _pool()
    try:
        return await pool.fetchrow(
            "SELECT role, staff_status FROM staff_members WHERE user_id = $1", int(user_id)
        )
    except Exception as exc:
        if "staff_status" not in str(exc).lower():
            raise
        return await pool.fetchrow(
            "SELECT role FROM staff_members WHERE user_id = $1", int(user_id)
        )


def live_staff_state(user_id: int | str) -> str | None:
    """The staff record's state right now, or ``None`` if it cannot be read.

    A missing record reads as ``former``: the address must not keep delivering
    to somebody who is no longer staff. A database that cannot be read at all
    reads as unknown, which callers treat as "deliver" — an outage must not
    start auto-replying to the whole world.
    """
    try:
        row = _run(_read_live_staff_state(int(user_id)))
    except (StaffEmailError, TypeError, ValueError):
        return None
    if not row:
        return "former"
    return _address_state(row.get("staff_status"))


def _unique_local(username: str, user_id: int, by_local: dict) -> str:
    """The address local part for a username, never taking another's address."""
    base = local_part(username) or f"staff-{user_id}"
    if base in RESERVED_LOCALS:
        base = f"{base}-{user_id}"
    candidate, index = base, 2
    while True:
        row = by_local.get(candidate)
        if row is None or int(row.get("user_id") or 0) == int(user_id):
            return candidate
        candidate = f"{base}-{index}"
        index += 1


def sync_addresses(force: bool = False) -> None:
    """Keep the address book in step with the staff roster.

    Active staff get an address minted from their Discord username. A rename
    moves them to the new address and leaves the old one pointing at it for a
    month. A suspension, a demotion, or a record that disappeared marks the
    address as one that can no longer receive mail. This runs from the page and
    from the inbound webhook, so an address exists the first time it is needed
    rather than when somebody remembers to create it.
    """
    global _address_sync_at
    now = time.time()
    if not force and now - _address_sync_at < ADDRESS_SYNC_SECONDS:
        return
    bot = getattr(runtime, "_discord_bot", None)
    if bot is None or not getattr(bot, "cxn", None):
        return
    records = _staff_records()
    if records is None:
        return
    _address_sync_at = now
    if not records:
        # No staff records at all: nothing to mint, but existing addresses of
        # deleted records still have to be retired below.
        pass
    roles = _staff_roles()
    rows = list(_run(_read_addresses()) or [])
    by_local = {str(row.get("local") or ""): row for row in rows}
    by_user: dict[int, dict] = {}
    for row in rows:
        if _address_state(row.get("status")) in ADDRESS_LIVE_STATES:
            try:
                by_user[int(row.get("user_id"))] = row
            except (TypeError, ValueError):
                continue

    expires = now - ADDRESS_REDIRECT_SECONDS
    for row in list(by_local.values()):
        if _address_state(row.get("status")) == "redirect" and float(row.get("retired_at") or 0) < expires:
            expired = {**row, "status": "expired"}
            _run(_update_address(expired))
            by_local[str(expired["local"])] = expired

    seen: set[int] = set()
    for record in records:
        try:
            user_id = int(record.get("user_id"))
        except (TypeError, ValueError):
            continue
        role = str(record.get("role") or "")
        if role not in roles:
            continue
        seen.add(user_id)
        state = _address_state(record.get("staff_status"))
        identity = _staff_identity(user_id)
        username = str(identity.get("username") or "").strip().lower()
        if not username:
            # Discord could not name this member right now. Minting a
            # placeholder address would only be renamed away on the next sync.
            continue
        display = str(identity.get("name") or "").strip() or username
        local = _unique_local(username, user_id, by_local)
        current = by_user.get(user_id)
        if current and str(current.get("local")) != local:
            retired = {
                **current,
                "status": "redirect",
                "redirect_to": address_for(local),
                "retired_at": now,
            }
            _run(_update_address(retired))
            by_local[str(retired["local"])] = retired
            current = None
        if current is None:
            existing = by_local.get(local)
            if existing and int(existing.get("user_id") or 0) != user_id:
                continue
            row = {
                **(existing or {}),
                "local": local,
                "user_id": user_id,
                "address": address_for(local),
                "display_name": display,
                "discord_username": username or None,
                "status": state,
                "redirect_to": None,
                "created_at": float((existing or {}).get("created_at") or now),
                "retired_at": None,
            }
            if existing:
                _run(_update_address(row))
            else:
                _run(_insert_address(row))
            by_local[local] = row
            by_user[user_id] = row
            continue
        updated = {
            **current,
            "address": address_for(str(current.get("local"))),
            "display_name": display,
            "discord_username": username or None,
            "status": state,
        }
        if any(current.get(key) != updated.get(key) for key in ("display_name", "discord_username", "status", "address")):
            _run(_update_address(updated))
        by_local[str(updated["local"])] = updated
        by_user[user_id] = updated

    # A record that was deleted rather than demoted must not leave an address
    # that still delivers.
    for user_id, row in list(by_user.items()):
        if user_id not in seen and _address_state(row.get("status")) != "former":
            former = {**row, "status": "former"}
            _run(_update_address(former))
            by_local[str(former["local"])] = former


def _serialize(row: dict, preview: bool = False) -> dict:
    body = str(row.get("body") or "")
    direction = str(row.get("direction") or "inbound")
    message = {
        "message_id": str(row.get("message_id") or ""),
        # Every message belongs to a conversation. A message that predates
        # threading is its own thread rather than an orphan.
        "thread_id": str(row.get("thread_id") or row.get("message_id") or ""),
        "mailbox": str(row.get("mailbox") or ""),
        "direction": direction,
        "from_address": str(row.get("sender_address") or ""),
        "from_name": row.get("sender_name") or None,
        "to_address": str(row.get("recipient_address") or ""),
        "subject": str(row.get("subject") or ""),
        "created_at": float(row.get("created_at") or 0),
        "read": row.get("read_at") is not None,
        # The delivery state is only meaningful for mail we sent: an inbound
        # message is simply here. "sent" is what a fresh send reads as until
        # the provider's first event lands.
        "status": str(row.get("status") or ("sent" if direction == "outbound" else "received")),
        "delivered_at": row.get("delivered_at"),
        "opened_at": row.get("opened_at"),
        "opened_count": int(row.get("opened_count") or 0),
        "attachments": _attachment_list(row.get("attachments")),
    }
    if preview:
        flat = " ".join(body.split())
        message["preview"] = flat[:PREVIEW_CHARS] + ("…" if len(flat) > PREVIEW_CHARS else "")
    else:
        message["body"] = body
    return message


def _attachment_list(raw) -> list[dict]:
    """The attachment names and sizes kept with a sent mail (never the bytes)."""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw) if raw.strip() else []
        except ValueError:
            raw = []
    if not isinstance(raw, list):
        return []
    return [
        {
            "name": str(item.get("name") or ""),
            "size": int(item.get("size") or 0),
            "type": str(item.get("type") or ""),
        }
        for item in raw
        if isinstance(item, dict) and str(item.get("name") or "")
    ]


def _message_columns() -> str:
    return (
        "message_id, mailbox, direction, sender_address, sender_name, "
        "recipient_address, subject, body, read_at, created_at, status, "
        "delivered_at, opened_at, opened_count, thread_id, attachments"
    )


def list_messages(role: str | None, user_id: int | str | None = None, limit: int = 80) -> list[dict]:
    locals_ = mailbox_locals(role, user_id)
    if not locals_:
        return []
    placeholders = ", ".join(f"${index + 1}" for index in range(len(locals_)))
    query = (
        f"SELECT {_message_columns()} FROM staff_emails "
        f"WHERE mailbox IN ({placeholders}) ORDER BY created_at DESC LIMIT ${len(locals_) + 1}"
    )

    async def read():
        return await _pool().fetch(query, *locals_, max(1, min(int(limit), 200)))

    return [_serialize(row, preview=True) for row in (_run(read()) or [])]


def open_message(role: str | None, message_id: str, user_id: int | str | None = None) -> dict | None:
    """One message in full, its conversation, and marks it read on the way out."""
    # Resolved before the coroutine runs: reading the address book is itself a
    # database call, and it must not be nested inside another one.
    allowed = mailbox_locals(role, user_id)

    async def read():
        pool = _pool()
        row = await pool.fetchrow(
            f"SELECT {_message_columns()} FROM staff_emails WHERE message_id = $1",
            message_id,
        )
        if row is None or str(row.get("mailbox") or "") not in allowed:
            return None
        thread_id = str(row.get("thread_id") or row.get("message_id") or "")
        conversation = await pool.fetch(
            f"SELECT {_message_columns()} FROM staff_emails WHERE thread_id = $1 "
            "ORDER BY created_at ASC LIMIT $2",
            thread_id,
            THREAD_MAX_MESSAGES,
        )
        if row.get("read_at") is None:
            await pool.execute(
                "UPDATE staff_emails SET read_at = $1 WHERE message_id = $2", time.time(), message_id
            )
            row["read_at"] = time.time()
        return row, conversation or [row]

    stored = _run(read())
    if not stored:
        return None
    row, conversation = stored
    message = _serialize(row)
    message["events"] = _run(_read_events(row["message_id"])) or []
    # The whole conversation, so a reply is answered in context rather than as
    # an isolated mail that happens to share a subject.
    message["thread"] = [_serialize(entry) for entry in conversation]
    return message


async def _insert(row: dict) -> dict:
    """Store one message, keeping the provider's ID as the dedupe key."""
    await _pool().execute(
        "INSERT INTO staff_emails (message_id, mailbox, direction, sender_address, "
        "sender_name, recipient_address, subject, body, provider_id, staff_user_id, "
        "read_at, created_at, thread_id, attachments) "
        "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)",
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
        row.get("thread_id") or row["message_id"],
        row.get("attachments"),
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


# ── Composing: formatting, signatures, and attachments ──────────────────────

MAX_ATTACHMENTS = 5
MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024

# The editor sends HTML so the recipient gets real formatting. Only shapes a
# mail body needs are kept: anything that could run, frame, or load something is
# dropped before the markup ever leaves the server.
ALLOWED_HTML_TAGS = frozenset({
    "p", "div", "br", "b", "strong", "i", "em", "u", "s", "strike", "ul", "ol", "li",
    "blockquote", "h1", "h2", "h3", "hr", "pre", "code", "a",
})
DROPPED_HTML_TAGS = (
    "script", "style", "iframe", "object", "embed", "form", "input", "button",
    "textarea", "select", "meta", "link", "svg", "math", "head", "title", "base",
)
_SAFE_LINK_PREFIXES = ("http://", "https://", "mailto:")

# The composed body is wrapped in this so a plain-text draft still looks like a
# letter rather than an unformatted stream of text.
_BODY_STYLE = "font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;font-size:14px;line-height:1.65;color:#25332c;"


def _sanitize_html(markup: str) -> str:
    """Reduce user HTML to the tags and attributes a mail body actually needs."""
    if not markup:
        return ""
    soup = BeautifulSoup(markup, "html.parser")
    for tag in soup(list(DROPPED_HTML_TAGS)):
        tag.decompose()
    for tag in soup.find_all(True):
        if tag.name not in ALLOWED_HTML_TAGS:
            tag.unwrap()
            continue
        attributes = {}
        if tag.name == "a":
            href = str(tag.get("href") or "").strip()
            if href.lower().startswith(_SAFE_LINK_PREFIXES):
                attributes = {"href": href, "target": "_blank", "rel": "noopener noreferrer"}
        tag.attrs = attributes
    return str(soup).strip()


def _text_to_html(text: str) -> str:
    """A plain-text draft as HTML, preserving the line breaks it was written with."""
    escaped = html.escape(str(text or "")).replace("\n", "<br>")
    return f'<div style="{_BODY_STYLE}white-space:pre-wrap;">{escaped}</div>'


def _signature_details(role: str | None, local: str, staff_user_id: int | None, domain: str) -> dict | None:
    """Who is writing from a shared address, for the signature block."""
    if not staff_user_id or local not in _SHARED_BY_LOCAL:
        return None
    identity = _staff_identity(staff_user_id)
    personal = None
    try:
        addresses = personal_addresses(staff_user_id)
    except StaffEmailError:
        addresses = []
    if addresses:
        personal = str(addresses[0].get("address") or "") or None
    username = str(identity.get("username") or "").strip().lstrip("@") or None
    name = (
        str(identity.get("name") or "").strip()
        or (str(addresses[0].get("display_name") or "").strip() if addresses else "")
        or username
    )
    if not name:
        return None
    return {
        "name": name,
        "username": username,
        "address": personal or f"{local}@{domain}",
        "team": f"Niko {_SHARED_BY_LOCAL[local]['label']}",
    }


def _signature_html(details: dict) -> str:
    """A small, inline-styled card: who wrote it and how to reach them.

    Mail clients ignore stylesheets and many strip <style> blocks, so the
    signature is a table with its styling inline.
    """
    name = html.escape(details["name"])
    team = html.escape(details["team"])
    address = details["address"]
    handle = f"@{html.escape(details['username'])} · {team}" if details.get("username") else team
    return (
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" '
        'style="margin:26px 0 0;border-collapse:collapse;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;">'
        "<tr>"
        '<td style="padding:0 14px 0 0;border-right:3px solid #8bd5b1;"></td>'
        '<td style="padding:2px 0 2px 14px;">'
        f'<div style="font-size:15px;font-weight:700;color:#16241d;letter-spacing:-0.2px;">{name}</div>'
        f'<div style="margin:2px 0 0;font-size:12px;color:#5f7268;">{handle}</div>'
        '<div style="margin:6px 0 0;font-size:12px;">'
        f'<a href="mailto:{html.escape(address, quote=True)}" style="color:#2f7d5c;text-decoration:none;">{html.escape(address)}</a>'
        "</div></td></tr></table>"
    )


def _signature_text(details: dict) -> str:
    handle = f" (@{details['username']})" if details.get("username") else ""
    return f"—\n{details['name']}{handle} · {details['team']}\n{details['address']}"


def _safe_attachment_name(name: str) -> str:
    cleaned = re.sub(r"[\x00-\x1f\x7f]+", "", str(name or ""))
    cleaned = cleaned.replace("\\", "/").rpartition("/")[2].strip().lstrip(".")
    return cleaned[:120] or "attachment"


def _prepare_attachments(raw) -> list[dict]:
    """Validate uploaded files and keep only what the provider needs."""
    prepared: list[dict] = []
    total = 0
    for item in raw or []:
        if not isinstance(item, dict):
            continue
        content = item.get("content") or b""
        if not content:
            continue
        if len(prepared) >= MAX_ATTACHMENTS:
            raise StaffEmailError(f"Attach at most {MAX_ATTACHMENTS} files.")
        total += len(content)
        if total > MAX_ATTACHMENT_BYTES:
            raise StaffEmailError("Those attachments are too large together. Keep them under 10 MB.")
        prepared.append({
            "name": _safe_attachment_name(str(item.get("filename") or "")),
            "content": content,
            "type": str(item.get("content_type") or "application/octet-stream")[:120],
        })
    return prepared


def _attachment_metadata(attachments: list[dict]) -> str:
    return json.dumps([
        {"name": item["name"], "size": len(item["content"]), "type": item["type"]}
        for item in attachments
    ])


async def _thread_tail(thread_id: str, limit: int = 1) -> list[dict]:
    return await _pool().fetch(
        f"SELECT {_message_columns()} FROM staff_emails WHERE thread_id = $1 "
        "ORDER BY created_at DESC LIMIT $2",
        thread_id,
        limit,
    ) or []


def send_message(
    *,
    role: str | None,
    mailbox: str,
    recipient: str,
    subject: str,
    body: str,
    html_body: str | None = None,
    attachments: list[dict] | None = None,
    staff_user_id: int | None = None,
    thread_id: str | None = None,
) -> dict:
    """Send one mail from a staff address and keep a copy in the inbox.

    Passing ``thread_id`` files the mail into an existing conversation and
    carries that conversation's ``In-Reply-To``/``References``, so the exchange
    stays one thread here and in the recipient's own mail client.

    Mail sent from a shared address carries the sender's own signature — their
    display name, Discord handle, and private address — so a person writing from
    ``support@`` is still reachable as themselves.
    """
    local = str(mailbox or "").strip().lower()
    if not mailbox_allowed(role, local, staff_user_id):
        raise StaffEmailError("That address is not available to you.")
    # Validate the draft before checking the provider: a mistyped address must
    # read as a mistyped address, not as "the mailbox is not connected".
    to_address = normalize_recipient(recipient)
    subject = " ".join(str(subject or "").split())[:MAX_SUBJECT_CHARS]
    body = str(body or "").strip()[:MAX_BODY_CHARS]
    html_body = str(html_body or "").strip()[:MAX_BODY_CHARS * 4]
    if not body and html_body:
        body = _html_to_text(html_body)[:MAX_BODY_CHARS]
    if not subject:
        raise StaffEmailError("Add a subject before sending.")
    if not body and not html_body:
        raise StaffEmailError("Write a message before sending.")
    files = _prepare_attachments(attachments)

    parent = None
    thread_id = str(thread_id or "").strip() or None
    if thread_id:
        try:
            conversation = _run(_thread_tail(thread_id, 5))
        except StaffEmailError as exc:
            raise StaffEmailError("That conversation could not be loaded.") from exc
        if not conversation or str(conversation[0].get("mailbox") or "") != local:
            raise StaffEmailError("That conversation is not in this address.")
        parent = str(conversation[0].get("provider_id") or "").strip().strip("<>") or None

    api_key = _api_key()

    domain = email_domain()
    sender = f"{mailbox_sender_name(role, local, staff_user_id)} <{local}@{domain}>"
    signature = _signature_details(role, local, staff_user_id, domain)
    plain = body + (("\n\n" + _signature_text(signature)) if signature else "")
    markup = _sanitize_html(html_body) if html_body else _text_to_html(body)
    markup = f'<div style="{_BODY_STYLE}">{markup}</div>' + (_signature_html(signature) if signature else "")
    data = {"from": sender, "to": to_address, "subject": subject, "text": plain, "html": markup}
    if parent:
        data["h:In-Reply-To"] = f"<{parent}>"
        data["h:References"] = f"<{parent}>"
    try:
        response = req.post(
            f"{_api_base()}/v3/{domain}/messages",
            auth=("api", api_key),
            data=data,
            files=[("attachment", (item["name"], item["content"], item["type"])) for item in files] or None,
            timeout=30,
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

    message_id = f"out-{uuid.uuid4().hex}"
    row = {
        "message_id": message_id,
        "thread_id": thread_id or message_id,
        "mailbox": local,
        "direction": "outbound",
        "sender_address": f"{local}@{domain}",
        "sender_name": mailbox_sender_name(role, local, staff_user_id),
        "recipient_address": to_address,
        "subject": subject,
        "body": body,
        "provider_id": provider_id,
        "staff_user_id": staff_user_id,
        "read_at": time.time(),
        "created_at": time.time(),
        "attachments": _attachment_metadata(files) if files else None,
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


def _signature_fields(payload) -> tuple[str, str, str]:
    """The three signature fields, from either of Mailgun's post shapes.

    A legacy webhook posts them as flat form fields; the current one posts JSON
    with them grouped under ``signature``. Both sign the same two values.
    """
    getter = getattr(payload, "get", None)
    nested = getter("signature", None) if getter else None
    source = nested if isinstance(nested, dict) else payload
    return (
        _field(source, "timestamp"),
        _field(source, "token"),
        _field(source, "signature"),
    )


def webhook_authorized(payload) -> bool:
    """Accept a delivery only when Mailgun's signature says it is Mailgun's.

    Mailgun signs ``timestamp + token`` with the account's webhook signing key
    (hex HMAC-SHA256) and sends the values and the digest with the post. That
    key is not the API key, and it covers every domain on the account. Without
    it a delivery cannot be told apart from a forgery, so an unset key rejects
    instead of trusting whoever called.
    """
    key = _signing_key()
    if not key:
        return False
    timestamp, token, signature = _signature_fields(payload)
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
        # Events carry epoch seconds as a number-looking string.
        return float(text)
    except ValueError:
        pass
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


# ── Conversations ─────────────────────────────────────────────────────────────

def _reply_ids(headers: dict) -> list[str]:
    """The message ids a delivery says it answers, nearest first."""
    ids: list[str] = []
    for name in ("in-reply-to", "references"):
        raw = str(headers.get(name) or "")
        found = re.findall(r"<([^<>\s]+)>", raw) or ([raw] if raw.strip() else [])
        for value in reversed(found):
            value = str(value).strip().strip("<>").strip()
            if value and value not in ids:
                ids.append(value)
    return ids


def _thread_subject(subject: str) -> str:
    """A subject with its reply/forward prefixes off, for matching conversations."""
    value = " ".join(str(subject or "").split())
    while True:
        stripped = re.sub(r"^(?:(?:re|fw|fwd|aw|sv)\s*:\s*)+", "", value, flags=re.IGNORECASE)
        if stripped == value:
            break
        value = stripped
    return value.casefold()[:MAX_SUBJECT_CHARS]


async def _thread_for(pool, headers: dict, mailbox: str, sender: str, subject: str) -> str | None:
    """The conversation a delivery belongs to, if this mailbox already holds it.

    Mail clients are supposed to answer with ``In-Reply-To``/``References`` and
    the provider's message id is what those point at. When they do not — a new
    client, a forwarded copy, a mail written from a phone — the same
    counterpart and the subject with its ``Re:`` prefix off is enough to keep
    the exchange in one place.
    """
    for parent in _reply_ids(headers):
        row = await pool.fetchrow(
            "SELECT thread_id FROM staff_emails WHERE provider_id = $1 "
            "OR message_id = $2 OR message_id = $3 LIMIT 1",
            parent,
            parent,
            f"in-{parent}",
        )
        if row and row.get("thread_id"):
            return str(row["thread_id"])
    wanted = _thread_subject(subject)
    if not wanted or not sender:
        return None
    rows = await pool.fetch(
        "SELECT thread_id, subject FROM staff_emails WHERE mailbox = $1 "
        "AND (sender_address = $2 OR recipient_address = $2) AND created_at >= $3 "
        "ORDER BY created_at DESC LIMIT $4",
        mailbox,
        sender,
        time.time() - THREAD_SUBJECT_WINDOW,
        50,
    ) or []
    for row in rows:
        if row.get("thread_id") and _thread_subject(row.get("subject")) == wanted:
            return str(row["thread_id"])
    return None


# ── Addresses that no longer receive: the lifecycle auto-reply ────────────────

# Reply-to addresses that are not a person: answering one starts a mail loop.
AUTOREPLY_IGNORED_LOCALS = frozenset({
    "mailer-daemon", "postmaster", "noreply", "no-reply", "donotreply", "do-not-reply", "bounce", "bounces",
})


def _auto_reply_allowed(payload, sender: str, domain: str) -> bool:
    """Whether answering this delivery is safe and useful."""
    sender = str(sender or "").strip().lower()
    if "@" not in sender:
        return False
    if sender.rpartition("@")[2] == domain:
        # Our own mail: an auto-reply to it would bounce between us and us.
        return False
    if sender.rpartition("@")[0] in AUTOREPLY_IGNORED_LOCALS:
        return False
    headers = _headers(payload)
    if str(headers.get("auto-submitted") or "no").strip().lower() not in ("", "no"):
        return False
    if str(headers.get("precedence") or "").strip().lower() in ("bulk", "list", "junk", "auto_reply"):
        return False
    return True


def _auto_reply_body(state: str, display: str | None, old_address: str, new_address: str | None, support: str) -> str:
    name = str(display or "This staff member").strip()
    if state == "redirect" and new_address:
        return (
            f"Hello,\n\n"
            f"{name} no longer reads mail at {old_address}. Their Niko address is now {new_address}, "
            f"so please send your message there and they will see it.\n\n"
            f"This is an automatic reply. If you need the team right away, write to {support}.\n\n"
            f"— Niko"
        )
    if state == "suspended":
        situation = f"{name}'s Niko mailbox is paused while their staff access is suspended"
    elif state == "expired":
        situation = "this address is no longer in use"
    else:
        situation = f"{name} has left the Niko staff team, so this address is no longer monitored"
    return (
        f"Hello,\n\n"
        f"{old_address} can no longer receive email: {situation}. Your message has not reached them.\n\n"
        f"Please write to {support} instead and a member of the support team will pick it up.\n\n"
        f"This is an automatic reply.\n\n"
        f"— Niko"
    )


def _send_auto_reply(
    *,
    to_address: str,
    subject: str,
    state: str,
    display: str | None,
    old_address: str,
    new_address: str | None = None,
) -> bool:
    """Answer a sender whose mail can no longer be delivered. Never raises."""
    if not provider_configured():
        log.warning("StaffEmail: no auto-reply for %s because the provider is not configured", old_address)
        return False
    domain = email_domain()
    support = support_address(domain)
    reply_subject = subject if subject.lower().startswith("re:") else f"Re: {subject or '(no subject)'}"
    try:
        response = req.post(
            f"{_api_base()}/v3/{domain}/messages",
            auth=("api", _api_key()),
            data={
                "from": f"Niko Support <{support}>",
                "to": to_address,
                "subject": reply_subject[:MAX_SUBJECT_CHARS],
                "text": _auto_reply_body(state, display, old_address, new_address, support),
                # Both headers are what stops two mail systems answering each
                # other forever.
                "h:Auto-Submitted": "auto-replied",
                "h:Precedence": "auto_reply",
            },
            timeout=20,
        )
    except req.RequestException as exc:
        log.warning("StaffEmail: auto-reply to %s failed: %s", to_address, exc)
        return False
    if response.status_code >= 400:
        log.warning("StaffEmail: provider rejected the auto-reply to %s (%s)", to_address, response.status_code)
        return False
    return True


# ── Receiving a delivery ──────────────────────────────────────────────────────

def receive_webhook(payload, domain: str | None = None) -> dict:
    """Turn one route delivery into an inbox row. Returns what happened.

    A delivery to an address that can no longer receive mail is still kept (its
    conversation survives a suspension or a rehire), and the sender is answered
    automatically: the old address either points at the new one or sends them
    to support.
    """
    domain = (domain or email_domain()).strip().lower()
    try:
        sync_addresses()
    except Exception:
        # Address book maintenance is best effort: a delivery that already has
        # an address must still be stored.
        log.warning("StaffEmail: address sync failed while receiving", exc_info=True)
    # ``recipient`` is the address as it arrived over SMTP; ``to`` is the header
    # and may list several addresses with display names.
    candidates = [
        part.strip()
        for part in f"{_field(payload, 'recipient')},{_field(payload, 'to')}".split(",")
        if part.strip()
    ]
    target = None
    for candidate in candidates:
        target = resolve_recipient(candidate, domain)
        if target:
            break
    if not target:
        return {"ignored": "No staff mailbox matches that recipient."}

    addressed_local = str(target["local"])
    mailbox = addressed_local
    state = str(target.get("status") or "active")
    notice: tuple[str, str | None] | None = None
    if target.get("kind") == "personal":
        live = live_staff_state(target.get("user_id"))
        if live and live != "active":
            state = live
            if live != target.get("status"):
                record = address_record(addressed_local)
                if record:
                    _run(_update_address({**record, "status": live}))
        if state == "redirect":
            redirect_local = local_for_address(str(target.get("redirect_to") or ""), domain)
            if redirect_local:
                notice = ("redirect", redirect_local)
                mailbox = redirect_local
            else:
                notice = ("expired", None)
        elif state in ("suspended", "former", "expired"):
            notice = (state, None)

    sender_address, sender_name = _sender_parts(payload)
    subject = " ".join(_field(payload, "subject").split())[:MAX_SUBJECT_CHARS] or "(no subject)"
    body = _message_body(payload)[:MAX_BODY_CHARS]
    key = _delivery_key(payload, sender_address, subject, body)
    headers = _headers(payload)

    row = {
        "message_id": f"in-{key}",
        "thread_id": None,
        "mailbox": mailbox,
        "direction": "inbound",
        "sender_address": sender_address or "unknown@sender",
        "sender_name": sender_name,
        "recipient_address": address_for(addressed_local, domain),
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
        row["thread_id"] = (
            await _thread_for(pool, headers, mailbox, sender_address, subject)
        ) or row["message_id"]
        await _insert(row)
        return True

    stored = _run(store())
    result = {"stored": row["message_id"], "duplicate": not stored, "mailbox": mailbox}
    if notice is None:
        return result

    kind, new_local = notice
    if not stored:
        # The provider retried a delivery it already handed over; one reply is
        # enough.
        result["auto_reply"] = "skipped"
        return result
    if not _auto_reply_allowed(payload, sender_address, domain):
        result["auto_reply"] = "suppressed"
        return result
    sent = _send_auto_reply(
        to_address=sender_address,
        subject=subject,
        state=kind,
        display=target.get("display_name"),
        old_address=address_for(addressed_local, domain),
        new_address=address_for(new_local, domain) if new_local else None,
    )
    result["auto_reply"] = kind if sent else "failed"
    return result


# ── Delivery events (delivered, opened, bounced…) ─────────────────────────────

def _event_list(payload) -> list[dict]:
    """The events in one webhook post.

    The current webhook posts JSON under ``event-data`` and may batch several
    events into a list; the legacy one posts a single event as a form. Anything
    else has no event in it and is handed back empty.
    """
    getter = getattr(payload, "get", None)
    data = getter("event-data", None) if getter else None
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if _field(payload, "event"):
        return [payload]
    return []


def _event_headers(raw: dict) -> dict:
    """The original MIME headers, wherever this post shape puts them."""
    message = raw.get("message")
    if isinstance(message, dict):
        headers = message.get("headers")
        if isinstance(headers, dict):
            return {str(key).lower(): str(value) for key, value in headers.items()}
    return _headers(raw)


def _event_message_id(raw: dict) -> str:
    headers = _event_headers(raw)
    value = headers.get("message-id") or _field(raw, "Message-Id") or _field(raw, "message-id")
    return str(value or "").strip().strip("<>")[:200]


def _event_recipient(raw: dict) -> str:
    recipient = _field(raw, "recipient")
    if not recipient:
        envelope = raw.get("envelope")
        targets = envelope.get("targets") if isinstance(envelope, dict) else ""
        if isinstance(targets, (list, tuple)):
            recipient = str(targets[0]) if targets else ""
        elif targets:
            recipient = str(targets).split(",")[0]
    _, bare = parseaddr(recipient)
    return (bare or recipient).strip()[:320]


def _event_failure(raw: dict) -> tuple[str, str]:
    """Why a delivery failed, from the flat fields or ``delivery-status``."""
    reason = _field(raw, "reason")
    severity = _field(raw, "severity")
    status = raw.get("delivery-status")
    if not isinstance(status, dict):
        raw_status = _field(raw, "delivery-status")
        try:
            parsed = json.loads(raw_status) if raw_status else {}
        except ValueError:
            parsed = {}
        status = parsed if isinstance(parsed, dict) else {}
    if not reason:
        reason = str(status.get("description") or status.get("message") or "")
    if not severity and status.get("code"):
        severity = str(status.get("code"))
    return reason.strip()[:300], severity.strip()[:40]


def _event_id(raw: dict, event: str, message_id: str, occurred_at: float) -> str:
    """A stable id per event, so a retried webhook is not a second read."""
    supplied = _field(raw, "id") or _field(raw, "event-id")
    if supplied:
        return supplied[:200]
    digest = hashlib.sha256(
        f"{event}\n{message_id}\n{occurred_at}\n{_field(raw, 'recipient')}".encode()
    ).hexdigest()[:32]
    return f"evt-{digest}"


def _parse_event(raw: dict) -> dict | None:
    event = _field(raw, "event").strip().lower()
    if not event:
        return None
    message_id = _event_message_id(raw)
    occurred_at = _epoch(raw.get("timestamp"))
    reason, severity = _event_failure(raw)
    return {
        "event": event[:60],
        "event_id": _event_id(raw, event, message_id, occurred_at),
        "provider_message_id": message_id,
        "recipient": _event_recipient(raw),
        "reason": reason,
        "severity": severity,
        "occurred_at": occurred_at,
    }


async def _read_events(message_id: str) -> list[dict]:
    rows = await _pool().fetch(
        "SELECT event, recipient, reason, severity, occurred_at FROM staff_email_events "
        f"WHERE message_id = $1 ORDER BY occurred_at DESC LIMIT ${2}",
        message_id,
        MAX_EVENTS_SHOWN,
    )
    return [
        {
            "event": str(row.get("event") or ""),
            "recipient": str(row.get("recipient") or ""),
            "reason": str(row.get("reason") or ""),
            "severity": str(row.get("severity") or ""),
            "occurred_at": float(row.get("occurred_at") or 0),
        }
        for row in (rows or [])
    ]


async def _apply_event(event: dict) -> str:
    """Store one event and roll the state of the mail it belongs to.

    Returns what happened: ``linked`` (stored and applied), ``stored`` (kept
    without a message to apply it to), ``duplicate`` or ``ignored`` (not ours).
    """
    pool = _pool()
    message = None
    if event["provider_message_id"]:
        message = await pool.fetchrow(
            "SELECT message_id, mailbox, status, delivered_at, opened_at, opened_count "
            "FROM staff_emails WHERE provider_id = $1",
            event["provider_message_id"],
        )
    mailbox = str((message or {}).get("mailbox") or "") or (
        mailbox_for_address(event["recipient"], email_domain()) or ""
    )
    if message is None and not mailbox:
        # An account-level webhook sees every domain on the account; mail that is
        # neither ours nor addressed to us is none of this inbox's business.
        return "ignored"

    existing = await pool.fetchrow(
        "SELECT event_id FROM staff_email_events WHERE event_id = $1", event["event_id"]
    )
    if existing:
        return "duplicate"

    await pool.execute(
        "INSERT INTO staff_email_events (event_id, message_id, mailbox, event, recipient, "
        "reason, severity, occurred_at) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
        event["event_id"],
        (message or {}).get("message_id"),
        mailbox or None,
        event["event"],
        event["recipient"],
        event["reason"],
        event["severity"],
        event["occurred_at"],
    )

    state = EVENT_STATUS.get(event["event"])
    if message is None or state is None:
        return "stored"
    current = str(message.get("status") or "")
    if STATUS_RANK.get(state, 0) < STATUS_RANK.get(current, 0):
        # A delayed "delivered" must not walk an already-opened mail backwards.
        return "stored"

    delivered_at = message.get("delivered_at")
    if delivered_at is None and state == "delivered":
        delivered_at = event["occurred_at"]
    opened_at = message.get("opened_at")
    opened_count = int(message.get("opened_count") or 0)
    if event["event"] == "opened":
        opened_at = opened_at or event["occurred_at"]
        opened_count += 1
    await pool.execute(
        "UPDATE staff_emails SET status = $1, delivered_at = $2, opened_at = $3, "
        "opened_count = $4, last_event_at = $5 WHERE message_id = $6",
        state,
        delivered_at,
        opened_at,
        opened_count,
        event["occurred_at"],
        message["message_id"],
    )
    return "linked"


def record_events(payload) -> dict:
    """Store every event in one webhook post. Returns what was kept."""
    parsed = [event for event in (_parse_event(raw) for raw in _event_list(payload)) if event]
    counts = {"received": len(parsed), "stored": 0, "linked": 0, "duplicate": 0, "ignored": 0}
    for event in parsed:
        outcome = _run(_apply_event(event))
        if outcome in ("stored", "linked"):
            counts["stored"] += 1
        if outcome == "linked":
            counts["linked"] += 1
        elif outcome in ("duplicate", "ignored"):
            counts[outcome] += 1
    return counts
