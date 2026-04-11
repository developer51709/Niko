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
from utils.ai_config import get_ai_config

# personality mode: "normal" or "cafe"
PERSONALITY = "cafe"

MESSAGES = {
    "normal": {
        "en": {
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
            "emoji_added": "Emoji erfolgreich hinzugefügt: {emoji} (`:{name}:`)",
            "server_full": "Dieser Server hat das Limit von {limit} Emojis erreicht.",
            "no_perms": "Ich habe keine Berechtigung, Emojis zu verwalten.",
            "error": "Ein Fehler ist aufgetreten: {error}",
            "not_found": "Emoji konnte nicht gefunden oder heruntergeladen werden. Bitte gib den vollständigen Emoji-String an (z.B. `<:name:id>`).",
            "timeout": "Zeit abgelaufen. Vorgang abgebrochen.",
            "invalid_name": "Ungültiger Name. Bitte nutze alphanumerische Zeichen (2-32 Zeichen).",
            "no_emojis": "Dieser Server hat keine benutzerdefinierten Emojis."
        }
    },
    "cafe": {
        "en": {
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
            "emoji_added": "yay! {emoji} (`:{name}:`) zur Sammlung hinzugefügt! 🎨✨",
            "server_full": "oh nein! das Café ist voll! wir haben das Limit von {limit} Emojis erreicht 🥐☕",
            "no_perms": "ich habe die Schlüssel zum Emoji-Schrank nicht! (Berechtigungen fehlen) 🗝️🍰",
            "error": "in der Küche ist etwas schiefgelaufen: {error} 🥘💨",
            "not_found": "ich konnte das Emoji nicht finden! hast du den vollen Code gesendet? (wie `<:name:id>`) 🔍🥐",
            "timeout": "zu langsam! die Milch ist kalt geworden. versuch es nochmal! ☕💤",
            "invalid_name": "der Name sieht nicht richtig aus! mach ihn alphanumerisch und süß (2-32 Zeichen) ✨🥨",
            "no_emojis": "das Emoji-Tablett ist leer! lass uns ein paar Leckereien hinzufügen 🥐✨"
        }
    }
}

def get_lang(ctx):
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
    return "en"

def get_personality(ctx):
    if ctx and ctx.guild:
        guild_id = ctx.guild.id
        personality = get_ai_config(guild_id, "personality")
        if personality:
            return personality
    return PERSONALITY if PERSONALITY in MESSAGES else "normal"

def msg(ctx, key, **kwargs):
    personality = get_personality(ctx)
    lang = get_lang(ctx)
    text = MESSAGES.get(personality, {}).get(lang, {}).get(key)
    if text is None:
        text = MESSAGES["normal"].get(lang, {}).get(key, key)
    return text.format(**kwargs) if kwargs else text

EMOJI_REGEX = re.compile(r"<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]+):(?P<id>[0-9]+)>")
URL_REGEX = re.compile(r"https?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

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

    @commands.command(name="emojimanager", aliases=["em"], help="show emoji helper menu 🎨✨ | zeige das Emoji-Hilfemenü")
    async def emojimanager_help(self, ctx):
        prefix = self.get_prefix(ctx)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content="### Niko's Emoji Studio 🎨✨"
                ),
                discord.ui.TextDisplay(
                    content="-# manage your café's aesthetics! | verwalte die Ästhetik deines Cafés!"
                ),
                accessory=discord.ui.Thumbnail(self.bot.user.avatar.url)
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )
        
        commands_list = [
            (f"{prefix}steal <emoji>", "steal an emoji | stiehl ein Emoji"),
            (f"{prefix}sm <emojis...>", "steal many emojis | stiehl viele Emojis"),
            (f"{prefix}surl <url> [name]", "add from url | von URL hinzufügen"),
            (f"{prefix}enlarge <emoji>", "big emoji view | Emoji groß anzeigen"),
            (f"{prefix}emojistats", "view slots | Emoji-Slots ansehen"),
            (f"{prefix}re <emoji>", "remove emoji | Emoji entfernen")
        ]
        for cmd, desc in commands_list:
            container.add_item(
                discord.ui.TextDisplay(
                    content=f"**`{cmd}`**\n{desc}"
                )
            )
        view.add_item(container)
        await ctx.send(view=view)

    @commands.command(name="steal", help="steal a cute emoji 🎨✨ | stiehl ein süßes Emoji")
    @has_permissions(manage_guild=True)
    async def steal_emoji(self, ctx, emoji_string: str):
        await ctx.typing()
        name, image_data, animated, url = await self._get_emoji_info(emoji_string)
        if not image_data:
            return await ctx.send(msg(ctx, "not_found"))
        await self._add_emoji(ctx, name, image_data)

    @commands.command(name="steal-multiple", aliases=["sm", "stealall"], help="steal many cute emojis 🎨✨ | stiehl viele süße Emojis")
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

    @commands.command(name="steal-from-url", aliases=["surl"], help="add emoji from a link 🔗✨ | Emoji von einem Link hinzufügen")
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

    @commands.command(name="enlarge", help="see an emoji in big size 🔍✨ | sieh ein Emoji in groß an")
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

    @commands.command(name="emojistats", help="check how many treats you can add 📊✨ | sieh nach, wie viele Emojis noch passen")
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

    @commands.command(name="remove-emoji", aliases=["re"], help="remove a treat from the server 🗑️ | entferne ein Emoji vom Server")
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
