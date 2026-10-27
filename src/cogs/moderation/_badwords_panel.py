"""
Moderation — the interactive `/badwords` panel (Components V2).

Laid out like the `/automod` panel: one Container with a section menu and the
controls for the active section underneath. The sections cover the custom word
list, the curated preset filters, and the delete/censor response — everything
the blocked-word filter does, editable without memorising subcommands.

The subcommands (`/badwords add`, `remove`, `clear`) stay available for scripted
use; this panel is the interactive front end.
"""
from types import SimpleNamespace

import discord

from config.emojis import get_emoji
from utils.i18n import get_lang
from ._presets import PRESET_FILTERS, preset_description, preset_label
from .utils import (
    MAX_BADWORDS_MASK_LENGTH,
    MAX_BLOCKED_WORDS,
    MAX_BLOCKED_WORD_LENGTH,
    normalize_badwords_mask,
    normalize_blocked_word,
)

ALLOWED_MENTIONS = discord.AllowedMentions.none()
PANEL_TIMEOUT = 300

SECTIONS = ("overview", "words", "presets", "response")

# The word list can hold far more entries than one panel can show (or than a
# select menu can offer), so the listing and the remove menu are both capped.
MAX_LISTED_WORDS = 40
MAX_REMOVE_OPTIONS = 25

EMOJI = {
    "mod": get_emoji("moderation"),
    "msg": get_emoji("message"),
    "gear": get_emoji("utility"),
    "tick": get_emoji("tick"),
    "cross": get_emoji("cross"),
    "plus": get_emoji("plus"),
    "trash": get_emoji("trash"),
    "warn": get_emoji("warning"),
}

