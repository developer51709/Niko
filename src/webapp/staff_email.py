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
  mail's parsed text and its own markup, so there is nothing to fetch back. A
  domain without MX records and a route yet simply never delivers, and the page
  says so.
* what happened to a sent mail comes back through the events webhook: Mailgun
  posts one request per delivery, open, click, bounce or complaint, and that is
  the only place a read receipt can come from. Those events are stored beside
  the message they belong to and roll its state forward.

Both directions keep the markup they were written in, so the page shows a mail
the way the recipient's client does — formatting, tables, pictures, and the
sender's signature — rather than a plainer second rendering of it. A reply's
quoted history is kept but folded behind a control, the way an inbox hides it,
so an answer reads as the answer. That markup is sanitized before it is stored,
because this page renders it.

Every sent mail also carries a footer linking to a public report form, with a
token minted for that one message. What comes back is a report filed against
the message — the reason, an optional note, and whether the recipient agreed to
share the whole conversation — which the bot owner reads and answers from the
queue. The answer is an ordinary mail from the address the message came from,
so it reaches the person who reported it and stays in the mailbox with it.

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
import secrets
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


def _owner_ids() -> list[int]:
    """The accounts that hold owner outside the staff roster.

    Ownership is a list rather than one account, and an owner has no staff
    record, so their private address is minted from here instead.
    """
    try:
        from config.ids import OWNER_IDS
    except Exception:  # pragma: no cover - only a broken install
        return []
    owners: list[int] = []
    for value in OWNER_IDS or ():
        try:
            owners.append(int(value))
        except (TypeError, ValueError):
            continue
    return owners


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
        numeric_user_id = int(user_id)
    except (TypeError, ValueError):
        return None
    if numeric_user_id in _owner_ids():
        # An owner holds no staff record, so the roster would read them as gone.
        return "active"
    try:
        row = _run(_read_live_staff_state(numeric_user_id))
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
    roles = {**_staff_roles(), "owner": "Owner"}
    # An owner has no staff record, but still needs a private inbox of their
    # own: several owners share ``owner@``, and none of them should have to read
    # the others' mail. They are folded into the roster the sync walks.
    known = set()
    for record in records:
        try:
            known.add(int(record.get("user_id")))
        except (TypeError, ValueError):
            continue
    records = list(records) + [
        {"user_id": owner, "role": "owner", "staff_status": "active"}
        for owner in _owner_ids()
        if owner not in known
    ]
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
        flat = _preview_text(body)
        message["preview"] = flat[:PREVIEW_CHARS] + ("…" if len(flat) > PREVIEW_CHARS else "")
    else:
        message["body"] = body
        # What the message looks like in the recipient's own client: the same
        # markup that was sent or received, with any quoted history folded out
        # so a reply reads as the reply rather than as the mail underneath it.
        visible, quoted = _display_body(row)
        message["html"] = visible
        if quoted:
            message["quoted_html"] = quoted
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
        "delivered_at, opened_at, opened_count, thread_id, attachments, html, quoted"
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
        "read_at, created_at, thread_id, attachments, html, quoted, report_token) "
        "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)",
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
        row.get("html"),
        row.get("quoted"),
        row.get("report_token"),
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

# The editor sends HTML so the recipient gets real formatting, and received mail
# arrives as HTML already. Only shapes a letter actually needs are kept: anything
# that could run, frame, or restyle the page around it is dropped before the
# markup is stored or sent, because both ends render it.
ALLOWED_HTML_TAGS = frozenset({
    "p", "div", "br", "b", "strong", "i", "em", "u", "s", "strike", "ul", "ol", "li",
    "blockquote", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "pre", "code", "a",
    "span", "small", "sup", "sub", "dl", "dt", "dd", "img",
    "table", "thead", "tbody", "tfoot", "tr", "td", "th", "caption", "colgroup", "col",
})
DROPPED_HTML_TAGS = (
    "script", "style", "iframe", "object", "embed", "form", "input", "button",
    "textarea", "select", "meta", "link", "svg", "math", "head", "title", "base",
)
_SAFE_LINK_PREFIXES = ("http://", "https://", "mailto:")
_TABLE_ATTRIBUTES = ("colspan", "rowspan", "width", "height", "align", "valign", "border", "cellpadding", "cellspacing")

