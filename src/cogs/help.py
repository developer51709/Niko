import discord
from discord.ext import commands
from config.emojis import get_emoji


# ============================
#  HELPER: Build a LayoutView
# ============================

def _make_layout(bot, content_text: str, include_dropdown: bool = True) -> discord.ui.LayoutView:
    """Return a cv2 LayoutView with a styled container and optional dropdown."""
    view = discord.ui.LayoutView()

    container = discord.ui.Container(
        discord.ui.Section(
            discord.ui.TextDisplay(content=content_text),
            accessory=discord.ui.Thumbnail(
                bot.user.avatar.url
            )
        )
    )
    if include_dropdown:
        container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        container.add_item(discord.ui.ActionRow(HelpDropdown(bot)))

    view.add_item(container)

    return view


def _commands_text(cog_names: list[str], bot, header: str) -> str:
    """Build a markdown string listing commands from one or more cogs."""
    prefix = bot.command_prefix if isinstance(bot.command_prefix, str) else bot.command_prefix[0]
    lines = [header, ""]
    for cog_name in cog_names:
        cog = bot.get_cog(cog_name)
        if cog:
            for cmd in cog.get_commands():
                desc = cmd.help or "No description"
                lines.append(f"**`{prefix}{cmd.name}`** — {desc}")
    return "\n".join(lines) if len(lines) > 2 else header + "\n\n*No commands found.*"


# ============================
#  DROPDOWN SELECT MENU
# ============================

CATEGORIES = [
    ("General",      "General bot information",           "🌸"),
    ("Fun",          "Fun commands",                      f"{get_emoji('icon_games')}"),
    ("Gambling",     "Blackjack, Slots, Roulette",        "🎰"),
    ("Economy",      "Balance, daily, work, etc.",        f"{get_emoji('icon_economy')}"),
    ("Roleplay",     "RP commands",                       "🎭"),
    ("Info",         "User/server info commands",         "ℹ️"),
    ("Utility",      "Misc tools and utilities",          f"{get_emoji('icon_utility')}"),
    ("AI",           "AI commands",                       f"{get_emoji('icon_ai')}"),
    ("Moderation",   "Moderation commands",               f"{get_emoji('icon_moderation')}"),
    ("AutoMod",      "AutoMod commands",                  f"{get_emoji('icon_automod')}"),
    ("EmojiManager", "EmojiManager commands",             "🎨"),
    ("Onboarding",   "Onboarding commands",               f"{get_emoji('icon_welcome')}"),
    ("NSFW",         "NSFW commands",                     "🔞"),
    ("Music",        "Music commands",                    f"{get_emoji('music')}"),
    ("Leveling",     "Leveling commands",                 f"{get_emoji('icon_leveling')}"),
    ("Notifier",     "Notifier commands",                "📢"),
    ("VoiceMaster",  "VoiceMaster commands",              "🎤"),
    ("Ticket",       "Ticket commands",                   f"{get_emoji('icon_ticket')}"),
    ("Image Tools",  "Image manipulation commands",       f"{get_emoji('icon_image')}"),
    ("Giveaway",     "Giveaway commands",                 f"{get_emoji('icon_giveaway')}"),
]

