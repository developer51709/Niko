"""Premium PIL renderers for the ``/fm`` listening cards.

The cards belong to Niko's own family rather than copying Last.fm's site: the
graphite canvas and raised panels come from ``utils.image.economy_card``, so a
listening card sits beside an economy or level card without looking like a
different brand. What is Last.fm's own is the mark in the masthead and the red
that warms the corners of the canvas.

The family is deliberately airier than the Spotify card — a Spotify card is a
cover, with a tinted backdrop and a progress bar; these are listings, so the
space goes into leading, gutters and breathing room between rows instead.

Five shapes exist, and every command composes one of them:

``overview``  the member's library at a glance: identity, scrobble total and
              the three top lists side by side.
``detail``    one artist or album: artwork, the member's own playcount, and
              the global numbers underneath.
``board``     a ranked list — charts, ``whoknows``, crowns and taste — with
              proportion bars so the shape of the ranking is readable at a
              glance.
``nowplaying`` one track, large: what ``/fm`` answers with before anything else.
``recent``    the last few scrobbles, with the now-playing track pinned on top.

Callers pass already-downloaded artwork and avatar bytes (downloaded off-loop,
e.g. with :func:`utils.image.economy_card.fetch_avatar_bytes`). Every renderer
returns a PNG in a ``BytesIO`` for a ``discord.File`` referenced from a
Components-V2 ``MediaGallery``, and the CPU-bound work runs in a thread.
"""

from __future__ import annotations

import asyncio
import re
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from utils.image._font_resolver import draw_text_with_fallback, font_getlength
from utils.image.economy_card import (
    DIM,
    INK,
    MUTED,
    PANEL_BORDER,
    _bold,
    _circle_avatar,
    _format_amount,
    _make_canvas,
    _panel,
    _reg,
    _rounded_mask,
    _strip_discord_emoji,
    _truncate,
)
#: Both cards read the site's own SVGs; the path flattener lives with the
#: Spotify mark, which was the first of the two to need it.
from utils.image.spotify_card import _flatten_svg_path

# ── Palette ────────────────────────────────────────────────────────────────

#: The red of Last.fm's own icon, used for the mark and the ranking accents.
LASTFM_RED = (227, 27, 35)
#: A lifted red for text on graphite — the brand red is too dark to read small.
LASTFM = (216, 100, 92)
LASTFM_SOFT = (232, 146, 138)
LASTFM_WASH = (216, 100, 92, 26)
#: The tracked captions that label a column or a metadata chip.
CAPTION = (150, 156, 166)

PAD = 48

# ── Layout ─────────────────────────────────────────────────────────────────

HEADER_Y = 26
HEADER_MARK = 30
HEADER_TEXT_Y = HEADER_Y + 9

OVERVIEW_W = 980
OVERVIEW_H = 684
OVERVIEW_COLUMNS_Y = 220
OVERVIEW_COLUMNS_H = 306
OVERVIEW_NOW_Y = 554
OVERVIEW_NOW_H = 60

DETAIL_W = 980
DETAIL_H = 480
DETAIL_ART = 264
DETAIL_ART_X = PAD
DETAIL_ART_Y = 112
DETAIL_PLAYS_Y = 238
DETAIL_CHIPS_Y = 314

BOARD_W = 980
BOARD_HEADER_H = 172
BOARD_ROW_H = 84
BOARD_FOOTER_H = 66
#: The rhythm inside one board row. The media (an avatar or an artwork) owns the
#: top of the row and the proportion bar sits below it with a visible gutter — a
#: 46px circle used to reach two pixels past the bar, which read as the bar
#: cutting through the bottom of every listener's profile picture.
BOARD_MEDIA = 44
BOARD_MEDIA_Y = 11
BOARD_MEDIA_STEP = 56
BOARD_NAME_Y = 12
BOARD_SUB_Y = 35
BOARD_RANK_Y = 23
BOARD_BAR_Y = 60
BOARD_BAR_H = 4

RECENT_W = 980
RECENT_HEADER_H = 184
RECENT_ROW_H = 78
RECENT_FOOTER_H = 66

NOW_W = 980
NOW_H = 400
NOW_ART = 236
NOW_ART_X = PAD
NOW_ART_Y = 92
NOW_TEXT_X = NOW_ART_X + NOW_ART + 48

CARD_RADIUS = 28


# ── Brand mark ─────────────────────────────────────────────────────────────
# The cards carry the site's own ``last-fm.svg`` — the official lockup, which
# already contains the wordmark, so the header spells nothing beside it. There
# is no SVG renderer in the bot's runtime (and cairosvg would drag a native
# cairo dependency into a Termux-friendly deploy), so the file's paths are
# flattened and filled here, exactly as the Spotify card does for its mark.

WORDMARK_H = 24

