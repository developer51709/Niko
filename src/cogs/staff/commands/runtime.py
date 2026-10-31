"""``.staff load`` and friends: extension reloads, restarts, sync and code eval."""

import asyncio
import io
import os
import sys
import textwrap
import traceback

import discord
from discord.ext import commands

from config.emojis import get_emoji
from cogs.staff.base import CMDS, StaffCommands
from utils.command_localization import apply_command_localizations


class RuntimeCommands:
    """Extension, process, slash-command and code control for the owner."""

    @StaffCommands.staff.command(name="load", help=CMDS.help("load"), hidden=True)
    async def load_cog(self, ctx: commands.Context, cog: str):
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"Loaded `{cog}`.")
        except Exception as exc:
            await ctx.send(f"{get_emoji('danger')} Could not load `{cog}`: `{exc}`")

    @StaffCommands.staff.command(name="unload", help=CMDS.help("unload"), hidden=True)
    async def unload_cog(self, ctx: commands.Context, cog: str):
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await ctx.send(f"Unloaded `{cog}`.")
        except Exception as exc:
            await ctx.send(f"{get_emoji('danger')} Could not unload `{cog}`: `{exc}`")

    @StaffCommands.staff.command(name="reload", help=CMDS.help("reload"), hidden=True)
    async def reload_cog(self, ctx: commands.Context, cog: str):
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await ctx.send(f"Reloaded `{cog}`.")
        except Exception as exc:
            await ctx.send(f"{get_emoji('danger')} Could not reload `{cog}`: `{exc}`")

    @StaffCommands.staff.command(name="restart", help=CMDS.help("restart"), hidden=True)
    async def restart_bot(self, ctx):
        """Restart the bot."""
        await ctx.send("🔄 Restarting bot...")
        await self.bot.close()

    @StaffCommands.staff.command(name="shutdown", help=CMDS.help("shutdown"), hidden=True)
    async def shutdown_bot(self, ctx):
        """Shut down the bot."""
        await ctx.send("🛑 Shutting down...")
        await self.bot.close()

    @StaffCommands.staff.command(name="sync", help=CMDS.help("sync"), hidden=True)
    async def sync_commands(self, ctx, scope: str = "global"):
        """Sync application commands."""
        try:
            # Commands loaded or reloaded since boot still need their catalogue
            # translations attached before Discord receives the payload.
            apply_command_localizations(self.bot.tree)
            if scope.lower() in ["guild", "local", "here"]:
                synced = await self.bot.tree.sync(guild=ctx.guild)
                scope_text = f"Synced `{len(synced)}` commands to **this guild only**."
            else:
                synced = await self.bot.tree.sync()
                scope_text = f"Synced `{len(synced)}` commands **globally**."

            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('tick')} Sync Complete"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=scope_text
                ),
                discord.ui.TextDisplay(
                    content=f"-# Includes slash commands & context menu commands."
                )
            )
            view.add_item(container)
            await ctx.send(view=view)

        except Exception as e:
            view = discord.ui.LayoutView()
            view.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"### {get_emoji('cross')} Sync Error\n```\n{e}\n```"
                    )
                )
            )
            await ctx.send(view=view)

    @StaffCommands.staff.command(name="eval", help=CMDS.help("eval"), hidden=True)
    async def eval_code(self, ctx, *, code: str):
        """Evaluate Python code (owner only)."""

        class SafeEnviron(dict):
            BLOCKED = {"DISCORD_BOT_TOKEN"}

            def __getitem__(self, key):
                if key in self.BLOCKED:
                    raise PermissionError(f"Access to environment variable '{key}' is blocked.")
                return os.environ.get(key)

            def get(self, key, default=None):
                if key in self.BLOCKED:
                    raise PermissionError(f"Access to environment variable '{key}' is blocked.")
                return os.environ.get(key, default)

        safe_env = SafeEnviron()

        env = {
            "bot": self.bot,
            "ctx": ctx,
            "discord": discord,
            "commands": commands,
            "asyncio": asyncio,
            "os": os,
            "sys": sys,
            "io": io,
            "env": safe_env,
        }

        # Inject all environment variables except the blocked ones
        for k, v in os.environ.items():
            if k != "DISCORD_BOT_TOKEN":
                env[k] = v

        code = code.strip("` ")

        try:
            result = eval(code, env)
            if asyncio.iscoroutine(result):
                result = await result

            await ctx.send(f"🧪 **Eval Result:**\n```\n{result}\n```")
        except Exception as e:
            await ctx.send(f"{get_emoji('cross')} Error:\n```\n{e}\n```")

    @StaffCommands.staff.command(name="exec", help=CMDS.help("devexec"), hidden=True)
    async def exec_code(self, ctx, *, code: str):
        """Execute Python code."""
        code = textwrap.dedent(code.strip("` "))

        env = {
            "bot": self.bot,
            "ctx": ctx,
            "discord": discord,
            "asyncio": asyncio,
            "__import__": __import__,
            "self": self,
        }

        try:
            exec(code, env)
            await ctx.send("Executed successfully.")
        except Exception:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"## {get_emoji('danger')} Execution Error\nAn error occurred while executing the code."
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"### Traceback\n```\n{traceback.format_exc()}\n```"
                )
            )
            view.add_item(container)
            await ctx.send(view=view)

    @StaffCommands.staff.command(name="say", help=CMDS.help("devsay"), hidden=True)
    async def say(self, ctx, *, message: str):
        await ctx.message.delete()
        await ctx.send(message)
