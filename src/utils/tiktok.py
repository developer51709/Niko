import aiohttp
import json
import re

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
}
_TIMEOUT = aiohttp.ClientTimeout(total=12)


async def fetch_latest_tiktok(username: str):
    """Scrape TikTok's web page to find the latest video for a user."""
    username = username.lstrip("@")
    url = f"https://www.tiktok.com/@{username}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=_HEADERS, timeout=_TIMEOUT) as resp:
                if resp.status != 200:
                    return None
                html = await resp.text()

        # TikTok embeds state JSON in a <script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"> tag
        match = re.search(
            r'<script[^>]+id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
            html, re.DOTALL
        )
        if not match:
            # Fallback: look for NEXT_DATA
            match = re.search(r'<script[^>]+id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
            if not match:
                return None

        data = json.loads(match.group(1))

        # Navigate to video list (structure varies by TikTok version)
        video_list = _extract_videos(data)
        if not video_list:
            return None

        latest = video_list[0]
        video_id = str(latest.get("id") or latest.get("videoId") or "")
        desc = latest.get("desc") or latest.get("description") or ""
        if not video_id:
            return None

        video_url = f"https://www.tiktok.com/@{username}/video/{video_id}"
        return {"id": video_id, "url": video_url, "text": desc}

    except Exception:
        return None


def _extract_videos(data: dict) -> list:
    """Try several known paths to find the video list in TikTok's JSON."""
    # Path 1: __DEFAULT_SCOPE__ > webapp.user-detail > userInfo > ... not useful
    # Try itemList under user page
    try:
        scope = data.get("__DEFAULT_SCOPE__", {})
        user_page = scope.get("webapp.user-detail", {})
        item_list = user_page.get("itemList", [])
        if item_list:
            return item_list
    except Exception:
        pass

    # Path 2: props > pageProps > items
    try:
        items = data["props"]["pageProps"]["items"]
        if items:
            return items
    except Exception:
        pass

    # Path 3: search recursively for "itemList"
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
                return resp.status == 200
    except Exception:
        return False
