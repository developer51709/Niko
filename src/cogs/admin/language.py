"""``/language`` — pick the language Niko speaks in a server.

Discord only exposes ``guild.preferred_locale`` once a server enables Community,
which left every other server stuck in English. The choice made here is stored
by :mod:`utils.guild_language` and read by ``utils.i18n.get_lang`` before the
Discord locale, so it works with or without Community mode.
"""

import discord
from discord import app_commands
from discord.ext import commands

from config.emojis import get_emoji
from utils import guild_language, logging
from utils.command_locales import command_texts
from utils.i18n import get_lang, make_flat_msg
from utils.locales import SUPPORTED_LANGUAGES, load_locales
from utils.prefix_manager import resolve_prefix

CMDS = command_texts(__package__)
MESSAGES = load_locales(__package__, "language")
msg = make_flat_msg(MESSAGES, {
    "settings": get_emoji("settings"),
    "tick": get_emoji("tick"),
    "warning": get_emoji("warning"),
})

#: Each language in its own name, so the picker reads the same to everyone.
LANGUAGE_NAMES = {
    "en": "English",
    "de": "Deutsch",
    "es": "Español",
    "fr": "Français",
    "ru": "Русский",
    "ja": "日本語",
    "zh": "中文",
    "hi": "हिन्दी",
    "ar": "العربية",
}

#: A prefix user may type any of these to go back to Discord's choice.
AUTO_VALUES = {"auto", "automatic", "default", "reset", "clear"}

LANGUAGE_CHOICES = [
    app_commands.Choice(
        name=LANGUAGE_NAMES.get(code, code.upper()), value=code
    )
    for code in SUPPORTED_LANGUAGES
] + [app_commands.Choice(name="Automatic", value="auto")]


def _label(code: str) -> str:
    return f"{LANGUAGE_NAMES.get(code, code.upper())} (`{code}`)"


def _available() -> str:
    return ", ".join(_label(code) for code in SUPPORTED_LANGUAGES)


def _card(title: str, body: str, accent: discord.Colour) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=title),
        discord.ui.Separator(),
        discord.ui.TextDisplay(content=body),
        accent_colour=accent,
    ))
    return view


class LanguageConfig(commands.Cog):
    """Server language selection without Discord's Community mode."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="language",
        aliases=["lang"],
        description=CMDS.text("language.description"),
        help=CMDS.help("language"),
    )
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(language=CMDS.arg("language", "language"))
    @app_commands.choices(language=LANGUAGE_CHOICES)
    async def language_config(self, ctx: commands.Context, language: str | None = None):
        """Show or change the language Niko uses in this server."""
        value = (language or "").strip().lower()

        if not value:
            override = guild_language.language_for(ctx.guild.id)
            mode = msg(ctx, "mode_override" if override else "mode_auto")
            body = msg(
                ctx, "current",
                language=_label(get_lang(ctx)),
                mode=mode,
            )
            body += "\n\n" + msg(ctx, "available", languages=_available())
            body += "\n" + msg(ctx, "usage", prefix=await resolve_prefix(self.bot, ctx))
            return await ctx.send(
                view=_card(msg(ctx, "title"), body, discord.Color.blurple())
            )

        pool = getattr(self.bot, "cxn", None)

        if value in AUTO_VALUES:
            try:
                await guild_language.clear_language(ctx.guild.id, pool)
            except Exception as exc:
                logging.error("Language", f"Could not reset {ctx.guild.id}: {exc}")
                return await ctx.send(view=_card(
                    msg(ctx, "error_title"), msg(ctx, "save_failed"), discord.Color.red()))
            return await ctx.send(view=_card(
                msg(ctx, "cleared_title"), msg(ctx, "cleared_body"), discord.Color.green()
            ))

        try:
            code = guild_language.normalize(value)
        except ValueError:
            return await ctx.send(view=_card(
                msg(ctx, "error_title"),
                msg(ctx, "invalid", value=value, languages=_available()),
                discord.Color.yellow(),
            ))

        try:
            await guild_language.set_language(ctx.guild.id, code, pool)
        except Exception as exc:
            logging.error("Language", f"Could not save {ctx.guild.id}: {exc}")
            return await ctx.send(view=_card(
                msg(ctx, "error_title"), msg(ctx, "save_failed"), discord.Color.red()))

        await ctx.send(view=_card(
            msg(ctx, "set_title"),
            msg(ctx, "set_body", language=_label(get_lang(ctx))),
            discord.Color.green(),
        ))


async def setup(bot):
    await bot.add_cog(LanguageConfig(bot))
