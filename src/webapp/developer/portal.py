"""Developer API access, scoped keys, and the owner's access roster.

The public API is deliberately small. Every endpoint that returns user data is
served under ``/api/v1`` and needs a key whose scopes are a subset of the scopes
the developer was granted. The website's own data routes stay available to the
site's same-origin fetches, but an external caller has to use this API.

Keys are never stored in plain text. The raw key is returned once, at creation;
the store keeps a peppered hash and a short display prefix so the portal can show
which key was used without ever being able to recreate it.

Grants, keys, usage rows, appeals and the hash pepper live in the portal's own
MongoDB database (see ``store``), not in the bot's primary database and
not on the deployment's disk, which production does not keep between deploys.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import threading
import time
from collections import deque
from functools import wraps
from urllib.parse import urlsplit

from flask import g, request, session

from config.ids import is_owner_id
from utils import logging

from ..api_errors import error_response
from .. import security as security_store
from . import store

#: Bump this when the developer guidelines change. A developer who accepted an
#: older version sees the agreement again before creating another key.
POLICY_VERSION = 2

POLICY_UPDATED = "2026-11-05"

#: Every scope a developer can be granted. The order is the order the portal
#: lists them in, from useful-for-migration to sensitive operations.
SCOPES: dict[str, dict] = {
    "economy:read": {
        "label": "Economy read",
        "description": "Read global economy standings and a user's current economy profile.",
        "sensitive": False,
    },
    "levels:read": {
        "label": "Leveling read",
        "description": "Read a server's leveling standings and one member's XP and level.",
        "sensitive": False,
    },
    "users:read": {
        "label": "User profiles",
        "description": "Resolve Discord usernames, display names, and avatars by user ID.",
        "sensitive": False,
    },
    "warns:read": {
        "label": "Warnings read",
        "description": "Read warning cases for guilds where the integration is allowed to operate.",
        "sensitive": False,
    },
    "warns:write": {
        "label": "Warnings write",
        "description": "Create and remove warning cases for allowed guilds. Intended for bot synchronization.",
        "sensitive": True,
    },
    "levels:write": {
        "label": "Leveling write",
        "description": "Write XP and levels for one member in a server.",
        "sensitive": True,
    },
    "blacklist:read": {
        "label": "Blacklist read",
        "description": "Read blacklist entries and their recorded reasons. Highly restricted.",
        "sensitive": True,
        "restricted": True,
    },
    "blacklist:write": {
        "label": "Blacklist write",
        "description": "Add or remove blacklist entries. Granted only to highly trusted applications.",
        "sensitive": True,
        "restricted": True,
    },
    "guilds:cross_server": {
        "label": "Cross-server access",
        "description": "Access approved moderation data for guilds the application's bot does not share with Niko. Highly restricted.",
        "sensitive": True,
        "restricted": True,
    },
}

ALL_SCOPES = tuple(SCOPES)

#: These scopes are never self-service. The portal hides them from application
#: requests and the owner explicitly selects them during review.
RESTRICTED_SCOPES = frozenset(
    scope for scope, definition in SCOPES.items() if definition.get("restricted")
)

_STORE_VERSION = 2
_USAGE_LIMIT = 5000
_LOCK = threading.RLock()

#: External requests are limited per source address before a key is even read,
#: so an invalid or leaked key still cannot drive an unbounded scan.
IP_RATE_LIMIT = 120
IP_RATE_WINDOW = 60.0

#: A single key is expected to stay well below this because every integration
#: is reviewed. Crossing the hard threshold is treated as automated abuse.
KEY_RATE_LIMIT = 300
KEY_RATE_WINDOW = 60.0

#: These four signals catch automation that rotates addresses or hides behind
#: the per-IP allowance: sustained volume, high error ratios, widely distributed
#: key use, and repeated rate-limit blocks.
ABUSE_ERROR_LIMIT = 80
ABUSE_ERROR_RATIO = 0.8
ABUSE_IP_LIMIT = 12
ABUSE_IP_WINDOW = 300.0
ABUSE_IP_MIN_REQUESTS = 30
ABUSE_BLOCK_LIMIT = 20
ABUSE_BLOCK_WINDOW = 300.0
_TRACKER_TTL = 600.0

_KEY_HITS: dict[str, dict] = {}
_TRACK_LOCK = threading.RLock()


def _pepper() -> bytes:
    """The stable secret mixed into key hashes.

    An environment variable wins so a deployment can manage it like the other
    application secrets. Otherwise the value is generated once and stored with
    the portal data, which is what keeps issued keys valid across restarts on a
    host without a persistent disk.
    """
    return store.key_pepper()


def _hash_key(raw_key: str) -> str:
    return hashlib.sha256(_pepper() + b":" + raw_key.encode("utf-8")).hexdigest()


def _empty_store() -> dict:
    return {
        "version": _STORE_VERSION,
        "developers": {},
        "keys": {},
        "usage": [],
        "appeals": [],
    }


def _normalise_store(document) -> dict:
    if not isinstance(document, dict):
        return _empty_store()
    developers = document.get("developers")
    keys = document.get("keys")
    usage = document.get("usage")
    appeals = document.get("appeals")
    return {
        "version": _STORE_VERSION,
        "developers": developers if isinstance(developers, dict) else {},
        "keys": keys if isinstance(keys, dict) else {},
        "usage": usage if isinstance(usage, list) else [],
        "appeals": appeals if isinstance(appeals, list) else [],
    }


def _load() -> dict:
    """Read the portal document from its store.

    MongoDB is used whenever it is configured; the historical JSON file is the
    local fallback (see ``store``).
    """
    return _normalise_store(store.load_document("portal"))


def _save(document: dict) -> None:
    store.save_document("portal", _normalise_store(document))


def _now() -> float:
    return time.time()


def _clean_scopes(raw) -> list[str]:
    if not isinstance(raw, (list, tuple, set)):
        return []
    seen: set[str] = set()
    scopes: list[str] = []
    for item in raw:
        scope = str(item or "").strip()
        if scope in SCOPES and scope not in seen:
            seen.add(scope)
            scopes.append(scope)
    return [scope for scope in ALL_SCOPES if scope in seen]


def _owner_scopes() -> list[str]:
    return list(ALL_SCOPES)


def _public_suspension(suspension) -> dict | None:
    if not isinstance(suspension, dict):
        return None
    return {
        "id": str(suspension.get("id") or ""),
        "active": bool(suspension.get("active", True)),
        "reason": str(suspension.get("reason") or ""),
        "trigger": str(suspension.get("trigger") or "abuse_detection"),
        "at": suspension.get("at"),
        "key_id": str(suspension.get("key_id") or "") or None,
        "key_prefix": str(suspension.get("key_prefix") or "") or None,
        "appeal_id": str(suspension.get("appeal_id") or "") or None,
        "notified_at": suspension.get("notified_at"),
        "resolved_at": suspension.get("resolved_at"),
        "resolution": str(suspension.get("resolution") or "") or None,
        "metadata": suspension.get("metadata") if isinstance(suspension.get("metadata"), dict) else {},
    }


def _public_appeal(appeal) -> dict | None:
    if not isinstance(appeal, dict):
        return None
    return {
        "id": str(appeal.get("id") or ""),
        "status": str(appeal.get("status") or "pending"),
        "text": str(appeal.get("text") or ""),
        "created_at": appeal.get("created_at"),
        "reviewed_at": appeal.get("reviewed_at"),
        "reviewed_by": str(appeal.get("reviewed_by") or "") or None,
        "note": str(appeal.get("note") or "") or None,
        "notified_at": appeal.get("notified_at"),
    }


def _latest_appeal(store: dict, suspension_id: str) -> dict | None:
    if not suspension_id:
        return None
    appeals = [
        appeal for appeal in store.get("appeals", [])
        if isinstance(appeal, dict) and str(appeal.get("suspension_id")) == str(suspension_id)
    ]
    if not appeals:
        return None
    appeals.sort(key=lambda item: float(item.get("created_at") or 0), reverse=True)
    return appeals[0]


def _active_suspension(record: dict | None) -> dict | None:
    if not isinstance(record, dict):
        return None
    suspension = record.get("suspension")
    if isinstance(suspension, dict) and suspension.get("active", True):
        return suspension
    return None


def developer_record(user_id: str) -> dict | None:
    user_id = str(user_id or "").strip()
    if not user_id:
        return None
    record = _load()["developers"].get(user_id)
    return record if isinstance(record, dict) else None


def developer_is_owner(user_id: str) -> bool:
    return is_owner_id(user_id)


def developer_access(user_id: str) -> dict:
    """The access shape both the portal and the key authenticator use.

    The owner is implicitly active with every scope. Everyone else needs a
    persisted grant; an empty or disabled grant is denied, not merely read-only.
    """
    user_id = str(user_id or "").strip()
    if developer_is_owner(user_id):
        return {
            "user_id": user_id,
            "is_owner": True,
            "enabled": True,
            "granted": True,
            "suspended": False,
            "suspension": None,
            "appeal": None,
            "scopes": _owner_scopes(),
            "notes": "",
            "policy_version": POLICY_VERSION,
            "policy_accepted": True,
            "policy_accepted_at": None,
            "granted_at": None,
            "granted_by": None,
        }
    record = developer_record(user_id)
    if record is None:
        return {
            "user_id": user_id,
            "is_owner": False,
            "enabled": False,
            "granted": False,
            "suspended": False,
            "suspension": None,
            "appeal": None,
            "scopes": [],
            "notes": "",
            "policy_version": POLICY_VERSION,
            "policy_accepted": False,
            "policy_accepted_at": None,
            "granted_at": None,
            "granted_by": None,
        }
    accepted_version = int(record.get("policy_version") or 0)
    granted = bool(record.get("enabled", True))
    suspension = _active_suspension(record)
    suspended = suspension is not None
    latest_appeal = _latest_appeal(_load(), str(suspension.get("id") or "")) if suspension else None
    return {
        "user_id": user_id,
        "is_owner": False,
        "enabled": granted and not suspended,
        "granted": granted,
        "suspended": suspended,
        "suspension": _public_suspension(suspension) if suspension else None,
        "appeal": _public_appeal(latest_appeal) if latest_appeal else None,
        "scopes": _clean_scopes(record.get("scopes")),
        "notes": str(record.get("notes") or ""),
        "policy_version": POLICY_VERSION,
        "policy_accepted": accepted_version >= POLICY_VERSION and bool(record.get("policy_accepted_at")),
        "policy_accepted_at": record.get("policy_accepted_at"),
        "granted_at": record.get("granted_at"),
        "granted_by": record.get("granted_by"),
    }


def has_scope(user_id: str, scope: str) -> bool:
    access = developer_access(user_id)
    return bool(access["enabled"] and scope in access["scopes"])


def accept_policy(user_id: str) -> dict:
    user_id = str(user_id or "").strip()
    if developer_is_owner(user_id):
        return developer_access(user_id)
    with _LOCK:
        store = _load()
        record = store["developers"].get(user_id)
        if not isinstance(record, dict) or not record.get("enabled", True):
            raise PermissionError("Developer access has not been granted.")
        if _active_suspension(record):
            raise PermissionError("Developer access is suspended. Submit an appeal in Discord.")
        record["policy_version"] = POLICY_VERSION
        record["policy_accepted_at"] = _now()
        _save(store)
    return developer_access(user_id)


def grant_access(
    user_id: str,
    scopes,
    *,
    enabled: bool = True,
    notes: str = "",
    actor_id: str = "",
    identity: dict | None = None,
) -> dict:
    user_id = str(user_id or "").strip()
    if not user_id.isdigit() or len(user_id) > 22:
        raise ValueError("A valid Discord user ID is required.")
    if developer_is_owner(user_id):
        raise ValueError("The bot owner already has full developer access.")
    cleaned = _clean_scopes(scopes)
    if enabled and not cleaned:
        raise ValueError("Grant at least one API permission.")
    identity = identity if isinstance(identity, dict) else {}
    now = _now()
    with _LOCK:
        store = _load()
        previous = store["developers"].get(user_id) if isinstance(store["developers"].get(user_id), dict) else {}
        suspension = previous.get("suspension") if isinstance(previous.get("suspension"), dict) else None
        record = {
            **previous,
            "user_id": user_id,
            "username": str(identity.get("username") or previous.get("username") or ""),
            "display_name": str(identity.get("display_name") or previous.get("display_name") or ""),
            "avatar_url": identity.get("avatar_url") or previous.get("avatar_url"),
            "enabled": bool(enabled),
            "scopes": cleaned,
            "notes": str(notes or previous.get("notes") or "")[:1000],
            "granted_at": previous.get("granted_at") or now,
            "granted_by": str(actor_id or previous.get("granted_by") or ""),
            "updated_at": now,
            # A grant change does not silently accept the guidelines on the
            # developer's behalf. The portal still asks them once.
            "policy_version": int(previous.get("policy_version") or 0),
            "policy_accepted_at": previous.get("policy_accepted_at"),
            "suspension": suspension,
        }
        store["developers"][user_id] = record
        if not enabled:
            for key in store["keys"].values():
                if str(key.get("user_id")) == user_id and not key.get("revoked_at"):
                    key["revoked_at"] = now
        _save(store)
    return developer_access(user_id)


def revoke_access(user_id: str, *, actor_id: str = "") -> bool:
    user_id = str(user_id or "").strip()
    if developer_is_owner(user_id):
        raise ValueError("The bot owner's developer access cannot be revoked.")
    with _LOCK:
        store = _load()
        record = store["developers"].get(user_id)
        if not isinstance(record, dict):
            return False
        if record.get("enabled", True) is not False:
            record["enabled"] = False
            record["updated_at"] = _now()
            record["revoked_by"] = str(actor_id or "")
            for key in store["keys"].values():
                if str(key.get("user_id")) == user_id and not key.get("revoked_at"):
                    key["revoked_at"] = _now()
            _save(store)
    return True


def _identity_rows(store: dict) -> list[dict]:
    rows = []
    for user_id, record in store["developers"].items():
        if not isinstance(record, dict):
            continue
        access = developer_access(str(user_id))
        keys = [key for key in store["keys"].values() if str(key.get("user_id")) == str(user_id)]
        active_keys = [key for key in keys if not key.get("revoked_at")]
        last_used = max((float(key.get("last_used_at") or 0) for key in keys), default=0)
        rows.append({
            **access,
            "username": str(record.get("username") or ""),
            "display_name": str(record.get("display_name") or ""),
            "avatar_url": record.get("avatar_url"),
            "key_count": len(active_keys),
            "last_used_at": last_used or None,
            "updated_at": record.get("updated_at") or record.get("granted_at"),
        })
    rows.sort(key=lambda item: (not item["enabled"], item["display_name"].casefold() or item["user_id"]))
    return rows


def appeal_rows() -> list[dict]:
    """Every appeal for the owner's review queue."""
    store = _load()
    appeals = [
        _public_appeal(appeal) | {"user_id": str(appeal.get("user_id") or "")}
        for appeal in store.get("appeals", [])
        if isinstance(appeal, dict)
    ]
    appeals.sort(key=lambda item: float(item.get("created_at") or 0), reverse=True)
    return [appeal for appeal in appeals if appeal.get("id")]


