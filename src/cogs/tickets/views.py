"""
Premium ticket system — single `ticket` group with admin + in-ticket sub-commands.

Admin sub-commands (manage_guild required):
    ticket setup              — open the configuration panel
    ticket panel              — post the public ticket panel here
    ticket category add/remove/list
    ticket support add/remove/list

In-ticket sub-commands (must be used inside a ticket channel,
support roles or manage_channels):
    ticket add <user>         — grant the user access
    ticket remove <user>      — revoke the user's access
    ticket rename <name>      — rename the channel
    ticket claim              — mark the ticket as claimed by you
    ticket transcript         — generate a text transcript
    ticket close              — soft-close (lock) the ticket
    ticket delete             — delete the ticket channel
"""

from __future__ import annotations

import asyncio
import io
from datetime import datetime, timezone
from typing import Optional

import discord
from discord.ext import commands
from discord.ui import Modal, TextInput

from utils.ticket_utils import (
    get_ticket_config,
    update_ticket_config,
    get_all_ticket_configs,
    find_open_ticket,
)
from utils.ticket_config import TicketConfig
from utils.ai_config import get_personality
from config.emojis import get_emoji


# ───────────────────────────────────────────────────
#  TRILINGUAL MESSAGE TABLE
# ───────────────────────────────────────────────────

