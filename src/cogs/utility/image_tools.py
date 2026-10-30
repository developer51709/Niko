import asyncio
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

from utils.command_locales import command_texts
from utils.i18n import make_flat_msg
from utils.locales import load_locales

CMDS = command_texts(__package__)
MESSAGES = load_locales(__package__, "misc")
tr = make_flat_msg(MESSAGES)

#: Select-menu order. Labels and descriptions are looked up as
#: ``fx_<value>_label`` / ``fx_<value>_desc`` so a translation never has to
#: touch the code.
EFFECT_ORDER = (
    "grayscale",
    "invert",
    "blur",
    "pixelate",
    "deepfry",
    "caption_top",
    "caption_bottom",
    "meme",
    "sepia",
    "vaporwave",
    "glitch",
    "edge_detect",
    "emboss",
    "rotate",
    "mirror",
    "flip",
    "sharpen",
    "posterize",
    "vignette",
    "oil_paint",
)


def build_cv2_container(
    title: str,
    filename: str,
    width: int,
    height: int,
    locale=None,
) -> discord.ui.LayoutView:
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
            content=tr(locale, "img_dimensions", width=width, height=height)
        )
    )

    view.add_item(container)
    return view


class EffectSelect(discord.ui.Select):
    def __init__(self, cog: "ImageTools", message: discord.Message, locale=None):
        self.cog = cog
        self.message = message
        self.locale = locale

        options = [
            discord.SelectOption(
                label=tr(locale, f"fx_{value}_label"),
                value=value,
                description=tr(locale, f"fx_{value}_desc"),
            )
            for value in EFFECT_ORDER
        ]

        super().__init__(
            placeholder=tr(locale, "fx_choose"),
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        effect = self.values[0]

        # Text/modal effects
        if effect in ("caption_top", "caption_bottom"):
            position = "top" if effect == "caption_top" else "bottom"
            return await interaction.response.send_modal(
                CaptionModal(self.cog, self.message, position, interaction)
            )

        if effect == "meme":
            return await interaction.response.send_modal(
                MemeModal(self.cog, self.message, interaction)
            )

        if effect == "rotate":
            return await interaction.response.send_modal(
                RotateModal(self.cog, self.message, interaction)
            )

        # Immediate effects
        raw = await extract_image_from_message(self.message)
        if not raw:
            return await interaction.response.send_message(
                tr(interaction, "img_none"), ephemeral=True
            )

        await interaction.response.defer()

        processors = {
            "grayscale":  (grayscale,       "grayscale.gif"),
            "invert":     (invert_colors,   "invert.gif"),
            "blur":       (blur_image,      "blur.gif"),
            "pixelate":   (pixelate_image,  "pixelate.gif"),
            "deepfry":    (deepfry_image,   "deepfry.gif"),
            "sepia":      (sepia,           "sepia.gif"),
            "vaporwave":  (vaporwave,       "vaporwave.gif"),
            "glitch":     (glitch_effect,   "glitch.gif"),
            "edge_detect":(edge_detect,     "edge_detect.gif"),
            "emboss":     (emboss,          "emboss.gif"),
            "mirror":     (mirror_image,    "mirror.gif"),
            "flip":       (flip_image,      "flip.gif"),
            "sharpen":    (sharpen_image,   "sharpen.gif"),
            "posterize":  (posterize_image, "posterize.gif"),
            "vignette":   (vignette,        "vignette.gif"),
            "oil_paint":  (oil_paint,       "oil_paint.gif"),
        }

        processor, filename = processors[effect]

        # Run heavy image processing in a thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        output = await loop.run_in_executor(None, lambda: process_image_animated(raw, processor))

        img = Image.open(output)
        width, height = img.size
        output.seek(0)

        title = tr(interaction, f"fx_{effect}_label")
        file = discord.File(output, filename=filename)
        view = build_cv2_container(title, filename, width, height, interaction)
        await interaction.followup.send(view=view, file=file, ephemeral=True)


class EffectSelectView(discord.ui.View):
    def __init__(self, cog: "ImageTools", message: discord.Message, locale=None):
        super().__init__(timeout=60)
        self.add_item(EffectSelect(cog, message, locale))


# ──────────────────────── modals ───────────────────

class CaptionModal(discord.ui.Modal):
    def __init__(self, cog: "ImageTools", message: discord.Message, position: str, locale=None):
        super().__init__(title=tr(locale, "img_modal_caption"))
        self.cog = cog
        self.message = message
        self.position = position
        self.locale = locale

        self.caption = discord.ui.TextInput(
            label=tr(locale, "img_modal_caption_label"), max_length=200
        )
        self.add_item(self.caption)

    async def on_submit(self, interaction: discord.Interaction):
        raw = await extract_image_from_message(self.message)
        if not raw:
            return await interaction.response.send_message(
                tr(interaction, "img_none"), ephemeral=True
            )

        text = str(self.caption)

        if self.position == "top":
            processor = lambda r: caption_top(r, text)
            title = tr(self.locale, "img_title_caption", text=text)
            filename = "caption_top.gif"
        else:
            processor = lambda r: caption_bottom(r, text)
            title = tr(self.locale, "img_title_caption_bottom", text=text)
            filename = "caption_bottom.gif"

        await interaction.response.defer()

        # Run heavy image processing in a thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        output = await loop.run_in_executor(None, lambda: process_image_animated(raw, processor))

        img = Image.open(output)
        width, height = img.size
        output.seek(0)

        file = discord.File(output, filename=filename)
        view = build_cv2_container(title, filename, width, height, self.locale)
        await interaction.response.send_message(view=view, file=file, ephemeral=True)


class MemeModal(discord.ui.Modal):
    def __init__(self, cog: "ImageTools", message: discord.Message, locale=None):
        super().__init__(title=tr(locale, "img_modal_meme"))
        self.cog = cog
        self.message = message
        self.locale = locale

        self.top = discord.ui.TextInput(
            label=tr(locale, "img_modal_top"), max_length=120, required=False
        )
        self.bottom = discord.ui.TextInput(
            label=tr(locale, "img_modal_bottom"), max_length=120, required=False
        )

        self.add_item(self.top)
        self.add_item(self.bottom)

    async def on_submit(self, interaction: discord.Interaction):
        raw = await extract_image_from_message(self.message)
        if not raw:
            return await interaction.response.send_message(
                tr(interaction, "img_none"), ephemeral=True
            )

        top_text = str(self.top) or ""
        bottom_text = str(self.bottom) or ""

        processor = lambda r: meme_top_bottom(r, top_text, bottom_text)

        await interaction.response.defer()

        # Run heavy image processing in a thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        output = await loop.run_in_executor(None, lambda: process_image_animated(raw, processor))

        img = Image.open(output)
        width, height = img.size
        output.seek(0)

        filename = "meme.gif"
        file = discord.File(output, filename=filename)
        view = build_cv2_container(
            tr(self.locale, "fx_meme_label"), filename, width, height, self.locale
        )
        await interaction.followup.send(view=view, file=file, ephemeral=True)


class RotateModal(discord.ui.Modal):
    def __init__(self, cog: "ImageTools", message: discord.Message, locale=None):
        super().__init__(title=tr(locale, "img_modal_rotate"))
        self.cog = cog
        self.message = message
        self.locale = locale

        self.angle = discord.ui.TextInput(
            label=tr(locale, "img_modal_angle_label"),
            placeholder=tr(locale, "img_modal_angle_placeholder"),
            max_length=8,
            default="90",
        )
        self.add_item(self.angle)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            angle = float(str(self.angle).strip())
        except ValueError:
            return await interaction.response.send_message(
                tr(interaction, "img_bad_angle"), ephemeral=True
            )

        raw = await extract_image_from_message(self.message)
        if not raw:
            return await interaction.response.send_message(
                tr(interaction, "img_none"), ephemeral=True
            )

        processor = lambda r: rotate_image(r, angle)

        await interaction.response.defer()

        # Run heavy image processing in a thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        output = await loop.run_in_executor(None, lambda: process_image_animated(raw, processor))

        img = Image.open(output)
        width, height = img.size
        output.seek(0)

        filename = "rotated.gif"
        file = discord.File(output, filename=filename)
        view = build_cv2_container(
            tr(self.locale, "img_title_rotate", angle=f"{angle:g}"),
            filename, width, height, self.locale,
        )
        await interaction.followup.send(view=view, file=file, ephemeral=True)


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

    async def _process_and_send_prefix(self, ctx, raw, effect, filename, processor):
        async with ctx.typing():
            # Run heavy image processing in a thread pool to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            output = await loop.run_in_executor(None, lambda: process_image_animated(raw, processor))
            img = Image.open(output)
            width, height = img.size
            output.seek(0)

        file = discord.File(output, filename=filename)
        view = build_cv2_container(
            tr(ctx, f"fx_{effect}_label"), filename, width, height, ctx
        )
        try:
            await ctx.reply(view=view, file=file)
        except Exception:
            await ctx.send(view=view, file=file)

    # ──────────── original prefix commands ─────────

    @commands.command(name="grayscale", help=CMDS.help("grayscale"))
    async def grayscale_prefix(self, ctx):
        source = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(source)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none"))
        await self._process_and_send_prefix(ctx, raw, "grayscale", "grayscale.gif", grayscale)

    @commands.command(name="invert", help=CMDS.help("invert"))
    async def invert_prefix(self, ctx):
        source = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(source)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none"))
        await self._process_and_send_prefix(ctx, raw, "invert", "invert.gif", invert_colors)

    @commands.command(name="blur", help=CMDS.help("blur"))
    async def blur_prefix(self, ctx):
        source = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(source)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none"))
        await self._process_and_send_prefix(ctx, raw, "blur", "blur.gif", blur_image)

    @commands.command(name="pixelate", help=CMDS.help("pixelate"))
    async def pixelate_prefix(self, ctx):
        source = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(source)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none"))
        await self._process_and_send_prefix(ctx, raw, "pixelate", "pixelate.gif", pixelate_image)

    @commands.command(name="deepfry", help=CMDS.help("deepfry"))
    async def deepfry_prefix(self, ctx):
        source = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(source)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none"))
        await self._process_and_send_prefix(ctx, raw, "deepfry", "deepfry.gif", deepfry_image)

    @commands.command(name="caption", help=CMDS.help("caption"))
    async def caption_prefix(self, ctx: commands.Context, *, text: str):
        message = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(message)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none_in_message"))
        processor = lambda r: caption_top(r, text)
        async with ctx.typing():
            loop = asyncio.get_event_loop()
            output = await loop.run_in_executor(None, lambda: process_image_animated(raw, processor))
            img = Image.open(output)
            width, height = img.size
            output.seek(0)
        file = discord.File(output, filename="caption_top.gif")
        view = build_cv2_container(
            tr(ctx, "img_title_caption", text=text), "caption_top.gif", width, height, ctx
        )
        try:
            await ctx.reply(view=view, file=file)
        except Exception:
            await ctx.send(view=view, file=file)

    @commands.command(name="captionbottom", help=CMDS.help("captionbottom"))
    async def caption_bottom_prefix(self, ctx: commands.Context, *, text: str):
        message = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(message)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none_in_message"))
        processor = lambda r: caption_bottom(r, text)
        async with ctx.typing():
            loop = asyncio.get_event_loop()
            output = await loop.run_in_executor(None, lambda: process_image_animated(raw, processor))
            img = Image.open(output)
            width, height = img.size
            output.seek(0)
        file = discord.File(output, filename="caption_bottom.gif")
        view = build_cv2_container(
            tr(ctx, "img_title_caption_bottom", text=text),
            "caption_bottom.gif", width, height, ctx,
        )
        try:
            await ctx.reply(view=view, file=file)
        except Exception:
            await ctx.send(view=view, file=file)

    # ──────────── new prefix commands ────────────

    @commands.command(name="sepia", help=CMDS.help("sepia"))
    async def sepia_prefix(self, ctx):
        source = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(source)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none"))
        await self._process_and_send_prefix(ctx, raw, "sepia", "sepia.gif", sepia)

    @commands.command(name="vaporwave", help=CMDS.help("vaporwave"))
    async def vaporwave_prefix(self, ctx):
        source = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(source)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none"))
        await self._process_and_send_prefix(ctx, raw, "vaporwave", "vaporwave.gif", vaporwave)

    @commands.command(name="glitch", help=CMDS.help("glitch"))
    async def glitch_prefix(self, ctx):
        source = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(source)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none"))
        await self._process_and_send_prefix(ctx, raw, "glitch", "glitch.gif", glitch_effect)

    @commands.command(name="edge", help=CMDS.help("edge"))
    async def edge_prefix(self, ctx):
        source = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(source)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none"))
        await self._process_and_send_prefix(ctx, raw, "edge_detect", "edge_detect.gif", edge_detect)

    @commands.command(name="emboss", help=CMDS.help("emboss"))
    async def emboss_prefix(self, ctx):
        source = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(source)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none"))
        await self._process_and_send_prefix(ctx, raw, "emboss", "emboss.gif", emboss)

    @commands.command(name="rotate", help=CMDS.help("rotate"))
    async def rotate_prefix(self, ctx, angle: float = 90.0):
        source = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(source)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none"))
        processor = lambda r: rotate_image(r, angle)
        async with ctx.typing():
            loop = asyncio.get_event_loop()
            output = await loop.run_in_executor(None, lambda: process_image_animated(raw, processor))
            img = Image.open(output)
            width, height = img.size
            output.seek(0)
        file = discord.File(output, filename="rotated.gif")
        view = build_cv2_container(
            tr(ctx, "img_title_rotate", angle=f"{angle:g}"),
            "rotated.gif", width, height, ctx,
        )
        try:
            await ctx.reply(view=view, file=file)
        except Exception:
            await ctx.send(view=view, file=file)

    @commands.command(name="mirror", help=CMDS.help("mirror"),
    )
    async def mirror_prefix(self, ctx):
        source = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(source)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none"))
        await self._process_and_send_prefix(ctx, raw, "mirror", "mirror.gif", mirror_image)

    @commands.command(name="flip", help=CMDS.help("flip"),
    )
    async def flip_prefix(self, ctx):
        source = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(source)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none"))
        await self._process_and_send_prefix(ctx, raw, "flip", "flip.gif", flip_image)

    @commands.command(name="sharpen", help=CMDS.help("sharpen"))
    async def sharpen_prefix(self, ctx):
        source = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(source)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none"))
        await self._process_and_send_prefix(ctx, raw, "sharpen", "sharpen.gif", sharpen_image)

    @commands.command(name="posterize", help=CMDS.help("posterize"))
    async def posterize_prefix(self, ctx):
        source = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(source)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none"))
        await self._process_and_send_prefix(ctx, raw, "posterize", "posterize.gif", posterize_image)

    @commands.command(name="vignette", help=CMDS.help("vignette"))
    async def vignette_prefix(self, ctx):
        source = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(source)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none"))
        await self._process_and_send_prefix(ctx, raw, "vignette", "vignette.gif", vignette)

    @commands.command(name="oilpaint", aliases=["oil"], help=CMDS.help("oilpaint"))
    async def oilpaint_prefix(self, ctx):
        source = await self._get_target_message_from_ctx(ctx)
        raw = await extract_image_from_message(source)
        if not raw:
            return await ctx.reply(tr(ctx, "img_none"))
        await self._process_and_send_prefix(ctx, raw, "oil_paint", "oil_paint.gif", oil_paint)

    # ──────────── context menu ────────────

    async def edit_image_context(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.send_message(
            tr(interaction, "fx_choose_prompt"),
            view=EffectSelectView(self, message, interaction),
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ImageTools(bot))
