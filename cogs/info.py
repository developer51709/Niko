import discord
from discord.ext import commands
import random

class InfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="serverinfo")
    async def serverinfo(self, ctx):
        server = ctx.guild
        embed = discord.Embed(title="Server Info", description=f"Server Name: {server.name}\nServer ID: {server.id}\nMember Count: {server.member_count}", color=0x00ff00)
        await ctx.send(embed=embed)

    @commands.command(name="userinfo")
    async def userinfo(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        embed = discord.Embed(title="User Info", description=f"Username: {target.display_name}\nUser ID: {target.id}\nJoined Server: {target.joined_at.strftime('%Y-%m-%d %H:%M:%S') if target.joined_at else 'N/A'}", color=0x00ff00)
        await ctx.send(embed=embed)

    @commands.command(name="avatar")
    async def avatar(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        embed = discord.Embed(title=f"{target.display_name}'s Avatar", color=0x00ff00)
        embed.set_image(url=target.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="about")
    async def about(self, ctx):
        embed = discord.Embed(title="About Niko", description="Niko is a friendly, playful, and socially aware femboy-coded AI. He is designed to be a fun and engaging companion in your Discord server.", color=0x00ff00)
        await ctx.send(embed=embed)

    @commands.command(name="creator")
    async def creator(self, ctx):
        creator = await self.bot.fetch_user(1435974392810307604)
        embed = discord.Embed(title="Creator", description=f"Niko was created by {creator.display_name}.", color=0x00ff00)
        await ctx.send(embed=embed)

    @commands.command(name="roleinfo")
    async def roleinfo(self, ctx, role: discord.Role):
        embed = discord.Embed(title=f"Role Info", description=f"Role Name: {role.name}\nRole ID: {role.id}\nRole Color: {role.color}\nRole Position: {role.position}\nRole Members: {len(role.members)}", color=0x00ff00)
        await ctx.send(embed=embed)

    @commands.command(name="serverstats")
    async def serverstats(self, ctx):
        server = ctx.guild
        embed = discord.Embed(title="Server Stats", description=f"Server Name: {server.name}\nServer ID: {server.id}\nMember Count: {server.member_count}\nUser Count: {len([member for member in server.members if not member.bot])}\nBot Count: {len([member for member in server.members if member.bot])}\nRole Count: {len(server.roles)}", color=0x00ff00)
        await ctx.send(embed=embed)

    @commands.command(name="servericon")
    async def servericon(self, ctx):
        server = ctx.guild
        embed = discord.Embed(title="Server Icon", color=0x00ff00)
        embed.set_image(url=server.icon.url)
        await ctx.send(embed=embed)

    @commands.command(name="serverbanner")
    async def serverbanner(self, ctx):
        server = ctx.guild
        if server.banner:
            embed = discord.Embed(title="Server Banner", color=0x00ff00)
            embed.set_image(url=server.banner.url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("This server does not have a banner.")

    @commands.command(name="booststats")
    async def booststats(self, ctx):
        server = ctx.guild
        embed = discord.Embed(title="Boost Stats", description=f"Boost Count: {server.premium_subscription_count}\nBoost Tier: {server.premium_tier}\nBoosters: {len(server.premium_subscribers)}\nBoost Progress: {server.premium_progress}\nActive Perks: {server.premium_features}", color=0x00ff00)
        await ctx.send(embed=embed)

    @commands.command(name="spotify")
    async def spotify(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        if target.activities:
            for activity in target.activities:
                if isinstance(activity, discord.Spotify):
                    embed = discord.Embed(title=f"{target.display_name}'s Spotify", description=f"Listening to: {activity.title}\nArtist: {activity.artist}\nAlbum: {activity.album}", color=0x00ff00)
                    embed.set_thumbnail(url=activity.album_cover_url)
                    await ctx.send(embed=embed)
                    return
            await ctx.send(f"{target.display_name} is not listening to Spotify.")
        else:
            await ctx.send(f"{target.display_name} is not listening to Spotify.")

    @commands.command(name="nyx")
    async def nyx(self, ctx):
        messages = [
            "Nyx is a really sexy guy.",
            "Nyx is so hot.",
            "I love Nyx.",
            "Nyx is sucking my dick right now.",
            "Nyx is so fucking hot.",
            "I want to fuck Nyx",
            "Nyx is so sexy.",
            "Daddy Nyx is the hottest guy in the world.",
            "I wish I could fuck Nyx so hard that he would cum all over my fucking face and I would lick it all off and then I would ride him like a fucking horse until he is so fucking tired that he would pass out.",
            "I just want to passionately make love to Nyx until we are so fucking tired that we pass out.",
            "Daddy Nyx is so fricking sexy that I wish I could just fuck him right now."
        ]
        random_message = random.choice(messages)
        await ctx.send(random_message)

async def setup(bot):
    await bot.add_cog(InfoCog(bot))
