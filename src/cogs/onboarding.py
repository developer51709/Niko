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
from utils.ratelimit import role_assign_limiter, welcome_limiter
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

async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    """
    Resolve the primary prefix for the current context/interaction.

    Supports:
    - Static string prefix
    - Static list/tuple of prefixes
    - Dynamic prefix function: command_prefix(bot, message) -> list[str]
    """
    raw = bot.command_prefix

    # Static prefix (string)
    if isinstance(raw, str):
        return raw

    # Static list/tuple of prefixes
    if isinstance(raw, (list, tuple)):
        return raw[0]

    # Dynamic prefix function
    try:
        # Context: has .message
        msg = getattr(ctx_or_interaction, "message", None)

        # Interaction: use the original message if present
        if msg is None and isinstance(ctx_or_interaction, discord.Interaction):
            msg = ctx_or_interaction.message

        if msg is None:
            return "!"

        prefixes = raw(bot, msg)
        if isinstance(prefixes, (list, tuple)) and prefixes:
            return prefixes[0]
    except Exception:
        pass

    # Fallback prefix if everything else fails
    return "."


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
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_tick')} Welcome message updated."
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)


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
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_tick')} Rules text updated."
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)


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
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} Invalid role."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)

        if cfg.role_menu_options is None:
            cfg.role_menu_options = []

        cfg.role_menu_options.append({
            "role_id": role_id,
            "label": label,
            "description": desc or None,
            "emoji": emoji or None,
        })

        update_config(self.guild_id, cfg)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_tick')} Role option added."
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)


# ------------ ONBOARDING SETUP BUTTONS ------------

class SetWelcomeMsgBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Set Welcome Message", style=discord.ButtonStyle.primary)
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # author check
        if interaction.user != self.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
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
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        cfg = get_config(self.guild_id)
        cfg.welcome_channel = interaction.channel.id
        update_config(self.guild_id, cfg)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_tick')} Welcome channel set to {interaction.channel.mention}."
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)


class SetRulesTextBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Set Rules Text", style=discord.ButtonStyle.primary)
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # author check
        if interaction.user != self.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        await interaction.response.send_modal(RulesModal(self.guild_id))


class PostRulesBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Post Rules Message Here", style=discord.ButtonStyle.secondary)
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # author check
        if interaction.user != self.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        cfg = get_config(self.guild_id)
        cfg.rules_channel = interaction.channel.id

        view = RulesAcknowledgeView(self.guild_id, cfg=cfg)
        msg = await interaction.channel.send(view=view)

        cfg.rules_message_id = msg.id
        update_config(self.guild_id, cfg)

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_tick')} Rules message posted."
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)


class SetRulesRoleBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Set Rules Role", style=discord.ButtonStyle.secondary)
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # author check
        if interaction.user != self.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_settings')} Reply in this channel with a role mention, ID, or name within 60 seconds."
            )
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)

        def check(msg: discord.Message) -> bool:
            return (
                msg.author == interaction.user
                and msg.channel == interaction.channel
            )

        try:
            msg = await interaction.client.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} Timed out. Try again."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.followup.send(view=view, ephemeral=True)

        if not interaction.guild:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} This must be used in a server."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.followup.send(view=view, ephemeral=True)

        role = parse_role_from_text(msg.content, interaction.guild)
        if role is None:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} Could not find that role. Use a mention, ID, or name."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.followup.send(view=view, ephemeral=True)

        cfg = get_config(interaction.guild.id)
        cfg.rules_role_id = role.id
        update_config(interaction.guild.id, cfg)

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_tick')} Rules role set to {role.mention}."
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.followup.send(view=view, ephemeral=True)


# ----------- AUTOROLE SETUP COMPONENTS -----------

class AddAutoroleSelect(discord.ui.RoleSelect):
    """Ephemeral role picker — adds chosen roles to the autorole list."""
    def __init__(self, guild_id: int, message: discord.Message):
        super().__init__(
            placeholder="Choose roles to add as autoroles…",
            min_values=1,
            max_values=10,
        )
        self.guild_id = guild_id
        self.message = message

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
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_tick')} Added {', '.join(added)} as autorole(s)."
                ),
                accent_colour=discord.Color.green()
            )
            view.add_item(container)
            # edit the interaction message
            await interaction.response.edit_message(
                view=view, allowed_mentions=discord.AllowedMentions.none()
            )
            # update the setup panel
            await self.message.edit(view=AutoroleSetupView(self.guild_id, interaction.user, interaction.guild), allowed_mentions=discord.AllowedMentions.none())
        else:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} Those roles are already in the autorole list."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            await interaction.response.edit_message(
                view=view
            )


