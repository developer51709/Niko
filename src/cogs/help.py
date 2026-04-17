from typing import List, Tuple

import discord
from discord.ext import commands
import json
from config.emojis import get_emoji


# ===================================================
#  CONFIGURATION
# ===================================================

# Number of commands shown per page in category views.
PAGE_SIZE = 8


# ===================================================
#  LANGUAGE UTILITY
# ===================================================

def get_lang(ctx_or_guild=None) -> str:
    """Return 'de' when the guild's preferred locale is German, else 'en'."""
    guild = None
    if isinstance(ctx_or_guild, commands.Context):
        guild = ctx_or_guild.guild
    elif isinstance(ctx_or_guild, discord.Guild):
        guild = ctx_or_guild
    if guild and guild.preferred_locale:
        if str(guild.preferred_locale).lower().startswith("de"):
            return "de"
    return "en"

# get_command_help will be used to fetch localized command descriptions where available.
# this requires commands to use a json formatted help string with language keys.
# Example formatting:
# help = "{ 'en': 'English help text', 'de': 'Deutscher Hilfetext' }"
def get_command_help(ctx: commands.Context, cmd: commands.Command):
    lang = get_lang(ctx)
    if cmd.help:
        try:
            help_dict = cmd.help.replace("'", '"')
            help_dict = json.loads(help_dict)
            text = help_dict.get(lang)
            return text
        except json.JSONDecodeError:
            return cmd.help or "Error reading help text."
    else:
        return cmd.help or "No help text available."
    

    
# ===================================================
#  PREFIX RESOLVER (supports dynamic multi-prefix functions)
# ===================================================

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


# ===================================================
#  CATEGORY DEFINITIONS
# ===================================================

CATEGORIES: List[Tuple[str, str, str]] = [
    ("General",       "General bot information",           f"{get_emoji('icon_general')}"),
    ("Fun",           "Fun commands",                      f"{get_emoji('icon_games')}"),
    ("Gambling",      "Blackjack, Slots, Roulette",        f"{get_emoji('icon_gambling')}"),
    ("Economy",       "Balance, daily, work, etc.",        f"{get_emoji('icon_economy')}"),
    ("Roleplay",      "RP commands",                       f"{get_emoji('icon_roleplay')}"),
    ("Info",          "User/server info commands",         f"{get_emoji('icon_stats')}"),
    ("Utility",       "Misc tools and utilities",          f"{get_emoji('icon_utility')}"),
    ("AI",            "AI commands",                       f"{get_emoji('icon_ai')}"),
    ("Moderation",    "Moderation commands",               f"{get_emoji('icon_moderation')}"),
    ("AutoMod",       "AutoMod commands",                  f"{get_emoji('icon_automod')}"),
    ("EmojiManager",  "EmojiManager commands",             f"{get_emoji('icon_paint')}"),
    ("Onboarding",    "Onboarding commands",               f"{get_emoji('icon_welcome')}"),
    ("NSFW",          "NSFW commands",                     f"{get_emoji('icon_nsfw')}"),
    ("Music",         "Music commands",                    f"{get_emoji('music')}"),
    ("Leveling",      "Leveling commands",                 f"{get_emoji('icon_leveling')}"),
    ("Notifier",      "Notifier commands",                 f"{get_emoji('icon_megaphone')}"),
    ("VoiceMaster",   "VoiceMaster commands",              f"{get_emoji('icon_voicemaster')}"),
    ("Ticket",        "Ticket commands",                   f"{get_emoji('icon_ticket')}"),
    ("Image Tools",   "Image manipulation commands",       f"{get_emoji('icon_image')}"),
    ("Giveaway",      "Giveaway commands",                 f"{get_emoji('icon_giveaway')}"),
    ("Customization", "Customization commands",            f"{get_emoji('icon_edit')}"),
]