def access_rows() -> dict:
    store = _load()
    owners = [
        {
            "user_id": str(user_id),
            "is_owner": True,
            "enabled": True,
            "scopes": _owner_scopes(),
            "notes": "Bot owner — full access",
        }
        for user_id in sorted(_configured_owner_ids())
    ]
    return {
        "scopes": scope_options(),
        "owners": owners,
        "developers": _identity_rows(store),
        "appeals": appeal_rows(),
    }


def _configured_owner_ids() -> set[str]:
    try:
        from config.ids import OWNER_IDS

        return {str(value) for value in OWNER_IDS}
    except Exception:
        return set()


def scope_options() -> list[dict]:
    return [{"key": key, **value} for key, value in SCOPES.items()]


def public_key(key: dict) -> dict:
    return {
        "id": str(key.get("id")),
        "name": str(key.get("name") or "API key"),
        "prefix": str(key.get("prefix") or ""),
        "scopes": _clean_scopes(key.get("scopes")),
        "application_id": str(key.get("application_id") or "") or None,
        "created_at": key.get("created_at"),
        "last_used_at": key.get("last_used_at"),
        "revoked_at": key.get("revoked_at"),
    }


def list_keys(user_id: str) -> list[dict]:
    user_id = str(user_id or "").strip()
    with _LOCK:
        store = _load()
        rows = [
            public_key(key)
            for key in store["keys"].values()
            if str(key.get("user_id")) == user_id
        ]
    rows.sort(key=lambda item: float(item.get("created_at") or 0), reverse=True)
    return rows


