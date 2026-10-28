#!/usr/bin/env python3
"""Generate the animated loading cards for Niko's economy image cards.

Each economy card type gets its own looping GIF so a command can show a
card-shaped placeholder from the public website while the real PNG renders:

    https://niko.sryze.cc/assets/loading-cards/economy/<card type>.gif

The artwork deliberately reuses the palette, the canvas helpers and the layout
constants from ``utils.image.economy_card``, so a loading card is not just the
same graphite, steel and sage card the finished image becomes — its skeleton
blocks sit where the finished card draws its text, and the labels that never
change ("NET WORTH", "CASH", "BANK", "VAULT TIER", …) are rendered for real.
That keeps the loading → finished transition from visually shifting.

The shop card grows with the number of items, so it gets one GIF per row count
the command can produce (``shop.gif`` for the whole catalogue, ``shop-<rows>.gif``
per category). Both this script and the bot's loading view read
``utils.economy_jobs.shop_loading_row_counts()``, so adding an item keeps the
placeholder and the finished card the same height.

The files are written into the Vite ``public`` directory and copied into the
served website build; ``npm run build`` runs this script first through the
package's ``prebuild`` hook.

Run it directly with:

    python3 scripts/generate_economy_loading_cards.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils.economy_jobs import shop_loading_row_counts  # noqa: E402
from utils.image._font_resolver import (  # noqa: E402
    draw_text_with_fallback,
    font_getlength,
    textlength_with_fallback,
)
from utils.image.economy_card import (  # noqa: E402
    ACCENT,
    ACCENT_BRIGHT,
    BALANCE_H,
    CARD_W,
    DIM,
    INV_W,
    INK,
    LB_W,
    MUTED,
    PANEL_BORDER,
    REWARD_H,
    REWARD_W,
    SAGE,
    SHOP_HEADER_H,
    SHOP_ROW_H,
    SHOP_W,
    _bold,
    _make_canvas,
    _reg,
    _rounded_mask,
    shop_card_height,
)

OUT_DIR = ROOT / "web" / "public" / "assets" / "loading-cards" / "economy"
# The built website is committed and served by Flask, so mirroring the GIFs
# there makes them available to the running bot before the next full build.
DIST_DIR = ROOT / "src" / "website" / "dist" / "assets" / "loading-cards" / "economy"

FRAME_COUNT = 20
FRAME_MS = 90

# type: (width, height, footer label)
CARD_LAYOUTS: dict[str, tuple[int, int, str]] = {
    "balance": (CARD_W, BALANCE_H, "wallet"),
    "reward": (REWARD_W, REWARD_H, "reward"),
    # The full-catalogue shop card; category variants are sized in `generate`.
    "shop": (SHOP_W, shop_card_height(max(shop_loading_row_counts())), "shop"),
    "inventory": (INV_W, 700, "inventory"),
    "leaderboard": (LB_W, 830, "leaderboard"),
}

# (inset, top, bold size) — the same wordmark geometry each finished card uses.
WORDMARK: dict[str, tuple[int, int, int]] = {
    "balance": (36, 28, 18),
    "reward": (36, 22, 16),
    "shop": (38, 28, 17),
    "inventory": (38, 28, 17),
    "leaderboard": (36, 28, 16),
}

# Footer text that also appears on the finished card, so it can stay put while
# the rest of the placeholder resolves.
FOOTER_TEXT: dict[str, str] = {
    "leaderboard": "use ‹ › below to navigate",
}

SKELETON = (38, 41, 47, 235)
SKELETON_EDGE = (45, 48, 53, 235)
SHIMMER = (213, 217, 223, 44)

# GIF transparency is a single palette slot; reserve the last one for the
# cut-out corners so the card floats on whatever background it is shown on.
TRANSPARENT_INDEX = 255


def _skeleton_panel(
    canvas: Image.Image,
    x: float,
    y: float,
    width: float,
    height: float,
    radius: int,
    t: float,
    delay: float = 0.0,
) -> None:
    """A rounded placeholder block with a light band sweeping across it."""
    w = max(2, int(width))
    h = max(2, int(height))
    box = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(box)
    r = max(1, min(int(radius), h // 2))
    draw.rounded_rectangle(
        [0, 0, w - 1, h - 1],
        radius=r,
        fill=SKELETON,
        outline=SKELETON_EDGE,
        width=1,
    )

    band_w = max(18, w // 3)
    cx = int(-band_w + (w + band_w) * (((t + delay) % 1.0)))
    shimmer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shimmer)
    sd.rounded_rectangle(
        [cx, 1, cx + band_w, h - 1],
        radius=max(1, min(8, r)),
        fill=SHIMMER,
    )
    shimmer.putalpha(
        Image.composite(
            shimmer.getchannel("A"),
            Image.new("L", (w, h), 0),
            _rounded_mask((w, h), r),
        )
    )
    box = Image.alpha_composite(box, shimmer)
    canvas.alpha_composite(box, (int(x), int(y)))


def _skeleton_circle(
    canvas: Image.Image,
    cx: float,
    cy: float,
    radius: float,
    t: float,
    delay: float = 0.0,
) -> None:
    """A circular avatar placeholder with a soft breathing highlight."""
    r = max(2, int(radius))
    size = r * 2
    avatar = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(avatar)
    draw.ellipse(
        [0, 0, size - 1, size - 1],
        fill=SKELETON,
        outline=SKELETON_EDGE,
        width=3,
    )
    pulse = int(22 + 26 * abs(((t + delay) % 1.0) * 2 - 1))
    draw.arc(
        [4, 4, size - 5, size - 5],
        start=int(-90 + 360 * ((t + delay) % 1.0)),
        end=int(-90 + 360 * ((t + delay) % 1.0) + 90),
        fill=(*ACCENT_BRIGHT, pulse),
        width=3,
    )
    canvas.alpha_composite(avatar, (int(cx - r), int(cy - r)))


def _label(
    canvas: Image.Image,
    xy: tuple[float, float],
    text: str,
    *,
    size: int = 13,
    bold: bool = False,
    fill=DIM,
) -> float:
    """Draw one of the finished card's static labels in place."""
    draw = ImageDraw.Draw(canvas)
    return draw_text_with_fallback(draw, xy, text, size=size, bold=bold, fill=fill)


