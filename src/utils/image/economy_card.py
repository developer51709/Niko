"""
Premium PIL renderers for the Café economy.

Every public coroutine returns a `BytesIO` containing a PNG that can be
sent as a `discord.File` and referenced from a `discord.ui.MediaGallery`
inside a Components-V2 LayoutView.

All CPU-bound work is offloaded to a thread executor via `asyncio.to_thread`,
so the bot's event loop stays fully responsive.

Avatar fetching: callers should pass raw avatar bytes (already downloaded
off-loop). A safe placeholder is used when avatar bytes are missing.
"""

from __future__ import annotations

import asyncio
import math
import os
import requests
import unicodedata
from io import BytesIO
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


# ── Palette ─────────────────────────────────────────────────────────────────
BG_TOP        = (38, 26, 22)        # warm espresso
BG_BOT        = (18, 12, 10)
PANEL_BG      = (50, 36, 30, 230)
PANEL_BORDER  = (110, 78, 50, 220)

CREAM         = (245, 232, 210)
CREAM_DIM     = (200, 188, 168)
GOLD          = (255, 196, 92)
GOLD_BRIGHT   = (255, 220, 140)
COFFEE        = (180, 124, 72)
GREEN_OK      = (118, 226, 156)
RED_BAD       = (244, 110, 124)
PURPLE_RANK   = (200, 162, 255)
SHADOW_RGBA   = (0, 0, 0, 130)


# ── Font loading (cached per size) ──────────────────────────────────────────
_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "LiberationSans-Bold.ttf",
    "arial.ttf",
]
_FONT_REGULAR_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "arial.ttf",
]
_FONT_BOLD_PATH: str | None = None
_FONT_REG_PATH: str | None = None
_FONT_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def _resolve_font_path(candidates: list[str]) -> str:
    for cand in candidates:
        try:
            ImageFont.truetype(cand, 12)
            return cand
        except (IOError, OSError):
            continue
    return ""


def _bold(size: int) -> ImageFont.FreeTypeFont:
    global _FONT_BOLD_PATH
    if _FONT_BOLD_PATH is None:
        _FONT_BOLD_PATH = _resolve_font_path(_FONT_CANDIDATES)
    key = ("b", size)
    f = _FONT_CACHE.get(key)
    if f is not None:
        return f
    if _FONT_BOLD_PATH:
        try:
            f = ImageFont.truetype(_FONT_BOLD_PATH, size)
            _FONT_CACHE[key] = f
            return f
        except Exception:
            pass
    f = ImageFont.load_default()
    _FONT_CACHE[key] = f
    return f


def _reg(size: int) -> ImageFont.FreeTypeFont:
    global _FONT_REG_PATH
    if _FONT_REG_PATH is None:
        _FONT_REG_PATH = _resolve_font_path(_FONT_REGULAR_CANDIDATES)
    key = ("r", size)
    f = _FONT_CACHE.get(key)
    if f is not None:
        return f
    if _FONT_REG_PATH:
        try:
            f = ImageFont.truetype(_FONT_REG_PATH, size)
            _FONT_CACHE[key] = f
            return f
        except Exception:
            pass
    return _bold(size)


# ── Primitives ──────────────────────────────────────────────────────────────


def _rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    """Mask for rounded rectangle."""
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255
    )
    return mask


def _vertical_gradient(size: tuple[int, int], top: tuple[int, int, int], bot: tuple[int, int, int]) -> Image.Image:
    """Vertical gradient from top to bottom."""
    w, h = size
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


def _make_canvas(width: int, height: int, radius: int = 26) -> Image.Image:
    """Base canvas with gradient background, subtle vignette, and gold border."""
    # gradient background
    grad = _vertical_gradient((width, height), BG_TOP, BG_BOT).convert("RGBA")
    grad.putalpha(_rounded_mask((width, height), radius))

    # subtle vignette
    vignette = Image.new("L", (width, height), 0)
    vd = ImageDraw.Draw(vignette)
    vd.ellipse(
        [-width // 3, -height // 3, width + width // 3, height + height // 3],
        fill=255,
    )
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=80))
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 90))
    overlay.putalpha(ImageOps.invert(vignette))
    grad = Image.alpha_composite(grad, overlay)

    # gold hairline border
    bd = ImageDraw.Draw(grad)
    bd.rounded_rectangle(
        [0, 0, width - 1, height - 1],
        radius=radius,
        outline=PANEL_BORDER,
        width=2,
    )
    return grad


