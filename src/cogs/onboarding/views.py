import asyncio
import discord
from discord.ext import commands
from discord.ui import Modal, TextInput

from utils.onboarding.utils import (
    get_config,
    update_config,
    build_welcome_view,
)
from utils.onboarding.config import (
    OnboardingConfig,
    load_all_configs,
    new_menu_id,
    MENU_TYPE_LABELS,
    DEFAULT_MENU_TYPE,
    BUTTON_STYLE_NAMES,
)
from utils.onboarding.captcha import generate_captcha
from utils.ratelimit import role_assign_limiter, welcome_limiter
from config.emojis import get_emoji
from config import links

_pending_verifications: dict[int, dict] = {}

BUTTON_STYLE_MAP = {
    "primary": discord.ButtonStyle.primary,
    "secondary": discord.ButtonStyle.secondary,
    "success": discord.ButtonStyle.success,
    "danger": discord.ButtonStyle.danger,
}


# --------------- UTILITY FUNCTIONS ---------------


def feedback_view(content: str, ok: bool = True) -> discord.ui.LayoutView:
    """Small helper for one-line ephemeral confirmation/error messages."""
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(
            content=f"{get_emoji('icon_tick') if ok else get_emoji('icon_cross')} {content}"
        ),
        accent_colour=discord.Color.green() if ok else discord.Color.red(),
    ))
    return view


def _generate_menu_name(title: str, existing_names: set[str]) -> str:
    """Derive a unique internal name from the menu title so nobody has to type one."""
    slug = "".join(c.lower() if c.isalnum() else "-" for c in title.strip())
    while "--" in slug:
        slug = slug.replace("--", "-")
    slug = slug.strip("-") or "role-menu"
    slug = slug[:40]

    if slug.lower() not in existing_names:
        return slug

    n = 2
    while f"{slug}-{n}".lower() in existing_names:
        n += 1
    return f"{slug}-{n}"


async def check_author(interaction: discord.Interaction, author: discord.abc.User) -> bool:
    """Ensure only the person who ran the setup command can use its components."""
    if interaction.user != author:
        await interaction.response.send_message(
            view=feedback_view("This button can only be used by the person that triggered the command.", ok=False),
            ephemeral=True,
        )
        return False
    return True

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
            required=False,
            default=get_config(guild_id).welcome_color or None
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


class RoleMenuOptionModal(Modal):
    """Shared modal for both adding a new role option and editing an existing one.
    The role itself is always chosen beforehand via a RoleSelect component
    (see RoleMenuAddRoleSelect / EditMenuOptionSelect) — this modal only ever
    collects the presentation details, so nobody has to type a role ID."""

    def __init__(
        self,
        guild_id: int,
        author: discord.Member,
        menu_id: str,
        message: discord.Message,
        role: discord.Role | None = None,
        *,
        edit_index: int | None = None,
        wizard: bool = False,
    ):
        cfg = get_config(guild_id)
        menu = (cfg.role_menus or {}).get(menu_id)
        existing = None
        if edit_index is not None and menu:
            options = menu.get("options") or []
            if 0 <= edit_index < len(options):
                existing = options[edit_index]

        role_label = existing["label"] if existing else (role.name if role else "Role")
        super().__init__(title=(f"Edit Role: {role_label}" if existing else f"Add Role: {role_label}")[:45])
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id
        self.message = message
        self.edit_index = edit_index
        self.wizard = wizard
        self.role_id = existing["role_id"] if existing else (role.id if role else None)

        self.label_input = TextInput(
            label="Label", max_length=100,
            default=existing["label"] if existing else role_label,
        )
        self.desc_input = TextInput(
            label="Description", required=False, max_length=100,
            default=(existing.get("description") if existing else None),
        )
        self.emoji_input = TextInput(
            label="Emoji", required=False,
            default=(existing.get("emoji") if existing else None),
        )
        self.style_input = TextInput(
            label="Button style (primary/secondary/etc)",
            required=False,
            placeholder="Only used for button-type menus",
            default=(existing.get("style") if existing else None),
        )

        for item in (self.label_input, self.desc_input, self.emoji_input, self.style_input):
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if menu is None or self.role_id is None:
            return await interaction.response.send_message(
                view=feedback_view("This role menu no longer exists.", ok=False), ephemeral=True
            )

        style = self.style_input.value.strip().lower() or None
        if style and style not in BUTTON_STYLE_NAMES:
            return await interaction.response.send_message(
                view=feedback_view(f"Style must be one of: {', '.join(BUTTON_STYLE_NAMES)}.", ok=False), ephemeral=True
            )

        options = menu.setdefault("options", [])
        duplicate = any(
            i != self.edit_index and o["role_id"] == self.role_id
            for i, o in enumerate(options)
        )
        if duplicate:
            return await interaction.response.send_message(
                view=feedback_view("That role is already in this menu.", ok=False), ephemeral=True
            )

        entry = {
            "role_id": self.role_id,
            "label": self.label_input.value.strip() or "Role",
            "description": self.desc_input.value.strip() or None,
            "emoji": self.emoji_input.value.strip() or None,
            "style": style,
        }

        if self.edit_index is not None and 0 <= self.edit_index < len(options):
            options[self.edit_index] = entry
            verb = "updated"
        else:
            if len(options) >= 25:
                return await interaction.response.send_message(
                    view=feedback_view("This menu already has the maximum of 25 roles.", ok=False), ephemeral=True
                )
            options.append(entry)
            verb = "added"

        update_config(self.guild_id, cfg)
        await interaction.response.send_message(view=feedback_view(f"Role option {verb}."), ephemeral=True)
        next_view = (
            RoleMenuWizardAddRolesView(self.guild_id, self.author, self.menu_id)
            if self.wizard
            else RoleMenuEditView(self.guild_id, self.author, self.menu_id)
        )
        await self.message.edit(view=next_view, allowed_mentions=discord.AllowedMentions.none())
        await refresh_posted_menu(interaction.client, self.guild_id, self.menu_id)


