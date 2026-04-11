# this cog will allow server admins to configure the AI settings for their server or even disable the AI features.

import discord
from discord.ext import commands
from config.emojis import get_emoji
from .error_handler import is_owner, under_development
from utils.ai_config import set_ai_config, get_ai_config


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
                    content=f"### {get_emoji('icon_danger')} Error\nYou need the `manage_guild` permission to use this button."
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
                    content=f"### {get_emoji('icon_danger')} Error\nYou need the `manage_guild` permission to use this button."
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
        view = AIConfigPanel(ctx, self.bot)
        await ctx.send(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(AIConfig(bot))