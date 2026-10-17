"""
Minimal SVG card URL builder for wsrv.nl proxy.

Every function passes IDs (guild, user, page) — the Flask endpoints query the
database for the actual data.  A ``&t=<timestamp>`` query parameter ensures
Discord's CDN cache is never stale.

Usage from a bot cog::

    from utils.image.svg_cards import rank_card_url, leaderboard_card_url
    url = rank_card_url(guild_id=123, user_id=456)
    # url → "https://wsrv.nl/?url=<encoded>&w=820&t=1726000000"
"""

from __future__ import annotations

import time
from urllib.parse import quote

_WEBSITE_BASE = "https://niko.sryze.cc"
WSRV_BASE = "https://wsrv.nl/"


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

def rank_card_url(
    *,
    guild_id: int | str,
    user_id: int | str,
) -> str:
    """Level / rank card URL (820×340).  Server-side queries the DB."""
    params = f"?guild={guild_id}&user={user_id}"
    return _proxy(f"/api/cards/rank{params}", w=820, h=340)


def leaderboard_card_url(
    *,
    guild_id: int | str,
    page: int = 1,
    card_type: str = "level",
) -> str:
    """Leaderboard card URL — variable height.  Server-side queries the DB."""
    params = f"?guild={guild_id}&page={page}&type={card_type}"
    return _proxy(f"/api/cards/leaderboard{params}", w=820, h=700)


def shop_card_url(
    *,
    category: str | None = None,
) -> str:
    """Shop card URL — server-side reads SHOP_ITEMS config."""
    params = f"?cat={_safe((category or 'all')[:20])}"
    return _proxy(f"/api/cards/shop{params}", w=820, h=800)


def economy_card_url(
    *,
    user_id: int | str,
) -> str:
    """Economy balance / profile card URL (820×380).  Server-side queries the DB."""
    params = f"?user={user_id}"
    return _proxy(f"/api/cards/economy{params}", w=820, h=380)


def daily_card_url(
    *,
    user_id: int | str,
    reward: int,
) -> str:
    """Daily reward card URL (820×280).  Server-side queries the DB."""
    params = f"?user={user_id}&reward={reward}"
    return _proxy(f"/api/cards/daily{params}", w=820, h=280)


def work_card_url(
    *,
    user_id: int | str,
    reward: int,
    message: str = "",
) -> str:
    """Work reward card URL (820×300).  Server-side queries the DB."""
    params = f"?user={user_id}&reward={reward}&msg={_safe(message[:80])}"
    return _proxy(f"/api/cards/work{params}", w=820, h=300)


def inventory_card_url(
    *,
    user_id: int | str,
) -> str:
    """Inventory card URL — variable height.  Server-side queries the DB."""
    params = f"?user={user_id}"
    return _proxy(f"/api/cards/inventory{params}", w=820, h=600)


def coinflip_card_url(
    *,
    user_id: int | str,
    call: str,
    result: str,
    won: bool,
    amount: int,
    payout: int,
) -> str:
    """Coinflip result card URL (820×300).  Server-side queries the DB."""
    params = (
        f"?user={user_id}"
        f"&call={_safe(call)}"
        f"&result={_safe(result)}"
        f"&won={'1' if won else '0'}"
        f"&amount={amount}"
        f"&payout={payout}"
    )
    return _proxy(f"/api/cards/coinflip{params}", w=820, h=300)
