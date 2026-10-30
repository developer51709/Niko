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

from utils.command_locales import command_texts
from utils.i18n import make_flat_msg
from utils.locales import load_locales

CMDS = command_texts(__package__)
MESSAGES = load_locales(__package__, "customization")
msg = make_flat_msg(MESSAGES, {
    "tick": get_emoji("tick"),
    "cross": get_emoji("cross"),
})

#: Font and colour-style choices, keyed to the Discord ``display_name_*_id``
#: values. Labels live in the locale catalogue so each language can name them.
FONT_OPTIONS = (
    ("font_sakura", "3"),
    ("font_jellybean", "4"),
    ("font_modern", "6"),
    ("font_medieval", "7"),
    ("font_8bit", "8"),
    ("font_vampyre", "10"),
    ("font_gg_sans", "11"),
    ("font_tempo", "12"),
)

EFFECT_OPTIONS = (
    ("effect_solid", "effect_solid_description", "1"),
    ("effect_gradient", "effect_gradient_description", "2"),
    ("effect_neon", "effect_neon_description", "3"),
    ("effect_toon", "effect_toon_description", "4"),
    ("effect_pop", "effect_pop_description", "5"),
    ("effect_glow", "effect_glow_description", "6"),
)

COLOUR_OPTIONS = (
    ("colour_white", "16777215"),
    ("colour_black", "0"),
    ("colour_blurple", "5793266"),
    ("colour_green", "5763719"),
    ("colour_red", "15548997"),
    ("colour_yellow", "16705372"),
    ("colour_pink", "16711935"),
    ("colour_purple", "8388736"),
    ("colour_blue", "5865"),
    ("colour_gold", "16766720"),
    ("colour_cyan", "65535"),
)

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

async def try_patch_with_fallbacks(urls, token, payload, extra_headers=None, timeout=10, proxy_manager=None):
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
                    request = (
                        proxy_manager.relay_or_request(
                            session,
                            "PATCH",
                            url,
                            headers=headers,
                            data=json.dumps(payload),
                            timeout=aiohttp.ClientTimeout(total=timeout),
                        )
                        if proxy_manager is not None
                        else session.patch(
                            url,
                            headers=headers,
                            data=json.dumps(payload),
                            timeout=aiohttp.ClientTimeout(total=timeout),
                        )
                    )
                    async with await request as r:
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

class DisplayNameModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title=msg(view.ctx, "display_name_modal_title"))
        self.view = view
        self.name = discord.ui.TextInput(
            label=msg(view.ctx, "display_name_label"), max_length=32)
        self.add_item(self.name)

    async def on_submit(self, interaction: discord.Interaction):
        self.view.display_name = str(self.name)
        await interaction.response.send_message(
            msg(interaction, "display_name_set"), ephemeral=True)


class BioModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title=msg(view.ctx, "bio_modal_title"))
        self.view = view
        self.bio_input = discord.ui.TextInput(
            label=msg(view.ctx, "bio_new_label"),
            style=discord.TextStyle.paragraph, max_length=190)
        self.add_item(self.bio_input)

    async def on_submit(self, interaction: discord.Interaction):
        self.view.bio = str(self.bio_input)
        await interaction.response.send_message(
            msg(interaction, "bio_updated"), ephemeral=True)


class ProfileModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title=msg(view.ctx, "profile_modal_title"))
        self.view = view

        # FileUpload is native in discord.py 2.7+. FileInput is retained as a
        # compatibility fallback for the project's older-library patch.
        upload_cls = getattr(discord.ui, "FileUpload", discord.ui.FileInput)
        self.pfp = upload_cls(custom_id="profile_pfp", required=False, max_values=1)
        self.banner = upload_cls(custom_id="profile_banner", required=False, max_values=1)
        self.bio = discord.ui.TextInput(
            label=msg(view.ctx, "bio_label"),
            style=discord.TextStyle.paragraph,
            max_length=190,
            required=False,
        )
        self.add_item(discord.ui.Label(
            text=msg(view.ctx, "profile_picture"),
            description=msg(view.ctx, "profile_picture_description"),
            component=self.pfp,
        ))
        self.add_item(discord.ui.Label(
            text=msg(view.ctx, "profile_banner"),
            description=msg(view.ctx, "profile_banner_description"),
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
                key = ("profile_picture_not_image" if target == "pfp_bytes"
                       else "profile_banner_not_image")
                await interaction.response.send_message(
                    msg(interaction, key), ephemeral=True)
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
            msg(interaction, "profile_saved"), ephemeral=True)


class FontSelect(discord.ui.Select):
    def __init__(self, ctx):
        options = [
            discord.SelectOption(label=msg(ctx, key), value=value)
            for key, value in FONT_OPTIONS
        ]
        super().__init__(placeholder=msg(ctx, "font_placeholder"), options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.font_id = int(self.values[0])
        await interaction.response.defer()


class EffectSelect(discord.ui.Select):
    def __init__(self, ctx):
        options = [
            discord.SelectOption(
                label=msg(ctx, label_key),
                value=value,
                description=msg(ctx, description_key),
            )
            for label_key, description_key, value in EFFECT_OPTIONS
        ]
        super().__init__(placeholder=msg(ctx, "effect_placeholder"), options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.effect_id = int(self.values[0])
        await interaction.response.defer()


class ColorSelect(discord.ui.Select):
    def __init__(self, label, target, ctx):
        self.target = target
        options = [
            discord.SelectOption(label=msg(ctx, key), value=value)
            for key, value in COLOUR_OPTIONS
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
    def __init__(self, guild_id, ctx):
        super().__init__(timeout=180)
        self.guild_id = guild_id
        self.ctx = ctx

        self.choice = None

        global_btn = discord.ui.Button(
            label=msg(ctx, "scope_global_button"),
            style=discord.ButtonStyle.primary, custom_id="global_btn")
        global_btn.callback = self.global_callback

        guild_btn = discord.ui.Button(
            label=msg(ctx, "scope_guild_button"),
            style=discord.ButtonStyle.primary, custom_id="guild_btn")
        guild_btn.callback = self.guild_callback

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=msg(ctx, "setname_heading")),
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
    def __init__(self, guild_id, ctx):
        super().__init__(timeout=180)
        self.guild_id = guild_id
        self.ctx = ctx

        self.display_name = None
        self.font_id = None
        self.effect_id = 2  # Preserve the existing gradient default.
        self.color1 = None
        self.color2 = None

        set_name_btn = discord.ui.Button(
            label=msg(ctx, "set_display_name_button"),
            style=discord.ButtonStyle.primary, custom_id="set_name_btn")
        set_name_btn.callback = self.set_name_callback

        apply_btn = discord.ui.Button(
            label=msg(ctx, "apply_button"),
            style=discord.ButtonStyle.green, custom_id="apply_btn")
        apply_btn.callback = self.apply_callback

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=msg(ctx, "setname_heading")),
            discord.ui.Separator(),
            discord.ui.ActionRow(set_name_btn),
            discord.ui.ActionRow(FontSelect(ctx)),
            discord.ui.ActionRow(EffectSelect(ctx)),
            discord.ui.ActionRow(ColorSelect(msg(ctx, "colour_first"), "color1", ctx)),
            discord.ui.ActionRow(ColorSelect(msg(ctx, "colour_second"), "color2", ctx)),
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
                    key = "colour_need_gradient"
                elif self.effect_id == 6:
                    key = "colour_need_glow"
                else:
                    key = "colour_need_one"
                return await interaction.followup.send(
                    msg(interaction, key), ephemeral=True)
            body["display_name_effect_id"] = self.effect_id
            body["display_name_colors"] = colors
        elif self.font_id:
            return await interaction.followup.send(
                msg(interaction, "colour_need_any"),
                ephemeral=True,
            )

        if self.font_id:
            body["display_name_font_id"] = self.font_id

        if not body:
            return await interaction.followup.send(
                msg(interaction, "nothing_to_update"), ephemeral=True)

        # if bot owner, ask if they want to set guild or global
        if await interaction.client.is_owner(interaction.user):
            owner = True
            view = GlobalOrGuildView(guild_id, interaction)
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
                
        success, attempts = await try_patch_with_fallbacks(
            urls, token, body, proxy_manager=getattr(interaction.client, "discord_proxy", None)
        )

        if success:
            if owner:
                await interaction.followup.send(
                    msg(interaction, "updated_in_scope",
                        scope=msg(interaction, f"scope_{choice}")),
                    ephemeral=True)
            else:
                await interaction.followup.send(
                    msg(interaction, "updated"), ephemeral=True)
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
                msg(interaction, "update_failed"), ephemeral=True
            )

    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
            elif isinstance(item, discord.ui.Select):
                item.disabled = True


class SetProfileView(discord.ui.LayoutView):
    def __init__(self, guild_id, ctx):
        super().__init__(timeout=180)
        self.guild_id = guild_id
        self.ctx = ctx

        self.pfp_bytes = None
        self.pfp_content_type = "image/png"
        self.banner_bytes = None
        self.banner_content_type = "image/png"
        self.bio = None
        self.updated_fields = set()

        edit_btn = discord.ui.Button(
            label=msg(ctx, "edit_profile_button"),
            style=discord.ButtonStyle.primary, custom_id="edit_profile_btn")
        edit_btn.callback = self.edit_profile_callback

        apply_btn = discord.ui.Button(
            label=msg(ctx, "apply_button"),
            style=discord.ButtonStyle.green, custom_id="apply_btn")
        apply_btn.callback = self.apply_callback

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=msg(ctx, "profile_heading")),
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
            return await interaction.response.send_message(
                msg(interaction, "internal_error"), ephemeral=True)

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
            return await interaction.followup.send(
                msg(interaction, "nothing_to_update"), ephemeral=True)

        # if bot owner, ask if they want to set guild or global
        if await interaction.client.is_owner(interaction.user):
            owner = True
            guild_id = interaction.guild_id
            view = GlobalOrGuildView(guild_id, interaction)
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

        success, attempts = await try_patch_with_fallbacks(
            urls, token, body, proxy_manager=getattr(interaction.client, "discord_proxy", None)
        )

        if success:
            if owner:
                await interaction.followup.send(
                    msg(interaction, "updated_in_scope",
                        scope=msg(interaction, f"scope_{choice}")),
                    ephemeral=True)
            else:
                await interaction.followup.send(
                    msg(interaction, "updated"), ephemeral=True)
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
                msg(interaction, "update_failed"), ephemeral=True
            )

# ---------- Cog ----------

class Customization(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setname", help=CMDS.help("setname"))
    @commands.has_permissions(administrator=True)
    async def setname(self, ctx):
        view = SetNameView(ctx.guild.id, ctx)
        await ctx.reply(view=view)

    @commands.command(name="setprofile", help=CMDS.help("setprofile"))
    @commands.has_permissions(administrator=True)
    async def setprofile(self, ctx):
        view = SetProfileView(ctx.guild.id, ctx)
        await ctx.reply(view=view)


async def setup(bot):
    await bot.add_cog(Customization(bot))
