import discord
from discord.ext import commands
from discord import app_commands
from io import BytesIO
from PIL import Image

from utils.image.extractor import extract_image_from_message
from utils.image.pil_tools import (
    grayscale,
    invert_colors,
    blur_image,
    pixelate_image,
    deepfry_image,
    caption_top,
    caption_bottom,
    meme_top_bottom,
    process_image_animated,
)


def build_cv2_container(title: str, filename: str, width: int, height: int) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()

    container = discord.ui.Container(
        discord.ui.TextDisplay(
            content=f"### {title}"
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.MediaGallery(
            discord.MediaGalleryItem(media=f"attachment://{filename}")
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=f"-# {width}×{height}"
        )
    )

    view.add_item(container)
    return view


class EffectSelect(discord.ui.Select):
    def __init__(self, cog: "ImageTools", message: discord.Message):
        self.cog = cog
        self.message = message

        options = [
            discord.SelectOption(label="Grayscale", value="grayscale", description="Convert the image to grayscale."),
            discord.SelectOption(label="Invert", value="invert", description="Invert the colors of the image."),
            discord.SelectOption(label="Blur", value="blur", description="Apply a soft blur to the image."),
            discord.SelectOption(label="Pixelate", value="pixelate", description="Pixelate the image."),
            discord.SelectOption(label="Deepfry", value="deepfry", description="Over-saturated, noisy deepfry effect."),
            discord.SelectOption(label="Caption (Top)", value="caption_top", description="Add a caption at the top."),
            discord.SelectOption(label="Caption (Bottom)", value="caption_bottom", description="Add a caption at the bottom."),
            discord.SelectOption(label="Meme (Top + Bottom)", value="meme", description="Classic meme text at top and bottom."),
        ]

        super().__init__(
            placeholder="Choose an effect…",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        effect = self.values[0]

        # Text-based effects → open modal
        if effect in ("caption_top", "caption_bottom"):
            position = "top" if effect == "caption_top" else "bottom"
            return await interaction.response.send_modal(CaptionModal(self.cog, self.message, position))

        if effect == "meme":
            return await interaction.response.send_modal(MemeModal(self.cog, self.message))

        # Non-text effects → process immediately
        raw = await extract_image_from_message(self.message)
        if not raw:
            return await interaction.response.send_message("No image found.", ephemeral=True)

        # Map effect → processor
        processors = {
            "grayscale": (grayscale, "Grayscale", "grayscale.gif"),
            "invert": (invert_colors, "Invert", "invert.gif"),
            "blur": (blur_image, "Blur", "blur.gif"),
            "pixelate": (pixelate_image, "Pixelate", "pixelate.gif"),
            "deepfry": (deepfry_image, "Deepfry", "deepfry.gif"),
        }

        processor, title, filename = processors[effect]

        # GIF-aware processing
        output = process_image_animated(raw, processor)

        img = Image.open(output)
        width, height = img.size
        output.seek(0)

        file = discord.File(output, filename=filename)
        view = build_cv2_container(title, filename, width, height)

        await interaction.response.send_message(view=view, file=file, ephemeral=True)


class EffectSelectView(discord.ui.View):
    def __init__(self, cog: "ImageTools", message: discord.Message):
        super().__init__(timeout=60)
        self.add_item(EffectSelect(cog, message))


class CaptionModal(discord.ui.Modal):
    def __init__(self, cog: "ImageTools", message: discord.Message, position: str):
        super().__init__(title="Add Caption")
        self.cog = cog
        self.message = message
        self.position = position

        self.caption = discord.ui.TextInput(label="Caption text", max_length=200)
        self.add_item(self.caption)

    async def on_submit(self, interaction: discord.Interaction):
        raw = await extract_image_from_message(self.message)
        if not raw:
            return await interaction.response.send_message("No image found.", ephemeral=True)

        text = str(self.caption)

        if self.position == "top":
            processor = lambda r: caption_top(r, text)
            title = f"Caption (Top)"
            filename = "caption_top.gif"
        else:
            processor = lambda r: caption_bottom(r, text)
            title = f"Caption (Bottom)"
            filename = "caption_bottom.gif"

        output = process_image_animated(raw, processor)

        img = Image.open(output)
        width, height = img.size
        output.seek(0)

        file = discord.File(output, filename=filename)
        view = build_cv2_container(title, filename, width, height)

        await interaction.response.send_message(view=view, file=file, ephemeral=True)


class MemeModal(discord.ui.Modal):
    def __init__(self, cog: "ImageTools", message: discord.Message):
        super().__init__(title="Meme-ify Image")
        self.cog = cog
        self.message = message

        self.top = discord.ui.TextInput(label="Top text", max_length=120, required=False)
        self.bottom = discord.ui.TextInput(label="Bottom text", max_length=120, required=False)

        self.add_item(self.top)
        self.add_item(self.bottom)

    async def on_submit(self, interaction: discord.Interaction):
        raw = await extract_image_from_message(self.message)
        if not raw:
            return await interaction.response.send_message("No image found.", ephemeral=True)

        top_text = str(self.top) or ""
        bottom_text = str(self.bottom) or ""

        processor = lambda r: meme_top_bottom(r, top_text, bottom_text)
        output = process_image_animated(raw, processor)

        img = Image.open(output)
        width, height = img.size
        output.seek(0)

        filename = "meme.gif"
        file = discord.File(output, filename=filename)
        view = build_cv2_container("Meme", filename, width, height)

        await interaction.response.send_message(view=view, file=file, ephemeral=True)


class ImageTools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.ctx_edit = app_commands.ContextMenu(
            name="Edit Image",
            callback=self.edit_image_context,
        )
        bot.tree.add_command(self.ctx_edit)

    async def cog_unload(self):
        self.bot.tree.remove_command(self.ctx_edit.name, type=self.ctx_edit.type)

    async def _get_target_message_from_ctx(self, ctx: commands.Context):
        if ctx.message.reference:
            return await ctx.channel.fetch_message(ctx.message.reference.message_id)
        return ctx.message

    async def _process_and_send_prefix(self, ctx, raw, effect_name, filename, processor):
        output = process_image_animated(raw, processor)
        img = Image.open(output)
        width, height = img.size
        output.seek(0)

        file = discord.File(output, filename=filename)
        view = build_cv2_container(effect_name, filename, width, height)
        await ctx.send(view=view, file=file)

    # ---------- prefix commands ----------

    @commands.command(
        name="grayscale",
        help="Convert an image to grayscale."
    )
    async def grayscale_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Grayscale", "grayscale.gif", grayscale)

    @commands.command(
        name="invert",
        help="Invert the colors of an image."
    )
    async def invert_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Invert", "invert.gif", invert_colors)

    @commands.command(
        name="blur",
        help="Apply a soft blur to an image."
    )
    async def blur_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Blur", "blur.gif", blur_image)

    @commands.command(
        name="pixelate",
        help="Pixelate an image for a retro/blocky look."
    )
    async def pixelate_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Pixelate", "pixelate.gif", pixelate_image)

    @commands.command(
        name="deepfry",
        help="Deepfry an image with heavy saturation, contrast, and noise."
    )
    async def deepfry_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Deepfry", "deepfry.gif", deepfry_image)

    @commands.command(
        name="caption",
        help="Add a caption to the top of an image."
    )
    async def caption_prefix(self, ctx: commands.Context, *, text: str):
        message = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(message)
        if not raw:
            return await ctx.reply("No image found in that message.")

        processor = lambda r: caption_top(r, text)
        await self._process_and_send_prefix(ctx, raw, f"Caption (Top): {text}", "caption_top.gif", processor)

    @commands.command(
        name="captionbottom",
        help="Add a caption to the bottom of an image."
    )
    async def caption_bottom_prefix(self, ctx: commands.Context, *, text: str):
        message = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(message)
        if not raw:
            return await ctx.reply("No image found in that message.")

        processor = lambda r: caption_bottom(r, text)
        await self._process_and_send_prefix(ctx, raw, f"Caption (Bottom): {text}", "caption_bottom.gif", processor)

    # ---------- context menu ----------

    async def edit_image_context(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.send_message(
            "Choose an effect:",
            view=EffectSelectView(self, message),
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ImageTools(bot))