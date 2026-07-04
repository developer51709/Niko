import discord
from discord.ext import commands, tasks
import re
import json
import datetime
import random
import asyncio

from config.emojis import get_emoji
from utils.paginator import PaginatedView, paginate
from utils.ai.config import get_personality


# ─────────────────────────────────────────────────────────────
#  REQUIREMENT HELPERS
# ─────────────────────────────────────────────────────────────

DEFAULT_REQUIREMENTS = {
    "account_age_days": 0,   # minimum Discord account age (days)
    "server_age_days":  0,   # minimum time the user has been in the guild (days)
    "role_ids":         [],  # all of these role IDs must be held
    "boost_required":   False,
}


def _load_reqs(raw) -> dict:
    """Return a fully-populated requirements dict from a raw DB value."""
    out = dict(DEFAULT_REQUIREMENTS)
    if not raw:
        return out
    try:
        data = json.loads(raw) if isinstance(raw, str) else dict(raw)
    except (ValueError, TypeError):
        return out
    for key, default in DEFAULT_REQUIREMENTS.items():
        if key in data and data[key] is not None:
            out[key] = data[key]
    if not isinstance(out["role_ids"], list):
        out["role_ids"] = []
    out["account_age_days"] = max(0, int(out["account_age_days"] or 0))
    out["server_age_days"]  = max(0, int(out["server_age_days"] or 0))
    out["boost_required"]   = bool(out["boost_required"])
    return out


def _dump_reqs(reqs: dict) -> str:
    return json.dumps({k: reqs.get(k, v) for k, v in DEFAULT_REQUIREMENTS.items()})


def _requirements_summary(reqs: dict, guild: discord.Guild | None = None) -> str:
    """Human-readable bullet list of the current requirements (or 'None')."""
    parts: list[str] = []
    if reqs["account_age_days"] > 0:
        parts.append(f"• Account age ≥ **{reqs['account_age_days']}** day(s)")
    if reqs["server_age_days"] > 0:
        parts.append(f"• Server member ≥ **{reqs['server_age_days']}** day(s)")
    if reqs["role_ids"]:
        if guild:
            mentions = []
            for rid in reqs["role_ids"]:
                role = guild.get_role(rid)
                mentions.append(role.mention if role else f"<@&{rid}>")
            parts.append("• Required roles: " + ", ".join(mentions))
        else:
            parts.append(
                "• Required roles: "
                + ", ".join(f"<@&{rid}>" for rid in reqs["role_ids"])
            )
    if reqs["boost_required"]:
        parts.append("• Must be boosting the server")
    return "\n".join(parts) if parts else "_None — anyone can enter._"


def _check_member_meets_reqs(member: discord.Member, reqs: dict) -> str | None:
    """Return ``None`` if ``member`` meets every requirement, else a reason string."""
    now = datetime.datetime.now(datetime.timezone.utc)

    if reqs["account_age_days"] > 0:
        age = (now - member.created_at).days
        if age < reqs["account_age_days"]:
            return (
                f"{get_emoji('icon_cross')} Your Discord account must be at least "
                f"**{reqs['account_age_days']}** day(s) old to join "
                f"this giveaway (yours is **{age}**)."
            )

    if reqs["server_age_days"] > 0:
        joined_at = getattr(member, "joined_at", None)
        if joined_at is None:
            return "{get_emoji('icon_cross')} I can't verify how long you've been in this server, so you can't join this giveaway."
        days_in = (now - joined_at).days
        if days_in < reqs["server_age_days"]:
            return (
                f"{get_emoji('icon_cross')} You must have been in this server for at least "
                f"**{reqs['server_age_days']}** day(s) to join this giveaway "
                f"(you've been here **{days_in}**)."
            )

    if reqs["role_ids"]:
        member_role_ids = {r.id for r in member.roles}
        missing = [rid for rid in reqs["role_ids"] if rid not in member_role_ids]
        if missing:
            mentions = ", ".join(f"<@&{rid}>" for rid in missing)
            return f"{get_emoji('icon_cross')} You're missing the required role(s): {mentions}."

    if reqs["boost_required"] and getattr(member, "premium_since", None) is None:
        return "{get_emoji('icon_cross')} Only members boosting this server can join this giveaway."

    return None

# ─────────────────────────────────────────────────────────────
#  MESSAGE TABLE
# ─────────────────────────────────────────────────────────────