MESSAGES = {
    "en": {
        "no_permission":     "{cross} You need **Manage Server** permissions to do that.",
        "panel_title":       "### {mod} Blocked Words",
        "panel_desc":        "Niko checks every message in this server against your own word list and the preset filters you switch on.",
        "overview_counts":   "**{words}** words in your list  •  **{presets}/{total}** preset filters on",
        "overview_mode":     "Response: **{mode}**",
        "overview_hint":     "-# Use the menu below to manage the word list, the preset filters, and what happens to a flagged message.",
        "words_title":       "### {msg} Word list",
        "words_desc":        "Whole-word matching, like Discord. `word*` also catches longer forms, `*word*` matches anywhere, and separators between letters are ignored — so `a.s.s` is still caught.",
        "words_empty":       "*No words yet — add the first one with the button below.*",
        "words_more":        "-# …and {count} more.",
        "words_hint":        "-# Add, remove, or clear words with the buttons below.",
        "presets_title":     "### {mod} Preset filters",
        "presets_desc":      "Curated regular expressions for slurs and other content a plain word list cannot keep up with. They also catch leet (`n1gg3r`), spaced (`n i g g e r`), repeated (`niiiigger`), self-censored (`sh*t`) and look-alike spellings, while leaving ordinary words like “class”, “analysis” and “spices” alone.",
        "presets_hint":      "-# Choose the filters with the menu below. Everything they catch follows the response in the Response section.",
        "response_title":    "### {gear} Response",
        "response_desc":     "What Niko does with a message that trips the word list or a preset filter.",
        "response_current":  "Currently: **{mode}**",
        "response_mask":     "Censor mask: `{mask}`",
        "response_mask_none":"Censor mask: *removes the word entirely*",
        "response_hint":     "-# Censoring deletes the message and reposts its text through a webhook using the member's name and avatar, so Niko needs **Manage Webhooks** in that channel. Without it the message is deleted instead.",
        "mode_delete":       "delete the message",
        "mode_censor":       "censor & repost it",
        "word_invalid":      "{cross} That cannot be blocked — use 60 characters or fewer.",
        "word_exists":       "{cross} `{word}` is already blocked.",
        "words_full":        "{cross} The word list is full ({max} words). Remove one first.",
        "word_added":        "{tick} Added `{word}`.",
        "remove_none":       "{cross} There is nothing to remove.",
        "remove_prompt":     "{msg} Pick the word to unblock:",
        "remove_more":       "-# Showing the first {shown} of {total} words — remove one to reach the rest.",
        "word_removed":      "{tick} Removed `{word}`.",
        "clear_prompt":      "{warn} Clear **all {count} words**? This cannot be undone.",
        "clear_confirm":     "Clear all words",
        "cancel":            "Cancel",
        "clear_cancelled":   "Nothing was changed.",
        "clear_done":        "{tick} Cleared {count} words.",
        "presets_saved":     "{tick} Preset filters updated.",
        "response_saved":    "{tick} Response set to **{mode}**.",
        "mask_title":        "Censor mask",
        "mask_placeholder":  "e.g. * or [removed]",
        "mask_saved":        "{tick} Censor mask set to `{mask}`.",
        "mask_saved_none":   "{tick} Censor mask cleared — blocked words are removed entirely.",
        "section_overview":  "Overview",
        "section_words":     "Word list",
        "section_presets":   "Preset filters",
        "section_response":  "Response",
        "section_placeholder": "Navigate sections…",
        "preset_placeholder": "Toggle preset filters…",
        "response_placeholder": "Choose the response…",
        "remove_placeholder": "Choose a word to remove…",
        "words_label":       "Words",
        "presets_label":     "Presets",
    },
    "de": {
        "no_permission":     "{cross} Dafür brauchst du die Berechtigung **Server verwalten**.",
        "panel_title":       "### {mod} Gesperrte Wörter",
        "panel_desc":        "Niko prüft jede Nachricht auf diesem Server anhand deiner Wortliste und der aktivierten Preset-Filter.",
        "overview_counts":   "**{words}** Wörter in deiner Liste  •  **{presets}/{total}** Preset-Filter aktiv",
        "overview_mode":     "Reaktion: **{mode}**",
        "overview_hint":     "-# Nutze das Menü unten, um Wortliste, Preset-Filter und die Reaktion auf eine markierte Nachricht zu verwalten.",
        "words_title":       "### {msg} Wortliste",
        "words_desc":        "Ganze Wörter, wie bei Discord. `wort*` erfasst auch längere Formen, `*wort*` trifft überall, und Trennzeichen zwischen Buchstaben werden ignoriert — `a.s.s` wird also weiterhin erkannt.",
        "words_empty":       "*Noch keine Wörter — füge das erste mit dem Button unten hinzu.*",
        "words_more":        "-# …und {count} weitere.",
        "words_hint":        "-# Füge Wörter hinzu, entferne oder lösche sie mit den Buttons unten.",
        "presets_title":     "### {mod} Preset-Filter",
        "presets_desc":      "Kuratierte reguläre Ausdrücke für Beleidigungen und andere Inhalte, mit denen eine reine Wortliste nicht mithalten kann. Sie erkennen auch Leet- (`n1gg3r`), getrennte (`n i g g e r`), wiederholte (`niiiigger`), selbst zensierte (`sh*t`) und ähnlich aussehende Schreibweisen — normale Wörter wie „Klasse“, „Analyse“ oder „Gewürze“ bleiben unberührt.",
        "presets_hint":      "-# Wähle die Filter mit dem Menü unten. Alles, was sie erkennen, folgt der Reaktion im Bereich „Reaktion“.",
        "response_title":    "### {gear} Reaktion",
        "response_desc":     "Was Niko mit einer Nachricht macht, die die Wortliste oder einen Preset-Filter auslöst.",
        "response_current":  "Aktuell: **{mode}**",
        "response_mask":     "Zensur-Maske: `{mask}`",
        "response_mask_none":"Zensur-Maske: *entfernt das Wort vollständig*",
        "response_hint":     "-# Beim Zensieren wird die Nachricht gelöscht und ihr Text über einen Webhook mit Name und Avatar des Mitglieds neu gesendet. Niko braucht dafür **Webhooks verwalten** in diesem Kanal — sonst wird die Nachricht nur gelöscht.",
        "mode_delete":       "Nachricht löschen",
        "mode_censor":       "zensieren & erneut senden",
        "word_invalid":      "{cross} Das kann nicht gesperrt werden — höchstens 60 Zeichen.",
        "word_exists":       "{cross} `{word}` ist bereits gesperrt.",
        "words_full":        "{cross} Die Wortliste ist voll ({max} Wörter). Entferne zuerst eines.",
        "word_added":        "{tick} `{word}` hinzugefügt.",
        "remove_none":       "{cross} Es gibt nichts zu entfernen.",
        "remove_prompt":     "{msg} Wähle das Wort, das du entsperren möchtest:",
        "remove_more":       "-# Es werden die ersten {shown} von {total} Wörtern gezeigt — entferne eines, um die restlichen zu sehen.",
        "word_removed":      "{tick} `{word}` entfernt.",
        "clear_prompt":      "{warn} **Alle {count} Wörter** löschen? Das kann nicht rückgängig gemacht werden.",
        "clear_confirm":     "Alle Wörter löschen",
        "cancel":            "Abbrechen",
        "clear_cancelled":   "Es wurde nichts geändert.",
        "clear_done":        "{tick} {count} Wörter gelöscht.",
        "presets_saved":     "{tick} Preset-Filter aktualisiert.",
        "response_saved":    "{tick} Reaktion auf **{mode}** gesetzt.",
        "mask_title":        "Zensur-Maske",
        "mask_placeholder":  "z. B. * oder [entfernt]",
        "mask_saved":        "{tick} Zensur-Maske auf `{mask}` gesetzt.",
        "mask_saved_none":   "{tick} Zensur-Maske geleert — gesperrte Wörter werden vollständig entfernt.",
        "section_overview":  "Übersicht",
        "section_words":     "Wortliste",
        "section_presets":   "Preset-Filter",
        "section_response":  "Reaktion",
        "section_placeholder": "Bereiche…",
        "preset_placeholder": "Preset-Filter umschalten…",
        "response_placeholder": "Reaktion wählen…",
        "remove_placeholder": "Wort zum Entfernen wählen…",
        "words_label":       "Wörter",
        "presets_label":     "Presets",
    },
    "es": {
        "no_permission":     "{cross} Necesitas el permiso **Gestionar servidor** para hacer eso.",
        "panel_title":       "### {mod} Palabras bloqueadas",
        "panel_desc":        "Niko revisa cada mensaje de este servidor con tu lista de palabras y los filtros predefinidos que actives.",
        "overview_counts":   "**{words}** palabras en tu lista  •  **{presets}/{total}** filtros predefinidos activos",
        "overview_mode":     "Respuesta: **{mode}**",
        "overview_hint":     "-# Usa el menú de abajo para gestionar la lista de palabras, los filtros predefinidos y qué ocurre con un mensaje marcado.",
        "words_title":       "### {msg} Lista de palabras",
        "words_desc":        "Coincidencia por palabra completa, como en Discord. `palabra*` también detecta formas más largas, `*palabra*` coincide en cualquier lugar y los separadores entre letras se ignoran, así que `a.s.s` sigue detectándose.",
        "words_empty":       "*Aún no hay palabras — añade la primera con el botón de abajo.*",
        "words_more":        "-# …y {count} más.",
        "words_hint":        "-# Añade, elimina o borra palabras con los botones de abajo.",
        "presets_title":     "### {mod} Filtros predefinidos",
        "presets_desc":      "Expresiones regulares seleccionadas para insultos y otro contenido que una lista de palabras no puede cubrir. También detectan variantes con leet (`n1gg3r`), separadas (`n i g g e r`), repetidas (`niiiigger`), autocensuradas (`sh*t`) y con caracteres parecidos, sin afectar a palabras normales como «clase», «análisis» o «especias».",
        "presets_hint":      "-# Elige los filtros con el menú de abajo. Todo lo que detecten sigue la respuesta de la sección Respuesta.",
        "response_title":    "### {gear} Respuesta",
        "response_desc":     "Qué hace Niko con un mensaje que activa la lista de palabras o un filtro predefinido.",
        "response_current":  "Actualmente: **{mode}**",
        "response_mask":     "Máscara de censura: `{mask}`",
        "response_mask_none":"Máscara de censura: *elimina la palabra por completo*",
        "response_hint":     "-# Censurar borra el mensaje y reenvía su texto mediante un webhook con el nombre y el avatar del miembro, así que Niko necesita **Gestionar webhooks** en ese canal. Sin él, el mensaje solo se elimina.",
        "mode_delete":       "eliminar el mensaje",
        "mode_censor":       "censurar y reenviar",
        "word_invalid":      "{cross} Eso no se puede bloquear — usa 60 caracteres o menos.",
        "word_exists":       "{cross} `{word}` ya está bloqueada.",
        "words_full":        "{cross} La lista está llena ({max} palabras). Elimina una primero.",
        "word_added":        "{tick} Se añadió `{word}`.",
        "remove_none":       "{cross} No hay nada que eliminar.",
        "remove_prompt":     "{msg} Elige la palabra que quieres desbloquear:",
        "remove_more":       "-# Mostrando las primeras {shown} de {total} palabras — elimina una para ver el resto.",
        "word_removed":      "{tick} Se eliminó `{word}`.",
        "clear_prompt":      "{warn} ¿Borrar **las {count} palabras**? No se puede deshacer.",
        "clear_confirm":     "Borrar todas",
        "cancel":            "Cancelar",
        "clear_cancelled":   "No se cambió nada.",
        "clear_done":        "{tick} Se borraron {count} palabras.",
        "presets_saved":     "{tick} Filtros predefinidos actualizados.",
        "response_saved":    "{tick} Respuesta establecida en **{mode}**.",
        "mask_title":        "Máscara de censura",
        "mask_placeholder":  "p. ej. * o [eliminado]",
        "mask_saved":        "{tick} Máscara de censura establecida en `{mask}`.",
        "mask_saved_none":   "{tick} Máscara borrada — las palabras bloqueadas se eliminan por completo.",
        "section_overview":  "Resumen",
        "section_words":     "Lista de palabras",
        "section_presets":   "Filtros predefinidos",
        "section_response":  "Respuesta",
        "section_placeholder": "Ir a una sección…",
        "preset_placeholder": "Activar filtros predefinidos…",
        "response_placeholder": "Elige la respuesta…",
        "remove_placeholder": "Elige una palabra para eliminar…",
        "words_label":       "Palabras",
        "presets_label":     "Filtros",
    },
}


