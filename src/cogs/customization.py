# this cog is partially experimental and some smaller parts may break in the future.

# the main feature that may break is the ability to change the bot's display name font and color per guild using an undocumented endpoint:
# to do this you need to send a PATCH request to the following endpoint:
# https://discord.com/api/v10/guilds/{guild_id}/members/@me
# with a body of:
# {
#   display_name_font_id: 11, 
#   display_name_effect_id: 2, 
#   display_name_colors: [14631474, 12423167]
# }
# display_name_colors: [14631474, 12423167]
# display_name_effect_id: 2
# display_name_font_id: 11

# Note:
# this endpoint is new and has not been officially dovumented by discord meaning that it may break or be removed at any time however it does not violate the discord ToS since it is part of the public profile endpoint.

import discord
from discord.ext import commands
import requests
import json
import os
import base64
# import numpy as np
from utils import logging


# ---------------------------------------------------------
# Utility: Convert integer color → BGR tuple
# ---------------------------------------------------------
def int_to_bgr(c: int):
    r = (c >> 16) & 255
    g = (c >> 8) & 255
    b = c & 255
    return (b, g, r)


# ---------------------------------------------------------
# Utility: Encode image file to base64
# ---------------------------------------------------------
def encode_image(file_bytes: bytes):
    return "data:image/png;base64," + base64.b64encode(file_bytes).decode()


# ---------------------------------------------------------
# Modal: Display Name Input
# ---------------------------------------------------------
class DisplayNameModal(discord.ui.Modal, title="Set Display Name"):
    name = discord.ui.TextInput(label="New Display Name", max_length=32)

    def __init__(self, view):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        self.view.display_name = str(self.name)
        await interaction.response.send_message("Display name set.", ephemeral=True)


# ---------------------------------------------------------
# Modal: Bio Input
# ---------------------------------------------------------
class BioModal(discord.ui.Modal, title="Set Bio"):
    bio = discord.ui.TextInput(label="New Bio", style=discord.TextStyle.paragraph, max_length=190)

    def __init__(self, view):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        self.view.bio = str(self.bio)
        await interaction.response.send_message("Bio updated.", ephemeral=True)


# ---------------------------------------------------------
# Modal: File Upload (PFP / Banner)
# ---------------------------------------------------------
class FileUploadModal(discord.ui.Modal):
    def __init__(self, view, title, target):
        super().__init__(title=title)
        self.view = view
        self.target = target

        self.file = discord.ui.FileInput(label="Upload Image")
        self.add_item(self.file)

    async def on_submit(self, interaction: discord.Interaction):
        attachment = self.file.value  # This is a discord.Attachment
        file_bytes = await attachment.read()

        if self.target == "pfp":
            self.view.pfp_bytes = file_bytes
        else:
            self.view.banner_bytes = file_bytes

        await interaction.response.send_message(
            "Image uploaded successfully.", ephemeral=True
        )


