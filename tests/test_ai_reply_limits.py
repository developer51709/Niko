"""AI reply length and reliability.

The reported bug: replies were "cut off" and not reliable. The client capped each
completion at ``max_tokens=300``, but gpt-oss is a reasoning model whose
reasoning tokens are billed against that same budget — measured against the live
API, a long answer came back with ``finish_reason="length"`` after ~870
characters. The message handler then hard-truncated anything over 1800
characters with an ellipsis. On top of that, transient API failures were never
retried, an empty completion produced an empty reply, and a corrupt
``memory.json`` raised at import time and took every reply down with it.
"""

import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from openai import APIConnectionError, APIStatusError, RateLimitError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import utils.ai.memory as memory  # noqa: E402
import utils.ai.openai_client as client  # noqa: E402
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


def stub_client(monkeypatch, steps):
    """Replace the API client; returns the list of request kwargs it received."""
    requests = []

    def create(**kwargs):
        requests.append(kwargs)
        step = steps.pop(0)
        if isinstance(step, Exception):
            raise step
        return step

    stub = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(client, "_get_client", lambda: stub)
    monkeypatch.setattr(client, "_reset_client", lambda: None)
    monkeypatch.setattr(client, "_RETRY_BACKOFF_SECS", 0)
    # Keep the reply path away from the real memory.json.
    monkeypatch.setattr(client, "get_user_memory", lambda user_id: "")
    monkeypatch.setattr(client, "get_conversation_history", lambda user_id, limit=3: "")
    monkeypatch.setattr(client, "get_favorability", lambda user_id: 0)
    monkeypatch.setattr(client, "update_user_memory", lambda *args, **kwargs: None)
    monkeypatch.setattr(client, "adjust_favorability", lambda *args, **kwargs: None)
    return requests


def ask(monkeypatch, steps, text="explain coffee", **kwargs):
    requests = stub_client(monkeypatch, steps)
    server = SimpleNamespace(name="Test server", id=1, members=[None] * 3)
    reply = client.generate_reply_openai(None, 7, server, text, "tester", "system prompt", **kwargs)
    return reply, requests


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


# ── Completion budget and continuation ────────────────────────────────────────


def test_the_request_uses_a_usable_completion_budget(monkeypatch):
    _, requests = ask(monkeypatch, [completion("hello")])
    sent = requests[0]
    assert "max_tokens" not in sent
    assert sent["max_completion_tokens"] >= 1024
    # Reasoning must not eat the visible answer.
    assert sent["extra_body"]["reasoning_effort"] == "low"
    assert sent["extra_body"]["include_reasoning"] is False
    assert sent["extra_body"]["reasoning_effort"] in {"low", "medium", "high"}


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
    assert follow_up[-2]["content"] == "The first half of the answer."
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
    # Reasoning can consume the whole budget and leave no visible text.
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


def test_tools_are_only_attached_when_an_action_is_requested(monkeypatch):
    _, requests = ask(monkeypatch, [completion("hey")], text="how are you today", ai_actions_enabled=True)
    assert "tools" not in requests[0]


# ── Transient failures ────────────────────────────────────────────────────────


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
    monkeypatch.setattr(client, "_rl_cooldown", {})
    reply, requests = ask(monkeypatch, [
        RateLimitError("slow down", response=_FakeResponse(429, {"retry-after": "7"}), body={}),
    ])
    assert reply.startswith("ai_error:rate_limit:")
    assert len(requests) == 1
    # The next call short-circuits without touching the API at all.
    reply, requests = ask(monkeypatch, [])
    assert reply.startswith("ai_error:rate_limit:")
    assert requests == []


def test_a_content_filter_response_reports_safety(monkeypatch):
    reply, _ = ask(monkeypatch, [completion(None, "content_filter")])
    assert reply == "ai_error:safety"


# ── Memory persistence cannot take the AI down ────────────────────────────────


def test_a_corrupt_memory_file_is_set_aside_and_memory_still_loads(tmp_path, monkeypatch):
    path = tmp_path / "memory.json"
    path.write_text("{ this is not json", encoding="utf-8")
    monkeypatch.setattr(memory, "MEMORY_FILE", str(path))

    data = memory._load_memory()

    assert data == {"users": {}, "favorability": {}, "conversations": {}}
    assert (tmp_path / "memory.json.corrupt").read_text(encoding="utf-8") == "{ this is not json"
    assert not path.exists()


def test_memory_writes_are_atomic_and_leave_no_temp_file(tmp_path, monkeypatch):
    path = tmp_path / "memory.json"
    monkeypatch.setattr(memory, "MEMORY_FILE", str(path))
    monkeypatch.setattr(memory, "_memory_data", {"users": {}, "favorability": {}, "conversations": {}})

    memory.update_user_memory(11, "hello", role="someone")

    assert json.loads(path.read_text(encoding="utf-8"))["conversations"]["11"][0]["content"] == "hello"
    assert list(tmp_path.iterdir()) == [path]


def test_a_malformed_memory_entry_does_not_break_reading(tmp_path, monkeypatch):
    monkeypatch.setattr(memory, "_memory_data", {
        "users": {"11": None},
        "favorability": {},
        "conversations": {"11": [{"role": "user", "content": "hi"}, "junk", None]},
    })
    assert memory.get_user_memory(11) == ""
    assert memory.get_conversation_history(11) == "user: hi"


def test_a_read_only_memory_file_never_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(memory, "MEMORY_FILE", str(tmp_path / "missing" / "memory.json"))
    monkeypatch.setattr(memory, "_memory_data", {"users": {}, "favorability": {}, "conversations": {}})
    memory.save_memory()  # must not raise into the reply path
    assert memory.get_user_memory(1) == ""
