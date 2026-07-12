import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions, MissingRequiredArgument, EmojiNotFound
import io
import aiohttp
import pathlib
import re
from typing import Optional
import zipfile
import asyncio
from utils import logging as log
from utils.ai.config import get_personality
from utils.i18n import make_msg

MESSAGES = {
    "normal": {
        "en": {
            "emojimanager_title": "Emoji Manager",
            "emojimanager_description": "Manage your server's emojis!",
            "steal_description": "steal an emoji",
            "sm_description": "steal many emojis",
            "surl_description": "add from url",
            "enlarge_description": "big emoji view",
            "emojistats_description": "view slots",
            "re_description": "remove emoji",
            "emoji_added": "Successfully added emoji: {emoji} (`:{name}:`)",
            "server_full": "This server has reached its maximum emoji limit of {limit}.",
            "no_perms": "I don't have the permissions to manage emojis.",
            "error": "An error occurred: {error}",
            "not_found": "Could not find or download the emoji. Please ensure you provided the full emoji string (e.g., `<:name:id>`).",
            "timeout": "You took too long. Operation cancelled.",
            "invalid_name": "Invalid name. Please use alphanumeric characters (2-32 chars).",
            "no_emojis": "This server has no custom emojis."
        },
        "de": {
            "emojimanager_title": "Emoji-Verwaltung",
            "emojimanager_description": "Verwalte die Emojis deines Servers!",
            "steal_description": "stiehl ein Emoji",
            "sm_description": "stiehl viele Emojis",
            "surl_description": "von URL hinzufügen",
            "enlarge_description": "Emoji groß anzeigen",
            "emojistats_description": "Emoji-Slots ansehen",
            "re_description": "Emoji entfernen",
            "emoji_added": "Emoji erfolgreich hinzugefügt: {emoji} (`:{name}:`)",
            "server_full": "Dieser Server hat das Limit von {limit} Emojis erreicht.",
            "no_perms": "Ich habe keine Berechtigung, Emojis zu verwalten.",
            "error": "Ein Fehler ist aufgetreten: {error}",
            "not_found": "Emoji konnte nicht gefunden oder heruntergeladen werden. Bitte gib den vollständigen Emoji-String an (z.B. `<:name:id>`).",
            "timeout": "Zeit abgelaufen. Vorgang abgebrochen.",
            "invalid_name": "Ungültiger Name. Bitte nutze alphanumerische Zeichen (2-32 Zeichen).",
            "no_emojis": "Dieser Server hat keine benutzerdefinierten Emojis."
        },
        "es": {
            "emojimanager_title": "Gestor de Emojis",
            "emojimanager_description": "¡Gestiona los emojis de tu servidor!",
            "steal_description": "robar un emoji",
            "sm_description": "robar varios emojis",
            "surl_description": "añadir desde URL",
            "enlarge_description": "ver emoji grande",
            "emojistats_description": "ver espacios",
            "re_description": "quitar emoji",
            "emoji_added": "Emoji añadido correctamente: {emoji} (`:{name}:`)",
            "server_full": "Este servidor ha alcanzado el límite máximo de {limit} emojis.",
            "no_perms": "No tengo permisos para gestionar emojis.",
            "error": "Ha ocurrido un error: {error}",
            "not_found": "No pude encontrar o descargar el emoji. Asegúrate de proporcionar el texto completo del emoji (p. ej. `<:nombre:id>`).",
            "timeout": "Tardaste demasiado. Operación cancelada.",
            "invalid_name": "Nombre inválido. Usa caracteres alfanuméricos (2-32 caracteres).",
            "no_emojis": "Este servidor no tiene emojis personalizados."
        }
    },
    "cafe": {
        "en": {
            "emojimanager_title": "Niko's Emoji Studio 🎨✨",
            "emojimanager_description": "manage your café's aesthetics!",
            "steal_description": "steal an emoji",
            "sm_description": "steal many emojis",
            "surl_description": "add from url",
            "enlarge_description": "big emoji view",
            "emojistats_description": "view slots",
            "re_description": "remove emoji",
            "emoji_added": "yay! added {emoji} (`:{name}:`) to the collection! 🎨✨",
            "server_full": "oh no! the café is full! we hit the limit of {limit} emojis 🥐☕",
            "no_perms": "i don't have the keys to the emoji cabinet! (need permissions) 🗝️🍰",
            "error": "something went wrong in the kitchen: {error} 🥘💨",
            "not_found": "i couldn't find that emoji! did you send the full code? (like `<:name:id>`) 🔍🥐",
            "timeout": "too slow, bestie! the milk went cold. try again! ☕💤",
            "invalid_name": "that name doesn't look right! keep it alphanumeric and cute (2-32 chars) ✨🥨",
            "no_emojis": "the emoji tray is empty! let's add some treats 🥐✨"
        },
        "de": {
            "emojimanager_title": "Nikos Emoji-Atelier 🎨✨️",
            "emojimanager_description": "verwalte die Ästhetik deines Cafés!",
            "steal_description": "stiehl ein Emoji",
            "sm_description": "stiehl viele Emojis",
            "surl_description": "von URL hinzufügen",
            "enlarge_description": "Emoji groß anzeigen",
            "emojistats_description": "Emoji-Slots ansehen",
            "re_description": "Emoji entfernen",
            "emoji_added": "yay! {emoji} (`:{name}:`) zur Sammlung hinzugefügt! 🎨✨",
            "server_full": "oh nein! das Café ist voll! wir haben das Limit von {limit} Emojis erreicht 🥐☕",
            "no_perms": "ich habe die Schlüssel zum Emoji-Schrank nicht! (Berechtigungen fehlen) 🗝️🍰",
            "error": "in der Küche ist etwas schiefgelaufen: {error} 🥘💨",
            "not_found": "ich konnte das Emoji nicht finden! hast du den vollen Code gesendet? (wie `<:name:id>`) 🔍🥐",
            "timeout": "zu langsam! die Milch ist kalt geworden. versuch es nochmal! ☕💤",
            "invalid_name": "der Name sieht nicht richtig aus! mach ihn alphanumerisch und süß (2-32 Zeichen) ✨🥨",
            "no_emojis": "das Emoji-Tablett ist leer! lass uns ein paar Leckereien hinzufügen 🥐✨"
        },
        "es": {
            "emojimanager_title": "Estudio de Emojis de Niko 🎨✨",
            "emojimanager_description": "¡gestiona la estética de tu café!",
            "steal_description": "robar un emoji",
            "sm_description": "robar varios emojis",
            "surl_description": "añadir desde URL",
            "enlarge_description": "ver emoji grande",
            "emojistats_description": "ver espacios",
            "re_description": "quitar emoji",
            "emoji_added": "¡yay! {emoji} (`:{name}:`) añadido a la colección 🎨✨",
            "server_full": "¡oh no! ¡el café está lleno! llegamos al límite de {limit} emojis 🥐☕",
            "no_perms": "¡no tengo las llaves del armario de emojis! (faltan permisos) 🗝️🍰",
            "error": "algo salió mal en la cocina: {error} 🥘💨",
            "not_found": "¡no encontré ese emoji! ¿enviaste el código completo? (como `<:nombre:id>`) 🔍🥐",
            "timeout": "¡muy lento, amix! la leche se enfrió. ¡prueba otra vez! ☕💤",
            "invalid_name": "¡ese nombre no se ve bien! mantenlo alfanumérico y bonito (2-32 caracteres) ✨🥨",
            "no_emojis": "¡la bandeja de emojis está vacía! añadamos algunas delicias 🥐✨"
        }
    }
}

