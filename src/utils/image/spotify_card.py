"""
PIL renderer for the ``.spotify`` image card.

Unlike the other command cards, which stay on the site's graphite canvas, this
one borrows Spotify's now-playing language: a tall card, a background tinted
from the album art's dominant colour, and the cover sitting in the foreground
like artwork on a shelf.

The card is built to Spotify's design and branding guidelines
(developer.spotify.com/documentation/design): the artwork is never blurred,
cropped, covered or distorted, its corners are rounded to the documented 8 px,
the artwork colour (or #191414 when there is none) is used for the background,
and the Spotify icon is the only attribution mark - rendered white because the
green colourway is only permitted on black or white, at 40 px so it stays above
the 21 px minimum after Discord scales the card, with half an icon's height of
clear space around it. The icon is never paired with another wordmark or brand,
the progress bar has no seek affordance, and the track links back to Spotify.

``render_spotify_card`` returns a ``BytesIO`` containing a PNG that can be sent
as a ``discord.File`` and referenced from a ``discord.ui.MediaGallery`` inside a
Components-V2 LayoutView. The CPU-bound work is offloaded to
``asyncio.to_thread`` so the bot's event loop stays responsive.

Cover art: callers pass raw image bytes (already downloaded off-loop). A themed
equalizer tile is used when the cover is missing or unreadable.
"""

from __future__ import annotations

import asyncio
import colorsys
import re
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

from utils.image._font_resolver import (
    draw_text_with_fallback,
    font_getlength,
)
from utils.image.economy_card import (
    _bold,
    _reg,
    _rounded_mask,
    _strip_discord_emoji,
    _truncate,
    _vertical_gradient,
)


# ── Palette ────────────────────────────────────────────────────────────────
# Spotify's own greys on top of the cover's colour: white titles, the #B3B3B3
# secondary text, and the green reserved for the progress bar.

SPOTIFY_GREEN = (29, 185, 84)          # #1DB954 — the brand green
SPOTIFY_GREEN_BRIGHT = (30, 215, 96)   # #1ED760 — the bar
SPOTIFY_GREEN_DARK = (20, 140, 63)     # bar terminus
SPOTIFY_BASE = (25, 20, 20)            # #191414 — the documented fallback

# The logo is drawn in white: the guidelines only allow the green colourway on
# black or white, and this card's background is tinted by the album art.
LOGO_INK = (255, 255, 255)

TITLE_INK = (255, 255, 255)
ARTIST_INK = (179, 179, 179)           # #B3B3B3
ALBUM_INK = (152, 152, 157)
TIME_INK = (167, 167, 167)
FOOTER_INK = (179, 179, 179)

HAIRLINE = (255, 255, 255, 28)
TRACK_BG = (255, 255, 255, 30)


# ── Layout ─────────────────────────────────────────────────────────────────

CARD_W = 820
CARD_H = 470
RADIUS = 30
PAD = 44

# The header row: the icon alone on the left, the "now playing" chip right.
# Spotify's 21 px digital minimum applies to the rendered size, and Discord
# scales this 820 px card down to phone width, so the icon is drawn at 44 px
# (still >= 21 px at ~400 px wide) and keeps half its height as clear space.
HEADER_Y = 32
HEADER_MARK = 44

# The album art is the hero: the guidelines ask for an 8 px corner radius on
# large surfaces, and it is never cropped or covered.
ART_X = PAD
ART_Y = 104
ART_SIZE = 240
ART_RADIUS = 8

TEXT_X = ART_X + ART_SIZE + 40
TEXT_W = CARD_W - TEXT_X - PAD

# The track progress runs the full width under the hero.
BAR_Y = 372
BAR_H = 6
TIMES_Y = BAR_Y + 18
FOOTER_RULE_Y = 416
FOOTER_TEXT_Y = 434


# ── Helpers ────────────────────────────────────────────────────────────────

def _clock(seconds: float | None) -> str:
    """``mm:ss`` for a duration that may be missing or negative."""
    try:
        total = max(0, int(round(float(seconds or 0))))
    except (TypeError, ValueError):
        total = 0
    return f"{total // 60}:{total % 60:02d}"


def _cover_image(raw: bytes | None) -> Image.Image | None:
    """Decode cover bytes, or ``None`` when they are missing or unreadable."""
    if not raw:
        return None
    try:
        return Image.open(BytesIO(raw)).convert("RGB")
    except Exception:
        return None


