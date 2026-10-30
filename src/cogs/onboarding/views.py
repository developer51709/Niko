import asyncio
import discord
from discord.ext import commands
from discord.ui import Modal, TextInput

from utils.onboarding.utils import (
    get_config,
    update_config,
    build_welcome_view,
    build_goodbye_view,
)
from utils.onboarding.config import (
    OnboardingConfig,
    load_all_configs,
    migrate_json_files,
    new_menu_id,
    build_role_menu,
    build_role_menu_option,
    MENU_TYPE_LABELS,
    DEFAULT_MENU_TYPE,
    BUTTON_STYLE_NAMES,
    format_hex_color,
    normalize_hex_color,
)
from utils.onboarding.captcha import generate_captcha, new_captcha_code
from utils.verification import links as verification_links
from utils.verification import modes as verification_modes
from utils.verification import service as verification_service
from utils.verification import store as verification_store
from utils.ratelimit import role_assign_limiter, welcome_limiter
from utils.prefix_manager import resolve_prefix
from utils.i18n import make_flat_msg
from utils.locales import load_locales
from config.emojis import get_emoji
from config import links

MESSAGES = load_locales(__package__, "views")
_MSG = make_flat_msg(MESSAGES, {
    "tick": get_emoji("tick"),
    "cross": get_emoji("cross"),
})


def _t(locale, key: str, **kwargs) -> str:
    """Translated string for a context, interaction or guild (``None`` = en)."""
    return _MSG(locale, key, **kwargs)


def _menu_type_label(locale, key: str) -> str:
    """A role-menu type's display name ("Dropdown — Multiple Roles")."""
    return _t(locale, f"menu_type_{key}")


def _mode_label(locale, mode: str) -> str:
    """A verification mode's display name."""
    return _t(locale, f"mode_{mode}_label")


def _mode_description(locale, mode: str) -> str:
    """One sentence on what pressing Verify does in this mode."""
    return _t(locale, f"mode_{mode}_description")


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
            content=f"{get_emoji('tick') if ok else get_emoji('cross')} {content}"
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
            view=feedback_view(_t(interaction, "not_allowed"), ok=False),
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
    """Return the primary prefix for this context, honouring a dynamic prefix."""
    return await resolve_prefix(bot, ctx_or_interaction)


# -------------------- MODALS --------------------

class WelcomeMessageModal(Modal, title="Set Welcome Message"):
    def __init__(self, guild_id: int, cfg: OnboardingConfig, locale=None):
        super().__init__()
        # A modal's title is class-level on Modal, so it is set per instance to
        # follow the guild's language.
        self.title = _t(locale, "welcome_modal_title")
        self.guild_id = guild_id

        self.title_input = TextInput(
            label=_t(locale, "field_title"),
            required=False,
            default=cfg.welcome_title or None
        )
        self.desc_input = TextInput(
            label=_t(locale, "field_description"),
            style=discord.TextStyle.long,
            placeholder=_t(locale, "field_description_hint"),
            required=False,
            default=cfg.welcome_description or None
        )
        self.image_input = TextInput(
            label=_t(locale, "field_image_url"),
            required=False,
            default=cfg.welcome_image or None
        )
        self.color_input = TextInput(
            label=_t(locale, "field_color"),
            required=False,
            placeholder=_t(locale, "field_color_hint"),
            default=format_hex_color(cfg.welcome_color),
        )

        self.add_item(self.title_input)
        self.add_item(self.desc_input)
        self.add_item(self.image_input)
        self.add_item(self.color_input)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = await get_config(self.guild_id)

        if self.title_input.value:
            cfg.welcome_title = self.title_input.value
        if self.desc_input.value:
            cfg.welcome_description = self.desc_input.value

        cfg.welcome_image = self.image_input.value or None

        color_text = self.color_input.value.strip()
        if color_text:
            color = normalize_hex_color(color_text)
            if color is None:
                return await interaction.response.send_message(
                    view=feedback_view(
                        _t(interaction, "color_invalid", example="`5865F2` or `#5865F2`"),
                        ok=False,
                    ),
                    ephemeral=True,
                )
            cfg.welcome_color = color
        else:
            cfg.welcome_color = None

        await update_config(self.guild_id, cfg)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('tick')} {_t(interaction, 'welcome_updated')}"
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)


class RulesModal(Modal, title="Set Rules Text"):
    def __init__(self, guild_id: int, cfg: OnboardingConfig, locale=None):
        super().__init__()
        self.title = _t(locale, "rules_modal_title")
        self.guild_id = guild_id

        self.rules_input = TextInput(
            label=_t(locale, "field_rules"),
            style=discord.TextStyle.long,
            default=cfg.rules_text or ""
        )
        self.add_item(self.rules_input)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = await get_config(self.guild_id)
        cfg.rules_text = self.rules_input.value
        await update_config(self.guild_id, cfg)
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
                content=f"{get_emoji('tick')} {_t(interaction, 'rules_updated')}"
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
        cfg: OnboardingConfig | None = None,
        edit_index: int | None = None,
        wizard: bool = False,
        locale=None,
    ):
        self._preload_cfg = cfg
        cfg = cfg  # callers fetch the config (async) and pass it in
        menu = (cfg.role_menus if cfg else {}).get(menu_id) if cfg else None
        existing = None
        if edit_index is not None and menu:
            options = menu.get("options") or []
            if 0 <= edit_index < len(options):
                existing = options[edit_index]

        role_label = existing["label"] if existing else (
            role.name if role else _t(locale, "fallback_role_label")
        )
        super().__init__(title=(
            _t(locale, "role_option_edit_title", role=role_label)
            if existing else _t(locale, "role_option_add_title", role=role_label)
        )[:45])
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id
        self.message = message
        self.edit_index = edit_index
        self.wizard = wizard
        self.role_id = existing["role_id"] if existing else (role.id if role else None)

        self.label_input = TextInput(
            label=_t(locale, "field_label"), max_length=100,
            default=existing["label"] if existing else role_label,
        )
        self.desc_input = TextInput(
            label=_t(locale, "field_description"), required=False, max_length=100,
            default=(existing.get("description") if existing else None),
        )
        self.emoji_input = TextInput(
            label=_t(locale, "field_emoji"), required=False,
            default=(existing.get("emoji") if existing else None),
        )
        self.style_input = TextInput(
            label=_t(locale, "field_style"),
            required=False,
            placeholder=_t(locale, "field_style_hint"),
            default=(existing.get("style") if existing else None),
        )

        for item in (self.label_input, self.desc_input, self.emoji_input, self.style_input):
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        cfg = await get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if menu is None or self.role_id is None:
            return await interaction.followup.send(
                view=feedback_view(_t(interaction, "error_menu_gone"), ok=False), ephemeral=True
            )

        style = self.style_input.value.strip().lower() or None
        if style and style not in BUTTON_STYLE_NAMES:
            return await interaction.followup.send(
                view=feedback_view(
                    _t(interaction, "error_style_invalid", styles=", ".join(BUTTON_STYLE_NAMES)),
                    ok=False,
                ), ephemeral=True
            )

        options = menu.setdefault("options", [])
        duplicate = any(
            i != self.edit_index and o["role_id"] == self.role_id
            for i, o in enumerate(options)
        )
        if duplicate:
            return await interaction.followup.send(
                view=feedback_view(_t(interaction, "error_role_in_menu"), ok=False), ephemeral=True
            )

        entry = build_role_menu_option(
            role_id=self.role_id,
            label=self.label_input.value.strip(),
            description=self.desc_input.value.strip() or None,
            emoji=self.emoji_input.value.strip() or None,
            style=style,
        )

        if self.edit_index is not None and 0 <= self.edit_index < len(options):
            options[self.edit_index] = entry
            done_key = "role_option_updated"
        else:
            if len(options) >= 25:
                return await interaction.followup.send(
                    view=feedback_view(_t(interaction, "error_menu_role_limit"), ok=False), ephemeral=True
                )
            options.append(entry)
            done_key = "role_option_added"

        await update_config(self.guild_id, cfg)
        await interaction.followup.send(
            view=feedback_view(_t(interaction, done_key)), ephemeral=True
        )
        next_view = (
            RoleMenuWizardAddRolesView(
                self.guild_id, self.author, self.menu_id,
                await get_config(self.guild_id), interaction,
            )
            if self.wizard
            else RoleMenuEditView(
                self.guild_id, self.author, self.menu_id,
                await get_config(self.guild_id), interaction,
            )
        )
        await self.message.edit(view=next_view, allowed_mentions=discord.AllowedMentions.none())
        await refresh_posted_menu(interaction.client, self.guild_id, self.menu_id)


