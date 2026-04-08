# nsfw.py
# uses the rule34 and gelbooru APIs to fetch images
# only works in NSFW channels

import discord
from discord.ext import commands
import requests
import random
import os
from utils.realbooru import search_realbooru, get_post_details

# get api keys and user ids from environment variables
RULE34_API_KEY = os.getenv('RULE34_API_KEY')
RULE34_USER_ID = os.getenv('RULE34_USER_ID')
GELBOORU_API_KEY = os.getenv('GELBOORU_API_KEY')
GELBOORU_USER_ID = os.getenv('GELBOORU_USER_ID')

class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='rule34', 
        aliases=['r34'],
        help='Search for images on rule34.xxx'
    )
    @commands.is_nsfw()
    async def rule34(self, ctx, *, query: str):
        # verify that the query is formatted correctly (must use url encoding for spaces and special characters)
        if ' ' in query:
            query = query.replace(' ', '+')
        if '&' in query:
            query = query.replace('&', '%26')
        if '=' in query:
            query = query.replace('=', '%3D')
        # make request to rule34 API with api key and user id
        RULE34_API_URL = f'https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={query}&limit=100&pid=0&api_key={RULE34_API_KEY}&user_id={RULE34_USER_ID}'
        response = requests.get(RULE34_API_URL)
        # check if response is valid
        if response.status_code != 200:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### Rule34\nAn error occurred while fetching images.\n-# Response code: `{response.status_code}`"
                )
            )
            view.add_item(container)
            return await ctx.send(view=view)
        # verify that the response is valid json
        content_type = response.headers.get("Content-Type", "")

        if "application/json" not in content_type:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### Rule34\nThe API returned an unexpected response format.\n-# Content-Type: `{content_type}`"
                )
            )
            view.add_item(container)
            return await ctx.send(view=view)
        # parse response
        data = response.json()
        # check if any images were found
        if not data:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### Rule34\nNo images found for the given query."
                )
            )
            view.add_item(container)
            return await ctx.send(view=view)
        # select random image
        image = random.choice(data)
        # check if image is valid
        if not image.get('file_url'):
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### Rule34\nAn error occurred while fetching the image.\n-# Invalid image URL"
                )
            )
            view.add_item(container)
            return await ctx.send(view=view)
        query = query.replace('+', '`, `')
        # send image in a cv2 container with the query and image source
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### Rule34\nQuery: `{query}`\n[Image Source]({image['file_url']})"
            ),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=image['file_url']
                )
            ),
            discord.ui.TextDisplay(
                content=f"-# Requested by {ctx.author.display_name}"
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

    @commands.command(
        name='gelbooru', 
        help='Search for images on gelbooru.com'
    )
    @commands.is_nsfw()
    async def gelbooru(self, ctx, *, query: str):
        # make request to gelbooru API with api key and user id
        GELBOORU_API_URL = f'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags={query}&limit=100&pid=0&api_key={GELBOORU_API_KEY}&user_id={GELBOORU_USER_ID}'
        response = requests.get(GELBOORU_API_URL)
        # check if response is valid
        if response.status_code != 200:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### Gelbooru\nAn error occurred while fetching images.\n-# Response code: `{response.status_code}`"
                )
            )
            view.add_item(container)
            return await ctx.send(view=view)
        # check if response is valid json
        content_type = response.headers.get("Content-Type", "")

        if "application/json" not in content_type:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### Gelbooru\nThe API returned an unexpected response format.\n-# Content-Type: `{content_type}`"
                )
            )
            view.add_item(container)
            return await ctx.send(view=view)
        # parse response
        data = response.json()
        posts = data.get("post", [])

        if not posts:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### Gelbooru\nNo images found for the given query."
                )
            )
            view.add_item(container)
            return await ctx.send(view=view)

        image = random.choice(posts)
        # check if image is valid
        if not image.get('file_url'):
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### Gelbooru\nAn error occurred while fetching the image.\n-# Invalid image URL"
                )
            )
            view.add_item(container)
            return await ctx.send(view=view)
        # send image in a cv2 container with the query and image source
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### Gelbooru\nTitle: {image['title']}\nQuery: `{query}`\n[Image Source]({image['source']})"
            ),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=image['preview_url']
                )
            ),
            discord.ui.TextDisplay(
                content=f"-# Requested by {ctx.author.display_name}"
            )
        )
        view.add_item(container)
        await ctx.send(view=view)


    @commands.command(
        name='realbooru',
        aliases=['realb'],
        help='Search for images on realbooru.com'
    )
    @commands.is_nsfw()
    async def realbooru(self, ctx, *, query: str):
        posts = search_realbooru(query)

        if not posts:
            return await self._send_error(
                ctx,
                f"No images found for query `{query}`."
            )

        # Pick a random post
        post = random.choice(posts)
        details = get_post_details(post["id"])

        if not details["media_url"]:
            return await self._send_error(
                ctx,
                "Failed to fetch full image from Realbooru."
            )

        # Build UI
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    f"### Realbooru\n"
                    f"Query: `{query}`"
                )
            ),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=details["media_url"]
                )
            ),
            discord.ui.TextDisplay(
                content=f"-# Requested by {ctx.author.display_name}"
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

    async def _send_error(self, ctx, message: str):
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### Realbooru\n{message}"
            )
        )
        view.add_item(container)
        return await ctx.send(view=view)


# setup
async def setup(bot):
    await bot.add_cog(NSFW(bot))