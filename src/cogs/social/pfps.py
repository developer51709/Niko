"""
PFP Cog — finds new profile pictures for users.
────────────────────────────────────────

"""
import discord
from discord.ext import commands
import os
import random
from config.emojis import get_emoji
from cogs.system.error_handler import is_owner
from utils.image.extractor import extract_images_from_message
from utils import logging
from utils.prefix_manager import resolve_prefix

from utils.command_locales import command_texts
from utils.i18n import make_flat_msg
from utils.locales import load_locales

CMDS = command_texts(__package__)
MESSAGES = load_locales(__package__, "pfps")
msg = make_flat_msg(MESSAGES, {
    "cross": get_emoji("cross"),
    "tick": get_emoji("tick"),
    "loading": get_emoji("loading"),
    "image": get_emoji("image"),
})


def _plural(count: int) -> str:
    """English plural suffix; other languages ignore the token."""
    return "" if count == 1 else "s"

PFPS_FOLDER = "src/assets/pfps"

# Supported options, kept in one place so the selectors and the upload
# validation can never disagree.
GENDERS = ("male", "female")
COUPLE_SUBFOLDERS = ("male-male", "male-female", "female-female")


def _image_suffix(data: bytes) -> str | None:
    """Return the file extension for image bytes, or None for other files."""
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return None


def _next_image_number(folder_path: str) -> int:
    numbers = []
    for name in os.listdir(folder_path):
        stem, _ = os.path.splitext(name)
        if stem.isdigit():
            numbers.append(int(stem))
    return max(numbers, default=0) + 1


def save_pfp_images(folder_path: str, images) -> int:
    """Save every image in *images* into *folder_path* and return the count.

    Uploads are numbered after the highest existing file, so a bulk upload can
    never overwrite pictures that are already in the folder.
    """
    saved = 0
    number = 0
    for image in images:
        data = image.read()
        suffix = _image_suffix(data) if data else None
        if suffix is None:
            continue
        if saved == 0:
            # Only create the folder once there is a picture to put in it, so
            # an empty upload cannot add a zero-image color category.
            os.makedirs(folder_path, exist_ok=True)
            number = _next_image_number(folder_path)
        while os.path.exists(os.path.join(folder_path, f"{number}{suffix}")):
            number += 1
        with open(os.path.join(folder_path, f"{number}{suffix}"), "wb") as handle:
            handle.write(data)
        number += 1
        saved += 1
    return saved


# ------------------------------
# Utility Functions
# ------------------------------

async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    """Return the primary prefix for this context, honouring a dynamic prefix."""
    return await resolve_prefix(bot, ctx_or_interaction)


# ------------------------------
# Profile Picture Functions
# ------------------------------
async def get_color_pfp(ctx: commands.Context, color: str):
    """Get a profile picture with the specified color."""
    color_folder_path = f"{PFPS_FOLDER}/colors/{color}"
    # get a random image from the folder
    image = random.choice(os.listdir(color_folder_path))
    return discord.File(f"{color_folder_path}/{image}")

async def get_gender_pfp(ctx: commands.Context, gender: str):
    """Get a profile picture with the specified gender."""
    gender_folder_path = f"{PFPS_FOLDER}/genders/{gender}"
    # get a random image from the folder
    image = random.choice(os.listdir(gender_folder_path))
    return discord.File(f"{gender_folder_path}/{image}")

async def get_couple_pfps(ctx: commands.Context, gender1: str, gender2: str):
    """Get matching profile pictures with the specified genders."""
    gender_folder = f"{PFPS_FOLDER}/couples"
    # get the subfolder that matches the genders (female-male is the same as male-female to avoid duplicates and reduce the number of folders)
    subfolder = f"{gender1}-{gender2}"
    if subfolder not in COUPLE_SUBFOLDERS:
        subfolder = f"{gender2}-{gender1}"
    gender_folder_path = f"{gender_folder}/{subfolder}"
    # get a random image from the folder and its matching partner (both images are in the same folder under the same name but with _1 and _2 at the end)
    image = random.choice(os.listdir(gender_folder_path))
    image1 = f"{gender_folder_path}/{image.split('_')[0]}_1.png"
    image2 = f"{gender_folder_path}/{image.split('_')[0]}_2.png"
    return discord.File(image1), discord.File(image2)
    