class CreateRoleMenuModal(Modal, title="Create Role Menu"):
    def __init__(self, guild_id: int, author: discord.Member, message: discord.Message, locale=None):
        super().__init__()
        self.title = _t(locale, "create_menu_modal_title")
        self.guild_id = guild_id
        self.author = author
        self.message = message

        self.title_input = TextInput(
            label=_t(locale, "field_menu_title"),
            default=_t(locale, "default_menu_title"),
            max_length=100,
        )
        self.desc_input = TextInput(
            label=_t(locale, "field_description"), style=discord.TextStyle.long, required=False,
            default=_t(locale, "default_menu_description"), max_length=300,
        )
        self.color_input = TextInput(
            label=_t(locale, "field_colour_optional"), required=False,
            placeholder=_t(locale, "field_color_example"),
        )

        for item in (self.title_input, self.desc_input, self.color_input):
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = await get_config(self.guild_id)
        if cfg.role_menus is None:
            cfg.role_menus = {}

        if len(cfg.role_menus) >= 25:
            return await interaction.response.send_message(
                view=feedback_view(_t(interaction, "error_menu_limit"), ok=False), ephemeral=True
            )

        color = None
        if self.color_input.value.strip():
            try:
                color = int(self.color_input.value.strip().replace("#", ""), 16)
            except ValueError:
                pass

        title = self.title_input.value.strip() or _t(interaction, "default_menu_title")
        existing_names = {m["name"].lower() for m in cfg.role_menus.values()}
        name = _generate_menu_name(title, existing_names)

        menu_id = new_menu_id()
        cfg.role_menus[menu_id] = build_role_menu(
            name=name,
            title=title,
            description=self.desc_input.value.strip() or None,
            color=color,
            menu_type=DEFAULT_MENU_TYPE,
        )
        await update_config(self.guild_id, cfg)

        await interaction.response.send_message(
            view=feedback_view(_t(interaction, "menu_created", name=name)), ephemeral=True
        )
        await self.message.edit(
            view=RoleMenuWizardTypeView(self.guild_id, self.author, menu_id, cfg),
            allowed_mentions=discord.AllowedMentions.none(),
        )


class EditMenuInfoModal(Modal, title="Edit Role Menu Info"):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, message: discord.Message, cfg: OnboardingConfig, locale=None):
        super().__init__()
        self.title = _t(locale, "edit_menu_info_modal_title")
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id
        self.message = message

        menu = cfg.role_menus[menu_id]

        self.name_input = TextInput(
            label=_t(locale, "field_internal_name"), default=menu["name"], max_length=50,
        )
        self.title_input = TextInput(
            label=_t(locale, "field_menu_title"), default=menu["title"], max_length=100,
        )
        self.desc_input = TextInput(
            label=_t(locale, "field_description"), style=discord.TextStyle.long, required=False,
            default=menu["description"], max_length=300,
        )
        self.color_input = TextInput(
            label=_t(locale, "field_colour"), required=False,
            default=f"{menu['color']:06X}" if menu.get("color") is not None else None,
        )

        for item in (self.name_input, self.title_input, self.desc_input, self.color_input):
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = await get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if menu is None:
            return await interaction.response.send_message(
                view=feedback_view(_t(interaction, "error_menu_gone"), ok=False), ephemeral=True
            )

        new_name = self.name_input.value.strip()
        if new_name and any(
            mid != self.menu_id and m["name"].lower() == new_name.lower()
            for mid, m in cfg.role_menus.items()
        ):
            return await interaction.response.send_message(
                view=feedback_view(
                    _t(interaction, "error_menu_name_taken", name=new_name), ok=False
                ), ephemeral=True
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

        await update_config(self.guild_id, cfg)
        await interaction.response.send_message(
            view=feedback_view(_t(interaction, "menu_info_updated")), ephemeral=True
        )
        await self.message.edit(
            view=RoleMenuEditView(
                self.guild_id, self.author, self.menu_id, cfg, interaction,
            ),
            allowed_mentions=discord.AllowedMentions.none(),
        )
        await refresh_posted_menu(interaction.client, self.guild_id, self.menu_id)


# ------------ ONBOARDING SETUP BUTTONS ------------

class SetWelcomeMsgBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, locale=None):
        super().__init__(
            label=_t(locale, "btn_set_welcome_message"), style=discord.ButtonStyle.primary
        )
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # author check
        if interaction.user != self.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=_t(interaction, "not_allowed")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        await interaction.response.send_modal(
            WelcomeMessageModal(self.guild_id, await get_config(self.guild_id), locale=interaction)
        )


class SetWelcomeChannelBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, locale=None):
        super().__init__(
            label=_t(locale, "btn_set_welcome_channel"), style=discord.ButtonStyle.secondary
        )
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # author check
        if interaction.user != self.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=_t(interaction, "not_allowed")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        cfg = await get_config(self.guild_id)
        cfg.welcome_channel = interaction.channel.id
        await update_config(self.guild_id, cfg)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('tick')} "
                + _t(interaction, "welcome_channel_set", channel=interaction.channel.mention)
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)


class GoodbyeMessageModal(Modal, title="Set Goodbye Message"):
    def __init__(self, guild_id: int, cfg: OnboardingConfig, locale=None):
        super().__init__()
        self.title = _t(locale, "goodbye_modal_title")
        self.guild_id = guild_id

        self.title_input = TextInput(
            label=_t(locale, "field_title"),
            required=False,
            default=cfg.goodbye_title or None
        )
        self.desc_input = TextInput(
            label=_t(locale, "field_description"),
            style=discord.TextStyle.long,
            placeholder=_t(locale, "field_description_hint"),
            required=False,
            default=cfg.goodbye_description or None
        )
        self.image_input = TextInput(
            label=_t(locale, "field_image_url"),
            required=False,
            default=cfg.goodbye_image or None
        )
        self.color_input = TextInput(
            label=_t(locale, "field_color"),
            required=False,
            placeholder=_t(locale, "field_color_hint"),
            default=format_hex_color(cfg.goodbye_color),
        )

        self.add_item(self.title_input)
        self.add_item(self.desc_input)
        self.add_item(self.image_input)
        self.add_item(self.color_input)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = await get_config(self.guild_id)

        # Unlike the welcome modal these clear when left blank, so a goodbye
        # title an admin typed once can be removed again.
        cfg.goodbye_title = self.title_input.value or None
        cfg.goodbye_description = self.desc_input.value or None
        cfg.goodbye_image = self.image_input.value or None

        color_text = self.color_input.value.strip()
        if color_text:
            color = normalize_hex_color(color_text)
            if color is None:
                return await interaction.response.send_message(
                    view=feedback_view(
                        _t(interaction, "color_invalid", example="`ED4245` or `#ED4245`"),
                        ok=False,
                    ),
                    ephemeral=True,
                )
            cfg.goodbye_color = color
        else:
            cfg.goodbye_color = None

        await update_config(self.guild_id, cfg)
        await interaction.response.send_message(
            view=feedback_view(_t(interaction, "goodbye_updated")),
            ephemeral=True,
        )


class SetGoodbyeMsgBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, locale=None):
        super().__init__(
            label=_t(locale, "btn_set_goodbye_message"), style=discord.ButtonStyle.primary
        )
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        await interaction.response.send_modal(
            GoodbyeMessageModal(self.guild_id, await get_config(self.guild_id), locale=interaction)
        )


class SetGoodbyeChannelBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, locale=None):
        super().__init__(
            label=_t(locale, "btn_set_goodbye_channel"), style=discord.ButtonStyle.secondary
        )
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        cfg = await get_config(self.guild_id)
        cfg.goodbye_channel = interaction.channel.id
        await update_config(self.guild_id, cfg)
        await interaction.response.send_message(
            view=feedback_view(
                _t(interaction, "goodbye_channel_set", channel=interaction.channel.mention)
            ),
            ephemeral=True,
        )


class SetRulesTextBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, locale=None):
        super().__init__(
            label=_t(locale, "btn_set_rules_text"), style=discord.ButtonStyle.primary
        )
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # author check
        if interaction.user != self.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=_t(interaction, "not_allowed")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        await interaction.response.send_modal(
            RulesModal(self.guild_id, await get_config(self.guild_id), locale=interaction)
        )


class PostRulesBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, locale=None):
        super().__init__(
            label=_t(locale, "btn_post_rules"), style=discord.ButtonStyle.secondary
        )
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # author check
        if interaction.user != self.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=_t(interaction, "not_allowed")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        cfg = await get_config(self.guild_id)
        cfg.rules_channel = interaction.channel.id

        view = RulesAcknowledgeView(self.guild_id, cfg=cfg)
        msg = await interaction.channel.send(view=view)

        cfg.rules_message_id = msg.id
        await update_config(self.guild_id, cfg)

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('tick')} {_t(interaction, 'rules_posted')}"
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)


class SetRulesRoleBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, locale=None):
        super().__init__(
            label=_t(locale, "btn_set_rules_role"), style=discord.ButtonStyle.secondary
        )
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # author check
        if interaction.user != self.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=_t(interaction, "not_allowed")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('settings')} {_t(interaction, 'rules_role_prompt')}"
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
                    content=f"{get_emoji('cross')} {_t(interaction, 'rules_role_timeout')}"
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.followup.send(view=view, ephemeral=True)

        if not interaction.guild:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} {_t(interaction, 'guild_only')}"
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
                    content=f"{get_emoji('cross')} {_t(interaction, 'rules_role_not_found')}"
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.followup.send(view=view, ephemeral=True)

        cfg = await get_config(interaction.guild.id)
        cfg.rules_role_id = role.id
        await update_config(interaction.guild.id, cfg)

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('tick')} "
                + _t(interaction, "rules_role_set", role=role.mention)
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.followup.send(view=view, ephemeral=True)


# ----------- AUTOROLE SETUP COMPONENTS -----------

