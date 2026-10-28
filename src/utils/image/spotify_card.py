"""
PIL renderer for the ``.spotify`` image card.

The card follows the same website theme as the leveling and economy cards
(``economy_card.py``): a near-black graphite canvas, steel chrome, and the
Spotify green reserved for the track progress. It is deliberately sparse — the
album art, the track, the artist and album, and a live progress bar — so the
command reads as one clean card rather than a wall of fields.

``render_spotify_card`` returns a ``BytesIO`` containing a PNG that can be sent
as a ``discord.File`` and referenced from a ``discord.ui.MediaGallery`` inside a
Components-V2 LayoutView. The CPU-bound work is offloaded to
``asyncio.to_thread`` so the bot's event loop stays responsive.

Cover art: callers pass raw image bytes (already downloaded off-loop). A themed
equalizer tile is used when the cover is missing or unreadable.
"""

from __future__ import annotations

import asyncio
from io import BytesIO

from PIL import Image, ImageDraw, ImageOps

from utils.image._font_resolver import (
    draw_text_with_fallback,
    font_getlength,
)
from utils.image.economy_card import (
    ACCENT,
    ACCENT_BRIGHT,
    DIM,
    INK,
    MUTED,
    PANEL_BG,
    PANEL_BORDER,
    _bold,
    _make_canvas,
    _progress_bar,
    _reg,
    _rounded_mask,
    _strip_discord_emoji,
    _truncate,
    _vertical_gradient,
)


# ── Palette ────────────────────────────────────────────────────────────────

SPOTIFY_GREEN = (29, 185, 84)        # #1DB954 — the track progress
SPOTIFY_GREEN_DARK = (20, 140, 63)   # progress bar terminus


# ── Layout ─────────────────────────────────────────────────────────────────

CARD_W = 820
CARD_H = 300
RADIUS = 28

ART_X = 36
ART_Y = 74
ART_SIZE = 152
ART_RADIUS = 18

TEXT_X = ART_X + ART_SIZE + 24
TEXT_W = CARD_W - TEXT_X - 36

BAR_Y = 190
BAR_H = 8
FOOTER_RULE_Y = 240
FOOTER_TEXT_Y = 255


# ── Helpers ────────────────────────────────────────────────────────────────

def _clock(seconds: float | None) -> str:
    """``mm:ss`` for a duration that may be missing or negative."""
    try:
        total = max(0, int(round(float(seconds or 0))))
    except (TypeError, ValueError):
        total = 0
    return f"{total // 60}:{total % 60:02d}"


def _cover_placeholder(size: int, radius: int) -> Image.Image:
    """A themed equalizer tile for tracks without cover art."""
    tile = _vertical_gradient((size, size), (26, 42, 33), PANEL_BG).convert("RGBA")

    bars = (0.30, 0.58, 0.42, 0.70)
    bar_w = size // 12
    gap = size // 16
    group_w = len(bars) * bar_w + (len(bars) - 1) * gap
    x = (size - group_w) // 2
    draw = ImageDraw.Draw(tile)
    for height in bars:
        bar_h = int(size * height)
        top = (size - bar_h) // 2
        draw.rounded_rectangle(
            [x, top, x + bar_w - 1, top + bar_h - 1],
            radius=bar_w // 2,
            fill=(*SPOTIFY_GREEN, 210),
        )
        x += bar_w + gap

    tile.putalpha(_rounded_mask((size, size), radius))
    return tile


def _cover_art(raw: bytes | None, size: int, radius: int) -> Image.Image:
    """Crop cover bytes to a rounded square, or fall back to the tile."""
    image = None
    if raw:
        try:
            image = Image.open(BytesIO(raw)).convert("RGBA")
        except Exception:
            image = None
    if image is None:
        return _cover_placeholder(size, radius)

    image = ImageOps.fit(image, (size, size), Image.LANCZOS)
    image.putalpha(_rounded_mask((size, size), radius))
    return image


def _pill(canvas: Image.Image, label: str) -> None:
    """The green ``NOW PLAYING`` chip in the top-right corner."""
    font = _bold(11)
    text_w = int(font_getlength(font, label))
    width, height = text_w + 44, 28
    x, y = CARD_W - width - 36, 24

    pill = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(pill)
    draw.rounded_rectangle(
        [0, 0, width - 1, height - 1],
        radius=height // 2,
        fill=(0, 0, 0, 130),
        outline=SPOTIFY_GREEN_DARK,
        width=1,
    )
    dot_y = height // 2
    draw.ellipse([13, dot_y - 3, 19, dot_y + 3], fill=SPOTIFY_GREEN)
    draw.text((28, 6), label, fill=ACCENT_BRIGHT, font=font)
    canvas.alpha_composite(pill, (x, y))