MESSAGES = {
    "normal": {
        "en": {
            "giveaway_title":         "Giveaway",
            "giveaway_ended_title":   "Giveaway Ended!",
            "label_prize":            "Prize",
            "label_ends":             "Ends",
            "label_hosted_by":        "Hosted by",
            "label_winner":           "Winner(s)",
            "label_no_participants":  "Nobody participated",
            "no_participants_msg":    "The giveaway for **{prize}** has ended, but nobody participated! 😢",
            "winner_announce":        "🎉 Congratulations {mentions}! You won **{prize}**!\n{url}",
            "reroll_announce":        "🎉 **Giveaway Reroll!** The new winner for **{prize}** is: {mentions}! Congratulations!",
            "join_success":           "🎉 You have successfully joined the giveaway! Good luck!",
            "join_already":           "✅ You have already joined this giveaway!",
            "join_ended":             "❌ This giveaway has already ended!",
            "join_host":              "❌ You cannot join your own giveaway!",
            "join_bot":               "❌ Bots cannot participate in giveaways!",
            "no_exist":               "❌ This giveaway doesn't exist anymore.",
            "no_perm_manage":         "❌ Only the giveaway host or a server admin can manage this giveaway.",
            "end_confirmed":          "✅ The giveaway has been ended. Winners have been announced in the channel.",
            "no_participants_yet":    "Nobody has joined the giveaway yet.",
            "reroll_no_participants": "❌ Nobody participated in this giveaway, so no one can be rerolled!",
            "reroll_not_ended":       "❌ This giveaway hasn't ended yet! You can only reroll ended giveaways.",
            "reroll_not_found":       "❌ Could not find a giveaway with that message ID.",
            "invalid_duration":       "❌ Invalid duration! Use numbers followed by `s`, `m`, `h`, or `d` (e.g. `30s`, `10m`, `2h`, `1d`).",
            "invalid_winners":        "❌ Invalid winners count! Must be a number (e.g. `2`).",
            "min_one_winner":         "❌ You must have at least 1 winner!",
            "footer_active":          "{count} Winner{s} | Ends at",
            "manage_title":           "⚙️ Giveaway Management",
            "manage_info":            "Use the buttons below to manage this giveaway.",
            "select_result":          "🎲 Randomly selected: {mention}",
            "select_no_entries":      "Nobody has entered the giveaway yet, so no one can be selected.",
            "participants_title":     "👥 Participants",
            "participants_empty":     "Nobody has joined the giveaway yet.",
        },
        "de": {
            "giveaway_title":         "Gewinnspiel",
            "giveaway_ended_title":   "Gewinnspiel beendet!",
            "label_prize":            "Preis",
            "label_ends":             "Endet",
            "label_hosted_by":        "Veranstaltet von",
            "label_winner":           "Gewinner",
            "label_no_participants":  "Niemand hat teilgenommen",
            "no_participants_msg":    "Das Gewinnspiel für **{prize}** ist beendet, aber niemand hat teilgenommen! 😢",
            "winner_announce":        "🎉 Glückwunsch {mentions}! Ihr habt **{prize}** gewonnen!\n{url}",
            "reroll_announce":        "🎉 **Reroll!** Der neue Gewinner für **{prize}** ist: {mentions}! Glückwunsch!",
            "join_success":           "🎉 Du hast erfolgreich am Gewinnspiel teilgenommen! Viel Glück!",
            "join_already":           "✅ Du hast bereits an diesem Gewinnspiel teilgenommen!",
            "join_ended":             "❌ Dieses Gewinnspiel ist bereits beendet!",
            "join_host":              "❌ Du kannst nicht an deinem eigenen Gewinnspiel teilnehmen!",
            "join_bot":               "❌ Bots können nicht an Gewinnspielen teilnehmen!",
            "no_exist":               "❌ Dieses Gewinnspiel existiert nicht mehr.",
            "no_perm_manage":         "❌ Nur der Veranstalter oder ein Server-Admin kann dieses Gewinnspiel verwalten.",
            "end_confirmed":          "✅ Das Gewinnspiel wurde beendet. Gewinner wurden im Channel bekannt gegeben.",
            "no_participants_yet":    "Noch niemand hat am Gewinnspiel teilgenommen.",
            "reroll_no_participants": "❌ Niemand hat teilgenommen, daher kann niemand erneut gezogen werden!",
            "reroll_not_ended":       "❌ Dieses Gewinnspiel ist noch nicht beendet!",
            "reroll_not_found":       "❌ Kein Gewinnspiel mit dieser Nachrichten-ID gefunden.",
            "invalid_duration":       "❌ Ungültige Dauer! Benutze Zahlen mit `s`, `m`, `h` oder `d` (z.B. `30s`, `10m`, `2h`, `1d`).",
            "invalid_winners":        "❌ Ungültige Gewinneranzahl! Muss eine Zahl sein (z.B. `2`).",
            "min_one_winner":         "❌ Es muss mindestens 1 Gewinner geben!",
            "footer_active":          "{count} Gewinner | Endet um",
            "manage_title":           "⚙️ Gewinnspiel-Verwaltung",
            "manage_info":            "Nutze die Schaltflächen unten, um das Gewinnspiel zu verwalten.",
            "select_result":          "🎲 Zufällig ausgewählt: {mention}",
            "select_no_entries":      "Noch niemand ist dabei, daher kann niemand ausgewählt werden.",
            "participants_title":     "👥 Teilnehmer",
            "participants_empty":     "Noch niemand hat am Gewinnspiel teilgenommen.",
        },
        "es": {
            "giveaway_title":         "Sorteo",
            "giveaway_ended_title":   "¡Sorteo Finalizado!",
            "label_prize":            "Premio",
            "label_ends":             "Finaliza",
            "label_hosted_by":        "Organizado por",
            "label_winner":           "Ganador(es)",
            "label_no_participants":  "Nadie participó",
            "no_participants_msg":    "El sorteo de **{prize}** ha terminado, ¡pero nadie participó! 😢",
            "winner_announce":        "🎉 ¡Felicidades {mentions}! ¡Has ganado **{prize}**!\n{url}",
            "reroll_announce":        "🎉 **¡Re-sorteo!** El nuevo ganador de **{prize}** es: {mentions}! ¡Felicidades!",
            "join_success":           "🎉 ¡Te has unido al sorteo correctamente! ¡Mucha suerte!",
            "join_already":           "✅ ¡Ya te uniste a este sorteo!",
            "join_ended":             "❌ ¡Este sorteo ya ha terminado!",
            "join_host":              "❌ ¡No puedes unirte a tu propio sorteo!",
            "join_bot":               "❌ ¡Los bots no pueden participar en sorteos!",
            "no_exist":               "❌ Este sorteo ya no existe.",
            "no_perm_manage":         "❌ Solo el organizador del sorteo o un admin del servidor puede gestionarlo.",
            "end_confirmed":          "✅ El sorteo ha sido finalizado. Los ganadores han sido anunciados en el canal.",
            "no_participants_yet":    "Nadie se ha unido al sorteo todavía.",
            "reroll_no_participants": "❌ ¡Nadie participó en este sorteo, así que no hay nadie a quien volver a elegir!",
            "reroll_not_ended":       "❌ ¡Este sorteo aún no ha terminado! Solo puedes volver a sortear sorteos finalizados.",
            "reroll_not_found":       "❌ No se encontró un sorteo con ese ID de mensaje.",
            "invalid_duration":       "❌ ¡Duración inválida! Usa números seguidos de `s`, `m`, `h` o `d` (p. ej. `30s`, `10m`, `2h`, `1d`).",
            "invalid_winners":        "❌ ¡Cantidad de ganadores inválida! Debe ser un número (p. ej. `2`).",
            "min_one_winner":         "❌ ¡Debe haber al menos 1 ganador!",
            "footer_active":          "{count} Ganador{s} | Finaliza el",
            "manage_title":           "⚙️ Gestión del Sorteo",
            "manage_info":            "Usa los botones de abajo para gestionar este sorteo.",
            "select_result":          "🎲 Elegido al azar: {mention}",
            "select_no_entries":      "Nadie se ha unido al sorteo todavía, así que no hay a quién elegir.",
            "participants_title":     "👥 Participantes",
            "participants_empty":     "Nadie se ha unido al sorteo todavía.",
        },
    },
    "cafe": {
        "en": {
            "giveaway_title":         "Giveaway",
            "giveaway_ended_title":   "Giveaway Ended ☕",
            "label_prize":            "prize",
            "label_ends":             "ends",
            "label_hosted_by":        "brewed by",
            "label_winner":           "winner(s) ✨",
            "label_no_participants":  "nobody sipped in 😢",
            "no_participants_msg":    "the giveaway for **{prize}** ended, but nobody joined 😭 maybe next time~",
            "winner_announce":        "🎉 congrats {mentions}! you won **{prize}**! enjoy it with a coffee ☕✨\n{url}",
            "reroll_announce":        "🎉 **reroll time!** the new winner for **{prize}** is: {mentions}! congrats ☕",
            "join_success":           "🎉 you're in! fingers crossed ☕✨",
            "join_already":           "☕ you already joined this one~ sit tight!",
            "join_ended":             "😔 this giveaway is already over...",
            "join_host":              "☕ can't join your own giveaway, silly~",
            "join_bot":               "🤖 bots can't join giveaways, sorry!",
            "no_exist":               "😔 this giveaway doesn't exist anymore.",
            "no_perm_manage":         "☕ only the giveaway host or a server admin can manage this.",
            "end_confirmed":          "✅ giveaway ended~ winners have been announced in the channel ☕",
            "no_participants_yet":    "nobody has joined yet 😔",
            "reroll_no_participants": "😔 nobody joined, so there's no one to reroll!",
            "reroll_not_ended":       "😔 this giveaway isn't over yet! rerolls are only for ended ones~",
            "reroll_not_found":       "😔 couldn't find a giveaway with that message id.",
            "invalid_duration":       "❌ invalid duration! use numbers with `s`, `m`, `h`, or `d` (e.g. `30s`, `10m`, `2h`, `1d`)",
            "invalid_winners":        "❌ invalid winner count! needs to be a number (e.g. `2`).",
            "min_one_winner":         "❌ at least 1 winner is needed!",
            "footer_active":          "{count} winner{s} | ends at",
            "manage_title":           "⚙️ giveaway management",
            "manage_info":            "use the buttons below to manage this giveaway ☕",
            "select_result":          "🎲 randomly picked: {mention}",
            "select_no_entries":      "nobody has entered yet, so there's no one to pick 😔",
            "participants_title":     "☕ participants",
            "participants_empty":     "nobody has joined yet 😔",
        },
        "de": {
            "giveaway_title":         "Gewinnspiel",
            "giveaway_ended_title":   "Gewinnspiel vorbei ☕",
            "label_prize":            "preis",
            "label_ends":             "endet",
            "label_hosted_by":        "veranstaltet von",
            "label_winner":           "gewinner ✨",
            "label_no_participants":  "niemand dabei 😢",
            "no_participants_msg":    "das gewinnspiel für **{prize}** ist vorbei, aber niemand hat mitgemacht 😭",
            "winner_announce":        "🎉 glückwunsch {mentions}! ihr habt **{prize}** gewonnen! genieß es mit einem kaffee ☕✨\n{url}",
            "reroll_announce":        "🎉 **reroll!** der neue gewinner für **{prize}**: {mentions}! glückwunsch ☕",
            "join_success":           "🎉 du bist dabei! drück die daumen ☕✨",
            "join_already":           "☕ du hast schon mitgemacht~ warte einfach!",
            "join_ended":             "😔 dieses gewinnspiel ist schon vorbei...",
            "join_host":              "☕ du kannst nicht am eigenen gewinnspiel teilnehmen~",
            "join_bot":               "🤖 bots können leider nicht mitmachen!",
            "no_exist":               "😔 dieses gewinnspiel existiert nicht mehr.",
            "no_perm_manage":         "☕ nur der veranstalter oder ein server-admin kann das verwalten.",
            "end_confirmed":          "✅ gewinnspiel beendet~ gewinner wurden im channel bekannt gegeben ☕",
            "no_participants_yet":    "noch niemand hat mitgemacht 😔",
            "reroll_no_participants": "😔 niemand war dabei, also gibt's niemanden zum rerolln!",
            "reroll_not_ended":       "😔 das gewinnspiel ist noch nicht vorbei!",
            "reroll_not_found":       "😔 kein gewinnspiel mit dieser nachrichten-id gefunden.",
            "invalid_duration":       "❌ ungültige dauer! benutze zahlen mit `s`, `m`, `h` oder `d` (z.b. `30s`, `10m`, `2h`, `1d`)",
            "invalid_winners":        "❌ ungültige gewinneranzahl! muss eine zahl sein (z.b. `2`).",
            "min_one_winner":         "❌ es braucht mindestens 1 gewinner!",
            "footer_active":          "{count} gewinner | endet um",
            "manage_title":           "⚙️ gewinnspiel-verwaltung",
            "manage_info":            "nutze die schaltflächen unten, um das gewinnspiel zu verwalten ☕",
            "select_result":          "🎲 zufällig ausgewählt: {mention}",
            "select_no_entries":      "noch niemand ist dabei, also kann niemand ausgewählt werden 😔",
            "participants_title":     "☕ teilnehmer",
            "participants_empty":     "noch niemand hat mitgemacht 😔",
        },
        "es": {
            "giveaway_title":         "Sorteo",
            "giveaway_ended_title":   "Sorteo Terminado ☕",
            "label_prize":            "premio",
            "label_ends":             "termina",
            "label_hosted_by":        "preparado por",
            "label_winner":           "ganador(es) ✨",
            "label_no_participants":  "nadie se animó 😢",
            "no_participants_msg":    "el sorteo de **{prize}** terminó, pero nadie se unió 😭 ¡quizá la próxima!",
            "winner_announce":        "🎉 ¡felicidades {mentions}! ¡has ganado **{prize}**! disfrútalo con un cafecito ☕✨\n{url}",
            "reroll_announce":        "🎉 **¡hora de re-sortear!** el nuevo ganador de **{prize}** es: {mentions}! felicidades ☕",
            "join_success":           "🎉 ¡estás dentro! crucemos los dedos ☕✨",
            "join_already":           "☕ ya te uniste a este~ ¡tranqui!",
            "join_ended":             "😔 este sorteo ya terminó...",
            "join_host":              "☕ no puedes unirte a tu propio sorteo, tontito~",
            "join_bot":               "🤖 ¡los bots no pueden unirse a sorteos, lo siento!",
            "no_exist":               "😔 este sorteo ya no existe.",
            "no_perm_manage":         "☕ solo el organizador o un admin del servidor puede gestionar esto.",
            "end_confirmed":          "✅ sorteo terminado~ los ganadores han sido anunciados en el canal ☕",
            "no_participants_yet":    "todavía nadie se ha unido 😔",
            "reroll_no_participants": "😔 ¡nadie se unió, así que no hay a quién re-sortear!",
            "reroll_not_ended":       "😔 ¡este sorteo aún no terminó! los re-sorteos son solo para los terminados~",
            "reroll_not_found":       "😔 no encontré un sorteo con ese id de mensaje.",
            "invalid_duration":       "❌ ¡duración inválida! usa números con `s`, `m`, `h` o `d` (p. ej. `30s`, `10m`, `2h`, `1d`)",
            "invalid_winners":        "❌ ¡cantidad de ganadores inválida! tiene que ser un número (p. ej. `2`).",
            "min_one_winner":         "❌ ¡se necesita al menos 1 ganador!",
            "footer_active":          "{count} ganador{s} | termina el",
            "manage_title":           "⚙️ gestión del sorteo",
            "manage_info":            "usa los botones de abajo para gestionar este sorteo ☕",
            "select_result":          "🎲 elegido al azar: {mention}",
            "select_no_entries":      "todavía nadie se ha unido, así que no hay a quién elegir 😔",
            "participants_title":     "☕ participantes",
            "participants_empty":     "todavía nadie se ha unido 😔",
        },
    },
}


