"""``/setup``: the guided wizard, and the new-server leveling default.

The wizard posts one public panel and saves each step as it is finished. These
checks cover the parts that can silently break: the panel has to render for every
step, every step has to offer a skip, only a server manager may drive it, and a
freshly invited server has to start with leveling off.
"""

from __future__ import annotations

import asyncio
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import discord  # noqa: E402

from cogs.leveling import panel as leveling_panel  # noqa: E402
from cogs.leveling.cog import Leveling  # noqa: E402
from cogs.setup import cog as setup_cog  # noqa: E402


# ──────────────────────────────────────────────────
#  Fakes
# ──────────────────────────────────────────────────

class _Response:
    def __init__(self):
        self.sent = None
        self.edited = None

    async def send_message(self, *args, **kwargs):
        self.sent = (args, kwargs)

    async def edit_message(self, *args, **kwargs):
        self.edited = (args, kwargs)


class _Permissions:
    def __init__(self, manage_guild: bool):
        self.manage_guild = manage_guild


class _User:
    def __init__(self, user_id: int = 1, manage_guild: bool = False):
        self.id = user_id
        self.guild_permissions = _Permissions(manage_guild)


class _Interaction:
    def __init__(self, *, manage_guild: bool = False, user_id: int = 1, guild=None):
        self.user = _User(user_id, manage_guild)
        self.guild = guild
        self.response = _Response()


class _Guild:
    def __init__(self, guild_id: int = 99):
        self.id = guild_id
        self.name = "Test Server"
        self.preferred_locale = "en"
        self.me = None

    def get_channel(self, _channel_id):
        return None


class _Pool:
    """A pool that answers the one query the new-guild default needs."""

    def __init__(self, existing=None):
        self.existing = existing
        self.executed = []

    async def fetchrow(self, query, *args):
        return self.existing

    async def execute(self, query, *args):
        self.executed.append((query, args))


class _Cog:
    def __init__(self, bot):
        self.bot = bot


def _texts(item) -> list[str]:
    out = []
    for child in getattr(item, "children", []) or []:
        if isinstance(child, str):
            continue
        content = getattr(child, "content", None)
        if isinstance(content, str):
            out.append(content)
        out.extend(_texts(child))
    return out


def _wizard(state: setup_cog.SetupState, *, bot=None, guild=None):
    return setup_cog.SetupWizard(
        bot or types.SimpleNamespace(user=types.SimpleNamespace(
            display_avatar=types.SimpleNamespace(url="https://example.test/a.png"))),
        guild or _Guild(),
        _User(user_id=7, manage_guild=True),
        state,
    )


# ──────────────────────────────────────────────────
#  Rendering
# ──────────────────────────────────────────────────

def test_every_step_renders_inside_discords_budget():
    for step in setup_cog.STEPS + ("done",):
        state = setup_cog.SetupState(
            step=step,
            filters={key: True for key, _ in setup_cog.FILTERS},
            presets=["slurs"],
            words=["badword"],
        )
        state.report = ["{tick} something changed"]
        wizard = _wizard(state)
        body = "\n".join(_texts(wizard))
        assert body.strip(), f"{step} rendered no text"
        # Components V2 caps the text of one message at 4,000 characters.
        assert len(body) < 4000, f"{step} renders {len(body)} characters"


def test_every_step_offers_a_skip():
    for step in setup_cog.STEPS[1:]:
        wizard = _wizard(setup_cog.SetupState(step=step))
        actions = _button_actions(wizard)
        assert "skip" in actions, f"{step} has no skip button"


def _button_actions(item) -> list[str]:
    actions = []
    for child in getattr(item, "children", []) or []:
        if isinstance(child, str):
            continue
        action = getattr(child, "action", None)
        if action:
            actions.append(action)
        actions.extend(_button_actions(child))
    return actions


# ──────────────────────────────────────────────────
#  Permissions
# ──────────────────────────────────────────────────

def _labels(item) -> list[str]:
    labels = []
    for child in getattr(item, "children", []) or []:
        if isinstance(child, str):
            continue
        label = getattr(child, "label", None)
        if label:
            labels.append(label)
        labels.extend(_labels(child))
    return labels


