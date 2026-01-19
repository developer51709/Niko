import discord
from discord.ext import commands

class AICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="favor")
    async def favor(self, ctx, member: discord.Member = None):
        from bot import get_favorability_score
        target = member or ctx.author
        score = get_favorability_score(target.id)
        await ctx.send(f"{target.display_name} has a favorability score of **{score}** with Niko.")

    @commands.command(name="memory")
    async def memory(self, ctx, member: discord.Member = None):
        from bot import get_memory_content
        target = member or ctx.author
        mem = get_memory_content(target.id)
        if not mem:
            await ctx.send(f"No memory recorded for {target.display_name}.")
        else:
            await ctx.send(f"Memory for {target.display_name}:\n{mem}")

async def setup(bot):
    await bot.add_cog(AICog(bot))
