# error_handler.py
import discord
from discord.ext import commands
from discord import app_commands
import traceback
import sys
import json
import datetime
import asyncio
import platform
from contextvars import ContextVar
from colorama import Fore, Style, init as colorama_init
from utils.error_reports import save_error_report
from config.emojis import get_emoji
from config.ids import OWNER_IDS
from config.links import WEBSITE
from utils import logging
from utils.ai.debugging import send_debug_report
from utils.blacklist_manager import BlacklistManager
from utils.i18n import make_flat_msg
from utils.locales import load_locales

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

MESSAGES = load_locales(__package__, "errors")
msg = make_flat_msg(MESSAGES)
_ERROR_REPORT_CODE: ContextVar[str | None] = ContextVar("error_report_code", default=None)


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
                    content=f"### {get_emoji('settings')} {msg(ctx, 'under_development_title')}"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content=msg(ctx, "under_development_body"))
            )
            view.add_item(container)
            await ctx.send(view=view)
            return False
        return True
    return commands.check(predicate)

def is_premium():
    """Check whether the invoking user has been granted premium by an owner."""
    async def predicate(ctx):
        from utils.premium_manager import PremiumManager
        if await PremiumManager.is_premium(ctx.bot.cxn, ctx.author.id):
            return True
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('warning')} {msg(ctx, 'premium_title')}"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=msg(ctx, "premium_body")),
            accent_colour=discord.Color.red(),
        ))
        await ctx.send(view=view)
        return False
    return commands.check(predicate)