# A letter's own styling is inline, and most of it is presentational. What is
# left out is what could take the page over (positioning, overlays) or fetch
# something the sanitizer did not vet (``url(...)``).
_SAFE_STYLE_PROPERTIES = frozenset({
    "color", "background", "background-color", "font", "font-family", "font-size",
    "font-style", "font-weight", "letter-spacing", "line-height", "text-align",
    "text-decoration", "text-indent", "text-transform", "white-space", "word-break",
    "overflow-wrap", "word-wrap", "vertical-align", "display", "float",
    "margin", "margin-top", "margin-right", "margin-bottom", "margin-left",
    "padding", "padding-top", "padding-right", "padding-bottom", "padding-left",
    "border", "border-top", "border-right", "border-bottom", "border-left",
    "border-color", "border-radius", "border-style", "border-width", "border-collapse",
    "width", "height", "max-width", "min-width", "max-height", "min-height",
    "list-style", "list-style-type",
})
_UNSAFE_STYLE_MARKERS = ("url(", "expression", "javascript:", "@import", "behavior", "\\", "<", "position")

# The composed body is wrapped in this so a plain-text draft still looks like a
# letter rather than an unformatted stream of text.
_BODY_STYLE = "font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;font-size:14px;line-height:1.65;color:#25332c;"


def _safe_style(value) -> str:
    """The declarations of an inline style that cannot escape the letter."""
    declarations: list[str] = []
    for declaration in str(value or "").replace("\n", " ").split(";"):
        name, _, raw = declaration.partition(":")
        name = name.strip().lower()
        raw = " ".join(raw.split())
        if not name or not raw or name not in _SAFE_STYLE_PROPERTIES or len(raw) > 200:
            continue
        lowered = raw.lower()
        if any(marker in lowered for marker in _UNSAFE_STYLE_MARKERS):
            continue
        declarations.append(f"{name}:{raw}")
    return ";".join(declarations)


def _safe_image_source(value) -> str:
    """A picture the reader can load, and only a picture.

    ``cid:`` references point at the mail's own MIME parts, which are not kept
    here, and an inline SVG can carry markup, so both are dropped rather than
    left as a broken box in the body.
    """
    url = str(value or "").strip()
    lowered = url.lower()
    if lowered.startswith("https://"):
        return url
    if lowered.startswith("data:image/") and not lowered.startswith("data:image/svg"):
        return url
    return ""


def _sanitize_html(markup: str) -> str:
    """Reduce mail HTML to the tags, attributes, and styling a letter needs."""
    if not markup:
        return ""
    soup = BeautifulSoup(markup, "html.parser")
    for tag in soup(list(DROPPED_HTML_TAGS)):
        tag.decompose()
    for tag in soup.find_all(True):
        if tag.name not in ALLOWED_HTML_TAGS:
            tag.unwrap()
            continue
        attributes: dict[str, str] = {}
        style = _safe_style(tag.get("style"))
        if style:
            attributes["style"] = style
        if tag.name == "a":
            href = str(tag.get("href") or "").strip()
            if href.lower().startswith(_SAFE_LINK_PREFIXES):
                attributes.update(href=href, target="_blank", rel="noopener noreferrer")
        elif tag.name == "img":
            source = _safe_image_source(tag.get("src"))
            if not source:
                tag.extract()
                continue
            attributes["src"] = source
            # A picture in a letter should not tell the sender which page opened
            # it, and one far down a long mail should not load until seen.
            attributes.update(loading="lazy", referrerpolicy="no-referrer")
            for name in ("alt", "width", "height"):
                value = str(tag.get(name) or "").strip()[:200]
                if value:
                    attributes[name] = value
        elif tag.name in ("table", "thead", "tbody", "tfoot", "tr", "td", "th"):
            for name in _TABLE_ATTRIBUTES:
                value = str(tag.get(name) or "").strip()[:40]
                if value:
                    attributes[name] = value
        elif tag.name == "ol":
            start = str(tag.get("start") or "").strip()
            if start.isdigit():
                attributes["start"] = start
        elif tag.name == "li":
            value = str(tag.get("value") or "").strip()
            if value.isdigit():
                attributes["value"] = value
        tag.attrs = attributes
    return str(soup).strip()


