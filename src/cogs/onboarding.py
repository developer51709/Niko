import asyncio
import discord
from discord.ext import commands
from discord.ui import Modal, TextInput

from utils.onboarding_utils import (
    get_config,
    update_config,
    build_welcome_view,
)
from utils.onboarding_config import OnboardingConfig, load_all_configs
from utils.captcha_gen import generate_captcha
from config.emojis import get_emoji

_pending_verifications: dict[int, dict] = {}


# --------------- UTILITY FUNCTIONS ---------------

def parse_role_from_text(text: str, guild: discord.Guild) -> discord.Role | None:
    text = text.strip()

    if text.isdigit():
        return guild.get_role(int(text))

    if text.startswith("<@&") and text.endswith(">"):
        try:
            rid = int(text[3:-1])
            return guild.get_role(rid)
        except ValueError:
            return None

    return discord.utils.get(guild.roles, name=text)


# -------------------- MODALS --------------------

class WelcomeMessageModal(Modal, title="Set Welcome Message"):
    def __init__(self, guild_id: int):
        super().__init__()
        self.guild_id = guild_id

        self.title_input = TextInput(
            label="Title", 
            required=False,
            default=get_config(guild_id).welcome_title or None
        )
        self.desc_input = TextInput(
            label="Description",
            style=discord.TextStyle.long,
            placeholder="Use {user} for mention, {name} for username.",
            required=False,
            default=get_config(guild_id).welcome_description or None
        )
        self.image_input = TextInput(
            label="Image URL", 
            required=False,
            default=get_config(guild_id).welcome_image or None
        )
        self.color_input = TextInput(
            label="Color (hex)", 
            required=False
        )

        self.add_item(self.title_input)
        self.add_item(self.desc_input)
        self.add_item(self.image_input)
        self.add_item(self.color_input)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)

        if self.title_input.value:
            cfg.welcome_title = self.title_input.value
        if self.desc_input.value:
            cfg.welcome_description = self.desc_input.value

        cfg.welcome_image = self.image_input.value or None

        if self.color_input.value:
            try:
                cfg.welcome_color = int(self.color_input.value.replace("#", ""), 16)
            except ValueError:
                pass

        update_config(self.guild_id, cfg)
        await interaction.response.send_message("Welcome message updated.", ephemeral=True)


class RulesModal(Modal, title="Set Rules Text"):
    def __init__(self, guild_id: int):
        super().__init__()
        self.guild_id = guild_id

        self.rules_input = TextInput(
            label="Rules", 
            style=discord.TextStyle.long,
            default=get_config(guild_id).rules_text or ""
        )
        self.add_item(self.rules_input)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)
        cfg.rules_text = self.rules_input.value
        update_config(self.guild_id, cfg)
        # update the existing rules message if it exists
        if cfg.rules_channel and cfg.rules_message_id:
            try:
                channel = interaction.guild.get_channel(cfg.rules_channel)
                if channel:
                    msg = await channel.fetch_message(cfg.rules_message_id)
                    if msg:
                        await msg.edit(view=RulesAcknowledgeView(self.guild_id, cfg=cfg))
            except discord.NotFound:
                pass
        await interaction.response.send_message("Rules updated.", ephemeral=True)


class RoleMenuOptionModal(Modal, title="Add Role Menu Option"):
    def __init__(self, guild_id: int):
        super().__init__()
        self.guild_id = guild_id

        self.role_input = TextInput(label="Role ID or @mention")
        self.label_input = TextInput(label="Label")
        self.desc_input = TextInput(label="Description", required=False)
        self.emoji_input = TextInput(label="Emoji", required=False)

        self.add_item(self.role_input)
        self.add_item(self.label_input)
        self.add_item(self.desc_input)
        self.add_item(self.emoji_input)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)

        raw_role = self.role_input.value.strip()
        label = self.label_input.value.strip()
        desc = self.desc_input.value.strip()
        emoji = self.emoji_input.value.strip()

        role_id = None
        if raw_role.isdigit():
            role_id = int(raw_role)
        elif raw_role.startswith("<@&") and raw_role.endswith(">"):
            try:
                role_id = int(raw_role[3:-1])
            except ValueError:
                pass

        if role_id is None:
            await interaction.response.send_message("Invalid role.", ephemeral=True)
            return

        if cfg.role_menu_options is None:
            cfg.role_menu_options = []

        cfg.role_menu_options.append({
            "role_id": role_id,
            "label": label,
            "description": desc or None,
            "emoji": emoji or None,
        })

        update_config(self.guild_id, cfg)
        await interaction.response.send_message("Role option added.", ephemeral=True)


# ------------ ONBOARDING SETUP BUTTONS ------------

class SetWelcomeMsgBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Set Welcome Message", style=discord.ButtonStyle.primary)
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # author check
        if interaction.user != self.author:
            return await interaction.response.send_message("This button can only be used by the person that triggered the command.", ephemeral=True)
        await interaction.response.send_modal(WelcomeMessageModal(self.guild_id))


class SetWelcomeChannelBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Set Welcome Channel", style=discord.ButtonStyle.secondary)
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # author check
        print(interaction.message)
        if interaction.user != self.author:
            return await interaction.response.send_message("This button can only be used by the person that triggered the command.", ephemeral=True)
        cfg = get_config(self.guild_id)
        cfg.welcome_channel = interaction.channel.id
        update_config(self.guild_id, cfg)
        await interaction.response.send_message(
            f"Welcome channel set to {interaction.channel.mention}.", ephemeral=True
        )


class SetRulesTextBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Set Rules Text", style=discord.ButtonStyle.primary)
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # author check
        if interaction.user != self.author:
            return await interaction.response.send_message("This button can only be used by the person that triggered the command.", ephemeral=True)
        await interaction.response.send_modal(RulesModal(self.guild_id))


class PostRulesBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Post Rules Message Here", style=discord.ButtonStyle.secondary)
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # author check
        if interaction.user != self.author:
            return await interaction.response.send_message("This button can only be used by the person that triggered the command.", ephemeral=True)
        cfg = get_config(self.guild_id)
        cfg.rules_channel = interaction.channel.id

        view = RulesAcknowledgeView(self.guild_id, cfg=cfg)
        msg = await interaction.channel.send(view=view)

        cfg.rules_message_id = msg.id
        update_config(self.guild_id, cfg)

        await interaction.response.send_message("Rules message posted.", ephemeral=True)


class SetRulesRoleBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Set Rules Role", style=discord.ButtonStyle.secondary)
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # author check
        if interaction.user != self.author:
            return await interaction.response.send_message("This button can only be used by the person that triggered the command.", ephemeral=True)
        await interaction.response.send_message(
            "Reply in this channel with a role mention, ID, or name within 60 seconds.",
            ephemeral=True
        )

        def check(msg: discord.Message) -> bool:
            return (
                msg.author == interaction.user
                and msg.channel == interaction.channel
            )

        try:
            msg = await interaction.client.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await interaction.followup.send("Timed out. Try again.", ephemeral=True)
            return

        if not interaction.guild:
            await interaction.followup.send("This must be used in a server.", ephemeral=True)
            return

        role = parse_role_from_text(msg.content, interaction.guild)
        if role is None:
            await interaction.followup.send(
                "Could not find that role. Use a mention, ID, or name.", ephemeral=True
            )
            return

        cfg = get_config(interaction.guild.id)
        cfg.rules_role_id = role.id
        update_config(interaction.guild.id, cfg)

        await interaction.followup.send(f"Rules role set to {role.mention}.", ephemeral=True)


# ----------- AUTOROLE SETUP COMPONENTS -----------

class AddAutoroleSelect(discord.ui.RoleSelect):
    """Ephemeral role picker — adds chosen roles to the autorole list."""
    def __init__(self, guild_id: int):
        super().__init__(
            placeholder="Choose roles to add as autoroles…",
            min_values=1,
            max_values=10,
        )
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)
        if cfg.autorole_ids is None:
            cfg.autorole_ids = []

        added = []
        for role in self.values:
            if role.id not in cfg.autorole_ids:
                cfg.autorole_ids.append(role.id)
                added.append(role.mention)

        update_config(self.guild_id, cfg)
        if added:
            await interaction.response.send_message(
                f"Added {', '.join(added)} as autorole(s).", ephemeral=True, allowed_mentions=discord.AllowedMentions.none()
            )
        else:
            await interaction.response.send_message(
                "Those roles are already in the autorole list.", ephemeral=True
            )


class AddAutoroleView(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=60)
        self.add_item(AddAutoroleSelect(guild_id))


class RemoveAutoroleSelect(discord.ui.Select):
    """Ephemeral select of current autoroles — removes chosen ones."""
    def __init__(self, guild_id: int, guild: discord.Guild):
        self.guild_id = guild_id
        cfg = get_config(guild_id)
        options = []
        for rid in (cfg.autorole_ids or []):
            role = guild.get_role(rid)
            label = role.name if role else f"Unknown Role ({rid})"
            options.append(discord.SelectOption(label=label, value=str(rid)))

        if not options:
            options = [discord.SelectOption(label="No autoroles configured", value="none")]

        super().__init__(
            placeholder="Choose autoroles to remove…",
            min_values=1,
            max_values=len(options),
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)
        if cfg.autorole_ids is None:
            cfg.autorole_ids = []

        removed = []
        for val in self.values:
            if val == "none":
                continue
            rid = int(val)
            if rid in cfg.autorole_ids:
                cfg.autorole_ids.remove(rid)
                removed.append(f"<@&{rid}>")

        update_config(self.guild_id, cfg)
        if removed:
            await interaction.response.send_message(
                f"Removed {', '.join(removed)} from autoroles.", ephemeral=True, allowed_mentions=discord.AllowedMentions.none()
            )
        else:
            await interaction.response.send_message(
                "Nothing was removed.", ephemeral=True
            )


