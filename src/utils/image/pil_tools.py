from io import BytesIO
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw, ImageFont
import random
import textwrap
import re
import requests
from utils import logging
from utils.image._font_resolver import get_bold, draw_textlength


# Unicode emoji detection
EMOJI_RE = re.compile(
    "[\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F900-\U0001F9FF"
    "\U0001F1E6-\U0001F1FF"
    "]+"
)

DISCORD_EMOJI_RE = re.compile(r"<a?:[A-Za-z0-9_~\-]+:(\d+)>")

def get_emoji_url(emoji_id: str) -> str:
    return f"https://cdn.discordapp.com/emojis/{emoji_id}.png"

# Cache to avoid re-downloading
_EMOJI_CACHE = {}

def _load_image_from_url(url: str) -> Image.Image:
    if url in _EMOJI_CACHE:
        return _EMOJI_CACHE[url].copy()

    r = requests.get(url, timeout=5)
    img = Image.open(BytesIO(r.content)).convert("RGBA")
    _EMOJI_CACHE[url] = img
    return img.copy()

def _render_twemoji(char: str, size: int) -> Image.Image:
    codepoints = "-".join(f"{ord(c):x}" for c in char)
    url = f"https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/{codepoints}.png"
    img = _load_image_from_url(url)
    return img.resize((size, size), Image.LANCZOS)

def _render_custom_emoji(emoji_id: str, size: int) -> Image.Image:
    url = get_emoji_url(emoji_id)
    img = _load_image_from_url(url)
    return img.resize((size, size), Image.LANCZOS)

# ---------------------------------------------------------
# UNIVERSAL INLINE TEXT + EMOJI RENDERER
# ---------------------------------------------------------

