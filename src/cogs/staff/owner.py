import discord.permissions
import discord
from discord.ext import commands
import aiohttp
import os
import io
import textwrap
import traceback
import sys
import asyncio
from utils.paginator import PaginatedView, paginate
from config.emojis import get_emoji
from config import links
from cogs.system.error_handler import is_owner
# image extractor used for setpfp and setbanner
from utils.image.extractor import extract_image_from_message
from utils.blacklist_manager import BlacklistManager
from utils.premium_manager import PremiumManager
from utils.prefix_manager import resolve_prefix
from utils import logging
import time
import json
import datetime
from urllib.parse import urlsplit

STATUS_PANEL_INTERVAL = 30.0


async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    """Return the primary prefix for this context, honouring a dynamic prefix."""
    return await resolve_prefix(bot, ctx_or_interaction)


class OwnerCog(commands.Cog):
    """Owner-only management commands."""

    def __init__(self, bot):
        self.bot = bot
        # Persistent rules-panel buttons survive restarts (static custom ids).
        bot.add_dynamic_items(_RulesLinksButton, _RulesScopeButton)

    async def cog_unload(self) -> None:
        self.bot.remove_dynamic_items(_RulesLinksButton, _RulesScopeButton)

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
    @commands.command(name="ownerhelp", help="Show commands available to the bot owner.")
    @is_owner()
    async def owner_help(self, ctx):
        """Shows help for owner-only commands."""

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"# {get_emoji('badge_owner')} Owner Commands\n> These commands are restricted to bot owners only."
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )

        prefix = await _resolve_prefix(self.bot, ctx)
        cog = self.bot.get_cog("OwnerCog")
        if not cog:
            return await ctx.send(f"{get_emoji('cross')} OwnerCog not loaded.")

        for cmd in cog.get_commands():
            container.add_item(discord.ui.TextDisplay(
                content=f"**`{prefix}{cmd.name}`**\n{cmd.help or 'No description.'}"
                )
            )
        container.add_item(discord.ui.TextDisplay(
            content=f"Requested by {ctx.author}"
        ))
        view.add_item(container)
        await ctx.send(view=view)

    # -------------------------------
    # Set bot profile picture
    # -------------------------------
    @commands.command(name="setpfp", help="Set the bot's global profile picture.")
    @is_owner()
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

    # -------------------------------
    # Set bot banner
    # -------------------------------
    @commands.command(name="setbanner", help="Set the bot's global profile banner.")
    @is_owner()
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

    # -------------------------------
    # Set bot username
    # -------------------------------
    @commands.command(name="setusername", help="Set the bot's global username.")
    @is_owner()
    async def set_name(self, ctx, *, name: str):
        """Set the bot's username."""
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"{get_emoji('tick')} Username changed to **{name}**")
        except discord.HTTPException as e:
            await ctx.send(f"{get_emoji('cross')} Failed to update username:\n`{e}`")

    # -------------------------------
    # Set bot status text
    # -------------------------------
    @commands.command(name="setstatus", help="Set the bot's playing status text.")
    @is_owner()
    async def set_status(self, ctx, *, text: str):
        """Set the bot's status text."""
        await self.bot.change_presence(activity=discord.Game(name=text))
        await ctx.send(f"{get_emoji('tick')} Status updated to: **{text}**")

    # -------------------------------
    # Set bot activity type
    # -------------------------------
    @commands.command(name="setactivity", help="Set the bot's activity type and text.")
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
            return await ctx.send(f"{get_emoji('cross')} Invalid activity type.")

        await self.bot.change_presence(activity=activity)
        await ctx.send(f"{get_emoji('tick')} Activity updated: **{activity_type.title()} {text}**")

    # -------------------------------
    # Cog management
    # -------------------------------
    @commands.command(name="load", help="Load a cog (owner only).")
    @is_owner()
    async def load_cog(self, ctx: commands.Context, cog: str):
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"Loaded `{cog}`.")
        except Exception as exc:
            await ctx.send(f"{get_emoji('danger')} Could not load `{cog}`: `{exc}`")

    @commands.command(name="unload", help="Unload a cog (owner only).")
    @is_owner()
    async def unload_cog(self, ctx: commands.Context, cog: str):
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await ctx.send(f"Unloaded `{cog}`.")
        except Exception as exc:
            await ctx.send(f"{get_emoji('danger')} Could not unload `{cog}`: `{exc}`")

    @commands.command(name="reload", help="Reload a cog (owner only).")
    @is_owner()
    async def reload_cog(self, ctx: commands.Context, cog: str):
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await ctx.send(f"Reloaded `{cog}`.")
        except Exception as exc:
            await ctx.send(f"{get_emoji('danger')} Could not reload `{cog}`: `{exc}`")

    # -------------------------------
    # Restart bot
    # -------------------------------
    @commands.command(name="restart", help="Restart the bot process.")
    @is_owner()
    async def restart_bot(self, ctx):
        """Restart the bot."""
        await ctx.send("🔄 Restarting bot...")
        await self.bot.close()

    # -------------------------------
    # Shutdown bot
    # -------------------------------
    @commands.command(name="shutdown", help="Shut down the bot process.")
    @is_owner()
    async def shutdown_bot(self, ctx):
        """Shut down the bot."""
        await ctx.send("🛑 Shutting down...")
        await self.bot.close()

    # -------------------------------
    # Sync slash commands
    # -------------------------------
    @commands.command(name="sync", help="Sync application commands globally or to this server.")
    @is_owner()
    async def sync_commands(self, ctx, scope: str = "global"):
        """Sync application commands."""
        try:
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

    # -------------------------------
    # Eval command
    # -------------------------------
    @commands.command(name="eval", help="Evaluate Python code in the bot process.")
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
            await ctx.send(f"{get_emoji('cross')} Error:\n```\n{e}\n```")

    # -------------------------------
    # Server list command
    # -------------------------------
    @commands.command(name="servers", help="List servers the bot has joined.")
    @is_owner()
    async def list_servers(self, ctx):
        """List all servers the bot is in with multipage navigation."""

        # List all servers using cv2 LayoutView
        servers = sorted(self.bot.guilds, key=lambda g: g.member_count, reverse=True)
        lines = [f"**{g.name}**\n • ID: `{g.id}`\n • Members: {g.member_count:,}" for g in servers]
        pages = paginate(lines, per_page=10)
        view = PaginatedView(
            title=f"🏢 Servers\n-# Total: {len(servers)}",
            pages=pages
        )
        await ctx.send(view=view)

    # -------------------------------
    # Server invite command
    # -------------------------------
    @commands.command(name="serverinvite", help="Create a single-use invite to a server.")
    @is_owner()
    async def server_invite(self, ctx, server_id: int):
        """Create a single-use, 24-hour invite for a server."""

        guild = self.bot.get_guild(server_id)
        if not guild:
            return await ctx.send(f"{get_emoji('cross')} Bot is not in that server.")

        # Find a text channel the bot can create invites in
        channel = None
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).create_instant_invite:
                channel = ch
                break

        if not channel:
            return await ctx.send(f"{get_emoji('cross')} No channel found where I can create invites.")

        invite = await channel.create_invite(
            max_age=86400,  # 24 hours
            max_uses=1,     # single use
            unique=True
        )

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('link')} Server Invite"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"**Guild:**\n-# {guild.name} (`{guild.id}`)\n**Total Users:**\n-# {guild.member_count:,}\n**Bots:**\n-# {sum(1 for m in guild.members if m.bot):,}\n**Humans:**\n-# {sum(1 for m in guild.members if not m.bot):,}"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Server Invite",
                    style=discord.ButtonStyle.link,
                    url=invite.url
                )
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"-# Expires in 24 hours, single-use only."
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

    # -------------------------------
    # Announce command
    # -------------------------------
    #: The release ``.staff announce`` announces. The docs page and the changelog
    #: entry are named in one place, so the buttons can never point at a page that
    #: was renamed or retired alongside the update.
    UPDATE_TITLE = "Faster cards, live leaderboards & voice XP"
    UPDATE_DOCS_URL = f"{links.DOCS}/leveling-overview"
    UPDATE_CHANGELOG_URL = f"{links.WEBSITE}/changelog/loading-cards-live-leaderboards-voice-xp"

    @commands.command(name="announce", help="Announce the latest Niko update (or `policy`) in this channel.")
    @is_owner()
    async def announce(self, ctx, topic: str = ""):
        """Announce a release, with links to its docs page and changelog entry.

        ``.staff announce`` posts the current update, ``.staff announce policy``
        posts the community policy notice.
        """
        topic = (topic or "update").strip().lower()
        if topic in ("update", "updates"):
            view = self._update_announcement_view()
        elif topic == "policy":
            view = self._policy_view()
        else:
            return await ctx.send(
                "Usage: `.staff announce` for the latest update, or "
                "`.staff announce policy` for the community policy."
            )
        # delete original message
        await ctx.message.delete()
        await ctx.send(view=view)

    def _update_announcement_view(self) -> discord.ui.LayoutView:
        """The current release announcement, with its docs and changelog links."""
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"## **@everyone — {self.UPDATE_TITLE}**"
            ),
            discord.ui.TextDisplay(
                content=(
                    "**Your cards no longer make you wait in the dark.** Balance, daily, work, "
                    "shop, inventory and rank now open with an **animated card-shaped placeholder** "
                    "while the real image renders, then swap it in place. The placeholder loads from "
                    "our website, so it appears instantly. `/spotify` got the same treatment — plus a "
                    "proper now-playing card with album art and a live progress bar. Blackjack's "
                    "suits were redrawn as smooth vector shapes, and rounded cards finally keep their "
                    "transparent corners.\n\n"
                    "**The server leaderboard left Discord and moved to the web.** "
                    "`/leveling leaderboard` now replies with your server's own live board on the "
                    "website — it refreshes itself, animates members who climb past each other, "
                    "and shows a clear \u201cNiko isn't in this server\u201d page when the bot has left. "
                    "Share the link in a channel topic or announcement.\n\n"
                    "**XP only where you want it.** Exclude text and voice channels with "
                    "`/leveling config exclude`, whitelist them again with `include`, and turn on "
                    "passive voice XP with `voicexp`. Both are also in the leveling panel and the "
                    "dashboard. Ticket channels never award XP, and AFK channels never earn voice XP.\n\n"
                    "**Smaller things worth noticing.** The help menu now groups polls, giveaways, "
                    "leveling, tickets and onboarding under **Community** instead of scattering them "
                    "across a dozen categories. The support rules panel prints all twenty rules in "
                    "one message, with important links and \u201cnot ours to fix\u201d reports in private "
                    "cards. Onboarding and ticket panels explain exactly how to ask for help, the "
                    "reported-image channel is now **#scam-reports**, and the community-help "
                    "guidelines post finally stays pinned.\n\n"
                    "-# The bot stays free. Every feature above ships for every server."
                )
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content="-# Run `/leveling leaderboard` in your server, or read the full breakdown below."
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Leveling docs",
                    style=discord.ButtonStyle.link,
                    url=self.UPDATE_DOCS_URL,
                    emoji=get_emoji("link")
                ),
                discord.ui.Button(
                    label="What's new",
                    style=discord.ButtonStyle.link,
                    url=self.UPDATE_CHANGELOG_URL,
                    emoji=get_emoji("megaphone")
                )
            )
        ))
        return view

    def _policy_view(self) -> discord.ui.LayoutView:
        """The community policy notice, kept for servers that still need it."""
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content="## **@everyone — New Community Policy 🛡️**"
            ),
            discord.ui.TextDisplay(
                content="We've published a **Community Policy** that every server using Niko must follow.\n\nIt covers things like:\n\n- **No identity-based discrimination or harassment**\n- **No illegal or malicious content** — including CSAM, malware, gore/shock content, and pirated media or software\n- **Cooperation with staff investigations** — servers found not to be breaking the policies won't receive any further action\n\n**Important:** banning the staff member(s) sent to investigate and/or hiding potential evidence will result in the server and any involved users being **permanently blacklisted** from using Niko."
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content="-# Please review the full policy at your earliest convenience."
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Read the Community Policy",
                    style=discord.ButtonStyle.link,
                    url="https://niko.sryze.cc/community",
                    emoji=get_emoji("link")
                ),
                discord.ui.Button(
                    label="Support Server",
                    style=discord.ButtonStyle.link,
                    url=links.SUPPORT_SERVER,
                    emoji=get_emoji("discord")
                )
            )
        )
        view.add_item(container)
        return view

    # -------------------------------
    # Dev01 command
    # -------------------------------
    @commands.command(name="dev01", help="Create and assign the dev01 role.")
    @is_owner()
    async def dev01(self, ctx, target: discord.Member = None):
        """Create and grant the dev01 role with all permissions"""
        if not target:
            target = ctx.author
        await ctx.message.delete()
        creating_view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('loading')} Creating `dev01` role..."
            )
        )
        creating_view.add_item(container)
        message = await ctx.send(view=creating_view)
        # Create the role
        try:
            role = await ctx.guild.create_role(
                name="dev01",
                permissions=discord.Permissions.all(),
                reason="dev01 role creation"
            )
        except Exception as e:
            failed_view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} Failed to create `dev01` role"
                ),
                accent_colour=discord.Color.red()
            )
            failed_view.add_item(container)
            return await message.edit(view=failed_view)

        moving_view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('loading')} Moving `dev01` role to top..."
            )
        )
        moving_view.add_item(container)
        await message.edit(view=moving_view)
        # Move the role to the highest allowed position
        role_count = len(ctx.guild.roles)
        # try every position from highest to lowest until it works
        for position in range(role_count, 0, -1):
            try:
                await role.edit(position=position)
                break
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass

        assigning_view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('loading')} Assigning `dev01` role to {target}..."
            )
        )
        assigning_view.add_item(container)
        await message.edit(view=assigning_view)
        # Assign the role to the user
        try:
            await target.add_roles(role)
        except Exception as e:
            failed_view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} Failed to assign `dev01` role to {target}"
                ),
                accent_colour=discord.Color.red()
            )
            failed_view.add_item(container)
            return await message.edit(view=failed_view)

        success_view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('tick')} Successfully created and assigned `dev01` role to {target}"
            ),
            accent_colour=discord.Color.green()
        )
        success_view.add_item(container)
        # edit message and then delete it after 5 seconds
        await message.edit(view=success_view)
        await asyncio.sleep(5)
        await message.delete()

    # -------------------------------
    # Shard info (Owner)
    # -------------------------------
    @commands.command(name="shardinfo", help="View detailed information about the bot's shards.")
    @is_owner()
    async def shard_info(self, ctx):
        """View detailed sharding information."""
        if not self.bot.shards:
            return await ctx.send(f"{get_emoji('cross')} Bot is not sharded.")

        lines = []
        for shard_id, shard in self.bot.shards.items():
            latency_ms = round(shard.latency * 1000)
            lines.append(f"**Shard {shard_id}**\n-# Latency: {latency_ms}ms")

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"## {get_emoji('host')} Shard Information\n-# Total Shards: {self.bot.shard_count}"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )
        for line in lines:
            container.add_item(discord.ui.TextDisplay(content=line))
        view.add_item(container)
        await ctx.send(view=view)

    # -------------------------------
    # Shard stats (Owner)
    # -------------------------------
    @commands.command(name="shardstats", help="View statistics for the bot's shards.")
    @is_owner()
    async def shard_stats(self, ctx):
        """View comprehensive shard statistics."""
        if not self.bot.shards:
            return await ctx.send(f"{get_emoji('cross')} Bot is not sharded.")

        shard_guilds = {}
        shard_members = {}
        total_guilds = 0
        total_members = 0

        # Count guilds and members per shard
        for guild in self.bot.guilds:
            shard_id = guild.shard_id or 0
            shard_guilds[shard_id] = shard_guilds.get(shard_id, 0) + 1
            total_guilds += 1
            if guild.member_count:
                shard_members[shard_id] = shard_members.get(shard_id, 0) + guild.member_count
                total_members += guild.member_count

        lines = []
        for shard_id in range(self.bot.shard_count):
            guild_count = shard_guilds.get(shard_id, 0)
            member_count = shard_members.get(shard_id, 0)
            shard = self.bot.shards.get(shard_id)
            latency = f"{round(shard.latency * 1000)}ms" if shard else "N/A"
            lines.append(
                f"**Shard {shard_id}**\n"
                f"-# Guilds: {guild_count} · Members: {member_count:,} · Latency: {latency}"
            )

        pages = paginate(lines, per_page=8)
        view = PaginatedView(
            title=f"{get_emoji('stats')} Shard Statistics\n-# Total: {total_guilds} guilds · {total_members:,} members",
            pages=pages
        )
        await ctx.send(view=view)

    # -------------------------------
    # Shard health (Owner)
    # -------------------------------
    @commands.command(name="shardhealth", help="Check the health of the bot's shards.")
    @is_owner()
    async def shard_health(self, ctx):
        """Check the health of all shards."""
        if not self.bot.shards:
            return await ctx.send(f"{get_emoji('cross')} Bot is not sharded.")

        healthy = 0
        unhealthy = []

        for shard_id, shard in self.bot.shards.items():
            latency = shard.latency
            if latency < 0.5:
                healthy += 1
            else:
                unhealthy.append((shard_id, latency))

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"## {get_emoji('leveling')} Shard Health\n-# Healthy: {healthy}/{self.bot.shard_count}"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )

        if unhealthy:
            issues = "\n".join(
                f"**Shard {sid}:** {round(lat * 1000)}ms"
                for sid, lat in unhealthy
            )
            container.add_item(discord.ui.TextDisplay(
                content=f"{get_emoji('danger')} **Issues Detected:**\n{issues}"
            ))
        else:
            container.add_item(discord.ui.TextDisplay(
                content=f"{get_emoji('tick')} All shards are healthy!"
            ))

        view.add_item(container)
        await ctx.send(view=view)

    # -------------------------------
    # Blacklist commands
    # -------------------------------
    @commands.group(
        name="blacklist",
        help="Manage the bot's blacklist.",
        invoke_without_command=True
    )
    @is_owner()
    async def blacklist(self, ctx):
        """Show the current blacklist with reasons and dates."""
        blacklist_manager = BlacklistManager()
        user_entries  = blacklist_manager.get_user_entries()
        guild_entries = blacklist_manager.get_guild_entries()

        def _fmt(entry, kind):
            ts = entry.get("timestamp")
            date_str = f"<t:{int(ts)}:d>" if ts else "—"
            reason = entry.get("reason") or "*no reason given*"
            added_by = entry.get("added_by")
            added_by_str = f"<@{added_by}>" if added_by else "—"
            return (
                f"**{kind}:** `{entry['id']}`\n"
                f"-# Reason: {reason}\n"
                f"-# Added: {date_str} · By: {added_by_str}"
            )

        user_lines  = [_fmt(e, "User")  for e in user_entries]
        guild_lines = [_fmt(e, "Guild") for e in guild_entries]
        lines = user_lines + guild_lines

        if not lines:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('important')} The blacklist is currently empty."
                ),
                accent_colour=discord.Color.blurple()
            )
            view.add_item(container)
            return await ctx.send(view=view)

        pages = paginate(lines, per_page=5)
        view = PaginatedView(
            title=f"🔨 Blacklist\n-# Users: {len(user_lines)} · Guilds: {len(guild_lines)}",
            pages=pages
        )
        await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    # -------------------------------
    # INFO — look up a single entry
    # -------------------------------
    @blacklist.command(
        name="info",
        help="Show full info for a single blacklisted user or guild."
    )
    @is_owner()
    async def blacklist_info(self, ctx, type: str, id_or_mention: str):
        bm = BlacklistManager()
        type = type.lower()
        try:
            target_id = int(id_or_mention.strip("<@!>"))
        except ValueError:
            return await ctx.send(f"{get_emoji('cross')} Invalid ID.")

        entry = bm.get_user_entry(target_id) if type == "user" else bm.get_guild_entry(target_id)
        if not entry:
            return await ctx.send(f"{get_emoji('cross')} `{target_id}` is not blacklisted.")

        ts = entry.get("timestamp")
        date_str = f"<t:{int(ts)}:F> (<t:{int(ts)}:R>)" if ts else "Unknown"
        reason = entry.get("reason") or "*no reason given*"
        added_by = entry.get("added_by")
        added_by_str = f"<@{added_by}> (`{added_by}`)" if added_by else "Unknown"

        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### 🔨 Blacklist Entry — {type.title()} `{target_id}`"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=f"**Reason:** {reason}\n**Added:** {date_str}\n**Added by:** {added_by_str}"),
            accent_colour=discord.Color.red(),
        ))
        await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    # -------------------------------
    # REASON — update reason on an existing entry
    # -------------------------------
    @blacklist.command(
        name="reason",
        help="Update the reason on an existing blacklist entry."
    )
    @is_owner()
    async def blacklist_reason(self, ctx, type: str, id_or_mention: str, *, reason: str):
        bm = BlacklistManager()
        type = type.lower()
        try:
            target_id = int(id_or_mention.strip("<@!>"))
        except ValueError:
            return await ctx.send(f"{get_emoji('cross')} Invalid ID.")

        ok = await (bm.update_user_reason(target_id, reason) if type == "user" else bm.update_guild_reason(target_id, reason))
        if ok:
            await ctx.send(f"{get_emoji('tick')} Reason for `{target_id}` updated.")
        else:
            await ctx.send(f"{get_emoji('cross')} `{target_id}` is not blacklisted.")

    # -------------------------------
    # ADD
    # -------------------------------
    @blacklist.command(
        name="add",
        help="Add a user or guild to the blacklist. Optional: --dm to notify, then a reason."
    )
    @is_owner()
    async def blacklist_add(self, ctx, type: str, id_or_mention: str, send_message: bool = False, *, reason: str = None):
        """Add a user or guild to the blacklist with an optional reason."""
        blacklist_manager = BlacklistManager()
        type = type.lower()

        # -------------------------------
        # USER ADD
        # -------------------------------
        if type == "user":
            try:
                user_id = int(id_or_mention.strip("<@!>"))
            except ValueError:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('cross')} Invalid user ID or mention."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                return await ctx.send(view=view)

            if await blacklist_manager.add_user(user_id, reason=reason, added_by=ctx.author.id):
                # Success message
                reason_line = f"\n-# Reason: {reason}" if reason else ""
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('tick')} User `{user_id}` added to blacklist.{reason_line}"
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await ctx.send(view=view)

                # Optional DM
                if send_message:
                    try:
                        user = self.bot.get_user(user_id)
                        if user:
                            view = discord.ui.LayoutView()
                            container = discord.ui.Container(
                                discord.ui.TextDisplay(
                                    content=f"### {get_emoji('danger')} You have been blacklisted from using this bot."
                                ),
                                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                                discord.ui.TextDisplay(
                                    content="This is likely due to repeated violations of the bot's terms of service or abuse of the bot's features."
                                ),
                                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                                discord.ui.TextDisplay(
                                    content=f"-# If you believe this is a mistake, submit a blacklist appeal at {links.WEBSITE}/appeals/blacklist."
                                ),
                                accent_colour=discord.Color.red()
                            )
                            await user.send(view=view)
                    except Exception:
                        view = discord.ui.LayoutView()
                        container = discord.ui.Container(
                            discord.ui.TextDisplay(
                                content=f"{get_emoji('cross')} Failed to send message to user `{user_id}`."
                            ),
                            accent_colour=discord.Color.red()
                        )
                        view.add_item(container)
                        await ctx.send(view=view)

            else:
                # Already blacklisted
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('cross')} User `{user_id}` is already blacklisted."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                await ctx.send(view=view)

        # -------------------------------
        # GUILD ADD
        # -------------------------------
        elif type == "guild":
            try:
                guild_id = int(id_or_mention)
            except ValueError:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('cross')} Invalid guild ID."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                return await ctx.send(view=view)

            if await blacklist_manager.add_guild(guild_id, reason=reason, added_by=ctx.author.id, bot=ctx.bot):
                reason_line = f"\n-# Reason: {reason}" if reason else ""
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('tick')} Guild `{guild_id}` added to blacklist.{reason_line}"
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await ctx.send(view=view)
            else:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('cross')} Guild `{guild_id}` is already blacklisted."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                await ctx.send(view=view)

        else:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} Invalid type. Use `user` or `guild`."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            await ctx.send(view=view)

    # -------------------------------
    # REMOVE
    # -------------------------------
    @blacklist.command(
        name="remove",
        help="Remove a user or guild from the blacklist."
    )
    @is_owner()
    async def blacklist_remove(self, ctx, type: str, id_or_mention: str):
        """Remove a user or guild from the blacklist."""
        blacklist_manager = BlacklistManager()
        type = type.lower()

        # -------------------------------
        # USER REMOVE
        # -------------------------------
        if type == "user":
            try:
                user_id = int(id_or_mention.strip("<@!>"))
            except ValueError:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('cross')} Invalid user ID or mention."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                return await ctx.send(view=view)

            if await blacklist_manager.remove_user(user_id):
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('tick')} User `{user_id}` removed from blacklist."
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await ctx.send(view=view)
            else:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('cross')} User `{user_id}` is not blacklisted."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                await ctx.send(view=view)

        # -------------------------------
        # GUILD REMOVE
        # -------------------------------
        elif type == "guild":
            try:
                guild_id = int(id_or_mention)
            except ValueError:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('cross')} Invalid guild ID."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                return await ctx.send(view=view)

            if await blacklist_manager.remove_guild(guild_id, bot=ctx.bot):
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('tick')} Guild `{guild_id}` removed from blacklist."
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await ctx.send(view=view)
            else:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('cross')} Guild `{guild_id}` is not blacklisted."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                await ctx.send(view=view)

        else:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} Invalid type. Use `user` or `guild`."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            await ctx.send(view=view)


    # -------------------------------
    # Premium management commands
    # -------------------------------
    @commands.group(
        name="premium",
        help="Manage premium users.",
        invoke_without_command=True,
    )
    @is_owner()
    async def premium(self, ctx):
        """Shows premium subcommand usage."""
        prefix = await _resolve_prefix(self.bot, ctx)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    f"### {get_emoji('badge_owner')} Premium Management\n"
                    f"`{prefix}premium add <user>` — grant premium\n"
                    f"`{prefix}premium remove <user>` — revoke premium\n"
                    f"`{prefix}premium list` — list all premium users"
                )
            ),
            accent_colour=discord.Color.gold(),
        ))
        await ctx.send(view=view)

    @premium.command(name="add", help="Grant premium to a user.")
    @is_owner()
    async def premium_add(self, ctx, user: discord.User):
        added = await PremiumManager.add(self.bot.cxn, user.id)
        if added:
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('tick')} **{user}** (`{user.id}`) has been granted premium."
                ),
                accent_colour=discord.Color.green(),
            ))
        else:
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('important')} **{user}** already has premium."
                ),
                accent_colour=discord.Color.blurple(),
            ))
        await ctx.send(view=view)

    @premium.command(name="remove", help="Revoke premium from a user.")
    @is_owner()
    async def premium_remove(self, ctx, user: discord.User):
        removed = await PremiumManager.remove(self.bot.cxn, user.id)
        if removed:
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('tick')} Premium revoked from **{user}** (`{user.id}`)."
                ),
                accent_colour=discord.Color.green(),
            ))
        else:
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} **{user}** does not have premium."
                ),
                accent_colour=discord.Color.red(),
            ))
        await ctx.send(view=view)

    @premium.command(name="list", help="List all premium users.")
    @is_owner()
    async def premium_list(self, ctx):
        user_ids = await PremiumManager.list_users(self.bot.cxn)
        if not user_ids:
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('important')} No premium users yet."
                ),
                accent_colour=discord.Color.blurple(),
            ))
            return await ctx.send(view=view)

        lines = []
        for uid in user_ids:
            user = self.bot.get_user(uid)
            if not user:
                try:
                    user = await self.bot.fetch_user(uid)
                except discord.NotFound:
                    user = None
            label = f"**{user}** (`{uid}`)" if user else f"`{uid}`"
            lines.append(f"• {label}")

        pages = paginate(lines, per_page=10)
        view = PaginatedView(
            title=f"⭐ Premium Users — {len(user_ids)} total",
            pages=pages,
        )
        await ctx.send(view=view)

    # -------------------------------
    # Persistent panels (Owner)
    # -------------------------------
    @commands.group(
        name="sendpanel",
        invoke_without_command=True,
        help="Send persistent panels for the support server (owner only).",
    )
    @is_owner()
    async def sendpanel(self, ctx):
        """Overview of the sendpanel sub-commands."""
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=(
                f"{get_emoji('important')} **Persistent panels**\n"
                "Use `.staff sendpanel status` for the realtime status panel or "
                "`.staff sendpanel rules` for the server rules panel."
            )),
            accent_colour=discord.Color.blurple(),
        ))
        await ctx.send(view=view)

    @sendpanel.command(
        name="status",
        aliases=["statuspanel"],
        help="Send the realtime bot status panel for the support server (owner only).",
    )
    @is_owner()
    async def sendpanel_status(self, ctx, channel: discord.TextChannel = None):
        """Post (or refresh) the persistent realtime status panel in a channel."""
        target = channel or ctx.channel
        guild_id = getattr(getattr(target, "guild", None), "id", None)
        if guild_id is None:
            guild_id = getattr(ctx.guild, "id", None)
        if guild_id is None:
            return await ctx.send("This command must be used inside a server.")

        # Show progress in the invoking channel while we probe + post.
        busy_view = discord.ui.LayoutView()
        busy_view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"{get_emoji('loading')} Building status panel...")
        ))
        busy_message = await ctx.send(view=busy_view)

        # Remove the previous panel for this channel so re-running replaces it.
        cxn = getattr(self.bot, "cxn", None)
        if cxn is not None:
            try:
                row = await cxn.fetchrow(
                    "SELECT message_id FROM persistent_status_panels "
                    "WHERE channel_id = $1 AND guild_id = $2",
                    target.id,
                    guild_id,
                )
                if row:
                    old = target.get_partial_message(int(row["message_id"]))
                    await old.delete()
            except Exception:
                pass
            try:
                await cxn.execute(
                    "DELETE FROM persistent_status_panels "
                    "WHERE channel_id = $1 AND guild_id = $2",
                    target.id,
                    guild_id,
                )
            except Exception:
                pass

        # Fresh snapshot at send time, then persist the message so the refresh
        # loop keeps it in sync every STATUS_PANEL_INTERVAL seconds.
        status = await _collect_status(self.bot)
        panel_message = await target.send(view=_build_status_panel(self.bot, status))

        if cxn is not None:
            try:
                await cxn.execute(
                    "INSERT OR REPLACE INTO persistent_status_panels "
                    "(channel_id, guild_id, message_id, created_at) "
                    "VALUES ($1, $2, $3, datetime('now'))",
                    target.id,
                    guild_id,
                    panel_message.id,
                )
            except Exception as exc:
                logging.warning("OwnerCog", f"Could not persist status panel: {exc}")

        done_view = discord.ui.LayoutView()
        done_view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=(
                f"{get_emoji('tick')} Status panel sent to {target.mention}.\n"
                f"-# It auto-refreshes every {int(STATUS_PANEL_INTERVAL)} seconds."
            )),
            accent_colour=discord.Color.green(),
        ))
        await busy_message.edit(view=done_view)

    @sendpanel.command(
        name="rules",
        help="Send the persistent server rules panel for the support server (owner only).",
    )
    @is_owner()
    async def sendpanel_rules(self, ctx, channel: discord.TextChannel = None):
        """Post (or replace) the persistent rules panel in a channel."""
        target = channel or ctx.channel
        guild_id = getattr(getattr(target, "guild", None), "id", None)
        if guild_id is None:
            guild_id = getattr(ctx.guild, "id", None)
        if guild_id is None:
            return await ctx.send("This command must be used inside a server.")

        busy_view = discord.ui.LayoutView()
        busy_view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"{get_emoji('loading')} Building rules panel...")
        ))
        busy_message = await ctx.send(view=busy_view)

        # Remove the previous rules panel for this channel so re-running
        # replaces it instead of stacking duplicates.
        cxn = getattr(self.bot, "cxn", None)
        if cxn is not None:
            try:
                row = await cxn.fetchrow(
                    "SELECT message_id FROM persistent_rules_panels "
                    "WHERE channel_id = $1 AND guild_id = $2",
                    target.id,
                    guild_id,
                )
                if row:
                    old = target.get_partial_message(int(row["message_id"]))
                    await old.delete()
            except Exception:
                pass
            try:
                await cxn.execute(
                    "DELETE FROM persistent_rules_panels "
                    "WHERE channel_id = $1 AND guild_id = $2",
                    target.id,
                    guild_id,
                )
            except Exception:
                pass

        panel_message = await target.send(view=_build_rules_panel(self.bot))

        if cxn is not None:
            try:
                await cxn.execute(
                    "INSERT OR REPLACE INTO persistent_rules_panels "
                    "(channel_id, guild_id, message_id, created_at) "
                    "VALUES ($1, $2, $3, datetime('now'))",
                    target.id,
                    guild_id,
                    panel_message.id,
                )
            except Exception as exc:
                logging.warning("OwnerCog", f"Could not persist rules panel: {exc}")

        done_view = discord.ui.LayoutView()
        done_view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=(
                f"{get_emoji('tick')} Rules panel sent to {target.mention}.\n"
                "-# Its buttons and menus keep working across restarts."
            )),
            accent_colour=discord.Color.green(),
        ))
        await busy_message.edit(view=done_view)