def _right_label(
    canvas: Image.Image,
    right: float,
    y: float,
    text: str,
    *,
    size: int = 13,
    bold: bool = False,
    fill=DIM,
) -> float:
    """Draw a static label right-aligned to *right*, returning its width."""
    width = textlength_with_fallback(text, size=size, bold=bold)
    _label(canvas, (right - width, y), text, size=size, bold=bold, fill=fill)
    return width


def _wordmark(canvas: Image.Image, width: int, card_type: str) -> None:
    inset, top, size = WORDMARK[card_type]
    draw = ImageDraw.Draw(canvas)
    draw.text((inset, top), "NIKO ECONOMY", fill=ACCENT, font=_bold(size))
    label = card_type.upper()
    label_w = int(font_getlength(_reg(11), label))
    draw.text(
        (width - inset - label_w, top + 3),
        label,
        fill=DIM,
        font=_reg(11),
    )


def _footer(
    canvas: Image.Image,
    width: int,
    height: int,
    label: str,
    t: float,
    text: str | None = None,
) -> None:
    draw = ImageDraw.Draw(canvas)
    caption = text or f"Preparing your {label} card…"
    draw_text_with_fallback(draw, (36, height - 40), caption, size=14, fill=DIM)

    # Spinning arc and label, right aligned with the card padding.
    radius = 9
    cx, cy = width - 50, height - 31
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        outline=PANEL_BORDER,
        width=2,
    )
    start = int(t * 360)
    draw.arc(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        start=start,
        end=start + 250,
        fill=ACCENT_BRIGHT,
        width=3,
    )
    label_w = int(font_getlength(_bold(11), "LOADING"))
    draw.text(
        (cx - radius - 10 - label_w, cy - 8),
        "LOADING",
        fill=ACCENT,
        font=_bold(11),
    )


def _draw_balance(canvas: Image.Image, width: int, height: int, t: float) -> None:
    # Title, and the leaderboard-rank pill in the top-right corner.
    _skeleton_panel(canvas, 36, 54, 280, 34, 9, t, 0.04)
    _skeleton_panel(canvas, width - 236, 36, 200, 28, 14, t, 0.08)

    # Avatar, name and the job/streak line.
    _skeleton_circle(canvas, 98, 168, 58, t, 0.06)
    _skeleton_panel(canvas, 178, 116, 260, 28, 9, t, 0.10)
    _skeleton_panel(canvas, 178, 154, 200, 15, 7, t, 0.14)

    # Net worth block, matching the finished card's label.
    _right_label(canvas, width - 40, 122, "NET WORTH")
    _skeleton_panel(canvas, width - 210, 142, 170, 28, 8, t, 0.18)

    # Stat chips: the labels are static, so they are already the real ones.
    chip_y, chip_h, gap = 254, 78, 14
    chip_w = (width - 80 - gap * 2) // 3
    for index, label in enumerate(("CASH", "BANK", "VAULT TIER")):
        x = 40 + index * (chip_w + gap)
        delay = 0.05 * index
        _skeleton_panel(canvas, x, chip_y, chip_w, chip_h, 16, t, delay)
        _label(canvas, (x + 16, chip_y + 11), label, size=13, fill=DIM)
        _skeleton_panel(
            canvas, x + 16, chip_y + 32, min(150, chip_w - 32), 26, 7, t, delay + 0.12,
        )

    # Level line and XP progress bar.
    _label(canvas, (40, 332), "LEVEL", size=15, bold=True, fill=INK)
    _skeleton_panel(canvas, 102, 332, 46, 15, 6, t, 0.22)
    _skeleton_panel(canvas, width - 160, 332, 120, 13, 6, t, 0.26)
    _skeleton_panel(canvas, 40, 354, width - 80, 16, 8, t, 0.30)