def _get_lang(obj) -> str:
    guild = getattr(obj, "guild", None)
    if guild and getattr(guild, "preferred_locale", None):
        if str(guild.preferred_locale).lower().startswith("de"):
            return "de"
        if str(guild.preferred_locale).lower().startswith("es"):
            return "es"
    return "en"


def msg(obj, key: str, **kwargs) -> str:
    personality = get_personality(obj)
    lang = _get_lang(obj)
    text = MESSAGES.get(personality, {}).get(lang, {}).get(key)
    if text is None:
        text = MESSAGES.get(personality, {}).get("en", {}).get(key)
    if text is None:
        text = MESSAGES["normal"].get(lang, {}).get(key)
    if text is None:
        text = MESSAGES["normal"]["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text


def _guild_msg(guild, key: str, **kwargs) -> str:
    class _Wrap:
        pass
    w = _Wrap()
    w.guild = guild
    return msg(w, key, **kwargs)


# ─────────────────────────────────────────────────────────────
#  MAIN MESSAGE BUTTONS  (per-giveaway custom_id for isolation)
# ─────────────────────────────────────────────────────────────

class _GiveawayJoinBtn(discord.ui.Button):
    """Join button — custom_id encodes the giveaway message_id."""

    def __init__(self, bot, message_id: int):
        super().__init__(
            label="Join",
            style=discord.ButtonStyle.primary,
            emoji=f"{get_emoji('icon_giveaway')}",
            custom_id=f"giveaway_join_{message_id}",
        )
        self._bot = bot

    async def callback(self, interaction: discord.Interaction):
        message_id = interaction.message.id
        user_id    = interaction.user.id

        giveaway = await self._bot.cxn.fetchrow(
            "SELECT host_id, ended, requirements FROM giveaways WHERE message_id = $1",
            message_id,
        )
        if not giveaway:
            return await interaction.response.send_message(msg(interaction, "no_exist"), ephemeral=True)
        if giveaway["ended"]:
            return await interaction.response.send_message(msg(interaction, "join_ended"), ephemeral=True)
        if user_id == giveaway["host_id"]:
            return await interaction.response.send_message(msg(interaction, "join_host"), ephemeral=True)
        if interaction.user.bot:
            return await interaction.response.send_message(msg(interaction, "join_bot"), ephemeral=True)

        # Enforce host-configured requirements (account age, server age, roles, boost).
        reqs = _load_reqs(giveaway["requirements"])
        if isinstance(interaction.user, discord.Member):
            failure = _check_member_meets_reqs(interaction.user, reqs)
            if failure:
                return await interaction.response.send_message(failure, ephemeral=True)

        existing = await self._bot.cxn.fetchval(
            "SELECT 1 FROM participants WHERE message_id = $1 AND user_id = $2",
            message_id, user_id
        )
        if existing:
            return await interaction.response.send_message(msg(interaction, "join_already"), ephemeral=True)

        await self._bot.cxn.execute(
            "INSERT INTO participants (message_id, user_id) VALUES ($1, $2)", message_id, user_id
        )
        await interaction.response.send_message(msg(interaction, "join_success"), ephemeral=True)


class _GiveawayManageBtn(discord.ui.Button):
    """Manage button — opens ephemeral panel for host / server admins."""

    def __init__(self, bot, message_id: int):
        super().__init__(
            label="Manage",
            style=discord.ButtonStyle.secondary,
            emoji=f"{get_emoji('icon_settings')}",
            custom_id=f"giveaway_manage_{message_id}",
        )
        self._bot = bot

    async def callback(self, interaction: discord.Interaction):
        message_id = interaction.message.id

        giveaway = await self._bot.cxn.fetchrow(
            "SELECT message_id, channel_id, guild_id, prize, winners_count, host_id, ended "
            "FROM giveaways WHERE message_id = $1", message_id
        )
        if not giveaway:
            return await interaction.response.send_message(msg(interaction, "no_exist"), ephemeral=True)
        if giveaway["ended"]:
            return await interaction.response.send_message(msg(interaction, "join_ended"), ephemeral=True)

        is_host  = interaction.user.id == giveaway["host_id"]
        is_admin = interaction.user.guild_permissions.manage_guild
        if not (is_host or is_admin):
            return await interaction.response.send_message(
                msg(interaction, "no_perm_manage"), ephemeral=True
            )

        panel = _build_manage_panel(self._bot, giveaway, interaction.guild)
        await interaction.response.send_message(view=panel, ephemeral=True)


def _make_persistent_view(bot, message_id: int) -> discord.ui.View:
    """
    A timeout=None View registered with bot.add_view(view, message_id=...).
    Each active giveaway gets its own registered view, keyed by message_id,
    so button interactions from different giveaway messages never interfere.
    """
    view = discord.ui.View(timeout=None)
    view.add_item(_GiveawayJoinBtn(bot, message_id))
    view.add_item(_GiveawayManageBtn(bot, message_id))
    return view


# ─────────────────────────────────────────────────────────────
#  MANAGEMENT PANEL BUTTONS  (ephemeral — no persistence needed)
# ─────────────────────────────────────────────────────────────

class _MgmtEndBtn(discord.ui.Button):
    def __init__(self, bot, message_id, prize, winners_count, channel_id, guild_id, host_id):
        super().__init__(label="End Giveaway", style=discord.ButtonStyle.danger, emoji="🛑")
        self._bot           = bot
        self._message_id    = message_id
        self._prize         = prize
        self._winners_count = winners_count
        self._channel_id    = channel_id
        self._guild_id      = guild_id
        self._host_id       = host_id

    async def callback(self, interaction: discord.Interaction):
        confirm_view = discord.ui.LayoutView()
        confirm_view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(interaction, "end_confirmed")),
            accent_colour=discord.Color.green()
        ))
        await interaction.response.edit_message(view=confirm_view)

        giveaway_cog = self._bot.get_cog("Giveaway")
        if giveaway_cog:
            await giveaway_cog.end_giveaway(
                self._message_id, self._channel_id, self._guild_id,
                self._prize, self._winners_count, self._host_id,
            )


