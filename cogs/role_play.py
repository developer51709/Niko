import discord
from discord.ext import commands

class RolePlayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # !kill command
    @commands.command(name="kill")
    async def kill(self, ctx, member: discord.Member = None):
        '''Kill another user. (not really)'''
        target = member or ctx.author
        await ctx.send(f"{ctx.author.display_name} killed {target.display_name}!")

    # !fuck command
    @commands.command(name="fuck")
    async def fuck(self, ctx, member: discord.Member = None):
        '''Fuck another user. (not really)'''
        target = member or ctx.author
        await ctx.send(f"{ctx.author.display_name} fucked {target.display_name}!")

    # !hug command
    @commands.command(name="hug")
    async def hug(self, ctx, member: discord.Member = None):
        '''Hug another user. (not really)'''
        target = member
        if target is None:
            await ctx.send("You need to mention someone to hug them!")
        else:
            await ctx.send(f"{ctx.author.display_name} hugged {target.display_name}! :hugging:")

    # !makeout command
    @commands.command(name="makeout")
    async def makeout(self, ctx, member: discord.Member = None):
        '''Make out with another user. (not really)'''
        target = member
        if target is None:
            await ctx.send("You need to mention someone to make out with them!")
        else:
            await ctx.send(f"{ctx.author.display_name} made out with {target.display_name}! :kissing_heart:")

    # !rape command
    @commands.command(name="rape")
    async def rape(self, ctx, member: discord.Member = None):
        '''Rape another user. (not really)'''
        target = member
        if target is None:
            await ctx.send("You have to mention someone to use this command on them!")
        else:
            await ctx.send(f"{ctx.author.display_name} raped {target.display_name}!")


async def setup(bot):
    await bot.add_cog(RolePlayCog(bot))