import asyncio
import aiohttp
import feedparser
import re

_HEADERS = {"User-Agent": "nikobot/1.0 (Discord bot; +https://nikobot.dev)"}
_TIMEOUT = aiohttp.ClientTimeout(total=10)
_MAX_RETRIES = 3
_RETRY_DELAY = 5  # seconds


def _clean_sub(subreddit: str) -> str:
    """Normalise a subreddit input (strip r/, spaces, etc.)."""
    return subreddit.strip().lstrip("r/").strip()


async def fetch_latest_reddit(subreddit: str) -> dict | None:
    """Fetch the most recent post from a subreddit using Reddit's RSS feed."""
    sub = _clean_sub(subreddit)
    url = f"https://www.reddit.com/r/{sub}/new/.rss?limit=1"

    for attempt in range(_MAX_RETRIES):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=_HEADERS, timeout=_TIMEOUT) as resp:
                    if resp.status == 429:
                        # Rate limited — wait and retry
                        if attempt < _MAX_RETRIES - 1:
                            await asyncio.sleep(_RETRY_DELAY * (attempt + 1))
                            continue
                        return None

                    if resp.status != 200:
                        return None

                    content = await resp.text()
                    feed = feedparser.parse(content)

                    if not feed.entries:
                        return None

                    entry = feed.entries[0]
                    # Reddit RSS ID format: https://reddit.com/r/sub/comments/id/title/
                    entry_id = entry.get("id", "")
                    post_id = entry_id.split("/")[-2] if "/" in entry_id else entry_id
                    title = entry.get("title", "")
                    link = entry.get("link", "")

                    # Extract text content
                    text = ""
                    if "content" in entry:
                        raw = entry.content[0].get("value", "")
                        text = re.sub(r"<[^>]+>", " ", raw).strip()
                    if len(text) > 280:
                        text = text[:280] + "…"

                    # Extract thumbnail
                    thumbnail = None
                    if "media_thumbnail" in entry:
                        thumbnail = entry.media_thumbnail[0].get("url")
                    elif "media_content" in entry:
                        for media in entry.media_content:
                            if media.get("medium") == "image":
                                thumbnail = media.get("url")
                                break

                    return {
                        "id": post_id or title,
                        "url": link,
                        "title": title,
                        "text": text or title,
                        "thumbnail": thumbnail,
                    }
        except Exception:
            if attempt < _MAX_RETRIES - 1:
                await asyncio.sleep(_RETRY_DELAY)
                continue
            return None

    return None


async def validate_reddit(subreddit: str) -> bool:
    """Return True if the subreddit exists and has recent posts."""
    sub = _clean_sub(subreddit)
    url = f"https://www.reddit.com/r/{sub}/new/.rss?limit=1"

    for attempt in range(_MAX_RETRIES):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=_HEADERS, timeout=_TIMEOUT) as resp:
                    if resp.status == 429:
                        if attempt < _MAX_RETRIES - 1:
                            await asyncio.sleep(_RETRY_DELAY * (attempt + 1))
                            continue
                        return False
                    if resp.status != 200:
                        return False
                    content = await resp.text()
                    feed = feedparser.parse(content)
                    return len(feed.entries) > 0
        except Exception:
            if attempt < _MAX_RETRIES - 1:
                await asyncio.sleep(_RETRY_DELAY)
                continue
            return False

    return False