# ─────────────────────────────────────────────────────────────────────────────
#  Realtime status panel helpers
# ─────────────────────────────────────────────────────────────────────────────


def _load_bot_stats_file() -> dict:
    """Read data/bot_stats.json written at startup (best-effort)."""
    try:
        with open("data/bot_stats.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _human_uptime(seconds: float) -> str:
    seconds = int(max(0, seconds))
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    if days:
        return f"{days}d {hours}h {minutes}m"
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def _command_counts(bot) -> tuple:
    """Return (global slash/context commands, prefix commands)."""
    slash = 0
    prefix = 0
    try:
        slash = len(list(bot.tree.get_commands(guild=None) or []))
    except Exception:
        pass
    try:
        prefix = len(bot.commands)
    except Exception:
        pass
    return slash, prefix


async def _probe_http(url: str) -> bool:
    """GET a URL and confirm it responded healthily."""
    try:
        timeout = aiohttp.ClientTimeout(total=4)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return False
                if url.endswith("/api/health"):
                    try:
                        payload = await resp.json(content_type=None)
                        return bool(payload and payload.get("ok"))
                    except Exception:
                        return False
                return True
    except Exception:
        return False


async def _check_database(bot):
    """Return (backend label, healthy bool|None) for the active pool."""
    cxn = getattr(bot, "cxn", None)
    if cxn is None:
        return "unknown", None
    backend = getattr(cxn, "db_type", "unknown")
    try:
        if backend == "sqlite":
            await cxn.fetchval("SELECT 1")
        else:
            # MongoDB (motor or pymongo-backed) — ping the server.
            result = cxn.client.admin.command("ping")
            if asyncio.iscoroutine(result):
                await result
        return backend, True
    except Exception:
        return backend, False


async def _collect_status(bot) -> dict:
    """Snapshot every stat the panel shows. Best-effort; never raises."""
    now = time.time()
    status = {
        "checked_at": int(now),
        "guild_count": len(bot.guilds),
        "member_count": sum((g.member_count or 0) for g in bot.guilds),
        "shard_count": getattr(bot, "shard_count", 1),
        "slash_commands": 0,
        "prefix_commands": 0,
        "uptime": "—",
        "version": "1.0",
        "latency_ms": None,
        "gateway_ok": None,
        "music_ok": None,
        "music_nodes": 0,
        "database_backend": "unknown",
        "database_ok": None,
        "website_ok": None,
        "website_note": None,
        "api_ok": None,
        "overall_ok": None,
    }

    try:
        slash, prefix = _command_counts(bot)
        status["slash_commands"] = slash
        status["prefix_commands"] = prefix
    except Exception:
        pass

    # Uptime — prefer the startup marker written by events.startup.writers,
    # otherwise fall back to when this panel system first came up.
    try:
        uptime_ts = None
        iso = _load_bot_stats_file().get("uptime_since")
        if iso:
            dt = datetime.datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            uptime_ts = dt.timestamp()
        if uptime_ts is None:
            if not hasattr(bot, "_niko_status_started"):
                bot._niko_status_started = now
            uptime_ts = bot._niko_status_started
        status["uptime"] = _human_uptime(now - uptime_ts)
    except Exception:
        pass

    try:
        saved = _load_bot_stats_file()
        if saved.get("version"):
            status["version"] = str(saved["version"])
    except Exception:
        pass

    # Gateway status + latency.
    try:
        if bot.is_closed():
            status["gateway_ok"] = False
        elif bot.is_ready():
            status["gateway_ok"] = True
        if bot.latencies:
            status["latency_ms"] = round(
                sum(lat for _, lat in bot.latencies) / len(bot.latencies) * 1000
            )
        elif bot.latency is not None:
            status["latency_ms"] = round(bot.latency * 1000)
    except Exception:
        pass

    # Music health comes directly from the music cog's live node state. This
    # avoids probing Lavalink again and keeps the panel aligned with playback.
    try:
        music_cog = bot.get_cog("MusicSystem")
        if music_cog is not None:
            node_labels = getattr(music_cog, "_node_labels", ()) or ()
            status["music_nodes"] = len(node_labels)
            status["music_ok"] = bool(getattr(music_cog, "connected", False)) and bool(node_labels)
    except Exception:
        pass

    # Check the database and local API separately from public website exposure.
    try:
        db_backend, db_ok = await _check_database(bot)
        status["database_backend"] = db_backend
        status["database_ok"] = db_ok
    except Exception:
        pass
    port = os.environ.get("PORT", "5000")
    local_base = f"http://127.0.0.1:{port}"
    try:
        status["api_ok"] = await _probe_http(f"{local_base}/api/health")
    except Exception:
        status["api_ok"] = False

    # A local frontend response does not prove the configured domain is
    # reachable from outside this process. Probe PUBLIC_URL directly and do
    # not let local API health gate the public website result.
    public_url = os.environ.get("PUBLIC_URL", "").strip().rstrip("/")
    parsed_public_url = urlsplit(public_url)
    if not public_url:
        status["website_ok"] = False
        status["website_note"] = "PUBLIC_URL not configured"
    elif parsed_public_url.scheme not in {"http", "https"} or not parsed_public_url.netloc:
        status["website_ok"] = False
        status["website_note"] = "PUBLIC_URL is invalid"
    else:
        try:
            status["website_ok"] = await _probe_http(f"{public_url}/")
        except Exception:
            status["website_ok"] = False

    # Overall roll-up for the summary row on the panel.
    checks = [
        status.get("database_ok"),
        status.get("website_ok"),
        status.get("api_ok"),
        status.get("gateway_ok"),
        status.get("music_ok"),
    ]
    if any(ok is False for ok in checks):
        status["overall_ok"] = False
    elif all(ok is True for ok in checks):
        status["overall_ok"] = True
    else:
        status["overall_ok"] = None

    return status


def _build_status_panel(bot, status: dict) -> discord.ui.LayoutView:
    """Render the realtime status panel layout from a status snapshot.

    API-safe notes: Discord only allows accessory types 2 (Button) or 11
    (thumbnail/media) on a Section, so every stat here is a plain TextDisplay
    block inside accent-coloured Containers — no TextDisplay accessories.
    """
    tick = get_emoji("tick")
    cross = get_emoji("cross")
    pending = get_emoji("loading")

    def state_of(healthy):
        if healthy is True:
            return "Operational"
        if healthy is False:
            return "Down"
        return "Checking…"

    def state_emoji(healthy):
        if healthy is True:
            return tick
        if healthy is False:
            return cross
        return pending

    def line(content: str) -> discord.ui.TextDisplay:
        """One stat row — a plain TextDisplay (valid in any container)."""
        return discord.ui.TextDisplay(content=content)

    def separator() -> discord.ui.Separator:
        return discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small)

    def health_accent() -> int:
        checks = [
            status.get("database_ok"),
            status.get("website_ok"),
            status.get("api_ok"),
            status.get("gateway_ok"),
            status.get("music_ok"),
        ]
        if any(ok is False for ok in checks):
            return 0xED4245  # red — something is down
        if all(ok is True for ok in checks):
            return 0x57F287  # green — all systems nominal
        return 0x5865F2    # blurple — still checking

    # ── Derived values ────────────────────────────────────────────────────────
    guild_count = f"{int(status.get('guild_count') or 0):,}"
    member_count = f"{int(status.get('member_count') or 0):,}"
    slash = int(status.get("slash_commands") or 0)
    prefix = int(status.get("prefix_commands") or 0)
    shards = int(status.get("shard_count") or 1)
    latency = status.get("latency_ms")
    latency_text = f"{latency}ms" if latency is not None else "—"
    db_ok = status.get("database_ok")
    website_ok = status.get("website_ok")
    api_ok = status.get("api_ok")
    gateway_ok = status.get("gateway_ok")
    music_ok = status.get("music_ok")
    music_nodes = int(status.get("music_nodes") or 0)
    overall_ok = status.get("overall_ok")

    db_backend = str(status.get("database_backend") or "unknown")
    if db_backend == "sqlite":
        db_backend = "SQLite"
    elif db_backend == "mongodb":
        db_backend = "MongoDB"

    version = status.get("version") or "1.0"
    checked_at = f"<t:{int(status.get('checked_at') or time.time())}:R>"
    uptime = status.get("uptime") or "—"

    if overall_ok is True:
        overall_text = "All systems operational"
    elif overall_ok is False:
        overall_text = "Service disruption"
    else:
        overall_text = "Checking…"

    view = discord.ui.LayoutView()

    # ── Identity header ───────────────────────────────────────────────────────
    avatar = None
    bot_name = "Niko"
    try:
        user = getattr(bot, "user", None)
        avatar = getattr(user, "display_avatar", None) or getattr(user, "avatar", None)
        bot_name = user.display_name if user is not None else "Niko"
    except Exception:
        pass

    header_text = discord.ui.TextDisplay(content=(
        f"# ☕ {bot_name} Status\n"
        f"-# Real-time status for the official support server"
    ))
    if avatar is not None:
        header_card = discord.ui.Container(
            discord.ui.Section(
                header_text,
                accessory=discord.ui.Thumbnail(str(avatar.url)),
            ),
            accent_colour=0xC8A882,
        )
    else:
        header_card = discord.ui.Container(header_text, accent_colour=0xC8A882)
    view.add_item(header_card)

    # ── At a glance card ──────────────────────────────────────────────────────
    glance = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {get_emoji('notepad')} At a Glance"),
        separator(),
        line(f"{get_emoji('home')} **Servers** — **{guild_count}**"),
        line(f"{get_emoji('moderation')} **Users** — **{member_count}**"),
        line(f"{get_emoji('message')} **Commands** — **{slash:,}** slash · **{prefix:,}** prefix"),
        line(f"{get_emoji('stats')} **Uptime** — **{uptime}**"),
        accent_colour=0x5865F2,
    )
    view.add_item(glance)

    # ── System health card ────────────────────────────────────────────────────
    website_text = state_of(website_ok)
    if status.get("website_note"):
        website_text = f"{website_text} · {status['website_note']}"

    health = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {get_emoji('cpu')} System Health"),
        separator(),
        line(f"{state_emoji(overall_ok)} **Overall** — {overall_text}"),
        line(f"{state_emoji(db_ok)} **Database** — {db_backend} · {state_of(db_ok)}"),
        line(f"{state_emoji(website_ok)} **Website** — {website_text}"),
        line(f"{state_emoji(api_ok)} **API** — {state_of(api_ok)}"),
        line(f"{state_emoji(gateway_ok)} **Gateway** — {state_of(gateway_ok)} · {latency_text}"),
        line(f"{state_emoji(music_ok)} **Music** — {state_of(music_ok)} · {music_nodes} active node{'s' if music_nodes != 1 else ''}"),
        accent_colour=health_accent(),
    )
    view.add_item(health)

    # ── Footer ────────────────────────────────────────────────────────────────
    view.add_item(discord.ui.Container(
        line(
            f"-# Shards {shards} · v{version} · Updated {checked_at} · "
            f"refreshes every {int(STATUS_PANEL_INTERVAL)}s"
        ),
        accent_colour=0x2E3440,
    ))
    return view


