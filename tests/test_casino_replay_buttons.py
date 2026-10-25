"""Persistent Play Again / Spin Again buttons for slots and roulette.

The old buttons were created inline, had no custom id, and only worked while the
originating view object was still alive in the process. Both games now use
``DynamicItem`` buttons whose custom id carries the player (and, for slots, the
wager) so a click on an old message replays the round after a restart.
"""

import asyncio
import sys
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.casino import roulette as roulette_module  # noqa: E402
from cogs.casino import slots as slots_module  # noqa: E402
from cogs.casino.replay import InteractionContext  # noqa: E402


class _Response:
    def __init__(self):
        self.deferred = False
        self.message = None

    async def defer(self):
        self.deferred = True

    async def send_message(self, content=None, **kwargs):
        self.message = {"content": content, **kwargs}


class _Followup:
    def __init__(self):
        self.sent = []

    async def send(self, *args, **kwargs):
        self.sent.append((args, kwargs))


class _Cog:
    def __init__(self):
        self.calls = []

    async def play(self, ctx, amount=None):
        self.calls.append((ctx, amount))


class _Client:
    def __init__(self, cogs):
        self._cogs = cogs

    def get_cog(self, name):
        return self._cogs.get(name)


class _Bot:
    def __init__(self):
        self.views = []

    def add_view(self, view, message_id=None):
        assert message_id is None
        self.views.append(view)


class _Economy:
    """Just enough of EconomyCog for the cooldown guard."""

    def __init__(self, **data):
        self.data = {"last_slots": 0, "last_roulette": 0, **data}

    async def get_user_economy_data(self, user_id):
        return self.data


def _interaction(user_id=42, cogs=None):
    return SimpleNamespace(
        user=SimpleNamespace(id=user_id),
        client=_Client(cogs or {}),
        response=_Response(),
        followup=_Followup(),
        guild=None,
        channel=None,
        message=None,
    )


# ── ids survive a restart ────────────────────────────────────────────────


def test_slots_button_keeps_the_player_and_the_wager_in_its_custom_id():
    button = slots_module.PlayAgainButton(42, 250)
    assert button.custom_id == "casino:slots:again:42:250"
    match = button.template.fullmatch(button.custom_id)
    assert match is not None
    rebuilt = asyncio.run(slots_module.PlayAgainButton.from_custom_id(None, None, match))
    assert (rebuilt.user_id, rebuilt.amount) == (42, 250)


def test_roulette_button_keeps_the_player_in_its_custom_id():
    button = roulette_module.SpinAgainButton(42)
    assert button.custom_id == "casino:roulette:again:42"
    match = button.template.fullmatch(button.custom_id)
    assert match is not None
    rebuilt = asyncio.run(roulette_module.SpinAgainButton.from_custom_id(None, None, match))
    assert rebuilt.user_id == 42


# ── replay behaviour ─────────────────────────────────────────────────────


def test_slots_replay_runs_the_same_spin_for_the_owner():
    cog = _Cog()
    interaction = _interaction(cogs={"Slots": cog, "EconomyCog": _Economy()})
    asyncio.run(slots_module.PlayAgainButton(42, 250).callback(interaction))
    assert interaction.response.deferred is True
    (ctx, amount), = cog.calls
    assert amount == 250
    assert isinstance(ctx, InteractionContext)
    assert ctx.author.id == 42


def test_roulette_replay_starts_a_new_round_for_the_owner():
    cog = _Cog()
    interaction = _interaction(cogs={"Roulette": cog, "EconomyCog": _Economy()})
    asyncio.run(roulette_module.SpinAgainButton(42).callback(interaction))
    assert interaction.response.deferred is True
    (ctx, _), = cog.calls
    assert isinstance(ctx, InteractionContext)
    assert ctx.author.id == 42


def test_someone_else_clicking_the_button_gets_only_a_notice():
    cog = _Cog()
    cogs = {"Slots": cog, "Roulette": cog, "EconomyCog": _Economy()}
    interaction = _interaction(user_id=99, cogs=cogs)
    asyncio.run(slots_module.PlayAgainButton(42, 250).callback(interaction))
    assert interaction.response.deferred is False
    assert cog.calls == []
    assert interaction.response.message["ephemeral"] is True

    interaction = _interaction(user_id=99, cogs=cogs)
    asyncio.run(roulette_module.SpinAgainButton(42).callback(interaction))
    assert interaction.response.deferred is False
    assert cog.calls == []


# ── cooldown spam guard ─────────────────────────────────────────────────


def test_slots_replay_on_cooldown_replies_privately():
    cog = _Cog()
    economy = _Economy(last_slots=time.time())
    interaction = _interaction(cogs={"Slots": cog, "EconomyCog": economy})

    asyncio.run(slots_module.PlayAgainButton(42, 250).callback(interaction))

    assert interaction.response.deferred is False
    assert interaction.response.message["ephemeral"] is True
    assert cog.calls == []
    assert not interaction.followup.sent
    assert "<t:" in repr(interaction.response.message["view"].to_components())


def test_roulette_replay_on_cooldown_replies_privately():
    cog = _Cog()
    economy = _Economy(last_roulette=time.time())
    interaction = _interaction(cogs={"Roulette": cog, "EconomyCog": economy})

    asyncio.run(roulette_module.SpinAgainButton(42).callback(interaction))

    assert interaction.response.deferred is False
    assert interaction.response.message["ephemeral"] is True
    assert cog.calls == []
    assert not interaction.followup.sent
    assert "<t:" in repr(interaction.response.message["view"].to_components())


# ── registration ─────────────────────────────────────────────────────────


def test_both_cogs_register_one_persistent_replay_view():
    for cog in (slots_module.Slots(_Bot()), roulette_module.Roulette(_Bot())):
        bot = cog.bot
        asyncio.run(cog.cog_load())
        assert len(bot.views) == 1
        view = bot.views[0]
        assert view.timeout is None
        assert view.is_persistent()
        assert [item.custom_id for item in view.walk_children() if hasattr(item, "custom_id")]


def test_the_roulette_result_view_carries_the_persistent_button():
    ctx = SimpleNamespace(author=SimpleNamespace(id=42))
    result = roulette_module.build_result_view(ctx, True, 7, "🔴 Red", "red", 100, 100)
    assert result.timeout is None
    assert "casino:roulette:again:42" in repr(result.to_components())