def create_key(user_id: str, name: str, scopes, *, application_id: str = "") -> tuple[dict, str]:
    user_id = str(user_id or "").strip()
    application_id = str(application_id or "").strip()
    access = developer_access(user_id)
    if access["suspended"]:
        raise PermissionError("Developer access is suspended. Submit an appeal in Discord.")
    if not access["enabled"]:
        raise PermissionError("Developer access has not been granted.")
    if not access["policy_accepted"]:
        raise PermissionError("Accept the developer guidelines before creating a key.")
    cleaned = _clean_scopes(scopes)
    if not cleaned:
        raise ValueError("Choose at least one API permission.")
    disallowed = [scope for scope in cleaned if scope not in access["scopes"]]
    if disallowed:
        raise PermissionError("One or more permissions have not been granted to this account.")
    application = None
    if application_id:
        from . import applications

        application = applications.get_application(application_id)
        if not isinstance(application, dict) or str(application.get("owner_id")) != user_id:
            raise PermissionError("That application does not belong to this account.")
        if str(application.get("status")) != "approved":
            raise PermissionError("The application must be approved before it can create keys.")
        approved_scopes = set(application.get("approved_scopes") or [])
        disallowed = [scope for scope in cleaned if scope not in approved_scopes]
        if disallowed:
            raise PermissionError("One or more permissions have not been approved for this application.")
    elif any(str(scope).startswith("warns:") for scope in cleaned):
        raise PermissionError("Warn permissions require an app-bound key.")
    elif any(scope in RESTRICTED_SCOPES for scope in cleaned):
        raise PermissionError("Special scopes require a reviewed application.")
    clean_name = " ".join(str(name or "").split()).strip()
    if not clean_name:
        raise ValueError("Give the key a name so you can recognise it later.")
    if len(clean_name) > 60:
        raise ValueError("Key names must be 60 characters or fewer.")

    raw_key = f"niko_dev_{secrets.token_urlsafe(32)}"
    key_id = secrets.token_hex(8)
    now = _now()
    record = {
        "id": key_id,
        "user_id": user_id,
        "name": clean_name,
        "prefix": raw_key[:18],
        "hash": _hash_key(raw_key),
        "scopes": cleaned,
        "application_id": application_id or None,
        "created_at": now,
        "last_used_at": None,
        "revoked_at": None,
    }
    with _LOCK:
        store = _load()
        store["keys"][key_id] = record
        _save(store)
    return public_key(record), raw_key


