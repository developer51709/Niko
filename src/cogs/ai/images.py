import discord
from discord.ext import commands
import aiohttp
import os
import io
import json
import base64
import asyncio
from utils import logging
from utils.image.extractor import extract_image_from_message
from config.emojis import get_emoji

HF_API_KEY       = os.environ.get("HUGGINGFACE_API_KEY", "")
FAL_API_KEY      = os.environ.get("FAL_API_KEY", "")
HF_INFERENCE_BASE = "https://router.huggingface.co/hf-inference/models"
FLUX_MODEL        = "black-forest-labs/FLUX.1-schnell"
EDIT_MODELS = [
    "https://router.huggingface.co/fal-ai/fal-ai/flux-2/klein/9b/edit?_subdomain=queue",
]

from utils.premium_manager import PremiumManager


class AiImageTools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        await self.session.close()

    # ── Helpers ───────────────────────────────────

    def _hf_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {HF_API_KEY}",
            "Content-Type": "application/json",
        }

    def _fal_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {FAL_API_KEY}",
            "Content-Type": "application/json",
        }

    async def _decode_b64(self, b64_data: str) -> io.BytesIO:
        return await asyncio.to_thread(lambda: io.BytesIO(base64.b64decode(b64_data)))

    def _raw_to_bytesio(self, raw: bytes) -> io.BytesIO:
        buf = io.BytesIO(raw)
        buf.seek(0)
        return buf

    async def _parse_hf_image_response(self, raw: bytes, content_type: str) -> io.BytesIO | None:
        """
        HuggingFace hf-inference endpoints can return either raw image bytes
        (content-type: image/*) or a JSON envelope.  Handle both.
        """
        if raw and "image" in content_type and len(raw) > 500:
            return self._raw_to_bytesio(raw)

        if raw and "json" in content_type:
            try:
                data = json.loads(raw)
                # [{…}] list form
                if isinstance(data, list) and data:
                    item = data[0]
                    if isinstance(item, dict):
                        for key in ("image", "generated_image", "b64_json"):
                            if key in item:
                                return await self._decode_b64(item[key])
                # {…} dict form
                if isinstance(data, dict):
                    for key in ("image", "generated_image", "b64_json"):
                        if key in data:
                            return await self._decode_b64(data[key])
            except Exception:
                pass

        # Content-type header may be wrong; trust size as last resort
        if raw and len(raw) > 5_000:
            return self._raw_to_bytesio(raw)

        return None

    # ── API methods ───────────────────────────────

    async def GenerateImage(self, prompt: str) -> tuple[io.BytesIO, None] | tuple[None, str]:
        """
        Generate an image via FLUX.1-schnell using the HuggingFace Inference API.
        Returns (BytesIO, None) on success or (None, error_str) on failure.
        """
        if not HF_API_KEY:
            return None, "No `HUGGINGFACE_API_KEY` is configured. Ask a bot owner to add it."

        url = f"{HF_INFERENCE_BASE}/{FLUX_MODEL}"
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 4,
                "width": 1024,
                "height": 1024,
            },
        }
        try:
            async with self.session.post(url, headers=self._hf_headers(), json=payload) as resp:
                raw          = await resp.read()
                content_type = resp.content_type or ""

                if not resp.ok:
                    return None, f"HuggingFace error {resp.status}: {raw.decode(errors='replace')[:200]}"

                image = await self._parse_hf_image_response(raw, content_type)
                if not image:
                    return None, "No image data in HuggingFace response."
                return image, None

        except Exception as e:
            return None, str(e)

    async def _update_queue_message(self, status_message: discord.Message, prompt: str, status: str, request_id: str | None = None, position: int | None = None, detail: str | None = None):
        try:
            await status_message.edit(view=self._queue_view(prompt, status, request_id=request_id, position=position, detail=detail))
        except Exception:
            pass

    def _queue_view(self, prompt: str, status: str, request_id: str | None = None, position: int | None = None, detail: str | None = None) -> discord.ui.LayoutView:
        lines = [
            f"### {get_emoji('icon_loading')} AI Image Edit",
            f"-# Status: **{status}**",
        ]
        if prompt:
            lines.append(f"-# Prompt: *{prompt[:200]}*")
        if position is not None:
            lines.append(f"-# Queue position: **{position}**")
        if request_id:
            lines.append(f"-# Request ID: `{request_id}`")
        if detail:
            lines.append(f"-# {detail}")

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content="\n".join(lines)),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )
        view.add_item(container)
        return view

    async def _poll_hf_queue(self, response_url: str, prompt: str, status_message: discord.Message | None) -> tuple[io.BytesIO, None] | tuple[None, str]:
        max_attempts = 24
        backoff = 1.5
        last_position = None
        last_status = None

        for attempt in range(max_attempts):
            try:
                # Try without auth first (response_url may be pre-signed)
                headers = {"Content-Type": "application/json"}
                async with self.session.get(response_url, headers=headers) as resp:
                    raw = await resp.read()
                    content_type = resp.content_type or ""

                    if resp.status in {401, 403}:
                        # Try Hugging Face token first.
                        async with self.session.get(response_url, headers=self._hf_headers()) as hf_resp:
                            raw = await hf_resp.read()
                            content_type = hf_resp.content_type or ""
                            resp = hf_resp

                        if not resp.ok and FAL_API_KEY:
                            # Fallback to FAL API key if the Hugging Face token is rejected.
                            async with self.session.get(response_url, headers=self._fal_headers()) as fal_resp:
                                raw = await fal_resp.read()
                                content_type = fal_resp.content_type or ""
                                resp = fal_resp

                    if resp.ok:
                        if "json" in content_type:
                            try:
                                data = json.loads(raw)
                            except Exception:
                                data = {}

                            status = str(data.get("status", "")).upper()
                            request_id = data.get("request_id") or data.get("requestId")
                            position = data.get("queue_position") or data.get("position")
                            detail = None
                            if data.get("estimated_time"):
                                detail = f"Estimated wait: {data.get('estimated_time')}"
                            elif data.get("message"):
                                detail = data.get("message")

                            if status == "IN_QUEUE":
                                if status_message:
                                    if status != last_status or position != last_position:
                                        await self._update_queue_message(
                                            status_message,
                                            prompt,
                                            "Queued",
                                            request_id=request_id,
                                            position=position,
                                            detail=detail,
                                        )
                                        last_status = status
                                        last_position = position
                                await asyncio.sleep(backoff)
                                backoff = min(8, backoff + 0.5)
                                continue

                            if status in {"COMPLETED", "SUCCEEDED", "SUCCESS", "DONE"}:
                                image = await self._parse_hf_image_response(raw, content_type)
                                if image:
                                    return image, None
                                return None, "HuggingFace queue finished but did not return a valid image."

                            if any(k in data for k in ("image", "generated_image", "b64_json")):
                                image = await self._parse_hf_image_response(raw, content_type)
                                if image:
                                    return image, None

                            if status == "FAILED":
                                error_text = data.get("error") or data.get("detail") or "The queued request failed."
                                return None, f"HuggingFace queue error: {error_text}"

                            # Still waiting on an unknown JSON response.
                            await asyncio.sleep(backoff)
                            backoff = min(8, backoff + 0.5)
                            continue

                        image = await self._parse_hf_image_response(raw, content_type)
                        if image:
                            return image, None
                        return None, "Unexpected HuggingFace queue response."

                    error_text = raw.decode(errors="replace")[:250]
                    return None, f"HuggingFace queue polling error {resp.status}: {error_text}"
            except Exception as e:
                if attempt == max_attempts - 1:
                    return None, str(e)
                await asyncio.sleep(backoff)
                backoff = min(8, backoff + 0.5)

        return None, "Timed out waiting for HuggingFace queue."

    async def EditImage(self, image_bytes: bytes, prompt: str, status_message: discord.Message | None = None) -> tuple[io.BytesIO, None] | tuple[None, str]:
        """
        Edit an image via image-to-image using hf-inference models.
        Tries EDIT_MODELS in order; returns the first successful result.
        Returns (BytesIO, None) on success or (None, error_str) on failure.
        """
        if not HF_API_KEY:
            return None, "No `HUGGINGFACE_API_KEY` is configured. Ask a bot owner to add it."

        b64_image = await asyncio.to_thread(lambda: base64.b64encode(image_bytes).decode())

        errors = {}
        for model in EDIT_MODELS:
            url = f"{model}"
            payload = {
                "inputs": b64_image,
                "parameters": {
                    "prompt": prompt,
                    "strength": 0.75,
                    "num_inference_steps": 20,
                    "guidance_scale": 7.5,
                },
            }
            try:
                async with self.session.post(url, headers=self._hf_headers(), json=payload) as resp:
                    raw = await resp.read()
                    content_type = resp.content_type or ""
                    if resp.ok:
                        if "json" in content_type:
                            try:
                                data = json.loads(raw)
                            except Exception:
                                data = {}

                            response_url = data.get("response_url") or data.get("responseUrl")
                            status = str(data.get("status", "")).upper()
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
                                return await self._poll_hf_queue(response_url, prompt, status_message)

                        image = await self._parse_hf_image_response(raw, content_type)
                        if image:
                            return image, None
                    errors[model] = f"{resp.status}: {raw.decode(errors='replace')[:120]}"
            except Exception as e:
                errors[model] = str(e)

        lines = "\n".join(f"• `{m}`: `{e}`" for m, e in errors.items())
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
        status_view = self._queue_view(prompt, "Submitting request...")
        try:
            status_message = await ctx.reply(view=status_view)
        except Exception:
            status_message = await ctx.send(view=status_view)

        result, err = await self.EditImage(raw_bytes, prompt, status_message=status_message)

        if err:
            try:
                await status_message.edit(view=self._error_view(err))
                return
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