def _lang(guild) -> str:
    """The guild's panel language, reusing the command-message resolver."""
    return get_lang(SimpleNamespace(guild=guild))


def _t(lang: str, key: str, **kwargs) -> str:
    """Look up a panel string, filling in the custom emojis and any kwargs."""
    text = MESSAGES.get(lang, {}).get(key) or MESSAGES["en"].get(key, key)
    return text.format(**EMOJI, **kwargs)


def _mode_label(lang: str, action: str) -> str:
    return _t(lang, "mode_censor" if action == "censor" else "mode_delete")


# ──────────────────────────────────────────────────
#  PERMISSIONS
# ──────────────────────────────────────────────────

def _may_manage(interaction: discord.Interaction) -> bool:
    """Whether the member may edit this server's filter (Manage Server)."""
    permissions = getattr(interaction.user, "guild_permissions", None)
    return bool(permissions is not None and getattr(permissions, "manage_guild", False))


async def _deny(interaction: discord.Interaction):
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=_t(_lang(interaction.guild), "no_permission")),
        accent_colour=discord.Color.red(),
    ))
    return await interaction.response.send_message(view=view, ephemeral=True)


async def _notice(interaction: discord.Interaction, text: str):
    """A one-line ephemeral reply, used for errors and confirmations."""
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
    return await interaction.response.send_message(view=view, ephemeral=True)