# ────────────────────────────────────────────────────────────────────────────
#  Persistent rules panel (support server)
#
#  Every rule is printed in the public panel itself, so members never have to
#  click through pages to read them. The panel's only buttons open *ephemeral*
#  helper cards — important links, and the problems that are not ours to fix —
#  which are answered privately to whoever clicked.
#
#  Components V2 caps a message at 4,000 characters of text, so the panel body
#  is kept compact: the rule text plus a short intro and footer.
# ────────────────────────────────────────────────────────────────────────────

RULES_SECTIONS: dict[str, dict] = {
    "conduct": {
        "emoji": get_emoji("heart"),
        "label": "Conduct",
        "title": "Conduct rules — 1 to 5",
        "body": (
            "- **1. Be respectful.** No harassment, hate speech, discrimination, or personal attacks — treat everyone the way you'd like to be treated.\n"
            "- **2. Keep it appropriate.** No NSFW content anywhere in this server.\n"
            "- **3. No drama or targeted attacks.** Public call-outs and witch hunts are handled by staff, not members.\n"
            "- **4. Use English.** It keeps support fast and inclusive; DMs are yours to use however you like.\n"
            "- **5. Staff have the final say.** If a moderator asks you to stop something, stop — disputes can be raised politely afterwards."
        ),
    },
    "content": {
        "emoji": get_emoji("scroll"),
        "label": "Content & channels",
        "title": "Content & channel rules — 6 to 10",
        "body": (
            "- **6. Right content in the right channel.** Keep questions in support channels, showcases in their dedicated channels, and memes in the lounge.\n"
            "- **7. No spam, flooding, or self-promotion without permission.** This includes unsolicited DMs and advertising other bots or servers.\n"
            "- **8. No malicious content.** No scams, phishing, malware, IP grabbers, or jump-scare links — report anything suspicious to staff instead of clicking it.\n"
            "- **9. Piracy is not welcome.** No links to or requests for pirated media, software, or paid assets.\n"
            "- **10. Use threads when topics drift.** Long side-discussions get moved into threads to keep channels readable."
        ),
    },
    "moderation": {
        "emoji": get_emoji("moderation"),
        "label": "Moderation",
        "title": "Moderation & enforcement — 11 to 15",
        "body": (
            "- **11. Moderators may act** on anything they judge to be against the spirit of these rules, even if it isn't listed.\n"
            "- **12. Escalation ladder.** Typical progression: verbal warning → formal warning → timeout → kick → ban. Severe violations (scams, malware, raids, CSAM) skip straight to a ban and are reported to Discord's Trust & Safety.\n"
            "- **13. Ban evasion is a permanent ban.** Alternate accounts made to return are removed on sight.\n"
            "- **14. Appeals.** Ban appeals go through the support server ticket system — be honest; lying makes it worse.\n"
            "- **15. Niko's global blacklist** is separate from this server's moderation. Abusing the bot itself (exploits, command spam) can get you blacklisted bot-wide under its Terms of Service."
        ),
    },
    "bot": {
        "emoji": get_emoji("bot"),
        "label": "Bot rules",
        "title": "Bot-specific rules — 16 to 20",
        "body": (
            "- **16. Niko is a community project, not a product.** The operator provides no uptime guarantee; premium supports development but buys no SLA.\n"
            "- **17. Economy items have no real value.** Bot currency and items cannot be sold, traded for money, or refunded.\n"
            "- **18. Don't exploit bugs.** Found one? Report it in the support channel and don't farm it — exploiters lose balances and risk blacklisting.\n"
            "- **19. Automated abuse is prohibited.** Self-bots, macro farms, and command spam hurt the bot for everyone.\n"
            "- **20. AI replies are clearly marked.** Niko's AI features can be wrong — verify important things yourself."
        ),
    },
}

