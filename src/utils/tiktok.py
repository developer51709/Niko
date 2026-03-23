from TikTokApi import TikTokApi

async def fetch_latest_tiktok(username: str):
    try:
        async with TikTokApi() as api:
            user = api.user(username)
            videos = await user.videos(count=1)

            if not videos:
                return None

            latest = videos[0]
            video_id = latest.id
            video_url = f"https://www.tiktok.com/@{username}/video/{video_id}"
            desc = latest.desc or ""

            return {
                "id": video_id,
                "url": video_url,
                "text": desc
            }

    except Exception:
        return None