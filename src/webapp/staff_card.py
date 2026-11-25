"""SVG card for a staff member's GitHub README.

The card is fetched by GitHub (through its image proxy) and rendered inside an
``<img>``, where an SVG cannot load external files. Everything the card needs is
therefore inlined: the avatar travels as a base64 data URI and the markup uses
plain SVG presentation attributes instead of an external stylesheet.

Status is read from the same live presence the public Team page uses, so a card
shows the staff member's real Discord state rather than a stored snapshot.
"""

from __future__ import annotations

import base64
import re
import time
from html import escape
from pathlib import Path
from urllib.parse import urlparse

import requests as req

CARD_WIDTH = 620
CARD_HEIGHT = 200
# An activity (Spotify track, game, stream) gets its own card at the bottom, so
# the document only grows when there is one to draw.
ACTIVITY_CARD_EXTRA = 76
CARD_HEIGHT_WITH_ACTIVITY = CARD_HEIGHT + ACTIVITY_CARD_EXTRA
HIDDEN_CARD_HEIGHT = 120

DEFAULT_ACCENT = "C8A882"

STATUS_COLORS = {
    "online": "#23A55A",
    "idle": "#F0B232",
    "dnd": "#F23F43",
    "offline": "#80848E",
}

AVATAR_CENTER = 84
AVATAR_RADIUS = 42
# The status art follows the website's ``.discord-status-avatar`` rule: the
# notch is the icon's silhouette grown by a 12% gap on every side and sits
# flush with the avatar's bottom-right corner, so the gap between the picture
# and the art is even. The art itself is the site's own 26px asset.
STATUS_ICON_SIZE = 26
STATUS_ICON_GAP = STATUS_ICON_SIZE * 0.12
STATUS_NOTCH_SIZE = STATUS_ICON_SIZE + 2 * STATUS_ICON_GAP
# A phone holding the presence replaces the dot, and Discord narrows the notch
# to the phone's silhouette (the site's ``--status-shape-width: .665``) while
# the square icon keeps its own transparent margin. The site's notch is a 75x100
# rect with a 16px corner, so the card's corner scales with the notch's width.
MOBILE_NOTCH_WIDTH = STATUS_ICON_SIZE * 0.665 + 2 * STATUS_ICON_GAP
MOBILE_NOTCH_CORNER = 16 / 75
# Discord draws an avatar decoration on a canvas 1.2x the avatar and centres
# the two, so the artwork overhangs the picture by the same amount everywhere.
DECORATION_SCALE = 1.2

# Two card styles: the compact strip a README has always shown, and a full
# profile card laid out like the website's Discord profile popup. ``compact``
# stays the default so an existing embed never changes on its own.
CARD_STYLES = ("compact", "profile")
PROFILE_BANNER_HEIGHT = 116
PROFILE_AVATAR_RADIUS = 48
PROFILE_AVATAR_CENTRE = (40 + PROFILE_AVATAR_RADIUS, PROFILE_BANNER_HEIGHT)
PROFILE_GUTTER = 40
PROFILE_BODY_WIDTH = CARD_WIDTH - PROFILE_GUTTER * 2
PROFILE_BADGE_SIZE = 22
PROFILE_BIO_LIMIT = 86
PROFILE_BIO_LINES = 4

PALETTES = {
    "dark": {
        "top": "#181B21",
        "bottom": "#0A0B0E",
        "ink": "#F4F5F7",
        "muted": "#B4BAC3",
        "dim": "#858C96",
        "line": "rgba(255, 255, 255, 0.10)",
        "chip": "rgba(255, 255, 255, 0.06)",
        "ring": "#14161A",
    },
    "light": {
        "top": "#FBF8F3",
        "bottom": "#EEE7DD",
        "ink": "#15171B",
        "muted": "#5B616A",
        "dim": "#8A9099",
        "line": "rgba(21, 23, 27, 0.12)",
        "chip": "rgba(21, 23, 27, 0.05)",
        "ring": "#FBF8F3",
    },
}

_HEX_RE = re.compile(r"^[0-9A-Fa-f]{6}$")
_ALLOWED_AVATAR_HOSTS = ("cdn.discordapp.com", "media.discordapp.net")
# Activity artwork: Spotify album covers, plus Discord-hosted activity assets.
_ALLOWED_ART_HOSTS = ("i.scdn.co", "cdn.discordapp.com", "media.discordapp.net")
_AVATAR_TTL = 6 * 60 * 60
_ART_TTL = 60 * 60
_IMAGE_MAX_BYTES = 3 * 1024 * 1024
_avatar_cache: dict[str, tuple[float, str | None]] = {}
_art_cache: dict[str, tuple[float, str | None]] = {}