def _panel(canvas: Image.Image, x: int, y: int, w: int, h: int, radius: int = 16):
    """Translucent rounded panel with thin gold border."""
    panel = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle(
        [0, 0, w - 1, h - 1],
        radius=radius,
        fill=PANEL_BG,
        outline=PANEL_BORDER,
        width=2,
    )
    canvas.alpha_composite(panel, (x, y))


def _circle_avatar(raw: bytes | None, size: int) -> Image.Image:
    """Crop avatar bytes to a perfect circle. Falls back to a stylised coffee-cup glyph."""
    av = None
    if raw:
        try:
            av = Image.open(BytesIO(raw)).convert("RGBA")
        except Exception:
            av = None

    if av is None:
        av = Image.new("RGBA", (size, size), (60, 42, 32, 255))
        d = ImageDraw.Draw(av)
        d.ellipse([8, 8, size - 8, size - 8], fill=(110, 78, 50, 255))
        # Stylised coffee cup glyph (no emoji font dependency)
        cup_w = int(size * 0.45)
        cup_h = int(size * 0.32)
        cup_x = (size - cup_w) // 2
        cup_y = (size - cup_h) // 2 + int(size * 0.04)
        d.rounded_rectangle(
            [cup_x, cup_y, cup_x + cup_w, cup_y + cup_h],
            radius=cup_h // 4, fill=CREAM,
        )
        d.ellipse(
            [cup_x + cup_w - 6, cup_y + 6, cup_x + cup_w + cup_h // 2, cup_y + cup_h - 6],
            outline=CREAM, width=4,
        )
        for i in range(3):
            wx = cup_x + 8 + i * (cup_w // 3)
            d.line(
                [(wx, cup_y - int(size * 0.08)), (wx + 4, cup_y - int(size * 0.16))],
                fill=CREAM, width=3,
            )
    else:
        av = av.resize((size, size), Image.LANCZOS)

    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size, size], fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(av, (0, 0), mask)
    return out


def _draw_circle_outline(canvas: Image.Image, cx: int, cy: int, r: int, color, width: int = 4):
    """Draw a circle outline on the canvas."""
    d = ImageDraw.Draw(canvas)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)


def _format_amount(n: int) -> str:
    """Compact human-friendly number. 12_345_678 → 12.35M"""
    n = int(n)
    if abs(n) >= 1_000_000_000:
        return f"{n / 1_000_000_000:.2f}B"
    if abs(n) >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if abs(n) >= 10_000:
        return f"{n / 1_000:.1f}K"
    return f"{n:,}"


