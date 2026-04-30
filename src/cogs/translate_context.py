import discord

from utils.translator import Translator

from discord.ext import commands
from discord import app_commands

class LanguageSelectView(discord.ui.LayoutView):
    def __init__(self, message: discord.Message, locale: discord.Locale) -> None:
        self.message = message
        self.locale = locale
        super().__init__()

class ContextMenu(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

        self.context_commands = [
            app_commands.ContextMenu(
                name = "Translate",
                callback = self.translate_message,
                type = discord.AppCommandType.message,
            )
        ]

        for command in self.context_commands:
            self.bot.tree.add_command(command)

    async def cog_unload(self) -> None:
        for command in self.context_commands:
            self.bot.tree.remove_command(str(command), type=command.type)

    async def translate(self, interaction: discord.Interaction, message: discord.Message, locale: discord.Locale) -> None:
        content = message.content.strip()

        if not content:
            await interaction.response.send_message("The message is empty.", ephemeral=True)
            return

        analysis = await Translator.detect(content)
        flag_emoji = Translator.code_to_flag(analysis)
        translation = await Translator.translate_to_locale(message.content, locale)

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {flag_emoji} -> {Translator.locale_to_flag(locale)}"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    f"**Original:**\n"
                    f"{content}"
                )
            ),
            discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    f"**Translation:**\n"
                    f"{translation}"
                )
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"-# Translated using Google Translate."
            )
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)

    async def translate_message(self, interaction: discord.Interaction, message: discord.Message) -> None:
        await self.translate(interaction, message, interaction.locale)



async def setup(bot) -> None:
    await bot.add_cog(ContextMenu(bot))