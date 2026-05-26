from .views import *

class HelpCog(commands.Cog):
    """Custom help system — fully trilingual (EN / DE / ES)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="help",
        description="Show the help menu",
        help="{ 'en': 'show the help menu 📘☕', 'de': 'zeige das Hilfemenü 📘☕', 'es': 'muestra el menú de ayuda 📘☕' }",
    )
    async def help(self, ctx: commands.Context, *, command_name: str = None):
        lang = get_lang(ctx)

        if command_name:
            cmd = self.bot.get_command(command_name)
            if not cmd:
                content = (
                    f"### {get_emoji('icon_cross')} {_ui(lang, 'cmd_not_found_title')}\n"
                    f"{_ui(lang, 'cmd_not_found_body', name=command_name)}"
                )
                view = _make_layout(self.bot, content, lang, include_dropdown=False)
                return await ctx.send(view=view)

            content = await _command_detail_text(self.bot, cmd, ctx)
            view    = _make_layout(self.bot, content, lang, include_dropdown=False)
            return await ctx.send(view=view)

        content = _general_text(self.bot, lang)
        view    = _make_layout(self.bot, content, lang, include_dropdown=True, general_page=True)
        await ctx.send(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