# ──────────────────────────────────────────────────
#  SECTION TEXT
# ──────────────────────────────────────────────────

def _preset_lines(utils, guild_id: int, lang: str) -> str:
    enabled = set(utils.get_badwords_presets(guild_id))
    lines = []
    for preset in PRESET_FILTERS:
        icon = EMOJI["tick"] if preset.key in enabled else EMOJI["cross"]
        lines.append(f"{icon} **{preset_label(preset, lang)}**\n-# {preset_description(preset, lang)}")
    return "\n".join(lines)


def _build_overview_text(utils, guild_id: int, lang: str) -> str:
    words = utils.get_blocked_words(guild_id)
    presets = utils.get_badwords_presets(guild_id)
    return "\n".join([
        _t(lang, "panel_title"),
        _t(lang, "panel_desc"),
        "",
        _t(lang, "overview_counts", words=len(words), presets=len(presets), total=len(PRESET_FILTERS)),
        _t(lang, "overview_mode", mode=_mode_label(lang, utils.get_badwords_action(guild_id))),
        "",
        _t(lang, "overview_hint"),
    ])


def _build_words_text(utils, guild_id: int, lang: str) -> str:
    words = utils.get_blocked_words(guild_id)
    if not words:
        listing = _t(lang, "words_empty")
    else:
        listing = " ".join(f"`{word}`" for word in words[:MAX_LISTED_WORDS])
        if len(words) > MAX_LISTED_WORDS:
            listing += "\n" + _t(lang, "words_more", count=len(words) - MAX_LISTED_WORDS)
    return "\n".join([
        _t(lang, "words_title"),
        _t(lang, "words_desc"),
        "",
        listing,
        "",
        _t(lang, "words_hint"),
    ])