def _draw_reward(canvas: Image.Image, width: int, height: int, t: float) -> None:
    _skeleton_circle(canvas, 91, 115, 55, t)
    _skeleton_panel(canvas, 170, 64, 320, 28, 9, t, 0.06)
    _skeleton_panel(canvas, 170, 102, 240, 16, 7, t, 0.12)
    # The footer is free-form text on the finished card, so the loading caption
    # from `_footer` stands in for it at the same baseline.

    panel_x, panel_y, panel_w, panel_h = width - 316, 132, 280, 90
    _skeleton_panel(canvas, panel_x, panel_y, panel_w, panel_h, 18, t, 0.18)
    _skeleton_panel(canvas, panel_x + 58, panel_y + 18, panel_w - 116, 32, 10, t, 0.24)

    # The "new balance:" caption stays, only the number is pending.
    caption = "new balance:"
    caption_w = textlength_with_fallback(caption, size=13)
    value_w = 72
    gap = 8
    left = panel_x + (panel_w - (caption_w + gap + value_w)) / 2
    _label(canvas, (left, panel_y + 60), caption, size=13, fill=MUTED)
    _skeleton_panel(canvas, left + caption_w + gap, panel_y + 61, value_w, 11, 5, t, 0.30)


def _shop_rows(height: int) -> int:
    return max(1, (height - SHOP_HEADER_H - 42) // SHOP_ROW_H)


def _draw_shop(canvas: Image.Image, width: int, height: int, t: float) -> None:
    # The shop title never changes, so it is drawn rather than skeletonised.
    _label(canvas, (38, 54), "Niko's Shop", size=34, bold=True, fill=INK)

    # Balance line: static caption, pending amount.
    balance_w = _right_label(canvas, width - 38, 41, "Balance", size=17, bold=True, fill=ACCENT_BRIGHT)
    _skeleton_panel(canvas, width - 38 - balance_w - 96, 42, 88, 18, 7, t, 0.10)
    _skeleton_panel(canvas, 38, 100, 430, 14, 7, t, 0.08)

    y = SHOP_HEADER_H
    for index in range(_shop_rows(height)):
        delay = 0.03 * index
        _skeleton_panel(canvas, 28, y, width - 56, SHOP_ROW_H - 8, 14, t, delay)
        _skeleton_panel(canvas, 48, y + 15, 20, 20, 6, t, delay + 0.04)
        _skeleton_panel(canvas, 76, y + 15, 240, 20, 7, t, delay + 0.08)
        _skeleton_panel(canvas, 48, y + 43, 360, 12, 6, t, delay + 0.12)
        _skeleton_panel(canvas, width - 190, y + 16, 100, 18, 7, t, delay + 0.16)
        _label(canvas, (width - 190, y + 43), "sell", size=12, fill=SAGE)
        _skeleton_panel(canvas, width - 190 + 30, y + 45, 44, 10, 5, t, delay + 0.20)
        y += SHOP_ROW_H


def _draw_inventory(canvas: Image.Image, width: int, height: int, t: float) -> None:
    _skeleton_panel(canvas, 38, 54, 360, 34, 9, t, 0.04)
    balance_w = _right_label(canvas, width - 38, 41, "Balance", size=17, bold=True, fill=ACCENT_BRIGHT)
    _skeleton_panel(canvas, width - 38 - balance_w - 96, 42, 88, 18, 7, t, 0.10)

    # Section heading, then the item rows at the finished card's pitch.
    _skeleton_panel(canvas, 48, 130, 150, 20, 7, t, 0.16)

    y, row_h = 170, 56
    rows = max(1, (height - y - 42) // row_h)
    for index in range(rows):
        delay = 0.03 * index
        _skeleton_panel(canvas, 28, y, width - 56, row_h - 8, 14, t, delay)
        _skeleton_panel(canvas, 48, y + 10, 210, 18, 6, t, delay + 0.06)
        _skeleton_panel(canvas, 48, y + 34, 320, 12, 5, t, delay + 0.10)
        _skeleton_panel(canvas, width - 116, y + 12, 48, 17, 6, t, delay + 0.14)
        y += row_h


def _draw_leaderboard(canvas: Image.Image, width: int, height: int, t: float) -> None:
    _skeleton_panel(canvas, 36, 54, 320, 28, 9, t, 0.02)
    _skeleton_panel(canvas, width - 150, 60, 114, 16, 6, t, 0.10)

    y, row_h = 112, 66
    rows = max(1, (height - y - 60) // row_h)
    for index in range(rows):
        delay = 0.02 * index
        _skeleton_panel(canvas, 28, y, width - 56, row_h - 10, 14, t, delay)
        _skeleton_panel(canvas, 52, y + 18, 28, 20, 6, t, delay + 0.04)
        _skeleton_circle(canvas, 112, y + 28, 20, t, delay + 0.06)
        _skeleton_panel(canvas, 146, y + 18, 260, 18, 7, t, delay + 0.08)
        _skeleton_panel(canvas, width - 142, y + 18, 90, 18, 7, t, delay + 0.12)
        y += row_h


_DRAWERS = {
    "balance": _draw_balance,
    "reward": _draw_reward,
    "shop": _draw_shop,
    "inventory": _draw_inventory,
    "leaderboard": _draw_leaderboard,
}


def _loading_frame(base: Image.Image, width: int, height: int, card_type: str, t: float) -> Image.Image:
    canvas = base.copy()
    _wordmark(canvas, width, card_type)
    _DRAWERS[card_type](canvas, width, height, t)
    _footer(
        canvas,
        width,
        height,
        CARD_LAYOUTS[card_type][2],
        t,
        FOOTER_TEXT.get(card_type),
    )

    frame = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    frame.alpha_composite(canvas)
    return frame


def _to_palette(frame: Image.Image, palette: Image.Image) -> Image.Image:
    """Map an RGBA frame onto the shared palette, keeping its alpha as a key."""
    quantized = frame.convert("RGB").quantize(palette=palette, dither=Image.NONE)
    transparent = frame.getchannel("A").point(lambda value: 255 if value < 128 else 0)
    quantized.paste(TRANSPARENT_INDEX, mask=transparent)
    return quantized


def _save_gif(frames: list[Image.Image], path: Path) -> None:
    """Write a shared-palette GIF so the size stays reasonable."""
    palette = frames[0].convert("RGB").quantize(
        colors=TRANSPARENT_INDEX, method=Image.MEDIANCUT
    )
    paletted = [_to_palette(frame, palette) for frame in frames]
    path.parent.mkdir(parents=True, exist_ok=True)
    paletted[0].save(
        path,
        save_all=True,
        append_images=paletted[1:],
        duration=FRAME_MS,
        loop=0,
        optimize=True,
        disposal=2,
        transparency=TRANSPARENT_INDEX,
    )


def _shop_files() -> dict[str, int]:
    """Loading GIF file name → item rows it should be drawn for.

    The whole catalogue keeps the plain ``shop.gif`` name; each category gets
    ``shop-<rows>.gif``. The bot's ``_shop_loading_file`` resolves the same
    mapping at runtime.
    """
    counts = shop_loading_row_counts()
    largest = max(counts)
    return {
        ("shop" if rows == largest else f"shop-{rows}"): rows
        for rows in counts
    }


def _render_card(card_type: str, width: int, height: int, file_name: str, out_dir: Path) -> Path:
    base = _make_canvas(width, height, radius=28)
    frames = [
        _loading_frame(base, width, height, card_type, index / FRAME_COUNT)
        for index in range(FRAME_COUNT)
    ]
    path = out_dir / file_name
    _save_gif(frames, path)
    print(f"  {path.stem:<12} {width}x{height}  {path.relative_to(ROOT)}  {path.stat().st_size / 1024:.0f} KB")

    if DIST_DIR.parent.is_dir():
        mirror = DIST_DIR / file_name
        mirror.parent.mkdir(parents=True, exist_ok=True)
        mirror.write_bytes(path.read_bytes())
    return path


def generate(out_dir: Path = OUT_DIR) -> list[Path]:
    written: list[Path] = []
    for card_type, (width, height, _label) in CARD_LAYOUTS.items():
        if card_type == "shop":
            continue
        written.append(_render_card(card_type, width, height, f"{card_type}.gif", out_dir))
    for file_name, rows in _shop_files().items():
        written.append(
            _render_card("shop", SHOP_W, shop_card_height(rows), f"{file_name}.gif", out_dir)
        )
    return written


def main() -> None:
    print("Economy loading cards")
    written = generate()
    print(f"Wrote {len(written)} animated loading cards.")


if __name__ == "__main__":
    main()