class RemoveAutoroleView(discord.ui.View):
    def __init__(self, guild_id: int, guild: discord.Guild):
        super().__init__(timeout=60)
        self.add_item(RemoveAutoroleSelect(guild_id, guild))


class AddAutoroleBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Add Autorole", style=discord.ButtonStyle.primary, emoji="➕")
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message(
                "This button can only be used by the person that triggered the command.", ephemeral=True
            )
        await interaction.response.send_message(
            "Select one or more roles to automatically assign to new members:",
            view=AddAutoroleView(self.guild_id),
            ephemeral=True,
        )


class RemoveAutoroleBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, guild: discord.Guild):
        super().__init__(label="Remove Autorole", style=discord.ButtonStyle.secondary, emoji="➖")
        self.guild_id = guild_id
        self.author = author
        self.guild = guild

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message(
                "This button can only be used by the person that triggered the command.", ephemeral=True
            )
        cfg = get_config(self.guild_id)
        if not cfg.autorole_ids:
            return await interaction.response.send_message(
                "No autoroles are configured yet.", ephemeral=True
            )
        await interaction.response.send_message(
            "Select autoroles to remove:",
            view=RemoveAutoroleView(self.guild_id, self.guild),
            ephemeral=True,
        )


class ClearAutorolesBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Clear All", style=discord.ButtonStyle.danger, emoji="🗑️")
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message(
                "This button can only be used by the person that triggered the command.", ephemeral=True
            )
        cfg = get_config(self.guild_id)
        cfg.autorole_ids = []
        update_config(self.guild_id, cfg)
        await interaction.response.send_message("All autoroles cleared.", ephemeral=True)


class AutoroleSetupView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, author: discord.Member, guild: discord.Guild):
        super().__init__(timeout=None)
        self.guild_id = guild_id

        cfg = get_config(guild_id)
        role_ids = cfg.autorole_ids or []

        if role_ids:
            role_lines = "\n".join(
                f"• {guild.get_role(rid).mention if guild.get_role(rid) else f'Unknown role `{rid}`'}"
                for rid in role_ids
            )
            current_text = f"**Current autoroles ({len(role_ids)}):**\n{role_lines}"
        else:
            current_text = "No autoroles configured yet.\nAdd roles with the buttons below."

        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### Autorole Configuration"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content="Autoroles are assigned to every new member the moment they join the server."
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=current_text),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                AddAutoroleBtn(guild_id, author),
                RemoveAutoroleBtn(guild_id, author, guild),
                ClearAutorolesBtn(guild_id, author),
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content="-# **Need help?**\n-# Ask in the [support server](https://dsc.gg/astral-haven) or check the [documentation](https://developer51709.github.io/Niko/docs)"
            ),
            accent_colour=discord.Colour(0xFEE75C),
        )
        self.add_item(container)


class ConfigureAutorolesBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Configure Autoroles", style=discord.ButtonStyle.secondary, emoji="🎭")
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message(
                "This button can only be used by the person that triggered the command.", ephemeral=True
            )
        await interaction.response.send_message(
            view=AutoroleSetupView(self.guild_id, self.author, interaction.guild),
            ephemeral=False,
        )


# ------------ ROLE MENU SETUP BUTTONS ------------

class AddRoleOptionBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Add Role Option", style=discord.ButtonStyle.primary)
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # author check
        if interaction.user != self.author:
            return await interaction.response.send_message("This button can only be used by the person that triggered the command.", ephemeral=True)
        await interaction.response.send_modal(RoleMenuOptionModal(self.guild_id))


class PostRoleMenuBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Post Role Menu Here", style=discord.ButtonStyle.secondary)
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # author check
        if interaction.user != self.author:
            return await interaction.response.send_message("This button can only be used by the person that triggered the command.", ephemeral=True)
        cfg = get_config(self.guild_id)

        if not cfg.role_menu_options:
            await interaction.response.send_message("No role options configured.", ephemeral=True)
            return

        cfg.role_menu_channel = interaction.channel.id

        view = RoleMenuView(self.guild_id, cfg=cfg)
        msg = await interaction.channel.send(view=view)

        cfg.role_menu_message_id = msg.id
        update_config(self.guild_id, cfg)

        await interaction.response.send_message("Role menu posted.", ephemeral=True)


