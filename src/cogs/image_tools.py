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
            await interaction.response.send_modal(CaptionModal(self.cog, self.message, position=position))
            return

        if effect == "meme":
            await interaction.response.send_modal(MemeModal(self.cog, self.message))
            return

        # Non-text effects → process immediately, ephemeral result
        raw = await extract_image_from_message(self.message)
        if not raw:
            return await interaction.response.send_message("No image found in that message.", ephemeral=True)

        if effect == "grayscale":
            processor = grayscale
            title = "Grayscale"
            filename = "grayscale.png"
        elif effect == "invert":
            processor = invert_colors
            title = "Invert"
            filename = "invert.png"
        elif effect == "blur":
            processor = blur_image
            title = "Blur"
            filename = "blur.png"
        elif effect == "pixelate":
            processor = pixelate_image
            title = "Pixelate"
            filename = "pixelate.png"
        elif effect == "deepfry":
            processor = deepfry_image
            title = "Deepfry"
            filename = "deepfry.png"
        else:
            return await interaction.response.send_message("Unknown effect selected.", ephemeral=True)

        output = processor(raw)
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
    def __init__(self, cog: "ImageTools", message: discord.Message, position: str = "top"):
        title = "Add Caption (Top)" if position == "top" else "Add Caption (Bottom)"
        super().__init__(title=title)
        self.cog = cog
        self.message = message
        self.position = position

        self.caption = discord.ui.TextInput(
            label="Caption text",
            max_length=200,
            required=True,
        )
        self.add_item(self.caption)

    async def on_submit(self, interaction: discord.Interaction):
        raw = await extract_image_from_message(self.message)
        if not raw:
            return await interaction.response.send_message("No image found in that message.", ephemeral=True)

        text = str(self.caption)

        if self.position == "top":
            output = caption_top(raw, text)
            title = f"Caption (Top): {text}"
            filename = "caption_top.png"
        else:
            output = caption_bottom(raw, text)
            title = f"Caption (Bottom): {text}"
            filename = "caption_bottom.png"

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

        self.top = discord.ui.TextInput(
            label="Top text",
            max_length=120,
            required=False,
        )
        self.bottom = discord.ui.TextInput(
            label="Bottom text",
            max_length=120,
            required=False,
        )

        self.add_item(self.top)
        self.add_item(self.bottom)

    async def on_submit(self, interaction: discord.Interaction):
        raw = await extract_image_from_message(self.message)
        if not raw:
            return await interaction.response.send_message("No image found in that message.", ephemeral=True)

        top_text = str(self.top) or ""
        bottom_text = str(self.bottom) or ""

        output = meme_top_bottom(raw, top_text, bottom_text)
        img = Image.open(output)
        width, height = img.size
        output.seek(0)

        filename = "meme.png"
        file = discord.File(output, filename=filename)
        view = build_cv2_container("Meme", filename, width, height)

        await interaction.response.send_message(view=view, file=file, ephemeral=True)


