"""
Help System — fully trilingual (EN / DE / ES)
─────────────────────────────────────────────
All UI strings, category descriptions, category headers, pagination labels,
and command detail labels are localised to the guild's preferred locale.
Command wording comes from each cog's ``locales/commands`` namespace; the
decorators serialise it into ``{ 'en': '…', 'de': '…', 'es': '…' }`` on
``command.help``, which is what this menu reads.
"""

from typing import List, Tuple
import json

import discord
from discord.ext import commands

from config.emojis import get_emoji
from config import links
from utils.command_locales import description_map
from utils.prefix_manager import resolve_prefix
from utils.locales import load_locales

PAGE_SIZE = 8


# ===================================================
#  LANGUAGE UTILITIES
# ===================================================

def get_lang(ctx_or_guild=None) -> str:
    """Return 'de' when the guild's preferred locale is German, else 'en'."""
    guild = None
    if isinstance(ctx_or_guild, commands.Context):
        guild = ctx_or_guild.guild
    elif isinstance(ctx_or_guild, discord.Interaction):
        guild = ctx_or_guild.guild
    elif isinstance(ctx_or_guild, discord.Guild):
        guild = ctx_or_guild
    if guild and guild.preferred_locale:
        if str(guild.preferred_locale).lower().startswith("de"):
            return "de"
        if str(guild.preferred_locale).lower().startswith("es"):
            return "es"
    return "en"


def get_command_help(ctx_or_interaction, cmd: commands.Command) -> str:
    """
    Return the localised help string for a command.

    Decorators serialise the locale entry into JSON on ``command.help``:
    ``{ 'en': '…', 'de': '…' }``. Commands that only declare a short
    description fall back to the same locale table, so the menu shows the same
    wording as the dashboard commands page.
    """
    lang = get_lang(ctx_or_interaction)
    if cmd.help:
        try:
            help_dict = json.loads(cmd.help.replace("'", '"'))
            text = help_dict.get(lang) or help_dict.get("en")
            if text:
                return text
        except (json.JSONDecodeError, AttributeError):
            return cmd.help
    catalogue = description_map(cmd)
    return catalogue.get(lang) or catalogue.get("en", "")


def _ui(lang: str, key: str, **kwargs) -> str:
    """Shorthand for pulling a UI string in the given language."""
    text = _UI_STRINGS.get(lang, _UI_STRINGS["en"]).get(key)
    if text is None:
        text = _UI_STRINGS["en"][key]
    return text.format(**kwargs) if kwargs else text


# ===================================================
#  LOCALISED UI STRINGS
# ===================================================

_UI_STRINGS = load_locales("cogs.help", "ui")


# ===================================================
#  CATEGORY DEFINITIONS
# ===================================================

# (label, emoji) — descriptions are pulled from CATEGORY_DESCS per lang
_CATEGORY_LIST: List[Tuple[str, str]] = [
    ("General",        f"{get_emoji('general')}"),
    ("Fun",            f"{get_emoji('games')}"),
    ("Gambling",       f"{get_emoji('gambling')}"),
    ("Economy",        f"{get_emoji('economy')}"),
    ("Roleplay",       f"{get_emoji('roleplay')}"),
    ("Info",           f"{get_emoji('stats')}"),
    ("Utility",        f"{get_emoji('utility')}"),
    ("AI",             f"{get_emoji('ai')}"),
    ("Moderation",     f"{get_emoji('moderation')}"),
    ("EmojiManager",   f"{get_emoji('paint')}"),
    ("Community",      f"{get_emoji('heart')}"),
    ("Music",          f"{get_emoji('music')}"),
    ("Notifier",       f"{get_emoji('megaphone')}"),
    ("VoiceMaster",    f"{get_emoji('voicemaster')}"),
    ("Image Tools",    f"{get_emoji('image')}"),
    ("Customization",  f"{get_emoji('edit')}"),
]

CATEGORY_DESCS = load_locales("cogs.help", "category_descriptions")

# Category header strings shown above the command list — localised.
# Keyed by lang → category label → header markdown string.
CATEGORY_HEADERS = load_locales("cogs.help", "category_headers")