def _build_presets_text(utils, guild_id: int, lang: str) -> str:
    return "\n".join([
        _t(lang, "presets_title"),
        _t(lang, "presets_desc"),
        "",
        _preset_lines(utils, guild_id, lang),
        "",
        _t(lang, "presets_hint"),
    ])


def _build_response_text(utils, guild_id: int, lang: str) -> str:
    mask = utils.get_badwords_mask(guild_id)
    return "\n".join([
        _t(lang, "response_title"),
        _t(lang, "response_desc"),
        "",
        _t(lang, "response_current", mode=_mode_label(lang, utils.get_badwords_action(guild_id))),
        _t(lang, "response_mask", mask=mask) if mask else _t(lang, "response_mask_none"),
        "",
        _t(lang, "response_hint"),
    ])


def _section_text(utils, guild_id: int, section: str, lang: str) -> str:
    if section == "words":
        return _build_words_text(utils, guild_id, lang)
    if section == "presets":
        return _build_presets_text(utils, guild_id, lang)
    if section == "response":
        return _build_response_text(utils, guild_id, lang)
    return _build_overview_text(utils, guild_id, lang)


# ──────────────────────────────────────────────────
#  PANEL
# ──────────────────────────────────────────────────

def build_panel(utils, guild_id: int, section: str = "overview", guild=None) -> discord.ui.LayoutView:
    """The `/badwords` panel for one section, ready to send or edit in place."""
    if section not in SECTIONS:
        section = "overview"
    lang = _lang(guild)
    view = discord.ui.LayoutView(timeout=PANEL_TIMEOUT)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=_section_text(utils, guild_id, section, lang)),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
    )
    container.add_item(discord.ui.ActionRow(SectionSelect(utils, guild_id, section, lang)))

    if section == "words":
        container.add_item(discord.ui.ActionRow(
            AddWordButton(utils, guild_id),
            RemoveWordButton(utils, guild_id),
            ClearWordsButton(utils, guild_id),
        ))
    elif section == "presets":
        container.add_item(discord.ui.ActionRow(PresetSelect(utils, guild_id, lang)))
    elif section == "response":
        container.add_item(discord.ui.ActionRow(ResponseSelect(utils, guild_id, lang)))
        container.add_item(discord.ui.ActionRow(SetMaskButton(utils, guild_id)))

    view.add_item(container)
    return view


async def _rerender(interaction: discord.Interaction, utils, guild_id: int, section: str):
    """Refresh the panel message the interaction came from."""
    await interaction.response.edit_message(
        view=build_panel(utils, guild_id, section, interaction.guild),
        allowed_mentions=ALLOWED_MENTIONS,
    )


class SectionSelect(discord.ui.Select):
    """Moves between the panel's sections."""

    def __init__(self, utils, guild_id: int, current: str, lang: str):
        self._utils = utils
        self._guild_id = guild_id
        options = [
            discord.SelectOption(
                label=_t(lang, label_key),
                value=value,
                emoji=emoji,
                default=(value == current),
            )
            for value, label_key, emoji in (
                ("overview", "section_overview", EMOJI["mod"]),
                ("words", "section_words", EMOJI["msg"]),
                ("presets", "section_presets", EMOJI["mod"]),
                ("response", "section_response", EMOJI["gear"]),
            )
        ]
        super().__init__(
            placeholder=_t(lang, "section_placeholder"),
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        await _rerender(interaction, self._utils, self._guild_id, self.values[0])


# ── Word list ────────────────────────────────────────────────────────────────

class AddWordButton(discord.ui.Button):
    def __init__(self, utils, guild_id: int):
        super().__init__(label="Add Word", style=discord.ButtonStyle.green, emoji=EMOJI["plus"])
        self._utils = utils
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        await interaction.response.send_modal(AddWordModal(self._utils, self._guild_id))


class AddWordModal(discord.ui.Modal, title="Blocked word"):
    word = discord.ui.TextInput(
        label="Word or phrase",
        placeholder="e.g. badword, bad*, *bad*",
        max_length=MAX_BLOCKED_WORD_LENGTH,
    )

    def __init__(self, utils, guild_id: int):
        super().__init__()
        self._utils = utils
        self._guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        lang = _lang(interaction.guild)
        if not _may_manage(interaction):
            return await _deny(interaction)
        word = normalize_blocked_word(self.word.value)
        if word is None:
            return await _notice(interaction, _t(lang, "word_invalid"))
        current = self._utils.get_blocked_words(self._guild_id)
        if word in current:
            return await _notice(interaction, _t(lang, "word_exists", word=word))
        if len(current) >= MAX_BLOCKED_WORDS:
            return await _notice(interaction, _t(lang, "words_full", max=MAX_BLOCKED_WORDS))
        self._utils.add_blocked_word(self._guild_id, word)
        await _rerender(interaction, self._utils, self._guild_id, "words")


class RemoveWordButton(discord.ui.Button):
    def __init__(self, utils, guild_id: int):
        super().__init__(label="Remove Word", style=discord.ButtonStyle.gray, emoji=EMOJI["trash"])
        self._utils = utils
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        lang = _lang(interaction.guild)
        if not _may_manage(interaction):
            return await _deny(interaction)
        words = self._utils.get_blocked_words(self._guild_id)
        if not words:
            return await _notice(interaction, _t(lang, "remove_none"))
        view = discord.ui.LayoutView(timeout=60)
        body = [_t(lang, "remove_prompt")]
        if len(words) > MAX_REMOVE_OPTIONS:
            body.append(_t(lang, "remove_more", shown=MAX_REMOVE_OPTIONS, total=len(words)))
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="\n".join(body)),
            discord.ui.ActionRow(
                RemoveWordSelect(self._utils, self._guild_id, words, interaction.message),
            ),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