class CreateRoleMenuModal(Modal, title="Create Role Menu"):
    def __init__(self, guild_id: int, author: discord.Member, message: discord.Message):
        super().__init__()
        self.guild_id = guild_id
        self.author = author
        self.message = message

        self.title_input = TextInput(label="Menu Title", default="Role Selection", max_length=100)
        self.desc_input = TextInput(
            label="Description", style=discord.TextStyle.long, required=False,
            default="Choose your roles below.", max_length=300,
        )
        self.color_input = TextInput(label="Colour (hex, optional)", required=False, placeholder="57F287")

        for item in (self.title_input, self.desc_input, self.color_input):
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)
        if cfg.role_menus is None:
            cfg.role_menus = {}

        if len(cfg.role_menus) >= 25:
            return await interaction.response.send_message(
                view=feedback_view("You've reached the maximum of 25 role menus.", ok=False), ephemeral=True
            )

        color = 0x57F287
        if self.color_input.value.strip():
            try:
                color = int(self.color_input.value.strip().replace("#", ""), 16)
            except ValueError:
                pass

        title = self.title_input.value.strip() or "Role Selection"
        existing_names = {m["name"].lower() for m in cfg.role_menus.values()}
        name = _generate_menu_name(title, existing_names)

        menu_id = new_menu_id()
        cfg.role_menus[menu_id] = {
            "name": name,
            "title": title,
            "description": self.desc_input.value.strip() or "Choose your roles below.",
            "color": color,
            "menu_type": DEFAULT_MENU_TYPE,
            "max_values": None,
            "channel_id": None,
            "message_id": None,
            "options": [],
        }
        update_config(self.guild_id, cfg)

        await interaction.response.send_message(
            view=feedback_view(f"Role menu `{name}` created — let's set it up!"), ephemeral=True
        )
        await self.message.edit(
            view=RoleMenuWizardTypeView(self.guild_id, self.author, menu_id),
            allowed_mentions=discord.AllowedMentions.none(),
        )


class EditMenuInfoModal(Modal, title="Edit Role Menu Info"):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, message: discord.Message):
        super().__init__()
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id
        self.message = message

        cfg = get_config(guild_id)
        menu = cfg.role_menus[menu_id]

        self.name_input = TextInput(label="Internal Name", default=menu["name"], max_length=50)
        self.title_input = TextInput(label="Menu Title", default=menu["title"], max_length=100)
        self.desc_input = TextInput(
            label="Description", style=discord.TextStyle.long, required=False,
            default=menu["description"], max_length=300,
        )
        self.color_input = TextInput(
            label="Colour (hex)", required=False,
            default=f"{menu['color']:06X}" if menu.get("color") is not None else None,
        )

        for item in (self.name_input, self.title_input, self.desc_input, self.color_input):
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if menu is None:
            return await interaction.response.send_message(
                view=feedback_view("This role menu no longer exists.", ok=False), ephemeral=True
            )

        new_name = self.name_input.value.strip()
        if new_name and any(
            mid != self.menu_id and m["name"].lower() == new_name.lower()
            for mid, m in cfg.role_menus.items()
        ):
            return await interaction.response.send_message(
                view=feedback_view(f"A role menu named `{new_name}` already exists.", ok=False), ephemeral=True
            )

        if new_name:
            menu["name"] = new_name
        menu["title"] = self.title_input.value.strip() or menu["title"]
        menu["description"] = self.desc_input.value.strip() or menu["description"]
        if self.color_input.value.strip():
            try:
                menu["color"] = int(self.color_input.value.strip().replace("#", ""), 16)
            except ValueError:
                pass

        update_config(self.guild_id, cfg)
        await interaction.response.send_message(view=feedback_view("Role menu info updated."), ephemeral=True)
        await self.message.edit(
            view=RoleMenuEditView(self.guild_id, self.author, self.menu_id),
            allowed_mentions=discord.AllowedMentions.none(),
        )
        await refresh_posted_menu(interaction.client, self.guild_id, self.menu_id)


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
                content=f"-# **Need help?**\n-# Ask in the [support server]({links.SUPPORT_SERVER}) or check the [documentation]({links.DOCS})"
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


