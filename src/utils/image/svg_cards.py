"""
SVG card URL builder for wsrv.nl proxy.

Every function returns a PNG-safe URL by pointing wsrv.nl at a Flask SVG
endpoint.  A ``&t=<timestamp>`` query parameter ensures Discord's CDN cache
is never stale.

Usage from a bot cog::

    from utils.image.svg_cards import economy_card_url, rank_card_url
    url = economy_card_url(balance=1000, bank=5000, name="Soren", avatar_url="...")
    # url → "https://wsrv.nl/?url=<encoded>&w=820&t=1726000000"

The Flask side lives in ``src/website.py`` and serves ``image/svg+xml``.
"""

from __future__ import annotations

import time
from urllib.parse import quote

# ── Public domain / base URL ────────────────────────────────────────────────

# The website domain.  wsrv.nl fetches from here, so it must be publicly
# reachable.  Falls back gracefully if the env-var is missing (local dev).
_WEBSITE_BASE = "https://niko.sryze.cc"

WSRV_BASE = "https://wsrv.nl/"

# ── Internal helpers ─────────────────────────────────────────────────────────


def _ts() -> str:
    """Current Unix timestamp as a string (cache-buster)."""
    return str(int(time.time()))


def _proxy(svg_url: str, w: int = 820, h: int | None = None) -> str:
    """Wrap *svg_url* through wsrv.nl so Discord receives a PNG."""
    inner = f"{_WEBSITE_BASE}{svg_url}"
    parts = [f"url={quote(inner, safe='')}"]
    parts.append(f"w={w}")
    if h:
        parts.append(f"h={h}")
    parts.append(f"t={_ts()}")
    return f"{WSRV_BASE}?" + "&".join(parts)


def _safe(text: str) -> str:
    """URL-encode a text value for an SVG query param."""
    return quote(str(text), safe="")


# ── Public API ───────────────────────────────────────────────────────────────


def economy_card_url(
    *,
    name: str,
    balance: int,
    bank: int,
    net_worth: int,
    job: str,
    daily_streak: int = 0,
    level: int = 0,
    avatar_url: str = "",
    accent: str = "FFC45C",
    bg_top: str = "261A16",
    bg_bot: str = "120C0A",
) -> str:
    """Economy balance / profile card URL (820×380)."""
    params = (
        f"?name={_safe(name)}"
        f"&balance={balance}"
        f"&bank={bank}"
        f"&net_worth={net_worth}"
        f"&job={_safe(job)}"
        f"&daily_streak={daily_streak}"
        f"&level={level}"
        f"&avatar_url={_safe(avatar_url)}"
        f"&accent={accent}"
        f"&bg_top={bg_top}"
        f"&bg_bot={bg_bot}"
    )
    return _proxy(f"/api/cards/economy{params}", w=820, h=380)


def daily_card_url(
    *,
    name: str,
    reward: int,
    streak: int,
    balance: int,
    job: str,
    avatar_url: str = "",
    accent: str = "FFC45C",
    bg_top: str = "261A16",
    bg_bot: str = "120C0A",
) -> str:
    """Daily reward card URL (820×280)."""
    params = (
        f"?name={_safe(name)}"
        f"&reward={reward}"
        f"&streak={streak}"
        f"&balance={balance}"
        f"&job={_safe(job)}"
        f"&avatar_url={_safe(avatar_url)}"
        f"&accent={accent}"
        f"&bg_top={bg_top}"
        f"&bg_bot={bg_bot}"
    )
    return _proxy(f"/api/cards/daily{params}", w=820, h=280)


def work_card_url(
    *,
    name: str,
    reward: int,
    job: str,
    balance: int,
    message: str = "",
    avatar_url: str = "",
    accent: str = "FFC45C",
    bg_top: str = "261A16",
    bg_bot: str = "120C0A",
) -> str:
    """Work reward card URL (820×300)."""
    params = (
        f"?name={_safe(name)}"
        f"&reward={reward}"
        f"&job={_safe(job)}"
        f"&balance={balance}"
        f"&message={_safe(message)}"
        f"&avatar_url={_safe(avatar_url)}"
        f"&accent={accent}"
        f"&bg_top={bg_top}"
        f"&bg_bot={bg_bot}"
    )
    return _proxy(f"/api/cards/work{params}", w=820, h=300)


