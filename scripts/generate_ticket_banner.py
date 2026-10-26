#!/usr/bin/env python3
"""Generate the support server's ticket-panel banner.

The ticket panel shows its banner through the configurable ``panel_image`` URL.
The support server uses the long-lived ``/ticket_banner.png`` asset, so this
script overwrites that exact file: every refresh and every build picks up the
new artwork without anyone re-saving the panel URL.

The artwork follows Niko's indigo, cream and warm-sand palette (the same
colours as the README banner and the support panels) and pairs the headline
with a private-ticket card. It is written into the Vite ``public`` directory
and mirrored into the served website build; ``bun run build`` runs this script
through the package's ``prebuild`` hook.

Run it directly with:

    python3 scripts/generate_ticket_banner.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils.image._font_resolver import font_getlength, get_bold, get_reg  # noqa: E402

OUT_PATH = ROOT / "web" / "public" / "ticket_banner.png"
# The built website is committed and served by Flask, so mirroring the banner
# there makes it available to the running bot before the next full build.
MIRROR_PATH = ROOT / "src" / "website" / "dist" / "ticket_banner.png"

WIDTH, HEIGHT = 2172, 724

# ── Palette ─────────────────────────────────────────────────────────────────
INDIGO_TOP = (28, 28, 60)
INDIGO_BOTTOM = (46, 46, 90)
PERIWINKLE = (99, 116, 214)
CREAM = (249, 231, 222)
SAND = (239, 202, 176)
BODY_TEXT = (222, 219, 240)

ORBITRON = ROOT / "web" / "public" / "fonts" / "orbitron-variable.ttf"

MARGIN_X = 132


# ── Primitives ──────────────────────────────────────────────────────────────
def _vertical_gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    """A smooth vertical gradient, built one pixel wide and stretched."""
    height = size[1]
    strip = Image.new("RGB", (1, height))
    pixels = strip.load()
    for y in range(height):
        t = y / max(1, height - 1)
        pixels[0, y] = tuple(round(a + (b - a) * t) for a, b in zip(top, bottom))
    return strip.resize(size, Image.Resampling.BICUBIC)


def _radial_glow(
    canvas: Image.Image,
    center: tuple[float, float],
    radius: int,
    colour: tuple[int, int, int],
    alpha: int,
) -> None:
    """Blend a soft circular light into the canvas."""
    layer = Image.new("RGBA", (radius * 2, radius * 2), (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse((0, 0, radius * 2 - 1, radius * 2 - 1), fill=(*colour, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.42))
    canvas.alpha_composite(layer, (round(center[0]) - radius, round(center[1]) - radius))


def _tracked_text(
    draw: ImageDraw.ImageDraw,
    position: tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    tracking: float,
) -> float:
    """Draw letter-spaced text and return its total width."""
    x, y = position
    for index, character in enumerate(text):
        draw.text((x, y), character, font=font, fill=fill)
        x += font_getlength(font, character) + (tracking if index < len(text) - 1 else 0)
    return x - position[0]


def _orbitron(size: int, weight: str = "SemiBold") -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(ORBITRON), size)
    try:
        font.set_variation_by_name(weight)
    except (OSError, ValueError):
        pass
    return font


def _fit_bold(text: str, size: int, max_width: float) -> ImageFont.ImageFont:
    """Shrink a headline until it fits, so the layout never clips."""
    while size > 24:
        font = get_bold(size)
        if font_getlength(font, text) <= max_width:
            return font
        size -= 2
    return get_bold(size)


# ── Background ──────────────────────────────────────────────────────────────
def _build_background() -> Image.Image:
    canvas = _vertical_gradient((WIDTH, HEIGHT), INDIGO_TOP, INDIGO_BOTTOM).convert("RGBA")

    _radial_glow(canvas, (720, 250), 720, PERIWINKLE, 58)
    _radial_glow(canvas, (1980, 90), 520, (249, 214, 190), 34)
    _radial_glow(canvas, (1760, 640), 560, (120, 134, 226), 42)
    _radial_glow(canvas, (480, 700), 480, (249, 214, 190), 15)

    # Concentric rings behind the ticket card: a quiet, graphic halo.
    rings = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ring_draw = ImageDraw.Draw(rings)
    for radius in (238, 322, 420, 528, 650):
        ring_draw.ellipse(
            (1706 - radius, 356 - radius, 1706 + radius, 356 + radius),
            outline=(*CREAM, 22),
            width=2,
        )
    ring_draw.ellipse((1490, 140, 1922, 572), fill=(*CREAM, 8))
    canvas.alpha_composite(rings)

    # Stars: a sparse field with a few brighter, softly blurred points.
    rng = random.Random(19)
    stars = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    star_draw = ImageDraw.Draw(stars)
    for _ in range(230):
        x = rng.uniform(24, WIDTH - 24)
        y = rng.uniform(20, HEIGHT - 20)
        radius = rng.choice((1, 1, 1, 2, 2, 3))
        alpha = rng.randint(18, 72)
        star_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*CREAM, alpha))
    canvas.alpha_composite(stars)

    bright = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    bright_draw = ImageDraw.Draw(bright)
    for _ in range(16):
        x = rng.uniform(80, WIDTH - 80)
        y = rng.uniform(40, HEIGHT - 40)
        radius = rng.choice((2, 3, 4))
        bright_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*CREAM, 120))
    bright = bright.filter(ImageFilter.GaussianBlur(3.2))
    canvas.alpha_composite(bright)

    # Fine film grain keeps the large gradients from banding on Discord.
    grain = Image.effect_noise((WIDTH, HEIGHT), 26).convert("L").convert("RGB")
    canvas = Image.blend(canvas.convert("RGB"), grain, 0.045).convert("RGBA")
    return canvas


# ── Ticket card ─────────────────────────────────────────────────────────────
CARD_W, CARD_H = 680, 420
CARD_RADIUS = 32
STUB_X = 528
NOTCH_RADIUS = 24


def _render_ticket_card() -> Image.Image:
    card = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)

    body = Image.new("L", (CARD_W, CARD_H), 0)
    body_draw = ImageDraw.Draw(body)
    body_draw.rounded_rectangle((0, 0, CARD_W - 1, CARD_H - 1), radius=CARD_RADIUS, fill=255)
    for notch_y in (0, CARD_H):
        body_draw.ellipse(
            (STUB_X - NOTCH_RADIUS, notch_y - NOTCH_RADIUS, STUB_X + NOTCH_RADIUS, notch_y + NOTCH_RADIUS),
            fill=0,
        )

    fill = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    tint = _vertical_gradient((CARD_W, CARD_H), (78, 80, 142), (38, 39, 78)).convert("RGBA")
    # A thin cream wash over the indigo glass keeps the card legible on both
    # the bright left glow and the darker right edge.
    wash = Image.new("RGBA", (CARD_W, CARD_H), (*CREAM, 26))
    fill = Image.alpha_composite(fill, tint)
    fill = Image.alpha_composite(fill, wash)
    card.paste(fill, (0, 0), body)

    # Inner sheen across the top edge.
    sheen = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    sheen_draw = ImageDraw.Draw(sheen)
    sheen_draw.rounded_rectangle((10, 8, CARD_W - 11, 120), radius=CARD_RADIUS - 6, fill=(*CREAM, 18))
    sheen = sheen.filter(ImageFilter.GaussianBlur(26))
    sheen.putalpha(Image.composite(sheen.getchannel("A"), Image.new("L", (CARD_W, CARD_H), 0), body))
    card.alpha_composite(sheen)

    border = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(border)
    border_draw.rounded_rectangle(
        (1, 1, CARD_W - 2, CARD_H - 2), radius=CARD_RADIUS - 1, outline=(*CREAM, 128), width=2
    )
    border.putalpha(Image.composite(border.getchannel("A"), Image.new("L", (CARD_W, CARD_H), 0), body))
    card.alpha_composite(border)

    # Perforation between the card and its stub.
    for y in range(40, CARD_H - 40, 24):
        draw.line((STUB_X, y, STUB_X, y + 12), fill=(*CREAM, 92), width=2)

    # Ticket glyph.
    icon = (44, 40, 112, 82)
    draw.rounded_rectangle(icon, radius=9, outline=(*CREAM, 232), width=3)
    draw.line((90, 48, 90, 74), fill=(*CREAM, 150), width=2)
    draw.line((54, 56, 76, 56), fill=(*CREAM, 170), width=2)
    draw.line((54, 65, 76, 65), fill=(*CREAM, 110), width=2)

    eyebrow_font = _orbitron(19, "SemiBold")
    _tracked_text(draw, (130, 45), "SUPPORT TICKET", eyebrow_font, (*CREAM, 188), 4.4)

    headline_font = _fit_bold("by default.", 58, 440)
    draw.text((44, 122), "Private,", font=headline_font, fill=(*CREAM, 246), anchor="la")
    draw.text((44, 192), "by default.", font=headline_font, fill=(*SAND, 250), anchor="la")

    row_font = get_reg(22)
    rows = ("Staff-only channel", "Human replies", "Kept until solved")
    for index, label in enumerate(rows):
        y = 286 + index * 42
        draw.ellipse((46, y, 70, y + 24), outline=(*CREAM, 168), width=2)
        # The bundled Liberation Sans has no U+2713, so the tick is drawn.
        draw.line((53, y + 12, 57, y + 17), fill=(*CREAM, 230), width=2)
        draw.line((57, y + 17, 64, y + 7), fill=(*CREAM, 230), width=2)
        draw.text((84, y + 12), label, font=row_font, fill=(*BODY_TEXT, 232), anchor="lm")

    # Stub: ticket number and its open-state badge.
    stub_centre = (STUB_X + (CARD_W - STUB_X) // 2, 0)
    number_font = _fit_bold("01", 78, 116)
    draw.text((stub_centre[0], 150), "01", font=number_font, fill=(*CREAM, 240), anchor="mm")
    stub_font = _orbitron(13, "SemiBold")
    number_width = font_getlength(stub_font, "TICKET") + 3.2 * 5
    _tracked_text(draw, (stub_centre[0] - number_width / 2, 200), "TICKET", stub_font, (*CREAM, 160), 3.2)

    badge = (stub_centre[0] - 46, 322, stub_centre[0] + 46, 360)
    draw.rounded_rectangle(badge, radius=19, outline=(*CREAM, 128), width=2)
    badge_font = _orbitron(13, "SemiBold")
    badge_width = font_getlength(badge_font, "OPEN") + 3.0 * 3
    _tracked_text(draw, (stub_centre[0] - badge_width / 2, 330), "OPEN", badge_font, (*CREAM, 215), 3.0)

    for dot_y in (54, 394):
        draw.ellipse(
            (stub_centre[0] - 3, dot_y - 3, stub_centre[0] + 3, dot_y + 3),
            fill=(*CREAM, 150),
        )

    return card


def _place_card(canvas: Image.Image) -> None:
    card = _render_ticket_card()
    tilted = card.rotate(-8, resample=Image.Resampling.BICUBIC, expand=True)

    ambient = tilted.getchannel("A").filter(ImageFilter.GaussianBlur(46)).point(lambda value: value // 5)
    ambient_layer = Image.new("RGBA", tilted.size, (*CREAM, 0))
    ambient_layer.putalpha(ambient)
    canvas.alpha_composite(ambient_layer, (1400, 170))

    shadow = tilted.getchannel("A").filter(ImageFilter.GaussianBlur(28)).point(lambda value: value * 3 // 5)
    shadow_layer = Image.new("RGBA", tilted.size, (8, 8, 24, 0))
    shadow_layer.putalpha(shadow)
    canvas.alpha_composite(shadow_layer, (1406, 220))

    canvas.alpha_composite(tilted, (1394, 160))


# ── Copy ────────────────────────────────────────────────────────────────────
def _draw_copy(canvas: Image.Image) -> None:
    draw = ImageDraw.Draw(canvas)

    # Eyebrow.
    draw.polygon(
        ((MARGIN_X, 150), (MARGIN_X + 9, 141), (MARGIN_X + 18, 150), (MARGIN_X + 9, 159)),
        fill=(*SAND, 235),
    )
    eyebrow_font = _orbitron(26, "SemiBold")
    _tracked_text(draw, (MARGIN_X + 34, 132), "NIKO SUPPORT", eyebrow_font, (*CREAM, 214), 6.6)

    # Headline. Two short lines read well even at Discord's thumbnail size.
    line_one = "Real people."
    line_two = "One ticket."
    font_one = _fit_bold(line_one, 134, 1120)
    font_two = _fit_bold(line_two, 134, 1120)
    draw.text((MARGIN_X, 300), line_one, font=font_one, fill=(*CREAM, 252), anchor="ls")
    draw.text((MARGIN_X, 440), line_two, font=font_two, fill=(*SAND, 252), anchor="ls")

    # Supporting copy.
    body_font = get_reg(34)
    body_lines = (
        "Open a private support ticket and the Niko team",
        "will pick it up from there.",
    )
    for index, line in enumerate(body_lines):
        draw.text((MARGIN_X, 520 + index * 44), line, font=body_font, fill=(*BODY_TEXT, 222), anchor="ls")

    # Footer: the public home of this server’s support community.
    footer_font = _orbitron(19, "Medium")
    footer_y = 650
    draw.ellipse((MARGIN_X, footer_y, MARGIN_X + 7, footer_y + 7), fill=(*SAND, 160))
    _tracked_text(draw, (MARGIN_X + 22, footer_y - 6), "NIKO.SRYZE.CC", footer_font, (*CREAM, 150), 2.6)
    rule_x = MARGIN_X + 270
    draw.line((rule_x, footer_y + 3, rule_x + 42, footer_y + 3), fill=(*CREAM, 70), width=2)
    _tracked_text(
        draw, (rule_x + 62, footer_y - 6), "PRIVATE SUPPORT", footer_font, (*CREAM, 118), 2.6
    )


def main() -> None:
    canvas = _build_background()
    _place_card(canvas)
    _draw_copy(canvas)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    MIRROR_PATH.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(OUT_PATH, format="PNG", optimize=True)
    canvas.convert("RGB").save(MIRROR_PATH, format="PNG", optimize=True)

    print(f"ticket banner written to {OUT_PATH.relative_to(ROOT)} and {MIRROR_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