class _MgmtSelectBtn(discord.ui.Button):
    def __init__(self, bot, message_id):
        super().__init__(label="Select Random", style=discord.ButtonStyle.secondary, emoji=f"{get_emoji('icon_gambling')}")
        self._bot        = bot
        self._message_id = message_id

    async def callback(self, interaction: discord.Interaction):
        rows = await self._bot.cxn.fetch(
            "SELECT user_id FROM participants WHERE message_id = $1", self._message_id
        )
        participants = [row["user_id"] for row in rows]

        if not participants:
            empty_view = discord.ui.LayoutView()
            empty_view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=msg(interaction, "select_no_entries")),
                accent_colour=discord.Color.orange()
            ))
            return await interaction.response.edit_message(view=empty_view)

        winner      = random.choice(participants)
        result_view = discord.ui.LayoutView()
        result_view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(interaction, "select_result", mention=f"<@{winner}>")),
            accent_colour=discord.Color.green()
        ))
        await interaction.response.edit_message(view=result_view)


class _MgmtParticipantsBtn(discord.ui.Button):
    def __init__(self, bot, message_id):
        super().__init__(label="Participants", style=discord.ButtonStyle.blurple, emoji="👥")
        self._bot        = bot
        self._message_id = message_id

    async def callback(self, interaction: discord.Interaction):
        rows = await self._bot.cxn.fetch(
            "SELECT user_id FROM participants WHERE message_id = $1", self._message_id
        )
        if not rows:
            empty_view = discord.ui.LayoutView()
            empty_view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {msg(interaction, 'participants_title')}\n"
                            f"{msg(interaction, 'participants_empty')}"
                ),
                accent_colour=discord.Color.blurple()
            ))
            return await interaction.response.edit_message(view=empty_view)

        lines             = [f"**{i}.** <@{row['user_id']}>" for i, row in enumerate(rows, 1)]
        pages             = paginate(lines, per_page=15)
        participants_view = PaginatedView(
            title=msg(interaction, "participants_title"),
            pages=pages,
            icon_url=interaction.guild.icon.url if interaction.guild and interaction.guild.icon else None,
        )
        await interaction.response.edit_message(view=participants_view)


