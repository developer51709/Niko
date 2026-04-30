# error_handler.py
import discord
from discord.ext import commands
from discord import app_commands
import traceback
import sys
import json
import datetime
import asyncio
from colorama import Fore, Style, init as colorama_init
from config.emojis import get_emoji
from utils import logging
from utils.ai_debugging import send_debug_report
from utils.blacklist_manager import BlacklistManager

# ── Prefix-command errors ───────────────────────────────────────────────
from discord.ext.commands import (
    CommandError, CommandInvokeError,
    CommandNotFound        as PfxCommandNotFound,
    MissingPermissions     as PfxMissingPermissions,
    MissingRequiredArgument, BadArgument,
    CommandOnCooldown      as PfxCommandOnCooldown,
    EmojiNotFound, NotOwner,
    MissingRole            as PfxMissingRole,
    BotMissingPermissions  as PfxBotMissingPermissions,
    NSFWChannelRequired    as PfxNSFWChannelRequired,
    NoPrivateMessage       as PfxNoPrivateMessage,
    PrivateMessageOnly, CheckFailure as PfxCheckFailure,
    MaxConcurrencyReached,
    MissingAnyRole         as PfxMissingAnyRole,
    MemberNotFound, RoleNotFound, ChannelNotFound,
    ChannelNotReadable, BadColourArgument, BadInviteArgument,
    TooManyArguments, BadUnionArgument, ConversionError,
    UserNotFound, MessageNotFound, GuildNotFound, BadBoolArgument,
    ArgumentParsingError, UnexpectedQuoteError,
    InvalidEndOfQuotedStringError, ExpectedClosingQuoteError,
    DisabledCommand, CommandRegistrationError,
    ExtensionError, ExtensionAlreadyLoaded, ExtensionNotLoaded,
    NoEntryPointError, ExtensionFailed, ExtensionNotFound,
)

# ── Slash-command errors ────────────────────────────────────────────────
from discord.app_commands import (
    CommandNotFound        as SlashCommandNotFound,
    MissingPermissions     as SlashMissingPermissions,
    MissingRole            as SlashMissingRole,
    MissingAnyRole         as SlashMissingAnyRole,
    BotMissingPermissions  as SlashBotMissingPermissions,
    NoPrivateMessage       as SlashNoPrivateMessage,
    CheckFailure           as SlashCheckFailure,
    CommandOnCooldown      as SlashCommandOnCooldown,
    CommandInvokeError     as SlashCommandInvokeError,
    TransformerError, CommandSignatureMismatch,
)

from discord.errors import Forbidden, HTTPException

colorama_init(autoreset=True)


# Optional: Add your owner IDs here if you want multiple owners
OWNER_IDS = {
    1435978243160145981, 
    1485732377958416565,
    1492310425348608170,
    1495618222488162439
}


def is_owner():
    """Custom owner check to support multiple owners."""
    async def predicate(ctx):
        return ctx.author.id in OWNER_IDS or await ctx.bot.is_owner(ctx.author)
    return commands.check(predicate)

def under_development(feature = None):
    async def predicate(ctx):
        if not is_owner():
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('icon_settings')} Under Development"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content="This feature is currently under development. Please feel free to check back later for updates or send some suggestions in the support server."
                )
            )
            view.add_item(container)
            await ctx.send(view=view)
            return False
        return True
    return commands.check(predicate)

def is_premium():
    # check for the premium role in the main guild
    async def predicate(ctx):
        premium_role_id = 1493294143600853062
        support_server_id = 1470878953743974587
        # error response
        error_view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('icon_danger')} Premium Required"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content="This feature is only available to premium users. You can get premium by joining the support server and boosting or making a donation to support the bot's development."
            )
        )
        guild = ctx.bot.get_guild(support_server_id)
        if guild is None:
            await ctx.send(view=error_view)
            return False
        role = guild.get_role(premium_role_id)
        if role is None:
            await ctx.send(view=error_view)
            return False
        member = guild.get_member(ctx.author.id)
        if member is None:
            await ctx.send(view=error_view)
            return False
        if role not in member.roles:
            await ctx.send(view=error_view)
            return False
        return True
    return commands.check(predicate)