_WORDMARK_SVG = (
    Path(__file__).resolve().parents[2] / "website" / "dist" / "assets" / "brand" / "last-fm.svg",
    Path(__file__).resolve().parents[3] / "web" / "public" / "assets" / "brand" / "last-fm.svg",
)
#: Fallback tile, only used if the site SVG is missing or unreadable.
_LOGO_ASSET = Path(__file__).resolve().parents[2] / "assets" / "brand" / "lastfm-mark.png"
_LOGO_CACHE: dict[int, Image.Image] = {}
_WORDMARK_CACHE: dict[tuple[int, tuple[int, int, int]], Image.Image] = {}
_WORDMARK_GEOMETRY: list | tuple | None = None
_WORDMARK_READ = False

_PATH_DATA_RE = re.compile(r'<path[^>]*\bd="([^"]+)"')
_MATRIX_RE = re.compile(
    r"matrix\(\s*(-?[\d.]+(?:e-?\d+)?)[ ,]+(-?[\d.]+(?:e-?\d+)?)[ ,]+"
    r"(-?[\d.]+(?:e-?\d+)?)[ ,]+(-?[\d.]+(?:e-?\d+)?)[ ,]+"
    r"(-?[\d.]+(?:e-?\d+)?)[ ,]+(-?[\d.]+(?:e-?\d+)?)\s*\)",
    re.IGNORECASE,
)


def _wordmark_geometry() -> tuple[list, float, float] | None:
    """The lockup's paths, transformed and shifted to start at ``(0, 0)``.

    Read once: the file never changes under a running bot, and parsing it on
    every card would cost more than the rest of the header together.
    """
    global _WORDMARK_GEOMETRY, _WORDMARK_READ
    if _WORDMARK_READ:
        return _WORDMARK_GEOMETRY
    _WORDMARK_READ = True

    source = None
    for candidate in _WORDMARK_SVG:
        try:
            source = candidate.read_text(encoding="utf-8")
        except OSError:
            continue
        break
    if source is None:
        return None

    match = _MATRIX_RE.search(source)
    a, b, c, d, e, f = (float(value) for value in match.groups()) if match else (1, 0, 0, 1, 0, 0)

    subpaths: list[list[tuple[float, float]]] = []
    try:
        for data in _PATH_DATA_RE.findall(source):
            for points in _flatten_svg_path(data):
                subpaths.append([(a * x + c * y + e, b * x + d * y + f) for x, y in points])
    except (TypeError, ValueError):
        return None
    if not subpaths:
        return None

    left = min(x for points in subpaths for x, _ in points)
    top = min(y for points in subpaths for _, y in points)
    right = max(x for points in subpaths for x, _ in points)
    bottom = max(y for points in subpaths for _, y in points)
    if right <= left or bottom <= top:
        return None

    _WORDMARK_GEOMETRY = (
        [[(x - left, y - top) for x, y in points] for points in subpaths],
        right - left,
        bottom - top,
    )
    return _WORDMARK_GEOMETRY


def _wordmark(height: int = WORDMARK_H, colour: tuple[int, int, int] = INK) -> Image.Image | None:
    """The site's Last.fm lockup at *height* pixels, in one flat colour.

    Drawn in the card's ink rather than the brand red: the lockup is thin at
    header size, and red on graphite does not clear a readable contrast. The
    red stays where it can be loud — the playing dot, the ranking accents and
    the warmth in the canvas corners.
    """
    key = (height, tuple(colour))
    cached = _WORDMARK_CACHE.get(key)
    if cached is not None:
        return cached

    geometry = _wordmark_geometry()
    if geometry is None:
        return None
    subpaths, box_w, box_h = geometry

    scale = height / box_h
    width = max(1, round(box_w * scale))
    supersample = 3
    mask = Image.new("L", (width * supersample, height * supersample), 0)
    draw = ImageDraw.Draw(mask)
    factor = scale * supersample
    for points in subpaths:
        if len(points) < 3:
            continue
        draw.polygon([(x * factor, y * factor) for x, y in points], fill=255)
    mask = mask.resize((width, height), Image.LANCZOS)

    mark = Image.new("RGBA", (width, height), (*colour, 255))
    mark.putalpha(mask)
    _WORDMARK_CACHE[key] = mark
    return mark


def _drawn_logo(size: int) -> Image.Image:
    """Fallback tile for an install without the bundled mark."""
    tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tile)
    draw.rounded_rectangle(
        [0, 0, size - 1, size - 1],
        radius=max(2, int(size * 0.26)),
        fill=(*LASTFM_RED, 255),
    )
    centre = size / 2
    for scale, stroke in ((0.74, 0.10), (0.54, 0.085), (0.34, 0.07)):
        radius = size * scale / 2
        draw.arc(
            [centre - radius, centre - radius, centre + radius, centre + radius],
            start=200,
            end=340,
            fill=(255, 255, 255, 255),
            width=max(1, int(round(size * stroke))),
        )
    return tile


def _logo(size: int) -> Image.Image:
    """The bundled icon tile at *size* pixels, cached per size.

    Only the fallback header uses this: the cards themselves carry the
    wordmark, which is the site's own lockup.
    """
    cached = _LOGO_CACHE.get(size)
    if cached is not None:
        return cached

    mark = None
    if _LOGO_ASSET.is_file():
        try:
            with Image.open(_LOGO_ASSET) as source:
                mark = source.convert("RGBA").resize((size, size), Image.LANCZOS)
        except Exception:
            mark = None
    if mark is None:
        mark = _drawn_logo(size)
    _LOGO_CACHE[size] = mark
    return mark


