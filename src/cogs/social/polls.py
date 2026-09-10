"""
Polls — multi-option polls with live vote buttons, now on the main database.

Commands (single `poll` group):
    poll create                         — interactive builder panel
    poll end <message_id>               — end a poll early (creator/admin)
    poll results <message_id>           — show final tally

Builder panel (like giveaway/triggers):
  - owner-only interactive LayoutView
  - Set question via modal
  - Add options via modal (≤10)
  - Each option rendered with its own ActionRow → Edit (modal) / Delete
  - Channel picker (defaults to invoking channel)
  - Send Poll validates (question + ≥2 options), posts the poll,
    registers the persistent vote view, and deletes the panel message.
  - Cancel / timeout handling
Vote buttons persist across restarts via bot.add_view(..., message_id=...)
"""

from __future__ import annotations

import json
import datetime
from typing import List

import discord
from discord.ext import commands

from config.emojis import get_emoji
from utils.ai.config import get_personality
from utils.i18n import make_msg

NUMBER_EMOJIS = [
    f"{get_emoji('number_zero')}", f"{get_emoji('number_one')}", f"{get_emoji('number_two')}",
    f"{get_emoji('number_three')}", f"{get_emoji('number_four')}", f"{get_emoji('number_five')}",
    f"{get_emoji('number_six')}", f"{get_emoji('number_seven')}", f"{get_emoji('number_eight')}", f"{get_emoji('number_nine')}",
]

MESSAGES = {
    "normal": {
        "en": {
            "need_options":  "❌ Provide at least 2 options — use **Add Option** in the builder, or run `poll create` to open the panel.",
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
            "only_host":     "❌ Only the poll creator can use this panel.",
            "need_question": "❌ Set a question first.",
            "sent":          "✅ Poll sent!",
            "cancelled":     "🗑 Poll setup cancelled.",
            "timed_out":     "⌛ Poll setup timed out.",
        },
        "de": {
            "need_options":  "❌ Mindestens 2 Optionen — nutze **Option hinzufügen** im Panel.",
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
            "only_host":     "❌ Nur der Ersteller kann dieses Panel bedienen.",
            "need_question": "❌ Bitte zuerst eine Frage festlegen.",
            "sent":          "✅ Umfrage gesendet!",
            "cancelled":     "🗑 Umfrage-Setup abgebrochen.",
            "timed_out":     "⌛ Umfrage-Setup abgelaufen.",
        },
        "es": {
            "need_options":  "❌ Al menos 2 opciones — usa **Añadir opción** en el panel.",
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
            "only_host":     "❌ Solo el creador puede usar este panel.",
            "need_question": "❌ Primero establece una pregunta.",
            "sent":          "✅ ¡Encuesta enviada!",
            "cancelled":     "🗑 Configuración cancelada.",
            "timed_out":     "⌛ Se agotó el tiempo de configuración.",
        },
    },
    "cafe": {
        "en": {
            "need_options":  "❌ at least 2 options please — hit **Add Option** ☕",
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
            "only_host":     "❌ only the poll creator can use this panel ☕",
            "need_question": "❌ set a question first, darling ☕",
            "sent":          "✅ poll sent! ☕✨",
            "cancelled":     "🗑 poll setup cancelled ☕",
            "timed_out":     "⌛ poll setup timed out ☕",
        },
        "de": {
            "need_options":  "❌ mindestens 2 optionen bitte — **Option hinzufügen** ☕",
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
            "only_host":     "❌ nur der ersteller kann das panel bedienen ☕",
            "need_question": "❌ erst eine frage festlegen ☕",
            "sent":          "✅ umfrage gesendet ☕",
            "cancelled":     "🗑 setup abgebrochen ☕",
            "timed_out":     "⌛ setup abgelaufen ☕",
        },
        "es": {
            "need_options":  "❌ al menos 2 opciones por favor — **Añadir opción** ☕",
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
            "only_host":     "❌ solo el creador puede usar este panel ☕",
            "need_question": "❌ primero pon una pregunta ☕",
            "sent":          "✅ encuesta enviada ☕✨",
            "cancelled":     "🗑 configuración cancelada ☕",
            "timed_out":     "⌛ tiempo agotado ☕",
        },
    },
}

