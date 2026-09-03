import aiohttp
import json
import re

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
}
_TIMEOUT = aiohttp.ClientTimeout(total=12)


async def fetch_latest_tiktok(username: str) -> dict | None:
    """Fetch the most recent video for a TikTok user using their web API."""
    username = username.lstrip("@")

    # Method 1: Try the web API user post endpoint
    try:
        api_url = f"https://www.tiktok.com/api/comment/list/?aid=1988&app_language=en&count=10&cursor=0&item_id=0&sec_uid={username}"
        # First, we need to get the user's secUid
        profile_url = f"https://www.tiktok.com/@{username}"
        async with aiohttp.ClientSession() as session:
            async with session.get(profile_url, headers=_HEADERS, timeout=_TIMEOUT) as resp:
                if resp.status != 200:
                    return None
                html = await resp.text()

        # Try to extract video data from the page's JSON
        match = re.search(
            r'<script[^>]+id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
            html, re.DOTALL
        )
        if match:
            data = json.loads(match.group(1))
            videos = _extract_videos(data)
            if videos:
                latest = videos[0]
                video_id = str(latest.get("id") or latest.get("videoId") or "")
                desc = latest.get("desc") or latest.get("description") or ""
                if video_id:
                    video_url = f"https://www.tiktok.com/@{username}/video/{video_id}"
                    return {"id": video_id, "url": video_url, "text": desc}

        # Method 2: Try the oembed endpoint for the user's latest
        # This won't give us the latest video, but we can try the user page meta
        og_match = re.search(
            r'<meta[^>]+property="og:description"[^>]+content="([^"]*)"',
            html
        )
        video_url_match = re.search(
            r'<meta[^>]+property="og:url"[^>]+content="([^"]*)"',
            html
        )
        if video_url_match:
            video_url = video_url_match.group(1)
            video_id_match = re.search(r'/video/(\d+)', video_url)
            if video_id_match:
                video_id = video_id_match.group(1)
                desc = og_match.group(1) if og_match else ""
                return {"id": video_id, "url": video_url, "text": desc}

    except Exception:
        pass

    return None


def _extract_videos(data: dict) -> list:
    """Try several known paths to find the video list in TikTok's JSON."""
    # Path 1: __DEFAULT_SCOPE__ > webapp.user-detail > userInfo > itemList
    try:
        scope = data.get("__DEFAULT_SCOPE__", {})
        user_page = scope.get("webapp.user-detail", {})
        user_info = user_page.get("userInfo", {})
        item_list = user_info.get("itemList", [])
        if item_list:
            return item_list
    except Exception:
        pass

    # Path 2: __DEFAULT_SCOPE__ > webapp.user-detail > itemList (older format)
    try:
        scope = data.get("__DEFAULT_SCOPE__", {})
        user_page = scope.get("webapp.user-detail", {})
        item_list = user_page.get("itemList", [])
        if item_list:
            return item_list
    except Exception:
        pass

    # Path 3: Recursive search
    return _find_key(data, "itemList") or []


def _find_key(obj, key: str):
    """Recursively search for a key in a nested dict/list."""
    if isinstance(obj, dict):
        if key in obj and isinstance(obj[key], list) and obj[key]:
            return obj[key]
        for v in obj.values():
            result = _find_key(v, key)
            if result:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = _find_key(item, key)
            if result:
                return result
    return None


async def validate_tiktok_username(username: str) -> bool:
    """Returns True if the username appears to be a real TikTok account."""
    username = username.lstrip("@")
    url = f"https://www.tiktok.com/@{username}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=_HEADERS, timeout=_TIMEOUT) as resp:
                if resp.status != 200:
                    return False
                html = await resp.text()
                # Check if the page has user data (not a redirect/error)
                return '"uniqueId"' in html or '"nickname"' in html
    except Exception:
        return False
