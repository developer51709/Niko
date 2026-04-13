# this cog uses the nikoapi to generate and edit images
import discord
from discord.ext import commands
import aiohttp
import os
import io
import base64
import asyncio
from utils import logging
from utils.image.extractor import extract_image_from_message
from config.emojis import get_emoji

BASE_URL = "https://ofkulvdrcwpsebewszsz.supabase.co/functions/v1"

premium_role_id = 1493294143600853062
support_server_id = 1470878953743974587

headers = {
    "Content-Type": "application/json",
    "x-api-key": os.environ.get("NIKOAPI_KEY")
}

class AiImageTools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        await self.session.close()

    async def _decode_image(self, b64_data: str):
        """Decode base64 image safely off the event loop."""
        return await asyncio.to_thread(lambda: io.BytesIO(base64.b64decode(b64_data)))

    async def GenerateImage(self, prompt: str):
        url = f"{BASE_URL}/api-image-generate"
        data = {"prompt": prompt}

        async with self.session.post(url, headers=headers, json=data) as resp:
            response = await resp.json()

        text = response["text"]
        image_b64 = response["images"][0].split(",")[1]

        image = await self._decode_image(image_b64)
        return text, image

    async def EditImage(self, image_b64: str, prompt: str):
        url = f"{BASE_URL}/api-image-edit"
        data = {"prompt": prompt, "image_url": image_b64}

        async with self.session.post(url, headers=headers, json=data) as resp:
            response = await resp.json()

        # Log the full response for debugging
        print("[AiImageTools/EditImage] API Response:", response)

        if "text" not in response or "images" not in response:
            return response

        text = response["text"]
        image_b64 = response["images"][0].split(",")[1]

        output_image = await self._decode_image(image_b64)
        return text, output_image

    # create cv2 container for the response
    def build_cv2_container(self, title: str, message: str, file: discord.File):
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {title}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small)
        )
        if message:
            container.add_item(discord.ui.TextDisplay(content=message))
        container.add_item(discord.ui.MediaGallery(discord.MediaGalleryItem(media=file)))
        view.add_item(container)
        return view

    def check_premium(self, member: discord.Member):
        guild = self.bot.get_guild(support_server_id)
        if guild is None:
            return False

        role = guild.get_role(premium_role_id)
        if role is None:
            return False

        guild_member = guild.get_member(member.id)
        if guild_member is None:
            return False

        return role in guild_member.roles

    @commands.command(
        name="generate",
        help="Generate an image using AI.",
        aliases=["imagen", "imagine"]
    )
    async def generate(self, ctx: commands.Context, *, prompt: str):
        if not self.check_premium(ctx.author):
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('icon_danger')} Premium Required"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content="Due to the cost of AI image generation, this command is only available to premium users.\n\nYou can get premium by joining the support server and boosting."
                )
            )
            view.add_item(container)
            return await ctx.send(view=view)

        async with ctx.typing():
            text, image = await self.GenerateImage(prompt)
            file = discord.File(image, filename="generated_image.png")
            view = self.build_cv2_container("Generated Image", text, file)

            try:
                await ctx.reply(view=view, file=file)
            except Exception:
                await ctx.send(view=view, file=file)


    @commands.command(
        name="edit",
        help="Edit an image using AI. Attach an image or reply to one.",
        aliases=["aiedit", "editimage"]
    )
    async def edit(self, ctx: commands.Context, *, prompt: str):
        # premium check
        if not self.check_premium(ctx.author):
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('icon_danger')} Premium Required"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content="AI image editing is a premium-only feature.\n\nJoin the support server and boost to unlock it."
                )
            )
            view.add_item(container)
            return await ctx.send(view=view)

        # extract image from message
        image_bytes = await extract_image_from_message(ctx.message)
        if image_bytes is None:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('icon_danger')} No Image Found"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content="Please attach an image or reply to one so I can edit it."
                )
            )
            view.add_item(container)
            return await ctx.send(view=view)

        async with ctx.typing():
            # convert image to base64 for API
            raw_bytes = image_bytes.getvalue()
            b64_image = await asyncio.to_thread(lambda: base64.b64encode(raw_bytes).decode())

            # the ai function will return either the text and image or an error so we need to be able to read both
            response = await self.EditImage(b64_image, prompt)
            # check if the error value contains a response
            if response["error"]:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"### {get_emoji('icon_danger')} NikoAPI Error"
                    ),
                    discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                    discord.ui.TextDisplay(
                        content=f"API Response:\n```\n{response}\n```"
                    )
                )
                view.add_item(container)
                try:
                    return await ctx.reply(view=view)
                except Exception:
                    return await ctx.send(view=view)
            else:
                text, edited_image = response

            file = discord.File(edited_image, filename="edited_image.png")
            view = self.build_cv2_container("Edited Image", text, file)

            try:
                await ctx.reply(view=view, file=file)
            except Exception:
                await ctx.send(view=view, file=file)


async def setup(bot: commands.Bot):
    await bot.add_cog(AiImageTools(bot))
