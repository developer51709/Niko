"""Reviewed developer applications and their bot webhook configuration.

A developer key has always belonged to a person. A *bot application* belongs to
that person too, but it also names the Discord application whose bot receives
events. The extra identity matters because the API can only trust the app for
guilds where that bot is actually a member alongside Niko.

Applications are deliberately reviewed by the owner before they can receive
events or create app-bound keys. The review depends on a screenshot of Discord's
application page with the profile menu open: the submitted client ID, the bot
resolved from Discord, and the visible profile name all have to agree. That is a
human check; automation only stores and serves the evidence safely here.
"""

from __future__ import annotations

import ipaddress
import json
import os
import re
import secrets
import socket
import threading
import time
from copy import deepcopy
from urllib.parse import urlsplit, urlunsplit

from utils import logging

from . import config

_STORE_NAME = "developer_applications.json"
_SCREENSHOT_DIR = "developer_application_screenshots"
_STORE_VERSION = 1
_LOCK = threading.RLock()
_STORE: dict | None = None
_STORE_STAMP: tuple[int, int] | None = None

MAX_SCREENSHOT_BYTES = 8 * 1024 * 1024
MAX_NAME = 80
MAX_DESCRIPTION = 400
MAX_NOTE = 2000
MAX_WEBHOOK_URL = 500

APPLICATION_STATUSES = ("pending", "approved", "denied")

#: Events an approved application can subscribe to. Webhook payloads carry no
#: user-facing text other than the warn reason, which the developer is already
#: allowed to read with the warns scope.
WEBHOOK_EVENTS: dict[str, dict] = {
    "warn.created": {
        "label": "Warning created",
        "description": "A warning was added through Niko or through the warns API.",
    },
    "warn.deleted": {
        "label": "Warning deleted",
        "description": "One warning was removed from a guild.",
    },
    "warns.cleared": {
        "label": "Warnings cleared",
        "description": "All warnings for one member in a guild were removed.",
    },
}

ALL_WEBHOOK_EVENTS = tuple(WEBHOOK_EVENTS)

#: Scopes that are never self-service. They can only be selected by the owner
#: during review, and only for a developer who already holds the same grant.
RESTRICTED_SCOPES = frozenset({"blacklist:read", "blacklist:write", "guilds:cross_server"})

_IMAGE_TYPES = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
}

_MEMBERSHIP_CACHE: dict[tuple[str, str], tuple[float, bool]] = {}
_MEMBERSHIP_TTL = 300.0


def _store_path() -> str:
    return os.path.join(config.DATA_DIR, _STORE_NAME)


def _screenshot_dir() -> str:
    return os.path.join(config.DATA_DIR, _SCREENSHOT_DIR)


def _empty_store() -> dict:
    return {"version": _STORE_VERSION, "applications": {}}


def _normalise_store(document) -> dict:
    if not isinstance(document, dict):
        return _empty_store()
    applications = document.get("applications")
    return {
        "version": _STORE_VERSION,
        "applications": applications if isinstance(applications, dict) else {},
    }


def _load() -> dict:
    global _STORE, _STORE_STAMP
    path = _store_path()
    try:
        stat = os.stat(path)
        stamp = (stat.st_mtime_ns, stat.st_size)
    except OSError:
        stamp = None
    with _LOCK:
        if _STORE is not None and stamp == _STORE_STAMP:
            return _STORE
        try:
            with open(path, "r", encoding="utf-8") as handle:
                document = json.load(handle)
        except (OSError, ValueError):
            document = _empty_store()
        _STORE = _normalise_store(document)
        _STORE_STAMP = stamp
        return _STORE


def _save(document: dict) -> None:
    global _STORE, _STORE_STAMP
    path = _store_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    document = _normalise_store(document)
    temporary = f"{path}.tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(document, handle, indent=2)
    os.replace(temporary, path)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    try:
        stat = os.stat(path)
        _STORE_STAMP = (stat.st_mtime_ns, stat.st_size)
    except OSError:
        _STORE_STAMP = None
    _STORE = document