def _text_body_html(text: str) -> str:
    """Plain text as display markup, keeping the line breaks it was written with."""
    escaped = html.escape(str(text or "")).replace("\n", "<br>")
    return f'<div style="white-space:pre-wrap;">{escaped}</div>'


# ── What a reader shows: the new text, with the history folded away ──────────

# Every mail client introduces the history it carries with the same sentence,
# and most also wrap it in a marker. A reply is read for what was just written,
# so that tail is kept — a reader can open it again — but folded out of the way.
_QUOTE_MARKER_RE = re.compile(
    r"gmail_quote|divRplyFwdMsg|appendonsend|moz-cite-prefix|yahoo_quoted", re.IGNORECASE
)
_ATTRIBUTION_RE = re.compile(r"^On\b.{2,400}?\bwrote:\s*$", re.IGNORECASE | re.DOTALL)
_ORIGINAL_RE = re.compile(r"^-{2,}\s*(?:Original Message|Forwarded message)\s*-{2,}$", re.IGNORECASE)
_REPLY_HEADER_RE = re.compile(r"^From:\s*\S.{0,300}?\bSent:\s*\S", re.IGNORECASE | re.DOTALL)
_QUOTE_TAGS = ("div", "p", "span", "section", "td")


def _collapse(value) -> str:
    return " ".join(str(value or "").split())


def _quote_anchor(soup):
    """The element a quoted history starts at, if the markup carries one."""
    for tag in soup.find_all(True):
        if _QUOTE_MARKER_RE.search(f"{tag.get('class') or ''} {tag.get('id') or ''}"):
            return tag
    for quoted in soup.find_all("blockquote"):
        return quoted
    for tag in soup.find_all(list(_QUOTE_TAGS)):
        text = _collapse(tag.get_text(" "))
        if len(text) > 500:
            continue
        if _ATTRIBUTION_RE.match(text) or _ORIGINAL_RE.match(text) or _REPLY_HEADER_RE.match(text):
            return tag
    return None


def _quote_start(anchor):
    """Walk back over the blank nodes and the attribution line that introduce it."""
    start = anchor
    sibling = anchor.previous_sibling
    while sibling is not None:
        if getattr(sibling, "name", None) is None:
            if str(sibling).strip():
                break
            start = sibling
        else:
            text = _collapse(sibling.get_text(" "))
            if not text:
                start = sibling
            elif len(text) <= 500 and (
                _ATTRIBUTION_RE.match(text) or _ORIGINAL_RE.match(text) or _REPLY_HEADER_RE.match(text)
            ):
                start = sibling
            else:
                break
        sibling = sibling.previous_sibling
    return start


def _drop_empty_wrapper(tag) -> None:
    """Remove the container a client put around its quote, once it is empty.

    Leaving it behind would give the reader an empty box where the history used
    to be. Only wrappers that hold nothing else are removed, so a message that
    was itself empty stays as it was.
    """
    while tag is not None and getattr(tag, "name", None) in ("div", "span", "section", "td"):
        if tag.get_text(strip=True) or tag.find("img"):
            return
        parent = tag.parent
        tag.extract()
        tag = parent


def _split_quoted_html(markup: str) -> tuple[str, str]:
    """One body split into what was written and the history it quotes."""
    try:
        soup = BeautifulSoup(markup, "html.parser")
    except Exception:  # pragma: no cover - the parser does not fail on text
        return markup, ""
    anchor = _quote_anchor(soup)
    if anchor is None:
        return markup, ""
    start = _quote_start(anchor)
    nodes = [start, *list(start.next_siblings)]
    container = start.parent
    quoted = "".join(str(node) for node in nodes).strip()
    for node in nodes:
        node.extract()
    _drop_empty_wrapper(container)
    return str(soup).strip(), quoted


