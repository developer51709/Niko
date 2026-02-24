import discord
import random
from discord.ext import commands

# personality mode: "normal" or "cafe"
PERSONALITY = "cafe"

MESSAGES = {
    "normal": {
        "en": {
            "need_mention": "You need to mention someone to use this command on them!",
            "hug_desc": "{author} hugged {target}! :hugging:",
            "kill_desc": "{author} killed {target}!",
        },
        "de": {
            "need_mention": "Du musst jemanden erwähnen, um diesen Befehl zu nutzen!",
            "hug_desc": "{author} hat {target} umarmt! :hugging:",
            "kill_desc": "{author} hat {target} getötet!",
        }
    },
    "cafe": {
        "en": {
            "need_mention": "who are we doing this with? mention a friend! ☕✨",
            "hug_desc": "omg! {author} gave {target} a big, warm café hug! ☕💖",
            "kill_desc": "oh no! {author} playfully took out {target}! ☕💀",
        },
        "de": {
            "need_mention": "Mit wem machen wir das? Erwähne einen Freund! ☕✨",
            "hug_desc": "omg! {author} hat {target} eine große, warme Café-Umarmung gegeben! ☕💖",
            "kill_desc": "oh nein! {author} hat {target} spielerisch ausgeschaltet! ☕💀",
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

    # !kill command
    @commands.command(name="kill", help="playfully take out a friend ☕💀 | schalte einen Freund spielerisch aus")
    async def kill(self, ctx, member: discord.Member = None):
        """Kill another user. (not really)"""
        try:
            if not member:
                return await ctx.send(msg(ctx, "need_mention"))
            target = member
            kill_gifs = [
                "https://i.pinimg.com/originals/36/d5/fd/36d5fd46d8331661819031b2b7adcda4.gif"
            ]
            kill_embed = discord.Embed(
                title="Kill", 
                description=msg(ctx, "kill_desc", author=ctx.author.display_name, target=target.display_name), 
                color=discord.Color.red()
            )
            kill_embed.set_image(url=random.choice(kill_gifs))
            kill_embed.set_footer(text="*This is a joke, don't actually kill anyone.*")
            await ctx.send(embed=kill_embed)
        except Exception as e:
            error_embed = discord.Embed(title="Error", description=f"An error occurred:\n```\n{e}\n```", color=discord.Color.red())
            await ctx.send(embed=error_embed)

    # !hug command
    @commands.command(name="hug", help="give a big, warm café hug ☕💖 | gib eine große, warme Café-Umarmung")
    async def hug(self, ctx, member: discord.Member = None):
        """Hug another user. (not really)"""
        try:
            if not member:
                return await ctx.send(msg(ctx, "need_mention"))
            target = member
            hug_gifs = [
                "https://static.klipy.com/ii/e293a233a303a98e471f78d04e13a1b0/88/68/BrZiPlu3.webp",
                "https://static.klipy.com/ii/935d7ab9d8c6202580a668421940ec81/f4/97/FWkQ3IhM.webp",
                "https://static.klipy.com/ii/c3a19a0b747a76e98651f2b9a3cca5ff/8a/00/V2DQIgua.webp"
            ]
            hug_embed = discord.Embed(
                title="Hug",
                description=msg(ctx, "hug_desc", author=ctx.author.display_name, target=target.display_name),
                color=discord.Color.green()
            )
            hug_embed.set_image(url=random.choice(hug_gifs))
            await ctx.send(embed=hug_embed)
        except Exception as e:
            error_embed = discord.Embed(title="Error", description=f"An error occurred:\n```\n{e}\n```", color=discord.Color.red())
            await ctx.send(embed=error_embed)


async def setup(bot):
    await bot.add_cog(RolePlayCog(bot))