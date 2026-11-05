"""The guided ``/setup`` wizard.

One message walks a server through the features people actually turn on:
leveling, AutoMod, blocked words, onboarding, logging, tickets and AI. Every
step is optional, every step is saved before the next one renders, and nothing
here needs the bot to be an administrator — each step uses the same settings the
individual panels and the dashboard already write.

The panel is posted in the channel rather than as an ephemeral message, so
:meth:`SetupWizard.interaction_check` is what keeps a normal member from
pressing its buttons. It accepts Manage Server (which Administrator implies),
the same permission the existing setup commands use.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import discord
from discord.ext import commands

from config.emojis import get_emoji
from config.links import DOCS, dashboard_url
from utils import logging
from utils.command_ids import replace_refs
from utils.command_locales import command_texts
from utils.i18n import get_lang, make_flat_msg
from utils.locales import load_locales

CMDS = command_texts(__package__)
MESSAGES = load_locales(__package__, "setup")
_msg = make_flat_msg(MESSAGES, {
    "icon": get_emoji("settings"),
    "tick": get_emoji("tick"),
    "cross": get_emoji("cross"),
    "plus": get_emoji("plus"),
})


def msg(guild, key, **fields):
    """Localised wizard copy with every ``/command`` reference turned into a
    mention (``</automod:id>``), which Discord renders as a clickable chip.

    The catalogues keep writing plain command names so translators never see a
    snowflake; :func:`replace_refs` leaves a reference as inline code when its
    ID is not known yet.
    """
    return replace_refs(_msg(guild, key, **fields))

#: The steps the wizard walks, in order. ``done`` is the summary card.
STEPS = ("welcome", "leveling", "automod", "words", "onboarding", "logging", "tickets", "ai")

#: AutoMod toggles the wizard offers, paired with their message-table key.
FILTERS = (
    ("antispam", "filter_antispam"),
    ("antilink", "filter_antilink"),
    ("badwords", "filter_badwords"),
    ("massmention", "filter_massmention"),
    ("antiraid", "filter_antiraid"),
)

#: Which channel the ``onboarding``, ``logging`` and ``tickets`` steps fill in.
CHANNEL_FIELDS = {
    "onboarding": "welcome_channel",
    "logging": "log_channel",
    "tickets": "ticket_channel",
}

#: The state each step edits. Leaving a step without pressing **Save &
#: continue** puts these back the way they were, so a skipped or abandoned
#: change is never written to the server.
STEP_FIELDS = {
    "leveling": ("leveling",),
    "automod": ("filters",),
    "words": ("presets", "words"),
    "onboarding": ("welcome_channel",),
    "logging": ("log_channel",),
    "tickets": ("ticket_channel",),
    "ai": ("ai",),
}

#: Cap on words a single wizard run queues, so one paste cannot exceed the
#: server's whole blocked-word budget.
MAX_WIZARD_WORDS = 200


@dataclass
class SetupState:
    """Everything one wizard run has decided so far."""

    step: str = "welcome"
    leveling: bool = False
    filters: dict = field(default_factory=dict)
    presets: list = field(default_factory=list)
    words: list = field(default_factory=list)
    welcome_channel: int | None = None
    log_channel: int | None = None
    ticket_channel: int | None = None
    ai: bool | None = None
    report: list = field(default_factory=list)
    skipped: set = field(default_factory=set)


def _may_manage(interaction: discord.Interaction) -> bool:
    """Whether the member may change this server's settings (Manage Server)."""
    permissions = getattr(interaction.user, "guild_permissions", None)
    return bool(permissions is not None and permissions.manage_guild)


async def _deny(interaction: discord.Interaction) -> None:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=msg(interaction.guild, "no_permission")),
        accent_colour=discord.Color.red(),
    ))
    await interaction.response.send_message(view=view, ephemeral=True)


def _moderation(bot):
    """The moderation-config cog, which owns the AutoMod/blocked-word settings."""
    return bot.get_cog("ModerationUtils")


def _preset_label(preset, lang: str) -> str:
    from cogs.moderation._presets import preset_label

    return preset_label(preset, lang)


