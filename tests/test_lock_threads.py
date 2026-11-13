"""`/lock` and `/unlock` inside threads, including forum posts.

A forum post is a thread, so locking one is the thread's own ``locked`` flag —
there is no @everyone overwrite to write, and the permission involved is
**Manage Threads** rather than **Manage Roles**.
"""
import asyncio
import sys
from pathlib import Path

import discord

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.moderation._channels import ChannelsMixin, set_thread_locked  # noqa: E402


class _Thread(discord.Thread):
    """A real Thread subclass without Discord state, recording its edit calls."""

    def __init__(self):
        self.id = 777
        self.calls = []

    async def edit(self, **kwargs):
        self.calls.append(kwargs)

    async def set_permissions(self, *args, **kwargs):
        raise AssertionError("a thread has no permission overwrites")


def _thread():
    return _Thread()


def _ctx(channel, **grants):
    permissions = type("Permissions", (), {
        "manage_roles": grants.get("manage_roles", False),
        "manage_threads": grants.get("manage_threads", False),
    })()
    return type("Context", (), {"channel": channel, "permissions": permissions})()


def test_locking_a_thread_sets_its_locked_flag():
    thread = _thread()

    asyncio.run(set_thread_locked(thread, True, reason="Locked by tester"))

    assert thread.calls == [{"locked": True, "reason": "Locked by tester"}]


def test_unlocking_a_thread_clears_its_locked_flag():
    thread = _thread()

    asyncio.run(set_thread_locked(thread, False, reason="Unlocked by tester"))

    assert thread.calls == [{"locked": False, "reason": "Unlocked by tester"}]


def test_a_thread_is_a_lockable_target():
    thread = _thread()

    assert ChannelsMixin._lockable_channel(object.__new__(ChannelsMixin), _ctx(thread)) is thread


def test_threads_are_gated_on_manage_threads():
    thread = _thread()
    mixin = object.__new__(ChannelsMixin)

    assert mixin._lock_permission(_ctx(thread, manage_threads=True), thread) is None
    assert mixin._lock_permission(_ctx(thread, manage_roles=True), thread) == "need_manage_threads"


def test_channels_still_need_manage_roles():
    channel = object()
    mixin = object.__new__(ChannelsMixin)

    assert mixin._lock_permission(_ctx(channel, manage_roles=True), channel) is None
    assert mixin._lock_permission(_ctx(channel, manage_threads=True), channel) == "need_manage_roles"


def test_both_commands_share_the_thread_aware_path():
    source = (ROOT / "src" / "cogs" / "moderation" / "_channels.py").read_text(encoding="utf-8")
    path = source.split("async def _set_locked(", 1)[1].split("async def lock(", 1)[0]

    assert "isinstance(channel, discord.Thread)" in path
    assert "set_thread_locked(" in path
    # A channel still has to be locked through the permission endpoint.
    assert "set_everyone_send_messages(" in path

    lock_body = source.split("async def lock(", 1)[1].split("async def unlock(", 1)[0]
    unlock_body = source.split("async def unlock(", 1)[1]
    assert "_set_locked(ctx, True)" in lock_body
    assert "_set_locked(ctx, False)" in unlock_body