# Map category label → (cog names list, header string)
CATEGORY_MAP: dict = {
    "General":      ([], ""),
    "Fun":          (["UwULock", "Meme", "tictactoe", "CuteAnimals", "FunCog"], f"{get_emoji('icon_games')} **Fun Commands**\n> Commands for fun and games!"),
    "Gambling":     (["Blackjack", "Roulette", "Slots", "GamblingCog"], f"{get_emoji('icon_gambling')} **Casino Commands**\n> Play games of chance!"),
    "Economy":      (["EconomyCog"], f"{get_emoji('icon_economy')} **Economy Commands**\n> Earn and spend virtual currency!"),
    "Roleplay":     (["RolePlayCog"], f"{get_emoji('icon_roleplay')} **Roleplay Commands**\n> Fun roleplay commands!"),
    "Info":         (["InfoCog"], f"{get_emoji('icon_stats')} **Information Commands**\n> Get info about users, servers, and more!"),
    "Utility":      (["UtilityCog", "Snipe", "Define", "AFKCog"], f"{get_emoji('icon_utility')} **Utility Commands**\n> Useful tools and utilities."),
    "AI":           (["AICog", "AIConfig"], f"{get_emoji('icon_ai')} **AI Commands**\n> Interact with Niko's AI features!"),
    "Moderation":   (["Moderation"], f"{get_emoji('icon_moderation')} **Moderation Commands**\n> Moderation tools for server management."),
    "AutoMod":      (["AutoMod"], f"{get_emoji('icon_automod')} **AutoMod Commands**\n> Automated moderation to keep your server safe."),
    "EmojiManager": (["EmojiManagerCog"], f"{get_emoji('icon_paint')} **Emoji Manager Commands**\n> Manage custom emojis in your server."),
    "Onboarding":   (["Onboarding"], f"{get_emoji('icon_welcome')} **Onboarding Commands**\n> Set up welcome messages and roles for new members."),
    "NSFW":         (["NSFW"], f"{get_emoji('icon_nsfw')} **NSFW Commands**\n> These commands only work in NSFW-marked channels."),
    "Music":        (["MusicSystem"], f"{get_emoji('music')} **Music Commands**\n> Play music in your voice channel!"),
    "Leveling":     (["Leveling"], f"{get_emoji('icon_leveling')} **Leveling Commands**\n> Level up by chatting and earning XP!"),
    "Notifier":     (["Notifier", "YouTube"], f"{get_emoji('icon_megaphone')} **Notifier Commands**\n> Get notified about new posts from your favorite creators!"),
    "VoiceMaster":  (["VoiceMaster"], f"{get_emoji('icon_voicemaster')} **VoiceMaster Commands**\n> Create and manage temporary voice channels!"),
    "Ticket":       (["Tickets"], f"{get_emoji('icon_ticket')} **Ticket Commands**\n> Create and manage support tickets."),
    "Image Tools":  (["ImageTools", "AiImageTools"], f"{get_emoji('icon_image')} **Image Tools**\n> Manipulate images with these commands!"),
    "Giveaway":     (["Giveaway"], f"{get_emoji('icon_giveaway')} **Giveaway Commands**\n> Host and manage giveaways in your server!"),
    "Customization": (["Customization", "PrefixConfig"], f"{get_emoji('icon_edit')} **Customization Commands**\n> Customize Niko's pfp, banner, and more!"),
}


# ===================================================
#  CONTENT BUILDERS
# ===================================================

def _general_text(bot: commands.Bot) -> str:
    """
    Build the static general help text.

    This page is non-paginated and shows the thumbnail.
    """
    invite = f"https://discord.com/oauth2/authorize?client_id={bot.user.id}&scope=bot&permissions=8"
    return (
        "### 🌸 Welcome to Niko's Help Menu\n"
        "Use the dropdown below to browse commands by category.\n\n"
        "**About Niko**\n"
        "Niko is a cozy, AI-powered Discord bot with a café personality — bilingual (EN/DE), "
        "packed with economy, leveling, music, moderation, and more!\n\n"
        f"**{get_emoji('icon_link')} Links**\n"
        f"-# [GitHub](https://github.com/developer51709/Niko) • "
        f"[Invite]({invite}) • "
        f"[Website](https://developer51709.github.io/Niko) • "
        f"[Support Server](https://dsc.gg/astral-haven)"
    )


