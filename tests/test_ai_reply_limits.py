"""AI reply pipeline: length, reliability, memory, permissions and triggers.

Covers the audit fixes: async provider calls with timeouts, per-user cooldowns,
per-guild budgets, guild-scoped memory (favorability removed), fence-aware
chunking, word-boundary name triggers, and the AI Actions permission/hierarchy
model.
"""

import asyncio
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import aiosqlite
import pytest
from openai import APIConnectionError, APIStatusError, RateLimitError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import database  # noqa: E402
import utils.ai.actions as actions  # noqa: E402
import utils.ai.config as ai_config  # noqa: E402
import utils.ai.memory as memory  # noqa: E402
import utils.ai.openai_client as client  # noqa: E402
from events import on_message as intake  # noqa: E402
from utils.ai.error_views import build_ai_error_view, parse_ai_error  # noqa: E402
from utils.ai.reply import split_reply  # noqa: E402

DISCORD_LIMIT = 2000


class _FakeResponse:
    def __init__(self, status_code=200, headers=None):
        self.status_code = status_code
        self.headers = headers or {}
        self.request = SimpleNamespace()
        self.text = ""
        self._request_id = "req"


def completion(content, finish_reason="stop", tool_calls=None):
    return SimpleNamespace(choices=[SimpleNamespace(
        finish_reason=finish_reason,
        message=SimpleNamespace(content=content, tool_calls=tool_calls),
    )])


def tool_call(name, arguments):
    return SimpleNamespace(function=SimpleNamespace(name=name, arguments=arguments))


class StubClient:
    """Async stand-in for AsyncOpenAI's chat.completions endpoint."""

    def __init__(self, steps):
        self.steps = list(steps)
        self.requests = []
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self.create),
        )

    async def create(self, **kwargs):
        self.requests.append(kwargs)
        step = self.steps.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


def stub_client(monkeypatch, steps):
    """Replace the API client; returns the stub (its `.requests` is inspected)."""
    stub = StubClient(steps)
    monkeypatch.setattr(client, "_get_client", lambda: stub)
    monkeypatch.setattr(client, "_reset_client", lambda: None)
    monkeypatch.setattr(client, "_RETRY_BACKOFF_SECS", 0)
    monkeypatch.setattr(client, "_rl_cooldown", {})
    monkeypatch.setattr(client, "_guild_usage", {})
    # Keep the reply path away from the real database.
    async def empty_context(guild_id, user_id, *, limit=3):
        return memory.MemoryContext("", "")

    async def record(*args, **kwargs):
        return None

    monkeypatch.setattr(client.ai_memory, "get_context", empty_context)
    monkeypatch.setattr(client.ai_memory, "record_turn", record)
    return stub


def ask(monkeypatch, steps, text="explain coffee", **kwargs):
    stub = stub_client(monkeypatch, steps)
    server = SimpleNamespace(name="Test server", id=1, members=[None] * 3)
    reply = asyncio.run(client.generate_reply_openai(
        None, 7, server, text, "tester", "system prompt", guild_id=1, **kwargs
    ))
    return reply, stub.requests


# ── Splitting long answers for Discord ────────────────────────────────────────

def test_a_short_reply_is_a_single_message():
    assert split_reply("hello there") == ["hello there"]
    assert split_reply("") == []
    assert split_reply(None) == []


def test_a_reply_at_the_limit_is_untouched():
    text = "x" * 1900
    assert split_reply(text) == [text]


@pytest.mark.parametrize("text", [
    "This is a sentence. " * 200,
    "\n\n".join("Paragraph %d %s" % (index, "word " * 60) for index in range(40)),
    "a" * 4500,                                    # one unbroken run
    "### Title\n- one\n- two\n\n" + "body text here. " * 300,
])
def test_long_replies_are_split_without_losing_anything(text):
    chunks = split_reply(text)
    assert len(chunks) > 1
    assert all(0 < len(chunk) <= DISCORD_LIMIT for chunk in chunks)
    # Trimming strips whitespace at a boundary and nothing else, so every
    # character of the answer survives the split.
    assert re.sub(r"\s+", "", "".join(chunks)) == re.sub(r"\s+", "", text)


