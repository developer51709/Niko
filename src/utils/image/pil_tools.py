from io import BytesIO
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw, ImageFont
import random
import textwrap
import re
import requests


# Regex to detect emoji codepoints
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002700-\U000027BF\U0001F300-\U0001F5FF]+"
)

def _draw_twemoji_text(canvas: Image.Image, draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font, fill, stroke_width, stroke_fill):
    cursor_x = x
    cursor_y = y
    font_size = font.size

    tokens = EMOJI_RE.split(text)
    emojis = EMOJI_RE.findall(text)

    for i, token in enumerate(tokens):
        # Draw normal text
        if token:
            draw.text(
                (cursor_x, cursor_y),
                token,
                font=font,
                fill=fill,
                stroke_width=stroke_width,
                stroke_fill=stroke_fill,
                anchor="lm",
            )
            cursor_x += draw.textlength(token, font=font)

        # Draw emoji
        if i < len(emojis):
            emoji = emojis[i]

            # Convert emoji → Twemoji filename
            codepoints = "-".join(f"{ord(c):x}" for c in emoji)
            url = f"https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/{codepoints}.png"

            try:
                r = requests.get(url, timeout=5)
                tw = Image.open(BytesIO(r.content)).convert("RGBA")
                tw = tw.resize((font_size, font_size), Image.LANCZOS)

                # PASTE ONTO CANVAS, NOT draw.im
                canvas.paste(tw, (int(cursor_x), int(cursor_y - font_size * 0.8)), tw)

                cursor_x += font_size

            except:
                # fallback: draw emoji as text
                draw.text(
                    (cursor_x, cursor_y),
                    emoji,
                    font=font,
                    fill=fill,
                    stroke_width=stroke_width,
                    stroke_fill=stroke_fill,
                    anchor="lm",
                )
                cursor_x += draw.textlength(emoji, font=font)


def process_image_animated(raw: BytesIO, effect_fn):
    img = Image.open(raw)

    # Not animated → just process normally
    if not getattr(img, "is_animated", False):
        return effect_fn(raw)

    frames = []
    durations = []

    for frame_index in range(img.n_frames):
        img.seek(frame_index)
        frame = img.convert("RGBA")

        # Convert frame to BytesIO for your existing effect functions
        buf = BytesIO()
        frame.save(buf, format="PNG")
        buf.seek(0)

        # Apply the effect to this frame
        processed = Image.open(effect_fn(buf)).convert("RGBA")

        frames.append(processed)
        durations.append(img.info.get("duration", 50))

    # Reassemble GIF
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

    # 1. MASSIVE saturation, contrast, sharpness
    img = ImageEnhance.Color(img).enhance(5.0)
    img = ImageEnhance.Contrast(img).enhance(4.0)
    img = ImageEnhance.Sharpness(img).enhance(10.0)

    # 2. Warm/orange tint
    r, g, b = img.split()
    r = r.point(lambda i: min(255, i + 40))
    g = g.point(lambda i: min(255, i + 10))
    img = Image.merge("RGB", (r, g, b))

    pixels = img.load()

    # 3. Pixel burnouts
    burnout_count = int(w * h * 0.08)
    for _ in range(burnout_count):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        pixels[x, y] = (
            random.randint(200, 255),
            random.randint(180, 255),
            random.randint(0, 80),
        )

    # 4. Noise
    noise_count = int(w * h * 0.15)
    for _ in range(noise_count):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        r, g, b = pixels[x, y]
        n = random.randint(-50, 50)
        pixels[x, y] = (
            max(0, min(255, r + n)),
            max(0, min(255, g + n)),
            max(0, min(255, b + n)),
        )

    # 5. RGB glitch (channel shifts)
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

    # 6. Scanlines
    draw = ImageDraw.Draw(img)
    line_color = (0, 0, 0, 40)
    spacing = 3  # distance between lines

    for y in range(0, h, spacing):
        draw.line([(0, y), (w, y)], fill=line_color, width=1)

    # 7. Halo/glow
    halo = img.filter(ImageFilter.GaussianBlur(radius=3))
    img = Image.blend(img, halo, alpha=0.25)

    buf = BytesIO()
    img.convert("RGBA").save(buf, format="PNG")
    buf.seek(0)
    return buf


def _get_font(width: int, scale: float = 0.07) -> ImageFont.FreeTypeFont:
    size = max(12, int(width * scale))
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default(size)


def _draw_caption_block(img: Image.Image, text: str, position: str = "top") -> Image.Image:
    width, height = img.size
    font_size = max(45, int(width * 0.09))
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default(font_size)

    wrapped = textwrap.fill(text, width=int(width / (font_size * 0.6)))

    dummy = ImageDraw.Draw(img)
    bbox = dummy.multiline_textbbox((0, 0), wrapped, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    padding_y = int(text_h * 0.18)
    block_height = text_h + padding_y * 2

    new_height = height + block_height
    canvas = Image.new("RGBA", (width, int(new_height)), (255, 255, 255, 0))
    draw = ImageDraw.Draw(canvas)

    if position == "top":
        draw.rectangle([0, 0, width, block_height], fill="white")
        text_y = block_height // 2
        paste_y = block_height
    else:
        canvas.paste(img, (0, 0))
        draw.rectangle([0, height, width, height + block_height], fill="white")
        text_y = height + block_height // 2
        paste_y = 0

    _draw_twemoji_text(
        canvas,
        draw,
        width // 2 - text_w // 2,
        text_y,
        wrapped,
        font,
        fill="black",
        stroke_width=6,
        stroke_fill="white",
    )

    # Paste original image
    if position == "top":
        canvas.paste(img, (0, int(paste_y)))
    else:
        pass

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