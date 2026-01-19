import requests
import discord
from discord.ext import commands
import random

class RolePlayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # !kill command
    @commands.command(name="kill")
    async def kill(self, ctx, member: discord.Member = None):
        target = member
        if target:
            await ctx.send(f"{ctx.author.display_name} killed {target.display_name}!")
        else:
            await ctx.send("You need to mention a user to kill them!")

    # !fuck command
    @commands.command(name="fuck")
    async def fuck(self, ctx, member: discord.Member = None):
        target = member
        if target:
            await ctx.send(f"{ctx.author.display_name} fucked {target.display_name}!")
        else:
            await ctx.send("You need to mention a user to fuck them!")


async def setup(bot):
    await bot.add_cog(RolePlayCog(bot))