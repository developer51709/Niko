import re
import asyncio
import aiohttp
import feedparser

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DiscordBot/1.0)"}
_TIMEOUT  = aiohttp.ClientTimeout(total=15)

_YT_FEED  = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
_YT_THUMB = "https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

#: A channel id is always "UC" plus 22 URL-safe base64 characters.
_CHANNEL_ID_RE = re.compile(r"^UC[A-Za-z0-9_\-]{22}$")


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


async def _fetch_feed(channel_id: str):
    """Read and parse a channel's upload feed, or ``None`` if it is unreadable."""
    url = _YT_FEED.format(channel_id=channel_id)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=_HEADERS, timeout=_TIMEOUT) as resp:
                if resp.status != 200:
                    return None
                content = await resp.read()
    except Exception:
        return None
    return feedparser.parse(content)


# ─────────────────────────────────────────
#  Fetchers
# ─────────────────────────────────────────

async def fetch_latest_youtube(username: str) -> dict | None:
    """Fetch the most recent video for a stored YouTube username."""
    _, cid = _parse_stored(username)
    feed = await _fetch_feed(cid)
    if feed is None or not feed.entries:
        return None

    try:
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


async def channel_exists(username: str) -> bool:
    """Whether a channel still exists, whether or not it has uploaded anything.

    The upload feed answers 200 for an empty channel and 404 for one that does
    not exist, which is exactly what the notifier needs: a quiet channel is
    healthy, a deleted one is not. A timeout, a rate limit or a 5xx is treated
    as "still there" — an unreachable feed is no evidence the channel is gone,
    and guessing wrong pauses a server's notifications for no reason.
    """
    _, cid = _parse_stored(username)
    if not _CHANNEL_ID_RE.match(cid):
        return False
    url = _YT_FEED.format(channel_id=cid)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=_HEADERS, timeout=_TIMEOUT) as resp:
                return resp.status not in (404, 410)
    except Exception:
        return True


async def resolve_youtube_channel(query: str) -> tuple[str, str] | None:
    """
    Resolve a YouTube @handle, short URL, or bare channel ID to
    (display_name, channel_id).  Returns None if unresolvable.

    A channel does not need any uploads to resolve: the display name comes from
    the feed's own title, which YouTube serves for an empty channel too.
    """
    query = query.strip().lstrip("@")

    # Already a valid channel ID (UC + 22 base64 chars = 24 total)
    if _CHANNEL_ID_RE.match(query):
        feed = await _fetch_feed(query)
        if feed is None:
            return None
        return (feed.feed.get("title") or query), query

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

    # Get display name from the RSS feed (most reliable source)
    display = query
    feed = await _fetch_feed(channel_id)
    if feed is not None and feed.feed.get("title"):
        display = feed.feed["title"]

    # Fallback: try page HTML channelName
    if display == query:
        name_match = re.search(r'"channelName"\s*:\s*"([^"]+)"', html)
        if name_match:
            display = name_match.group(1)

    return display, channel_id


async def validate_youtube_channel(query: str) -> tuple[str, str] | None:
    """
    Validate a YouTube channel and return (display_name, channel_id).

    Verification is about the channel existing, not about it having uploaded a
    video: a brand-new channel with an empty feed is still a channel somebody
    may want to follow, so it must be addable.
    """
    return await resolve_youtube_channel(query)