def draw_text_with_emojis(
    canvas: Image.Image,
    x: int,
    y: int,
    text: str,
    font,
    fill="black",
    stroke_width=0,
    stroke_fill="white",
    emoji_size=32,
):
    """
    Render a SINGLE line of text with inline Unicode + Discord custom emojis.
    Line wrapping must be handled by the caller.
    """
    draw = ImageDraw.Draw(canvas)
    cursor_x = x
    i = 0

    while i < len(text):

        # Discord custom emoji: <:name:id> or <a:name:id>
        m = DISCORD_EMOJI_RE.search(text, i)
        if m and m.start() == i:
            emoji_id = m.group(1)
            emoji_img = _render_custom_emoji(emoji_id, emoji_size)
            canvas.alpha_composite(emoji_img, (int(cursor_x), int(y - emoji_size // 2)))
            cursor_x += emoji_size + 2
            i = m.end()
            continue

        # Unicode emoji
        m = EMOJI_RE.search(text, i)
        if m and m.start() == i:
            emoji_char = m.group(0)
            emoji_img = _render_twemoji(emoji_char, emoji_size)
            canvas.alpha_composite(emoji_img, (int(cursor_x), int(y - emoji_size // 2)))
            cursor_x += emoji_size + 2
            i = m.end()
            continue

        # Normal text
        char = text[i]
        draw.text(
            (cursor_x, y),
            char,
            font=font,
            fill=fill,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
            anchor="lm",
        )
        cursor_x += draw_textlength(draw, char, font=font)
        i += 1


def process_image_animated(raw: BytesIO, effect_fn):
    img = Image.open(raw)

    if not getattr(img, "is_animated", False):
        return effect_fn(raw)

    frames = []
    durations = []

    for frame_index in range(img.n_frames):
        img.seek(frame_index)
        frame = img.convert("RGBA")

        buf = BytesIO()
        frame.save(buf, format="PNG")
        buf.seek(0)

        processed = Image.open(effect_fn(buf)).convert("RGBA")
        frames.append(processed)
        durations.append(img.info.get("duration", 50))

    out = BytesIO()
    frames[0].save(
        out,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=durations,
        disposal=2,
        transparency=0,
    )
    out.seek(0)
    return out


def _open_rgba(raw: BytesIO) -> Image.Image:
    raw.seek(0)
    return Image.open(raw).convert("RGBA")


# ───────────────────── existing effects ────────────

def grayscale(raw: BytesIO) -> BytesIO:
    img = _open_rgba(raw)
    gray = ImageOps.grayscale(img).convert("RGBA")
    buf = BytesIO()
    gray.save(buf, format="PNG")
    buf.seek(0)
    return buf


def invert_colors(raw: BytesIO) -> BytesIO:
    img = _open_rgba(raw)
    rgb = img.convert("RGB")
    inv = ImageOps.invert(rgb).convert("RGBA")
    buf = BytesIO()
    inv.save(buf, format="PNG")
    buf.seek(0)
    return buf


def blur_image(raw: BytesIO, radius: float = 4.0) -> BytesIO:
    img = _open_rgba(raw)
    blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
    buf = BytesIO()
    blurred.save(buf, format="PNG")
    buf.seek(0)
    return buf


def pixelate_image(raw: BytesIO, factor: int = 12) -> BytesIO:
    img = _open_rgba(raw)
    w, h = img.size
    small = img.resize(
        (max(1, w // factor), max(1, h // factor)),
        resample=Image.NEAREST
    )
    pixelated = small.resize((w, h), resample=Image.NEAREST)
    buf = BytesIO()
    pixelated.save(buf, format="PNG")
    buf.seek(0)
    return buf


def deepfry_image(raw: BytesIO) -> BytesIO:
    img = _open_rgba(raw).convert("RGB")
    w, h = img.size

    img = ImageEnhance.Color(img).enhance(5.0)
    img = ImageEnhance.Contrast(img).enhance(4.0)
    img = ImageEnhance.Sharpness(img).enhance(10.0)

    r, g, b = img.split()
    r = r.point(lambda i: min(255, i + 40))
    g = g.point(lambda i: min(255, i + 10))
    img = Image.merge("RGB", (r, g, b))

    pixels = img.load()

    burnout_count = int(w * h * 0.08)
    for _ in range(burnout_count):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        pixels[x, y] = (
            random.randint(200, 255),
            random.randint(180, 255),
            random.randint(0, 80),
        )

    noise_count = int(w * h * 0.15)
    for _ in range(noise_count):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        rv, gv, bv = pixels[x, y]
        n = random.randint(-50, 50)
        pixels[x, y] = (
            max(0, min(255, rv + n)),
            max(0, min(255, gv + n)),
            max(0, min(255, bv + n)),
        )

    r, g, b = img.split()

    def shift_channel(channel: Image.Image, dx: int, dy: int) -> Image.Image:
        return channel.transform(
            (w, h),
            Image.AFFINE,
            (1, 0, dx, 0, 1, dy),
            resample=Image.BICUBIC,
        )

    r_shift = shift_channel(r, random.randint(-4, 4), random.randint(-2, 2))
    g_shift = shift_channel(g, random.randint(-3, 3), random.randint(-2, 2))
    b_shift = shift_channel(b, random.randint(-5, 5), random.randint(-3, 3))

    img = Image.merge("RGB", (r_shift, g_shift, b_shift))

    draw = ImageDraw.Draw(img)
    for y in range(0, h, 3):
        draw.line([(0, y), (w, y)], fill=(0, 0, 0, 40), width=1)

    halo = img.filter(ImageFilter.GaussianBlur(radius=3))
    img = Image.blend(img, halo, alpha=0.25)

    buf = BytesIO()
    img.convert("RGBA").save(buf, format="PNG")
    buf.seek(0)
    return buf


# ── Font helpers (delegate to shared resolver with Termux/Android support) ──
def _caption_font(size: int) -> ImageFont.ImageFont:
    """Return a bold font at *size*. Termux-safe via _font_resolver."""
    return get_bold(size)


def _get_font(width: int, scale: float = 0.07) -> ImageFont.ImageFont:
    return get_bold(max(12, int(width * scale)))


def _wrap_to_pixel_width(
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    """Greedy word-wrap by measured pixel width, with hard breaks for long words."""
    measure = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        current = ""
        for word in words:
            # Hard-break tokens that exceed the line width by themselves.
            if draw_textlength(measure, word, font=font) > max_width and word:
                if current:
                    lines.append(current)
                    current = ""
                buf = ""
                for ch in word:
                    trial = buf + ch
                    if draw_textlength(measure, trial, font=font) > max_width and buf:
                        lines.append(buf)
                        buf = ch
                    else:
                        buf = trial
                current = buf
                continue

            trial = word if not current else (current + " " + word)
            if draw_textlength(measure, trial, font=font) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        elif not words:
            lines.append("")
    return lines or [""]


def _draw_caption_block(img: Image.Image, text: str, position: str = "top") -> Image.Image:
    width, height = img.size

    # Font sized relative to the image, but with sensible bounds so very
    # small or very large pictures still produce a legible caption.
    font_size = max(20, min(72, int(width * 0.075)))
    font = _caption_font(font_size)

    # Side padding for the text. Caption width is image width minus 2× padding.
    side_padding = max(16, int(width * 0.04))
    text_max_width = max(1, width - side_padding * 2)

    # Pixel-accurate wrapping
    lines = _wrap_to_pixel_width(text, font, text_max_width)

    # Use real font metrics for line spacing (consistent across line counts).
    try:
        ascent, descent = font.getmetrics()
        line_height = ascent + descent
    except Exception:
        bbox_one = ImageDraw.Draw(img).textbbox((0, 0), "Ay", font=font)
        line_height = bbox_one[3] - bbox_one[1]

    line_spacing = int(line_height * 0.18)
    text_block_h = line_height * len(lines) + line_spacing * max(0, len(lines) - 1)

    pad_y = max(12, int(font_size * 0.45))
    block_height = text_block_h + pad_y * 2

    new_height = height + block_height
    canvas = Image.new("RGBA", (width, new_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(canvas)

    if position == "top":
        draw.rectangle([0, 0, width, block_height], fill="white")
        block_top = 0
        paste_y = block_height
    else:
        canvas.paste(img, (0, 0))
        draw.rectangle([0, height, width, height + block_height], fill="white")
        block_top = height
        paste_y = 0

    measure = ImageDraw.Draw(canvas)
    text_top = block_top + pad_y
    for i, line in enumerate(lines):
        line_w = draw_textlength(measure, line, font=font)
        x = int((width - line_w) // 2)
        # draw_text_with_emojis uses anchor="lm" → y is the line's vertical centre
        baseline_y = text_top + i * (line_height + line_spacing) + line_height // 2
        draw_text_with_emojis(
            canvas,
            x,
            baseline_y,
            line,
            font=font,
            fill="black",
            stroke_width=0,
            stroke_fill="white",
            emoji_size=int(font_size * 1.1),
        )

    if position == "top":
        canvas.paste(img, (0, paste_y))

    return canvas


def caption_top(raw: BytesIO, text: str) -> BytesIO:
    img = _open_rgba(raw)
    out = _draw_caption_block(img, text, position="top")
    buf = BytesIO()
    out.save(buf, format="PNG")
    buf.seek(0)
    return buf


def caption_bottom(raw: BytesIO, text: str) -> BytesIO:
    img = _open_rgba(raw)
    out = _draw_caption_block(img, text, position="bottom")
    buf = BytesIO()
    out.save(buf, format="PNG")
    buf.seek(0)
    return buf


def meme_top_bottom(raw: BytesIO, top: str, bottom: str) -> BytesIO:
    img = _open_rgba(raw)
    width, height = img.size
    font = _get_font(width, scale=0.08)
    draw = ImageDraw.Draw(img)

    def draw_centered(text: str, y: int):
        wrapped = textwrap.fill(text, width=20)
        draw.multiline_text(
            (width // 2, y),
            wrapped,
            font=font,
            fill="white",
            anchor="ma",
            align="center",
            stroke_width=3,
            stroke_fill="black",
        )

    if top:
        draw_centered(top, 20)
    if bottom:
        draw_centered(bottom, height - 40)

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


# ───────────────────── new effects ─────────────────

def sepia(raw: BytesIO) -> BytesIO:
    """Classic warm brown sepia tone."""
    img = _open_rgba(raw).convert("L").convert("RGB")
    r, g, b = img.split()
    r = r.point(lambda i: min(255, int(i * 1.08)))
    g = g.point(lambda i: min(255, int(i * 0.85)))
    b = b.point(lambda i: min(255, int(i * 0.65)))
    out = Image.merge("RGB", (r, g, b))
    buf = BytesIO()
    out.convert("RGBA").save(buf, format="PNG")
    buf.seek(0)
    return buf


def vaporwave(raw: BytesIO) -> BytesIO:
    """Retrowave pink/purple palette with scanlines."""
    img = _open_rgba(raw).convert("RGB")
    w, h = img.size

    r, g, b = img.split()
    r = r.point(lambda i: min(255, int(i * 1.1 + 40)))
    g = g.point(lambda i: min(255, int(i * 0.6)))
    b = b.point(lambda i: min(255, int(i * 1.4 + 50)))
    img = Image.merge("RGB", (r, g, b))

    # Horizontal scanlines
    draw = ImageDraw.Draw(img)
    for y in range(0, h, 4):
        draw.line([(0, y), (w, y)], fill=(20, 0, 40), width=1)

    # Dreamy soft blur
    img = img.filter(ImageFilter.GaussianBlur(radius=0.7))

    buf = BytesIO()
    img.convert("RGBA").save(buf, format="PNG")
    buf.seek(0)
    return buf


def glitch_effect(raw: BytesIO) -> BytesIO:
    """RGB channel shift + horizontal slice corruption + noise blocks."""
    img = _open_rgba(raw)
    w, h = img.size

    # 1. RGB channel offset
    r, g, b, a = img.split()
    shift_x = random.randint(6, 20)
    r = r.transform((w, h), Image.AFFINE, (1, 0, shift_x, 0, 1, 0), resample=Image.NEAREST)
    b = b.transform((w, h), Image.AFFINE, (1, 0, -shift_x, 0, 1, 0), resample=Image.NEAREST)
    result = Image.merge("RGBA", (r, g, b, a))

    # 2. Horizontal slice shifts (no pixel loops — use paste)
    for _ in range(random.randint(6, 14)):
        y0 = random.randint(0, max(1, h - 12))
        sh = random.randint(2, 10)
        dx = random.randint(-40, 40)
        y1 = min(y0 + sh, h)
        strip = result.crop((0, y0, w, y1))
        result.paste(strip, (dx, y0))

    # 3. Random color noise bars
    draw = ImageDraw.Draw(result)
    for _ in range(random.randint(4, 10)):
        x1 = random.randint(0, max(1, w - 20))
        y1 = random.randint(0, max(1, h - 4))
        x2 = min(x1 + random.randint(30, 120), w)
        y2 = min(y1 + random.randint(1, 3), h)
        draw.rectangle(
            [x1, y1, x2, y2],
            fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 210)
        )

    buf = BytesIO()
    result.save(buf, format="PNG")
    buf.seek(0)
    return buf


def edge_detect(raw: BytesIO) -> BytesIO:
    """Highlight edges in the image."""
    img = _open_rgba(raw).convert("RGB")
    edges = img.filter(ImageFilter.FIND_EDGES)
    buf = BytesIO()
    edges.convert("RGBA").save(buf, format="PNG")
    buf.seek(0)
    return buf


def emboss(raw: BytesIO) -> BytesIO:
    """3D emboss / raised-relief effect."""
    img = _open_rgba(raw).convert("RGB")
    embossed = img.filter(ImageFilter.EMBOSS)
    # Boost contrast so the emboss pops
    embossed = ImageEnhance.Contrast(embossed).enhance(2.5)
    buf = BytesIO()
    embossed.convert("RGBA").save(buf, format="PNG")
    buf.seek(0)
    return buf


def rotate_image(raw: BytesIO, angle: float = 90.0) -> BytesIO:
    """Rotate the image clockwise by the given angle."""
    img = _open_rgba(raw)
    rotated = img.rotate(-angle, expand=True, resample=Image.BICUBIC)
    buf = BytesIO()
    rotated.save(buf, format="PNG")
    buf.seek(0)
    return buf


def mirror_image(raw: BytesIO) -> BytesIO:
    """Flip the image horizontally (left ↔ right)."""
    img = _open_rgba(raw)
    mirrored = ImageOps.mirror(img)
    buf = BytesIO()
    mirrored.save(buf, format="PNG")
    buf.seek(0)
    return buf


def flip_image(raw: BytesIO) -> BytesIO:
    """Flip the image vertically (top ↔ bottom)."""
    img = _open_rgba(raw)
    flipped = ImageOps.flip(img)
    buf = BytesIO()
    flipped.save(buf, format="PNG")
    buf.seek(0)
    return buf


def sharpen_image(raw: BytesIO) -> BytesIO:
    """Aggressive unsharp-mask sharpening."""
    img = _open_rgba(raw)
    sharpened = img.filter(ImageFilter.UnsharpMask(radius=2, percent=250, threshold=3))
    sharpened = ImageEnhance.Sharpness(sharpened).enhance(2.0)
    buf = BytesIO()
    sharpened.save(buf, format="PNG")
    buf.seek(0)
    return buf


def posterize_image(raw: BytesIO, bits: int = 3) -> BytesIO:
    """Reduce color depth for a flat, poster-art look."""
    img = _open_rgba(raw).convert("RGB")
    posterized = ImageOps.posterize(img, bits)
    buf = BytesIO()
    posterized.convert("RGBA").save(buf, format="PNG")
    buf.seek(0)
    return buf


def vignette(raw: BytesIO, strength: float = 0.75) -> BytesIO:
    """Dark feathered vignette around the edges."""
    img = _open_rgba(raw)
    w, h = img.size

    # Build a white-centre → black-edge radial mask
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    steps = 120
    for i in range(steps, 0, -1):
        ratio = i / steps
        rw = int(w * ratio)
        rh = int(h * ratio)
        x0 = (w - rw) // 2
        y0 = (h - rh) // 2
        brightness = int(255 * (1 - (1 - ratio) * strength * 2.2))
        brightness = max(0, min(255, brightness))
        draw.ellipse([x0, y0, x0 + rw, y0 + rh], fill=brightness)

    # Black overlay dimmed by inverse of mask
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    overlay.putalpha(ImageOps.invert(mask))
    result = Image.alpha_composite(img, overlay)

    buf = BytesIO()
    result.save(buf, format="PNG")
    buf.seek(0)
    return buf


def oil_paint(raw: BytesIO) -> BytesIO:
    """Simulate an oil painting with multiple median-filter passes + colour boost."""
    img = _open_rgba(raw).convert("RGB")
    for _ in range(5):
        img = img.filter(ImageFilter.MedianFilter(size=5))
    img = ImageEnhance.Color(img).enhance(2.2)
    img = ImageEnhance.Contrast(img).enhance(1.3)
    img = ImageEnhance.Sharpness(img).enhance(0.3)
    buf = BytesIO()
    img.convert("RGBA").save(buf, format="PNG")
    buf.seek(0)
    return buf