def _now() -> float:
    return time.time()


def detect_image_type(raw: bytes, reported: str = "") -> str | None:
    """Return the image MIME type from its magic bytes, never the claim alone."""
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if raw.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if raw.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "image/webp"
    return None


def _screenshot_for(app: dict) -> dict | None:
    shot = app.get("screenshot")
    if not isinstance(shot, dict) or not shot.get("path"):
        return None
    if not os.path.isfile(os.path.join(config.DATA_DIR, str(shot["path"]))):
        return None
    return {
        "url": f"/api/developer/applications/{app.get('id')}/screenshot",
        "content_type": shot.get("content_type"),
        "size": shot.get("size"),
        "uploaded_at": shot.get("uploaded_at"),
    }


def _public_webhook(app: dict, *, include_secret: bool) -> dict:
    webhook = app.get("webhook") if isinstance(app.get("webhook"), dict) else {}
    events = webhook.get("events") if isinstance(webhook.get("events"), list) else list(ALL_WEBHOOK_EVENTS)
    events = [event for event in ALL_WEBHOOK_EVENTS if event in events]
    payload = {
        "url": str(webhook.get("url") or ""),
        "enabled": bool(webhook.get("enabled")),
        "events": events,
        "updated_at": webhook.get("updated_at"),
        "last_delivery_at": webhook.get("last_delivery_at"),
        "last_delivery_status": webhook.get("last_delivery_status"),
        "last_delivery_error": webhook.get("last_delivery_error"),
        "last_event": webhook.get("last_event"),
    }
    if include_secret:
        payload["secret"] = str(webhook.get("secret") or "")
    return payload


def public_application(app: dict, *, include_secret: bool = True) -> dict:
    app = app if isinstance(app, dict) else {}
    webhook = app.get("webhook") if isinstance(app.get("webhook"), dict) else {}
    return {
        "id": str(app.get("id") or ""),
        "owner_id": str(app.get("owner_id") or ""),
        "owner_username": str(app.get("owner_username") or ""),
        "owner_display_name": str(app.get("owner_display_name") or ""),
        "owner_avatar_url": app.get("owner_avatar_url"),
        "name": str(app.get("name") or ""),
        "description": str(app.get("description") or ""),
        "bot_user_id": str(app.get("bot_user_id") or ""),
        "bot_username": str(app.get("bot_username") or ""),
        "bot_display_name": str(app.get("bot_display_name") or ""),
        "bot_avatar_url": app.get("bot_avatar_url"),
        "status": str(app.get("status") or "pending"),
        "requested_scopes": list(app.get("requested_scopes") or []),
        "approved_scopes": list(app.get("approved_scopes") or []),
        "screenshot": _screenshot_for(app),
        "webhook": _public_webhook(app, include_secret=include_secret),
        "created_at": app.get("created_at"),
        "updated_at": app.get("updated_at"),
        "submitted_at": app.get("submitted_at"),
        "reviewed_at": app.get("reviewed_at"),
        "reviewed_by": app.get("reviewed_by"),
        "review_note": app.get("review_note"),
        "webhook_configured": bool(webhook.get("url")),
    }


def application_summary(app: dict) -> dict:
    """The small, non-secret copy attached to an authenticated API request."""
    app = app if isinstance(app, dict) else {}
    return {
        "id": str(app.get("id") or ""),
        "name": str(app.get("name") or ""),
        "bot_user_id": str(app.get("bot_user_id") or ""),
        "status": str(app.get("status") or ""),
        "scopes": list(app.get("approved_scopes") or []),
        "webhook_enabled": bool((app.get("webhook") or {}).get("enabled")),
    }


def get_application(application_id: str, *, public: bool = False, include_secret: bool = True) -> dict | None:
    application_id = str(application_id or "").strip()
    if not application_id:
        return None
    app = _load()["applications"].get(application_id)
    if not isinstance(app, dict):
        return None
    return public_application(app, include_secret=include_secret) if public else deepcopy(app)


