import discord
from discord.ext import commands
import aiohttp
import json
import os
import base64
from utils import logging
from config.emojis import get_emoji
from cogs.system.error_handler import is_owner
from utils.fileinput_patch.fileinput import ensure_universal_fileinput

# FileInput is provided natively by newer discord.py versions and by the
# project's compatibility patch on older versions.
ensure_universal_fileinput()

# ---------- Helpers ----------

def encode_image(file_bytes: bytes, content_type: str = "image/png") -> str:
    """Encode an uploaded image as a Discord-compatible data URI."""
    if content_type not in {"image/png", "image/jpeg", "image/gif"}:
        content_type = "image/png"
    return f"data:{content_type};base64," + base64.b64encode(file_bytes).decode()

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


class ProfileModal(discord.ui.Modal, title="Customize Server Profile"):
    def __init__(self, view):
        super().__init__()
        self.view = view

        # FileUpload is native in discord.py 2.7+. FileInput is retained as a
        # compatibility fallback for the project's older-library patch.
        upload_cls = getattr(discord.ui, "FileUpload", discord.ui.FileInput)
        self.pfp = upload_cls(custom_id="profile_pfp", required=False, max_values=1)
        self.banner = upload_cls(custom_id="profile_banner", required=False, max_values=1)
        self.bio = discord.ui.TextInput(
            label="Bio",
            style=discord.TextStyle.paragraph,
            max_length=190,
            required=False,
        )
        self.add_item(discord.ui.Label(
            text="Profile Picture",
            description="Optional image upload for the bot's server avatar.",
            component=self.pfp,
        ))
        self.add_item(discord.ui.Label(
            text="Banner",
            description="Optional image upload for the bot's server banner.",
            component=self.banner,
        ))
        self.add_item(self.bio)

    @staticmethod
    def _first_attachment(field):
        values = getattr(field, "values", None)
        if values:
            return values[0]
        return getattr(field, "value", None)

    async def on_submit(self, interaction: discord.Interaction):
        for field, target in ((self.pfp, "pfp_bytes"), (self.banner, "banner_bytes")):
            attachment = self._first_attachment(field)
            if attachment is None:
                continue
            if not (attachment.content_type or "").startswith("image/"):
                name = "profile picture" if target == "pfp_bytes" else "banner"
                await interaction.response.send_message(
                    f"{get_emoji('icon_cross')} The {name} must be an image.",
                    ephemeral=True,
                )
                return
            setattr(self.view, target, await attachment.read())
            setattr(
                self.view,
                "pfp_content_type" if target == "pfp_bytes" else "banner_content_type",
                attachment.content_type or "image/png",
            )
            self.view.updated_fields.add("pfp" if target == "pfp_bytes" else "banner")

        bio = str(self.bio).strip()
        if bio:
            self.view.bio = bio
            self.view.updated_fields.add("bio")

        await interaction.response.send_message(
            f"{get_emoji('icon_tick')} Profile details saved. Click **Apply** to update the bot.",
            ephemeral=True,
        )


class FontSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Sakura", value="3"),
            discord.SelectOption(label="Jellybean", value="4"),
            discord.SelectOption(label="Modern", value="6"),
            discord.SelectOption(label="Medieval", value="7"),
            discord.SelectOption(label="8Bit", value="8"),
            discord.SelectOption(label="Vampyre", value="10"),
            discord.SelectOption(label="gg sans (Default)", value="11"),
            discord.SelectOption(label="Tempo", value="12"),
        ]
        super().__init__(placeholder="Select Font", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.font_id = int(self.values[0])
        await interaction.response.defer()


class EffectSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Solid", value="1", description="Flat single-color fill"),
            discord.SelectOption(label="Gradient", value="2", description="Blend two colors from left to right"),
            discord.SelectOption(label="Neon", value="3", description="Glowing outline around the letters"),
            discord.SelectOption(label="Toon", value="4", description="Gradient fill with a visible outline"),
            discord.SelectOption(label="Pop", value="5", description="Colored drop shadow behind the letters"),
            discord.SelectOption(label="Glow", value="6", description="Soft outer glow with an optional accent"),
        ]
        super().__init__(placeholder="Select Color Style", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.effect_id = int(self.values[0])
        await interaction.response.defer()


class ColorSelect(discord.ui.Select):
    def __init__(self, label, target):
        self.target = target
        options = [
            discord.SelectOption(label="White", value="16777215"),
            discord.SelectOption(label="Black", value="0"),
            discord.SelectOption(label="Blurple", value="5793266"),
            discord.SelectOption(label="Green", value="5763719"),
            discord.SelectOption(label="Red", value="15548997"),
            discord.SelectOption(label="Yellow", value="16705372"),
            discord.SelectOption(label="Pink", value="16711935"),
            discord.SelectOption(label="Purple", value="8388736"),
            discord.SelectOption(label="Blue", value="5865"),
            discord.SelectOption(label="Gold", value="16766720"),
            discord.SelectOption(label="Cyan", value="65535"),
        ]
        super().__init__(placeholder=label, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.target == "color1":
            self.view.color1 = int(self.values[0])
        else:
            self.view.color2 = int(self.values[0])
        await interaction.response.defer()

# ---------- Main Views ----------

class GlobalOrGuildView(discord.ui.LayoutView):
    def __init__(self, guild_id):
        super().__init__(timeout=180)
        self.guild_id = guild_id

        self.choice = None

        global_btn = discord.ui.Button(label="Global", style=discord.ButtonStyle.primary, custom_id="global_btn")
        global_btn.callback = self.global_callback

        guild_btn = discord.ui.Button(label="Guild", style=discord.ButtonStyle.primary, custom_id="guild_btn")
        guild_btn.callback = self.guild_callback

        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### Customize Display Name"),
            discord.ui.Separator(),
            discord.ui.ActionRow(global_btn),
            discord.ui.ActionRow(guild_btn),
            accent_colour=discord.Colour(0x5865F2)
        )

        self.add_item(container)

    async def interaction_check(self, interaction):
        return interaction.user.guild_permissions.administrator or await interaction.client.is_owner(interaction.user)

    async def global_callback(self, interaction: discord.Interaction):
        self.choice = "global"
        try:
            await interaction.message.delete()
        except Exception:
            pass
        await interaction.response.defer()
        self.stop()

    async def guild_callback(self, interaction: discord.Interaction):
        self.choice = "guild"
        try:
            await interaction.message.delete()
        except Exception:
            pass
        await interaction.response.defer()
        self.stop()


class SetNameView(discord.ui.LayoutView):
    def __init__(self, guild_id):
        super().__init__(timeout=180)
        self.guild_id = guild_id

        self.display_name = None
        self.font_id = None
        self.effect_id = 2  # Preserve the existing gradient default.
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
            discord.ui.ActionRow(EffectSelect()),
            discord.ui.ActionRow(ColorSelect("Select Color 1", "color1")),
            discord.ui.ActionRow(ColorSelect("Select Color 2", "color2")),
            discord.ui.ActionRow(apply_btn),
            accent_colour=discord.Colour(0x5865F2),
        )

        self.add_item(container)

    async def interaction_check(self, interaction):
        return interaction.user.guild_permissions.administrator or await interaction.client.is_owner(interaction.user)

    async def set_name_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(DisplayNameModal(self))

    async def apply_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        token = os.getenv("DISCORD_BOT_TOKEN")
        guild_id = self.guild_id
        bot_id = str(interaction.client.user.id)

        urls = [
            f"https://canary.discord.com/api/v9/guilds/{self.guild_id}/members/@me",
            f"https://canary.discord.com/api/v9/guilds/{self.guild_id}/members/{bot_id}",
            f"https://discord.com/api/v9/guilds/{self.guild_id}/members/@me",
            f"https://discord.com/api/v9/guilds/{self.guild_id}/members/{bot_id}",
        ]

        body = {}
        if self.display_name:
            body["nick"] = self.display_name
        colors = [color for color in (self.color1, self.color2) if color is not None]
        if colors:
            required_colors = {
                1: (1, 1),  # Solid
                2: (2, 2),  # Gradient
                3: (1, 1),  # Neon
                4: (1, 1),  # Toon
                5: (1, 1),  # Pop
                6: (1, 2),  # Glow, optional accent
            }
            minimum, maximum = required_colors[self.effect_id]
            if not minimum <= len(colors) <= maximum:
                if self.effect_id == 2:
                    message = "Gradient style requires both color selectors."
                elif self.effect_id == 6:
                    message = "Glow style requires at least one color."
                else:
                    message = "This style requires exactly one color."
                return await interaction.followup.send(message, ephemeral=True)
            body["display_name_effect_id"] = self.effect_id
            body["display_name_colors"] = colors
        elif self.font_id:
            return await interaction.followup.send(
                "Select at least one color before applying a name style.",
                ephemeral=True,
            )

        if self.font_id:
            body["display_name_font_id"] = self.font_id

        if not body:
            return await interaction.followup.send("Nothing to update.", ephemeral=True)

        # if bot owner, ask if they want to set guild or global
        if await interaction.client.is_owner(interaction.user):
            owner = True
            view = GlobalOrGuildView(guild_id)
            await interaction.followup.send(view=view, ephemeral=True)
            await view.wait()
            choice = view.choice
            
            if choice == "global":
                urls = [
                    f"https://canary.discord.com/api/v9/users/@me",
                    f"https://canary.discord.com/api/v9/users/{bot_id}",
                    f"https://discord.com/api/v9/users/@me",
                    f"https://discord.com/api/v9/users/{bot_id}"
                ]
        else:
            """
            Note:
             we must assign a value or it will send 
             an error in the console everytime a 
             non-owner uses the command even though 
             the command will still work properly
            """
            owner = False
                
        success, attempts = await try_patch_with_fallbacks(urls, token, body)

        if success:
            if owner:
                await interaction.followup.send(f"Updated successfully in {choice} settings.", ephemeral=True)
            else:
                await interaction.followup.send("Updated successfully.", ephemeral=True)
        else:
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
                "Failed to update profile. Please try again later.", ephemeral=True
            )

    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
            elif isinstance(item, discord.ui.Select):
                item.disabled = True


