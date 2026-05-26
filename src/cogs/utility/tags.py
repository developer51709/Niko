"""
Tags — server-specific custom commands / quick-replies.

Commands (single `tag` group):
    tag show <name>          — show a tag (also: just `<prefix>name`)
    tag create <name> <text> — create a new tag (anyone)
    tag edit <name> <text>   — edit a tag (owner or manage_messages)
    tag delete <name>        — delete a tag (owner or manage_messages)
    tag list                 — list all tags in this server
    tag info <name>          — show metadata about a tag
    tag raw <name>           — show the raw markdown
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict

import discord
from discord.ext import commands

from config.emojis import get_emoji
from utils.ai_config import get_personality
from utils.paginator import paginate, PaginatedView

DATA_FILE = "data/tags.json"
MAX_TAGS_PER_GUILD = 500
MAX_TAG_LEN = 1900


MESSAGES = {
    "normal": {
        "en": {
            "created":      "✅ Tag **{name}** created.",
            "edited":       "✅ Tag **{name}** edited.",
            "deleted":      "✅ Tag **{name}** deleted.",
            "exists":       "⚠️ A tag named **{name}** already exists.",
            "missing":      "⚠️ No tag named **{name}** in this server.",
            "no_perm":      "❌ You can only edit or delete your own tags (unless you have manage_messages).",
            "list_empty":   "No tags in this server yet.",
            "list_title":   "### {icon} Tags ({n})",
            "info":         "### {icon} Tag `{name}`\n**Owner:** {owner}\n**Uses:** {uses}\n**Created:** <t:{created}:R>",
            "raw_title":    "### Raw `{name}`",
            "limit_hit":    "⚠️ This server already has {max} tags — delete some before creating more.",
            "too_long":     "⚠️ Tag content must be ≤ {n} characters.",
        },
        "de": {
            "created":      "✅ Tag **{name}** erstellt.",
            "edited":       "✅ Tag **{name}** bearbeitet.",
            "deleted":      "✅ Tag **{name}** gelöscht.",
            "exists":       "⚠️ Ein Tag namens **{name}** existiert bereits.",
            "missing":      "⚠️ Kein Tag namens **{name}** auf diesem Server.",
            "no_perm":      "❌ Du kannst nur eigene Tags bearbeiten oder löschen (außer du hast manage_messages).",
            "list_empty":   "Noch keine Tags auf diesem Server.",
            "list_title":   "### {icon} Tags ({n})",
            "info":         "### {icon} Tag `{name}`\n**Besitzer:** {owner}\n**Benutzungen:** {uses}\n**Erstellt:** <t:{created}:R>",
            "raw_title":    "### Roh `{name}`",
            "limit_hit":    "⚠️ Dieser Server hat bereits {max} Tags — lösche einige, bevor du neue erstellst.",
            "too_long":     "⚠️ Tag-Inhalt muss ≤ {n} Zeichen sein.",
        },
        "es": {
            "created":      "✅ Tag **{name}** creado.",
            "edited":       "✅ Tag **{name}** editado.",
            "deleted":      "✅ Tag **{name}** eliminado.",
            "exists":       "⚠️ Ya existe un tag llamado **{name}**.",
            "missing":      "⚠️ No hay un tag llamado **{name}** en este servidor.",
            "no_perm":      "❌ Solo puedes editar o eliminar tus propios tags (a menos que tengas manage_messages).",
            "list_empty":   "Aún no hay tags en este servidor.",
            "list_title":   "### {icon} Tags ({n})",
            "info":         "### {icon} Tag `{name}`\n**Dueño:** {owner}\n**Usos:** {uses}\n**Creado:** <t:{created}:R>",
            "raw_title":    "### Raw `{name}`",
            "limit_hit":    "⚠️ Este servidor ya tiene {max} tags — elimina algunos antes de crear más.",
            "too_long":     "⚠️ El contenido del tag debe ser ≤ {n} caracteres.",
        },
    },
    "cafe": {
        "en": {
            "created":      "✅ pinned tag **{name}** to the menu ☕",
            "edited":       "✅ rewrote tag **{name}** in nicer handwriting ✨",
            "deleted":      "✅ tag **{name}** wiped off the chalkboard ☕",
            "exists":       "⚠️ tag **{name}** is already on the menu ☕",
            "missing":      "⚠️ no tag **{name}** here, sweet bean ☕",
            "no_perm":      "❌ you can only mess with your own tags ☕",
            "list_empty":   "no tags yet — the chalkboard is empty ☕",
            "list_title":   "### {icon} café tags ({n}) ☕",
            "info":         "### {icon} tag `{name}` ☕\n**owner:** {owner}\n**sips:** {uses}\n**brewed:** <t:{created}:R>",
            "raw_title":    "### raw `{name}` ☕",
            "limit_hit":    "⚠️ chalkboard is full — {max} tags max, please erase some ☕",
            "too_long":     "⚠️ that's a bit long — keep it under {n} characters ☕",
        },
        "de": {
            "created":      "✅ tag **{name}** an die karte gepinnt ☕",
            "edited":       "✅ tag **{name}** in schönerer schrift neu geschrieben ✨",
            "deleted":      "✅ tag **{name}** von der tafel gewischt ☕",
            "exists":       "⚠️ tag **{name}** steht schon auf der karte ☕",
            "missing":      "⚠️ kein tag **{name}** hier, süßer ☕",
            "no_perm":      "❌ du kannst nur deine eigenen tags bearbeiten ☕",
            "list_empty":   "noch keine tags — die tafel ist leer ☕",
            "list_title":   "### {icon} café-tags ({n}) ☕",
            "info":         "### {icon} tag `{name}` ☕\n**besitzer:** {owner}\n**schlucke:** {uses}\n**gebraut:** <t:{created}:R>",
            "raw_title":    "### roh `{name}` ☕",
            "limit_hit":    "⚠️ tafel ist voll — max {max} tags, bitte einige wischen ☕",
            "too_long":     "⚠️ ein bisschen lang — bleib unter {n} zeichen ☕",
        },
        "es": {
            "created":      "✅ tag **{name}** colgado en la pizarra ☕",
            "edited":       "✅ tag **{name}** reescrito con mejor letra ✨",
            "deleted":      "✅ tag **{name}** borrado de la pizarra ☕",
            "exists":       "⚠️ el tag **{name}** ya está en la pizarra ☕",
            "missing":      "⚠️ no hay tag **{name}** aquí, cariño ☕",
            "no_perm":      "❌ solo puedes editar tus propios tags ☕",
            "list_empty":   "no hay tags aún — la pizarra está vacía ☕",
            "list_title":   "### {icon} tags del café ({n}) ☕",
            "info":         "### {icon} tag `{name}` ☕\n**dueño:** {owner}\n**sorbos:** {uses}\n**preparado:** <t:{created}:R>",
            "raw_title":    "### crudo `{name}` ☕",
            "limit_hit":    "⚠️ pizarra llena — máximo {max} tags, borra algunos ☕",
            "too_long":     "⚠️ un poco largo — mantenlo bajo {n} caracteres ☕",
        },
    },
}


def _lang(ctx) -> str:
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        l = str(ctx.guild.preferred_locale).lower()
        if l.startswith("de"): return "de"
        if l.startswith("es"): return "es"
    return "en"


def msg(ctx, key: str, **kw) -> str:
    p = get_personality(ctx) if isinstance(ctx, commands.Context) else "cafe"
    lang = _lang(ctx)
    table = MESSAGES.get(p, MESSAGES["normal"])
    text = table.get(lang, {}).get(key) or table.get("en", {}).get(key) or MESSAGES["normal"]["en"].get(key, key)
    return text.format(**kw) if kw else text


def cv2(text: str) -> discord.ui.LayoutView:
    v = discord.ui.LayoutView()
    v.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
    return v


# ───────────────────────────────────────────────────
#  STORAGE
# ───────────────────────────────────────────────────

def _load() -> Dict[str, Dict[str, dict]]:
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save(d: dict):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)


# ───────────────────────────────────────────────────
#  COG
# ───────────────────────────────────────────────────

class Tags(commands.Cog):
    """Custom server tags — quick text snippets keyed by name."""

    def __init__(self, bot):
        self.bot = bot
        self.data: Dict[str, Dict[str, dict]] = _load()

    def _gtags(self, gid: int) -> Dict[str, dict]:
        return self.data.setdefault(str(gid), {})

    @commands.hybrid_group(
        name="tag",
        description="Server tag system.",
        help="{ 'en': 'Server tag system: create, edit, delete, list, show.', 'de': 'Server-Tag-System: erstellen, bearbeiten, löschen, anzeigen.', 'es': 'Sistema de tags del servidor: crear, editar, eliminar, listar, mostrar.' }",
        invoke_without_command=True,
    )
    @commands.guild_only()
    async def tag(self, ctx: commands.Context, *, name: str = None):
        if name:
            return await self._show(ctx, name)
        await ctx.send_help(self.tag)

    @tag.command(
        name="show",
        description="Show a tag's content.",
        help="{ 'en': 'Show a tag.', 'de': 'Einen Tag anzeigen.', 'es': 'Muestra un tag.' }",
    )
    async def tag_show(self, ctx: commands.Context, *, name: str):
        await self._show(ctx, name)

    async def _show(self, ctx: commands.Context, name: str):
        tags = self._gtags(ctx.guild.id)
        t = tags.get(name.lower())
        if not t:
            return await ctx.send(view=cv2(msg(ctx, "missing", name=name)))
        t["uses"] = int(t.get("uses", 0)) + 1
        _save(self.data)
        await ctx.send(view=cv2(t["content"]))

    @tag.command(
        name="create",
        description="Create a new tag.",
        help="{ 'en': 'Create a new tag.', 'de': 'Einen neuen Tag erstellen.', 'es': 'Crea un nuevo tag.' }",
    )
    async def tag_create(self, ctx: commands.Context, name: str, *, content: str):
        tags = self._gtags(ctx.guild.id)
        if len(tags) >= MAX_TAGS_PER_GUILD:
            return await ctx.send(view=cv2(msg(ctx, "limit_hit", max=MAX_TAGS_PER_GUILD)))
        if len(content) > MAX_TAG_LEN:
            return await ctx.send(view=cv2(msg(ctx, "too_long", n=MAX_TAG_LEN)))
        key = name.lower()[:50]
        if key in tags:
            return await ctx.send(view=cv2(msg(ctx, "exists", name=name)))
        tags[key] = {
            "name": key,
            "content": content,
            "owner_id": ctx.author.id,
            "created_at": int(datetime.now(timezone.utc).timestamp()),
            "uses": 0,
        }
        _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "created", name=key)))

    @tag.command(
        name="edit",
        description="Edit a tag you own.",
        help="{ 'en': 'Edit a tag you own.', 'de': 'Einen eigenen Tag bearbeiten.', 'es': 'Edita un tag que te pertenece.' }",
    )
    async def tag_edit(self, ctx: commands.Context, name: str, *, content: str):
        tags = self._gtags(ctx.guild.id)
        t = tags.get(name.lower())
        if not t:
            return await ctx.send(view=cv2(msg(ctx, "missing", name=name)))
        if t["owner_id"] != ctx.author.id and not ctx.author.guild_permissions.manage_messages:
            return await ctx.send(view=cv2(msg(ctx, "no_perm")))
        if len(content) > MAX_TAG_LEN:
            return await ctx.send(view=cv2(msg(ctx, "too_long", n=MAX_TAG_LEN)))
        t["content"] = content
        _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "edited", name=name.lower())))

    @tag.command(
        name="delete",
        description="Delete a tag.",
        help="{ 'en': 'Delete a tag you own.', 'de': 'Einen eigenen Tag löschen.', 'es': 'Elimina un tag que te pertenece.' }",
    )
    async def tag_delete(self, ctx: commands.Context, *, name: str):
        tags = self._gtags(ctx.guild.id)
        t = tags.get(name.lower())
        if not t:
            return await ctx.send(view=cv2(msg(ctx, "missing", name=name)))
        if t["owner_id"] != ctx.author.id and not ctx.author.guild_permissions.manage_messages:
            return await ctx.send(view=cv2(msg(ctx, "no_perm")))
        tags.pop(name.lower(), None)
        _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "deleted", name=name.lower())))

    @tag.command(
        name="list",
        description="List all tags in this server.",
        help="{ 'en': 'List all tags in this server.', 'de': 'Alle Tags auf diesem Server anzeigen.', 'es': 'Lista todos los tags de este servidor.' }",
    )
    async def tag_list(self, ctx: commands.Context):
        tags = self._gtags(ctx.guild.id)
        if not tags:
            return await ctx.send(view=cv2(msg(ctx, "list_empty")))
        sorted_t = sorted(tags.values(), key=lambda x: x["name"])
        lines = [f"• `{t['name']}` · -# uses: {t.get('uses', 0)}" for t in sorted_t]
        title = msg(ctx, "list_title", icon=get_emoji("icon_message"), n=len(sorted_t))
        if len(lines) <= 20:
            body = title + "\n" + "\n".join(lines)
            return await ctx.send(view=cv2(body))
        pages = paginate(lines, per_page=20)
        # prepend title to each page
        pages = [title + "\n" + p for p in pages]
        view = PaginatedView(title=msg(ctx, "list_title", icon=get_emoji("icon_message"), n=len(sorted_t)),
                             pages=pages, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        await ctx.send(view=view)

    @tag.command(
        name="info",
        description="Show metadata about a tag.",
        help="{ 'en': 'Show metadata about a tag.', 'de': 'Metadaten zu einem Tag anzeigen.', 'es': 'Muestra metadatos de un tag.' }",
    )
    async def tag_info(self, ctx: commands.Context, *, name: str):
        tags = self._gtags(ctx.guild.id)
        t = tags.get(name.lower())
        if not t:
            return await ctx.send(view=cv2(msg(ctx, "missing", name=name)))
        owner = ctx.guild.get_member(t["owner_id"])
        owner_str = owner.mention if owner else f"<@{t['owner_id']}>"
        body = msg(ctx, "info",
                   icon=get_emoji("icon_message"), name=t["name"],
                   owner=owner_str, uses=t.get("uses", 0), created=t.get("created_at", 0))
        await ctx.send(view=cv2(body))

    @tag.command(
        name="raw",
        description="Show the raw markdown of a tag.",
        help="{ 'en': 'Show the raw markdown of a tag.', 'de': 'Roh-Markdown eines Tags anzeigen.', 'es': 'Muestra el markdown crudo de un tag.' }",
    )
    async def tag_raw(self, ctx: commands.Context, *, name: str):
        tags = self._gtags(ctx.guild.id)
        t = tags.get(name.lower())
        if not t:
            return await ctx.send(view=cv2(msg(ctx, "missing", name=name)))
        body = msg(ctx, "raw_title", name=t["name"]) + f"\n```\n{t['content'][:1700]}\n```"
        await ctx.send(view=cv2(body))


async def setup(bot):
    await bot.add_cog(Tags(bot))