# ------------ ROLE MENU SETUP COMPONENTS ------------
#
# Data model: OnboardingConfig.role_menus is a dict of menu_id -> menu dict.
# A guild can have any number of independently configured role menus, each
# with its own title/description/colour, "menu_type" (dropdown or buttons,
# single or multiple selection), and its own set of role options.
#
# UI flow:
#   RoleMenuManagerView  — lists all menus, lets you create a new one or pick
#                          one to manage via RoleMenuManagerSelect.
#   RoleMenuEditView     — per-menu panel: edit info, change type, add/edit/
#                          remove roles, post/update the live menu, delete it.


async def refresh_posted_menu(bot, guild_id: int, menu_id: str):
    """Re-render a menu's live posted message after its config changes."""
    cfg = get_config(guild_id)
    menu = (cfg.role_menus or {}).get(menu_id)
    if not menu or not menu.get("channel_id") or not menu.get("message_id"):
        return
    channel = bot.get_channel(menu["channel_id"])
    if not channel:
        return
    try:
        msg = await channel.fetch_message(menu["message_id"])
    except (discord.NotFound, discord.Forbidden):
        return
    try:
        await msg.edit(view=RoleMenuView(guild_id, menu_id, cfg=cfg))
    except discord.HTTPException:
        pass


class RoleMenuManagerSelect(discord.ui.Select):
    """Pick an existing role menu to manage."""

    def __init__(self, guild_id: int, author: discord.Member):
        self.guild_id = guild_id
        self.author = author
        cfg = get_config(guild_id)
        menus = cfg.role_menus or {}

        options = [
            discord.SelectOption(
                label=m["name"][:100],
                description=(
                    f"{MENU_TYPE_LABELS.get(m['menu_type'], m['menu_type'])} · "
                    f"{len(m.get('options') or [])} role(s)"
                )[:100],
                value=mid,
            )
            for mid, m in menus.items()
        ][:25]

        if not options:
            options = [discord.SelectOption(label="No role menus yet", value="none")]

        super().__init__(placeholder="Manage a role menu...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        if self.values[0] == "none":
            return await interaction.response.send_message(
                view=feedback_view("Create a role menu first.", ok=False), ephemeral=True
            )
        await interaction.response.edit_message(
            view=RoleMenuEditView(self.guild_id, self.author, self.values[0]),
            allowed_mentions=discord.AllowedMentions.none(),
        )


class CreateRoleMenuBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Create Role Menu", style=discord.ButtonStyle.success, emoji=get_emoji('icon_plus'))
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        await interaction.response.send_modal(
            CreateRoleMenuModal(self.guild_id, self.author, interaction.message)
        )


class BackToManagerBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary, emoji=get_emoji('arrow_left'))
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        await interaction.response.edit_message(
            view=RoleMenuManagerView(self.guild_id, self.author),
            allowed_mentions=discord.AllowedMentions.none(),
        )


class EditMenuInfoBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str):
        super().__init__(label="Edit Info", style=discord.ButtonStyle.primary)
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        await interaction.response.send_modal(
            EditMenuInfoModal(self.guild_id, self.author, self.menu_id, interaction.message)
        )


class ChangeMenuTypeSelect(discord.ui.Select):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, message: discord.Message):
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id
        self.message = message

        cfg = get_config(guild_id)
        current = cfg.role_menus[menu_id]["menu_type"]
        options = [
            discord.SelectOption(label=label, value=key, default=(key == current))
            for key, label in MENU_TYPE_LABELS.items()
        ]
        super().__init__(placeholder="Choose a menu type...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if menu is None:
            return await interaction.response.edit_message(view=feedback_view("This role menu no longer exists.", ok=False))

        menu["menu_type"] = self.values[0]
        update_config(self.guild_id, cfg)

        await interaction.response.edit_message(
            view=feedback_view(f"Menu type set to **{MENU_TYPE_LABELS[self.values[0]]}**.")
        )
        await self.message.edit(
            view=RoleMenuEditView(self.guild_id, self.author, self.menu_id),
            allowed_mentions=discord.AllowedMentions.none(),
        )
        await refresh_posted_menu(interaction.client, self.guild_id, self.menu_id)


class ChangeMenuTypeBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str):
        super().__init__(label="Change Type", style=discord.ButtonStyle.secondary, emoji=get_emoji('icon_shuffle'))
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        message = interaction.message
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"{get_emoji('icon_settings')} Choose the new menu type:"),
            discord.ui.ActionRow(ChangeMenuTypeSelect(self.guild_id, self.author, self.menu_id, message)),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


