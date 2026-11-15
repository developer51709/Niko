"""Temporary, IP-bound credentials for testing authenticated surfaces.

The owner MCP server can mint either a short-lived developer API key or a
staff-login link for a chosen staff role.  Both are deliberately narrow:

* an API key is stored in the developer portal like a normal key, but its record
  carries an expiry and an exact client address;
* a login link carries a signed, expiring payload and becomes a test-only Flask
  session.  The session is rechecked against the same address on every request.

Raw credentials are never logged.  The API key is returned once; the login URL
is returned once and is useless from any other address.
"""

from __future__ import annotations

import secrets
import time
from urllib.parse import urlencode

from flask import current_app, has_app_context, has_request_context, request, session
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from cogs.staff.records import STAFF_ROLES
from config.ids import OWNER_IDS

from . import config, runtime
from .client_ip import normalise_ip, request_client_ip

SESSION_KEY = "test_access"
TOKEN_SALT = "niko-test-access-login"
DEFAULT_TTL_SECONDS = 900
MAX_TTL_SECONDS = 3600
MIN_TTL_SECONDS = 60
DEFAULT_NEXT = "/dashboard"


def roles() -> tuple[str, ...]:
    """Staff roles a test session may assume, plus the owner view."""
    return ("owner", *STAFF_ROLES)


def owner_id() -> str:
    """The owner identity a test credential acts as.

    Test sessions use the configured owner so the developer portal resolves the
    owner's normal full access.  The selected staff role still controls every
    staff-page decision through ``_current_staff_role``.
    """
    try:
        return str(sorted(OWNER_IDS)[0])
    except (IndexError, TypeError):
        raise RuntimeError("No owner is configured for test access.")


def clean_role(raw) -> str:
    role = str(raw or "").strip().lower()
    if role not in roles():
        raise ValueError(f"role must be one of {', '.join(roles())}.")
    return role


def clean_next_path(raw) -> str:
    path = str(raw or "").strip() or DEFAULT_NEXT
    if (
        not path.startswith("/")
        or path.startswith("//")
        or "\\" in path
        or any(ord(char) < 32 for char in path)
    ):
        raise ValueError("next must be a path on this site, such as /dashboard/staff.")
    return path[:500]


def clean_ttl(raw) -> int:
    try:
        seconds = int(raw if raw is not None else DEFAULT_TTL_SECONDS)
    except (TypeError, ValueError):
        raise ValueError("ttl_seconds must be a whole number of seconds.")
    if not MIN_TTL_SECONDS <= seconds <= MAX_TTL_SECONDS:
        raise ValueError(
            f"ttl_seconds must be between {MIN_TTL_SECONDS} and {MAX_TTL_SECONDS}."
        )
    return seconds


def _serializer() -> URLSafeTimedSerializer:
    if has_app_context():
        secret = current_app.secret_key
    else:
        from .server import app

        secret = app.secret_key
    if not secret:
        raise RuntimeError("The session secret is not configured.")
    return URLSafeTimedSerializer(secret, salt=TOKEN_SALT)


def site_origin() -> str:
    """The canonical site origin used in a generated login link."""
    canonical = config.canonical_origin()
    if canonical:
        return canonical
    if has_request_context():
        proto = (
            request.headers.get("X-Forwarded-Proto") or request.scheme or "https"
        ).split(",", 1)[0].strip()
        return f"{proto}://{runtime.request_host()}".rstrip("/")
    return ""


def issue_login(
    *,
    role,
    ip,
    ttl_seconds=DEFAULT_TTL_SECONDS,
    next_path=DEFAULT_NEXT,
    user_id: str | None = None,
) -> dict:
    """Create a signed login link bound to one exact client address."""
    address = normalise_ip(ip)
    if not address:
        raise ValueError("ip must be a valid IPv4 or IPv6 address.")
    role = clean_role(role)
    ttl = clean_ttl(ttl_seconds)
    next_path = clean_next_path(next_path)
    now = time.time()
    payload = {
        "kind": "session",
        "role": role,
        "ip": address,
        "exp": now + ttl,
        "user_id": str(user_id or owner_id()),
        "next": next_path,
        "jti": secrets.token_hex(8),
    }
    token = _serializer().dumps(payload)
    origin = site_origin()
    query = urlencode({"token": token})
    return {
        "kind": "session",
        "login_url": f"{origin}/auth/test-session?{query}" if origin else f"/auth/test-session?{query}",
        "token": token,
        "role": role,
        "ip": address,
        "expires_at": payload["exp"],
        "ttl_seconds": ttl,
    }


def accept_login(token: str) -> dict:
    """Verify a login token and its bound address, returning its payload."""
    if not token:
        raise ValueError("A test login token is required.")
    try:
        payload = _serializer().loads(token, max_age=MAX_TTL_SECONDS + 60)
    except SignatureExpired:
        raise ValueError("That test login link has expired.")
    except BadSignature:
        raise ValueError("That test login link is invalid.")
    if not isinstance(payload, dict) or payload.get("kind") != "session":
        raise ValueError("That test login link is invalid.")
    try:
        expires_at = float(payload.get("exp") or 0)
    except (TypeError, ValueError):
        raise ValueError("That test login link is invalid.")
    if expires_at <= time.time():
        raise ValueError("That test login link has expired.")
    bound_ip = normalise_ip(payload.get("ip"))
    if not bound_ip or request_client_ip() != bound_ip:
        raise PermissionError(
            "This test login is bound to a different IP address."
        )
    payload["role"] = clean_role(payload.get("role"))
    payload["ip"] = bound_ip
    payload["next"] = clean_next_path(payload.get("next"))
    return payload


def install(payload: dict) -> None:
    """Replace the browser session with the verified test identity."""
    session.clear()
    role = clean_role(payload.get("role"))
    session["user"] = {
        "id": str(payload.get("user_id") or owner_id()),
        "username": "niko-test-access",
        "global_name": f"Niko test access ({role})",
        "bot": False,
    }
    session["access_token"] = "test-access"
    session["token_exp"] = float(payload.get("exp") or 0)
    session["oauth_scopes"] = ["identify"]
    session["csrf_token"] = secrets.token_urlsafe(24)
    session[SESSION_KEY] = {
        "kind": "session",
        "role": role,
        "ip": normalise_ip(payload.get("ip")),
        "expires_at": float(payload.get("exp") or 0),
        "user_id": str(payload.get("user_id") or ""),
    }


def current() -> dict | None:
    """The active test session, or ``None`` after expiry/address mismatch.

    An invalid test marker clears the whole session so a stale cookie cannot
    fall back to a normal signed-in identity.
    """
    if not has_request_context():
        return None
    marker = session.get(SESSION_KEY)
    if not isinstance(marker, dict):
        return None
    try:
        expires_at = float(marker.get("expires_at") or 0)
    except (TypeError, ValueError):
        session.clear()
        return None
    if expires_at <= time.time() or normalise_ip(marker.get("ip")) != request_client_ip():
        session.clear()
        return None
    return marker