def _quote_line(lines: list[str]) -> int | None:
    """The first line of the quoted history in a plain-text body."""
    for index, line in enumerate(lines):
        if _ORIGINAL_RE.match(line.strip()):
            return index
        # A client wraps its attribution over two or three lines before the quote.
        for width in (1, 2, 3):
            window = _collapse(" ".join(lines[index:index + width]))
            if len(window) > 500:
                continue
            if _ATTRIBUTION_RE.match(window) or _REPLY_HEADER_RE.match(window):
                return index
    # Nothing announced the quote: a trailing run of ">" lines is still one.
    tail = None
    for index in range(len(lines) - 1, -1, -1):
        stripped = lines[index].strip()
        if not stripped:
            continue
        if not stripped.startswith(">"):
            break
        tail = index
    return tail


def _split_quoted_text(text: str) -> tuple[str, str]:
    """The same split for a body that arrived as plain text only."""
    lines = str(text or "").splitlines()
    start = _quote_line(lines)
    if start is None:
        return str(text or "").strip(), ""
    return "\n".join(lines[:start]).strip(), "\n".join(lines[start:]).strip()


def _display_body(row: dict) -> tuple[str, str]:
    """A message as the recipient's inbox shows it, and the history it quotes.

    Both halves were split and sanitized on the way in, so what is stored is
    exactly what a browser may render. A message from before markup was kept
    falls back to its text, escaped here — a body is never handed to a browser
    as it arrived, and never twice-rendered once it was.
    """
    markup = str(row.get("html") or "").strip()
    quoted = str(row.get("quoted") or "").strip()
    if markup or quoted:
        return markup, quoted
    visible, history = _split_quoted_text(str(row.get("body") or ""))
    return _text_body_html(visible), (_text_body_html(history) if history else "")


def _preview_text(body: str) -> str:
    """The one-line gist of a message, without the history it quotes."""
    visible, quoted = _split_quoted_text(str(body or ""))
    source = visible if visible.strip() else quoted
    return " ".join(line.lstrip("> ").strip() for line in source.splitlines() if line.strip())


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
    # The avatar is a public HTTPS URL on Discord's CDN; anything else would be
    # a broken image in somebody's mail client, so it is dropped instead.
    avatar = str(identity.get("avatar_url") or "").strip()
    if not avatar.lower().startswith("https://"):
        avatar = ""
    return {
        "name": name,
        "username": username,
        "address": personal or f"{local}@{domain}",
        "team": f"Niko {_SHARED_BY_LOCAL[local]['label']}",
        "avatar": avatar,
        "initials": "".join(part[0] for part in name.split()[:2]).upper(),
    }


def _signature_html(details: dict) -> str:
    """A compact profile card: the sender's picture, name, and how to reach them.

    Mail clients ignore stylesheets and many strip <style> blocks, so the card
    is a table with its styling inline. Without a picture the card shows their
    initials rather than a broken image, so it reads as one card either way.
    """
    name = html.escape(details["name"])
    team = html.escape(details["team"])
    address = details["address"]
    handle = f"@{html.escape(details['username'])} · {team}" if details.get("username") else team
    avatar = details.get("avatar") or ""
    if avatar:
        portrait = (
            f'<img src="{html.escape(avatar, quote=True)}" width="46" height="46" alt="{name}" '
            'style="display:block;width:46px;height:46px;border-radius:50%;border:0;'
            'outline:none;text-decoration:none;">'
        )
    else:
        portrait = (
            '<div style="width:46px;height:46px;border-radius:50%;background:#8bd5b1;'
            'color:#16241d;font-size:16px;font-weight:700;line-height:46px;text-align:center;">'
            f'{html.escape(details.get("initials") or "")}</div>'
        )
    return (
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" '
        'style="margin:26px 0 0;border-collapse:separate;border:1px solid #e2ece6;'
        'border-radius:14px;background:#f7fbf9;'
        'font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;">'
        "<tr>"
        f'<td width="46" style="padding:13px 0 13px 14px;vertical-align:middle;">{portrait}</td>'
        '<td style="padding:11px 17px 12px 12px;vertical-align:middle;">'
        f'<div style="font-size:14px;font-weight:700;color:#16241d;letter-spacing:-0.2px;">{name}</div>'
        f'<div style="margin:3px 0 0;font-size:11.5px;line-height:1.4;color:#5f7268;">{handle}</div>'
        '<div style="margin:6px 0 0;font-size:12px;line-height:1.4;">'
        f'<a href="mailto:{html.escape(address, quote=True)}" style="color:#2f7d5c;text-decoration:none;">{html.escape(address)}</a>'
        "</div></td></tr></table>"
    )


