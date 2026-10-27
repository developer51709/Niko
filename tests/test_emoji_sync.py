"""The emoji sync's live ids and full replacement.

Discord cannot replace an emoji's image, so re-uploading art means new ids for
the whole set. Two things have to follow that: ``get_emoji`` in the *running*
process, and the module constants that cached emoji strings at import time.
Otherwise every panel keeps sending ids that no longer exist, and the only fix
is a restart — which is what ``.staff replaceemojis`` exists to avoid.
"""

import asyncio
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import config.emojis as emoji_config  # noqa: E402
import utils.emoji_sync as emoji_sync  # noqa: E402
from config.emojis import apply_live_emoji_ids, get_emoji, live_emoji_ids  # noqa: E402


@pytest.fixture(autouse=True)
def restore_live_ids():
    """Every test starts and ends with no live replacements in force."""
    saved = live_emoji_ids()
    emoji_config._LIVE_IDS.clear()
    try:
        yield
    finally:
        emoji_config._LIVE_IDS.clear()
        emoji_config._LIVE_IDS.update(saved)


class FakeEmoji:
    """The parts of ``discord.Emoji`` the sync touches."""

    def __init__(self, name, emoji_id, bot=None, animated=False):
        self.name = name
        self.id = emoji_id
        self.animated = animated
        self._bot = bot

    async def delete(self):
        self._bot.events.append(("delete", self.name))
        # Discord drops the emoji from the application, so the sync's next
        # fetch must not see it — otherwise it would be treated as already
        # present and its old art would survive the replacement.
        self._bot._existing = [emoji for emoji in self._bot._existing if emoji is not self]


class FakeBot:
    """An application whose emoji routes are recorded instead of called."""

    def __init__(self, existing=(), next_id=900):
        self.events = []
        self.uploaded = {}
        self._existing = [FakeEmoji(name, emoji_id, self) for name, emoji_id in existing]
        self._next_id = next_id

    async def fetch_application_emojis(self):
        self.events.append(("fetch", None))
        return list(self._existing)

    async def create_application_emoji(self, name, image):
        self.events.append(("create", name))
        self.uploaded[name] = image
        self._next_id += 1
        return FakeEmoji(name, self._next_id, self)


class FakeSession:
    """Stands in for aiohttp; the tests' assets always exist locally."""

    def __init__(self):
        self.requests = []

    def get(self, url, **kwargs):  # pragma: no cover - only reached on a bug
        self.requests.append(url)
        raise AssertionError(f"the sync tried to download {url}")


CONFIG_TEMPLATE = '''def get_emoji(emoji_name: str):
    if emoji_name == "tick":
        return "<:tick:{tick}>"
    if emoji_name == "cross":
        return "<:cross:{cross}>"
'''


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    """A throwaway config file and asset directory the sync writes to."""
    assets = tmp_path / "emojis"
    assets.mkdir()
    (assets / "tick.png").write_bytes(b"local-tick-art")
    (assets / "cross.png").write_bytes(b"local-cross-art")
    config_file = tmp_path / "emojis.py"
    config_file.write_text(
        CONFIG_TEMPLATE.format(tick="111111111111111111", cross="222222222222222222"),
        encoding="utf-8",
    )
    monkeypatch.setattr(emoji_sync, "EMOJIS_CONFIG", config_file)
    monkeypatch.setattr(emoji_sync, "EMOJI_ASSETS", assets)
    monkeypatch.setattr(emoji_sync, "_API_PAUSE", 0)
    return config_file


# ── live ids ─────────────────────────────────────────────────────────────────


def test_get_emoji_uses_the_ids_the_sync_applied_without_reloading():
    """A module that imported ``get_emoji`` before the sync must still be right.

    ``from config.emojis import get_emoji`` is how every cog imports it, so the
    function object is captured at import and only the ids behind it can change.
    """
    old_tick = get_emoji("tick")
    assert old_tick.startswith("<:tick:") and not old_tick.endswith(":0>")

    apply_live_emoji_ids({int(old_tick.rsplit(":", 1)[1].rstrip(">")): "<:tick:999>"})

    assert get_emoji("tick") == "<:tick:999>"
    # Untouched keys are unaffected.
    assert get_emoji("cross").startswith("<:cross:")


