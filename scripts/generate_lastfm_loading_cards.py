#!/usr/bin/env python3
"""Generate the animated loading cards for Niko's Last.fm image cards.

Each shape the cog renders gets its own looping GIF so a command can show a
card-shaped placeholder from the public website while the real PNG renders:

    https://niko.sryze.cc/assets/loading-cards/lastfm/<shape>.gif

The artwork reuses the graphite canvas, palette and shimmer helpers from
``scripts/generate_economy_loading_cards.py`` and the layout constants from
``utils.image.lastfm_card``, so the skeleton blocks sit where the finished card
draws its text — the loading → finished transition does not jump.

Shapes: ``nowplaying`` (the default ``/fm`` card), ``overview``, ``chart``
(a ten-row board, also used by the other boards), ``recent`` and ``detail``
(artist or album).

Run it directly with:

    python3 scripts/generate_lastfm_loading_cards.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPTS))

from generate_economy_loading_cards import (  # noqa: E402
    FRAME_COUNT,
    FRAME_MS,
    _save_gif,
    _skeleton_circle,
    _skeleton_panel,
)

from utils.image.economy_card import _make_canvas  # noqa: E402
from utils.image.lastfm_card import (  # noqa: E402
    BOARD_HEADER_H,
    BOARD_ROW_H,
    DETAIL_ART,
    DETAIL_ART_Y,
    DETAIL_CHIPS_Y,
    DETAIL_H,
    DETAIL_PLAYS_Y,
    DETAIL_W,
    HEADER_TEXT_Y,
    NOW_ART,
    NOW_ART_X,
    NOW_ART_Y,
    NOW_H,
    NOW_TEXT_X,
    NOW_W,
    OVERVIEW_COLUMNS_H,
    OVERVIEW_COLUMNS_Y,
    OVERVIEW_H,
    OVERVIEW_NOW_H,
    OVERVIEW_NOW_Y,
    OVERVIEW_W,
    PAD,
    RECENT_HEADER_H,
    RECENT_ROW_H,
    RECENT_W,
    _masthead,
    board_height,
)

OUT_DIR = ROOT / "web" / "public" / "assets" / "loading-cards" / "lastfm"
# The built website is committed and served by Flask, so mirroring the GIFs
# there makes them available before the next full build.
DIST_DIR = ROOT / "src" / "website" / "dist" / "assets" / "loading-cards" / "lastfm"

#: Recent card placeholder height: the header, a full screen of rows and the
#: footer, so it is the tallest the real card is likely to be.
RECENT_ROWS = 8

SKELETON_RULE = (255, 255, 255, 26)


def _wordmark(canvas: Image.Image, t: float = 0.0) -> None:
    # The lockup is static, not a skeleton: the loading card should already
    # look like the card it is standing in for. Only the section label after it
    # shimmers, because only that depends on which card is coming.
    label_x = _masthead(canvas)
    _bar(canvas, label_x + 30, HEADER_TEXT_Y + 2, 84, 10, t, 0.4)


def _bar(canvas: Image.Image, x: float, y: float, w: float, h: float, t: float, delay: float = 0.0) -> None:
    _skeleton_panel(canvas, x, y, w, h, min(8, int(h) // 2), t, delay)


def _footer_rule(canvas: Image.Image, width: int, y: int, t: float) -> None:
    draw = ImageDraw.Draw(canvas)
    draw.line([(PAD, y), (width - PAD, y)], fill=SKELETON_RULE, width=1)
    _bar(canvas, PAD, y + 14, 220, 9, t, 0.35)
    _bar(canvas, width - PAD - 70, y + 14, 70, 9, t, 0.45)


def _draw_nowplaying(canvas: Image.Image, width: int, height: int, t: float) -> None:
    _skeleton_panel(canvas, NOW_ART_X, NOW_ART_Y, NOW_ART, NOW_ART, 20, t, 0.05)
    _bar(canvas, NOW_TEXT_X, 100, 104, 11, t, 0.1)
    _bar(canvas, NOW_TEXT_X, 138, 470, 30, t, 0.16)
    _bar(canvas, NOW_TEXT_X, 190, 330, 30, t, 0.22)
    _bar(canvas, NOW_TEXT_X, 254, 240, 18, t, 0.28)
    _bar(canvas, NOW_TEXT_X, 288, 190, 11, t, 0.34)
    _footer_rule(canvas, width, height - 56, t)


def _draw_overview(canvas: Image.Image, width: int, height: int, t: float) -> None:
    _skeleton_circle(canvas, PAD + 47, 96 + 47, 47, t, 0.05)
    _bar(canvas, PAD + 122, 100, 260, 24, t, 0.08)
    _bar(canvas, PAD + 122, 148, 160, 12, t, 0.12)
    _bar(canvas, PAD + 122, 172, 140, 10, t, 0.16)
    _bar(canvas, width - PAD - 170, 92, 170, 42, t, 0.08)
    _bar(canvas, width - PAD - 96, 148, 96, 10, t, 0.16)

    columns = 3
    gap = 20
    column_w = (width - PAD * 2 - gap * (columns - 1)) // columns
    for column in range(columns):
        x = PAD + column * (column_w + gap)
        _skeleton_panel(canvas, x, OVERVIEW_COLUMNS_Y, column_w, OVERVIEW_COLUMNS_H, 20, t, 0.1 + column * 0.06)
        _bar(canvas, x + 24, OVERVIEW_COLUMNS_Y + 24, 96, 10, t, 0.2 + column * 0.06)
        for row in range(5):
            row_y = OVERVIEW_COLUMNS_Y + 56 + row * 50
            _bar(canvas, x + 24, row_y, 14, 14, t, 0.26 + row * 0.04)
            _bar(canvas, x + 52, row_y, column_w - 150, 12, t, 0.3 + row * 0.04)
            _bar(canvas, x + column_w - 82, row_y, 58, 12, t, 0.34 + row * 0.04)

    _skeleton_panel(canvas, PAD, OVERVIEW_NOW_Y, width - PAD * 2, OVERVIEW_NOW_H, 16, t, 0.5)
    _bar(canvas, PAD + 26, OVERVIEW_NOW_Y + 20, 14, 14, t, 0.55)
    _bar(canvas, PAD + 50, OVERVIEW_NOW_Y + 14, 240, 14, t, 0.58)
    _bar(canvas, PAD + 50, OVERVIEW_NOW_Y + 36, 150, 9, t, 0.62)


def _draw_board(canvas: Image.Image, width: int, height: int, t: float) -> None:
    _bar(canvas, PAD, 66, 340, 22, t, 0.05)
    _bar(canvas, PAD, 112, 180, 11, t, 0.1)

    rows = max(1, (height - BOARD_HEADER_H - 58) // BOARD_ROW_H)
    for row in range(rows):
        row_y = BOARD_HEADER_H + row * BOARD_ROW_H
        _skeleton_panel(canvas, PAD, row_y, width - PAD * 2, BOARD_ROW_H - 10, 18, t, 0.16 + row * 0.03)
        _bar(canvas, PAD + 30, row_y + 22, 20, 18, t, 0.2 + row * 0.03)
        _skeleton_panel(canvas, PAD + 74, row_y + 14, 46, 46, 10, t, 0.22 + row * 0.03)
        _bar(canvas, PAD + 134, row_y + 16, 300, 14, t, 0.24 + row * 0.03)
        _bar(canvas, PAD + 134, row_y + 40, 180, 9, t, 0.28 + row * 0.03)
        _bar(canvas, width - PAD - 120, row_y + 18, 94, 16, t, 0.32 + row * 0.03)
        _bar(canvas, PAD + 26, row_y + 58, width - PAD * 2 - 52, 4, t, 0.34 + row * 0.03)

    _footer_rule(canvas, width, height - 56, t)


def _draw_recent(canvas: Image.Image, width: int, height: int, t: float) -> None:
    _skeleton_circle(canvas, PAD + 35, 80 + 35, 35, t, 0.05)
    _bar(canvas, PAD + 88, 84, 240, 22, t, 0.08)
    _bar(canvas, PAD + 88, 122, 160, 11, t, 0.12)
    for row in range(RECENT_ROWS):
        row_y = RECENT_HEADER_H + row * RECENT_ROW_H
        _skeleton_panel(canvas, PAD, row_y, width - PAD * 2, RECENT_ROW_H - 10, 16, t, 0.16 + row * 0.03)
        _skeleton_panel(canvas, PAD + 16, row_y + 10, 48, 48, 10, t, 0.2 + row * 0.03)
        _bar(canvas, PAD + 78, row_y + 16, 300, 13, t, 0.24 + row * 0.03)
        _bar(canvas, PAD + 78, row_y + 40, 200, 9, t, 0.28 + row * 0.03)
        _bar(canvas, width - PAD - 90, row_y + 18, 68, 10, t, 0.32 + row * 0.03)
    _footer_rule(canvas, width, height - 56, t)


def _draw_detail(canvas: Image.Image, width: int, height: int, t: float) -> None:
    _skeleton_panel(canvas, PAD, DETAIL_ART_Y, DETAIL_ART, DETAIL_ART, 20, t, 0.05)
    x = PAD + DETAIL_ART + 44
    max_w = width - PAD - x
    _bar(canvas, x, DETAIL_ART_Y + 6, min(max_w, 430), 32, t, 0.14)
    _bar(canvas, x, DETAIL_ART_Y + 58, min(max_w, 280), 14, t, 0.2)
    _bar(canvas, x, DETAIL_PLAYS_Y, min(max_w, 130), 46, t, 0.28)
    chip_w = 130
    for index in range(3):
        _skeleton_panel(canvas, x + index * (chip_w + 12), DETAIL_CHIPS_Y, chip_w, 66, 14, t, 0.34 + index * 0.05)
    _footer_rule(canvas, width, height - 56, t)


#: file name → (width, height, drawer)
CARD_LAYOUTS = {
    "nowplaying": (NOW_W, NOW_H, _draw_nowplaying),
    "overview": (OVERVIEW_W, OVERVIEW_H, _draw_overview),
    "chart": (980, board_height(10), _draw_board),
    "recent": (RECENT_W, RECENT_HEADER_H + RECENT_ROWS * RECENT_ROW_H + 66, _draw_recent),
    "detail": (DETAIL_W, DETAIL_H, _draw_detail),
}


def _frame(base: Image.Image, width: int, height: int, drawer, t: float) -> Image.Image:
    canvas = base.copy()
    _wordmark(canvas, t)
    drawer(canvas, width, height, t)
    frame = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    frame.alpha_composite(canvas)
    return frame


def _render_card(name: str, width: int, height: int, drawer, out_dir: Path) -> Path:
    # The plain theme canvas, not ``_canvas``: the red corner warmth is a smooth
    # gradient, and a shared 255-colour palette spends its budget dithering it
    # instead of drawing the skeletons — it roughly doubles every GIF. The
    # placeholder therefore warms to the finished card's tint on swap.
    base = _make_canvas(width, height, radius=28)
    frames = [
        _frame(base, width, height, drawer, index / FRAME_COUNT)
        for index in range(FRAME_COUNT)
    ]
    path = out_dir / f"{name}.gif"
    _save_gif(frames, path)
    print(f"  {name:<10} {width}x{height}  {path.relative_to(ROOT)}  {path.stat().st_size / 1024:.0f} KB")

    if DIST_DIR.parent.is_dir():
        mirror = DIST_DIR / f"{name}.gif"
        mirror.parent.mkdir(parents=True, exist_ok=True)
        mirror.write_bytes(path.read_bytes())
    return path


def generate(out_dir: Path = OUT_DIR) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    return [
        _render_card(name, width, height, drawer, out_dir)
        for name, (width, height, drawer) in CARD_LAYOUTS.items()
    ]


def main() -> None:
    print("Last.fm loading cards")
    written = generate()
    print(f"Wrote {len(written)} animated loading cards ({FRAME_COUNT} frames, {FRAME_MS} ms).")


if __name__ == "__main__":
    main()