def test_chunks_break_on_sentence_boundaries_not_mid_sentence():
    chunks = split_reply("First sentence. " * 200)
    assert all(chunk.endswith(".") for chunk in chunks[:-1])
    assert chunks[-1].endswith(".")


def test_a_long_code_block_is_closed_and_reopened():
    code = "```python\n" + "\n".join(f"print({index})" for index in range(400)) + "\n```"
    chunks = split_reply(code)
    assert len(chunks) > 1
    # Every chunk is valid markdown on its own: an even number of fences.
    for chunk in chunks:
        assert chunk.count("```") % 2 == 0
    assert chunks[0].startswith("```python")
    assert all(chunk.startswith("```") for chunk in chunks[1:])


# ── Completion budget and continuation ────────────────────────────────────────

def test_the_request_uses_a_usable_completion_budget(monkeypatch):
    _, requests = ask(monkeypatch, [completion("hello")])
    sent = requests[0]
    assert "max_tokens" not in sent
    assert sent["max_completion_tokens"] >= 1024
    assert sent["extra_body"]["reasoning_effort"] == "low"
    assert sent["extra_body"]["include_reasoning"] is False


def test_the_budget_can_be_overridden_and_is_clamped(monkeypatch):
    monkeypatch.setenv("GROQ_MAX_COMPLETION_TOKENS", "4096")
    _, requests = ask(monkeypatch, [completion("hi")])
    assert requests[0]["max_completion_tokens"] == 4096

    monkeypatch.setenv("GROQ_MAX_COMPLETION_TOKENS", "1")
    _, requests = ask(monkeypatch, [completion("hi")])
    assert requests[0]["max_completion_tokens"] == 256

    monkeypatch.setenv("GROQ_MAX_COMPLETION_TOKENS", "not-a-number")
    _, requests = ask(monkeypatch, [completion("hi")])
    assert requests[0]["max_completion_tokens"] == 1024


def test_a_truncated_answer_is_continued_instead_of_cut_off(monkeypatch):
    reply, requests = ask(monkeypatch, [
        completion("The first half of the answer.", "length"),
        completion("and the second half.", "stop"),
    ])
    assert reply == "The first half of the answer. and the second half."
    assert len(requests) == 2
    follow_up = requests[1]["messages"]
    assert follow_up[-2]["role"] == "assistant"
    assert "Continue" in follow_up[-1]["content"]


def test_continuations_are_capped(monkeypatch):
    reply, requests = ask(monkeypatch, [
        completion("one ", "length"),
        completion("two ", "length"),
        completion("three", "length"),
    ])
    assert reply == "one two three"
    assert len(requests) == client._MAX_REPLY_REQUESTS


def test_an_empty_completion_answers_with_the_fallback(monkeypatch):
    reply, _ = ask(monkeypatch, [completion("", "stop")])
    assert reply in client._FALLBACK_REPLIES


def test_a_tool_call_still_returns_the_action(monkeypatch):
    reply, requests = ask(
        monkeypatch,
        [completion(None, "tool_calls", [tool_call("kick_member", '{"user": "42", "reason": "spam"}')])],
        text="kick this user",
        ai_actions_enabled=True,
    )
    assert reply == {"action": "kick_member", "user": "42", "reason": "spam"}
    assert "tools" in requests[0]


@pytest.mark.parametrize("text", ["how are you today", "that movie had a great banana gag", "urban planning"])
def test_tools_are_not_attached_for_casual_chat(monkeypatch, text):
    _, requests = ask(monkeypatch, [completion("hey")], text=text, ai_actions_enabled=True)
    assert "tools" not in requests[0]


def test_tools_are_attached_for_an_explicit_request(monkeypatch):
    _, requests = ask(monkeypatch, [completion("sure")], text="ban that troll", ai_actions_enabled=True)
    assert "tools" in requests[0]


@pytest.mark.parametrize("text", [
    "create a channel called memes",
    "create a channel",
    "can you make a new channel for art?",
    "set up a channel for gaming",
    "add a channel please",
    "new channel please",
    "please create a text channel named announcements",
    "delete the channel #spam",
    "rename this channel",
    "create a role for staff",
    "give a role to bob",
    "make him a moderator role",
])
def test_natural_phrasings_attach_the_action_tools(monkeypatch, text):
    _, requests = ask(monkeypatch, [completion("sure")], text=text, ai_actions_enabled=True)
    assert "tools" in requests[0], text