def is_blacklisted():
    async def predicate(ctx):
        bm = BlacklistManager()
        user_entry = bm.get_user_entry(ctx.author.id)
        if user_entry:
            reason = user_entry.get("reason") or "No reason provided."
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### {get_emoji('icon_danger')} Blacklisted"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content=f"You have been blacklisted from using this bot.\n**Reason:** {reason}\n\nIf you believe this is a mistake, please open a ticket in the support server."),
                accent_colour=discord.Color.red()
            ))
            await ctx.send(view=view)
            return False
        if ctx.guild:
            guild_entry = bm.get_guild_entry(ctx.guild.id)
            if guild_entry:
                reason = guild_entry.get("reason") or "No reason provided."
                view = discord.ui.LayoutView()
                view.add_item(discord.ui.Container(
                    discord.ui.TextDisplay(content=f"### {get_emoji('icon_danger')} Blacklisted"),
                    discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                    discord.ui.TextDisplay(content=f"This server has been blacklisted from using this bot.\n**Reason:** {reason}\n\nIf you believe this is a mistake, please open a ticket in the support server."),
                    accent_colour=discord.Color.red()
                ))
                await ctx.send(view=view)
                return False
        return True
    return commands.check(predicate)

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # Utility: embed generator
    def error_embed(self, title, description):
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('icon_danger')} {title}"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=description
            )
        )
        view.add_item(container)
        return view

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):

        # Ignore errors already handled locally by the command
        if hasattr(ctx.command, "on_error"):
            return

        # Unwrap CommandInvokeError to get the original exception
        error = getattr(error, "original", error)

        # ── Silent / ignored ───────────────────────────────────────────────
        if isinstance(error, PfxCommandNotFound):
            return

        # ── Permission errors ──────────────────────────────────────────────
        if isinstance(error, PfxMissingPermissions):
            view = self.error_embed(
                "Missing Permissions",
                f"You lack the required permissions: `{', '.join(error.missing_permissions)}`"
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"{ctx.author} tried {ctx.command} without permissions")
            return

        if isinstance(error, PfxBotMissingPermissions):
            view = self.error_embed(
                "Bot Missing Permissions",
                f"I need these permissions to run this command: `{', '.join(error.missing_permissions)}`"
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"Bot missing permissions for {ctx.command}")
            return

        if isinstance(error, Forbidden):
            view = self.error_embed(
                "Forbidden Action",
                "I don't have permission to perform this action. Please check my roles and permissions."
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"403 Forbidden in {ctx.command}")
            return

        if isinstance(error, PfxMissingRole):
            view = self.error_embed(
                "Missing Role",
                f"You must have the `{error.missing_role}` role to use this command."
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"{ctx.author} missing role {error.missing_role}")
            return

        if isinstance(error, PfxMissingAnyRole):
            view = self.error_embed(
                "Missing Required Roles",
                f"You need **one** of these roles: `{', '.join(str(r) for r in error.missing_roles)}`"
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"{ctx.author} missing any of roles {error.missing_roles}")
            return

        # ── Cooldown ───────────────────────────────────────────────────────
        if isinstance(error, PfxCommandOnCooldown):
            view = self.error_embed(
                "Cooldown Active",
                f"Try again in `{error.retry_after:.1f}` seconds."
            )
            await ctx.reply(view=view)
            logging.info("error_handler", f"{ctx.author} hit cooldown on {ctx.command}")
            return

        # ── Argument errors ────────────────────────────────────────────────
        if isinstance(error, MissingRequiredArgument):
            view = self.error_embed(
                "Missing Argument",
                f"You're missing a required argument: `{error.param.name}`"
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"{ctx.author} missing arg {error.param.name}")
            return

        if isinstance(error, BadArgument):
            view = self.error_embed(
                "Invalid Argument",
                "One or more arguments were invalid. Check your input and try again."
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"Bad argument from {ctx.author} in {ctx.command}")
            return

        # ── Channel restrictions ───────────────────────────────────────────
        if isinstance(error, PfxNoPrivateMessage):
            view = self.error_embed("Not Allowed in DMs", "This command can only be used in a server.")
            try:
                await ctx.author.send(view=view)
            except discord.HTTPException:
                pass
            logging.info("error_handler", f"{ctx.author} tried {ctx.command} in DMs")
            return

        if isinstance(error, PrivateMessageOnly):
            view = self.error_embed("DM Only Command", "This command can only be used in private messages.")
            await ctx.reply(view=view)
            logging.info("error_handler", f"{ctx.author} tried DM-only command in guild")
            return

        if isinstance(error, PfxNSFWChannelRequired):
            view = self.error_embed("NSFW Required", "This command can only be used in an NSFW channel.")
            await ctx.reply(view=view)
            logging.warning("error_handler", f"{ctx.author} used NSFW command in non-NSFW channel")
            return

        # ── Owner only ─────────────────────────────────────────────────────
        if isinstance(error, NotOwner):
            view = self.error_embed("Owner Only", "Only the bot owner can use this command.")
            await ctx.reply(view=view)
            logging.warning("error_handler", f"{ctx.author} attempted owner-only command")
            return

        # ── Lookup errors ──────────────────────────────────────────────────
        lookup_errors = (
            MemberNotFound, RoleNotFound, ChannelNotFound, UserNotFound,
            MessageNotFound, GuildNotFound, EmojiNotFound
        )
        if isinstance(error, lookup_errors):
            view = self.error_embed("Not Found", str(error))
            await ctx.reply(view=view)
            logging.warning("error_handler", f"Lookup error: {error}")
            return

        # ── HTTP / API errors ──────────────────────────────────────────────
        if isinstance(error, HTTPException):
            view = self.error_embed(
                "Discord API Error",
                f"A Discord API error occurred (HTTP {error.status}). Please try again.\n-# {error.text}"
            )
            try:
                await ctx.reply(view=view)
            except discord.HTTPException:
                pass
            logging.error("error_handler", f"HTTPException in {ctx.command}: {error}")
            return

        if isinstance(error, json.JSONDecodeError):
            view = self.error_embed(
                "API Error",
                "There was an issue decoding the API response. Please try again later."
            )
            await ctx.reply(view=view)
            logging.error("error_handler", f"JSONDecodeError in {ctx.command}: {error}")
            return

        # ── Other known non-fatal errors ───────────────────────────────────
        other_known = (
            TooManyArguments, BadUnionArgument, ConversionError,
            BadColourArgument, BadInviteArgument, BadBoolArgument,
            ArgumentParsingError, UnexpectedQuoteError,
            InvalidEndOfQuotedStringError, ExpectedClosingQuoteError,
            DisabledCommand, CommandRegistrationError,
            ExtensionError, ExtensionAlreadyLoaded, ExtensionNotLoaded,
            NoEntryPointError, ExtensionFailed, ExtensionNotFound,
            MaxConcurrencyReached,
        )
        if isinstance(error, other_known):
            view = self.error_embed("Error", str(error))
            await ctx.reply(view=view)
            logging.warning("error_handler", f"Known error in {ctx.command}: {error}")
            return

        # ── Check failure (generic) ────────────────────────────────────────
        if isinstance(error, PfxCheckFailure):
            view = self.error_embed(
                "Check Failed",
                "You don't meet the requirements to use this command."
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"Check failed for {ctx.author} in {ctx.command}")
            return

        # ── Unexpected / critical errors ───────────────────────────────────
        logging.error("error_handler", f"Unexpected error in command {ctx.command}: {error}")
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

        view = self.error_embed(
            "Unexpected Error",
            "An unexpected error occurred. The developers have been notified."
        )
        try:
            await ctx.reply(view=view)
        except discord.HTTPException:
            pass

        cog_name = ctx.command.cog.__class__.__name__.lower() if ctx.command and ctx.command.cog else None
        if cog_name:
            import os as _os
            cog_files = [f[:-3] for f in _os.listdir("src/cogs") if f.endswith(".py")]
            if cog_name not in cog_files:
                cog_name = None
        asyncio.create_task(send_debug_report(self.bot, error, cog_name=cog_name))


    # ── Slash command error handler ────────────────────────────────────────
    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        error = getattr(error, "original", error)

        async def _reply(view):
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(view=view, ephemeral=True)
                else:
                    await interaction.response.send_message(view=view, ephemeral=True)
            except discord.HTTPException:
                pass

        if isinstance(error, (SlashCommandNotFound, CommandSignatureMismatch)):
            return

        if isinstance(error, Forbidden):
            await _reply(self.error_embed("Forbidden Action", "I don't have permission to perform this action. Please check my roles and permissions."))
            logging.warning("error_handler", f"403 Forbidden in slash {interaction.command}")
            return

        if isinstance(error, SlashMissingPermissions):
            await _reply(self.error_embed("Missing Permissions", f"You lack the required permissions: `{', '.join(error.missing_permissions)}`"))
            logging.warning("error_handler", f"{interaction.user} missing perms for slash {interaction.command}")
            return

        if isinstance(error, SlashBotMissingPermissions):
            await _reply(self.error_embed("Bot Missing Permissions", f"I need these permissions: `{', '.join(error.missing_permissions)}`"))
            logging.warning("error_handler", f"Bot missing perms for slash {interaction.command}")
            return

        if isinstance(error, SlashMissingRole):
            await _reply(self.error_embed("Missing Role", f"You must have the `{error.missing_role}` role to use this command."))
            logging.warning("error_handler", f"{interaction.user} missing role {error.missing_role}")
            return

        if isinstance(error, SlashMissingAnyRole):
            await _reply(self.error_embed("Missing Required Roles", f"You need **one** of these roles: `{', '.join(str(r) for r in error.missing_roles)}`"))
            logging.warning("error_handler", f"{interaction.user} missing any roles {error.missing_roles}")
            return

        if isinstance(error, SlashCommandOnCooldown):
            await _reply(self.error_embed("Cooldown Active", f"Try again in `{error.retry_after:.1f}` seconds."))
            logging.info("error_handler", f"{interaction.user} hit cooldown on slash {interaction.command}")
            return

        if isinstance(error, SlashNoPrivateMessage):
            await _reply(self.error_embed("Not Allowed in DMs", "This command can only be used in a server."))
            logging.info("error_handler", f"{interaction.user} tried slash {interaction.command} in DMs")
            return

        if isinstance(error, SlashCheckFailure):
            await _reply(self.error_embed("Check Failed", "You don't meet the requirements to use this command."))
            logging.warning("error_handler", f"Slash check failed for {interaction.user} in {interaction.command}")
            return

        if isinstance(error, TransformerError):
            await _reply(self.error_embed("Invalid Argument", f"Couldn't convert `{error.value}` to the expected type."))
            logging.warning("error_handler", f"TransformerError in slash {interaction.command}: {error}")
            return

        if isinstance(error, HTTPException):
            await _reply(self.error_embed("Discord API Error", f"A Discord API error occurred (HTTP {error.status}). Please try again."))
            logging.error("error_handler", f"HTTPException in slash {interaction.command}: {error}")
            return

        # ── Unexpected critical ────────────────────────────────────────────
        logging.error("error_handler", f"Unexpected error in slash {interaction.command}: {error}")
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        await _reply(self.error_embed("Unexpected Error", "An unexpected error occurred. The developers have been notified."))

        cog_name = interaction.command.cog.__class__.__name__.lower() if interaction.command and interaction.command.cog else None
        if cog_name:
            import os as _os
            cog_files = [f[:-3] for f in _os.listdir("src/cogs") if f.endswith(".py")]
            if cog_name not in cog_files:
                cog_name = None
        asyncio.create_task(send_debug_report(self.bot, error, cog_name=cog_name))


    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        error = sys.exc_info()[1]
        if error is None:
            return
        logging.error("error_handler", f"Unexpected error in event {event}: {error}")
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        asyncio.create_task(send_debug_report(self.bot, error, cog_name=None))
        

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))