def applications_for_user(user_id: str) -> list[dict]:
    user_id = str(user_id or "").strip()
    with _LOCK:
        apps = [
            public_application(app)
            for app in _load()["applications"].values()
            if isinstance(app, dict) and str(app.get("owner_id")) == user_id
        ]
    apps.sort(key=lambda item: float(item.get("updated_at") or 0), reverse=True)
    return apps


def review_rows() -> list[dict]:
    with _LOCK:
        apps = [public_application(app) for app in _load()["applications"].values() if isinstance(app, dict)]
    apps.sort(key=lambda item: (item.get("status") != "pending", -float(item.get("submitted_at") or item.get("created_at") or 0)))
    return apps


def approved_applications() -> list[dict]:
    """Internal copies of every approved application, for event fan-out."""
    with _LOCK:
        return [
            deepcopy(app)
            for app in _load()["applications"].values()
            if isinstance(app, dict) and str(app.get("status")) == "approved"
        ]


def _clean_scopes(raw, allowed: set[str] | None = None) -> list[str]:
    if not isinstance(raw, (list, tuple, set)):
        return []
    seen: set[str] = set()
    for item in raw:
        value = str(item or "").strip()
        if value and value not in seen and (allowed is None or value in allowed):
            seen.add(value)
    return sorted(seen)


def _validate_identity(name: str, description: str, bot_user_id: str) -> tuple[str, str, str]:
    clean_name = " ".join(str(name or "").split()).strip()
    if len(clean_name) < 2:
        raise ValueError("Give the application a name with at least two characters.")
    if len(clean_name) > MAX_NAME:
        raise ValueError(f"Application names must be {MAX_NAME} characters or fewer.")
    clean_description = " ".join(str(description or "").split()).strip()
    if len(clean_description) > MAX_DESCRIPTION:
        raise ValueError(f"Descriptions must be {MAX_DESCRIPTION} characters or fewer.")
    clean_bot_id = str(bot_user_id or "").strip()
    if not re.fullmatch(r"\d{15,22}", clean_bot_id):
        raise ValueError("Enter the bot's numeric Discord user or application/client ID.")
    return clean_name, clean_description, clean_bot_id


def _store_screenshot(application_id: str, raw: bytes, content_type: str) -> dict:
    if not raw:
        raise ValueError("Upload a screenshot of the application overview page.")
    if len(raw) > MAX_SCREENSHOT_BYTES:
        raise ValueError("Screenshots must be 8 MB or smaller.")
    extension = _IMAGE_TYPES.get(content_type)
    if extension is None:
        raise ValueError("Upload a PNG, JPEG, GIF, or WebP screenshot.")
    directory = _screenshot_dir()
    os.makedirs(directory, exist_ok=True)
    for name in os.listdir(directory):
        if name.startswith(f"{application_id}."):
            try:
                os.remove(os.path.join(directory, name))
            except OSError:
                pass
    filename = f"{application_id}.{extension}"
    path = os.path.join(directory, filename)
    with open(path, "wb") as handle:
        handle.write(raw)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return {
        "path": os.path.join(_SCREENSHOT_DIR, filename),
        "content_type": content_type,
        "size": len(raw),
        "uploaded_at": _now(),
    }