@pytest.mark.parametrize("text", [
    "what role do you play in this",
    "i like this channel",
    "my channel is lagging",
    "new here, what channel should i post in",
])
def test_talking_about_channels_does_not_attach_the_tools(monkeypatch, text):
    _, requests = ask(monkeypatch, [completion("hey")], text=text, ai_actions_enabled=True)
    assert "tools" not in requests[0], text


def test_a_create_channel_tool_call_returns_the_action(monkeypatch):
    payload = '{"name": "memes", "type": "text", "topic": "fresh memes"}'
    reply, requests = ask(
        monkeypatch,
        [completion(None, "tool_calls", [tool_call("create_channel", payload)])],
        text="create a channel called memes",
        ai_actions_enabled=True,
    )
    assert reply == {"action": "create_channel", "name": "memes", "type": "text", "topic": "fresh memes"}
    assert "tools" in requests[0]


def test_a_tool_call_is_used_even_when_the_finish_reason_is_stop(monkeypatch):
    payload = '{"name": "memes"}'
    reply, _ = ask(
        monkeypatch,
        [completion(None, "stop", [tool_call("create_channel", payload)])],
        text="create a channel called memes",
        ai_actions_enabled=True,
    )
    assert reply == {"action": "create_channel", "name": "memes"}


def test_action_mode_is_explained_only_when_the_tools_are_attached(monkeypatch):
    _, action_requests = ask(
        monkeypatch, [completion("sure")], text="create a channel called memes", ai_actions_enabled=True
    )
    system = action_requests[0]["messages"][0]["content"]
    assert "Action mode" in system

    _, chat_requests = ask(monkeypatch, [completion("hey")], text="how are you", ai_actions_enabled=True)
    assert "Action mode" not in chat_requests[0]["messages"][0]["content"]


# ── Transient failures and sentinels ──────────────────────────────────────────

def test_a_transient_error_is_retried(monkeypatch):
    reply, requests = ask(monkeypatch, [
        APIStatusError("boom", response=_FakeResponse(500), body={}),
        completion("recovered"),
    ])
    assert reply == "recovered"
    assert len(requests) == 2


def test_a_connection_error_is_retried_then_gives_up(monkeypatch):
    errors = [APIConnectionError(request=SimpleNamespace()) for _ in range(client._REQUEST_ATTEMPTS)]
    reply, requests = ask(monkeypatch, errors)
    assert reply == "ai_error:generic"
    assert len(requests) == client._REQUEST_ATTEMPTS


def test_a_rejected_request_is_not_retried(monkeypatch):
    reply, requests = ask(monkeypatch, [
        APIStatusError("bad request", response=_FakeResponse(400), body={"error": {"message": "bad"}}),
    ])
    assert reply == "ai_error:generic"
    assert len(requests) == 1


def test_a_rate_limit_sets_a_cooldown_instead_of_retrying(monkeypatch):
    stub = stub_client(monkeypatch, [
        RateLimitError("slow down", response=_FakeResponse(429, {"retry-after": "7"}), body={}),
    ])
    server = SimpleNamespace(name="S", id=1, members=[])
    first = asyncio.run(client.generate_reply_openai(
        None, 7, server, "hi", "tester", "system", guild_id=1
    ))
    assert first.startswith("ai_error:rate_limit:")
    second = asyncio.run(client.generate_reply_openai(
        None, 7, server, "hi", "tester", "system", guild_id=1
    ))
    assert second.startswith("ai_error:rate_limit:")
    # The second call never reached the API.
    assert len(stub.requests) == 1


def test_a_content_filter_response_reports_safety(monkeypatch):
    reply, _ = ask(monkeypatch, [completion(None, "content_filter")])
    assert reply == "ai_error:safety"


def test_a_missing_key_reports_not_configured(monkeypatch):
    monkeypatch.setattr(client, "client", None)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    server = SimpleNamespace(name="Test server", id=1, members=[])
    reply = asyncio.run(client.generate_reply_openai(
        None, 7, server, "hi", "tester", "system", guild_id=1
    ))
    assert reply == "ai_error:not_configured"


