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
    # 1. Attachments
    if message.attachments:
        return BytesIO(await message.attachments[0].read())

    # 2. Embeds (image / thumbnail)
    for embed in message.embeds:
        if embed.image and embed.image.url:
            return await _fetch_url(embed.image.url)
        if embed.thumbnail and embed.thumbnail.url:
            return await _fetch_url(embed.thumbnail.url)

        # 3. URLs in description
        if embed.description:
            match = IMAGE_URL_REGEX.search(embed.description)
            if match:
                return await _fetch_url(match.group(1))

    # 4. Raw URLs in content
    if message.content:
        match = IMAGE_URL_REGEX.search(message.content)
        if match:
            return await _fetch_url(match.group(1))

    return None