def revoke_key(user_id: str, key_id: str, *, allow_any: bool = False) -> bool:
    user_id = str(user_id or "").strip()
    key_id = str(key_id or "").strip()
    access = developer_access(user_id)
    if access["suspended"] and not allow_any:
        return False
    with _LOCK:
        store = _load()
        key = store["keys"].get(key_id)
        if not isinstance(key, dict):
            return False
        if not allow_any and str(key.get("user_id")) != user_id:
            return False
        if key.get("revoked_at"):
            return True
        key["revoked_at"] = _now()
        _save(store)
    return True


def usage_rows(user_id: str, *, limit: int = 100, all_users: bool = False) -> list[dict]:
    user_id = str(user_id or "").strip()
    try:
        limit = max(1, min(int(limit), 500))
    except (TypeError, ValueError):
        limit = 100
    with _LOCK:
        rows = list(_load()["usage"])
    if not all_users:
        rows = [row for row in rows if isinstance(row, dict) and str(row.get("user_id")) == user_id]
    rows = [row for row in rows if isinstance(row, dict)]
    rows.reverse()
    return rows[:limit]


# ── Suspensions, abuse signals, and appeals ──────────────────────────────────

def _clear_key_suspension(store: dict, user_id: str) -> None:
    """A suspension keeps every key revoked; approval never revives a secret."""
    for key in store["keys"].values():
        if not isinstance(key, dict) or str(key.get("user_id")) != str(user_id):
            continue
        if not key.get("revoked_at"):
            key["revoked_at"] = _now()
            key["revoked_reason"] = "developer_suspended"


def suspend_developer(
    user_id: str,
    *,
    reason: str,
    trigger: str,
    key_id: str = "",
    key_prefix: str = "",
    metadata: dict | None = None,
) -> dict | None:
    """Suspend one developer, revoke every key they own, and notify them.

    The grant stays recorded so an owner can restore it after an appeal; the
    derived ``enabled`` flag turns false while the suspension is active, which
    blocks both key authentication and developer-portal key management.
    """
    user_id = str(user_id or "").strip()
    if not user_id or developer_is_owner(user_id):
        return None
    with _LOCK:
        store = _load()
        record = store["developers"].get(user_id)
        if not isinstance(record, dict):
            return None
        existing = _active_suspension(record)
        if existing is not None:
            return _public_suspension(existing)
        now = _now()
        suspension = {
            "id": secrets.token_hex(8),
            "active": True,
            "reason": str(reason or "Automated abuse detection suspended this account.")[:1000],
            "trigger": str(trigger or "abuse_detection")[:80],
            "at": now,
            "key_id": str(key_id or "") or None,
            "key_prefix": str(key_prefix or "") or None,
            "appeal_id": None,
            "notified_at": None,
            "resolved_at": None,
            "resolution": None,
            "metadata": metadata if isinstance(metadata, dict) else {},
        }
        record["suspension"] = suspension
        record["updated_at"] = now
        _clear_key_suspension(store, user_id)
        _save(store)
    _schedule_suspension_notice(user_id, suspension["id"])
    logging.warning(
        "DeveloperAPI",
        f"Suspended developer {user_id} after {trigger}: {reason}",
    )
    return _public_suspension(suspension)