def test_the_guild_budget_stops_requests(monkeypatch):
    monkeypatch.setenv("AI_GUILD_HOURLY_REQUESTS", "1")
    stub = stub_client(monkeypatch, [completion("one")])
    server = SimpleNamespace(name="S", id=1, members=[])
    first = asyncio.run(client.generate_reply_openai(
        None, 7, server, "hi", "tester", "system", guild_id=1
    ))
    second = asyncio.run(client.generate_reply_openai(
        None, 7, server, "hi", "tester", "system", guild_id=1
    ))
    assert first == "one"
    assert second == "ai_error:budget"
    assert len(stub.requests) == 1


# ── Memory: guild-scoped, capped, no favorability ────────────────────────────

def test_build_turn_appends_and_caps_at_a_line_boundary():
    memory_text = "\n".join(f"old line {index}" for index in range(200))
    turns = [{"role": "tester", "content": "earlier"}]
    new_memory, new_turns = memory.build_turn(
        memory_text, turns, "hello", "hi there",
        user_label="tester", assistant_label="Niko",
    )
    assert len(new_memory) <= memory.MAX_MEMORY_CHARS
    assert not new_memory.startswith("d line")       # cut on a boundary, not mid-line
    assert new_memory.endswith("Niko: hi there")
    assert [turn["content"] for turn in new_turns] == ["earlier", "hello", "hi there"]
    assert len(new_turns) <= memory.MAX_HISTORY_TURNS


def test_memory_has_no_favorability_anywhere():
    assert not hasattr(memory, "get_favorability")
    assert not hasattr(memory, "adjust_favorability")
    source = (ROOT / "src/utils/ai/memory.py").read_text(encoding="utf-8").split('"""', 2)[-1]
    assert "favorability" not in source


async def _pool(tmp_path):
    connection = await aiosqlite.connect(tmp_path / "ai.db")
    return database.SQLitePool(connection)


def test_memory_is_scoped_per_guild_and_can_be_cleared(tmp_path, monkeypatch):
    async def run():
        pool = await _pool(tmp_path)
        monkeypatch.setattr(database, "_shared_pool", pool)
        monkeypatch.setattr(memory, "_table_pool", None)

        await memory.record_turn(1, 42, "hello one", "hi one", user_label="tester", assistant_label="Niko")
        await memory.record_turn(2, 42, "hello two", "hi two", user_label="tester", assistant_label="Niko")

        one = await memory.get_context(1, 42)
        two = await memory.get_context(2, 42)
        assert "hello one" in one.memory and "hello two" not in one.memory
        assert "hello two" in two.memory and "hello one" not in two.memory
        assert "tester: hello one" in one.history

        assert await memory.has_memory(1, 42)
        await memory.clear_user(1, 42)
        assert not await memory.has_memory(1, 42)
        assert await memory.has_memory(2, 42)
        await pool._db.close()

    asyncio.run(run())


def test_the_prompt_uses_this_guild_memory(monkeypatch):
    stub = stub_client(monkeypatch, [completion("ok")])
    seen = {}

    async def context(guild_id, user_id, *, limit=3):
        seen["guild_id"] = guild_id
        return memory.MemoryContext("likes tea", "tester: earlier\nNiko: hm")

    async def record(*args, **kwargs):
        seen["recorded"] = (args, kwargs)

    monkeypatch.setattr(client.ai_memory, "get_context", context)
    monkeypatch.setattr(client.ai_memory, "record_turn", record)
    server = SimpleNamespace(name="S", id=9, members=[])
    asyncio.run(client.generate_reply_openai(
        None, 7, server, "hi", "tester", "system", guild_id=9, ai_name="Nova"
    ))
    sent = stub.requests[0]["messages"][1]["content"]
    assert "likes tea" in sent
    assert seen["guild_id"] == 9
    args, kwargs = seen["recorded"]
    assert args[0] == 9 and args[1] == 7
    assert kwargs["assistant_label"] == "Nova"


# ── Config: cached, async, validated ─────────────────────────────────────────

