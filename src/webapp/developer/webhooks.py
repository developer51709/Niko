"""Signed, guild-filtered webhook delivery for approved bot applications.

An application opts in with an HTTPS endpoint and a secret. Niko sends a small
JSON event after the matching warn operation, signed with HMAC-SHA256 over
``<timestamp>.<raw body>``. Delivering after the database write means a slow or
broken receiver can never hold up Niko's moderation commands.

The guild rule is enforced at the last possible moment, per application: an app
receives an event only when its bot is currently a member of that guild. The
owner can grant ``guilds:cross_server`` to a trusted app when cross-server
moderation data is intentionally approved.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import secrets
import time

from utils import logging

from . import applications, portal

DELIVERY_TIMEOUT_SECONDS = 8
DELIVERY_ATTEMPTS = 3
RETRY_DELAYS = (0.0, 2.0, 6.0)
TEST_EVENT = "webhook.test"
_DELIVERY_TASKS: set = set()


def _payload(event_type: str, guild_id: str, data: dict, application_id: str = "") -> dict:
    return {
        "id": secrets.token_hex(12),
        "type": str(event_type),
        "created_at": time.time(),
        "application_id": str(application_id or ""),
        "guild_id": str(guild_id or "") or None,
        "data": data if isinstance(data, dict) else {},
    }


def _signature(secret: str, timestamp: int, body: str) -> str:
    signed = f"{timestamp}.{body}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()


def _webhook_ready(app: dict, event_type: str) -> bool:
    if str(app.get("status")) != "approved":
        return False
    # The event selection is not a substitute for a reviewed permission. A
    # warning event contains warning data, so the application must hold the
    # corresponding read scope in addition to selecting the event.
    if event_type.startswith("warn") and "warns:read" not in (app.get("approved_scopes") or []):
        return False
    webhook = app.get("webhook") if isinstance(app.get("webhook"), dict) else {}
    if not webhook.get("enabled") or not webhook.get("url") or not webhook.get("secret"):
        return False
    events = webhook.get("events") if isinstance(webhook.get("events"), list) else []
    return event_type in events


def _application_allows_guild(app: dict, guild_id: str) -> bool:
    if "guilds:cross_server" in (app.get("approved_scopes") or []):
        return True
    return False


async def _post_once(url: str, body: str, headers: dict) -> tuple[bool, int | None, str]:
    try:
        import aiohttp
    except Exception as error:  # pragma: no cover - dependency is in requirements
        return False, None, f"aiohttp unavailable: {error}"
    try:
        timeout = aiohttp.ClientTimeout(total=DELIVERY_TIMEOUT_SECONDS)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, data=body.encode("utf-8"), headers=headers, allow_redirects=False) as response:
                text = (await response.text())[:300]
                if 200 <= response.status < 300:
                    return True, response.status, ""
                return False, response.status, f"HTTP {response.status}: {text}"
    except Exception as error:
        return False, None, f"{type(error).__name__}: {error}"


async def _deliver(application_id: str, payload: dict, *, attempts: int = DELIVERY_ATTEMPTS) -> bool:
    app = applications.get_application(application_id)
    if not isinstance(app, dict):
        return False
    webhook = app.get("webhook") if isinstance(app.get("webhook"), dict) else {}
    raw_url = str(webhook.get("url") or "")
    secret = str(webhook.get("secret") or "")
    if not raw_url or not secret:
        return False
    try:
        # Re-check at delivery time as well as at save time: DNS records can
        # change, and the stored URL is untrusted input.
        url = applications._normalise_webhook_url(raw_url)
    except ValueError as error:
        applications.record_delivery(
            application_id,
            event_type=str(payload.get("type") or ""),
            status=None,
            error=str(error),
        )
        return False
    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    last_status: int | None = None
    last_error = ""
    for attempt in range(max(1, attempts)):
        timestamp = int(time.time())
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Niko-Developer-Webhooks/1.0",
            "X-Niko-Application": str(app.get("id") or ""),
            "X-Niko-Delivery": str(payload.get("id") or ""),
            "X-Niko-Event": str(payload.get("type") or ""),
            "X-Niko-Signature": f"t={timestamp},v1={_signature(secret, timestamp, body)}",
        }
        ok, last_status, last_error = await _post_once(url, body, headers)
        if ok:
            applications.record_delivery(
                application_id,
                event_type=str(payload.get("type") or ""),
                status=last_status,
            )
            return True
        # A 4xx is the receiver's answer, not a transient failure. Retrying a
        # rejected signature or a removed endpoint only creates noise.
        if last_status is not None and 400 <= last_status < 500 and last_status != 429:
            break
        if attempt + 1 < attempts:
            await asyncio.sleep(RETRY_DELAYS[min(attempt + 1, len(RETRY_DELAYS) - 1)])
    applications.record_delivery(
        application_id,
        event_type=str(payload.get("type") or ""),
        status=last_status,
        error=last_error,
    )
    return False


async def dispatch_guild_event_async(event_type: str, guild_id: str, data: dict) -> int:
    """Deliver one event to every approved app that is allowed to receive it."""
    if event_type not in applications.WEBHOOK_EVENTS:
        return 0
    guild_id = str(guild_id or "").strip()
    if not guild_id:
        return 0
    apps = applications.approved_applications()
    deliveries = 0
    for app in apps:
        if not _webhook_ready(app, event_type):
            continue
        # A suspended or revoked developer stops receiving events immediately,
        # even if an old approval and webhook configuration still exist. The
        # effective scope is still the intersection, so a removed read grant
        # must also stop the corresponding event stream.
        owner_access = portal.developer_access(str(app.get("owner_id") or ""))
        if not owner_access["enabled"]:
            continue
        if event_type.startswith("warn") and "warns:read" not in (owner_access.get("scopes") or []):
            continue
        if not _application_allows_guild(app, guild_id):
            if not await applications.application_in_guild_async(app, guild_id):
                continue
        payload = _payload(event_type, guild_id, data, str(app.get("id") or ""))
        # Each receiver gets its own task so one slow endpoint cannot delay the
        # rest. Keep a strong reference until it completes; otherwise the event
        # loop may garbage-collect an in-flight delivery.
        task = asyncio.create_task(_deliver(str(app.get("id") or ""), payload))
        _DELIVERY_TASKS.add(task)
        task.add_done_callback(_DELIVERY_TASKS.discard)
        deliveries += 1
    return deliveries


def dispatch_guild_event(event_type: str, guild_id: str, data: dict) -> int:
    """Schedule guild-filtered delivery without blocking the caller."""
    from .. import runtime

    if runtime._discord_bot is None:
        return 0
    try:
        runtime.schedule_on_bot_loop(dispatch_guild_event_async(event_type, guild_id, data))
        return 1
    except Exception as error:
        logging.warning("DeveloperWebhooks", f"Could not schedule {event_type} delivery: {error}")
        return 0


async def send_test_event_async(application_id: str) -> tuple[bool, int | None, str]:
    app = applications.get_application(application_id)
    if not isinstance(app, dict):
        return False, None, "Application not found."
    if str(app.get("status")) != "approved":
        return False, None, "Webhook delivery is only available after the application is approved."
    webhook = app.get("webhook") if isinstance(app.get("webhook"), dict) else {}
    if not webhook.get("url"):
        return False, None, "Add a webhook URL first."
    payload = _payload(
        TEST_EVENT,
        "",
        {
            "message": "This is a test delivery from Niko. No guild data is included.",
            "application": app.get("name"),
        },
        application_id,
    )
    ok = await _deliver(application_id, payload, attempts=1)
    updated = applications.get_application(application_id) or {}
    state = updated.get("webhook") if isinstance(updated.get("webhook"), dict) else {}
    return ok, state.get("last_delivery_status"), str(state.get("last_delivery_error") or "")


def send_test_event(application_id: str) -> tuple[bool, int | None, str]:
    from .. import runtime

    try:
        return runtime.run_on_bot_loop(send_test_event_async(application_id), timeout=15)
    except Exception as error:
        return False, None, f"Webhook delivery is unavailable: {error}"
