import discord
from discord.ext import commands
import aiohttp
import random

class Meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="meme")
    async def meme(self, ctx):
        """Fetch a random meme using meme-api.com."""
        url = "https://meme-api.com/gimme/50"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await ctx.send("Couldn't fetch memes right now.")

                data = await resp.json()

        memes = data.get("memes", [])

        # Filter out NSFW memes if channel isn't NSFW
        if not ctx.channel.is_nsfw():
            memes = [m for m in memes if not m.get("nsfw")]

        if not memes:
            return await ctx.send("No safe memes available right now.")

        meme = random.choice(memes)

        embed = discord.Embed(
            title=meme["title"],
            url=meme["postLink"],
            color=discord.Color.random()
        )
        embed.set_image(url=meme["url"])
        embed.set_footer(text=f"👍 {meme['ups']} • r/{meme['subreddit']}")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Meme(bot))