class RoleMenuAddRoleSelect(discord.ui.RoleSelect):
    """Ephemeral role picker for adding a role option — no typing an ID/mention required.
    Once a role is chosen, a small modal collects the label/description/emoji/style."""

    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, message: discord.Message, *, wizard: bool = False):
        super().__init__(placeholder="Choose a role...", min_values=1, max_values=1)
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id
        self.message = message
        self.wizard = wizard

    async def callback(self, interaction: discord.Interaction):
        role = self.values[0]
        cfg = get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if menu is None:
            return await interaction.response.edit_message(view=feedback_view("This role menu no longer exists.", ok=False))
        if any(o["role_id"] == role.id for o in (menu.get("options") or [])):
            return await interaction.response.edit_message(view=feedback_view(f"{role.mention} is already in this menu.", ok=False))
        if len(menu.get("options") or []) >= 25:
            return await interaction.response.edit_message(view=feedback_view("This menu already has the maximum of 25 roles.", ok=False))

        try:
            await interaction.response.send_modal(
                RoleMenuOptionModal(self.guild_id, self.author, self.menu_id, self.message, role, wizard=self.wizard)
            )
        except Exception as e:
            print(f"Error adding role menu option: {e}")


class AddMenuOptionBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, *, wizard: bool = False):
        super().__init__(label="Add a Role", style=discord.ButtonStyle.success, emoji=get_emoji('icon_plus'))
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id
        self.wizard = wizard

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        cfg = get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if menu and len(menu.get("options") or []) >= 25:
            return await interaction.response.send_message(
                view=feedback_view("This menu already has the maximum of 25 roles.", ok=False), ephemeral=True
            )
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"{get_emoji('icon_settings')} Which role should this option grant? Pick it from the dropdown below."),
            discord.ui.ActionRow(RoleMenuAddRoleSelect(self.guild_id, self.author, self.menu_id, interaction.message, wizard=self.wizard)),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


class EditMenuOptionSelect(discord.ui.Select):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, message: discord.Message):
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id
        self.message = message

        cfg = get_config(guild_id)
        menu = (cfg.role_menus or {}).get(menu_id)
        options_list = (menu.get("options") if menu else []) or []
        options = [
            discord.SelectOption(label=o["label"][:100], description=f"role id: {o['role_id']}", value=str(i))
            for i, o in enumerate(options_list)
        ][:25]
        if not options:
            options = [discord.SelectOption(label="No roles to edit", value="none")]

        super().__init__(placeholder="Choose a role to edit...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            return await interaction.response.edit_message(view=feedback_view("Nothing to edit yet.", ok=False))

        cfg = get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        idx = int(self.values[0])
        options_list = (menu.get("options") if menu else []) or []
        existing = options_list[idx] if 0 <= idx < len(options_list) else None
        role = interaction.guild.get_role(existing["role_id"]) if (existing and interaction.guild) else None

        await interaction.response.send_modal(
            RoleMenuOptionModal(self.guild_id, self.author, self.menu_id, self.message, role, edit_index=idx)
        )


class EditMenuOptionBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str):
        super().__init__(label="Edit Role", style=discord.ButtonStyle.secondary, emoji=get_emoji('icon_edit'))
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        message = interaction.message
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"{get_emoji('icon_settings')} Choose a role option to edit:"),
            discord.ui.ActionRow(EditMenuOptionSelect(self.guild_id, self.author, self.menu_id, message)),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


class RemoveMenuOptionSelect(discord.ui.Select):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, message: discord.Message):
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id
        self.message = message

        cfg = get_config(guild_id)
        menu = (cfg.role_menus or {}).get(menu_id)
        options_list = (menu.get("options") if menu else []) or []
        options = [
            discord.SelectOption(label=o["label"][:100], description=f"role id: {o['role_id']}", value=str(i))
            for i, o in enumerate(options_list)
        ][:25]
        if not options:
            options = [discord.SelectOption(label="No roles to remove", value="none")]

        super().__init__(
            placeholder="Choose role(s) to remove...",
            options=options,
            min_values=1,
            max_values=len(options),
        )

    async def callback(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if menu is None or self.values[0] == "none":
            return await interaction.response.edit_message(view=feedback_view("Nothing to remove.", ok=False))

        indices = sorted({int(v) for v in self.values}, reverse=True)
        options = menu.get("options") or []
        removed = []
        for i in indices:
            if 0 <= i < len(options):
                removed.append(options.pop(i)["label"])

        update_config(self.guild_id, cfg)
        await interaction.response.edit_message(
            view=feedback_view(f"Removed: {', '.join(removed)}" if removed else "Nothing was removed.", ok=bool(removed))
        )
        await self.message.edit(
            view=RoleMenuEditView(self.guild_id, self.author, self.menu_id),
            allowed_mentions=discord.AllowedMentions.none(),
        )
        await refresh_posted_menu(interaction.client, self.guild_id, self.menu_id)


class RemoveMenuOptionBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str):
        super().__init__(label="Remove Role", style=discord.ButtonStyle.danger, emoji=get_emoji('icon_minus'))
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        cfg = get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if not menu or not menu.get("options"):
            return await interaction.response.send_message(
                view=feedback_view("This menu has no roles yet.", ok=False), ephemeral=True
            )
        message = interaction.message
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"{get_emoji('icon_settings')} Choose role option(s) to remove:"),
            discord.ui.ActionRow(RemoveMenuOptionSelect(self.guild_id, self.author, self.menu_id, message)),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


class PostMenuBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str):
        super().__init__(label="Post / Update Here", style=discord.ButtonStyle.primary, emoji="📌")
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        await interaction.response.defer(ephemeral=True, thinking=True)

        cfg = get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if menu is None:
            return await interaction.followup.send(
                view=feedback_view("This role menu no longer exists.", ok=False), ephemeral=True
            )
        if not menu.get("options"):
            return await interaction.followup.send(
                view=feedback_view("Add at least one role before posting.", ok=False), ephemeral=True
            )

        # If it's already posted in this exact channel, edit it in place instead of duplicating.
        if menu.get("channel_id") == interaction.channel.id and menu.get("message_id"):
            try:
                msg = await interaction.channel.fetch_message(menu["message_id"])
                await msg.edit(view=RoleMenuView(self.guild_id, self.menu_id, cfg=cfg))
                return await interaction.followup.send(
                    view=feedback_view("Role menu updated in place."), ephemeral=True
                )
            except discord.NotFound:
                pass  # message was deleted — fall through and re-post

        posted_view = RoleMenuView(self.guild_id, self.menu_id, cfg=cfg)
        msg = await interaction.channel.send(view=posted_view)
        menu["channel_id"] = interaction.channel.id
        menu["message_id"] = msg.id
        update_config(self.guild_id, cfg)

        await interaction.followup.send(view=feedback_view("Role menu posted."), ephemeral=True)
        await interaction.message.edit(
            view=RoleMenuEditView(self.guild_id, self.author, self.menu_id),
            allowed_mentions=discord.AllowedMentions.none(),
        )


class ConfirmDeleteMenuBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, message: discord.Message):
        super().__init__(label="Confirm Delete", style=discord.ButtonStyle.danger, emoji=get_emoji('icon_trash'))
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)
        menu = (cfg.role_menus or {}).pop(self.menu_id, None)
        update_config(self.guild_id, cfg)

        if menu and menu.get("channel_id") and menu.get("message_id") and interaction.guild:
            channel = interaction.guild.get_channel(menu["channel_id"])
            if channel:
                try:
                    old_msg = await channel.fetch_message(menu["message_id"])
                    await old_msg.delete()
                except (discord.NotFound, discord.Forbidden):
                    pass

        name = menu["name"] if menu else "menu"
        await interaction.response.edit_message(view=feedback_view(f"Role menu `{name}` deleted."))
        await self.message.edit(
            view=RoleMenuManagerView(self.guild_id, self.author),
            allowed_mentions=discord.AllowedMentions.none(),
        )


class DeleteMenuBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str):
        super().__init__(label="Delete Menu", style=discord.ButtonStyle.danger, emoji=get_emoji('icon_trash'))
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        message = interaction.message
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_settings')} Are you sure you want to delete this role menu? This cannot be undone."
            ),
            discord.ui.ActionRow(ConfirmDeleteMenuBtn(self.guild_id, self.author, self.menu_id, message)),
            accent_colour=discord.Color.red(),
        ))
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
                content=f"-# **Need help?**\n-# Ask in the [support server]({links.SUPPORT_SERVER}) or check the [documentation]({links.DOCS})"
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

        await interaction.response.defer(ephemeral=True, thinking=True)
        await interaction.user.add_roles(role, reason="Acknowledged rules")
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_tick')} You have acknowledged the rules."
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.followup.send(view=view, ephemeral=True)


def _build_select_options(menu: dict) -> list[discord.SelectOption]:
    options = []
    for o in (menu.get("options") or []):
        options.append(discord.SelectOption(
            label=o["label"][:100],
            description=(o.get("description") or None),
            emoji=(o.get("emoji") or None),
            value=str(o["role_id"]),
        ))
    if not options:
        options = [discord.SelectOption(label="No roles configured", value="none")]
    return options


