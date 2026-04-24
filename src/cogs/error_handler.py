# error_handler.py
import discord
from discord.ext import commands
import traceback
import sys
import datetime
import asyncio
import requests
from colorama import Fore, Style, init as colorama_init
from config.emojis import get_emoji
from utils import logging
from utils.ai_debugging import send_debug_report
from utils.blacklist_manager import BlacklistManager

from discord.ext.commands import (
    CommandError, CommandInvokeError, CommandNotFound,
    MissingPermissions, MissingRequiredArgument, BadArgument,
    CommandOnCooldown, EmojiNotFound, NotOwner, MissingRole,
    BotMissingPermissions, NSFWChannelRequired, NoPrivateMessage,
    PrivateMessageOnly, CheckFailure, MaxConcurrencyReached,
    MissingAnyRole, MemberNotFound, RoleNotFound, ChannelNotFound,
    ChannelNotReadable, BadColourArgument, BadInviteArgument,
    TooManyArguments, BadUnionArgument, ConversionError,
    UserNotFound, MessageNotFound, GuildNotFound, BadBoolArgument,
    ArgumentParsingError, UnexpectedQuoteError,
    InvalidEndOfQuotedStringError, ExpectedClosingQuoteError,
    DisabledCommand, CommandRegistrationError,
    ExtensionError, ExtensionAlreadyLoaded, ExtensionNotLoaded,
    NoEntryPointError, ExtensionFailed, ExtensionNotFound
)

from discord.errors import (
    Forbidden, HTTPException
)