# ---------------------------------------------------------
# Dropdowns for fonts and colors
# ---------------------------------------------------------
class FontSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Font 11", value="11"),
            discord.SelectOption(label="Font 12", value="12"),
            discord.SelectOption(label="Font 13", value="13"),
        ]
        super().__init__(placeholder="Select Font", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.font_id = int(self.values[0])
        await interaction.response.defer()


class ColorSelect(discord.ui.Select):
    def __init__(self, label, target):
        self.target = target
        options = [
            discord.SelectOption(label="Red", value="16711680"),
            discord.SelectOption(label="Green", value="65280"),
            discord.SelectOption(label="Blue", value="255"),
            discord.SelectOption(label="Pink", value="14631474"),
            discord.SelectOption(label="Orange", value="12423167"),
        ]
        super().__init__(placeholder=label, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.target == "color1":
            self.view.color1 = int(self.values[0])
        else:
            self.view.color2 = int(self.values[0])
        await interaction.response.defer()


# ---------------------------------------------------------
# View: Set Name
# ---------------------------------------------------------
class SetNameView(discord.ui.LayoutView):
    def __init__(self, guild_id):
        super().__init__(timeout=180)
        self.guild_id = guild_id

        self.display_name = None
        self.font_id = None
        self.color1 = None
        self.color2 = None

        # --- Buttons with callbacks attached ---
        set_name_btn = discord.ui.Button(
            label="Set Display Name",
            style=discord.ButtonStyle.primary,
            custom_id="set_name_btn"
        )
        set_name_btn.callback = self.set_name_callback

        apply_btn = discord.ui.Button(
            label="Apply",
            style=discord.ButtonStyle.green,
            custom_id="apply_btn"
        )
        apply_btn.callback = self.apply_callback

        # --- Container Layout ---
        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### Customize Display Name"),
            discord.ui.Separator(),
            discord.ui.ActionRow(set_name_btn),
            discord.ui.ActionRow(FontSelect()),
            discord.ui.ActionRow(ColorSelect("Select Color 1", "color1")),
            discord.ui.ActionRow(ColorSelect("Select Color 2", "color2")),
            discord.ui.ActionRow(apply_btn),
            accent_colour=discord.Colour(0x5865F2)
        )

        self.add_item(container)

    async def interaction_check(self, interaction):
        return interaction.user.guild_permissions.administrator

    # ---------------------------------------------------------
    # Button Callbacks
    # ---------------------------------------------------------
    async def set_name_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(DisplayNameModal(self))

    async def apply_callback(self, interaction: discord.Interaction):
        if not all([self.display_name, self.font_id, self.color1, self.color2]):
            return await interaction.response.send_message("Missing fields.", ephemeral=True)

        token = os.getenv("DISCORD_TOKEN")
        url = f"https://discord.com/api/v10/guilds/{self.guild_id}/members/@me"

        payload = {
            "nick": self.display_name,
            "display_name_font_id": self.font_id,
            "display_name_effect_id": 2,
            "display_name_colors": [self.color1, self.color2]
        }

        headers = {
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json"
        }

        r = requests.patch(url, headers=headers, data=json.dumps(payload))

        if r.status_code in (200, 204):
            return await interaction.response.send_message("Updated successfully.", ephemeral=True)

        logging.error("customization", f"API Error: {r.status_code} - {r.text}")
        return await interaction.response.send_message("Failed to update.", ephemeral=True)


# ---------------------------------------------------------
# View: Set Profile (PFP, Banner, Bio)
# ---------------------------------------------------------
class SetProfileView(discord.ui.LayoutView):
    def __init__(self, guild_id):
        super().__init__(timeout=180)
        self.guild_id = guild_id

        self.pfp_bytes = None
        self.banner_bytes = None
        self.bio = None

        # --- Buttons with callbacks attached ---
        pfp_btn = discord.ui.Button(
            label="Upload PFP",
            style=discord.ButtonStyle.primary,
            custom_id="pfp_btn"
        )
        pfp_btn.callback = self.pfp_callback

        banner_btn = discord.ui.Button(
            label="Upload Banner",
            style=discord.ButtonStyle.primary,
            custom_id="banner_btn"
        )
        banner_btn.callback = self.banner_callback

        bio_btn = discord.ui.Button(
            label="Set Bio",
            style=discord.ButtonStyle.primary,
            custom_id="bio_btn"
        )
        bio_btn.callback = self.bio_callback

        apply_btn = discord.ui.Button(
            label="Apply",
            style=discord.ButtonStyle.green,
            custom_id="apply_btn"
        )
        apply_btn.callback = self.apply_callback

        # --- Container Layout ---
        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### Customize Server Profile"),
            discord.ui.Separator(),
            discord.ui.ActionRow(pfp_btn),
            discord.ui.ActionRow(banner_btn),
            discord.ui.ActionRow(bio_btn),
            discord.ui.ActionRow(apply_btn),
            accent_colour=discord.Colour(0x5865F2)
        )

        self.add_item(container)

    async def interaction_check(self, interaction):
        return interaction.user.guild_permissions.administrator

    # ---------------------------------------------------------
    # Button Callbacks
    # ---------------------------------------------------------
    async def pfp_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(FileUploadModal(self, "Upload PFP", "pfp"))

    async def banner_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(FileUploadModal(self, "Upload Banner", "banner"))

    async def bio_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(BioModal(self))

    async def apply_callback(self, interaction: discord.Interaction):
        token = os.getenv("DISCORD_TOKEN")
        url = f"https://discord.com/api/v10/guilds/{self.guild_id}/members/@me"

        payload = {}

        if self.pfp_bytes:
            payload["avatar"] = encode_image(self.pfp_bytes)

        if self.banner_bytes:
            payload["banner"] = encode_image(self.banner_bytes)

        if self.bio:
            payload["bio"] = self.bio

        if not payload:
            return await interaction.response.send_message("Nothing to update.", ephemeral=True)

        headers = {
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json"
        }

        r = requests.patch(url, headers=headers, data=json.dumps(payload))

        if r.status_code in (200, 204):
            return await interaction.response.send_message("Profile updated.", ephemeral=True)

        logging.error("customization", f"API Error: {r.status_code} - {r.text}")
        return await interaction.response.send_message("Failed to update.", ephemeral=True)


# ---------------------------------------------------------
# Cog
# ---------------------------------------------------------
class Customization(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setname", help="Set and customize the bot's display name.")
    @commands.has_permissions(administrator=True)
    async def setname(self, ctx):
        view = SetNameView(ctx.guild.id)
        await ctx.reply(view=view)

    @commands.command(name="setprofile", help="Customize the bot's PFP, banner, and bio.")
    @commands.has_permissions(administrator=True)
    async def setprofile(self, ctx):
        view = SetProfileView(ctx.guild.id)
        await ctx.reply(view=view)


async def setup(bot):
    await bot.add_cog(Customization(bot))