async def _apply_role_selection(interaction: discord.Interaction, guild_id: int, menu_id: str, keep_role_ids: set[int]):
    """Add/remove roles for the member so their roles among this menu's options match keep_role_ids."""
    await interaction.response.defer(ephemeral=True, thinking=True)

    cfg = get_config(guild_id)
    menu = (cfg.role_menus or {}).get(menu_id)
    if not menu:
        return await interaction.followup.send(
            view=feedback_view("This role menu is no longer configured.", ok=False), ephemeral=True
        )

    member = interaction.user
    all_roles = {int(o["role_id"]) for o in (menu.get("options") or [])}
    to_add, to_remove = [], []

    for rid in all_roles:
        role = interaction.guild.get_role(rid)
        if not role:
            continue
        if rid in keep_role_ids and role not in member.roles:
            to_add.append(role)
        if rid not in keep_role_ids and role in member.roles:
            to_remove.append(role)

    try:
        if to_add:
            await member.add_roles(*to_add, reason=f"Role menu: {menu['name']}")
        if to_remove:
            await member.remove_roles(*to_remove, reason=f"Role menu: {menu['name']}")
    except discord.Forbidden:
        return await interaction.followup.send(
            view=feedback_view("I don't have permission to manage one or more of these roles.", ok=False), ephemeral=True
        )

    await interaction.followup.send(view=feedback_view("Roles updated."), ephemeral=True)


class RoleMenuSelectMulti(discord.ui.Select):
    def __init__(self, guild_id: int, menu_id: str, menu: dict):
        self.guild_id = guild_id
        self.menu_id = menu_id
        options = _build_select_options(menu)
        max_values = menu.get("max_values") or len(options)
        super().__init__(
            placeholder="Select roles...",
            min_values=0,
            max_values=min(max_values, len(options)),
            options=options,
            custom_id=f"rmm_selm_{menu_id}",
        )

    async def callback(self, interaction: discord.Interaction):
        selected = {int(v) for v in self.values if v != "none"}
        await _apply_role_selection(interaction, self.guild_id, self.menu_id, selected)


class RoleMenuSelectSingle(discord.ui.Select):
    def __init__(self, guild_id: int, menu_id: str, menu: dict):
        self.guild_id = guild_id
        self.menu_id = menu_id
        options = _build_select_options(menu)
        super().__init__(
            placeholder="Select a role...",
            min_values=0,
            max_values=1,
            options=options,
            custom_id=f"rmm_sels_{menu_id}",
        )

    async def callback(self, interaction: discord.Interaction):
        chosen = {int(self.values[0])} if self.values and self.values[0] != "none" else set()
        await _apply_role_selection(interaction, self.guild_id, self.menu_id, chosen)


class RoleMenuToggleButton(discord.ui.Button):
    """button_multi: clicking toggles that single role on/off, independent of others."""

    def __init__(self, guild_id: int, menu_id: str, option: dict):
        super().__init__(
            label=option["label"][:80],
            emoji=option.get("emoji") or None,
            style=BUTTON_STYLE_MAP.get(option.get("style"), discord.ButtonStyle.secondary),
            custom_id=f"rmm_btnm_{menu_id}_{option['role_id']}",
        )
        self.guild_id = guild_id
        self.menu_id = menu_id
        self.role_id = option["role_id"]

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        cfg = get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if not menu:
            return await interaction.followup.send(
                view=feedback_view("This role menu is no longer configured.", ok=False), ephemeral=True
            )
        role = interaction.guild.get_role(self.role_id)
        if not role:
            return await interaction.followup.send(view=feedback_view("That role no longer exists.", ok=False), ephemeral=True)

        member = interaction.user
        try:
            if role in member.roles:
                await member.remove_roles(role, reason=f"Role menu: {menu['name']}")
                msg = f"Removed {role.mention}."
            else:
                await member.add_roles(role, reason=f"Role menu: {menu['name']}")
                msg = f"Added {role.mention}."
        except discord.Forbidden:
            return await interaction.followup.send(
                view=feedback_view("I don't have permission to manage that role.", ok=False), ephemeral=True
            )
        await interaction.followup.send(view=feedback_view(msg), ephemeral=True)