MESSAGES = {
    "normal": {
        "en": {
            "panel_default_title":  "Open a Ticket",
            "panel_default_desc":   "Select a category or press the button below to open a ticket.",
            "open_btn":             "Create Ticket",
            "select_category":      "### Select a Category",
            "select_placeholder":   "Select category...",
            "ticket_welcome":       "### {icon} {category} Ticket\nWelcome {mention}! A staff member will be with you shortly.",
            "ticket_created":       "✅ Your ticket has been created: {channel}",
            "panel_updated":        "✅ Ticket panel updated.",
            "panel_posted":         "✅ Ticket panel posted in {channel}.",
            "category_added":       "✅ Added category **{name}**.",
            "category_removed":     "✅ Removed category **{name}**.",
            "category_exists":      "⚠️ Category **{name}** already exists.",
            "category_missing":     "⚠️ Category **{name}** doesn't exist.",
            "categories_empty":     "No categories configured. Tickets will be opened with a single 'General' category.",
            "categories_list":      "### Ticket Categories\n{list}",
            "support_added":        "✅ Added {role} as a support role.",
            "support_removed":      "✅ Removed {role} from support roles.",
            "support_exists":       "⚠️ {role} is already a support role.",
            "support_missing":      "⚠️ {role} is not a support role.",
            "support_empty":        "No support roles configured.",
            "support_list":         "### Support Roles\n{list}",
            "not_in_ticket":        "❌ This command can only be used inside a ticket channel.",
            "no_perm_close":        "❌ You don't have permission to close tickets.",
            "no_perm_delete":       "❌ You don't have permission to delete tickets.",
            "no_perm_manage":       "❌ You don't have permission to manage this ticket.",
            "user_added":           "✅ {user} has been added to the ticket.",
            "user_removed":         "✅ {user} has been removed from the ticket.",
            "user_already_added":   "⚠️ {user} already has access to this ticket.",
            "user_not_in_ticket":   "⚠️ {user} doesn't have access to this ticket.",
            "renamed":              "✅ Ticket renamed to **{name}**.",
            "claimed":              "✅ Ticket claimed by {user}.",
            "already_claimed":      "⚠️ This ticket is already claimed by {user}.",
            "transcript_built":     "📝 Transcript generated.",
            "closing":              "{loading} Closing ticket…",
            "closed":               "🔒 This ticket has been closed by {user}.",
            "deleting":             "🗑️ Deleting this ticket in {seconds}s…",
            "setup_title":          "### {icon} Ticket System Setup",
            "setup_desc":           "Configure your ticket system below. Add categories, set up support roles, then post the panel.",
        },
        "de": {
            "panel_default_title":  "Ticket öffnen",
            "panel_default_desc":   "Wähle eine Kategorie oder drücke den Button unten, um ein Ticket zu öffnen.",
            "open_btn":             "Ticket erstellen",
            "select_category":      "### Wähle eine Kategorie",
            "select_placeholder":   "Kategorie wählen...",
            "ticket_welcome":       "### {icon} {category} Ticket\nWillkommen {mention}! Ein Mitarbeiter ist gleich für dich da.",
            "ticket_created":       "✅ Dein Ticket wurde erstellt: {channel}",
            "panel_updated":        "✅ Ticket-Panel aktualisiert.",
            "panel_posted":         "✅ Ticket-Panel in {channel} gepostet.",
            "category_added":       "✅ Kategorie **{name}** hinzugefügt.",
            "category_removed":     "✅ Kategorie **{name}** entfernt.",
            "category_exists":      "⚠️ Kategorie **{name}** existiert bereits.",
            "category_missing":     "⚠️ Kategorie **{name}** existiert nicht.",
            "categories_empty":     "Keine Kategorien konfiguriert. Tickets werden mit einer einzigen Kategorie 'Allgemein' geöffnet.",
            "categories_list":      "### Ticket-Kategorien\n{list}",
            "support_added":        "✅ {role} als Support-Rolle hinzugefügt.",
            "support_removed":      "✅ {role} aus Support-Rollen entfernt.",
            "support_exists":       "⚠️ {role} ist bereits eine Support-Rolle.",
            "support_missing":      "⚠️ {role} ist keine Support-Rolle.",
            "support_empty":        "Keine Support-Rollen konfiguriert.",
            "support_list":         "### Support-Rollen\n{list}",
            "not_in_ticket":        "❌ Dieser Befehl kann nur in einem Ticket-Kanal verwendet werden.",
            "no_perm_close":        "❌ Du hast keine Berechtigung, Tickets zu schließen.",
            "no_perm_delete":       "❌ Du hast keine Berechtigung, Tickets zu löschen.",
            "no_perm_manage":       "❌ Du hast keine Berechtigung, dieses Ticket zu verwalten.",
            "user_added":           "✅ {user} wurde dem Ticket hinzugefügt.",
            "user_removed":         "✅ {user} wurde aus dem Ticket entfernt.",
            "user_already_added":   "⚠️ {user} hat bereits Zugriff auf dieses Ticket.",
            "user_not_in_ticket":   "⚠️ {user} hat keinen Zugriff auf dieses Ticket.",
            "renamed":              "✅ Ticket umbenannt zu **{name}**.",
            "claimed":              "✅ Ticket beansprucht von {user}.",
            "already_claimed":      "⚠️ Dieses Ticket ist bereits von {user} beansprucht.",
            "transcript_built":     "📝 Transkript erstellt.",
            "closing":              "{loading} Ticket wird geschlossen…",
            "closed":               "🔒 Dieses Ticket wurde von {user} geschlossen.",
            "deleting":             "🗑️ Ticket wird in {seconds}s gelöscht…",
            "setup_title":          "### {icon} Ticketsystem-Einrichtung",
            "setup_desc":           "Konfiguriere dein Ticketsystem unten. Füge Kategorien hinzu, richte Support-Rollen ein und poste dann das Panel.",
        },
        "es": {
            "panel_default_title":  "Abrir un Ticket",
            "panel_default_desc":   "Selecciona una categoría o pulsa el botón a continuación para abrir un ticket.",
            "open_btn":             "Crear Ticket",
            "select_category":      "### Selecciona una categoría",
            "select_placeholder":   "Selecciona categoría...",
            "ticket_welcome":       "### {icon} Ticket de {category}\n¡Bienvenido {mention}! Un miembro del staff estará contigo en breve.",
            "ticket_created":       "✅ Tu ticket ha sido creado: {channel}",
            "panel_updated":        "✅ Panel de tickets actualizado.",
            "panel_posted":         "✅ Panel de tickets publicado en {channel}.",
            "category_added":       "✅ Se añadió la categoría **{name}**.",
            "category_removed":     "✅ Se eliminó la categoría **{name}**.",
            "category_exists":      "⚠️ La categoría **{name}** ya existe.",
            "category_missing":     "⚠️ La categoría **{name}** no existe.",
            "categories_empty":     "No hay categorías configuradas. Los tickets se abrirán con una única categoría 'General'.",
            "categories_list":      "### Categorías de Tickets\n{list}",
            "support_added":        "✅ Se añadió {role} como rol de soporte.",
            "support_removed":      "✅ Se eliminó {role} de los roles de soporte.",
            "support_exists":       "⚠️ {role} ya es un rol de soporte.",
            "support_missing":      "⚠️ {role} no es un rol de soporte.",
            "support_empty":        "No hay roles de soporte configurados.",
            "support_list":         "### Roles de Soporte\n{list}",
            "not_in_ticket":        "❌ Este comando solo se puede usar dentro de un canal de ticket.",
            "no_perm_close":        "❌ No tienes permiso para cerrar tickets.",
            "no_perm_delete":       "❌ No tienes permiso para eliminar tickets.",
            "no_perm_manage":       "❌ No tienes permiso para gestionar este ticket.",
            "user_added":           "✅ {user} ha sido añadido al ticket.",
            "user_removed":         "✅ {user} ha sido eliminado del ticket.",
            "user_already_added":   "⚠️ {user} ya tiene acceso a este ticket.",
            "user_not_in_ticket":   "⚠️ {user} no tiene acceso a este ticket.",
            "renamed":              "✅ Ticket renombrado a **{name}**.",
            "claimed":              "✅ Ticket reclamado por {user}.",
            "already_claimed":      "⚠️ Este ticket ya está reclamado por {user}.",
            "transcript_built":     "📝 Transcripción generada.",
            "closing":              "{loading} Cerrando ticket…",
            "closed":               "🔒 Este ticket ha sido cerrado por {user}.",
            "deleting":             "🗑️ Eliminando este ticket en {seconds}s…",
            "setup_title":          "### {icon} Configuración del Sistema de Tickets",
            "setup_desc":           "Configura tu sistema de tickets a continuación. Añade categorías, configura roles de soporte y luego publica el panel.",
        },
    },
    "cafe": {
        "en": {
            "panel_default_title":  "open a cozy ticket ☕",
            "panel_default_desc":   "pick a category or tap the button below — we'll grab a chair for you ✨",
            "open_btn":             "create ticket",
            "select_category":      "### pick a flavor ☕",
            "select_placeholder":   "choose category...",
            "ticket_welcome":       "### {icon} {category} ticket\nhey {mention} ☕ pull up a chair, the staff will be with you in a moment ✨",
            "ticket_created":       "✅ your cozy ticket is ready over at {channel} ☕",
            "panel_updated":        "✅ ticket panel polished and updated ✨",
            "panel_posted":         "✅ ticket panel served fresh in {channel} ☕",
            "category_added":       "✅ added **{name}** to the menu ☕",
            "category_removed":     "✅ took **{name}** off the menu",
            "category_exists":      "⚠️ **{name}** is already on the menu ☕",
            "category_missing":     "⚠️ no **{name}** on the menu hun~",
            "categories_empty":     "no categories yet — tickets will open under a default 'General' tag ☕",
            "categories_list":      "### ticket menu ☕\n{list}",
            "support_added":        "✅ welcome {role} to the staff lounge ☕",
            "support_removed":      "✅ removed {role} from the staff lounge",
            "support_exists":       "⚠️ {role} is already in the staff lounge ☕",
            "support_missing":      "⚠️ {role} isn't in the staff lounge",
            "support_empty":        "the staff lounge is empty for now ☕",
            "support_list":         "### staff lounge ☕\n{list}",
            "not_in_ticket":        "❌ this only works inside a ticket booth, sweet bean ☕",
            "no_perm_close":        "❌ you can't close tickets, sorry ☕",
            "no_perm_delete":       "❌ you can't delete tickets, sorry ☕",
            "no_perm_manage":       "❌ you can't manage this ticket, sorry ☕",
            "user_added":           "✅ pulled up a chair for {user} ☕",
            "user_removed":         "✅ {user} stepped out of the booth",
            "user_already_added":   "⚠️ {user} is already in the booth ☕",
            "user_not_in_ticket":   "⚠️ {user} isn't in this booth",
            "renamed":              "✅ ticket renamed to **{name}** ✨",
            "claimed":              "✅ {user} grabbed this ticket ☕",
            "already_claimed":      "⚠️ {user} already grabbed this one ☕",
            "transcript_built":     "📝 transcript brewed and ready ☕",
            "closing":              "{loading} closing the booth gently…",
            "closed":               "🔒 closed by {user} — see ya next time ☕",
            "deleting":             "🗑️ wiping the table in {seconds}s…",
            "setup_title":          "### {icon} ticket system setup ☕",
            "setup_desc":           "set up your ticket booth below — add menu items, invite staff, then post the cute panel ✨",
        },
        "de": {
            "panel_default_title":  "ein gemütliches ticket öffnen ☕",
            "panel_default_desc":   "wähle eine kategorie oder tippe den button unten — wir holen dir nen stuhl ✨",
            "open_btn":             "ticket erstellen",
            "select_category":      "### wähl ne sorte ☕",
            "select_placeholder":   "kategorie wählen...",
            "ticket_welcome":       "### {icon} {category} ticket\nhey {mention} ☕ mach's dir gemütlich, jemand vom team kommt gleich ✨",
            "ticket_created":       "✅ dein gemütliches ticket wartet drüben in {channel} ☕",
            "panel_updated":        "✅ ticket-panel poliert und aktualisiert ✨",
            "panel_posted":         "✅ ticket-panel frisch serviert in {channel} ☕",
            "category_added":       "✅ **{name}** zur karte hinzugefügt ☕",
            "category_removed":     "✅ **{name}** von der karte genommen",
            "category_exists":      "⚠️ **{name}** steht schon auf der karte ☕",
            "category_missing":     "⚠️ kein **{name}** auf der karte~",
            "categories_empty":     "noch keine kategorien — tickets öffnen sich mit standard 'Allgemein' ☕",
            "categories_list":      "### ticket-karte ☕\n{list}",
            "support_added":        "✅ willkommen {role} im personal-lounge ☕",
            "support_removed":      "✅ {role} aus der personal-lounge entfernt",
            "support_exists":       "⚠️ {role} ist schon in der personal-lounge ☕",
            "support_missing":      "⚠️ {role} ist nicht in der personal-lounge",
            "support_empty":        "die personal-lounge ist noch leer ☕",
            "support_list":         "### personal-lounge ☕\n{list}",
            "not_in_ticket":        "❌ das geht nur in einer ticket-nische, süßer ☕",
            "no_perm_close":        "❌ du kannst keine tickets schließen, sorry ☕",
            "no_perm_delete":       "❌ du kannst keine tickets löschen, sorry ☕",
            "no_perm_manage":       "❌ du kannst dieses ticket nicht verwalten, sorry ☕",
            "user_added":           "✅ einen stuhl für {user} rangezogen ☕",
            "user_removed":         "✅ {user} ist aus der nische gegangen",
            "user_already_added":   "⚠️ {user} ist schon in der nische ☕",
            "user_not_in_ticket":   "⚠️ {user} ist nicht in dieser nische",
            "renamed":              "✅ ticket umbenannt zu **{name}** ✨",
            "claimed":              "✅ {user} hat dieses ticket übernommen ☕",
            "already_claimed":      "⚠️ {user} hat das schon übernommen ☕",
            "transcript_built":     "📝 transkript frisch aufgebrüht ☕",
            "closing":              "{loading} schließe die nische sanft…",
            "closed":               "🔒 geschlossen von {user} — bis bald ☕",
            "deleting":             "🗑️ tisch wird in {seconds}s abgewischt…",
            "setup_title":          "### {icon} ticketsystem-setup ☕",
            "setup_desc":           "richte deine ticket-nische ein — kategorien hinzufügen, personal einladen, dann das süße panel posten ✨",
        },
        "es": {
            "panel_default_title":  "abre un ticket acogedor ☕",
            "panel_default_desc":   "elige una categoría o pulsa el botón — te traemos una silla ✨",
            "open_btn":             "crear ticket",
            "select_category":      "### elige un sabor ☕",
            "select_placeholder":   "elegir categoría...",
            "ticket_welcome":       "### {icon} ticket de {category}\nholi {mention} ☕ acomódate, el staff vendrá enseguida ✨",
            "ticket_created":       "✅ tu ticket acogedor te espera en {channel} ☕",
            "panel_updated":        "✅ panel de tickets pulido y actualizado ✨",
            "panel_posted":         "✅ panel de tickets servido fresquito en {channel} ☕",
            "category_added":       "✅ **{name}** añadida al menú ☕",
            "category_removed":     "✅ **{name}** quitada del menú",
            "category_exists":      "⚠️ **{name}** ya está en el menú ☕",
            "category_missing":     "⚠️ no hay **{name}** en el menú~",
            "categories_empty":     "aún no hay categorías — los tickets abren con la categoría 'General' por defecto ☕",
            "categories_list":      "### menú de tickets ☕\n{list}",
            "support_added":        "✅ bienvenida {role} a la sala del staff ☕",
            "support_removed":      "✅ {role} retirada de la sala del staff",
            "support_exists":       "⚠️ {role} ya está en la sala del staff ☕",
            "support_missing":      "⚠️ {role} no está en la sala del staff",
            "support_empty":        "la sala del staff está vacía por ahora ☕",
            "support_list":         "### sala del staff ☕\n{list}",
            "not_in_ticket":        "❌ esto solo funciona dentro de un cubículo de ticket, cariño ☕",
            "no_perm_close":        "❌ no puedes cerrar tickets, lo siento ☕",
            "no_perm_delete":       "❌ no puedes eliminar tickets, lo siento ☕",
            "no_perm_manage":       "❌ no puedes gestionar este ticket, lo siento ☕",
            "user_added":           "✅ acerqué una silla para {user} ☕",
            "user_removed":         "✅ {user} salió del cubículo",
            "user_already_added":   "⚠️ {user} ya está en el cubículo ☕",
            "user_not_in_ticket":   "⚠️ {user} no está en este cubículo",
            "renamed":              "✅ ticket renombrado a **{name}** ✨",
            "claimed":              "✅ {user} tomó este ticket ☕",
            "already_claimed":      "⚠️ {user} ya tomó este ☕",
            "transcript_built":     "📝 transcripción recién hecha ☕",
            "closing":              "{loading} cerrando el cubículo con cuidado…",
            "closed":               "🔒 cerrado por {user} — nos vemos pronto ☕",
            "deleting":             "🗑️ limpiando la mesa en {seconds}s…",
            "setup_title":          "### {icon} configuración del sistema de tickets ☕",
            "setup_desc":           "configura tu cubículo de tickets — añade categorías, invita staff y luego publica el panel adorable ✨",
        },
    },
}