def suspension_for_user(user_id: str) -> dict | None:
    user_id = str(user_id or "").strip()
    record = developer_record(user_id)
    return _public_suspension(_active_suspension(record))


def appeal_for_user(user_id: str) -> dict | None:
    """The latest appeal attached to this developer's active suspension."""
    user_id = str(user_id or "").strip()
    record = developer_record(user_id)
    suspension = _active_suspension(record)
    if suspension is None:
        return None
    return _public_appeal(_latest_appeal(_load(), str(suspension.get("id") or "")))


def appeal_by_id(appeal_id: str) -> dict | None:
    appeal_id = str(appeal_id or "").strip()
    if not appeal_id:
        return None
    for appeal in _load().get("appeals", []):
        if isinstance(appeal, dict) and str(appeal.get("id")) == appeal_id:
            return _public_appeal(appeal)
    return None


def submit_appeal(user_id: str, text: str) -> dict:
    """Open one appeal for the developer's current suspension."""
    user_id = str(user_id or "").strip()
    clean_text = " ".join(str(text or "").split()).strip()
    if not clean_text:
        raise ValueError("Write an appeal before submitting it.")
    if len(clean_text) > 4000:
        raise ValueError("Appeals must be 4,000 characters or fewer.")
    with _LOCK:
        store = _load()
        record = store["developers"].get(user_id)
        suspension = _active_suspension(record)
        if suspension is None:
            raise PermissionError("This account does not have an active API suspension.")
        suspension_id = str(suspension.get("id") or "")
        previous = _latest_appeal(store, suspension_id)
        if previous is not None:
            status = str(previous.get("status") or "pending")
            if status == "pending":
                raise ValueError("An appeal is already under review.")
            if status == "denied":
                raise ValueError("The appeal for this suspension was already denied.")
        now = _now()
        appeal = {
            "id": secrets.token_hex(8),
            "user_id": user_id,
            "username": str(record.get("username") or ""),
            "display_name": str(record.get("display_name") or ""),
            "suspension_id": suspension_id,
            "text": clean_text,
            "status": "pending",
            "created_at": now,
            "reviewed_at": None,
            "reviewed_by": None,
            "note": None,
            "notified_at": None,
        }
        store["appeals"].append(appeal)
        suspension["appeal_id"] = appeal["id"]
        record["updated_at"] = now
        _save(store)
    return _public_appeal(appeal)


def review_appeal(
    appeal_id: str,
    status: str,
    *,
    note: str = "",
    actor_id: str = "",
) -> dict | None:
    """Approve or deny one pending appeal; approval lifts the suspension."""
    appeal_id = str(appeal_id or "").strip()
    status = str(status or "").strip().lower()
    if status not in {"approved", "denied"}:
        raise ValueError("Choose approved or denied.")
    clean_note = str(note or "").strip()[:2000]
    with _LOCK:
        store = _load()
        appeal = next(
            (item for item in store["appeals"]
             if isinstance(item, dict) and str(item.get("id")) == appeal_id),
            None,
        )
        if appeal is None:
            return None
        if str(appeal.get("status")) != "pending":
            return None
        user_id = str(appeal.get("user_id") or "")
        record = store["developers"].get(user_id)
        suspension = record.get("suspension") if isinstance(record, dict) and isinstance(record.get("suspension"), dict) else None
        now = _now()
        appeal["status"] = status
        appeal["reviewed_at"] = now
        appeal["reviewed_by"] = str(actor_id or "")
        appeal["note"] = clean_note or None
        if suspension is not None:
            suspension["resolution"] = status
            suspension["resolved_at"] = now
            if status == "approved":
                suspension["active"] = False
        if isinstance(record, dict):
            record["updated_at"] = now
        _save(store)
    _schedule_appeal_decision_notice(user_id, appeal_id)
    return _public_appeal(appeal) | {"user_id": user_id}


def mark_suspension_notified(user_id: str, suspension_id: str) -> None:
    with _LOCK:
        store = _load()
        record = store["developers"].get(str(user_id))
        suspension = record.get("suspension") if isinstance(record, dict) else None
        if not isinstance(suspension, dict) or str(suspension.get("id")) != str(suspension_id):
            return
        suspension["notified_at"] = _now()
        _save(store)


def mark_appeal_notified(appeal_id: str) -> None:
    with _LOCK:
        store = _load()
        for appeal in store["appeals"]:
            if isinstance(appeal, dict) and str(appeal.get("id")) == str(appeal_id):
                appeal["notified_at"] = _now()
                _save(store)
                return


def _schedule_suspension_notice(user_id: str, suspension_id: str) -> None:
    """Deliver the suspension DM without holding up the API request."""
    try:
        from .. import runtime

        if runtime._discord_bot is None:
            return

        async def deliver():
            from cogs.system.developer_appeals import send_suspension_dm

            await send_suspension_dm(runtime._discord_bot, user_id, suspension_id)

        runtime.schedule_on_bot_loop(deliver())
    except Exception as error:
        logging.warning("DeveloperAPI", f"Could not schedule suspension DM for {user_id}: {error}")