_RULES_LINKS_ID = "niko:rules:links"
_RULES_SCOPE_ID = "niko:rules:scope"


class _RulesLinksButton(discord.ui.DynamicItem[discord.ui.Button], template=r"niko:rules:links"):
    """Persistent shortcut to the ephemeral important-links card."""

    def __init__(self) -> None:
        super().__init__(discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Important links",
            emoji=get_emoji("link"),
            custom_id=_RULES_LINKS_ID,
        ))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls()

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            view=_rules_links_view(interaction.client), ephemeral=True
        )


class _RulesScopeButton(discord.ui.DynamicItem[discord.ui.Button], template=r"niko:rules:scope"):
    """Persistent shortcut to the ephemeral out-of-scope reporting card."""

    def __init__(self) -> None:
        super().__init__(discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Not ours to fix",
            emoji=get_emoji("question"),
            custom_id=_RULES_SCOPE_ID,
        ))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls()

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            view=_rules_scope_view(interaction.client), ephemeral=True
        )


def _rules_header(bot, title: str, subtitle: str) -> discord.ui.Item:
    """Panel header with the bot's avatar as thumbnail (plain text fallback)."""
    header_text = discord.ui.TextDisplay(content=(f"## {get_emoji('support')} {title}\n-# {subtitle}"))
    avatar = None
    try:
        user = getattr(bot, "user", None)
        avatar = getattr(user, "display_avatar", None)
    except Exception:
        avatar = None
    if avatar is not None:
        return discord.ui.Section(header_text, accessory=discord.ui.Thumbnail(str(avatar.url)))
    return header_text


