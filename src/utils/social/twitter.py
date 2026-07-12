import asyncio
import aiohttp
from bs4 import BeautifulSoup

NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.1d4.us",
    "https://nitter.cz",
    "https://nitter.space",
]

_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
_TIMEOUT = aiohttp.ClientTimeout(total=8)


async def _try_instance(session: aiohttp.ClientSession, instance: str, username: str):
    try:
        url = f"{instance}/{username}"
        async with session.get(url, headers=_HEADERS, timeout=_TIMEOUT) as resp:
            if resp.status != 200:
                return None
            html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        tweet = soup.select_one(".timeline-item")
        if not tweet:
            return None

        tweet_id = tweet.get("data-id")
        if not tweet_id:
            return None

        content = tweet.select_one(".tweet-content")
        text = content.get_text(" ", strip=True) if content else ""
        tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"

        return {"id": tweet_id, "url": tweet_url, "text": text}
    except Exception:
        return None


async def fetch_latest_tweet(username: str):
    """Try all Nitter instances concurrently and return the first valid result."""
    async with aiohttp.ClientSession() as session:
        tasks = [_try_instance(session, inst, username) for inst in NITTER_INSTANCES]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, dict) and result.get("id"):
            return result

    return None


async def validate_twitter_username(username: str) -> bool:
    """Returns True if the username can be fetched from at least one Nitter instance."""
    result = await fetch_latest_tweet(username)
    return result is not None
