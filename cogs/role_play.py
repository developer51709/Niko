import requests
import discord
from discord.ext import commands
import random

class RolePlayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="isitworking")
    async def isitworking(self, ctx):
        messages = [
            "Gfys",
            "Go die in a fucking hole bitch",
            "Kys",
            "Fuck you",
            "Fuck off",
            "I'm not your fucking slave dumb ass",
            "Please just do us all a favor and fucking die",
            "Kill yourself bitch"
        ]
        random_message = random.choice(messages)
        await ctx.send(random_message)


async def setup(bot):
    await bot.add_cog(RolePlayCog(bot))