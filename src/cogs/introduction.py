# introduction.py
# Sends an introduction message when the bot joins a new server

import discord
from discord.ext import commands
from utils.logging import info, success, warning, error, debug

MAIN_CHANNEL_NAMES = [
    "general",
    "chat",
    "lobby",
    "main",
    "welcome",
    "home",
    "community",
    "discussion",
    "talk",
    "general-chat",
    "🌐general",
    "💬general",
]

class Introduction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --------------------------------
    # Utility: pick the best channel to send the intro message
    # --------------------------------
    def pick_best_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        # 1. Prefer channels with common "main chat" names
        for name in MAIN_CHANNEL_NAMES:
            for channel in guild.text_channels:
                if channel.name.lower() == name.lower():
                    perms = channel.permissions_for(guild.me)
                    if perms.send_messages:
                        debug("Introduction", f"Preferred channel found: #{channel.name}")
                        return channel

        # 2. Otherwise, pick the first channel where the bot can speak
        for channel in guild.text_channels:
            perms = channel.permissions_for(guild.me)
            if perms.send_messages:
                debug("Introduction", f"Fallback channel selected: #{channel.name}")
                return channel

        return None

    # --------------------------------
    # Event: on_guild_join
    # --------------------------------
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        info("Introduction", f"Joined new guild: {guild.name} ({guild.id})")

        # Build introduction UI using your custom components
        view = discord.ui.LayoutView()

        container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content="### Hello, I'm Niko!"
                ),
                discord.ui.TextDisplay(
                    content="> I am a multi-purpose bot for your server. I can help you with moderation, fun commands, music, onboarding, and more!"
                ),
                accessory=discord.ui.Thumbnail(self.bot.user.avatar.url)
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"**To get started, type `{self.bot.command_prefix}help` or just say “hey niko” in the chat.**"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content="-# 📌 **Need help?**\n-# Ask in the [support server](https://dsc.gg/astral-haven) or check the [documentation](https://developer51709.github.io/Niko/docs)"
            )
        )

        view.add_item(container)

        # Pick the best channel
        channel = self.pick_best_channel(guild)

        if channel is None:
            warning("Introduction", f"No available channel to send introduction message in {guild.name}")
            return

        # Send the introduction message
        try:
            await channel.send(view=view)
            success("Introduction", f"Sent introduction message in {guild.name} → #{channel.name}")
        except Exception as e:
            error("Introduction", f"Failed to send introduction message in {channel.name}: {e}")


async def setup(bot):
    await bot.add_cog(Introduction(bot))