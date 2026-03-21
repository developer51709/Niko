# error_handler.py
import discord
from discord.ext import commands
import traceback
import sys
import datetime
import asyncio
import requests
from colorama import Fore, Style, init as colorama_init

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

from requests.exceptions import (
    JSONDecodeError
)

colorama_init(autoreset=True)

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Utility: clean colored logging
    def log(self, level, message):
        colors = {
            "INFO": Fore.CYAN,
            "WARN": Fore.YELLOW,
            "ERROR": Fore.RED,
            "CRITICAL": Fore.MAGENTA,
        }
        color = colors.get(level, Fore.WHITE)
        print(f"{color}[{level}] {Style.RESET_ALL}{message}")

    # Utility: embed generator
    def error_embed(self, title, description):
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=f"### ⚠️ {title}\n{description}"
                ),
                accessory=discord.ui.Thumbnail(self.bot.user.avatar.url)
            )
        )
        view.add_item(container)
        return view
        # return discord.Embed(
        #     title=title,
        #     description=description,
        #     color=discord.Color.red(),
        #     timestamp=datetime.datetime.utcnow()
        # )

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

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
            view = self.error_embed(
                "Missing Permissions",
                f"You lack the required permissions: `{', '.join(error.missing_permissions)}`"
            )
            await ctx.reply(view=view)
            self.log("WARN", f"{ctx.author} tried to use {ctx.command} without permissions")
            return

        if isinstance(error, BotMissingPermissions):
            view = self.error_embed(
                "Bot Missing Permissions",
                f"I need these permissions to run this command: `{', '.join(error.missing_permissions)}`"
            )
            await ctx.reply(view=view)
            self.log("ERROR", f"Bot missing permissions for {ctx.command}")
            return

        if isinstance(error, MissingRole):
            view = self.error_embed(
                "Missing Role",
                f"You must have the `{error.missing_role}` role to use this command."
            )
            await ctx.reply(view=view)
            self.log("WARN", f"{ctx.author} missing role {error.missing_role}")
            return

        if isinstance(error, MissingAnyRole):
            view = self.error_embed(
                "Missing Required Roles",
                f"You need **one** of these roles: `{', '.join(error.missing_roles)}`"
            )
            await ctx.reply(view=view)
            self.log("WARN", f"{ctx.author} missing any of roles {error.missing_roles}")
            return

        if isinstance(error, CommandOnCooldown):
            view = self.error_embed(
                "Cooldown Active",
                f"Try again in `{error.retry_after:.1f}` seconds."
            )
            await ctx.reply(view=view)
            self.log("INFO", f"{ctx.author} hit cooldown on {ctx.command}")
            return

        if isinstance(error, MissingRequiredArgument):
            view = self.error_embed(
                "Missing Argument",
                f"You're missing a required argument: `{error.param.name}`"
            )
            await ctx.reply(view=view)
            self.log("WARN", f"{ctx.author} missing argument {error.param.name}")
            return

        if isinstance(error, BadArgument):
            view = self.error_embed(
                "Invalid Argument",
                "One or more arguments were invalid. Check your input and try again."
            )
            await ctx.reply(view=view)
            self.log("WARN", f"Bad argument from {ctx.author} in {ctx.command}")
            return

        if isinstance(error, NoPrivateMessage):
            view = self.error_embed(
                "Not Allowed in DMs",
                "This command can only be used in a server."
            )
            await ctx.author.send(view=view)
            self.log("INFO", f"{ctx.author} tried using {ctx.command} in DMs")
            return

        if isinstance(error, PrivateMessageOnly):
            view = self.error_embed(
                "DM Only Command",
                "This command can only be used in private messages."
            )
            await ctx.reply(view=view)
            self.log("INFO", f"{ctx.author} tried using DM-only command in a guild")
            return

        if isinstance(error, NSFWChannelRequired):
            view = self.error_embed(
                "NSFW Required",
                "This command can only be used in an NSFW channel."
            )
            await ctx.reply(view=view)
            self.log("WARN", f"{ctx.author} attempted NSFW command in non-NSFW channel")
            return

        # --- NotOwner ---
        if isinstance(error, NotOwner):
            view = self.error_embed(
                "Owner Only",
                "Only the bot owner can use this command."
            )
            await ctx.reply(view=view)
            self.log("WARN", f"{ctx.author} attempted owner-only command")
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
            self.log("WARN", f"Lookup error: {error}")
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
            self.log("ERROR", f"API error: {error}")
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
            self.log("WARN", f"Handled known error: {error}")
            return

        # --- Unexpected / Critical Errors ---
        self.log("CRITICAL", f"Unexpected error in command {ctx.command}: {error}")
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

        view = self.error_embed(
            "Unexpected Error",
            "An unexpected error occurred. The developers have been notified."
        )
        await ctx.reply(view=view)

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))