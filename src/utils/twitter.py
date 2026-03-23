import aiohttp
from bs4 import BeautifulSoup

NITTER_INSTANCE = "https://nitter.net"

async def fetch_latest_tweet(username: str):
    url = f"{NITTER_INSTANCE}/{username}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
            if resp.status != 200:
                return None

            html = await resp.text()

    soup = BeautifulSoup(html, "html.parser")
    tweet = soup.select_one(".timeline-item")

    if not tweet:
        return None

    tweet_id = tweet.get("data-id")
    content = tweet.select_one(".tweet-content")
    text = content.get_text(" ", strip=True) if content else ""

    tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"

    return {
        "id": tweet_id,
        "url": tweet_url,
        "text": text
    }