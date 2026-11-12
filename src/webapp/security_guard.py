"""Refuse requests from addresses banned on the honeypot owner page.

A ban is global: it is checked in the first ``before_request`` hook, so it
covers the website, every ``/api`` and ``/v1`` route, the auth flow, and any
subdomain before subdomain routing can serve a page. The check reads the small
active-ban cache in :mod:`webapp.security`; it does not query the database on
every request.
"""

from __future__ import annotations

import time

from flask import Response, jsonify, request
from utils.verification.ip_intel import client_ip

from . import security

_BANNED_PAGE = (
    "Access denied.\n\n"
    "This address has been blocked from Niko's website, APIs, and subdomains."
)


def _request_ip() -> str:
    return security.normalise_ip(
        client_ip(request.remote_addr, request.headers.get("X-Forwarded-For"))
    )


def banned_response():
    """A 403 for a banned address, or ``None`` when the request may continue."""
    ip = _request_ip()
    if not ip:
        return None
    ban = security.active_ban(ip)
    if ban is None:
        return None

    headers: dict[str, str] = {"X-Niko-Blocked": "ip-ban"}
    expires_at = ban.get("expires_at")
    try:
        retry_after = int(float(expires_at) - time.time())
    except (TypeError, ValueError):
        retry_after = 0
    if retry_after > 0:
        headers["Retry-After"] = str(retry_after)

    if request.path.startswith(("/api/", "/v1/")):
        return (
            jsonify({
                "error": "This address has been blocked.",
                "code": "IP_BANNED",
                "retry_after": retry_after or None,
            }),
            403,
            headers,
        )
    return Response(_BANNED_PAGE, status=403, mimetype="text/plain", headers=headers)