def _tracked(draw, xy, text: str, font, fill, spacing: float = 2.2) -> float:
    """Draw *text* with extra letter spacing and return its width."""
    x, y = xy
    start = x
    for index, char in enumerate(text):
        draw.text((x, y), char, font=font, fill=fill)
        x += font_getlength(font, char) + (spacing if index < len(text) - 1 else 0)
    return x - start


def _wrap_lines(text: str, font, max_w: int, max_lines: int = 2) -> list[str]:
    """Split *text* into at most *max_lines* lines that each fit *max_w*."""
    words = (text or "").split()
    if not words:
        return []

    lines: list[str] = []
    current = words[0]
    index = 1
    while index < len(words):
        candidate = f"{current} {words[index]}"
        if font_getlength(font, candidate) <= max_w:
            current = candidate
            index += 1
            continue
        if len(lines) + 1 >= max_lines:
            # No room for another line: fold the rest into this one and clip it.
            current = " ".join([candidate] + words[index + 1:])
            break
        lines.append(current)
        current = words[index]
        index += 1

    lines.append(_truncate(current, font, max_w))
    return lines[:max_lines]


def _cover_placeholder(size: int, radius: int) -> Image.Image:
    """A themed equalizer tile for tracks without cover art."""
    tile = _vertical_gradient((size, size), (24, 52, 36), (10, 14, 12)).convert("RGBA")

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
    """The artwork at full size with rounded corners, never cropped."""
    image = _cover_image(raw)
    if image is None:
        return _cover_placeholder(size, radius)

    image = image.convert("RGBA")
    if image.width != image.height:
        # The guidelines forbid cropping artwork, so a non-square cover is
        # padded with its own colour instead of being cut to fit.
        image = ImageOps.pad(
            image,
            (size, size),
            method=Image.LANCZOS,
            color=_dominant_colour(image),
        )
    else:
        image = image.resize((size, size), Image.LANCZOS)
    image.putalpha(_rounded_mask((size, size), radius))
    return image


def _dominant_colour(image: Image.Image) -> tuple[int, int, int]:
    """The artwork's most characterful colour, the way Spotify's Palette picks one."""
    sample = ImageOps.fit(image.convert("RGB"), (48, 48), Image.LANCZOS)
    quantized = sample.quantize(colors=8, method=Image.MEDIANCUT)
    palette = quantized.getpalette() or []
    best_score, best = -1.0, SPOTIFY_BASE
    for count, index in quantized.getcolors() or []:
        red, green, blue = palette[index * 3:index * 3 + 3]
        high, low = max(red, green, blue), min(red, green, blue)
        saturation = (high - low) / high if high else 0.0
        # Favour swatches that are both common and saturated, not just bright.
        score = count * (0.25 + saturation) * (0.35 + high / 255)
        if score > best_score:
            best_score, best = score, (red, green, blue)
    return best


def _shade(colour: tuple[int, int, int], value: float) -> tuple[int, int, int]:
    """The colour at a fixed brightness, keeping its hue and saturation."""
    hue, saturation, _ = colorsys.rgb_to_hsv(*(component / 255 for component in colour))
    red, green, blue = colorsys.hsv_to_rgb(hue, min(1.0, saturation * 1.15), value)
    return int(round(red * 255)), int(round(green * 255)), int(round(blue * 255))


def _backdrop(cover_bytes: bytes | None, size: tuple[int, int], radius: int) -> Image.Image:
    """The artwork's colour, darkened into the card's background.

    Spotify's playing-view guidelines recommend extracting the artwork colour
    for the background and name #191414 as the fallback. They also forbid
    blurring the artwork itself, which is why this is a colour sample rather
    than a blurred copy of the cover.
    """
    width, height = size
    image = _cover_image(cover_bytes)
    colour = _dominant_colour(image) if image is not None else SPOTIFY_BASE

    top = _shade(colour, 0.30 if image is not None else 0.16)
    bottom = _shade(colour, 0.06)
    backdrop = _vertical_gradient((width, height), top, bottom).convert("RGBA")

    backdrop.putalpha(_rounded_mask((width, height), radius))
    ImageDraw.Draw(backdrop).rounded_rectangle(
        [0, 0, width - 1, height - 1],
        radius=radius,
        outline=(255, 255, 255, 34),
        width=1,
    )
    return backdrop


