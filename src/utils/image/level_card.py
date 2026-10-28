"""
Premium PIL renderers for the Niko leveling system.

Every public coroutine returns a ``BytesIO`` containing a PNG that can be
sent as a ``discord.File`` and referenced from a ``discord.ui.MediaGallery``
inside a Components-V2 LayoutView.

All CPU-bound work is offloaded to ``asyncio.to_thread`` so the bot's
event loop stays fully responsive.

Avatar fetching: callers should pass raw avatar bytes (already downloaded
off-loop).  A safe placeholder is used when avatar bytes are missing.

Customization: callers may pass accent / background colour tuples to tint
cards per-guild.  Defaults match the website theme palette, imported from
`economy_card.py`.
"""

from __future__ import annotations

import asyncio
import requests
from io import BytesIO

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps
from utils.image._font_resolver import (
    get_bold,
    get_reg,
    font_getlength,
    draw_text_with_fallback,
)
from utils.image.economy_card import (
    _circle_avatar,
    _draw_circle_outline,
    _make_canvas,
    _panel,
    _progress_bar,
    _rounded_mask,
    _vertical_gradient,
    _format_amount,
    _truncate,
    render_text_with_emojis,
    _strip_discord_emoji,
    fetch_avatar_bytes,
    _bold,
    _reg,
    # Theme palette (see `economy_card.py`)
    ACCENT,
    ACCENT_BRIGHT,
    CANVAS_BOT,
    CANVAS_TOP,
    DIM,
    INK,
    MUTED,
)


# ── Helpers ────────────────────────────────────────────────────────────────


def _resolve_colours(
    accent_rgb: tuple[int, int, int] | None = None,
    bg_top_rgb: tuple[int, int, int] | None = None,
    bg_bot_rgb: tuple[int, int, int] | None = None,
):
    """Return (accent, bg_top, bg_bot) from optional overrides, falling back
    to the theme defaults.  Input tuples are plain RGB ints (0-255)."""
    accent = tuple(accent_rgb) if accent_rgb else ACCENT_BRIGHT
    top    = tuple(bg_top_rgb) if bg_top_rgb else CANVAS_TOP
    bot    = tuple(bg_bot_rgb) if bg_bot_rgb else CANVAS_BOT
    return accent, top, bot


# ──────────────────────────────────────────────────────────────────────────
# RANK / LEVEL CARD
# ──────────────────────────────────────────────────────────────────────────

RANK_W = 820
RANK_H = 340


