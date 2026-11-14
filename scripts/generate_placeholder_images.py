#!/usr/bin/env python3
"""Generate the placeholder images for content-flagged deleted-message media.

Discord's content scanning flags attachments as explicit, gore, or self-harm.
Reposting a flagged image in a deleted-message log would put the same media back
in a channel, so the log shows one of these placeholders instead and links to the
page that explains the swap. The files are served by the website from stable
URLs, one per flag type:

    https://niko.sryze.cc/assets/placeholders/explicit.png
    https://niko.sryze.cc/assets/placeholders/gore.png
    https://niko.sryze.cc/assets/placeholders/self-harm.png

``utils/safety/flagged_media.py`` owns those slugs, so the artwork, the log note and the
explainer page cannot drift apart.

The card is deliberately plain: the near-black site canvas with one faint glow,
a thin slashed ring, a short headline and one sentence, in the two typefaces the
site already ships. The flag type is named in that sentence, so the three cards
differ by a word rather than by decoration, and the log note underneath is what
carries the link. Everything is drawn at twice the final size and scaled down,
which is what keeps the ring and the type smooth without a font renderer.

The files are written into the Vite ``public`` directory and mirrored into the
served website build; ``npm run build`` runs this script through the package's
``prebuild`` hook.

Run it directly with:

    python3 scripts/generate_placeholder_images.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils.safety import flagged_media  # noqa: E402
from utils.image._font_resolver import font_getlength  # noqa: E402

OUT_DIR = ROOT / "web" / "public" / "assets" / "placeholders"
# The built website is committed and served by Flask, so mirroring the artwork
# there makes it reachable by Discord before the next full build.
DIST_DIR = ROOT / "src" / "website" / "dist" / "assets" / "placeholders"

WIDTH, HEIGHT = 1200, 900
#: Drawn at 2x and resampled once, so the ring and the type are not aliased.
SCALE = 2

#: How wide the sentence may run before it wraps, in design-space pixels.
TEXT_WIDTH = 760

ORBITRON = ROOT / "web" / "public" / "fonts" / "orbitron-variable.ttf"
NOTO = ROOT / "src" / "assets" / "fonts" / "NotoSans-Regular.ttf"

# ── Palette (the site's own tokens) ─────────────────────────────────────────
BACKDROP_CENTER = (19, 21, 25)
BACKDROP_EDGE = (7, 8, 10)
INK = (244, 245, 247)
MUTED = (154, 161, 171)
AMBER = (232, 178, 99)

#: The one headline every card carries; the flag type is named below it.
HEADLINE = "Image hidden"

#: The sentence under the headline, keyed by the flag slug.
BODIES = {
    flagged_media.EXPLICIT:
        "This image was flagged as explicit by an automated content filter and could not be displayed.",
    flagged_media.GORE:
        "This image was flagged as graphic content by an automated content filter and could not be displayed.",
    flagged_media.SELF_HARM:
        "This image was flagged as self-harm by an automated content filter and could not be displayed.",
}


def _px(value: float) -> int:
    """A design-space measurement in device pixels."""
    return round(value * SCALE)


def _backdrop(size: tuple[int, int]) -> Image.Image:
    """A near-black canvas with a single soft glow behind the artwork."""
    shade = ImageOps.invert(Image.radial_gradient("L")).resize(
        size, Image.Resampling.BICUBIC
    )
    shade = shade.filter(ImageFilter.GaussianBlur(size[0] * 0.03))
    return Image.composite(
        Image.new("RGB", size, BACKDROP_CENTER),
        Image.new("RGB", size, BACKDROP_EDGE),
        shade,
    )


def _orbitron(size: int, weight: str = "Medium") -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(ORBITRON), size)
    try:
        font.set_variation_by_name(weight)
    except (OSError, ValueError):
        pass
    return font


def _noto(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(NOTO), size)


def _tracked(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill,
    tracking: int = 0,
) -> None:
    """Draw *text* with letter spacing."""
    x, y = position
    for index, character in enumerate(text):
        draw.text((x, y), character, font=font, fill=fill)
        x += font_getlength(font, character) + (tracking if index < len(text) - 1 else 0)


def _centred(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    top: int,
    fill,
    tracking: int = 0,
) -> None:
    """Draw one line centred on the canvas, *top* being its top edge."""
    width = sum(
        font_getlength(font, character) + (tracking if index < len(text) - 1 else 0)
        for index, character in enumerate(text)
    )
    _tracked(
        draw,
        (round((_px(WIDTH) - width) / 2), top),
        text, font, fill, tracking,
    )


def _wrap(text: str, font: ImageFont.ImageFont, max_width: float) -> list[str]:
    lines: list[str] = []
    line = ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if line and font_getlength(font, candidate) > max_width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def _slash_ring(draw: ImageDraw.ImageDraw) -> None:
    """A thin slashed ring: the one symbol that reads as "not shown" at any size."""
    cx, cy = _px(WIDTH) // 2, _px(320)
    radius = _px(52)
    width = max(_px(3.5), 2)
    colour = (*AMBER, 210)
    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        outline=colour, width=width,
    )
    reach = radius * 0.62
    draw.line((cx - reach, cy + reach, cx + reach, cy - reach), fill=colour, width=width)


def render(flag: str) -> Image.Image:
    """The placeholder card for one flag type."""
    canvas = _backdrop((_px(WIDTH), _px(HEIGHT))).convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    _slash_ring(draw)

    headline = _orbitron(_px(58), "Medium")
    _centred(draw, HEADLINE, headline, _px(438), INK, _px(2))

    body_font = _noto(_px(28))
    lines = _wrap(BODIES[flag], body_font, _px(TEXT_WIDTH))
    top = _px(540)
    for index, line in enumerate(lines):
        _centred(draw, line, body_font, top + index * _px(46), MUTED)

    return canvas.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    for flag in flagged_media.FLAG_TYPES:
        card = render(flag)
        name = f"{flag}.png"
        card.save(OUT_DIR / name, format="PNG", optimize=True)
        card.save(DIST_DIR / name, format="PNG", optimize=True)
        print(f"placeholders: wrote {name}")


if __name__ == "__main__":
    main()
