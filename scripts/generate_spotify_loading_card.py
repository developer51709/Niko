#!/usr/bin/env python3
"""Generate the animated loading card for Niko's Spotify image card.

The ``.spotify`` command shows this card-shaped placeholder from the public
website while the real card renders:

    https://niko.sryze.cc/assets/loading-cards/spotify.gif

The artwork reuses the skeleton helpers from
``scripts/generate_economy_loading_cards.py`` and the layout from
``utils.image.spotify_card``, so the placeholder has the same shape as the
finished PNG that replaces it. The file is written into the Vite ``public``
directory and mirrored into the served website build; ``npm run build`` runs
this script through the package's ``prebuild`` hook.

Run it directly with:

    python3 scripts/generate_spotify_loading_card.py
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
    _footer,
    _save_gif,
    _skeleton_panel,
)

from utils.image._font_resolver import font_getlength  # noqa: E402
from utils.image.economy_card import (  # noqa: E402
    ACCENT,
    ACCENT_BRIGHT,
    _bold,
    _make_canvas,
)
from utils.image.spotify_card import (  # noqa: E402
    ART_SIZE,
    ART_X,
    ART_Y,
    BAR_H,
    BAR_Y,
    CARD_H,
    CARD_W,
    SPOTIFY_GREEN,
    SPOTIFY_GREEN_DARK,
    TEXT_W,
    TEXT_X,
)

OUT_DIR = ROOT / "web" / "public" / "assets" / "loading-cards"
# The built website is committed and served by Flask, so mirroring the GIF
# there makes it available to the running bot before the next full build.
DIST_DIR = ROOT / "src" / "website" / "dist" / "assets" / "loading-cards"

# type: (width, height, footer label)
CARD_LAYOUTS: dict[str, tuple[int, int, str]] = {
    "nowplaying": (CARD_W, CARD_H, "Spotify"),
}

# The Spotify placeholder sits directly in the loading-cards folder rather than
# in a set of its own, so its file name is fixed instead of following the card
# type.
CARD_FILE = "spotify.gif"


def _wordmark(canvas: Image.Image, width: int, *, inset: int = 36, top: int = 28) -> None:
    draw = ImageDraw.Draw(canvas)
    draw.text((inset, top), "NIKO SPOTIFY", fill=ACCENT, font=_bold(16))

    label = "NOW PLAYING"
    font = _bold(11)
    text_w = int(font_getlength(font, label))
    pill_w, pill_h = text_w + 44, 28
    px, py = width - pill_w - inset, top - 4

    pill = Image.new("RGBA", (pill_w, pill_h), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle(
        [0, 0, pill_w - 1, pill_h - 1],
        radius=pill_h // 2,
        fill=(0, 0, 0, 130),
        outline=SPOTIFY_GREEN_DARK,
        width=1,
    )
    pd.ellipse([13, pill_h // 2 - 3, 19, pill_h // 2 + 3], fill=SPOTIFY_GREEN)
    pd.text((28, 6), label, fill=ACCENT_BRIGHT, font=font)
    canvas.alpha_composite(pill, (px, py))


def _draw_nowplaying(canvas: Image.Image, width: int, height: int, t: float) -> None:
    # Album art on the left.
    _skeleton_panel(canvas, ART_X, ART_Y, ART_SIZE, ART_SIZE, 18, t, 0.02)

    # Track title, artist and album.
    _skeleton_panel(canvas, TEXT_X, 78, min(430, TEXT_W), 26, 8, t, 0.08)
    _skeleton_panel(canvas, TEXT_X, 118, min(250, TEXT_W), 16, 7, t, 0.14)
    _skeleton_panel(canvas, TEXT_X, 149, min(180, TEXT_W), 12, 6, t, 0.18)

    # Track progress and its times.
    _skeleton_panel(canvas, TEXT_X, BAR_Y, TEXT_W, BAR_H, BAR_H // 2, t, 0.24)
    _skeleton_panel(canvas, TEXT_X, BAR_Y + 18, 44, 10, 5, t, 0.30)
    _skeleton_panel(canvas, TEXT_X + TEXT_W - 44, BAR_Y + 18, 44, 10, 5, t, 0.32)


_DRAWERS = {
    "nowplaying": _draw_nowplaying,
}


def _loading_frame(base: Image.Image, width: int, height: int, card_type: str, t: float) -> Image.Image:
    canvas = base.copy()
    _wordmark(canvas, width)
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
        path = out_dir / CARD_FILE
        _save_gif(frames, path)
        written.append(path)
        print(f"  {card_type:<12} {width}x{height}  {path.relative_to(ROOT)}  {path.stat().st_size / 1024:.0f} KB")

        if DIST_DIR.parent.is_dir():
            mirror = DIST_DIR / CARD_FILE
            mirror.parent.mkdir(parents=True, exist_ok=True)
            mirror.write_bytes(path.read_bytes())
    return written


def main() -> None:
    print("Spotify loading card")
    written = generate()
    print(f"Wrote {len(written)} animated loading card.")


if __name__ == "__main__":
    main()
