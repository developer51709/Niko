import discord
from discord.ext import commands
import aiohttp
import random
from utils.i18n import make_flat_msg
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

# -----------------------------
# MESSAGE DICTIONARY
# -----------------------------
MESSAGES = load_locales("cogs.fun", "memes")

msg = make_flat_msg(MESSAGES)


# -----------------------------
# MEME COG
# -----------------------------
class Meme(commands.Cog):
    """Fetches memes with bilingual support."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="meme",
        help=CMDS.help("meme"),
    )
    async def meme(self, ctx):
        """Fetch a random meme using meme-api.com"""
        url = "https://meme-api.com/gimme/50"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await ctx.send(msg(ctx, "fetch_fail"))

                data = await resp.json()

        memes = data.get("memes", [])

        # Filter out NSFW memes if channel isn't NSFW
        if not ctx.channel.is_nsfw():
            memes = [m for m in memes if not m.get("nsfw")]

        if not memes:
            return await ctx.send(msg(ctx, "no_safe_memes"))

        meme = random.choice(memes)

        title_prefix = msg(ctx, "meme_title_prefix")
        title = f"{title_prefix}{meme['title']}"

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {title}\n[Source]({meme['postLink']})"
            ),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=meme['url']
                )
            ),
            discord.ui.TextDisplay(
                content=f"-# 👍 {meme['ups']} • r/{meme['subreddit']}"
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

async def setup(bot):
    await bot.add_cog(Meme(bot))