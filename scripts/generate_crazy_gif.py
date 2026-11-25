#!/usr/bin/env python3
"""Generate the infinitely scrolling GIF behind ``/crazy``.

The command replies with this artwork instead of its old text wall:

    https://niko.sryze.cc/assets/crazy.gif

The animation is one repeating block of the "Crazy? I was crazy once" text that
travels straight up the canvas forever. The block is drawn once into a tile
whose height is exactly the scroll period, and every frame simply pastes that
tile at a different offset — so the last frame hands back to the first with no
jump and the GIF loops cleanly. Nothing moves sideways: the text only travels
vertically.

The background stays fully transparent (the frame alpha is written into the
palette's transparency slot, like the loading cards), so Discord and the site
can show it on any surface. The file is written into the Vite ``public``
directory and mirrored into the served website build.

Run it directly with:

    python3 scripts/generate_crazy_gif.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "web" / "public" / "assets" / "crazy.gif"
# The built website is committed and served by the bot, so mirroring the GIF
# there makes /crazy work before the next full web build.
DIST_PATH = ROOT / "src" / "website" / "dist" / "assets" / "crazy.gif"

FONT_PATH = ROOT / "web" / "public" / "fonts" / "cherry-bomb-one.ttf"

# ── Frame geometry ──────────────────────────────────────────────────────────
# 480x560 sits comfortably in a Discord media gallery without being heavy.
WIDTH = 480
HEIGHT = 560
# Everything is drawn at 2x and scaled down, which keeps the letter shapes
# clean even though GIF transparency itself is only one bit.
SUPERSAMPLE = 2
# 288 frames at 20 ms is a 5.76 s loop at 50 fps: the text advances about one
# pixel per frame, which reads as continuous motion instead of a stutter.
FRAME_COUNT = 288
FRAME_MS = 20
CONTENT_WIDTH = WIDTH - 96
# Frames are drawn with a few transparent pixels of margin and cropped back
# afterwards, so the downscale filter never mixes the canvas edge into the
# visible rows: each frame then is an exact whole-pixel shift of the last.
MARGIN = 8

# ── Palette (the site's own tokens) ─────────────────────────────────────────
INK = (244, 245, 247)
ACCENT = (139, 213, 177)
DIM = (90, 97, 107)
OUTLINE = (5, 6, 7)
# Index 0 is the transparency slot, so it must stay a colour the art never
# uses as a solid fill.
PALETTE = [OUTLINE, INK, ACCENT, DIM]

# (text, size, colour) — the block that repeats, top to bottom.
LINES: tuple[tuple[str, int, tuple[int, int, int]], ...] = (
    ("Crazy?", 62, ACCENT),
    ("I was crazy once.", 40, INK),
    ("They locked me in a room.", 40, INK),
    ("A rubber room.", 40, INK),
    ("A rubber room with rats.", 40, INK),
    ("And rats make me crazy.", 40, INK),
)
# Line boxes are this much taller than their type size, which leaves room for
# ascenders, descenders and the dark outline.
LINE_BOX = 1.34
# The dotted rule between two blocks.
DOT_RULE_HEIGHT = 46
DOT_RADIUS = 5
DOT_GAP = 20


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype(str(FONT_PATH), size)
    except OSError:  # pragma: no cover - only when the font file is missing
        return ImageFont.load_default(size=max(8, size // 2))


def _fitted(text: str, size: int) -> tuple[ImageFont.ImageFont, int]:
    """Shrink a line until it fits the content width, so nothing clips."""
    font = _font(size * SUPERSAMPLE)
    limit = CONTENT_WIDTH * SUPERSAMPLE
    while size > 18 and font.getlength(text) > limit:
        size -= 1
        font = _font(size * SUPERSAMPLE)
    return font, size


def _strip() -> Image.Image:
    """One complete block of text, tiled vertically by every frame."""
    boxes: list[tuple[str, ImageFont.ImageFont, int, tuple[int, int, int]]] = []
    for text, size, color in LINES:
        font, fitted = _fitted(text, size)
        boxes.append((text, font, round(fitted * LINE_BOX * SUPERSAMPLE), color))

    height = sum(box[2] for box in boxes) + DOT_RULE_HEIGHT * SUPERSAMPLE
    strip = Image.new("RGBA", (WIDTH * SUPERSAMPLE, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(strip)
    center = strip.width // 2
    y = 0

    for text, font, box_height, color in boxes:
        stroke = max(2, round(font.size / 16))
        draw.text(
            (center, y + box_height // 2),
            text,
            font=font,
            fill=color,
            anchor="mm",
            stroke_width=stroke,
            stroke_fill=OUTLINE,
        )
        y += box_height

    # Three dots mark where one block ends and the next begins.
    dot_y = y + DOT_RULE_HEIGHT * SUPERSAMPLE // 2
    for offset in (-DOT_GAP * SUPERSAMPLE, 0, DOT_GAP * SUPERSAMPLE):
        radius = DOT_RADIUS * SUPERSAMPLE
        draw.ellipse(
            [center + offset - radius, dot_y - radius, center + offset + radius, dot_y + radius],
            fill=DIM,
        )

    # The scroll moves in whole output pixels, so the tile height has to be a
    # whole number of them: pad by one supersampled row when it is odd.
    if strip.height % SUPERSAMPLE:
        padded = Image.new("RGBA", (strip.width, strip.height + 1), (0, 0, 0, 0))
        padded.alpha_composite(strip)
        strip = padded
    return strip


def _frame(strip: Image.Image, index: int) -> Image.Image:
    """Draw the tile at this frame's vertical offset.

    The offset is rounded in output pixels and only then scaled up, so every
    frame is an exact whole-pixel shift of the one before it. Moving by half a
    pixel instead would resample the glyphs every frame and make the edges
    shimmer.
    """
    period = strip.height // SUPERSAMPLE
    offset = round(index * period / FRAME_COUNT) * SUPERSAMPLE

    wide, tall = (WIDTH + 2 * MARGIN) * SUPERSAMPLE, (HEIGHT + 2 * MARGIN) * SUPERSAMPLE
    canvas = Image.new("RGBA", (wide, tall), (0, 0, 0, 0))
    y = MARGIN * SUPERSAMPLE - (offset % strip.height)
    while y < canvas.height:
        canvas.alpha_composite(strip, (0, y))
        y += strip.height

    # Resize in premultiplied alpha so the transparent surroundings cannot
    # bleed a dark halo into the letter edges, then drop the margin.
    scaled = canvas.convert("RGBa").resize((wide // SUPERSAMPLE, tall // SUPERSAMPLE), Image.LANCZOS)
    frame = scaled.crop((MARGIN, MARGIN, MARGIN + WIDTH, MARGIN + HEIGHT)).convert("RGBA")
    frame.putalpha(frame.getchannel("A").point(lambda value: 255 if value >= 128 else 0))
    return frame


def _to_palette(frame: Image.Image) -> Image.Image:
    palette = Image.new("P", (1, 1))
    flat: list[int] = []
    for red, green, blue in PALETTE:
        flat += [red, green, blue]
    palette.putpalette(flat + [0, 0, 0] * (256 - len(PALETTE)))

    quantized = frame.convert("RGB").quantize(palette=palette, dither=Image.NONE)
    clear = frame.getchannel("A").point(lambda value: 255 if value == 0 else 0)
    quantized.paste(0, mask=clear)
    return quantized


def generate(out_path: Path = OUT_PATH) -> Path:
    strip = _strip()
    frames = [_to_palette(_frame(strip, index)) for index in range(FRAME_COUNT)]

    # A clean loop is the point of the piece, so prove the frame after the last
    # one is pixel-identical to the first instead of trusting the maths.
    seam = _frame(strip, FRAME_COUNT).tobytes()
    if seam != _frame(strip, 0).tobytes():
        raise RuntimeError("the scroll does not close cleanly on the loop seam")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_MS,
        loop=0,
        optimize=True,
        disposal=2,
        transparency=0,
    )

    if DIST_PATH.parent.is_dir():
        DIST_PATH.write_bytes(out_path.read_bytes())

    print(
        f"  crazy.gif  {WIDTH}x{HEIGHT}  {FRAME_COUNT} frames @ {FRAME_MS} ms  "
        f"period {strip.height // SUPERSAMPLE}px  {out_path.stat().st_size / 1024:.0f} KB"
    )
    return out_path


def main() -> None:
    print("Crazy scroll")
    generate()
    print("Wrote web/public/assets/crazy.gif (mirrored into the website build).")

if __name__ == "__main__":
    main()
