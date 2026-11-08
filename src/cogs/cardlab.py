"""Card lab — a temporary cog for choosing the next economy card design.

A review tool, not a feature: it paints candidate balance-card styles onto
*sample* figures so they can be compared without touching anyone's real economy
data. It is deliberately standalone — no database, no other cog, every renderer
in this one file — so deleting the file removes the whole experiment.

The three styles are the ones that survived the first review:

    A  Aurora        the avatar, saturated and blurred, under dark glass
    B  Duotone       the avatar squeezed onto two palette tones
    C  Midnight      the avatar sunk to black and lit by palette glow

All three are painted onto the *live* balance card's layout, at its real size
(820x380), so the only thing that differs between them is the style. Pick a
style here first; the layout question comes after one is chosen.

No design uses the current graphite economy theme: every palette is derived
from the member's avatar hue.

One post, not a burst: the command posts a single Components v2 container
whose media galleries start on the economy *balance* loading GIF, then fills
them in one at a time as each card finishes rendering. A Components v2 message
cannot carry a poll, so the 24 hour vote is posted as its own message directly
under the cards.

Commands (owner only):
    .cardlab          all three styles, plus the vote
    .cardlab a        just Aurora
    .cardlab c        just Midnight

Remove this file once a design is chosen.
"""

from __future__ import annotations

import asyncio
import colorsys
import os
from dataclasses import dataclass
from datetime import timedelta
from io import BytesIO
from typing import Callable

import discord
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps
from discord.ext import commands

from utils.image._font_resolver import (
    draw_text_with_fallback,
    font_getlength,
    textlength_with_fallback,
)
from config.links import WEBSITE
from utils.image.economy_card import (
    _bold,
    _circle_avatar,
    _format_amount,
    _reg,
    _rounded_mask,
    _strip_discord_emoji,
    _truncate,
    _vertical_gradient,
    fetch_avatar_bytes,
)
from utils.loading_cards import loading_card_url

WHITE = (255, 255, 255)
RADIUS = 32

#: The live balance card's canvas, so the previews are what `.balance` would
#: actually look like — and the same size as its loading GIF, so the swap in
#: the message does not resize anything.
CARD_W, CARD_H = 820, 380

#: Hue used when the avatar has no colour to borrow (blank, greyscale picture).
FALLBACK_HUE = 0.58


# ── Palette ─────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Palette:
    """A theme's colours, all derived from one avatar hue."""

    hue: float
    base: tuple[int, int, int]      # mid-tone brand colour
    deep: tuple[int, int, int]      # shadow end of a gradient
    glow: tuple[int, int, int]      # bright accent for dark backgrounds


def _hsv(h: float, s: float, v: float) -> tuple[int, int, int]:
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
    return int(r * 255), int(g * 255), int(b * 255)


def _mix(a, b, t: float) -> tuple[int, int, int]:
    """Linear blend of two colours; ``t=0`` is *a*, ``t=1`` is *b*."""
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _hue_of(raw: bytes | None) -> tuple[float, float]:
    """The avatar's most common colourful hue, or a neutral fallback."""
    if not raw:
        return FALLBACK_HUE, 0.0
    try:
        img = Image.open(BytesIO(raw)).convert("RGB").resize((32, 32), Image.LANCZOS)
    except Exception:
        return FALLBACK_HUE, 0.0

    best: tuple[float, float] | None = None
    for _count, (r, g, b) in sorted(img.quantize(colors=6).convert("RGB").getcolors(4096) or [], reverse=True):
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if 0.10 <= s <= 0.95 and 0.12 <= v <= 0.96:
            best = (h, s)
            break

    if best is None:
        r, g, b = img.resize((1, 1), Image.LANCZOS).getpixel((0, 0))
        h, s, _ = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        return (h, s) if s >= 0.12 else (FALLBACK_HUE, 0.0)
    return best


