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


def normalize_theme(value) -> str:
    """``dark`` or ``light``; anything else falls back to the dark card."""
    return "light" if str(value or "").strip().lower() == "light" else "dark"


def accent_hex(value, fallback: str = DEFAULT_ACCENT) -> str:
    """A bare ``RRGGBB`` colour, so it can be dropped into SVG attributes."""
    raw = str(value or "").lstrip("#").strip()
    return raw.upper() if _HEX_RE.match(raw) else fallback


def status_icon_data_url(status) -> str | None:
    """Inline the website's status icon for ``status`` (``offline`` fallback)."""
    key = str(status or "").strip().lower()
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


def _activity_card(activity: dict, palette: dict) -> str:
    """The activity card that sits at the bottom of the staff card."""
    kind = str(activity.get("kind") or "activity").strip().lower()
    label, title, subtitle = _activity_copy(activity)
    top = CARD_HEIGHT - 40
    art = activity_art_data_url(activity.get("image_url"))
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


def _avatar_block(avatar_data_url: str | None, accent: str, palette: dict,
                  initials: str) -> str:
    """Round avatar with a status ring, or an initial when there is no image."""
    if not avatar_data_url:
        return (
            f'<circle cx="84" cy="84" r="42" fill="{palette["chip"]}" '
            f'stroke="{palette["line"]}" stroke-width="2"/>'
            + _text(84, 95, initials, fill=palette["muted"], size=26, weight=800,
                    anchor="middle")
        )
    return (
        '<defs><clipPath id="staff-avatar-clip">'
        '<circle cx="84" cy="84" r="42"/>'
        "</clipPath></defs>"
        f'<circle cx="84" cy="84" r="42" fill="{palette["chip"]}"/>'
        f'<image href="{escape(avatar_data_url)}" x="42" y="42" width="84" '
        'height="84" preserveAspectRatio="xMidYMid slice" '
        'clip-path="url(#staff-avatar-clip)"/>'
        f'<circle cx="84" cy="84" r="42" fill="none" stroke="{accent}" '
        'stroke-width="2" opacity="0.55"/>'
    )


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
    avatar_data_url: str | None = None,
) -> str:
    """Render one staff card.

    ``member`` comes from the public roster (``_load_staff_rows``). ``None``
    means the profile is hidden, missing, or suspended, and yields a neutral
    card so a README never shows a broken image.
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
    status_icon = status_icon_data_url(status) if live else None

    role_chip = f"NIKO STAFF \u00b7 {role_label.upper()}"
    chip_width = min(320, int(len(role_chip) * 7.2) + 24)

    avatar = _avatar_block(avatar_data_url, accent_colour, palette, initials)
    if live:
        # The status lives on the profile picture only — the same treatment as
        # the website — so the rest of the card stays free of status chrome.
        avatar += f'<circle cx="116" cy="116" r="16" fill="{palette["ring"]}"/>'
        if status_icon:
            avatar += f'<image href="{escape(status_icon)}" x="103" y="103" width="26" height="26"/>'
        else:
            avatar += f'<circle cx="116" cy="116" r="8" fill="{STATUS_COLORS[status]}"/>'

    # A live activity grows the card by its own row; nothing else changes.
    activity = _primary_activity(member) if live else None
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