def test_a_key_that_returns_several_emojis_is_remapped_too():
    """``enabled`` returns two emojis; both ids must follow their replacements."""
    value = get_emoji("enabled")
    ids = [int(part.rsplit(":", 1)[1].rstrip(">")) for part in value.split("><")]
    assert len(ids) == 2

    apply_live_emoji_ids({ids[0]: "<:first:1001>", ids[1]: "<:second:1002>"})

    assert get_emoji("enabled") == "<:first:1001><:second:1002>"


def test_unknown_emoji_names_stay_empty():
    assert get_emoji("no_such_emoji") is None


# ── constants cached at import ───────────────────────────────────────────────


def test_snapshots_are_rewritten_in_place():
    """A dict/list constant is updated in place, so old imports see it too.

    ``from x import TABLE`` binds the object, not the module attribute, so the
    refresh has to mutate containers rather than replace them.
    """
    module = types.ModuleType("cogs._emoji_snapshot_probe")
    module.LABEL = "<:tick:111> Enabled"
    module.TABLE = {"en": {"text": "<:tick:111> Enabled"}}
    module.ROWS = ["<:tick:111>", "plain text", ("<:cross:222>",)]
    sys.modules[module.__name__] = module
    try:
        table = module.TABLE
        rows = module.ROWS
        emoji_sync.refresh_snapshot_strings({111: "<:tick:900>", 222: "<:cross:901>"})

        assert module.LABEL == "<:tick:900> Enabled"
        # Same objects, new contents.
        assert module.TABLE is table and module.ROWS is rows
        assert table == {"en": {"text": "<:tick:900> Enabled"}}
        assert rows == ["<:tick:900>", "plain text", ("<:cross:901>",)]
    finally:
        del sys.modules[module.__name__]


def test_the_real_panels_follow_the_new_ids():
    """The help menu and the Connect Four board are snapshots in real modules.

    Both build their labels at import, so this is the case a config rewrite
    alone would leave broken until the next boot.
    """
    import cogs.fun.connect_four as connect_four
    import cogs.help.views as help_views

    old_general = get_emoji("general")
    old_blank = connect_four.BLANK
    general_id = int(old_general.rsplit(":", 1)[1].rstrip(">"))
    blank_id = int(old_blank.rsplit(":", 1)[1].rstrip(">"))
    categories = list(help_views._CATEGORY_LIST)
    try:
        remap = {general_id: "<:general:2222>", blank_id: "<:C4Empty:4444>"}
        apply_live_emoji_ids(remap)
        emoji_sync.refresh_snapshot_strings(remap)

        assert help_views._CATEGORY_LIST[0][1] == "<:general:2222>"
        assert connect_four.BLANK == "<:C4Empty:4444>"
        assert get_emoji("general") == "<:general:2222>"
        # Only the replaced ids move; the rest of the board is untouched.
        assert connect_four._CONTROLS[0].startswith("<:White1:")
    finally:
        help_views._CATEGORY_LIST[:] = categories
        connect_four.BLANK = old_blank


def test_snapshots_outside_the_project_and_plain_strings_are_left_alone():
    module = types.ModuleType("discord._emoji_snapshot_probe")
    module.LABEL = "<:tick:111>"
    sys.modules[module.__name__] = module
    try:
        emoji_sync.refresh_snapshot_strings({111: "<:tick:900>"})
        assert module.LABEL == "<:tick:111>"
    finally:
        del sys.modules[module.__name__]


# ── the replace flow ─────────────────────────────────────────────────────────


