"""
Blackjack table image renderer.

Generates premium-looking blackjack table images using Pillow.  Cards are
drawn procedurally (no asset files required) — the suit symbols are vector
shapes so rendering is font-independent for the icons themselves.

The synchronous renderer never touches asyncio.  The public `render_table`
coroutine offloads the work to a thread executor via `asyncio.to_thread`
so the bot's event loop stays fully responsive even for complex tables.
"""

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import asyncio
import os
from utils.image._font_resolver import get_bold


# ── Layout constants ────────────────────────────────────────────────────────
CARD_W, CARD_H   = 110, 158
CARD_RADIUS      = 12
CARD_STEP        = 60   # x-distance between successive cards in a hand

TABLE_BG_TOP     = (22, 70, 44)
TABLE_BG_BOT     = (8, 36, 22)
TABLE_PADDING    = 28
TABLE_RADIUS     = 24

CARD_FACE_BG     = (250, 250, 248)
CARD_BACK_BG     = (24, 50, 110)
CARD_BACK_LINE   = (60, 92, 168)
CARD_BORDER      = (40, 40, 40)
CARD_SHADOW_RGBA = (0, 0, 0, 110)

SUIT_RED         = (200, 30, 30)
SUIT_BLK         = (15, 15, 15)

ACTIVE_HALO      = (255, 215, 0)
TEXT_WHITE       = (245, 245, 245)
TEXT_DIM         = (190, 190, 190)
TEXT_GOLD        = (255, 215, 0)
TEXT_GREEN       = (87, 242, 135)
TEXT_RED         = (237, 90, 96)


# ── Font helper (Termux/Android-safe via shared resolver) ───────────────────
def _font(size: int) -> ImageFont.ImageFont:
    return get_bold(size)


# ── Suit drawing (vector — no glyph dependency) ─────────────────────────────

def _draw_heart(d: ImageDraw.ImageDraw, cx: float, cy: float, size: float, color):
    s = size
    r = s * 0.30
    d.ellipse([cx - s*0.5,        cy - s*0.45, cx - s*0.5 + 2*r, cy - s*0.45 + 2*r], fill=color)
    d.ellipse([cx + s*0.5 - 2*r,  cy - s*0.45, cx + s*0.5,       cy - s*0.45 + 2*r], fill=color)
    d.polygon([
        (cx - s*0.55, cy - s*0.10),
        (cx + s*0.55, cy - s*0.10),
        (cx,          cy + s*0.55),
    ], fill=color)


def _draw_diamond(d, cx, cy, size, color):
    s = size * 0.55
    d.polygon([
        (cx,         cy - s),
        (cx + s*0.7, cy),
        (cx,         cy + s),
        (cx - s*0.7, cy),
    ], fill=color)


def _draw_spade(d, cx, cy, size, color):
    s = size
    r = s * 0.30
    # inverted heart shape (point up)
    d.polygon([
        (cx,          cy - s*0.55),
        (cx - s*0.55, cy + s*0.10),
        (cx + s*0.55, cy + s*0.10),
    ], fill=color)
    d.ellipse([cx - s*0.5,       cy + s*0.10 - 2*r*0.6, cx - s*0.5 + 2*r,  cy + s*0.10 + 2*r*0.4], fill=color)
    d.ellipse([cx + s*0.5 - 2*r, cy + s*0.10 - 2*r*0.6, cx + s*0.5,        cy + s*0.10 + 2*r*0.4], fill=color)
    # stem
    d.polygon([
        (cx - s*0.16, cy + s*0.30),
        (cx + s*0.16, cy + s*0.30),
        (cx + s*0.34, cy + s*0.62),
        (cx - s*0.34, cy + s*0.62),
    ], fill=color)


def _draw_club(d, cx, cy, size, color):
    s = size
    r = s * 0.30
    d.ellipse([cx - r,           cy - s*0.55 - r, cx + r,           cy - s*0.55 + r], fill=color)
    d.ellipse([cx - s*0.45 - r,  cy - r,          cx - s*0.45 + r,  cy + r],          fill=color)
    d.ellipse([cx + s*0.45 - r,  cy - r,          cx + s*0.45 + r,  cy + r],          fill=color)
    d.polygon([
        (cx - s*0.16, cy + s*0.05),
        (cx + s*0.16, cy + s*0.05),
        (cx + s*0.34, cy + s*0.62),
        (cx - s*0.34, cy + s*0.62),
    ], fill=color)


_SUIT_FNS = {"H": _draw_heart, "D": _draw_diamond, "S": _draw_spade, "C": _draw_club}


