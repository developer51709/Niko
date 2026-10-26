"""
Blackjack table image renderer.

Generates premium-looking blackjack table images using Pillow.  Cards are
drawn procedurally (no asset files required) — the suit symbols are vector
shapes so rendering is font-independent for the icons themselves.

The synchronous renderer never touches asyncio.  The public `render_table`
coroutine offloads the work to a thread executor via `asyncio.to_thread`
so the bot's event loop stays fully responsive even for complex tables.

The table chrome follows the website theme (`web/src/styles.css`): a graphite
canvas with steel accents and sage for positive states.  Playing-card faces
keep their classic colours.
"""

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import asyncio
import math
import os
from functools import lru_cache
from utils.image._font_resolver import get_bold


# ── Layout constants ────────────────────────────────────────────────────────
CARD_W, CARD_H   = 110, 158
CARD_RADIUS      = 12
CARD_STEP        = 60   # x-distance between successive cards in a hand

TABLE_BG_TOP     = (25, 27, 31)      # --surface-muted #191b1f
TABLE_BG_BOT     = (5, 6, 7)         # --canvas        #050607
TABLE_PADDING    = 28
TABLE_RADIUS     = 24

CARD_FACE_BG     = (250, 250, 248)
CARD_BACK_BG     = (32, 34, 38)      # --surface-raised #202226
CARD_BACK_LINE   = (45, 48, 53)      # --line           #2d3035
CARD_BORDER      = (40, 40, 40)
CARD_SHADOW_RGBA = (0, 0, 0, 110)

SUIT_RED         = (200, 30, 30)
SUIT_BLK         = (15, 15, 15)

ACTIVE_HALO      = (213, 217, 223)   # --accent-dark #d5d9df
TEXT_WHITE       = (244, 245, 247)   # --ink         #f4f5f7
TEXT_DIM         = (133, 140, 150)   # --dim         #858c96
TEXT_GOLD        = (139, 213, 177)   # --sage        #8bd5b1
TEXT_GREEN       = (139, 213, 177)   # --sage        #8bd5b1
TEXT_RED         = (232, 162, 162)   # loss amounts


# ── Font helper (Termux/Android-safe via shared resolver) ───────────────────
def _font(size: int) -> ImageFont.ImageFont:
    return get_bold(size)


# ── Suit drawing (vector — no glyph dependency) ─────────────────────────────
#
# Each suit is rasterised once as a high-resolution mask and downsampled with
# Lanczos, so the edges are properly anti-aliased instead of stair-stepping.
# The silhouettes come from parametric curves (not a few straight polygons),
# which keeps the lobes, tips and tapers smooth at every size.

_SUIT_SS     = 4                                    # supersampling factor
_SUIT_ASPECT = {"H": 0.88, "D": 0.76, "S": 0.88, "C": 0.88}  # width / height


def _sgn_pow(value: float, exponent: float) -> float:
    """Sign-preserving power — used for superellipse (diamond) outlines."""
    if value == 0:
        return 0.0
    return math.copysign(abs(value) ** exponent, value)