# ─────────────────────────────────────────────────────────────
#  VIEW BUILDERS
# ─────────────────────────────────────────────────────────────

def _build_content_view(prize: str, end_timestamp: int, winners_count: int,
                        author_mention: str, guild=None) -> discord.ui.LayoutView:
    """
    Layout-only view (no buttons).  Sent first so we can obtain the message_id,
    then immediately edited to add interactive buttons.
    """
    s      = "s" if winners_count > 1 else ""
    footer = _guild_msg(guild, "footer_active", count=winners_count, s=s)

    view      = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {get_emoji('icon_giveaway')} {_guild_msg(guild, 'giveaway_title')}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=(
                f"**{_guild_msg(guild, 'label_prize')}:** {prize}\n"
                f"**{_guild_msg(guild, 'label_ends')}:** <t:{end_timestamp}:R> (<t:{end_timestamp}:f>)\n"
                f"**{_guild_msg(guild, 'label_hosted_by')}:** {author_mention}"
            )
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=f"-# {footer} <t:{end_timestamp}:f>"),
        accent_colour=discord.Color.purple()
    )
    view.add_item(container)
    return view


def _build_active_view(bot, message_id: int, prize: str, end_timestamp: int,
                       winners_count: int, author_mention: str,
                       guild=None) -> discord.ui.LayoutView:
    """Full active giveaway view with interactive Join + Manage buttons."""
    s      = "s" if winners_count > 1 else ""
    footer = _guild_msg(guild, "footer_active", count=winners_count, s=s)

    view      = discord.ui.LayoutView(timeout=None)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {get_emoji('icon_giveaway')} {_guild_msg(guild, 'giveaway_title')}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=(
                f"**{_guild_msg(guild, 'label_prize')}:** {prize}\n"
                f"**{_guild_msg(guild, 'label_ends')}:** <t:{end_timestamp}:R> (<t:{end_timestamp}:f>)\n"
                f"**{_guild_msg(guild, 'label_hosted_by')}:** {author_mention}"
            )
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            _GiveawayJoinBtn(bot, message_id),
            _GiveawayManageBtn(bot, message_id),
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=f"-# {footer} <t:{end_timestamp}:f>"),
        accent_colour=discord.Color.purple()
    )
    view.add_item(container)
    return view