def test_config_roundtrip_and_validation(tmp_path, monkeypatch):
    async def run():
        pool = await _pool(tmp_path)
        monkeypatch.setattr(database, "_shared_pool", pool)
        monkeypatch.setattr(ai_config, "_table_pool", None)
        ai_config._cache.clear()
        ai_config._cache_at.clear()

        default = await ai_config.load_config(1)
        assert default["ai_name"] == "Niko" and default["enabled"] == "True"

        saved = await ai_config.save_config(1, "ai_name", "Nova")
        assert saved["ai_name"] == "Nova"
        assert (await ai_config.load_config(1))["ai_name"] == "Nova"
        assert (await ai_config.load_config(1, fresh=True))["ai_name"] == "Nova"

        assert (await ai_config.load_config(2))["ai_name"] == "Niko"

        for bad in ("", "a", "ab"):
            with pytest.raises(ValueError):
                await ai_config.save_config(1, "ai_name", bad)
        with pytest.raises(ValueError):
            await ai_config.save_config(1, "personality", "chaotic")
        with pytest.raises(ValueError):
            await ai_config.save_config(1, "not_a_key", "x")
        await pool._db.close()

    asyncio.run(run())


def test_config_is_cached_until_invalidated(tmp_path, monkeypatch):
    async def run():
        pool = await _pool(tmp_path)
        monkeypatch.setattr(database, "_shared_pool", pool)
        monkeypatch.setattr(ai_config, "_table_pool", None)
        ai_config._cache.clear()
        ai_config._cache_at.clear()
        await ai_config.load_config(5)

        calls = {"count": 0}
        real_fetchrow = pool.fetchrow

        async def counting_fetchrow(*args, **kwargs):
            calls["count"] += 1
            return await real_fetchrow(*args, **kwargs)

        monkeypatch.setattr(pool, "fetchrow", counting_fetchrow)
        await ai_config.load_config(5)
        await ai_config.load_config(5)
        assert calls["count"] == 0          # served from cache
        await ai_config.load_config(5, fresh=True)
        assert calls["count"] == 1
        await pool._db.close()

    asyncio.run(run())


# ── Trigger rules ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("content,expected", [
    ("hey niko what's up", True),
    ("NIKO, look at this", True),
    ("I love my Nikon camera", False),
    ("that harmoniko sounds nice", False),
    ("banana niko", True),
])
def test_name_matching_is_whole_word(content, expected):
    assert intake.mentions_ai_name(content, "Niko") is expected


def test_short_ai_names_never_trigger_by_name():
    for name in ("a", "ni", " "):
        assert intake.mentions_ai_name("a niko ai message", name) is False


def test_replying_to_niko_triggers_without_a_ping():
    bot = SimpleNamespace(user=SimpleNamespace(id=99))
    reply_to_bot = SimpleNamespace(reference=SimpleNamespace(
        resolved=SimpleNamespace(author=SimpleNamespace(id=99)), cached_message=None,
    ))
    reply_to_user = SimpleNamespace(reference=SimpleNamespace(
        resolved=SimpleNamespace(author=SimpleNamespace(id=7)), cached_message=None,
    ))
    assert intake.replies_to_bot(bot, reply_to_bot) is True
    assert intake.replies_to_bot(bot, reply_to_user) is False
    assert intake.replies_to_bot(bot, SimpleNamespace(reference=None)) is False


# ── AI Actions: permissions and hierarchy ────────────────────────────────────

class _FakeRole:
    def __init__(self, position, name="role"):
        self.position = position
        self.name = name
        self.managed = False

    def is_default(self):
        return False

    def __ge__(self, other):
        return self.position >= getattr(other, "position", 0)

    def __gt__(self, other):
        return self.position > getattr(other, "position", 0)


def _member(member_id, top_role_position, guild=None, administrator=False, **overwrites):
    perms = SimpleNamespace(administrator=administrator, **overwrites)
    return SimpleNamespace(
        id=member_id,
        top_role=_FakeRole(top_role_position),
        guild_permissions=perms,
        guild=guild,
        mention=f"<@{member_id}>",
    )


def test_channel_overwrites_are_respected_for_channel_actions():
    member = _member(7, 5, manage_messages=True)
    channel = SimpleNamespace(
        mention="#staff",
        permissions_for=lambda _member: SimpleNamespace(manage_messages=False, administrator=False),
    )
    assert actions._has_perm(member, "manage_messages") is True
    assert actions._has_perm(member, "manage_messages", channel=channel) is False