class AddAutoroleView(discord.ui.ActionRow):
    def __init__(self, guild_id: int, message: discord.Message):
        super().__init__()
        self.add_item(AddAutoroleSelect(guild_id, message))


class RemoveAutoroleSelect(discord.ui.Select):
    """Ephemeral select of current autoroles — removes chosen ones."""
    def __init__(self, guild_id: int, guild: discord.Guild, message: discord.Message):
        self.guild_id = guild_id
        self.message = message
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
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_tick')} Removed {', '.join(removed)} from autoroles."
                ),
                accent_colour=discord.Color.green()
            )
            view.add_item(container)
            await interaction.response.edit_message(
                view=view, allowed_mentions=discord.AllowedMentions.none()
            )
            await self.message.edit(view=AutoroleSetupView(self.guild_id, interaction.user, interaction.guild), allowed_mentions=discord.AllowedMentions.none())
        else:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} Nothing was removed."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            await interaction.response.edit_message(view=view)


class RemoveAutoroleView(discord.ui.ActionRow):
    def __init__(self, guild_id: int, guild: discord.Guild, message: discord.Message):
        super().__init__()
        self.add_item(RemoveAutoroleSelect(guild_id, guild, message))


class AddAutoroleBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Add Autorole", style=discord.ButtonStyle.primary, emoji="➕")
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        message = interaction.message
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_settings')} Select one or more roles to automatically assign to new members:"
            ),
            AddAutoroleView(self.guild_id, message)
        )
        view.add_item(container)
        await interaction.response.send_message(
            view=view, ephemeral=True,
        )


class RemoveAutoroleBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, guild: discord.Guild):
        super().__init__(label="Remove Autorole", style=discord.ButtonStyle.secondary, emoji="➖")
        self.guild_id = guild_id
        self.author = author
        self.guild = guild

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        cfg = get_config(self.guild_id)
        if not cfg.autorole_ids:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} No autoroles are configured yet."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)

        message = interaction.message
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_settings')} Select autoroles to remove:"
            ),
            RemoveAutoroleView(self.guild_id, self.guild, message)
        )
        view.add_item(container)
        await interaction.response.send_message(
            view=view, ephemeral=True,
        )


class ClearAutorolesBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Clear All", style=discord.ButtonStyle.danger, emoji=get_emoji('icon_trash'))
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        cfg = get_config(self.guild_id)
        cfg.autorole_ids = []
        update_config(self.guild_id, cfg)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_tick')} All autoroles cleared."
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)
        await interaction.message.edit(view=AutoroleSetupView(self.guild_id, interaction.user, interaction.guild))


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
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        await interaction.response.send_message(
            view=AutoroleSetupView(self.guild_id, self.author, interaction.guild),
            ephemeral=False,
            allowed_mentions=discord.AllowedMentions.none()
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
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        await interaction.response.send_modal(RoleMenuOptionModal(self.guild_id))


class PostRoleMenuBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Post Role Menu Here", style=discord.ButtonStyle.secondary)
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # author check
        if interaction.user != self.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        cfg = get_config(self.guild_id)

        if not cfg.role_menu_options:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} No role options configured."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)

        cfg.role_menu_channel = interaction.channel.id

        view = RoleMenuView(self.guild_id, cfg=cfg)
        msg = await interaction.channel.send(view=view)

        cfg.role_menu_message_id = msg.id
        update_config(self.guild_id, cfg)

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_tick')} Role menu posted."
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)


# --------- CAPTCHA VERIFY BUTTON & PANEL ---------

class CaptchaVerifyButton(discord.ui.Button):
    def __init__(self, guild_id: int):
        super().__init__(
            label="Verify",
            style=discord.ButtonStyle.success,
            emoji=get_emoji('icon_tick'),
            custom_id=f"captcha_verify_{guild_id}",
        )
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        guild_id = self.guild_id

        # check if captcha is enabled
        cfg = get_config(guild_id)
        if not cfg.captcha_enabled:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} Captcha verification is currently disabled for this server."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
            
        if user.id in _pending_verifications:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} You already have a captcha pending. Please check your DMs."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)

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
            sent_view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_tick')} A captcha has been sent to your DMs. Please check and reply with the code."
                ),
                accent_colour=discord.Color.green()
            )
            sent_view.add_item(container)
            await interaction.response.send_message(view=sent_view, ephemeral=True)
        except discord.Forbidden:
            _pending_verifications.pop(user.id, None)
            error_view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} I couldn't send you a DM. Please enable DMs from server members and try again."
                ),
                accent_colour=discord.Color.red()
            )
            error_view.add_item(container)
            await interaction.response.send_message(view=error_view, ephemeral=True)


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
    def __init__(self, guild_id: int, message: discord.Message):
        super().__init__(
            placeholder="Choose roles to ADD after verification…",
            min_values=1,
            max_values=10,
        )
        self.guild_id = guild_id
        self.message = message

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
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_tick')} Will **add** {', '.join(added)} on verification."
                ),
                accent_colour=discord.Color.green()
            )
            view.add_item(container)
            await interaction.response.edit_message(view=view)
            await self.message.edit(view=CaptchaSetupView(self.guild_id, interaction.user, interaction.guild))
        else:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} Those roles are already configured."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            await interaction.response.edit_message(view=view)


