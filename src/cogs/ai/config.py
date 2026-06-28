# this cog will allow server admins to configure the AI settings for their server or even disable the AI features.

import discord
from discord.ext import commands
import json
from config.emojis import get_emoji
from cogs.system.error_handler import is_owner, under_development
from utils.ai.config import set_ai_config, get_ai_config


# exeriments view
# this is where users can learn about the experimental features and toggle them on or off
class ExperimentsView(discord.ui.LayoutView):
    def __init__(self, bot: commands.Bot, guild_id: int):
        self.bot = bot
        self.guild_id = guild_id
        super().__init__()
        self.container = discord.ui.Container()
        self.container.add_item(discord.ui.TextDisplay(content=f"### {get_emoji('icon_ai')} Experiments"))
        self.container.add_item(discord.ui.TextDisplay(content="> These are experimental features that are still under development. They may not work as expected and may change at any time."))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content="**AI Actions**"))
        self.container.add_item(discord.ui.TextDisplay(content="Allows the AI to perform real Discord actions on your behalf — such as creating polls — when you ask it to in chat."))
        self.container.add_item(discord.ui.ActionRow(
            ExperimentToggle(self.bot, "ai_actions", self.guild_id),
            ExperimentAboutButton(self.bot, "ai_actions")
        ))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content="**Better Context**"))
        self.container.add_item(discord.ui.TextDisplay(content="Gives the AI awareness of the last 5 channel messages and the message being replied to, so it can respond more naturally in ongoing conversations."))
        self.container.add_item(discord.ui.ActionRow(
            ExperimentToggle(self.bot, "better_context", self.guild_id),
            ExperimentAboutButton(self.bot, "better_context")
        ))
        self.add_item(self.container)

class ExperimentAboutButton(discord.ui.Button):
    def __init__(self, bot: commands.Bot, experiment: str):
        self.bot = bot
        self.experiment = experiment
        super().__init__(label="About", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        if self.experiment == "ai_actions":
            view = AIActionsExperimentAbout(self.bot)
        elif self.experiment == "better_context":
            view = BetterContextExperimentAbout(self.bot)
        else:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=f"### {get_emoji('icon_danger')} Unknown Experiment"),
                discord.ui.TextDisplay(content="The about page for this experiment could not be found.")
            )
            view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)

class ExperimentToggle(discord.ui.Button):
    def __init__(self, bot: commands.Bot, experiment: str, guild_id: int):
        self.bot = bot
        self.experiment = experiment
        self.guild_id = guild_id
        current_status = get_ai_config(guild_id, f"{experiment}_experiment")
        if current_status == "True":
            emoji = get_emoji("icon_tick")
            label = "Enabled"
            style = discord.ButtonStyle.green
        else:
            emoji = get_emoji("icon_cross")
            label = "Disabled"
            style = discord.ButtonStyle.red
        super().__init__(label=label, style=style, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('icon_danger')} Error"
                ),
                discord.ui.Separator(
                    visible=True,
                    spacing=discord.SeparatorSpacing.small
                ),
                discord.ui.TextDisplay(
                    content="You need the `manage_guild` permission to use this button."
                ),
                accent_colour=discord.Color.yellow()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        guild_id = interaction.guild.id
        current_status = get_ai_config(guild_id, f"{self.experiment}_experiment")
        if current_status == "True":
            set_ai_config(guild_id, f"{self.experiment}_experiment", "False")
            self.emoji = get_emoji("icon_cross")
            self.label = "Disabled"
            self.style = discord.ButtonStyle.red
        else:
            set_ai_config(guild_id, f"{self.experiment}_experiment", "True")
            self.emoji = get_emoji("icon_tick")
            self.label = "Enabled"
            self.style = discord.ButtonStyle.green
        await interaction.response.edit_message(view=self.view)

class AIActionsExperimentAbout(discord.ui.LayoutView):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.container = discord.ui.Container()
        self.container.add_item(discord.ui.TextDisplay(content=f"### {get_emoji('icon_ai')} AI Actions Experiment"))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content="This experiment lets Niko take real action on your server when you ask in natural language."))
        self.container.add_item(discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(
            content=(
                "**What Niko can do**\n"
                "• Polls — *create a quick poll in chat*\n"
                "• Moderation — *kick, ban, unban, time-out, remove time-out, warn, purge messages*\n"
                "• Server management — *create/delete/rename channels, set channel topic, "
                "create/delete roles, give or take a role, change a member's nickname*"
            )
        ))
        self.container.add_item(discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(
            content=(
                "**How it works**\n"
                "Just talk to Niko (e.g. *“ban this user for spam”* or *“make a channel called announcements”*).\n"
                "Before anything happens, Niko shows a confirmation card with the exact action and waits for "
                "you to click **Confirm** or **Cancel** — only the person who asked can answer."
            )
        ))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(
            content=(
                "**Permissions**\n"
                "Niko will only run an action if **both** you and Niko hold the Discord permission required for it "
                "(Kick Members, Ban Members, Moderate Members, Manage Messages, Manage Channels, Manage Roles, "
                "Manage Nicknames). Otherwise the request is refused."
            )
        ))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content="**Note:** This feature is experimental — always double-check the confirmation card before clicking Confirm."))
        self.add_item(self.container)