def _ctx_lang(ctx_or_int) -> str:
    guild = None
    if isinstance(ctx_or_int, commands.Context):
        guild = ctx_or_int.guild
    elif isinstance(ctx_or_int, discord.Interaction):
        guild = ctx_or_int.guild
    elif isinstance(ctx_or_int, discord.Guild):
        guild = ctx_or_int
    if guild and guild.preferred_locale:
        loc = str(guild.preferred_locale).lower()
        if loc.startswith("de"):
            return "de"
        if loc.startswith("es"):
            return "es"
    return "en"


def _ctx_personality(ctx_or_int) -> str:
    if isinstance(ctx_or_int, commands.Context):
        return get_personality(ctx_or_int)
    # interaction-like
    class _Shim:
        guild = ctx_or_int.guild if hasattr(ctx_or_int, "guild") else None
    return get_personality(_Shim())


def msg(ctx_or_int, key: str, **kwargs) -> str:
    p = _ctx_personality(ctx_or_int)
    lang = _ctx_lang(ctx_or_int)
    table = MESSAGES.get(p, MESSAGES["normal"])
    text = (
        table.get(lang, {}).get(key)
        or table.get("en", {}).get(key)
        or MESSAGES["normal"].get(lang, {}).get(key)
        or MESSAGES["normal"]["en"].get(key, key)
    )
    return text.format(**kwargs) if kwargs else text


