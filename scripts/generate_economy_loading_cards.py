#!/usr/bin/env python3
"""Generate the animated loading cards for Niko's economy image cards.

Each economy card type gets its own looping GIF so a command can show a
card-shaped placeholder from the public website while the real PNG renders:

    https://niko.sryze.cc/assets/loading-cards/economy/<card type>.gif

The artwork deliberately reuses the palette and canvas helpers from
``utils.image.economy_card`` so a loading card is the same graphite, steel and
sage card the finished image becomes. The files are written into the Vite
``public`` directory and copied into the served website build; ``npm run
build`` runs this script first through the package's ``prebuild`` hook.

Run it directly with:

    python3 scripts/generate_economy_loading_cards.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils.image._font_resolver import font_getlength  # noqa: E402
from utils.image.economy_card import (  # noqa: E402
    ACCENT,
    ACCENT_BRIGHT,
    DIM,
    PANEL_BORDER,
    _bold,
    _make_canvas,
    _reg,
    _rounded_mask,
)

OUT_DIR = ROOT / "web" / "public" / "assets" / "loading-cards" / "economy"
# The built website is committed and served by Flask, so mirroring the GIFs
# there makes them available to the running bot before the next full build.
DIST_DIR = ROOT / "src" / "website" / "dist" / "assets" / "loading-cards" / "economy"

FRAME_COUNT = 20
FRAME_MS = 90

# type: (width, height, footer label)
CARD_LAYOUTS: dict[str, tuple[int, int, str]] = {
    "balance": (820, 380, "wallet"),
    "reward": (820, 280, "reward"),
    "shop": (900, 760, "shop"),
    "inventory": (900, 700, "inventory"),
    "leaderboard": (820, 830, "leaderboard"),
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


def _wordmark(canvas: Image.Image, width: int, card_type: str, *, inset: int = 36, top: int = 22) -> None:
    draw = ImageDraw.Draw(canvas)
    draw.text((inset, top), "NIKO ECONOMY", fill=ACCENT, font=_bold(16))
    label = card_type.upper()
    label_w = int(font_getlength(_reg(11), label))
    draw.text(
        (width - inset - label_w, top + 3),
        label,
        fill=DIM,
        font=_reg(11),
    )


def _footer(canvas: Image.Image, width: int, height: int, label: str, t: float) -> None:
    draw = ImageDraw.Draw(canvas)
    draw.text((36, height - 40), f"Preparing your {label} card…", fill=DIM, font=_reg(14))

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
    _skeleton_circle(canvas, 91, 118, 55, t)
    _skeleton_panel(canvas, 160, 74, 280, 24, 8, t, 0.06)
    _skeleton_panel(canvas, 160, 110, 210, 14, 7, t, 0.10)
    _skeleton_panel(canvas, width - 250, 76, 210, 14, 7, t, 0.14)
    _skeleton_panel(canvas, width - 250, 100, 150, 12, 6, t, 0.18)

    chip_y, chip_h, gap = 184, 82, 16
    chip_w = (width - 80 - gap * 2) // 3
    for index in range(3):
        x = 40 + index * (chip_w + gap)
        _skeleton_panel(canvas, x, chip_y, chip_w, chip_h, 16, t, 0.05 * index)
        _skeleton_panel(canvas, x + 18, chip_y + 18, 54, 9, 5, t, 0.05 * index + 0.10)
        _skeleton_panel(
            canvas,
            x + 18,
            chip_y + 42,
            chip_w - 92,
            18,
            7,
            t,
            0.05 * index + 0.16,
        )

    _skeleton_panel(canvas, 40, 284, 64, 12, 6, t, 0.20)
    _skeleton_panel(canvas, 40, 304, width - 80, 14, 7, t, 0.25)


def _draw_reward(canvas: Image.Image, width: int, height: int, t: float) -> None:
    _skeleton_circle(canvas, 91, 114, 55, t)
    _skeleton_panel(canvas, 160, 70, 320, 24, 8, t, 0.06)
    _skeleton_panel(canvas, 160, 106, 240, 14, 7, t, 0.12)
    _skeleton_panel(canvas, 36, 190, 280, 12, 6, t, 0.20)

    panel_x, panel_y, panel_w, panel_h = width - 316, 142, 280, 90
    _skeleton_panel(canvas, panel_x, panel_y, panel_w, panel_h, 18, t, 0.18)
    _skeleton_panel(canvas, panel_x + 58, panel_y + 18, panel_w - 116, 32, 10, t, 0.24)
    _skeleton_panel(canvas, panel_x + 82, panel_y + 60, panel_w - 164, 11, 6, t, 0.30)


def _draw_shop(canvas: Image.Image, width: int, height: int, t: float) -> None:
    _skeleton_panel(canvas, 38, 58, 300, 30, 9, t, 0.02)
    _skeleton_panel(canvas, 38, 100, 430, 14, 7, t, 0.08)
    _skeleton_panel(canvas, width - 238, 44, 200, 18, 7, t, 0.12)

    y, row_h = 132, 88
    for index in range(6):
        _skeleton_panel(canvas, 28, y, width - 56, row_h - 10, 14, t, 0.03 * index)
        _skeleton_panel(canvas, 48, y + 16, 36, 36, 10, t, 0.03 * index + 0.04)
        _skeleton_panel(canvas, 98, y + 14, 240, 19, 7, t, 0.03 * index + 0.08)
        _skeleton_panel(canvas, 98, y + 42, 360, 12, 6, t, 0.03 * index + 0.12)
        _skeleton_panel(canvas, width - 242, y + 14, 100, 19, 7, t, 0.03 * index + 0.16)
        _skeleton_panel(canvas, width - 242, y + 44, 62, 10, 5, t, 0.03 * index + 0.20)
        y += row_h


def _draw_inventory(canvas: Image.Image, width: int, height: int, t: float) -> None:
    _skeleton_panel(canvas, 38, 58, 360, 30, 9, t, 0.02)
    _skeleton_panel(canvas, width - 238, 44, 200, 18, 7, t, 0.12)
    _skeleton_panel(canvas, 48, 128, 150, 18, 7, t, 0.16)

    y, row_h = 160, 62
    for index in range(7):
        _skeleton_panel(canvas, 28, y, width - 56, row_h - 10, 14, t, 0.03 * index)
        _skeleton_panel(canvas, 48, y + 12, 210, 17, 6, t, 0.03 * index + 0.06)
        _skeleton_panel(canvas, 48, y + 36, 320, 10, 5, t, 0.03 * index + 0.10)
        _skeleton_panel(canvas, width - 116, y + 12, 48, 17, 6, t, 0.03 * index + 0.14)
        y += row_h


def _draw_leaderboard(canvas: Image.Image, width: int, height: int, t: float) -> None:
    _skeleton_panel(canvas, 36, 60, 320, 28, 9, t, 0.02)
    _skeleton_panel(canvas, width - 150, 62, 114, 16, 6, t, 0.10)

    y, row_h = 112, 76
    for index in range(8):
        _skeleton_panel(canvas, 28, y, width - 56, 66, 14, t, 0.02 * index)
        _skeleton_panel(canvas, 52, y + 22, 28, 20, 6, t, 0.02 * index + 0.04)
        _skeleton_circle(canvas, 118, y + 33, 24, t, 0.02 * index + 0.06)
        _skeleton_panel(canvas, 156, y + 16, 260, 18, 7, t, 0.02 * index + 0.08)
        _skeleton_panel(canvas, width - 150, y + 18, 90, 18, 7, t, 0.02 * index + 0.12)
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
    _wordmark(canvas, width, card_type, inset=38 if width >= 900 else 36, top=28 if width >= 900 else 22)
    _DRAWERS[card_type](canvas, width, height, t)
    _footer(canvas, width, height, CARD_LAYOUTS[card_type][2], t)

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


def generate(out_dir: Path = OUT_DIR) -> list[Path]:
    written: list[Path] = []
    for card_type, (width, height, _label) in CARD_LAYOUTS.items():
        base = _make_canvas(width, height, radius=28)
        frames = [
            _loading_frame(base, width, height, card_type, index / FRAME_COUNT)
            for index in range(FRAME_COUNT)
        ]
        path = out_dir / f"{card_type}.gif"
        _save_gif(frames, path)
        written.append(path)
        print(f"  {card_type:<12} {width}x{height}  {path.relative_to(ROOT)}  {path.stat().st_size / 1024:.0f} KB")

        if DIST_DIR.parent.is_dir():
            mirror = DIST_DIR / f"{card_type}.gif"
            mirror.parent.mkdir(parents=True, exist_ok=True)
            mirror.write_bytes(path.read_bytes())
    return written


def main() -> None:
    print("Economy loading cards")
    written = generate()
    print(f"Wrote {len(written)} animated loading cards.")


if __name__ == "__main__":
    main()