# Map category label → list of cog names that contribute to it.
CATEGORY_COGS: dict[str, List[str]] = {
    "General":       [],
    "Fun":           ["UwULock", "Meme", "tictactoe", "CuteAnimals", "FunCog", "ConnectFourCog", "PfpCog"],
    "Gambling":      ["Blackjack", "Roulette", "Slots", "GamblingCog"],
    "Economy":       ["EconomyCog"],
    "Roleplay":      ["RolePlayCog"],
    "Info":          ["InfoCog", "Legal"],
    "Utility":       [
        "UtilityCog", "Snipe", "Define", "AFKCog", "Tags", "Highlights", "Reminders",
        "Sticky", "Triggers", "DonationCog", "HelpCog",
    ],
    "AI":            ["AICog", "AIConfig"],
    "Moderation":    ["Moderation", "AutoMod", "ServerLogger"],
    "EmojiManager":  ["EmojiManagerCog"],
    "Community":     [
        "Polls", "Starboard", "Suggestions", "Birthdays", "Onboarding",
        "Leveling", "Giveaway", "Tickets",
    ],
    "Music":         ["MusicSystem"],
    "Notifier":      ["Notifier"],
    "VoiceMaster":   ["VoiceMaster"],
    "Image Tools":   ["ImageTools", "AiImageTools"],
    "Customization": ["Customization", "PrefixConfig"],
}


def _category_header(lang: str, category: str) -> str:
    return CATEGORY_HEADERS.get(lang, CATEGORY_HEADERS["en"]).get(
        category,
        CATEGORY_HEADERS["en"].get(category, ""),
    )


def _category_desc(lang: str, category: str) -> str:
    return CATEGORY_DESCS.get(lang, CATEGORY_DESCS["en"]).get(
        category,
        CATEGORY_DESCS["en"].get(category, ""),
    )


# ===================================================
#  PREFIX RESOLVER
# ===================================================

async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    """Return the primary prefix for this context, honouring a dynamic prefix."""
    return await resolve_prefix(bot, ctx_or_interaction)


# ===================================================
#  CONTENT BUILDERS
# ===================================================

def _general_text(bot: commands.Bot, lang: str) -> str:
    invite = f"https://discord.com/oauth2/authorize?client_id={bot.user.id}&scope=bot&permissions=8"
    return (
        f"{_ui(lang, 'general_title')}\n"
        f"{_ui(lang, 'general_intro')}\n\n"
        f"{_ui(lang, 'general_about_title')}\n"
        f"{_ui(lang, 'general_about_body')}\n\n"
        f"{_ui(lang, 'general_links_title', icon=get_emoji('link'))}\n"
        f"-# [GitHub](https://github.com/developer51709/Niko) • "
        f"[Invite]({invite}) • "
        f"[Website]({links.WEBSITE}) • "
        f"[Support Server]({links.SUPPORT_SERVER})"
    )


async def _commands_text(
    cog_names: List[str],
    bot: commands.Bot,
    ctx_or_interaction,
    page: int,
) -> Tuple[str, int]:
    """
    Build a paginated markdown string listing commands from one or more cogs.
    Returns (content, total_pages).
    """
    lang   = get_lang(ctx_or_interaction)
    prefix = await _resolve_prefix(bot, ctx_or_interaction)

    commands_list: List[commands.Command] = []
    for cog_name in cog_names:
        cog = bot.get_cog(cog_name)
        if cog:
            # Hidden commands (for example .dmpurge) are operator tooling: the
            # help menu must not advertise them even from a listed cog.
            commands_list.extend(
                cmd for cmd in cog.get_commands() if not getattr(cmd, "hidden", False)
            )

    if not commands_list:
        return _ui(lang, "no_commands"), 1

    total       = len(commands_list)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page        = max(1, min(page, total_pages))

    start         = (page - 1) * PAGE_SIZE
    page_commands = commands_list[start: start + PAGE_SIZE]

    no_desc = _ui(lang, "no_desc")
    lines   = []
    for cmd in page_commands:
        desc = get_command_help(ctx_or_interaction, cmd) or no_desc
        lines.append(f"**`{prefix}{cmd.name}`**\n-# {desc}")

    return "\n".join(lines), total_pages


