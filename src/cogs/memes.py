import discord
from discord.ext import commands
import aiohttp
import random
from utils.ai_config import get_personality

# -----------------------------
# MESSAGE DICTIONARY
# -----------------------------
MESSAGES = {
    "normal": {
        "en": {
            "fetch_fail": "Couldn't fetch memes right now.",
            "no_safe_memes": "No safe memes available right now.",
            "meme_title_prefix": "",
        },
        "de": {
            "fetch_fail": "Konnte gerade keine Memes abrufen.",
            "no_safe_memes": "Keine sicheren Memes verfügbar.",
            "meme_title_prefix": "",
        },
    },

    "cafe": {
        "en": {
            "fetch_fail": "aww i couldn’t fetch any memes rn 😭☕",
            "no_safe_memes": "no safe memes in the café right now 😭☕",
            "meme_title_prefix": "☕ meme of the moment — ",
        },
        "de": {
            "fetch_fail": "aww ich konnte gerade keine memes holen 😭☕",
            "no_safe_memes": "keine sicheren memes im café gerade 😭☕",
            "meme_title_prefix": "☕ meme des moments — ",
        },
    },

    # future personalities can be added here
}

# -----------------------------
# LANGUAGE + PERSONALITY HELPERS
# -----------------------------
def get_lang(ctx):
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
    return "en"


def msg(ctx, key, **kwargs):
    personality = get_personality(ctx)
    lang = get_lang(ctx)

    # try personality + lang
    block = MESSAGES.get(personality, {}).get(lang, {})
    text = block.get(key)

    # fallback personality + en
    if text is None:
        text = MESSAGES.get(personality, {}).get("en", {}).get(key)

    # fallback normal + lang
    if text is None:
        text = MESSAGES["normal"].get(lang, {}).get(key)

    # fallback normal + en
    if text is None:
        text = MESSAGES["normal"]["en"].get(key, key)

    return text.format(**kwargs) if kwargs else text


# -----------------------------
# MEME COG
# -----------------------------
class Meme(commands.Cog):
    """Fetches memes with cozy café personality + bilingual support."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="meme",
        help="get a cozy random meme ☕✨ | holt ein zufälliges meme"
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

        # personality-aware embed styling
        personality = get_personality()
        lang = get_lang(ctx)

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