# ------------------------------
# Color Profile Picture Views
# ------------------------------
# this function allows for dynamic color lists based on the folders thar exist
def get_color_list():
    color_folder_path = f"{PFPS_FOLDER}/colors"
    # this function returns both the color names and the number of images in each folder
    colors = []
    for color in os.listdir(color_folder_path):
        colors.append((color, len(os.listdir(f"{color_folder_path}/{color}"))))
    return colors

class ColorSelect(discord.ui.Select):
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        options = []
        for color, count in get_color_list():
            options.append(discord.SelectOption(
                label=color.capitalize(),
                value=color,
                description=msg(ctx, "images_count", count=count),
            ))
        super().__init__(
            placeholder=msg(ctx, "select_color"), min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=msg(self.ctx, "not_author")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        color = self.values[0]
        # assign it to a variable in the context
        self.ctx.color = color
        await interaction.response.defer()

class ColorSubmit(discord.ui.Button):
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        super().__init__(label=msg(ctx, "submit"), style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=msg(self.ctx, "not_author")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        # get the color from the context
        if not hasattr(self.ctx, "color"):
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=msg(self.ctx, "select_color_first")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        color = self.ctx.color
        # edit the message to a loading message
        message = interaction.message
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(self.ctx, "finding_color")
            )
        )
        view.add_item(container)
        await message.edit(view=view)
        # get the profile picture
        try:
            pfp = await get_color_pfp(self.ctx, color)
        except Exception as e:
            logging.error("pfps_cog", f"An error occurred while fetching a pfp for color {color}: {e}")
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=msg(self.ctx, "error_color")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await message.edit(view=view)
        # send the profile picture
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(self.ctx, "title_pfp")
            ),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=pfp
                )
            )
        )
        view.add_item(container)
        await message.edit(view=view, attachments=[pfp])

class ColorSelectView(discord.ui.LayoutView):
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        super().__init__()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(self.ctx, "title_pfp")
            ),
            discord.ui.ActionRow(
                ColorSelect(ctx)
            ),
            discord.ui.ActionRow(
                ColorSubmit(ctx)
            )
        )
        self.add_item(container)


# ------------------------------
# Gender Profile Picture Views
# ------------------------------
# folders are static meaning we can hardcode the options and just fetch the images from the existing folders as well as image count
def get_gender_image_counts():
    gender_folder_path = f"{PFPS_FOLDER}/genders"
    counts = []
    for gender in GENDERS:
        counts.append((gender, len(os.listdir(f"{gender_folder_path}/{gender}"))))
    return counts

def _gender_options(ctx) -> list[discord.SelectOption]:
    """The male/female choices of the couple picker, in the guild's language."""
    return [
        discord.SelectOption(label=msg(ctx, "gender_male"), value="male"),
        discord.SelectOption(label=msg(ctx, "gender_female"), value="female"),
    ]


class GenderSelect(discord.ui.Select):
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        options = []
        for gender, count in get_gender_image_counts():
            options.append(discord.SelectOption(
                label=gender.capitalize(),
                value=gender,
                description=msg(ctx, "images_count", count=f"{count:,}"),
            ))
        super().__init__(
            placeholder=msg(ctx, "select_gender"), min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=msg(self.ctx, "not_author")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        gender = self.values[0]
        self.ctx.gender = gender
        await interaction.response.defer()

class GenderSubmit(discord.ui.Button):
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        super().__init__(label=msg(ctx, "submit"), style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=msg(self.ctx, "not_author")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        # get the gender from the context
        gender = self.ctx.gender
        # edit the message to a loading message
        message = interaction.message
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(self.ctx, "finding_gender")
            )
        )
        view.add_item(container)
        await message.edit(view=view)
        # get the profile picture
        pfp = await get_gender_pfp(self.ctx, gender)
        # send the profile picture
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(self.ctx, "title_pfp")
            ),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=pfp
                )
            )
        )
        view.add_item(container)
        await message.edit(view=view, attachments=[pfp])