async def _commands_text(
    cog_names: List[str],
    bot: commands.Bot,
    ctx_or_interaction,
    page: int,
) -> Tuple[str, int]:
    """
    Build a paginated markdown string listing commands from one or more cogs.

    Returns:
        (commands_only_content, total_pages)
    """
    prefix = await _resolve_prefix(bot, ctx_or_interaction)

    # Collect all commands from the given cogs
    commands_list: List[commands.Command] = []
    for cog_name in cog_names:
        cog = bot.get_cog(cog_name)
        if cog:
            for cmd in cog.get_commands():
                commands_list.append(cmd)

    if not commands_list:
        return "*No commands found.*", 1

    total = len(commands_list)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(1, min(page, total_pages))

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    page_commands = commands_list[start:end]

    lines: List[str] = []
    for cmd in page_commands:
        desc = get_command_help(ctx_or_interaction, cmd) or "No description provided."
        lines.append(f"**`{prefix}{cmd.name}`**\n-# {desc}")

    return "\n".join(lines), total_pages


async def _command_detail_text(
    bot: commands.Bot,
    cmd: commands.Command,
    ctx_or_interaction,
) -> str:
    """
    Build a detailed help view for a single command, including usage,
    aliases, subcommands, and category.
    """
    prefix = await _resolve_prefix(bot, ctx_or_interaction)
    signature = cmd.signature or ""

    if hasattr(cmd, "parent") and cmd.parent:
        parent = cmd.parent.name
        usage = f"{prefix}{parent} {cmd.name} {signature}"
    else:
        parent = None
        usage = f"{prefix}{cmd.name} {signature}"

    lines = [
        f"### 📘 `{cmd.name}`",
        "",
        f"**Description**\n{get_command_help(ctx_or_interaction, cmd) or 'No description provided.'}",
        "",
        f"**Usage**\n```\n{usage}\n```",
    ]

    if cmd.aliases:
        lines.append(f"\n**Aliases**\n" + ", ".join(f"`{a}`" for a in cmd.aliases))

    if hasattr(cmd, "commands"):
        lines.append("\n**Subcommands**")
        for subcommand in cmd.commands:
            if parent:
                lines.append(
                    f"`{prefix}{parent} {cmd.name} {subcommand.name}`\n"
                    f"-# {get_command_help(ctx_or_interaction, subcommand) or 'No description provided.'}"
                )
            else:
                lines.append(
                    f"`{prefix}{cmd.name} {subcommand.name}`\n"
                    f"-# {get_command_help(ctx_or_interaction, subcommand) or 'No description provided.'}"
                )

    if cmd.cog_name:
        lines.append(f"\n**Category**\n{cmd.cog_name}")

    return "\n".join(lines)


# ===================================================
#  DROPDOWN SELECT MENU
# ===================================================