msg = make_msg(MESSAGES)


# ───────────────────────────────────────────────────
#  helpers
# ───────────────────────────────────────────────────

def _options_from_row(row) -> List[str]:
    raw = row.get("options") if isinstance(row, dict) else getattr(row, "options", None)
    if isinstance(raw, list):
        return [str(o) for o in raw]
    if isinstance(raw, str):
        try:
            v = json.loads(raw)
            if isinstance(v, list):
                return [str(o) for o in v]
        except Exception:
            pass
        return [raw] if raw else []
    return []


def _guild_shim(guild):
    class _S: pass
    s = _S()
    s.guild = guild
    return s


def _build_poll_text(poll_row, counts: List[int], guild) -> str:
    shim = _guild_shim(guild)
    question = poll_row["question"]
    options = _options_from_row(poll_row)
    title = msg(shim, "title", icon=get_emoji("icon_lightbulb"), question=question)
    total = sum(counts) or 1
    lines = []
    for i, opt in enumerate(options):
        pct = round(counts[i] * 100 / total) if i < len(counts) else 0
        c = counts[i] if i < len(counts) else 0
        lines.append(msg(shim, "vote_count", letter=NUMBER_EMOJIS[i], opt=opt, count=c, pct=pct))
    # author mention
    author_id = poll_row["author_id"]
    closed = bool(poll_row.get("closed"))
    member = guild.get_member(author_id) if guild else None
    author_str = member.mention if member else f"<@{author_id}>"
    footer_key = "footer_closed" if closed else "footer_open"
    footer = msg(shim, footer_key, author=author_str)
    return title + "\n" + "\n".join(lines) + "\n\n" + footer


async def _fetch_poll_counts(bot, message_id: int) -> tuple[dict | None, List[int], List[dict]]:
    poll = await bot.cxn.fetchrow("SELECT * FROM polls WHERE message_id = $1", message_id)
    if not poll:
        return None, [], []
    options = _options_from_row(poll)
    counts = [0] * len(options)
    # fetch all votes and tally in Python (avoids GROUP BY which MongoPool doesn't parse)
    vote_rows = await bot.cxn.fetch("SELECT * FROM poll_votes WHERE message_id = $1", message_id)
    for r in vote_rows:
        try:
            idx = int(r["option_idx"])
            if 0 <= idx < len(counts):
                counts[idx] += 1
        except Exception:
            continue
    return poll, counts, vote_rows


async def _build_active_poll_view(bot, message_id: int, guild) -> discord.ui.LayoutView | None:
    poll, counts, _ = await _fetch_poll_counts(bot, message_id)
    if not poll:
        return None
    options = _options_from_row(poll)
    closed = bool(poll.get("closed"))
    text = _build_poll_text(poll, counts, guild)
    # buttons
    view = discord.ui.LayoutView(timeout=None)
    children: list = [discord.ui.TextDisplay(content=text)]
    if not closed:
        btns = [PollVoteButton(bot, message_id, i, disabled=False) for i in range(len(options))]
        for i in range(0, len(btns), 5):
            children.append(discord.ui.ActionRow(*btns[i:i+5]))
    view.add_item(discord.ui.Container(*children, accent_colour=discord.Color.blurple()))
    return view


def _make_persistent_poll_view(bot, message_id: int, option_count: int) -> discord.ui.LayoutView:
    """View registered via bot.add_view for persistence across restarts.

    Discord routes interactions by custom_id, so the TextDisplay content can be
    a minimal placeholder — the real message content is already on Discord and
    will be refreshed on the next vote. The button custom_ids must match the
    live poll view exactly (poll_vote_{mid}_{idx}).
    """
    view = discord.ui.LayoutView(timeout=None)
    btns = [PollVoteButton(bot, message_id, i, disabled=False) for i in range(option_count)]
    rows = []
    for i in range(0, len(btns), 5):
        rows.append(discord.ui.ActionRow(*btns[i:i+5]))
    placeholder = discord.ui.TextDisplay(content=f"-# poll {message_id}")
    container = discord.ui.Container(placeholder, *rows, accent_colour=discord.Color.blurple())
    view.add_item(container)
    return view