# ── Logo ───────────────────────────────────────────────────────────────────
# The mark is the site's own ``spotify.svg``, rasterised from its path data.
# There is no SVG renderer in the bot's runtime (and cairosvg would drag a
# native cairo dependency into a Termux-friendly deploy), so the path is parsed
# and flattened here. Only the commands that file uses are supported, and a
# missing or unreadable asset falls back to the old drawn arcs.

_LOGO_VIEWBOX = 24.0
_LOGO_SUPERSAMPLE = 4
_LOGO_CACHE: dict[tuple[str, int, tuple[int, int, int]], Image.Image] = {}

_PATH_TOKEN_RE = re.compile(r"[MmLlHhVvCcSsZz]|-?\d*\.?\d+(?:[eE][-+]?\d+)?")


def _logo_asset_path() -> Path | None:
    """The site's Spotify SVG: the served build first, the source second."""
    here = Path(__file__).resolve()
    for candidate in (
        here.parents[2] / "website" / "dist" / "spotify.svg",
        here.parents[3] / "web" / "public" / "spotify.svg",
    ):
        if candidate.is_file():
            return candidate
    return None


def _logo_subpaths() -> list[list[tuple[float, float]]]:
    """The logo's outline and its three arc cut-outs, flattened to polygons."""
    path = _logo_asset_path()
    if path is None:
        raise ValueError("spotify.svg is not available")
    source = path.read_text(encoding="utf-8")
    match = re.search(r"<path[^>]*\bd=\"([^\"]+)\"", source)
    if match is None:
        raise ValueError("spotify.svg has no path data")
    return _flatten_svg_path(match.group(1))


def _flatten_svg_path(d: str, steps: int = 20) -> list[list[tuple[float, float]]]:
    """Flatten an SVG path's subpaths into polylines (the subset we need)."""
    tokens = _PATH_TOKEN_RE.findall(d)
    subpaths: list[list[tuple[float, float]]] = []
    current: list[tuple[float, float]] = []
    x = y = 0.0
    start = (0.0, 0.0)
    control: tuple[float, float] | None = None
    command = None
    index = 0

    def number() -> float:
        nonlocal index
        value = float(tokens[index])
        index += 1
        return value

    def curve(p1, p2, p3) -> None:
        nonlocal control, x, y
        for step in range(1, steps + 1):
            t = step / steps
            u = 1 - t
            current.append((
                u * u * u * x + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0],
                u * u * u * y + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1],
            ))
        control = p2
        x, y = p3

    while index < len(tokens):
        token = tokens[index]
        if token.isalpha():
            command = token
            index += 1
            if command in "Zz":
                if current:
                    current.append(start)
                    subpaths.append(current)
                    current = []
                control = None
                continue

        if command in ("M", "m"):
            px, py = number(), number()
            x, y = (x + px, y + py) if command == "m" else (px, py)
            if current:
                subpaths.append(current)
            current = [(x, y)]
            start = (x, y)
            control = None
            command = "l" if command == "m" else "L"
        elif command in ("L", "l"):
            px, py = number(), number()
            x, y = (x + px, y + py) if command == "l" else (px, py)
            current.append((x, y))
            control = None
        elif command in ("H", "h"):
            px = number()
            x = x + px if command == "h" else px
            current.append((x, y))
            control = None
        elif command in ("V", "v"):
            py = number()
            y = y + py if command == "v" else py
            current.append((x, y))
            control = None
        elif command in ("C", "c"):
            values = [number() for _ in range(6)]
            if command == "c":
                values = [
                    values[0] + x, values[1] + y,
                    values[2] + x, values[3] + y,
                    values[4] + x, values[5] + y,
                ]
            curve(
                (values[0], values[1]),
                (values[2], values[3]),
                (values[4], values[5]),
            )
        elif command in ("S", "s"):
            values = [number() for _ in range(4)]
            if command == "s":
                values = [values[0] + x, values[1] + y, values[2] + x, values[3] + y]
            mirror = (2 * x - control[0], 2 * y - control[1]) if control else (x, y)
            curve(mirror, (values[0], values[1]), (values[2], values[3]))
        else:
            raise ValueError(f"unsupported SVG command {command!r}")

    if current:
        subpaths.append(current)
    return subpaths


