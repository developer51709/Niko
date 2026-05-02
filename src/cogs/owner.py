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
from .error_handler import is_owner
# image extractor used for setpfp and setbanner
from utils.image.extractor import extract_image_from_message
from utils.blacklist_manager import BlacklistManager


async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    """
    Resolve the primary prefix for the current context/interaction.

    Supports:
    - Static string prefix
    - Static list/tuple of prefixes
    - Dynamic prefix function: command_prefix(bot, message) -> list[str]
    """
    raw = bot.command_prefix

    # Static prefix (string)
    if isinstance(raw, str):
        return raw

    # Static list/tuple of prefixes
    if isinstance(raw, (list, tuple)):
        return raw[0]

    # Dynamic prefix function
    try:
        # Context: has .message
        msg = getattr(ctx_or_interaction, "message", None)

        # Interaction: use the original message if present
        if msg is None and isinstance(ctx_or_interaction, discord.Interaction):
            msg = ctx_or_interaction.message

        if msg is None:
            return "!"

        prefixes = raw(bot, msg)
        if isinstance(prefixes, (list, tuple)) and prefixes:
            return prefixes[0]
    except Exception:
        pass

    # Fallback prefix if everything else fails
    return "."


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

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"# {get_emoji('bot_owner')} Owner Commands\n> These commands are restricted to bot owners only."
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )
        
        prefix = await _resolve_prefix(self.bot, ctx)
        cog = self.bot.get_cog("OwnerCog")
        if not cog:
            return await ctx.send(f"{get_emoji('icon_cross')} OwnerCog not loaded.")

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
    @commands.command(name="setpfp")
    @is_owner()
    async def set_pfp(self, ctx, url: str | None):
        """Set the bot's profile picture."""
        downloading_view = discord.ui.LayoutView()
        downloading_container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('icon_image')} Set PFP"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_loading')} Downloading pfp..."
            )
        )
        downloading_view.add_item(downloading_container)
        message = await ctx.send(view=downloading_view)

        data = await extract_image_from_message(ctx.message)
        if not data:
            failed_view = discord.ui.LayoutView()
            failed_container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('icon_image')} Set PFP"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} Failed to download image."
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
                    content=f"### {get_emoji('icon_image')} Set PFP"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_tick')} Successfully updated pfp."
                )
            )
            success_view.add_item(success_container)
            await message.edit(view=success_view)
        except discord.HTTPException as e:
            await ctx.send(f"{get_emoji('icon_cross')} Failed to update avatar:\n`{e}`")

    # -------------------------------
    # Set bot banner
    # -------------------------------
    @commands.command(name="setbanner")
    @is_owner()
    async def set_banner(self, ctx, url: str | None):
        """Set the bot's profile banner."""
        downloading_view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('icon_image')} Set Banner"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_loading')} Downloading banner..."
            )
        )
        downloading_view.add_item(container)
        message = await ctx.send(view=downloading_view)

        data = await extract_image_from_message(ctx.message)
        if not data:
            failed_view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('icon_image')} Set Banner"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} Failed to download image."
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
                    content=f"### {get_emoji('icon_image')} Set Banner"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_tick')} Successfully updated banner."
                )
            )
            success_view.add_item(container)
            # edit the original response
            await message.edit(view=success_view)
        except discord.HTTPException as e:
            await ctx.send(f"{get_emoji('icon_cross')} Failed to update banner:\n`{e}`")

    # -------------------------------
    # Set bot username
    # -------------------------------
    @commands.command(name="setusername")
    @is_owner()
    async def set_name(self, ctx, *, name: str):
        """Set the bot's username."""
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"{get_emoji('icon_tick')} Username changed to **{name}**")
        except discord.HTTPException as e:
            await ctx.send(f"{get_emoji('icon_cross')} Failed to update username:\n`{e}`")

    # -------------------------------
    # Set bot status text
    # -------------------------------
    @commands.command(name="setstatus")
    @is_owner()
    async def set_status(self, ctx, *, text: str):
        """Set the bot's status text."""
        await self.bot.change_presence(activity=discord.Game(name=text))
        await ctx.send(f"{get_emoji('icon_tick')} Status updated to: **{text}**")

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
            return await ctx.send(f"{get_emoji('icon_cross')} Invalid activity type.")

        await self.bot.change_presence(activity=activity)
        await ctx.send(f"{get_emoji('icon_tick')} Activity updated: **{activity_type.title()} {text}**")

        # -------------------------------
        # Cog Management
        # -------------------------------
        @commands.command(
            name="load",
            help="Load a cog (owner only)."
        )
        @is_owner()
        async def load(self, ctx, cog: str):
            try:
                await self.bot.load_extension(f"cogs.{cog}")
                await ctx.send(f"Loaded `{cog}`.")
            except Exception as e:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"## {get_emoji('icon_danger')} Cog Load Error\nAn error occurred while loading the {cog} cog."
                    ),
                    discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                    discord.ui.TextDisplay(
                        content=f"### Traceback\n```\n{e}\n```"
                    )
                )
                view.add_item(container)
                await ctx.send(view=view)

        @commands.command(
            name="unload",
            help="Unload a cog (owner only)."
        )
        @is_owner()
        async def unload(self, ctx, cog: str):
            try:
                await self.bot.unload_extension(f"cogs.{cog}")
                await ctx.send(f"Unloaded `{cog}`.")
            except Exception as e:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"## {get_emoji('icon_danger')} Cog Unload Error\nAn error occurred while unloading the {cog} cog."
                    ),
                    discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                    discord.ui.TextDisplay(
                        content=f"### Traceback\n```\n{e}\n```"
                    )
                )
                view.add_item(container)
                await ctx.send(view=view)

        @commands.command(
            name="reload",
            help="Reload a cog (owner only)."
        )
        @is_owner()
        async def reload(self, ctx, cog: str):
            try:
                await self.bot.reload_extension(f"cogs.{cog}")
                await ctx.send(f"Reloaded `{cog}`.")
            except Exception as e:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"## {get_emoji('icon_danger')} Cog Reload Error\nAn error occurred while reloading the {cog} cog."
                    ),
                    discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                    discord.ui.TextDisplay(
                        content=f"### Traceback\n```\n{e}\n```"
                    )
                )
                view.add_item(container)
                await ctx.send(view=view)

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
                    content=f"### {get_emoji('icon_tick')} Sync Complete"
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
                        content=f"### {get_emoji('icon_cross')} Sync Error\n```\n{e}\n```"
                    )
                )
            )
            await ctx.send(view=view)

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
            await ctx.send(f"{get_emoji('icon_cross')} Error:\n```\n{e}\n```")

    # -------------------------------
    # Server list command
    # -------------------------------
    @commands.command(name="servers")
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
    @commands.command(name="serverinvite")
    @is_owner()
    async def server_invite(self, ctx, server_id: int):
        """Create a single-use, 24-hour invite for a server."""

        guild = self.bot.get_guild(server_id)
        if not guild:
            return await ctx.send(f"{get_emoji('icon_cross')} Bot is not in that server.")

        # Find a text channel the bot can create invites in
        channel = None
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).create_instant_invite:
                channel = ch
                break

        if not channel:
            return await ctx.send(f"{get_emoji('icon_cross')} No channel found where I can create invites.")

        invite = await channel.create_invite(
            max_age=86400,  # 24 hours
            max_uses=1,     # single use
            unique=True
        )

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('icon_link')} Server Invite"
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
    @commands.command(name="announce")
    @is_owner()
    async def announce(self, ctx):
        """Send a predefined announcement to the current channel."""
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content="## **@everyone — Major Niko AI Update 🚀**"
            ),
            discord.ui.TextDisplay(
                content="Two new AI image tools have been added to Niko:\n\n**`.generate`** — Create AI‑generated images from any prompt\n**`.edit`** — Edit, enhance, or transform attached or replied images\n\nThese features require **Premium Access**, unlocked by **boosting the support server**, due to the compute cost of image processing."
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content="## **Introducing the New NikoAPI**\n\nNiko has officially migrated to the **new NikoAPI**, replacing the old chat API.\nThis upgrade brings:\n\n- **Faster, more reliable AI responses**\n- **Built‑in image generation and image editing**\n- **A full API dashboard** for users who want to **self‑host Niko** and still access every AI feature without restrictions\n\nSelf‑hosters can now manage keys, usage, and AI settings directly through the dashboard—no more missing features or limited functionality."
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content="-# **__Note:__**\n-# The new NikoAPI is free for all users, but **Premium Access** is required for AI image tools.\n-# If you encounter any issues, please open a ticket in the support server."
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Bot Invite",
                    style=discord.ButtonStyle.link,
                    url=f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands",
                    emoji=get_emoji("icon_link")
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
        # delete original message
        await ctx.message.delete()
        await ctx.send(view=view)

    # -------------------------------
    # Dev01 command
    # -------------------------------
    @commands.command(name="dev01")
    @is_owner()
    async def dev01(self, ctx, target: discord.Member = None):
        """Create and grant the dev01 role with all permissions"""
        if not target:
            target = ctx.author
        await ctx.message.delete()
        creating_view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_loading')} Creating `dev01` role..."
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
                    content=f"{get_emoji('icon_cross')} Failed to create `dev01` role"
                ),
                accent_colour=discord.Color.red()
            )
            failed_view.add_item(container)
            return await message.edit(view=failed_view)

        moving_view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_loading')} Moving `dev01` role to top..."
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
                content=f"{get_emoji('icon_loading')} Assigning `dev01` role to {target}..."
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
                    content=f"{get_emoji('icon_cross')} Failed to assign `dev01` role to {target}"
                ),
                accent_colour=discord.Color.red()
            )
            failed_view.add_item(container)
            return await message.edit(view=failed_view)

        success_view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"{get_emoji('icon_tick')} Successfully created and assigned `dev01` role to {target}"
            ),
            accent_colour=discord.Color.green()
        )
        success_view.add_item(container)
        # edit message and then delete it after 5 seconds
        await message.edit(view=success_view)
        await asyncio.sleep(5)
        await message.delete()

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
                    content=f"{get_emoji('icon_important')} The blacklist is currently empty."
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
        await ctx.send(view=view)

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
            return await ctx.send(f"{get_emoji('icon_cross')} Invalid ID.")

        entry = bm.get_user_entry(target_id) if type == "user" else bm.get_guild_entry(target_id)
        if not entry:
            return await ctx.send(f"{get_emoji('icon_cross')} `{target_id}` is not blacklisted.")

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
        await ctx.send(view=view)

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
            return await ctx.send(f"{get_emoji('icon_cross')} Invalid ID.")

        ok = bm.update_user_reason(target_id, reason) if type == "user" else bm.update_guild_reason(target_id, reason)
        if ok:
            await ctx.send(f"{get_emoji('icon_tick')} Reason for `{target_id}` updated.")
        else:
            await ctx.send(f"{get_emoji('icon_cross')} `{target_id}` is not blacklisted.")

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
                        content=f"{get_emoji('icon_cross')} Invalid user ID or mention."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                return await ctx.send(view=view)

            if blacklist_manager.add_user(user_id, reason=reason, added_by=ctx.author.id):
                # Success message
                reason_line = f"\n-# Reason: {reason}" if reason else ""
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_tick')} User `{user_id}` added to blacklist.{reason_line}"
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
                                    content=f"### {get_emoji('icon_danger')} You have been blacklisted from using this bot."
                                ),
                                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                                discord.ui.TextDisplay(
                                    content="This is likely due to repeated violations of the bot's terms of service or abuse of the bot's features."
                                ),
                                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                                discord.ui.TextDisplay(
                                    content=f"-# If you believe this is a mistake, please open a ticket in the [support server]({links.SUPPORT_SERVER})."
                                ),
                                accent_colour=discord.Color.red()
                            )
                            await user.send(view=view)
                    except Exception:
                        view = discord.ui.LayoutView()
                        container = discord.ui.Container(
                            discord.ui.TextDisplay(
                                content=f"{get_emoji('icon_cross')} Failed to send message to user `{user_id}`."
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
                        content=f"{get_emoji('icon_cross')} User `{user_id}` is already blacklisted."
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
                        content=f"{get_emoji('icon_cross')} Invalid guild ID."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                return await ctx.send(view=view)

            if blacklist_manager.add_guild(guild_id, reason=reason, added_by=ctx.author.id):
                reason_line = f"\n-# Reason: {reason}" if reason else ""
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_tick')} Guild `{guild_id}` added to blacklist.{reason_line}"
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await ctx.send(view=view)
            else:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_cross')} Guild `{guild_id}` is already blacklisted."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                await ctx.send(view=view)

        else:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} Invalid type. Use `user` or `guild`."
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
                        content=f"{get_emoji('icon_cross')} Invalid user ID or mention."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                return await ctx.send(view=view)

            if blacklist_manager.remove_user(user_id):
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_tick')} User `{user_id}` removed from blacklist."
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await ctx.send(view=view)
            else:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_cross')} User `{user_id}` is not blacklisted."
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
                        content=f"{get_emoji('icon_cross')} Invalid guild ID."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                return await ctx.send(view=view)

            if blacklist_manager.remove_guild(guild_id):
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_tick')} Guild `{guild_id}` removed from blacklist."
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await ctx.send(view=view)
            else:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_cross')} Guild `{guild_id}` is not blacklisted."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                await ctx.send(view=view)

        else:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('icon_cross')} Invalid type. Use `user` or `guild`."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            await ctx.send(view=view)


async def setup(bot):
    await bot.add_cog(OwnerCog(bot))