def test_skipping_a_step_discards_the_change_and_saves_nothing():
    class _Moderation:
        def __init__(self):
            self.saved = []

        def get_guild_config(self, _guild_id):
            return {"automod": {key: False for key, _ in setup_cog.FILTERS}}

        def save_config(self, guild_id):
            self.saved.append(guild_id)

    moderation = _Moderation()
    bot = types.SimpleNamespace(
        get_cog=lambda name: moderation if name == "ModerationUtils" else None,
    )
    state = setup_cog.SetupState(
        step="automod", filters={key: False for key, _ in setup_cog.FILTERS})
    wizard = _wizard(state, bot=bot)
    interaction = _Interaction(manage_guild=True, guild=_Guild())

    asyncio.run(wizard.handle(interaction, "filter:antispam"))
    assert state.filters["antispam"] is True

    asyncio.run(wizard.handle(interaction, "skip"))

    assert state.step == "words"
    # The draft is gone and nothing reached the server: Skip is not a save.
    assert state.filters["antispam"] is False
    assert moderation.saved == []


def test_going_back_discards_an_unsaved_channel_pick():
    state = setup_cog.SetupState(step="onboarding")
    wizard = _wizard(state)
    select = setup_cog._ChannelSelect(wizard, "onboarding")
    select._values = [types.SimpleNamespace(id=555)]
    interaction = _Interaction(manage_guild=True, guild=_Guild())

    asyncio.run(select.callback(interaction))
    assert state.welcome_channel == 555

    asyncio.run(wizard.handle(interaction, "back"))

    assert state.step == "words"
    assert state.welcome_channel is None


def test_a_saved_step_stays_saved_when_visited_again():
    saved = {}

    class _Leveling:
        async def _guild_cfg(self, _guild_id):
            return {"xp_enabled": False}

        async def _save_guild_cfg(self, _guild_id, cfg):
            saved["cfg"] = cfg

    bot = types.SimpleNamespace(
        get_cog=lambda name: _Leveling() if name == "Leveling" else None,
    )
    state = setup_cog.SetupState(step="leveling", leveling=False)
    wizard = _wizard(state, bot=bot)
    interaction = _Interaction(manage_guild=True, guild=_Guild())

    asyncio.run(wizard.handle(interaction, "leveling_on"))
    asyncio.run(wizard.handle(interaction, "next"))
    assert saved["cfg"]["xp_enabled"] is True
    assert state.step == "automod"

    asyncio.run(wizard.handle(interaction, "back"))

    # Saved values come back; only the abandoned draft is dropped.
    assert state.step == "leveling"
    assert state.leveling is True


def test_skipping_the_words_step_drops_the_queued_words():
    state = setup_cog.SetupState(step="words")
    wizard = _wizard(state)
    interaction = _Interaction(manage_guild=True, guild=_Guild())

    wizard.queue_words("alpha, beta")
    assert state.words == ["alpha", "beta"]

    asyncio.run(wizard.handle(interaction, "skip"))

    assert state.step == "onboarding"
    assert state.words == []


def test_the_counter_ignores_the_welcome_and_summary_cards():
    wizard = _wizard(setup_cog.SetupState())

    assert "Step 1 of 7" in wizard._header("leveling")
    assert "Step 7 of 7" in wizard._header("ai")
    assert "Step" not in wizard._header("welcome")
    assert "Step" not in wizard._header("done")


def test_the_last_step_offers_finish_instead_of_continue():
    wizard = _wizard(setup_cog.SetupState(step="ai"))
    labels = _labels(wizard)

    assert "Finish" in labels
    assert "Save & continue" not in labels
    assert "Skip this step" in labels


def test_enabled_checks_are_spelled_out_not_only_icons():
    state = setup_cog.SetupState(
        step="automod",
        filters={key: False for key, _ in setup_cog.FILTERS} | {"antispam": True},
    )
    summary = _wizard(state)._filter_summary()

    assert "Spam — **on**" in summary
    assert "Invite links — **off**" in summary


def test_the_welcome_card_says_how_long_it_takes():
    body = "\n".join(_texts(_wizard(setup_cog.SetupState(step="welcome"))))

    assert "7 short steps" in body
    assert "2 minutes" in body
    assert "Start setup" in _labels(_wizard(setup_cog.SetupState(step="welcome")))


def test_a_normal_member_cannot_drive_the_public_panel():
    wizard = _wizard(setup_cog.SetupState())
    interaction = _Interaction(manage_guild=False, guild=_Guild())

    assert asyncio.run(wizard.interaction_check(interaction)) is False
    assert interaction.response.sent is not None


def test_a_server_manager_can_drive_the_panel():
    wizard = _wizard(setup_cog.SetupState())
    interaction = _Interaction(manage_guild=True, guild=_Guild())

    assert asyncio.run(wizard.interaction_check(interaction)) is True


# ──────────────────────────────────────────────────
#  State and saving
# ──────────────────────────────────────────────────

