"""
Music System — Lavalink node discovery.

Fetches public v4 nodes from the community node list (DarrenOfficial/
lavalink-list markdown), probes them for responsiveness, and dedupes by
unique host (an SSL twin and a non-SSL twin of the same server count as one
physical node). Falls back to a small embedded list when upstreams are down.
"""

import asyncio
import re
import time as _time

import aiohttp

from config.lavalink import LAVALINK_NODES
from utils import logging as log
from utils.music.constants import _MAX_PROBERS, _PROBE_TIMEOUT

# The bot defaults to the comprehensive hardcoded list in src/config/lavalink.py
# and only merges extra nodes from DarrenOfficial/lavalink-list when the
# upstream is reachable. The hardcoded list is updated periodically and is
# the authoritative source at startup.
_DN_SSL_RAW    = "https://raw.githubusercontent.com/DarrenOfficial/lavalink-list/master/docs/SSL/Lavalink-SSL.md"
_DN_NOSSL_RAW  = "https://raw.githubusercontent.com/DarrenOfficial/lavalink-list/master/docs/NoSSL/Lavalink-NonSSL.md"

_FALLBACK_NODES: list[dict] = list(LAVALINK_NODES)


# Nodes that use the Nodelink protocol are not compatible with Wavelink.
# We strip them out before merging any upstream results.
_NODELINK_HOSTS: set[str] = {
    "nodelink.triniumhost.com",
    "nodelink-02.triniumhost.com",
    "sg1-nodelink.nyxbot.app",
    "sg2-nodelink.nyxbot.app",
}


# Match a fenced ``bash``…`` block containing Host/Port/Password/Secure lines.
_DN_NODE_RE = re.compile(
    r"```bash\s*\n"
    r"\s*Host\s*:\s*(?P<host>\S+).*?\n"
    r"\s*Port\s*:\s*(?P<port>\d+).*?\n"
    r"\s*Password\s*:\s*(?P<password>.+?)\s*\n"
    r"\s*Secure\s*:\s*(?P<secure>[A-Za-z]+)\s*\n"
    r"```",
    re.IGNORECASE | re.DOTALL,
)


def _parse_dn_markdown(md: str, default_secure: bool) -> list[dict]:
    nodes: list[dict] = []
    for m in _DN_NODE_RE.finditer(md):
        host = m.group("host").strip()
        try:
            port = int(m.group("port").strip())
        except ValueError:
            continue
        # Strip surrounding quotes if present in the password field.
        password = m.group("password").strip().strip('"').strip("'")
        secure_raw = m.group("secure").strip().lower()
        secure = secure_raw in ("true", "yes", "1") if secure_raw else default_secure
        nodes.append({
            "host": host,
            "port": port,
            "password": password,
            "secure": secure,
            "version": "v4",
        })
    return nodes


async def _fetch_dn_source(session: aiohttp.ClientSession, url: str, default_secure: bool) -> list[dict]:
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status != 200:
                return []
            text = await r.text()
        return _parse_dn_markdown(text, default_secure)
    except Exception:
        return []


def _dedupe_nodes(nodes: list[dict]) -> list[dict]:
    seen: set[tuple[str, int, bool]] = set()
    unique: list[dict] = []
    for n in nodes:
        key = (n.get("host"), n.get("port"), bool(n.get("secure")))
        if key in seen:
            continue
        seen.add(key)
        unique.append(n)
    return unique


# The discovered pool only changes slowly, so cache it. Without this, retries
# after a failed connect (which back off from 30s) refetched both upstream
# markdown files every attempt.
_NODE_LIST_TTL = 1800.0
_cached_nodes: list[dict] | None = None
_cached_at: float = 0.0