def _cv2(text: str) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
    return view


# ───────────────────────────────────────────────────
#  HELPERS
# ───────────────────────────────────────────────────

def parse_hex_color(text: str) -> Optional[int]:
    text = text.strip().replace("#", "")
    try:
        return int(text, 16)
    except ValueError:
        return None


def color_to_markdown(color: Optional[int]) -> str:
    if color is None:
        return ""
    return f"`#{color:06X}`"


def is_ticket_channel(ctx: commands.Context) -> Optional[dict]:
    if not ctx.guild:
        return None
    return find_open_ticket(ctx.guild.id, ctx.channel.id)


def has_support_perms(member: discord.Member, cfg: TicketConfig) -> bool:
    if member.guild_permissions.manage_channels:
        return True
    role_ids = {r.id for r in member.roles}
    return any(rid in role_ids for rid in cfg.support_roles)


# ───────────────────────────────────────────────────
#  MODALS — admin setup
# ───────────────────────────────────────────────────

class TicketPanelModal(Modal, title="Configure Ticket Panel"):
    def __init__(self, guild_id: int):
        super().__init__()
        self.guild_id = guild_id

        cfg = get_ticket_config(guild_id)
        self.title_input = TextInput(
            label="Panel Title", required=False, default=cfg.panel_title or ""
        )
        self.desc_input = TextInput(
            label="Panel Description", style=discord.TextStyle.long,
            required=False, default=cfg.panel_description or ""
        )
        self.color_input = TextInput(
            label="Color (hex)", required=False,
            default=f"#{cfg.panel_color:06X}" if cfg.panel_color else ""
        )
        self.image_input = TextInput(
            label="Image URL", required=False, default=cfg.panel_image or ""
        )

        self.add_item(self.title_input)
        self.add_item(self.desc_input)
        self.add_item(self.color_input)
        self.add_item(self.image_input)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = get_ticket_config(self.guild_id)
        if self.title_input.value:
            cfg.panel_title = self.title_input.value
        if self.desc_input.value:
            cfg.panel_description = self.desc_input.value
        if self.color_input.value:
            parsed = parse_hex_color(self.color_input.value)
            if parsed is not None:
                cfg.panel_color = parsed
        cfg.panel_image = self.image_input.value or None
        update_ticket_config(self.guild_id, cfg)

        # update existing posted panel if present
        if cfg.panel_message_id and cfg.panel_channel_id:
            channel = interaction.guild.get_channel(cfg.panel_channel_id)
            if channel:
                try:
                    m = await channel.fetch_message(cfg.panel_message_id)
                    await m.edit(view=TicketPanelView(self.guild_id, cfg))
                except Exception:
                    pass

        await interaction.response.send_message(msg(interaction, "panel_updated"), ephemeral=True)


