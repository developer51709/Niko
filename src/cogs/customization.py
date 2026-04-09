import asyncio
import discord
from discord.ext import commands
import aiohttp
import json
import os
import base64
from utils import logging

# ---------- Helpers ----------

def encode_image(file_bytes: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(file_bytes).decode()

def _mask_token(t: str) -> str:
    if not t:
        return "<missing>"
    if len(t) <= 8:
        return t[0:2] + "..." + t[-1:]
    return t[0:4] + "..." + t[-4:]

DISCORD_BOTCLIENT_UA = (
    "DiscordBot (https://github.com/aiko-chan-ai/DiscordBotClient, 1.0)"
)

async def try_patch_with_fallbacks(urls, token, payload, extra_headers=None, timeout=10):
    """
    urls: list of URL strings to try in order
    token: raw token string from env
    payload: dict to send as JSON
    extra_headers: dict of additional headers to include
    Returns: (success: bool, attempts: list of dicts)
    """
    attempted = []
    headers_base = {
        "User-Agent": DISCORD_BOTCLIENT_UA,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if extra_headers:
        headers_base.update(extra_headers)

    auth_variants = [
        ("raw", token),
        ("bot_prefix", f"Bot {token}" if token else ""),
    ]

    async with aiohttp.ClientSession() as session:
        for url in urls:
            for auth_name, auth_value in auth_variants:
                headers = dict(headers_base)
                if auth_value:
                    headers["Authorization"] = auth_value
                else:
                    headers.pop("Authorization", None)

                try:
                    async with session.patch(
                        url,
                        headers=headers,
                        data=json.dumps(payload),
                        timeout=aiohttp.ClientTimeout(total=timeout)
                    ) as r:
                        status = r.status
                        text = await r.text()
                        attempted.append({
                            "url": url,
                            "auth": auth_name,
                            "status_code": status,
                            "response_text": text[:1000],
                        })
                        if status in (200, 204):
                            return True, attempted
                except Exception as exc:
                    attempted.append({
                        "url": url,
                        "auth": auth_name,
                        "status": "request_error",
                        "error": str(exc),
                    })
                    continue

    return False, attempted

# ---------- Views and Modals ----------

class DisplayNameModal(discord.ui.Modal, title="Set Display Name"):
    name = discord.ui.TextInput(label="New Display Name", max_length=32)

    def __init__(self, view):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        self.view.display_name = str(self.name)
        await interaction.response.send_message("Display name set.", ephemeral=True)


class BioModal(discord.ui.Modal, title="Set Bio"):
    bio = discord.ui.TextInput(label="New Bio", style=discord.TextStyle.paragraph, max_length=190)

    def __init__(self, view):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        self.view.bio = str(self.bio)
        await interaction.response.send_message("Bio updated.", ephemeral=True)


class FileUploadModal(discord.ui.Modal):
    def __init__(self, view, title, target):
        super().__init__(title=title)
        self.view = view
        self.target = target

        self.file = discord.ui.FileInput(label="Upload Image")
        self.add_item(self.file)

    async def on_submit(self, interaction: discord.Interaction):
        attachment = self.file.value
        if attachment is None:
            return await interaction.response.send_message(
                "No file received. File upload may not be supported in this context.", ephemeral=True
            )
        file_bytes = await attachment.read()

        if self.target == "pfp":
            self.view.pfp_bytes = file_bytes
        else:
            self.view.banner_bytes = file_bytes

        await interaction.response.send_message("Image uploaded successfully.", ephemeral=True)


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

# ---------- Main Views ----------

class SetNameView(discord.ui.LayoutView):
    def __init__(self, guild_id):
        super().__init__(timeout=180)
        self.guild_id = guild_id

        self.display_name = None
        self.font_id = None
        self.color1 = None
        self.color2 = None

        set_name_btn = discord.ui.Button(label="Set Display Name", style=discord.ButtonStyle.primary, custom_id="set_name_btn")
        set_name_btn.callback = self.set_name_callback

        apply_btn = discord.ui.Button(label="Apply", style=discord.ButtonStyle.green, custom_id="apply_btn")
        apply_btn.callback = self.apply_callback

        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### Customize Display Name"),
            discord.ui.Separator(),
            discord.ui.ActionRow(set_name_btn),
            discord.ui.ActionRow(FontSelect()),
            discord.ui.ActionRow(ColorSelect("Select Color 1", "color1")),
            discord.ui.ActionRow(ColorSelect("Select Color 2", "color2")),
            discord.ui.ActionRow(apply_btn),
            accent_colour=discord.Colour(0x5865F2),
        )

        self.add_item(container)

    async def interaction_check(self, interaction):
        return interaction.user.guild_permissions.administrator

    async def set_name_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(DisplayNameModal(self))

    async def apply_callback(self, interaction: discord.Interaction):
        if not all([self.display_name, self.font_id, self.color1, self.color2]):
            return await interaction.response.send_message("Missing fields.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        token = os.getenv("DISCORD_BOT_TOKEN")
        guild_id = self.guild_id

        url = f"https://discord.com/api/v10/guilds/{guild_id}/members/@me"

        payload = {
            "display_name_font_id": self.font_id,
            "display_name_effect_id": 2,
            "display_name_colors": [self.color1, self.color2]
        }

        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "Origin": "https://discord.com",
            "Referer": f"https://discord.com/channels/{guild_id}/{interaction.channel_id}",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            )
        }

        success, _ = await try_patch_with_fallbacks([url], token, payload, extra_headers={
            "Origin": headers["Origin"],
            "Referer": headers["Referer"],
            "User-Agent": headers["User-Agent"],
        })

        if success:
            await interaction.followup.send("Updated successfully.", ephemeral=True)
        else:
            logging.error("customization", f"Failed to update display name for guild {guild_id}")
            await interaction.followup.send("Failed to update.", ephemeral=True)