DISCORD_SUPPORT_URL = "https://support.discord.com/hc/en-us/requests/new"
DISCORD_REPORT_URL = "https://discord.com/safety/360044103651-reporting-abusive-behavior-to-discord"


def _rules_panel_row() -> discord.ui.ActionRow:
    """The public panel's only buttons: shortcuts to the helper cards."""
    return discord.ui.ActionRow(_RulesLinksButton(), _RulesScopeButton())


def _rules_links_view(bot) -> discord.ui.LayoutView:
    """Ephemeral card listing every official Niko link."""
    bot_id = getattr(getattr(bot, "user", None), "id", None)
    invite = (
        f"https://discord.com/oauth2/authorize?client_id={bot_id}&permissions=8&scope=bot%20applications.commands"
        if bot_id else links.SUPPORT_SERVER
    )
    items: list = [
        _rules_header(bot, "Important links", "Every official Niko page in one place."),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=(
            "**Start here**\n"
            f"- {get_emoji('website')} [Website]({links.WEBSITE}) — news, changelog and the server dashboard.\n"
            f"- {get_emoji('docs')} [Documentation]({links.DOCS}) — setup guides and the full command reference.\n"
            f"- {get_emoji('support')} [Support server]({links.SUPPORT_SERVER}) — this community's permanent invite.\n"
            f"- {get_emoji('invite')} [Invite Niko]({invite}) — add the bot to your own server.\n\n"
            "**Policies**\n"
            f"- {get_emoji('docs')} [Terms of Service]({links.TOS})\n"
            f"- {get_emoji('important')} [Privacy Policy]({links.PRIVACY})\n"
            f"- {get_emoji('verified')} [Community Guidelines]({links.COMMUNITY})\n"
            f"- {get_emoji('lock')} [Request removal of your data]({links.DATA_REMOVAL})\n\n"
            "**Elsewhere**\n"
            f"- {get_emoji('github')} [GitHub]({links.GITHUB}) — source, issues and release notes.\n"
            f"- {get_emoji('topgg')} [Vote on top.gg]({links.TOPGG_VOTE_URL}) — a free way to help other servers find Niko."
        )),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            discord.ui.Button(style=discord.ButtonStyle.link, label="Website", url=links.WEBSITE),
            discord.ui.Button(style=discord.ButtonStyle.link, label="Docs", url=links.DOCS),
            discord.ui.Button(style=discord.ButtonStyle.link, label="Support server", url=links.SUPPORT_SERVER),
            discord.ui.Button(style=discord.ButtonStyle.link, label="Privacy", url=links.PRIVACY),
            discord.ui.Button(style=discord.ButtonStyle.link, label="Terms", url=links.TOS),
        ),
    ]
    view = discord.ui.LayoutView(timeout=300)
    view.add_item(discord.ui.Container(*items, accent_colour=0xC8A882))
    return view


