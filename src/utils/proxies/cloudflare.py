"""Cloudflare interstitial detection for Discord responses.

Discord serves every API response through Cloudflare, so ``Server: cloudflare``
and ``CF-Ray`` are on ordinary traffic too and prove nothing. Only Cloudflare's
own block/challenge page, its ``cf-mitigated`` header, or a numeric ``error
code: 10xx`` body is a real block — that is the signature a different egress IP
clears.

Used by the Webshare failover (a throttle means "rotate egress") and by the
dashboard's Discord client (a block means "retry over the proxy").
"""

from __future__ import annotations

import json
import re

# Markers only Cloudflare's own interstitial carries.
_PAGE_MARKERS = (
    "cf-error-details",
    "cf-wrapper",
    "attention required",
    "just a moment",
    "cf-chl",
    "cloudflare ray id",
    "checking your browser",
)

# Cloudflare's plain-text access-denied answers ("error code: 1020") carry no
# HTML at all, so its numeric error codes are matched on their own.
_ERROR_CODE = re.compile(r"(?:error code|cloudflare error)\s*:?\s*10\d\d")

# The interstitial's footer names the client address it refused, which is the one
# fact that tells a real block of a proxy apart from a request that never left
# through it.  The live page hides it behind a "Click to reveal" button —
# ``id="cf-footer-ip"`` holds the value, followed by the plain-text form on
# pages that render it directly.
_EGRESS_IP = re.compile(
    r'id="cf-footer-ip"[^>]*>\s*([0-9a-fA-F.:]{3,45})'
    r"|your ip:?\s*(?:<[^>]*>\s*)*([0-9a-fA-F.:]{3,45})"
)

_BLOCK_STATUSES = {403, 429, 503}


def _status(response) -> int:
    return getattr(response, "status", getattr(response, "status_code", 0))


def _body(response, fallback: str = "") -> str:
    """Read a response body from either client without calling a coroutine.

    ``requests`` exposes ``text`` as a string property while aiohttp exposes it
    as an async method. Never invoke a callable here: doing so can create an
    un-awaited coroutine. The aiohttp caller reads the body itself and passes it
    as the fallback.
    """
    body = getattr(response, "text", "")
    if callable(body) or not isinstance(body, str) or not body:
        body = fallback
    return body if isinstance(body, str) else ""


def _is_discord_api_error(body: str) -> bool:
    """True for a Discord JSON API or rate-limit body (never a Cloudflare page)."""
    if not body.strip().startswith("{"):
        return False
    try:
        payload = json.loads(body)
    except ValueError:
        return False
    return isinstance(payload, dict) and ("message" in payload or "error" in payload)


def _evidence(headers, body: str) -> str | None:
    """Return the interstitial signature Cloudflare left behind, if any."""
    if str(headers.get("cf-mitigated", "")).strip():
        return f"cf-mitigated: {headers.get('cf-mitigated')}"
    lowered = body.lower()
    match = _ERROR_CODE.search(lowered)
    if match:
        return match.group(0)
    for marker in _PAGE_MARKERS:
        if marker in lowered:
            return marker
    if "cloudflare" in lowered and ("<html" in lowered or "<!doctype html" in lowered):
        return "cloudflare block page"
    return None


def blocked_egress_ip(body: str) -> str | None:
    """The client address Cloudflare's block page says it refused, if it says.

    Cloudflare prints ``Your IP: <address>`` in the interstitial's footer.  That
    address is the egress the block belongs to: if it is the proxy the request
    went through, the proxy really is blocked; if it is something else, the
    request did not leave through the proxy and blacklisting the proxy for it
    would throw away a working endpoint.
    """
    match = _EGRESS_IP.search((body or "").lower())
    if not match:
        return None
    return (match.group(1) or match.group(2) or "").strip(".:-") or None


def interstitial_signature(response, body_fallback: str = "") -> str | None:
    """The Cloudflare block signature on a response, or ``None``.

    A plain Discord 429 or JSON error returns ``None``: treating those as blocks
    would report a ban that never happened.
    """
    if _status(response) not in _BLOCK_STATUSES:
        return None
    body = _body(response, body_fallback)
    if _is_discord_api_error(body):
        return None
    return _evidence(getattr(response, "headers", {}), body)