def create_or_resubmit(
    owner_id: str,
    *,
    name: str,
    description: str,
    bot_user_id: str,
    requested_scopes,
    allowed_scopes,
    bot_identity: dict | None = None,
    owner_identity: dict | None = None,
    screenshot: bytes,
    screenshot_content_type: str,
) -> dict:
    """Create a pending application, or resubmit this owner's denied one."""
    owner_id = str(owner_id or "").strip()
    if not owner_id:
        raise ValueError("A signed-in developer is required.")
    clean_name, clean_description, clean_bot_id = _validate_identity(name, description, bot_user_id)
    content_type = detect_image_type(screenshot, screenshot_content_type)
    if content_type is None:
        raise ValueError("Upload a PNG, JPEG, GIF, or WebP screenshot.")
    if len(screenshot) > MAX_SCREENSHOT_BYTES:
        raise ValueError("Screenshots must be 8 MB or smaller.")

    allowed = set(allowed_scopes or ())
    requested = _clean_scopes(requested_scopes, allowed)
    submitted = {str(item or "").strip() for item in requested_scopes or () if str(item or "").strip()}
    restricted = sorted(submitted & RESTRICTED_SCOPES)
    if restricted:
        raise ValueError("Special scopes are granted by the owner during review, not requested here.")
    unknown = sorted(submitted - allowed)
    if unknown:
        raise ValueError(f"Unknown or unavailable permission: {unknown[0]}")
    if not requested:
        raise ValueError("Choose at least one API permission for the application.")

    bot_identity = bot_identity if isinstance(bot_identity, dict) else {}
    owner_identity = owner_identity if isinstance(owner_identity, dict) else {}
    now = _now()
    with _LOCK:
        store = _load()
        existing = next(
            (
                app for app in store["applications"].values()
                if isinstance(app, dict) and str(app.get("bot_user_id")) == clean_bot_id
            ),
            None,
        )
        if existing is not None:
            if str(existing.get("owner_id")) != owner_id:
                raise FileExistsError("That bot or application ID is already registered to another developer.")
            if str(existing.get("status")) != "denied":
                raise FileExistsError("That bot is already registered. Wait for the current review before resubmitting.")
            app_id = str(existing["id"])
            # A resubmission replaces the evidence and review state. It does
            # not inherit old permissions or webhook credentials.
            existing.update({
                "name": clean_name,
                "description": clean_description,
                "requested_scopes": requested,
                "approved_scopes": [],
                "bot_username": str(bot_identity.get("username") or ""),
                "bot_display_name": str(bot_identity.get("display_name") or ""),
                "bot_avatar_url": bot_identity.get("avatar_url"),
                "status": "pending",
                "updated_at": now,
                "submitted_at": now,
                "reviewed_at": None,
                "reviewed_by": None,
                "review_note": None,
                "webhook": {},
            })
            existing["screenshot"] = _store_screenshot(app_id, screenshot, content_type)
            _save(store)
            return public_application(existing)

        app_id = secrets.token_hex(8)
        app = {
            "id": app_id,
            "owner_id": owner_id,
            "owner_username": str(owner_identity.get("username") or ""),
            "owner_display_name": str(owner_identity.get("display_name") or ""),
            "owner_avatar_url": owner_identity.get("avatar_url"),
            "name": clean_name,
            "description": clean_description,
            "bot_user_id": clean_bot_id,
            "bot_username": str(bot_identity.get("username") or ""),
            "bot_display_name": str(bot_identity.get("display_name") or ""),
            "bot_avatar_url": bot_identity.get("avatar_url"),
            "status": "pending",
            "requested_scopes": requested,
            "approved_scopes": [],
            "screenshot": _store_screenshot(app_id, screenshot, content_type),
            "webhook": {},
            "created_at": now,
            "updated_at": now,
            "submitted_at": now,
            "reviewed_at": None,
            "reviewed_by": None,
            "review_note": None,
        }
        store["applications"][app_id] = app
        _save(store)
        return public_application(app)


def review_application(
    application_id: str,
    status: str,
    *,
    scopes,
    note: str = "",
    actor_id: str = "",
    allowed_scopes,
) -> dict | None:
    """Approve or deny a pending submission. Only the owner route calls this."""
    application_id = str(application_id or "").strip()
    status = str(status or "").strip().lower()
    if status not in {"approved", "denied"}:
        raise ValueError("Choose approved or denied.")
    allowed = set(allowed_scopes or ())
    clean_note = str(note or "").strip()[:MAX_NOTE]
    with _LOCK:
        store = _load()
        app = store["applications"].get(application_id)
        if not isinstance(app, dict):
            return None
        if str(app.get("status")) != "pending":
            raise ValueError("This application has already been reviewed.")
        now = _now()
        app["reviewed_at"] = now
        app["reviewed_by"] = str(actor_id or "")
        app["review_note"] = clean_note or None
        app["updated_at"] = now
        if status == "approved":
            approved = _clean_scopes(scopes if scopes is not None else app.get("requested_scopes"), allowed)
            if not approved:
                raise ValueError("Select at least one permission for the approved application.")
            disallowed = sorted(set(approved) - allowed)
            if disallowed:
                raise ValueError(f"The developer does not hold the {disallowed[0]} permission.")
            app["approved_scopes"] = approved
            app["status"] = "approved"
        else:
            app["approved_scopes"] = []
            app["status"] = "denied"
        _save(store)
        return public_application(app)


