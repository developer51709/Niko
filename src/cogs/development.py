import discord
import asyncio
import traceback
import textwrap
import time
import os
import psutil
from discord.ext import commands
import colorama

# Developer user IDs
DEVELOPERS = {
    1435974392810307604,  # Nyxen
}


class Development(commands.Cog):
    """Developer-only debugging and control commands."""

    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    # -------------------------------
    # Error handling
    # -------------------------------
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            # Log the unauthorized access attempt
            print(colorama.Fore.RED + """╔══════════════════════════════════╗
║ ALERT:                           ║
║  Unauthorized dev access attempt ║
╚══════════════════════════════════╝""" + colorama.Style.RESET_ALL)
            print(colorama.Fore.RED + f"Username: {ctx.author.name}#{ctx.author.discriminator}" + colorama.Style.RESET_ALL)
            print(colorama.Fore.RED + f"User ID: {ctx.author.id}" + colorama.Style.RESET_ALL)
            if ctx.guild:
                print(colorama.Fore.RED + f"Guild Name: {ctx.guild.name}" + colorama.Style.RESET_ALL)
                print(colorama.Fore.RED + f"Guild ID: {ctx.guild.id}" + colorama.Style.RESET_ALL)
                print(colorama.Fore.RED + f"Channel Name: {ctx.channel.name}" + colorama.Style.RESET_ALL)
                print(colorama.Fore.RED + f"Channel ID: {ctx.channel.id}" + colorama.Style.RESET_ALL)
            else:
                print(colorama.Fore.RED + "Used in DMs" + colorama.Style.RESET_ALL)
            print(colorama.Fore.RED + f"Command: {ctx.command}" + colorama.Style.RESET_ALL)
            # command args
            if ctx.args:
                print(colorama.Fore.RED + f"Args: {ctx.args}" + colorama.Style.RESET_ALL)
            else:
                print(colorama.Fore.RED + "No args" + colorama.Style.RESET_ALL)
            embed = discord.Embed(
                title="⚠️ Unauthorized Access",
                description="This command is restricted to developers only.\n**__Notice:__**\nYour attempt has been logged.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    # -------------------------------
    # Developer-only check
    # -------------------------------
    async def cog_check(self, ctx: commands.Context):
        return ctx.author.id in DEVELOPERS

    # -------------------------------
    # Developer Help
    # -------------------------------
    @commands.command(name="devhelp")
    async def dev_help(self, ctx):
        embed = discord.Embed(
            title="Developer Toolkit",
            description="Easy-to-use debugging and control commands.",
            color=0x3498DB
        )

        embed.add_field(
            name="Cog Management",
            value="`!devload <cog>`\n`!devunload <cog>`\n`!devreload <cog>`",
            inline=False
        )
        embed.add_field(
            name="Diagnostics",
            value="`!devping`\n`!devlatency`\n`!devuptime`\n`!devmem`\n`!devtasks`",
            inline=False
        )
        embed.add_field(
            name="Guild Tools",
            value="`!devguild`\n`!devchannels`\n`!devroles`\n`!devmembers`",
            inline=False
        )
        embed.add_field(
            name="Eval / Exec",
            value="`!deveval <code>`\n`!devexec <code>`",
            inline=False
        )
        embed.add_field(
            name="Bot Control",
            value="`!devsay <msg>`\n`!devshutdown`",
            inline=False
        )

        await ctx.send(embed=embed)

    # -------------------------------
    # Cog Management
    # -------------------------------
    @commands.command(name="devload")
    async def dev_load(self, ctx, cog: str):
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"Loaded `{cog}`.")
        except Exception as e:
            await ctx.send(f"Error loading `{cog}`:\n```{e}```")

    @commands.command(name="devunload")
    async def dev_unload(self, ctx, cog: str):
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await ctx.send(f"Unloaded `{cog}`.")
        except Exception as e:
            await ctx.send(f"Error unloading `{cog}`:\n```{e}```")

    @commands.command(name="devreload")
    async def dev_reload(self, ctx, cog: str):
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await ctx.send(f"Reloaded `{cog}`.")
        except Exception as e:
            await ctx.send(f"Error reloading `{cog}`:\n```{e}```")

    # -------------------------------
    # Diagnostics
    # -------------------------------
    @commands.command(name="devping")
    async def dev_ping(self, ctx):
        before = time.monotonic()
        msg = await ctx.send("Pinging…")
        ping = (time.monotonic() - before) * 1000
        await msg.edit(content=f"Pong! `{ping:.2f}ms`")

    @commands.command(name="devlatency")
    async def dev_latency(self, ctx):
        await ctx.send(f"Websocket latency: `{self.bot.latency * 1000:.2f}ms`")

    @commands.command(name="devuptime")
    async def dev_uptime(self, ctx):
        delta = time.time() - self.start_time
        hours, remainder = divmod(delta, 3600)
        minutes, seconds = divmod(remainder, 60)
        await ctx.send(f"Uptime: `{int(hours)}h {int(minutes)}m {int(seconds)}s`")

    @commands.command(name="devmem")
    async def dev_memory(self, ctx):
        process = psutil.Process(os.getpid())
        mem = process.memory_info().rss / 1024 / 1024
        await ctx.send(f"Memory usage: `{mem:.2f} MB`")

    @commands.command(name="devtasks")
    async def dev_tasks(self, ctx):
        tasks = asyncio.all_tasks()
        await ctx.send(f"Active asyncio tasks: `{len(tasks)}`")

    # -------------------------------
    # Guild Inspection
    # -------------------------------
    @commands.command(name="devguild")
    async def dev_guild(self, ctx):
        g = ctx.guild
        embed = discord.Embed(
            title=f"Guild Info: {g.name}",
            color=0x95A5A6
        )
        embed.add_field(name="ID", value=g.id)
        embed.add_field(name="Members", value=g.member_count)
        embed.add_field(name="Owner", value=g.owner)
        embed.add_field(name="Channels", value=len(g.channels))
        embed.add_field(name="Roles", value=len(g.roles))
        await ctx.send(embed=embed)

    @commands.command(name="devchannels")
    async def dev_channels(self, ctx):
        channels = "\n".join([f"{c.id} — {c.name}" for c in ctx.guild.channels])
        await ctx.send(f"**Channels:**\n```\n{channels}\n```")

    @commands.command(name="devroles")
    async def dev_roles(self, ctx):
        roles = "\n".join([f"{r.id} — {r.name}" for r in ctx.guild.roles])
        await ctx.send(f"**Roles:**\n```\n{roles}\n```")

    @commands.command(name="devmembers")
    async def dev_members(self, ctx):
        members = "\n".join([f"{m.id} — {m}" for m in ctx.guild.members][:50])
        await ctx.send(f"**Members (first 50):**\n```\n{members}\n```")

    # -------------------------------
    # Eval / Exec
    # -------------------------------
    @commands.command(name="deveval")
    async def dev_eval(self, ctx, *, code: str):
        """Evaluate Python code."""
        code = code.strip("` ")

        try:
            result = eval(code)
            if asyncio.iscoroutine(result):
                result = await result
            await ctx.send(f"```\n{result}\n```")
        except Exception as e:
            await ctx.send(f"Error:\n```{e}```")

    @commands.command(name="devexec")
    async def dev_exec(self, ctx, *, code: str):
        """Execute Python code."""
        code = textwrap.dedent(code.strip("` "))

        env = {
            "bot": self.bot,
            "ctx": ctx,
            "discord": discord,
            "asyncio": asyncio,
            "__import__": __import__,
        }

        try:
            exec(code, env)
            await ctx.send("Executed successfully.")
        except Exception:
            await ctx.send(f"Error:\n```{traceback.format_exc()}```")

    # -------------------------------
    # Bot Control
    # -------------------------------
    @commands.command(name="devsay")
    async def dev_say(self, ctx, *, message: str):
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command(name="devshutdown")
    async def dev_shutdown(self, ctx):
        await ctx.send("Shutting down…")
        await self.bot.close()


async def setup(bot):
    await bot.add_cog(Development(bot))