def test_queue_words_splits_dedupes_and_ignores_blanks():
    state = setup_cog.SetupState()
    wizard = _wizard(state)

    added, full = wizard.queue_words("bad, worse\nbad\n\n  ok  word  ,")

    assert (added, full) == (3, False)
    assert state.words == ["bad", "worse", "ok word"]


def _find(view, kind):
    for child in getattr(view, "children", []) or []:
        if isinstance(child, kind):
            return child
        found = _find(child, kind)
        if found is not None:
            return found
    return None


def test_picking_blocked_word_presets_rerenders_the_step():
    state = setup_cog.SetupState(step="words")
    wizard = _wizard(state)
    select = setup_cog._PresetSelect(wizard)
    # ``values`` reads Discord's per-interaction ContextVar, falling back to
    # this attribute when a callback is invoked outside a real interaction.
    select._values = ["slurs"]
    interaction = _Interaction(manage_guild=True, guild=_Guild())

    asyncio.run(select.callback(interaction))

    assert state.presets == ["slurs"]
    edited = interaction.response.edited
    assert edited is not None, "the select never edited the message"
    rebuilt = edited[1]["view"]
    # The menu has to be rebuilt from the new state: Discord draws a select's
    # checkmarks from the options' ``default`` flags, not from the callback.
    menu = _find(rebuilt, setup_cog._PresetSelect)
    defaults = {option.value: option.default for option in menu.options}
    assert defaults["slurs"] is True
    assert defaults["profanity"] is False
    assert "**Ready-made lists selected:** 1" in "\n".join(_texts(rebuilt))


def test_picking_a_channel_updates_the_steps_summary():
    state = setup_cog.SetupState(step="onboarding")
    wizard = _wizard(state)
    select = setup_cog._ChannelSelect(wizard, "onboarding")
    select._values = [types.SimpleNamespace(id=555)]
    interaction = _Interaction(manage_guild=True, guild=_Guild())

    asyncio.run(select.callback(interaction))

    assert state.welcome_channel == 555
    rebuilt = interaction.response.edited[1]["view"]
    assert "<#555>" in "\n".join(_texts(rebuilt))


def test_leveling_step_writes_what_was_chosen():
    saved = {}

    class _Leveling:
        async def _guild_cfg(self, guild_id):
            return {"xp_enabled": True}

        async def _save_guild_cfg(self, guild_id, cfg):
            saved["guild_id"] = guild_id
            saved["cfg"] = cfg

    bot = types.SimpleNamespace(
        get_cog=lambda name: _Leveling() if name == "Leveling" else None,
    )
    state = setup_cog.SetupState(step="leveling", leveling=False)
    wizard = _wizard(state, bot=bot)

    asyncio.run(wizard._apply_leveling(_Interaction(guild=_Guild())))

    assert saved["guild_id"] == 99
    assert saved["cfg"]["xp_enabled"] is False
    assert state.report


def test_build_state_reads_the_saved_settings():
    class _Leveling:
        async def _guild_cfg(self, guild_id):
            return {"xp_enabled": False}

    bot = types.SimpleNamespace(
        get_cog=lambda name: _Leveling() if name == "Leveling" else None,
    )
    state = asyncio.run(setup_cog.build_state(bot, _Guild()))

    assert state.leveling is False
    assert set(state.filters) == {key for key, _ in setup_cog.FILTERS}


# ──────────────────────────────────────────────────
#  New-guild leveling default
# ──────────────────────────────────────────────────

def test_new_guilds_start_with_leveling_off():
    assert leveling_panel.NEW_GUILD_LEVEL_CONFIG["xp_enabled"] is False
    # A missing row still reads as enabled so an existing server does not stop.
    assert leveling_panel.DEFAULT_GUILD_LEVEL_CONFIG["xp_enabled"] is True


def test_joining_writes_the_disabled_default_row():
    guild = _Guild()
    pool = _Pool(existing=None)
    cog = Leveling(types.SimpleNamespace(cxn=pool))

    asyncio.run(cog.on_guild_join(guild))

    inserted = pool.executed
    assert inserted, "on_guild_join did not save a leveling row"
    query, args = inserted[0]
    assert "level_config" in query
    # guild_id, xp_enabled, multiplier, cooldown, ...
    assert args[0] == guild.id
    assert args[1] == 0


def test_rejoining_never_resets_a_configured_server():
    cog = Leveling(types.SimpleNamespace(cxn=_Pool(existing={"guild_id": 99})))

    asyncio.run(cog.on_guild_join(_Guild()))

    assert cog.bot.cxn.executed == []


def test_the_wizard_imports_the_command_text_it_declares():
    assert setup_cog.CMDS.text("setup.description")
    assert setup_cog.CMDS.help("setup")