def _build_ended_view(guild, prize: str, host_id: int,
                      winners: list = None) -> discord.ui.LayoutView:
    if winners:
        winner_mentions = ", ".join(f"<@{w}>" for w in winners)
        result_text = (
            f"**{_guild_msg(guild, 'label_prize')}:** {prize}\n"
            f"**{_guild_msg(guild, 'label_hosted_by')}:** <@{host_id}>\n"
            f"**{_guild_msg(guild, 'label_winner')}:** {winner_mentions}"
        )
    else:
        result_text = (
            f"**{_guild_msg(guild, 'label_prize')}:** {prize}\n"
            f"**{_guild_msg(guild, 'label_hosted_by')}:** <@{host_id}>\n"
            f"**{_guild_msg(guild, 'label_no_participants')}**"
        )

    view      = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {get_emoji('icon_giveaway')} {_guild_msg(guild, 'giveaway_ended_title')}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=result_text),
        accent_colour=discord.Color.gold()
    )
    view.add_item(container)
    return view


def _build_manage_panel(bot, giveaway_row, guild=None) -> discord.ui.LayoutView:
    message_id    = giveaway_row["message_id"]
    prize         = giveaway_row["prize"]
    winners_count = giveaway_row["winners_count"]
    channel_id    = giveaway_row["channel_id"]
    guild_id      = giveaway_row["guild_id"]
    host_id       = giveaway_row["host_id"]

    view      = discord.ui.LayoutView(timeout=180)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {_guild_msg(guild, 'manage_title')}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=(
                f"**{_guild_msg(guild, 'label_prize')}:** {prize}\n"
                f"**{_guild_msg(guild, 'label_hosted_by')}:** <@{host_id}>\n\n"
                f"{_guild_msg(guild, 'manage_info')}"
            )
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            _MgmtEndBtn(bot, message_id, prize, winners_count, channel_id, guild_id, host_id),
            _MgmtSelectBtn(bot, message_id),
            _MgmtParticipantsBtn(bot, message_id),
        ),
        accent_colour=discord.Color.purple()
    )
    view.add_item(container)
    return view


# ─────────────────────────────────────────────────────────────
#  INTERACTIVE SETUP — `.giveaway start` panel
# ─────────────────────────────────────────────────────────────

def _parse_duration_str(value: str) -> int:
    """Mirror of ``Giveaway.parse_duration`` but free-standing for the setup view."""
    m = re.match(r"\s*([\d\.]+)\s*([smhd])\s*$", value.lower())
    if not m:
        return -1
    try:
        amount = float(m.group(1))
        unit   = m.group(2)
        return int(amount * {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit])
    except ValueError:
        return -1


def _format_duration(seconds: int) -> str:
    if seconds <= 0:
        return "—"
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    bits = []
    if days:    bits.append(f"{days}d")
    if hours:   bits.append(f"{hours}h")
    if minutes: bits.append(f"{minutes}m")
    if secs:    bits.append(f"{secs}s")
    return " ".join(bits) if bits else "—"


class _SetupState:
    """Mutable state held by an in-flight giveaway-setup view."""
    __slots__ = ("prize", "duration_s", "winners", "channel_id", "requirements")

    def __init__(self, channel_id: int):
        self.prize: str | None         = None
        self.duration_s: int           = 0
        self.winners: int              = 1
        self.channel_id: int           = channel_id
        self.requirements: dict        = dict(DEFAULT_REQUIREMENTS)
        self.requirements["role_ids"] = []


def _build_setup_view(bot, ctx_or_inter, state: _SetupState, host_id: int) -> "_GiveawaySetupView":
    return _GiveawaySetupView(bot, ctx_or_inter, state, host_id)


# ── Modals ──────────────────────────────────────────────────

class _PrizeModal(discord.ui.Modal, title="Set Prize"):
    prize = discord.ui.TextInput(
        label="Prize", placeholder="e.g. Discord Nitro (1 month)",
        max_length=200, required=True, style=discord.TextStyle.short,
    )

    def __init__(self, parent: "_GiveawaySetupView"):
        super().__init__()
        self._setup_view = parent
        if parent.state.prize:
            self.prize.default = parent.state.prize

    async def on_submit(self, interaction: discord.Interaction):
        self._setup_view.state.prize = self.prize.value.strip()
        await self._setup_view.refresh(interaction)


