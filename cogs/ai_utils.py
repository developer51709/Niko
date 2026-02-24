import discord
from discord.ext import commands

# personality mode: "normal" or "cafe"
PERSONALITY = "cafe"

MESSAGES = {
    "normal": {
        "en": {
            "favor_score": "{name} has a favorability score of **{score}** with Niko.",
            "no_memory": "No memory recorded for {name}.",
            "memory_title": "Memory for {name}",
        },
        "de": {
            "favor_score": "{name} hat einen Beliebtheitswert von **{score}** bei Niko.",
            "no_memory": "Kein Speicher für {name} gefunden.",
            "memory_title": "Speicher für {name}",
        }
    },
    "cafe": {
        "en": {
            "favor_score": "{name} and i have a vibe score of **{score}**! ☕✨",
            "no_memory": "i don't have any notes on {name} yet... we should chat more! ☕📝",
            "memory_title": "☕ café notes on {name}",
        },
        "de": {
            "favor_score": "{name} und ich haben einen Vibe-Wert von **{score}**! ☕✨",
            "no_memory": "ich habe noch keine Notizen über {name}... wir sollten mehr plaudern! ☕📝",
            "memory_title": "☕ Café-Notizen über {name}",
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

class AICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="favor")
    async def favor(self, ctx, member: discord.Member = None):
        """Display the favorability score for a user."""
        from bot import get_favorability_score
        target = member or ctx.author
        score = get_favorability_score(target.id)
        await ctx.send(msg(ctx, "favor_score", name=target.display_name, score=score))

    @commands.command(name="memory")
    async def memory(self, ctx, member: discord.Member = None):
        """Display the memory content for a user."""
        from bot import get_memory_content
        target = member or ctx.author
        mem = get_memory_content(target.id)
        if not mem:
            await ctx.send(msg(ctx, "no_memory", name=target.display_name))
        else:
            try:
                memory_embed = discord.Embed(
                    title=msg(ctx, "memory_title", name=target.display_name),
                    description=f"```\n{mem}\n```",
                    color=discord.Color.green()
                )
                await ctx.send(embed=memory_embed)
            except Exception as e:
                error_embed = discord.Embed(title="Error", description=f"Failed to display memory: \n```\n{e}\n```")
                await ctx.send(embed=error_embed)

async def setup(bot):
    await bot.add_cog(AICog(bot))
