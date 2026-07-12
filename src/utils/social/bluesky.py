import aiohttp

_API  = "https://public.api.bsky.app/xrpc"
_TOUT = aiohttp.ClientTimeout(total=10)


async def fetch_latest_bluesky(handle: str) -> dict | None:
    """Fetch the most recent post from a Bluesky account (no auth required)."""
    handle = handle.lstrip("@")
    url = f"{_API}/app.bsky.feed.getAuthorFeed?actor={handle}&limit=1&filter=posts_no_replies"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=_TOUT) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        feed = data.get("feed", [])
        if not feed:
            return None

        item   = feed[0]
        post   = item.get("post", {})
        record = post.get("record", {})

        uri     = post.get("uri", "")
        post_id = uri.split("/")[-1] if uri else ""
        text    = record.get("text", "")
        profile_url = f"https://bsky.app/profile/{handle}/post/{post_id}"

        # Image from the post embed view
        thumbnail = None
        view_embed = post.get("embed", {})
        etype = view_embed.get("$type", "")
        if "images#view" in etype:
            imgs = view_embed.get("images", [])
            if imgs:
                thumbnail = imgs[0].get("fullsize") or imgs[0].get("thumb")
        elif "external#view" in etype:
            thumbnail = view_embed.get("external", {}).get("thumb")

        return {
            "id":        post_id,
            "url":       profile_url,
            "text":      text,
            "thumbnail": thumbnail,
        }
    except Exception:
        return None


async def validate_bluesky_handle(handle: str) -> bool:
    """Return True if the Bluesky handle resolves to a real account."""
    handle = handle.lstrip("@")
    url = f"{_API}/app.bsky.actor.getProfile?actor={handle}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=_TOUT) as resp:
                return resp.status == 200
    except Exception:
        return False
