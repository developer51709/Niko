"""``.staff setpfp`` and friends: the bot's own profile and presence."""

import io

import aiohttp
import discord
from discord.ext import commands

from config.emojis import get_emoji
from cogs.staff.base import CMDS, StaffCommands
from utils.image.extractor import extract_image_from_message


class ProfileCommands:
    """Avatar, banner, username, status and activity."""

    async def fetch_bytes(self, url: str):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return None
                    return await resp.read()
            except Exception:
                return None

    @StaffCommands.staff.command(name="setpfp", help=CMDS.help("setpfp"), hidden=True)
    async def set_pfp(self, ctx, url: str | None):
        downloading_view = discord.ui.LayoutView()
        downloading_container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('image')} Set PFP"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"{get_emoji('loading')} Downloading pfp..."
            )
        )
        downloading_view.add_item(downloading_container)
        message = await ctx.send(view=downloading_view)

        data = await extract_image_from_message(ctx.message)
        if not data:
            failed_view = discord.ui.LayoutView()
            failed_container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('image')} Set PFP"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} Failed to download image."
                )
            )
            failed_view.add_item(failed_container)
            return await message.edit(view=failed_view)

        if isinstance(data, bytes):
            data = io.BytesIO(data)
        else:
            data.seek(0)
        data = data.read()

        try:
            await self.bot.user.edit(avatar=data)
            success_view = discord.ui.LayoutView()
            success_container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('image')} Set PFP"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"{get_emoji('tick')} Successfully updated pfp."
                )
            )
            success_view.add_item(success_container)
            await message.edit(view=success_view)
        except discord.HTTPException as e:
            await ctx.send(f"{get_emoji('cross')} Failed to update avatar:\n`{e}`")

    @StaffCommands.staff.command(name="setbanner", help=CMDS.help("setbanner"), hidden=True)
    async def set_banner(self, ctx, url: str | None):
        downloading_view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('image')} Set Banner"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"{get_emoji('loading')} Downloading banner..."
            )
        )
        downloading_view.add_item(container)
        message = await ctx.send(view=downloading_view)

        data = await extract_image_from_message(ctx.message)
        if not data:
            failed_view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('image')} Set Banner"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} Failed to download image."
                )
            )
            failed_view.add_item(container)
            return await message.edit(view=failed_view)

        if isinstance(data, bytes):
            data = io.BytesIO(data)
        else:
            data.seek(0)
        data = data.read()

        try:
            await self.bot.user.edit(banner=data)
            success_view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('image')} Set Banner"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"{get_emoji('tick')} Successfully updated banner."
                )
            )
            success_view.add_item(container)
            # edit the original response
            await message.edit(view=success_view)
        except discord.HTTPException as e:
            await ctx.send(f"{get_emoji('cross')} Failed to update banner:\n`{e}`")

    @StaffCommands.staff.command(name="setusername", help=CMDS.help("setusername"), hidden=True)
    async def set_name(self, ctx, *, name: str):
        """Set the bot's username."""
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"{get_emoji('tick')} Username changed to **{name}**")
        except discord.HTTPException as e:
            await ctx.send(f"{get_emoji('cross')} Failed to update username:\n`{e}`")

    @StaffCommands.staff.command(name="setstatus", help=CMDS.help("setstatus"), hidden=True)
    async def set_status(self, ctx, *, text: str):
        """Set the bot's status text."""
        await self.bot.change_presence(activity=discord.Game(name=text))
        await ctx.send(f"{get_emoji('tick')} Status updated to: **{text}**")

    @StaffCommands.staff.command(name="setactivity", help=CMDS.help("setactivity"), hidden=True)
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
            return await ctx.send(f"{get_emoji('cross')} Invalid activity type.")

        await self.bot.change_presence(activity=activity)
        await ctx.send(f"{get_emoji('tick')} Activity updated: **{activity_type.title()} {text}**")