def _signature_text(details: dict) -> str:
    handle = f" (@{details['username']})" if details.get("username") else ""
    return f"—\n{details['name']}{handle} · {details['team']}\n{details['address']}"


# ── Reporting a sent message ────────────────────────────────────────────────
#
# Every mail leaves with a link back to a form, and that link is the only way
# in: the token is random, minted with that one mail, and reaches nothing else
# in the mailbox. A report is filed against the message, never against an
# address, so the owner sees exactly what was sent and who received it.

REPORT_PATH = "/report"
REPORT_TOKEN_BYTES = 24
REPORT_REASONS = (
    ("spam", "Spam or unsolicited mail"),
    ("phishing", "Phishing or a suspicious link"),
    ("harassment", "Harassment or abuse"),
    ("inappropriate", "Inappropriate content"),
    ("mistake", "I should not have received this"),
    ("other", "Something else"),
)
REPORT_REASON_LABELS = dict(REPORT_REASONS)
MAX_REPORT_DETAILS = 1200
MAX_REPORTS_PER_MESSAGE = 5


def _report_origin() -> str:
    """The public origin a recipient's report link points at.

    A send normally happens inside a request, which knows its own host. A script
    or a test has no request to ask, and the mail domain is the one origin this
    mailbox is certain of.
    """
    try:
        origin = str(runtime.public_base_url() or "").rstrip("/")
    except Exception:
        origin = ""
    return origin or f"https://{email_domain()}"


def report_url(token: str) -> str:
    """The link a recipient clicks to report the mail that carried it."""
    return f"{_report_origin()}{REPORT_PATH}/{token}"


def _report_footer_html(url: str) -> str:
    """The quiet line under every sent mail that offers a way to complain."""
    return (
        '<div style="margin:26px 0 0;padding:13px 0 0;border-top:1px solid #e2ece6;'
        f'{_BODY_STYLE}font-size:11px;line-height:1.6;color:#7c8b83;">'
        "Something wrong with this email? "
        f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer" '
        'style="color:#2f7d5c;text-decoration:underline;">'
        "Report this message</a> and the Niko team will look into it."
        "</div>"
    )


def _report_footer_text(url: str) -> str:
    return (
        "Something wrong with this email? Report it and the Niko team will look into it:\n"
        f"{url}"
    )


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
    # The link a recipient can complain through is minted here, with the mail,
    # and kept beside it so the report is about this message and no other.
    report_token = secrets.token_urlsafe(REPORT_TOKEN_BYTES)
    report_link = report_url(report_token)
    footer_markup = _report_footer_html(report_link)
    plain = body + (("\n\n" + _signature_text(signature)) if signature else "")
    plain = f"{plain}\n\n{_report_footer_text(report_link)}"
    # One piece of markup serves both ends: the recipient's client renders it,
    # and the copy kept in this mailbox shows the very same thing, signature and
    # footer all, instead of a plainer second rendering of the same mail.
    letter = _sanitize_html(html_body) if html_body else _text_body_html(body)
    signature_markup = _signature_html(signature) if signature else ""
    markup = f'<div style="{_BODY_STYLE}">{letter}</div>{signature_markup}{footer_markup}'
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
        "html": letter + signature_markup + footer_markup,
        "quoted": None,
        "report_token": report_token,
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


