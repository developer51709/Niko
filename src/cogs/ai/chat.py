import discord
from discord.ext import commands
from config.emojis import get_emoji
from utils.ai.config import get_personality
from utils.i18n import make_msg

MESSAGES = {
    "normal": {
        "en": {
            "favor_score":     "{name} has a favorability score of **{score}** with Niko.",
            "no_memory":       "No memory recorded for {name}.",
            "memory_title":    "Memory for {name}",
            "history_cleared": "✅ Your conversation history and memory with Niko have been cleared.",
            "history_empty":   "You don't have any conversation history with Niko yet.",
        },
        "de": {
            "favor_score":     "{name} hat einen Beliebtheitswert von **{score}** bei Niko.",
            "no_memory":       "Kein Speicher für {name} gefunden.",
            "memory_title":    "Speicher für {name}",
            "history_cleared": "✅ Dein Gesprächsverlauf und Gedächtnis mit Niko wurden gelöscht.",
            "history_empty":   "Du hast noch keinen Gesprächsverlauf mit Niko.",
        },
        "es": {
            "favor_score":     "{name} tiene una puntuación de favoritismo de **{score}** con Niko.",
            "no_memory":       "No hay memoria registrada para {name}.",
            "memory_title":    "Memoria de {name}",
            "history_cleared": "✅ Tu historial de conversación y memoria con Niko han sido borrados.",
            "history_empty":   "Aún no tienes historial de conversación con Niko.",
        }
    },
}

msg = make_msg(MESSAGES)


class AICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="favor", help="{ 'en': 'check our vibe score ☕✨', 'de': 'sieh dir unseren Vibe-Wert an' }")
    async def favor(self, ctx, member: discord.Member = None):
        """Display the favorability score for a user."""
        from utils.ai.memory import get_favorability_score
        target = member or ctx.author
        score  = get_favorability_score(target.id)
        await ctx.send(msg(ctx, "favor_score", name=target.display_name, score=score))

    @commands.command(name="memory", help="{ 'en': 'see my café notes on you ☕📝', 'de': 'sieh dir meine Café-Notizen an' }")
    async def memory(self, ctx, member: discord.Member = None):
        """Display the memory content for a user."""
        from utils.ai.memory import get_memory_content
        target = member or ctx.author
        mem    = get_memory_content(target.id)
        if not mem:
            await ctx.send(msg(ctx, "no_memory", name=target.display_name))
        else:
            try:
                mem   = mem[-3000:]
                title = msg(ctx, "memory_title", name=target.display_name)
                text  = f"### {title}\n```\n{mem}\n```"
                view  = discord.ui.LayoutView()
                view.add_item(discord.ui.Container(
                    discord.ui.TextDisplay(content=text)
                ))
                await ctx.send(view=view)
            except Exception as e:
                view = discord.ui.LayoutView()
                view.add_item(discord.ui.Container(
                    discord.ui.TextDisplay(content=f"### {get_emoji('cross')} Error\nFailed to display memory:\n```\n{e}\n```")
                ))
                await ctx.send(view=view)

    @commands.hybrid_command(
        name="clearhistory",
        description="Clear your conversation history and memory with Niko",
        aliases=["clearchat", "resetmemory"],
        help="{ 'en': 'wipe your conversation history + memory with niko ☕', 'de': 'Gesprächsverlauf + Gedächtnis mit Niko löschen', 'es': 'borrar tu historial de conversación con Niko' }",
    )
    async def clearhistory(self, ctx: commands.Context):
        """Wipe your own short-term conversation history and long-term memory with Niko."""
        from utils.ai.memory import clear_conversation_history, get_conversation_history, get_memory_content
        has_history = bool(get_conversation_history(ctx.author.id) or get_memory_content(ctx.author.id))
        if not has_history:
            text = msg(ctx, "history_empty")
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=text),
                accent_colour=discord.Color.yellow(),
            ))
            return await ctx.send(view=view, ephemeral=True)

        clear_conversation_history(ctx.author.id)
        text = msg(ctx, "history_cleared")
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=text),
            accent_colour=discord.Color.green(),
        ))
        await ctx.send(view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(AICog(bot))