def delete_application(application_id: str, owner_id: str) -> bool:
    application_id = str(application_id or "").strip()
    owner_id = str(owner_id or "").strip()
    with _LOCK:
        store = _load()
        app = store["applications"].get(application_id)
        if not isinstance(app, dict) or str(app.get("owner_id")) != owner_id:
            return False
        if str(app.get("status")) != "denied":
            raise ValueError("Only a denied application can be removed. Approved apps keep their keys.")
        screenshot = app.get("screenshot") if isinstance(app.get("screenshot"), dict) else {}
        path = screenshot.get("path")
        if path:
            try:
                os.remove(os.path.join(config.DATA_DIR, str(path)))
            except OSError:
                pass
        store["applications"].pop(application_id, None)
        _save(store)
    return True


def screenshot_path(application_id: str) -> tuple[str, str] | None:
    app = _load()["applications"].get(str(application_id or ""))
    if not isinstance(app, dict):
        return None
    shot = app.get("screenshot")
    if not isinstance(shot, dict) or not shot.get("path"):
        return None
    path = os.path.join(config.DATA_DIR, str(shot["path"]))
    if not os.path.isfile(path):
        return None
    return path, str(shot.get("content_type") or "application/octet-stream")


def _normalise_webhook_url(value) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    if len(raw) > MAX_WEBHOOK_URL:
        raise ValueError(f"Webhook URLs must be {MAX_WEBHOOK_URL} characters or fewer.")
    try:
        parts = urlsplit(raw)
        host = (parts.hostname or "").strip().lower()
        port = parts.port or 443
    except ValueError as error:
        raise ValueError("Enter a valid webhook URL.") from error
    if parts.scheme.lower() != "https":
        raise ValueError("Webhook endpoints must use HTTPS.")
    if parts.username or parts.password:
        raise ValueError("Webhook URLs cannot contain credentials.")
    if not host:
        raise ValueError("Enter a valid webhook URL.")
    if host in {"localhost", "localhost.localdomain"} or host.endswith((".local", ".internal", ".localhost")):
        raise ValueError("Webhook endpoints must be publicly reachable.")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        try:
            resolved = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        except OSError as error:
            raise ValueError("The webhook host could not be resolved.") from error
        addresses = []
        for item in resolved:
            try:
                addresses.append(ipaddress.ip_address(item[4][0]))
            except ValueError:
                continue
        if not addresses or any(not address.is_global for address in addresses):
            raise ValueError("Webhook endpoints must resolve to a public address.")
    else:
        if not address.is_global:
            raise ValueError("Webhook endpoints must resolve to a public address.")
    path = parts.path or "/"
    return urlunsplit(("https", parts.netloc, path, parts.query, ""))