def _rasterise_logo(size: int, colour: tuple[int, int, int]) -> Image.Image | None:
    """Fill the SVG's outline and punch its cut-outs out of the mask."""
    try:
        subpaths = _logo_subpaths()
    except (OSError, ValueError):
        return None

    hi = size * _LOGO_SUPERSAMPLE
    scale = hi / _LOGO_VIEWBOX
    mask = Image.new("L", (hi, hi), 0)
    draw = ImageDraw.Draw(mask)
    for position, points in enumerate(subpaths):
        if len(points) < 3:
            continue
        polygon = [(point[0] * scale, point[1] * scale) for point in points]
        # The first subpath is the disc; the ones after it are its cut-outs.
        draw.polygon(polygon, fill=255 if position == 0 else 0)
    mask = mask.resize((size, size), Image.LANCZOS)

    mark = Image.new("RGBA", (size, size), (*colour, 255))
    mark.putalpha(mask)
    return mark


def _spotify_logo(size: int) -> Image.Image:
    """The site logo at *size* in white, rasterised once and cached.

    The icon is drawn monochrome because Spotify only permits the green
    colourway on a black or white background, and this card's background is
    tinted by the album art.
    """
    path = _logo_asset_path()
    key = (str(path or ""), size, LOGO_INK)
    cached = _LOGO_CACHE.get(key)
    if cached is not None:
        return cached

    mark = _rasterise_logo(size, LOGO_INK) if path is not None else None
    if mark is None:
        mark = _drawn_logo(size)
    _LOGO_CACHE[key] = mark
    return mark


def _drawn_logo(size: int) -> Image.Image:
    """Fallback mark for an install without the website's SVG."""
    mark = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(mark)
    draw.ellipse([0, 0, size - 1, size - 1], fill=(*LOGO_INK, 255))

    centre = size / 2
    for scale, stroke in ((0.66, 0.075), (0.49, 0.065), (0.32, 0.055)):
        radius = size * scale / 2
        draw.arc(
            [centre - radius, centre - radius * 0.80, centre + radius, centre + radius * 0.88],
            start=202,
            end=338,
            fill=(0, 0, 0, 0),
            width=max(1, int(round(size * stroke))),
        )
    return mark


def _spotify_mark(canvas: Image.Image, x: int, y: int, size: int) -> None:
    """Composite the site's Spotify logo onto *canvas*."""
    canvas.alpha_composite(_spotify_logo(size), (x, y))


def _now_playing_pill(canvas: Image.Image, label: str) -> None:
    """The ``NOW PLAYING`` chip in the top-right corner.

    Kept monochrome so the only green on the card is the progress bar, and the
    chip can never be mistaken for a variation on the logo.
    """
    font = _bold(11)
    text_w = int(_tracked_width(font, label))
    width, height = text_w + 46, 30
    x, y = CARD_W - width - PAD, HEADER_Y + 5

    pill = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(pill)
    draw.rounded_rectangle(
        [0, 0, width - 1, height - 1],
        radius=height // 2,
        fill=(255, 255, 255, 18),
        outline=(255, 255, 255, 60),
        width=1,
    )
    mid = height // 2
    draw.ellipse([12, mid - 6, 24, mid + 6], fill=(255, 255, 255, 40))
    draw.ellipse([15, mid - 3, 21, mid + 3], fill=(255, 255, 255, 220))
    _tracked(draw, (29, 8), label, font, TITLE_INK)
    canvas.alpha_composite(pill, (x, y))


def _tracked_width(font, text: str, spacing: float = 2.2) -> float:
    if not text:
        return 0.0
    return sum(font_getlength(font, char) for char in text) + spacing * (len(text) - 1)


def _draw_text(draw, xy, text: str, *, size: int, bold: bool, fill) -> None:
    draw_text_with_fallback(draw, xy, text, size=size, bold=bold, fill=fill)


