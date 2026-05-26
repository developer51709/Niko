import discord
from discord import app_commands
from discord.ext import commands

class WebhookSender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="sayas",
        description="Send a message using a temporary webhook that mimics your profile."
    )
    @app_commands.describe(
        message="The message to send",
        attachment="Optional file to attach"
    )
    async def sayas(
        self,
        interaction: discord.Interaction,
        message: str,
        attachment: discord.Attachment | None = None
    ):
        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel

        # Basic safety: ensure we're in a guild text channel
        if not isinstance(channel, (discord.TextChannel, discord.Thread)):
            return await interaction.followup.send(
                "This command can only be used in server text channels or threads.",
                ephemeral=True
            )

        # Check bot permissions
        bot_perms = channel.permissions_for(channel.guild.me)
        if not bot_perms.manage_webhooks:
            return await interaction.followup.send(
                "I don't have permission to manage webhooks in this channel.",
                ephemeral=True
            )
        if attachment is not None and not bot_perms.attach_files:
            return await interaction.followup.send(
                "I don't have permission to attach files in this channel.",
                ephemeral=True
            )

        # Check user permissions for attaching files
        user_perms = channel.permissions_for(interaction.user)
        if attachment is not None and not user_perms.attach_files:
            return await interaction.followup.send(
                "You don't have permission to attach files in this channel.",
                ephemeral=True
            )

        # Build allowed mentions based on the user's permissions
        # If they don't have mention_everyone, we silence @everyone and role pings
        can_mention_everyone = interaction.user.guild_permissions.mention_everyone
        allowed_mentions = discord.AllowedMentions(
            everyone=can_mention_everyone,
            roles=can_mention_everyone,
            users=True,
            replied_user=False
        )

        # Create webhook
        webhook = await channel.create_webhook(
            name=interaction.user.display_name
        )

        file_kwarg = {}
        if attachment is not None:
            file_bytes = await attachment.read()
            file = discord.File(fp=file_bytes, filename=attachment.filename)
            file_kwarg["file"] = file

        try:
            await webhook.send(
                content=message,
                username=interaction.user.display_name,
                avatar_url=interaction.user.display_avatar.url,
                allowed_mentions=allowed_mentions,
                **file_kwarg
            )
        finally:
            # Always try to delete the webhook, even if sending fails
            try:
                await webhook.delete()
            except discord.HTTPException:
                pass

        await interaction.followup.send("Message sent!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(WebhookSender(bot))
