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
cards per-guild.  Defaults match the warm café palette.
"""

from __future__ import annotations

import asyncio
import requests
from io import BytesIO

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
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
    # Default palette
    CREAM,
    CREAM_DIM,
    GOLD,
    GOLD_BRIGHT,
    PURPLE_RANK,
)


# ── Helpers ────────────────────────────────────────────────────────────────


def _resolve_colours(
    accent_rgb: tuple[int, int, int] | None = None,
    bg_top_rgb: tuple[int, int, int] | None = None,
    bg_bot_rgb: tuple[int, int, int] | None = None,
):
    """Return (accent, bg_top, bg_bot) from optional overrides, falling back
    to the café defaults.  Input tuples are plain RGB ints (0-255)."""
    accent = tuple(accent_rgb) if accent_rgb else GOLD_BRIGHT
    top    = tuple(bg_top_rgb) if bg_top_rgb else (38, 26, 22)
    bot    = tuple(bg_bot_rgb) if bg_bot_rgb else (18, 12, 10)
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

    # border
    bd = ImageDraw.Draw(canvas)
    bd.rounded_rectangle([0, 0, RANK_W - 1, RANK_H - 1], radius=28, outline=ac, width=2)

    d = ImageDraw.Draw(canvas)

    # ── Header ──
    d.text((36, 28), "CAFÉ LEVELING", fill=GOLD, font=_bold(16))
    d.text((36, 52), f"Level Stats — {name}", fill=CREAM, font=_bold(28))

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
    d.text((badge_x + lvl_label_w + 8, badge_y + 18), "LEVEL", fill=CREAM_DIM, font=lf)

    # ── Stats columns ──
    stat_x = badge_x + lvl_label_w + 100
    stat_label_font = _reg(13)
    stat_value_font = _bold(24)

    # XP
    d.text((stat_x, av_y + 8), "XP", fill=CREAM_DIM, font=stat_label_font)
    xp_text = f"{_format_amount(xp)} / {_format_amount(xp_for_next)}"
    d.text((stat_x, av_y + 28), xp_text, fill=CREAM, font=stat_value_font)

    # Rank
    rank_x = stat_x + 220
    d.text((rank_x, av_y + 8), "RANK", fill=CREAM_DIM, font=stat_label_font)
    rank_text = f"#{rank}"
    d.text((rank_x, av_y + 28), rank_text, fill=PURPLE_RANK, font=stat_value_font)

    # ── XP progress bar ──
    bar_y = av_y + av_size + 30
    pct = 0.0 if xp_for_next <= 0 else min(1.0, xp / xp_for_next)
    _progress_bar(canvas, 36, bar_y, RANK_W - 72, 18, pct, fill_top=ac, fill_bot=(110, 78, 50))
    pct_text = f"{pct * 100:.0f}%"
    pw2 = int(_reg(13).getlength(pct_text))
    d.text((RANK_W - 36 - pw2, bar_y + 2), pct_text, fill=CREAM_DIM, font=_reg(13))

    out = BytesIO()
    canvas.convert("RGB").save(out, format="PNG", optimize=True)
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


# ──────────────────────────────────────────────────────────────────────────
# LEVEL LEADERBOARD CARD
# ──────────────────────────────────────────────────────────────────────────

LB_W = 820
LB_ROW_H = 60


def _render_level_leaderboard_sync(
    title: str,
    entries: list[dict],
    page: int,
    pages: int,
    *,
    accent: tuple[int, int, int] | None = None,
    bg_top: tuple[int, int, int] | None = None,
    bg_bot: tuple[int, int, int] | None = None,
) -> BytesIO:
    """Render a level leaderboard image card.

    ``entries``: list of ``{"rank": int, "name": str, "level": int, "xp": int, "avatar": bytes|None}``
    """
    ac, bt, bb = _resolve_colours(accent, bg_top, bg_bot)

    n = len(entries)
    height = 110 + n * (LB_ROW_H + 8) + 56
    canvas = _make_canvas(LB_W, height, radius=28)

    # Overwrite gradient with custom colours
    grad = _vertical_gradient((LB_W, height), bt, bb).convert("RGBA")
    grad.putalpha(_rounded_mask((LB_W, height), 28))
    vignette = Image.new("L", (LB_W, height), 0)
    vd = ImageDraw.Draw(vignette)
    vd.ellipse([-LB_W // 3, -height // 3, LB_W + LB_W // 3, height + height // 3], fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=80))
    overlay = Image.new("RGBA", (LB_W, height), (0, 0, 0, 90))
    overlay.putalpha(ImageOps.invert(vignette))
    canvas = Image.alpha_composite(grad, overlay)
    bd = ImageDraw.Draw(canvas)
    bd.rounded_rectangle([0, 0, LB_W - 1, height - 1], radius=28, outline=ac, width=2)

    d = ImageDraw.Draw(canvas)

    # Header
    d.text((36, 28), "CAFÉ LEVELING", fill=GOLD, font=_bold(16))
    render_text_with_emojis(canvas, title, _bold(28), 36, 54, 28, CREAM)
    page_text = f"Page {page}/{pages}"
    pf = _reg(14)
    pw = int(pf.getlength(page_text))
    d.text((LB_W - 36 - pw, 60), page_text, fill=CREAM_DIM, font=pf)

    y = 110
    medals = {1: "1st", 2: "2nd", 3: "3rd"}
    for entry in entries:
        rank  = entry["rank"]
        name  = entry["name"]
        lvl   = entry["level"]
        xp    = entry.get("xp", 0)
        avatar = entry.get("avatar")

        is_top3 = rank <= 3
        entry_accent = GOLD_BRIGHT if rank == 1 else (CREAM if rank == 2 else (ac if rank == 3 else CREAM_DIM))
        _panel(canvas, 28, y, LB_W - 56, LB_ROW_H, radius=14)

        # rank text
        rank_text = medals.get(rank, f"#{rank}")
        rf = _bold(22 if is_top3 else 18)
        rw = int(rf.getlength(rank_text))
        render_text_with_emojis(canvas, rank_text, rf, 28 + (56 - rw) // 2, y + (LB_ROW_H - 22) // 2 - 2, 22, entry_accent)

        # avatar
        av = _circle_avatar(avatar, LB_ROW_H - 16)
        canvas.alpha_composite(av, (28 + 60, y + 8))

        # name
        nx = 28 + 60 + (LB_ROW_H - 16) + 14
        nf = _bold(20)
        render_text_with_emojis(canvas, name, nf, nx, y + 10, 20, CREAM)

        # level + xp on right
        lvl_text = f"Lv.{lvl}"
        lf = _bold(22)
        lw = int(lf.getlength(lvl_text))
        draw_text_with_fallback(d, (LB_W - 28 - 24 - lw, y + 10), lvl_text, size=22, bold=True, fill=ac)

        xp_text = f"{_format_amount(xp)} XP"
        xf = _reg(13)
        xw = int(xf.getlength(xp_text))
        d.text((LB_W - 28 - 24 - xw, y + 36), xp_text, fill=CREAM_DIM, font=xf)

        y += LB_ROW_H + 8

    # footer
    draw_text_with_fallback(d, (36, height - 32), "use arrows below to navigate", size=13, fill=CREAM_DIM)

    out = BytesIO()
    canvas.convert("RGB").save(out, format="PNG", optimize=True)
    out.seek(0)
    return out


async def render_level_leaderboard_card(
    *,
    title: str,
    entries: list[dict],
    page: int = 1,
    pages: int = 1,
    accent: tuple[int, int, int] | None = None,
    bg_top: tuple[int, int, int] | None = None,
    bg_bot: tuple[int, int, int] | None = None,
) -> BytesIO:
    return await asyncio.to_thread(
        _render_level_leaderboard_sync,
        title, entries, page, pages,
        accent=accent, bg_top=bg_top, bg_bot=bg_bot,
    )