class GenderSelectView(discord.ui.LayoutView):
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        super().__init__()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(self.ctx, "title_pfp")
            ),
            discord.ui.ActionRow(
                GenderSelect(ctx)
            ),
            discord.ui.ActionRow(
                GenderSubmit(ctx)
            )
        )
        self.add_item(container)


# ------------------------------
# Couple Profile Picture Views
# ------------------------------
class CoupleGenderSelect(discord.ui.Select):
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        options = _gender_options(ctx)
        super().__init__(
            placeholder=msg(ctx, "select_your_gender"), min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=msg(self.ctx, "not_author")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)

        gender = self.values[0]
        # assign it to a variable in the context
        self.ctx.gender1 = gender
        await interaction.response.defer()

class CoupleGenderSelect2(discord.ui.Select):
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        options = _gender_options(ctx)
        super().__init__(
            placeholder=msg(ctx, "select_partner_gender"), min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=msg(self.ctx, "not_author")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        gender = self.values[0]
        self.ctx.gender2 = gender
        await interaction.response.defer()

class CoupleGenderSubmit(discord.ui.Button):
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        super().__init__(label=msg(ctx, "submit"), style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=msg(self.ctx, "not_author")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        # get the gender from the context
        gender1 = self.ctx.gender1
        gender2 = self.ctx.gender2
        # edit the message with the genders
        message = interaction.message
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(self.ctx, "finding_couple")
            )
        )
        view.add_item(container)
        await message.edit(view=view)
        # get the profile pictures
        try:
            pfp1, pfp2 = await get_couple_pfps(self.ctx, gender1, gender2)
        except Exception as e:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=msg(self.ctx, "no_match")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await message.edit(view=view)
        # send the profile pictures
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(self.ctx, "title_couple")
            ),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=pfp1
                ),
                discord.MediaGalleryItem(
                    media=pfp2
                )
            )
        )
        view.add_item(container)
        await message.edit(view=view, attachments=[pfp1, pfp2])
    
class CouplesGenderSelect(discord.ui.LayoutView):
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        super().__init__()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(self.ctx, "title_couple")
            ),
            discord.ui.ActionRow(
                CoupleGenderSelect(ctx),
            ),
            discord.ui.ActionRow(
                CoupleGenderSelect2(ctx)
            ),
            discord.ui.ActionRow(
                CoupleGenderSubmit(ctx)
            )
        )
        self.add_item(container)