def test_replacing_deletes_every_emoji_then_uploads_the_local_art(workspace):
    bot = FakeBot(existing=[("tick", 111), ("cross", 222)])
    stats = asyncio.run(
        emoji_sync.sync_application_emojis(bot, session=FakeSession(), replace=True)
    )

    kinds = [kind for kind, _ in bot.events]
    assert kinds.count("delete") == 2
    assert kinds.count("create") == 2
    # Nothing is uploaded until the old set is gone, or the uploads would be
    # skipped as "already present" and the old art would survive.
    assert max(index for index, kind in enumerate(kinds) if kind == "delete") < min(
        index for index, kind in enumerate(kinds) if kind == "create"
    )
    # The PNGs come from the repository, not from Discord's copies of them.
    assert bot.uploaded == {"tick": b"local-tick-art", "cross": b"local-cross-art"}
    assert stats["deleted"] == 2 and stats["delete_failed"] == 0
    assert stats["uploaded"] == 2 and stats["already"] == 0 and stats["failed"] == 0


def test_replacing_rewrites_the_config_and_adopts_the_new_ids(workspace):
    bot = FakeBot(existing=[("tick", 111), ("cross", 222)])
    stats = asyncio.run(
        emoji_sync.sync_application_emojis(bot, session=FakeSession(), replace=True)
    )

    text = workspace.read_text(encoding="utf-8")
    assert "<:tick:901>" in text and "<:cross:902>" in text
    assert "<:tick:111>" not in text and "<:cross:222>" not in text
    assert stats["config_updated"] is True
    # The running process knows the new ids, so no restart is needed.
    assert live_emoji_ids() == {
        111111111111111111: "<:tick:901>",
        222222222222222222: "<:cross:902>",
    }
    assert stats["live_ids"] == 2


def test_a_plain_sync_never_deletes(workspace):
    bot = FakeBot(existing=[("tick", 111)])
    stats = asyncio.run(emoji_sync.sync_application_emojis(bot, session=FakeSession()))

    assert not [kind for kind, _ in bot.events if kind == "delete"]
    assert stats["deleted"] == 0
    # ``tick`` already exists under that name, so only ``cross`` is uploaded.
    assert list(bot.uploaded) == ["cross"]


def test_a_failed_delete_is_reported_and_the_rest_still_upload(workspace):
    """One emoji the bot cannot delete must not stop the other re-uploads.

    It also keeps working: a delete that failed leaves the emoji in place under
    its old id, so the sync sees it as already present and remaps to that id
    instead of uploading a second copy under the same name.
    """
    bot = FakeBot(existing=[("tick", 111), ("cross", 222)])

    async def refuse(self):
        bot.events.append(("delete_failed", self.name))
        raise _forbidden()

    bot._existing[0].delete = refuse.__get__(bot._existing[0])
    stats = asyncio.run(
        emoji_sync.sync_application_emojis(bot, session=FakeSession(), replace=True)
    )

    assert stats["deleted"] == 1 and stats["delete_failed"] == 1
    assert list(bot.uploaded) == ["cross"]
    assert stats["uploaded"] == 1 and stats["already"] == 1
    assert stats["live_ids"] == 2


def _forbidden():
    """A minimal stand-in for ``discord.HTTPException`` (403 on delete)."""
    import discord

    response = types.SimpleNamespace(status=403, reason="Forbidden")
    return discord.Forbidden(response, "Missing Access")


# ── the command ──────────────────────────────────────────────────────────────


def test_replaceemojis_is_owner_only():
    from cogs.staff.staff import OWNER_ONLY_COMMANDS, command_allowed_for_role

    assert "replaceemojis" in OWNER_ONLY_COMMANDS
    assert command_allowed_for_role("owner", "replaceemojis") is True
    for role in ("head_admin", "moderator", "head_support", "support"):
        assert command_allowed_for_role(role, "replaceemojis") is False, role


def test_the_force_argument_skips_the_confirmation_prompt():
    """Only a deliberate flag bypasses the prompt; anything else still asks."""
    from cogs.staff.development import skips_confirmation

    for argument in ("--force", "-f", "force", "--yes", "-y", "YES"):
        assert skips_confirmation(argument), argument
    for argument in (None, "", "confirm", "no", "forc"):
        assert not skips_confirmation(argument), argument
