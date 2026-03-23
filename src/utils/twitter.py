import aiohttp
from bs4 import BeautifulSoup

NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.1d4.us",
]

async def fetch_latest_tweet(username: str):
    for instance in NITTER_INSTANCES:
        url = f"{instance}/{username}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        continue

                    html = await resp.text()

            soup = BeautifulSoup(html, "html.parser")
            tweet = soup.select_one(".timeline-item")

            if not tweet:
                continue

            tweet_id = tweet.get("data-id")
            content = tweet.select_one(".tweet-content")
            text = content.get_text(" ", strip=True) if content else ""

            tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"

            return {
                "id": tweet_id,
                "url": tweet_url,
                "text": text
            }

        except Exception:
            continue

    return None