# ───────────────────────────────────────────────────
#  USER-FACING PANEL
# ───────────────────────────────────────────────────

class OpenTicketBtn(discord.ui.Button):
    def __init__(self, guild_id: int, label: str = "Create Ticket"):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.green,
            custom_id=f"open_ticket_{guild_id}",
        )
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        cfg = get_ticket_config(self.guild_id)
        categories = cfg.panel_categories
        if categories:
            view = discord.ui.LayoutView(timeout=None)
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=msg(interaction, "select_category")),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                CategorySelectRow(self.guild_id, categories, msg(interaction, "select_placeholder")),
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)
        await create_ticket(interaction, "General")


class CategorySelect(discord.ui.Select):
    def __init__(self, guild_id: int, categories: list[str], placeholder: str):
        self.guild_id = guild_id
        options = [
            discord.SelectOption(label=c, value=c) for c in categories
        ]
        super().__init__(placeholder=placeholder, options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await create_ticket(interaction, self.values[0])


class CategorySelectRow(discord.ui.ActionRow):
    def __init__(self, guild_id: int, categories: list[str], placeholder: str):
        super().__init__()
        self.add_item(CategorySelect(guild_id, categories, placeholder))


class TicketPanelView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, cfg: Optional[TicketConfig] = None):
        super().__init__(timeout=None)
        cfg = cfg or get_ticket_config(guild_id)
        guild = None  # we don't have a context here; localise with default fallback
        # Default fallback to english panel labels — admins can override via the modal
        title = cfg.panel_title or MESSAGES["cafe"]["en"]["panel_default_title"]
        desc = cfg.panel_description or MESSAGES["cafe"]["en"]["panel_default_desc"]
        color_md = color_to_markdown(cfg.panel_color)

        header = f"### {get_emoji('icon_ticket')} {title}"
        if color_md:
            header += f" {color_md}"

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=header),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=desc),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )
        if cfg.panel_image:
            container.add_item(
                discord.ui.MediaGallery(discord.MediaGalleryItem(media=cfg.panel_image))
            )
        container.add_item(
            discord.ui.ActionRow(
                OpenTicketBtn(guild_id, label=MESSAGES["cafe"]["en"]["open_btn"])
            )
        )
        self.add_item(container)


