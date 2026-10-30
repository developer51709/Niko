"""Anti-spam must not police Niko's own log output.

The reported bug: anti-spam actioned the logging webhook. A burst of moderation
posted a burst of log entries through that one webhook, the sender crossed the
spam threshold, anti-spam deleted the entries and logged its own enforcement —
which was one more entry from the same webhook, which counted too. The bot
spammed its own logs until somebody changed the threshold.

So posted output (a webhook or bot author) never counts, and a channel the
server routes logs to is never policed, whichever account posts there.
"""

import asyncio
import functools
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

GUILD_ID = 5511
LOG_CHANNEL_ID = 900
BOT_ID = 7


def async_test(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return asyncio.run(fn(*args, **kwargs))
    return wrapper


class _Author:
    def __init__(self, user_id=5, bot=False):
        self.id = user_id
        self.bot = bot
        self.mention = f"<@{user_id}>"
        self.name = "member"
        self.display_name = "Member"


class _Channel:
    def __init__(self, channel_id=555):
        self.id = channel_id
        self.mention = "#general"


class _Message:
    def __init__(self, author, channel=None, content="hello", webhook_id=None):
        self.author = author
        self.channel = channel if channel is not None else _Channel()
        self.content = content
        self.webhook_id = webhook_id
        self.guild = _Guild()
        self.deleted = False

    async def delete(self):
        self.deleted = True


class _Guild:
    id = GUILD_ID
    name = "Test Guild"

    def get_member(self, user_id):
        return SimpleNamespace(id=user_id, mention=f"<@{user_id}>")


class _UtilsStub:
    def __init__(self):
        self.logged = []
        self.muted = []

    def is_whitelisted(self, guild_id, member):
        return False

    def get_badwords_action(self, guild_id):
        return "delete"

    def contains_blocked_word(self, guild_id, content):
        return False

    async def log_action(self, guild, title, description, display_title=None):
        self.logged.append((display_title or title, description))

    async def mute_member(self, guild, member, duration=60, reason=""):
        self.muted.append((member, reason))


class _LoggerStub:
    """The ServerLogger cog's log routing, as auto-moderation sees it."""

    def __init__(self, channel_ids=()):
        self.channel_ids = set(channel_ids)

    def configured_channel_ids(self, guild_id):
        return self.channel_ids


def make_automod(log_channels=(), threshold=6):
    from cogs.automod.cog import AutoMod

    logger = _LoggerStub(log_channels)
    cog = AutoMod.__new__(AutoMod)
    cog.bot = SimpleNamespace(
        user=SimpleNamespace(id=BOT_ID),
        get_cog=lambda name: logger if name == "ServerLogger" else None,
    )
    utils = _UtilsStub()
    cog.utils = lambda: utils
    cog.get_cfg = lambda guild_id: {
        "automod": {
            "antispam": True,
            "antilink": False,
            "badwords": False,
            "massmention": False,
        },
        "antiraid_ext": {},
        "spam_threshold": threshold,
        "spam_interval": 7,
    }
    cog._msg_history = {}
    cog._censor_webhook_ids = set()
    return cog, utils


def _spam(cog, author, channel=None, webhook_id=None, times=7):
    async def run():
        sent = []
        for _ in range(times):
            message = _Message(author, channel, webhook_id=webhook_id)
            sent.append(message)
            await cog.on_message(message)
        return sent

    return asyncio.run(run())


def test_log_webhook_entries_do_not_count_as_spam():
    """The exact round trip: seven log entries from one logging webhook."""
    cog, utils = make_automod()
    sent = _spam(cog, _Author(user_id=1000, bot=True), webhook_id=999)

    assert [message.deleted for message in sent] == [False] * len(sent)
    assert utils.logged == []
    assert utils.muted == []
    assert cog._msg_history == {}


def test_bot_output_without_a_webhook_is_not_counted():
    """The webhook-less fallback posts as a bot account, which is still output."""
    cog, utils = make_automod()
    sent = _spam(cog, _Author(user_id=1001, bot=True))

    assert not any(message.deleted for message in sent)
    assert utils.logged == []


def test_a_log_channel_is_never_policed():
    """Even a non-bot message in the log channel is not spam enforcement's job."""
    cog, utils = make_automod(log_channels=[LOG_CHANNEL_ID])
    sent = _spam(cog, _Author(), channel=_Channel(LOG_CHANNEL_ID))

    assert not any(message.deleted for message in sent)
    assert utils.logged == []
    assert cog._msg_history == {}


def test_a_member_still_trips_anti_spam():
    """The guard must not disarm anti-spam for the members it exists for."""
    cog, utils = make_automod()
    sent = _spam(cog, _Author())

    assert [message.deleted for message in sent] == [False] * 5 + [True] * 2
    assert [title for title, _ in utils.logged] == ["Anti-Spam", "Anti-Spam"]
    assert [reason for _, reason in utils.muted] == ["Auto-mute: spam"] * 2


def test_a_member_in_normal_channels_is_counted_before_the_threshold():
    cog, utils = make_automod()
    sent = _spam(cog, _Author(), times=5)

    assert not any(message.deleted for message in sent)
    assert utils.logged == []
    assert cog._msg_history == {GUILD_ID: {5: cog._msg_history[GUILD_ID][5]}}
    assert len(cog._msg_history[GUILD_ID][5]) == 5
