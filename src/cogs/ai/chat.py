import discord
from discord.ext import commands
from config.emojis import get_emoji
from utils.i18n import make_msg

MESSAGES = {
    "normal": {
        "en": {
            "no_memory":       "No memory recorded for {name} in this server.",
            "memory_title":    "Memory for {name}",
            "guild_only":      "Niko's memory is kept per server, so this only works inside a server.",
            "history_cleared": "Your conversation history and memory with Niko in this server have been cleared.",
            "history_empty":   "You don't have any conversation history with Niko in this server yet.",
        },
        "de": {
            "no_memory":       "Kein Speicher für {name} in diesem Server gefunden.",
            "memory_title":    "Speicher für {name}",
            "guild_only":      "Nikios Gedächtnis wird pro Server gespeichert — das funktioniert nur in einem Server.",
            "history_cleared": "Dein Gesprächsverlauf und Gedächtnis mit Niko in diesem Server wurden gelöscht.",
            "history_empty":   "Du hast in diesem Server noch keinen Gesprächsverlauf mit Niko.",
        },
        "es": {
            "no_memory":       "No hay memoria registrada para {name} en este servidor.",
            "memory_title":    "Memoria de {name}",
            "guild_only":      "La memoria de Niko es por servidor, así que esto solo funciona dentro de un servidor.",
            "history_cleared": "Tu historial de conversación y memoria con Niko en este servidor han sido borrados.",
            "history_empty":   "Aún no tienes historial de conversación con Niko en este servidor.",
        }
    },
}

msg = make_msg(MESSAGES)


class AICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="memory", help="{ 'en': 'see my café notes on you ☕📝', 'de': 'sieh dir meine Café-Notizen an' }")
    async def memory(self, ctx, member: discord.Member = None):
        """Display this server's memory content for a user."""
        from utils.ai.memory import get_memory_text

        if ctx.guild is None:
            return await ctx.send(msg(ctx, "guild_only"))

        target = member or ctx.author
        mem = await get_memory_text(ctx.guild.id, target.id)
        if not mem:
            return await ctx.send(msg(ctx, "no_memory", name=target.display_name))

        mem = mem[-3000:]
        title = msg(ctx, "memory_title", name=target.display_name)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {title}\n```\n{mem}\n```")
        ))
        await ctx.send(view=view)

    @commands.hybrid_command(
        name="clearhistory",
        description="Clear your conversation history and memory with Niko in this server",
        aliases=["clearchat", "resetmemory"],
        help="{ 'en': 'wipe your conversation history + memory with niko ☕', 'de': 'Gesprächsverlauf + Gedächtnis mit Niko löschen', 'es': 'borrar tu historial de conversación con Niko' }",
    )
    async def clearhistory(self, ctx: commands.Context):
        """Wipe your own short-term history and memory with Niko in this server."""
        from utils.ai.memory import clear_user, has_memory

        if ctx.guild is None:
            return await ctx.send(msg(ctx, "guild_only"), ephemeral=True)

        if not await has_memory(ctx.guild.id, ctx.author.id):
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=msg(ctx, "history_empty")),
            ))
            return await ctx.send(view=view, ephemeral=True)

        await clear_user(ctx.guild.id, ctx.author.id)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"{get_emoji('tick')} {msg(ctx, 'history_cleared')}"),
        ))
        await ctx.send(view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(AICog(bot))