class RoleMenuRadioButton(discord.ui.Button):
    """button_single: clicking assigns that role and clears any other role from this menu's group."""

    def __init__(self, guild_id: int, menu_id: str, option: dict, all_role_ids: list[int]):
        super().__init__(
            label=option["label"][:80],
            emoji=option.get("emoji") or None,
            style=BUTTON_STYLE_MAP.get(option.get("style"), discord.ButtonStyle.secondary),
            custom_id=f"rmm_btns_{menu_id}_{option['role_id']}",
        )
        self.guild_id = guild_id
        self.menu_id = menu_id
        self.role_id = option["role_id"]
        self.all_role_ids = all_role_ids

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        cfg = get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if not menu:
            return await interaction.followup.send(
                view=feedback_view("This role menu is no longer configured.", ok=False), ephemeral=True
            )
        role = interaction.guild.get_role(self.role_id)
        if not role:
            return await interaction.followup.send(view=feedback_view("That role no longer exists.", ok=False), ephemeral=True)

        member = interaction.user
        already_has = role in member.roles
        to_remove = [
            r for rid in self.all_role_ids if rid != self.role_id
            for r in [interaction.guild.get_role(rid)] if r and r in member.roles
        ]

        try:
            if to_remove:
                await member.remove_roles(*to_remove, reason=f"Role menu: {menu['name']}")
            if already_has:
                await member.remove_roles(role, reason=f"Role menu: {menu['name']}")
                msg = f"Removed {role.mention}."
            else:
                await member.add_roles(role, reason=f"Role menu: {menu['name']}")
                msg = f"Set your role to {role.mention}."
        except discord.Forbidden:
            return await interaction.followup.send(
                view=feedback_view("I don't have permission to manage one or more of these roles.", ok=False), ephemeral=True
            )
        await interaction.followup.send(view=feedback_view(msg), ephemeral=True)


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
    """The live, persistent menu members interact with. Renders differently
    depending on the menu's configured menu_type."""

    def __init__(self, guild_id: int, menu_id: str, cfg=None):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.menu_id = menu_id

        if cfg is None:
            cfg = get_config(guild_id)
        menu = (cfg.role_menus or {}).get(menu_id) or {}

        title = menu.get("title") or "Role Selection"
        description = menu.get("description") or "Choose your roles below."
        menu_type = menu.get("menu_type", DEFAULT_MENU_TYPE)
        options = menu.get("options") or []

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {title}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=description),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            accent_colour=discord.Colour(menu.get("color") or 0x57F287),
        )

        if not options:
            container.add_item(discord.ui.TextDisplay(content="*No roles have been configured for this menu yet.*"))
        elif menu_type == "select_single":
            container.add_item(discord.ui.ActionRow(RoleMenuSelectSingle(guild_id, menu_id, menu)))
        elif menu_type in ("button_multi", "button_single"):
            all_role_ids = [o["role_id"] for o in options]
            row = discord.ui.ActionRow()
            row_count = 0
            for o in options:
                btn = (
                    RoleMenuToggleButton(guild_id, menu_id, o)
                    if menu_type == "button_multi"
                    else RoleMenuRadioButton(guild_id, menu_id, o, all_role_ids)
                )
                row.add_item(btn)
                row_count += 1
                if row_count == 5:
                    container.add_item(row)
                    row = discord.ui.ActionRow()
                    row_count = 0
            if row_count:
                container.add_item(row)
        else:  # select_multi (default)
            container.add_item(discord.ui.ActionRow(RoleMenuSelectMulti(guild_id, menu_id, menu)))

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
                content=f"-# **Need help?**\n-# Ask in the [support server]({links.SUPPORT_SERVER}) or check the [documentation]({links.DOCS})"
            ),
            accent_colour=discord.Colour(0x5865F2)
        )
        self.add_item(container)


class RoleMenuManagerView(discord.ui.LayoutView):
    """Top-level `.onboarding role-menu` panel: lists all menus for the guild."""

    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(timeout=None)
        self.guild_id = guild_id

        cfg = get_config(guild_id)
        menus = cfg.role_menus or {}

        if menus:
            lines = []
            for m in menus.values():
                posted = f" · posted in <#{m['channel_id']}>" if m.get("channel_id") and m.get("message_id") else ""
                lines.append(
                    f"• **{m['name']}** — {MENU_TYPE_LABELS.get(m['menu_type'], m['menu_type'])} · "
                    f"{len(m.get('options') or [])} role(s){posted}"
                )
            body = "\n".join(lines)
        else:
            body = "No role menus configured yet. Create one to get started."

        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### Role Menus"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    f"Your server has **{len(menus)}** role menu(s).\n{body}\n\n"
                    "-# Click **Create Role Menu** and I'll walk you through the rest step by step — "
                    "everything is done with buttons and dropdowns, no role IDs to type."
                )
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )
        if menus:
            container.add_item(discord.ui.ActionRow(RoleMenuManagerSelect(guild_id, author)))
        container.add_item(discord.ui.ActionRow(CreateRoleMenuBtn(guild_id, author)))
        container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        container.add_item(discord.ui.TextDisplay(
            content=f"-# **Need help?**\n-# Ask in the [support server]({links.SUPPORT_SERVER}) or check the [documentation]({links.DOCS})"
        ))
        container.accent_colour = discord.Colour(0x57F287)
        self.add_item(container)


WIZARD_TYPE_HINTS = {
    "select_multi":  "One dropdown — members can pick several roles at once",
    "select_single": "One dropdown — members can only pick one role",
    "button_multi":  "Buttons — members can toggle any number on or off",
    "button_single": "Buttons — picking one clears any other role in this menu",
}