def palette_from(raw: bytes | None) -> Palette:
    """Build the shared tones from the avatar's dominant hue.

    Saturation is clamped rather than copied, so a neon avatar still gives
    readable tones and every style keeps the same contrast structure no matter
    whose picture is on the card.
    """
    hue, sat = _hue_of(raw)
    sat = max(0.42, min(0.68, sat if sat > 0 else 0.5))
    return Palette(
        hue=hue,
        base=_hsv(hue, sat, 0.50),
        deep=_hsv(hue, sat + 0.06, 0.15),
        glow=_hsv(hue, sat * 0.75, 0.88),
    )


# ── Picture helpers ─────────────────────────────────────────────────────────

def _synthetic_backdrop(size: tuple[int, int], hue: float) -> Image.Image:
    """Stand-in backdrop for a missing avatar: soft coloured light, no photo."""
    w, h = size
    img = _vertical_gradient(size, _hsv(hue, 0.55, 0.46), _hsv(hue + 0.08, 0.65, 0.16))
    for box, alpha in (
        ((-0.35 * w, -0.55 * h, 0.75 * w, 0.55 * h), 120),
        ((0.45 * w, 0.35 * h, 1.35 * w, 1.25 * h), 90),
    ):
        blob = Image.new("L", size, 0)
        ImageDraw.Draw(blob).ellipse(box, fill=alpha)
        layer = Image.new("RGBA", size, (*_hsv(hue + 0.12, 0.35, 0.95), 255))
        layer.putalpha(blob.filter(ImageFilter.GaussianBlur(radius=w // 6)))
        img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return img


def _blurred_cover(
    raw: bytes | None,
    size: tuple[int, int],
    *,
    hue: float,
    blur: float = 44,
    saturate: float = 1.0,
) -> Image.Image:
    """The avatar, fitted to *size* and blurred into a background."""
    img: Image.Image | None = None
    if raw:
        try:
            img = Image.open(BytesIO(raw)).convert("RGB")
        except Exception:
            img = None
    img = ImageOps.fit(img, size, Image.LANCZOS) if img is not None else _synthetic_backdrop(size, hue)
    if saturate != 1.0:
        img = ImageEnhance.Color(img).enhance(saturate)
    return img.filter(ImageFilter.GaussianBlur(blur))


def _card(bg: Image.Image, radius: int = RADIUS) -> Image.Image:
    """An opaque picture clipped to the card's rounded silhouette."""
    card = bg.convert("RGBA")
    card.putalpha(_rounded_mask(card.size, radius))
    return card


def _clamp_brightness(img: Image.Image, ceiling: int) -> Image.Image:
    """Dim a picture just enough that its brightest area is *ceiling*.

    White type is only legible over a bounded background, and an avatar can be
    anything from a black square to a white studio shot. Scaling the picture by
    its own 99.5th percentile means the style holds for every member instead of
    only for dark pictures; colours survive, only the exposure changes.
    """
    histogram = img.convert("L").histogram()
    total = sum(histogram)
    if not total:
        return img
    running = 0
    brightest = 255
    for value, count in enumerate(histogram):
        running += count
        if running >= total * 0.995:
            brightest = value
            break
    if brightest <= ceiling:
        return img
    return ImageEnhance.Brightness(img).enhance(ceiling / max(1, brightest))


def _scrim(canvas: Image.Image, stops: list[tuple[int, int]], *, color=(0, 0, 0)) -> None:
    """Darken the picture behind text, keeping the rounded corners intact.

    *stops* are ``(y, alpha)`` pairs interpolated down the card. The small type
    lives in the header and footer bands, which get a heavier veil than the
    middle where the oversized numeral only needs large-text contrast.
    """
    w, h = canvas.size
    strip = Image.new("L", (1, h))
    px = strip.load()
    for y in range(h):
        for index in range(len(stops) - 1):
            y0, a0 = stops[index]
            y1, a1 = stops[index + 1]
            if y0 <= y <= y1 or index == len(stops) - 2:
                t = 0.0 if y1 == y0 else (y - y0) / (y1 - y0)
                px[0, y] = int(a0 + (a1 - a0) * max(0.0, min(1.0, t)))
                break
    mask = strip.resize((w, h), Image.BILINEAR)
    layer = Image.new("RGBA", (w, h), (*color, 255))
    layer.putalpha(ImageChops.multiply(mask, canvas.getchannel("A")))
    canvas.alpha_composite(layer)


def _blob(canvas: Image.Image, box, color, alpha: int, *, blur: float) -> None:
    """Soft coloured light used to tint a blurred picture."""
    mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(mask).ellipse(box, fill=alpha)
    mask = mask.filter(ImageFilter.GaussianBlur(blur))
    layer = Image.new("RGBA", canvas.size, (*color, 255))
    layer.putalpha(ImageChops.multiply(mask, canvas.getchannel("A")))
    canvas.alpha_composite(layer)


# ── Drawing helpers ─────────────────────────────────────────────────────────
# Pillow writes a fill's alpha straight into an RGBA canvas rather than
# blending it, so a translucent fill leaves see-through pixels — type that
# looks eaten away by whatever sits behind the PNG. Every translucent ink is
# therefore resolved against the card first and drawn opaque.

def _ink(canvas: Image.Image, xy, color) -> tuple[int, int, int]:
    """Blend a translucent colour with the card under *xy*."""
    if len(color) < 4 or color[3] >= 255:
        return tuple(color[:3])
    x = max(0, min(canvas.width - 1, int(xy[0])))
    y = max(0, min(canvas.height - 1, int(xy[1])))
    bg = canvas.getpixel((x, y))
    t = color[3] / 255
    return tuple(int(bg[i] + (color[i] - bg[i]) * t) for i in range(3))


def _text(canvas: Image.Image, xy, text: str, *, size: int, bold: bool = False, fill=WHITE) -> float:
    return draw_text_with_fallback(
        ImageDraw.Draw(canvas), xy, text, size=size, bold=bold, fill=_ink(canvas, xy, fill)
    )


def _text_w(text: str, *, size: int, bold: bool = False) -> float:
    return textlength_with_fallback(text, bold=bold, size=size)


def _text_right(canvas, x_right: float, y: float, text: str, *, size: int, bold: bool = False, fill=WHITE) -> None:
    _text(canvas, (x_right - _text_w(text, size=size, bold=bold), y), text, size=size, bold=bold, fill=fill)


def _tracked(canvas, xy, text: str, font, fill, *, spacing: float = 2.4) -> None:
    """Letter-spaced label: reads as chrome instead of data."""
    draw = ImageDraw.Draw(canvas)
    ink = _ink(canvas, xy, fill)
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=font, fill=ink)
        x += font_getlength(font, char) + spacing


def _label(canvas, xy, text: str, *, size: int = 10, fill=WHITE, spacing: float = 2.4) -> None:
    _tracked(canvas, xy, text, _reg(size), fill, spacing=spacing)


def _avatar(canvas: Image.Image, raw: bytes | None, x: int, y: int, size: int, *, ring=(255, 255, 255, 76)) -> None:
    canvas.alpha_composite(_circle_avatar(raw, size), (x, y))
    # The live card rings the face in its accent, so the ring is part of the style.
    layer = Image.new("RGBA", (size + 6, size + 6), (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse([0, 0, size + 5, size + 5], outline=ring, width=3)
    canvas.alpha_composite(layer, (x - 3, y - 3))


def _pill(canvas: Image.Image, x_right: int, y: int, text: str, *, size: int = 14, fill=WHITE) -> None:
    font = _reg(size)
    width, height = int(font_getlength(font, text)) + 28, 28
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle(
        [0, 0, width - 1, height - 1], radius=height // 2,
        fill=(0, 0, 0, 122), outline=(255, 255, 255, 92), width=1,
    )
    canvas.alpha_composite(layer, (x_right - width, y))
    _text(canvas, (x_right - width + 14, y + 6), text, size=size, fill=fill)


def _progress(canvas: Image.Image, x: int, y: int, w: int, h: int, pct: float, *, fill) -> None:
    pct = max(0.0, min(1.0, pct))
    track = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(track).rounded_rectangle([0, 0, w - 1, h - 1], radius=h // 2, fill=(255, 255, 255, 34))
    canvas.alpha_composite(track, (x, y))
    if pct <= 0.001:
        return
    width = max(h, int(w * pct))
    bar = Image.new("RGBA", (width, h), (*fill, 255))
    bar.putalpha(_rounded_mask((width, h), h // 2))
    canvas.alpha_composite(bar, (x, y))


def _finish(canvas: Image.Image) -> BytesIO:
    out = BytesIO()
    canvas.save(out, format="PNG", optimize=True)
    out.seek(0)
    return out


# ── Demo figures ────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Demo:
    """Sample figures shaped like a real wallet: plausible, never personal."""

    name: str
    cash: int = 48_260
    bank: int = 1_240_000
    cap: int = 2_000_000
    tier: str = "Gold"
    level: int = 34
    xp: int = 12_340
    xp_next: int = 24_000
    job: str = "Mechanic"
    streak: int = 12
    rank: int = 214

    @property
    def net_worth(self) -> int:
        return self.cash + self.bank

    @property
    def bank_text(self) -> str:
        return f"{_format_amount(self.bank)} / {_format_amount(self.cap)}"

    @property
    def xp_text(self) -> str:
        return f"{self.xp:,} / {self.xp_next:,} XP"

    @property
    def xp_pct(self) -> float:
        return 0.0 if self.xp_next <= 0 else min(1.0, self.xp / self.xp_next)


def _display_name(d: Demo) -> str:
    return _strip_discord_emoji(d.name) or "Member"



# ── Styles ──────────────────────────────────────────────────────────────────

class Theme:
    """One visual style: owns the background and how a stat panel is painted."""

    key = ""
    name = ""
    #: One line explaining the style, shown under its card in the vote post.
    blurb = ""

    def __init__(self, avatar: bytes | None, palette: Palette) -> None:
        self.palette = palette
        self.ink = WHITE
        # Small type keeps its hierarchy from size and letter-spacing, not from
        # fading out: at 10px a translucent label cannot reach 4.5:1 over a
        # bright picture, so the labels stay essentially white and the scrim
        # does the work instead.
        self.sub = (255, 255, 255, 238)
        self.faint = (255, 255, 255, 238)
        self.eyebrow = (255, 255, 255, 238)
        self.cell = (255, 255, 255, 240)
        self.rule = (255, 255, 255, 48)
        self.accent = WHITE
        self._background = self._build(avatar, palette)

    # -- hooks ---------------------------------------------------------------
    def _build(self, avatar: bytes | None, palette: Palette) -> Image.Image:
        raise NotImplementedError

    def panel(self, canvas: Image.Image, box, radius: int = 24) -> None:
        """A slab that *darkens* what is under it, so its type gains contrast."""
        x, y, w, h = box
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(layer).rounded_rectangle(
            [0, 0, w - 1, h - 1], radius=radius,
            fill=(0, 0, 0, 62), outline=(255, 255, 255, 58), width=1,
        )
        canvas.alpha_composite(layer, (x, y))

    # -- public --------------------------------------------------------------
    def canvas(self) -> Image.Image:
        return self._background.copy()


class AuroraTheme(Theme):
    """Saturated avatar blur, a dark veil, and frosted glass on top."""

    key, name = "a", "Aurora"
    blurb = "Blurred portrait, saturated, sitting behind dark frosted glass."

    def __init__(self, avatar, palette) -> None:
        self._picture: Image.Image | None = None
        super().__init__(avatar, palette)

    def _build(self, avatar, palette) -> Image.Image:
        # Bound the picture first, then darken it with the scrim. Clamping after
        # the scrim would lift the top of the card back to the ceiling and put
        # the small header labels on glare.
        picture = _blurred_cover(avatar, (CARD_W, CARD_H), hue=palette.hue, blur=42, saturate=1.45)
        picture = _clamp_brightness(picture, 112)
        self._picture = picture

        canvas = _card(picture)
        _blob(canvas, (520, 300, 1260, 820), palette.glow, 80, blur=120)
        _scrim(canvas, [(0, 200), (120, 190), (240, 178), (CARD_H, 210)])
        return canvas

    def panel(self, canvas, box, radius: int = 24) -> None:
        """Frosted glass: the picture again, re-blurred under a dark wash."""
        x, y, w, h = box
        crop = self._picture.crop((x, y, x + w, y + h)).filter(ImageFilter.GaussianBlur(10)).convert("RGBA")
        crop = _clamp_brightness(crop, 76)
        mask = _rounded_mask((w, h), radius)
        crop.putalpha(mask)
        canvas.alpha_composite(crop, (x, y))

        wash = Image.new("RGBA", (w, h), (6, 8, 12, 255))
        wash.putalpha(ImageChops.multiply(Image.new("L", (w, h), 165), mask))
        canvas.alpha_composite(wash, (x, y))

        ImageDraw.Draw(canvas).rounded_rectangle(
            [x, y, x + w - 1, y + h - 1], radius=radius, outline=(255, 255, 255, 52), width=1
        )


class DuotoneTheme(Theme):
    """The avatar squeezed onto two palette tones: a flat colour poster."""

    key, name = "b", "Duotone"
    blurb = "The portrait cut down to two tones of one hue — a flat poster."

    def _build(self, avatar, palette) -> Image.Image:
        photo = _blurred_cover(avatar, (CARD_W, CARD_H), hue=palette.hue, blur=38)
        greyed = ImageOps.autocontrast(photo.convert("L"))
        # The light end is the palette at mid-darkness, not its brightest tone:
        # a two-colour poster still has to carry white type.
        poster = ImageOps.colorize(
            greyed, black=palette.deep, white=_mix(palette.base, palette.deep, 0.15)
        ).convert("RGB")
        canvas = _card(poster)
        _scrim(canvas, [(0, 186), (120, 176), (240, 164), (CARD_H, 198)])
        self.accent = _mix(palette.glow, WHITE, 0.55)
        return _clamp_brightness(canvas, 118)


class MeshTheme(Theme):
    """The avatar sunk to black, lit from behind by palette glow."""

    key, name = "c", "Midnight"
    blurb = "The portrait sunk to near-black, lit by a glow built from its hue."

    def _build(self, avatar, palette) -> Image.Image:
        base = _blurred_cover(avatar, (CARD_W, CARD_H), hue=palette.hue, blur=54, saturate=1.2)
        base = ImageEnhance.Brightness(base).enhance(0.22)
        canvas = _card(base)
        _blob(canvas, (-220, -240, 380, 190), palette.base, 120, blur=120)
        _blob(canvas, (620, -260, 1200, 230), palette.glow, 70, blur=130)
        _blob(canvas, (160, 330, 900, 900), _mix(palette.base, palette.deep, 0.4), 110, blur=140)
        _scrim(canvas, [(0, 174), (120, 162), (240, 152), (CARD_H, 186)])
        self.accent = _mix(palette.glow, WHITE, 0.35)
        return _clamp_brightness(canvas, 82)


THEMES: dict[str, type[Theme]] = {
    AuroraTheme.key: AuroraTheme,
    DuotoneTheme.key: DuotoneTheme,
    MeshTheme.key: MeshTheme,
}


# ── Layout ──────────────────────────────────────────────────────────────────
# One layout for now, and it is not a new one: the live balance card's own
# arrangement at its real 820x380. Only the style underneath changes, which is
# the decision on the table.

def _layout_balance(theme: Theme, d: Demo, avatar: bytes | None) -> Image.Image:
    """The live `.balance` card, painted by *theme*.

    Mirrors ``utils.image.economy_card._render_balance_sync`` position for
    position — header, rank pill, ringed avatar, right-aligned net worth, three
    chips, XP bar — so a winning style can drop straight into that renderer
    without the layout moving.
    """
    canvas = theme.canvas()

    _text(canvas, (36, 26), "NIKO ECONOMY", size=18, bold=True, fill=theme.accent)
    _text(canvas, (36, 52), "Wallet", size=34, bold=True, fill=theme.ink)
    _pill(canvas, CARD_W - 36, 36, f"#{d.rank} on the leaderboard", size=14, fill=theme.ink)

    _avatar(canvas, avatar, 40, 110, 116, ring=theme.palette.glow)
    _text(canvas, (178, 116), _truncate(_display_name(d), _bold(28), 400), size=28, bold=True, fill=theme.ink)
    _text(canvas, (178, 154), f"{d.job}   •   Streak {d.streak}", size=15, fill=theme.sub)

    _text_right(canvas, CARD_W - 40, 122, "NET WORTH", size=13, fill=theme.faint)
    _text_right(canvas, CARD_W - 40, 142, f"{d.net_worth:,}", size=28, bold=True, fill=theme.ink)

    chips_y, chip_h, gap = 254, 78, 14
    chip_w = (CARD_W - 80 - gap * 2) // 3
    chips = (
        ("CASH", _format_amount(d.cash), theme.accent),
        ("BANK", d.bank_text, theme.ink),
        ("VAULT TIER", d.tier, _mix(theme.palette.glow, WHITE, 0.45)),
    )
    for index, (label, value, accent) in enumerate(chips):
        x = 40 + index * (chip_w + gap)
        theme.panel(canvas, (x, chips_y, chip_w, chip_h), radius=14)
        _label(canvas, (x + 16, chips_y + 12), label, size=9, fill=theme.cell)
        size = 26
        while size > 16 and _text_w(value, size=size, bold=True) > chip_w - 32:
            size -= 2
        _text(canvas, (x + 16, chips_y + 34), _truncate(value, _bold(size), chip_w - 32),
              size=size, bold=True, fill=accent)

    _text(canvas, (40, 330), f"LEVEL {d.level}", size=15, bold=True, fill=theme.ink)
    _text_right(canvas, CARD_W - 40, 332, d.xp_text, size=13, fill=theme.sub)
    _progress(canvas, 40, 354, CARD_W - 80, 16, d.xp_pct, fill=theme.accent)
    return canvas


# ── Catalogue ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Design:
    style: str
    render: Callable[[bytes | None, Demo], BytesIO]

    @property
    def key(self) -> str:
        return self.style

    @property
    def style_name(self) -> str:
        return THEMES[self.style].name

    @property
    def blurb(self) -> str:
        return THEMES[self.style].blurb

    @property
    def title(self) -> str:
        return f"{self.key.upper()} · {self.style_name}"


def _renderer(style_key: str) -> Callable[[bytes | None, Demo], BytesIO]:
    theme_cls = THEMES[style_key]

    def render(avatar: bytes | None, demo: Demo) -> BytesIO:
        palette = palette_from(avatar)
        theme = theme_cls(avatar, palette)
        return _finish(_layout_balance(theme, demo, avatar))

    return render


DESIGNS: tuple[Design, ...] = tuple(Design(style, _renderer(style)) for style in THEMES)


def select(token: str | None) -> list[Design]:
    """``a`` / ``b`` / ``e`` picks one style; nothing picks all three."""
    text = (token or "").strip().lower()
    if not text:
        return list(DESIGNS)
    return [d for d in DESIGNS if d.key == text]


# ── Message layout ──────────────────────────────────────────────────────────

#: The brand accent every other Niko container uses.
ACCENT = discord.Colour(0xC8A882)


def _balance_loading_media() -> str:
    """URL of the economy balance loading GIF.

    Mirrors ``cogs.economy.data._loading_cards_base`` — the same placeholder
    ``_loading_card_view`` shows, read from the same site folder — without
    pulling the whole economy module into a cog that is meant to be deleted on
    its own.
    """
    origin = os.environ.get("PUBLIC_URL", "").strip().rstrip("/")
    return loading_card_url(f"{origin or WEBSITE}/assets/loading-cards", "economy/balance.gif")


#: Components v2 messages cannot carry a poll (Discord disables the field while
#: IS_COMPONENTS_V2 is set), so the vote is posted as its own message under the
#: cards rather than pretending one message can hold both.
POLL_QUESTION = "Which balance card style should the wallet card use?"
POLL_HOURS = 24


def _lab_view(designs: list[Design], media: dict[str, str]) -> discord.ui.LayoutView:
    """The vote post: a heading, then each style's card with a one-line blurb.

    *media* maps a design key to its gallery source: the balance loading GIF
    until that card has rendered, then ``attachment://card-<key>.png``.
    """
    count = len(designs)
    view = discord.ui.LayoutView()
    container = discord.ui.Container(accent_colour=ACCENT)
    container.add_item(discord.ui.TextDisplay(content="### Balance card vote · pick a style"))
    container.add_item(discord.ui.TextDisplay(
        content="-# Candidates for the `.balance` card, drawn on the card's current layout with "
                "sample figures. "
                + ("Vote in the poll below — the winning style ships in the next update."
                   if count > 1 else "Shown on its own for a closer look.")
    ))
    container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.large))

    for index, item in enumerate(designs):
        if index:
            container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        container.add_item(discord.ui.TextDisplay(content=f"**{item.title}**\n-# {item.blurb}"))
        container.add_item(discord.ui.MediaGallery(discord.MediaGalleryItem(media=media[item.key])))

    view.add_item(container)
    return view


# ── Cog ─────────────────────────────────────────────────────────────────────

class CardLab(commands.Cog):
    """Owner-only balance-card style vote, posted with a 24 hour poll."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="cardlab",
        aliases=["cards"],
        description="Post the balance-card style vote and its 24 hour poll (owner only).",
        help="Post the balance-card style vote.",
    )
    @commands.guild_only()
    @commands.is_owner()
    async def cardlab(self, ctx, design: str = None):
        chosen = select(design)
        if not chosen:
            styles = ", ".join(f"`{k}` ({v.name})" for k, v in THEMES.items())
            return await ctx.send(f"Unknown style `{design}`. Styles: {styles}.")

        if ctx.interaction:
            await ctx.defer()

        author = ctx.author
        avatar_url = author.display_avatar.url if author.display_avatar else None
        avatar = await fetch_avatar_bytes(avatar_url, size=256)
        demo = Demo(name=author.display_name)

        # Every slot opens on the balance loading card, so the message already
        # has its final shape and each edit swaps a single gallery instead of
        # resizing the layout under the reader.
        media = {item.key: _balance_loading_media() for item in chosen}
        if ctx.interaction:
            message = await ctx.interaction.edit_original_response(view=_lab_view(chosen, media))
        else:
            message = await ctx.send(view=_lab_view(chosen, media))

        # Every edit re-sends the cards rendered so far. An edit replaces the
        # message's attachment set, and passing the existing attachments back to
        # keep them is not reliable — Discord dropped them, and the galleries
        # already filled then pointed at attachments that no longer existed
        # ("The referenced attachment attachment://card-a1.png was not found").
        # Uploading the whole set each time keeps every attachment:// reference
        # in the same request as its file, so each edit is valid on its own and
        # a failure leaves the previous, complete card set on screen.
        rendered: dict[str, bytes] = {}
        for item in chosen:
            buf = await asyncio.to_thread(item.render, avatar, demo)
            rendered[item.key] = buf.getvalue()
            media[item.key] = f"attachment://card-{item.key}.png"
            message = await message.edit(
                view=_lab_view(chosen, media),
                attachments=[
                    discord.File(BytesIO(png), filename=f"card-{key}.png")
                    for key, png in rendered.items()
                ],
            )

        # The vote goes straight under the cards. A poll needs at least two
        # answers, so a single-style preview gets no poll at all.
        if len(chosen) > 1:
            poll = discord.Poll(question=POLL_QUESTION, duration=timedelta(hours=POLL_HOURS))
            for item in chosen:
                poll.add_answer(text=item.title)
            await ctx.send(poll=poll)


async def setup(bot):
    await bot.add_cog(CardLab(bot))