msg = make_msg(MESSAGES)

EMOJI_REGEX = re.compile(r"<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]+):(?P<id>[0-9]+)>")
URL_REGEX = re.compile(r"https?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

# Prefix resolver (required for dynamic prefixes to work)
async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    """
    Resolve the primary prefix for the current context/interaction.

    Supports:
    - Static string prefix
    - Static list/tuple of prefixes
    - Dynamic prefix function: command_prefix(bot, message) -> list[str]
    """
    raw = bot.command_prefix

    # Static prefix (string)
    if isinstance(raw, str):
        return raw

    # Static list/tuple of prefixes
    if isinstance(raw, (list, tuple)):
        return raw[0]

    # Dynamic prefix function
    try:
        # Context: has .message
        msg = getattr(ctx_or_interaction, "message", None)

        # Interaction: use the original message if present
        if msg is None and isinstance(ctx_or_interaction, discord.Interaction):
            msg = ctx_or_interaction.message

        if msg is None:
            return "!"

        prefixes = raw(bot, msg)
        if isinstance(prefixes, (list, tuple)) and prefixes:
            return prefixes[0]
    except Exception:
        pass

    # Fallback prefix if everything else fails
    return "."

class EmojiManagerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        await self.session.close()

    def get_prefix(self, ctx):
        if isinstance(self.bot.command_prefix, list):
            return self.bot.command_prefix[0]
        return self.bot.command_prefix

    async def _get_emoji_info(self, emoji_string: str):
        match = EMOJI_REGEX.match(emoji_string)
        if not match:
            return None, None, None, None 

        emoji_id = match.group("id")
        emoji_name = match.group("name")
        animated = bool(match.group("animated"))
        url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{'gif' if animated else 'png'}"

        try:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    return emoji_name, image_data, animated, url
        except:
            pass
        return emoji_name, None, animated, None

    async def _add_emoji(self, ctx, name, image_data):
        try:
            guild = ctx.guild
            if len(guild.emojis) >= guild.emoji_limit:
                await ctx.send(msg(ctx, "server_full", limit=guild.emoji_limit))
                return False

            new_emoji = await guild.create_custom_emoji(name=name, image=image_data)
            await ctx.send(msg(ctx, "emoji_added", emoji=str(new_emoji), name=new_emoji.name))
            return True
        except discord.Forbidden:
            await ctx.send(msg(ctx, "no_perms"))
        except Exception as e:
            await ctx.send(msg(ctx, "error", error=str(e)))
        return False

    @commands.command(name="emojimanager", aliases=["em"], help="{ 'en': 'show emoji helper menu 🎨✨', 'de': 'zeige das Emoji-Hilfemenü' }")
    async def emojimanager_help(self, ctx):
        prefix = await _resolve_prefix(self.bot, ctx)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=f"### {msg(ctx, 'emojimanager_title')}"
                ),
                discord.ui.TextDisplay(
                    content=f"-# {msg(ctx, 'emojimanager_description')}"
                ),
                accessory=discord.ui.Thumbnail(self.bot.user.avatar.url)
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )
        
        commands_list = [
            (f"{prefix}steal <emoji>", f"{msg(ctx, 'steal_description')}"),
            (f"{prefix}sm <emojis...>", f"{msg(ctx, 'sm_description')}"),
            (f"{prefix}surl <url> [name]", f"{msg(ctx, 'surl_description')}"),
            (f"{prefix}enlarge <emoji>", f"{msg(ctx, 'enlarge_description')}"),
            (f"{prefix}emojistats", f"{msg(ctx, 'emojistats_description')}"),
            (f"{prefix}re <emoji>", f"{msg(ctx, 're_description')}")
        ]
        for cmd, desc in commands_list:
            container.add_item(
                discord.ui.TextDisplay(
                    content=f"**`{cmd}`**\n{desc}"
                )
            )
        view.add_item(container)
        await ctx.send(view=view)

    @commands.command(name="steal", help="{ 'en': 'steal a cute emoji 🎨✨', 'de': 'stiehl ein süßes Emoji' }")
    @has_permissions(manage_guild=True)
    async def steal_emoji(self, ctx, emoji_string: str):
        await ctx.typing()
        name, image_data, animated, url = await self._get_emoji_info(emoji_string)
        if not image_data:
            return await ctx.send(msg(ctx, "not_found"))
        await self._add_emoji(ctx, name, image_data)

    @commands.command(name="steal-multiple", aliases=["sm", "stealall"], help="{ 'en': 'steal many cute emojis 🎨✨', 'de': 'stiehl viele süße Emojis' }")
    @has_permissions(manage_guild=True)
    async def steal_multiple_emojis(self, ctx, *emoji_strings: str):
        if not emoji_strings:
            return await ctx.send(msg(ctx, "not_found"))
        await ctx.typing()
        added = []
        for s in emoji_strings:
            name, data, _, _ = await self._get_emoji_info(s)
            if data and await self._add_emoji(ctx, name, data):
                added.append(name)
        if added:
            log.success("Emoji", f"Stole {len(added)} emojis in {ctx.guild.name}")

    @commands.command(name="steal-from-url", aliases=["surl"], help="{ 'en': 'add emoji from a link 🔗✨', 'de': 'Emoji von einem Link hinzufügen' }")
    @has_permissions(manage_guild=True)
    async def steal_from_url(self, ctx, url: str, name: Optional[str] = None):
        if not URL_REGEX.match(url):
            return await ctx.send(msg(ctx, "error", error="Invalid URL"))
        await ctx.typing()
        try:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    if not name:
                        name = url.split('/')[-1].split('.')[0] or "emoji"
                    await self._add_emoji(ctx, name, data)
                else:
                    await ctx.send(msg(ctx, "error", error="Download failed"))
        except Exception as e:
            await ctx.send(msg(ctx, "error", error=str(e)))

    @commands.command(name="enlarge", help="{ 'en': 'see an emoji in big size 🔍✨', 'de': 'sieh ein Emoji in groß an' }")
    async def enlarge_emoji(self, ctx, emoji_string: str):
        name, data, _, url = await self._get_emoji_info(emoji_string)
        if not url:
            return await ctx.send(msg(ctx, "not_found"))
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### 🔍 :{name}:"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=url
                )
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

    @commands.command(name="emojistats", help="{ 'en': 'check how many treats you can add 📊✨', 'de': 'sieh nach, wie viele Emojis noch passen' }")
    async def emoji_stats(self, ctx):
        guild = ctx.guild
        static = len([e for e in guild.emojis if not e.animated])
        animated = len([e for e in guild.emojis if e.animated])
        limit = guild.emoji_limit
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### Emoji Pantry 📊✨️"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"**Static**\n{static}/{limit} 🥐\n**Animated**\n{animated}/{limit} ☕️"
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

    @commands.command(name="remove-emoji", aliases=["re"], help="{ 'en': 'remove a treat from the server 🗑️', 'de': 'entferne ein Emoji vom Server' }")
    @has_permissions(manage_guild=True)
    async def remove_emoji(self, ctx, emoji: discord.Emoji):
        try:
            name = emoji.name
            await emoji.delete()
            await ctx.send(f"🗑️ removed `:{name}:` from the tray!")
        except:
            await ctx.send(msg(ctx, "no_perms"))

async def setup(bot):
    await bot.add_cog(EmojiManagerCog(bot))