class RoleMenuWizardTypeSelect(discord.ui.Select):
    """Step 2 of the guided setup: pick a menu type, described in plain language."""

    def __init__(self, guild_id: int, author: discord.Member, menu_id: str):
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id

        cfg = get_config(guild_id)
        current = cfg.role_menus[menu_id]["menu_type"]
        options = [
            discord.SelectOption(label=label, value=key, description=WIZARD_TYPE_HINTS.get(key), default=(key == current))
            for key, label in MENU_TYPE_LABELS.items()
        ]
        super().__init__(placeholder="Choose how members will pick roles...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        cfg = get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if menu is None:
            return await interaction.response.edit_message(view=feedback_view("This role menu no longer exists.", ok=False))

        menu["menu_type"] = self.values[0]
        update_config(self.guild_id, cfg)
        await interaction.response.edit_message(view=RoleMenuWizardAddRolesView(self.guild_id, self.author, self.menu_id))


class RoleMenuWizardTypeView(discord.ui.LayoutView):
    """Step 2 of 3 in the guided setup: choose the menu type."""

    def __init__(self, guild_id: int, author: discord.Member, menu_id: str):
        super().__init__(timeout=None)
        cfg = get_config(guild_id)
        menu = cfg.role_menus[menu_id]

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### Setting up “{menu['name']}” — Step 2 of 3"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content="Nice! Now pick how members will choose their roles from this menu."),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(RoleMenuWizardTypeSelect(guild_id, author, menu_id)),
            accent_colour=discord.Colour(menu.get("color") or 0x57F287),
        )
        self.add_item(container)


class WizardFinishBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str):
        super().__init__(label="Finish Setup", style=discord.ButtonStyle.primary, emoji=get_emoji('icon_tick'))
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        cfg = get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if not menu or not menu.get("options"):
            return await interaction.response.send_message(
                view=feedback_view("Add at least one role before finishing.", ok=False), ephemeral=True
            )
        await interaction.response.edit_message(view=RoleMenuEditView(self.guild_id, self.author, self.menu_id))


class RoleMenuWizardAddRolesView(discord.ui.LayoutView):
    """Step 3 of 3 in the guided setup: add roles via RoleSelect, no typing needed."""

    def __init__(self, guild_id: int, author: discord.Member, menu_id: str):
        super().__init__(timeout=None)
        cfg = get_config(guild_id)
        menu = cfg.role_menus[menu_id]
        options = menu.get("options") or []

        opt_lines = "\n".join(
            f"{i + 1}. {(o.get('emoji') or '').strip()} **{o['label']}** — <@&{o['role_id']}>"
            for i, o in enumerate(options)
        ) or "*No roles added yet.*"

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### Setting up “{menu['name']}” — Step 3 of 3"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    "Add the roles members can choose from. Click **Add a Role**, then pick it from the "
                    "dropdown that appears — no typing required.\n\n"
                    f"**Roles added ({len(options)}/25):**\n{opt_lines}"
                )
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                AddMenuOptionBtn(guild_id, author, menu_id, wizard=True),
                WizardFinishBtn(guild_id, author, menu_id),
            ),
            accent_colour=discord.Colour(menu.get("color") or 0x57F287),
        )
        self.add_item(container)


class RoleMenuEditView(discord.ui.LayoutView):
    """Per-menu management panel: edit info/type, manage roles, post, delete."""

    def __init__(self, guild_id: int, author: discord.Member, menu_id: str):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.menu_id = menu_id

        cfg = get_config(guild_id)
        menu = (cfg.role_menus or {}).get(menu_id)

        if menu is None:
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=f"{get_emoji('icon_cross')} This role menu no longer exists."),
                discord.ui.ActionRow(BackToManagerBtn(guild_id, author)),
                accent_colour=discord.Color.red(),
            )
            self.add_item(container)
            return

        options = menu.get("options") or []
        opt_lines = "\n".join(
            f"{i + 1}. {(o.get('emoji') or '').strip()} **{o['label']}** — <@&{o['role_id']}>"
            + (f" · _{o['description']}_" if o.get("description") else "")
            for i, o in enumerate(options)
        ) or "No roles added yet."

        posted = f"\n📌 Posted in <#{menu['channel_id']}>" if menu.get("channel_id") and menu.get("message_id") else ""

        info = (
            f"**Title:** {menu['title']}\n"
            f"**Description:** {menu['description']}\n"
            f"**Type:** {MENU_TYPE_LABELS.get(menu['menu_type'], menu['menu_type'])}\n"
            f"**Roles ({len(options)}/25):**\n{opt_lines}"
            f"{posted}"
        )

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### Managing: {menu['name']}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=info),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                EditMenuInfoBtn(guild_id, author, menu_id),
                ChangeMenuTypeBtn(guild_id, author, menu_id),
                AddMenuOptionBtn(guild_id, author, menu_id),
            ),
            discord.ui.ActionRow(
                EditMenuOptionBtn(guild_id, author, menu_id),
                RemoveMenuOptionBtn(guild_id, author, menu_id),
            ),
            discord.ui.ActionRow(
                PostMenuBtn(guild_id, author, menu_id),
                DeleteMenuBtn(guild_id, author, menu_id),
                BackToManagerBtn(guild_id, author),
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"-# **Need help?**\n-# Ask in the [support server]({links.SUPPORT_SERVER}) or check the [documentation]({links.DOCS})"
            ),
            accent_colour=discord.Colour(menu.get("color") or 0x57F287),
        )
        self.add_item(container)


# -------------------- PREFIX COMMAND COG --------------------


__all__ = [k for k in list(globals()) if not k.startswith("__")]