class _DurationModal(discord.ui.Modal, title="Set Duration"):
    duration = discord.ui.TextInput(
        label="Duration", placeholder="30s · 10m · 2h · 1d",
        max_length=20, required=True, style=discord.TextStyle.short,
    )

    def __init__(self, parent: "_GiveawaySetupView"):
        super().__init__()
        self._setup_view = parent

    async def on_submit(self, interaction: discord.Interaction):
        seconds = _parse_duration_str(self.duration.value)
        if seconds <= 0:
            return await interaction.response.send_message(
                msg(interaction, "invalid_duration"), ephemeral=True
            )
        self._setup_view.state.duration_s = seconds
        await self._setup_view.refresh(interaction)


class _WinnersModal(discord.ui.Modal, title="Set Winners"):
    winners = discord.ui.TextInput(
        label="Winners", placeholder="1",
        max_length=4, required=True, style=discord.TextStyle.short,
    )

    def __init__(self, parent: "_GiveawaySetupView"):
        super().__init__()
        self._setup_view = parent
        self.winners.default = str(parent.state.winners)

    async def on_submit(self, interaction: discord.Interaction):
        digits = "".join(ch for ch in self.winners.value if ch.isdigit())
        if not digits or int(digits) < 1:
            return await interaction.response.send_message(
                msg(interaction, "min_one_winner"), ephemeral=True
            )
        self._setup_view.state.winners = int(digits)
        await self._setup_view.refresh(interaction)


class _AccountAgeModal(discord.ui.Modal, title="Minimum Account Age"):
    days = discord.ui.TextInput(
        label="Account age in days (0 = no requirement)",
        placeholder="e.g. 7", max_length=5, required=True,
        style=discord.TextStyle.short,
    )

    def __init__(self, parent: "_GiveawaySetupView"):
        super().__init__()
        self._setup_view = parent
        self.days.default = str(parent.state.requirements["account_age_days"])

    async def on_submit(self, interaction: discord.Interaction):
        digits = "".join(ch for ch in self.days.value if ch.isdigit())
        value = int(digits) if digits else 0
        self._setup_view.state.requirements["account_age_days"] = max(0, min(value, 3650))
        await self._setup_view.refresh(interaction)


class _ServerAgeModal(discord.ui.Modal, title="Minimum Time in Server"):
    days = discord.ui.TextInput(
        label="Days in server (0 = no requirement)",
        placeholder="e.g. 3", max_length=5, required=True,
        style=discord.TextStyle.short,
    )

    def __init__(self, parent: "_GiveawaySetupView"):
        super().__init__()
        self._setup_view = parent
        self.days.default = str(parent.state.requirements["server_age_days"])

    async def on_submit(self, interaction: discord.Interaction):
        digits = "".join(ch for ch in self.days.value if ch.isdigit())
        value = int(digits) if digits else 0
        self._setup_view.state.requirements["server_age_days"] = max(0, min(value, 3650))
        await self._setup_view.refresh(interaction)


# ── Buttons ─────────────────────────────────────────────────

class _SetupBtn(discord.ui.Button):
    def __init__(self, label: str, style, emoji, parent: "_GiveawaySetupView", action: str,
                 *, row: int = 0):
        super().__init__(label=label, style=style, emoji=emoji)
        self._setup_view = parent
        self.action = action

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self._setup_view.host_id:
            return await interaction.response.send_message(
                f"{get_emoji('icon_cross')} Only the host of this setup can configure this giveaway.",
                ephemeral=True,
            )
        action = self.action
        if action == "prize":
            return await interaction.response.send_modal(_PrizeModal(self._setup_view))
        if action == "duration":
            return await interaction.response.send_modal(_DurationModal(self._setup_view))
        if action == "winners":
            return await interaction.response.send_modal(_WinnersModal(self._setup_view))
        if action == "account_age":
            return await interaction.response.send_modal(_AccountAgeModal(self._setup_view))
        if action == "server_age":
            return await interaction.response.send_modal(_ServerAgeModal(self._setup_view))
        if action == "boost":
            self._setup_view.state.requirements["boost_required"] = (
                not self._setup_view.state.requirements["boost_required"]
            )
            return await self._setup_view.refresh(interaction)
        if action == "clear_roles":
            self._setup_view.state.requirements["role_ids"] = []
            return await self._setup_view.refresh(interaction)
        if action == "cancel":
            cancelled = discord.ui.LayoutView()
            cancelled.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content="🗑 Giveaway setup cancelled."),
                accent_colour=discord.Color.red(),
            ))
            return await interaction.response.edit_message(view=cancelled)
        if action == "start":
            return await self._setup_view.launch(interaction)


class _SetupChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, parent: "_GiveawaySetupView"):
        super().__init__(
            placeholder="Pick the channel to host the giveaway in…",
            channel_types=[discord.ChannelType.text, discord.ChannelType.news],
            min_values=1, max_values=1,
        )
        self._setup_view = parent

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self._setup_view.host_id:
            return await interaction.response.send_message(
                "{get_emoji('icon_cross')} Only the host can configure this giveaway.", ephemeral=True
            )
        self._setup_view.state.channel_id = self.values[0].id
        await self._setup_view.refresh(interaction)


class _SetupRoleSelect(discord.ui.RoleSelect):
    def __init__(self, parent: "_GiveawaySetupView"):
        super().__init__(
            placeholder="Pick required roles (entrants must hold all)…",
            min_values=0, max_values=10,
        )
        self._setup_view = parent

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self._setup_view.host_id:
            return await interaction.response.send_message(
                "{get_emoji('icon_cross')} Only the host can configure this giveaway.", ephemeral=True
            )
        self._setup_view.state.requirements["role_ids"] = [r.id for r in self.values]
        await self._setup_view.refresh(interaction)


# ── Setup view ─────────────────────────────────────────────