class CaptchaAddRolesView(discord.ui.ActionRow):
    def __init__(self, guild_id: int, message: discord.Message):
        super().__init__()
        self.add_item(CaptchaAddRolesSelect(guild_id, message))


class CaptchaRemoveRolesSelect(discord.ui.RoleSelect):
    def __init__(self, guild_id: int, message: discord.Message):
        super().__init__(
            placeholder="Choose roles to REMOVE after verification…",
            min_values=1,
            max_values=10,
        )
        self.guild_id = guild_id
        self.message = message

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
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_tick')} Will **remove** {', '.join(added)} on verification."
                ),
                accent_colour=discord.Color.green()
            )
            view.add_item(container)
            await interaction.response.edit_message(view=view)
            await self.message.edit(view=CaptchaSetupView(self.guild_id, interaction.user, interaction.guild))
        else:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} Those roles are already configured."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            await interaction.response.edit_message(view=view)


class CaptchaRemoveRolesView(discord.ui.ActionRow):
    def __init__(self, guild_id: int, message: discord.Message):
        super().__init__()
        self.add_item(CaptchaRemoveRolesSelect(guild_id, message))


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
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(view=view, ephemeral=True)
                c = get_config(self_inner.guild_id)
                c.captcha_enabled = not c.captcha_enabled
                update_config(self_inner.guild_id, c)
                # state = "enabled" if c.captcha_enabled else "disabled"
                # emoji = get_emoji("icon_tick") if state == "enabled" else get_emoji("icon_cross")
                # color = discord.Color.green() if state == "enabled" else discord.Color.red()
                # view = discord.ui.LayoutView()
                # container = discord.ui.Container(
                #     discord.ui.TextDisplay(
                #         content=f"{emoji} Captcha verification **{state}**."
                #     ),
                #     accent_colour=color
                # )
                # view.add_item(container)
                # await interaction.response.send_message(view=view, ephemeral=True)
                await interaction.response.defer()
                await interaction.message.edit(view=CaptchaSetupView(self_inner.guild_id, interaction.user, interaction.guild))

        class PostPanelBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(label="Post Verify Panel Here", style=discord.ButtonStyle.primary, emoji="📌")
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(view=view, ephemeral=True)
                c = get_config(self_inner.guild_id)
                c.captcha_channel_id = interaction.channel.id
                panel_view = CaptchaPanelView(self_inner.guild_id)
                msg = await interaction.channel.send(view=panel_view)
                c.captcha_panel_message_id = msg.id
                update_config(self_inner.guild_id, c)
                interaction.client.add_view(panel_view, message_id=msg.id)
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_tick')} Verification panel posted in this channel."
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await interaction.response.send_message(view=view, ephemeral=True)
                await interaction.message.edit(view=CaptchaSetupView(self_inner.guild_id, interaction.user, interaction.guild))

        class SetAddRolesBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(label="Set Roles to Add", style=discord.ButtonStyle.secondary, emoji="➕")
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(view=view, ephemeral=True)
                message = interaction.message
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_settings')} Select roles to **add** to members after they pass verification:"
                    ),
                    CaptchaAddRolesView(self_inner.guild_id, message)
                )
                view.add_item(container)
                await interaction.response.send_message(view=view, ephemeral=True)

        class SetRemoveRolesBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(label="Set Roles to Remove", style=discord.ButtonStyle.secondary, emoji="➖")
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(view=view, ephemeral=True)
                message = interaction.message
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_settings')} Select roles to **remove** from members after they pass verification:"
                    ),
                    CaptchaRemoveRolesView(self_inner.guild_id, message)
                )
                view.add_item(container)
                await interaction.response.send_message(view=view, ephemeral=True)

        class ToggleKickBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(label="Toggle Kick on Fail", style=discord.ButtonStyle.secondary, emoji="🚫")
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(view=view, ephemeral=True)
                c = get_config(self_inner.guild_id)
                c.captcha_kick_on_fail = not c.captcha_kick_on_fail
                update_config(self_inner.guild_id, c)
                state = "enabled" if c.captcha_kick_on_fail else "disabled"
                emoji = get_emoji("icon_tick") if state == "enabled" else get_emoji("icon_cross")
                color = discord.Color.green() if state == "enabled" else discord.Color.red()
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{emoji} Kick on failed captcha **{state}**."
                    ),
                    accent_colour=color
                )
                view.add_item(container)
                await interaction.response.send_message(view=view, ephemeral=True)
                await interaction.message.edit(view=CaptchaSetupView(self_inner.guild_id, interaction.user, interaction.guild))

        class ClearAddRolesBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(label="Clear Add Roles", style=discord.ButtonStyle.danger, emoji=get_emoji("icon_trash"))
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(view=view, ephemeral=True)
                c = get_config(self_inner.guild_id)
                c.captcha_add_role_ids = []
                update_config(self_inner.guild_id, c)
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_tick')} Cleared all roles to add."
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await interaction.response.send_message(view=view, ephemeral=True)
                await interaction.message.edit(view=CaptchaSetupView(self_inner.guild_id, interaction.user, interaction.guild))

        class ClearRemoveRolesBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(label="Clear Remove Roles", style=discord.ButtonStyle.danger, emoji=get_emoji("icon_trash"))
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(view=view, ephemeral=True)
                c = get_config(self_inner.guild_id)
                c.captcha_remove_role_ids = []
                update_config(self_inner.guild_id, c)
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_tick')} Cleared all roles to remove."
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await interaction.response.send_message(view=view, ephemeral=True)
                await interaction.message.edit(view=CaptchaSetupView(self_inner.guild_id, interaction.user, interaction.guild))

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
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} This button can only be used by the person that triggered the command."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
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
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} No role configured."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)

        role = interaction.guild.get_role(cfg.rules_role_id)
        if not role:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} Configured role no longer exists."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)

        await interaction.user.add_roles(role, reason="Acknowledged rules")
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_tick')} You have acknowledged the rules."
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)


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

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_tick')} Roles updated."
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)


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
            prefix = await _resolve_prefix(self.bot, ctx)
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
        prefix = await _resolve_prefix(self.bot, ctx)
        await ctx.send(view=OnboardingSetupView(ctx.guild.id, ctx.author, prefix=prefix), allowed_mentions=discord.AllowedMentions.none())

    @onboarding.command(name="role-menu")
    @commands.has_permissions(administrator=True)
    async def onboarding_role_menu(self, ctx: commands.Context):
        """Setup role menu for the server."""
        prefix = await _resolve_prefix(self.bot, ctx)
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
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_tick')} Verification passed! However, I could not find the server to apply roles."
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                return await message.channel.send(view=view)

            member = guild.get_member(user_id)
            if member is None:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_tick')} Verification passed! However, I could not find you in the server."
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                return await message.channel.send(view=view)

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
                # Queue role assignments per-guild so a join wave doesn't
                # blow through Discord's role-edit rate limit.
                await role_assign_limiter.acquire(member.guild.id)
                try:
                    await member.add_roles(*roles_to_add, reason="Onboarding autoroles")
                except discord.Forbidden:
                    pass  # bot lacks permission — silently skip
                except discord.HTTPException:
                    pass

        # ── Welcome message ───────────────────────
        if not cfg.welcome_channel:
            return

        channel = member.guild.get_channel(cfg.welcome_channel)
        if not channel:
            return

        view = build_welcome_view(cfg, member)
        # allow user and role mentions but not everyone and here
        welcome_mentions = discord.AllowedMentions(everyone=False, roles=True, users=True)
        # Throttle welcome sends per-guild so raids can't spam the channel.
        await welcome_limiter.acquire(member.guild.id)
        try:
            await channel.send(view=view, allowed_mentions=welcome_mentions)
        except discord.HTTPException:
            pass

async def setup(bot):
    await bot.add_cog(Onboarding(bot))

    for guild_id, cfg in load_all_configs():
        if cfg.rules_channel and cfg.rules_message_id:
            bot.add_view(RulesAcknowledgeView(guild_id), message_id=cfg.rules_message_id)

        if cfg.role_menu_channel and cfg.role_menu_message_id:
            bot.add_view(RoleMenuView(guild_id), message_id=cfg.role_menu_message_id)

        if cfg.captcha_channel_id and cfg.captcha_panel_message_id:
            bot.add_view(CaptchaPanelView(guild_id), message_id=cfg.captcha_panel_message_id)
