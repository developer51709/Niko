"""``.staff manage``: assign, change, or revoke a member's staff role."""

import discord
from discord.ext import commands

from cogs.staff.base import CMDS, StaffCommands
from cogs.staff.permissions import role_label
from cogs.staff.records import ROLE_ORDER, STAFF_ROLES, get_staff_role, set_staff_role


class StaffRoleSelect(discord.ui.Select):
    def __init__(self, bot, target: discord.Member, owner_id: int):
        self.bot = bot
        self.target = target
        self.owner_id = owner_id
        options = [
            discord.SelectOption(
                label=STAFF_ROLES[key],
                value=key,
                description=f"Assign the {STAFF_ROLES[key]} staff role.",
            )
            for key in ROLE_ORDER
        ]
        options.append(discord.SelectOption(
            label="Revoke staff access",
            value="revoke",
            description="Remove the user's staff role.",
        ))
        super().__init__(placeholder="Choose a staff role…", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("Only the bot owner can manage staff access.", ephemeral=True)
        value = self.values[0]
        role = None if value == "revoke" else value
        try:
            await set_staff_role(
                self.bot, self.target.id, role, interaction.user.id,
                reason="Staff access changed from .staff manage",
            )
        except Exception as exc:
            # A failed write or role sync must reach the operator rather than
            # leaving the interaction unanswered ("This interaction failed").
            return await interaction.response.send_message(
                f"Staff access was not updated: `{type(exc).__name__}: {exc}`", ephemeral=True
            )
        message = (
            f"Revoked staff access from {self.target.mention}."
            if role is None
            else f"Assigned **{STAFF_ROLES[role]}** to {self.target.mention}."
        )
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=f"### Staff access updated\n{message}"), accent_colour=discord.Colour.green()))
        await interaction.response.edit_message(view=view)


class StaffManageView(discord.ui.LayoutView):
    def __init__(self, bot, target: discord.Member, owner_id: int, current_role: str | None = None):
        super().__init__(timeout=300)
        current = role_label(current_role) if current_role else "No staff role assigned"
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### Manage staff access\n**User:** {target.mention}\n**Current:** {current}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(StaffRoleSelect(bot, target, owner_id)),
            accent_colour=discord.Colour(0xC8A882),
        )
        self.add_item(container)


class ManageCommands:
    """``.staff manage`` — owner-only roster control."""

    @StaffCommands.staff.command(name="manage", help=CMDS.help("staff.manage"), hidden=True)
    async def staff_manage(self, ctx: commands.Context, target: discord.Member):
        current_role = await get_staff_role(self.bot, target.id)
        await ctx.send(view=StaffManageView(self.bot, target, ctx.author.id, current_role))