class AddAutoroleSelect(discord.ui.RoleSelect):
    """Ephemeral role picker — adds chosen roles to the autorole list."""
    def __init__(self, guild_id: int, message: discord.Message, locale=None):
        super().__init__(
            placeholder=_t(locale, "autorole_add_placeholder"),
            min_values=1,
            max_values=10,
        )
        self.guild_id = guild_id
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        cfg = await get_config(self.guild_id)
        if cfg.autorole_ids is None:
            cfg.autorole_ids = []

        added = []
        for role in self.values:
            if role.id not in cfg.autorole_ids:
                cfg.autorole_ids.append(role.id)
                added.append(role.mention)

        await update_config(self.guild_id, cfg)
        if added:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('tick')} "
                    + _t(interaction, "autorole_added", roles=", ".join(added))
                ),
                accent_colour=discord.Color.green()
            )
            view.add_item(container)
            # edit the interaction message
            await interaction.response.edit_message(
                view=view, allowed_mentions=discord.AllowedMentions.none()
            )
            # update the setup panel
            await self.message.edit(
                view=AutoroleSetupView(
                    self.guild_id, interaction.user, interaction.guild,
                    await get_config(self.guild_id), interaction,
                ),
                allowed_mentions=discord.AllowedMentions.none(),
            )
        else:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} {_t(interaction, 'autorole_already')}"
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            await interaction.response.edit_message(
                view=view
            )


class AddAutoroleView(discord.ui.ActionRow):
    def __init__(self, guild_id: int, message: discord.Message, locale=None):
        super().__init__()
        self.add_item(AddAutoroleSelect(guild_id, message, locale))


class RemoveAutoroleSelect(discord.ui.Select):
    """Ephemeral select of current autoroles — removes chosen ones."""
    def __init__(self, guild_id: int, guild: discord.Guild, message: discord.Message, cfg: OnboardingConfig, locale=None):
        self.guild_id = guild_id
        self.message = message
        options = []
        for rid in (cfg.autorole_ids or []):
            role = guild.get_role(rid)
            label = role.name if role else _t(locale, "autorole_unknown_option", id=rid)
            options.append(discord.SelectOption(label=label, value=str(rid)))

        if not options:
            options = [discord.SelectOption(label=_t(locale, "autorole_none_option"), value="none")]

        super().__init__(
            placeholder=_t(locale, "autorole_remove_placeholder"),
            min_values=1,
            max_values=len(options),
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        cfg = await get_config(self.guild_id)
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

        await update_config(self.guild_id, cfg)
        if removed:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('tick')} "
                    + _t(interaction, "autorole_removed", roles=", ".join(removed))
                ),
                accent_colour=discord.Color.green()
            )
            view.add_item(container)
            await interaction.response.edit_message(
                view=view, allowed_mentions=discord.AllowedMentions.none()
            )
            await self.message.edit(
                view=AutoroleSetupView(
                    self.guild_id, interaction.user, interaction.guild,
                    await get_config(self.guild_id), interaction,
                ),
                allowed_mentions=discord.AllowedMentions.none(),
            )
        else:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} {_t(interaction, 'autorole_none_removed')}"
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            await interaction.response.edit_message(view=view)


class RemoveAutoroleView(discord.ui.ActionRow):
    def __init__(self, guild_id: int, guild: discord.Guild, message: discord.Message, cfg: OnboardingConfig, locale=None):
        super().__init__()
        self.add_item(RemoveAutoroleSelect(guild_id, guild, message, cfg, locale))


class AddAutoroleBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, locale=None):
        super().__init__(
            label=_t(locale, "btn_add_autorole"), style=discord.ButtonStyle.primary, emoji="➕"
        )
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=_t(interaction, "not_allowed")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        message = interaction.message
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('settings')} {_t(interaction, 'autorole_add_prompt')}"
            ),
            AddAutoroleView(self.guild_id, message, interaction)
        )
        view.add_item(container)
        await interaction.response.send_message(
            view=view, ephemeral=True,
        )


class RemoveAutoroleBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, guild: discord.Guild, locale=None):
        super().__init__(
            label=_t(locale, "btn_remove_autorole"), style=discord.ButtonStyle.secondary, emoji="➖"
        )
        self.guild_id = guild_id
        self.author = author
        self.guild = guild

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=_t(interaction, "not_allowed")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        cfg = await get_config(self.guild_id)
        if not cfg.autorole_ids:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} {_t(interaction, 'autorole_none_yet')}"
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)

        message = interaction.message
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('settings')} {_t(interaction, 'autorole_remove_prompt')}"
            ),
            RemoveAutoroleView(
                self.guild_id, self.guild, message,
                await get_config(self.guild_id), interaction,
            )
        )
        view.add_item(container)
        await interaction.response.send_message(
            view=view, ephemeral=True,
        )


class ClearAutorolesBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, locale=None):
        super().__init__(
            label=_t(locale, "btn_clear_all"), style=discord.ButtonStyle.danger,
            emoji=get_emoji('trash'),
        )
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=_t(interaction, "not_allowed")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        cfg = await get_config(self.guild_id)
        cfg.autorole_ids = []
        await update_config(self.guild_id, cfg)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('tick')} {_t(interaction, 'autorole_cleared')}"
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)
        await interaction.message.edit(view=AutoroleSetupView(
            self.guild_id, interaction.user, interaction.guild,
            await get_config(self.guild_id), interaction,
        ))


class AutoroleSetupView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, author: discord.Member, guild: discord.Guild, cfg: OnboardingConfig, locale=None):
        super().__init__(timeout=None)
        self.guild_id = guild_id

        role_ids = cfg.autorole_ids or []

        if role_ids:
            role_lines = "\n".join(
                f"• {guild.get_role(rid).mention if guild.get_role(rid) else _t(locale, 'autorole_unknown_line', id=rid)}"
                for rid in role_ids
            )
            current_text = _t(
                locale, "autorole_current", count=len(role_ids), lines=role_lines
            )
        else:
            current_text = _t(locale, "autorole_empty")

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=_t(locale, "autorole_panel_title")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=_t(locale, "autorole_panel_body")
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=current_text),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                AddAutoroleBtn(guild_id, author, locale),
                RemoveAutoroleBtn(guild_id, author, guild, locale),
                ClearAutorolesBtn(guild_id, author, locale),
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=_t(locale, "help_footer", support=links.SUPPORT_SERVER, docs=links.DOCS)
            ),
            accent_colour=discord.Colour(0xFEE75C),
        )
        self.add_item(container)


class ConfigureAutorolesBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, locale=None):
        super().__init__(
            label=_t(locale, "btn_configure_autoroles"), style=discord.ButtonStyle.secondary,
            emoji="🎭",
        )
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=_t(interaction, "not_allowed")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        await interaction.response.send_message(
            view=AutoroleSetupView(
                self.guild_id, self.author, interaction.guild,
                await get_config(self.guild_id), interaction,
            ),
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
    cfg = await get_config(guild_id)
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

    def __init__(self, guild_id: int, author: discord.Member, cfg: OnboardingConfig, locale=None):
        self.guild_id = guild_id
        self.author = author
        menus = cfg.role_menus or {}

        options = [
            discord.SelectOption(
                label=m["name"][:100],
                description=(
                    f"{_menu_type_label(locale, m['menu_type'])} · "
                    f"{_t(locale, 'role_count', count=len(m.get('options') or []))}"
                )[:100],
                value=mid,
            )
            for mid, m in menus.items()
        ][:25]

        if not options:
            options = [discord.SelectOption(label=_t(locale, "menu_none_option"), value="none")]

        super().__init__(
            placeholder=_t(locale, "menu_manager_placeholder"),
            options=options, min_values=1, max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        if self.values[0] == "none":
            return await interaction.response.send_message(
                view=feedback_view(_t(interaction, "error_create_menu_first"), ok=False),
                ephemeral=True,
            )
        await interaction.response.edit_message(
            view=RoleMenuEditView(
                self.guild_id, self.author, self.values[0],
                await get_config(self.guild_id), interaction,
            ),
            allowed_mentions=discord.AllowedMentions.none(),
        )


class CreateRoleMenuBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, locale=None):
        super().__init__(
            label=_t(locale, "btn_create_menu"), style=discord.ButtonStyle.success,
            emoji=get_emoji('plus'),
        )
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        await interaction.response.send_modal(
            CreateRoleMenuModal(self.guild_id, self.author, interaction.message, interaction)
        )


class BackToManagerBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, locale=None):
        super().__init__(
            label=_t(locale, "btn_back"), style=discord.ButtonStyle.secondary,
            emoji=get_emoji('arrow_left'),
        )
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        await interaction.response.edit_message(
            view=RoleMenuManagerView(
                self.guild_id, self.author, await get_config(self.guild_id), interaction,
            ),
            allowed_mentions=discord.AllowedMentions.none(),
        )


class EditMenuInfoBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, locale=None):
        super().__init__(label=_t(locale, "btn_edit_info"), style=discord.ButtonStyle.primary)
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        await interaction.response.send_modal(
            EditMenuInfoModal(
                self.guild_id, self.author, self.menu_id, interaction.message,
                await get_config(self.guild_id), interaction,
            )
        )


class ChangeMenuTypeSelect(discord.ui.Select):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, message: discord.Message, cfg: OnboardingConfig, locale=None):
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id
        self.message = message

        current = cfg.role_menus[menu_id]["menu_type"]
        options = [
            discord.SelectOption(
                label=_menu_type_label(locale, key), value=key, default=(key == current),
            )
            for key in MENU_TYPE_LABELS
        ]
        super().__init__(
            placeholder=_t(locale, "menu_type_placeholder"),
            options=options, min_values=1, max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        cfg = await get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if menu is None:
            return await interaction.response.edit_message(
                view=feedback_view(_t(interaction, "error_menu_gone"), ok=False)
            )

        menu["menu_type"] = self.values[0]
        await update_config(self.guild_id, cfg)

        await interaction.response.edit_message(
            view=feedback_view(
                _t(interaction, "menu_type_set", label=_menu_type_label(interaction, self.values[0]))
            )
        )
        await self.message.edit(
            view=RoleMenuEditView(
                self.guild_id, self.author, self.menu_id,
                await get_config(self.guild_id), interaction,
            ),
            allowed_mentions=discord.AllowedMentions.none(),
        )
        await refresh_posted_menu(interaction.client, self.guild_id, self.menu_id)


class ChangeMenuTypeBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, locale=None):
        super().__init__(
            label=_t(locale, "btn_change_type"), style=discord.ButtonStyle.secondary,
            emoji=get_emoji('shuffle'),
        )
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
                content=f"{get_emoji('settings')} {_t(interaction, 'menu_type_prompt')}"
            ),
            discord.ui.ActionRow(ChangeMenuTypeSelect(
                self.guild_id, self.author, self.menu_id, message,
                await get_config(self.guild_id), interaction,
            )),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