def rank_card_url(
    *,
    name: str,
    level: int,
    xp: int,
    xp_for_next: int,
    rank: int,
    avatar_url: str = "",
    accent: str = "FFC45C",
    bg_top: str = "261A16",
    bg_bot: str = "120C0A",
) -> str:
    """Level / rank card URL (820×340)."""
    params = (
        f"?name={_safe(name)}"
        f"&level={level}"
        f"&xp={xp}"
        f"&xp_for_next={xp_for_next}"
        f"&rank={rank}"
        f"&avatar_url={_safe(avatar_url)}"
        f"&accent={accent}"
        f"&bg_top={bg_top}"
        f"&bg_bot={bg_bot}"
    )
    return _proxy(f"/api/cards/rank{params}", w=820, h=340)


def leaderboard_card_url(
    *,
    title: str,
    entries: list[dict],
    page: int = 1,
    pages: int = 1,
    accent: str = "FFC45C",
    bg_top: str = "261A16",
    bg_bot: str = "120C0A",
    card_type: str = "economy",
) -> str:
    """Leaderboard card URL — variable height.

    Each *entry* is ``{"rank": int, "name": str, "value": int, "avatar_url": str}``.
    """
    import json as _json

    row_h = 68
    n = len(entries)
    height = 110 + n * row_h + 56

    params = (
        f"?title={_safe(title)}"
        f"&page={page}"
        f"&pages={pages}"
        f"&entries={_safe(_json.dumps(entries))}"
        f"&accent={accent}"
        f"&bg_top={bg_top}"
        f"&bg_bot={bg_bot}"
        f"&type={card_type}"
    )
    return _proxy(f"/api/cards/leaderboard{params}", w=820, h=height)


def shop_card_url(
    *,
    items: list[dict],
    balance: int,
    category: str | None = None,
    accent: str = "FFC45C",
    bg_top: str = "261A16",
    bg_bot: str = "120C0A",
) -> str:
    """Shop card URL — variable height based on item count.

    Each *item* is ``{"item_id": str, "name": str, "price": int, "emoji": str, "category": str, "description": str}``.
    """
    import json as _json

    row_h = 52
    n = len(items)
    header_h = 120
    height = header_h + n * row_h + 40
    height = min(height, 1200)  # cap

    params = (
        f"?items={_safe(_json.dumps(items))}"
        f"&balance={balance}"
        f"&category={_safe(category or '')}"
        f"&accent={accent}"
        f"&bg_top={bg_top}"
        f"&bg_bot={bg_bot}"
    )
    return _proxy(f"/api/cards/shop{params}", w=820, h=height)


def inventory_card_url(
    *,
    name: str,
    balance: int,
    sections: list[dict],
    avatar_url: str = "",
    accent: str = "FFC45C",
    bg_top: str = "261A16",
    bg_bot: str = "120C0A",
) -> str:
    """Inventory card URL — variable height based on items.

    Each *section* is ``{"label": str, "items": [{"emoji": str, "name": str, "count": int, "desc": str}]}``.
    """
    import json as _json

    row_h = 44
    total_items = sum(len(s.get("items", [])) for s in sections)
    height = 120 + len(sections) * 56 + total_items * row_h + 40
    height = min(height, 1200)

    params = (
        f"?name={_safe(name)}"
        f"&balance={balance}"
        f"&sections={_safe(_json.dumps(sections))}"
        f"&avatar_url={_safe(avatar_url)}"
        f"&accent={accent}"
        f"&bg_top={bg_top}"
        f"&bg_bot={bg_bot}"
    )
    return _proxy(f"/api/cards/inventory{params}", w=820, h=height)


def coinflip_card_url(
    *,
    name: str,
    call: str,
    result: str,
    won: bool,
    amount: int,
    payout: int,
    balance: int,
    avatar_url: str = "",
    accent: str = "FFC45C",
    bg_top: str = "261A16",
    bg_bot: str = "120C0A",
) -> str:
    """Coinflip result card URL (820×300)."""
    params = (
        f"?name={_safe(name)}"
        f"&call={_safe(call)}"
        f"&result={_safe(result)}"
        f"&won={'1' if won else '0'}"
        f"&amount={amount}"
        f"&payout={payout}"
        f"&balance={balance}"
        f"&avatar_url={_safe(avatar_url)}"
        f"&accent={accent}"
        f"&bg_top={bg_top}"
        f"&bg_bot={bg_bot}"
    )
    return _proxy(f"/api/cards/coinflip{params}", w=820, h=300)