class ImageTools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Single message context menu
        self.ctx_edit = app_commands.ContextMenu(
            name="Edit Image",
            callback=self.edit_image_context,
        )
        bot.tree.add_command(self.ctx_edit)

    async def cog_unload(self):
        self.bot.tree.remove_command(self.ctx_edit.name, type=self.ctx_edit.type)

    # ---------- helpers ----------

    async def _get_target_message_from_ctx(self, ctx: commands.Context) -> discord.Message:
        if ctx.message.reference:
            return await ctx.channel.fetch_message(ctx.message.reference.message_id)
        return ctx.message

    async def _process_and_send_prefix(
        self,
        ctx: commands.Context,
        raw: BytesIO,
        effect_name: str,
        filename: str,
        processor,
    ):
        output = processor(raw)
        img = Image.open(output)
        width, height = img.size
        output.seek(0)

        file = discord.File(output, filename=filename)
        view = build_cv2_container(effect_name, filename, width, height)
        await ctx.send(view=view, file=file)

    # ---------- prefix commands (public) ----------

    @commands.command(
        name="grayscale",
        help="Convert an image to grayscale and show it in a CV2 container.",
    )
    async def grayscale_prefix(self, ctx: commands.Context):
        message = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(message)
        if not raw:
            return await ctx.reply("No image found in that message.")
        await self._process_and_send_prefix(ctx, raw, "Grayscale", "grayscale.png", grayscale)

    @commands.command(
        name="invert",
        help="Invert the colors of an image.",
    )
    async def invert_prefix(self, ctx: commands.Context):
        message = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(message)
        if not raw:
            return await ctx.reply("No image found in that message.")
        await self._process_and_send_prefix(ctx, raw, "Invert", "invert.png", invert_colors)

    @commands.command(
        name="blur",
        help="Apply a soft blur to an image.",
    )
    async def blur_prefix(self, ctx: commands.Context):
        message = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(message)
        if not raw:
            return await ctx.reply("No image found in that message.")
        await self._process_and_send_prefix(ctx, raw, "Blur", "blur.png", blur_image)

    @commands.command(
        name="pixelate",
        help="Pixelate an image for a retro/blocky look.",
    )
    async def pixelate_prefix(self, ctx: commands.Context):
        message = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(message)
        if not raw:
            return await ctx.reply("No image found in that message.")
        await self._process_and_send_prefix(ctx, raw, "Pixelate", "pixelate.png", pixelate_image)

    @commands.command(
        name="deepfry",
        help="Deepfry an image with heavy saturation, contrast, and noise.",
    )
    async def deepfry_prefix(self, ctx: commands.Context):
        message = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(message)
        if not raw:
            return await ctx.reply("No image found in that message.")
        await self._process_and_send_prefix(ctx, raw, "Deepfry", "deepfry.png", deepfry_image)

    @commands.command(
        name="caption",
        help="Add a caption to the top of an image. Use by replying to an image message.",
    )
    async def caption_prefix(self, ctx: commands.Context, *, text: str):
        message = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(message)
        if not raw:
            return await ctx.reply("No image found in that message.")

        output = caption_top(raw, text)
        img = Image.open(output)
        width, height = img.size
        output.seek(0)

        filename = "caption_top.png"
        file = discord.File(output, filename=filename)
        view = build_cv2_container(f"Caption (Top): {text}", filename, width, height)
        await ctx.send(view=view, file=file)

    @commands.command(
        name="captionbottom",
        help="Add a caption to the bottom of an image. Use by replying to an image message.",
    )
    async def captionbottom_prefix(self, ctx: commands.Context, *, text: str):
        message = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(message)
        if not raw:
            return await ctx.reply("No image found in that message.")

        output = caption_bottom(raw, text)
        img = Image.open(output)
        width, height = img.size
        output.seek(0)

        filename = "caption_bottom.png"
        file = discord.File(output, filename=filename)
        view = build_cv2_container(f"Caption (Bottom): {text}", filename, width, height)
        await ctx.send(view=view, file=file)

    @commands.command(
        name="memeify",
        help="Create a meme with top and bottom text. Usage: !meme top text | bottom text (reply to an image).",
    )
    async def meme_prefix(self, ctx: commands.Context, *, text: str):
        parts = text.split("|", 1)
        top = parts[0].strip()
        bottom = parts[1].strip() if len(parts) > 1 else ""

        message = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(message)
        if not raw:
            return await ctx.reply("No image found in that message.")

        output = meme_top_bottom(raw, top, bottom)
        img = Image.open(output)
        width, height = img.size
        output.seek(0)

        filename = "meme.png"
        file = discord.File(output, filename=filename)
        view = build_cv2_container("Meme", filename, width, height)
        await ctx.send(view=view, file=file)

    # ---------- context menu (one, with dropdown) ----------

    async def edit_image_context(self, interaction: discord.Interaction, message: discord.Message):
        # Ephemeral dropdown to choose effect
        view = EffectSelectView(self, message)
        await interaction.response.send_message(
            content="Select an effect to apply to this image:",
            view=view,
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ImageTools(bot))