from requests.exceptions import (
    JSONDecodeError
)

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
        blacklist_manager = BlacklistManager()
        user_entry = blacklist_manager.get_user_entry(ctx.author.id)
        if user_entry:
            reason = user_entry.get("reason") or "No reason provided."
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('icon_danger')} Blacklisted"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"You have been blacklisted from using this bot.\n**Reason:** {reason}\n\nIf you believe this is a mistake, please open a ticket in the support server."
                )
            )
            view.add_item(container)
            await ctx.send(view=view)
            return False
        if ctx.guild:
            guild_entry = blacklist_manager.get_guild_entry(ctx.guild.id)
            if guild_entry:
                reason = guild_entry.get("reason") or "No reason provided."
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"### {get_emoji('icon_danger')} Blacklisted"
                    ),
                    discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                    discord.ui.TextDisplay(
                        content=f"This server has been blacklisted from using this bot.\n**Reason:** {reason}\n\nIf you believe this is a mistake, please open a ticket in the support server."
                    )
                )
                view.add_item(container)
                await ctx.send(view=view)
                return False
        return True

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
    async def on_command_error(self: commands.Cog, ctx: commands.Context, error: commands.CommandError, *args, **kwargs):

        # Ignore errors already handled locally
        if hasattr(ctx.command, "on_error"):
            return

        # Unwrap original error
        error = getattr(error, "original", error)

        # --- Quiet / Ignored Errors ---
        if isinstance(error, CommandNotFound):
            return  # silently ignore unknown commands

        # --- User-Facing Errors (with embeds) ---
        if isinstance(error, MissingPermissions):
            # owner bypass
            owner_bypass = False
            if owner_bypass:
                if await is_owner().predicate(ctx):
                    if not args:
                        args = ctx.message.content.split()[1:]
                        if args:
                            args = [arg for arg in args]
                            args = [int(arg) if arg.isdigit() else arg for arg in args]
                            if ctx.command.parent:
                                args = args[1:]
                    command_cog = ctx.command.cog
                    await ctx.command.callback(command_cog, ctx, *args, **kwargs)
                    logging.warning("error_handler", f"Permission check bypassed for trusted owner {ctx.author}")
                    return
            view = self.error_embed(
                "Missing Permissions",
                f"You lack the required permissions: `{', '.join(error.missing_permissions)}`"
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"{ctx.author} tried to use {ctx.command} without permissions")
            return

        if isinstance(error, BotMissingPermissions):
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
                f"I don't have permission to perform this action. Please check my roles and permissions."
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"403 Forbidden in {ctx.command}")
            return

        if isinstance(error, MissingRole):
            view = self.error_embed(
                "Missing Role",
                f"You must have the `{error.missing_role}` role to use this command."
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"{ctx.author} missing role {error.missing_role}")
            return

        if isinstance(error, MissingAnyRole):
            view = self.error_embed(
                "Missing Required Roles",
                f"You need **one** of these roles: `{', '.join(error.missing_roles)}`"
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"{ctx.author} missing any of roles {error.missing_roles}")
            return

        if isinstance(error, CommandOnCooldown):
            view = self.error_embed(
                "Cooldown Active",
                f"Try again in `{error.retry_after:.1f}` seconds."
            )
            await ctx.reply(view=view)
            logging.info("error_handler", f"{ctx.author} hit cooldown on {ctx.command}")
            return

        if isinstance(error, MissingRequiredArgument):
            view = self.error_embed(
                "Missing Argument",
                f"You're missing a required argument: `{error.param.name}`"
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"{ctx.author} missing argument {error.param.name}")
            return

        if isinstance(error, BadArgument):
            view = self.error_embed(
                "Invalid Argument",
                "One or more arguments were invalid. Check your input and try again."
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"Bad argument from {ctx.author} in {ctx.command}")
            return

        if isinstance(error, NoPrivateMessage):
            view = self.error_embed(
                "Not Allowed in DMs",
                "This command can only be used in a server."
            )
            await ctx.author.send(view=view)
            logging.info("error_handler", f"{ctx.author} tried using {ctx.command} in DMs")
            return

        if isinstance(error, PrivateMessageOnly):
            view = self.error_embed(
                "DM Only Command",
                "This command can only be used in private messages."
            )
            await ctx.reply(view=view)
            logging.info("error_handler", f"{ctx.author} tried using DM-only command in a guild")
            return

        if isinstance(error, NSFWChannelRequired):
            view = self.error_embed(
                "NSFW Required",
                "This command can only be used in an NSFW channel."
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"{ctx.author} attempted NSFW command in non-NSFW channel")
            return

        # --- NotOwner ---
        if isinstance(error, NotOwner):
            view = self.error_embed(
                "Owner Only",
                "Only the bot owner can use this command."
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"{ctx.author} attempted owner-only command")
            return

        # --- Lookup Errors (Member/Role/Channel/etc.) ---
        lookup_errors = (
            MemberNotFound, RoleNotFound, ChannelNotFound, UserNotFound,
            MessageNotFound, GuildNotFound, EmojiNotFound
        )
        if isinstance(error, lookup_errors):
            view = self.error_embed(
                "Not Found",
                str(error)
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"Lookup error: {error}")
            return

        # --- API Errors ---
        api_errors = (
            JSONDecodeError, 
        )
        if isinstance(error, api_errors):
            view = self.error_embed(
                "API Error",
                "There was an issue with the API request. Please try again later.\n-# Error: " + str(error)
            )
            await ctx.reply(view=view)
            logging.error("error_handler", f"API error: {error}")
            return

        # --- Other Known Errors (non-fatal) ---
        other_known = (
            TooManyArguments, BadUnionArgument, ConversionError,
            BadColourArgument, BadInviteArgument, BadBoolArgument,
            ArgumentParsingError, UnexpectedQuoteError,
            InvalidEndOfQuotedStringError, ExpectedClosingQuoteError,
            DisabledCommand, CommandRegistrationError,
            ExtensionError, ExtensionAlreadyLoaded, ExtensionNotLoaded,
            NoEntryPointError, ExtensionFailed, ExtensionNotFound,
            MaxConcurrencyReached
        )
        if isinstance(error, other_known):
            view = self.error_embed(
                "Error", 
                str(error)
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"Handled known error: {error}")
            return

        # --- CheckFailure ---
        if isinstance(error, CheckFailure):
            view = self.error_embed(
                "Check Failed",
                "You don't meet the requirements to use this command."
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"Check failed for {ctx.author} in {ctx.command}")
            return

        # --- Unexpected / Critical Errors ---
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

        # Send to AI debug channel if configured
        cog_name = ctx.command.cog.__class__.__name__.lower() if ctx.command and ctx.command.cog else None
        # Try to match cog class name to a cog file name
        if cog_name:
            import os as _os
            cog_files = [f[:-3] for f in _os.listdir("src/cogs") if f.endswith(".py")]
            if cog_name not in cog_files:
                cog_name = None
        asyncio.create_task(send_debug_report(self.bot, error, cog_name=cog_name))


    # send other errors to the AI debug channel
    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        error = sys.exc_info()[1]
        self.log("CRITICAL", f"Unexpected error in {event}: {error}")
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        # Send to AI debug channel if configured
        cog_name = args[0].command.cog.__class__.__name__.lower() if args and args[0].command and args[0].command.cog else None
        # Try to match cog class name to a cog file name
        if cog_name:
            import os as _os
            cog_files = [f[:-3] for f in _os.listdir("src/cogs") if f.endswith(".py")]
            if cog_name not in cog_files:
                cog_name = None
        asyncio.create_task(send_debug_report(self.bot, error, cog_name=cog_name))
        

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))