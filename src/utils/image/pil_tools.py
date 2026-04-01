from io import BytesIO
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw, ImageFont
import random
import textwrap


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

    # Over-saturate, over-contrast, oversharpen
    img = ImageEnhance.Color(img).enhance(3.0)
    img = ImageEnhance.Contrast(img).enhance(2.5)
    img = ImageEnhance.Sharpness(img).enhance(3.0)

    # Add noise
    pixels = img.load()
    w, h = img.size
    noise_pixels = int(w * h * 0.05)
    for _ in range(noise_pixels):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        r, g, b = pixels[x, y]
        n = random.randint(-80, 80)
        pixels[x, y] = (
            max(0, min(255, r + n)),
            max(0, min(255, g + n)),
            max(0, min(255, b + n)),
        )

    buf = BytesIO()
    img.convert("RGBA").save(buf, format="PNG")
    buf.seek(0)
    return buf


def _get_font(width: int, scale: float = 0.07) -> ImageFont.FreeTypeFont:
    size = max(12, int(width * scale))
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


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

    # padding for the caption bar
    padding_y = int(text_h * 0.18)
    block_height = text_h + padding_y * 2

    # New canvas with extra space
    new_height = height + block_height
    canvas = Image.new("RGBA", (width, new_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(canvas)

    if position == "top":
        # White bar
        draw.rectangle([0, 0, width, block_height], fill="white")

        # Centered text
        draw.multiline_text(
            (width // 2, block_height // 2),
            wrapped,
            font=font,
            fill="black",
            anchor="mm",
            align="center",
            stroke_width=6,
            stroke_fill="white",
        )

        # Paste original image below
        canvas.paste(img, (0, block_height))

    else:  # bottom caption
        canvas.paste(img, (0, 0))

        draw.rectangle([0, height, width, height + block_height], fill="white")

        draw.multiline_text(
            (width // 2, height + block_height // 2),
            wrapped,
            font=font,
            fill="black",
            anchor="mm",
            align="center",
            stroke_width=6,
            stroke_fill="white",
        )

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