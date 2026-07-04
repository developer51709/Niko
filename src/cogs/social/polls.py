"""
Polls — multi-option polls with live vote buttons.

Commands (single `poll` group):
    poll create <question> | <opt1> | <opt2> | …   — create a poll (≤10 opts)
    poll end <message_id>                          — end a poll early (creator/admin)
    poll results <message_id>                      — show final tally

Vote by pressing the corresponding button. Press again to remove your vote.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, List

import discord
from discord.ext import commands

from config.emojis import get_emoji
from utils.ai.config import get_personality
from utils.i18n import make_msg

DATA_FILE = "data/polls.json"
NUMBER_EMOJIS = [f"{get_emoji('number_zero')}", f"{get_emoji('number_one')}", f"{get_emoji('number_two')}", f"{get_emoji('number_three')}", f"{get_emoji('number_four')}", f"{get_emoji('number_five')}", f"{get_emoji('number_six')}", f"{get_emoji('number_seven')}", f"{get_emoji('number_eight')}", f"{get_emoji('number_nine')}"]


MESSAGES = {
    "normal": {
        "en": {
            "need_options":  "❌ Provide at least 2 options separated by `|`. Example: `poll create Best drink? | Coffee | Tea`.",
            "too_many":      "❌ Maximum of 10 options.",
            "title":         "### {icon} {question}",
            "vote_count":    "**{letter}** {opt} — `{count}` votes ({pct}%)",
            "footer_open":   "-# Click a button to vote · poll by {author}",
            "footer_closed": "-# Poll ended · created by {author}",
            "vote_added":    "✅ Voted for **{opt}**.",
            "vote_removed":  "✅ Vote removed.",
            "ended":         "✅ Poll ended.",
            "not_found":     "⚠️ No poll with that message ID found.",
            "not_owner":     "❌ Only the poll creator or an admin can do that.",
            "results_title": "### {icon} Final Results",
        },
        "de": {
            "need_options":  "❌ Mindestens 2 Optionen mit `|` getrennt angeben. Beispiel: `poll create Bestes Getränk? | Kaffee | Tee`.",
            "too_many":      "❌ Maximal 10 Optionen.",
            "title":         "### {icon} {question}",
            "vote_count":    "**{letter}** {opt} — `{count}` Stimmen ({pct}%)",
            "footer_open":   "-# Drücke einen Button zum Abstimmen · Umfrage von {author}",
            "footer_closed": "-# Umfrage beendet · erstellt von {author}",
            "vote_added":    "✅ Für **{opt}** gestimmt.",
            "vote_removed":  "✅ Stimme entfernt.",
            "ended":         "✅ Umfrage beendet.",
            "not_found":     "⚠️ Keine Umfrage mit dieser Nachrichten-ID gefunden.",
            "not_owner":     "❌ Nur der Ersteller oder ein Admin kann das.",
            "results_title": "### {icon} Endergebnisse",
        },
        "es": {
            "need_options":  "❌ Proporciona al menos 2 opciones separadas por `|`. Ejemplo: `poll create ¿Mejor bebida? | Café | Té`.",
            "too_many":      "❌ Máximo 10 opciones.",
            "title":         "### {icon} {question}",
            "vote_count":    "**{letter}** {opt} — `{count}` votos ({pct}%)",
            "footer_open":   "-# Pulsa un botón para votar · encuesta de {author}",
            "footer_closed": "-# Encuesta finalizada · creada por {author}",
            "vote_added":    "✅ Votaste por **{opt}**.",
            "vote_removed":  "✅ Voto eliminado.",
            "ended":         "✅ Encuesta finalizada.",
            "not_found":     "⚠️ No se encontró una encuesta con ese ID de mensaje.",
            "not_owner":     "❌ Solo el creador o un admin puede hacer esto.",
            "results_title": "### {icon} Resultados finales",
        },
    },
    "cafe": {
        "en": {
            "need_options":  "❌ at least 2 options please, separated by `|` ☕ — like `poll create best drink? | coffee | tea`",
            "too_many":      "❌ 10 options max, sweet bean ☕",
            "title":         "### {icon} {question} ☕",
            "vote_count":    "**{letter}** {opt} — `{count}` sips ({pct}%)",
            "footer_open":   "-# tap a button to vote · poll by {author} ☕✨",
            "footer_closed": "-# poll closed ☕ · by {author}",
            "vote_added":    "✅ vote tossed in for **{opt}** ☕",
            "vote_removed":  "✅ vote pulled back ☕",
            "ended":         "✅ poll closed cozily ☕",
            "not_found":     "⚠️ couldn't find that poll hun~",
            "not_owner":     "❌ only the poll creator or admins can do that ☕",
            "results_title": "### {icon} final tally ☕✨",
        },
        "de": {
            "need_options":  "❌ mindestens 2 optionen bitte, mit `|` getrennt ☕ — wie `poll create bestes getränk? | kaffee | tee`",
            "too_many":      "❌ max 10 optionen, süßer ☕",
            "title":         "### {icon} {question} ☕",
            "vote_count":    "**{letter}** {opt} — `{count}` schlucke ({pct}%)",
            "footer_open":   "-# tipp einen button zum abstimmen · umfrage von {author} ☕✨",
            "footer_closed": "-# umfrage geschlossen ☕ · von {author}",
            "vote_added":    "✅ stimme für **{opt}** rein ☕",
            "vote_removed":  "✅ stimme zurückgezogen ☕",
            "ended":         "✅ umfrage gemütlich geschlossen ☕",
            "not_found":     "⚠️ konnte die umfrage nicht finden hun~",
            "not_owner":     "❌ nur der ersteller oder admins können das ☕",
            "results_title": "### {icon} endabrechnung ☕✨",
        },
        "es": {
            "need_options":  "❌ al menos 2 opciones por favor, separadas por `|` ☕ — como `poll create ¿mejor bebida? | café | té`",
            "too_many":      "❌ máximo 10 opciones, cariño ☕",
            "title":         "### {icon} {question} ☕",
            "vote_count":    "**{letter}** {opt} — `{count}` sorbos ({pct}%)",
            "footer_open":   "-# pulsa un botón para votar · encuesta de {author} ☕✨",
            "footer_closed": "-# encuesta cerrada ☕ · por {author}",
            "vote_added":    "✅ voto echado por **{opt}** ☕",
            "vote_removed":  "✅ voto retirado ☕",
            "ended":         "✅ encuesta cerrada acogedoramente ☕",
            "not_found":     "⚠️ no encontré esa encuesta hun~",
            "not_owner":     "❌ solo el creador o admins pueden hacer eso ☕",
            "results_title": "### {icon} resultados finales ☕✨",
        },
    },
}


def _lang(ctx) -> str:
    g = getattr(ctx, "guild", None)
    if g and g.preferred_locale:
        l = str(g.preferred_locale).lower()
        if l.startswith("de"): return "de"
        if l.startswith("es"): return "es"
    return "en"


def _personality(ctx) -> str:
    if isinstance(ctx, commands.Context):
        return get_personality(ctx)
    class _S: pass
    s = _S()
    s.guild = getattr(ctx, "guild", None)
    return get_personality(s)


msg = make_msg(MESSAGES)


def _load() -> dict:
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
#  POLL VIEW
# ───────────────────────────────────────────────────

def _build_poll_text(poll: dict, ctx_like) -> str:
    title = msg(ctx_like, "title", icon=get_emoji("icon_lightbulb"), question=poll["question"])
    counts = [len(v) for v in poll["votes"]]
    total = sum(counts) or 1
    lines = []
    for i, opt in enumerate(poll["options"]):
        pct = round(counts[i] * 100 / total)
        lines.append(msg(ctx_like, "vote_count",
                         letter=NUMBER_EMOJIS[i], opt=opt,
                         count=counts[i], pct=pct))
    author = ctx_like.guild.get_member(poll["author_id"]) if ctx_like and ctx_like.guild else None
    author_str = author.mention if author else f"<@{poll['author_id']}>"
    footer_key = "footer_closed" if poll.get("closed") else "footer_open"
    footer = msg(ctx_like, footer_key, author=author_str)
    return title + "\n" + "\n".join(lines) + "\n\n" + footer


class _VoteButton(discord.ui.Button):
    def __init__(self, idx: int, poll_id: int, disabled: bool):
        super().__init__(
            label=NUMBER_EMOJIS[idx][0] if False else "",
            emoji=NUMBER_EMOJIS[idx],
            style=discord.ButtonStyle.secondary,
            custom_id=f"poll:{poll_id}:{idx}",
            disabled=disabled,
        )
        self.idx = idx
        self.poll_id = poll_id

    async def callback(self, interaction: discord.Interaction):
        cog: "Polls" = interaction.client.get_cog("Polls")
        if not cog:
            return
        poll = cog.polls.get(str(self.poll_id))
        if not poll or poll.get("closed"):
            return await interaction.response.send_message(msg(interaction, "ended"), ephemeral=True)
        uid = interaction.user.id
        # remove existing vote
        removed = False
        for vlist in poll["votes"]:
            if uid in vlist:
                vlist.remove(uid)
                removed = True
        added = False
        if not removed or self.idx not in [i for i, v in enumerate(poll["votes"]) if uid in v]:
            # toggle: if previous vote was a different option (or none), add to chosen idx
            if uid not in poll["votes"][self.idx]:
                poll["votes"][self.idx].append(uid)
                added = True
        _save(cog.polls)
        view = PollView(poll, closed=poll.get("closed", False))
        try:
            await interaction.response.edit_message(view=view)
        except Exception:
            await interaction.followup.edit_message(message_id=interaction.message.id, view=view)
        try:
            opt = poll["options"][self.idx]
            if added:
                await interaction.followup.send(msg(interaction, "vote_added", opt=opt), ephemeral=True)
            else:
                await interaction.followup.send(msg(interaction, "vote_removed"), ephemeral=True)
        except Exception:
            pass


class PollView(discord.ui.LayoutView):
    def __init__(self, poll: dict, closed: bool = False):
        super().__init__(timeout=None)

        # build a shim object so msg() can access .guild
        guild_id = poll.get("guild_id")

        class _Shim: pass
        s = _Shim()
        s.guild = None
        # Try to look up the guild for proper localisation
        # (we don't have bot here, so just pass None — fallback works fine)
        text = _build_poll_text(poll, s)

        children = [discord.ui.TextDisplay(content=text)]
        if not closed:
            # one row per ≤5 buttons
            buttons = [_VoteButton(i, poll["id"], disabled=False) for i in range(len(poll["options"]))]
            for i in range(0, len(buttons), 5):
                children.append(discord.ui.ActionRow(*buttons[i:i + 5]))
        self.add_item(discord.ui.Container(*children))


class Polls(commands.Cog):
    """Multi-option polls with live vote buttons."""

    def __init__(self, bot):
        self.bot = bot
        self.polls: Dict[str, dict] = _load()
        self._reattach()

    def _reattach(self):
        for poll in self.polls.values():
            if poll.get("closed"):
                continue
            try:
                self.bot.add_view(PollView(poll), message_id=poll["id"])
            except Exception:
                pass

    @commands.hybrid_group(
        name="poll",
        description="Multi-option polls.",
        help="{ 'en': 'Multi-option polls with live vote buttons.', 'de': 'Mehrfach-Umfragen mit Live-Buttons.', 'es': 'Encuestas multi-opción con botones de voto.' }",
        invoke_without_command=True,
    )
    @commands.guild_only()
    async def poll(self, ctx: commands.Context):
        await ctx.send_help(self.poll)

    @poll.command(
        name="create",
        description="Create a poll: question | option1 | option2 …",
        help="{ 'en': 'Create a poll: question | option1 | option2 …', 'de': 'Umfrage erstellen: Frage | Option1 | Option2 …', 'es': 'Crear encuesta: pregunta | opción1 | opción2 …' }",
    )
    async def poll_create(self, ctx: commands.Context, *, args: str):
        parts = [p.strip() for p in args.split("|") if p.strip()]
        if len(parts) < 3:
            return await ctx.send(msg(ctx, "need_options"))
        question, options = parts[0], parts[1:]
        if len(options) > 10:
            return await ctx.send(msg(ctx, "too_many"))

        # build poll (id is filled after sending)
        poll = {
            "id": 0,
            "guild_id": ctx.guild.id,
            "channel_id": ctx.channel.id,
            "author_id": ctx.author.id,
            "question": question[:200],
            "options": [o[:80] for o in options],
            "votes": [[] for _ in options],
            "closed": False,
            "created_at": int(datetime.now(timezone.utc).timestamp()),
        }
        view = PollView(poll)
        sent = await ctx.send(view=view)
        poll["id"] = sent.id
        self.polls[str(sent.id)] = poll
        _save(self.polls)
        # rebuild the view now that we have the message id (so custom_ids include it)
        try:
            await sent.edit(view=PollView(poll))
            self.bot.add_view(PollView(poll), message_id=sent.id)
        except Exception:
            pass

    @poll.command(
        name="end",
        description="End a poll early.",
        help="{ 'en': 'End a poll early (creator or admin).', 'de': 'Eine Umfrage vorzeitig beenden (Ersteller/Admin).', 'es': 'Finaliza una encuesta antes de tiempo (creador/admin).' }",
    )
    async def poll_end(self, ctx: commands.Context, message_id: str):
        poll = self.polls.get(str(message_id))
        if not poll:
            return await ctx.send(msg(ctx, "not_found"))
        if poll["author_id"] != ctx.author.id and not ctx.author.guild_permissions.manage_messages:
            return await ctx.send(msg(ctx, "not_owner"))
        poll["closed"] = True
        _save(self.polls)
        ch = ctx.guild.get_channel(poll["channel_id"])
        if ch:
            try:
                m = await ch.fetch_message(int(message_id))
                await m.edit(view=PollView(poll, closed=True))
            except Exception:
                pass
        await ctx.send(msg(ctx, "ended"))

    @poll.command(
        name="results",
        description="Show poll results.",
        help="{ 'en': 'Show poll results.', 'de': 'Ergebnisse einer Umfrage anzeigen.', 'es': 'Muestra los resultados de una encuesta.' }",
    )
    async def poll_results(self, ctx: commands.Context, message_id: str):
        poll = self.polls.get(str(message_id))
        if not poll:
            return await ctx.send(msg(ctx, "not_found"))
        title = msg(ctx, "results_title", icon=get_emoji("icon_lightbulb"))
        body = _build_poll_text(poll, ctx)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=title + "\n" + body)))
        await ctx.send(view=view)


async def setup(bot):
    await bot.add_cog(Polls(bot))
