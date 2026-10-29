"""SVG card for Niko's own profile, for the GitHub README.

The card is fetched by GitHub (through its image proxy) and rendered inside an
``<img>``, where an SVG cannot load external files. Everything the card needs is
therefore inlined: the avatar travels as a base64 data URI and the markup uses
plain SVG presentation attributes instead of an external stylesheet.

It deliberately borrows the staff card's palette and geometry, so the bot card
sits beside a member's profile card instead of looking like a different product.
The numbers come from the running bot, so a README refresh shows the current
guild, member, command, latency, and uptime figures rather than a snapshot.
"""

from __future__ import annotations

from html import escape

from .staff_card import (
    DEFAULT_ACCENT,
    PALETTES,
    _clip,
    _document,
    _text,
    accent_hex,
    normalize_theme,
    status_icon_data_url,
)

CARD_WIDTH = 620
CARD_HEIGHT = 254
AVATAR_CENTER = 84
AVATAR_RADIUS = 42
MONO = "Space Mono, ui-monospace, monospace"

TAGLINE = "Moderation, music, leveling, economy and AI \u2014 one bot."
CHIP_LABEL = "NIKO \u00b7 GLOBAL PROFILE"

# Five equal tiles across the card, inside the same 24px margin the staff card
# uses. Wider cards would stretch in a README column; narrower ones wrap labels.
STAT_TILE_GAP = 10
STAT_TILE_TOP = 170
STAT_TILE_HEIGHT = 64
STAT_TILE_WIDTH = (CARD_WIDTH - 48 - STAT_TILE_GAP * 4) / 5


def _compact(value) -> str:
    """A count that fits a 106px tile: ``9``, ``1,234``, ``12.3k``, ``1.2M``."""
    try:
        number = int(value or 0)
    except (TypeError, ValueError):
        number = 0
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M".replace(".0M", "M")
    if number >= 10_000:
        return f"{number / 1_000:.1f}k".replace(".0k", "k")
    return f"{max(0, number):,}"


def _duration(seconds) -> str:
    """``3d 4h``-style uptime, or an em dash when it is unknown."""
    if seconds is None:
        return "\u2014"
    total = max(0, int(seconds))
    days, remainder = divmod(total, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes = remainder // 60
    if days:
        return f"{days}d {hours}h"
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def _latency(milliseconds) -> str:
    if milliseconds is None:
        return "\u2014"
    try:
        return f"{max(0, int(milliseconds))} ms"
    except (TypeError, ValueError):
        return "\u2014"


def _avatar_block(avatar_data_url: str | None, accent: str, palette: dict) -> str:
    """Round bot avatar, or the brand initial when there is no image."""
    cx, cy, radius = AVATAR_CENTER, AVATAR_CENTER, AVATAR_RADIUS
    if not avatar_data_url:
        return (
            f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{palette["chip"]}" '
            f'stroke="{accent}" stroke-width="2" stroke-opacity="0.45"/>'
            + _text(cx, cy + 12, "n", fill=accent, size=30, weight=800, anchor="middle")
        )
    return (
        '<defs><clipPath id="niko-card-avatar">'
        f'<circle cx="{cx}" cy="{cy}" r="{radius}"/>'
        "</clipPath></defs>"
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{palette["chip"]}"/>'
        f'<image href="{escape(avatar_data_url)}" x="{cx - radius}" y="{cy - radius}" '
        f'width="{radius * 2}" height="{radius * 2}" '
        'preserveAspectRatio="xMidYMid slice" clip-path="url(#niko-card-avatar)"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{accent}" '
        'stroke-width="2" opacity="0.55"/>'
    )


def _status_badge(online: bool, palette: dict) -> str:
    """The presence art on the avatar, matching the website and staff cards."""
    status = "online" if online else "offline"
    icon = status_icon_data_url(status)
    badge = (
        f'<circle cx="{AVATAR_CENTER + 32}" cy="{AVATAR_CENTER + 32}" r="16" '
        f'fill="{palette["ring"]}"/>'
    )
    if icon:
        return badge + (
            f'<image href="{icon}" x="{AVATAR_CENTER + 19}" y="{AVATAR_CENTER + 19}" '
            'width="26" height="26"/>'
        )
    colour = "#23A55A" if online else "#80848E"
    return badge + f'<circle cx="{AVATAR_CENTER + 32}" cy="{AVATAR_CENTER + 32}" r="8" fill="{colour}"/>'


def _stat_tile(x: float, label: str, value: str, palette: dict) -> str:
    return (
        f'<rect x="{x:.1f}" y="{STAT_TILE_TOP}" width="{STAT_TILE_WIDTH:.1f}" '
        f'height="{STAT_TILE_HEIGHT}" rx="14" fill="{palette["chip"]}" '
        f'stroke="{palette["line"]}" stroke-width="1"/>'
        + _text(x + 14, STAT_TILE_TOP + 24, label.upper(), fill=palette["dim"], size=8.5,
                weight=700, family=MONO, spacing="1.1")
        + _text(x + 14, STAT_TILE_TOP + 50, value, fill=palette["ink"], size=17, weight=800)
    )


def render_bot_card(
    profile: dict,
    *,
    theme=None,
    accent=None,
    avatar_data_url: str | None = None,
) -> str:
    """Render Niko's profile card from a live ``_bot_card_profile`` snapshot."""
    palette = PALETTES[normalize_theme(theme)]
    accent_hex_value = accent_hex(accent, DEFAULT_ACCENT)
    accent_colour = f"#{accent_hex_value}"

    name = _clip(profile.get("name"), 28) or "Niko"
    handle = _clip(profile.get("handle"), 24) or "niko"
    online = bool(profile.get("online"))

    chip_width = min(320, int(len(CHIP_LABEL) * 7.2) + 24)
    stats = (
        ("Servers", _compact(profile.get("guild_count"))),
        ("Members", _compact(profile.get("user_count"))),
        ("Commands", _compact(profile.get("command_count"))),
        ("Ping", _latency(profile.get("latency_ms"))),
        ("Uptime", _duration(profile.get("uptime_seconds"))),
    )
    tiles = "".join(
        _stat_tile(24 + index * (STAT_TILE_WIDTH + STAT_TILE_GAP), label, value, palette)
        for index, (label, value) in enumerate(stats)
    )

    parts = [
        f'<rect width="{CARD_WIDTH}" height="{CARD_HEIGHT}" rx="22" fill="url(#staff-card-bg)"/>',
        f'<rect x="1" y="1" width="{CARD_WIDTH - 2}" height="{CARD_HEIGHT - 2}" rx="21" '
        f'fill="none" stroke="{accent_colour}" stroke-width="1.5" opacity="0.42"/>',
        _avatar_block(avatar_data_url, accent_colour, palette),
        _status_badge(online, palette),
        # Profile chip
        f'<rect x="148" y="36" width="{chip_width}" height="24" rx="12" '
        f'fill="{accent_colour}" opacity="0.16"/>',
        _text(160, 53, CHIP_LABEL, fill=accent_colour, size=10, weight=700,
              family=MONO, spacing="1.1"),
        _text(148, 92, name, fill=palette["ink"], size=25, weight=800),
        _text(148, 114, f"@{handle}", fill=palette["dim"], size=12, family=MONO),
        _text(148, 146, TAGLINE, fill=palette["muted"], size=11.5),
        tiles,
    ]

    return _document("".join(parts), CARD_WIDTH, CARD_HEIGHT, palette,
                     f"{name} \u2014 live bot profile")