async def build_state(bot: commands.Bot, guild: discord.Guild) -> SetupState:
    """Read the server's current settings into a fresh wizard state."""
    state = SetupState()

    leveling = bot.get_cog("Leveling")
    if leveling is not None:
        try:
            cfg = await leveling._guild_cfg(guild.id)
            state.leveling = bool(cfg.get("xp_enabled", False))
        except Exception as error:  # noqa: BLE001 - a read failure must not stop setup
            logging.warning("Setup", f"Could not read leveling config for {guild.id}: {error}")

    moderation = _moderation(bot)
    if moderation is not None:
        try:
            cfg = moderation.get_guild_config(guild.id)
            state.filters = {
                key: bool(cfg.get("automod", {}).get(key, False)) for key, _ in FILTERS
            }
            state.presets = list(moderation.get_badwords_presets(guild.id))
        except Exception as error:  # noqa: BLE001
            logging.warning("Setup", f"Could not read AutoMod config for {guild.id}: {error}")
    if not state.filters:
        state.filters = {key: False for key, _ in FILTERS}

    try:
        from utils.onboarding.utils import get_config

        onboarding = await get_config(guild.id)
        state.welcome_channel = onboarding.welcome_channel
    except Exception as error:  # noqa: BLE001
        logging.warning("Setup", f"Could not read onboarding config for {guild.id}: {error}")

    logger = bot.get_cog("ServerLogger")
    if logger is not None:
        try:
            cfg = logger._get_cfg(guild.id)
            state.log_channel = next(
                (cfg[key] for key in cfg if key != "disabled" and cfg.get(key)), None
            )
        except Exception as error:  # noqa: BLE001
            logging.warning("Setup", f"Could not read logging config for {guild.id}: {error}")

    try:
        from utils.ai.config import load_config

        ai = await load_config(guild.id)
        state.ai = str(ai.get("enabled")) == "True"
    except Exception as error:  # noqa: BLE001
        logging.warning("Setup", f"Could not read AI config for {guild.id}: {error}")

    return state


# ──────────────────────────────────────────────────
#  SHARED COMPONENTS
# ──────────────────────────────────────────────────

class _StepButton(discord.ui.Button):
    """One button on the wizard; every action is handled in one place."""

    def __init__(self, wizard: "SetupWizard", action: str, *, label: str,
                 style: discord.ButtonStyle, emoji=None, disabled: bool = False):
        super().__init__(label=label, style=style, emoji=emoji, disabled=disabled)
        self.wizard = wizard
        self.action = action

    async def callback(self, interaction: discord.Interaction):
        await self.wizard.handle(interaction, self.action)


class _WordsModal(discord.ui.Modal):
    """Collects a paste of blocked words (commas or new lines)."""

    def __init__(self, wizard: "SetupWizard"):
        super().__init__(title=msg(wizard.guild, "words_modal_title"))
        self.wizard = wizard
        self.words = discord.ui.TextInput(
            label=msg(wizard.guild, "words_modal_label"),
            placeholder=msg(wizard.guild, "words_modal_placeholder"),
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=2000,
        )
        self.add_item(self.words)

    async def on_submit(self, interaction: discord.Interaction):
        self.wizard.queue_words(self.words.value)
        # Rebuild before editing so the step's summary shows the new count.
        await self.wizard.refresh(interaction)


class _PresetSelect(discord.ui.Select):
    """Curated filters, multi-select, pre-checked from the saved config."""

    def __init__(self, wizard: "SetupWizard"):
        from cogs.moderation._presets import PRESET_FILTERS

        lang = get_lang(wizard.guild)
        options = [
            discord.SelectOption(
                label=_preset_label(preset, lang),
                value=preset.key,
                description=preset.descriptions.get(lang) or preset.descriptions["en"],
                default=preset.key in wizard.state.presets,
            )
            for preset in PRESET_FILTERS[:25]
        ]
        super().__init__(
            placeholder=msg(wizard.guild, "presets_placeholder"),
            options=options,
            min_values=0,
            max_values=len(options),
        )
        self.wizard = wizard

    async def callback(self, interaction: discord.Interaction):
        self.wizard.state.presets = list(self.values)
        # Discord draws a select's selection from its options' ``default`` flags,
        # so re-sending the same view would leave the menu looking unchanged.
        # ``refresh`` rebuilds it from the state that was just stored.
        await self.wizard.refresh(interaction)