def configure_webhook(
    application_id: str,
    owner_id: str,
    *,
    url,
    enabled: bool,
    events,
) -> dict:
    """Save an approved app's endpoint. The secret is stable across edits."""
    application_id = str(application_id or "").strip()
    owner_id = str(owner_id or "").strip()
    clean_url = _normalise_webhook_url(url)
    if enabled and not clean_url:
        raise ValueError("Add a webhook URL before enabling delivery.")
    selected = _clean_scopes_events(events)
    if not selected:
        raise ValueError("Choose at least one event.")
    with _LOCK:
        store = _load()
        app = store["applications"].get(application_id)
        if not isinstance(app, dict) or str(app.get("owner_id")) != owner_id:
            raise LookupError("Application not found.")
        if str(app.get("status")) != "approved":
            raise PermissionError("Webhook delivery is only available after the application is approved.")
        if "warns:read" not in (app.get("approved_scopes") or []):
            raise PermissionError("The application needs warnings read approval before it can receive warning events.")
        webhook = app.get("webhook") if isinstance(app.get("webhook"), dict) else {}
        now = _now()
        webhook = {
            **webhook,
            "url": clean_url,
            "enabled": bool(enabled and clean_url),
            "events": selected,
            "secret": str(webhook.get("secret") or secrets.token_urlsafe(32)),
            "updated_at": now,
        }
        app["webhook"] = webhook
        app["updated_at"] = now
        _save(store)
        return _public_webhook(app, include_secret=True)


def _clean_scopes_events(raw) -> list[str]:
    if not isinstance(raw, (list, tuple, set)):
        return list(ALL_WEBHOOK_EVENTS)
    seen = {str(item or "").strip() for item in raw}
    return [event for event in ALL_WEBHOOK_EVENTS if event in seen]


def record_delivery(
    application_id: str,
    *,
    event_type: str,
    status: int | None,
    error: str = "",
) -> None:
    with _LOCK:
        store = _load()
        app = store["applications"].get(str(application_id or ""))
        if not isinstance(app, dict) or not isinstance(app.get("webhook"), dict):
            return
        webhook = app["webhook"]
        webhook["last_delivery_at"] = _now()
        webhook["last_delivery_status"] = status
        webhook["last_delivery_error"] = (str(error or "")[:500] or None)
        webhook["last_event"] = str(event_type or "")
        app["updated_at"] = webhook["last_delivery_at"]
        _save(store)


def shared_guild_count(app: dict) -> int:
    """Cached membership count, used only as a review hint."""
    bot = _runtime_bot()
    if bot is None or not isinstance(app, dict):
        return 0
    bot_id = str(app.get("bot_user_id") or "")
    if not bot_id:
        return 0
    total = 0
    for guild in getattr(bot, "guilds", ()) or ():
        try:
            if guild.get_member(int(bot_id)) is not None:
                total += 1
        except (AttributeError, TypeError, ValueError):
            continue
    return total


def _runtime_bot():
    from . import runtime

    return runtime._discord_bot


async def application_in_guild_async(app: dict, guild_id: str) -> bool:
    """Whether the application bot shares this guild with Niko right now."""
    app = app if isinstance(app, dict) else {}
    app_id = str(app.get("id") or "")
    bot_id = str(app.get("bot_user_id") or "")
    guild_id = str(guild_id or "")
    if not app_id or not bot_id or not guild_id:
        return False
    key = (app_id, guild_id)
    cached = _MEMBERSHIP_CACHE.get(key)
    if cached and cached[0] > time.monotonic():
        return cached[1]
    bot = _runtime_bot()
    guild = None
    try:
        guild = bot.get_guild(int(guild_id)) if bot is not None else None
    except (AttributeError, TypeError, ValueError):
        guild = None
    if guild is None:
        _MEMBERSHIP_CACHE[key] = (time.monotonic() + 60, False)
        return False
    member = None
    try:
        member = guild.get_member(int(bot_id))
    except (AttributeError, TypeError, ValueError):
        member = None
    if member is None:
        try:
            member = await guild.fetch_member(int(bot_id))
        except Exception:
            member = None
    result = member is not None
    _MEMBERSHIP_CACHE[key] = (time.monotonic() + _MEMBERSHIP_TTL, result)
    return result


def application_in_guild(app: dict, guild_id: str) -> bool:
    """Synchronous wrapper for request handlers running off the bot loop."""
    from . import runtime

    try:
        return bool(runtime.run_on_bot_loop(application_in_guild_async(app, guild_id), timeout=6))
    except Exception as error:
        logging.warning("DeveloperApps", f"Guild membership check failed: {error}")
        return False
