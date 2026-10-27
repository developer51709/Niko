import random
import secrets
import string
import io
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# No vowels and no characters that read the same at a glance: a member reads this
# once, off a deliberately noisy image, and has three attempts to get it right.
CAPTCHA_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def new_captcha_code(length: int = 6) -> str:
    """A fresh captcha code, drawn from the system's secure random source."""
    return "".join(secrets.choice(CAPTCHA_ALPHABET) for _ in range(max(1, length)))


def generate_captcha(length: int = 6) -> tuple[str, io.BytesIO]:
    """Generate a captcha image and return (code, image_bytes)."""
    code = new_captcha_code(length)
    return code, render_captcha(code)


# Two palettes, one renderer. Dark glyphs on paper read best in a Discord DM,
# and light glyphs on the site's own surface read best on the dark verification
# page — the contrast is what matters, so the same code is legible either way.
_PALETTES = {
    False: {
        "background": (245, 245, 250),
        "noise": (160, 230),
        "rule": (120, 200),
        "glyph": ((15, 80), (15, 80), (60, 140)),
    },
    True: {
        # #171a1f, the page's inset surface.
        "background": (23, 26, 31),
        "noise": (28, 52),
        "rule": (58, 92),
        "glyph": ((196, 255), (206, 255), (216, 255)),
    },
}


def render_captcha(code: str, *, dark: bool = False) -> io.BytesIO:
    """Render the image for an existing code.

    Kept separate from code generation because the web verification page stores
    only the code: the image is drawn again, per request, from that stored value.
    ``dark`` draws it for the website's dark theme.
    """
    length = max(1, len(code or ""))
    palette = _PALETTES[bool(dark)]

    width, height = 300, 100

    img = Image.new("RGB", (width, height), color=palette["background"])
    draw = ImageDraw.Draw(img)

    for _ in range(1200):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        shade = random.randint(*palette["noise"])
        draw.point((x, y), fill=(shade, shade, shade + random.randint(0, 10)))

    for _ in range(8):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        shade = random.randint(*palette["rule"])
        color = (shade, shade, min(255, shade + random.randint(0, 14)))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=1)

    try:
        font = ImageFont.load_default(size=44)
    except TypeError:
        font = ImageFont.load_default()

    char_width = width // (length + 1)
    for i, char in enumerate(code):
        x = int(char_width * (i + 0.55) + random.randint(-6, 6))
        y = random.randint(8, 28)
        r = random.randint(*palette["glyph"][0])
        g = random.randint(*palette["glyph"][1])
        b = random.randint(*palette["glyph"][2])
        draw.text((x, y), char, fill=(r, g, b), font=font)

    img = img.filter(ImageFilter.GaussianBlur(radius=0.6))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