def _suit_color(suit: str):
    return SUIT_RED if suit in ("H", "D") else SUIT_BLK


# ── Card images ─────────────────────────────────────────────────────────────

def _rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255
    )
    return mask


def _make_card_face(rank: str, suit: str) -> Image.Image:
    img = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        [0, 0, CARD_W - 1, CARD_H - 1],
        radius=CARD_RADIUS,
        fill=CARD_FACE_BG,
        outline=CARD_BORDER,
        width=2,
    )

    color = _suit_color(suit)
    suit_fn = _SUIT_FNS[suit]

    rank_font = _font(26 if rank == "10" else 30)
    rank_text = rank

    # Top-left rank + small suit
    draw.text((9, 5), rank_text, fill=color, font=rank_font)
    suit_fn(draw, 21, 50, 16, color)

    # Center large suit
    suit_fn(draw, CARD_W // 2, CARD_H // 2 + 4, 46, color)

    # Bottom-right (rotated copy of top-left)
    bot = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bot)
    bd.text((9, 5), rank_text, fill=color, font=rank_font)
    suit_fn(bd, 21, 50, 16, color)
    bot = bot.rotate(180)
    img = Image.alpha_composite(img, bot)

    return img


def _make_card_back() -> Image.Image:
    base = Image.new("RGBA", (CARD_W, CARD_H), CARD_BACK_BG + (255,))
    draw = ImageDraw.Draw(base)

    # Diagonal cross-hatch pattern
    for i in range(-CARD_H, CARD_W + CARD_H, 10):
        draw.line([(i, 0), (i + CARD_H, CARD_H)], fill=CARD_BACK_LINE, width=1)
        draw.line([(i, CARD_H), (i + CARD_H, 0)], fill=CARD_BACK_LINE, width=1)

    # Inner border
    draw.rounded_rectangle(
        [6, 6, CARD_W - 7, CARD_H - 7],
        radius=CARD_RADIUS - 4,
        outline=(255, 215, 0),
        width=2,
    )

    # Mask to rounded card shape
    masked = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    masked.paste(base, (0, 0), _rounded_mask((CARD_W, CARD_H), CARD_RADIUS))

    # Outer border on top
    od = ImageDraw.Draw(masked)
    od.rounded_rectangle(
        [0, 0, CARD_W - 1, CARD_H - 1],
        radius=CARD_RADIUS,
        outline=CARD_BORDER,
        width=2,
    )
    return masked


def _paste_with_shadow(canvas: Image.Image, card: Image.Image, x: int, y: int):
    shadow = Image.new("RGBA", (CARD_W + 20, CARD_H + 20), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        [6, 8, CARD_W + 10, CARD_H + 12],
        radius=CARD_RADIUS,
        fill=CARD_SHADOW_RGBA,
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=5))
    canvas.alpha_composite(shadow, (x - 8, y - 4))
    canvas.alpha_composite(card, (x, y))


# ── Hand utilities ──────────────────────────────────────────────────────────

def _hand_value(cards: list[str]) -> int:
    value = 0
    aces = 0
    for c in cards:
        rank = c[:-1]
        if rank.isdigit():
            value += int(rank)
        elif rank in ("J", "Q", "K"):
            value += 10
        else:
            value += 11
            aces += 1
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value


def _hand_pixel_width(card_count: int) -> int:
    if card_count <= 0:
        return 0
    return CARD_W + (card_count - 1) * CARD_STEP


def _draw_hand(canvas: Image.Image, x: int, y: int, cards: list[tuple[str, bool]]):
    """cards = [(card_str, is_back), ...]"""
    cx = x
    for card, is_back in cards:
        face = _make_card_back() if is_back else _make_card_face(card[:-1], card[-1])
        _paste_with_shadow(canvas, face, cx, y)
        cx += CARD_STEP


# ── Top-level renderer ──────────────────────────────────────────────────────

