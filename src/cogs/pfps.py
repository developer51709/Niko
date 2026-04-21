"""
PFP Cog — finds new profile pictures for users.
────────────────────────────────────────

"""
import discord
from discord.ext import commands
import os
import random
import asyncio
from config.emojis import get_emoji
from .error_handler import is_owner
from utils.image.extractor import extract_image_from_message, extract_images_from_message
from utils import logging

PFPS_FOLDER = "src/assets/pfps"


# ------------------------------
# Utility Functions
# ------------------------------

async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    raw = bot.command_prefix
    if isinstance(raw, str):
        return raw
    if isinstance(raw, (list, tuple)):
        return raw[0]
    try:
        msg = getattr(ctx_or_interaction, "message", None)
        if msg is None and isinstance(ctx_or_interaction, discord.Interaction):
            msg = ctx_or_interaction.message
        if msg is None:
            return "."
        prefixes = raw(bot, msg)
        if isinstance(prefixes, (list, tuple)) and prefixes:
            return prefixes[0]
    except Exception:
        pass
    return "."

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
    gender_subfolders = [
        "male-male",
        "male-female",
        "female-female",
        "non-binary-male",
        "non-binary-female",
        "non-binary-non-binary"
    ]
    # get the subfolder that matches the genders (female-male is the same as male-female to avoid duplicates and reduce the number of folders)
    subfolder = f"{gender1}-{gender2}"
    if subfolder not in gender_subfolders:
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
            options.append(discord.SelectOption(label=color.capitalize(), value=color, description=f"{count} images"))
        super().__init__(placeholder="Select a color", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You are not the author of this command."
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
        super().__init__(label="Submit", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You are not the author of this command."
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
                    content=f"{get_emoji('icon_cross')} You must select a color first!"
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
                content=f"{get_emoji('icon_loading')} Finding a profile picture for the selected color..."
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
                    content=f"{get_emoji('icon_cross')} An error occurred while finding the profile picture. Please try again later."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await message.edit(view=view)
        # send the profile picture
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('icon_image')} Profile Picture"
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
                content=f"### {get_emoji('icon_image')} Profile Picture"
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
    genders = ["male", "female", "non-binary"]
    counts = []
    for gender in genders:
        counts.append((gender, len(os.listdir(f"{gender_folder_path}/{gender}"))))
    return counts

class GenderSelect(discord.ui.Select):
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        options = []
        for gender, count in get_gender_image_counts():
            options.append(discord.SelectOption(label=gender.capitalize(), value=gender, description=f"{count} images"))
        super().__init__(placeholder="Select a gender", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You are not the author of this command."
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
        super().__init__(label="Submit", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You are not the author of this command."
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
                content=f"{get_emoji('icon_loading')} Finding a profile picture for the selected gender..."
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
                content=f"### {get_emoji('icon_image')} Profile Picture"
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
                content=f"### {get_emoji('icon_image')} Profile Picture"
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
        options = [
            discord.SelectOption(label="Male", value="male"),
            discord.SelectOption(label="Female", value="female"),
            discord.SelectOption(label="Non-binary", value="non-binary")
        ]
        super().__init__(placeholder="Select your gender", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You are not the author of this command."
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
        options = [
            discord.SelectOption(label="Male", value="male"),
            discord.SelectOption(label="Female", value="female"),
            discord.SelectOption(label="Non-binary", value="non-binary")
        ]
        super().__init__(placeholder="Select your partner's gender", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You are not the author of this command."
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
        super().__init__(label="Submit", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You are not the author of this command."
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
                content=f"{get_emoji('icon_loading')} Finding matching profile pictures for the selected genders..."
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
                    content=f"{get_emoji('icon_cross')} We couldn't find any matching profile pictures for the selected genders."
                ),
                discord.ui.TextDisplay(
                    content="-# **Note from Developers:**\n-# This feature is still really new and not all the combinations are available yet. If you would like to help contribute to this feature, please feel free to add me on Discord (my username is `nyxenwastaken`) and send me message asking for more details on how you can contribute to the project.\n-# ~Sincerely, Nyxen"
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await message.edit(view=view)
        # send the profile pictures
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('icon_image')} Couple Profile Pictures"
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
                content=f"### {get_emoji('icon_image')} Couple Profile Pictures"
            ),
            discord.ui.ActionRow(
                CoupleGenderSelect(ctx),
            ),
            discord.ui.ActionRow(
                CoupleGenderSelect2(ctx)
            ),
            discord.ui.ActionRow(
                CoupleGenderSubmit(ctx)
            ),
            discord.ui.TextDisplay(
                content="-# **Note:**\n-# This feature is still in development and may not work as expected."
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
        help="{ 'en': 'Find new profile pictures.', 'de': 'Finde neue Profilbilder.' }",
        invoke_without_command=True
    )
    async def pfp(self, ctx: commands.Context):
        prefix = await _resolve_prefix(self.bot, ctx)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('icon_image')} Profile Pictures\n"
                f"Find new profile pictures.\n\n"
                f"**Subcommands:**\n"
                f"`{prefix}pfp color` - Find a profile picture with the specified color.\n"
                f"`{prefix}pfp gender` - Find a profile picture with the specified gender.\n"
                f"`{prefix}pfp couple` - Find matching profile pictures with the specified genders.\n"
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

    # color command
    @pfp.command(
        name="color",
        aliases=["colour"],
        help="{ 'en': 'Find a profile picture with the specified color.', 'de': 'Finde ein Profilbild mit der angegebenen Farbe.' }"
    )
    async def color(self, ctx: commands.Context):
        # rewrittem to use the select menu - 04/21/2026
        view = ColorSelectView(ctx)
        await ctx.send(view=view)

    # gender command
    @pfp.command(
        name="gender",
        aliases=["sex"],
        help="{ 'en': 'Find a profile picture with the specified gender.', 'de': 'Finde ein Profilbild mit dem angegebenen Geschlecht.' }"
    )
    async def gender(self, ctx: commands.Context):
        # rewritten to use the select menu - 04/21/2026
        view = GenderSelectView(ctx)
        await ctx.send(view=view)

    # couple command
    @pfp.command(
        name="couple",
        aliases=["couples", "pair", "pairs"],
        help="{ 'en': 'Find matching profile pictures with the specified genders.', 'de': 'Finde passende Profilbilder mit den angegebenen Geschlechtern.' }"
    )
    async def couple(self, ctx: commands.Context):
         # send a message with the gender selection dropdowns
        view = CouplesGenderSelect(ctx)
        await ctx.send(view=view)

    # owner only upload subgroup
    @pfp.group(
        name="upload",
        help="{ 'en': 'Upload a profile picture.', 'de': 'Lade ein Profilbild hoch.' }",
        invoke_without_command=True
    )
    @is_owner()
    async def upload(self, ctx: commands.Context):
        prefix = await _resolve_prefix(self.bot, ctx)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('icon_image')} Upload Profile Picture\n"
                f"Upload a profile picture.\n\n"
                f"**Subcommands:**\n"
                f"`{prefix}pfp upload color <color>` - Upload a profile picture with the specified color.\n"
                f"`{prefix}pfp upload gender` - Upload a profile picture with the specified gender.\n"
                f"`{prefix}pfp upload couple` - Upload matching profile pictures with the specified genders.\n"
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

    # color upload command
    @upload.command(
        name="color",
        aliases=["colour"],
        help="{ 'en': 'Upload a profile picture with the specified color.', 'de': 'Lade ein Profilbild mit der angegebenen Farbe hoch.' }"
    )
    @is_owner()
    async def upload_color(self, ctx: commands.Context, color: str):
        # get the image from the message
        image = await extract_image_from_message(ctx.message)
        if not image:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} No image found in the message."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await ctx.send(view=view)
        try:
            # save the image to the folder
            color_folder_path = f"{PFPS_FOLDER}/colors/{color.lower()}"
            # get the number of images in the folder
            number_of_images = len(os.listdir(color_folder_path))
            # save the image to the folder
            with open(f"{color_folder_path}/{number_of_images + 1}.png", "wb") as f:
                f.write(image.read())
        # handle missing folder error
        except FileNotFoundError:
            # create the folder
            os.mkdir(f"{PFPS_FOLDER}/colors/{color.lower()}")
            # save the image to the folder
            color_folder_path = f"{PFPS_FOLDER}/colors/{color.lower()}"
            # get the number of images in the folder
            number_of_images = len(os.listdir(f"{PFPS_FOLDER}/colors/{color.lower()}"))
            # save the image to the folder
            with open(f"{color_folder_path}/{number_of_images + 1}.png", "wb") as f:
                f.write(image.read())
        # send a success message
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_tick')} The profile picture has been uploaded successfully."
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await ctx.send(view=view)

    # gender upload command
    @upload.command(
        name="gender",
        aliases=["sex"],
        help="{ 'en': 'Upload a profile picture with the specified gender.', 'de': 'Lade ein Profilbild mit dem angegebenen Geschlecht hoch.' }"
    )
    @is_owner()
    async def upload_gender(self, ctx: commands.Context, gender: str):
        # 3 genders are supported: male, female, non-binary
        supported_genders = ["male", "female", "non-binary"]
        if gender.lower() not in supported_genders:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} The specified gender is not supported. Supported genders are: {', '.join(supported_genders)}"
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await ctx.send(view=view)
        # get the image from the message
        image = await extract_image_from_message(ctx.message)
        if not image:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} No image found in the message."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await ctx.send(view=view)
        # save the image to the folder
        gender_folder_path = f"{PFPS_FOLDER}/genders/{gender.lower()}"
        # get the number of images in the folder
        number_of_images = len(os.listdir(gender_folder_path))
        # save the image to the folder
        with open(f"{gender_folder_path}/{number_of_images + 1}.png", "wb") as f:
            f.write(image.read())
        # send a success message
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_tick')} The profile picture has been uploaded successfully."
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await ctx.send(view=view)

    # couple upload command
    @upload.command(
        name="couple",
        aliases=["couples", "pair", "pairs"],
        help="{ 'en': 'Upload matching profile pictures with the specified genders.', 'de': 'Lade passende Profilbilder mit den angegebenen Geschlechtern hoch.' }"
    )
    @is_owner()
    async def upload_couple(self, ctx: commands.Context, gender1: str, gender2: str):
        # 3 genders are supported: male, female, non-binary
        supported_genders = ["male", "female", "non-binary"]
        if gender1.lower() not in supported_genders or gender2.lower() not in supported_genders:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} The specified gender is not supported. Supported genders are: {', '.join(supported_genders)}"
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
                    content=f"{get_emoji('icon_cross')} No images found in the message or the number of images is not 2."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await ctx.send(view=view)
        # save the images to the folder
        gender_folder = f"{PFPS_FOLDER}/couples"
        gender_subfolders = [
            "male-male",
            "male-female",
            "female-female",
            "non-binary-male",
            "non-binary-female",
            "non-binary-non-binary"
        ]
        # get the subfolder that matches the genders (female-male is the same as male-female to avoid duplicates and reduce the number of folders)
        subfolder = f"{gender1}-{gender2}"
        if subfolder not in gender_subfolders:
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
                content=f"{get_emoji('icon_tick')} The profile pictures have been uploaded successfully."
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await ctx.send(view=view)


async def setup(bot):
     await bot.add_cog(PfpCog(bot))