# ───────────────────────────────────────────────────
#  VOTE BUTTON
# ───────────────────────────────────────────────────

class PollVoteButton(discord.ui.Button):
    def __init__(self, bot, poll_id: int, idx: int, disabled: bool):
        super().__init__(
            emoji=NUMBER_EMOJIS[idx],
            style=discord.ButtonStyle.secondary,
            custom_id=f"poll_vote_{poll_id}_{idx}",
            disabled=disabled,
        )
        self.bot = bot
        self.poll_id = poll_id
        self.idx = idx

    async def callback(self, interaction: discord.Interaction):
        bot = self.bot
        # fetch poll
        poll = await bot.cxn.fetchrow("SELECT * FROM polls WHERE message_id = $1", self.poll_id)
        if not poll or poll.get("closed"):
            return await interaction.response.send_message(msg(interaction, "ended"), ephemeral=True)
        uid = interaction.user.id
        options = _options_from_row(poll)
        if self.idx >= len(options):
            return await interaction.response.send_message(msg(interaction, "not_found"), ephemeral=True)
        # toggle vote
        existing = await bot.cxn.fetchrow("SELECT option_idx FROM poll_votes WHERE message_id = $1 AND user_id = $2", self.poll_id, uid)
        added = False
        opt_name = options[self.idx]
        if existing is None:
            await bot.cxn.execute("INSERT INTO poll_votes (message_id, user_id, option_idx) VALUES ($1, $2, $3)", self.poll_id, uid, self.idx)
            added = True
        else:
            prev = int(existing["option_idx"])
            if prev == self.idx:
                await bot.cxn.execute("DELETE FROM poll_votes WHERE message_id = $1 AND user_id = $2", self.poll_id, uid)
                added = False
            else:
                await bot.cxn.execute("UPDATE poll_votes SET option_idx = $1 WHERE message_id = $2 AND user_id = $3", self.idx, self.poll_id, uid)
                added = True
        # rebuild view with fresh counts and edit message
        view = await _build_active_poll_view(bot, self.poll_id, interaction.guild)
        if view is None:
            return
        try:
            # Re-register persistent view so future edits keep working
            # (bot.add_view is idempotent)
            try:
                bot.add_view(_make_persistent_poll_view(bot, self.poll_id, len(options)), message_id=self.poll_id)
            except Exception:
                pass
            await interaction.response.edit_message(view=view)
        except discord.InteractionResponded:
            try:
                await interaction.followup.edit_message(message_id=interaction.message.id, view=view)
            except Exception:
                pass
        except Exception:
            try:
                await interaction.message.edit(view=view)
                await interaction.response.defer()
            except Exception:
                pass
        # followup vote confirm
        try:
            if added:
                await interaction.followup.send(msg(interaction, "vote_added", opt=opt_name), ephemeral=True)
            else:
                await interaction.followup.send(msg(interaction, "vote_removed"), ephemeral=True)
        except Exception:
            pass


# ───────────────────────────────────────────────────
#  BUILDER STATE & MODALS
# ───────────────────────────────────────────────────

class _PollSetupState:
    __slots__ = ("question", "options", "channel_id")
    def __init__(self, channel_id: int):
        self.question: str | None = None
        self.options: List[str] = []
        self.channel_id: int = channel_id


class _QuestionModal(discord.ui.Modal, title="Set Question"):
    question = discord.ui.TextInput(label="Poll question", placeholder="e.g. Best drink?", max_length=200, required=True, style=discord.TextStyle.short)
    def __init__(self, parent: "PollSetupView"):
        super().__init__()
        self._view = parent
        if parent.state.question:
            self.question.default = parent.state.question
    async def on_submit(self, interaction: discord.Interaction):
        self._view.state.question = self.question.value.strip()[:200]
        await self._view.refresh(interaction)


class _AddOptionModal(discord.ui.Modal, title="Add Option"):
    option = discord.ui.TextInput(label="Option", placeholder="e.g. Coffee", max_length=80, required=True, style=discord.TextStyle.short)
    def __init__(self, parent: "PollSetupView"):
        super().__init__()
        self._view = parent
    async def on_submit(self, interaction: discord.Interaction):
        if len(self._view.state.options) >= 10:
            return await interaction.response.send_message(msg(interaction, "too_many"), ephemeral=True)
        self._view.state.options.append(self.option.value.strip()[:80])
        await self._view.refresh(interaction)