async def _command_detail_text(
    bot: commands.Bot,
    cmd: commands.Command,
    ctx_or_interaction,
) -> str:
    lang   = get_lang(ctx_or_interaction)
    prefix = await _resolve_prefix(bot, ctx_or_interaction)

    if hasattr(cmd, "parent") and cmd.parent:
        parent = cmd.parent.name
        usage  = f"{prefix}{parent} {cmd.name} {cmd.signature or ''}"
    else:
        parent = None
        usage  = f"{prefix}{cmd.name} {cmd.signature or ''}"

    no_desc = _ui(lang, "no_desc")
    lines   = [
        f"### {get_emoji('question')} `{cmd.name}`",
        "",
        f"**{_ui(lang, 'detail_description')}**\n"
        f"{get_command_help(ctx_or_interaction, cmd) or no_desc}",
        "",
        f"**{_ui(lang, 'detail_usage')}**\n```\n{usage.strip()}\n```",
    ]

    if cmd.aliases:
        lines.append(
            f"\n**{_ui(lang, 'detail_aliases')}**\n"
            + ", ".join(f"`{a}`" for a in cmd.aliases)
        )

    if hasattr(cmd, "commands"):
        lines.append(f"\n**{_ui(lang, 'detail_subcommands')}**")
        for sub in cmd.commands:
            sub_desc = get_command_help(ctx_or_interaction, sub) or no_desc
            if parent:
                sub_usage = f"`{prefix}{parent} {cmd.name} {sub.name}`"
            else:
                sub_usage = f"`{prefix}{cmd.name} {sub.name}`"
            lines.append(f"{sub_usage}\n-# {sub_desc}")

    if cmd.cog_name:
        lines.append(f"\n**{_ui(lang, 'detail_category')}**\n{cmd.cog_name}")

    return "\n".join(lines)


# ===================================================
#  DROPDOWN
# ===================================================

_DROPDOWN_PAGE_SIZE = 24  # Discord max is 25; reserve 1 slot for the page-switch sentinel
_DROPDOWN_NAV_VALUE = "__help_nav_page__"


