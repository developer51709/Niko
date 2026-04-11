import discord
from discord.ext import commands, tasks
import re
import datetime
import random
import asyncio

from utils.paginator import PaginatedView, paginate

PERSONALITY = "cafe"

# ─────────────────────────────────────────────────────────────
#  MESSAGE TABLE
# ─────────────────────────────────────────────────────────────

MESSAGES = {
    "normal": {
        "en": {
            "giveaway_title":         "🎉 Giveaway",
            "giveaway_ended_title":   "🎉 Giveaway Ended!",
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
            "ending_early":           "✅ Giveaway ended! Winners have been announced.",
            "no_perm_end":            "❌ Only the giveaway host or a bot owner can end this giveaway early.",
            "no_perm_select":         "❌ Only the giveaway host or a bot owner can select users.",
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
            "end_confirmed":          "✅ The giveaway has been ended. Winners have been announced in the channel.",
            "participants_title":     "👥 Participants",
            "participants_empty":     "Nobody has joined the giveaway yet.",
        },
        "de": {
            "giveaway_title":         "🎉 Gewinnspiel",
            "giveaway_ended_title":   "🎉 Gewinnspiel beendet!",
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
            "ending_early":           "✅ Gewinnspiel beendet! Gewinner wurden bekannt gegeben.",
            "no_perm_end":            "❌ Nur der Veranstalter oder ein Bot-Besitzer kann das Gewinnspiel vorzeitig beenden.",
            "no_perm_select":         "❌ Nur der Veranstalter oder ein Bot-Besitzer kann Nutzer auswählen.",
            "no_participants_yet":    "Noch niemand hat am Gewinnspiel teilgenommen.",
            "reroll_no_participants": "❌ Niemand hat teilgenommen, daher kann niemand erneut gezogen werden!",
            "reroll_not_ended":       "❌ Dieses Gewinnspiel ist noch nicht beendet! Rerolls sind nur für beendete Gewinnspiele.",
            "reroll_not_found":       "❌ Kein Gewinnspiel mit dieser Nachrichten-ID gefunden.",
            "invalid_duration":       "❌ Ungültige Dauer! Benutze Zahlen mit `s`, `m`, `h` oder `d` (z.B. `30s`, `10m`, `2h`, `1d`).",
            "invalid_winners":        "❌ Ungültige Gewinneranzahl! Muss eine Zahl sein (z.B. `2`).",
            "min_one_winner":         "❌ Es muss mindestens 1 Gewinner geben!",
            "footer_active":          "{count} Gewinner | Endet um",
            "manage_title":           "⚙️ Gewinnspiel-Verwaltung",
            "manage_info":            "Nutze die Schaltflächen unten, um das Gewinnspiel zu verwalten.",
            "select_result":          "🎲 Zufällig ausgewählt: {mention}",
            "select_no_entries":      "Noch niemand hat am Gewinnspiel teilgenommen, daher kann niemand ausgewählt werden.",
            "end_confirmed":          "✅ Das Gewinnspiel wurde beendet. Gewinner wurden im Channel bekannt gegeben.",
            "participants_title":     "👥 Teilnehmer",
            "participants_empty":     "Noch niemand hat am Gewinnspiel teilgenommen.",
        },
    },
    "cafe": {
        "en": {
            "giveaway_title":         "🎉 Giveaway",
            "giveaway_ended_title":   "🎉 Giveaway Ended ☕",
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
            "ending_early":           "✅ giveaway ended! winners have been announced~",
            "no_perm_end":            "☕ only the host or a bot owner can end this early.",
            "no_perm_select":         "☕ only the host or a bot owner can pick someone.",
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
            "end_confirmed":          "✅ giveaway ended~ winners have been announced in the channel ☕",
            "participants_title":     "☕ participants",
            "participants_empty":     "nobody has joined yet 😔",
        },
        "de": {
            "giveaway_title":         "🎉 Gewinnspiel",
            "giveaway_ended_title":   "🎉 Gewinnspiel vorbei ☕",
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
            "ending_early":           "✅ gewinnspiel beendet~ gewinner wurden bekannt gegeben ☕",
            "no_perm_end":            "☕ nur der veranstalter oder ein bot-besitzer kann das früh beenden.",
            "no_perm_select":         "☕ nur der veranstalter oder ein bot-besitzer kann jemanden auswählen.",
            "no_participants_yet":    "noch niemand hat mitgemacht 😔",
            "reroll_no_participants": "😔 niemand war dabei, also gibt's niemanden zum rerolln!",
            "reroll_not_ended":       "😔 das gewinnspiel ist noch nicht vorbei! rerolls gibt's nur für beendete.",
            "reroll_not_found":       "😔 kein gewinnspiel mit dieser nachrichten-id gefunden.",
            "invalid_duration":       "❌ ungültige dauer! benutze zahlen mit `s`, `m`, `h` oder `d` (z.b. `30s`, `10m`, `2h`, `1d`)",
            "invalid_winners":        "❌ ungültige gewinneranzahl! muss eine zahl sein (z.b. `2`).",
            "min_one_winner":         "❌ es braucht mindestens 1 gewinner!",
            "footer_active":          "{count} gewinner | endet um",
            "manage_title":           "⚙️ gewinnspiel-verwaltung",
            "manage_info":            "nutze die schaltflächen unten, um das gewinnspiel zu verwalten ☕",
            "select_result":          "🎲 zufällig ausgewählt: {mention}",
            "select_no_entries":      "noch niemand ist dabei, also kann niemand ausgewählt werden 😔",
            "end_confirmed":          "✅ gewinnspiel beendet~ gewinner wurden im channel bekannt gegeben ☕",
            "participants_title":     "☕ teilnehmer",
            "participants_empty":     "noch niemand hat mitgemacht 😔",
        },
    },
}