def _schedule_appeal_decision_notice(user_id: str, appeal_id: str) -> None:
    try:
        from .. import runtime

        if runtime._discord_bot is None:
            return

        async def deliver():
            from cogs.system.developer_appeals import send_appeal_decision_dm

            await send_appeal_decision_dm(runtime._discord_bot, user_id, appeal_id)

        runtime.schedule_on_bot_loop(deliver())
    except Exception as error:
        logging.warning("DeveloperAPI", f"Could not schedule appeal decision DM for {user_id}: {error}")


def _request_token() -> str:
    authorization = (request.headers.get("Authorization") or "").strip()
    if authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return (request.headers.get("X-API-Key") or "").strip()


def authenticate(token: str, *, allow_suspended: bool = False) -> dict | None:
    token = str(token or "").strip()
    if not token:
        return None
    digest = _hash_key(token)
    with _LOCK:
        store = _load()
        for key in store["keys"].values():
            if not isinstance(key, dict):
                continue
            stored = str(key.get("hash") or "")
            if not stored or not hmac.compare_digest(stored, digest):
                continue
            user_id = str(key.get("user_id") or "")
            access = developer_access(user_id)
            application = None
            application_id = str(key.get("application_id") or "")
            if application_id:
                from . import applications

                application = applications.get_application(application_id)
                if (
                    not isinstance(application, dict)
                    or str(application.get("owner_id")) != user_id
                    or str(application.get("status")) != "approved"
                ):
                    continue
            def application_summary():
                if not application:
                    return None
                from . import applications

                return applications.application_summary(application)

            if key.get("revoked_at"):
                if allow_suspended and key.get("revoked_reason") == "developer_suspended" and access["suspended"]:
                    return {
                        "key": public_key(key),
                        "user_id": user_id,
                        "scopes": [],
                        "access": access,
                        "application": application_summary(),
                        "suspended": True,
                    }
                continue
            if not access["enabled"]:
                if allow_suspended and access["suspended"]:
                    return {
                        "key": public_key(key),
                        "user_id": user_id,
                        "scopes": [],
                        "access": access,
                        "application": application_summary(),
                        "suspended": True,
                    }
                return None
            key["last_used_at"] = _now()
            _save(store)
            approved_by_application = set(application.get("approved_scopes") or []) if application else None
            return {
                "key": public_key(key),
                "user_id": user_id,
                "scopes": [
                    scope for scope in _clean_scopes(key.get("scopes"))
                    if scope in access["scopes"]
                    and (approved_by_application is None or scope in approved_by_application)
                ],
                "access": access,
                "application": application_summary(),
                "suspended": False,
            }
    return None


def _client_ip() -> str:
    """The source address used for the external per-IP allowance.

    ``remote_addr`` is the connection's peer. A proxy deployment should preserve
    the client address at that layer rather than trusting a spoofable header in
    the application.
    """
    return str(request.remote_addr or "unknown").strip() or "unknown"


def check_ip_rate_limit() -> dict:
    """Consume one slot in the caller's IP window and report its headers.

    The window lives in the shared security store, not in a per-process map of
    request timestamps, so a crawl cannot grow this process's memory.
    """
    return security_store.api_rate_limit(
        _client_ip(), limit=IP_RATE_LIMIT, window=IP_RATE_WINDOW
    )


def _rate_headers(info: dict) -> dict:
    headers = {
        "X-RateLimit-Limit": str(info.get("limit", IP_RATE_LIMIT)),
        "X-RateLimit-Remaining": str(max(0, int(info.get("remaining", 0)))),
        "X-RateLimit-Reset": str(int(info.get("reset") or (time.time() + IP_RATE_WINDOW))),
    }
    if info.get("retry_after"):
        headers["Retry-After"] = str(int(info["retry_after"]))
    return headers


def _apply_rate_headers(response, info: dict):
    if hasattr(response, "headers"):
        for name, value in _rate_headers(info).items():
            response.headers[name] = value
    return response


def _suspended_error(user_id: str, *, headers: dict | None = None):
    access = developer_access(user_id)
    suspension = access.get("suspension") or {}
    return error_response(
        "ACCESS_SUSPENDED",
        "This developer account is suspended. Submit an appeal through the DM Niko sent you.",
        403,
        docs="/developers/rate-limits",
        details={
            "suspension": suspension,
            "appeal": access.get("appeal"),
        },
        headers=headers,
    )


def _suspension_for_signal(auth: dict, trigger: str, reason: str, metadata: dict) -> dict | None:
    return suspend_developer(
        auth["user_id"],
        reason=reason,
        trigger=trigger,
        key_id=str(auth["key"].get("id") or ""),
        key_prefix=str(auth["key"].get("prefix") or ""),
        metadata=metadata,
    )


