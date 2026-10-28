"""Proxy and VPN detection for the web captcha.

The website captcha is the only verification a member completes from a browser,
so it is the only one where the bot can see the connection's IP address. Servers
that are being raided through a proxy pool can therefore ask for proxy and VPN
traffic to be refused; every other mode ignores this module entirely.

Lookups go to ip-api.com's free endpoint: no key, 45 requests a minute, and two
fields that matter here — ``proxy`` (open proxy, VPN exit, or Tor) and
``hosting`` (datacenter ranges, which is where most commercial VPN exits and
every scripted bypass live). Results are cached per address for hours, because
the same handful of house IPs verify over and over.

Every failure path is deliberately permissive. A lookup outage blocking every
joining member would be a worse outcome than a raid slipping through, so a
timeout, a rate-limit rejection, or an unparseable reply means "not blocked".
"""

import ipaddress
import threading
import time
from collections import deque

import requests as req

LOOKUP_URL = "http://ip-api.com/json/{ip}?fields=status,message,proxy,hosting,mobile,countryCode"

CACHE_TTL_SECONDS = 6 * 3600

CACHE_LIMIT = 4096

# The free endpoint allows 45 lookups a minute. Stay under it: past the budget
# the lookup is skipped, which reads as "not blocked".
_RATE_LIMIT = 40

_RATE_WINDOW = 60.0

_cache: dict[str, tuple[float, dict]] = {}

_cache_lock = threading.Lock()

_call_times: deque[float] = deque()


def _is_private(ip: str) -> bool:
    """Loopback, private, and link-local addresses never leave the machine."""
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return True
    return address.is_private or address.is_loopback or address.is_link_local or address.is_reserved


def client_ip(remote_addr: str | None, forwarded_for: str | None = None) -> str:
    """The address to judge, from the proxy chain the deployment forwards.

    The site runs behind a reverse proxy, so ``remote_addr`` is the proxy
    itself. The left-most ``X-Forwarded-For`` entry is the original client — the
    one a proxy or VPN would be visible on.
    """
    for candidate in (forwarded_for or "").split(","):
        candidate = candidate.strip()
        if candidate:
            return candidate
    return (remote_addr or "").strip()


def _within_budget() -> bool:
    now = time.time()
    with _cache_lock:
        while _call_times and now - _call_times[0] > _RATE_WINDOW:
            _call_times.popleft()
        if len(_call_times) >= _RATE_LIMIT:
            return False
        _call_times.append(now)
        return True


def lookup(ip: str) -> dict | None:
    """ip-api's flags for one address, cached; ``None`` when it cannot be read."""
    if not ip or _is_private(ip):
        return {"proxy": False, "hosting": False, "mobile": False, "country": None}
    now = time.time()
    with _cache_lock:
        cached = _cache.get(ip)
        if cached is not None and now - cached[0] < CACHE_TTL_SECONDS:
            return cached[1]
    if not _within_budget():
        return None
    try:
        response = req.get(LOOKUP_URL.format(ip=ip), timeout=3)
        if response.status_code != 200:
            return None
        data = response.json()
    except (req.RequestException, ValueError):
        return None
    if not isinstance(data, dict) or data.get("status") != "success":
        return None
    flags = {
        "proxy": bool(data.get("proxy")),
        "hosting": bool(data.get("hosting")),
        "mobile": bool(data.get("mobile")),
        "country": data.get("countryCode"),
    }
    with _cache_lock:
        if len(_cache) >= CACHE_LIMIT:
            _cache.clear()
        _cache[ip] = (now, flags)
    return flags


def refusal(ip: str, block_proxies: bool = False, block_vpn: bool = False) -> str | None:
    """Why this address may not verify, or ``None`` when it may.

    ``block_proxies`` covers what ip-api reports as proxy/VPN/Tor exits;
    ``block_vpn`` additionally refuses hosting and datacenter ranges, which is
    what a commercial VPN endpoint and a bypass server both look like.
    """
    if not (block_proxies or block_vpn):
        return None
    flags = lookup(ip)
    if not flags:
        return None
    if block_proxies and flags.get("proxy"):
        return "proxy"
    if block_vpn and flags.get("hosting") and not flags.get("mobile"):
        return "vpn"
    return None


def clear_cache() -> None:
    """Forget every cached verdict (used by the tests)."""
    with _cache_lock:
        _cache.clear()
        _call_times.clear()