# --------- CAPTCHA VERIFY BUTTON & PANEL ---------

class CaptchaVerifyButton(discord.ui.Button):
    def __init__(self, guild_id: int):
        super().__init__(
            label="Verify",
            style=discord.ButtonStyle.success,
            emoji="✅",
            custom_id=f"captcha_verify_{guild_id}",
        )
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        guild_id = self.guild_id

        if user.id in _pending_verifications:
            await interaction.response.send_message(
                "You already have a captcha pending. Please check your DMs.", ephemeral=True
            )
            return

        code, img_bytes = generate_captcha()
        _pending_verifications[user.id] = {
            "guild_id": guild_id,
            "code": code,
            "attempts": 0,
        }

        try:
            dm = await user.create_dm()
            file = discord.File(img_bytes, filename="captcha.png")
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content="### Human Verification"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content="Type the code shown in the image below to verify you are human."
                ),
                discord.ui.MediaGallery(
                    discord.MediaGalleryItem(
                        media=file
                    )
                ),
                discord.ui.TextDisplay(
                    content="-# The code is **case-insensitive**. You have **3 attempts**."
                )
            )
            view.add_item(container)
            await dm.send(view=view, file=file)
            await interaction.response.send_message(
                "A captcha has been sent to your DMs. Please check and reply with the code.",
                ephemeral=True,
            )
        except discord.Forbidden:
            _pending_verifications.pop(user.id, None)
            await interaction.response.send_message(
                "I couldn't send you a DM. Please enable DMs from server members and try again.",
                ephemeral=True,
            )


class CaptchaPanelView(discord.ui.LayoutView):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id

        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### Human Verification"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    "Before you can access this server, you need to prove you're human.\n\n"
                    "Click **Verify** below and the bot will send you a DM with a captcha image. "
                    "Reply to the DM with the code shown in the image."
                )
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(CaptchaVerifyButton(guild_id)),
            accent_colour=discord.Colour(0x57F287),
        )
        self.add_item(container)


# ------------ CAPTCHA SETUP COMPONENTS ------------

class CaptchaAddRolesSelect(discord.ui.RoleSelect):
    def __init__(self, guild_id: int):
        super().__init__(
            placeholder="Choose roles to ADD after verification…",
            min_values=1,
            max_values=10,
        )
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)
        if cfg.captcha_add_role_ids is None:
            cfg.captcha_add_role_ids = []
        added = []
        for role in self.values:
            if role.id not in cfg.captcha_add_role_ids:
                cfg.captcha_add_role_ids.append(role.id)
                added.append(role.mention)
        update_config(self.guild_id, cfg)
        if added:
            await interaction.response.send_message(
                f"Will **add** {', '.join(added)} on verification.", ephemeral=True
            )
        else:
            await interaction.response.send_message("Those roles are already configured.", ephemeral=True)


class CaptchaAddRolesView(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=60)
        self.add_item(CaptchaAddRolesSelect(guild_id))


class CaptchaRemoveRolesSelect(discord.ui.RoleSelect):
    def __init__(self, guild_id: int):
        super().__init__(
            placeholder="Choose roles to REMOVE after verification…",
            min_values=1,
            max_values=10,
        )
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)
        if cfg.captcha_remove_role_ids is None:
            cfg.captcha_remove_role_ids = []
        added = []
        for role in self.values:
            if role.id not in cfg.captcha_remove_role_ids:
                cfg.captcha_remove_role_ids.append(role.id)
                added.append(role.mention)
        update_config(self.guild_id, cfg)
        if added:
            await interaction.response.send_message(
                f"Will **remove** {', '.join(added)} on verification.", ephemeral=True
            )
        else:
            await interaction.response.send_message("Those roles are already configured.", ephemeral=True)


class CaptchaRemoveRolesView(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=60)
        self.add_item(CaptchaRemoveRolesSelect(guild_id))