def _fit(points, width: float, height: float):
    """Scale a point cloud to exactly fill a width x height box."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    sx = width / (x1 - x0) if x1 > x0 else 1.0
    sy = height / (y1 - y0) if y1 > y0 else 1.0
    return [((x - x0) * sx, (y - y0) * sy) for x, y in points]


def _heart_outline(inverted: bool = False, steps: int = 180):
    """Classic heart curve; inverted turns the tip up for a spade body."""
    points = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        points.append((x, y if inverted else -y))
    return points


def _stem(d, cx: float, y_top: float, y_bottom: float,
          top_half: float, bottom_half: float, flare: float = 0.45, steps: int = 24):
    """Narrow shaft that curves out into a flared base (spade / club)."""
    left, right = [], []
    for i in range(steps + 1):
        t = i / steps
        y = y_top + (y_bottom - y_top) * t
        u = max(0.0, (t - flare) / (1.0 - flare))
        half = top_half + (bottom_half - top_half) * (u ** 1.6)
        left.append((cx - half, y))
        right.append((cx + half, y))
    d.polygon(left + right[::-1], fill=255)


def _shape_heart(d, w: float, h: float):
    d.polygon(_fit(_heart_outline(), w, h), fill=255)


def _shape_diamond(d, w: float, h: float):
    # Superellipse with the exponent just short of 2: straight sides, soft tips.
    a, b = w / 2, h / 2
    points = []
    steps = 200
    for i in range(steps):
        t = 2 * math.pi * i / steps
        points.append((
            a + a * _sgn_pow(math.cos(t), 1.95),
            b + b * _sgn_pow(math.sin(t), 1.95),
        ))
    d.polygon(points, fill=255)


def _shape_spade(d, w: float, h: float):
    # Inverted heart body with a short flared stem wedged between the lobes.
    body_h = h * 0.84
    d.polygon(_fit(_heart_outline(inverted=True), w, body_h), fill=255)
    _stem(d, w / 2, body_h * 0.50, h * 0.99, w * 0.045, w * 0.24, flare=0.55)


def _shape_club(d, w: float, h: float):
    # Three equal circles on an equilateral triangle (spacing 1.65r) plus a stem.
    r = h * 0.239
    spacing = 1.65 * r
    circum = spacing / math.sqrt(3)
    cy = circum + r          # centre of the triangle, so the top lobe starts at y=0
    for cx, top in (
        (w / 2, cy - circum),                    # top lobe
        (w / 2 - spacing / 2, cy + circum / 2),  # bottom-left lobe
        (w / 2 + spacing / 2, cy + circum / 2),  # bottom-right lobe
    ):
        d.ellipse([cx - r, top - r, cx + r, top + r], fill=255)
    _stem(d, w / 2, h * 0.50, h * 0.99, w * 0.06, w * 0.20, flare=0.45)


_SUIT_SHAPES = {
    "H": _shape_heart,
    "D": _shape_diamond,
    "S": _shape_spade,
    "C": _shape_club,
}


def _suit_color(suit: str):
    return SUIT_RED if suit in ("H", "D") else SUIT_BLK


@lru_cache(maxsize=128)
def _suit_sprite(suit: str, size: int, color: tuple) -> Image.Image:
    """Anti-aliased RGBA suit glyph, *size* pixels tall, cached per size/colour."""
    h = max(3, int(size))
    w = max(3, int(round(h * _SUIT_ASPECT[suit])))
    ss = _SUIT_SS
    mask = Image.new("L", (w * ss, h * ss), 0)
    _SUIT_SHAPES[suit](ImageDraw.Draw(mask), w * ss, h * ss)
    mask = mask.resize((w, h), Image.LANCZOS)
    sprite = Image.new("RGBA", (w, h), color + (255,))
    sprite.putalpha(mask)
    return sprite


def _draw_suit(img: Image.Image, suit: str, cx: float, cy: float, size: float, color):
    sprite = _suit_sprite(suit, int(round(size)), tuple(color))
    img.alpha_composite(
        sprite,
        (int(round(cx - sprite.width / 2)), int(round(cy - sprite.height / 2))),
    )


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

    rank_font = _font(26 if rank == "10" else 30)
    corner_cx = 22

    def draw_corner(target: Image.Image):
        cd = ImageDraw.Draw(target)
        # Centre the rank ink on the same axis as the suit below it.
        box = cd.textbbox((0, 0), rank, font=rank_font)
        cd.text(
            (corner_cx - (box[0] + box[2]) / 2, 4 - box[1]),
            rank, fill=color, font=rank_font,
        )
        _draw_suit(target, suit, corner_cx, 44, 18, color)

    # Top-left rank + small suit
    draw_corner(img)

    # Center large suit
    _draw_suit(img, suit, CARD_W // 2, CARD_H // 2 + 4, 46, color)

    # Bottom-right (rotated copy of top-left)
    bot = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    draw_corner(bot)
    img = Image.alpha_composite(img, bot.rotate(180))

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
        outline=ACTIVE_HALO,
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
