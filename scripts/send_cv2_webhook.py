import io
import json
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sys
import math
import random

# -----------------------------------
# Utility: Create a nebula-style background
# -----------------------------------
def generate_nebula(width=1200, height=450):
    img = Image.new("RGB", (width, height), (10, 10, 20))
    draw = ImageDraw.Draw(img)

    # Random nebula clouds
    for _ in range(6):
        # Random cloud center
        cx = random.randint(0, width)
        cy = random.randint(0, height)

        # Random cloud size
        radius = random.randint(200, 500)

        # Nebula colors (purples, blues, magentas)
        color = random.choice([
            (120, 60, 200),
            (80, 40, 160),
            (50, 80, 200),
            (150, 70, 220),
            (100, 30, 140)
        ])

        # Draw soft cloud
        cloud = Image.new("RGBA", (width, height))
        cloud_draw = ImageDraw.Draw(cloud)
        cloud_draw.ellipse(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            fill=color + (90,)
        )
        cloud = cloud.filter(ImageFilter.GaussianBlur(radius / 2))
        img = Image.alpha_composite(img.convert("RGBA"), cloud)

    # Add stars
    star_draw = ImageDraw.Draw(img)
    for _ in range(250):
        x = random.randint(0, width)
        y = random.randint(0, height)
        brightness = random.randint(150, 255)
        star_draw.point((x, y), fill=(brightness, brightness, brightness))

    return img.convert("RGB")


# -----------------------------------
# Utility: Draw text with shadow
# -----------------------------------
def draw_text(draw, position, text, font, fill, shadow=True):
    x, y = position
    if shadow:
        draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 180))
    draw.text((x, y), text, font=font, fill=fill)


# -----------------------------------
# Utility: Measure text width
# -----------------------------------
def measure_text(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height


# -----------------------------------
# Main generator
# -----------------------------------
def create_commit_card(author, message, sha):
    width, height = 1200, 450
    img = generate_nebula(width, height)
    draw = ImageDraw.Draw(img)

    # Load fonts (you can replace with your own TTFs)
    try:
        font_title = ImageFont.truetype("fonts/Inter-Bold.ttf", 52)
        font_body = ImageFont.truetype("fonts/Inter-Regular.ttf", 32)
        font_watermark = ImageFont.truetype("fonts/Inter-Regular.ttf", 24)
    except Exception:
        # use a guaranteed font if custom fonts fail
        font_title = ImageFont.load_default(52)
        font_body = ImageFont.load_default(32)
        font_watermark = ImageFont.load_default(24)

    # Title
    draw_text(draw, (50, 40), "New Commit", font_title, fill=(255, 255, 255))

    # Commit details
    y = 140
    draw_text(draw, (50, y), f"Author: {author}", font_body, fill=(230, 230, 230))
    y += 50
    draw_text(draw, (50, y), f"Message: {message}", font_body, fill=(230, 230, 230))
    y += 50
    draw_text(draw, (50, y), f"Commit: {sha[:10]}...", font_body, fill=(230, 230, 230))

    # Watermark (subtle + glowing)
    watermark = "Astral Haven Development"
    wm_w, wm_h = measure_text(draw, watermark, font_watermark)

    # Glow layer
    glow = Image.new("RGBA", img.size)
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.text(
        (width - wm_w - 40, height - wm_h - 30),
        watermark,
        font=font_watermark,
        fill=(120, 160, 255, 120)
    )
    glow = glow.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img.convert("RGBA"), glow)

    # Actual watermark text
    draw = ImageDraw.Draw(img)
    draw.text(
        (width - wm_w - 40, height - wm_h - 30),
        watermark,
        font=font_watermark,
        fill=(255, 255, 255, 180)
    )

    return img.convert("RGB")


# -----------------------------------
# Webhook sender
# -----------------------------------
def send_to_webhook(webhook, author, message, sha, repo_url, commit_url):
    img = create_commit_card(author, message, sha)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    payload = {
        "content": f"New commit by **{author}**",
        "embeds": [
            {
                "image": {"url": "attachment://commit.png"},
                "color": 1146986
            }
        ]
    }

    files = {"file": ("commit.png", buffer, "image/png")}
    requests.post(webhook, data={"payload_json": json.dumps(payload)}, files=files)


# -----------------------------------
# CLI entry
# -----------------------------------
if __name__ == "__main__":
    webhook = sys.argv[1]
    author = sys.argv[2]
    message = sys.argv[3]
    sha = sys.argv[4]
    repo_url = sys.argv[5]
    commit_url = sys.argv[6]

    send_to_webhook(webhook, author, message, sha, repo_url, commit_url)
