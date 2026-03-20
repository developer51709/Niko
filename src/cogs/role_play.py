import discord
import random
from discord.ext import commands

PERSONALITY = "cafe"

MESSAGES = {
    "normal": {
        "en": {
            "need_mention": "You need to mention someone to use this command on them!",
            "hug_desc": "{author} hugged {target}! :hugging:",
            "kill_desc": "{author} killed {target}!",
            "kill_footer": "*This is a joke, don't actually kill anyone.*",
        },
        "de": {
            "need_mention": "Du musst jemanden erwähnen, um diesen Befehl zu nutzen!",
            "hug_desc": "{author} hat {target} umarmt! :hugging:",
            "kill_desc": "{author} hat {target} getötet!",
            "kill_footer": "*Das ist ein Witz, töte bitte niemanden wirklich.*",
        }
    },
    "cafe": {
        "en": {
            "need_mention": "who are we doing this with? mention a friend! ☕✨",
            "hug_desc": "omg! {author} gave {target} a big, warm café hug! ☕💖",
            "kill_desc": "oh no! {author} playfully took out {target}! ☕💀",
            "kill_footer": "*this is just café roleplay, no one actually got hurt ☕*",
        },
        "de": {
            "need_mention": "Mit wem machen wir das? Erwähne einen Freund! ☕✨",
            "hug_desc": "omg! {author} hat {target} eine große, warme Café-Umarmung gegeben! ☕💖",
            "kill_desc": "oh nein! {author} hat {target} spielerisch ausgeschaltet! ☕💀",
            "kill_footer": "*das ist nur café-roleplay, niemand wurde wirklich verletzt ☕*",
        }
    }
}

def get_lang(ctx):
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
    return "en"

def msg(ctx, key, **kwargs):
    personality = PERSONALITY if PERSONALITY in MESSAGES else "normal"
    lang = get_lang(ctx)
    text = MESSAGES.get(personality, {}).get(lang, {}).get(key)
    if text is None:
        text = MESSAGES["normal"].get(lang, {}).get(key, key)
    return text.format(**kwargs) if kwargs else text


class RolePlayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="kill", help="playfully take out a friend ☕💀 | schalte einen Freund spielerisch aus")
    async def kill(self, ctx, member: discord.Member = None):
        """Kill another user. (not really)"""
        try:
            if not member:
                return await ctx.send(msg(ctx, "need_mention"))
            kill_gifs = [
                "https://i.pinimg.com/originals/36/d5/fd/36d5fd46d8331661819031b2b7adcda4.gif"
            ]
            text = (
                f"### ☕💀 kill\n"
                f"{msg(ctx, 'kill_desc', author=ctx.author.display_name, target=member.display_name)}\n"
                f"-# {msg(ctx, 'kill_footer')}"
            )
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
            view.add_item(discord.ui.MediaGallery(
                discord.ui.MediaGalleryItem(url=random.choice(kill_gifs))
            ))
            await ctx.send(view=view)
        except Exception as e:
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(discord.ui.TextDisplay(
                content=f"### ❌ Error\n```\n{e}\n```"
            )))
            await ctx.send(view=view)

    @commands.command(name="hug", help="give a big, warm café hug ☕💖 | gib eine große, warme Café-Umarmung")
    async def hug(self, ctx, member: discord.Member = None):
        """Hug another user."""
        try:
            if not member:
                return await ctx.send(msg(ctx, "need_mention"))
            hug_gifs = [
                "https://static.klipy.com/ii/e293a233a303a98e471f78d04e13a1b0/88/68/BrZiPlu3.webp",
                "https://static.klipy.com/ii/935d7ab9d8c6202580a668421940ec81/f4/97/FWkQ3IhM.webp",
                "https://static.klipy.com/ii/c3a19a0b747a76e98651f2b9a3cca5ff/8a/00/V2DQIgua.webp"
            ]
            text = (
                f"### ☕💖 hug\n"
                f"{msg(ctx, 'hug_desc', author=ctx.author.display_name, target=member.display_name)}"
            )
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
            view.add_item(discord.ui.MediaGallery(
                discord.ui.MediaGalleryItem(url=random.choice(hug_gifs))
            ))
            await ctx.send(view=view)
        except Exception as e:
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(discord.ui.TextDisplay(
                content=f"### ❌ Error\n```\n{e}\n```"
            )))
            await ctx.send(view=view)


async def setup(bot):
    await bot.add_cog(RolePlayCog(bot))
