#!/usr/bin/env python3
"""Generate the animated loading cards for Niko's leveling image cards.

Each leveling card type gets its own looping GIF so a command can show a
card-shaped placeholder from the public website while the real PNG renders:

    https://niko.sryze.cc/assets/loading-cards/leveling/<card type>.gif

The artwork reuses the skeleton helpers from
``scripts/generate_economy_loading_cards.py`` and the palette and canvas
helpers from ``utils.image.level_card``, so a loading card is the same
graphite, steel and sage card the finished image becomes. The files are
written into the Vite ``public`` directory and copied into the served website
build; ``npm run build`` runs this script first through the package's
``prebuild`` hook.

Run it directly with:

    python3 scripts/generate_leveling_loading_cards.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPTS))

# Shared skeleton drawing kit, so both loading card sets stay identical.
from generate_economy_loading_cards import (  # noqa: E402
    FRAME_COUNT,
    FRAME_MS,
    _footer,
    _save_gif,
    _skeleton_circle,
    _skeleton_panel,
)

from utils.image._font_resolver import font_getlength  # noqa: E402
from utils.image.level_card import (  # noqa: E402
    RANK_H,
    RANK_W,
)
from utils.image.economy_card import (  # noqa: E402
    ACCENT,
    ACCENT_BRIGHT,
    DIM,
    _bold,
    _make_canvas,
    _reg,
)

OUT_DIR = ROOT / "web" / "public" / "assets" / "loading-cards" / "leveling"
# The built website is committed and served by Flask, so mirroring the GIFs
# there makes them available to the running bot before the next full build.
DIST_DIR = ROOT / "src" / "website" / "dist" / "assets" / "loading-cards" / "leveling"

# type: (width, height, footer label)
CARD_LAYOUTS: dict[str, tuple[int, int, str]] = {
    "rank": (RANK_W, RANK_H, "rank"),
}


def _wordmark(canvas: Image.Image, width: int, card_type: str, *, inset: int = 36, top: int = 28) -> None:
    draw = ImageDraw.Draw(canvas)
    draw.text((inset, top), "NIKO LEVELING", fill=ACCENT, font=_bold(16))
    label = card_type.upper()
    label_w = int(font_getlength(_reg(11), label))
    draw.text(
        (width - inset - label_w, top + 3),
        label,
        fill=DIM,
        font=_reg(11),
    )


def _draw_rank(canvas: Image.Image, width: int, height: int, t: float) -> None:
    # Title line under the wordmark.
    _skeleton_panel(canvas, 36, 50, 330, 30, 9, t, 0.04)
    # Rank pill in the top-right corner.
    _skeleton_panel(canvas, width - 200, 34, 164, 30, 15, t, 0.10)

    # Avatar on the left.
    _skeleton_circle(canvas, 96, 156, 60, t, 0.06)

    # Level number and its label.
    _skeleton_panel(canvas, 184, 100, 74, 52, 12, t, 0.12)
    _skeleton_panel(canvas, 288, 118, 62, 14, 7, t, 0.16)

    # XP and rank stat columns.
    _skeleton_panel(canvas, 380, 104, 46, 10, 5, t, 0.20)
    _skeleton_panel(canvas, 380, 124, 156, 24, 8, t, 0.24)
    _skeleton_panel(canvas, 600, 104, 52, 10, 5, t, 0.28)
    _skeleton_panel(canvas, 600, 124, 84, 24, 8, t, 0.32)

    # XP progress bar.
    _skeleton_panel(canvas, 36, 246, width - 72, 18, 9, t, 0.36)


_DRAWERS = {
    "rank": _draw_rank,
}


def _loading_frame(base: Image.Image, width: int, height: int, card_type: str, t: float) -> Image.Image:
    canvas = base.copy()
    _wordmark(canvas, width, card_type)
    _DRAWERS[card_type](canvas, width, height, t)
    _footer(canvas, width, height, CARD_LAYOUTS[card_type][2], t)

    # Keep the rounded corners transparent: the shared GIF saver writes the
    # frame alpha into the palette's transparency slot so the card floats on
    # whatever background Discord shows it on, exactly like the economy cards.
    frame = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    frame.alpha_composite(canvas)
    return frame


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
    print("Leveling loading cards")
    written = generate()
    print(f"Wrote {len(written)} animated loading cards.")


if __name__ == "__main__":
    main()
