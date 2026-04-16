# snipe.py
# Stores the last 10 deleted messages per channel and lets users view them
# with a paginated cv2 LayoutView (one message per page, author avatar per page).

import discord
from discord.ext import commands
from datetime import datetime, timezone
from utils.ai_config import get_personality

MAX_HISTORY = 10   # deleted messages kept per channel
MAX_CONTENT = 900  # characters shown before truncation

MESSAGES = {
    "normal": {
        "en": {
            "empty":     "No recently deleted messages in this channel.",
            "header":    "Sniped Message",
            "no_text":   "*(no text content)*",
            "attach":    "📎 {n} attachment(s)",
            "footer":    "Deleted message {cur} of {total}",
            "sticker":   "🎟️ Sticker: {name}",
            "embed_msg": "*(had an embed)*",
        },
        "de": {
            "empty":     "Keine kürzlich gelöschten Nachrichten in diesem Kanal.",
            "header":    "Abgefangene Nachricht",
            "no_text":   "*(kein Textinhalt)*",
            "attach":    "📎 {n} Anhang/Anhänge",
            "footer":    "Gelöschte Nachricht {cur} von {total}",
            "sticker":   "🎟️ Aufkleber: {name}",
            "embed_msg": "*(hatte einen Embed)*",
        },
    },
    "cafe": {
        "en": {
            "empty":     "nothing was deleted here recently — the café is clean ☕✨",
            "header":    "☕ sniped message",
            "no_text":   "*(they said nothing, just silence ☕)*",
            "attach":    "📎 {n} attachment(s) — gone like last night's pastries 🥐",
            "footer":    "deleted message {cur} of {total} · gone but not forgotten ☕",
            "sticker":   "🎟️ sticker: {name}",
            "embed_msg": "*(had an embed — the mystery deepens ☕)*",
        },
        "de": {
            "empty":     "hier wurde kürzlich nichts gelöscht — das café ist sauber ☕✨",
            "header":    "☕ abgefangene nachricht",
            "no_text":   "*(sie haben nichts gesagt, nur stille ☕)*",
            "attach":    "📎 {n} anhang/anhänge — weg wie gestern das gebäck 🥐",
            "footer":    "gelöschte nachricht {cur} von {total} · weg, aber nicht vergessen ☕",
            "sticker":   "🎟️ aufkleber: {name}",
            "embed_msg": "*(hatte einen embed — das rätsel vertieft sich ☕)*",
        },
    },
}


def get_lang(ctx: commands.Context) -> str:
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
    return "en"


def msg_raw(ctx, key: str, **kwargs) -> str:
    p = get_personality(ctx)
    base = MESSAGES.get(p, {})
    text = base.get(get_lang(ctx), {}).get(key)
    if text is None:
        text = base.get("en", {}).get(key)
    if text is None:
        text = MESSAGES["normal"].get(ctx.lang, {}).get(key)
    if text is None:
        text = MESSAGES["normal"]["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text


# ───────────────────────────────────────────────────
#  PAGINATED SNIPE VIEW
# ───────────────────────────────────────────────────

class _SnipePrev(discord.ui.Button):
    def __init__(self, disabled: bool):
        super().__init__(label="◀", style=discord.ButtonStyle.secondary, disabled=disabled)

    async def callback(self, interaction: discord.Interaction):
        v: SnipeView = self.view
        v.page -= 1
        v._build()
        await interaction.response.edit_message(view=v)


class _SnipeIndicator(discord.ui.Button):
    def __init__(self, label: str):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, disabled=True)

    async def callback(self, interaction: discord.Interaction):
        pass


class _SnipeNext(discord.ui.Button):
    def __init__(self, disabled: bool):
        super().__init__(label="▶", style=discord.ButtonStyle.secondary, disabled=disabled)

    async def callback(self, interaction: discord.Interaction):
        v: SnipeView = self.view
        v.page += 1
        v._build()
        await interaction.response.edit_message(view=v)