async def fetch_node_list() -> list[dict]:
    """Return the hardcoded node list, optionally merged with upstream nodes.

    The hardcoded list is always the baseline.  When the public list is
    reachable, any nodes not already in the baseline are appended so the
    pool is as large as possible.  Nodelink entries are filtered out.

    Results are cached for ``_NODE_LIST_TTL`` seconds so reconnect retries
    do not refetch both upstream files on every attempt.
    """
    global _cached_nodes, _cached_at

    if _cached_nodes is not None and _time.monotonic() - _cached_at < _NODE_LIST_TTL:
        return list(_cached_nodes)

    baseline: list[dict] = list(_FALLBACK_NODES)

    try:
        async with aiohttp.ClientSession() as s:
            ssl_nodes, nossl_nodes = await asyncio.gather(
                _fetch_dn_source(s, _DN_SSL_RAW, default_secure=True),
                _fetch_dn_source(s, _DN_NOSSL_RAW, default_secure=False),
                return_exceptions=False,
            )
        upstream = _dedupe_nodes(list(ssl_nodes) + list(nossl_nodes))
        # Remove Nodelink nodes that are not compatible with Wavelink.
        upstream = [n for n in upstream if n["host"] not in _NODELINK_HOSTS]
        if upstream:
            # Merge: keep baseline first, then append any new upstream nodes.
            merged = _dedupe_nodes(baseline + upstream)
            new_count = len(merged) - len(baseline)
            if new_count > 0:
                log.info(
                    "Lavalink",
                    f"Merged {new_count} extra nodes from DarrenOfficial/lavalink-list "
                    f"({len(merged)} total).",
                )
            else:
                log.info("Lavalink", f"Hardcoded list covers all upstream nodes ({len(merged)} total).")
            _cached_nodes, _cached_at = merged, _time.monotonic()
            return merged
    except Exception as e:
        log.warning("Lavalink", f"Upstream fetch failed (using hardcoded list): {e}")

    log.info("Lavalink", f"Using hardcoded Lavalink node list ({len(baseline)} nodes).")
    _cached_nodes, _cached_at = baseline, _time.monotonic()
    return baseline


async def _probe_node(
    session: aiohttp.ClientSession,
    node: dict,
    sem: asyncio.Semaphore,
) -> tuple[dict, float] | None:
    host   = node["host"]
    port   = node["port"]
    scheme = "https" if node.get("secure") else "http"
    # Probe exactly what wavelink will use: the v4 REST API, authenticated with
    # the node's password. The old probe hit an unauthenticated ``/version`` and
    # required a 200, which discarded working nodes: some builds do not route
    # ``/version`` at all (404) and others answer 401 without the password
    # ("Who are you?? Why you here!"). Only the two serenetia twins happened to
    # answer it, so the pool collapsed onto the one host with the tightest
    # loadtracks rate limit while everything else was "failed" silently.
    url     = f"{scheme}://{host}:{port}/v4/info"
    headers = {"Authorization": str(node.get("password") or "")}
    async with sem:
        try:
            t0 = _time.monotonic()
            # Verify TLS like wavelink will: probing with ssl=False accepted
            # nodes whose certificate wavelink then refused, wasting a slot.
            async with session.get(
                url, headers=headers, timeout=aiohttp.ClientTimeout(total=_PROBE_TIMEOUT)
            ) as r:
                if r.status != 200:
                    log.info("Lavalink", f"Probe rejected {host}:{port} — HTTP {r.status}.")
                    return None
                # A 200 from something that is not Lavalink (a proxy page, a
                # Cloudflare interstitial) must not take a pool slot.
                info = await r.json(content_type=None)
                if not isinstance(info, dict) or "version" not in info:
                    log.info(
                        "Lavalink", f"Probe rejected {host}:{port} — /v4/info is not Lavalink."
                    )
                    return None
                return (node, (_time.monotonic() - t0) * 1000)
        except Exception as exc:
            log.info("Lavalink", f"Probe rejected {host}:{port} — {type(exc).__name__}: {exc}")
    return None


async def find_responsive_nodes(nodes: list[dict]) -> list[dict]:
    sem = asyncio.Semaphore(_MAX_PROBERS)
    async with aiohttp.ClientSession() as s:
        results = await asyncio.gather(
            *[_probe_node(s, n, sem) for n in nodes],
            return_exceptions=True,
        )
    alive = [r for r in results if r and not isinstance(r, BaseException)]
    alive.sort(key=lambda x: x[1])

    # The public list often carries the same host twice (an SSL and a non-SSL
    # twin, e.g. host:443 + host:80) — that is one physical server, so keep
    # only its fastest responding port. Two sessions to the same host would
    # both die together and inflate the "connected" count.
    seen_hosts: set[str] = set()
    unique: list[tuple[dict, float]] = []
    for node, latency in alive:
        host = node["host"]
        if host in seen_hosts:
            continue
        seen_hosts.add(host)
        unique.append((node, latency))
    alive = unique

    if alive:
        summary = ", ".join(f"{n['host']}:{n['port']} ({lat:.0f}ms)" for n, lat in alive[:4])
        log.info(
            "Lavalink",
            f"{len(alive)}/{len(nodes)} nodes responsive (per unique host) — {summary}",
        )
    else:
        log.warning("Lavalink", f"No nodes responded out of {len(nodes)} tried.")
    return [n for n, _ in alive]