def _note_key_activity(auth: dict, *, status: int | None = None, blocked: bool = False) -> dict | None:
    """Track one authenticated request and suspend on automated-abuse signals."""
    if auth.get("suspended"):
        return None
    key_id = str(auth["key"].get("id") or "")
    if not key_id:
        return None
    now = time.monotonic()
    with _TRACK_LOCK:
        entry = _KEY_HITS.setdefault(key_id, {
            "requests": deque(),
            "errors": deque(),
            "ips": deque(),
            "blocks": deque(),
        })
        request_cutoff = now - max(KEY_RATE_WINDOW, ABUSE_IP_WINDOW, _TRACKER_TTL)
        for name in ("requests", "errors", "ips", "blocks"):
            hits = entry[name]
            while hits and hits[0][0] <= request_cutoff:
                hits.popleft()
        if status is None and not blocked:
            entry["requests"].append((now, 0))
            entry["ips"].append((now, _client_ip()))
        if status is not None and int(status) >= 400:
            entry["errors"].append((now, int(status)))
        if blocked:
            entry["blocks"].append((now, 0))
        request_count = sum(1 for at, _ in entry["requests"] if at > now - KEY_RATE_WINDOW)
        error_count = sum(1 for at, _ in entry["errors"] if at > now - KEY_RATE_WINDOW)
        ip_count = len({ip for at, ip in entry["ips"] if at > now - ABUSE_IP_WINDOW})
        block_count = sum(1 for at, _ in entry["blocks"] if at > now - ABUSE_BLOCK_WINDOW)

    if request_count >= KEY_RATE_LIMIT:
        return _suspension_for_signal(
            auth,
            "sustained_request_rate",
            f"Automated abuse detection: {request_count} authenticated requests in {int(KEY_RATE_WINDOW)} seconds exceeded the {KEY_RATE_LIMIT}-request safety limit.",
            {"requests": request_count, "window_seconds": int(KEY_RATE_WINDOW)},
        )
    if error_count >= ABUSE_ERROR_LIMIT and error_count / max(1, request_count) >= ABUSE_ERROR_RATIO:
        return _suspension_for_signal(
            auth,
            "error_scanning",
            f"Automated abuse detection: {error_count} error responses in {int(KEY_RATE_WINDOW)} seconds ({error_count / max(1, request_count):.0%} of requests), consistent with automated probing.",
            {"errors": error_count, "requests": request_count, "window_seconds": int(KEY_RATE_WINDOW)},
        )
    if ip_count >= ABUSE_IP_LIMIT and request_count >= ABUSE_IP_MIN_REQUESTS:
        return _suspension_for_signal(
            auth,
            "distributed_key_use",
            f"Automated abuse detection: one key was used from {ip_count} addresses in {int(ABUSE_IP_WINDOW)} seconds.",
            {"addresses": ip_count, "requests": request_count, "window_seconds": int(ABUSE_IP_WINDOW)},
        )
    if block_count >= ABUSE_BLOCK_LIMIT:
        return _suspension_for_signal(
            auth,
            "rate_limit_abuse",
            f"Automated abuse detection: {block_count} rate-limit blocks in {int(ABUSE_BLOCK_WINDOW)} seconds.",
            {"blocks": block_count, "window_seconds": int(ABUSE_BLOCK_WINDOW)},
        )
    return None


def _record_key_block() -> dict | None:
    """Best effort: identify the key behind a blocked request and count it."""
    token = _request_token()
    if not token:
        return None
    auth = authenticate(token, allow_suspended=True)
    if auth is None or auth.get("suspended"):
        return None
    return _note_key_activity(auth, blocked=True)


def _authenticate_api_request(required_scopes: tuple[str, ...], info: dict):
    """Authenticate one external request after its IP slot was consumed."""
    headers = _rate_headers(info)
    token = _request_token()
    if not token:
        return None, _unauthorised(headers=headers)
    auth = authenticate(token, allow_suspended=True)
    if auth is None:
        return None, _unauthorised("That developer API key is invalid or revoked.", headers=headers)
    if auth.get("suspended"):
        return None, _suspended_error(auth["user_id"], headers=headers)
    missing = [scope for scope in required_scopes if scope not in auth["scopes"]]
    if missing:
        return None, _forbidden("This key does not have the required permission.", missing[0], headers=headers)
    suspension = _note_key_activity(auth)
    if suspension is not None:
        return None, _suspended_error(auth["user_id"], headers=headers)
    return auth, None


def _finish_api_response(response, auth: dict, info: dict, required_scopes: tuple[str, ...], started: float):
    status = response[1] if isinstance(response, tuple) and len(response) > 1 else getattr(response, "status_code", 200)
    status = int(status)
    suspension = _note_key_activity(auth, status=status)
    if suspension is not None:
        response = _suspended_error(auth["user_id"], headers=_rate_headers(info))
        status = 403
    _log_usage(
        key=auth["key"],
        user_id=auth["user_id"],
        scope=",".join(required_scopes),
        status=status,
        started=started,
    )
    if hasattr(response, "headers"):
        response.headers["X-Niko-Key"] = str(auth["key"].get("prefix") or "")
        response.headers["X-Niko-Scopes"] = " ".join(auth["scopes"])
    return _apply_rate_headers(response, info)


def _log_usage(*, key: dict, user_id: str, scope: str, status: int, started: float) -> None:
    with _LOCK:
        store = _load()
        store["usage"].append({
            "id": secrets.token_hex(6),
            "at": _now(),
            "user_id": user_id,
            "key_id": str(key.get("id") or ""),
            "key_name": str(key.get("name") or "API key"),
            "key_prefix": str(key.get("prefix") or ""),
            "scope": scope,
            "method": request.method,
            "path": request.path,
            "status": int(status),
            "latency_ms": max(0, round((time.perf_counter() - started) * 1000)),
        })
        if len(store["usage"]) > _USAGE_LIMIT:
            store["usage"] = store["usage"][-_USAGE_LIMIT:]
        _save(store)