def _render_table_sync(
    player_hands: list[dict],
    dealer_cards: list[str],
    reveal_dealer: bool,
    current_hand_index: int,
    title: str,
    status: str,
    status_color: tuple,
) -> BytesIO:
    n_hands = max(1, len(player_hands))

    widest_player = max((_hand_pixel_width(len(h["cards"])) for h in player_hands), default=CARD_W)
    dealer_width  = _hand_pixel_width(len(dealer_cards))
    width = max(720, widest_player + 2 * TABLE_PADDING + 40, dealer_width + 2 * TABLE_PADDING + 40)

    title_h         = 60 if title else 0
    dealer_block_h  = 36 + CARD_H + 28
    sep_h           = 24
    hand_block_h    = 38 + CARD_H + 26
    status_h        = 50 if status else 20

    height = TABLE_PADDING + title_h + dealer_block_h + sep_h + n_hands * hand_block_h + status_h + TABLE_PADDING

    # Gradient background, rounded
    bg = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    grad = Image.new("RGB", (width, height))
    gd = ImageDraw.Draw(grad)
    for y in range(height):
        t = y / max(1, height - 1)
        r = int(TABLE_BG_TOP[0] + (TABLE_BG_BOT[0] - TABLE_BG_TOP[0]) * t)
        g = int(TABLE_BG_TOP[1] + (TABLE_BG_BOT[1] - TABLE_BG_TOP[1]) * t)
        b = int(TABLE_BG_TOP[2] + (TABLE_BG_BOT[2] - TABLE_BG_TOP[2]) * t)
        gd.line([(0, y), (width, y)], fill=(r, g, b))
    grad_rgba = grad.convert("RGBA")
    grad_rgba.putalpha(_rounded_mask((width, height), TABLE_RADIUS))
    bg.alpha_composite(grad_rgba, (0, 0))

    canvas = bg
    draw = ImageDraw.Draw(canvas)

    y = TABLE_PADDING

    if title:
        draw.text((TABLE_PADDING, y), title, fill=TEXT_WHITE, font=_font(30))
        y += title_h

    # Dealer label
    if reveal_dealer:
        d_val = _hand_value(dealer_cards)
        d_label = f"Dealer  •  {d_val}"
    else:
        d_label = "Dealer"
    draw.text((TABLE_PADDING, y), d_label, fill=TEXT_DIM, font=_font(20))
    y += 32

    # Dealer cards
    dealer_render = [(c, (not reveal_dealer) and i > 0) for i, c in enumerate(dealer_cards)]
    dealer_x = (width - _hand_pixel_width(len(dealer_cards))) // 2
    _draw_hand(canvas, dealer_x, y, dealer_render)
    y += CARD_H + 28

    # Separator line
    draw.line([(TABLE_PADDING, y), (width - TABLE_PADDING, y)], fill=(255, 255, 255, 50), width=1)
    y += sep_h

    # Player hands
    for i, hand in enumerate(player_hands):
        cards = hand["cards"]
        val = _hand_value(cards)
        is_active = (i == current_hand_index) and not hand.get("finished")
        is_bust = val > 21
        is_bj   = (len(cards) == 2 and val == 21)

        if is_bj:
            tag = "  •  BLACKJACK"
        elif is_bust:
            tag = "  •  BUST"
        elif hand.get("finished"):
            tag = "  •  Stand"
        elif is_active:
            tag = "  •  Your move"
        else:
            tag = ""

        label_color = TEXT_GOLD if is_active else TEXT_WHITE
        n_label = f"Hand #{i+1}  •  " if len(player_hands) > 1 else ""
        label_text = f"{n_label}{val}  •  Bet {hand['bet']}{tag}"
        draw.text((TABLE_PADDING, y), label_text, fill=label_color, font=_font(20))
        y += 34

        hx = (width - _hand_pixel_width(len(cards))) // 2

        if is_active:
            draw.rounded_rectangle(
                [hx - 12, y - 8, hx + _hand_pixel_width(len(cards)) + 12, y + CARD_H + 8],
                radius=18, outline=ACTIVE_HALO, width=3,
            )

        _draw_hand(canvas, hx, y, [(c, False) for c in cards])
        y += CARD_H + 26

    # Status
    if status:
        draw.text((TABLE_PADDING, y + 6), status, fill=status_color, font=_font(24))

    out = BytesIO()
    canvas.convert("RGB").save(out, format="PNG", optimize=True)
    out.seek(0)
    return out


async def render_table(
    player_hands: list[dict],
    dealer_cards: list[str],
    *,
    reveal_dealer: bool = False,
    current_hand_index: int = 0,
    title: str = "",
    status: str = "",
    status_color: tuple = TEXT_GOLD,
) -> BytesIO:
    """
    Render a blackjack table as a PNG and return a BytesIO ready for upload.

    Runs the (CPU-bound) Pillow work in a thread executor so the asyncio
    event loop is never blocked.
    """
    return await asyncio.to_thread(
        _render_table_sync,
        player_hands,
        dealer_cards,
        reveal_dealer,
        current_hand_index,
        title,
        status,
        status_color,
    )