class RoleMenuAddRoleSelect(discord.ui.RoleSelect):
    """Ephemeral role picker for adding a role option — no typing an ID/mention required.
    Once a role is chosen, a small modal collects the label/description/emoji/style."""

    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, message: discord.Message, *, wizard: bool = False, locale=None):
        super().__init__(
            placeholder=_t(locale, "role_pick_placeholder"), min_values=1, max_values=1,
        )
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id
        self.message = message
        self.wizard = wizard

    async def callback(self, interaction: discord.Interaction):
        role = self.values[0]
        cfg = await get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if menu is None:
            return await interaction.response.edit_message(
                view=feedback_view(_t(interaction, "error_menu_gone"), ok=False)
            )
        if any(o["role_id"] == role.id for o in (menu.get("options") or [])):
            return await interaction.response.edit_message(
                view=feedback_view(
                    _t(interaction, "error_role_in_menu_named", role=role.mention), ok=False
                )
            )
        if len(menu.get("options") or []) >= 25:
            return await interaction.response.edit_message(
                view=feedback_view(_t(interaction, "error_menu_role_limit"), ok=False)
            )

        try:
            await interaction.response.send_modal(
                RoleMenuOptionModal(
                    self.guild_id, self.author, self.menu_id, self.message, role,
                    cfg=await get_config(self.guild_id), wizard=self.wizard,
                    locale=interaction,
                )
            )
        except Exception as e:
            print(f"Error adding role menu option: {e}")


class AddMenuOptionBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, *, wizard: bool = False, locale=None):
        super().__init__(
            label=_t(locale, "btn_add_role"), style=discord.ButtonStyle.success,
            emoji=get_emoji('plus'),
        )
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id
        self.wizard = wizard

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        cfg = await get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if menu and len(menu.get("options") or []) >= 25:
            return await interaction.response.send_message(
                view=feedback_view(_t(interaction, "error_menu_role_limit"), ok=False), ephemeral=True
            )
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('settings')} {_t(interaction, 'add_option_prompt')}"
            ),
            discord.ui.ActionRow(RoleMenuAddRoleSelect(
                self.guild_id, self.author, self.menu_id, interaction.message,
                wizard=self.wizard, locale=interaction,
            )),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


class EditMenuOptionSelect(discord.ui.Select):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, message: discord.Message, cfg: OnboardingConfig, locale=None):
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id
        self.message = message

        menu = (cfg.role_menus or {}).get(menu_id)
        options_list = (menu.get("options") if menu else []) or []
        options = [
            discord.SelectOption(
                label=o["label"][:100],
                description=_t(locale, "role_id_option", id=o["role_id"]),
                value=str(i),
            )
            for i, o in enumerate(options_list)
        ][:25]
        if not options:
            options = [discord.SelectOption(label=_t(locale, "no_roles_edit_option"), value="none")]

        super().__init__(
            placeholder=_t(locale, "edit_role_placeholder"),
            options=options, min_values=1, max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            return await interaction.response.edit_message(
                view=feedback_view(_t(interaction, "error_nothing_to_edit"), ok=False)
            )

        cfg = await get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        idx = int(self.values[0])
        options_list = (menu.get("options") if menu else []) or []
        existing = options_list[idx] if 0 <= idx < len(options_list) else None
        role = interaction.guild.get_role(existing["role_id"]) if (existing and interaction.guild) else None

        await interaction.response.send_modal(
            RoleMenuOptionModal(
                self.guild_id, self.author, self.menu_id, self.message, role,
                cfg=await get_config(self.guild_id), edit_index=idx, locale=interaction,
            )
        )


class EditMenuOptionBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, locale=None):
        super().__init__(
            label=_t(locale, "btn_edit_role"), style=discord.ButtonStyle.secondary,
            emoji=get_emoji('edit'),
        )
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
                content=f"{get_emoji('settings')} {_t(interaction, 'edit_role_prompt')}"
            ),
            discord.ui.ActionRow(EditMenuOptionSelect(
                self.guild_id, self.author, self.menu_id, message,
                await get_config(self.guild_id), interaction,
            )),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


class RemoveMenuOptionSelect(discord.ui.Select):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, message: discord.Message, cfg: OnboardingConfig, locale=None):
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id
        self.message = message

        menu = (cfg.role_menus or {}).get(menu_id)
        options_list = (menu.get("options") if menu else []) or []
        options = [
            discord.SelectOption(
                label=o["label"][:100],
                description=_t(locale, "role_id_option", id=o["role_id"]),
                value=str(i),
            )
            for i, o in enumerate(options_list)
        ][:25]
        if not options:
            options = [discord.SelectOption(label=_t(locale, "no_roles_remove_option"), value="none")]

        super().__init__(
            placeholder=_t(locale, "remove_role_placeholder"),
            options=options,
            min_values=1,
            max_values=len(options),
        )

    async def callback(self, interaction: discord.Interaction):
        cfg = await get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if menu is None or self.values[0] == "none":
            return await interaction.response.edit_message(
                view=feedback_view(_t(interaction, "error_nothing_to_remove"), ok=False)
            )

        indices = sorted({int(v) for v in self.values}, reverse=True)
        options = menu.get("options") or []
        removed = []
        for i in indices:
            if 0 <= i < len(options):
                removed.append(options.pop(i)["label"])

        await update_config(self.guild_id, cfg)
        await interaction.response.edit_message(
            view=feedback_view(
                _t(interaction, "removed_list", roles=", ".join(removed)) if removed
                else _t(interaction, "autorole_none_removed"),
                ok=bool(removed),
            )
        )
        await self.message.edit(
            view=RoleMenuEditView(
                self.guild_id, self.author, self.menu_id, cfg, interaction,
            ),
            allowed_mentions=discord.AllowedMentions.none(),
        )
        await refresh_posted_menu(interaction.client, self.guild_id, self.menu_id)


class RemoveMenuOptionBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, locale=None):
        super().__init__(
            label=_t(locale, "btn_remove_role"), style=discord.ButtonStyle.danger,
            emoji=get_emoji('minus'),
        )
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        cfg = await get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if not menu or not menu.get("options"):
            return await interaction.response.send_message(
                view=feedback_view(_t(interaction, "error_no_roles_yet"), ok=False), ephemeral=True
            )
        message = interaction.message
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('settings')} {_t(interaction, 'remove_role_prompt')}"
            ),
            discord.ui.ActionRow(RemoveMenuOptionSelect(
                self.guild_id, self.author, self.menu_id, message,
                await get_config(self.guild_id), interaction,
            )),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


class PostMenuBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, locale=None):
        super().__init__(
            label=_t(locale, "btn_post_here"), style=discord.ButtonStyle.primary, emoji="📌"
        )
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id

    async def callback(self, interaction: discord.Interaction):
        try:
            if not await check_author(interaction, self.author):
                return
            await interaction.response.defer(ephemeral=True, thinking=True)

            cfg = await get_config(self.guild_id)
            menu = (cfg.role_menus or {}).get(self.menu_id)
            if menu is None:
                return await interaction.followup.send(
                    view=feedback_view(_t(interaction, "error_menu_gone"), ok=False), ephemeral=True
                )
            if not menu.get("options"):
                return await interaction.followup.send(
                    view=feedback_view(_t(interaction, "error_add_role_first"), ok=False), ephemeral=True
                )

            # If it's already posted in this exact channel, edit it in place instead of duplicating.
            if menu.get("channel_id") == interaction.channel.id and menu.get("message_id"):
                try:
                    msg = await interaction.channel.fetch_message(menu["message_id"])
                    await msg.edit(view=RoleMenuView(self.guild_id, self.menu_id, cfg=cfg))
                    return await interaction.followup.send(
                        view=feedback_view(_t(interaction, "menu_updated_in_place")), ephemeral=True
                    )
                except discord.NotFound:
                    pass  # message was deleted — fall through and re-post

            posted_view = RoleMenuView(self.guild_id, self.menu_id, cfg=cfg)
            msg = await interaction.channel.send(view=posted_view)
            menu["channel_id"] = interaction.channel.id
            menu["message_id"] = msg.id
            await update_config(self.guild_id, cfg)

            await interaction.followup.send(
                view=feedback_view(_t(interaction, "menu_posted")), ephemeral=True
            )
            await interaction.message.edit(
                view=RoleMenuEditView(
                    self.guild_id, self.author, self.menu_id, cfg, interaction,
                ),
                allowed_mentions=discord.AllowedMentions.none(),
            )
        except Exception as e:
            logging.error("role_menu", f"Error posting role menu: {e}")


class ConfirmDeleteMenuBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, message: discord.Message, locale=None):
        super().__init__(
            label=_t(locale, "btn_confirm_delete"), style=discord.ButtonStyle.danger,
            emoji=get_emoji('trash'),
        )
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        cfg = await get_config(self.guild_id)
        menu = (cfg.role_menus or {}).pop(self.menu_id, None)
        await update_config(self.guild_id, cfg)

        if menu and menu.get("channel_id") and menu.get("message_id") and interaction.guild:
            channel = interaction.guild.get_channel(menu["channel_id"])
            if channel:
                try:
                    old_msg = await channel.fetch_message(menu["message_id"])
                    await old_msg.delete()
                except (discord.NotFound, discord.Forbidden):
                    pass

        name = menu["name"] if menu else _t(interaction, "fallback_menu_name")
        await interaction.response.edit_message(
            view=feedback_view(_t(interaction, "menu_deleted", name=name))
        )
        await self.message.edit(
            view=RoleMenuManagerView(self.guild_id, self.author, await get_config(self.guild_id)),
            allowed_mentions=discord.AllowedMentions.none(),
        )


class DeleteMenuBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, locale=None):
        super().__init__(
            label=_t(locale, "btn_delete_menu"), style=discord.ButtonStyle.danger,
            emoji=get_emoji('trash'),
        )
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
                content=f"{get_emoji('settings')} {_t(interaction, 'delete_confirm')}"
            ),
            discord.ui.ActionRow(ConfirmDeleteMenuBtn(
                self.guild_id, self.author, self.menu_id, message, interaction,
            )),
            accent_colour=discord.Color.red(),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


# --------- CAPTCHA VERIFY BUTTON & PANEL ---------

def _captcha_notice(content: str, colour: discord.Color = None) -> discord.ui.LayoutView:
    """A one-line CV2 reply, the shape every branch of the panel answers with."""
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=content),
        accent_colour=colour,
    ))
    return view


class CaptchaVerifyButton(discord.ui.Button):
    def __init__(self, guild_id: int, label: str = "Verify"):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.success,
            emoji=get_emoji('tick'),
            custom_id=f"captcha_verify_{guild_id}",
        )
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        guild_id = self.guild_id

        # check if captcha is enabled
        cfg = await get_config(guild_id)
        if not cfg.captcha_enabled:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=_t(interaction, "captcha_disabled")),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)

        mode = verification_modes.normalize_mode(cfg.captcha_mode)
        if mode == verification_modes.CLICK:
            return await self._verify_immediately(interaction, guild_id, user)
        if mode == verification_modes.WEB:
            return await self._send_web_challenge(interaction, guild_id, user)

        if user.id in _pending_verifications:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=_t(interaction, "captcha_pending")),
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
                discord.ui.TextDisplay(content=_t(interaction, "captcha_title")),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=_t(interaction, "captcha_dm_body")
                ),
                discord.ui.MediaGallery(
                    discord.MediaGalleryItem(
                        media=file
                    )
                ),
                discord.ui.TextDisplay(
                    content=_t(interaction, "captcha_dm_footer")
                )
            )
            view.add_item(container)
            await dm.send(view=view, file=file)
            sent_view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=_t(interaction, "captcha_sent")),
                accent_colour=discord.Color.green()
            )
            sent_view.add_item(container)
            await interaction.response.send_message(view=sent_view, ephemeral=True)
        except discord.Forbidden:
            _pending_verifications.pop(user.id, None)
            error_view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=_t(interaction, "captcha_dm_blocked")),
                accent_colour=discord.Color.red()
            )
            error_view.add_item(container)
            await interaction.response.send_message(view=error_view, ephemeral=True)

    async def _verify_immediately(self, interaction: discord.Interaction, guild_id: int, user) -> None:
        """One-click mode: the click *is* the verification."""
        await interaction.response.defer(ephemeral=True)
        result = await verification_service.complete(
            interaction.client, guild_id, user.id, source=verification_modes.LABELS[verification_modes.CLICK],
        )
        if result["problem"] == "guild":
            content = _t(interaction, "verified_no_guild")
        elif result["problem"] == "member":
            content = _t(interaction, "verified_no_member")
        else:
            lines = [_t(interaction, "verified_title"), _t(interaction, "verified_body")]
            if result["applied"]:
                lines.append(_t(interaction, "verified_roles_added", roles=", ".join(result["applied"])))
            if result["removed"]:
                lines.append(_t(interaction, "verified_roles_removed", roles=", ".join(result["removed"])))
            content = "\n".join(lines)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=content),
            accent_colour=discord.Color.green(),
        ))
        await interaction.followup.send(view=view, ephemeral=True)

    async def _send_web_challenge(self, interaction: discord.Interaction, guild_id: int, user) -> None:
        """Website mode: hand the member a single-use link to the captcha page."""
        pool = getattr(interaction.client, "cxn", None)
        try:
            challenge = await verification_store.create(pool, guild_id, user.id, new_captcha_code())
        except verification_store.VerificationUnavailable:
            return await interaction.response.send_message(
                view=_captcha_notice(
                    _t(interaction, "web_unavailable"),
                    discord.Color.red(),
                ),
                ephemeral=True,
            )

        link = verification_links.verification_url(challenge["token"])
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=_t(interaction, "captcha_title")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=_t(interaction, "web_body")),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label=_t(interaction, "web_button"),
                    style=discord.ui.ButtonStyle.link,
                    url=link,
                    emoji=get_emoji('tick'),
                )
            ),
            discord.ui.TextDisplay(content=_t(interaction, "web_footer")),
            accent_colour=discord.Colour(0x57F287),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


class CaptchaPanelView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, mode: str = None, locale=None):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.mode = verification_modes.normalize_mode(mode)

        prompt = _t(locale, f"prompt_{self.mode}")
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=_t(locale, "captcha_title")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=_t(locale, "panel_intro", prompt=prompt)),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(CaptchaVerifyButton(guild_id, _t(locale, "verify_button"))),
            accent_colour=discord.Colour(0x57F287),
        )
        self.add_item(container)


# ------------ CAPTCHA SETUP COMPONENTS ------------

class CaptchaAddRolesSelect(discord.ui.RoleSelect):
    def __init__(self, guild_id: int, message: discord.Message, locale=None):
        super().__init__(
            placeholder=_t(locale, "captcha_add_roles_placeholder"),
            min_values=1,
            max_values=10,
        )
        self.guild_id = guild_id
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        cfg = await get_config(self.guild_id)
        if cfg.captcha_add_role_ids is None:
            cfg.captcha_add_role_ids = []
        added = []
        for role in self.values:
            if role.id not in cfg.captcha_add_role_ids:
                cfg.captcha_add_role_ids.append(role.id)
                added.append(role.mention)
        await update_config(self.guild_id, cfg)
        if added:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('tick')} "
                    + _t(interaction, "captcha_will_add", roles=", ".join(added))
                ),
                accent_colour=discord.Color.green()
            )
            view.add_item(container)
            await interaction.response.edit_message(view=view)
            await self.message.edit(view=CaptchaSetupView(
                self.guild_id, interaction.user, interaction.guild,
                await get_config(self.guild_id), interaction,
            ))
        else:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} {_t(interaction, 'captcha_already_configured')}"
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            await interaction.response.edit_message(view=view)


class CaptchaAddRolesView(discord.ui.ActionRow):
    def __init__(self, guild_id: int, message: discord.Message, locale=None):
        super().__init__()
        self.add_item(CaptchaAddRolesSelect(guild_id, message, locale))


class CaptchaRemoveRolesSelect(discord.ui.RoleSelect):
    def __init__(self, guild_id: int, message: discord.Message, locale=None):
        super().__init__(
            placeholder=_t(locale, "captcha_remove_roles_placeholder"),
            min_values=1,
            max_values=10,
        )
        self.guild_id = guild_id
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        cfg = await get_config(self.guild_id)
        if cfg.captcha_remove_role_ids is None:
            cfg.captcha_remove_role_ids = []
        added = []
        for role in self.values:
            if role.id not in cfg.captcha_remove_role_ids:
                cfg.captcha_remove_role_ids.append(role.id)
                added.append(role.mention)
        await update_config(self.guild_id, cfg)
        if added:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('tick')} "
                    + _t(interaction, "captcha_will_remove", roles=", ".join(added))
                ),
                accent_colour=discord.Color.green()
            )
            view.add_item(container)
            await interaction.response.edit_message(view=view)
            await self.message.edit(view=CaptchaSetupView(
                self.guild_id, interaction.user, interaction.guild,
                await get_config(self.guild_id), interaction,
            ))
        else:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} {_t(interaction, 'captcha_already_configured')}"
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            await interaction.response.edit_message(view=view)


class CaptchaRemoveRolesView(discord.ui.ActionRow):
    def __init__(self, guild_id: int, message: discord.Message, locale=None):
        super().__init__()
        self.add_item(CaptchaRemoveRolesSelect(guild_id, message, locale))


async def refresh_captcha_panel(interaction: discord.Interaction, guild_id: int, cfg: OnboardingConfig) -> bool:
    """Re-render the posted Verify panel after its mode changes.

    The panel's wording is the member's first instruction, so it cannot keep
    describing a challenge the server no longer uses. Failures are silent: the
    setting is already saved, and the panel is re-rendered the next time it is
    posted or the bot restarts.
    """
    if not (cfg.captcha_channel_id and cfg.captcha_panel_message_id):
        return False
    guild = interaction.guild
    channel = guild.get_channel(cfg.captcha_channel_id) if guild is not None else None
    if channel is None:
        return False
    try:
        message = await channel.fetch_message(cfg.captcha_panel_message_id)
        view = CaptchaPanelView(guild_id, mode=cfg.captcha_mode, locale=guild)
        await message.edit(view=view)
        interaction.client.add_view(view, message_id=message.id)
        return True
    except Exception:
        return False