class PfpCog(commands.Cog):
    """Find new profile pictures for users."""
    def __init__(self, bot):
        self.bot = bot

    # pfp command group
    @commands.group(
        name="pfp", 
        aliases=["profilepicture", "profilepic", "pf"],
        help=CMDS.help("pfp"),
        invoke_without_command=True
    )
    async def pfp(self, ctx: commands.Context):
        prefix = await _resolve_prefix(self.bot, ctx)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(ctx, "help_title")
                + "\n"
                + msg(ctx, "help_body", prefix=prefix)
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

    # color command
    @pfp.command(
        name="color",
        aliases=["colour"],
        help=CMDS.help("pfp.color"),
    )
    async def color(self, ctx: commands.Context):
        # rewrittem to use the select menu - 04/21/2026
        view = ColorSelectView(ctx)
        await ctx.send(view=view)

    # gender command
    @pfp.command(
        name="gender",
        aliases=["sex"],
        help=CMDS.help("pfp.gender"),
    )
    async def gender(self, ctx: commands.Context):
        # rewritten to use the select menu - 04/21/2026
        view = GenderSelectView(ctx)
        await ctx.send(view=view)

    # couple command
    @pfp.command(
        name="couple",
        aliases=["couples", "pair", "pairs"],
        help=CMDS.help("pfp.couple"),
    )
    async def couple(self, ctx: commands.Context):
         # send a message with the gender selection dropdowns
        view = CouplesGenderSelect(ctx)
        await ctx.send(view=view)

    # owner only upload subgroup
    @pfp.group(
        name="upload",
        help=CMDS.help("pfp.upload"),
        invoke_without_command=True
    )
    @is_owner()
    async def upload(self, ctx: commands.Context):
        prefix = await _resolve_prefix(self.bot, ctx)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(ctx, "upload_title")
                + "\n"
                + msg(ctx, "upload_body", prefix=prefix)
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

    # color upload command
    @upload.command(
        name="color",
        aliases=["colour"],
        help=CMDS.help("pfp.upload.color"),
    )
    @is_owner()
    async def upload_color(self, ctx: commands.Context, color: str):
        # every image in the message (or its gallery, embeds, links or reply)
        images = await extract_images_from_message(ctx.message)
        saved = save_pfp_images(f"{PFPS_FOLDER}/colors/{color.lower()}", images or [])
        if not saved:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=msg(ctx, "no_image")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await ctx.send(view=view)
        # send a success message
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(
                    ctx, "uploaded", count=saved, s=_plural(saved), collection=color.lower()
                )
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await ctx.send(view=view)

    # gender upload command
    @upload.command(
        name="gender",
        aliases=["sex"],
        help=CMDS.help("pfp.upload.gender"),
    )
    @is_owner()
    async def upload_gender(self, ctx: commands.Context, gender: str):
        supported_genders = list(GENDERS)
        if gender.lower() not in supported_genders:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=msg(ctx, "unsupported_gender", genders=", ".join(supported_genders))
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await ctx.send(view=view)
        # every image in the message (or its gallery, embeds, links or reply)
        images = await extract_images_from_message(ctx.message)
        saved = save_pfp_images(f"{PFPS_FOLDER}/genders/{gender.lower()}", images or [])
        if not saved:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=msg(ctx, "no_image")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await ctx.send(view=view)
        # send a success message
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(
                    ctx, "uploaded", count=saved, s=_plural(saved), collection=gender.lower()
                )
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await ctx.send(view=view)

    # couple upload command
    @upload.command(
        name="couple",
        aliases=["couples", "pair", "pairs"],
        help=CMDS.help("pfp.upload.couple"),
    )
    @is_owner()
    async def upload_couple(self, ctx: commands.Context, gender1: str, gender2: str):
        supported_genders = list(GENDERS)
        if gender1.lower() not in supported_genders or gender2.lower() not in supported_genders:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=msg(ctx, "unsupported_gender", genders=", ".join(supported_genders))
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await ctx.send(view=view)
        # get the images from the message
        images = await extract_images_from_message(ctx.message)
        if not images or len(images) != 2:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=msg(ctx, "couple_images")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await ctx.send(view=view)
        # save the images to the folder
        gender_folder = f"{PFPS_FOLDER}/couples"
        # get the subfolder that matches the genders (female-male is the same as male-female to avoid duplicates and reduce the number of folders)
        subfolder = f"{gender1}-{gender2}"
        if subfolder not in COUPLE_SUBFOLDERS:
            subfolder = f"{gender2}-{gender1}"
        gender_folder_path = f"{gender_folder}/{subfolder}"
        # get the number of images in the folder
        number_of_images = len(os.listdir(gender_folder_path))
        # save the images to the folder
        with open(f"{gender_folder_path}/{number_of_images + 1}_1.png", "wb") as f:
            f.write(images[0].read())
        with open(f"{gender_folder_path}/{number_of_images + 1}_2.png", "wb") as f:
            f.write(images[1].read())
        # send a success message
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(ctx, "couple_uploaded")
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await ctx.send(view=view)


async def setup(bot):
     await bot.add_cog(PfpCog(bot))