class SetProfileView(discord.ui.LayoutView):
    def __init__(self, guild_id):
        super().__init__(timeout=180)
        self.guild_id = guild_id

        self.pfp_bytes = None
        self.banner_bytes = None
        self.bio = None

        pfp_btn = discord.ui.Button(label="Upload PFP", style=discord.ButtonStyle.primary, custom_id="pfp_btn")
        pfp_btn.callback = self.pfp_callback

        banner_btn = discord.ui.Button(label="Upload Banner", style=discord.ButtonStyle.primary, custom_id="banner_btn")
        banner_btn.callback = self.banner_callback

        bio_btn = discord.ui.Button(label="Set Bio", style=discord.ButtonStyle.primary, custom_id="bio_btn")
        bio_btn.callback = self.bio_callback

        apply_btn = discord.ui.Button(label="Apply", style=discord.ButtonStyle.green, custom_id="apply_btn")
        apply_btn.callback = self.apply_callback

        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### Customize Server Profile"),
            discord.ui.Separator(),
            discord.ui.ActionRow(pfp_btn),
            discord.ui.ActionRow(banner_btn),
            discord.ui.ActionRow(bio_btn),
            discord.ui.ActionRow(apply_btn),
            accent_colour=discord.Colour(0x5865F2),
        )

        self.add_item(container)

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator

    async def pfp_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(FileUploadModal(self, "Upload PFP", "pfp"))

    async def banner_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(FileUploadModal(self, "Upload Banner", "banner"))

    async def bio_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(BioModal(self))

    async def apply_callback(self, interaction: discord.Interaction):
        token = os.getenv("DISCORD_BOT_TOKEN")
        if not token:
            logging.error("customization", "DISCORD_BOT_TOKEN is not set in environment.")
            return await interaction.response.send_message("Internal configuration error.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        bot_id = str(interaction.client.user.id)
        urls = [
            f"https://canary.discord.com/api/v10/guilds/{self.guild_id}/members/@me",
            f"https://canary.discord.com/api/v10/guilds/{self.guild_id}/members/{bot_id}",
            f"https://discord.com/api/v10/guilds/{self.guild_id}/members/@me",
            f"https://discord.com/api/v10/guilds/{self.guild_id}/members/{bot_id}",
        ]

        body = {}
        if self.pfp_bytes:
            body["avatar"] = encode_image(self.pfp_bytes)
        if self.banner_bytes:
            body["banner"] = encode_image(self.banner_bytes)
        if self.bio:
            body["bio"] = self.bio

        if not body:
            return await interaction.followup.send("Nothing to update.", ephemeral=True)

        success, attempts = await try_patch_with_fallbacks(urls, token, body)
        if success:
            return await interaction.followup.send("Profile updated.", ephemeral=True)

        msg_lines = ["Failed to update profile. Attempts:"]
        for a in attempts:
            if a.get("status") == "request_error":
                msg_lines.append(f"- {a['url']} auth={a['auth']} error={a['error']}")
            else:
                code = a.get("status_code")
                body_text = a.get("response_text", "")
                msg_lines.append(f"- {a['url']} auth={a['auth']} status={code} body={body_text}")

        logging.error("customization", " | ".join(msg_lines))
        return await interaction.followup.send(
            "Failed to update profile. Check logs for details.", ephemeral=True
        )

# ---------- Cog ----------

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
