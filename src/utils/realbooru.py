import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://realbooru.com/index.php"


def search_realbooru(query: str):
    """
    Scrapes Realbooru search results and returns a list of posts.
    Each post contains: id, preview_url, post_url
    """
    url = f"{BASE_URL}?page=post&s=list&tags={query}"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    posts = []

    for thumb in soup.select(".thumb"):
        link = thumb.find("a")
        img = thumb.find("img")

        if not link or not img:
            continue

        href = link.get("href", "")
        if "id=" not in href:
            continue

        post_id = href.split("id=")[-1]

        preview_url = img.get("src")
        if preview_url.startswith("//"):
            preview_url = "https:" + preview_url

        posts.append({
            "id": post_id,
            "preview_url": preview_url,
            "post_url": f"{BASE_URL}?page=post&s=view&id={post_id}"
        })

    return posts


def get_post_details(post_id: str):
    """
    Scrapes a Realbooru post page to extract:
    - highest quality media (image or video)
    - media type ("image" or "video")
    - title
    - source URL
    """
    url = f"{BASE_URL}?page=post&s=view&id={post_id}"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    # -------------------------
    # 1. Detect if post is a video
    # -------------------------
    video_tag = soup.find("video")
    if video_tag:
        # Realbooru uses <source src="..."> inside <video>
        source_tag = video_tag.find("source")
        if source_tag:
            video_url = source_tag.get("src")
            if video_url.startswith("//"):
                video_url = "https:" + video_url

            return {
                "media_url": video_url,
                "media_type": "video",
                "title": _extract_title(soup),
                "source": _extract_source(soup)
            }

    # -------------------------
    # 2. Otherwise, it's an image
    # -------------------------
    img = soup.select_one("#image")
    file_url = img.get("src") if img else None

    if file_url and file_url.startswith("//"):
        file_url = "https:" + file_url

    # Realbooru sometimes has sample images; try to find full-size
    full_image = _find_highest_quality_image(soup, file_url)

    return {
        "media_url": full_image,
        "media_type": "image",
        "title": _extract_title(soup),
        "source": _extract_source(soup)
    }


# ---------------------------------------------------------
# Helper: Extract title
# ---------------------------------------------------------
def _extract_title(soup: BeautifulSoup):
    title_tag = soup.select_one("title")
    if not title_tag:
        return "Untitled"
    return title_tag.text.replace("Realbooru - ", "").strip()


# ---------------------------------------------------------
# Helper: Extract source link
# ---------------------------------------------------------
def _extract_source(soup: BeautifulSoup):
    for li in soup.select("li"):
        if "Source" in li.text:
            a = li.find("a")
            if a:
                return a.get("href")
    return "No source provided"


# ---------------------------------------------------------
# Helper: Find highest quality image
# ---------------------------------------------------------
def _find_highest_quality_image(soup: BeautifulSoup, fallback_url: str):
    """
    Realbooru sometimes embeds:
    - sample image
    - full image
    - resized image

    We try to find the highest quality version.
    """
    # Look for links to full-size images
    for a in soup.find_all("a"):
        href = a.get("href", "")
        if any(href.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
            if href.startswith("//"):
                href = "https:" + href
            if href.startswith("/"):
                href = urljoin(BASE_URL, href)
            return href

    # Fallback to the displayed image
    return fallback_url