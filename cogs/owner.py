import discord
from discord.ext import commands
import aiohttp
import os
import io
import textwrap
import traceback
import sys
import asyncio

# Optional: Add your owner IDs here if you want multiple owners
OWNER_IDS = {123456789012345678, 987654321098765432}  # replace with yours


def is_owner():
    """Custom owner check supporting multiple owners."""
    async def predicate(ctx):
        return ctx.author.id in OWNER_IDS or await ctx.bot.is_owner(ctx.author)
    return commands.check(predicate)


class OwnerCog(commands.Cog):
    """Owner-only management commands."""

    def __init__(self, bot):
        self.bot = bot

    # -------------------------------
    # Helper: Download image bytes
    # -------------------------------
    async def fetch_bytes(self, url: str):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return None
                    return await resp.read()
            except Exception:
                return None

    # -------------------------------
    # Owner help command
    # -------------------------------
    @commands.command(name="ownerhelp")
    @is_owner()
    async def owner_help(self, ctx):
        """Shows help for owner-only commands."""

        embed = discord.Embed(
            title="🛠️ Owner Command Panel",
            description="These commands are restricted to bot owners only.",
            color=discord.Color.red()
        )

        cog = self.bot.get_cog("OwnerCog")
        if not cog:
            return await ctx.send("❌ OwnerCog not loaded.")

        for cmd in cog.get_commands():
            embed.add_field(
                name=f"`{cmd.name}`",
                value=cmd.help or "No description provided.",
                inline=False
            )

        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    # -------------------------------
    # Set bot profile picture
    # -------------------------------
    @commands.command(name="setpfp")
    @is_owner()
    async def set_pfp(self, ctx, url: str):
        """Set the bot's profile picture."""
        await ctx.send("📥 Downloading image...")

        data = await self.fetch_bytes(url)
        if not data:
            return await ctx.send("❌ Failed to download image.")

        try:
            await self.bot.user.edit(avatar=data)
            await ctx.send("✅ Profile picture updated.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to update avatar:\n`{e}`")

    # -------------------------------
    # Set bot banner
    # -------------------------------
    @commands.command(name="setbanner")
    @is_owner()
    async def set_banner(self, ctx, url: str):
        """Set the bot's profile banner."""
        await ctx.send("📥 Downloading banner...")

        data = await self.fetch_bytes(url)
        if not data:
            return await ctx.send("❌ Failed to download banner.")

        try:
            await self.bot.user.edit(banner=data)
            await ctx.send("✅ Banner updated.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to update banner:\n`{e}`")

    # -------------------------------
    # Set bot username
    # -------------------------------
    @commands.command(name="setname")
    @is_owner()
    async def set_name(self, ctx, *, name: str):
        """Set the bot's username."""
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"✅ Username changed to **{name}**")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to update username:\n`{e}`")

    # -------------------------------
    # Set bot status text
    # -------------------------------
    @commands.command(name="setstatus")
    @is_owner()
    async def set_status(self, ctx, *, text: str):
        """Set the bot's status text."""
        await self.bot.change_presence(activity=discord.Game(name=text))
        await ctx.send(f"✅ Status updated to: **{text}**")

    # -------------------------------
    # Set bot activity type
    # -------------------------------
    @commands.command(name="setactivity")
    @is_owner()
    async def set_activity(self, ctx, activity_type: str, *, text: str):
        """
        Set the bot's activity.
        Types: playing, watching, listening, competing
        """
        activity_type = activity_type.lower()

        if activity_type == "playing":
            activity = discord.Game(name=text)
        elif activity_type == "watching":
            activity = discord.Activity(type=discord.ActivityType.watching, name=text)
        elif activity_type == "listening":
            activity = discord.Activity(type=discord.ActivityType.listening, name=text)
        elif activity_type == "competing":
            activity = discord.Activity(type=discord.ActivityType.competing, name=text)
        else:
            return await ctx.send("❌ Invalid activity type.")

        await self.bot.change_presence(activity=activity)
        await ctx.send(f"✅ Activity updated: **{activity_type.title()} {text}**")

    # -------------------------------
    # Reload a cog
    # -------------------------------
    @commands.command(name="reload")
    @is_owner()
    async def reload_cog(self, ctx, cog: str):
        """Reload a cog."""
        try:
            await self.bot.reload_extension(cog)
            await ctx.send(f"🔄 Reloaded `{cog}`")
        except Exception as e:
            await ctx.send(f"❌ Failed to reload `{cog}`:\n`{e}`")

    # -------------------------------
    # Load a cog
    # -------------------------------
    @commands.command(name="load")
    @is_owner()
    async def load_cog(self, ctx, cog: str):
        """Load a cog."""
        try:
            await self.bot.load_extension(cog)
            await ctx.send(f"📥 Loaded `{cog}`")
        except Exception as e:
            await ctx.send(f"❌ Failed to load `{cog}`:\n`{e}`")

    # -------------------------------
    # Unload a cog
    # -------------------------------
    @commands.command(name="unload")
    @is_owner()
    async def unload_cog(self, ctx, cog: str):
        """Unload a cog."""
        try:
            await self.bot.unload_extension(cog)
            await ctx.send(f"📤 Unloaded `{cog}`")
        except Exception as e:
            await ctx.send(f"❌ Failed to unload `{cog}`:\n`{e}`")

    # -------------------------------
    # Restart bot
    # -------------------------------
    @commands.command(name="restart")
    @is_owner()
    async def restart_bot(self, ctx):
        """Restart the bot."""
        await ctx.send("🔄 Restarting bot...")
        await self.bot.close()

    # -------------------------------
    # Shutdown bot
    # -------------------------------
    @commands.command(name="shutdown")
    @is_owner()
    async def shutdown_bot(self, ctx):
        """Shut down the bot."""
        await ctx.send("🛑 Shutting down...")
        await self.bot.close()

    # -------------------------------
    # Sync slash commands
    # -------------------------------
    @commands.command(name="sync")
    @is_owner()
    async def sync_commands(self, ctx):
        """Sync slash commands globally."""
        synced = await self.bot.tree.sync()
        await ctx.send(f"✅ Synced `{len(synced)}` commands globally.")

    # -------------------------------
    # Eval command
    # -------------------------------
    @commands.command(name="eval")
    @is_owner()
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
            await ctx.send(f"❌ Error:\n```\n{e}\n```")


async def setup(bot):
    await bot.add_cog(OwnerCog(bot))