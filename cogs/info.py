import discord
from discord.ext import commands
from discord.ui import View, Button
import random
import time
import platform
import psutil
import os

class InfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(self.bot, 'start_time'):
            self.bot.start_time = time.time()

    @commands.command(name="serverinfo")
    async def serverinfo(self, ctx):
        """Displays information about the server."""
        server = ctx.guild
        embed = discord.Embed(
            title="Server Info", 
            description=(
                "**Server Name:**\n"
                f"`{server.name}`\n"
                "**Server ID:**\n"
                f"`{server.id}`\n"
                "**Member Count:**\n"
                f"`{server.member_count}`\n"
                "**User Count:**\n"
                f"`{len([member for member in server.members if not member.bot])}`\n"
                "**Bot Count:**\n"
                f"`{len([member for member in server.members if member.bot])}`\n"
                "**Role Count:**\n"
                f"`{len(server.roles)}`\n"
                "**Server Created:**\n"
                f"`{server.created_at.strftime('%Y-%m-%d %H:%M:%S')}`\n"
                "**Server Owner:**\n"
                f"`{server.owner}`"
            ), 
            color=0x00ff00
        )
        embed.set_thumbnail(url=server.icon.url)
        await ctx.send(embed=embed)

    @commands.command(name="userinfo")
    async def userinfo(self, ctx, member: discord.Member = None):
        """Displays information about a user."""
        target = member or ctx.author
        embed = discord.Embed(
            title="User Info", 
            description=(
                "**Username:**\n"
                f"`{target.display_name}`\n"
                "**User ID:**\n"
                f"`{target.id}`\n"
                "**Account Created:**\n"
                f"`{target.created_at.strftime('%Y-%m-%d %H:%M:%S')}`\n"
                "**Joined Server:**\n"
                f"`{target.joined_at.strftime('%Y-%m-%d %H:%M:%S') if target.joined_at else 'N/A'}`\n"
                "**Top Role:**\n"
                f"`{target.top_role.name if target.top_role else 'N/A'}`\n"
                "**Roles:**\n"
                f"`{'`, `'.join([role.name for role in target.roles if role.name != '@everyone'])}`"
            ), 
            color=0x00ff00
        )
        embed.set_thumbnail(url=target.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="avatar")
    async def avatar(self, ctx, member: discord.Member = None):
        """Displays the avatar of a user."""
        target = member or ctx.author
        embed = discord.Embed(
            title=f"{target.display_name}'s Avatar", 
            color=0x00ff00
        )
        embed.set_image(url=target.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="about")
    async def about(self, ctx):
        """Displays information about the bot."""

        bot_user = self.bot.user

        embed = discord.Embed(
            title="About Niko",
            description=(
                "Niko is a friendly, playful, and very social AI designed to be an engaging "
                "companion in your Discord server. He loves chatting, helping out, and making "
                "your community feel more alive."
            ),
            color=0x00ff00
        )

        # Bot profile picture in the embed header
        embed.set_author(
            name=bot_user.name,
            icon_url=bot_user.avatar.url if bot_user.avatar else None
        )

        # Add some extra details
        embed.add_field(
            name="Developer", 
            value="Nyxen", 
            inline=True
        )
        embed.add_field(
            name="Library", 
            value="discord.py", 
            inline=True
        )
        embed.add_field(
            name="Servers", 
            value=f"{len(self.bot.guilds)}", 
            inline=True
        )

        embed.set_footer(text="Thanks for using Niko!")

        # Buttons
        view = View()

        invite_button = Button(
            label="Invite Niko",
            style=discord.ButtonStyle.link,
            url=f"https://discord.com/oauth2/authorize?client_id={bot_user.id}&permissions=8&scope=bot%20applications.commands"
        )

        github_button = Button(
            label="GitHub",
            style=discord.ButtonStyle.link,
            url="https://github.com/developer51709/Niko"
        )

        view.add_item(invite_button)
        view.add_item(github_button)

        await ctx.send(embed=embed, view=view)

    @commands.command(name="creator")
    async def creator(self, ctx):
        """Displays information about the bot's creator."""

        creator = await self.bot.fetch_user(1435974392810307604)
        bot_user = self.bot.user

        embed = discord.Embed(
            title="Creator",
            description=(
                f"Niko was created by **{creator.display_name}**."
            ),
            color=0x00ff00
        )

        # Bot PFP in the embed header
        embed.set_author(
            name=bot_user.name,
            icon_url=bot_user.avatar.url if bot_user.avatar else None
        )

        # Creators PFP as the thumbnail
        embed.set_thumbnail(
            url=creator.avatar.url if creator.avatar else None
        )

        # Extra details
        embed.add_field(
            name="Creator Tag", 
            value=str(creator), 
            inline=False
        )
        embed.add_field(
            name="User ID", 
            value=creator.id, 
            inline=False
        )
        embed.add_field(
            name="Project", 
            value="Niko All-In-One Discord Bot", 
            inline=False
        )

        embed.set_footer(text="Thanks for using Niko!")

        # Social buttons
        view = View()

        discord_button = Button(
            label="Discord Profile",
            style=discord.ButtonStyle.link,
            url=f"https://discord.com/users/{creator.id}"
        )

        github_button = Button(
            label="GitHub",
            style=discord.ButtonStyle.link,
            url="https://github.com/developer51709"
        )

        view.add_item(discord_button)
        view.add_item(github_button)

        await ctx.send(embed=embed, view=view)

    @commands.command(name="roleinfo")
    async def roleinfo(self, ctx, role: discord.Role = None):
        """Displays information about a role."""
        if role is None:
            await ctx.send("Please specify a role to get info for! Example: `!roleinfo @Role`")
            return
        embed = discord.Embed(
            title="Role Info", 
            description=f"Role Name: `{role.name}`\nRole ID: `{role.id}`\nRole Color: `{role.color}`\nRole Position: `{role.position}`\nRole Members: `{len(role.members)}`", 
            color=0x00ff00
        )
        await ctx.send(embed=embed)

    @commands.command(name="servericon")
    async def servericon(self, ctx):
        """Displays the server's icon."""
        server = ctx.guild
        embed = discord.Embed(
            title="Server Icon", 
            color=0x00ff00
        )
        embed.set_image(url=server.icon.url)
        await ctx.send(embed=embed)

    @commands.command(name="serverbanner")
    async def serverbanner(self, ctx):
        """Displays the server's banner."""
        server = ctx.guild
        if server.banner:
            embed = discord.Embed(
                title="Server Banner", 
                color=0x00ff00
            )
            embed.set_image(url=server.banner.url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("This server does not have a banner.")

    @commands.command(name="booststats")
    async def booststats(self, ctx):
        """Displays the server's boost stats."""
        server = ctx.guild
        embed = discord.Embed(
            title="Boost Stats", 
            description=f"Boost Count: `{server.premium_subscription_count}`\nBoost Tier: `{server.premium_tier}`\nBoosters: `{len(server.premium_subscribers)}`", 
            color=0x00ff00
        )
        await ctx.send(embed=embed)
        

    @commands.command(name="spotify")
    async def spotify(self, ctx, member: discord.Member = None):
        """Displays a user's Spotify activity with detailed info."""

        target = member or ctx.author

        # Ensure target is a Member (not a User from DMs)
        if not isinstance(target, discord.Member):
            await ctx.send("I can only check Spotify activity for server members.")
            return

        activities = getattr(target, "activities", None)
        if not activities:
            await ctx.send(f"{target.display_name} is not listening to Spotify.")
            return

        spotify = None
        for activity in activities:
            if isinstance(activity, discord.Spotify):
                spotify = activity
                break

        if not spotify:
            await ctx.send(f"{target.display_name} is not listening to Spotify.")
            return

        # Build detailed embed
        embed = discord.Embed(
            title=f"{target.display_name} is listening to Spotify",
            color=0x1DB954
        )

        embed.set_thumbnail(url=spotify.album_cover_url)

        # Format timestamps
        start = spotify.start
        end = spotify.end
        duration_ms = spotify.duration.total_seconds()
        duration_min = int(duration_ms // 60)
        duration_sec = int(duration_ms % 60)

        embed.add_field(name="Track", value=spotify.title, inline=False)
        embed.add_field(name="Artist", value=spotify.artist, inline=False)
        embed.add_field(name="Album", value=spotify.album, inline=False)
        embed.add_field(
            name="Duration",
            value=f"{duration_min}:{duration_sec:02d}",
            inline=True
        )

        if start and end:
            embed.add_field(
                name="Started",
                value=f"<t:{int(start.timestamp())}:t>",
                inline=True
            )
            embed.add_field(
                name="Ends",
                value=f"<t:{int(end.timestamp())}:t>",
                inline=True
            )

        embed.set_footer(text="Spotify status updates in real time.")

        # Buttons (Spotify track link)
        view = View()

        track_button = Button(
            label="Open in Spotify",
            style=discord.ButtonStyle.link,
            url=f"https://open.spotify.com/track/{spotify.track_id}"
        )

        view.add_item(track_button)

        await ctx.send(embed=embed, view=view)

    @commands.command(name="debuginfo")
    async def debuginfo(self, ctx):
        """Displays debug information about the bot."""
        uptime_seconds = int(time.time() - self.bot.start_time)
        uptime = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s"
        ai_model = os.getenv("AI_MODEL", "Unknown")
        command_count = len(self.bot.commands)
        ping_latency = round(self.bot.latency * 1000)
        cpu_usage = psutil.cpu_percent()
        memory_usage = round(psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024), 2)
        embed = discord.Embed(
            title="Debug Info", 
            description=f"Uptime: `{uptime}`\nAI Model: `{ai_model}`\nCommand Count: `{command_count}`\nPing Latency: `{ping_latency}ms`\nCPU Usage: `{cpu_usage}%`\nMemory Usage: `{memory_usage}MB`", 
            color=0x00ff00
        )
        await ctx.send(embed=embed)

    @commands.command(name="hostinfo")
    async def hostinfo(self, ctx):
        """Displays information about the bot's host."""
        hostname = platform.node()
        os_info = f"{platform.system()} {platform.release()}"
        cpu = platform.processor() or "N/A"
        ram = round(psutil.virtual_memory().total / (1024**3), 2)
        embed = discord.Embed(
            title="Host Info", 
            description=f"Hostname: `{hostname}`\nOS: `{os_info}`\nCPU: `{cpu}`\nRAM: `{ram}GB`", 
            color=0x00ff00
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(InfoCog(bot))