class CaptchaModeSelect(discord.ui.Select):
    def __init__(self, guild_id: int, message: discord.Message, current: str, locale=None):
        current = verification_modes.normalize_mode(current)
        super().__init__(
            placeholder=_t(locale, "captcha_mode_placeholder"),
            options=[
                discord.SelectOption(
                    label=_mode_label(locale, mode),
                    value=mode,
                    description=_mode_description(locale, mode).replace("**", "")[:100],
                    default=(mode == current),
                )
                for mode in verification_modes.MODES
            ],
        )
        self.guild_id = guild_id
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        mode = verification_modes.normalize_mode(self.values[0])
        cfg = await get_config(self.guild_id)
        cfg.captcha_mode = mode
        await update_config(self.guild_id, cfg)
        await refresh_captcha_panel(interaction, self.guild_id, cfg)
        await interaction.response.send_message(
            view=_captcha_notice(
                f"{get_emoji('tick')} "
                + _t(
                    interaction, "captcha_mode_set",
                    label=_mode_label(interaction, mode),
                    description=_mode_description(interaction, mode),
                ),
                discord.Color.green(),
            ),
            ephemeral=True,
        )
        await self.message.edit(view=CaptchaSetupView(
            self.guild_id, interaction.user, interaction.guild,
            await get_config(self.guild_id), interaction,
        ))


class CaptchaModeView(discord.ui.ActionRow):
    def __init__(self, guild_id: int, message: discord.Message, current: str, locale=None):
        super().__init__()
        self.add_item(CaptchaModeSelect(guild_id, message, current, locale))


class CaptchaSetupView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, author: discord.Member, guild: discord.Guild, cfg: OnboardingConfig, locale=None):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.author = author
        self.guild = guild

        mode = verification_modes.normalize_mode(cfg.captcha_mode)
        status = (
            f"{get_emoji('tick')} {_t(locale, 'captcha_status_enabled')}" if cfg.captcha_enabled
            else f"{get_emoji('cross')} {_t(locale, 'captcha_status_disabled')}"
        )
        channel_text = (
            f"<#{cfg.captcha_channel_id}>" if cfg.captcha_channel_id
            else _t(locale, "not_set")
        )
        delivery_text = f"**{_mode_label(locale, mode)}**\n{_mode_description(locale, mode)}"
        restrictions = []
        if cfg.captcha_block_proxies:
            restrictions.append(_t(locale, "captcha_restrict_proxies"))
        if cfg.captcha_block_vpn:
            restrictions.append(_t(locale, "captcha_restrict_vpn"))
        restrictions_text = (
            _t(locale, "captcha_refused", items=", ".join(restrictions)) if restrictions
            else _t(locale, "none")
        )
        if restrictions and mode != verification_modes.WEB:
            restrictions_text += "\n" + _t(locale, "captcha_web_only_note")
        add_roles = (
            ", ".join(f"<@&{r}>" for r in cfg.captcha_add_role_ids)
            if cfg.captcha_add_role_ids
            else _t(locale, "none")
        )
        remove_roles = (
            ", ".join(f"<@&{r}>" for r in cfg.captcha_remove_role_ids)
            if cfg.captcha_remove_role_ids
            else _t(locale, "none")
        )
        kick_text = (
            _t(locale, "captcha_kick_yes") if cfg.captcha_kick_on_fail
            else _t(locale, "captcha_kick_no")
        )

        info = _t(
            locale, "captcha_info",
            status=status,
            channel=channel_text,
            method=delivery_text,
            restrictions=restrictions_text,
            add=add_roles,
            remove=remove_roles,
            kick=kick_text,
        )

        toggle_label = (
            _t(locale, "btn_disable_captcha") if cfg.captcha_enabled
            else _t(locale, "btn_enable_captcha")
        )
        toggle_style = discord.ButtonStyle.danger if cfg.captcha_enabled else discord.ButtonStyle.success

        class ToggleCaptchaBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(label=toggle_label, style=toggle_style, emoji=get_emoji("lock"))
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=_t(interaction, "not_allowed")
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(view=view, ephemeral=True)
                c = await get_config(self_inner.guild_id)
                c.captcha_enabled = not c.captcha_enabled
                await update_config(self_inner.guild_id, c)
                # state = "enabled" if c.captcha_enabled else "disabled"
                # emoji = get_emoji("tick") if state == "enabled" else get_emoji("cross")
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
                await interaction.message.edit(view=CaptchaSetupView(
                    self_inner.guild_id, interaction.user, interaction.guild,
                    await get_config(self_inner.guild_id), interaction,
                ))

        class PostPanelBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(
                    label=_t(locale, "btn_post_verify_panel"),
                    style=discord.ButtonStyle.primary, emoji="📌",
                )
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=_t(interaction, "not_allowed")
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(view=view, ephemeral=True)
                c = await get_config(self_inner.guild_id)
                panel_view = CaptchaPanelView(
                    self_inner.guild_id, mode=c.captcha_mode, locale=interaction,
                )
                msg = None
                if c.captcha_channel_id == interaction.channel.id and c.captcha_panel_message_id:
                    try:
                        msg = await interaction.channel.fetch_message(c.captcha_panel_message_id)
                        await msg.edit(view=panel_view)
                    except discord.HTTPException:
                        msg = None
                if msg is None:
                    msg = await interaction.channel.send(view=panel_view)
                    if c.captcha_channel_id and c.captcha_panel_message_id and c.captcha_channel_id != interaction.channel.id:
                        old_channel = interaction.guild.get_channel(c.captcha_channel_id)
                        if old_channel is not None:
                            try:
                                old_message = await old_channel.fetch_message(c.captcha_panel_message_id)
                                await old_message.delete()
                            except discord.HTTPException:
                                pass
                c.captcha_channel_id = interaction.channel.id
                c.captcha_panel_message_id = msg.id
                await update_config(self_inner.guild_id, c)
                interaction.client.add_view(panel_view, message_id=msg.id)
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('tick')} {_t(interaction, 'captcha_panel_posted')}"
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await interaction.response.send_message(view=view, ephemeral=True)
                await interaction.message.edit(view=CaptchaSetupView(
                    self_inner.guild_id, interaction.user, interaction.guild,
                    await get_config(self_inner.guild_id), interaction,
                ))

        class SetAddRolesBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(
                    label=_t(locale, "btn_set_roles_add"),
                    style=discord.ButtonStyle.secondary, emoji="➕",
                )
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=_t(interaction, "not_allowed")
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(view=view, ephemeral=True)
                message = interaction.message
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('settings')} {_t(interaction, 'captcha_add_prompt')}"
                    ),
                    CaptchaAddRolesView(self_inner.guild_id, message, interaction)
                )
                view.add_item(container)
                await interaction.response.send_message(view=view, ephemeral=True)

        class SetRemoveRolesBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(
                    label=_t(locale, "btn_set_roles_remove"),
                    style=discord.ButtonStyle.secondary, emoji="➖",
                )
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=_t(interaction, "not_allowed")
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(view=view, ephemeral=True)
                message = interaction.message
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('settings')} {_t(interaction, 'captcha_remove_prompt')}"
                    ),
                    CaptchaRemoveRolesView(self_inner.guild_id, message, interaction)
                )
                view.add_item(container)
                await interaction.response.send_message(view=view, ephemeral=True)

        class ToggleKickBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(
                    label=_t(locale, "btn_toggle_kick"),
                    style=discord.ButtonStyle.secondary, emoji="🚫",
                )
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=_t(interaction, "not_allowed")
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(view=view, ephemeral=True)
                c = await get_config(self_inner.guild_id)
                c.captcha_kick_on_fail = not c.captcha_kick_on_fail
                await update_config(self_inner.guild_id, c)
                state = (
                    _t(interaction, "state_enabled") if c.captcha_kick_on_fail
                    else _t(interaction, "state_disabled")
                )
                emoji = get_emoji("tick") if c.captcha_kick_on_fail else get_emoji("cross")
                color = discord.Color.green() if c.captcha_kick_on_fail else discord.Color.red()
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{emoji} {_t(interaction, 'captcha_kick_state', state=state)}"
                    ),
                    accent_colour=color
                )
                view.add_item(container)
                await interaction.response.send_message(view=view, ephemeral=True)
                await interaction.message.edit(view=CaptchaSetupView(
                    self_inner.guild_id, interaction.user, interaction.guild,
                    await get_config(self_inner.guild_id), interaction,
                ))

        class ClearAddRolesBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(
                    label=_t(locale, "btn_clear_add_roles"),
                    style=discord.ButtonStyle.danger, emoji=get_emoji("trash"),
                )
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=_t(interaction, "not_allowed")
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(view=view, ephemeral=True)
                c = await get_config(self_inner.guild_id)
                c.captcha_add_role_ids = []
                await update_config(self_inner.guild_id, c)
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('tick')} {_t(interaction, 'captcha_add_cleared')}"
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await interaction.response.send_message(view=view, ephemeral=True)
                await interaction.message.edit(view=CaptchaSetupView(
                    self_inner.guild_id, interaction.user, interaction.guild,
                    await get_config(self_inner.guild_id), interaction,
                ))

        class ClearRemoveRolesBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(
                    label=_t(locale, "btn_clear_remove_roles"),
                    style=discord.ButtonStyle.danger, emoji=get_emoji("trash"),
                )
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=_t(interaction, "not_allowed")
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(view=view, ephemeral=True)
                c = await get_config(self_inner.guild_id)
                c.captcha_remove_role_ids = []
                await update_config(self_inner.guild_id, c)
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('tick')} {_t(interaction, 'captcha_remove_cleared')}"
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await interaction.response.send_message(view=view, ephemeral=True)
                await interaction.message.edit(view=CaptchaSetupView(
                    self_inner.guild_id, interaction.user, interaction.guild,
                    await get_config(self_inner.guild_id), interaction,
                ))

        class ChangeMethodBtn(discord.ui.Button):
            def __init__(self_inner):
                super().__init__(
                    label=_t(locale, "btn_change_method"),
                    style=discord.ButtonStyle.primary, emoji="🔀",
                )
                self_inner.guild_id = guild_id
                self_inner.author = author

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=_t(interaction, "not_allowed")
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(view=view, ephemeral=True)
                c = await get_config(self_inner.guild_id)
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('settings')} {_t(interaction, 'captcha_method_prompt')}"
                    ),
                    CaptchaModeView(
                        self_inner.guild_id, interaction.message, c.captcha_mode, interaction,
                    ),
                )
                view.add_item(container)
                await interaction.response.send_message(view=view, ephemeral=True)

        class ToggleRestrictionBtn(discord.ui.Button):
            """One toggle per web-only restriction, so the pair stay independent."""

            def __init__(self_inner, field: str, label: str, emoji: str, noun: str):
                super().__init__(label=label, style=discord.ButtonStyle.secondary, emoji=emoji)
                self_inner.guild_id = guild_id
                self_inner.author = author
                self_inner.field = field
                self_inner.noun = noun

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user != self_inner.author:
                    view = discord.ui.LayoutView()
                    container = discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=_t(interaction, "not_allowed")
                        ),
                        accent_colour=discord.Color.red()
                    )
                    view.add_item(container)
                    return await interaction.response.send_message(view=view, ephemeral=True)
                c = await get_config(self_inner.guild_id)
                setattr(c, self_inner.field, not getattr(c, self_inner.field))
                await update_config(self_inner.guild_id, c)
                enabled = getattr(c, self_inner.field)
                emoji = get_emoji('tick') if enabled else get_emoji('cross')
                color = discord.Color.green() if enabled else discord.Color.red()
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{emoji} " + _t(
                    interaction, "captcha_restriction_toggled",
                    noun=self_inner.noun,
                    state=_t(
                        interaction, "state_enabled" if enabled else "state_disabled"
                    ),
                )
                    ),
                    accent_colour=color
                )
                view.add_item(container)
                await interaction.response.send_message(view=view, ephemeral=True)
                await interaction.message.edit(view=CaptchaSetupView(
                    self_inner.guild_id, interaction.user, interaction.guild,
                    await get_config(self_inner.guild_id), interaction,
                ))

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=_t(locale, "captcha_setup_title")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=info),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(ToggleCaptchaBtn(), PostPanelBtn()),
            discord.ui.ActionRow(SetAddRolesBtn(), SetRemoveRolesBtn()),
            discord.ui.ActionRow(ToggleKickBtn(), ClearAddRolesBtn(), ClearRemoveRolesBtn()),
            discord.ui.ActionRow(
                ChangeMethodBtn(),
                ToggleRestrictionBtn(
                    "captcha_block_proxies", _t(locale, "btn_block_proxies"), "🛡️",
                    _t(locale, "captcha_proxies_noun"),
                ),
                ToggleRestrictionBtn(
                    "captcha_block_vpn", _t(locale, "btn_block_vpn"), "🌐",
                    _t(locale, "captcha_vpn_noun"),
                ),
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=_t(locale, "help_footer", support=links.SUPPORT_SERVER, docs=links.DOCS)
            ),
            accent_colour=discord.Colour(0x57F287),
        )
        self.add_item(container)


class ConfigureCaptchaBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, locale=None):
        super().__init__(
            label=_t(locale, "btn_configure_captcha"), style=discord.ButtonStyle.secondary,
            emoji="🔐",
        )
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=_t(interaction, "not_allowed")
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        await interaction.response.send_message(
            view=CaptchaSetupView(
                self.guild_id, self.author, interaction.guild,
                await get_config(self.guild_id), interaction,
            ),
            ephemeral=False,
        )


# -------------------- AGREE BUTTON & ROLE SELECT --------------------

class AgreeButton(discord.ui.Button):
    def __init__(self, guild_id: int, label: str = "I Agree"):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.success,
            custom_id=f"rules_agree_{guild_id}"
        )
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        cfg = await get_config(self.guild_id)

        if not cfg.rules_role_id:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=_t(interaction, "rules_no_role")),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.followup.send(view=view, ephemeral=True)

        role = interaction.guild.get_role(cfg.rules_role_id)
        if not role:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=_t(interaction, "rules_role_gone")),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            return await interaction.followup.send(view=view, ephemeral=True)

        await interaction.user.add_roles(role, reason="Acknowledged rules")
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=_t(interaction, "rules_acknowledged")),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.followup.send(view=view, ephemeral=True)


def _build_select_options(menu: dict, locale=None) -> list[discord.SelectOption]:
    options = []
    for o in (menu.get("options") or []):
        options.append(discord.SelectOption(
            label=o["label"][:100],
            description=(o.get("description") or None),
            emoji=(o.get("emoji") or None),
            value=str(o["role_id"]),
        ))
    if not options:
        options = [discord.SelectOption(label=_t(locale, "no_roles_option"), value="none")]
    return options


async def _apply_role_selection(interaction: discord.Interaction, guild_id: int, menu_id: str, keep_role_ids: set[int]):
    """Add/remove roles for the member so their roles among this menu's options match keep_role_ids."""
    await interaction.response.defer(ephemeral=True, thinking=True)

    cfg = await get_config(guild_id)
    menu = (cfg.role_menus or {}).get(menu_id)
    if not menu:
        return await interaction.followup.send(
            view=feedback_view(_t(interaction, "error_menu_not_configured"), ok=False),
            ephemeral=True,
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
            view=feedback_view(_t(interaction, "error_no_permission_roles"), ok=False),
            ephemeral=True,
        )

    await interaction.followup.send(
        view=feedback_view(_t(interaction, "roles_updated")), ephemeral=True
    )


class RoleMenuSelectMulti(discord.ui.Select):
    def __init__(self, guild_id: int, menu_id: str, menu: dict, locale=None):
        self.guild_id = guild_id
        self.menu_id = menu_id
        options = _build_select_options(menu, locale)
        max_values = menu.get("max_values") or len(options)
        super().__init__(
            placeholder=_t(locale, "select_roles_placeholder"),
            min_values=0,
            max_values=min(max_values, len(options)),
            options=options,
            custom_id=f"rmm_selm_{menu_id}",
        )

    async def callback(self, interaction: discord.Interaction):
        selected = {int(v) for v in self.values if v != "none"}
        await _apply_role_selection(interaction, self.guild_id, self.menu_id, selected)


class RoleMenuSelectSingle(discord.ui.Select):
    def __init__(self, guild_id: int, menu_id: str, menu: dict, locale=None):
        self.guild_id = guild_id
        self.menu_id = menu_id
        options = _build_select_options(menu, locale)
        super().__init__(
            placeholder=_t(locale, "select_role_placeholder"),
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

        cfg = await get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if not menu:
            return await interaction.followup.send(
                view=feedback_view(_t(interaction, "error_menu_not_configured"), ok=False),
                ephemeral=True,
            )
        role = interaction.guild.get_role(self.role_id)
        if not role:
            return await interaction.followup.send(
                view=feedback_view(_t(interaction, "error_role_gone"), ok=False), ephemeral=True
            )

        member = interaction.user
        try:
            if role in member.roles:
                await member.remove_roles(role, reason=f"Role menu: {menu['name']}")
                msg = _t(interaction, "role_removed", role=role.mention)
            else:
                await member.add_roles(role, reason=f"Role menu: {menu['name']}")
                msg = _t(interaction, "role_added", role=role.mention)
        except discord.Forbidden:
            return await interaction.followup.send(
                view=feedback_view(_t(interaction, "error_no_permission_role"), ok=False),
                ephemeral=True,
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

        cfg = await get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if not menu:
            return await interaction.followup.send(
                view=feedback_view(_t(interaction, "error_menu_not_configured"), ok=False),
                ephemeral=True,
            )
        role = interaction.guild.get_role(self.role_id)
        if not role:
            return await interaction.followup.send(
                view=feedback_view(_t(interaction, "error_role_gone"), ok=False), ephemeral=True
            )

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
                msg = _t(interaction, "role_removed", role=role.mention)
            else:
                await member.add_roles(role, reason=f"Role menu: {menu['name']}")
                msg = _t(interaction, "role_set", role=role.mention)
        except discord.Forbidden:
            return await interaction.followup.send(
                view=feedback_view(_t(interaction, "error_no_permission_roles"), ok=False),
                ephemeral=True,
            )
        await interaction.followup.send(view=feedback_view(msg), ephemeral=True)


# -------------------- PERSISTENT VIEWS --------------------

class RulesAcknowledgeView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, cfg=None, locale=None):
        super().__init__(timeout=None)
        self.guild_id = guild_id

        rules_text = (cfg.rules_text if cfg else None) or _t(locale, "rules_default")

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=_t(locale, "rules_title")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=rules_text),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=_t(locale, "rules_footer")),
            discord.ui.ActionRow(AgreeButton(guild_id, _t(locale, "rules_agree_button"))),
            accent_colour=discord.Colour(0xED4245)
        )
        self.add_item(container)