def _draw_text(draw, xy, text: str, *, size: int, bold: bool, fill) -> None:
    draw_text_with_fallback(draw, xy, text, size=size, bold=bold, fill=fill)


# ── Renderer ───────────────────────────────────────────────────────────────

def _render_spotify_sync(
    cover_bytes: bytes | None,
    title: str,
    artist: str,
    album: str,
    duration: float,
    elapsed: float | None,
    footer: str,
) -> BytesIO:
    canvas = _make_canvas(CARD_W, CARD_H, radius=RADIUS)
    draw = ImageDraw.Draw(canvas)

    title = _strip_discord_emoji(title or "Spotify") or "Spotify"
    artist = _strip_discord_emoji(artist or "")
    album = _strip_discord_emoji(album or "")
    footer = _strip_discord_emoji(footer or "")

    # ── Header ──
    draw.text((ART_X, 28), "NIKO SPOTIFY", fill=ACCENT, font=_bold(16))
    _pill(canvas, "NOW PLAYING")

    # ── Album art ──
    cover = _cover_art(cover_bytes, ART_SIZE, ART_RADIUS)
    canvas.alpha_composite(cover, (ART_X, ART_Y))
    ImageDraw.Draw(canvas).rounded_rectangle(
        [ART_X, ART_Y, ART_X + ART_SIZE - 1, ART_Y + ART_SIZE - 1],
        radius=ART_RADIUS,
        outline=PANEL_BORDER,
        width=1,
    )

    # ── Track, artist, album ──
    _draw_text(
        draw,
        (TEXT_X, 74),
        _truncate(title, _bold(30), TEXT_W),
        size=30,
        bold=True,
        fill=INK,
    )
    if artist:
        _draw_text(
            draw,
            (TEXT_X, 118),
            _truncate(artist, _reg(18), TEXT_W),
            size=18,
            bold=False,
            fill=MUTED,
        )
    if album:
        _draw_text(
            draw,
            (TEXT_X, 149),
            _truncate(album, _reg(14), TEXT_W),
            size=14,
            bold=False,
            fill=DIM,
        )

    # ── Progress ──
    total = max(0.0, float(duration or 0))
    played = min(max(float(elapsed or 0), 0.0), total) if total else 0.0
    percent = played / total if total else 0.0
    _progress_bar(
        canvas,
        TEXT_X,
        BAR_Y,
        TEXT_W,
        BAR_H,
        percent,
        fill_top=SPOTIFY_GREEN,
        fill_bot=SPOTIFY_GREEN_DARK,
    )
    draw = ImageDraw.Draw(canvas)
    _draw_text(draw, (TEXT_X, BAR_Y + 18), _clock(played), size=11, bold=False, fill=DIM)
    total_label = _clock(total)
    total_w = int(font_getlength(_reg(11), total_label))
    _draw_text(
        draw,
        (TEXT_X + TEXT_W - total_w, BAR_Y + 18),
        total_label,
        size=11,
        bold=False,
        fill=DIM,
    )

    # ── Footer ──
    draw.line(
        [(ART_X, FOOTER_RULE_Y), (CARD_W - 36, FOOTER_RULE_Y)],
        fill=PANEL_BORDER,
        width=1,
    )
    if footer:
        _draw_text(
            draw,
            (ART_X, FOOTER_TEXT_Y),
            _truncate(footer, _reg(13), CARD_W - 72 - 90),
            size=13,
            bold=False,
            fill=DIM,
        )
    label = "SPOTIFY"
    label_w = int(font_getlength(_bold(11), label))
    draw.text((CARD_W - 36 - label_w, FOOTER_TEXT_Y + 2), label, fill=ACCENT, font=_bold(11))

    out = BytesIO()
    # Keep the alpha channel: `_make_canvas` clips the canvas to the rounded
    # card shape, so saving as RGB would paste the corner cut-outs back in as
    # opaque black when Discord renders the PNG.
    canvas.save(out, format="PNG", optimize=True)
    out.seek(0)
    return out


async def render_spotify_card(
    *,
    cover_bytes: bytes | None,
    title: str,
    artist: str,
    album: str,
    duration: float,
    elapsed: float | None = None,
    footer: str = "",
) -> BytesIO:
    """Render the ``.spotify`` card and return the PNG in a ``BytesIO``."""
    return await asyncio.to_thread(
        _render_spotify_sync,
        cover_bytes,
        title,
        artist,
        album,
        duration,
        elapsed,
        footer,
    )
