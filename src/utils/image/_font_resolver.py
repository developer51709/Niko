"""
Shared PIL font resolution with Termux / Android fallback.

Search order (only attempted when FreeType is available):
  1. Termux prefix  ($PREFIX env var, then hard-coded default)
  2. Android system fonts  (/system/fonts, /system/product/fonts, …)
  3. Standard Linux paths  (/usr/share/fonts/…)
  4. macOS paths           (/Library/Fonts, …)
  5. Any .ttf/.otf found anywhere in the above directories

If the Pillow build on the current platform does NOT include the FreeType
C extension (_imagingft), every truetype call is skipped entirely and the
PIL built-in bitmap font is used as the unconditional fallback.  This is
the situation on Termux when Pillow was installed without FreeType support.

Public API
----------
get_bold(size)         -> ImageFont  (bold TrueType, or bitmap fallback)
get_reg(size)          -> ImageFont  (regular TrueType, or bold, or bitmap)
font_getlength(f, txt) -> float      (shim: works for FreeType and bitmap)
draw_textlength(d,t,f) -> float      (shim: draw.textlength with bbox fallback)
"""
from __future__ import annotations

import os
from PIL import Image, ImageDraw, ImageFont

# ── FreeType availability probe ───────────────────────────────────────────────
# Detect once at import time whether the FreeType C extension is usable.
# PIL uses a DeferredError sentinel when _imagingft is absent, so trying to
# call truetype() raises ImportError through exception chaining in a way that
# can escape a bare `except Exception` block in some Pillow versions.
# Checking here avoids ever calling truetype() when it can't work.

_FREETYPE_OK: bool = False
try:
    # Direct import of the FreeType C extension.
    # Fails immediately and cleanly if Pillow was built without FreeType
    # (common on Termux when installed via pip without system freetype-dev).
    from PIL import _imagingft as _ft_probe  # type: ignore[attr-defined]  # noqa: F401
    del _ft_probe
    _FREETYPE_OK = True
except (ImportError, AttributeError, Exception):
    _FREETYPE_OK = False

# ── Preferred font filenames, tried in priority order ───────────────────────
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
    """Return candidate font directories, Termux / Android first."""
    dirs: list[str] = []

    # Termux: honour $PREFIX (set automatically by Termux)
    prefix = os.environ.get("PREFIX", "")
    if prefix:
        for sub in ("share/fonts/TTF", "share/fonts/truetype", "share/fonts"):
            dirs.append(os.path.join(prefix, sub))
    # Termux hard-coded default (in case $PREFIX is unset)
    for sub in ("share/fonts/TTF", "share/fonts/truetype", "share/fonts"):
        dirs.append(f"/data/data/com.termux/files/usr/{sub}")

    # Android system fonts
    dirs += [
        "/system/fonts",
        "/system/product/fonts",
        "/vendor/fonts",
        "/product/fonts",
    ]

    # Standard Linux
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

    # macOS (developer convenience)
    dirs += [
        "/Library/Fonts",
        "/System/Library/Fonts",
        os.path.expanduser("~/Library/Fonts"),
    ]

    return dirs


def _try_load(path: str) -> bool:
    """Return True only if truetype() succeeds on this path."""
    if not _FREETYPE_OK:
        return False  # short-circuit before PIL's deferred error fires
    try:
        ImageFont.truetype(path, 12)
        return True
    except BaseException:
        # BaseException (not just Exception) catches everything including
        # re-raised ImportError chains from PIL's DeferredError sentinel.
        return False


def _find_font(names: list[str]) -> str:
    """Return the first resolvable TrueType font path, or '' if none found."""
    if not _FREETYPE_OK:
        return ""

    # 1. Bare filename — works if PIL's own search path covers it
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

    # 3. Any .ttf / .otf in the search dirs (e.g. Termux font-* packages)
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
    """
    PIL built-in font, chosen to never require the FreeType extension.
    Pillow 10+ changed load_default(size=N) to call truetype() with a bundled
    base64-encoded TTF — which fails when _imagingft is absent (Termux without
    freetype-dev).  The no-argument form load_default() still returns the old
    fixed-pitch 8 px bitmap glyph set that has existed since PIL 1.x and has
    zero native-extension dependency.
    We only use the size= variant when FreeType is confirmed available.
    """
    if _FREETYPE_OK:
        try:
            return ImageFont.load_default(size=size)
        except Exception:
            pass
    # FreeType unavailable (or size= call failed) — use the tiny bitmap font.
    # It is small and fixed-pitch but guaranteed to work on every platform.
    return ImageFont.load_default()


# ── Module-level resolved paths (lazy, cached) ───────────────────────────────
_bold_path: str | None = None   # None = not yet resolved; "" = no font found
_reg_path:  str | None = None
_cache: dict[tuple, ImageFont.ImageFont] = {}


def get_bold(size: int) -> ImageFont.ImageFont:
    """Return a bold TrueType font at *size*, or a bitmap fallback."""
    global _bold_path
    if _bold_path is None:
        _bold_path = _find_font(_BOLD_NAMES)

    key = ("b", size)
    if key in _cache:
        return _cache[key]

    font: ImageFont.ImageFont
    if _bold_path and _FREETYPE_OK:
        try:
            font = ImageFont.truetype(_bold_path, size)
            _cache[key] = font
            return font
        except BaseException:
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
            _reg_path = _bold_path or ""

    key = ("r", size)
    if key in _cache:
        return _cache[key]

    font: ImageFont.ImageFont
    if _reg_path and _FREETYPE_OK:
        try:
            font = ImageFont.truetype(_reg_path, size)
            _cache[key] = font
            return font
        except BaseException:
            pass

    font = _bitmap_default(size)
    _cache[key] = font
    return font


# ── Measurement shims ─────────────────────────────────────────────────────────

def font_getlength(font: ImageFont.ImageFont, text: str) -> float:
    """
    Shim for ``font.getlength(text)``.

    ``FreeTypeFont`` has ``.getlength()``; the bitmap ``ImageFont`` from
    ``load_default()`` does not.  Falls back to ``textbbox`` so all callers
    work regardless of which font type is in use.
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

    Falls back to ``textbbox`` on older Pillow builds or edge-cases.
    """
    try:
        return draw.textlength(text, font=font)
    except Exception:
        bbox = draw.textbbox((0, 0), text, font=font)
        return float(bbox[2] - bbox[0])