class CaptchaSetupView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, author: discord.Member, guild: discord.Guild):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.author = author
        self.guild = guild

        cfg = get_config(guild_id)

        status = f"{get_emoji('icon_tick')} Enabled" if cfg.captcha_enabled else f"{get_emoji('icon_cross')} Disabled"
        channel_text = (
            f"<#{cfg.captcha_channel_id}>" if cfg.captcha_channel_id else "Not set"
        )
        add_roles = (
            ", ".join(f"<@&{r}>" for r in cfg.captcha_add_role_ids)
            if cfg.captcha_add_role_ids
            else "None"
        )
        remove_roles = (
            ", ".join(f"<@&{r}>" for r in cfg.captcha_remove_role_ids)
            if cfg.captcha_remove_role_ids
            else "None"
        )
        kick_text = "Yes" if cfg.captcha_kick_on_fail else "No"

        info = (
            f"**Status:** {status}\n"
            f"**Channel:** {channel_text}\n"
            f"**Roles to add:** {add_roles}\n"
            f"**Roles to remove:** {remove_roles}\n"
            f"**Kick on 3 failed attempts:** {kick_text}"
        )

        toggle_label = "Disable Captcha" if cfg.captcha_enabled else "Enable Captcha"
        toggle_style = discord.ButtonStyle.danger if cfg.captcha_enabled else discord.ButtonStyle.success

        class ToggleCaptchaBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(label=toggle_label, style=toggle_style, emoji=get_emoji("icon_lock"))
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    return await interaction.response.send_message(
                        "This button can only be used by the person that triggered the command.", ephemeral=True
                    )
                c = get_config(self_inner.guild_id)
                c.captcha_enabled = not c.captcha_enabled
                update_config(self_inner.guild_id, c)
                state = "enabled" if c.captcha_enabled else "disabled"
                await interaction.response.send_message(f"Captcha verification **{state}**.", ephemeral=True)

        class PostPanelBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(label="Post Verify Panel Here", style=discord.ButtonStyle.primary, emoji="📌")
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    return await interaction.response.send_message(
                        "This button can only be used by the person that triggered the command.", ephemeral=True
                    )
                c = get_config(self_inner.guild_id)
                c.captcha_channel_id = interaction.channel.id
                panel_view = CaptchaPanelView(self_inner.guild_id)
                msg = await interaction.channel.send(view=panel_view)
                c.captcha_panel_message_id = msg.id
                update_config(self_inner.guild_id, c)
                interaction.client.add_view(panel_view, message_id=msg.id)
                await interaction.response.send_message(
                    "Verification panel posted in this channel.", ephemeral=True
                )

        class SetAddRolesBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(label="Set Roles to Add", style=discord.ButtonStyle.secondary, emoji="➕")
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    return await interaction.response.send_message(
                        "This button can only be used by the person that triggered the command.", ephemeral=True
                    )
                await interaction.response.send_message(
                    "Select roles to **add** to members after they pass verification:",
                    view=CaptchaAddRolesView(self_inner.guild_id),
                    ephemeral=True,
                )

        class SetRemoveRolesBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(label="Set Roles to Remove", style=discord.ButtonStyle.secondary, emoji="➖")
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    return await interaction.response.send_message(
                        "This button can only be used by the person that triggered the command.", ephemeral=True
                    )
                await interaction.response.send_message(
                    "Select roles to **remove** from members after they pass verification:",
                    view=CaptchaRemoveRolesView(self_inner.guild_id),
                    ephemeral=True,
                )

        class ToggleKickBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(label="Toggle Kick on Fail", style=discord.ButtonStyle.secondary, emoji="🚫")
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    return await interaction.response.send_message(
                        "This button can only be used by the person that triggered the command.", ephemeral=True
                    )
                c = get_config(self_inner.guild_id)
                c.captcha_kick_on_fail = not c.captcha_kick_on_fail
                update_config(self_inner.guild_id, c)
                state = "enabled" if c.captcha_kick_on_fail else "disabled"
                await interaction.response.send_message(
                    f"Kick on failed captcha **{state}**.", ephemeral=True
                )

        class ClearAddRolesBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(label="Clear Add Roles", style=discord.ButtonStyle.danger, emoji="🗑️")
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    return await interaction.response.send_message(
                        "This button can only be used by the person that triggered the command.", ephemeral=True
                    )
                c = get_config(self_inner.guild_id)
                c.captcha_add_role_ids = []
                update_config(self_inner.guild_id, c)
                await interaction.response.send_message("Cleared all roles to add.", ephemeral=True)

        class ClearRemoveRolesBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(label="Clear Remove Roles", style=discord.ButtonStyle.danger, emoji="🗑️")
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    return await interaction.response.send_message(
                        "This button can only be used by the person that triggered the command.", ephemeral=True
                    )
                c = get_config(self_inner.guild_id)
                c.captcha_remove_role_ids = []
                update_config(self_inner.guild_id, c)
                await interaction.response.send_message("Cleared all roles to remove.", ephemeral=True)

        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### Captcha Verification Setup"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=info),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(ToggleCaptchaBtn(), PostPanelBtn()),
            discord.ui.ActionRow(SetAddRolesBtn(), SetRemoveRolesBtn()),
            discord.ui.ActionRow(ToggleKickBtn(), ClearAddRolesBtn(), ClearRemoveRolesBtn()),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content="-# **Need help?**\n-# Ask in the [support server](https://dsc.gg/astral-haven) or check the [documentation](https://developer51709.github.io/Niko/docs)"
            ),
            accent_colour=discord.Colour(0x57F287),
        )
        self.add_item(container)


class ConfigureCaptchaBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Configure Captcha", style=discord.ButtonStyle.secondary, emoji="🔐")
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message(
                "This button can only be used by the person that triggered the command.", ephemeral=True
            )
        await interaction.response.send_message(
            view=CaptchaSetupView(self.guild_id, self.author, interaction.guild),
            ephemeral=False,
        )


# -------------------- AGREE BUTTON & ROLE SELECT --------------------

class AgreeButton(discord.ui.Button):
    def __init__(self, guild_id: int):
        super().__init__(
            label="I Agree",
            style=discord.ButtonStyle.success,
            custom_id=f"rules_agree_{guild_id}"
        )
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)

        if not cfg.rules_role_id:
            await interaction.response.send_message("No role configured.", ephemeral=True)
            return

        role = interaction.guild.get_role(cfg.rules_role_id)
        if not role:
            await interaction.response.send_message("Configured role no longer exists.", ephemeral=True)
            return

        await interaction.user.add_roles(role, reason="Acknowledged rules")
        await interaction.response.send_message("You have acknowledged the rules.", ephemeral=True)


class RoleMenuSelect(discord.ui.Select):
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        cfg = get_config(guild_id)

        options = []
        if cfg.role_menu_options:
            for opt in cfg.role_menu_options:
                options.append(
                    discord.SelectOption(
                        label=opt["label"],
                        description=opt.get("description"),
                        emoji=opt.get("emoji"),
                        value=str(opt["role_id"]),
                    )
                )

        if not options:
            options = [discord.SelectOption(label="No roles configured", value="none")]

        super().__init__(
            placeholder="Select roles...",
            min_values=0,
            max_values=len(options),
            options=options,
            custom_id=f"role_menu_select_{guild_id}",
        )

    async def callback(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)
        member = interaction.user

        selected = {int(v) for v in self.values if v != "none"}
        all_roles = {int(opt["role_id"]) for opt in (cfg.role_menu_options or [])}

        to_add = []
        to_remove = []

        for rid in all_roles:
            role = interaction.guild.get_role(rid)
            if not role:
                continue
            if rid in selected and role not in member.roles:
                to_add.append(role)
            if rid not in selected and role in member.roles:
                to_remove.append(role)

        if to_add:
            await member.add_roles(*to_add)
        if to_remove:
            await member.remove_roles(*to_remove)

        await interaction.response.send_message("Roles updated.", ephemeral=True)


# -------------------- PERSISTENT VIEWS --------------------

class RulesAcknowledgeView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, cfg=None):
        super().__init__(timeout=None)
        self.guild_id = guild_id

        if cfg is None:
            cfg = get_config(guild_id)

        rules_text = cfg.rules_text or "No rules have been set yet."

        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### Server Rules"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=rules_text),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content="-# Click the button below to acknowledge the rules."),
            discord.ui.ActionRow(AgreeButton(guild_id)),
            accent_colour=discord.Colour(0xED4245)
        )
        self.add_item(container)


class RoleMenuView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, cfg=None):
        super().__init__(timeout=None)
        self.guild_id = guild_id

        if cfg is None:
            cfg = get_config(guild_id)

        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### Role Selection"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content="Choose your roles below."),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(RoleMenuSelect(guild_id)),
            accent_colour=discord.Colour(0x57F287)
        )
        self.add_item(container)


# -------------------- SETUP VIEWS --------------------

class OnboardingSetupView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, author: discord.Member, prefix: str = "."):
        super().__init__(timeout=None)
        self.guild_id = guild_id

        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### Onboarding Setup"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content="Use the buttons below to configure the onboarding system for your server."
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                SetWelcomeMsgBtn(guild_id, author),
                SetWelcomeChannelBtn(guild_id, author),
            ),
            discord.ui.ActionRow(
                SetRulesTextBtn(guild_id, author),
                PostRulesBtn(guild_id, author),
                SetRulesRoleBtn(guild_id, author),
            ),
            discord.ui.ActionRow(
                ConfigureAutorolesBtn(guild_id, author),
                ConfigureCaptchaBtn(guild_id, author),
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"-# **Need help?**\n-# Ask in the [support server](https://dsc.gg/astral-haven) or check the [documentation](https://developer51709.github.io/Niko/docs)"
            ),
            accent_colour=discord.Colour(0x5865F2)
        )
        self.add_item(container)


