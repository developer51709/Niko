import io
import os
import json
import sys
import base64
import random
import textwrap
import re
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# -----------------------------------
# Emoji detection regex
# -----------------------------------
EMOJI_REGEX = re.compile(
    "[\U0001F1E0-\U0001F1FF]"
    "|[\U0001F300-\U0001F5FF]"
    "|[\U0001F600-\U0001F64F]"
    "|[\U0001F680-\U0001F6FF]"
    "|[\U0001F700-\U0001F77F]"
    "|[\U0001F780-\U0001F7FF]"
    "|[\U0001F800-\U0001F8FF]"
    "|[\U0001F900-\U0001F9FF]"
    "|[\U0001FA00-\U0001FA6F]"
    "|[\U0001FA70-\U0001FAFF]"
    "|[\U00002600-\U000026FF]"
    "|[\U00002700-\U000027BF]",
    flags=re.UNICODE,
)


# -----------------------------------
# Twemoji loader
# -----------------------------------
def emoji_to_twemoji(char):
    codepoints = "-".join(f"{ord(c):x}" for c in char)
    url = f"https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/{codepoints}.png"
    r = requests.get(url, stream=True, timeout=5)
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
            (100, 30, 140, 90),
        ])
        cloud = Image.new("RGBA", (width, height))
        ImageDraw.Draw(cloud).ellipse(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            fill=color,
        )
        cloud = cloud.filter(ImageFilter.GaussianBlur(radius / 2))
        base = Image.alpha_composite(base, cloud)

    draw = ImageDraw.Draw(base)
    for _ in range(250):
        x = random.randint(0, width)
        y = random.randint(0, height)
        b = random.randint(150, 255)
        draw.point((x, y), fill=(b, b, b, 255))

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
    for char in text:
        if EMOJI_REGEX.match(char):
            tw = emoji_to_twemoji(char)
            if tw:
                em_size = font.size + 6
                tw = tw.resize((em_size, em_size), Image.LANCZOS)
                base_img.paste(tw, (cursor_x, y - 4), tw)
                cursor_x += em_size + 2
                continue
        w = draw.textbbox((0, 0), char, font=font)[2]
        draw.text((cursor_x, y), char, font=font, fill=fill)
        cursor_x += w
    return y + font.size + 10


# -----------------------------------
# Main commit card generator
# -----------------------------------
def create_commit_card(author, message, sha):
    width, height = 1200, 600
    img = generate_nebula(width, height)
    draw = ImageDraw.Draw(img)

    try:
        font_title     = ImageFont.truetype("fonts/Inter-Bold.ttf",    52)
        font_body      = ImageFont.truetype("fonts/Inter-Regular.ttf", 32)
        font_watermark = ImageFont.truetype("fonts/Inter-Regular.ttf", 24)
    except Exception:
        font_title     = ImageFont.load_default(52)
        font_body      = ImageFont.load_default(32)
        font_watermark = ImageFont.load_default(24)

    draw_text(draw, (50, 40), "New Commit", font_title, (255, 255, 255))

    y = 140
    draw_text(draw, (50, y), f"Author: {author}", font_body, (230, 230, 230))
    y += 50
    draw_text(draw, (50, y), f"Commit: {sha[:10]}...", font_body, (230, 230, 230))
    y += 60
    draw_text(draw, (50, y), "Message:", font_body, (230, 230, 230))
    y += 40

    safe_message = sanitize_markdown(message)
    for raw_line in safe_message.split("\n"):
        for line in textwrap.wrap(raw_line, width=40) or [""]:
            y = draw_text_with_twemoji(img, 70, y, line, font_body, (230, 230, 230))

    watermark = "developer51709/Niko | GitHub Notifications"
    wm_w, wm_h = draw.textbbox((0, 0), watermark, font=font_watermark)[2:]

    glow = Image.new("RGBA", img.size)
    ImageDraw.Draw(glow).text(
        (width - wm_w - 40, height - wm_h - 30),
        watermark, font=font_watermark, fill=(120, 160, 255, 120),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img.convert("RGBA"), glow)

    draw = ImageDraw.Draw(img)
    draw.text(
        (width - wm_w - 40, height - wm_h - 30),
        watermark, font=font_watermark, fill=(255, 255, 255, 180),
    )

    return img.convert("RGB")