def _message_html(payload) -> str:
    """The delivery's own markup, when the sender's client wrote one.

    ``body-html`` is the full body as it arrived; ``stripped-html`` is Mailgun's
    own quote-stripped copy, kept as a fallback for a delivery that carries no
    full HTML. Either way it is sanitized before it is stored.
    """
    getter = getattr(payload, "getlist", None)
    parts = list(getter("body-html") or []) if getter else []
    if not parts:
        parts = [
            value for value in (_field(payload, "body-html"), _field(payload, "stripped-html")) if value
        ]
    return "\n".join(str(part) for part in parts)


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
        # The counterpart appears twice; it is passed twice because a numbered
        # placeholder that is reused is not portable across both backends here.
        "SELECT thread_id, subject FROM staff_emails WHERE mailbox = $1 "
        "AND (sender_address = $2 OR recipient_address = $3) AND created_at >= $4 "
        "ORDER BY created_at DESC LIMIT $5",
        mailbox,
        sender,
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
    # The markup the sender's own client produced, minus everything that could
    # run or restyle the page, and minus the history they quoted back at us.
    markup = _sanitize_html(_message_html(payload)[: MAX_BODY_CHARS * 4])
    visible_html, quoted_html = _split_quoted_html(markup) if markup else ("", "")

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
        "html": visible_html,
        "quoted": quoted_html,
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


def _event_failure(raw: dict) -> tuple[str, str, str]:
    """Why a delivery failed, from the flat fields or ``delivery-status``.

    ``reason`` and ``severity`` are the provider's machine codes (``espblock``,
    ``permanent``); ``detail`` is the sentence it wrote for a human, which is
    what a failed mail needs to explain itself in the reader.
    """
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
    detail = str(status.get("message") or status.get("description") or "")
    if not detail and _field(raw, "message"):
        detail = _field(raw, "message")
    return reason.strip()[:300], severity.strip()[:40], " ".join(detail.split())[:600]


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
    reason, severity, detail = _event_failure(raw)
    return {
        "event": event[:60],
        "event_id": _event_id(raw, event, message_id, occurred_at),
        "provider_message_id": message_id,
        "recipient": _event_recipient(raw),
        "reason": reason,
        "severity": severity,
        "detail": detail,
        "occurred_at": occurred_at,
    }


