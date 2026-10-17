import asyncio
import aiohttp
import re

_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
_TIMEOUT = aiohttp.ClientTimeout(total=10)


async def fetch_latest_tweet(username: str) -> dict | None:
    """Fetch the most recent tweet using multiple fallback approaches."""
    username = username.lstrip("@")

    # Approach 1: Syndication timeline embed
    result = await _fetch_via_syndication(username)
    if result:
        return result

    # Approach 2: Twitter publish oembed
    result = await _fetch_via_oembed(username)
    if result:
        return result

    return None


async def _fetch_via_syndication(username: str) -> dict | None:
    """Try fetching via Twitter's syndication embed endpoint."""
    try:
        url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{username}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=_HEADERS, timeout=_TIMEOUT) as resp:
                if resp.status != 200:
                    return None
                html = await resp.text()

        # Extract tweet ID from data-tweet-id or status links
        tweet_id_match = re.search(r'data-tweet-id="(\d+)"', html)
        if not tweet_id_match:
            tweet_id_match = re.search(rf'/{re.escape(username)}/status/(\d+)', html)
        if not tweet_id_match:
            return None

        tweet_id = tweet_id_match.group(1)
        tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"

        # Extract tweet text
        text = ""
        text_match = re.search(
            r'class="[^"]*tweet-text[^"]*"[^>]*>(.*?)</(?:p|div)',
            html, re.DOTALL
        )
        if text_match:
            text = re.sub(r'<[^>]+>', ' ', text_match.group(1)).strip()

        return {"id": tweet_id, "url": tweet_url, "text": text}
    except Exception:
        return None


async def _fetch_via_oembed(username: str) -> dict | None:
    """Try fetching via Twitter's oembed API (returns the latest tweet as an embed)."""
    try:
        # oembed accepts a profile URL and returns the latest tweet
        profile_url = f"https://twitter.com/{username}"
        oembed_url = f"https://publish.twitter.com/oembed?url={profile_url}&omit_script=true&maxwidth=550"

        async with aiohttp.ClientSession() as session:
            async with session.get(oembed_url, headers=_HEADERS, timeout=_TIMEOUT) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        html = data.get("html", "")
        if not html:
            return None

        # Extract tweet ID from the embed HTML
        tweet_id_match = re.search(r'/status/(\d+)', html)
        if not tweet_id_match:
            return None

        tweet_id = tweet_id_match.group(1)
        tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"

        # Extract text from the embed
        text = ""
        text_match = re.search(r'class="[^"]*tweet-text[^"]*"[^>]*>(.*?)</(?:p|div)', html, re.DOTALL)
        if text_match:
            text = re.sub(r'<[^>]+>', ' ', text_match.group(1)).strip()
        else:
            # Try extracting from data-tweet-removed or visible text
            text_match = re.search(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
            if text_match:
                text = re.sub(r'<[^>]+>', ' ', text_match.group(1)).strip()

        return {"id": tweet_id, "url": tweet_url, "text": text}
    except Exception:
        return None


async def validate_twitter_username(username: str) -> bool:
    """Returns True if the username can be fetched."""
    result = await fetch_latest_tweet(username)
    return result is not None