def _progress(canvas: Image.Image, x: int, y: int, w: int, h: int, percent: float) -> None:
    """Spotify's flat bar.

    No thumb or handle: the guidelines ask that the progress bar read as
    information only, with nothing suggesting the listener can seek.
    """
    percent = max(0.0, min(1.0, percent))

    track = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(track).rounded_rectangle(
        [0, 0, w - 1, h - 1], radius=h // 2, fill=TRACK_BG
    )
    canvas.alpha_composite(track, (x, y))

    if percent <= 0.001:
        return

    fill_w = max(h, int(w * percent))
    fill = _vertical_gradient(
        (fill_w, h), SPOTIFY_GREEN_BRIGHT, SPOTIFY_GREEN_DARK
    ).convert("RGBA")
    fill.putalpha(_rounded_mask((fill_w, h), h // 2))
    canvas.alpha_composite(fill, (x, y))


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
    title = _strip_discord_emoji(title or "Spotify") or "Spotify"
    artist = _strip_discord_emoji(artist or "")
    album = _strip_discord_emoji(album or "")
    footer = _strip_discord_emoji(footer or "")

    canvas = _backdrop(cover_bytes, (CARD_W, CARD_H), RADIUS)
    draw = ImageDraw.Draw(canvas)

    # ── Header: the Spotify icon on its own, then the now-playing chip ──
    # The icon is the attribution mark, so it is never joined by another word
    # or brand: the guidelines forbid pairing Spotify with other brands and
    # require half an icon's height of clear space around it.
    _spotify_mark(canvas, PAD, HEADER_Y, HEADER_MARK)
    _now_playing_pill(canvas, "NOW PLAYING")

    # ── Album art, lifted off the backdrop by a soft shadow ──
    shadow_size = ART_SIZE + 56
    shadow = Image.new("L", (shadow_size, shadow_size), 0)
    ImageDraw.Draw(shadow).rounded_rectangle(
        [24, 30, 24 + ART_SIZE - 1, 30 + ART_SIZE - 1],
        radius=ART_RADIUS + 4,
        fill=150,
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=14))
    shadow_layer = Image.new("RGBA", (shadow_size, shadow_size), (0, 0, 0, 255))
    shadow_layer.putalpha(shadow)
    canvas.alpha_composite(shadow_layer, (ART_X - 24, ART_Y - 24))

    canvas.alpha_composite(_cover_art(cover_bytes, ART_SIZE, ART_RADIUS), (ART_X, ART_Y))

    # ── Track, artist, album — vertically centred beside the art ──
    title_font = _bold(40)
    title_lines = _wrap_lines(title, title_font, TEXT_W, max_lines=2)
    line_h = 48
    block_h = len(title_lines) * line_h
    if artist:
        block_h += 8 + 24
    if album:
        block_h += 4 + 20

    y = ART_Y + max(0, (ART_SIZE - block_h) // 2) - 2
    for line in title_lines:
        _draw_text(draw, (TEXT_X, y), line, size=40, bold=True, fill=TITLE_INK)
        y += line_h
    if artist:
        y += 4
        _draw_text(
            draw,
            (TEXT_X, y),
            _truncate(artist, _reg(20), TEXT_W),
            size=20,
            bold=False,
            fill=ARTIST_INK,
        )
        y += 28
    if album:
        y += 2
        _draw_text(
            draw,
            (TEXT_X, y),
            _truncate(album, _reg(15), TEXT_W),
            size=15,
            bold=False,
            fill=ALBUM_INK,
        )

    # ── Progress ──
    total = max(0.0, float(duration or 0))
    played = min(max(float(elapsed or 0), 0.0), total) if total else 0.0
    percent = played / total if total else 0.0
    _progress(canvas, PAD, BAR_Y, CARD_W - PAD * 2, BAR_H, percent)
    draw = ImageDraw.Draw(canvas)
    _draw_text(draw, (PAD, TIMES_Y), _clock(played), size=12, bold=False, fill=TIME_INK)
    total_label = _clock(total)
    total_w = int(font_getlength(_reg(12), total_label))
    _draw_text(
        draw,
        (CARD_W - PAD - total_w, TIMES_Y),
        total_label,
        size=12,
        bold=False,
        fill=TIME_INK,
    )

    # ── Footer ──
    draw.line([(PAD, FOOTER_RULE_Y), (CARD_W - PAD, FOOTER_RULE_Y)], fill=HAIRLINE, width=1)
    if footer:
        _draw_text(
            draw,
            (PAD, FOOTER_TEXT_Y),
            _truncate(footer, _reg(13), CARD_W - PAD * 2),
            size=13,
            bold=False,
            fill=FOOTER_INK,
        )

    out = BytesIO()
    # Keep the alpha channel: the backdrop is clipped to the rounded card shape,
    # so saving as RGB would paste the corner cut-outs back in as opaque black
    # when Discord renders the PNG.
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
