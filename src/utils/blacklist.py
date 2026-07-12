"""
Blacklist helpers — message-level and interaction-level checks.
Both return True / False (blocked or not).
"""
import discord
from config.emojis import get_emoji
from utils.blacklist_manager import BlacklistManager


async def check_message_blacklist(msg: discord.Message) -> bool:
    """
    Returns True (and notifies the channel) if the message author or their
    guild is blacklisted.  Call this before processing any command.
    """
    bm = BlacklistManager()

    user_entry = bm.get_user_entry(msg.author.id)
    if user_entry:
        reason = user_entry.get("reason") or "No reason provided."
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_danger')} Blacklisted"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"You are blacklisted from using this bot.\n**Reason:** {reason}\n\n"
                        "If you believe this is a mistake, please open a ticket in the support server."
            ),
            accent_colour=discord.Color.red(),
        ))
        await msg.channel.send(view=view)
        return True

    if msg.guild:
        guild_entry = bm.get_guild_entry(msg.guild.id)
        if guild_entry:
            reason = guild_entry.get("reason") or "No reason provided."
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### {get_emoji('icon_danger')} Blacklisted"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"This server is blacklisted from using this bot.\n**Reason:** {reason}\n\n"
                            "If you believe this is a mistake, please open a ticket in the support server."
                ),
                accent_colour=discord.Color.red(),
            ))
            await msg.channel.send(view=view)
            return True

    return False


async def check_interaction_blacklist(interaction: discord.Interaction) -> bool:
    """
    Returns False (and sends an ephemeral notice) if the user or guild is
    blacklisted.  Attach to bot.tree.interaction_check.
    """
    bm = BlacklistManager()

    user_entry = bm.get_user_entry(interaction.user.id)
    if user_entry:
        reason = user_entry.get("reason") or "No reason provided."
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_danger')} Blacklisted"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"You are blacklisted from using this bot.\n**Reason:** {reason}\n\n"
                        "If you believe this is a mistake, please open a ticket in the support server."
            ),
            accent_colour=discord.Color.red(),
        ))
        try:
            await interaction.response.send_message(view=view, ephemeral=True)
        except Exception:
            pass
        return False

    if interaction.guild:
        guild_entry = bm.get_guild_entry(interaction.guild.id)
        if guild_entry:
            reason = guild_entry.get("reason") or "No reason provided."
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### {get_emoji('icon_danger')} Blacklisted"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"This server is blacklisted from using this bot.\n**Reason:** {reason}\n\n"
                            "If you believe this is a mistake, please open a ticket in the support server."
                ),
                accent_colour=discord.Color.red(),
            ))
            try:
                await interaction.response.send_message(view=view, ephemeral=True)
            except Exception:
                pass
            return False

    return True