def _get_lang(obj) -> str:
    guild = getattr(obj, "guild", None)
    if guild and getattr(guild, "preferred_locale", None):
        if str(guild.preferred_locale).lower().startswith("de"):
            return "de"
    return "en"


def msg(obj, key: str, **kwargs) -> str:
    p    = PERSONALITY if PERSONALITY in MESSAGES else "normal"
    lang = _get_lang(obj)
    text = MESSAGES.get(p, {}).get(lang, {}).get(key)
    if text is None:
        text = MESSAGES.get(p, {}).get("en", {}).get(key)
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
#  VIEW BUILDERS
# ─────────────────────────────────────────────────────────────

def _build_active_view(bot, prize: str, end_timestamp: int,
                       winners_count: int, author_mention: str,
                       guild=None) -> discord.ui.LayoutView:
    s      = "s" if winners_count > 1 else ""
    footer = _guild_msg(guild, "footer_active", count=winners_count, s=s)

    view      = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {_guild_msg(guild, 'giveaway_title')}"),
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
            JoinGiveawayBtn(bot),
            ManageGiveawayBtn(bot),
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
        discord.ui.TextDisplay(content=f"### {_guild_msg(guild, 'giveaway_ended_title')}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=result_text),
        accent_colour=discord.Color.gold()
    )
    view.add_item(container)
    return view


def _build_manage_panel(bot, giveaway_row, guild=None) -> discord.ui.LayoutView:
    """Build the ephemeral management panel shown only to host/admins."""
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
#  MANAGEMENT PANEL BUTTONS  (ephemeral — no persistent custom_id needed)
# ─────────────────────────────────────────────────────────────

class _MgmtEndBtn(discord.ui.Button):
    def __init__(self, bot, message_id, prize, winners_count, channel_id, guild_id, host_id):
        super().__init__(label="End Giveaway", style=discord.ButtonStyle.danger, emoji="🛑")
        self._bot          = bot
        self._message_id   = message_id
        self._prize        = prize
        self._winners_count = winners_count
        self._channel_id   = channel_id
        self._guild_id     = guild_id
        self._host_id      = host_id

    async def callback(self, interaction: discord.Interaction):
        # Edit the ephemeral panel first so the interaction is acknowledged
        confirm_view = discord.ui.LayoutView()
        confirm_view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(interaction, "end_confirmed")),
            accent_colour=discord.Color.green()
        ))
        await interaction.response.edit_message(view=confirm_view)

        # End the giveaway
        giveaway_cog = self._bot.get_cog("Giveaway")
        if giveaway_cog:
            await giveaway_cog.end_giveaway(
                self._message_id, self._channel_id, self._guild_id,
                self._prize, self._winners_count, self._host_id,
            )


class _MgmtSelectBtn(discord.ui.Button):
    def __init__(self, bot, message_id):
        super().__init__(label="Select Random", style=discord.ButtonStyle.secondary, emoji="🎲")
        self._bot        = bot
        self._message_id = message_id

    async def callback(self, interaction: discord.Interaction):
        rows = await self._bot.cxn.fetch(
            "SELECT user_id FROM participants WHERE message_id = $1", self._message_id
        )
        participants = [row["user_id"] for row in rows]

        if not participants:
            result_view = discord.ui.LayoutView()
            result_view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=msg(interaction, "select_no_entries")),
                accent_colour=discord.Color.orange()
            ))
            return await interaction.response.edit_message(view=result_view)

        winner = random.choice(participants)
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

        lines = [f"**{i}.** <@{row['user_id']}>" for i, row in enumerate(rows, 1)]
        pages = paginate(lines, per_page=15)
        participants_view = PaginatedView(
            title=msg(interaction, "participants_title"),
            pages=pages,
            icon_url=interaction.guild.icon.url if interaction.guild and interaction.guild.icon else None,
        )
        await interaction.response.edit_message(view=participants_view)


