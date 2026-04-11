import discord
import aiohttp
import re
from io import BytesIO

IMAGE_URL_REGEX = re.compile(
    r"(https?://[^\s]+?\.(?:png|jpe?g|gif|webp))",
    re.IGNORECASE
)


async def _fetch_url(url: str) -> BytesIO:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.read()
            return BytesIO(data)


async def extract_image_from_message(message: discord.Message):
    # 1. Attachments (always check first)
    if message.attachments:
        return BytesIO(await message.attachments[0].read())

    # 2. Fetch RAW message JSON (discord.py does NOT expose CV2 UI)
    try:
        raw = await message._state.http.get_message(message.channel.id, message.id)
    except Exception:
        raw = None

    # 3. Parse CV2 container structure from raw JSON
    if raw:
        for row in raw.get("components", []):
            if row.get("type") == 17:  # LayoutView
                for comp in row.get("components", []):

                    # --- A) MediaGallery (full-size images) ---
                    if comp.get("type") == 12:  # MediaGallery
                        for item in comp.get("items", []):
                            media = item.get("media")
                            if isinstance(media, dict):
                                url = media.get("url")
                                if url:
                                    return await _fetch_url(url)

                    # --- B) Accessory thumbnails (type 11) ---
                    accessory = comp.get("accessory")
                    if accessory and accessory.get("type") == 11:
                        media = accessory.get("media")
                        if isinstance(media, dict):
                            url = media.get("url")
                            if url:
                                return await _fetch_url(url)

    # 4. Embeds (normal)
    for embed in message.embeds:
        if embed.image and embed.image.url:
            return await _fetch_url(embed.image.url)
        if embed.thumbnail and embed.thumbnail.url:
            return await _fetch_url(embed.thumbnail.url)

    # 5. URLs in content
    if message.content:
        match = IMAGE_URL_REGEX.search(message.content)
        if match:
            return await _fetch_url(match.group(1))

    # 6. Stickers
    if message.stickers:
        # only get the first sticker
        sticker = message.stickers[0]
        if sticker.url:
            return await _fetch_url(sticker.url)

    # 7. Reply fallback
    if message.reference:
        try:
            ref = await message.channel.fetch_message(message.reference.message_id)
            return await extract_image_from_message(ref)
        except:
            pass

    return None