class SnipeView(discord.ui.LayoutView):
    """
    One page = one deleted message.
    Pages run newest-first so page 0 is the most recently deleted.
    """

    def __init__(self, entries: list[dict], ctx, timeout: float = 120):
        super().__init__(timeout=timeout)
        self.entries = entries
        self.ctx = ctx
        self.page = 0
        self._build()

    def _build(self):
        self.clear_items()
        total = len(self.entries)
        e = self.entries[self.page]

        # ── assemble body text ─────────────────────
        content = e.get("content", "").strip()
        if not content and e.get("has_embeds"):
            content = msg_raw(self.ctx, "embed_msg")
        if not content:
            content = msg_raw(self.ctx, "no_text")
        elif len(content) > MAX_CONTENT:
            content = content[:MAX_CONTENT] + "…"

        # Stickers
        sticker_lines = [
            msg_raw(self.ctx, "sticker", name=s)
            for s in e.get("stickers", [])
        ]
        if sticker_lines:
            content += "\n" + "\n".join(sticker_lines)

        # Attachments note
        attach_count = e.get("attachment_count", 0)
        if attach_count:
            content += "\n" + msg_raw(self.ctx, "attach", n=attach_count)

        # Timestamp
        ts: datetime = e["deleted_at"]
        ts_str = f"<t:{int(ts.timestamp())}:R>"

        header = msg_raw(self.ctx, "header")
        footer = msg_raw(self.ctx, "footer", cur=self.page + 1, total=total)

        body = (
            f"### {header}\n"
            f"**{e['author_name']}** • {ts_str}\n"
            f"{content}"
        )

        # ── build cv2 container ────────────────────
        avatar = e.get("author_avatar")
        if avatar:
            inner = discord.ui.Section(
                discord.ui.TextDisplay(content=body),
                accessory=discord.ui.Thumbnail(avatar),
            )
        else:
            inner = discord.ui.TextDisplay(content=body)

        container = discord.ui.Container(
            inner,
            discord.ui.TextDisplay(content=f"-# {footer}"),
        )

        # ── navigation row (only when >1 page) ─────
        if total > 1:
            container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
            container.add_item(discord.ui.ActionRow(
                _SnipePrev(disabled=self.page == 0),
                _SnipeIndicator(label=f"{self.page + 1} / {total}"),
                _SnipeNext(disabled=self.page == total - 1),
            ))

        # ── attachment images (first page only to avoid spam) ──
        first_image = e.get("first_image_url")
        if first_image:
            container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
            container.add_item(discord.ui.MediaGallery(
                discord.MediaGalleryItem(media=first_image)
            ))
        self.add_item(container)


# ───────────────────────────────────────────────────
#  COG
# ───────────────────────────────────────────────────

class Snipe(commands.Cog):
    """Stores recently deleted messages and lets users snipe them."""

    def __init__(self, bot):
        self.bot = bot
        # {channel_id: [entry, ...]}  newest-first, max MAX_HISTORY entries
        self._history: dict[int, list[dict]] = {}

    # ── listener ───────────────────────────────────

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        # Skip bot messages and DMs
        if message.author.bot or not message.guild:
            return

        entry = {
            "author_name":    message.author.mention,
            "author_avatar":  str(message.author.display_avatar.url),
            "content":        message.content or "",
            "has_embeds":     bool(message.embeds),
            "attachment_count": len(message.attachments),
            "first_image_url": next(
                (
                    a.url for a in message.attachments
                    if a.content_type and a.content_type.startswith("image/")
                ),
                None,
            ),
            "stickers": [s.name for s in message.stickers],
            "deleted_at": datetime.now(tz=timezone.utc),
        }

        channel_id = message.channel.id
        history = self._history.setdefault(channel_id, [])
        history.insert(0, entry)   # newest first
        if len(history) > MAX_HISTORY:
            history.pop()

    # ── command ────────────────────────────────────

    @commands.command(
        name="snipe",
        aliases=["sn"],
        help="{ 'en': 'see recently deleted messages ☕🔍', 'de': 'sieh kürzlich gelöschte nachrichten' }"
    )
    async def snipe(self, ctx: commands.Context):
        """Show the last deleted messages in this channel."""
        history = self._history.get(ctx.channel.id, [])

        if not history:
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=msg_raw(ctx, "empty"))
            ))
            return await ctx.send(view=view)

        view = SnipeView(entries=history, ctx=ctx)
        await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())


async def setup(bot):
    await bot.add_cog(Snipe(bot))
