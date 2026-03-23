import aiohttp

async def fetch_latest_tiktok(username: str):
    url = f"https://www.tiktok.com/@{username}?__a=1&__d=1"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.tiktok.com/"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                return None

            data = await resp.json(content_type=None)

    try:
        videos = data["items"]
        latest = videos[0]

        video_id = latest["id"]
        video_url = f"https://www.tiktok.com/@{username}/video/{video_id}"
        desc = latest.get("desc", "")

        return {
            "id": video_id,
            "url": video_url,
            "text": desc
        }

    except Exception:
        return None