def _render_level_sync(
    avatar_bytes: bytes | None,
    name: str,
    level: int,
    xp: int,
    xp_for_next: int,
    rank: int,
    *,
    accent: tuple[int, int, int] | None = None,
    bg_top: tuple[int, int, int] | None = None,
    bg_bot: tuple[int, int, int] | None = None,
) -> BytesIO:
    ac, bt, bb = _resolve_colours(accent, bg_top, bg_bot)

    # Build canvas with custom gradient
    grad = _vertical_gradient((RANK_W, RANK_H), bt, bb).convert("RGBA")
    grad.putalpha(_rounded_mask((RANK_W, RANK_H), 28))

    # vignette
    vignette = Image.new("L", (RANK_W, RANK_H), 0)
    vd = ImageDraw.Draw(vignette)
    vd.ellipse([-RANK_W // 3, -RANK_H // 3, RANK_W + RANK_W // 3, RANK_H + RANK_H // 3], fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=80))
    overlay = Image.new("RGBA", (RANK_W, RANK_H), (0, 0, 0, 90))
    overlay.putalpha(ImageOps.invert(vignette))
    canvas = Image.alpha_composite(grad, overlay)

    # The vignette overlay covers the whole rectangle, so compositing it fills
    # the space outside the rounded corners back in. Clip the alpha to the
    # rounded shape so the corner cut-outs stay transparent in the saved image.
    canvas.putalpha(ImageChops.multiply(canvas.getchannel("A"), _rounded_mask((RANK_W, RANK_H), 28)))

    # border
    bd = ImageDraw.Draw(canvas)
    bd.rounded_rectangle([0, 0, RANK_W - 1, RANK_H - 1], radius=28, outline=ac, width=2)

    d = ImageDraw.Draw(canvas)

    # ── Header ──
    d.text((36, 28), "NIKO LEVELING", fill=ACCENT, font=_bold(16))
    d.text((36, 52), f"Level Stats — {name}", fill=INK, font=_bold(28))

    # rank pill (top-right)
    pill_text = f"#{rank} in this server"
    pf = _reg(14)
    pw = int(pf.getlength(pill_text)) + 28
    ph = 28
    px = RANK_W - pw - 36
    py = 36
    pill = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle([0, 0, pw - 1, ph - 1], radius=ph // 2, fill=(0, 0, 0, 130), outline=ac, width=1)
    pd.text((14, 5), pill_text, fill=ac, font=pf)
    canvas.alpha_composite(pill, (px, py))

    # ── Avatar (left) ──
    av_size = 120
    av_x, av_y = 36, 96
    avatar = _circle_avatar(avatar_bytes, av_size)
    canvas.alpha_composite(avatar, (av_x, av_y))
    _draw_circle_outline(canvas, av_x + av_size // 2, av_y + av_size // 2, av_size // 2 + 3, ac, width=3)

    # ── Level badge (right of avatar) ──
    badge_x = av_x + av_size + 28
    badge_y = av_y + 6

    # Big level number
    level_font = _bold(56)
    d.text((badge_x, badge_y - 8), str(level), fill=ac, font=level_font)
    lvl_label_w = int(level_font.getlength(str(level)))
    lf = _reg(16)
    d.text((badge_x + lvl_label_w + 8, badge_y + 18), "LEVEL", fill=DIM, font=lf)

    # ── Stats columns ──
    stat_x = badge_x + lvl_label_w + 100
    stat_label_font = _reg(13)
    stat_value_font = _bold(24)

    # XP
    d.text((stat_x, av_y + 8), "XP", fill=DIM, font=stat_label_font)
    xp_text = f"{_format_amount(xp)} / {_format_amount(xp_for_next)}"
    d.text((stat_x, av_y + 28), xp_text, fill=INK, font=stat_value_font)

    # Rank
    rank_x = stat_x + 220
    d.text((rank_x, av_y + 8), "RANK", fill=DIM, font=stat_label_font)
    rank_text = f"#{rank}"
    d.text((rank_x, av_y + 28), rank_text, fill=ACCENT_BRIGHT, font=stat_value_font)

    # ── XP progress bar ──
    bar_y = av_y + av_size + 30
    pct = 0.0 if xp_for_next <= 0 else min(1.0, xp / xp_for_next)
    _progress_bar(canvas, 36, bar_y, RANK_W - 72, 18, pct, fill_top=ac, fill_bot=ACCENT)
    pct_text = f"{pct * 100:.0f}%"
    pw2 = int(_reg(13).getlength(pct_text))
    d.text((RANK_W - 36 - pw2, bar_y + 2), pct_text, fill=DIM, font=_reg(13))

    out = BytesIO()
    # Save with the alpha channel so the rounded corner cut-outs stay
    # transparent instead of becoming opaque black.
    canvas.save(out, format="PNG", optimize=True)
    out.seek(0)
    return out


async def render_level_card(
    *,
    avatar_bytes: bytes | None,
    name: str,
    level: int,
    xp: int,
    xp_for_next: int,
    rank: int,
    accent: tuple[int, int, int] | None = None,
    bg_top: tuple[int, int, int] | None = None,
    bg_bot: tuple[int, int, int] | None = None,
) -> BytesIO:
    return await asyncio.to_thread(
        _render_level_sync,
        avatar_bytes, name, level, xp, xp_for_next, rank,
        accent=accent, bg_top=bg_top, bg_bot=bg_bot,
    )