class _ChannelSelect(discord.ui.ChannelSelect):
    """Picks the channel one step configures."""

    def __init__(self, wizard: "SetupWizard", step: str):
        super().__init__(
            placeholder=msg(wizard.guild, f"{step}_placeholder"),
            channel_types=[discord.ChannelType.text, discord.ChannelType.news],
            min_values=1,
            max_values=1,
        )
        self.wizard = wizard
        self.step = step

    async def callback(self, interaction: discord.Interaction):
        channel = self.values[0]
        setattr(self.wizard.state, CHANNEL_FIELDS[self.step], channel.id)
        # Rebuild so the step's summary line shows the channel that was picked.
        await self.wizard.refresh(interaction)


# ──────────────────────────────────────────────────
#  THE WIZARD
# ──────────────────────────────────────────────────

class SetupWizard(discord.ui.LayoutView):
    """The single message every step of ``/setup`` renders into."""

    def __init__(self, bot: commands.Bot, guild: discord.Guild,
                 author: discord.abc.User, state: SetupState):
        super().__init__(timeout=900)
        self.bot = bot
        self.guild = guild
        self.author = author
        self.state = state
        self.message: discord.Message | None = None
        # The last saved values, one entry per editable field. Every control on
        # a step only edits ``state``; ``_saved`` is what the server actually
        # has, and is only updated after a step is saved.
        self._saved = self._snapshot()
        self._build()

    # ── permission gate ────────────────────────────

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if _may_manage(interaction):
            return True
        await _deny(interaction)
        return False

    # ── rendering ──────────────────────────────────

    def _header(self, step: str) -> str:
        """Title first, then a quiet progress line — the name is what a member
        scans for, the counter only tells them how much is left."""
        if step == "welcome":
            return msg(self.guild, "title")
        if step == "done":
            return msg(self.guild, "done_title")
        names = {
            "leveling": "leveling_name",
            "automod": "automod_name",
            "words": "words_name",
            "onboarding": "onboarding_name",
            "logging": "logging_name",
            "tickets": "tickets_name",
            "ai": "ai_name",
        }
        # The welcome card is not a step, so leveling is "1 of 7".
        current = STEPS.index(step)
        return "\n".join((
            msg(self.guild, names[step]),
            msg(self.guild, "step_label", current=current, total=len(STEPS) - 1),
        ))

    def _nav_row(self, step: str) -> discord.ui.ActionRow:
        items = []
        index = STEPS.index(step)
        if index > 0:
            items.append(_StepButton(
                self, "back", label=msg(self.guild, "back"),
                style=discord.ButtonStyle.secondary,
            ))
        items.append(_StepButton(
            self, "skip", label=msg(self.guild, "skip"),
            style=discord.ButtonStyle.secondary,
        ))
        items.append(_StepButton(
            self, "next",
            label=msg(self.guild, "finish" if step == STEPS[-1] else "next"),
            style=discord.ButtonStyle.success, emoji=get_emoji("tick"),
        ))
        return discord.ui.ActionRow(*items)

    def _build(self):
        self.clear_items()
        step = self.state.step
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=self._header(step)),
        )
        if step == "welcome":
            # The estimate belongs under the title, before the rule, so it reads
            # as part of the heading rather than as body copy.
            container.add_item(discord.ui.TextDisplay(content=msg(self.guild, "welcome_meta")))
        container.add_item(discord.ui.Separator(
            visible=True, spacing=discord.SeparatorSpacing.small))

        if step == "welcome":
            container.add_item(discord.ui.TextDisplay(content=msg(self.guild, "intro")))
            container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
            container.add_item(discord.ui.TextDisplay(content=msg(self.guild, "welcome_body")))
            container.add_item(discord.ui.ActionRow(
                _StepButton(self, "start", label=msg(self.guild, "start"),
                            style=discord.ButtonStyle.success, emoji=get_emoji("tick")),
                _StepButton(self, "finish_early", label=msg(self.guild, "skip_setup"),
                            style=discord.ButtonStyle.secondary),
            ))

        elif step == "leveling":
            container.add_item(discord.ui.TextDisplay(content=msg(self.guild, "leveling_body")))
            container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
            container.add_item(discord.ui.TextDisplay(content=msg(
                self.guild, "leveling_state",
                state=msg(self.guild, "leveling_enabled" if self.state.leveling else "leveling_disabled"),
            )))
            container.add_item(discord.ui.ActionRow(
                _StepButton(
                    self, "leveling_on", label=msg(self.guild, "leveling_on"),
                    style=(discord.ButtonStyle.success if self.state.leveling else discord.ButtonStyle.secondary),
                    emoji=get_emoji("leveling") if self.state.leveling else None,
                ),
                _StepButton(
                    self, "leveling_off", label=msg(self.guild, "leveling_off"),
                    style=(discord.ButtonStyle.secondary if self.state.leveling else discord.ButtonStyle.success),
                    emoji=None if self.state.leveling else get_emoji("tick"),
                ),
            ))
            container.add_item(discord.ui.TextDisplay(content=msg(self.guild, "leveling_hint")))
            container.add_item(self._nav_row(step))

        elif step == "automod":
            container.add_item(discord.ui.TextDisplay(content=msg(self.guild, "automod_body")))
            container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
            container.add_item(discord.ui.TextDisplay(content=self._filter_summary()))
            first = [_StepButton(
                self, f"filter:{key}", label=msg(self.guild, label_key),
                style=(discord.ButtonStyle.success if self.state.filters.get(key) else discord.ButtonStyle.secondary),
                emoji=get_emoji("tick") if self.state.filters.get(key) else get_emoji("cross"),
            ) for key, label_key in FILTERS[:3]]
            second = [_StepButton(
                self, f"filter:{key}", label=msg(self.guild, label_key),
                style=(discord.ButtonStyle.success if self.state.filters.get(key) else discord.ButtonStyle.secondary),
                emoji=get_emoji("tick") if self.state.filters.get(key) else get_emoji("cross"),
            ) for key, label_key in FILTERS[3:]]
            container.add_item(discord.ui.ActionRow(*first))
            container.add_item(discord.ui.ActionRow(*second))
            container.add_item(discord.ui.TextDisplay(content=msg(self.guild, "automod_hint")))
            container.add_item(self._nav_row(step))

        elif step == "words":
            container.add_item(discord.ui.TextDisplay(content=msg(self.guild, "words_body")))
            container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
            container.add_item(discord.ui.TextDisplay(content=self._words_summary()))
            container.add_item(discord.ui.ActionRow(_PresetSelect(self)))
            container.add_item(discord.ui.ActionRow(
                _StepButton(self, "add_words", label=msg(self.guild, "words_add"),
                            style=discord.ButtonStyle.primary, emoji=get_emoji("plus")),
            ))
            container.add_item(discord.ui.TextDisplay(content=msg(self.guild, "presets_hint")))
            container.add_item(self._nav_row(step))

        elif step in CHANNEL_FIELDS:
            container.add_item(discord.ui.TextDisplay(content=msg(self.guild, f"{step}_body")))
            container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
            container.add_item(discord.ui.TextDisplay(content=self._channel_summary(step)))
            container.add_item(discord.ui.ActionRow(_ChannelSelect(self, step)))
            container.add_item(discord.ui.TextDisplay(content=msg(self.guild, f"{step}_hint")))
            container.add_item(self._nav_row(step))

        elif step == "ai":
            enabled = bool(self.state.ai)
            container.add_item(discord.ui.TextDisplay(content=msg(self.guild, "ai_body")))
            container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
            container.add_item(discord.ui.TextDisplay(content=msg(
                self.guild, "ai_state",
                state=msg(self.guild, "ai_enabled" if enabled else "ai_disabled"),
            )))
            container.add_item(discord.ui.ActionRow(
                _StepButton(self, "ai_on", label=msg(self.guild, "ai_on"),
                            style=(discord.ButtonStyle.success if enabled else discord.ButtonStyle.secondary)),
                _StepButton(self, "ai_off", label=msg(self.guild, "ai_off"),
                    style=(discord.ButtonStyle.secondary if enabled else discord.ButtonStyle.danger)),
            ))
            container.add_item(discord.ui.TextDisplay(content=msg(self.guild, "ai_hint")))
            container.add_item(self._nav_row(step))

        else:  # done
            report = "\n".join(self.state.report) or msg(self.guild, "done_empty")
            container.add_item(discord.ui.TextDisplay(content=msg(
                self.guild, "done_body", report=report)))
            container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
            container.add_item(discord.ui.TextDisplay(content=msg(
                self.guild, "done_next", docs=DOCS)))
            container.add_item(discord.ui.ActionRow(
                discord.ui.Button(
                    label=msg(self.guild, "dashboard_button"),
                    style=discord.ButtonStyle.link,
                    url=dashboard_url(self.guild.id),
                ),
                discord.ui.Button(
                    label=msg(self.guild, "docs_button"),
                    style=discord.ButtonStyle.link,
                    url=DOCS,
                ),
            ))

        if step not in ("welcome", "done"):
            # The welcome card already reassures people; the footer's "Skip this
            # step" wording only makes sense once there is a step on screen.
            container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
            container.add_item(discord.ui.TextDisplay(content=msg(self.guild, "footer")))

        container.accent_colour = discord.Colour(0x5865F2)
        self.add_item(container)

    # ── drafts ─────────────────────────────────────

    def _snapshot(self) -> dict:
        """Copy the editable fields, so restoring never aliases a live dict."""
        return {
            "leveling": self.state.leveling,
            "filters": dict(self.state.filters),
            "presets": list(self.state.presets),
            "words": list(self.state.words),
            "welcome_channel": self.state.welcome_channel,
            "log_channel": self.state.log_channel,
            "ticket_channel": self.state.ticket_channel,
            "ai": self.state.ai,
        }

    def _commit_current(self) -> None:
        """The step was saved: it is now the baseline for future visits."""
        self._saved = self._snapshot()

    def _discard_current(self) -> None:
        """Throw away unsaved edits on the step being left.

        Tapping a filter, picking a channel or typing words is only a draft;
        the step is saved when the member presses **Save & continue**. Back and
        Skip therefore put the draft back to the last saved values, so a change
        the member did not confirm is never stored and never reappears later.
        """
        for field in STEP_FIELDS.get(self.state.step, ()):
            value = self._saved.get(field)
            if isinstance(value, dict):
                setattr(self.state, field, dict(value))
            elif isinstance(value, list):
                setattr(self.state, field, list(value))
            else:
                setattr(self.state, field, value)

    # ── step summaries ─────────────────────────────

    def _filter_summary(self) -> str:
        """Every check with its state spelled out — an icon alone is unreadable
        when emojis are disabled or a member cannot tell green from grey."""
        lines = []
        for key, label_key in FILTERS:
            enabled = self.state.filters.get(key)
            lines.append(msg(
                self.guild, "filter_line",
                icon=get_emoji("tick") if enabled else get_emoji("cross"),
                name=msg(self.guild, label_key),
                state=msg(self.guild, "filter_on" if enabled else "filter_off"),
            ))
        return "\n".join(lines)

    def _words_summary(self) -> str:
        presets = len(self.state.presets)
        if not self.state.words:
            body = msg(self.guild, "words_empty")
        else:
            shown = ", ".join(f"`{word}`" for word in self.state.words[:12])
            body = msg(self.guild, "words_queued", words=shown)
        return msg(self.guild, "words_summary", body=body, presets=presets)

    def _channel_summary(self, step: str) -> str:
        channel_id = getattr(self.state, CHANNEL_FIELDS[step])
        if not channel_id:
            return msg(self.guild, f"{step}_none")
        return msg(self.guild, f"{step}_selected", channel=f"<#{channel_id}>")

    # ── state mutations ────────────────────────────

    def queue_words(self, raw: str) -> tuple[int, bool]:
        """Queue a pasted word list, returning ``(added, hit_the_cap)``."""
        existing = {word.lower() for word in self.state.words}
        added = 0
        for chunk in raw.replace("\n", ",").split(","):
            word = " ".join(chunk.split())
            if not word or word.lower() in existing:
                continue
            if len(self.state.words) >= MAX_WIZARD_WORDS:
                return added, True
            self.state.words.append(word)
            existing.add(word.lower())
            added += 1
        return added, False

    async def handle(self, interaction: discord.Interaction, action: str):
        state = self.state

        if action == "start":
            state.step = "leveling"
            return await self.refresh(interaction)
        if action == "finish_early":
            state.step = "done"
            return await self.refresh(interaction)
        if action == "back":
            # Back is not a save: drop whatever was drafted on this step.
            self._discard_current()
            index = max(0, STEPS.index(state.step) - 1)
            state.step = STEPS[index]
            return await self.refresh(interaction)
        if action == "skip":
            self._discard_current()
            state.skipped.add(state.step)
            return await self._advance(interaction)
        if action == "next":
            try:
                await self._apply(interaction)
            except Exception as error:  # noqa: BLE001 - report, never crash the panel
                logging.warning("Setup", f"{state.step} step failed for {self.guild.id}: {error}")
                return await interaction.response.send_message(
                    msg(self.guild, "error", error=str(error)[:300]), ephemeral=True
                )
            # Only a successful save makes the edits the new baseline.
            self._commit_current()
            return await self._advance(interaction)
        if action == "leveling_on":
            state.leveling = True
            return await self.refresh(interaction)
        if action == "leveling_off":
            state.leveling = False
            return await self.refresh(interaction)
        if action.startswith("filter:"):
            key = action.split(":", 1)[1]
            state.filters[key] = not state.filters.get(key, False)
            return await self.refresh(interaction)
        if action == "add_words":
            return await interaction.response.send_modal(_WordsModal(self))
        if action == "ai_on":
            state.ai = True
            return await self.refresh(interaction)
        if action == "ai_off":
            state.ai = False
            return await self.refresh(interaction)

    async def refresh(self, interaction: discord.Interaction):
        self._build()
        await interaction.response.edit_message(view=self)

    async def _advance(self, interaction: discord.Interaction):
        index = STEPS.index(self.state.step)
        self.state.step = STEPS[index + 1] if index + 1 < len(STEPS) else "done"
        self._build()
        await interaction.response.edit_message(view=self)

    # ── saving ─────────────────────────────────────

    async def _apply(self, interaction: discord.Interaction) -> None:
        step = self.state.step
        if step == "leveling":
            await self._apply_leveling(interaction)
        elif step == "automod":
            await self._apply_automod(interaction)
        elif step == "words":
            await self._apply_words(interaction)
        elif step == "onboarding":
            await self._apply_onboarding(interaction)
        elif step == "logging":
            await self._apply_logging(interaction)
        elif step == "tickets":
            await self._apply_tickets(interaction)
        elif step == "ai":
            await self._apply_ai(interaction)

    async def _apply_leveling(self, interaction: discord.Interaction) -> None:
        leveling = self.bot.get_cog("Leveling")
        if leveling is None:
            raise RuntimeError("the leveling cog is not loaded")
        cfg = await leveling._guild_cfg(self.guild.id)
        cfg["xp_enabled"] = bool(self.state.leveling)
        await leveling._save_guild_cfg(self.guild.id, cfg)
        self.state.report.append(msg(
            self.guild, "leveling_saved_on" if self.state.leveling else "leveling_saved_off"))

    async def _apply_automod(self, interaction: discord.Interaction) -> None:
        moderation = _moderation(self.bot)
        if moderation is None:
            raise RuntimeError("the moderation settings cog is not loaded")
        cfg = moderation.get_guild_config(self.guild.id)
        for key, _ in FILTERS:
            cfg["automod"][key] = bool(self.state.filters.get(key, cfg["automod"].get(key, False)))
        moderation.save_config(self.guild.id)
        enabled = [
            msg(self.guild, label_key) for key, label_key in FILTERS if self.state.filters.get(key)
        ]
        self.state.report.append(msg(
            self.guild, "automod_saved",
            filters=", ".join(enabled) if enabled else msg(self.guild, "automod_none"),
        ))

    async def _apply_words(self, interaction: discord.Interaction) -> None:
        moderation = _moderation(self.bot)
        if moderation is None:
            raise RuntimeError("the moderation settings cog is not loaded")
        for word in self.state.words:
            moderation.add_blocked_word(self.guild.id, word)
        moderation.set_badwords_presets(self.guild.id, self.state.presets)
        # A word list nobody reads is a list of decorations: switch the filter on
        # when this step actually configured something.
        if self.state.words or self.state.presets:
            cfg = moderation.get_guild_config(self.guild.id)
            cfg["automod"]["badwords"] = True
            moderation.save_config(self.guild.id)
        self.state.report.append(msg(
            self.guild, "words_saved",
            words=len(self.state.words), presets=len(self.state.presets),
        ))

    async def _apply_onboarding(self, interaction: discord.Interaction) -> None:
        channel_id = self.state.welcome_channel
        if not channel_id:
            return
        from utils.onboarding.utils import get_config, update_config

        cfg = await get_config(self.guild.id)
        cfg.welcome_channel = int(channel_id)
        await update_config(self.guild.id, cfg)
        self.state.report.append(msg(
            self.guild, "onboarding_saved", channel=f"<#{channel_id}>"))

    async def _apply_logging(self, interaction: discord.Interaction) -> None:
        channel_id = self.state.log_channel
        if not channel_id:
            return
        logger = self.bot.get_cog("ServerLogger")
        if logger is None:
            raise RuntimeError("the logging cog is not loaded")
        from cogs.logging.formatters import CATEGORIES

        cfg = dict(logger._get_cfg(self.guild.id))
        before = dict(cfg)
        for category in CATEGORIES:
            cfg[category] = int(channel_id)
        await logger.save_config(
            self.guild, cfg, actor=interaction.user,
            summary=f"Setup wizard → every category → <#{channel_id}>", before=before,
        )
        self.state.report.append(msg(
            self.guild, "logging_saved", channel=f"<#{channel_id}>"))

    async def _apply_tickets(self, interaction: discord.Interaction) -> None:
        channel_id = self.state.ticket_channel
        if not channel_id:
            return
        channel = self.guild.get_channel(int(channel_id))
        if channel is None:
            raise RuntimeError("that channel no longer exists")
        from cogs.tickets.views import TicketPanelView
        from utils.tickets.utils import async_update_ticket_config, get_ticket_config

        cfg = get_ticket_config(self.guild.id)
        me = self.guild.me
        if me is not None and not channel.permissions_for(me).send_messages:
            raise RuntimeError(f"I cannot send messages in <#{channel_id}>")
        sent = await channel.send(view=TicketPanelView(self.guild.id, cfg))
        cfg.panel_message_id = sent.id
        cfg.panel_channel_id = channel.id
        await async_update_ticket_config(self.guild.id, cfg)
        self.state.report.append(msg(
            self.guild, "tickets_saved", channel=channel.mention))

    async def _apply_ai(self, interaction: discord.Interaction) -> None:
        if self.state.ai is None:
            return
        from utils.ai.config import save_config

        await save_config(
            self.guild.id, "enabled", "True" if self.state.ai else "False")
        self.state.report.append(msg(
            self.guild, "ai_saved_on" if self.state.ai else "ai_saved_off"))

    # ── lifecycle ──────────────────────────────────

    async def on_timeout(self):
        if self.message is None:
            return
        try:
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=msg(self.guild, "timeout")),
                accent_colour=discord.Color.greyple(),
            ))
            await self.message.edit(view=view)
        except discord.HTTPException:
            pass


class Setup(commands.Cog):
    """The guided first-run setup command."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="setup",
        description=CMDS.text("setup.description"),
        help=CMDS.help("setup"),
    )
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def setup(self, ctx: commands.Context):
        """Post the guided setup panel and let the admin walk through it."""
        state = await build_state(self.bot, ctx.guild)
        wizard = SetupWizard(self.bot, ctx.guild, ctx.author, state)
        message = await ctx.send(view=wizard, allowed_mentions=discord.AllowedMentions.none())
        wizard.message = message
        logging.info("Setup", f"Setup wizard opened in {ctx.guild.name} ({ctx.guild.id})")


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