class RemoveWordSelect(discord.ui.Select):
    """Ephemeral picker — unblocks one word and refreshes the panel."""

    def __init__(self, utils, guild_id: int, words: list, message):
        self._utils = utils
        self._guild_id = guild_id
        self.message = message
        super().__init__(
            placeholder=_t(_lang(getattr(message, "guild", None)), "remove_placeholder"),
            options=[
                discord.SelectOption(label=word[:100], value=word[:100])
                for word in words[:MAX_REMOVE_OPTIONS]
            ],
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        lang = _lang(interaction.guild)
        if not _may_manage(interaction):
            return await _deny(interaction)
        word = self.values[0]
        self._utils.remove_blocked_word(self._guild_id, word)
        await _notice(interaction, _t(lang, "word_removed", word=word))
        if self.message is not None:
            await self.message.edit(
                view=build_panel(self._utils, self._guild_id, "words", interaction.guild),
                allowed_mentions=ALLOWED_MENTIONS,
            )


class ClearWordsButton(discord.ui.Button):
    def __init__(self, utils, guild_id: int):
        super().__init__(label="Clear All", style=discord.ButtonStyle.red, emoji=EMOJI["trash"])
        self._utils = utils
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        lang = _lang(interaction.guild)
        if not _may_manage(interaction):
            return await _deny(interaction)
        words = self._utils.get_blocked_words(self._guild_id)
        if not words:
            return await _notice(interaction, _t(lang, "remove_none"))
        view = discord.ui.LayoutView(timeout=60)
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=_t(lang, "clear_prompt", count=len(words))),
            discord.ui.ActionRow(
                ConfirmClearButton(self._utils, self._guild_id, len(words), interaction.message),
                CancelClearButton(),
            ),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


class ConfirmClearButton(discord.ui.Button):
    def __init__(self, utils, guild_id: int, count: int, message):
        lang = _lang(getattr(message, "guild", None))
        super().__init__(label=_t(lang, "clear_confirm"), style=discord.ButtonStyle.red, emoji=EMOJI["trash"])
        self._utils = utils
        self._guild_id = guild_id
        self._count = count
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        lang = _lang(interaction.guild)
        if not _may_manage(interaction):
            return await _deny(interaction)
        self._utils.clear_blocked_words(self._guild_id)
        await _notice(interaction, _t(lang, "clear_done", count=self._count))
        if self.message is not None:
            await self.message.edit(
                view=build_panel(self._utils, self._guild_id, "words", interaction.guild),
                allowed_mentions=ALLOWED_MENTIONS,
            )


class CancelClearButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Cancel", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        lang = _lang(interaction.guild)
        if not _may_manage(interaction):
            return await _deny(interaction)
        await _notice(interaction, _t(lang, "clear_cancelled"))


# ── Preset filters ───────────────────────────────────────────────────────────

