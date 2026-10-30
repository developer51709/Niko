"""A finished giveaway setup panel must not come back as the timeout notice.

``.giveaway start`` posts a Components v2 panel with a 10 minute view timeout.
Launching or cancelling replaces that panel with a card that has no components
left, so the timer firing afterwards would only overwrite the card the host is
looking at — the launched giveaway card in the setup channel — with "setup
timed out". Abandoning the panel still gets the timeout notice.
"""

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogs.giveaway import views as giveaway_views  # noqa: E402
from cogs.giveaway.views import _SetupState  # noqa: E402

HOST = 7
CHANNEL_ID = 500


def timer_disarmed(view) -> bool:
    """True when the view's timeout task is gone, so discord.py won't call on_timeout."""
    task = view._BaseView__timeout_task
    return task is None or task.done() or task.cancelled()


def view_text(view) -> str:
    parts = []

    def walk(item):
        content = getattr(item, "content", None)
        if isinstance(content, str):
            parts.append(content)
        for child in getattr(item, "children", None) or []:
            walk(child)

    walk(view)
    return "\n".join(parts)


class FakeResponse:
    def __init__(self):
        self.edited = []
        self.messages = []

    async def edit_message(self, *, view=None, **kwargs):
        self.edited.append(view)

    async def send_message(self, content=None, *, ephemeral=False, **kwargs):
        self.messages.append(content)


class FakeMessage:
    def __init__(self):
        self.id = 4242
        self.edits = []

    async def edit(self, *, view=None, **kwargs):
        self.edits.append(view)


class FakeChannel:
    def __init__(self):
        self.id = CHANNEL_ID
        self.mention = f"<#{CHANNEL_ID}>"
        self.sent = []
        self.sent_views = []

    async def send(self, *, view=None, **kwargs):
        message = FakeMessage()
        self.sent.append(message)
        self.sent_views.append(view)
        return message

    def permissions_for(self, _member):
        return SimpleNamespace(send_messages=True)


class FakeConnection:
    def __init__(self):
        self.rows = []

    async def execute(self, *args):
        self.rows.append(args)


class FakeBot:
    def __init__(self):
        self.cxn = FakeConnection()
        self.registered = []

    def add_view(self, view, message_id=None):
        self.registered.append((view, message_id))


def make_world():
    channel = FakeChannel()
    guild = SimpleNamespace(
        id=1,
        preferred_locale="en-US",
        me=SimpleNamespace(id=99),
        get_channel=lambda channel_id: channel,
    )
    bot = FakeBot()
    state = _SetupState(channel_id=CHANNEL_ID)
    state.prize = "Nitro"
    state.duration_s = 3600
    state.winners = 1
    interaction = SimpleNamespace(
        guild=guild,
        user=SimpleNamespace(id=HOST),
        response=FakeResponse(),
    )
    view = giveaway_views._build_setup_view(bot, interaction, state, HOST)
    view.message = FakeMessage()
    return SimpleNamespace(
        bot=bot, guild=guild, channel=channel, state=state,
        interaction=interaction, view=view, panel=view.message,
    )


# Each test gets its own panel: the view is stateful and the fakes record edits.
@pytest.fixture
def world():
    return make_world()


def test_launching_a_giveaway_retires_the_panel(world):
    view = world.view
    panel = world.panel

    asyncio.run(view.launch(world.interaction))

    # The giveaway itself went out and the panel turned into the done card.
    assert len(world.channel.sent) == 1
    done = world.interaction.response.edited[-1]
    assert "Nitro" in view_text(done)

    # Nothing is listening on the panel any more, so the timer cannot fire.
    assert timer_disarmed(view)
    assert view.message is None
    assert panel.edits == []

    # Even a direct call leaves the done card alone.
    asyncio.run(view.on_timeout())
    assert panel.edits == []


def test_cancelling_the_panel_retires_it(world):
    view = world.view
    panel = world.panel
    cancel = giveaway_views._SetupBtn(
        "Cancel", giveaway_views.discord.ButtonStyle.danger, None, view, "cancel"
    )

    asyncio.run(cancel.callback(world.interaction))

    cancelled = world.interaction.response.edited[-1]
    assert "cancelled" in view_text(cancelled).lower()
    assert timer_disarmed(view)
    assert view.message is None

    asyncio.run(view.on_timeout())
    assert panel.edits == []


def test_an_abandoned_panel_still_explains_the_timeout(world):
    view = world.view
    panel = world.panel

    asyncio.run(view.on_timeout())

    assert len(panel.edits) == 1
    text = view_text(panel.edits[0])
    assert "timed out" in text.lower()
    assert "{" not in text
