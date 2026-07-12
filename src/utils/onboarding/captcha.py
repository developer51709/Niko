import random
import string
import io
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def generate_captcha(length: int = 6) -> tuple[str, io.BytesIO]:
    """Generate a captcha image and return (code, image_bytes)."""
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

    width, height = 300, 100

    img = Image.new("RGB", (width, height), color=(245, 245, 250))
    draw = ImageDraw.Draw(img)

    for _ in range(1200):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        shade = random.randint(160, 230)
        draw.point((x, y), fill=(shade, shade, shade + random.randint(0, 10)))

    for _ in range(8):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        color = (
            random.randint(120, 200),
            random.randint(120, 200),
            random.randint(120, 200),
        )
        draw.line([(x1, y1), (x2, y2)], fill=color, width=1)

    try:
        font = ImageFont.load_default(size=44)
    except TypeError:
        font = ImageFont.load_default()

    char_width = width // (length + 1)
    for i, char in enumerate(code):
        x = int(char_width * (i + 0.55) + random.randint(-6, 6))
        y = random.randint(8, 28)
        r = random.randint(15, 80)
        g = random.randint(15, 80)
        b = random.randint(60, 140)
        draw.text((x, y), char, fill=(r, g, b), font=font)

    img = img.filter(ImageFilter.GaussianBlur(radius=0.6))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return code, buf
