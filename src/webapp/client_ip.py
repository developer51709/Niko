"""Resolve the address a request came from, including the proxy's hop.

The supervisor owns the public socket and replaces any incoming forwarding
headers with the address it trusts.  The web child therefore reads the left-most
``X-Forwarded-For`` entry instead of its own peer, which is usually loopback.
Tests and direct local requests without a proxy fall back to ``remote_addr``.
"""

from __future__ import annotations

import ipaddress

from flask import has_request_context, request


def normalise_ip(raw) -> str:
    """Return canonical IPv4/IPv6 text, or ``""`` when it is not an address."""
    value = str(raw or "").strip()
    if not value or value.lower() == "unknown":
        return ""
    if value.startswith("[") and "]" in value:
        value = value[1 : value.index("]")]
    elif value.count(":") == 1 and "." in value:
        host, _, port = value.partition(":")
        if port.isdigit():
            value = host
    try:
        return str(ipaddress.ip_address(value))
    except ValueError:
        return ""


def _first_forwarded_ip(raw) -> str:
    for item in str(raw or "").split(","):
        address = normalise_ip(item)
        if address:
            return address
    return ""


def request_client_ip() -> str:
    """The visitor address for this request, or ``""`` outside a request."""
    if not has_request_context():
        return ""
    # The supervisor strips client-supplied forwarding headers and writes the
    # trusted address here. Cloudflare's headers are a fallback for requests
    # that reached the app through a different trusted proxy.
    for header in ("X-Forwarded-For", "CF-Connecting-IP", "True-Client-IP"):
        address = _first_forwarded_ip(request.headers.get(header))
        if address:
            return address
    return normalise_ip(request.remote_addr)
