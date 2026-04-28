import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

class WebhookSender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sayas", description="Send a message using a temporary webhook that mimics your profile.")
    async def sayas(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel

        # Create webhook
        webhook = await channel.create_webhook(
            name=interaction.user.display_name
        )

        # Fetch avatar bytes
        avatar_url = interaction.user.display_avatar.url
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as resp:
                avatar_bytes = await resp.read()

        # Send message through webhook
        await webhook.send(
            content=message,
            username=interaction.user.display_name,
            avatar_url=interaction.user.display_avatar.url
        )

        # Delete webhook
        await webhook.delete()

        await interaction.followup.send("Message sent!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(WebhookSender(bot))
