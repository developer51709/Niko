import io
import json
import sys
import random
import textwrap
import re
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# -----------------------------------
# Emoji detection regex
# -----------------------------------
EMOJI_REGEX = re.compile(
    "[\U0001F1E0-\U0001F1FF]"  # flags
    "|[\U0001F300-\U0001F5FF]"  # symbols & pictographs
    "|[\U0001F600-\U0001F64F]"  # emoticons
    "|[\U0001F680-\U0001F6FF]"  # transport & map
    "|[\U0001F700-\U0001F77F]"
    "|[\U0001F780-\U0001F7FF]"
    "|[\U0001F800-\U0001F8FF]"
    "|[\U0001F900-\U0001F9FF]"
    "|[\U0001FA00-\U0001FA6F]"
    "|[\U0001FA70-\U0001FAFF]"
    "|[\U00002600-\U000026FF]"  # misc symbols
    "|[\U00002700-\U000027BF]"  # dingbats
    , flags=re.UNICODE
)

# -----------------------------------
# Twemoji loader
# -----------------------------------
def emoji_to_twemoji(char):
    codepoints = "-".join(f"{ord(c):x}" for c in char)
    url = f"https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/{codepoints}.png"
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        return Image.open(io.BytesIO(r.content)).convert("RGBA")
    return None

# -----------------------------------
# Markdown sanitizer (keeps emojis)
# -----------------------------------
def sanitize_markdown(text):
    return re.sub(r"(\*\*|\*|__|~~|`)", "", text)

# -----------------------------------
# Nebula background generator
# -----------------------------------
def generate_nebula(width=1200, height=450):
    base = Image.new("RGBA", (width, height), (10, 10, 20, 255))

    for _ in range(6):
        cx = random.randint(0, width)
        cy = random.randint(0, height)
        radius = random.randint(200, 500)

        color = random.choice([
            (120, 60, 200, 90),
            (80, 40, 160, 90),
            (50, 80, 200, 90),
            (150, 70, 220, 90),
            (100, 30, 140, 90)
        ])

        cloud = Image.new("RGBA", (width, height))
        draw = ImageDraw.Draw(cloud)
        draw.ellipse(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            fill=color
        )
        cloud = cloud.filter(ImageFilter.GaussianBlur(radius / 2))
        base = Image.alpha_composite(base, cloud)

    # Stars
    draw = ImageDraw.Draw(base)
    for _ in range(250):
        x = random.randint(0, width)
        y = random.randint(0, height)
        brightness = random.randint(150, 255)
        draw.point((x, y), fill=(brightness, brightness, brightness, 255))

    return base.convert("RGB")

# -----------------------------------
# Draw text with shadow
# -----------------------------------
def draw_text(draw, position, text, font, fill):
    x, y = position
    draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 180))
    draw.text((x, y), text, font=font, fill=fill)

# -----------------------------------
# Twemoji-aware text renderer
# -----------------------------------
def draw_text_with_twemoji(base_img, x, y, text, font, fill):
    draw = ImageDraw.Draw(base_img)
    cursor_x = x
    cursor_y = y

    for char in text:
        # Emoji → Twemoji
        if EMOJI_REGEX.match(char):
            tw = emoji_to_twemoji(char)
            if tw:
                em_size = font.size + 6
                tw = tw.resize((em_size, em_size), Image.LANCZOS)
                base_img.paste(tw, (cursor_x, cursor_y - 4), tw)
                cursor_x += em_size + 2
                continue

        # Normal character
        w, h = draw.textbbox((0, 0), char, font=font)[2:]
        draw.text((cursor_x, cursor_y), char, font=font, fill=fill)
        cursor_x += w

    return cursor_y + font.size + 10

# -----------------------------------
# Main commit card generator
# -----------------------------------
def create_commit_card(author, message, sha):
    width, height = 1200, 600
    img = generate_nebula(width, height)
    draw = ImageDraw.Draw(img)

    # Load fonts
    try:
        font_title = ImageFont.truetype("fonts/Inter-Bold.ttf", 52)
        font_body = ImageFont.truetype("fonts/Inter-Regular.ttf", 32)
        font_watermark = ImageFont.truetype("fonts/Inter-Regular.ttf", 24)
    except:
        font_title = ImageFont.load_default(52)
        font_body = ImageFont.load_default(32)
        font_watermark = ImageFont.load_default(24)

    # Title
    draw_text(draw, (50, 40), "New Commit", font_title, (255, 255, 255))

    # Author
    y = 140
    draw_text(draw, (50, y), f"Author: {author}", font_body, (230, 230, 230))
    y += 50

    # Commit SHA
    draw_text(draw, (50, y), f"Commit: {sha[:10]}...", font_body, (230, 230, 230))
    y += 60

    # Message header
    draw_text(draw, (50, y), "Message:", font_body, (230, 230, 230))
    y += 40

    # Sanitize markdown
    safe_message = sanitize_markdown(message)

    # Preserve real newlines and wrap each line
    lines = safe_message.split("\n")

    for raw_line in lines:
        wrapped_lines = textwrap.wrap(raw_line, width=40) or [""]

        for line in wrapped_lines:
            y = draw_text_with_twemoji(img, 70, y, line, font_body, (230, 230, 230))

    # Watermark glow
    watermark = "Astral Haven Development"
    wm_w, wm_h = draw.textbbox((0, 0), watermark, font=font_watermark)[2:]

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

    # Watermark text
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
        ],
        "components": [
            {
                "type": 1,
                "components": [
                    {
                        "type": 2,
                        "style": 5,
                        "label": "Repository",
                        "url": repo_url
                    },
                    {
                        "type": 2,
                        "style": 5,
                        "label": "View Commit",
                        "url": commit_url
                    }
                ]
            }
        ]
    }

    files = {"file": ("commit.png", buffer, "image/png")}

    r = requests.post(
        webhook,
        data={"payload_json": json.dumps(payload)},
        files=files
    )

    if r.status_code >= 300:
        print("Webhook error:", r.status_code, r.text)

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

    # Turn literal "\n" into real newlines, without touching emojis
    message = message.replace("\\n", "\n")

    send_to_webhook(webhook, author, message, sha, repo_url, commit_url)