class SetProfileView(discord.ui.LayoutView):
    def __init__(self, guild_id):
        super().__init__(timeout=180)
        self.guild_id = guild_id

        self.pfp_bytes = None
        self.pfp_content_type = "image/png"
        self.banner_bytes = None
        self.banner_content_type = "image/png"
        self.bio = None
        self.updated_fields = set()

        edit_btn = discord.ui.Button(label="Edit Profile", style=discord.ButtonStyle.primary, custom_id="edit_profile_btn")
        edit_btn.callback = self.edit_profile_callback

        apply_btn = discord.ui.Button(label="Apply", style=discord.ButtonStyle.green, custom_id="apply_btn")
        apply_btn.callback = self.apply_callback

        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### Customize Server Profile"),
            discord.ui.Separator(),
            discord.ui.ActionRow(edit_btn),
            discord.ui.ActionRow(apply_btn),
            accent_colour=discord.Colour(0x5865F2),
        )

        self.add_item(container)

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator or await interaction.client.is_owner(interaction.user)

    async def edit_profile_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ProfileModal(self))

    def build_profile_payload(self):
        """Build only the profile fields changed in this setup flow."""
        body = {}
        if "pfp" in self.updated_fields and self.pfp_bytes:
            body["avatar"] = encode_image(self.pfp_bytes, self.pfp_content_type)
        if "banner" in self.updated_fields and self.banner_bytes:
            body["banner"] = encode_image(self.banner_bytes, self.banner_content_type)
        if "bio" in self.updated_fields and self.bio:
            body["bio"] = self.bio
        return body

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

        body = self.build_profile_payload()

        if not body:
            return await interaction.followup.send("Nothing to update.", ephemeral=True)

        # if bot owner, ask if they want to set guild or global
        if await interaction.client.is_owner(interaction.user):
            owner = True
            guild_id = interaction.guild_id
            view = GlobalOrGuildView(guild_id)
            await interaction.followup.send(view=view, ephemeral=True)
            await view.wait()
            choice = view.choice

            if choice == "global":
                urls = [
                    f"https://canary.discord.com/api/v9/users/@me",
                    f"https://canary.discord.com/api/v9/users/{bot_id}",
                    f"https://discord.com/api/v9/users/@me",
                    f"https://discord.com/api/v9/users/{bot_id}"
                ]
        else:
            owner = False

        success, attempts = await try_patch_with_fallbacks(urls, token, body)

        if success:
            if owner:
                await interaction.followup.send(f"Updated successfully in {choice} settings.", ephemeral=True)
            else:
                await interaction.followup.send("Updated successfully.", ephemeral=True)
        else:
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
                "Failed to update profile. Please try again later.", ephemeral=True
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