def is_blacklisted():
    async def predicate(ctx):
        bm = BlacklistManager()
        user_entry = bm.get_user_entry(ctx.author.id)
        if user_entry:
            reason = user_entry.get("reason") or msg(ctx, "no_reason")
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### {get_emoji('warning')} {msg(ctx, 'blacklisted_title')}"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content=msg(
                    ctx, "blacklisted_user",
                    reason=reason,
                    appeal=f"{WEBSITE}/appeals/blacklist",
                )),
                accent_colour=discord.Color.red()
            ))
            await ctx.send(view=view)
            return False
        if ctx.guild:
            guild_entry = bm.get_guild_entry(ctx.guild.id)
            if guild_entry:
                reason = guild_entry.get("reason") or msg(ctx, "no_reason")
                view = discord.ui.LayoutView()
                view.add_item(discord.ui.Container(
                    discord.ui.TextDisplay(content=f"### {get_emoji('warning')} {msg(ctx, 'blacklisted_title')}"),
                    discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                    discord.ui.TextDisplay(content=msg(
                        ctx, "blacklisted_guild",
                        reason=reason,
                        support=f"{WEBSITE}/support",
                    )),
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
    def error_embed(self, title, description, report_code: str | None = None):
        report_code = report_code or _ERROR_REPORT_CODE.get()
        if report_code:
            description = f"{description}\n\n-# Error report code: `{report_code}`"
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('warning')} {title}"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=description
            )
        )
        view.add_item(container)
        return view

    @staticmethod
    def _prefix_report_details(ctx: commands.Context) -> str:
        command = ctx.command
        guild = ctx.guild
        channel = ctx.channel
        message = ctx.message
        args = getattr(ctx, "args", ())
        kwargs = getattr(ctx, "kwargs", {})
        arg_offset = 2 if command and command.cog else 1
        parsed_args = args[arg_offset:] if len(args) >= arg_offset else args
        return (
            "Invocation context\n"
            "------------------\n"
            f"Source: Prefix command\n"
            f"Command: {command.qualified_name if command else '(unknown)'}\n"
            f"Signature: {command.signature if command else '(unknown)'}\n"
            f"Exact invocation: {getattr(message, 'content', '(unavailable)')}\n"
            f"Parsed positional args: {parsed_args!r}\n"
            f"Parsed keyword args: {kwargs!r}\n"
            f"User: {ctx.author} (ID {ctx.author.id})\n"
            f"Guild: {guild.name if guild else '(DM)'} (ID {guild.id if guild else 'n/a'})\n"
            f"Channel: {getattr(channel, 'name', channel)} (ID {getattr(channel, 'id', 'n/a')})\n"
            f"Message ID: {getattr(message, 'id', 'n/a')}\n"
            f"Message created at: {getattr(message, 'created_at', 'n/a')}\n"
            f"Shard ID: {getattr(guild, 'shard_id', 'n/a') if guild else 'n/a'}\n"
            f"Bot user: {ctx.bot.user} (ID {getattr(ctx.bot.user, 'id', 'n/a')})\n"
            f"Python: {platform.python_version()}\n"
        )

    @staticmethod
    def _slash_report_details(interaction: discord.Interaction) -> str:
        command = interaction.command
        guild = interaction.guild
        channel = interaction.channel
        try:
            arguments = json.dumps(interaction.data, ensure_ascii=False, indent=2, default=str)
        except Exception:
            arguments = repr(getattr(interaction, 'data', None))
        return (
            "Invocation context\n"
            "------------------\n"
            f"Source: Slash command\n"
            f"Command: {command.qualified_name if command else '(unknown)'}\n"
            f"Interaction ID: {interaction.id}\n"
            f"Interaction created at: {interaction.created_at}\n"
            f"Exact command arguments (interaction payload):\n{arguments}\n"
            f"User: {interaction.user} (ID {interaction.user.id})\n"
            f"Guild: {guild.name if guild else '(DM)'} (ID {guild.id if guild else 'n/a'})\n"
            f"Channel: {getattr(channel, 'name', channel)} (ID {getattr(channel, 'id', 'n/a')})\n"
            f"Shard ID: {getattr(guild, 'shard_id', 'n/a') if guild else 'n/a'}\n"
            f"Bot user: {interaction.client.user} (ID {getattr(interaction.client.user, 'id', 'n/a')})\n"
            f"Python: {platform.python_version()}\n"
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):

        # Unwrap CommandInvokeError to get the original exception
        error = getattr(error, "original", error)

        # ── Automated anti-abuse strike ────────────────────────────────────
        from utils.abuse_detection import AbuseRateLimit, strike_notice
        if isinstance(error, AbuseRateLimit):
            await ctx.send(strike_notice(error.result))
            return

        # ── Silent / ignored ───────────────────────────────────────────────
        if isinstance(error, PfxCommandNotFound):
            return

        report_code, _ = await save_error_report(error, self._prefix_report_details(ctx), self.bot)
        _ERROR_REPORT_CODE.set(report_code)
        if ctx.command and hasattr(ctx.command, "on_error"):
            # A command-local handler may use error_embed and include the same
            # report code; do not produce a second response here.
            return

        # ── Permission errors ──────────────────────────────────────────────
        if isinstance(error, PfxMissingPermissions):
            view = self.error_embed(
                msg(ctx, "missing_permissions_title"),
                msg(ctx, "missing_permissions_body", perms=", ".join(error.missing_permissions)),
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"{ctx.author} tried {ctx.command} without permissions")
            return

        if isinstance(error, PfxBotMissingPermissions):
            view = self.error_embed(
                msg(ctx, "bot_missing_permissions_title"),
                msg(ctx, "bot_missing_permissions_body", perms=", ".join(error.missing_permissions)),
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"Bot missing permissions for {ctx.command}")
            return

        if isinstance(error, Forbidden):
            view = self.error_embed(
                msg(ctx, "forbidden_title"), msg(ctx, "forbidden_body")
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"403 Forbidden in {ctx.command}")
            return

        if isinstance(error, PfxMissingRole):
            view = self.error_embed(
                msg(ctx, "missing_role_title"),
                msg(ctx, "missing_role_body", role=error.missing_role),
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"{ctx.author} missing role {error.missing_role}")
            return

        if isinstance(error, PfxMissingAnyRole):
            view = self.error_embed(
                msg(ctx, "missing_any_role_title"),
                msg(ctx, "missing_any_role_body", roles=", ".join(str(r) for r in error.missing_roles)),
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"{ctx.author} missing any of roles {error.missing_roles}")
            return

        # ── Cooldown ───────────────────────────────────────────────────────
        if isinstance(error, PfxCommandOnCooldown):
            view = self.error_embed(
                msg(ctx, "cooldown_title"),
                msg(ctx, "cooldown_body", seconds=f"{error.retry_after:.1f}"),
            )
            await ctx.reply(view=view)
            logging.info("error_handler", f"{ctx.author} hit cooldown on {ctx.command}")
            return

        # ── Argument errors ────────────────────────────────────────────────
        if isinstance(error, MissingRequiredArgument):
            view = self.error_embed(
                msg(ctx, "missing_argument_title"),
                msg(ctx, "missing_argument_body", arg=error.param.name),
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"{ctx.author} missing arg {error.param.name}")
            return

        if isinstance(error, BadArgument):
            # Build a helpful message: what went wrong + how to call it right.
            cmd = ctx.command
            if isinstance(error, MemberNotFound):
                reason = msg(ctx, "bad_member", value=error.argument)
            elif isinstance(error, UserNotFound):
                reason = msg(ctx, "bad_user", value=error.argument)
            elif isinstance(error, ChannelNotFound):
                reason = msg(ctx, "bad_channel", value=error.argument)
            elif isinstance(error, RoleNotFound):
                reason = msg(ctx, "bad_role", value=error.argument)
            elif isinstance(error, BadBoolArgument):
                reason = msg(ctx, "bad_bool", value=error.argument)
            elif isinstance(error, BadColourArgument):
                reason = msg(ctx, "bad_colour", value=error.argument)
            elif isinstance(error, BadInviteArgument):
                reason = msg(ctx, "bad_invite", value=error.argument)
            else:
                reason = msg(ctx, "bad_generic", error=error)

            usage = cmd.qualified_name if cmd else None
            sig = cmd.signature if cmd else None
            usage_line = msg(ctx, "usage_line", usage=f".{usage} {sig}" if sig else f".{usage}")

            view = self.error_embed(
                msg(ctx, "invalid_argument_title"),
                msg(ctx, "invalid_argument_body", reason=reason, usage=usage_line),
            )
            await ctx.reply(view=view)
            logging.warning("error_handler", f"Bad argument from {ctx.author} in {ctx.command}: {error}")
            return

        # ── Channel restrictions ───────────────────────────────────────────
        if isinstance(error, PfxNoPrivateMessage):
            view = self.error_embed(msg(ctx, "dm_only_title"), msg(ctx, "dm_only_body"))
            try:
                await ctx.author.send(view=view)
            except discord.HTTPException:
                pass
            logging.info("error_handler", f"{ctx.author} tried {ctx.command} in DMs")
            return

        if isinstance(error, PrivateMessageOnly):
            view = self.error_embed(msg(ctx, "pm_only_title"), msg(ctx, "pm_only_body"))
            await ctx.reply(view=view)
            logging.info("error_handler", f"{ctx.author} tried DM-only command in guild")
            return

        if isinstance(error, PfxNSFWChannelRequired):
            view = self.error_embed(msg(ctx, "nsfw_title"), msg(ctx, "nsfw_body"))
            await ctx.reply(view=view)
            logging.warning("error_handler", f"{ctx.author} used NSFW command in non-NSFW channel")
            return

        # ── Owner only ─────────────────────────────────────────────────────
        if isinstance(error, NotOwner):
            view = self.error_embed(msg(ctx, "owner_title"), msg(ctx, "owner_body"))
            await ctx.reply(view=view)
            logging.warning("error_handler", f"{ctx.author} attempted owner-only command")
            return

        # ── Lookup errors ──────────────────────────────────────────────────
        lookup_errors = (
            MemberNotFound, RoleNotFound, ChannelNotFound, UserNotFound,
            MessageNotFound, GuildNotFound, EmojiNotFound
        )
        if isinstance(error, lookup_errors):
            view = self.error_embed(msg(ctx, "not_found_title"), str(error))
            await ctx.reply(view=view)
            logging.warning("error_handler", f"Lookup error: {error}")
            return

        # ── HTTP / API errors ──────────────────────────────────────────────
        if isinstance(error, HTTPException):
            view = self.error_embed(
                msg(ctx, "api_title"),
                msg(ctx, "api_body", status=error.status, text=error.text),
            )
            try:
                await ctx.reply(view=view)
            except discord.HTTPException:
                pass
            logging.error("error_handler", f"HTTPException in {ctx.command}: {error}")
            return

        if isinstance(error, json.JSONDecodeError):
            view = self.error_embed(msg(ctx, "decode_title"), msg(ctx, "decode_body"))
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
            view = self.error_embed(msg(ctx, "error_title"), str(error))
            await ctx.reply(view=view)
            logging.warning("error_handler", f"Known error in {ctx.command}: {error}")
            return

        # ── Check failure (generic) ────────────────────────────────────────
        if isinstance(error, PfxCheckFailure):
            view = self.error_embed(msg(ctx, "check_failed_title"), msg(ctx, "check_failed_body"))
            await ctx.reply(view=view)
            logging.warning("error_handler", f"Check failed for {ctx.author} in {ctx.command}")
            return

        # ── Unexpected / critical errors ───────────────────────────────────
        logging.error("error_handler", f"Unexpected error in command {ctx.command} (report {report_code}): {error}")
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

        view = self.error_embed(msg(ctx, "unexpected_title"), msg(ctx, "unexpected_body"))
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
        _ERROR_REPORT_CODE.set(None)

    # ── Slash command error handler ────────────────────────────────────────
    # ── Slash command / context menu error handler ──────────────────────────
    # NOTE: discord.py does NOT dispatch an "on_app_command_error" gateway
    # event, so this cannot be a @commands.Cog.listener(). App-command errors
    # flow through CommandTree.on_error, whose default implementation only
    # logs "Ignoring exception in command" and never tells the user. We bind
    # it in setup() below so every slash/context-menu error reaches the
    # interaction.response / interaction.followup replies here.
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
            finally:
                _ERROR_REPORT_CODE.set(None)

        if isinstance(error, (SlashCommandNotFound, CommandSignatureMismatch)):
            return

        report_code, _ = await save_error_report(error, self._slash_report_details(interaction), self.bot)
        _ERROR_REPORT_CODE.set(report_code)
        if interaction.command and interaction.command.on_error:
            return

        if isinstance(error, Forbidden):
            await _reply(self.error_embed(msg(interaction, "forbidden_title"), msg(interaction, "forbidden_body")))
            logging.warning("error_handler", f"403 Forbidden in slash {interaction.command}")
            return

        if isinstance(error, SlashMissingPermissions):
            await _reply(self.error_embed(
                msg(interaction, "missing_permissions_title"),
                msg(interaction, "missing_permissions_body", perms=", ".join(error.missing_permissions)),
            ))
            logging.warning("error_handler", f"{interaction.user} missing perms for slash {interaction.command}")
            return

        if isinstance(error, SlashBotMissingPermissions):
            await _reply(self.error_embed(
                msg(interaction, "bot_missing_permissions_title"),
                msg(interaction, "bot_missing_permissions_short", perms=", ".join(error.missing_permissions)),
            ))
            logging.warning("error_handler", f"Bot missing perms for slash {interaction.command}")
            return

        if isinstance(error, SlashMissingRole):
            await _reply(self.error_embed(
                msg(interaction, "missing_role_title"),
                msg(interaction, "missing_role_body", role=error.missing_role),
            ))
            logging.warning("error_handler", f"{interaction.user} missing role {error.missing_role}")
            return

        if isinstance(error, SlashMissingAnyRole):
            await _reply(self.error_embed(
                msg(interaction, "missing_any_role_title"),
                msg(interaction, "missing_any_role_body", roles=", ".join(str(r) for r in error.missing_roles)),
            ))
            logging.warning("error_handler", f"{interaction.user} missing any roles {error.missing_roles}")
            return

        if isinstance(error, SlashCommandOnCooldown):
            await _reply(self.error_embed(
                msg(interaction, "cooldown_title"),
                msg(interaction, "cooldown_body", seconds=f"{error.retry_after:.1f}"),
            ))
            logging.info("error_handler", f"{interaction.user} hit cooldown on slash {interaction.command}")
            return

        if isinstance(error, SlashNoPrivateMessage):
            await _reply(self.error_embed(msg(interaction, "dm_only_title"), msg(interaction, "dm_only_body")))
            logging.info("error_handler", f"{interaction.user} tried slash {interaction.command} in DMs")
            return

        if isinstance(error, SlashCheckFailure):
            await _reply(self.error_embed(msg(interaction, "check_failed_title"), msg(interaction, "check_failed_body")))
            logging.warning("error_handler", f"Slash check failed for {interaction.user} in {interaction.command}")
            return

        if isinstance(error, TransformerError):
            await _reply(self.error_embed(
                msg(interaction, "invalid_argument_title"),
                msg(interaction, "transformer_body", value=error.value),
            ))
            logging.warning("error_handler", f"TransformerError in slash {interaction.command}: {error}")
            return

        if isinstance(error, HTTPException):
            await _reply(self.error_embed(
                msg(interaction, "api_title"),
                msg(interaction, "api_short", status=error.status),
            ))
            logging.error("error_handler", f"HTTPException in slash {interaction.command}: {error}")
            return

        # ── Unexpected critical ────────────────────────────────────────────
        logging.error("error_handler", f"Unexpected error in slash {interaction.command} (report {report_code}): {error}")
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        await _reply(self.error_embed(msg(interaction, "unexpected_title"), msg(interaction, "unexpected_body")))

        cog_name = None
        command = interaction.command
        cog = getattr(command, "cog", None)
        if cog is None and command is not None:
            # Context menus have no .cog attribute; fall back to the bound
            # callback's class (cog methods carry a __self__).
            binding = getattr(getattr(command, "callback", None), "__self__", None)
            cog = binding if isinstance(binding, commands.Cog) else None
        if cog is not None:
            cog_name = cog.__class__.__name__.lower()
            import os as _os
            cog_files = [f[:-3] for f in _os.listdir("src/cogs") if f.endswith(".py")]
            if cog_name not in cog_files:
                cog_name = None
        asyncio.create_task(send_debug_report(self.bot, error, cog_name=cog_name))
        _ERROR_REPORT_CODE.set(None)

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        error = sys.exc_info()[1]
        if error is None:
            return
        report_code, _ = await save_error_report(
            error,
            f"Invocation context\n------------------\nSource: Gateway event\nEvent: {event}\nArguments: {args!r}\nKeyword arguments: {kwargs!r}\nBot user: {self.bot.user} (ID {getattr(self.bot.user, 'id', 'n/a')})\nPython: {platform.python_version()}",
            self.bot,
        )
        logging.error("error_handler", f"Unexpected error in event {event} (report {report_code}): {error}")
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        asyncio.create_task(send_debug_report(self.bot, error, cog_name=None))


async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))

    # Route every application-command error through the cog handler above.
    # Tree.error registers a CommandTree.on_error override — the only hook
    # discord.py actually calls for slash / context menu errors.
    handler_cog = bot.get_cog("ErrorHandler")
    if handler_cog is not None:

        @bot.tree.error
        async def _tree_on_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
            await handler_cog.on_app_command_error(interaction, error)
