import discord
from discord.ext import commands
from config.emojis import get_emoji
from utils.ai_config import get_personality

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
    personality = get_personality(ctx)
    lang = get_lang(ctx)
    text = MESSAGES.get(personality, {}).get(lang, {}).get(key)
    if text is None:
        text = MESSAGES["normal"].get(lang, {}).get(key, key)
    return text.format(**kwargs) if kwargs else text


class AICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="favor", help="{ 'en': 'check our vibe score ☕✨', 'de': 'sieh dir unseren Vibe-Wert an' }")
    async def favor(self, ctx, member: discord.Member = None):
        """Display the favorability score for a user."""
        from bot import get_favorability_score
        target = member or ctx.author
        score = get_favorability_score(target.id)
        await ctx.send(msg(ctx, "favor_score", name=target.display_name, score=score))

    @commands.command(name="memory", help="{ 'en': 'see my café notes on you ☕📝', 'de': 'sieh dir meine Café-Notizen an' }")
    async def memory(self, ctx, member: discord.Member = None):
        """Display the memory content for a user."""
        from bot import get_memory_content
        target = member or ctx.author
        mem = get_memory_content(target.id)
        if not mem:
            await ctx.send(msg(ctx, "no_memory", name=target.display_name))
        else:
            try:
                mem = mem[-3000:]
                title = msg(ctx, "memory_title", name=target.display_name)
                text = f"### {title}\n```\n{mem}\n```"
                view = discord.ui.LayoutView()
                view.add_item(discord.ui.Container(
                    discord.ui.TextDisplay(content=text)
                ))
                await ctx.send(view=view)
            except Exception as e:
                view = discord.ui.LayoutView()
                view.add_item(discord.ui.Container(
                    discord.ui.TextDisplay(content=f"### {get_emoji('icon_cross')} Error\nFailed to display memory:\n```\n{e}\n```")
                ))
                await ctx.send(view=view)


async def setup(bot):
    await bot.add_cog(AICog(bot))