async def _read_events(message_id: str) -> list[dict]:
    rows = await _pool().fetch(
        "SELECT event, recipient, reason, severity, detail, occurred_at FROM staff_email_events "
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
            "detail": str(row.get("detail") or ""),
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
        "reason, severity, detail, occurred_at) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
        event["event_id"],
        (message or {}).get("message_id"),
        mailbox or None,
        event["event"],
        event["recipient"],
        event["reason"],
        event["severity"],
        event.get("detail") or None,
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


# ── The report queue ─────────────────────────────────────────────────────────


REPORT_COLUMNS = (
    "report_id, token, message_id, mailbox, reason, details, include_thread, "
    "reporter_address, created_at, status, response, responded_at, responded_by"
)


def _report_message(token: str) -> dict | None:
    """The one sent message a report link belongs to."""
    async def read():
        return await _pool().fetchrow(
            "SELECT message_id, thread_id, mailbox, direction, subject, sender_address, "
            "sender_name, recipient_address, created_at FROM staff_emails "
            "WHERE report_token = $1 LIMIT 1",
            token,
        )

    row = _run(read())
    if not row or str(row.get("direction") or "") != "outbound":
        return None
    return row


def _thread_ids(thread_id: str) -> list[str]:
    async def read():
        rows = await _pool().fetch(
            "SELECT message_id FROM staff_emails WHERE thread_id = $1 "
            "ORDER BY created_at ASC LIMIT $2",
            thread_id,
            THREAD_MAX_MESSAGES,
        )
        return [str(row.get("message_id") or "") for row in rows or []]

    return _run(read())


def _message_row(message_id: str) -> dict | None:
    async def read():
        return await _pool().fetchrow(
            f"SELECT {_message_columns()} FROM staff_emails WHERE message_id = $1",
            message_id,
        )

    return _run(read())


def _thread_rows(thread_id: str) -> list[dict]:
    async def read():
        return await _pool().fetch(
            f"SELECT {_message_columns()} FROM staff_emails WHERE thread_id = $1 "
            "ORDER BY created_at ASC LIMIT $2",
            thread_id,
            THREAD_MAX_MESSAGES,
        )

    return _run(read()) or []


def report_target(token: str) -> dict | None:
    """What the report form shows: which mail this link belongs to.

    Deliberately little: the token was only ever handed to the recipient, so the
    mail itself is not echoed back over the web on the strength of it.
    """
    row = _report_message(token)
    if row is None:
        return None
    thread_id = str(row.get("thread_id") or row.get("message_id") or "")
    return {
        "subject": str(row.get("subject") or ""),
        "from_name": row.get("sender_name") or None,
        "from_address": str(row.get("sender_address") or ""),
        "to_address": str(row.get("recipient_address") or ""),
        "sent_at": float(row.get("created_at") or 0),
        "conversation_count": len(_thread_ids(thread_id)),
        "reasons": [{"value": value, "label": label} for value, label in REPORT_REASONS],
        "max_details": MAX_REPORT_DETAILS,
    }


def submit_report(token: str, reason: str, details: str, include_thread: bool) -> dict:
    """File one recipient's report against the message the link points at."""
    row = _report_message(token)
    if row is None:
        raise StaffEmailError("That report link is no longer valid.")
    reason = str(reason or "").strip().lower()
    if reason not in REPORT_REASON_LABELS:
        raise StaffEmailError("Choose a reason for the report.")
    details = str(details or "").strip()[:MAX_REPORT_DETAILS]

    async def existing():
        return await _pool().fetch(
            "SELECT report_id FROM staff_email_reports WHERE token = $1 LIMIT $2",
            token,
            MAX_REPORTS_PER_MESSAGE + 1,
        )

    if len(_run(existing()) or []) >= MAX_REPORTS_PER_MESSAGE:
        raise StaffEmailError(
            "This message has already been reported several times. The team has it."
        )

    report_id = f"rpt-{uuid.uuid4().hex}"
    mail = {
        "report_id": report_id,
        "token": token,
        "message_id": str(row.get("message_id") or ""),
        "mailbox": str(row.get("mailbox") or ""),
        "reason": reason,
        "details": details,
        "include_thread": 1 if include_thread else 0,
        "reporter_address": str(row.get("recipient_address") or ""),
        "created_at": time.time(),
        "status": "open",
    }

    async def store():
        await _pool().execute(
            "INSERT INTO staff_email_reports (report_id, token, message_id, mailbox, reason, "
            "details, include_thread, reporter_address, created_at, status) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
            mail["report_id"],
            mail["token"],
            mail["message_id"],
            mail["mailbox"],
            mail["reason"],
            mail["details"],
            mail["include_thread"],
            mail["reporter_address"],
            mail["created_at"],
            mail["status"],
        )

    _run(store())
    return _report_payload(mail)


def _report_payload(row: dict) -> dict:
    reason = str(row.get("reason") or "")
    return {
        "report_id": str(row.get("report_id") or ""),
        "message_id": str(row.get("message_id") or ""),
        "mailbox": str(row.get("mailbox") or ""),
        "reason": reason,
        "reason_label": REPORT_REASON_LABELS.get(reason, reason),
        "details": str(row.get("details") or ""),
        "include_thread": bool(int(row.get("include_thread") or 0)),
        "reporter_address": str(row.get("reporter_address") or ""),
        "created_at": float(row.get("created_at") or 0),
        "status": str(row.get("status") or "open"),
        "response": row.get("response"),
        "responded_at": row.get("responded_at"),
        "responded_by": str(row.get("responded_by") or "") or None,
    }


def list_reports(limit: int = 100) -> list[dict]:
    """The owner's queue: every report, with the message it is about.

    The conversation is attached only when the reporter chose to share it, which
    is the whole point of asking: what they did not agree to share stays out of
    the report.
    """
    async def read():
        return await _pool().fetch(
            f"SELECT {REPORT_COLUMNS} FROM staff_email_reports ORDER BY created_at DESC LIMIT $1",
            max(1, min(int(limit), 200)),
        )

    reports: list[dict] = []
    for row in _run(read()) or []:
        report = _report_payload(row)
        message = _message_row(report["message_id"])
        report["message"] = _serialize(message) if message else None
        if report["include_thread"] and message:
            thread_id = str(message.get("thread_id") or message.get("message_id") or "")
            # Only what had happened when they reported: they agreed to share the
            # conversation they had seen, not whatever was written after it.
            report["thread"] = [
                _serialize(entry) for entry in _thread_rows(thread_id)
                if float(entry.get("created_at") or 0) <= report["created_at"]
            ]
        else:
            report["thread"] = []
        reports.append(report)
    return reports


def _report_row(report_id: str) -> dict | None:
    async def read():
        return await _pool().fetchrow(
            f"SELECT {REPORT_COLUMNS} FROM staff_email_reports WHERE report_id = $1",
            report_id,
        )

    return _run(read())


def _close_report(report_id: str, owner_id: int | None, reply: str | None) -> dict:
    now = time.time()

    async def store():
        await _pool().execute(
            "UPDATE staff_email_reports SET status = $1, response = $2, responded_at = $3, "
            "responded_by = $4 WHERE report_id = $5",
            "replied" if reply else "resolved",
            reply,
            now,
            str(owner_id or ""),
            report_id,
        )

    _run(store())
    row = _report_row(report_id)
    return _report_payload(row) if row else {"report_id": report_id, "status": "resolved"}


def respond_to_report(report_id: str, message: str, owner_id: int | None) -> dict:
    """Answer a report by email, to the address the mail was sent to.

    The answer comes from the mailbox the reported mail came from, so it lands in
    the same conversation. A report about somebody's private address is answered
    from support instead: the owner cannot write from another person's box.
    """
    report = _report_row(report_id)
    if report is None:
        raise StaffEmailError("That report is no longer in the queue.")
    if str(report.get("status") or "") == "resolved":
        raise StaffEmailError("That report is already closed.")
    text = str(message or "").strip()[:MAX_BODY_CHARS]
    if not text:
        raise StaffEmailError("Write a response before sending it.")
    source = _message_row(str(report.get("message_id") or ""))
    if source is None:
        raise StaffEmailError("The reported message is no longer in the mailbox.")
    recipient = str(report.get("reporter_address") or source.get("recipient_address") or "").strip()
    if not recipient:
        raise StaffEmailError("There is no address to answer on this report.")

    subject = str(source.get("subject") or "").strip() or "(no subject)"
    reply_subject = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    mailbox = str(report.get("mailbox") or source.get("mailbox") or "").strip().lower()
    thread_id = str(source.get("thread_id") or "").strip() or None
    if not mailbox or not mailbox_allowed("owner", mailbox, owner_id):
        mailbox = "support"
        thread_id = None

    sent = send_message(
        role="owner",
        mailbox=mailbox,
        recipient=recipient,
        subject=reply_subject,
        body=text,
        staff_user_id=owner_id,
        thread_id=thread_id,
    )
    return {"report": _close_report(report_id, owner_id, text), "message": sent}


def close_report(report_id: str, owner_id: int | None) -> dict:
    """Close a report without writing back (nothing to add, or already handled)."""
    report = _report_row(report_id)
    if report is None:
        raise StaffEmailError("That report is no longer in the queue.")
    if str(report.get("status") or "") == "resolved":
        raise StaffEmailError("That report is already closed.")
    return _close_report(report_id, owner_id, None)
