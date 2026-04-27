# this cog will allow server admins to configure the AI settings for their server or even disable the AI features.

import discord
from discord.ext import commands
import json
from config.emojis import get_emoji
from .error_handler import is_owner, under_development
from utils.ai_config import set_ai_config, get_ai_config


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
        self.container.add_item(discord.ui.TextDisplay(content="This experiment allows the AI to perform actions on your behalf. This includes things like creating channels, roles, and more."))
        self.container.add_item(discord.ui.ActionRow(
            ExperimentToggle(self.bot, "ai_actions", self.guild_id),
            ExperimentAboutButton(self.bot, "ai_actions")
        ))
        self.add_item(self.container)

class ExperimentAboutButton(discord.ui.Button):
    def __init__(self, bot: commands.Bot, experiment: str):
        self.bot = bot
        self.experiment = experiment
        super().__init__(label="About", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        # send the experiment about view as an ephemeral message
        view = discord.ui.LayoutView()
        if self.experiment == "ai_actions":
            view = AIActionsExperimentAbout(self.bot)
        else:
            # unknown experiment
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('icon_danger')} Unknown Experiment"
                ),
                discord.ui.TextDisplay(
                    content="The about page for this experiment could not be found."
                )
            )
            view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)

class ExperimentToggle(discord.ui.Button):
    def __init__(self, bot: commands.Bot, experiment: str, guild_id: int):
        # the emoji and text will be set based on the current status of the experiment
        self.bot = bot
        self.experiment = experiment
        self.current_status = get_ai_config(guild_id, "experiments")
        self.current_status = self.current_status.get(experiment, "False")
        if self.current_status == "True":
            self.emoji = get_emoji("icon_tick")
            self.label = "Enabled"
            self.style = discord.ButtonStyle.green
        else:
            self.emoji = get_emoji("icon_cross")
            self.label = "Disabled"
            self.style = discord.ButtonStyle.red
        super().__init__(label=self.label, style=self.style, emoji=self.emoji)

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
        current_status = get_ai_config(guild_id, "experiments")[self.experiment]
        if current_status == "True":
            set_ai_config(guild_id, "experiments", {self.experiment: "False"})
            self.emoji = get_emoji("icon_cross")
            self.label = "Disabled"
            self.style = discord.ButtonStyle.red
        else:
            set_ai_config(guild_id, "experiments", {self.experiment: "True"})
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
        self.container.add_item(discord.ui.TextDisplay(content="This experiment allows the AI to perform actions on your behalf. This includes things like creating channels, roles, and more."))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content="**Note:** This feature is still under development and may not work as expected."))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))

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

    @commands.command(
        name="ai-config",
        help="Configure the AI settings for your server."
    )
    @commands.has_permissions(manage_guild=True)
    async def ai_config(self, ctx: commands.Context):
        # this function will ensure that the guild has a config entry in the ai_config.json file
        get_ai_config(ctx.guild.id, "enabled")
        # send the panel
        view = AIConfigPanel(ctx, self.bot)
        await ctx.send(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(AIConfig(bot))