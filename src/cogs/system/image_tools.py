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
    sepia,
    vaporwave,
    glitch_effect,
    edge_detect,
    emboss,
    rotate_image,
    mirror_image,
    flip_image,
    sharpen_image,
    posterize_image,
    vignette,
    oil_paint,
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
            # ── original ──
            discord.SelectOption(label="Grayscale",         value="grayscale",      description="Convert to grayscale."),
            discord.SelectOption(label="Invert",            value="invert",         description="Invert all colours."),
            discord.SelectOption(label="Blur",              value="blur",           description="Soft Gaussian blur."),
            discord.SelectOption(label="Pixelate",          value="pixelate",       description="Retro blocky pixelation."),
            discord.SelectOption(label="Deepfry",           value="deepfry",        description="Over-saturated deepfry effect."),
            discord.SelectOption(label="Caption (Top)",     value="caption_top",    description="Add a caption at the top."),
            discord.SelectOption(label="Caption (Bottom)",  value="caption_bottom", description="Add a caption at the bottom."),
            discord.SelectOption(label="Meme (Top+Bottom)", value="meme",           description="Classic impact-font meme text."),
            # ── new ──
            discord.SelectOption(label="Sepia",             value="sepia",          description="Classic warm sepia tone."),
            discord.SelectOption(label="Vaporwave",         value="vaporwave",      description="Pink/purple retro palette."),
            discord.SelectOption(label="Glitch",            value="glitch",         description="RGB channel shift + corruption."),
            discord.SelectOption(label="Edge Detect",       value="edge_detect",    description="Highlight image edges."),
            discord.SelectOption(label="Emboss",            value="emboss",         description="Raised-relief 3-D effect."),
            discord.SelectOption(label="Rotate",            value="rotate",         description="Rotate by a custom angle."),
            discord.SelectOption(label="Mirror",            value="mirror",         description="Flip horizontally (left ↔ right)."),
            discord.SelectOption(label="Flip",              value="flip",           description="Flip vertically (top ↔ bottom)."),
            discord.SelectOption(label="Sharpen",           value="sharpen",        description="Aggressive unsharp-mask sharpening."),
            discord.SelectOption(label="Posterize",         value="posterize",      description="Flat, poster-art colour reduction."),
            discord.SelectOption(label="Vignette",          value="vignette",       description="Dark feathered edges."),
            discord.SelectOption(label="Oil Paint",         value="oil_paint",      description="Simulate an oil painting."),
        ]

        super().__init__(
            placeholder="Choose an effect…",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        effect = self.values[0]

        # Text/modal effects
        if effect in ("caption_top", "caption_bottom"):
            position = "top" if effect == "caption_top" else "bottom"
            return await interaction.response.send_modal(CaptionModal(self.cog, self.message, position))

        if effect == "meme":
            return await interaction.response.send_modal(MemeModal(self.cog, self.message))

        if effect == "rotate":
            return await interaction.response.send_modal(RotateModal(self.cog, self.message))

        # Immediate effects
        raw = await extract_image_from_message(self.message)
        if not raw:
            return await interaction.response.send_message("No image found.", ephemeral=True)

        processors = {
            "grayscale":  (grayscale,       "Grayscale",   "grayscale.gif"),
            "invert":     (invert_colors,   "Invert",      "invert.gif"),
            "blur":       (blur_image,      "Blur",        "blur.gif"),
            "pixelate":   (pixelate_image,  "Pixelate",    "pixelate.gif"),
            "deepfry":    (deepfry_image,   "Deepfry",     "deepfry.gif"),
            "sepia":      (sepia,           "Sepia",       "sepia.gif"),
            "vaporwave":  (vaporwave,       "Vaporwave",   "vaporwave.gif"),
            "glitch":     (glitch_effect,   "Glitch",      "glitch.gif"),
            "edge_detect":(edge_detect,     "Edge Detect", "edge_detect.gif"),
            "emboss":     (emboss,          "Emboss",      "emboss.gif"),
            "mirror":     (mirror_image,    "Mirror",      "mirror.gif"),
            "flip":       (flip_image,      "Flip",        "flip.gif"),
            "sharpen":    (sharpen_image,   "Sharpen",     "sharpen.gif"),
            "posterize":  (posterize_image, "Posterize",   "posterize.gif"),
            "vignette":   (vignette,        "Vignette",    "vignette.gif"),
            "oil_paint":  (oil_paint,       "Oil Paint",   "oil_paint.gif"),
        }

        processor, title, filename = processors[effect]
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


# ──────────────────────── modals ───────────────────

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
            title = "Caption (Top)"
            filename = "caption_top.gif"
        else:
            processor = lambda r: caption_bottom(r, text)
            title = "Caption (Bottom)"
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


class RotateModal(discord.ui.Modal):
    def __init__(self, cog: "ImageTools", message: discord.Message):
        super().__init__(title="Rotate Image")
        self.cog = cog
        self.message = message

        self.angle = discord.ui.TextInput(
            label="Angle (degrees, clockwise)",
            placeholder="e.g. 90, 180, 45, -30",
            max_length=8,
            default="90",
        )
        self.add_item(self.angle)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            angle = float(str(self.angle).strip())
        except ValueError:
            return await interaction.response.send_message("Invalid angle — enter a number like 90 or -45.", ephemeral=True)

        raw = await extract_image_from_message(self.message)
        if not raw:
            return await interaction.response.send_message("No image found.", ephemeral=True)

        processor = lambda r: rotate_image(r, angle)
        output = process_image_animated(raw, processor)

        img = Image.open(output)
        width, height = img.size
        output.seek(0)

        filename = "rotated.gif"
        file = discord.File(output, filename=filename)
        view = build_cv2_container(f"Rotate ({angle:g}°)", filename, width, height)
        await interaction.response.send_message(view=view, file=file, ephemeral=True)


# ──────────────────────── cog ──────────────────────

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
        async with ctx.typing():
            output = process_image_animated(raw, processor)
            img = Image.open(output)
            width, height = img.size
            output.seek(0)

        file = discord.File(output, filename=filename)
        view = build_cv2_container(effect_name, filename, width, height)
        try:
            await ctx.reply(view=view, file=file)
        except Exception as e:
            await ctx.send(view=view, file=file)

    # ──────────── original prefix commands ─────────

    @commands.command(name="grayscale", help="Convert an image to grayscale.")
    async def grayscale_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Grayscale", "grayscale.gif", grayscale)

    @commands.command(name="invert", help="Invert the colours of an image.")
    async def invert_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Invert", "invert.gif", invert_colors)

    @commands.command(name="blur", help="Apply a soft Gaussian blur to an image.")
    async def blur_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Blur", "blur.gif", blur_image)

    @commands.command(name="pixelate", help="Pixelate an image for a retro/blocky look.")
    async def pixelate_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Pixelate", "pixelate.gif", pixelate_image)

    @commands.command(name="deepfry", help="Deepfry an image with heavy saturation and noise.")
    async def deepfry_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Deepfry", "deepfry.gif", deepfry_image)

    @commands.command(name="caption", help="Add a caption to the top of an image.")
    async def caption_prefix(self, ctx: commands.Context, *, text: str):
        message = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(message)
        if not raw:
            return await ctx.reply("No image found in that message.")
        processor = lambda r: caption_top(r, text)
        await self._process_and_send_prefix(ctx, raw, f"Caption (Top): {text}", "caption_top.gif", processor)

    @commands.command(name="captionbottom", help="Add a caption to the bottom of an image.")
    async def caption_bottom_prefix(self, ctx: commands.Context, *, text: str):
        message = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(message)
        if not raw:
            return await ctx.reply("No image found in that message.")
        processor = lambda r: caption_bottom(r, text)
        await self._process_and_send_prefix(ctx, raw, f"Caption (Bottom): {text}", "caption_bottom.gif", processor)

    # ──────────── new prefix commands ────────────

    @commands.command(name="sepia", help="Apply a classic warm sepia tone to an image.")
    async def sepia_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Sepia", "sepia.gif", sepia)

    @commands.command(name="vaporwave", help="Apply a pink/purple vaporwave palette to an image.")
    async def vaporwave_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Vaporwave", "vaporwave.gif", vaporwave)

    @commands.command(name="glitch", help="Apply an RGB glitch/corruption effect to an image.")
    async def glitch_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Glitch", "glitch.gif", glitch_effect)

    @commands.command(name="edge", help="Detect and highlight edges in an image.")
    async def edge_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Edge Detect", "edge_detect.gif", edge_detect)

    @commands.command(name="emboss", help="Apply a 3D raised-relief emboss effect to an image.")
    async def emboss_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Emboss", "emboss.gif", emboss)

    @commands.command(name="rotate", help="Rotate an image clockwise by a given angle. Usage: !rotate <angle>")
    async def rotate_prefix(self, ctx, angle: float = 90.0):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        processor = lambda r: rotate_image(r, angle)
        await self._process_and_send_prefix(ctx, raw, f"Rotate ({angle:g}°)", "rotated.gif", processor)

    @commands.command(name="mirror", help="Flip an image horizontally (left ↔ right).")
    async def mirror_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Mirror", "mirror.gif", mirror_image)

    @commands.command(name="flip", help="Flip an image vertically (top ↔ bottom).")
    async def flip_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Flip", "flip.gif", flip_image)

    @commands.command(name="sharpen", help="Apply aggressive unsharp-mask sharpening to an image.")
    async def sharpen_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Sharpen", "sharpen.gif", sharpen_image)

    @commands.command(name="posterize", help="Reduce colour depth for a flat poster-art look.")
    async def posterize_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Posterize", "posterize.gif", posterize_image)

    @commands.command(name="vignette", help="Add a dark feathered vignette around the edges of an image.")
    async def vignette_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Vignette", "vignette.gif", vignette)

    @commands.command(name="oilpaint", aliases=["oil"], help="Simulate an oil painting effect.")
    async def oilpaint_prefix(self, ctx):
        msg = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(msg)
        if not raw:
            return await ctx.reply("No image found.")
        await self._process_and_send_prefix(ctx, raw, "Oil Paint", "oil_paint.gif", oil_paint)

    # ──────────── context menu ────────────

    async def edit_image_context(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.send_message(
            "Choose an effect:",
            view=EffectSelectView(self, message),
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ImageTools(bot))
