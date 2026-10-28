"""AI image tools.

Generation runs on Pollinations' free, keyless endpoint: no API key, no
per-image bill. That is also why it is rate limited — every render is a request
to a shared public service, and one person spamming it gets everyone throttled.

Image editing used to call paid image-to-image models. It is retired: no free
provider produced results worth shipping, so /edit now explains that and points
people at the support server to suggest one.
"""

import io
import os
import random
from urllib.parse import quote

import aiohttp
import discord
from discord.ext import commands

from config import links
from config.emojis import get_emoji
from utils import logging

PROVIDER_URL = "https://image.pollinations.ai/prompt"
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=60)

#: Seconds one member must wait between generations. `IMAGE_GEN_COOLDOWN=15`
#: makes it faster; there is no way to turn the limit off. The cooldown applies
#: per user across every server, so switching channels does not reset it.
USER_COOLDOWN = max(1, int(os.getenv("IMAGE_GEN_COOLDOWN") or 30))


class AiImageTools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── Provider ──────────────────────────────────

    async def generate_image(self, prompt: str) -> tuple[io.BytesIO | None, str | None]:
        """Render one image, returning ``(image, error)``."""
        url = f"{PROVIDER_URL}/{quote(prompt.strip(), safe='')}"
        try:
            async with aiohttp.ClientSession(timeout=REQUEST_TIMEOUT) as session:
                async with session.get(url, params={"seed": random.randint(1, 1_000_000)}) as response:
                    if response.status != 200:
                        detail = (await response.text())[:160]
                        logging.warning(
                            "AiImageTools", f"Provider returned {response.status}: {detail}"
                        )
                        return None, "The image provider is busy right now. Try again in a moment."
                    data = await response.read()
        except Exception as error:
            logging.warning("AiImageTools", f"Generation request failed: {error}")
            return None, "The image provider could not be reached. Try again in a moment."

        if not data:
            logging.warning("AiImageTools", "Provider returned an empty body.")
            return None, "The image provider sent back an empty image. Try again in a moment."
        return io.BytesIO(data), None

    # ── Response builders ─────────────────────────

    def build_cv2_container(self, title: str, message: str, filename: str) -> discord.ui.LayoutView:
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {title}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )
        if message:
            container.add_item(discord.ui.TextDisplay(content=message))
        container.add_item(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(media=f"attachment://{filename}")
            )
        )
        view.add_item(container)
        return view

    def _error_view(self, detail: str) -> discord.ui.LayoutView:
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('danger')} Generation Failed"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=detail),
            accent_colour=discord.Color.red(),
        )
        view.add_item(container)
        return view

    # ── Commands ──────────────────────────────────

    @commands.command(
        name="generate",
        help="Generate an image using AI.",
        aliases=["imagen", "imagine"],
    )
    @commands.cooldown(1, USER_COOLDOWN, commands.BucketType.user)
    async def generate(self, ctx: commands.Context, *, prompt: str):
        async with ctx.typing():
            image, error = await self.generate_image(prompt)

        if error or image is None:
            detail = error or "The image provider returned nothing. Try again in a moment."
            try:
                return await ctx.reply(view=self._error_view(detail))
            except Exception:
                return await ctx.send(view=self._error_view(detail))

        image.seek(0)
        file = discord.File(image, filename="generated_image.png")
        view = self.build_cv2_container(
            f"{get_emoji('image')} Generated Image",
            f"-# Prompt: *{discord.utils.escape_markdown(prompt[:200])}*",
            file.filename,
        )
        try:
            await ctx.reply(view=view, file=file)
        except Exception:
            await ctx.send(view=view, file=file)

    @commands.command(
        name="edit",
        help="Image editing was retired — this explains why.",
        aliases=["aiedit", "editimage"],
        hidden=True,
    )
    async def edit(self, ctx: commands.Context, *, prompt: str | None = None):
        """/edit is gone; keep the name so old muscle memory gets an answer."""
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('image')} Image editing was removed"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    "AI image editing was retired because the hosted models charged "
                    "per edit, and we have not found a free provider that produces "
                    "results we would be happy to ship.\n\n"
                    f"Image **generation** is still free and unlimited-ish — try "
                    f"`{ctx.prefix}imagine <prompt>`.\n\n"
                    "If you know a provider worth trying (a generous free tier or "
                    "something we could self-host), join the support server and leave "
                    "a suggestion. We would genuinely like to bring editing back."
                )
            ),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Suggest a provider",
                    style=discord.ButtonStyle.link,
                    url=links.SUPPORT_SERVER,
                )
            ),
        ))
        await ctx.reply(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(AiImageTools(bot))
