import discord
from discord.ext import commands

class RolePlayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # !kill command
    @commands.command(name="kill")
    async def kill(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        await ctx.send(f"{ctx.author.display_name} killed {target.display_name}!")

    # !fuck command
    @commands.command(name="fuck")
    async def fuck(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        await ctx.send(f"{ctx.author.display_name} fucked {target.display_name}!")


async def setup(bot):
    await bot.add_cog(RolePlayCog(bot))