def _truncate(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> str:
    """Truncate text to fit within max_w, adding ellipsis if needed."""
    if font.getlength(text) <= max_w:
        return text
    while text and font.getlength(text + "…") > max_w:
        text = text[:-1]
    return text + "…"


def _emoji_to_codepoints(emoji: str) -> str:
    # Convert emoji into hyphen-separated lowercase hex codepoints
    return "-".join(f"{ord(c):x}" for c in emoji)


def _render_emoji(emoji: str, size: int) -> Image.Image:
    """Render an emoji using Twemoji PNG assets."""
    code = _emoji_to_codepoints(emoji)
    url = f"https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/{code}.png"

    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Twemoji asset not found for {emoji} ({code})")

    img = Image.open(BytesIO(response.content)).convert("RGBA")
    img = img.resize((size, size), Image.LANCZOS)
    return img


def _normalize_text(text: str) -> str:
    """Normalize text to remove font modifiers (bold, italic, script, fraktur, etc.)."""
    # NFKD decomposes styled characters into base characters + modifiers
    decomposed = unicodedata.normalize("NFKD", text)

    # Keep only characters that are not combining marks
    # (font modifiers become combining marks after NFKD)
    cleaned = "".join(c for c in decomposed if not unicodedata.combining(c))

    return cleaned


# ── Stat chip ──────────────────────────────────────────────────────────────


def _stat_chip(
    canvas: Image.Image,
    x: int,
    y: int,
    w: int,
    h: int,
    label: str,
    value: str,
    accent: tuple[int, int, int] = GOLD,
):
    _panel(canvas, x, y, w, h, radius=14)
    d = ImageDraw.Draw(canvas)

    label_font = _reg(13)
    d.text((x + 16, y + 11), label.upper(), fill=CREAM_DIM, font=label_font)

    # Auto-shrink value font so it always fits inside the chip
    inner = w - 32
    chosen = None
    for candidate in (28, 24, 20, 17):
        f = _bold(candidate)
        if f.getlength(value) <= inner:
            chosen = f
            break
    if chosen is None:
        chosen = _bold(17)
        value = _truncate(value, chosen, inner)
    d.text((x + 16, y + 32), value, fill=accent, font=chosen)


def _progress_bar(
    canvas: Image.Image,
    x: int,
    y: int,
    w: int,
    h: int,
    pct: float,
    fill_top: tuple[int, int, int] = GOLD,
    fill_bot: tuple[int, int, int] = COFFEE,
):
    pct = max(0.0, min(1.0, pct))
    # track
    track = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    td = ImageDraw.Draw(track)
    td.rounded_rectangle([0, 0, w - 1, h - 1], radius=h // 2, fill=(0, 0, 0, 110), outline=PANEL_BORDER, width=1)
    canvas.alpha_composite(track, (x, y))

    if pct <= 0.001:
        return
    fill_w = max(h, int(w * pct))
    fill_img = _vertical_gradient((fill_w, h), fill_top, fill_bot).convert("RGBA")
    fill_img.putalpha(_rounded_mask((fill_w, h), h // 2))
    canvas.alpha_composite(fill_img, (x, y))


# ──────────────────────────────────────────────────────────────────────────
# BALANCE / PROFILE CARD
# ──────────────────────────────────────────────────────────────────────────

CARD_W = 820
BALANCE_H = 380


def _render_balance_sync(
    avatar_bytes: bytes | None,
    name: str,
    cash: int,
    bank: int,
    bank_cap_v: int,
    bank_tier_name: str,
    net_worth: int,
    level: int,
    xp_in_level: int,
    xp_for_next: int,
    job_name: str,
    job_emoji: str,
    daily_streak: int,
    rank: int | None,
    title: str = "Wallet",
) -> BytesIO:
    canvas = _make_canvas(CARD_W, BALANCE_H, radius=28)
    d = ImageDraw.Draw(canvas)

    # ── Header bar ──
    d.text((36, 28), "CAFÉ ECONOMY", fill=GOLD, font=_bold(18))
    d.text((36, 54), title, fill=CREAM, font=_bold(34))

    # rank pill (top-right)
    if rank is not None:
        pill_text = f"#{rank} on the leaderboard"
        pf = _reg(14)
        pw = int(pf.getlength(pill_text)) + 28
        ph = 28
        px = CARD_W - pw - 36
        py = 36
        pill = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        pd = ImageDraw.Draw(pill)
        pd.rounded_rectangle([0, 0, pw - 1, ph - 1], radius=ph // 2, fill=(0, 0, 0, 130), outline=GOLD, width=1)
        pd.text((14, 5), pill_text, fill=GOLD, font=pf)
        canvas.alpha_composite(pill, (px, py))

    # ── Avatar + name (left side) ──
    avatar_size = 116
    avatar_x = 40
    avatar_y = 110
    avatar = _circle_avatar(avatar_bytes, avatar_size)
    canvas.alpha_composite(avatar, (avatar_x, avatar_y))
    _draw_circle_outline(
        canvas,
        avatar_x + avatar_size // 2,
        avatar_y + avatar_size // 2,
        avatar_size // 2 + 3,
        GOLD,
        width=3,
    )

    name_x = avatar_x + avatar_size + 22
    name_font = _bold(28)
    sub_font = _reg(15)
    d.text(
        (name_x, avatar_y + 6),
        _truncate(name, name_font, CARD_W - name_x - 40),
        fill=CREAM,
        font=name_font,
    )
    job_line = f"{job_name}   •   Streak {daily_streak}"
    if job_emoji:
        job_line = f"{job_emoji}  " + job_line
    d.text(
        (name_x, avatar_y + 44),
        job_line,
        fill=CREAM_DIM,
        font=sub_font,
    )

    # Big net worth (right side)
    nw_label = "NET WORTH"
    nw_value = f"{int(net_worth):,}"
    nw_font  = _bold(28)
    lf       = _reg(13)
    nw_w     = int(nw_font.getlength(nw_value))
    lab_w    = int(lf.getlength(nw_label))
    right    = CARD_W - 40
    d.text((right - lab_w, avatar_y + 12), nw_label, fill=CREAM_DIM, font=lf)
    d.text((right - nw_w,  avatar_y + 32), nw_value, fill=GOLD_BRIGHT, font=nw_font)

    # ── Three stat chips: Cash / Bank / Bank Tier ──
    chips_y = avatar_y + avatar_size + 28
    chip_h  = 78
    gap     = 14
    chip_w  = (CARD_W - 80 - gap * 2) // 3

    bank_pct  = 0.0 if bank_cap_v <= 0 else min(1.0, bank / bank_cap_v)
    bank_text = f"{_format_amount(bank)} / {_format_amount(bank_cap_v)}"

    _stat_chip(canvas, 40,                           chips_y, chip_w, chip_h, "Cash",       _format_amount(cash),  GOLD)
    _stat_chip(canvas, 40 + chip_w + gap,            chips_y, chip_w, chip_h, "Bank",       bank_text,             GREEN_OK)
    _stat_chip(canvas, 40 + (chip_w + gap) * 2,      chips_y, chip_w, chip_h, "Vault Tier", bank_tier_name,        PURPLE_RANK)

    # ── XP bar ──
    bar_y = chips_y + chip_h + 22
    pct = 0.0 if xp_for_next <= 0 else xp_in_level / xp_for_next
    d.text((40, bar_y - 22), f"LEVEL {level}", fill=CREAM, font=_bold(15))
    xp_text = f"{xp_in_level}/{xp_for_next} XP"
    xp_w = int(_reg(13).getlength(xp_text))
    d.text((CARD_W - 40 - xp_w, bar_y - 20), xp_text, fill=CREAM_DIM, font=_reg(13))
    _progress_bar(canvas, 40, bar_y, CARD_W - 80, 16, pct, fill_top=GOLD_BRIGHT, fill_bot=COFFEE)

    out = BytesIO()
    canvas.convert("RGB").save(out, format="PNG", optimize=True)
    out.seek(0)
    return out


async def render_balance_card(
    *,
    avatar_bytes: bytes | None,
    name: str,
    cash: int,
    bank: int,
    bank_cap_v: int,
    bank_tier_name: str,
    net_worth: int,
    level: int,
    xp_in_level: int,
    xp_for_next: int,
    job_name: str,
    job_emoji: str,
    daily_streak: int,
    rank: int | None = None,
    title: str = "Wallet",
) -> BytesIO:
    return await asyncio.to_thread(
        _render_balance_sync,
        avatar_bytes,
        name,
        cash,
        bank,
        bank_cap_v,
        bank_tier_name,
        net_worth,
        level,
        xp_in_level,
        xp_for_next,
        job_name,
        job_emoji,
        daily_streak,
        rank,
        title,
    )


# ──────────────────────────────────────────────────────────────────────────
# REWARD CARD (daily / work / crime success)
# ──────────────────────────────────────────────────────────────────────────

REWARD_W = 820
REWARD_H = 280


def _render_reward_sync(
    avatar_bytes: bytes | None,
    name: str,
    title: str,
    subtitle: str,
    amount: int,
    new_balance: int,
    accent: tuple[int, int, int],
    footer: str,
) -> BytesIO:
    canvas = _make_canvas(REWARD_W, REWARD_H, radius=28)
    d = ImageDraw.Draw(canvas)

    # Avatar
    av_size = 110
    av_x, av_y = 36, 60
    avatar = _circle_avatar(avatar_bytes, av_size)
    canvas.alpha_composite(avatar, (av_x, av_y))
    _draw_circle_outline(canvas, av_x + av_size // 2, av_y + av_size // 2, av_size // 2 + 3, accent, width=3)

    # Header
    d.text((36, 22), "CAFÉ ECONOMY", fill=GOLD, font=_bold(16))

    # Title + subtitle
    text_x = av_x + av_size + 24
    title_font = _bold(28)
    sub_font   = _reg(16)
    # render emojis in the title
    text_parts = title.split(" ")
    for i, part in enumerate(text_parts):
        if part.startswith(("🏆", "💰", "🎖️", "🥇", "🥈", "🥉", "🏅", "💸", "💵", "💴", "💶", "💷", "✨")):
            emoji = _render_emoji(part, 28)
            canvas.alpha_composite(emoji, (36 + i * 36, 54))
            text_parts[i] = "  "  # remove the emoji from the title
        else:
            text_parts[i] = part
        title = " ".join(text_parts)
    # clean up any fonts in the name like 𝐭𝐡𝐢𝐬 or 𝕥𝕙𝕚𝕤 that can't be rendered by PIL
    name = _normalize_text(name)
    text_parts = name.split(" ")
    for i, part in enumerate(text_parts):
        if part.startswith(("🏆", "💰", "🎖️", "🥇", "🥈", "🥉", "🏅", "💸", "💵", "💴", "💶", "💷", "✨")):
            emoji = _render_emoji(part, 28)
            canvas.alpha_composite(emoji, (36 + i * 36, 54))
            text_parts[i] = "  "  # remove the emoji from the title
        else:
            text_parts[i] = part
        name = " ".join(text_parts)
    d.text(
        (text_x, av_y + 4),
        _truncate(f"{title} — {name}", title_font, REWARD_W - text_x - 36),
        fill=CREAM,
        font=title_font,
    )
    d.text((text_x, av_y + 42), _truncate(subtitle, sub_font, REWARD_W - text_x - 36), fill=CREAM_DIM, font=sub_font)

    # Big amount block (right side panel)
    panel_w = 280
    panel_h = 90
    panel_x = REWARD_W - panel_w - 36
    panel_y = av_y + 72
    _panel(canvas, panel_x, panel_y, panel_w, panel_h, radius=18)

    sign = "+" if amount >= 0 else "−"
    amt_value = f"{sign}{abs(int(amount)):,}"
    amt_font  = _bold(40)
    label_font = _reg(13)

    aw = int(amt_font.getlength(amt_value))
    d.text((panel_x + (panel_w - aw) // 2, panel_y + 18),
           amt_value, fill=accent, font=amt_font)

    nb_text = f"new balance: {int(new_balance):,}"
    nbw = int(label_font.getlength(nb_text))
    d.text((panel_x + (panel_w - nbw) // 2, panel_y + 60),
           nb_text, fill=CREAM_DIM, font=label_font)

    # Footer
    if footer:
        text_parts = footer.split(" ")
        for i, part in enumerate(text_parts):
            if part.startswith(("🏆", "💰", "🎖️", "🥇", "🥈", "🥉", "🏅", "💸", "💵", "💴", "💶", "💷", "✨")):
                emoji = _render_emoji(part, 28)
                canvas.alpha_composite(emoji, (36 + i * 36, 54))
                text_parts[i] = "  "  # remove the emoji from the title
            else:
                text_parts[i] = part
            footer = " ".join(text_parts)
        d.text((36, REWARD_H - 38), footer, fill=CREAM_DIM, font=_reg(14))

    out = BytesIO()
    canvas.convert("RGB").save(out, format="PNG", optimize=True)
    out.seek(0)
    return out


async def render_reward_card(
    *,
    avatar_bytes: bytes | None,
    name: str,
    title: str,
    subtitle: str,
    amount: int,
    new_balance: int,
    accent: tuple[int, int, int] = GOLD,
    footer: str = "",
) -> BytesIO:
    return await asyncio.to_thread(
        _render_reward_sync,
        avatar_bytes,
        name,
        title,
        subtitle,
        amount,
        new_balance,
        accent,
        footer,
    )


# Convenience accents exported for cogs that don't want to import the palette
ACCENT_GOLD  = GOLD_BRIGHT
ACCENT_GREEN = GREEN_OK
ACCENT_RED   = RED_BAD


# ──────────────────────────────────────────────────────────────────────────
# LEADERBOARD CARD
# ──────────────────────────────────────────────────────────────────────────

LB_W = 820
LB_ROW_H = 56


def _render_leaderboard_sync(
    title: str,
    entries: list[dict],
    page: int,
    pages: int,
) -> BytesIO:
    """
    entries: list of {"rank": int, "name": str, "total": int, "avatar": bytes|None}
    """
    n = len(entries)
    height = 110 + n * (LB_ROW_H + 10) + 60
    canvas = _make_canvas(LB_W, height, radius=28)
    d = ImageDraw.Draw(canvas)

    # Header
    d.text((36, 28), "CAFÉ ECONOMY", fill=GOLD, font=_bold(16))
    text_parts = title.split(" ")
    for i, part in enumerate(text_parts):
        if part.startswith(("🏆", "💰", "🎖️", "🥇", "🥈", "🥉", "🏅")):
            emoji = _render_emoji(part, 28)
            canvas.alpha_composite(emoji, (36 + i * 36, 54))
            text_parts[i] = "  "  # remove the emoji from the title
        else:
            text_parts[i] = part
        title = " ".join(text_parts)
    d.text((36, 54), title, fill=CREAM, font=_bold(28))
    page_text = f"Page {page}/{pages}"
    pf = _reg(14)
    pw = int(pf.getlength(page_text))
    d.text((LB_W - 36 - pw, 60), page_text, fill=CREAM_DIM, font=pf)

    y = 110
    medals = {1: "1st", 2: "2nd", 3: "3rd"}
    for entry in entries:
        rank   = entry["rank"]
        name   = entry["name"]
        total  = entry["total"]
        avatar = entry.get("avatar")

        is_top3 = rank <= 3
        accent = GOLD_BRIGHT if rank == 1 else (CREAM if rank == 2 else (COFFEE if rank == 3 else CREAM_DIM))
        _panel(canvas, 28, y, LB_W - 56, LB_ROW_H, radius=14)

        # rank
        rank_text = medals.get(rank, f"#{rank}")
        rf = _bold(22 if is_top3 else 18)
        rw = int(rf.getlength(rank_text))
        d.text((28 + (60 - rw) // 2, y + (LB_ROW_H - 28) // 2), rank_text, fill=accent, font=rf)

        # avatar
        av = _circle_avatar(avatar, LB_ROW_H - 16)
        canvas.alpha_composite(av, (28 + 64, y + 8))

        # name
        nf = _bold(20)
        nx = 28 + 64 + (LB_ROW_H - 16) + 14
        max_name_w = LB_W - 56 - 220 - (nx - 28)
        # clean up any fonts in the name like 𝐭𝐡𝐢𝐬 or 𝕥𝕙𝕚𝕤 that can't be rendered by PIL
        name = _normalize_text(name)
        text_parts = name.split(" ")
        for i, part in enumerate(text_parts):
            if part.startswith(("🏆", "💰", "🎖️", "🥇", "🥈", "🥉", "🏅", "💸", "💵", "💴", "💶", "💷", "✨")):
                emoji = _render_emoji(part, 28)
                canvas.alpha_composite(emoji, (36 + i * 36, 54))
                text_parts[i] = "  "  # remove the emoji from the title
            else:
                text_parts[i] = part
            name = " ".join(text_parts)
        d.text((nx, y + 14), _truncate(name, nf, max_name_w), fill=CREAM, font=nf)

        # total
        amt = f"{int(total):,}"
        af = _bold(22)
        aw = int(af.getlength(amt))
        d.text((LB_W - 28 - 24 - aw, y + 14), amt, fill=accent, font=af)

        y += LB_ROW_H + 10

    # Footer
    d.text((36, height - 36), "use ‹ › below to navigate", fill=CREAM_DIM, font=_reg(13))

    out = BytesIO()
    canvas.convert("RGB").save(out, format="PNG", optimize=True)
    out.seek(0)
    return out


async def render_leaderboard_card(
    *,
    title: str,
    entries: list[dict],
    page: int = 1,
    pages: int = 1,
) -> BytesIO:
    return await asyncio.to_thread(
        _render_leaderboard_sync, title, entries, page, pages
    )


# ──────────────────────────────────────────────────────────────────────────
# Avatar fetch helper
# ──────────────────────────────────────────────────────────────────────────


async def fetch_avatar_bytes(url: str | None, *, size: int = 256) -> bytes | None:
    """
    Pull avatar bytes off-loop. Returns None on any failure so renderers
    can fall back to the placeholder glyph.
    """
    if not url:
        return None
    try:
        import requests  # local import keeps this module light to import
        # discord.Asset URLs already accept ?size=, but appending again is harmless
        sep = "&" if "?" in url else "?"
        full = f"{url}{sep}size={size}"
        r = await asyncio.to_thread(requests.get, full, timeout=5)
        if r.status_code == 200 and r.content:
            return r.content
    except Exception:
        return None
    return None