def _masthead(canvas: Image.Image, label: str = "") -> float:
    """The brand lockup every card opens with; returns where it ends.

    The lockup is the downloaded wordmark, which already carries the name, so
    nothing is spelled beside it. *label* is the card's own section —
    ``OVERVIEW``, ``ARTIST``, ``CROWNS`` — set in tracked caps after a dot, so
    the header says what the card is without stealing focus from the numbers.
    """
    mark = _wordmark()
    if mark is not None:
        canvas.alpha_composite(mark, (PAD, HEADER_Y + 3))
        x = PAD + mark.width
    else:
        # An install without the site asset still gets a recognisable header.
        canvas.alpha_composite(_logo(HEADER_MARK), (PAD, HEADER_Y))
        x = PAD + HEADER_MARK

    draw = ImageDraw.Draw(canvas)
    value = _clean(label).upper()
    if value:
        draw.ellipse([x + 16, HEADER_TEXT_Y + 6, x + 19, HEADER_TEXT_Y + 9], fill=(255, 255, 255, 70))
        x += 30
        x += _tracked(draw, (x, HEADER_TEXT_Y), value, _bold(12), LASTFM_SOFT, 3.0)
    return x


def _top_right(
    draw: ImageDraw.ImageDraw,
    width: int,
    text: str,
    *,
    fill=DIM,
    y: int = HEADER_TEXT_Y,
) -> int:
    """Draw muted metadata in the header's right corner; return its width."""
    value = _clean(text)
    if not value:
        return 0
    font = _reg(12)
    value_w = int(font_getlength(font, value))
    draw_text_with_fallback(draw, (width - PAD - value_w, y), value, size=12, bold=False, fill=fill)
    return value_w


# ── Helpers ────────────────────────────────────────────────────────────────

def _clean(text: str | None) -> str:
    return _strip_discord_emoji(str(text or "")).strip()


def _tracked(draw: ImageDraw.ImageDraw, xy, text: str, font, fill, spacing: float = 3.0) -> float:
    """Draw small-caps style text with letter spacing; return its width."""
    x, y = xy
    start = x
    for index, char in enumerate(text):
        draw.text((x, y), char, font=font, fill=fill)
        x += font_getlength(font, char) + (spacing if index < len(text) - 1 else 0)
    return x - start


def _tracked_width(font, text: str, spacing: float = 3.0) -> float:
    if not text:
        return 0.0
    return sum(font_getlength(font, char) for char in text) + spacing * (len(text) - 1)


def _text(draw, xy, text, *, size, bold, fill, max_w: int | None = None) -> None:
    """Draw one line, clipped to ``max_w`` when given."""
    value = _clean(text)
    if max_w is not None:
        value = _truncate(value, _bold(size) if bold else _reg(size), max_w)
    draw_text_with_fallback(draw, xy, value, size=size, bold=bold, fill=fill)


def _wrap(text: str, *, size: int, bold: bool, max_w: int, lines: int = 2) -> list[str]:
    """Wrap a title onto at most *lines* lines, ellipsising the last one."""
    font = _bold(size) if bold else _reg(size)
    words = _clean(text).split()
    if not words:
        return []
    out: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if font_getlength(font, candidate) <= max_w:
            current = candidate
            continue
        if len(out) + 1 >= lines:
            current = f"{current} {word}"
            break
        out.append(current)
        current = word
    out.append(_truncate(current, font, max_w))
    return out[:lines]


_GLOW_SCALE = 4