SPOTIFY_GREEN = "#1DB954"

ACTIVITY_LABELS = {
    "playing": "Playing",
    "listening": "Listening to",
    "watching": "Watching",
    "streaming": "Streaming",
    "competing": "Competing in",
}

# The website's Discord status art, inlined the same way the avatar is: an SVG
# rendered inside <img> cannot fetch the PNG from /assets at draw time.
_STATUS_ICON_DIRS = (
    Path(__file__).resolve().parents[1] / "website" / "dist" / "assets" / "discord-status",
    Path(__file__).resolve().parents[2] / "web" / "public" / "assets" / "discord-status",
)
# The Spotify wordmark is inlined as a path so the card needs no external file.
_SPOTIFY_MARK_PATHS = (
    Path(__file__).resolve().parents[1] / "website" / "dist" / "spotify.svg",
    Path(__file__).resolve().parents[2] / "web" / "public" / "spotify.svg",
)
_spotify_mark_cache: dict[str, str | None] = {}
_status_icon_cache: dict[str, str | None] = {}
# Badges are 24px SVGs that ship with the site, so the profile card inlines
# them the same way it inlines the status art.
_BADGE_DIRS = (
    Path(__file__).resolve().parents[1] / "website" / "dist" / "assets" / "badges",
    Path(__file__).resolve().parents[2] / "web" / "public" / "assets" / "badges",
)
_badge_cache: dict[str, str | None] = {}
_banner_cache: dict[str, tuple[float, str | None]] = {}


def normalize_theme(value) -> str:
    """``dark`` or ``light``; anything else falls back to the dark card."""
    return "light" if str(value or "").strip().lower() == "light" else "dark"


def normalize_style(value) -> str:
    """``compact`` or ``profile``; anything else falls back to compact."""
    key = str(value or "").strip().lower()
    return key if key in CARD_STYLES else "compact"


def accent_hex(value, fallback: str = DEFAULT_ACCENT) -> str:
    """A bare ``RRGGBB`` colour, so it can be dropped into SVG attributes."""
    raw = str(value or "").lstrip("#").strip()
    return raw.upper() if _HEX_RE.match(raw) else fallback


def status_icon_data_url(status) -> str | None:
    """Inline the website's status icon for ``status`` (``offline`` fallback).

    ``status`` may name a mobile icon (``online_mobile``), which is the same
    phone-shaped art the website uses, so the card and the site agree.
    """
    key = str(status or "").strip().lower()
    if key.endswith("_mobile") and key[: -len("_mobile")] in STATUS_COLORS:
        key = key
    else:
        key = key if key in STATUS_COLORS else "offline"
    if key in _status_icon_cache:
        return _status_icon_cache[key]
    data_url = None
    for directory in _STATUS_ICON_DIRS:
        try:
            raw = (directory / f"status_{key}.png").read_bytes()
        except OSError:
            continue
        if raw:
            data_url = f"data:image/png;base64,{base64.b64encode(raw).decode('ascii')}"
            break
    _status_icon_cache[key] = data_url
    return data_url


