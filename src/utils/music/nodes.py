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


async def fetch_node_list() -> list[dict]:
    """Return the hardcoded node list, optionally merged with upstream nodes.

    The hardcoded list is always the baseline.  When the public list is
    reachable, any nodes not already in the baseline are appended so the
    pool is as large as possible.  Nodelink entries are filtered out.
    """
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
            return merged
    except Exception as e:
        log.warning("Lavalink", f"Upstream fetch failed (using hardcoded list): {e}")

    log.info("Lavalink", f"Using hardcoded Lavalink node list ({len(baseline)} nodes).")
    return baseline


async def _probe_node(
    session: aiohttp.ClientSession,
    node: dict,
    sem: asyncio.Semaphore,
) -> tuple[dict, float] | None:
    host   = node["host"]
    port   = node["port"]
    scheme = "https" if node.get("secure") else "http"
    url    = f"{scheme}://{host}:{port}/version"
    async with sem:
        try:
            t0 = _time.monotonic()
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=_PROBE_TIMEOUT), ssl=False) as r:
                if r.status == 200:
                    return (node, (_time.monotonic() - t0) * 1000)
        except Exception:
            pass
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