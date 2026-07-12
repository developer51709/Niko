import aiohttp

_HEADERS = {"User-Agent": "Mozilla/5.0 DiscordBot/1.0"}
_TOUT    = aiohttp.ClientTimeout(total=10)


def _clean_sub(subreddit: str) -> str:
    """Normalise a subreddit input (strip r/, spaces, etc.)."""
    return subreddit.strip().lstrip("r/").strip()


async def fetch_latest_reddit(subreddit: str) -> dict | None:
    """Fetch the most recent post from a subreddit using Reddit's JSON API."""
    sub = _clean_sub(subreddit)
    url = f"https://www.reddit.com/r/{sub}/new.json?limit=1"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=_HEADERS, timeout=_TOUT) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        posts = data.get("data", {}).get("children", [])
        if not posts:
            return None

        pd      = posts[0].get("data", {})
        post_id = pd.get("id", "")
        title   = pd.get("title", "")
        text    = pd.get("selftext", "")
        if len(text) > 280:
            text = text[:280] + "…"
        link    = f"https://reddit.com{pd.get('permalink', '')}"

        # Use post thumbnail if it's a real image URL
        thumb = pd.get("thumbnail", "")
        if thumb and thumb.startswith("http"):
            thumbnail = thumb
        else:
            thumbnail = None

        # Prefer the preview image (higher resolution)
        try:
            preview_url = pd["preview"]["images"][0]["source"]["url"]
            # Reddit HTML-escapes the URL
            thumbnail = preview_url.replace("&amp;", "&")
        except (KeyError, IndexError):
            pass

        return {
            "id":        post_id,
            "url":       link,
            "title":     title,
            "text":      text or title,
            "thumbnail": thumbnail,
        }
    except Exception:
        return None


async def validate_reddit(subreddit: str) -> bool:
    """Return True if the subreddit exists and is accessible."""
    sub = _clean_sub(subreddit)
    url = f"https://www.reddit.com/r/{sub}/about.json"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=_HEADERS, timeout=_TOUT) as resp:
                if resp.status != 200:
                    return False
                data = await resp.json()
                # Make sure it's an actual subreddit, not a quarantined/banned one
                return data.get("data", {}).get("subscribers", 0) > 0
    except Exception:
        return False