class RoleMenuView(discord.ui.LayoutView):
    """The live, persistent menu members interact with. Renders differently
    depending on the menu's configured menu_type."""

    def __init__(self, guild_id: int, menu_id: str, cfg=None, locale=None):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.menu_id = menu_id
        menu = (cfg.role_menus or {}).get(menu_id) or {}

        title = menu.get("title") or _t(locale, "default_menu_title")
        description = menu.get("description") or _t(locale, "default_menu_description")
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
            container.add_item(discord.ui.TextDisplay(
                content=_t(locale, "no_roles_configured_body")
            ))
        elif menu_type == "select_single":
            container.add_item(
                discord.ui.ActionRow(RoleMenuSelectSingle(guild_id, menu_id, menu, locale))
            )
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
            container.add_item(
                discord.ui.ActionRow(RoleMenuSelectMulti(guild_id, menu_id, menu, locale))
            )

        self.add_item(container)


# -------------------- SETUP VIEWS --------------------

class OnboardingSetupView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, author: discord.Member, prefix: str = ".", locale=None):
        super().__init__(timeout=None)
        self.guild_id = guild_id

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=_t(locale, "setup_title")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=_t(locale, "setup_body")
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                SetWelcomeMsgBtn(guild_id, author, locale),
                SetWelcomeChannelBtn(guild_id, author, locale),
            ),
            discord.ui.ActionRow(
                SetGoodbyeMsgBtn(guild_id, author, locale),
                SetGoodbyeChannelBtn(guild_id, author, locale),
            ),
            discord.ui.ActionRow(
                SetRulesTextBtn(guild_id, author, locale),
                PostRulesBtn(guild_id, author, locale),
                SetRulesRoleBtn(guild_id, author, locale),
            ),
            discord.ui.ActionRow(
                ConfigureAutorolesBtn(guild_id, author, locale),
                ConfigureCaptchaBtn(guild_id, author, locale),
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=_t(locale, "help_footer", support=links.SUPPORT_SERVER, docs=links.DOCS)
            ),
            accent_colour=discord.Colour(0x5865F2)
        )
        self.add_item(container)


class RoleMenuManagerView(discord.ui.LayoutView):
    """Top-level `.onboarding role-menu` panel: lists all menus for the guild."""

    def __init__(self, guild_id: int, author: discord.Member, cfg, locale=None):
        super().__init__(timeout=None)
        self.guild_id = guild_id

        menus = cfg.role_menus or {}

        if menus:
            lines = []
            for m in menus.values():
                posted = (
                    _t(locale, "menu_posted_in", channel=m["channel_id"])
                    if m.get("channel_id") and m.get("message_id") else ""
                )
                lines.append(_t(
                    locale, "menu_line",
                    name=m["name"],
                    type=_menu_type_label(locale, m["menu_type"]),
                    count=len(m.get("options") or []),
                    posted=posted,
                ))
            body = "\n".join(lines)
        else:
            body = _t(locale, "menus_empty")

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=_t(locale, "menus_title")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=_t(locale, "menus_summary", count=len(menus), body=body)
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )
        if menus:
            container.add_item(
                discord.ui.ActionRow(RoleMenuManagerSelect(guild_id, author, cfg, locale))
            )
        container.add_item(discord.ui.ActionRow(CreateRoleMenuBtn(guild_id, author, locale)))
        container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        container.add_item(discord.ui.TextDisplay(
            content=_t(locale, "help_footer", support=links.SUPPORT_SERVER, docs=links.DOCS)
        ))
        container.accent_colour = discord.Colour(0x57F287)
        self.add_item(container)


#: Locale key suffix for the plain-language hint under each menu type.
WIZARD_TYPE_HINT_KEYS = {
    "select_multi":  "wizard_hint_select_multi",
    "select_single": "wizard_hint_select_single",
    "button_multi":  "wizard_hint_button_multi",
    "button_single": "wizard_hint_button_single",
}


class RoleMenuWizardTypeSelect(discord.ui.Select):
    """Step 2 of the guided setup: pick a menu type, described in plain language."""

    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, cfg, locale=None):
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id

        current = cfg.role_menus[menu_id]["menu_type"]
        options = [
            discord.SelectOption(
                label=_menu_type_label(locale, key), value=key,
                description=_t(locale, WIZARD_TYPE_HINT_KEYS[key]),
            )
            for key in MENU_TYPE_LABELS
        ]
        super().__init__(
            placeholder=_t(locale, "wizard_pick_placeholder"),
            options=options, min_values=1, max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        cfg = await get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if menu is None:
            return await interaction.response.edit_message(
                view=feedback_view(_t(interaction, "error_menu_gone"), ok=False)
            )

        menu["menu_type"] = self.values[0]
        await update_config(self.guild_id, cfg)
        await interaction.response.edit_message(view=RoleMenuWizardAddRolesView(
            self.guild_id, self.author, self.menu_id,
            await get_config(self.guild_id), interaction,
        ))


class RoleMenuWizardTypeView(discord.ui.LayoutView):
    """Step 2 of 3 in the guided setup: choose the menu type."""

    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, cfg, locale=None):
        super().__init__(timeout=None)
        menu = cfg.role_menus[menu_id]

        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=_t(locale, "wizard_step2_title", name=menu["name"])
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=_t(locale, "wizard_step2_body")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(RoleMenuWizardTypeSelect(
                guild_id, author, menu_id, cfg, locale,
            )),
            accent_colour=discord.Colour(menu.get("color") or 0x57F287),
        )
        self.add_item(container)


class WizardFinishBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, locale=None):
        super().__init__(
            label=_t(locale, "btn_finish_setup"), style=discord.ButtonStyle.primary,
            emoji=get_emoji('tick'),
        )
        self.guild_id = guild_id
        self.author = author
        self.menu_id = menu_id

    async def callback(self, interaction: discord.Interaction):
        if not await check_author(interaction, self.author):
            return
        cfg = await get_config(self.guild_id)
        menu = (cfg.role_menus or {}).get(self.menu_id)
        if not menu or not menu.get("options"):
            return await interaction.response.send_message(
                view=feedback_view(_t(interaction, "error_add_role_first_finish"), ok=False),
                ephemeral=True,
            )
        await interaction.response.edit_message(view=RoleMenuEditView(
            self.guild_id, self.author, self.menu_id,
            await get_config(self.guild_id), interaction,
        ))


class RoleMenuWizardAddRolesView(discord.ui.LayoutView):
    """Step 3 of 3 in the guided setup: add roles via RoleSelect, no typing needed."""

    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, cfg, locale=None):
        super().__init__(timeout=None)
        menu = cfg.role_menus[menu_id]
        options = menu.get("options") or []

        opt_lines = "\n".join(
            f"{i + 1}. {(o.get('emoji') or '').strip()} **{o['label']}** — <@&{o['role_id']}>"
            for i, o in enumerate(options)
        ) or _t(locale, "no_roles_added")

        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=_t(locale, "wizard_step3_title", name=menu["name"])
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=_t(
                    locale, "wizard_step3_body",
                    count=len(options), lines=opt_lines,
                )
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                AddMenuOptionBtn(guild_id, author, menu_id, wizard=True, locale=locale),
                WizardFinishBtn(guild_id, author, menu_id, locale),
            ),
            accent_colour=discord.Colour(menu.get("color") or 0x57F287),
        )
        self.add_item(container)


class RoleMenuEditView(discord.ui.LayoutView):
    """Per-menu management panel: edit info/type, manage roles, post, delete."""

    def __init__(self, guild_id: int, author: discord.Member, menu_id: str, cfg, locale=None):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.menu_id = menu_id
        menu = (cfg.role_menus or {}).get(menu_id)

        if menu is None:
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} {_t(locale, 'error_menu_gone')}"
                ),
                discord.ui.ActionRow(BackToManagerBtn(guild_id, author, locale)),
                accent_colour=discord.Color.red(),
            )
            self.add_item(container)
            return

        options = menu.get("options") or []
        opt_lines = "\n".join(
            f"{i + 1}. {(o.get('emoji') or '').strip()} **{o['label']}** — <@&{o['role_id']}>"
            + (f" · _{o['description']}_" if o.get("description") else "")
            for i, o in enumerate(options)
        ) or _t(locale, "no_roles_added_plain")

        posted = (
            _t(locale, "menu_posting_line", channel=menu["channel_id"])
            if menu.get("channel_id") and menu.get("message_id") else ""
        )

        info = _t(
            locale, "menu_edit_info",
            title=menu["title"],
            description=menu["description"],
            type=_menu_type_label(locale, menu["menu_type"]),
            count=len(options),
            lines=opt_lines,
            posted=posted,
        )

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=_t(locale, "menu_managing_title", name=menu["name"])),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=info),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                EditMenuInfoBtn(guild_id, author, menu_id, locale),
                ChangeMenuTypeBtn(guild_id, author, menu_id, locale),
                AddMenuOptionBtn(guild_id, author, menu_id, locale=locale),
            ),
            discord.ui.ActionRow(
                EditMenuOptionBtn(guild_id, author, menu_id, locale),
                RemoveMenuOptionBtn(guild_id, author, menu_id, locale),
            ),
            discord.ui.ActionRow(
                PostMenuBtn(guild_id, author, menu_id, locale),
                DeleteMenuBtn(guild_id, author, menu_id, locale),
                BackToManagerBtn(guild_id, author, locale),
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=_t(locale, "help_footer", support=links.SUPPORT_SERVER, docs=links.DOCS)
            ),
            accent_colour=discord.Colour(menu.get("color") or 0x57F287),
        )
        self.add_item(container)


# -------------------- PREFIX COMMAND COG --------------------


__all__ = [k for k in list(globals()) if not k.startswith("__")]
