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
from utils.locales import load_locales
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

MESSAGES = load_locales("cogs.moderation", "badwords_panel")


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


async def _log(utils, interaction: discord.Interaction, body: str) -> None:
    """Record a filter change in the server's AutoMod log.

    Whitelisting a user exempts them from anti-nuke, so who changed what has to
    leave a trace — none of these edits used to be logged at all.
    """
    await utils.log_action(
        interaction.guild, "Blocked Words", body, moderator=interaction.user)


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
            AddWordButton(utils, guild_id, lang),
            RemoveWordButton(utils, guild_id, lang),
            ClearWordsButton(utils, guild_id, lang),
        ))
    elif section == "presets":
        container.add_item(discord.ui.ActionRow(PresetSelect(utils, guild_id, lang)))
    elif section == "response":
        container.add_item(discord.ui.ActionRow(ResponseSelect(utils, guild_id, lang)))
        container.add_item(discord.ui.ActionRow(SetMaskButton(utils, guild_id, lang)))

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
    def __init__(self, utils, guild_id: int, lang: str):
        super().__init__(label=_t(lang, "btn_add_word"), style=discord.ButtonStyle.green, emoji=EMOJI["plus"])
        self._utils = utils
        self._guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not _may_manage(interaction):
            return await _deny(interaction)
        await interaction.response.send_modal(
            AddWordModal(self._utils, self._guild_id, _lang(interaction.guild)))


class AddWordModal(discord.ui.Modal):
    def __init__(self, utils, guild_id: int, lang: str = "en"):
        super().__init__(title=_t(lang, "add_word_title"))
        # Built here rather than as a class attribute: the label has to be in
        # the guild's language, and a modal is assembled per interaction.
        self.word = discord.ui.TextInput(
            label=_t(lang, "add_word_label"),
            placeholder="e.g. badword, bad*, *bad*",
            max_length=MAX_BLOCKED_WORD_LENGTH,
        )
        self.add_item(self.word)
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
        await _log(self._utils, interaction, f"**Action:** Word added\n**Word:** `{word}`")
        await _rerender(interaction, self._utils, self._guild_id, "words")


class RemoveWordButton(discord.ui.Button):
    def __init__(self, utils, guild_id: int, lang: str):
        super().__init__(label=_t(lang, "btn_remove_word"), style=discord.ButtonStyle.gray, emoji=EMOJI["trash"])
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
        await _log(self._utils, interaction, f"**Action:** Word removed\n**Word:** `{word}`")
        await _notice(interaction, _t(lang, "word_removed", word=word))
        if self.message is not None:
            await self.message.edit(
                view=build_panel(self._utils, self._guild_id, "words", interaction.guild),
                allowed_mentions=ALLOWED_MENTIONS,
            )


class ClearWordsButton(discord.ui.Button):
    def __init__(self, utils, guild_id: int, lang: str):
        super().__init__(label=_t(lang, "btn_clear_words"), style=discord.ButtonStyle.red, emoji=EMOJI["trash"])
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
                CancelClearButton(lang),
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
        await _log(self._utils, interaction, f"**Action:** Every blocked word cleared ({self._count})")
        await _notice(interaction, _t(lang, "clear_done", count=self._count))
        if self.message is not None:
            await self.message.edit(
                view=build_panel(self._utils, self._guild_id, "words", interaction.guild),
                allowed_mentions=ALLOWED_MENTIONS,
            )


class CancelClearButton(discord.ui.Button):
    def __init__(self, lang: str):
        super().__init__(label=_t(lang, "cancel"), style=discord.ButtonStyle.secondary)

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
        enabled = self._utils.set_badwords_presets(self._guild_id, self.values)
        await _log(self._utils, interaction,
                   "**Action:** Preset filters updated\n**Enabled:** "
                   f"{', '.join(f'`{key}`' for key in enabled) or 'none'}")
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
        self._utils.save_config(self._guild_id)
        await _log(self._utils, interaction, f"**Action:** Blocked-word response set to `{value}`")
        await interaction.response.edit_message(
            view=build_panel(self._utils, self._guild_id, "response", interaction.guild),
            allowed_mentions=ALLOWED_MENTIONS,
        )
        await interaction.followup.send(
            _t(lang, "response_saved", mode=_mode_label(lang, value)), ephemeral=True)


class SetMaskButton(discord.ui.Button):
    def __init__(self, utils, guild_id: int, lang: str):
        super().__init__(label=_t(lang, "btn_set_mask"), style=discord.ButtonStyle.gray, emoji=EMOJI["gear"])
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

    def __init__(self, utils, guild_id: int, lang: str):
        super().__init__(title=_t(lang, "mask_title"))
        self.mask = discord.ui.TextInput(
            label=_t(lang, "mask_label"),
            placeholder=_t(lang, "mask_placeholder"),
            max_length=MAX_BADWORDS_MASK_LENGTH,
            # Empty is allowed on purpose: it means "remove the word entirely".
            required=False,
            default=utils.get_badwords_mask(guild_id),
        )
        self.add_item(self.mask)
        self._utils = utils
        self._guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        lang = _lang(interaction.guild)
        if not _may_manage(interaction):
            return await _deny(interaction)
        mask = normalize_badwords_mask(self.mask.value)
        self._utils.get_guild_config(self._guild_id)["badwords_mask"] = mask
        self._utils.save_config(self._guild_id)
        await _log(self._utils, interaction,
                   f"**Action:** Censor mask set to `{mask}`" if mask else "**Action:** Censor mask cleared")
        await _rerender(interaction, self._utils, self._guild_id, "response")
        await interaction.followup.send(
            _t(lang, "mask_saved", mask=mask) if mask else _t(lang, "mask_saved_none"),
            ephemeral=True,
        )