def test_a_lower_moderator_cannot_target_a_higher_member():
    guild = SimpleNamespace(
        id=1,
        owner_id=1,
        me=SimpleNamespace(id=99, top_role=_FakeRole(100), mention="<@99>"),
    )
    author = _member(7, 5, guild=guild)
    target = _member(8, 8, guild=guild)
    msg = SimpleNamespace(guild=guild, author=author)

    assert actions._member_hierarchy_error(msg, target, action_label="kick") is not None
    assert actions._member_hierarchy_error(msg, _member(9, 2, guild=guild), action_label="kick") is None


def test_the_server_owner_bypasses_the_invoker_check():
    guild = SimpleNamespace(
        id=1,
        owner_id=7,
        me=SimpleNamespace(id=99, top_role=_FakeRole(100), mention="<@99>"),
    )
    author = _member(7, 1, guild=guild)
    msg = SimpleNamespace(guild=guild, author=author)
    assert actions._member_hierarchy_error(msg, _member(8, 50, guild=guild), action_label="ban") is None


def test_a_moderator_cannot_manage_a_role_above_their_own():
    guild = SimpleNamespace(
        id=1,
        owner_id=1,
        me=SimpleNamespace(id=99, top_role=_FakeRole(100)),
    )
    author = _member(7, 5, guild=guild)
    msg = SimpleNamespace(guild=guild, author=author)

    above = _FakeRole(20, name="Admin")
    below = _FakeRole(2, name="Member")

    assert actions._role_hierarchy_error(msg, above, action_label="assign") is not None
    assert actions._role_hierarchy_error(msg, below, action_label="assign") is None


def test_purge_checks_the_target_channel_permissions():
    guild = SimpleNamespace(
        id=1,
        owner_id=1,
        me=SimpleNamespace(id=99, top_role=_FakeRole(100), mention="<@99>"),
    )
    author = _member(7, 5, guild=guild, manage_messages=True)
    msg = SimpleNamespace(guild=guild, author=author)
    blocked = SimpleNamespace(
        mention="#private",
        permissions_for=lambda _member: SimpleNamespace(manage_messages=False, administrator=False),
    )
    allowed = SimpleNamespace(
        mention="#public",
        permissions_for=lambda _member: SimpleNamespace(manage_messages=True, administrator=False),
    )
    assert actions._check_perms(msg, "manage_messages", action_label="purge", channel=blocked) is not None
    assert actions._check_perms(msg, "manage_messages", action_label="purge", channel=allowed) is None


# ── Error cards ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("kind", ["rate_limit", "safety", "generic", "not_configured", "budget"])
def test_every_sentinel_builds_a_card(kind):
    import discord

    assert isinstance(build_ai_error_view(kind, 30), discord.ui.LayoutView)
    assert parse_ai_error(f"ai_error:{kind}")[0] == kind


def test_unknown_error_kinds_fall_back_to_generic():
    assert parse_ai_error("ai_error:nonsense")[0] == "generic"
    assert parse_ai_error("not-a-sentinel") == ("generic", 0)
    assert parse_ai_error("ai_error:rate_limit:12") == ("rate_limit", 12)


# ── Owner-only debugging tools ───────────────────────────────────────────────

def test_the_debug_tools_are_owner_only():
    from utils.ai import debugging

    class _Bot:
        def __init__(self, owner):
            self.owner = owner

        async def is_owner(self, user):
            return self.owner

    sent = {}

    class _Response:
        async def send_message(self, content, ephemeral=False):
            sent["content"] = content

    interaction = SimpleNamespace(response=_Response(), user=SimpleNamespace(id=7))
    assert asyncio.run(debugging._is_bot_owner(_Bot(True), interaction)) is True
    assert asyncio.run(debugging._is_bot_owner(_Bot(False), interaction)) is False
    assert "owner" in sent["content"].lower()


def test_nested_traceback_files_are_detected():
    from utils.ai import debugging

    traceback_text = (
        '  File "/app/src/utils/ai/openai_client.py", line 10, in generate\n'
        '  File "/app/src/cogs/ai/chat.py", line 4, in memory\n'
    )
    assert debugging._infer_file_from_tb(traceback_text) == "cogs/ai/chat"