class PresetSelect(discord.ui.Select):
    """Switches the curated preset filters on and off in one interaction."""

    def __init__(self, utils, guild_id: int, lang: str):
        self._utils = utils
        self._guild_id = guild_id
        enabled = set(utils.get_badwords_presets(guild_id))
        options = [
            discord.SelectOption(
                label=preset_label(preset, lang)[:100],
                value=preset.key,
                description=preset_description(preset, lang)[:100],
                emoji=EMOJI["tick"] if preset.key in enabled else None,
                default=preset.key in enabled,
            )
            for preset in PRESET_FILTERS
        ]
        super().__init__(
            placeholder=_t(lang, "preset_placeholder"),
            options=options,
            min_values=0,
            max_values=len(options),
        )

    async def callback(self, interaction: discord.Interaction):
        lang = _lang(interaction.guild)
        if not _may_manage(interaction):
            return await _deny(interaction)
        self._utils.set_badwords_presets(self._guild_id, self.values)
        await interaction.response.edit_message(
            view=build_panel(self._utils, self._guild_id, "presets", interaction.guild),
            allowed_mentions=ALLOWED_MENTIONS,
        )
        await interaction.followup.send(_t(lang, "presets_saved"), ephemeral=True)


# ── Response ─────────────────────────────────────────────────────────────────

class ResponseSelect(discord.ui.Select):
    """Chooses whether a flagged message is deleted or censored and reposted."""

    def __init__(self, utils, guild_id: int, lang: str):
        self._utils = utils
        self._guild_id = guild_id
        current = utils.get_badwords_action(guild_id)
        super().__init__(
            placeholder=_t(lang, "response_placeholder"),
            options=[
                discord.SelectOption(
                    label=_t(lang, "mode_delete"),
                    value="delete",
                    description="Remove the message and log it",
                    default=(current == "delete"),
                ),
                discord.SelectOption(
                    label=_t(lang, "mode_censor"),
                    value="censor",
                    description="Repost it through a webhook as the author, words masked",
                    default=(current == "censor"),
                ),
            ],
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        lang = _lang(interaction.guild)
        if not _may_manage(interaction):
            return await _deny(interaction)
        value = self.values[0]
        if value not in ("delete", "censor"):
            return await _notice(interaction, _t(lang, "response_placeholder"))
        self._utils.get_guild_config(self._guild_id)["badwords_action"] = value
        self._utils.save_config()
        await interaction.response.edit_message(
            view=build_panel(self._utils, self._guild_id, "response", interaction.guild),
            allowed_mentions=ALLOWED_MENTIONS,
        )
        await interaction.followup.send(
            _t(lang, "response_saved", mode=_mode_label(lang, value)), ephemeral=True)


class SetMaskButton(discord.ui.Button):
    def __init__(self, utils, guild_id: int):
        super().__init__(label="Set Mask", style=discord.ButtonStyle.gray, emoji=EMOJI["gear"])
        self._utils = utils
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        lang = _lang(interaction.guild)
        await interaction.response.send_modal(
            MaskModal(self._utils, self._guild_id, lang))


class MaskModal(discord.ui.Modal):
    """Edits the text that replaces a censored word."""

    # The label stays English like every other modal in the bot; only the
    # placeholder (which carries the syntax hint) is localised.
    mask = discord.ui.TextInput(
        label="Mask text",
        max_length=MAX_BADWORDS_MASK_LENGTH,
        # Empty is allowed on purpose: it means "remove the word entirely".
        required=False,
    )

    def __init__(self, utils, guild_id: int, lang: str):
        super().__init__(title=_t(lang, "mask_title"))
        self._utils = utils
        self._guild_id = guild_id
        self.mask.placeholder = _t(lang, "mask_placeholder")
        self.mask.default = utils.get_badwords_mask(guild_id)

    async def on_submit(self, interaction: discord.Interaction):
        lang = _lang(interaction.guild)
        if not _may_manage(interaction):
            return await _deny(interaction)
        mask = normalize_badwords_mask(self.mask.value)
        self._utils.get_guild_config(self._guild_id)["badwords_mask"] = mask
        self._utils.save_config()
        await _rerender(interaction, self._utils, self._guild_id, "response")
        await interaction.followup.send(
            _t(lang, "mask_saved", mask=mask) if mask else _t(lang, "mask_saved_none"),
            ephemeral=True,
        )