# ─────────────────────────────────────────────────────────────
#  MAIN GIVEAWAY BUTTONS  (persistent — survive restarts)
# ─────────────────────────────────────────────────────────────

class JoinGiveawayBtn(discord.ui.Button):
    def __init__(self, bot):
        super().__init__(
            label="Join",
            style=discord.ButtonStyle.primary,
            emoji="🎉",
            custom_id="giveaway_system_join",
        )
        self._bot = bot

    async def callback(self, interaction: discord.Interaction):
        message_id = interaction.message.id
        user_id    = interaction.user.id

        giveaway = await self._bot.cxn.fetchrow(
            "SELECT host_id, ended FROM giveaways WHERE message_id = $1", message_id
        )
        if not giveaway:
            return await interaction.response.send_message(msg(interaction, "no_exist"), ephemeral=True)
        if giveaway["ended"]:
            return await interaction.response.send_message(msg(interaction, "join_ended"), ephemeral=True)
        if user_id == giveaway["host_id"]:
            return await interaction.response.send_message(msg(interaction, "join_host"), ephemeral=True)
        if interaction.user.bot:
            return await interaction.response.send_message(msg(interaction, "join_bot"), ephemeral=True)

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


class ManageGiveawayBtn(discord.ui.Button):
    def __init__(self, bot):
        super().__init__(
            label="Manage",
            style=discord.ButtonStyle.secondary,
            emoji="⚙️",
            custom_id="giveaway_system_manage",
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

        # Gate: host or server admin only
        is_host  = interaction.user.id == giveaway["host_id"]
        is_admin = interaction.user.guild_permissions.manage_guild
        if not (is_host or is_admin):
            return await interaction.response.send_message(
                msg(interaction, "no_perm_manage"), ephemeral=True
            )

        panel = _build_manage_panel(self._bot, giveaway, interaction.guild)
        await interaction.response.send_message(view=panel, ephemeral=True)


# ─────────────────────────────────────────────────────────────
#  PERSISTENT VIEW — registered on startup for post-restart dispatch
# ─────────────────────────────────────────────────────────────

class GiveawayPersistentView(discord.ui.View):
    """Holds only the two main-message buttons — registered with bot.add_view()."""

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(JoinGiveawayBtn(bot))
        self.add_item(ManageGiveawayBtn(bot))


# ─────────────────────────────────────────────────────────────
#  GIVEAWAY COG
# ─────────────────────────────────────────────────────────────

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    async def cog_load(self):
        # Register persistent view so Discord re-dispatches button clicks after restart
        self.bot.add_view(GiveawayPersistentView(self.bot))

        await self.bot.cxn.execute("""
            CREATE TABLE IF NOT EXISTS giveaways (
                message_id    INTEGER PRIMARY KEY,
                channel_id    INTEGER,
                guild_id      INTEGER,
                prize         TEXT,
                winners_count INTEGER,
                end_time      TEXT,
                ended         BOOLEAN DEFAULT 0,
                host_id       INTEGER
            )
        """)
        await self.bot.cxn.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                message_id INTEGER,
                user_id    INTEGER,
                PRIMARY KEY (message_id, user_id)
            )
        """)

        # Sanitise any rows with unparseable end_time left by old bugs
        await self.bot.cxn.execute(
            "UPDATE giveaways SET ended = 1 WHERE ended = 0 AND end_time NOT LIKE '____-%'"
        )

    async def cog_unload(self):
        self.check_giveaways.cancel()

    # ─── HELPERS ─────────────────────────────────────────────

    def parse_duration(self, duration_str: str) -> int:
        m = re.match(r"([\d\.]+)([smhd])", duration_str.lower())
        if not m:
            return -1
        try:
            value = float(m.group(1))
            unit  = m.group(2)
            return int(value * {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit])
        except ValueError:
            return -1

    # ─── COMMANDS ─────────────────────────────────────────────

    @commands.group(name="giveaway", aliases=["g"], invoke_without_command=True)
    async def giveaway(self, ctx):
        """Manage giveaways."""
        await ctx.send_help(ctx.command)

    @giveaway.command(name="start")
    @commands.has_permissions(manage_guild=True)
    async def start(self, ctx, duration: str, winners: str, *, prize: str):
        """Start a new giveaway.  Usage: .giveaway start <duration> <winners> <prize>"""
        seconds = self.parse_duration(duration)
        if seconds <= 0:
            return await ctx.send(msg(ctx, "invalid_duration"))

        winners_clean = "".join(filter(str.isdigit, winners))
        if not winners_clean:
            return await ctx.send(msg(ctx, "invalid_winners"))
        winners_count = int(winners_clean)
        if winners_count < 1:
            return await ctx.send(msg(ctx, "min_one_winner"))

        end_time      = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=seconds)
        end_timestamp = int(end_time.timestamp())

        view = _build_active_view(
            self.bot, prize, end_timestamp, winners_count,
            ctx.author.mention, ctx.guild
        )
        sent = await ctx.send(view=view)

        await self.bot.cxn.execute(
            "INSERT INTO giveaways "
            "(message_id, channel_id, guild_id, prize, winners_count, end_time, ended, host_id) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
            sent.id, ctx.channel.id, ctx.guild.id,
            prize, winners_count, end_time.isoformat(), False, ctx.author.id
        )

    @giveaway.command(name="reroll")
    @commands.has_permissions(manage_guild=True)
    async def reroll(self, ctx, message_id: int):
        """Reroll a finished giveaway to pick a new winner."""
        giveaway = await self.bot.cxn.fetchrow(
            "SELECT prize, winners_count, ended FROM giveaways WHERE message_id = $1", message_id
        )
        if not giveaway:
            return await ctx.send(msg(ctx, "reroll_not_found"))
        if not giveaway["ended"]:
            return await ctx.send(msg(ctx, "reroll_not_ended"))

        rows = await self.bot.cxn.fetch(
            "SELECT user_id FROM participants WHERE message_id = $1", message_id
        )
        participants = [row["user_id"] for row in rows]
        if not participants:
            return await ctx.send(msg(ctx, "reroll_no_participants"))

        new_winners     = random.sample(participants, 1)
        winner_mentions = ", ".join(f"<@{w}>" for w in new_winners)
        await ctx.send(msg(ctx, "reroll_announce", prize=giveaway["prize"], mentions=winner_mentions))

    # ─── BACKGROUND TASK ─────────────────────────────────────

    @tasks.loop(seconds=15)
    async def check_giveaways(self):
        try:
            now  = datetime.datetime.now(datetime.timezone.utc)
            rows = await self.bot.cxn.fetch(
                "SELECT message_id, channel_id, guild_id, prize, winners_count, end_time, host_id "
                "FROM giveaways WHERE ended = 0"
            )
            for row in rows:
                message_id   = row["message_id"]
                end_time_str = row["end_time"]
                try:
                    end_time = datetime.datetime.fromisoformat(str(end_time_str))
                    if end_time.tzinfo is None:
                        end_time = end_time.replace(tzinfo=datetime.timezone.utc)
                except (TypeError, ValueError):
                    await self.bot.cxn.execute(
                        "UPDATE giveaways SET ended = 1 WHERE message_id = $1", message_id
                    )
                    continue

                if now >= end_time:
                    await self.end_giveaway(
                        message_id, row["channel_id"], row["guild_id"],
                        row["prize"], row["winners_count"], row["host_id"],
                    )
                    await asyncio.sleep(0.1)
        except Exception as e:
            print(f"[Giveaway Task Error] {e}")

    # ─── END GIVEAWAY ─────────────────────────────────────────

    async def end_giveaway(self, message_id, channel_id, guild_id, prize, winners_count, host_id):
        # Mark as ended first to prevent double-triggering
        await self.bot.cxn.execute(
            "UPDATE giveaways SET ended = 1 WHERE message_id = $1", message_id
        )

        channel = self.bot.get_channel(channel_id)
        if not channel:
            try:
                channel = await self.bot.fetch_channel(channel_id)
            except Exception:
                return

        guild = self.bot.get_guild(guild_id) or getattr(channel, "guild", None)

        try:
            giveaway_msg = await channel.fetch_message(message_id)
        except Exception:
            giveaway_msg = None

        rows         = await self.bot.cxn.fetch(
            "SELECT user_id FROM participants WHERE message_id = $1", message_id
        )
        participants = [row["user_id"] for row in rows]
        msg_url      = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"

        if not participants:
            ended_view = _build_ended_view(guild, prize, host_id, winners=None)
            if giveaway_msg:
                try:
                    await giveaway_msg.edit(view=ended_view)
                except Exception:
                    pass
            await channel.send(_guild_msg(guild, "no_participants_msg", prize=prize))
            return

        winner_count    = min(winners_count, len(participants))
        winners         = random.sample(participants, winner_count)
        winner_mentions = ", ".join(f"<@{w}>" for w in winners)

        ended_view = _build_ended_view(guild, prize, host_id, winners=winners)
        if giveaway_msg:
            try:
                await giveaway_msg.edit(view=ended_view)
            except Exception:
                pass

        await channel.send(
            _guild_msg(guild, "winner_announce", mentions=winner_mentions, prize=prize, url=msg_url)
        )

    @check_giveaways.before_loop
    async def before_check_giveaways(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Giveaway(bot))