# -----------------------------------
# Helpers
# -----------------------------------
def repo_name_from_url(url: str) -> str:
    m = re.search(r"github\.com/([^/]+/[^/?#]+)", url)
    return m.group(1) if m else url


def subject_line(message: str) -> str:
    line = next((l.strip() for l in message.splitlines() if l.strip()), message.strip())
    return line[:69] + "..." if len(line) > 72 else line


# -----------------------------------
# imgbb upload — returns a permanent public URL
# -----------------------------------
def upload_to_imgbb(buffer: io.BytesIO) -> str | None:
    api_key = os.environ.get("IMGBB_API_KEY", "")
    if not api_key:
        print("[imgbb] IMGBB_API_KEY is not set — cannot upload image")
        return None

    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    try:
        r = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": api_key, "image": b64},
            timeout=30,
        )
        if r.ok:
            return r.json()["data"]["display_url"]
        print(f"[imgbb] upload failed {r.status_code}: {r.text[:120]}")
    except Exception as e:
        print(f"[imgbb] upload error: {e}")
    return None


# -----------------------------------
# Send the CV2 container
# -----------------------------------
def send_cv2(webhook: str, author: str, message: str, sha: str,
             repo_url: str, commit_url: str, image_url: str) -> bool:
    """
    IS_COMPONENTS_V2 (flags: 1<<15) + ?with_components=true.

    ?with_components=true is required so Discord respects the components
    field on a non-application-owned (type-1 incoming) webhook.

    IS_COMPONENTS_V2 means the message body may ONLY contain components —
    no content, no embeds, no files.  The image is served via the Discord
    CDN URL obtained in the park step.
    """
    repo      = repo_name_from_url(repo_url)
    short_sha = sha[:10]
    subject   = subject_line(message)

    payload = {
        "flags": 1 << 15,
        "components": [
            {
                "type": 17,              # Container
                "accent_color": 0x2d7d46,
                "components": [
                    {
                        "type": 10,      # TextDisplay
                        "content": (
                            f"## ☁️ {subject}\n"
                            f"-# [`{short_sha}`]({commit_url}) · {repo} · pushed by **{author}**"
                        ),
                    },
                    {
                        "type": 14,      # Separator
                        "divider": True,
                        "spacing": 1,
                    },
                    {
                        "type": 12,      # MediaGallery
                        "items": [
                            {
                                "media": {"url": image_url},
                                "description": f"Commit card for {short_sha}",
                            }
                        ],
                    },
                    {
                        "type": 14,      # Separator (spacing, no line)
                        "divider": False,
                        "spacing": 1,
                    },
                    {
                        "type": 1,       # ActionRow
                        "components": [
                            {
                                "type": 2, "style": 5,
                                "label": "View Repository",
                                "url": repo_url,
                            },
                            {
                                "type": 2, "style": 5,
                                "label": "View Commit",
                                "url": commit_url,
                            },
                        ],
                    },
                ],
            }
        ],
    }

    r = requests.post(
        f"{webhook}?wait=true&with_components=true",
        json=payload,
        timeout=15,
    )

    if r.status_code in (200, 204):
        print(f"[webhook] CV2 sent — status {r.status_code}")
        return True

    print(f"[webhook] CV2 failed {r.status_code}: {r.text[:200]}")
    return False


# -----------------------------------
# Orchestrator
# -----------------------------------
def send_to_webhook(webhook, author, message, sha, repo_url, commit_url):
    img = create_commit_card(author, message, sha)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    image_url = upload_to_imgbb(buffer)
    if not image_url:
        print("[webhook] IMGBB_API_KEY must be set as a GitHub Actions secret")
        return False

    return send_cv2(webhook, author, message, sha, repo_url, commit_url, image_url)


# -----------------------------------
# CLI entry
# -----------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 7:
        print("Usage: send_cv2_webhook.py <webhook> <author> <message> <sha> <repo_url> <commit_url>")
        sys.exit(1)

    _webhook    = sys.argv[1]
    _author     = sys.argv[2]
    _message    = sys.argv[3].replace("\\n", "\n")
    _sha        = sys.argv[4]
    _repo_url   = sys.argv[5]
    _commit_url = sys.argv[6]

    ok = send_to_webhook(_webhook, _author, _message, _sha, _repo_url, _commit_url)
    sys.exit(0 if ok else 1)