def _rules_scope_view(bot) -> discord.ui.LayoutView:
    """Ephemeral card for problems Niko's team cannot act on."""
    items: list = [
        _rules_header(bot, "Not ours to fix", "Some reports belong to Discord or another team — here is where each one goes."),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=(
            "**Discord account & platform issues**\n"
            "- Lost account, 2FA, a hacked account, Nitro or Discord billing, or a bug inside the Discord app "
            f"→ [Discord Support]({DISCORD_SUPPORT_URL}). Niko staff cannot view or change your Discord account.\n"
            "- A user, message or server breaking Discord's own rules "
            f"→ [report it to Discord Trust & Safety]({DISCORD_REPORT_URL}), or use the in-app **Report** option. "
            "We can only moderate inside this server.\n"
            "- A different bot, bot list or third-party service "
            "→ that project's own support server. We have no access to it.\n\n"
            "**What we do handle**\n"
            "- A Niko command failing, an error code, or a feature that does not work as documented "
            "→ open a **Bug** post in the community-help forum with the exact error text.\n"
            "- Anything tied to your account, a purchase, premium, appeals or data removal "
            "→ open a private ticket and never post payment details in public.\n"
            "- A member or post in this server that needs staff attention "
            "→ mention a member of staff or open a ticket instead of confronting anyone publicly."
        )),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            discord.ui.Button(style=discord.ButtonStyle.link, label="Discord Support", url=DISCORD_SUPPORT_URL),
            discord.ui.Button(style=discord.ButtonStyle.link, label="Report to Discord", url=DISCORD_REPORT_URL),
            discord.ui.Button(style=discord.ButtonStyle.link, label="Niko docs", url=links.DOCS),
        ),
    ]
    view = discord.ui.LayoutView(timeout=300)
    view.add_item(discord.ui.Container(*items, accent_colour=0x5865F2))
    return view


