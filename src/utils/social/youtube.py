import re
import asyncio
import aiohttp
import feedparser

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DiscordBot/1.0)"}
_TIMEOUT  = aiohttp.ClientTimeout(total=15)

_YT_FEED  = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
_YT_THUMB = "https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"


# ─────────────────────────────────────────
#  Internal helpers
# ─────────────────────────────────────────

def _parse_stored(username: str) -> tuple[str, str]:
    """
    Stored YouTube usernames use the format  'DisplayName|ChannelID'.
    Returns (display_name, channel_id).
    Falls back to (username, username) for bare channel IDs.
    """
    if "|" in username:
        display, cid = username.split("|", 1)
        return display, cid
    return username, username


def make_stored(display_name: str, channel_id: str) -> str:
    """Encode a display name + channel ID into the stored format."""
    safe_display = display_name.replace("|", "")
    return f"{safe_display}|{channel_id}"


def display_name(username: str) -> str:
    """Return the human-readable display name for a stored YouTube username."""
    d, _ = _parse_stored(username)
    return d


def channel_id_of(username: str) -> str:
    """Extract the raw channel ID from a stored YouTube username."""
    _, cid = _parse_stored(username)
    return cid


# ─────────────────────────────────────────
#  Fetchers
# ─────────────────────────────────────────

async def fetch_latest_youtube(username: str) -> dict | None:
    """Fetch the most recent video for a stored YouTube username."""
    _, cid = _parse_stored(username)
    url = _YT_FEED.format(channel_id=cid)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=_HEADERS, timeout=_TIMEOUT) as resp:
                if resp.status != 200:
                    return None
                content = await resp.read()

        feed = feedparser.parse(content)
        if not feed.entries:
            return None

        entry    = feed.entries[0]
        video_id = entry.get("yt_videoid", "")
        if not video_id:
            return None

        return {
            "id":        video_id,
            "url":       f"https://www.youtube.com/watch?v={video_id}",
            "title":     entry.get("title", ""),
            "author":    entry.get("author", ""),
            "text":      entry.get("title", ""),
            "thumbnail": _YT_THUMB.format(video_id=video_id),
        }
    except Exception:
        return None


async def resolve_youtube_channel(query: str) -> tuple[str, str] | None:
    """
    Resolve a YouTube @handle, short URL, or bare channel ID to
    (display_name, channel_id).  Returns None if unresolvable.
    """
    query = query.strip().lstrip("@")

    # Already a valid channel ID (UC + 22 base64 chars = 24 total)
    if re.match(r"^UC[A-Za-z0-9_\-]{22}$", query):
        post = await fetch_latest_youtube(f"tmp|{query}")
        name = post.get("author", query) if post else query
        return name, query

    # Try as a @handle
    page_url = f"https://www.youtube.com/@{query}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                page_url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=aiohttp.ClientTimeout(total=12),
            ) as resp:
                if resp.status != 200:
                    return None
                html = await resp.text()
    except Exception:
        return None

    # Channel ID is embedded in the page JSON
    match = re.search(r'"channelId"\s*:\s*"(UC[A-Za-z0-9_\-]{22})"', html)
    if not match:
        match = re.search(r'"externalId"\s*:\s*"(UC[A-Za-z0-9_\-]{22})"', html)
    if not match:
        return None

    channel_id = match.group(1)

    # Try to get display name
    name_match = re.search(r'"channelName"\s*:\s*"([^"]+)"', html)
    if not name_match:
        name_match = re.search(r'"title"\s*:\s*"([^"]+)"', html)
    display = name_match.group(1) if name_match else query

    return display, channel_id


async def validate_youtube_channel(query: str) -> tuple[str, str] | None:
    """
    Validate a YouTube channel and return (display_name, channel_id),
    or None if the channel cannot be found / has no videos.
    """
    result = await resolve_youtube_channel(query)
    if result is None:
        return None
    display, cid = result
    # Confirm the feed actually has videos
    post = await fetch_latest_youtube(f"{display}|{cid}")
    return (display, cid) if post else None