class _EditOptionModal(discord.ui.Modal, title="Edit Option"):
    option = discord.ui.TextInput(label="Option", max_length=80, required=True, style=discord.TextStyle.short)
    def __init__(self, parent: "PollSetupView", idx: int):
        super().__init__()
        self._view = parent
        self._idx = idx
        self.option.default = parent.state.options[idx] if 0 <= idx < len(parent.state.options) else ""
    async def on_submit(self, interaction: discord.Interaction):
        if not (0 <= self._idx < len(self._view.state.options)):
            return await interaction.response.send_message("That option no longer exists.", ephemeral=True)
        self._view.state.options[self._idx] = self.option.value.strip()[:80]
        await self._view.refresh(interaction)


# ───────────────────────────────────────────────────
#  BUILDER BUTTONS
# ───────────────────────────────────────────────────

class _BuilderBtn(discord.ui.Button):
    def __init__(self, label: str, style, emoji, parent: "PollSetupView", action: str, idx: int | None = None):
        super().__init__(label=label, style=style, emoji=emoji)
        self._view_ref = parent
        self.action = action
        self.idx = idx
    async def callback(self, interaction: discord.Interaction):
        v = self._view_ref
        if interaction.user.id != v.host_id:
            return await interaction.response.send_message(msg(interaction, "only_host"), ephemeral=True)
        a = self.action
        if a == "question":
            return await interaction.response.send_modal(_QuestionModal(v))
        if a == "add_option":
            if len(v.state.options) >= 10:
                return await interaction.response.send_message(msg(interaction, "too_many"), ephemeral=True)
            return await interaction.response.send_modal(_AddOptionModal(v))
        if a == "edit":
            return await interaction.response.send_modal(_EditOptionModal(v, self.idx))  # type: ignore
        if a == "delete":
            if self.idx is not None and 0 <= self.idx < len(v.state.options):
                v.state.options.pop(self.idx)  # type: ignore
                await v.refresh(interaction)
            else:
                await interaction.response.defer()
            return
        if a == "cancel":
            done = discord.ui.LayoutView()
            done.add_item(discord.ui.Container(discord.ui.TextDisplay(content=msg(interaction, "cancelled")), accent_colour=discord.Color.red()))
            await interaction.response.edit_message(view=done)
            # delete after a short delay? spec says delete on send only; cancel keeps message but disabled
            return
        if a == "send":
            return await v.launch(interaction)


class _BuilderChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, parent: "PollSetupView"):
        super().__init__(placeholder="Pick channel to post the poll in…", channel_types=[discord.ChannelType.text, discord.ChannelType.news], min_values=1, max_values=1)
        self._view_ref = parent
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self._view_ref.host_id:
            return await interaction.response.send_message(msg(interaction, "only_host"), ephemeral=True)
        self._view_ref.state.channel_id = self.values[0].id
        await self._view_ref.refresh(interaction)


# ───────────────────────────────────────────────────
#  BUILDER VIEW
# ───────────────────────────────────────────────────