class BetterContextExperimentAbout(discord.ui.LayoutView):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.container = discord.ui.Container()
        self.container.add_item(discord.ui.TextDisplay(content=f"### {get_emoji('icon_ai')} Better Context Experiment"))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content="Gives Niko awareness of recent conversation history so responses feel more natural and connected to what's happening in the channel."))
        self.container.add_item(discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content="**What it adds**\n• The last 5 non-bot messages in the channel\n• The content of any message being replied to\n\nNiko uses this extra context to understand the flow of conversation before responding."))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content="**Note:** This feature is still under development and may not work as expected."))
        self.add_item(self.container)


class ExperimentsButton(discord.ui.Button):
    def __init__(self, bot: commands.Bot):
        super().__init__(
            label="Experiments",
            style=discord.ButtonStyle.secondary
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        # require manage guild perm
        if not interaction.user.guild_permissions.manage_guild:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('icon_danger')} Error"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content="You need the `manage_guild` permission to use this button."
                ),
                accent_colour=discord.Color.yellow()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        guild_id = interaction.guild.id
        view = ExperimentsView(self.bot, guild_id)
        await interaction.response.send_message(view=view, ephemeral=True)

class BotPersonalitySelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot):
        super().__init__(
            placeholder="Select a personality",
            options=[
                discord.SelectOption(label="Normal", value="normal"),
                discord.SelectOption(label="Café", value="cafe")
            ]
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        # perm check handled by the button
        guild_id = interaction.guild.id
        personality = self.values[0]
        set_ai_config(guild_id, "personality", personality)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('icon_ai')} Bot Personality"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"The bot personality has been set to **{personality}** for this server."
            ),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)
            
class BotPersonalityButton(discord.ui.Button):
    def __init__(self, bot: commands.Bot):
        super().__init__(
            label="Bot Personality",
            style=discord.ButtonStyle.secondary
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        # require manage guild perm
        if not interaction.user.guild_permissions.manage_guild:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('icon_danger')} Error"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content="You need the `manage_guild` permission to use this button."
                ),
                accent_colour=discord.Color.yellow()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('icon_ai')} Bot Personality"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content="Select the personality you want the bot to have."
            ),
            discord.ui.ActionRow(
                BotPersonalitySelect(self.bot)
            ),
            discord.ui.TextDisplay(
                content="-# **Note:** This feature is still under development and may not work as expected."
            )
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)



class ToggleAIButton(discord.ui.Button):
    def __init__(self, bot: commands.Bot):
        super().__init__(
            label="Toggle AI",
            style=discord.ButtonStyle.secondary
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        # require manage guild perm
        if not interaction.user.guild_permissions.manage_guild:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('icon_danger')} Error"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content="You need the `manage_guild` permission to use this button."
                ),
                accent_colour=discord.Color.yellow()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        guild_id = interaction.guild.id
        current_status = get_ai_config(guild_id, "enabled")
        if current_status == "True":
            set_ai_config(guild_id, "enabled", "False")
            return await interaction.response.send_message("AI has been successfully disabled for this server.", ephemeral=True)
        else:
            set_ai_config(guild_id, "enabled", "True")
            return await interaction.response.send_message("AI has been successfully enabled for this server.", ephemeral=True)


class MainPanelButtons(discord.ui.ActionRow):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.add_item(ToggleAIButton(self.bot))
        self.add_item(BotPersonalityButton(self.bot))
        self.add_item(ExperimentsButton(self.bot))


class AIConfigPanel(discord.ui.LayoutView):
    def __init__(self, ctx, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.container = discord.ui.Container()
        self.container.add_item(discord.ui.TextDisplay(content=f"### {get_emoji('icon_ai')} AI Configuration Panel"))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content="Use the options below to configure the AI settings for your server."))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(MainPanelButtons(self.bot))
        self.add_item(self.container)


class AIConfig(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="ai-config",
        description="Configure the AI settings for this server",
        help="Configure the AI settings for your server."
    )
    @commands.has_permissions(manage_guild=True)
    async def ai_config(self, ctx: commands.Context):
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer(ephemeral=False)
        get_ai_config(ctx.guild.id, "enabled")
        view = AIConfigPanel(ctx, self.bot)
        await ctx.send(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(AIConfig(bot))