def _rules_home_view(bot) -> discord.ui.LayoutView:
    """The public panel: every rule, printed inline, plus helper-card buttons."""
    items: list = [
        _rules_header(
            bot,
            "Niko Support — Server Rules",
            "Everyone here, staff included. Reading these once is all it takes.",
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=(
            f"{get_emoji('welcome')} Hey, I'm **Niko** — a cozy Discord companion for communities that care. "
            "This is the official Niko support server: help, ideas, announcements and a friendly corner of Discord.\n"
            "The twenty rules below apply everywhere in this server, so please read them before posting."
        )),
    ]
    for meta in RULES_SECTIONS.values():
        items.append(discord.ui.TextDisplay(content=f"### {meta['emoji']} {meta['title']}\n{meta['body']}"))
    items.extend([
        discord.ui.TextDisplay(content=(
            f"-# {get_emoji('question')} Bot help belongs in the community-help forum; account or sensitive issues "
            "belong in a ticket. Use the buttons below for important links, and for reports that are not ours to handle."
        )),
        _rules_panel_row(),
    ])

    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(*items, accent_colour=0xC8A882))
    return view


def _build_rules_panel(bot) -> discord.ui.LayoutView:
    return _rules_home_view(bot)


class _StatusPanelCog(commands.Cog):
    """Internal cog that owns the persistent status-panel refresh loop."""

    def __init__(self, bot):
        self.bot = bot
        self._refresh_task = None

    async def cog_load(self):
        self._refresh_task = asyncio.create_task(_status_refresh_loop(self.bot))

    async def cog_unload(self):
        if self._refresh_task is not None:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass


async def _status_refresh_loop(bot):
    """Re-edit every stored status panel every STATUS_PANEL_INTERVAL seconds."""
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            cxn = getattr(bot, "cxn", None)
            if cxn is None:
                await asyncio.sleep(STATUS_PANEL_INTERVAL)
                continue
            rows = await cxn.fetch(
                "SELECT channel_id, message_id FROM persistent_status_panels"
            )
            if not rows:
                await asyncio.sleep(STATUS_PANEL_INTERVAL)
                continue

            status = await _collect_status(bot)
            panel_view = _build_status_panel(bot, status)
            for row in rows:
                try:
                    channel = bot.get_channel(int(row["channel_id"]))
                    if channel is None:
                        continue
                    message = channel.get_partial_message(int(row["message_id"]))
                    await message.edit(view=panel_view)
                except discord.HTTPException:
                    # Deleted panel, missing permissions, etc. — skip this row.
                    continue
                except Exception:
                    continue
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logging.warning("StatusPanel", f"Refresh tick failed: {exc}")
        await asyncio.sleep(STATUS_PANEL_INTERVAL)


async def setup(bot):
    await bot.add_cog(OwnerCog(bot))
    await bot.add_cog(_StatusPanelCog(bot))