class PollSetupView(discord.ui.LayoutView):
    """Interactive poll builder — owner-only, like giveaway/triggers panels."""

    def __init__(self, bot, ctx_or_inter, state: _PollSetupState, host_id: int):
        super().__init__(timeout=600)
        self.bot = bot
        self.state = state
        self.host_id = host_id
        self.guild = getattr(ctx_or_inter, "guild", None)
        self.message: discord.Message | None = None
        self._build()

    def _build(self):
        self.clear_items()
        s = self.state
        guild = self.guild
        q_disp = s.question if s.question else "_not set_"
        ch_disp = f"<#{s.channel_id}>" if s.channel_id else "—"
        # header
        header = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_lightbulb')} Poll Builder"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=f"**Question:** {q_disp}\n**Channel:** {ch_disp}\n**Options:** {len(s.options)}/10"),
            accent_colour=discord.Color.blurple(),
        )
        self.add_item(header)

        # options list — each option with its own ActionRow (Edit / Delete)
        if s.options:
            for idx, opt in enumerate(s.options):
                container = discord.ui.Container(
                    discord.ui.TextDisplay(content=f"**{idx+1}.** {opt}"),
                    discord.ui.ActionRow(
                        _BuilderBtn("Edit", discord.ButtonStyle.secondary, f"{get_emoji('icon_edit')}", self, "edit", idx),
                        _BuilderBtn("Delete", discord.ButtonStyle.danger, f"{get_emoji('icon_trash')}", self, "delete", idx),
                    ),
                    accent_colour=discord.Color.greyple(),
                )
                self.add_item(container)
        else:
            self.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"-# No options yet — press {get_emoji('icon_plus')} **Add Option** to create one."),
                accent_colour=discord.Color.greyple(),
            ))

        # controls
        ready = bool(s.question) and len(s.options) >= 2 and len(s.options) <= 10 and s.channel_id
        send_style = discord.ButtonStyle.success if ready else discord.ButtonStyle.secondary

        controls = discord.ui.Container(
            discord.ui.ActionRow(
                _BuilderBtn("Set Question", discord.ButtonStyle.primary, f"{get_emoji('icon_edit')}", self, "question"),
                _BuilderBtn("Add Option", discord.ButtonStyle.primary, f"{get_emoji('icon_plus')}", self, "add_option"),
            ),
            discord.ui.ActionRow(_BuilderChannelSelect(self)),
            discord.ui.ActionRow(
                _BuilderBtn("Send Poll", send_style, f"{get_emoji('icon_tick')}", self, "send"),
                _BuilderBtn("Cancel", discord.ButtonStyle.danger, f"{get_emoji('icon_cross')}", self, "cancel"),
            ),
            accent_colour=discord.Color.blurple(),
        )
        self.add_item(controls)

        if not ready:
            hints = []
            if not s.question:
                hints.append("• Set a question")
            if len(s.options) < 2:
                hints.append(f"• Add at least {2 - len(s.options)} more option(s)")
            if not s.channel_id:
                hints.append("• Pick a channel")
            self.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content="-# " + " · ".join(hints)),
                accent_colour=discord.Color.greyple(),
            ))

    async def refresh(self, interaction: discord.Interaction):
        self._build()
        try:
            if interaction.response.is_done():
                await interaction.edit_original_response(view=self)
            else:
                await interaction.response.edit_message(view=self)
        except Exception:
            try:
                await interaction.followup.edit_message(message_id=interaction.message.id, view=self)
            except Exception:
                pass

    async def on_timeout(self):
        if self.message is None:
            return
        try:
            v = discord.ui.LayoutView()
            v.add_item(discord.ui.Container(discord.ui.TextDisplay(content=msg(_guild_shim(self.guild), "timed_out")), accent_colour=discord.Color.greyple()))
            await self.message.edit(view=v)
        except Exception:
            pass

    async def launch(self, interaction: discord.Interaction):
        s = self.state
        problems = []
        if not s.question:
            problems.append("- Question is not set")
        if len(s.options) < 2:
            problems.append("- Need at least 2 options")
        if len(s.options) > 10:
            problems.append("- Too many options (max 10)")
        if not s.channel_id:
            problems.append("- Channel is not set")
        if problems:
            return await interaction.response.send_message(f"{get_emoji('icon_cross')} Can't send the poll yet:\n" + "\n".join(problems), ephemeral=True)
        guild = interaction.guild
        channel = guild.get_channel(s.channel_id) if guild else None
        if channel is None:
            return await interaction.response.send_message(f"{get_emoji('icon_cross')} I can't find that channel anymore.", ephemeral=True)
        me = guild.me if guild else None
        if me and not channel.permissions_for(me).send_messages:
            return await interaction.response.send_message(f"{get_emoji('icon_cross')} I can't send messages in {channel.mention}.", ephemeral=True)

        question = s.question.strip()[:200]
        options = [o.strip()[:80] for o in s.options]
        # Defer first so we can do network work without timing out the interaction.
        # For button interactions we can defer the message update; the panel will
        # be deleted right after, so the user sees the poll appear.
        try:
            if not interaction.response.is_done():
                await interaction.response.defer()
        except Exception:
            pass
        # send stub then persistent view
        stub_text = f"### {get_emoji('icon_lightbulb')} {question}\n" + "\n".join(f"**{NUMBER_EMOJIS[i]}** {o} — `0` votes (0%)" for i, o in enumerate(options)) + f"\n\n-# Click a button to vote · poll by <@{self.host_id}>"
        stub_view = discord.ui.LayoutView()
        stub_view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=stub_text), accent_colour=discord.Color.blurple()))
        sent = await channel.send(view=stub_view)
        # persist to DB
        await self.bot.cxn.execute(
            "INSERT INTO polls (message_id, guild_id, channel_id, author_id, question, options, closed, created_at) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)",
            sent.id, guild.id, channel.id, self.host_id, question, json.dumps(options), 0, datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )
        # build real active view and register persistence
        active = await _build_active_poll_view(self.bot, sent.id, guild)
        if active:
            try:
                await sent.edit(view=active)
            except Exception:
                pass
        try:
            self.bot.add_view(_make_persistent_poll_view(self.bot, sent.id, len(options)), message_id=sent.id)
        except Exception:
            pass
        # delete the builder panel message as requested — this is the UX the
        # spec asks for: clicking Send Poll removes the setup panel entirely.
        try:
            if self.message:
                await self.message.delete()
            elif interaction.message:
                await interaction.message.delete()
        except Exception:
            # if delete fails (missing perms), fall back to editing the panel
            try:
                done = discord.ui.LayoutView()
                done.add_item(discord.ui.Container(discord.ui.TextDisplay(content=msg(interaction, "sent")), accent_colour=discord.Color.green()))
                await interaction.followup.edit_message(message_id=interaction.message.id, view=done)  # type: ignore
            except Exception:
                pass


