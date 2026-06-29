"""
Shared PIL font resolution with Termux / Android fallback.

Search order:
  1. Termux prefix ($PREFIX env var, default /data/data/com.termux/files/usr)
  2. Android system fonts  (/system/fonts, /system/product/fonts, …)
  3. Standard Linux paths  (/usr/share/fonts/…)
  4. macOS paths           (/Library/Fonts, …)
  5. Any .ttf/.otf found anywhere in the above directories
  6. PIL built-in bitmap font (always succeeds — small but readable)

Public API
----------
get_bold(size)         -> ImageFont  (bold / semi-bold TrueType, or bitmap fallback)
get_reg(size)          -> ImageFont  (regular TrueType, or bold, or bitmap fallback)
font_getlength(f, txt) -> float      (shim: works for both FreeType and bitmap fonts)
"""
from __future__ import annotations

import os
from PIL import Image, ImageDraw, ImageFont

# ── Preferred font filenames, tried in this order ───────────────────────────
_BOLD_NAMES: list[str] = [
    "DejaVuSans-Bold.ttf",
    "LiberationSans-Bold.ttf",
    "Roboto-Bold.ttf",
    "NotoSans-Bold.ttf",
    "DroidSans-Bold.ttf",
    "FreeSansBold.ttf",
    "Hack-Bold.ttf",
    "SourceCodePro-Bold.ttf",
    "Arial-BoldMT.ttf",
    "arial.ttf",
]

_REG_NAMES: list[str] = [
    "DejaVuSans.ttf",
    "LiberationSans-Regular.ttf",
    "Roboto-Regular.ttf",
    "NotoSans-Regular.ttf",
    "DroidSans.ttf",
    "FreeSans.ttf",
    "Hack-Regular.ttf",
    "SourceCodePro-Regular.ttf",
    "Arial.ttf",
    "arial.ttf",
]


def _search_dirs() -> list[str]:
    """Return candidate directories, Termux / Android first."""
    dirs: list[str] = []

    # ── Termux ──────────────────────────────────────────────────────────────
    prefix = os.environ.get("PREFIX", "")
    if prefix:
        for sub in ("share/fonts/TTF", "share/fonts/truetype", "share/fonts"):
            dirs.append(os.path.join(prefix, sub))
    # Hard-coded Termux default (in case $PREFIX is unset)
    for sub in ("share/fonts/TTF", "share/fonts/truetype", "share/fonts"):
        dirs.append(f"/data/data/com.termux/files/usr/{sub}")

    # ── Android system ───────────────────────────────────────────────────────
    dirs += [
        "/system/fonts",
        "/system/product/fonts",
        "/vendor/fonts",
        "/product/fonts",
    ]

    # ── Standard Linux ───────────────────────────────────────────────────────
    dirs += [
        "/usr/share/fonts/truetype/dejavu",
        "/usr/share/fonts/dejavu",
        "/usr/share/fonts/TTF",
        "/usr/share/fonts/truetype/liberation",
        "/usr/share/fonts/truetype/noto",
        "/usr/share/fonts/truetype/hack",
        "/usr/share/fonts/truetype/freefont",
        "/usr/share/fonts/truetype",
        "/usr/share/fonts",
        "/usr/local/share/fonts",
    ]

    # ── macOS (developer convenience) ───────────────────────────────────────
    dirs += [
        "/Library/Fonts",
        "/System/Library/Fonts",
        os.path.expanduser("~/Library/Fonts"),
    ]

    return dirs


def _try_load(path: str) -> bool:
    try:
        ImageFont.truetype(path, 12)
        return True
    except Exception:
        return False


def _find_font(names: list[str]) -> str:
    """Return the first resolvable TrueType font path, or ''."""
    # 1. Bare filename — works if font is on PIL's internal search path
    for name in names:
        if _try_load(name):
            return name

    # 2. Known directories + preferred names
    for d in _search_dirs():
        if not os.path.isdir(d):
            continue
        for name in names:
            path = os.path.join(d, name)
            if os.path.isfile(path) and _try_load(path):
                return path

    # 3. Any .ttf / .otf in the search dirs (Termux with non-DejaVu font packs)
    for d in _search_dirs():
        if not os.path.isdir(d):
            continue
        try:
            for fname in sorted(os.listdir(d)):
                if fname.lower().endswith((".ttf", ".otf")):
                    path = os.path.join(d, fname)
                    if _try_load(path):
                        return path
        except (PermissionError, OSError):
            continue

    return ""


def _bitmap_default(size: int) -> ImageFont.ImageFont:
    """PIL built-in bitmap font — always succeeds regardless of platform."""
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


# ── Module-level resolved paths (lazy, cached) ───────────────────────────────
_bold_path: str | None = None   # None = not yet resolved
_reg_path:  str | None = None
_cache: dict[tuple, ImageFont.ImageFont] = {}


def get_bold(size: int) -> ImageFont.ImageFont:
    """Return a bold TrueType font at *size*, or a bitmap fallback."""
    global _bold_path
    if _bold_path is None:
        _bold_path = _find_font(_BOLD_NAMES)  # "" means no TrueType found

    key = ("b", size)
    if key in _cache:
        return _cache[key]

    font: ImageFont.ImageFont
    if _bold_path:
        try:
            font = ImageFont.truetype(_bold_path, size)
            _cache[key] = font
            return font
        except Exception:
            pass

    font = _bitmap_default(size)
    _cache[key] = font
    return font


def get_reg(size: int) -> ImageFont.ImageFont:
    """Return a regular TrueType font at *size*, or a bitmap fallback."""
    global _bold_path, _reg_path
    if _reg_path is None:
        _reg_path = _find_font(_REG_NAMES)
        if not _reg_path:
            if _bold_path is None:
                _bold_path = _find_font(_BOLD_NAMES)
            _reg_path = _bold_path  # use bold as regular if nothing else found

    key = ("r", size)
    if key in _cache:
        return _cache[key]

    font: ImageFont.ImageFont
    if _reg_path:
        try:
            font = ImageFont.truetype(_reg_path, size)
            _cache[key] = font
            return font
        except Exception:
            pass

    font = _bitmap_default(size)
    _cache[key] = font
    return font


# ── Measurement shims ─────────────────────────────────────────────────────────

def font_getlength(font: ImageFont.ImageFont, text: str) -> float:
    """
    Shim for ``font.getlength(text)``.

    ``FreeTypeFont`` has ``.getlength()``; the bitmap ``ImageFont`` returned
    by ``ImageFont.load_default()`` does **not**.  This shim falls back to
    ``textbbox`` so code works regardless of which font type is in use.
    """
    try:
        return font.getlength(text)  # type: ignore[attr-defined]
    except AttributeError:
        dummy = ImageDraw.Draw(Image.new("L", (1, 1)))
        bbox = dummy.textbbox((0, 0), text, font=font)
        return float(bbox[2] - bbox[0])


def draw_textlength(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> float:
    """
    Shim for ``draw.textlength(text, font=font)``.

    Older Pillow (<8.0) and some edge-cases lack this method; fall back to
    ``textbbox`` in that situation.
    """
    try:
        return draw.textlength(text, font=font)
    except Exception:
        bbox = draw.textbbox((0, 0), text, font=font)
        return float(bbox[2] - bbox[0])