class HelpDropdown(discord.ui.Select):
    """Category dropdown — options are localised per guild locale.

    Discord's Select component is capped at 25 options. We have more categories
    than that, so the dropdown is paginated: each page shows up to 24 categories
    plus a 25th sentinel option that flips to the next page.
    """

    def __init__(self, bot: commands.Bot, lang: str = "en", page: int = 0):
        self.bot  = bot
        self.lang = lang

        total       = len(_CATEGORY_LIST)
        total_pages = max(1, (total + _DROPDOWN_PAGE_SIZE - 1) // _DROPDOWN_PAGE_SIZE)
        self.page   = max(0, min(page, total_pages - 1))
        self.total_pages = total_pages

        start = self.page * _DROPDOWN_PAGE_SIZE
        end   = start + _DROPDOWN_PAGE_SIZE
        slice_ = _CATEGORY_LIST[start:end]

        options = [
            discord.SelectOption(
                label=label,
                description=_category_desc(lang, label),
                emoji=emoji,
            )
            for label, emoji in slice_
        ]

        if total_pages > 1:
            next_page_idx = (self.page + 1) % total_pages
            options.append(
                discord.SelectOption(
                    label=_ui(lang, "dropdown_more_label").format(
                        page=next_page_idx + 1, total=total_pages
                    ),
                    value=f"{_DROPDOWN_NAV_VALUE}:{next_page_idx}",
                    description=_ui(lang, "dropdown_more_desc"),
                    emoji=get_emoji("arrow_right"),
                )
            )

        super().__init__(
            placeholder=_ui(lang, "dropdown_placeholder"),
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        lang     = get_lang(interaction)
        value    = self.values[0]

        # Page-switch sentinel — re-render current message with the new dropdown page,
        # keeping whatever content (general or category) was already shown.
        if value.startswith(_DROPDOWN_NAV_VALUE):
            try:
                next_page = int(value.split(":", 1)[1])
            except (ValueError, IndexError):
                next_page = 0
            content = _general_text(self.bot, lang)
            view    = _make_layout(
                self.bot, content, lang,
                include_dropdown=True, general_page=True,
                dropdown_page=next_page,
            )
            return await interaction.response.edit_message(view=view)

        category  = value
        cog_names = CATEGORY_COGS.get(category, [])

        if category == "General":
            content = _general_text(self.bot, lang)
            view    = _make_layout(
                self.bot, content, lang,
                include_dropdown=True, general_page=True,
                dropdown_page=self.page,
            )
            return await interaction.response.edit_message(view=view)

        page                      = 1
        commands_content, total_pages = await _commands_text(
            cog_names, self.bot, interaction, page
        )
        header = _category_header(lang, category)

        view = HelpPagination(
            bot=self.bot,
            category=category,
            cog_names=cog_names,
            lang=lang,
            ctx_or_interaction=interaction,
            page=page,
            total_pages=total_pages,
            dropdown_page=self.page,
        )
        view.header_display.content   = header
        view.commands_display.content = commands_content

        await interaction.response.edit_message(view=view)


# ===================================================
#  PAGINATION VIEW
# ===================================================

class HelpPagination(discord.ui.LayoutView):
    """
    Paginated category view.

    Container:
      TextDisplay (header — persists across pages)
      TextDisplay (commands list — updates on page change)
      ActionRow   (Prev · Page X/Y · Next) — only if total_pages > 1
      Separator
      ActionRow   (HelpDropdown)
    """

    def __init__(
        self,
        bot: commands.Bot,
        category: str,
        cog_names: List[str],
        lang: str,
        ctx_or_interaction,
        page: int = 1,
        total_pages: int = 1,
        dropdown_page: int = 0,
    ):
        super().__init__(timeout=None)
        self.bot                = bot
        self.category           = category
        self.cog_names          = cog_names
        self.lang               = lang
        self.page               = page
        self.total_pages        = total_pages
        self.ctx_or_interaction = ctx_or_interaction
        self.dropdown_page      = dropdown_page

        self.header_display:   discord.ui.TextDisplay
        self.commands_display: discord.ui.TextDisplay
        self.prev_button:      discord.ui.Button | None = None
        self.next_button:      discord.ui.Button | None = None
        self.page_indicator:   discord.ui.Button | None = None

        self._build_layout()

    def _build_layout(self):
        container = discord.ui.Container()

        self.header_display = discord.ui.TextDisplay(content="")
        container.add_item(self.header_display)

        self.commands_display = discord.ui.TextDisplay(content="")
        container.add_item(self.commands_display)

        if self.total_pages > 1:
            row = discord.ui.ActionRow()

            self.prev_button = discord.ui.Button(
                label=_ui(self.lang, "btn_prev"),
                style=discord.ButtonStyle.secondary,
                disabled=(self.page <= 1),
            )
            self.prev_button.callback = self._prev_page
            row.add_item(self.prev_button)

            self.page_indicator = discord.ui.Button(
                label=_ui(self.lang, "btn_page", page=self.page, total=self.total_pages),
                style=discord.ButtonStyle.secondary,
                disabled=True,
            )
            row.add_item(self.page_indicator)

            self.next_button = discord.ui.Button(
                label=_ui(self.lang, "btn_next"),
                style=discord.ButtonStyle.secondary,
                disabled=(self.page >= self.total_pages),
            )
            self.next_button.callback = self._next_page
            row.add_item(self.next_button)

            container.add_item(row)

        container.add_item(
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small)
        )
        container.add_item(discord.ui.ActionRow(HelpDropdown(self.bot, self.lang, page=self.dropdown_page)))
        self.add_item(container)

    async def _update_content(self, interaction: discord.Interaction):
        lang = get_lang(interaction)
        commands_content, total_pages = await _commands_text(
            self.cog_names, self.bot, interaction, self.page
        )
        self.total_pages                = total_pages
        self.commands_display.content   = commands_content

        if self.total_pages > 1 and self.prev_button and self.next_button and self.page_indicator:
            self.prev_button.disabled    = self.page <= 1
            self.next_button.disabled    = self.page >= self.total_pages
            self.prev_button.label       = _ui(lang, "btn_prev")
            self.next_button.label       = _ui(lang, "btn_next")
            self.page_indicator.label    = _ui(lang, "btn_page", page=self.page, total=self.total_pages)

        await interaction.response.edit_message(view=self)

    async def _prev_page(self, interaction: discord.Interaction):
        if self.page > 1:
            self.page -= 1
        await self._update_content(interaction)

    async def _next_page(self, interaction: discord.Interaction):
        if self.page < self.total_pages:
            self.page += 1
        await self._update_content(interaction)


# ===================================================
#  LAYOUT BUILDER (GENERAL + DETAIL PAGES)
# ===================================================

def _make_layout(
    bot: commands.Bot,
    content_text: str,
    lang: str = "en",
    include_dropdown: bool = True,
    general_page: bool = False,
    dropdown_page: int = 0,
) -> discord.ui.LayoutView:
    view      = discord.ui.LayoutView()
    container = discord.ui.Container()

    if general_page:
        section = discord.ui.Section(
            discord.ui.TextDisplay(content=content_text),
            accessory=discord.ui.Thumbnail(bot.user.avatar.url),
        )
        container.add_item(section)
    else:
        container.add_item(discord.ui.TextDisplay(content=content_text))

    if include_dropdown:
        container.add_item(
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small)
        )
        container.add_item(discord.ui.ActionRow(HelpDropdown(bot, lang, page=dropdown_page)))

    view.add_item(container)
    return view


# ===================================================
#  HELP COG
# ===================================================


__all__ = [k for k in list(globals()) if not k.startswith("__")]