class RoleMenuSetupView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, author: discord.Member, prefix: str = "."):
        super().__init__(timeout=None)
        self.guild_id = guild_id

        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### Role Menu Setup"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content="Add role options then post the menu to a channel."),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                AddRoleOptionBtn(guild_id, author),
                PostRoleMenuBtn(guild_id, author),
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"-# **Need help?**\n-# Ask in the [support server](https://dsc.gg/astral-haven) or check the [documentation](https://developer51709.github.io/Niko/docs)"
            ),
            accent_colour=discord.Colour(0x57F287)
        )
        self.add_item(container)


# -------------------- PREFIX COMMAND COG --------------------

class Onboarding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="onboarding", help="Manage server onboarding")
    async def onboarding(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            prefix = self.bot.command_prefix if isinstance(self.bot.command_prefix, str) else self.bot.command_prefix[0]
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(content="### Server Onboarding"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content="Setup onboarding for your server to help new members get started without requiring an entire staff team to welcome them!"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content="**Onboarding Commands**"),
                discord.ui.TextDisplay(
                    content=(
                        f"**`{prefix}onboarding setup`** — Setup onboarding for the server.\n"
                        f"**`{prefix}onboarding role-menu`** — Setup role menu for the server.\n"
                        f"**`{prefix}onboarding autoroles`** — Configure auto-assigned roles on join.\n"
                        f"**`{prefix}onboarding captcha`** — Configure captcha human verification."
                    )
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"-# **Need help?**\n-# Ask in the [support server](https://dsc.gg/astral-haven) or check the [documentation](https://developer51709.github.io/Niko/docs)"
                )
            )
            view.add_item(container)
            await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    @onboarding.command(name="setup")
    @commands.has_permissions(administrator=True)
    async def onboarding_setup(self, ctx: commands.Context):
        """Setup onboarding for the server."""
        prefix = self.bot.command_prefix if isinstance(self.bot.command_prefix, str) else self.bot.command_prefix[0]
        await ctx.send(view=OnboardingSetupView(ctx.guild.id, ctx.author, prefix=prefix), allowed_mentions=discord.AllowedMentions.none())

    @onboarding.command(name="role-menu")
    @commands.has_permissions(administrator=True)
    async def onboarding_role_menu(self, ctx: commands.Context):
        """Setup role menu for the server."""
        prefix = self.bot.command_prefix if isinstance(self.bot.command_prefix, str) else self.bot.command_prefix[0]
        await ctx.send(view=RoleMenuSetupView(ctx.guild.id, ctx.author, prefix=prefix), allowed_mentions=discord.AllowedMentions.none())

    @onboarding.command(name="autoroles")
    @commands.has_permissions(administrator=True)
    async def onboarding_autoroles(self, ctx: commands.Context):
        """Configure which roles are automatically given to new members on join."""
        await ctx.send(view=AutoroleSetupView(ctx.guild.id, ctx.author, ctx.guild), allowed_mentions=discord.AllowedMentions.none())

    @onboarding.command(name="captcha")
    @commands.has_permissions(administrator=True)
    async def onboarding_captcha(self, ctx: commands.Context):
        """Configure captcha verification for the server."""
        await ctx.send(view=CaptchaSetupView(ctx.guild.id, ctx.author, ctx.guild), allowed_mentions=discord.AllowedMentions.none())

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is not None:
            return
        if message.author.bot:
            return

        user_id = message.author.id
        pending = _pending_verifications.get(user_id)
        if pending is None:
            return

        guess = message.content.strip().upper()
        correct = pending["code"].upper()

        if guess == correct:
            _pending_verifications.pop(user_id, None)
            guild_id = pending["guild_id"]
            guild = self.bot.get_guild(guild_id)
            cfg = get_config(guild_id)

            if guild is None:
                await message.channel.send("Verification passed! However, I could not find the server to apply roles.")
                return

            member = guild.get_member(user_id)
            if member is None:
                await message.channel.send("Verification passed! However, I could not find you in the server.")
                return

            applied = []
            removed = []

            if cfg.captcha_add_role_ids:
                for rid in cfg.captcha_add_role_ids:
                    role = guild.get_role(rid)
                    if role:
                        try:
                            await member.add_roles(role, reason="Captcha verification passed")
                            applied.append(role.name)
                        except discord.Forbidden:
                            pass

            if cfg.captcha_remove_role_ids:
                for rid in cfg.captcha_remove_role_ids:
                    role = guild.get_role(rid)
                    if role and role in member.roles:
                        try:
                            await member.remove_roles(role, reason="Captcha verification passed")
                            removed.append(role.name)
                        except discord.Forbidden:
                            pass

            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('icon_tick')} Verification complete!"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content="You have been verified."
                )
            )
            if applied:
                container.add_item(discord.ui.TextDisplay(f"Roles added: {', '.join(applied)}"))
            if removed:
                container.add_item(discord.ui.TextDisplay(f"Roles removed: {', '.join(removed)}"))
            view.add_item(container)

            await message.channel.send(view=view)

            # Log captcha pass
            logger = self.bot.get_cog("ServerLogger")
            if logger and guild and member:
                pass_body = (
                    f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                    f"**Result:** Passed\n"
                    f"**Roles Added:** {', '.join(applied) if applied else 'None'}\n"
                    f"**Roles Removed:** {', '.join(removed) if removed else 'None'}"
                )
                await logger.log_event(
                    guild, "captcha", "Captcha Passed", pass_body,
                    target_id=member.id
                )

        else:
            pending["attempts"] += 1
            attempts_left = 3 - pending["attempts"]

            if attempts_left <= 0:
                _pending_verifications.pop(user_id, None)
                guild_id = pending["guild_id"]
                guild = self.bot.get_guild(guild_id)
                cfg = get_config(guild_id) if guild else None

                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"### {get_emoji('icon_cross')} Verification failed!"
                    ),
                    discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                    discord.ui.TextDisplay(
                        content="You have failed the captcha verification."
                    )
                )
                if cfg and cfg.captcha_kick_on_fail:
                    container.add_item(discord.ui.TextDisplay("You have been kicked from the server."))
                else:
                    container.add_item(discord.ui.TextDisplay(content="Return to the server and click **Verify** again to get a new captcha."))
                view.add_item(container)
                await message.channel.send(view=view)

                will_kick = guild and cfg and cfg.captcha_kick_on_fail

                # Log captcha fail / kick
                logger = self.bot.get_cog("ServerLogger")
                if logger and guild:
                    log_title = "Captcha Kicked" if will_kick else "Captcha Failed"
                    fail_body = (
                        f"**User:** <@{user_id}> (ID: `{user_id}`)\n"
                        f"**Result:** {'Failed all 3 attempts and kicked' if will_kick else 'Failed all 3 attempts'}"
                    )
                    await logger.log_event(
                        guild, "captcha", log_title, fail_body,
                        target_id=user_id, action_key=log_title
                    )

                if will_kick:
                    member = guild.get_member(user_id)
                    if member:
                        try:
                            await member.kick(reason="Failed captcha verification (3 wrong attempts)")
                        except discord.Forbidden:
                            pass
            else:
                code, img_bytes = generate_captcha()
                pending["code"] = code
                file = discord.File(img_bytes, filename="captcha.png")
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"### {get_emoji('icon_cross')} Incorrect."
                    ),
                    discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                    discord.ui.TextDisplay(
                        content=f"You have **{attempts_left}** attempt(s) left. Here is a new captcha:"
                    ),
                    discord.ui.MediaGallery(
                        discord.MediaGalleryItem(
                            media=file
                        )
                    )
                )
                view.add_item(container)
                await message.channel.send(view=view, file=file)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        cfg = get_config(member.guild.id)

        # ── Autoroles ─────────────────────────────
        if cfg.autorole_ids:
            roles_to_add = [
                member.guild.get_role(rid)
                for rid in cfg.autorole_ids
                if member.guild.get_role(rid)
            ]
            if roles_to_add:
                try:
                    await member.add_roles(*roles_to_add, reason="Onboarding autoroles")
                except discord.Forbidden:
                    pass  # bot lacks permission — silently skip

        # ── Welcome message ───────────────────────
        if not cfg.welcome_channel:
            return

        channel = member.guild.get_channel(cfg.welcome_channel)
        if not channel:
            return

        view = build_welcome_view(cfg, member)
        # allow user and role mentions but not everyone and here
        welcome_mentions = discord.AllowedMentions(everyone=False, roles=True, users=True)
        await channel.send(view=view, allowed_mentions=welcome_mentions)

async def setup(bot):
    await bot.add_cog(Onboarding(bot))

    for guild_id, cfg in load_all_configs():
        if cfg.rules_channel and cfg.rules_message_id:
            bot.add_view(RulesAcknowledgeView(guild_id), message_id=cfg.rules_message_id)

        if cfg.role_menu_channel and cfg.role_menu_message_id:
            bot.add_view(RoleMenuView(guild_id), message_id=cfg.role_menu_message_id)

        if cfg.captcha_channel_id and cfg.captcha_panel_message_id:
            bot.add_view(CaptchaPanelView(guild_id), message_id=cfg.captcha_panel_message_id)