def _spotify_mark_path() -> str | None:
    """The Spotify glyph's path data, read from the website asset once."""
    if "path" in _spotify_mark_cache:
        return _spotify_mark_cache["path"]
    path = None
    for candidate in _SPOTIFY_MARK_PATHS:
        try:
            match = re.search(r'\bd="([^"]+)"', candidate.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
        if match:
            path = match.group(1)
            break
    _spotify_mark_cache["path"] = path
    return path


def _spotify_mark(x: float, y: float, size: float) -> str:
    """The Spotify glyph drawn at ``size`` pixels from the top-left ``x, y``."""
    path = _spotify_mark_path()
    if not path:
        return ""
    scale = size / 24
    return (
        f'<path d="{escape(path)}" fill="{SPOTIFY_GREEN}" '
        f'transform="translate({x:.2f} {y:.2f}) scale({scale:.4f})"/>'
    )


def _image_data_url(url, allowed_hosts, cache, ttl) -> str | None:
    """Inline a remote image so the card works inside GitHub's image proxy."""
    raw = str(url or "").strip()
    if not raw:
        return None
    parsed = urlparse(raw)
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in {"http", "https"} or not host.endswith(tuple(allowed_hosts)):
        return None

    cached = cache.get(raw)
    if cached and time.time() - cached[0] < ttl:
        return cached[1]

    data_url = None
    try:
        response = req.get(raw, timeout=6, headers={"User-Agent": "NikoStaffCard/1.0"})
        content_type = str(response.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        if response.ok and content_type.startswith("image/") and 0 < len(response.content) <= _IMAGE_MAX_BYTES:
            data_url = f"data:{content_type};base64,{base64.b64encode(response.content).decode('ascii')}"
    except Exception:
        data_url = None

    # A transient CDN failure is cached briefly so a README refresh cannot turn
    # into a burst of image requests.
    cache[raw] = (time.time() if data_url else time.time() - ttl + 120, data_url)
    return data_url


def activity_art_data_url(url) -> str | None:
    """Inline an activity's artwork (e.g. a Spotify album cover)."""
    return _image_data_url(url, _ALLOWED_ART_HOSTS, _art_cache, _ART_TTL)


def validate_accent(value) -> str | None:
    """Return the normalised accent, ``""`` to reset, or ``None`` when invalid."""
    raw = str(value or "").lstrip("#").strip()
    if not raw:
        return ""
    return raw.upper() if _HEX_RE.match(raw) else None


def _clip(text, limit: int) -> str:
    value = " ".join(str(text or "").split())
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "\u2026"


def _text(x, y, content, *, fill, size, weight=400, family=None, anchor=None,
          spacing=None, opacity=None) -> str:
    family = family or "Plus Jakarta Sans, Segoe UI, Helvetica, Arial, sans-serif"
    attrs = (
        f'x="{x}" y="{y}" fill="{fill}" font-family="{family}" '
        f'font-size="{size}" font-weight="{weight}"'
    )
    if anchor:
        attrs += f' text-anchor="{anchor}"'
    if spacing:
        attrs += f' letter-spacing="{spacing}"'
    if opacity is not None:
        attrs += f' opacity="{opacity}"'
    return f"<text {attrs}>{escape(str(content))}</text>"


def _status_detail(member: dict) -> str | None:
    """The member's custom-status text, or ``None`` when there is none.

    Activities are drawn in their own card below this line, so this line is
    only the custom status.
    """
    custom = member.get("custom_status") or {}
    if not isinstance(custom, dict):
        return None
    return _clip(custom.get("text"), 62) or None


def _primary_activity(member: dict) -> dict | None:
    """The first live activity the card can draw, or ``None``."""
    for activity in member.get("activities") or []:
        if isinstance(activity, dict) and _clip(activity.get("name"), 40):
            return activity
    return None


def _activity_copy(activity: dict) -> tuple[str, str, str]:
    """The label, headline, and supporting line for an activity card."""
    kind = str(activity.get("kind") or "activity").strip().lower()
    activity_type = str(activity.get("type") or "").strip().lower()
    if kind == "spotify":
        return (
            "Listening on Spotify",
            _clip(activity.get("details") or activity.get("name"), 46) or "Spotify",
            _clip(activity.get("state"), 46),
        )
    title = _clip(activity.get("name"), 46) or "Activity"
    extras = [
        line
        for line in (_clip(activity.get("details"), 38), _clip(activity.get("state"), 38))
        if line and line.casefold() != title.casefold()
    ]
    # Keep the two supporting lines distinct without repeating the headline.
    deduped = []
    for line in extras:
        if line.casefold() not in {item.casefold() for item in deduped}:
            deduped.append(line)
    return (
        ACTIVITY_LABELS.get(activity_type, "Activity"),
        title,
        _clip(" \u00b7 ".join(deduped), 46),
    )


def _activity_card(activity: dict, palette: dict, *, top: float | None = None) -> str:
    """The activity card that sits at the bottom of the staff card."""
    kind = str(activity.get("kind") or "activity").strip().lower()
    label, title, subtitle = _activity_copy(activity)
    top = CARD_HEIGHT - 40 if top is None else top
    art = activity_art_data_url(activity.get("image_url"))
    small_art = activity_art_data_url(activity.get("small_image_url")) if art and activity.get("small_image_url") else None
    text_x = 104 if art or kind == "spotify" else 40

    parts = [
        f'<rect x="24" y="{top}" width="{CARD_WIDTH - 48}" height="92" rx="16" '
        f'fill="{palette["chip"]}" stroke="{palette["line"]}" stroke-width="1"/>',
    ]
    if art:
        parts.append(
            '<defs><clipPath id="staff-activity-art">'
            f'<rect x="40" y="{top + 20}" width="52" height="52" rx="12"/>'
            "</clipPath></defs>"
            f'<image href="{escape(art)}" x="40" y="{top + 20}" width="52" height="52" '
            'preserveAspectRatio="xMidYMid slice" clip-path="url(#staff-activity-art)"/>'
        )
        if small_art:
            # Discord overlaps a small badge on the artwork's bottom-right.
            parts.append(
                '<defs><clipPath id="staff-activity-small">'
                f'<circle cx="81" cy="{top + 61}" r="11"/>'
                '</clipPath></defs>'
                f'<circle cx="81" cy="{top + 61}" r="12" fill="{palette["chip"]}"/>'
                f'<image href="{escape(small_art)}" x="70" y="{top + 50}" width="22" height="22" '
                'preserveAspectRatio="xMidYMid slice" clip-path="url(#staff-activity-small)"/>'
            )
    elif kind == "spotify":
        # No cover art in the presence: a green tile with the Spotify glyph.
        parts.append(
            f'<rect x="40" y="{top + 20}" width="52" height="52" rx="12" '
            f'fill="{SPOTIFY_GREEN}" opacity="0.16"/>'
        )
        parts.append(_spotify_mark(40 + 12, top + 20 + 12, 28))

    label_x = text_x
    if kind == "spotify":
        parts.append(_spotify_mark(text_x, top + 13, 14))
        label_x = text_x + 21
    parts.append(_text(label_x, top + 23, label.upper(), fill=palette["dim"], size=8,
                       weight=700, family="Space Mono, ui-monospace, monospace",
                       spacing="1.1"))
    parts.append(_text(text_x, top + 45, title, fill=palette["ink"], size=13, weight=700))
    if subtitle:
        parts.append(_text(text_x, top + 62, subtitle, fill=palette["muted"], size=10.5))
    return "".join(parts)


def _status_notch(mobile: bool, *, centre: tuple[float, float] = (AVATAR_CENTER, AVATAR_CENTER),
                  radius: float = AVATAR_RADIUS) -> tuple[str, float, float]:
    """The hole cut for the status art, and the art's own top-left corner.

    The notch grows out of the avatar's bottom-right corner exactly as the
    website places it, so the art sits the same distance from the picture on
    both axes and the card's background shows through the hole.
    """
    corner_x = centre[0] + radius
    corner_y = centre[1] + radius
    icon_x = corner_x - STATUS_ICON_GAP - STATUS_ICON_SIZE
    icon_y = corner_y - STATUS_ICON_GAP - STATUS_ICON_SIZE
    notch_x = icon_x + STATUS_ICON_SIZE / 2
    notch_y = icon_y + STATUS_ICON_SIZE / 2
    if mobile:
        width = MOBILE_NOTCH_WIDTH
        notch = (
            f'<rect x="{notch_x - width / 2:.2f}" y="{corner_y - STATUS_NOTCH_SIZE:.2f}" '
            f'width="{width:.2f}" height="{STATUS_NOTCH_SIZE:.2f}" '
            f'rx="{width * MOBILE_NOTCH_CORNER:.2f}" fill="black"/>'
        )
    else:
        notch = (
            f'<circle cx="{notch_x:.2f}" cy="{notch_y:.2f}" '
            f'r="{STATUS_NOTCH_SIZE / 2:.2f}" fill="black"/>'
        )
    return notch, icon_x, icon_y


def _avatar_block(avatar_data_url: str | None, decoration_data_url: str | None,
                  accent: str, palette: dict, initials: str,
                  status_hole: str | None = None, *,
                  centre: tuple[float, float] = (AVATAR_CENTER, AVATAR_CENTER),
                  radius: float = AVATAR_RADIUS) -> str:
    """Round avatar, or an initial when there is no image.

    ``status_hole`` is the shape of the status notch. The avatar and its
    decoration share one masked group, as they do on the website, so the notch
    is cut out of both and the card's own background shows through the gap
    instead of a painted disc sitting on top of the art.
    """
    cx, cy = centre
    defs = ('<defs><clipPath id="staff-avatar-clip">'
            f'<circle cx="{cx}" cy="{cy}" r="{radius}"/>'
            "</clipPath>")
    if status_hole:
        defs += ('<mask id="staff-avatar-hole">'
                 f'<rect width="{CARD_WIDTH}" height="{CARD_HEIGHT_WITH_ACTIVITY}" fill="white"/>'
                 f'{status_hole}</mask>')
    defs += "</defs>"

    if not avatar_data_url:
        body = (
            f'<circle cx="{cx}" cy="{cy}" r="{radius}" '
            f'fill="{palette["chip"]}" stroke="{palette["line"]}" stroke-width="2"/>'
            + _text(cx, cy + radius * 0.26, initials, fill=palette["muted"],
                    size=radius * 0.62, weight=800, anchor="middle")
        )
    else:
        body = (
            f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{palette["chip"]}"/>'
            f'<image href="{escape(avatar_data_url)}" x="{cx - radius}" '
            f'y="{cy - radius}" width="{radius * 2}" height="{radius * 2}" '
            'preserveAspectRatio="xMidYMid slice" clip-path="url(#staff-avatar-clip)"/>'
        )
        if decoration_data_url:
            decoration_size = radius * 2 * DECORATION_SCALE
            body += (
                f'<image href="{escape(decoration_data_url)}" '
                f'x="{cx - decoration_size / 2:.2f}" '
                f'y="{cy - decoration_size / 2:.2f}" '
                f'width="{decoration_size:.2f}" height="{decoration_size:.2f}" '
                'preserveAspectRatio="xMidYMid meet"/>'
            )
        body += (
            f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" '
            f'stroke="{accent}" stroke-width="2" opacity="0.55"/>'
        )
    if status_hole:
        body = f'<g mask="url(#staff-avatar-hole)">{body}</g>'
    return defs + body


def badge_data_url(key) -> str | None:
    """Inline one of the site's badge SVGs so the card can draw it inside GitHub."""
    name = str(key or "").strip()
    if not re.fullmatch(r"[a-z0-9_]+", name):
        return None
    if name in _badge_cache:
        return _badge_cache[name]
    data_url = None
    for directory in _BADGE_DIRS:
        try:
            raw = (directory / f"{name}.svg").read_bytes()
        except OSError:
            continue
        if raw:
            data_url = f"data:image/svg+xml;base64,{base64.b64encode(raw).decode('ascii')}"
            break
    _badge_cache[name] = data_url
    return data_url


def profile_banner_data_url(url) -> str | None:
    """Inline a public banner hosted where the card is allowed to fetch images.

    Banners point at arbitrary hosts, and the card only fetches the image hosts
    the rest of it already trusts: anything else falls back to the accent band
    rather than turning this endpoint into a fetch-anything proxy.
    """
    return _image_data_url(url, _ALLOWED_AVATAR_HOSTS, _banner_cache, _AVATAR_TTL)


def _wrap(text, limit: int, max_lines: int) -> list[str]:
    """Split text into at most ``max_lines`` lines, marking a clipped tail."""
    words = " ".join(str(text or "").split()).split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        if current and len(" ".join([*current, word])) > limit:
            lines.append(" ".join(current))
            current = [word]
            if len(lines) == max_lines:
                if lines:
                    lines[-1] = lines[-1][: limit - 1].rstrip() + "\u2026"
                return lines
            continue
        current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines[:max_lines]


def _profile_banner(banner_data_url: str | None, palette: dict, accent: str) -> str:
    """The popup's banner, with the ring the avatar sits in cut out of it."""
    height = PROFILE_BANNER_HEIGHT
    cx, cy = PROFILE_AVATAR_CENTRE
    outline = (
        f'M 21 1 H {CARD_WIDTH - 21} A 20 20 0 0 1 {CARD_WIDTH - 1} 21 '
        f'V {height} H 1 V 21 A 20 20 0 0 1 21 1 Z'
    )
    defs = (
        "<defs>"
        f'<clipPath id="staff-banner-clip"><path d="{outline}"/></clipPath>'
        '<mask id="staff-banner-hole">'
        f'<rect x="1" y="1" width="{CARD_WIDTH - 2}" height="{height - 1}" fill="white"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{PROFILE_AVATAR_RADIUS + 4}" fill="black"/>'
        "</mask>"
        '<linearGradient id="staff-banner-accent" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="{accent}" stop-opacity="0.5"/>'
        f'<stop offset="100%" stop-color="{accent}" stop-opacity="0.1"/>'
        "</linearGradient>"
        "</defs>"
    )
    if banner_data_url:
        art = (f'<image href="{escape(banner_data_url)}" x="0" y="0" width="{CARD_WIDTH}" '
               f'height="{height}" preserveAspectRatio="xMidYMid slice"/>')
    else:
        art = f'<rect width="{CARD_WIDTH}" height="{height}" fill="url(#staff-banner-accent)"/>'
    return (
        defs
        + f'<g clip-path="url(#staff-banner-clip)" mask="url(#staff-banner-hole)">{art}</g>'
        + f'<path d="{outline}" fill="none" stroke="{palette["line"]}" stroke-width="1"/>'
    )


def _badge_row(badges, top: float) -> tuple[str, float]:
    """The member's badges in one row, as the popup draws them."""
    urls = [url for url in (badge_data_url(key) for key in (badges or [])[:8]) if url]
    parts = []
    x = PROFILE_GUTTER
    for url in urls:
        parts.append(f'<image href="{escape(url)}" x="{x}" y="{top:.2f}" '
                     f'width="{PROFILE_BADGE_SIZE}" height="{PROFILE_BADGE_SIZE}"/>')
        x += PROFILE_BADGE_SIZE + 6
    return "".join(parts), top + PROFILE_BADGE_SIZE


def _link_chips(links, palette: dict, top: float) -> tuple[str, float]:
    """The profile's links as one row of chips, clipped to the card's width."""
    parts = []
    x = PROFILE_GUTTER
    for link in (links or [])[:5]:
        label = _clip(link.get("label"), 18)
        if not label:
            continue
        width = int(len(label) * 6.4) + 20
        if x + width > CARD_WIDTH - PROFILE_GUTTER:
            break
        parts.append(f'<rect x="{x:.1f}" y="{top:.2f}" width="{width}" height="24" rx="12" '
                     f'fill="{palette["chip"]}" stroke="{palette["line"]}" stroke-width="1"/>')
        parts.append(_text(x + 10, top + 16, label, fill=palette["muted"], size=9.5,
                           weight=700, family="Space Mono, ui-monospace, monospace"))
        x += width + 8
    return "".join(parts), top + 24


def _profile_card(
    member: dict,
    *,
    palette: dict,
    accent: str,
    name: str,
    handle: str,
    role_label: str,
    live: bool,
    status: str,
    mobile: bool,
    status_icon: str | None,
    activity: dict | None,
    avatar_data_url: str | None,
    avatar_decoration_data_url: str | None,
    banner_data_url: str | None,
) -> str:
    """The full profile style: the popup's banner, avatar, badges and about."""
    centre = PROFILE_AVATAR_CENTRE
    radius = PROFILE_AVATAR_RADIUS
    notch, icon_x, icon_y = (
        _status_notch(mobile, centre=centre, radius=radius) if live else (None, 0.0, 0.0)
    )

    parts = [
        _profile_banner(banner_data_url, palette, accent),
        _avatar_block(avatar_data_url, avatar_decoration_data_url, accent, palette,
                      name[:1].upper(), notch, centre=centre, radius=radius),
    ]
    if live:
        if status_icon:
            parts.append(f'<image href="{escape(status_icon)}" x="{icon_x:.2f}" '
                         f'y="{icon_y:.2f}" width="{STATUS_ICON_SIZE}" '
                         f'height="{STATUS_ICON_SIZE}"/>')
        else:
            parts.append(f'<circle cx="{icon_x + STATUS_ICON_SIZE / 2:.2f}" '
                         f'cy="{icon_y + STATUS_ICON_SIZE / 2:.2f}" r="8" '
                         f'fill="{STATUS_COLORS[status]}"/>')

    # Identity block, in the popup's own order: name, role pill, handle, custom
    # status, badges, then the about section and links.
    y = centre[1] + radius + 34
    parts.append(_text(PROFILE_GUTTER, y, name, fill=palette["ink"], size=26, weight=800))
    pill = f"NIKO STAFF \u00b7 {role_label.upper()}"
    pill_width = int(len(pill) * 6.9) + 20
    pill_x = PROFILE_GUTTER + min(len(name) * 14.0, PROFILE_BODY_WIDTH - pill_width) + 12
    if pill_x + pill_width <= CARD_WIDTH - PROFILE_GUTTER:
        parts.append(f'<rect x="{pill_x:.1f}" y="{y - 16}" width="{pill_width}" height="20" '
                     f'rx="10" fill="{accent}" opacity="0.16"/>')
        parts.append(_text(pill_x + 10, y - 2, pill, fill=accent, size=9, weight=700,
                           family="Space Mono, ui-monospace, monospace", spacing="1.0"))
    y += 22
    if handle:
        parts.append(_text(PROFILE_GUTTER, y, f"@{handle}", fill=palette["dim"], size=12.5,
                           family="Space Mono, ui-monospace, monospace"))
    y += 24

    detail = _status_detail(member) if live else None
    if detail:
        parts.append(_text(PROFILE_GUTTER, y, detail, fill=palette["muted"], size=12))
        y += 22

    badges, badges_bottom = _badge_row(member.get("badges") or [], y - 2)
    if badges:
        parts.append(badges)
        y = badges_bottom + 12

    bio_lines = _wrap(member.get("bio"), PROFILE_BIO_LIMIT, PROFILE_BIO_LINES)
    if bio_lines:
        parts.append(f'<line x1="{PROFILE_GUTTER}" y1="{y:.2f}" '
                     f'x2="{CARD_WIDTH - PROFILE_GUTTER}" y2="{y:.2f}" '
                     f'stroke="{palette["line"]}" stroke-width="1"/>')
        y += 20
        parts.append(_text(PROFILE_GUTTER, y, "ABOUT ME", fill=palette["dim"], size=9.5,
                           weight=700, family="Space Mono, ui-monospace, monospace",
                           spacing="1.2"))
        y += 20
        for line in bio_lines:
            parts.append(_text(PROFILE_GUTTER, y, line, fill=palette["muted"], size=12.5))
            y += 18
        y += 2

    chips, chips_bottom = _link_chips(member.get("public_links") or [], palette, y)
    if chips:
        parts.append(chips)
        y = chips_bottom + 10

    if activity:
        parts.append(_activity_card(activity, palette, top=y))
        y += 92 + 20

    height = int(max(y + 18, PROFILE_BANNER_HEIGHT + 80))
    parts.insert(0, f'<rect x="1" y="1" width="{CARD_WIDTH - 2}" height="{height - 2}" rx="21" '
                    f'fill="none" stroke="{accent}" stroke-width="1.5" opacity="0.42"/>')
    parts.insert(0, f'<rect width="{CARD_WIDTH}" height="{height}" rx="22" '
                    'fill="url(#staff-card-bg)"/>')
    return _document("".join(parts), CARD_WIDTH, height, palette,
                     f"{name} \u2014 Niko staff profile card")


def _hidden_card(palette: dict, accent: str) -> str:
    """Neutral card for a hidden, suspended, or unknown profile."""
    colour = f"#{accent}"
    body = (
        f'<rect width="{CARD_WIDTH}" height="{HIDDEN_CARD_HEIGHT}" rx="22" fill="url(#staff-card-bg)"/>'
        f'<rect x="1" y="1" width="{CARD_WIDTH - 2}" height="{HIDDEN_CARD_HEIGHT - 2}" rx="21" '
        f'fill="none" stroke="{colour}" stroke-width="1.5" opacity="0.45"/>'
        + _text(CARD_WIDTH / 2, 40, "NIKO STAFF", fill=colour, size=11, weight=700,
                family="Space Mono, ui-monospace, monospace", anchor="middle",
                spacing="2.6")
        + _text(CARD_WIDTH / 2, 72, "Niko staff", fill=palette["ink"], size=22,
                weight=800, anchor="middle")
        + _text(CARD_WIDTH / 2, 94, "This profile is not public right now.",
                fill=palette["muted"], size=12, anchor="middle")
    )
    return _document(body, CARD_WIDTH, HIDDEN_CARD_HEIGHT, palette, "Niko staff card")


def _document(body: str, width: int, height: int, palette: dict, label: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="{escape(label)}">'
        "<defs>"
        '<linearGradient id="staff-card-bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{palette["top"]}"/>'
        f'<stop offset="100%" stop-color="{palette["bottom"]}"/>'
        "</linearGradient>"
        "</defs>"
        f"{body}</svg>"
    )


def render_staff_card(
    member: dict | None,
    *,
    theme=None,
    accent=None,
    show_status: bool | None = None,
    style=None,
    avatar_data_url: str | None = None,
    avatar_decoration_data_url: str | None = None,
    banner_data_url: str | None = None,
) -> str:
    """Render one staff card.

    ``member`` comes from the public roster (``_load_staff_rows``). ``None``
    means the profile is hidden, missing, or suspended, and yields a neutral
    card so a README never shows a broken image. ``avatar_data_url`` and
    ``avatar_decoration_data_url`` and ``banner_data_url`` are already-inlined
    images: the route resolves them from the member's own URLs, and all are
    optional. ``style`` picks the layout; the saved setting is the default.
    """
    settings = (member or {}).get("card") or {}
    palette = PALETTES[normalize_theme(theme or settings.get("theme"))]
    resolved_accent = accent_hex(accent or settings.get("accent"))
    accent_colour = f"#{resolved_accent}"

    if not member:
        return _hidden_card(palette, resolved_accent)

    name = _clip(member.get("name"), 28) or "Niko staff"
    handle = _clip(member.get("username"), 24)
    role_label = _clip(member.get("role_label"), 26) or "Staff"
    initials = (str(member.get("name") or "").strip()[:1] or "N").upper()

    live = settings.get("show_status", True) if show_status is None else bool(show_status)
    raw_status = str(member.get("status") or "offline").strip().lower()
    status = raw_status if raw_status in STATUS_COLORS else "offline"
    # A phone-only presence draws the mobile icon, which is a phone rather than
    # a dot: its notch is a narrower rectangle so the cutout hugs that shape.
    mobile = bool(member.get("is_mobile")) and status != "offline"
    status_icon = status_icon_data_url(f"{status}_mobile" if mobile else status) if live else None
    status_hole = None
    status_icon_at = 0.0
    if live:
        status_hole, status_icon_at, _ = _status_notch(mobile)

    activity = _primary_activity(member) if live else None
    if normalize_style(style or settings.get("style")) == "profile":
        return _profile_card(
            member,
            palette=palette,
            accent=accent_colour,
            name=name,
            handle=handle,
            role_label=role_label,
            live=live,
            status=status,
            mobile=mobile,
            status_icon=status_icon,
            activity=activity,
            avatar_data_url=avatar_data_url,
            avatar_decoration_data_url=avatar_decoration_data_url,
            banner_data_url=banner_data_url,
        )

    role_chip = f"NIKO STAFF \u00b7 {role_label.upper()}"
    chip_width = min(320, int(len(role_chip) * 7.2) + 24)

    # The status lives on the profile picture only — the same treatment as the
    # website — so the rest of the card stays free of status chrome.
    avatar = _avatar_block(avatar_data_url, avatar_decoration_data_url, accent_colour,
                           palette, initials, status_hole)
    if live:
        if status_icon:
            # The art is drawn over the hole, not into it: the mask leaves the
            # gap and the card's background, exactly as the website does.
            avatar += (f'<image href="{escape(status_icon)}" x="{status_icon_at:.2f}" '
                       f'y="{status_icon_at:.2f}" width="{STATUS_ICON_SIZE}" '
                       f'height="{STATUS_ICON_SIZE}"/>')
        else:
            avatar += (f'<circle cx="{status_icon_at + STATUS_ICON_SIZE / 2:.2f}" '
                       f'cy="{status_icon_at + STATUS_ICON_SIZE / 2:.2f}" r="8" '
                       f'fill="{STATUS_COLORS[status]}"/>')

    # A live activity grows the card by its own row; nothing else changes.
    activity_markup = _activity_card(activity, palette) if activity else ""
    height = CARD_HEIGHT_WITH_ACTIVITY if activity_markup else CARD_HEIGHT

    parts = [
        f'<rect width="{CARD_WIDTH}" height="{height}" rx="22" fill="url(#staff-card-bg)"/>',
        f'<rect x="1" y="1" width="{CARD_WIDTH - 2}" height="{height - 2}" rx="21" fill="none" '
        f'stroke="{accent_colour}" stroke-width="1.5" opacity="0.42"/>',
        avatar,
        # Role chip
        f'<rect x="148" y="36" width="{chip_width}" height="24" rx="12" '
        f'fill="{accent_colour}" opacity="0.16"/>',
        _text(160, 53, role_chip, fill=accent_colour, size=10, weight=700,
              family="Space Mono, ui-monospace, monospace", spacing="1.1"),
        _text(148, 92, name, fill=palette["ink"], size=25, weight=800),
        _text(148, 114, f"@{handle}" if handle else "Discord team member",
              fill=palette["dim"], size=12,
              family="Space Mono, ui-monospace, monospace"),
    ]

    # A custom status is plain text; the status icon appears on the avatar and
    # nowhere else on the card.
    if live:
        detail = _status_detail(member)
        if detail:
            parts.append(_text(148, 146, detail, fill=palette["muted"], size=11.5))
    parts.append(activity_markup)

    return _document("".join(parts), CARD_WIDTH, height, palette,
                     f"{name} — Niko staff card")


def avatar_data_url(url) -> str | None:
    """Inline a Discord avatar so the card works inside GitHub's image proxy."""
    return _image_data_url(url, _ALLOWED_AVATAR_HOSTS, _avatar_cache, _AVATAR_TTL)