# ───────────────────────────────────────────────────
#  COG
# ───────────────────────────────────────────────────

class Polls(commands.Cog):
    """Multi-option polls with live vote buttons (DB + persistent)."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        # create tables (covers SQLite and Mongo)
        await self.bot.cxn.execute("""
            CREATE TABLE IF NOT EXISTS polls (
                message_id INTEGER PRIMARY KEY,
                guild_id   INTEGER,
                channel_id INTEGER,
                author_id  INTEGER,
                question   TEXT,
                options    TEXT,
                closed     INTEGER DEFAULT 0,
                created_at TEXT
            )
        """)
        await self.bot.cxn.execute("""
            CREATE TABLE IF NOT EXISTS poll_votes (
                message_id INTEGER,
                user_id    INTEGER,
                option_idx INTEGER,
                PRIMARY KEY (message_id, user_id)
            )
        """)
        # migrate legacy JSON file if present
        await self._migrate_json()
        # re-register persistent vote views for every open poll
        try:
            active = await self.bot.cxn.fetch("SELECT message_id, options FROM polls WHERE closed = 0")
            for row in active:
                mid = int(row["message_id"])
                opts = _options_from_row(row)
                try:
                    self.bot.add_view(_make_persistent_poll_view(self.bot, mid, len(opts)), message_id=mid)
                except Exception:
                    continue
        except Exception:
            pass

    async def _migrate_json(self):
        import os
        path = "data/polls.json"
        if not os.path.exists(path):
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
            if not isinstance(data, dict) or not data:
                os.rename(path, path + ".migrated")
                return
            migrated = 0
            for mid_str, poll in data.items():
                try:
                    mid = int(mid_str)
                    exists = await self.bot.cxn.fetchval("SELECT message_id FROM polls WHERE message_id = $1", mid)
                    if exists:
                        continue
                    question = poll.get("question", "Poll")[:200]
                    options = poll.get("options", [])[:10]
                    votes = poll.get("votes", [])
                    closed = 1 if poll.get("closed") else 0
                    await self.bot.cxn.execute(
                        "INSERT INTO polls (message_id, guild_id, channel_id, author_id, question, options, closed, created_at) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)",
                        mid, poll.get("guild_id"), poll.get("channel_id"), poll.get("author_id"), question, json.dumps(options), closed, datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    )
                    # votes: list of lists of user_ids
                    for idx, voters in enumerate(votes):
                        if not isinstance(voters, list):
                            continue
                        for uid in voters:
                            try:
                                await self.bot.cxn.execute("INSERT OR IGNORE INTO poll_votes (message_id, user_id, option_idx) VALUES ($1,$2,$3)", mid, int(uid), idx)
                            except Exception:
                                continue
                    migrated += 1
                except Exception:
                    continue
            if migrated:
                os.rename(path, path + ".migrated")
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
        help_cmd = self.bot.get_command("help")
        if help_cmd is None:
            return await ctx.send_help(self.poll)
        await ctx.invoke(help_cmd, command_name="poll")

    @poll.command(
        name="create",
        description="Open the interactive poll builder.",
        help="{ 'en': 'Open the interactive poll builder.', 'de': 'Interaktiven Umfrage-Builder öffnen.', 'es': 'Abre el creador interactivo de encuestas.' }",
    )
    @commands.guild_only()
    async def poll_create(self, ctx: commands.Context):
        """Open the interactive poll builder panel (like triggers/giveaway)."""
        state = _PollSetupState(channel_id=ctx.channel.id)
        view = PollSetupView(self.bot, ctx, state, ctx.author.id)
        sent = await ctx.send(view=view)
        view.message = sent

    @poll.command(
        name="end",
        description="End a poll early.",
        help="{ 'en': 'End a poll early (creator or admin).', 'de': 'Eine Umfrage vorzeitig beenden (Ersteller/Admin).', 'es': 'Finaliza una encuesta antes de tiempo (creador/admin).' }",
    )
    async def poll_end(self, ctx: commands.Context, message_id: str):
        try:
            mid = int(message_id)
        except ValueError:
            return await ctx.send(msg(ctx, "not_found"))
        poll = await self.bot.cxn.fetchrow("SELECT * FROM polls WHERE message_id = $1", mid)
        if not poll:
            return await ctx.send(msg(ctx, "not_found"))
        if poll["author_id"] != ctx.author.id and not ctx.author.guild_permissions.manage_messages:
            return await ctx.send(msg(ctx, "not_owner"))
        await self.bot.cxn.execute("UPDATE polls SET closed = 1 WHERE message_id = $1", mid)
        ch = ctx.guild.get_channel(poll["channel_id"])
        view = await _build_active_poll_view(self.bot, mid, ctx.guild)
        if ch and view:
            try:
                m = await ch.fetch_message(mid)
                await m.edit(view=view)
            except Exception:
                pass
        elif ch:
            # fallback: try updating without view rebuild
            pass
        await ctx.send(msg(ctx, "ended"))

    @poll.command(
        name="results",
        description="Show poll results.",
        help="{ 'en': 'Show poll results.', 'de': 'Ergebnisse einer Umfrage anzeigen.', 'es': 'Muestra los resultados de una encuesta.' }",
    )
    async def poll_results(self, ctx: commands.Context, message_id: str):
        try:
            mid = int(message_id)
        except ValueError:
            return await ctx.send(msg(ctx, "not_found"))
        poll = await self.bot.cxn.fetchrow("SELECT * FROM polls WHERE message_id = $1", mid)
        if not poll:
            return await ctx.send(msg(ctx, "not_found"))
        view = await _build_active_poll_view(self.bot, mid, ctx.guild)
        if view is None:
            return await ctx.send(msg(ctx, "not_found"))
        # Use results title + same body but without buttons (active view for closed already has no buttons)
        # If poll is still open we still show live counts in a non-interactive container
        # Reuse view's container content but without buttons -> fetch counts and build a read-only view
        poll_obj, counts, _ = await _fetch_poll_counts(self.bot, mid)
        text = _build_poll_text(poll_obj, counts, ctx.guild)  # type: ignore
        title = msg(ctx, "results_title", icon=get_emoji("icon_lightbulb"))
        ro_view = discord.ui.LayoutView()
        ro_view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=title + "\n" + text), accent_colour=discord.Color.blurple()))
        await ctx.send(view=ro_view)


async def setup(bot):
    await bot.add_cog(Polls(bot))
