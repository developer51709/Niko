"""
Music System — Lavalink node catalogue.

The catalogue has exactly two sources: the hardcoded list in
``src/config/lavalink.py`` and the private nodes the bot owner saved from the
dashboard (stored in the music database, never in the repository). Nothing is
fetched from a public node list, so the pool is predictable and no third-party
markdown can inject — or withdraw — a node.

Candidates are probed for responsiveness and deduped by unique host (an SSL
twin and a non-SSL twin of the same server count as one physical node).
"""

import asyncio
import time as _time

import aiohttp

from config.lavalink import LAVALINK_NODES
from utils import logging as log
from utils.music.constants import _MAX_PROBERS, _PROBE_TIMEOUT

_FALLBACK_NODES: list[dict] = list(LAVALINK_NODES)


# Nodes that use the Nodelink protocol are not compatible with Wavelink.
_NODELINK_HOSTS: set[str] = {
    "nodelink.triniumhost.com",
    "nodelink-02.triniumhost.com",
    "sg1-nodelink.nyxbot.app",
    "sg2-nodelink.nyxbot.app",
}


def node_identifier(node: dict) -> str:
    """``host:port`` — the pool key wavelink uses for a node."""
    return f"{node['host']}:{node['port']}"


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


def node_catalog(private_nodes: list[dict] | None = None) -> list[dict]:
    """Return the pool catalogue: the owner's private nodes, then the static list.

    Private nodes come first and win duplicate ``host:port`` keys, so an owner
    entry with a working password replaces a stale public one instead of being
    silently dropped by the merge. The ``private`` flag travels with each entry
    so the cog can keep owner nodes ahead of public ones in the pool.
    """
    private = [{**dict(node), "private": True} for node in (private_nodes or [])]
    merged = _dedupe_nodes(private + list(_FALLBACK_NODES))
    return [node for node in merged if node["host"] not in _NODELINK_HOSTS]


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
    # Private nodes are the owner's own servers, so they lead the group even
    # when a public node probes faster; latency orders the rest.
    alive.sort(key=lambda x: (not x[0].get("private"), x[1]))

    # The catalogue often carries the same host twice (an SSL and a non-SSL
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
