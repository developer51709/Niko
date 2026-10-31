"""``.staff help``: what each staff role may run, in the guild's language."""

import discord
from discord.ext import commands

from config.ids import OWNER_IDS
from cogs.staff.base import CMDS, StaffCommands
from cogs.staff.permissions import (
    SUPPORT_COMMANDS,
    command_names_for_role,
    help_line,
    role_label,
)
from cogs.staff.records import STAFF_ROLES, ROLE_ORDER, get_staff_role
from utils.i18n import get_lang


async def _is_staff_interaction(interaction: discord.Interaction) -> bool:
    if interaction.user.id in OWNER_IDS:
        return True
    return await get_staff_role(interaction.client, interaction.user.id) is not None


class StaffHelpSelect(discord.ui.Select):
    def __init__(self, bot, ctx: commands.Context):
        self.bot = bot
        self.ctx = ctx
        options = [
            discord.SelectOption(label="All staff commands", value="all", description="Show commands available to every staff role."),
            discord.SelectOption(label="Owner commands", value="owner", description="Show bot-owner-only commands."),
            *[
                discord.SelectOption(label=STAFF_ROLES[key], value=key, description=f"Show {STAFF_ROLES[key]} commands.")
                for key in ROLE_ORDER
            ],
        ]
        super().__init__(placeholder="Choose a staff role to view…", options=options)

    async def callback(self, interaction: discord.Interaction):
        if not await _is_staff_interaction(interaction):
            return await interaction.response.send_message("This help menu is for official Niko staff only.", ephemeral=True)
        value = self.values[0]
        if value == "owner" and interaction.user.id not in OWNER_IDS:
            return await interaction.response.send_message(
                "Only the bot owner can view owner commands.", ephemeral=True
            )
        await interaction.response.edit_message(view=build_staff_help(self.bot, interaction, value))


def build_staff_help(bot, ctx_or_interaction, selected_role: str = "all") -> discord.ui.LayoutView:
    lang = get_lang(ctx_or_interaction)
    role = selected_role
    if role == "all":
        label = "All staff"
        names = SUPPORT_COMMANDS
    else:
        label = role_label(role)
        names = command_names_for_role(role)

    lines = []
    for command in sorted(bot.get_command("staff").commands, key=lambda item: item.name):
        if command.name in {"help", "manage"}:
            continue
        short_name = command.name
        if names == {"*"} or short_name in names:
            lines.append(f"**`.staff {short_name}`** — {help_line(command, lang)}")
    if not lines:
        lines.append("No commands are assigned to this role yet.")

    view = discord.ui.LayoutView(timeout=300)
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=f"# Staff commands — {label}\n" + "\n".join(lines)),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(StaffHelpSelect(bot, ctx_or_interaction)),
        accent_colour=discord.Colour(0x5865F2),
    ))
    return view


class HelpCommands:
    """``.staff help`` — the same panel the bare ``.staff`` command opens."""

    @StaffCommands.staff.command(name="help", help=CMDS.help("staff.help"), hidden=True)
    async def staff_help(self, ctx: commands.Context):
        await ctx.send(view=build_staff_help(self.bot, ctx, "all"))