def _unauthorised(message: str = "A developer API key is required.", *, headers: dict | None = None):
    return error_response(
        "AUTH_KEY_REQUIRED" if message == "A developer API key is required." else "AUTH_KEY_INVALID",
        message,
        401,
        docs="/developers/authentication",
        details={"auth": "Send Authorization: Bearer <key> or X-API-Key: <key>."},
        headers=headers,
    )


def _forbidden(message: str, scope: str = "", *, headers: dict | None = None):
    details = {"required_scope": scope} if scope else None
    return error_response(
        "SCOPE_REQUIRED" if scope else "ACCESS_FORBIDDEN",
        message,
        403,
        docs="/developers/scopes",
        details=details,
        headers=headers,
    )


def require_api_key(*required_scopes: str):
    """Require a valid key that carries every named scope."""
    def decorator(view):
        @wraps(view)
        def inner(*args, **kwargs):
            info = check_ip_rate_limit()
            headers = _rate_headers(info)
            if info["blocked"]:
                suspension = _record_key_block()
                if suspension is not None:
                    token = _request_token()
                    auth = authenticate(token, allow_suspended=True) if token else None
                    if auth is not None:
                        return _suspended_error(auth["user_id"], headers=headers)
                return error_response(
                    "RATE_LIMITED",
                    f"Too many requests from this address. Retry in {info['retry_after']} seconds.",
                    429,
                    docs="/developers/rate-limits",
                    details={
                        "limit": info["limit"],
                        "remaining": 0,
                        "retry_after": info["retry_after"],
                    },
                    headers=headers,
                )
            auth, error = _authenticate_api_request(tuple(required_scopes), info)
            if error is not None:
                return error
            g.developer_api = auth
            started = time.perf_counter()
            response = view(*args, **kwargs)
            return _finish_api_response(response, auth, info, tuple(required_scopes), started)
        return inner
    return decorator


def is_first_party_request() -> bool:
    """Whether this request came from a page on this site.

    The site's own leaderboard and profile popups still need their data. A
    browser sends ``Sec-Fetch-Site`` on its fetches; the referer is the fallback
    for older clients. A direct script, crawler, or another origin has neither
    and is sent to the keyed API instead.
    """
    fetch_site = (request.headers.get("Sec-Fetch-Site") or "").strip().lower()
    if fetch_site == "same-origin":
        return True
    referer = (request.headers.get("Referer") or "").strip()
    if not referer:
        return False
    try:
        return urlsplit(referer).netloc.lower() == request.host.lower()
    except ValueError:
        return False


def allow_site_or_key(*required_scopes: str):
    """Protect a website data route without breaking its own same-origin page.

    A request with a key is authenticated exactly like ``/api/v1``. A request
    without one is accepted only when it is a same-origin fetch from the site;
    direct API clients must present a key.
    """
    def decorator(view):
        @wraps(view)
        def inner(*args, **kwargs):
            token = _request_token()
            if not token and is_first_party_request():
                return view(*args, **kwargs)
            info = check_ip_rate_limit()
            headers = _rate_headers(info)
            if info["blocked"]:
                suspension = _record_key_block()
                if suspension is not None:
                    auth = authenticate(token, allow_suspended=True) if token else None
                    if auth is not None:
                        return _suspended_error(auth["user_id"], headers=headers)
                return error_response(
                    "RATE_LIMITED",
                    f"Too many requests from this address. Retry in {info['retry_after']} seconds.",
                    429,
                    docs="/developers/rate-limits",
                    details={"limit": info["limit"], "remaining": 0, "retry_after": info["retry_after"]},
                    headers=headers,
                )
            if not token:
                return error_response(
                    "AUTH_KEY_REQUIRED",
                    "This endpoint is for the Niko website. Use /api/v1 with an API key.",
                    401,
                    docs="/developers/authentication",
                    details={"auth": "Send Authorization: Bearer <key> or X-API-Key: <key>."},
                    headers=headers,
                )
            auth, error = _authenticate_api_request(tuple(required_scopes), info)
            if error is not None:
                return error
            g.developer_api = auth
            started = time.perf_counter()
            response = view(*args, **kwargs)
            return _finish_api_response(response, auth, info, tuple(required_scopes), started)
        return inner
    return decorator


def first_party_only(view):
    @wraps(view)
    def inner(*args, **kwargs):
        if not is_first_party_request():
            return error_response(
                "WEBSITE_ONLY",
                "This endpoint is only available inside the Niko website.",
                403,
                docs="/developers",
            )
        return view(*args, **kwargs)
    return inner


def session_user_id() -> str:
    return str((session.get("user") or {}).get("id") or "")


def resolve_identity(user_id: str) -> dict:
    """Best-effort Discord identity for an access row.

    The access roster is still usable when Discord is unavailable: the numeric
    id remains the stable identity and the owner can grant by id.
    """
    from .. import runtime

    user_id = str(user_id or "").strip()
    identity = {"username": "", "display_name": "", "avatar_url": None}
    bot = runtime._discord_bot
    if bot is None:
        return identity
    try:
        user = bot.get_user(int(user_id))
        if user is None:
            user = runtime.run_on_bot_loop(bot.fetch_user(int(user_id)), timeout=6)
        if user is None:
            return identity
        avatar = getattr(user, "display_avatar", None)
        return {
            "username": str(getattr(user, "name", "") or ""),
            "display_name": str(getattr(user, "global_name", "") or getattr(user, "display_name", "") or getattr(user, "name", "") or ""),
            "avatar_url": str(avatar.url) if avatar is not None else None,
        }
    except Exception:
        return identity
