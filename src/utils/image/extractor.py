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


# extract multiple images from a message (same as the other function but can return multiple images instead of just one)
async def extract_images_from_message(message: discord.Message):
    # 1. Attachments (always check first)
    if message.attachments:
        # get all attachments
        attachments = []
        for attachment in message.attachments:
            attachments.append(BytesIO(await attachment.read()))
        return attachments

    # 2. Fetch RAW message JSON (discord.py does NOT expose CV2 UI)
    try:
        raw = await message._state.http.get_message(message.channel.id, message.id)
        # 3. Parse CV2 container structure from raw JSON
        if raw:
            # get all media galleries
            media_galleries = []
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
                                        media_galleries.append(await _fetch_url(url))
            if media_galleries:
                return media_galleries
    except Exception:
        pass

    # 4. Embeds (normal)
    embeds = []
    for embed in message.embeds:
        if embed.image and embed.image.url:
            embeds.append(await _fetch_url(embed.image.url))
        if embed.thumbnail and embed.thumbnail.url:
            embeds.append(await _fetch_url(embed.thumbnail.url))
    if embeds:
        return embeds

    # 5. URLs in content
    # get all urls in the message content
    urls = IMAGE_URL_REGEX.findall(message.content)
    if urls:
        # fetch all urls
        images = []
        for url in urls:
            images.append(await _fetch_url(url))
        return images

    # 6. Stickers
    # get all stickers
    if message.stickers:
        # get all stickers
        stickers = []
        for sticker in message.stickers:
            if sticker.url:
                stickers.append(await _fetch_url(sticker.url))
        return stickers

    # 7. Reply fallback
    # get all images from the replied message
    if message.reference:
        # get the replied message
        try:
            ref = await message.channel.fetch_message(message.reference.message_id)
            # get all images from the replied message
            images = await extract_images_from_message(ref)
            if images:
                return images
        except:
            pass
    return None