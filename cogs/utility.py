import discord
from discord.ext import commands

class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send("Pong!")

    @commands.command(name="echo")
    async def echo(self, ctx, *, message: str):
        await ctx.send(message)

    @commands.command(name="uwu")
    async def uwu(self, ctx):
        await ctx.send("Nyaa~!")

    @commands.command(name="nitro")
    async def nitro(self, ctx):
        rickroll_gif = "https://csyn.me/assets/rickroll.gif"
        embed = discord.Embed(title="Nitro", description="No nitro here!", color=0x00ff00)
        embed.set_image(url=rickroll_gif)
        await ctx.send(embed=embed)

    @commands.command(name="partnership_request")
    async def partnership_request(self, ctx, invite: str):
        requester = ctx.author
        log_channel = self.bot.get_channel(1462614744052797683)
        if log_channel:
            embed = discord.Embed(title="Partnership Request", description=f"Requested by: {requester.display_name}\nInvite: {invite}", color=0x00ff00)
            await log_channel.send(embed=embed)
            await ctx.send("Partnership request sent successfully!")
        else:
            await ctx.send("Error: Log channel not found.")

    @commands.command(name="boring")
    async def boring(self, ctx):
        embed = discord.Embed(title="What did you expect?", description="I bet you thought this command would do something cool, but no. It's just boring.", color=0x00ff00)
        await ctx.send(embed=embed)

    @commands.command(name="notboring")
    async def notboring(self, ctx):
        embed = discord.Embed(title="I lied :)", description="This command is actually in fact quite boring.", color=0x00ff00)
        await ctx.send(embed=embed)

    @commands.command(name="crazy")
    async def crazy(self, ctx):
        embed = discord.Embed(title="Crazy?", description="Crazy? I was crazy once. They locked me in a room. A rubber room. A rubber room with rats. And rats make me crazy.\n\nCrazy? I was crazy once. They locked me in a room. A rubber room. A rubber room with rats. And rats make me crazy.\n\nCrazy? I was crazy once...", color=0x00ff00)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