# Map category label → (cog names list, header string)
CATEGORY_MAP: dict[str, tuple[list[str], str]] = {
    "General":      ([], ""),   # handled specially
    "Fun":          (["UwULock", "Meme", "tictactoe", "CuteAnimals"], f"{get_emoji('icon_games')} **Fun Commands**\n> Commands for fun and games!"),
    "Gambling":     (["Blackjack", "Roulette", "Slots", "GamblingCog"], "🎰 **Casino Commands**\n> Play games of chance!"),
    "Economy":      (["EconomyCog"], f"{get_emoji('icon_economy')} **Economy Commands**\n> Earn and spend virtual currency!"),
    "Roleplay":     (["RolePlayCog"], "🎭 **Roleplay Commands**\n> Fun roleplay commands!"),
    "Info":         (["InfoCog"], "ℹ️ **Information Commands**\n> Get info about users, servers, and more!"),
    "Utility":      (["UtilityCog", "Snipe"], f"{get_emoji('icon_utility')} **Utility Commands**\n> Useful tools and utilities."),
    "AI":           (["AICog", "AIConfig"], f"{get_emoji('icon_ai')} **AI Commands**\n> Interact with Niko's AI features!"),
    "Moderation":   (["Moderation"], f"{get_emoji('icon_moderation')} **Moderation Commands**\n> Moderation tools for server management."),
    "AutoMod":      (["AutoMod"], f"{get_emoji('icon_automod')} **AutoMod Commands**\n> Automated moderation to keep your server safe."),
    "EmojiManager": (["EmojiManagerCog"], "🎨 **Emoji Manager Commands**\n> Manage custom emojis in your server."),
    "Onboarding":   (["Onboarding"], f"{get_emoji('icon_welcome')} **Onboarding Commands**\n> Set up welcome messages and roles for new members."),
    "NSFW":         (["NSFW"], "🔞 **NSFW Commands**\n> These commands only work in NSFW-marked channels."),
    "Music":        (["MusicSystem"], f"{get_emoji('music')} **Music Commands**\n> Play music in your voice channel!"),
    "Leveling":     (["Leveling"], f"{get_emoji('icon_leveling')} **Leveling Commands**\n> Level up by chatting and earning XP!"),
    "Notifier":     (["Notifier", "YouTube"], "📢 **Notifier Commands**\n> Get notified about new posts from your favorite creators!"),
    "VoiceMaster":  (["VoiceMaster"], "🎤 **VoiceMaster Commands**\n> Create and manage temporary voice channels!"),
    "Ticket":       (["Tickets"], f"{get_emoji('icon_ticket')} **Ticket Commands**\n> Create and manage support tickets."),
    "Image Tools":  (["ImageTools"], f"{get_emoji('icon_image')} **Image Tools**\n> Manipulate images with these commands!"),
    "Giveaway":     (["Giveaway"], f"{get_emoji('icon_giveaway')} **Giveaway Commands**\n> Host and manage giveaways in your server!"),
}


class HelpDropdown(discord.ui.Select):
    def __init__(self, bot):
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

        if category == "General":
            content = _general_text(self.bot)
        else:
            content = _commands_text(cog_names, self.bot, header)

        view = _make_layout(self.bot, content, include_dropdown=True)
        await interaction.response.edit_message(view=view)


# ============================
#  CONTENT BUILDERS
# ============================

def _general_text(bot) -> str:
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


def _command_detail_text(bot, cmd) -> str:
    prefix = bot.command_prefix if isinstance(bot.command_prefix, str) else bot.command_prefix[0]
    signature = cmd.signature or ""
    lines = [
        f"### 📘 `{cmd.name}`",
        "",
        f"**Description**\n{cmd.help or 'No description provided.'}",
        "",
        f"**Usage**\n```\n{prefix}{cmd.name} {signature}\n```",
    ]
    if cmd.aliases:
        lines.append(f"\n**Aliases**\n" + ", ".join(f"`{a}`" for a in cmd.aliases))
    if cmd.cog_name:
        lines.append(f"\n**Category**\n{cmd.cog_name}")
    return "\n".join(lines)


# ============================
#  HELP COG
# ============================

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", help="show the help menu 📘☕ | zeige das Hilfemenü")
    async def help(self, ctx, *, command_name: str = None):
        """Shows the help menu or info about a specific command."""

        # --- Individual command lookup ---
        if command_name:
            cmd = self.bot.get_command(command_name)
            if not cmd:
                content = (
                    f"### {get_emoji('icon_cross')} Command Not Found\n"
                    f"No command named `{command_name}` exists.\n"
                    f"Try `!help` for the full menu."
                )
                view = _make_layout(self.bot, content, include_dropdown=False)
                return await ctx.send(view=view)

            content = _command_detail_text(self.bot, cmd)
            view = _make_layout(self.bot, content, include_dropdown=False)
            return await ctx.send(view=view)

        # --- Default help menu ---
        content = _general_text(self.bot)
        view = _make_layout(self.bot, content, include_dropdown=True)
        await ctx.send(view=view)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
