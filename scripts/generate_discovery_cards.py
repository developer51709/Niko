#!/usr/bin/env python3
"""Generate the App Directory discovery cards.

Each language gets one card that introduces Niko on the bot's discovery page.
The cards are static artwork, so they are rendered here and served by the
website from a stable URL:

    https://niko.sryze.cc/assets/discovery/en.png
    https://niko.sryze.cc/assets/discovery/de.png
    https://niko.sryze.cc/assets/discovery/es.png
    https://niko.sryze.cc/assets/discovery/fr.png

``docs/discovery/`` embeds those URLs in the per-language extended
descriptions, so the artwork and the listing copy always ship together.

The artwork is deliberately quiet: it uses the dashboard's own tokens — the
near-black canvas, ``--surface``, ``--ink``, ``--muted``, ``--dim``, ``--line``
and the single ``--sage`` accent — and nothing else. No glows, noise, or
floating panels: inside a discovery message the card should read as a heading
and three lines of copy, not as a second design.

The card is a rounded rectangle saved as RGBA, so everything outside its
rounded edge is transparent and the listing's own background shows through the
corners instead of a painted box. Colours are copied from
``web/src/styles.css`` and the layout is set on a fixed grid, so a build is
deterministic and repeated builds are byte-identical.

The files are written into the Vite ``public`` directory and mirrored into the
served website build; ``npm run build`` runs this script through the package's
``prebuild`` hook.

Run it directly with:

    python3 scripts/generate_discovery_cards.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils.image._font_resolver import font_getlength, get_bold, get_reg  # noqa: E402

OUT_DIR = ROOT / "web" / "public" / "assets" / "discovery"
# The built website is committed and served by Flask, so mirroring the cards
# there makes them available to the running bot before the next full build.
DIST_DIR = ROOT / "src" / "website" / "dist" / "assets" / "discovery"

WIDTH, HEIGHT = 1600, 900
MARGIN = 104
#: Measured from ``MARGIN`` on both sides; every rule and row spans it.
CONTENT_W = WIDTH - MARGIN * 2

#: The card is a rounded rectangle floating on transparency, so the listing page
#: can paint it over either its dark or its light background without a painted
#: border box around it.
CARD_INSET = 18
CARD_RADIUS = 30
#: Rounded corners are drawn 4x and downsampled; PIL's own arcs are aliased.
CARD_SS = 4

# ── Dashboard palette (web/src/styles.css) ──────────────────────────────────
CANVAS_TOP = (11, 13, 16)      # a step above --canvas, so the card is not a void
CANVAS_BOTTOM = (5, 6, 7)      # --canvas
INK = (244, 245, 247)          # --ink
MUTED = (180, 186, 195)        # --muted
DIM = (133, 140, 150)          # --dim
LINE = (45, 48, 53)            # --line
LINE_SOFT = (34, 37, 42)       # --line-soft
SAGE = (139, 213, 177)         # --sage

# One entry per language the bot ships. The headline and the three rows are
# drawn on the card; the long description that embeds it lives in
# `docs/discovery/<lang>.md`. Keep the two in step when the pitch changes.
CARD_COPY: dict[str, dict[str, object]] = {
    "en": {
        "label": "ENGLISH",
        "headline": ("Warm moderation.", "Serious tooling."),
        "tagline": (
            "Moderation, music, economy, tickets, and AI in one polished "
            "Discord companion — with a full web dashboard."
        ),
        "rows": (
            "Automod, tickets, and clean logs",
            "Economy, levels, and giveaways",
            "An AI companion that remembers",
        ),
    },
    "de": {
        "label": "DEUTSCH",
        "headline": ("Moderation mit Gefühl.", "Werkzeuge mit Substanz."),
        "tagline": (
            "Moderation, Musik, Wirtschaft, Tickets und KI in einem "
            "Discord-Begleiter — mit vollständigem Web-Dashboard."
        ),
        "rows": (
            "Automod, Tickets und saubere Logs",
            "Wirtschaft, Level und Verlosungen",
            "Ein KI-Begleiter mit Gedächtnis",
        ),
    },
    "es": {
        "label": "ESPAÑOL",
        "headline": ("Moderación cercana.", "Herramientas serias."),
        "tagline": (
            "Moderación, música, economía, tickets e IA en un solo "
            "compañero de Discord, con panel web completo."
        ),
        "rows": (
            "Automod, tickets y registros claros",
            "Economía, niveles y sorteos",
            "Un compañero de IA con memoria",
        ),
    },
    "fr": {
        "label": "FRANÇAIS",
        "headline": ("Modération douce.", "Outils solides."),
        "tagline": (
            "Modération, musique, économie, tickets et IA dans un "
            "compagnon Discord complet, avec un tableau de bord web."
        ),
        "rows": (
            "Automod, tickets et journaux propres",
            "Économie, niveaux et giveaways",
            "Un compagnon IA qui se souvient",
        ),
    },
}


# ── Text helpers ────────────────────────────────────────────────────────────
def _tracked(
    draw: ImageDraw.ImageDraw,
    position: tuple[float, float],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    tracking: float,
) -> float:
    """Draw letter-spaced text and return its width."""
    x, y = position
    for index, character in enumerate(text):
        draw.text((x, y), character, font=font, fill=fill)
        x += font_getlength(font, character) + (tracking if index < len(text) - 1 else 0)
    return x - position[0]


def _wrap(text: str, font: ImageFont.ImageFont, max_width: float) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and font_getlength(font, candidate) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _fit_line(text: str, size: int, max_width: float, *, floor: int = 32) -> ImageFont.ImageFont:
    """Shrink a headline until it fits, so no translation clips the grid."""
    while size > floor:
        font = get_bold(size)
        if font_getlength(font, text) <= max_width:
            return font
        size -= 2
    return get_bold(size)


def _fit_wrapped(
    text: str, size: int, max_width: float, max_lines: int, *, floor: int = 20
) -> tuple[ImageFont.ImageFont, list[str]]:
    while size > floor:
        font = get_reg(size)
        lines = _wrap(text, font, max_width)
        if len(lines) <= max_lines:
            return font, lines
        size -= 2
    font = get_reg(size)
    return font, _wrap(text, font, max_width)[:max_lines]


# ── Artwork ─────────────────────────────────────────────────────────────────
def _background() -> Image.Image:
    """One smooth vertical gradient, drawn a pixel wide and stretched."""
    strip = Image.new("RGB", (1, HEIGHT))
    pixels = strip.load()
    for y in range(HEIGHT):
        t = y / max(1, HEIGHT - 1)
        pixels[0, y] = tuple(
            round(a + (b - a) * t) for a, b in zip(CANVAS_TOP, CANVAS_BOTTOM)
        )
    return strip.resize((WIDTH, HEIGHT), Image.Resampling.BICUBIC).convert("RGBA")


def _supersampled(draw_fn) -> Image.Image:
    """Rasterise a rounded shape at 4x and downsample it into a smooth mask."""
    big = Image.new("L", (WIDTH * CARD_SS, HEIGHT * CARD_SS), 0)
    draw_fn(ImageDraw.Draw(big))
    return big.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def _card_mask() -> Image.Image:
    """Everything outside the rounded card is transparent."""

    def shape(draw: ImageDraw.ImageDraw) -> None:
        draw.rounded_rectangle(
            (
                CARD_INSET * CARD_SS,
                CARD_INSET * CARD_SS,
                (WIDTH - CARD_INSET) * CARD_SS - 1,
                (HEIGHT - CARD_INSET) * CARD_SS - 1,
            ),
            radius=CARD_RADIUS * CARD_SS,
            fill=255,
        )

    return _supersampled(shape)


def _card_frame() -> Image.Image:
    """The hairline on the card edge, kept a pixel inside the mask."""

    def ring(draw: ImageDraw.ImageDraw) -> None:
        draw.rounded_rectangle(
            (
                (CARD_INSET + 1) * CARD_SS,
                (CARD_INSET + 1) * CARD_SS,
                (WIDTH - CARD_INSET - 1) * CARD_SS - 1,
                (HEIGHT - CARD_INSET - 1) * CARD_SS - 1,
            ),
            radius=(CARD_RADIUS - 1) * CARD_SS,
            outline=255,
            width=2 * CARD_SS,
        )

    frame = Image.new("RGBA", (WIDTH, HEIGHT), (*LINE, 255))
    frame.putalpha(_supersampled(ring))
    return frame


def render(language: str) -> Image.Image:
    copy = CARD_COPY[language]
    canvas = _background()
    draw = ImageDraw.Draw(canvas)

    # Eyebrow: sage dot, wordmark, and the language this card is written in.
    label_font = get_bold(19)
    dot_y = 116
    draw.ellipse((MARGIN, dot_y - 4, MARGIN + 8, dot_y + 4), fill=SAGE)
    wordmark_width = _tracked(draw, (MARGIN + 24, 106), "NIKO", label_font, DIM, 4.2)
    draw.line(
        (MARGIN + 24 + wordmark_width + 20, dot_y, MARGIN + 24 + wordmark_width + 52, dot_y),
        fill=LINE,
        width=1,
    )
    _tracked(
        draw,
        (MARGIN + 24 + wordmark_width + 72, 106),
        str(copy["label"]),
        label_font,
        MUTED,
        3.0,
    )
    _tracked(
        draw,
        (WIDTH - MARGIN - _tracked_width("DISCORD COMPANION", label_font, 3.0), 106),
        "DISCORD COMPANION",
        label_font,
        DIM,
        3.0,
    )

    # Headline: two lines at one size, so the block reads as a single statement.
    first, second = copy["headline"]  # type: ignore[misc]
    headline_size = 84
    while headline_size > 32:
        headline_font = get_bold(headline_size)
        if max(
            font_getlength(headline_font, str(first)),
            font_getlength(headline_font, str(second)),
        ) <= CONTENT_W:
            break
        headline_size -= 2
    headline_font = get_bold(headline_size)
    draw.text((MARGIN, 322), str(first), font=headline_font, fill=INK, anchor="ls")
    draw.text((MARGIN, 416), str(second), font=headline_font, fill=INK, anchor="ls")

    # Tagline, on a narrower measure than the headline.
    tagline_font, tagline_lines = _fit_wrapped(str(copy["tagline"]), 29, 1080, 2)
    for index, line in enumerate(tagline_lines):
        draw.text(
            (MARGIN, 480 + index * 40), line, font=tagline_font, fill=MUTED, anchor="ls"
        )

    # Three feature rows, separated by hairlines rather than decorated.
    row_font = get_reg(26)
    rows = copy["rows"]
    top = 588
    row_height = 62
    for index, label in enumerate(rows):  # type: ignore[union-attr]
        y = top + index * row_height
        draw.line(
            (MARGIN, y, MARGIN + CONTENT_W, y),
            fill=LINE_SOFT if index else LINE,
            width=1,
        )
        draw.ellipse((MARGIN + 2, y + 26, MARGIN + 10, y + 34), fill=SAGE)
        draw.text(
            (MARGIN + 32, y + 30), str(label), font=row_font, fill=MUTED, anchor="lm"
        )
        if index == len(rows) - 1:  # type: ignore[arg-type]
            draw.line((MARGIN, y + row_height, MARGIN + CONTENT_W, y + row_height), fill=LINE, width=1)

    # Footer: where the card links to, in the same quiet type as the eyebrow.
    footer_font = get_bold(17)
    footer_y = 812
    _tracked(draw, (MARGIN, footer_y), "NIKO.SRYZE.CC", footer_font, DIM, 3.2)
    right = "DASHBOARD  /  COMMANDS  /  DOCS"
    _tracked(
        draw,
        (WIDTH - MARGIN - _tracked_width(right, footer_font, 2.6), footer_y),
        right,
        footer_font,
        DIM,
        2.6,
    )

    # The frame is composite over the artwork, then the mask cuts the corners
    # away, so the saved PNG is a rounded card on transparency.
    canvas.alpha_composite(_card_frame())
    canvas.putalpha(_card_mask())
    return canvas


def _tracked_width(text: str, font: ImageFont.ImageFont, tracking: float) -> float:
    """The width ``_tracked`` will use, without drawing the text."""
    return sum(font_getlength(font, character) for character in text) + tracking * (len(text) - 1)


# ── Assembly ────────────────────────────────────────────────────────────────
def generate(out_dir: Path = OUT_DIR) -> list[Path]:
    """Write one card per language, plus the mirrored copy the bot serves."""
    written: list[Path] = []
    for language in CARD_COPY:
        # RGBA on purpose: the corners outside the card stay transparent.
        card = render(language)

        path = out_dir / f"{language}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        card.save(path, format="PNG", optimize=True)
        written.append(path)

        mirror = DIST_DIR / f"{language}.png"
        mirror.parent.mkdir(parents=True, exist_ok=True)
        card.save(mirror, format="PNG", optimize=True)
        written.append(mirror)

    return written


def main() -> None:
    for path in generate():
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