def _glow(width: int, height: int) -> Image.Image:
    """The red corner warmth, built small: this would be the slow part.

    Blurring a full-size layer costs more than the rest of the card put
    together, and the result is identical at a quarter of the resolution, so
    the layer is drawn tiny, blurred, and scaled back up — about 8 ms, which is
    cheaper than holding a full-size layer per card height in memory.
    """
    small = (max(1, width // _GLOW_SCALE), max(1, height // _GLOW_SCALE))
    layer = Image.new("RGBA", small, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.ellipse(
        [small[0] - 116, -76, small[0] + 30, 76],
        fill=(*LASTFM_RED, 58),
    )
    draw.ellipse([-80, small[1] - 76, 86, small[1] + 56], fill=(*LASTFM_RED, 34))
    layer = layer.filter(ImageFilter.GaussianBlur(30))
    layer = layer.resize((width, height), Image.BILINEAR)
    layer.putalpha(
        ImageChops.multiply(layer.getchannel("A"), _rounded_mask((width, height), CARD_RADIUS))
    )
    return layer


def _canvas(width: int, height: int) -> Image.Image:
    """The theme canvas plus a soft red warmth in two corners.

    It is a tint rather than a backdrop: nothing on the card is blurred over
    artwork, which is what keeps these cards a different family from the
    Spotify card, and it keeps the panels readable on any album cover.
    """
    canvas = _make_canvas(width, height, radius=CARD_RADIUS)
    canvas.alpha_composite(_glow(width, height))
    return canvas


def _artwork(raw: bytes | None, size: int, radius: int = 16) -> Image.Image:
    """Square artwork with rounded corners, or a themed empty sleeve."""
    image = None
    if raw:
        try:
            image = Image.open(BytesIO(raw)).convert("RGBA")
        except Exception:
            image = None

    if image is None:
        tile = Image.new("RGBA", (size, size), (26, 28, 32, 255))
        draw = ImageDraw.Draw(tile)
        # A faint vinyl groove reads as "no cover" without shouting.
        for inset in (size // 5, size // 3, size * 5 // 12):
            draw.ellipse(
                [inset, inset, size - inset, size - inset],
                outline=(255, 255, 255, 20),
                width=1,
            )
        draw.ellipse(
            [size // 2 - 5, size // 2 - 5, size // 2 + 5, size // 2 + 5],
            fill=(*LASTFM, 150),
        )
        image = tile
    else:
        image = image.resize((size, size), Image.LANCZOS)

    image.putalpha(_rounded_mask((size, size), radius))
    return image


def _chip(canvas: Image.Image, x: int, y: int, label: str, value: str, *, accent=INK) -> int:
    """A small stat chip (``12,480`` / ``LISTENERS``). Returns the width drawn."""
    label_font = _reg(11)
    value_font = _bold(16)
    label_w = _tracked_width(label_font, label.upper())
    value_w = font_getlength(value_font, value)
    width = int(max(label_w, value_w)) + 40
    height = 66

    chip = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(chip)
    draw.rounded_rectangle(
        [0, 0, width - 1, height - 1],
        radius=14,
        fill=(255, 255, 255, 10),
        outline=PANEL_BORDER,
        width=1,
    )
    _tracked(draw, (20, 13), label.upper(), label_font, CAPTION)
    draw_text_with_fallback(draw, (20, 33), value, size=16, bold=True, fill=accent)
    canvas.alpha_composite(chip, (x, y))
    return width


def _period_pill(canvas: Image.Image, label: str) -> None:
    font = _bold(11)
    text_w = int(_tracked_width(font, label.upper()))
    width, height = text_w + 44, 30
    x, y = OVERVIEW_W - width - PAD, HEADER_Y

    pill = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(pill)
    draw.rounded_rectangle(
        [0, 0, width - 1, height - 1],
        radius=height // 2,
        fill=LASTFM_WASH,
        outline=(*LASTFM, 90),
        width=1,
    )
    _tracked(draw, (22, 8), label.upper(), font, LASTFM_SOFT)
    canvas.alpha_composite(pill, (x, y))


def _now_dot(draw: ImageDraw.ImageDraw, x: int, y: int, r: int = 4) -> None:
    draw.ellipse([x, y, x + r * 2, y + r * 2], fill=LASTFM)


def _footer(draw: ImageDraw.ImageDraw, width: int, y: int, text: str, right: str = "NIKO") -> None:
    draw.line([(PAD, y - 16), (width - PAD, y - 16)], fill=(255, 255, 255, 26), width=1)
    if text:
        _text(draw, (PAD, y), text, size=12, bold=False, fill=DIM, max_w=width - PAD * 2 - 200)
    if right:
        font = _reg(12)
        right_w = int(font_getlength(font, right))
        draw_text_with_fallback(draw, (width - PAD - right_w, y), right, size=12, bold=False, fill=DIM)


# ── Overview ───────────────────────────────────────────────────────────────

def _column(
    canvas: Image.Image,
    x: int,
    y: int,
    w: int,
    h: int,
    title: str,
    rows: list[dict],
    empty: str,
) -> None:
    """One top-list column: a titled panel with ranked, counted rows."""
    _panel(canvas, x, y, w, h, radius=20)
    draw = ImageDraw.Draw(canvas)
    _tracked(draw, (x + 24, y + 24), title.upper(), _bold(11), LASTFM_SOFT)

    if not rows:
        _text(draw, (x + 24, y + 66), empty, size=13, bold=False, fill=DIM, max_w=w - 48)
        return

    row_h = 50
    top = y + 56
    for index, entry in enumerate(rows):
        ry = top + index * row_h
        if index:
            draw.line([(x + 24, ry - 8), (x + w - 24, ry - 8)], fill=(255, 255, 255, 14), width=1)

        rank = str(entry.get("rank") or index + 1)
        draw_text_with_fallback(draw, (x + 24, ry + 2), rank, size=12, bold=False, fill=DIM)

        count = str(entry.get("value") or "")
        count_font = _bold(14)
        count_w = int(font_getlength(count_font, count))
        _text(
            draw,
            (x + w - 24 - count_w, ry),
            count,
            size=14,
            bold=True,
            fill=LASTFM_SOFT if entry.get("highlight") else MUTED,
        )

        name_w = w - 48 - count_w - 42
        _text(draw, (x + 52, ry - 2), entry.get("name"), size=15, bold=True, fill=INK, max_w=name_w)
        if entry.get("subtitle"):
            _text(draw, (x + 52, ry + 21), entry.get("subtitle"), size=12, bold=False, fill=DIM, max_w=name_w)


def _render_overview_sync(
    avatar_bytes: bytes | None,
    display_name: str,
    handle: str,
    period: str,
    scrobbles: int,
    artists: list[dict],
    albums: list[dict],
    tracks: list[dict],
    member_since: str,
    now_playing: dict | None,
    footer: str,
    empty_text: str,
) -> BytesIO:
    canvas = _canvas(OVERVIEW_W, OVERVIEW_H)
    _masthead(canvas, "Overview")
    _period_pill(canvas, period)
    draw = ImageDraw.Draw(canvas)

    # ── Identity ──
    avatar = _circle_avatar(avatar_bytes, 94)
    canvas.alpha_composite(avatar, (PAD, 96))
    draw = ImageDraw.Draw(canvas)
    # A hairline of brand red on the avatar's own edge, so the identity block
    # still starts exactly on the card's gutter.
    draw.ellipse([PAD, 96, PAD + 93, 96 + 93], outline=(*LASTFM, 200), width=2)

    _text(draw, (PAD + 122, 100), display_name, size=30, bold=True, fill=INK, max_w=470)
    _text(draw, (PAD + 122, 144), handle, size=14, bold=False, fill=MUTED, max_w=470)
    if member_since:
        _text(draw, (PAD + 122, 168), member_since, size=12, bold=False, fill=DIM, max_w=470)

    # ── Scrobble total, right aligned ──
    total = _format_amount(int(scrobbles or 0))
    total_font = _bold(44)
    total_w = int(font_getlength(total_font, total))
    draw_text_with_fallback(
        draw, (OVERVIEW_W - PAD - total_w, 92), total, size=44, bold=True, fill=INK
    )
    label_font = _bold(11)
    label_w = int(_tracked_width(label_font, "SCROBBLES"))
    _tracked(draw, (OVERVIEW_W - PAD - label_w, 148), "SCROBBLES", label_font, CAPTION)

    # ── Three top lists ──
    gap = 20
    column_w = (OVERVIEW_W - PAD * 2 - gap * 2) // 3
    for index, (title, rows) in enumerate(
        (("Top artists", artists), ("Top albums", albums), ("Top tracks", tracks))
    ):
        _column(
            canvas,
            PAD + index * (column_w + gap),
            OVERVIEW_COLUMNS_Y,
            column_w,
            OVERVIEW_COLUMNS_H,
            title,
            rows,
            empty_text,
        )

    # ── Now playing strip ──
    _panel(canvas, PAD, OVERVIEW_NOW_Y, OVERVIEW_W - PAD * 2, OVERVIEW_NOW_H, radius=16)
    draw = ImageDraw.Draw(canvas)
    if now_playing:
        _now_dot(draw, PAD + 26, OVERVIEW_NOW_Y + 24)
        _text(
            draw,
            (PAD + 44, OVERVIEW_NOW_Y + 11),
            now_playing.get("title"),
            size=16,
            bold=True,
            fill=INK,
            max_w=OVERVIEW_W - PAD * 2 - 300,
        )
        _text(
            draw,
            (PAD + 44, OVERVIEW_NOW_Y + 34),
            now_playing.get("artist"),
            size=12,
            bold=False,
            fill=MUTED,
            max_w=OVERVIEW_W - PAD * 2 - 300,
        )
        status_w = int(_tracked_width(_bold(11), "NOW PLAYING"))
        _tracked(
            draw,
            (OVERVIEW_W - PAD - 26 - status_w, OVERVIEW_NOW_Y + 22),
            "NOW PLAYING",
            _bold(11),
            LASTFM_SOFT,
        )
    else:
        _text(
            draw,
            (PAD + 26, OVERVIEW_NOW_Y + 21),
            empty_text,
            size=13,
            bold=False,
            fill=DIM,
        )

    _footer(draw, OVERVIEW_W, OVERVIEW_H - 40, footer)

    out = BytesIO()
    canvas.save(out, format="PNG", optimize=True)
    out.seek(0)
    return out


async def render_overview_card(
    *,
    avatar_bytes: bytes | None,
    display_name: str,
    handle: str,
    period: str,
    scrobbles: int,
    artists: list[dict],
    albums: list[dict],
    tracks: list[dict],
    member_since: str = "",
    now_playing: dict | None = None,
    footer: str = "",
    empty_text: str = "Nothing scrobbled in this period yet.",
) -> BytesIO:
    """The ``/fm overview`` card."""
    return await asyncio.to_thread(
        _render_overview_sync,
        avatar_bytes,
        display_name,
        handle,
        period,
        scrobbles,
        artists,
        albums,
        tracks,
        member_since,
        now_playing,
        footer,
        empty_text,
    )


# ── Detail (one artist or album) ───────────────────────────────────────────

def _render_detail_sync(
    image_bytes: bytes | None,
    kind: str,
    title: str,
    subtitle: str,
    playcount: int,
    chips: list[tuple[str, str]],
    footer: str,
    plays_label: str,
) -> BytesIO:
    canvas = _canvas(DETAIL_W, DETAIL_H)
    _masthead(canvas, kind)

    art = _artwork(image_bytes, DETAIL_ART, radius=20)
    canvas.alpha_composite(art, (DETAIL_ART_X, DETAIL_ART_Y))

    text_x = DETAIL_ART_X + DETAIL_ART + 44
    text_w = DETAIL_W - text_x - PAD
    draw = ImageDraw.Draw(canvas)

    # The title bands are fixed rather than flowing, so a two-line title can
    # never push the playcount into the row of numbers underneath it.
    title_y = DETAIL_ART_Y + 4
    lines = _wrap(title, size=38, bold=True, max_w=text_w, lines=2)
    for index, line in enumerate(lines):
        _text(draw, (text_x, title_y + index * 46), line, size=38, bold=True, fill=INK)
    y = title_y + len(lines) * 46 + 6
    if subtitle:
        _text(draw, (text_x, y), subtitle, size=17, bold=False, fill=MUTED, max_w=text_w)
        y += 32

    # The member's own number is the reason this card exists, so it is the
    # largest thing on it after the title.
    if playcount is not None:
        play_y = max(DETAIL_PLAYS_Y, y + 8)
        play_text = _format_amount(int(playcount))
        draw_text_with_fallback(
            draw, (text_x, play_y), play_text, size=46, bold=True, fill=LASTFM_SOFT
        )
        value_w = int(font_getlength(_bold(46), play_text))
        _tracked(draw, (text_x + value_w + 14, play_y + 30), plays_label.upper(), _bold(11), CAPTION)

    # ── Global chips ──
    chip_x = text_x
    for label, value in chips[:3]:
        if not value:
            continue
        chip_x += _chip(canvas, chip_x, DETAIL_CHIPS_Y, label, value) + 12
    draw = ImageDraw.Draw(canvas)

    _footer(draw, DETAIL_W, DETAIL_H - 40, footer)

    out = BytesIO()
    canvas.save(out, format="PNG", optimize=True)
    out.seek(0)
    return out


async def render_detail_card(
    *,
    image_bytes: bytes | None,
    kind: str,
    title: str,
    subtitle: str = "",
    playcount: int | None = None,
    chips: list[tuple[str, str]] | None = None,
    footer: str = "",
    plays_label: str = "plays",
) -> BytesIO:
    """An artist or album card with the member's playcount as the hero number."""
    return await asyncio.to_thread(
        _render_detail_sync,
        image_bytes,
        kind,
        title,
        subtitle,
        playcount,
        list(chips or []),
        footer,
        plays_label,
    )


# ── Boards (charts, whoknows, crowns, taste) ───────────────────────────────

def board_height(rows: int) -> int:
    """Height of a board card showing *rows* entries."""
    return BOARD_HEADER_H + max(1, int(rows)) * BOARD_ROW_H + BOARD_FOOTER_H


def _render_board_sync(
    title: str,
    subtitle: str,
    entries: list[dict],
    footer: str,
    empty_text: str,
    value_label: str,
    show_images: bool,
) -> BytesIO:
    rows = max(1, len(entries))
    height = board_height(rows)
    canvas = _canvas(BOARD_W, height)
    _masthead(canvas, value_label)
    draw = ImageDraw.Draw(canvas)

    for line in _wrap(title, size=32, bold=True, max_w=BOARD_W - PAD * 2, lines=1):
        _text(draw, (PAD, 66), line, size=32, bold=True, fill=INK)
    if subtitle:
        _text(draw, (PAD, 110), subtitle, size=13, bold=False, fill=MUTED, max_w=BOARD_W - PAD * 2)

    top = BOARD_HEADER_H
    if not entries:
        _panel(canvas, PAD, top, BOARD_W - PAD * 2, BOARD_ROW_H - 10, radius=18)
        draw = ImageDraw.Draw(canvas)
        _text(draw, (PAD + 26, top + 28), empty_text, size=14, bold=False, fill=DIM, max_w=BOARD_W - PAD * 2 - 52)
    else:
        largest = max(
            (float(entry.get("bar") or entry.get("value") or 0) for entry in entries),
            default=0.0,
        )
        track_x = PAD + 26
        track_w = BOARD_W - PAD * 2 - 52
        for index, entry in enumerate(entries):
            row_y = top + index * BOARD_ROW_H
            _panel(canvas, PAD, row_y, BOARD_W - PAD * 2, BOARD_ROW_H - 10, radius=18)
            draw = ImageDraw.Draw(canvas)

            rank = str(entry.get("rank") or index + 1)
            rank_font = _bold(20)
            rank_w = int(font_getlength(rank_font, rank))
            draw_text_with_fallback(
                draw,
                (PAD + 30 + (26 - rank_w) // 2, row_y + BOARD_RANK_Y),
                rank,
                size=20,
                bold=True,
                fill=LASTFM_SOFT if index < 3 else DIM,
            )

            x = PAD + 74
            media_y = row_y + BOARD_MEDIA_Y
            artwork = entry.get("image")
            avatar = entry.get("avatar")
            if show_images and artwork:
                thumb = _artwork(artwork, BOARD_MEDIA, radius=10)
                canvas.alpha_composite(thumb, (x, media_y))
                x += BOARD_MEDIA_STEP
            elif avatar:
                thumb = _circle_avatar(avatar, BOARD_MEDIA)
                canvas.alpha_composite(thumb, (x, media_y))
                # A hairline ring keeps a photo from bleeding into the panel and
                # makes the circle read as framed rather than cut out.
                ring = ImageDraw.Draw(canvas)
                ring.ellipse(
                    [x - 1, media_y - 1, x + BOARD_MEDIA, media_y + BOARD_MEDIA],
                    outline=PANEL_BORDER,
                    width=2,
                )
                draw = ImageDraw.Draw(canvas)
                x += BOARD_MEDIA_STEP

            value = str(entry.get("value") if entry.get("value") is not None else "")
            value_font = _bold(18)
            value_w = int(font_getlength(value_font, value))

            name_w = BOARD_W - PAD - 26 - value_w - 34 - x
            _text(draw, (x, row_y + BOARD_NAME_Y), entry.get("name"), size=18, bold=True, fill=INK, max_w=max(90, name_w))
            if entry.get("subtitle"):
                _text(
                    draw,
                    (x, row_y + BOARD_SUB_Y),
                    entry.get("subtitle"),
                    size=12,
                    bold=False,
                    fill=DIM,
                    max_w=max(90, name_w),
                )

            # The count shares the name's baseline, so the row's right edge reads
            # as one line instead of a number floating between two.
            draw_text_with_fallback(
                draw,
                (BOARD_W - PAD - 26 - value_w, row_y + BOARD_NAME_Y),
                value,
                size=18,
                bold=True,
                fill=LASTFM_SOFT if index < 3 else MUTED,
            )

            # Proportion bar: the ranking's shape without a chart library. The
            # track runs the full width so the length of the bar is comparable
            # between rows instead of starting wherever the name ends.
            try:
                fraction = float(entry.get("bar") or entry.get("value") or 0) / largest if largest else 0.0
            except (TypeError, ValueError):
                fraction = 0.0
            fraction = max(0.0, min(1.0, fraction))
            bar_y = row_y + BOARD_BAR_Y
            draw.rounded_rectangle(
                [track_x, bar_y, track_x + track_w, bar_y + BOARD_BAR_H],
                radius=2,
                fill=(255, 255, 255, 16),
            )
            if fraction > 0:
                draw.rounded_rectangle(
                    [track_x, bar_y, track_x + max(3, int(track_w * fraction)), bar_y + BOARD_BAR_H],
                    radius=2,
                    fill=(*LASTFM, 175 if index < 3 else 110),
                )

    draw = ImageDraw.Draw(canvas)
    _footer(draw, BOARD_W, height - 40, footer)

    out = BytesIO()
    canvas.save(out, format="PNG", optimize=True)
    out.seek(0)
    return out


async def render_board_card(
    *,
    title: str,
    subtitle: str = "",
    entries: list[dict],
    footer: str = "",
    empty_text: str = "Nothing to show yet.",
    value_label: str = "",
    show_images: bool = True,
) -> BytesIO:
    """A ranked board card. Entries carry ``name``, ``value`` and optionally
    ``subtitle``, ``rank``, ``bar``, ``image`` (artwork) or ``avatar`` bytes."""
    return await asyncio.to_thread(
        _render_board_sync,
        title,
        subtitle,
        entries,
        footer,
        empty_text,
        value_label,
        show_images,
    )


# ── Recent scrobbles ───────────────────────────────────────────────────────

def _render_recent_sync(
    avatar_bytes: bytes | None,
    display_name: str,
    handle: str,
    entries: list[dict],
    footer: str,
    empty_text: str,
    now_label: str,
) -> BytesIO:
    rows = max(1, len(entries))
    height = RECENT_HEADER_H + rows * RECENT_ROW_H + RECENT_FOOTER_H
    canvas = _canvas(RECENT_W, height)
    _masthead(canvas, "Recent")
    draw = ImageDraw.Draw(canvas)

    avatar = _circle_avatar(avatar_bytes, 70)
    canvas.alpha_composite(avatar, (PAD, 80))
    draw = ImageDraw.Draw(canvas)
    _text(draw, (PAD + 88, 84), display_name, size=27, bold=True, fill=INK, max_w=RECENT_W - PAD * 2 - 88)
    _text(draw, (PAD + 88, 120), handle, size=13, bold=False, fill=MUTED, max_w=RECENT_W - PAD * 2 - 88)

    top = RECENT_HEADER_H
    if not entries:
        _panel(canvas, PAD, top, RECENT_W - PAD * 2, RECENT_ROW_H - 10, radius=16)
        draw = ImageDraw.Draw(canvas)
        _text(draw, (PAD + 26, top + 24), empty_text, size=14, bold=False, fill=DIM, max_w=RECENT_W - PAD * 2 - 52)
    for index, entry in enumerate(entries):
        row_y = top + index * RECENT_ROW_H
        _panel(canvas, PAD, row_y, RECENT_W - PAD * 2, RECENT_ROW_H - 10, radius=16)
        draw = ImageDraw.Draw(canvas)

        thumb = _artwork(entry.get("image"), 48, radius=10)
        canvas.alpha_composite(thumb, (PAD + 16, row_y + 10))
        x = PAD + 78
        draw = ImageDraw.Draw(canvas)

        live = bool(entry.get("now_playing"))
        if live:
            _now_dot(draw, x, row_y + 12, 3)
            _tracked(draw, (x + 13, row_y + 8), now_label.upper(), _bold(10), LASTFM_SOFT)

        when = str(entry.get("when") or "")
        when_font = _reg(12)
        when_w = int(font_getlength(when_font, when))
        draw_text_with_fallback(
            draw, (RECENT_W - PAD - 22 - when_w, row_y + 16), when, size=12, bold=False, fill=DIM
        )

        name_w = RECENT_W - PAD - 22 - when_w - 26 - x
        title_y = row_y + (24 if live else 14)
        _text(draw, (x, title_y), entry.get("title"), size=16, bold=True, fill=INK, max_w=max(100, name_w))
        subtitle = entry.get("subtitle") or ""
        if subtitle:
            _text(draw, (x, title_y + 24), subtitle, size=12, bold=False, fill=MUTED, max_w=max(100, name_w))

    draw = ImageDraw.Draw(canvas)
    _footer(draw, RECENT_W, height - 40, footer)

    out = BytesIO()
    canvas.save(out, format="PNG", optimize=True)
    out.seek(0)
    return out


async def render_recent_card(
    *,
    avatar_bytes: bytes | None,
    display_name: str,
    handle: str,
    entries: list[dict],
    footer: str = "",
    empty_text: str = "No scrobbles yet.",
    now_label: str = "Now playing",
) -> BytesIO:
    """The recent-scrobbles card."""
    return await asyncio.to_thread(
        _render_recent_sync,
        avatar_bytes,
        display_name,
        handle,
        entries,
        footer,
        empty_text,
        now_label,
    )


# ── Now playing ────────────────────────────────────────────────────────────

def _render_now_playing_sync(
    image_bytes: bytes | None,
    title: str,
    artist: str,
    album: str,
    live: bool,
    handle: str,
    footer: str,
    empty_text: str,
    now_label: str,
    last_label: str,
) -> BytesIO:
    """One track, drawn large — the answer ``/fm`` gives before anything else.

    Nothing playing is not an error: the same card shows the last scrobble with
    a quieter label, so the command still answers with music instead of an
    apology.
    """
    canvas = _canvas(NOW_W, NOW_H)
    _masthead(canvas, "")
    draw = ImageDraw.Draw(canvas)
    if handle:
        _top_right(draw, NOW_W, f"last.fm/user/{handle}")

    if not _clean(title):
        _panel(canvas, PAD, NOW_ART_Y, NOW_W - PAD * 2, NOW_ART, radius=20)
        draw = ImageDraw.Draw(canvas)
        _text(
            draw,
            (PAD + 32, NOW_ART_Y + NOW_ART // 2 - 10),
            empty_text,
            size=15,
            bold=False,
            fill=DIM,
            max_w=NOW_W - PAD * 2 - 64,
        )
        _footer(draw, NOW_W, NOW_H - 40, footer)
        out = BytesIO()
        canvas.save(out, format="PNG", optimize=True)
        out.seek(0)
        return out

    art = _artwork(image_bytes, NOW_ART, radius=20)
    canvas.alpha_composite(art, (NOW_ART_X, NOW_ART_Y))
    draw = ImageDraw.Draw(canvas)

    max_w = NOW_W - PAD - NOW_TEXT_X
    label = (now_label if live else last_label).upper()
    if live:
        _now_dot(draw, NOW_TEXT_X, 104, 4)
        _tracked(draw, (NOW_TEXT_X + 17, 100), label, _bold(11), LASTFM_SOFT)
    else:
        _tracked(draw, (NOW_TEXT_X, 100), label, _bold(11), CAPTION)

    lines = _wrap(title, size=40, bold=True, max_w=max_w, lines=2)
    for index, line in enumerate(lines):
        _text(draw, (NOW_TEXT_X, 132 + index * 52), line, size=40, bold=True, fill=INK, max_w=max_w)
    y = 132 + len(lines) * 52 + 6
    if artist:
        _text(draw, (NOW_TEXT_X, y), artist, size=21, bold=False, fill=MUTED, max_w=max_w)
        y += 34
    if album:
        _text(draw, (NOW_TEXT_X, y), album, size=14, bold=False, fill=DIM, max_w=max_w)

    _footer(draw, NOW_W, NOW_H - 40, footer)

    out = BytesIO()
    canvas.save(out, format="PNG", optimize=True)
    out.seek(0)
    return out


async def render_now_playing_card(
    *,
    image_bytes: bytes | None,
    title: str,
    artist: str,
    album: str = "",
    live: bool = True,
    handle: str = "",
    footer: str = "",
    empty_text: str = "Nothing playing yet.",
    now_label: str = "Now playing",
    last_label: str = "Last played",
) -> BytesIO:
    """The large now-playing card."""
    return await asyncio.to_thread(
        _render_now_playing_sync,
        image_bytes,
        title,
        artist,
        album,
        live,
        handle,
        footer,
        empty_text,
        now_label,
        last_label,
    )