class TicketWelcomeView(discord.ui.LayoutView):
    """The first message inside a freshly-created ticket. No buttons —
    the user controls the ticket via `ticket close/delete/add/...` sub-commands."""
    def __init__(self, category: str, user: discord.Member):
        super().__init__(timeout=None)
        body = MESSAGES["cafe"]["en"]["ticket_welcome"].format(
            icon=get_emoji("icon_ticket"),
            category=category,
            mention=user.mention,
        )
        self.add_item(discord.ui.Container(discord.ui.TextDisplay(content=body)))


# ───────────────────────────────────────────────────
#  CREATE TICKET
# ───────────────────────────────────────────────────

async def create_ticket(interaction: discord.Interaction, category: str):
    guild = interaction.guild
    user = interaction.user

    cfg = get_ticket_config(guild.id)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, embed_links=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }
    for rid in cfg.support_roles:
        role = guild.get_role(rid)
        if role:
            overwrites[role] = discord.PermissionOverwrite(
                read_messages=True, send_messages=True, manage_messages=True
            )

    channel = await guild.create_text_channel(
        name=f"ticket-{user.name}",
        overwrites=overwrites,
        reason=f"Ticket opened by {user}",
    )

    view = TicketWelcomeView(category, user)
    msg_obj = await channel.send(view=view)

    cfg.open_tickets.append({
        "channel_id": channel.id,
        "message_id": msg_obj.id,
        "category": category,
        "opener_id": user.id,
        "claimed_by": None,
        "status": "open",
    })
    update_ticket_config(guild.id, cfg)

    text = msg(interaction, "ticket_created", channel=channel.mention)
    if interaction.response.is_done():
        await interaction.followup.send(text, ephemeral=True)
    else:
        await interaction.response.send_message(text, ephemeral=True)


# ───────────────────────────────────────────────────
#  COG
# ───────────────────────────────────────────────────


__all__ = [k for k in list(globals()) if not k.startswith("__")]