class _GiveawaySetupView(discord.ui.LayoutView):
    """Interactive panel returned by ``.giveaway start``."""

    def __init__(self, bot, ctx_or_inter, state: _SetupState, host_id: int):
        super().__init__(timeout=600)
        self.bot       = bot
        self.state     = state
        self.host_id   = host_id
        self.guild     = getattr(ctx_or_inter, "guild", None)
        self.message: discord.Message | None = None  # set after the first send
        self._build()

    # ── building ───────────────────────────────────────

    def _build(self):
        self.clear_items()
        s = self.state
        guild = self.guild

        channel_disp = f"<#{s.channel_id}>" if s.channel_id else "—"
        prize_disp   = s.prize if s.prize else "_not set_"
        dur_disp     = _format_duration(s.duration_s)

        summary = (
            f"**Prize:** {prize_disp}\n"
            f"**Duration:** {dur_disp}\n"
            f"**Winners:** {s.winners}\n"
            f"**Channel:** {channel_disp}"
        )
        reqs_text = _requirements_summary(s.requirements, guild)

        boost_label = (
            "Booster Only ✓" if s.requirements["boost_required"] else "Booster Only"
        )
        boost_style = (
            discord.ButtonStyle.success if s.requirements["boost_required"]
            else discord.ButtonStyle.secondary
        )

        ready = bool(s.prize) and s.duration_s > 0 and s.channel_id
        start_style = discord.ButtonStyle.success if ready else discord.ButtonStyle.secondary

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_giveaway')} Giveaway Setup"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=summary),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=f"**Requirements**\n{reqs_text}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _SetupBtn("Prize",    discord.ButtonStyle.primary,   "🎁", self, "prize"),
                _SetupBtn("Duration", discord.ButtonStyle.primary,   "⏳", self, "duration"),
                _SetupBtn("Winners",  discord.ButtonStyle.primary,   "🏆", self, "winners"),
            ),
            discord.ui.ActionRow(_SetupChannelSelect(self)),
            discord.ui.ActionRow(_SetupRoleSelect(self)),
            discord.ui.ActionRow(
                _SetupBtn("Account Age", discord.ButtonStyle.secondary, "📅", self, "account_age"),
                _SetupBtn("Server Time", discord.ButtonStyle.secondary, "🏠", self, "server_age"),
                _SetupBtn(boost_label,   boost_style,                   "💎", self, "boost"),
                _SetupBtn("Clear Roles", discord.ButtonStyle.secondary, "🧹", self, "clear_roles"),
            ),
            discord.ui.ActionRow(
                _SetupBtn("Start Giveaway", start_style,                 f"{get_emoji('icon_giveaway')}", self, "start"),
                _SetupBtn("Cancel",         discord.ButtonStyle.danger,  "🗑", self, "cancel"),
            ),
            accent_colour=discord.Color.purple(),
        )
        self.add_item(container)

    async def refresh(self, interaction: discord.Interaction):
        self._build()
        await interaction.response.edit_message(view=self)

    async def on_timeout(self):
        if self.message is None:
            return
        try:
            timeout_view = discord.ui.LayoutView()
            timeout_view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content="⌛ Giveaway setup timed out."),
                accent_colour=discord.Color.greyple(),
            ))
            await self.message.edit(view=timeout_view)
        except discord.HTTPException:
            pass

    # ── launching the giveaway from setup state ─────────

    async def launch(self, interaction: discord.Interaction):
        s = self.state
        problems = []
        if not s.prize:
            problems.append("- Prize is not set")
        if s.duration_s <= 0:
            problems.append("- Duration is not set")
        if not s.channel_id:
            problems.append("- Channel is not set")
        if problems:
            return await interaction.response.send_message(
                "{get_emoji('icon_cross')} Can't start the giveaway yet:\n" + "\n".join(problems),
                ephemeral=True,
            )

        guild   = interaction.guild
        channel = guild.get_channel(s.channel_id) if guild else None
        if channel is None:
            return await interaction.response.send_message(
                "{get_emoji('icon_cross')} I can't find the configured channel anymore.", ephemeral=True
            )
        me = guild.me if guild else None
        if me and not channel.permissions_for(me).send_messages:
            return await interaction.response.send_message(
                f"{get_emoji('icon_cross')} I can't send messages in {channel.mention}.", ephemeral=True
            )

        end_time      = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=s.duration_s)
        end_timestamp = int(end_time.timestamp())
        author_mention = f"<@{self.host_id}>"

        # Step 1: send a stub message in the chosen channel to obtain its ID.
        content_view = _build_content_view(
            s.prize, end_timestamp, s.winners, author_mention, guild
        )
        sent = await channel.send(view=content_view)

        # Step 2: register persistent buttons + edit them in.
        active_view = _build_active_view(
            self.bot, sent.id, s.prize, end_timestamp, s.winners,
            author_mention, guild,
        )
        persistent_view = _make_persistent_view(self.bot, sent.id)
        self.bot.add_view(persistent_view, message_id=sent.id)
        await sent.edit(view=active_view)

        # Step 3: persist everything to the DB, including requirements.
        await self.bot.cxn.execute(
            "INSERT INTO giveaways "
            "(message_id, channel_id, guild_id, prize, winners_count, end_time, ended, host_id, requirements) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
            sent.id, channel.id, guild.id,
            s.prize, s.winners, end_time.isoformat(), False, self.host_id,
            _dump_reqs(s.requirements),
        )

        # Step 4: collapse the setup panel.
        done_view = discord.ui.LayoutView()
        reqs_line = _requirements_summary(s.requirements, guild)
        done_view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    f"### {get_emoji('icon_tick')} Giveaway started!\n"
                    f"**Prize:** {s.prize}\n"
                    f"**Channel:** {channel.mention}\n"
                    f"**Ends:** <t:{end_timestamp}:R>\n\n"
                    f"**Requirements**\n{reqs_line}"
                )
            ),
            accent_colour=discord.Color.green(),
        ))
        await interaction.response.edit_message(view=done_view)


# ─────────────────────────────────────────────────────────────
#  GIVEAWAY COG
# ─────────────────────────────────────────────────────────────


__all__ = [k for k in list(globals()) if not k.startswith("__")]
