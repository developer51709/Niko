import discord
import aiohttp
import re
from io import BytesIO
import imageio.v3 as iio
import numpy as np
import ffmpeg

IMAGE_URL_REGEX = re.compile(
    r"(https?://[^\s]+?\.(?:png|jpe?g|gif|webp))",
    re.IGNORECASE
)


async def convert_video_to_gif_raw(url: str) -> BytesIO:
    """
    Convert MP4/WebP to GIF without compression.
    This produces a large but VALID animated GIF.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            video_bytes = await resp.read()

    process = (
        ffmpeg
        .input('pipe:', format='mp4')
        .output('pipe:', format='gif')
        .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
    )

    gif_bytes, _ = process.communicate(input=video_bytes)

    buf = BytesIO(gif_bytes)
    buf.seek(0)
    return buf


async def compress_gif(gif_bytes: BytesIO) -> BytesIO:
    """
    Compress an existing GIF using ffmpeg palettegen + paletteuse.
    This reduces size dramatically while keeping animation.
    """
    gif_bytes.seek(0)
    raw = gif_bytes.read()

    # PASS 1: palette generation
    palette_proc = (
        ffmpeg
        .input('pipe:', format='gif')
        .filter('fps', 12)
        .filter('scale', 480, -1)
        .filter('palettegen')
        .output('pipe:', format='png')
        .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
    )
    palette_png, _ = palette_proc.communicate(input=raw)

    # PASS 2: apply palette
    gif_proc = (
        ffmpeg
        .input('pipe:', format='gif')
        .input('pipe:', format='png')
        .filter_complex('[0:v][1:v]paletteuse')
        .output('pipe:', format='gif')
        .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
    )
    compressed_bytes, _ = gif_proc.communicate(input=raw + palette_png)

    buf = BytesIO(compressed_bytes)
    buf.seek(0)
    return buf


async def _fetch_url(url: str) -> BytesIO:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return BytesIO(await resp.read())


def extract_tenor_animated(raw: dict) -> str | None:
    """
    Extract the animated Tenor MP4/WebP from the raw payload.
    """
    for embed in raw.get("embeds", []):
        if embed.get("type") != "gifv":
            continue

        provider = embed.get("provider") or {}
        if provider.get("name", "").lower() != "tenor":
            continue

        video = embed.get("video") or {}
        return video.get("proxy_url") or video.get("url")

    return None


async def extract_image_from_message(message: discord.Message):
    # 1. Attachments
    if message.attachments:
        return BytesIO(await message.attachments[0].read())

    # 2. Raw payload
    try:
        raw = await message._state.http.get_message(message.channel.id, message.id)
    except:
        raw = None

    # 2a. Tenor animated extraction
    if raw:
        animated_url = extract_tenor_animated(raw)
        if animated_url:
            # Step 1: convert MP4/WebP → GIF (large but valid)
            gif_raw = await convert_video_to_gif_raw(animated_url)

            # Step 2: compress GIF → smaller GIF
            gif_compressed = await compress_gif(gif_raw)

            return gif_compressed

    # 3. CV2 containers
    if raw:
        for row in raw.get("components", []):
            if row.get("type") == 17:
                for comp in row.get("components", []):
                    if comp.get("type") == 12:
                        for item in comp.get("items", []):
                            media = item.get("media")
                            if isinstance(media, dict) and media.get("url"):
                                return await _fetch_url(media["url"])

                    accessory = comp.get("accessory")
                    if accessory and accessory.get("type") == 11:
                        media = accessory.get("media")
                        if isinstance(media, dict) and media.get("url"):
                            return await _fetch_url(media["url"])

    # 4. Embeds
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

    # 6. Reply fallback
    if message.reference:
        try:
            ref = await message.channel.fetch_message(message.reference.message_id)
            return await extract_image_from_message(ref)
        except:
            pass

    return None