class HelpDropdown(discord.ui.Select):
    """
    Category dropdown for the help menu.

    - "General" shows the static general help page.
    - Other categories show a paginated list of commands.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        options = [
            discord.SelectOption(label=label, description=desc, emoji=emoji)
            for label, desc, emoji in CATEGORIES
        ]
        super().__init__(
            placeholder="☕ Pick a category…",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        cog_names, header = CATEGORY_MAP[category]

        # General page: static, non-paginated, with thumbnail
        if category == "General":
            content = _general_text(self.bot)
            view = _make_layout(self.bot, content, include_dropdown=True, general_page=True)
            return await interaction.response.edit_message(view=view)

        # Category page: paginated, no Section, header persists
        page = 1
        commands_content, total_pages = await _commands_text(
            cog_names,
            self.bot,
            interaction,
            page,
        )

        view = HelpPagination(
            bot=self.bot,
            category=category,
            cog_names=cog_names,
            header=header,
            ctx_or_interaction=interaction,
            page=page,
            total_pages=total_pages,
        )

        # Set header + commands content
        view.header_display.content = header
        view.commands_display.content = commands_content

        await interaction.response.edit_message(view=view)


# ===================================================
#  PAGINATION VIEW
# ===================================================

class HelpPagination(discord.ui.LayoutView):
    """
    View that holds pagination state for a specific category.

    Structure (no Section, to avoid accessory requirement):
    - Container
      - TextDisplay (header)
      - TextDisplay (commands list)
      - ActionRow(Prev, Page, Next) [only if total_pages > 1]
      - Separator
      - ActionRow(HelpDropdown)
    """

    def __init__(
        self,
        bot: commands.Bot,
        category: str,
        cog_names: List[str],
        header: str,
        ctx_or_interaction,
        page: int = 1,
        total_pages: int = 1,
    ):
        super().__init__(timeout=None)
        self.bot = bot
        self.category = category
        self.cog_names = cog_names
        self.header = header
        self.page = page
        self.total_pages = total_pages
        self.ctx_or_interaction = ctx_or_interaction

        self.header_display: discord.ui.TextDisplay
        self.commands_display: discord.ui.TextDisplay
        self.prev_button: discord.ui.Button | None = None
        self.next_button: discord.ui.Button | None = None
        self.page_indicator: discord.ui.Button | None = None

        self._build_layout()

    def _build_layout(self):
        container = discord.ui.Container()

        # Header TextDisplay (header persists across pages)
        self.header_display = discord.ui.TextDisplay(content=self.header)
        container.add_item(self.header_display)

        # Commands TextDisplay (updated on page changes)
        self.commands_display = discord.ui.TextDisplay(content="")
        container.add_item(self.commands_display)

        # Pagination row (only if multiple pages)
        if self.total_pages > 1:
            pagination_row = discord.ui.ActionRow()

            self.prev_button = discord.ui.Button(
                label="◀ Prev",
                style=discord.ButtonStyle.secondary,
                disabled=(self.page <= 1),
            )
            self.prev_button.callback = self._prev_page
            pagination_row.add_item(self.prev_button)

            self.page_indicator = discord.ui.Button(
                label=f"Page {self.page}/{self.total_pages}",
                style=discord.ButtonStyle.secondary,
                disabled=True,
            )
            pagination_row.add_item(self.page_indicator)

            self.next_button = discord.ui.Button(
                label="Next ▶",
                style=discord.ButtonStyle.secondary,
                disabled=(self.page >= self.total_pages),
            )
            self.next_button.callback = self._next_page
            pagination_row.add_item(self.next_button)

            container.add_item(pagination_row)

        # Separator above dropdown
        container.add_item(
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small)
        )

        # Dropdown row
        container.add_item(discord.ui.ActionRow(HelpDropdown(self.bot)))

        self.add_item(container)

    async def _update_content(self, interaction: discord.Interaction):
        """
        Rebuild the commands text for the current page and update the view.
        Header persists; only commands + pagination state change.
        """
        commands_content, total_pages = await _commands_text(
            self.cog_names,
            self.bot,
            interaction,
            self.page,
        )
        self.total_pages = total_pages

        self.commands_display.content = commands_content

        if self.total_pages > 1 and self.prev_button and self.next_button and self.page_indicator:
            self.prev_button.disabled = self.page <= 1
            self.next_button.disabled = self.page >= self.total_pages
            self.page_indicator.label = f"Page {self.page}/{self.total_pages}"

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
    include_dropdown: bool = True,
    general_page: bool = False,
) -> discord.ui.LayoutView:
    """
    Build the base LayoutView for non-paginated pages.

    - General page: Section + Thumbnail + dropdown.
    - Detail pages: no Section (no accessory), just TextDisplay (+ optional dropdown).
    """
    view = discord.ui.LayoutView()
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
        container.add_item(discord.ui.ActionRow(HelpDropdown(bot)))

    view.add_item(container)
    return view


# ===================================================
#  HELP COG
# ===================================================

class HelpCog(commands.Cog):
    """
    Custom help system for Niko.

    Features:
    - Dynamic multi-prefix support
    - CV2-based UI with dropdown categories
    - Paginated category views
    - Thumbnail only on the General page
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="help",
        help="{ 'en': 'show the help menu 📘☕', 'de': 'zeige das Hilfemenü' }",
    )
    async def help(self, ctx: commands.Context, *, command_name: str = None):
        """
        Show the main help menu or detailed info about a specific command.

        - Without arguments: shows the General help page with dropdown.
        - With a command name: shows detailed info for that command.
        """
        if command_name:
            cmd = self.bot.get_command(command_name)
            if not cmd:
                content = (
                    f"### {get_emoji('icon_cross')} Command Not Found\n"
                    f"No command named `{command_name}` exists.\n"
                    f"Use the help menu to browse available commands."
                )
                view = _make_layout(self.bot, content, include_dropdown=False, general_page=False)
                return await ctx.send(view=view)

            content = await _command_detail_text(self.bot, cmd, ctx)
            view = _make_layout(self.bot, content, include_dropdown=False, general_page=False)
            return await ctx.send(view=view)

        content = _general_text(self.bot)
        view = _make_layout(self.bot, content, include_dropdown=True, general_page=True)
        await ctx.send(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))