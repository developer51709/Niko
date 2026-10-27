"""Blocked-word filtering for AutoMod.

The reported bug: the blocked word filter "did not work properly". Matching was a
raw substring test, so blocking "ass" deleted "class", "grass" and "assistant",
while spacing or punctuation ("a.s.s") walked straight through. An entry stored
with surrounding whitespace never matched anything, a blank entry matched *every*
message, a non-list value (``null`` from a hand-edited store) raised inside the
listener, and edited messages were never re-checked at all.
"""

import asyncio
import functools
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import discord
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.moderation.utils import (  # noqa: E402
    MAX_BADWORDS_MASK_LENGTH,
    MAX_BLOCKED_WORD_LENGTH,
    ModerationUtils,
    PRESET_KEYS,
    build_blocked_word_regex,
    normalize_badwords_action,
    normalize_badwords_mask,
    normalize_blocked_word,
    normalize_message_content,
    normalize_presets,
    preset_catalog,
)
from cogs.moderation._presets import (  # noqa: E402
    PRESET_FILTERS,
    build_preset_regex,
    preset_description,
    preset_label,
)

GUILD_ID = 4242


def async_test(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return asyncio.run(fn(*args, **kwargs))
    return wrapper


class _ClosedLoop:
    """A stand-in for the bot loop, so config saves never touch a database."""

    def is_closed(self) -> bool:
        return True

    def create_task(self, coroutine):  # pragma: no cover - never reached
        coroutine.close()


def make_utils(blocked_words=None, action=None, mask=None, presets=None) -> ModerationUtils:
    """A ModerationUtils whose stored config is already available."""
    stored = {"blocked_words": list(blocked_words or [])}
    if presets is not None:
        stored["badwords_presets"] = list(presets)
    if action is not None:
        stored["badwords_action"] = action
    if mask is not None:
        stored["badwords_mask"] = mask
    cog = ModerationUtils.__new__(ModerationUtils)
    cog.bot = SimpleNamespace(loop=_ClosedLoop())
    cog.config = {str(GUILD_ID): stored}
    cog._stale_entries = set()
    cog._blocked_patterns = {}
    return cog


def matches(words, text) -> bool:
    pattern = build_blocked_word_regex(words)
    return bool(pattern and pattern.search(normalize_message_content(text)))


# ── Entry normalisation ───────────────────────────────────────────────────────


def test_entries_are_stripped_lowercased_and_folded():
    assert normalize_blocked_word("  Ass  ") == "ass"
    assert normalize_blocked_word("Hello   World") == "hello world"
    assert normalize_blocked_word("ＦＵＣＫ") == "fuck"  # fullwidth form


@pytest.mark.parametrize("entry", ["", "   ", None, 42, ["ass"], "x" * (MAX_BLOCKED_WORD_LENGTH + 1)])
def test_unusable_entries_are_rejected(entry):
    # The blank entry is the dangerous one: "" matches every message.
    assert normalize_blocked_word(entry) is None


# ── Matching semantics (Discord's keyword rules) ──────────────────────────────


@pytest.mark.parametrize(
    "words, text, expected",
    [
        # whole words only, so innocent messages survive
        (["ass"], "Class starts at five", False),
        (["ass"], "grass is green", False),
        (["ass"], "assistant mode", False),
        (["ass"], "update the assets", False),
        (["ass"], "You are an ass", True),
        (["ass"], "ASS", True),
        # a filtered word spaced or punctuated out is still caught
        (["ass"], "a.s.s", True),
        (["ass"], "a s s", True),
        (["ass"], "as\u200bs", True),  # zero-width space inside the word
        (["fuck"], "that is fucking awful", False),
        # a trailing * opts into longer forms, like Discord
        (["fuck*"], "that is fucking awful", True),
        (["ass*"], "assistant mode", True),
        (["ass*"], "class starts", False),
        # a leading * drops the word-start requirement
        (["*ass"], "glass", True),
        (["*ass*"], "harassed the class", True),
        # multi-word entries match as a phrase
        (["bad word"], "what a bad word!", True),
        (["bad word"], "that word is bad", False),
        # nothing configured, or nothing usable, never matches
        ([], "anything at all", False),
        (["", "   ", "*"], "anything at all", False),
    ],
)
def test_matching(words, text, expected):
    assert matches(words, text) is expected


def test_an_empty_word_list_produces_no_pattern():
    assert build_blocked_word_regex([]) is None
    assert build_blocked_word_regex(["", None, 7]) is None
    assert build_blocked_word_regex(None) is None


# ── Cog-level API ─────────────────────────────────────────────────────────────


def test_adding_a_word_strips_it_and_blocks_it():
    cog = make_utils()
    cog.add_blocked_word(GUILD_ID, "  Ass  ")
    assert cog.get_blocked_words(GUILD_ID) == ["ass"]
    assert cog.contains_blocked_word(GUILD_ID, "you are an ass")
    assert not cog.contains_blocked_word(GUILD_ID, "class starts soon")


def test_blank_and_duplicate_words_are_never_stored():
    cog = make_utils()
    for word in ["", "   ", "ass", "ASS", " ass "]:
        cog.add_blocked_word(GUILD_ID, word)
    assert cog.get_blocked_words(GUILD_ID) == ["ass"]
    # an empty entry would otherwise match every message in the server
    assert not cog.contains_blocked_word(GUILD_ID, "a perfectly fine message")


def test_oversized_words_are_rejected():
    cog = make_utils()
    cog.add_blocked_word(GUILD_ID, "x" * (MAX_BLOCKED_WORD_LENGTH + 1))
    assert cog.get_blocked_words(GUILD_ID) == []


def test_a_legacy_padded_entry_starts_working():
    # Words saved by the old code kept their whitespace, so they never matched.
    cog = make_utils(["  ass  ", "kicked"])
    assert cog.get_blocked_words(GUILD_ID) == ["ass", "kicked"]
    assert cog.contains_blocked_word(GUILD_ID, "you ass")
    assert not cog.contains_blocked_word(GUILD_ID, "you threw the ball")


def test_removing_a_word_ignores_case_and_padding():
    cog = make_utils(["  ass  "])
    cog.remove_blocked_word(GUILD_ID, "ASS")
    assert cog.get_blocked_words(GUILD_ID) == []
    assert not cog.contains_blocked_word(GUILD_ID, "you ass")


@pytest.mark.parametrize("junk", [None, "ass", 5, {"ass": True}])
def test_a_malformed_stored_list_cannot_break_the_listener(junk):
    cog = make_utils()
    cog.config[str(GUILD_ID)]["blocked_words"] = junk
    assert cog.get_blocked_words(GUILD_ID) == []
    assert cog.contains_blocked_word(GUILD_ID, "hello there") is False


def test_a_stored_list_of_blanks_matches_nothing():
    cog = make_utils(["", "   "])
    assert cog.get_blocked_words(GUILD_ID) == []
    assert cog.contains_blocked_word(GUILD_ID, "any ordinary sentence") is False


def test_content_that_is_not_text_is_ignored():
    cog = make_utils(["ass"])
    assert cog.contains_blocked_word(GUILD_ID, None) is False
    assert cog.contains_blocked_word(GUILD_ID, "") is False


def test_the_compiled_pattern_is_cached_per_word_list():
    cog = make_utils(["ass"])
    assert cog.blocked_word_pattern(GUILD_ID) is cog.blocked_word_pattern(GUILD_ID)
    cog.add_blocked_word(GUILD_ID, "kicked")
    pattern = cog.blocked_word_pattern(GUILD_ID)
    assert pattern is not None and pattern.search("you kicked it")


# ── Edited messages ───────────────────────────────────────────────────────────


class _Author:
    def __init__(self, bot=False):
        self.bot = bot
        self.mention = "@member"
        self.id = 5
        self.name = "member"
        self.display_name = "Member"
        self.display_avatar = SimpleNamespace(url="https://cdn.example/avatar.png")


class _Channel:
    mention = "#general"


class _Message:
    def __init__(self, content, author, channel=None):
        self.content = content
        self.author = author
        self.guild = SimpleNamespace(id=GUILD_ID)
        self.channel = channel if channel is not None else _Channel()
        self.deleted = False

    async def delete(self):
        self.deleted = True


class _UtilsStub:
    def __init__(self, blocked_word):
        self.blocked_word = blocked_word
        self.logged = []

    def is_whitelisted(self, guild_id, member):
        return False

    def get_badwords_action(self, guild_id):
        return "delete"

    def contains_blocked_word(self, guild_id, content):
        return self.blocked_word in content

    async def log_action(self, guild, title, description):
        self.logged.append((title, description))


def make_automod(blocked_word):
    from cogs.automod.cog import AutoMod

    cog = AutoMod.__new__(AutoMod)
    utils = _UtilsStub(blocked_word)
    cog.utils = lambda: utils
    cog.get_cfg = lambda guild_id: {"automod": {"badwords": True}}
    return cog, utils


@async_test
async def test_editing_a_blocked_word_in_is_caught():
    cog, utils = make_automod("ass")
    author = _Author()
    after = _Message("all good you ass", author)
    await cog.on_message_edit(_Message("all good", author), after)
    assert after.deleted is True
    assert [title for title, _ in utils.logged] == ["Bad Word Filter"]


@async_test
async def test_harmless_edits_do_nothing():
    cog, utils = make_automod("ass")
    author = _Author()
    for before_text, after_text in [("all good", "still good"), ("same", "same")]:
        after = _Message(after_text, author)
        await cog.on_message_edit(_Message(before_text, author), after)
        assert after.deleted is False
    assert utils.logged == []


@async_test
async def test_a_bot_edit_is_ignored():
    cog, _ = make_automod("ass")
    author = _Author(bot=True)
    after = _Message("all good you ass", author)
    await cog.on_message_edit(_Message("all good", author), after)
    assert after.deleted is False


# ── Censoring instead of deleting ─────────────────────────────────────────────


def test_the_mask_defaults_to_one_star_per_character():
    assert normalize_badwords_mask(None) == "*"
    assert normalize_badwords_mask("  *  ") == "*"
    assert normalize_badwords_mask("[removed]") == "[removed]"
    assert normalize_badwords_mask("") == ""  # clears the word instead of masking it
    assert len(normalize_badwords_mask("x" * 40)) == MAX_BADWORDS_MASK_LENGTH


def test_the_response_defaults_to_deleting_and_rejects_junk():
    assert normalize_badwords_action(None) == "delete"
    assert normalize_badwords_action(" CENSOR ") == "censor"
    assert normalize_badwords_action("log") == "delete"
    assert make_utils().get_badwords_action(GUILD_ID) == "delete"
    assert make_utils(action="censor").get_badwords_action(GUILD_ID) == "censor"


@pytest.mark.parametrize("words, text, expected", [
    (["ass"], "you are an ass", "you are an ***"),
    (["ass"], "class starts soon", "class starts soon"),
    (["ass"], "a.s.s", "*****"),
    (["fuck*"], "that is fucking awful", "that is ******* awful"),
    (["ass", "kicked"], "ass and kicked", "*** and ******"),
])
def test_censoring_masks_every_detected_word(words, text, expected):
    assert make_utils(words).censor_blocked_words(GUILD_ID, text) == expected


def test_censoring_keeps_up_with_detection():
    """Anything the filter flags must actually be masked in the repost."""
    cog = make_utils(["ass*", "bad word"])
    for text in ["you ass", "a.s.s", "assistant", "a bad word here", "harmless"]:
        censored = cog.censor_blocked_words(GUILD_ID, text)
        assert (censored != text) == cog.contains_blocked_word(GUILD_ID, text)


def test_the_censor_mask_is_configurable():
    assert make_utils(["ass"], mask="").censor_blocked_words(GUILD_ID, "you ass!") == "you !"
    assert make_utils(["ass"], mask="[removed]").censor_blocked_words(GUILD_ID, "you ass") == "you [removed]"
    # An explicit mask argument wins over the stored one.
    assert make_utils(["ass"]).censor_blocked_words(GUILD_ID, "you ass", mask="?") == "you ???"


def test_censoring_content_without_blocked_words_is_unchanged():
    cog = make_utils(["ass"])
    assert cog.censor_blocked_words(GUILD_ID, "all clear here") == "all clear here"
    assert cog.censor_blocked_words(GUILD_ID, None) == ""
    assert make_utils([]).censor_blocked_words(GUILD_ID, "ass") == "ass"


class _Webhook:
    def __init__(self, name="Niko Censor"):
        self.name = name
        self.user = SimpleNamespace(id=7)
        self.sent = []

    async def send(self, **payload):
        self.sent.append(payload)


_WEBHOOK_STATE: dict = {}


class _WebhookChannel(discord.TextChannel):
    """A TextChannel with its webhook API replaced (the real one is a slot descriptor)."""

    async def webhooks(self):
        return _WEBHOOK_STATE[self.id]["existing"]

    async def create_webhook(self, *, name, reason=None):
        state = _WEBHOOK_STATE[self.id]
        state["created"] += 1
        if state["raise"]:
            raise discord.Forbidden(SimpleNamespace(status=403, reason="Forbidden"), "Missing Permissions")
        webhook = _Webhook(name)
        state["existing"].append(webhook)
        return webhook


def make_channel(existing=False, create_raises=False, channel_id=555):
    _WEBHOOK_STATE[channel_id] = {
        "existing": [_Webhook()] if existing else [],
        "created": 0,
        "raise": create_raises,
    }
    channel = object.__new__(_WebhookChannel)
    channel.id = channel_id
    channel.name = "general"
    return channel


class _CensorUtils:
    """Delegates to a real ModerationUtils so the masking matches production."""

    def __init__(self, store):
        self.store = store
        self.logged = []

    def is_whitelisted(self, guild_id, member):
        return False

    def get_badwords_action(self, guild_id):
        return self.store.get_badwords_action(guild_id)

    def censor_blocked_words(self, guild_id, content):
        return self.store.censor_blocked_words(guild_id, content)

    def contains_blocked_word(self, guild_id, content):
        return self.store.contains_blocked_word(guild_id, content)

    async def log_action(self, guild, title, description):
        self.logged.append((title, description))


def make_censor_automod(blocked_words, action="censor", mask="*"):
    from cogs.automod.cog import AutoMod

    cog = AutoMod.__new__(AutoMod)
    cog.bot = SimpleNamespace(user=SimpleNamespace(id=7))
    cog._censor_webhooks = {}
    return cog, _CensorUtils(make_utils(blocked_words, action=action, mask=mask))


@async_test
async def test_the_censor_response_reposts_as_the_author():
    cog, utils = make_censor_automod(["ass"])
    channel = make_channel()
    message = _Message("you are an ass", _Author(), channel)

    await cog._handle_blocked_message(message, utils, message.content)

    assert message.deleted is True
    assert _WEBHOOK_STATE[channel.id]["created"] == 1
    (hook,) = _WEBHOOK_STATE[channel.id]["existing"]
    (payload,) = hook.sent
    assert payload["content"] == "you are an ***"
    assert payload["username"] == "Member"
    assert payload["avatar_url"] == "https://cdn.example/avatar.png"
    assert payload["allowed_mentions"].everyone is False and payload["allowed_mentions"].users is False
    assert "censored" in utils.logged[0][1].lower()


@async_test
async def test_an_existing_censor_webhook_is_reused_and_cached():
    cog, utils = make_censor_automod(["ass"])
    channel = make_channel(existing=True)
    for text in ("ass one", "ass two"):
        message = _Message(text, _Author(), channel)
        await cog._handle_blocked_message(message, utils, message.content)

    assert _WEBHOOK_STATE[channel.id]["created"] == 0
    assert len(cog._censor_webhooks) == 1
    assert len(_WEBHOOK_STATE[channel.id]["existing"][0].sent) == 2


@async_test
async def test_censoring_falls_back_to_deleting_without_manage_webhooks():
    cog, utils = make_censor_automod(["ass"])
    channel = make_channel(create_raises=True)
    message = _Message("ass", _Author(), channel)

    await cog._handle_blocked_message(message, utils, message.content)

    assert message.deleted is True
    assert _WEBHOOK_STATE[channel.id]["existing"] == []
    assert utils.logged[0][0] == "Bad Word Filter"


@async_test
async def test_delete_mode_never_creates_a_webhook():
    cog, utils = make_censor_automod(["ass"], action="delete")
    channel = make_channel()
    message = _Message("ass", _Author(), channel)

    await cog._handle_blocked_message(message, utils, message.content)

    assert message.deleted is True
    assert _WEBHOOK_STATE[channel.id]["created"] == 0
    assert cog._censor_webhooks == {}


@async_test
async def test_threads_are_deleted_rather_than_censored():
    cog, utils = make_censor_automod(["ass"])
    thread = object.__new__(discord.Thread)
    thread.id = 556
    thread.name = "a thread"
    message = _Message("ass", _Author(), thread)

    await cog._handle_blocked_message(message, utils, message.content)

    assert message.deleted is True
    assert cog._censor_webhooks == {}


def test_the_automod_panel_shows_the_configured_response_in_every_language():
    from cogs.automod.views import _build_filter_text

    labels = {
        "en": ("Response:", "Delete message", "Censor & repost"),
        "de": ("Reaktion:", "Nachricht löschen", "Zensieren & erneut senden"),
        "es": ("Respuesta:", "Eliminar mensaje", "Censurar y reenviar"),
    }
    for lang, (label, deleting, censoring) in labels.items():
        deleting_text = _build_filter_text({"automod": {"badwords": True}, "badwords_action": "delete"}, lang)
        censoring_text = _build_filter_text({"automod": {"badwords": True}, "badwords_action": "censor"}, lang)
        assert f"{label} `{deleting}`" in deleting_text, lang
        assert f"{label} `{censoring}`" in censoring_text, lang
        # A junk value must never break the panel.
        assert _build_filter_text({"automod": {}, "badwords_action": "shred"}, lang)


# ── Dashboard validation ──────────────────────────────────────────────────────


class _FakeModerationCog:
    def __init__(self):
        self.config = {}
        self.saved = []

    def get_guild_config(self, guild_id):
        return self.config.setdefault(str(guild_id), {"automod": {}})

    def save_config(self, guild_id=None):
        self.saved.append(guild_id)


def save_automod(body, cog):
    """Call the AutoMod save route directly, bypassing auth and CSRF decorators."""
    from webapp import app, dashboard_routes

    original_bot = dashboard_routes._discord_bot
    original_reader = dashboard_routes.get_runtime_moderation_config
    dashboard_routes._discord_bot = SimpleNamespace(get_cog=lambda name: cog)
    dashboard_routes.get_runtime_moderation_config = lambda guild_id: cog.get_guild_config(guild_id)
    try:
        with app.test_request_context(json=body):
            save = dashboard_routes.api_save_automod
            return save.__wrapped__.__wrapped__.__wrapped__(str(GUILD_ID))
    finally:
        dashboard_routes._discord_bot = original_bot
        dashboard_routes.get_runtime_moderation_config = original_reader


def test_the_dashboard_saves_normalized_words():
    cog = _FakeModerationCog()
    response = save_automod({"automod": {"badwords": True}, "blocked_words": ["  Ass ", "KICKED", "ass", ""]}, cog)
    assert response.get_json()["ok"] is True
    assert cog.config[str(GUILD_ID)]["blocked_words"] == ["ass", "kicked"]
    assert cog.saved == [GUILD_ID]


def test_the_dashboard_accepts_a_comma_separated_string():
    cog = _FakeModerationCog()
    save_automod({"blocked_words": "ass, kicked"}, cog)
    assert cog.config[str(GUILD_ID)]["blocked_words"] == ["ass", "kicked"]


def test_the_dashboard_rejects_an_oversized_word():
    cog = _FakeModerationCog()
    response = save_automod({"blocked_words": ["x" * (MAX_BLOCKED_WORD_LENGTH + 1)]}, cog)
    assert response[1] == 400
    assert "60 characters" in response[0].get_json()["error"]
    assert cog.saved == []


def test_the_dashboard_rejects_a_non_list():
    cog = _FakeModerationCog()
    response = save_automod({"blocked_words": {"ass": True}}, cog)
    assert response[1] == 400
    assert cog.saved == []


def test_the_dashboard_saves_the_censor_response_and_mask():
    cog = _FakeModerationCog()
    save_automod({"badwords_action": "censor", "badwords_mask": "#"}, cog)
    assert cog.config[str(GUILD_ID)]["badwords_action"] == "censor"
    assert cog.config[str(GUILD_ID)]["badwords_mask"] == "#"


def test_the_dashboard_rejects_an_unknown_response():
    cog = _FakeModerationCog()
    response = save_automod({"badwords_action": "shred"}, cog)
    assert response[1] == 400
    assert "delete" in response[0].get_json()["error"]
    assert cog.saved == []


def test_the_dashboard_rejects_an_overlong_censor_mask():
    cog = _FakeModerationCog()
    response = save_automod({"badwords_mask": "x" * (MAX_BADWORDS_MASK_LENGTH + 1)}, cog)
    assert response[1] == 400
    assert cog.saved == []


# ── Preset filters: the spellings a word list cannot catch ────────────────────

# Every one of these is a known way to walk a plain keyword filter: leet
# substitutions, separators, repeated letters, a self-censored letter, a dropped
# doubled letter, fullwidth forms, zero-width characters, and unicode look-alikes
# (the Cyrillic і in "nіgger").
BYPASS_SPELLINGS = [
    "n1gg3r", "niger", "n1ger", "n i g g e r", "n.i.g.g.e.r", "n-i-g-g-e-r",
    "n_i_g_g_e_r", "niiiigger", "NIGGER", "ＮＩＧＧＥＲ", "n\u200biger",
    "nіgger", "nigger!", "niggers", "n*gga", "f4gg0t", "f.a.g.g.o.t",
    "sh1t", "s h i t", "sh*t", "sh#t", "fuuuck", "b!tch", "b1tch", "b*tch",
    "c_u_n_t", "@sshole", "4sshole", "d1ckhead", "w4nker", "wh0re", "sl*t",
    "p1ssed", "ret4rd", "tr4nny", "k1ke", "g00k", "ch1nk", "p4ki", "c00n",
    "w3tback", "spic", "p0rn", "h3ntai", "d1ldo", "bl0wjob", "0rgasm",
    "p3nis", "v4gina", "b00bs", "t1ts", "n1pples", "h0rny", "s3xting",
    "r4pe", "m0lest", "p3dophile", "1ncest", "kys", "k.y.s", "kill yourself",
    "k1ll yourself", "kill your self", "neck yourself", "drink bleach",
    "end yourself", "retarded", "spastic", "spazzy", "midget", "redskins",
]

# Ordinary English that a naive pattern (or the old substring test) happily
# destroys — plus words that share a stem with a filtered term.
ORDINARY_TEXT = [
    "Class starts at five", "grass is green", "assistant mode", "update the assets",
    "analysis of the data", "raccoon in the garden", "a cocktail please",
    "Scunthorpe", "Nigerian food is great", "therapist appointment", "grape juice",
    "drape the cloth", "scrape the pan", "spices and herbs", "spiced cider",
    "spicy noodles", "spicing things up", "chinking the logs", "sniggering at jokes",
    "kidney beans", "Pakistan", "skipper the boat", "swanky hotel", "prickly pear",
    "prickle", "thesis writing", "my only fans of cheese", "lollipop", "potato",
    "compass", "assess", "associate", "brass", "grasshopper", "Montgomery",
    "Nigel", "digger", "bigger", "figure", "trigger", "giggle", "country roads",
    "keep your seat", "book your seat", "keys on the table", "sky is blue",
    "kayaks are fun", "tit for tat", "title of the page", "tissue paper",
    "analytical thinking", "canal cruise", "banal remark", "retardant spray",
    "pedometer readings", "semantics of the word", "classic rock", "glassware",
    "risky business", "lyrics to the song", "butterfly", "spigot", "cunning plan",
]


@pytest.mark.parametrize("text", BYPASS_SPELLINGS)
def test_a_preset_catches_spellings_a_word_list_cannot(text):
    everyone = make_utils(presets=PRESET_KEYS)
    assert everyone.contains_blocked_word(GUILD_ID, text) is True, text
    # The same message is clean while no preset is switched on, so the preset is
    # what did the work rather than a stray word entry.
    assert make_utils().contains_blocked_word(GUILD_ID, text) is False, text


@pytest.mark.parametrize("text", ORDINARY_TEXT)
def test_preset_filters_leave_ordinary_messages_alone(text):
    assert make_utils(presets=PRESET_KEYS).contains_blocked_word(GUILD_ID, text) is False, text
    # …even when combined with a custom list that a substring test would trip on.
    assert make_utils(["ass", "kicked"], presets=PRESET_KEYS).contains_blocked_word(GUILD_ID, text) is False, text


def test_preset_filters_are_whole_word_and_use_case_insensitive_spelling():
    cog = make_utils(presets=["profanity"])
    assert cog.contains_blocked_word(GUILD_ID, "what the FUCK")
    assert cog.contains_blocked_word(GUILD_ID, "F.u.c.k")
    assert not cog.contains_blocked_word(GUILD_ID, "classic rock night")
    assert not cog.contains_blocked_word(GUILD_ID, "a prickly situation")


def test_the_three_known_trade_offs_are_deliberate():
    """Aggressive preset matching has three documented costs.

    Pinned here so a change to them is a deliberate decision rather than an
    accident: a dropped doubled letter makes the country name "Niger" trip the
    slur preset, and the exact-word entries still match the bare word in "spick
    and span" and "a chink in the armour".
    """
    assert make_utils(presets=["slurs"]).contains_blocked_word(GUILD_ID, "Niger")
    assert make_utils(presets=["slurs"]).contains_blocked_word(GUILD_ID, "spick and span")
    assert make_utils(presets=["slurs"]).contains_blocked_word(GUILD_ID, "a chink in the armour")


def test_presets_are_off_until_a_server_switches_them_on():
    cog = make_utils()
    assert cog.get_badwords_presets(GUILD_ID) == []
    assert not cog.contains_blocked_word(GUILD_ID, "you n1gger")
    assert cog.set_badwords_preset(GUILD_ID, "slurs") is True
    assert cog.get_badwords_presets(GUILD_ID) == ["slurs"]
    assert cog.contains_blocked_word(GUILD_ID, "you n1gger")


def test_preset_state_is_normalized_and_ordered_by_the_catalog():
    cog = make_utils()
    assert cog.set_badwords_presets(GUILD_ID, ["threats", "slurs", "slurs"]) == ["slurs", "threats"]
    assert cog.get_badwords_presets(GUILD_ID) == ["slurs", "threats"]
    assert cog.set_badwords_presets(GUILD_ID, ["SLURS", "not-a-filter", 7]) == ["slurs"]


def test_setting_and_toggling_report_whether_anything_changed():
    cog = make_utils(presets=["slurs"])
    assert cog.set_badwords_preset(GUILD_ID, "slurs") is False  # already on
    assert cog.set_badwords_preset(GUILD_ID, "nonsense") is False
    assert cog.toggle_badwords_preset(GUILD_ID, "slurs") is False
    assert cog.get_badwords_presets(GUILD_ID) == []
    assert cog.toggle_badwords_preset(GUILD_ID, "sexual") is True
    assert cog.toggle_badwords_preset(GUILD_ID, "nonsense") is None
    assert cog.get_badwords_presets(GUILD_ID) == ["sexual"]


@pytest.mark.parametrize("junk", [None, "slurs", 5, {"slurs": True}, [None], [""] ])
def test_a_malformed_preset_value_cannot_break_the_filter(junk):
    cog = make_utils()
    cog.config[str(GUILD_ID)]["badwords_presets"] = junk
    enabled = cog.get_badwords_presets(GUILD_ID)
    assert enabled in ([], ["slurs"])
    assert cog.contains_blocked_word(GUILD_ID, "a perfectly ordinary sentence") is False


def test_normalize_presets_accepts_a_single_string_and_drops_junk():
    assert normalize_presets("slurs") == ["slurs"]
    assert normalize_presets(["sexual", "slurs", "sexual"]) == ["slurs", "sexual"]
    assert normalize_presets(None) == []
    assert normalize_presets(["nope", 12]) == []


def test_the_pattern_is_compiled_once_per_preset_set():
    assert build_preset_regex(["slurs", "profanity"]) is build_preset_regex(["slurs", "profanity"])
    assert build_preset_regex([]) is None
    assert build_preset_regex(["not-a-preset"]) is None


def test_the_catalog_describes_every_filter_in_three_languages():
    assert PRESET_KEYS == ("slurs", "profanity", "sexual", "threats")
    catalog = preset_catalog()
    assert [entry["key"] for entry in catalog] == list(PRESET_KEYS)
    for entry, preset in zip(catalog, PRESET_FILTERS):
        assert entry["label"] == preset.labels["en"]
        assert entry["description"]
        assert entry["terms"] == len(preset.terms) > 0
        for lang in ("en", "de", "es"):
            assert preset_label(preset, lang) and preset_description(preset, lang)
    # An unknown language falls back to English rather than raising.
    assert preset_label(PRESET_FILTERS[0], "fr") == PRESET_FILTERS[0].labels["en"]
    assert preset_description(PRESET_FILTERS[0], "fr") == PRESET_FILTERS[0].descriptions["en"]
    assert preset_catalog("de")[0]["label"] == PRESET_FILTERS[0].labels["de"]


# ── Censoring a preset match ──────────────────────────────────────────────────


@pytest.mark.parametrize("text, expected", [
    ("you n1gg3r", "you ******"),  # six characters, six stars
    ("n i g g e r", "***********"),
    ("sh1t", "****"),
    ("kill yourself", "*************"),
    ("class starts soon", "class starts soon"),
])
def test_censoring_masks_preset_matches_too(text, expected):
    cog = make_utils(presets=PRESET_KEYS)
    assert cog.censor_blocked_words(GUILD_ID, text) == expected


def test_censoring_covers_presets_and_the_word_list_together():
    cog = make_utils(["ass"], presets=["slurs"], mask="[removed]")
    assert cog.censor_blocked_words(GUILD_ID, "you ass and n1gger") == "you [removed] and [removed]"
    # Presets alone never mask ordinary text.
    assert cog.censor_blocked_words(GUILD_ID, "class starts soon") == "class starts soon"


def test_detection_and_censoring_agree_for_presets():
    cog = make_utils(["ass*"], presets=PRESET_KEYS)
    for text in ["you ass", "you n1gg3r", "kill yourself", "a plain sentence", "class of 2024"]:
        censored = cog.censor_blocked_words(GUILD_ID, text)
        assert (censored != text) == cog.contains_blocked_word(GUILD_ID, text), text


def test_presets_do_not_leak_into_a_guild_without_them():
    with_preset = make_utils(presets=["slurs"])
    without = make_utils()
    without.config[str(GUILD_ID)]["badwords_presets"] = []
    assert with_preset.contains_blocked_word(GUILD_ID, "n1gg3r")
    assert not without.contains_blocked_word(GUILD_ID, "n1gg3r")


# ── Dashboard: preset filters ─────────────────────────────────────────────────


def test_the_dashboard_saves_and_clears_preset_filters():
    cog = _FakeModerationCog()
    save_automod({"badwords_presets": ["sexual", "slurs"]}, cog)
    assert cog.config[str(GUILD_ID)]["badwords_presets"] == ["slurs", "sexual"]
    save_automod({"badwords_presets": []}, cog)
    assert cog.config[str(GUILD_ID)]["badwords_presets"] == []


def test_the_dashboard_accepts_a_comma_separated_preset_list():
    cog = _FakeModerationCog()
    save_automod({"badwords_presets": "profanity, slurs"}, cog)
    assert cog.config[str(GUILD_ID)]["badwords_presets"] == ["slurs", "profanity"]


def test_the_dashboard_rejects_an_unknown_or_malformed_preset():
    cog = _FakeModerationCog()
    response = save_automod({"badwords_presets": ["slurs", "everything"]}, cog)
    assert response[1] == 400
    assert "everything" in response[0].get_json()["error"]
    assert save_automod({"badwords_presets": {"slurs": True}}, cog)[1] == 400
    assert cog.saved == []


def test_the_dashboard_receives_the_catalog_without_storing_it():
    cog = _FakeModerationCog()
    saved = save_automod({"badwords_presets": ["slurs"]}, cog).get_json()["config"]
    assert [entry["key"] for entry in saved["preset_filters"]] == list(PRESET_KEYS)
    assert saved["badwords_presets"] == ["slurs"]
    # Reference data must never be written into the guild's config.
    assert "preset_filters" not in cog.config[str(GUILD_ID)]


def test_the_config_payload_carries_the_preset_catalog():
    from unittest.mock import patch

    from webapp import app, dashboard_routes

    class _Cog:
        def get_guild_config(self, guild_id):
            return {"automod": {}, "badwords_presets": ["slurs"]}

    with patch.object(dashboard_routes, "_discord_bot", SimpleNamespace(get_cog=lambda name: _Cog())), \
            patch.object(dashboard_routes, "get_runtime_moderation_config", lambda guild_id: _Cog().get_guild_config(guild_id)), \
            patch.object(dashboard_routes, "_get_runtime_server_config", lambda guild_id: {}), \
            patch.object(dashboard_routes, "_guild_premium_view", lambda guild_id: {"active": False}), \
            patch.object(dashboard_routes, "get_ai_config", lambda guild_id: {}), \
            patch.object(dashboard_routes, "get_runtime_level_config", lambda guild_id: {}):
        with app.test_request_context():
            payload = dashboard_routes.api_guild_config.__wrapped__.__wrapped__(str(GUILD_ID)).get_json()
    moderation = payload["moderation"]
    assert moderation["badwords_presets"] == ["slurs"]
    assert [entry["key"] for entry in moderation["preset_filters"]] == list(PRESET_KEYS)
    assert moderation["preset_filters"][0]["label"] and moderation["preset_filters"][0]["description"]


# ── The /badwords panel ───────────────────────────────────────────────────────


def _panel(utils, section, locale=None):
    from cogs.moderation._badwords_panel import build_panel

    guild = SimpleNamespace(id=GUILD_ID, preferred_locale=locale) if locale else SimpleNamespace(id=GUILD_ID, preferred_locale=None)
    return build_panel(utils, GUILD_ID, section, guild)


def _panel_text(view):
    return view.to_components()[0]["components"][0]["content"]


def _panel_rows(view):
    return [row["components"] for row in view.to_components()[0]["components"] if row["type"] == 1]


@pytest.mark.parametrize("section", ["overview", "words", "presets", "response"])
def test_the_panel_renders_every_section_as_a_container(section):
    view = _panel(make_utils(["ass"], presets=["slurs"], action="censor"), section)
    components = view.to_components()[0]["components"]
    assert components[0]["type"] == 10  # text display
    assert components[1]["type"] == 14  # separator
    assert len(components) + 1 <= 40
    assert len(_panel_rows(view)) >= 1  # the section menu
    assert _panel_text(view).startswith("### ")


def test_the_panel_shows_the_state_of_every_setting():
    utils = make_utils(["ass", "kicked"], presets=["slurs"], action="censor", mask="#")
    overview = _panel_text(_panel(utils, "overview"))
    assert "2" in overview and "1/4" in overview
    assert "censor" in overview.lower() or "zensieren" in overview  # the response line
    words = _panel_text(_panel(utils, "words"))
    assert "`ass`" in words and "`kicked`" in words
    presets = _panel_text(_panel(utils, "presets"))
    assert "Slurs & hate speech" in presets
    response = _panel_text(_panel(utils, "response"))
    assert "`#`" in response


def test_the_panel_word_list_is_capped():
    utils = make_utils([f"word{index}" for index in range(120)])
    text = _panel_text(_panel(utils, "words"))
    assert len(re.findall(r"`word\d+`", text)) == 40
    assert "80" in text  # …and 80 more


def test_the_panel_speaks_the_guild_language_and_falls_back_to_english():
    utils = make_utils(presets=["slurs"])
    german = _panel_text(_panel(utils, "overview", discord.Locale.german))
    spanish = _panel_text(_panel(utils, "overview", discord.Locale.spain_spanish))
    english = _panel_text(_panel(utils, "overview", discord.Locale.french))
    assert "Gesperrte Wörter" in german
    assert "Palabras bloqueadas" in spanish
    assert "Blocked Words" in english
    assert len({german, spanish, english}) == 3


def test_every_panel_string_exists_in_every_language():
    from cogs.moderation._badwords_panel import MESSAGES, SECTIONS

    assert set(SECTIONS) == {"overview", "words", "presets", "response"}
    for key in MESSAGES["en"]:
        for lang in ("de", "es"):
            assert MESSAGES[lang].get(key), f"{key} is missing from {lang}"


class _FakeResponse:
    def __init__(self):
        self.sent = []
        self.edited = []
        self.modals = []

    async def send_message(self, *args, **kwargs):
        self.sent.append((args, kwargs))

    async def edit_message(self, *args, **kwargs):
        self.edited.append((args, kwargs))

    async def send_modal(self, modal):
        self.modals.append(modal)


class _FakeFollowup:
    def __init__(self):
        self.sent = []

    async def send(self, *args, **kwargs):
        self.sent.append((args, kwargs))


class _FakeMessage:
    def __init__(self):
        self.edits = []

    async def edit(self, *args, **kwargs):
        self.edits.append((args, kwargs))


class _FakeInteraction:
    def __init__(self, manage_guild=True, message=None, locale=None):
        self.response = _FakeResponse()
        self.followup = _FakeFollowup()
        self.user = SimpleNamespace(guild_permissions=SimpleNamespace(manage_guild=manage_guild))
        self.guild = SimpleNamespace(id=GUILD_ID, preferred_locale=locale)
        self.message = message


def _choose(select, values):
    """Inject a selection the way discord.py does when a menu is used."""
    from discord.ui.select import selected_values

    selected_values.set({select.custom_id: list(values)})
    return select


def _buttons(view):
    return [component for row in _panel_rows(view) for component in row if component.get("type") == 2 or "label" in component.get("data", {})]


@async_test
async def test_the_preset_menu_switches_filters_on_and_off():
    from cogs.moderation._badwords_panel import PresetSelect

    utils = make_utils(presets=["slurs"])
    select = _choose(PresetSelect(utils, GUILD_ID, "en"), ["profanity", "threats"])
    interaction = _FakeInteraction()
    await select.callback(interaction)
    assert utils.get_badwords_presets(GUILD_ID) == ["profanity", "threats"]
    assert interaction.response.edited, "the panel must be refreshed in place"
    assert "Profanity" in _panel_text(interaction.response.edited[0][1]["view"]) or interaction.response.edited[0][1]["view"]
    assert interaction.followup.sent  # a confirmation


@async_test
async def test_the_preset_menu_can_clear_every_filter():
    from cogs.moderation._badwords_panel import PresetSelect

    utils = make_utils(presets=["slurs", "sexual"])
    select = _choose(PresetSelect(utils, GUILD_ID, "en"), [])
    await select.callback(_FakeInteraction())
    assert utils.get_badwords_presets(GUILD_ID) == []


@async_test
async def test_the_response_menu_sets_delete_or_censor():
    from cogs.moderation._badwords_panel import ResponseSelect

    utils = make_utils(action="delete")
    select = _choose(ResponseSelect(utils, GUILD_ID, "en"), ["censor"])
    interaction = _FakeInteraction()
    await select.callback(interaction)
    assert utils.get_badwords_action(GUILD_ID) == "censor"
    assert interaction.response.edited


@async_test
async def test_adding_a_word_through_the_modal_validates_and_stores():
    from cogs.moderation._badwords_panel import AddWordModal

    utils = make_utils(["ass"])
    modal = AddWordModal(utils, GUILD_ID)

    modal.word._value = "  KICKED  "
    interaction = _FakeInteraction()
    await modal.on_submit(interaction)
    assert utils.get_blocked_words(GUILD_ID) == ["ass", "kicked"]
    assert interaction.response.edited

    modal.word._value = "ASS"
    duplicate = _FakeInteraction()
    await modal.on_submit(duplicate)
    assert utils.get_blocked_words(GUILD_ID) == ["ass", "kicked"]
    assert duplicate.response.sent and duplicate.response.edited == []

    modal.word._value = "x" * (MAX_BLOCKED_WORD_LENGTH + 1)
    oversized = _FakeInteraction()
    await modal.on_submit(oversized)
    assert utils.get_blocked_words(GUILD_ID) == ["ass", "kicked"]
    assert oversized.response.sent


@async_test
async def test_removing_a_word_refreshes_the_panel():
    from cogs.moderation._badwords_panel import RemoveWordButton, RemoveWordSelect

    utils = make_utils(["ass", "kicked"])
    message = _FakeMessage()
    interaction = _FakeInteraction(message=message)
    await RemoveWordButton(utils, GUILD_ID).callback(interaction)
    assert interaction.response.sent

    select = _choose(RemoveWordSelect(utils, GUILD_ID, utils.get_blocked_words(GUILD_ID), message), ["ass"])
    await select.callback(_FakeInteraction())
    assert utils.get_blocked_words(GUILD_ID) == ["kicked"]
    assert message.edits and message.edits[0][1]["view"]


@async_test
async def test_clearing_the_word_list_asks_for_confirmation_first():
    from cogs.moderation._badwords_panel import ClearWordsButton, ConfirmClearButton

    utils = make_utils(["ass", "kicked"])
    message = _FakeMessage()
    prompt = _FakeInteraction(message=message)
    await ClearWordsButton(utils, GUILD_ID).callback(prompt)
    assert prompt.response.sent
    assert utils.get_blocked_words(GUILD_ID) == ["ass", "kicked"], "nothing is dropped before the confirm"

    await ConfirmClearButton(utils, GUILD_ID, 2, message).callback(_FakeInteraction())
    assert utils.get_blocked_words(GUILD_ID) == []
    assert message.edits


@async_test
async def test_the_panel_refuses_a_member_without_manage_server():
    from cogs.moderation._badwords_panel import AddWordButton, ClearWordsButton, PresetSelect, ResponseSelect, SectionSelect

    utils = make_utils(["ass"], presets=["slurs"])
    for component in (
        SectionSelect(utils, GUILD_ID, "overview", "en"),
        _choose(PresetSelect(utils, GUILD_ID, "en"), ["sexual"]),
        _choose(ResponseSelect(utils, GUILD_ID, "en"), ["censor"]),
        AddWordButton(utils, GUILD_ID),
        ClearWordsButton(utils, GUILD_ID),
    ):
        interaction = _FakeInteraction(manage_guild=False)
        await component.callback(interaction)
        assert interaction.response.sent, type(component).__name__
        assert interaction.response.edited == [] and interaction.response.modals == []
    assert utils.get_badwords_presets(GUILD_ID) == ["slurs"]
    assert utils.get_badwords_action(GUILD_ID) == "delete"
    assert utils.get_blocked_words(GUILD_ID) == ["ass"]


@async_test
async def test_the_mask_modal_edits_and_clears_the_mask():
    from cogs.moderation._badwords_panel import MaskModal

    utils = make_utils(["ass"])
    modal = MaskModal(utils, GUILD_ID, "en")
    modal.mask._value = "#"
    await modal.on_submit(_FakeInteraction())
    assert utils.get_badwords_mask(GUILD_ID) == "#"

    modal.mask._value = ""
    await modal.on_submit(_FakeInteraction())
    assert utils.get_badwords_mask(GUILD_ID) == ""
    assert utils.censor_blocked_words(GUILD_ID, "you ass!") == "you !"
