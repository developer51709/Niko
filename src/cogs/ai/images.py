import discord
from discord.ext import commands
import aiohttp
import os
import io
import json
import base64
import asyncio
import random
from urllib.parse import urlparse
from utils import logging
from utils.image.extractor import extract_image_from_message
from config.emojis import get_emoji

HF_API_KEY        = os.environ.get("HUGGINGFACE_API_KEY", "")
FAL_API_KEY       = os.environ.get("FAL_API_KEY", "")
EDIT_MODELS = [
    # black-forest-labs/FLUX.2-klein-9B
    "https://router.huggingface.co/fal-ai/fal-ai/flux-2/klein/9b/edit?_subdomain=queue",
    "https://router.huggingface.co/replicate/v1/models/black-forest-labs/flux-2-klein-9b/predictions",
    # Qwen/Qwen-Image-Edit
    "https://router.huggingface.co/fal-ai/fal-ai/qwen-image-edit?_subdomain=queue",
    "https://router.huggingface.co/wavespeed/api/v3/wavespeed-ai/qwen-image/edit",
    "https://router.huggingface.co/replicate/v1/models/qwen/qwen-image-edit/predictions",
]

from utils.premium_manager import PremiumManager


class AiImageTools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        await self.session.close()

    # ── API methods ───────────────────────────────

    async def GenerateImage(self, prompt: str) -> tuple[io.BytesIO, None] | tuple[None, str]:
        async with aiohttp.ClientSession() as session:
            while True:
                seed = random.randint(1, 100000)
                image_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}"
                async with session.get(image_url) as response:
                    image_data = await response.read()
                    return io.BytesIO(image_data), None

    async def EditImage(self, image_bytes: bytes, prompt: str) -> tuple[io.BytesIO, None] | tuple[None, str]:
        """
        Edit an image via image-to-image models.
        """
        return None, "This feature has been temporarily removed until a reliable long term fix can be implemented."
        if not HF_API_KEY:
            return None, "No `HUGGINGFACE_API_KEY` is configured. Ask a bot owner to add it."

        mime = self._detect_mime(image_bytes)
        b64_image = await asyncio.to_thread(lambda: base64.b64encode(image_bytes).decode())
        data_uri = f"data:{mime};base64,{b64_image}"

        errors = {}
        for model in EDIT_MODELS:
            url = f"{model}"
            # fal-ai FLUX.2 [klein] edit models expect a flat payload (not the
            # generic HF "inputs"/"parameters" envelope): top-level "prompt"
            # (required) and "image_urls" (required list, URL or data URI).
            payload = {
                "prompt": prompt,
                "image_urls": [data_uri],
                "num_inference_steps": 4,
            }
            try:
                async with self.session.post(url, headers=self._hf_headers(), json=payload) as resp:
                    raw = await resp.read()
                    content_type = resp.content_type or ""
                    logging.debug("AiImageTools", f"[edit-debug] submit POST {url} payload={payload} -> status={resp.status} content_type={content_type} body={raw.decode(errors='replace')[:500]}")
                    if resp.ok:
                        if "json" in content_type:
                            try:
                                data = json.loads(raw)
                            except Exception:
                                data = {}

                            response_url = data.get("response_url") or data.get("responseUrl")
                            if response_url:
                                if status_message:
                                    await self._update_queue_message(
                                        status_message,
                                        prompt,
                                        "Queued",
                                        request_id=data.get("request_id") or data.get("requestId"),
                                        position=data.get("queue_position") or data.get("position"),
                                        detail=data.get("message") or data.get("estimated_time"),
                                    )
                                return await self._poll_hf_queue(url, data, prompt, status_message)

                        image = await self._parse_hf_image_response(raw, content_type)
                        if image:
                            return image, None
                    errors[model] = f"{resp.status}: {raw.decode(errors='replace')[:120]}"
            except Exception as e:
                errors[model] = str(e)

        lines = "\n".join(f"- `{m}`: `{e}`" for m, e in errors.items())
        return None, f"All edit models failed.\n{lines}"

    # ── CV2 response builder ──────────────────────

    def build_cv2_container(self, title: str, message: str, file: discord.File):
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {title}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )
        if message:
            container.add_item(discord.ui.TextDisplay(content=message))
        container.add_item(discord.ui.MediaGallery(discord.MediaGalleryItem(media=file)))
        view.add_item(container)
        return view

    def _error_view(self, detail: str) -> discord.ui.LayoutView:
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_danger')} Generation Failed"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=detail),
            accent_colour=discord.Color.red(),
        )
        view.add_item(container)
        return view

    # ── Premium check ─────────────────────────────

    def check_premium(self, member: discord.Member) -> bool:
        return PremiumManager.is_premium(member.id)

    def _premium_required_view(self, detail: str) -> discord.ui.LayoutView:
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_danger')} Premium Required"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=detail),
        )
        view.add_item(container)
        return view

    # ── Commands ──────────────────────────────────

    @commands.command(
        name="generate",
        help="Generate an image using AI.",
        aliases=["imagen", "imagine"],
    )
    async def generate(self, ctx: commands.Context, *, prompt: str):
        if not self.check_premium(ctx.author):
            return await ctx.send(view=self._premium_required_view(
                "Due to the cost of AI image generation, this command is only available to premium users.\n\n"
                "You can get premium by joining the support server and boosting."
            ))

        async with ctx.typing():
            image, err = await self.GenerateImage(prompt)

        if err:
            try:
                return await ctx.reply(view=self._error_view(err))
            except Exception:
                return await ctx.send(view=self._error_view(err))

        file = discord.File(image, filename="generated_image.png")
        view = self.build_cv2_container(
            f"{get_emoji('icon_image')} Generated Image",
            f"-# Prompt: *{prompt[:200]}*",
            file,
        )
        image.seek(0)
        file2 = discord.File(image, filename="generated_image.png")
        try:
            await ctx.reply(view=view, file=file2)
        except Exception:
            await ctx.send(view=view, file=file2)

    @commands.command(
        name="edit",
        help="Edit an image using AI. Attach an image or reply to one.",
        aliases=["aiedit", "editimage"],
    )
    async def edit(self, ctx: commands.Context, *, prompt: str):
        if not self.check_premium(ctx.author):
            return await ctx.send(view=self._premium_required_view(
                "AI image editing is a premium-only feature.\n\n"
                "Join the support server and boost to unlock it."
            ))

        image_bytes = await extract_image_from_message(ctx.message)
        if image_bytes is None:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=f"### {get_emoji('icon_danger')} No Image Found"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content="Please attach an image or reply to one so I can edit it."),
            )
            view.add_item(container)
            return await ctx.send(view=view)

        raw_bytes = image_bytes.getvalue()

        async with ctx.typing():
            result, err = await self.EditImage(raw_bytes, prompt)

        if err:
            try:
                return await ctx.reply(view=self._error_view(err))
            except Exception:
                return await ctx.send(view=self._error_view(err))

        result.seek(0)
        file = discord.File(result, filename="edited_image.png")
        view = self.build_cv2_container(
            f"{get_emoji('icon_image')} Edited Image",
            f"-# Prompt: *{prompt[:200]}*",
            file,
        )
        file2 = discord.File(result, filename="edited_image.png")
        try:
            await status_message.edit(view=view, attachments=[file2])
        except Exception:
            try:
                await ctx.reply(view=view, file=file2)
            except Exception:
                await ctx.send(view=view, file=file2)


async def setup(bot: commands.Bot):
    await bot.add_cog(AiImageTools(bot))
