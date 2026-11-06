"""Part 3 drill: one child and one set of boot side effects at a time.

The 24-hour soak's duplicate-side-effect audit cannot run without a real bot and
Discord. This is the process-level core of it: across repeated supervised
restarts, no two children overlap, every boot runs its startup effect exactly
once, and nothing is left behind when the supervisor stops.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path

import psutil


def _boot_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []


def test_restarts_never_overlap_children_or_repeat_a_startup_effect(supervisor, tmp_path):
    effect_dir = tmp_path / "effects"
    effect_dir.mkdir()
    handle = supervisor(
        "normal",
        backoff_initial=0.01,
        backoff_max=0.02,
        env={"FAKE_CHILD_EFFECT_DIR": str(effect_dir)},
    )
    handle.wait_ready()

    samples: list[int] = []
    stop_sampling = threading.Event()

    def sample_children() -> None:
        try:
            process = psutil.Process(handle.pid)
        except psutil.Error:
            return
        while not stop_sampling.is_set():
            try:
                samples.append(len(process.children(recursive=True)))
            except psutil.Error:
                pass
            time.sleep(0.02)

    sampler = threading.Thread(target=sample_children, name="child-sample", daemon=True)
    sampler.start()

    restarts = 5
    try:
        for _ in range(restarts):
            old_pid = handle.status()["child"]["pid"]
            accepted = handle.control("restart", delay=0.05, reason="single-writer drill")
            assert accepted["ok"] is True
            handle.wait_for_new_child(old_pid, timeout=15)
            handle.wait_ready(timeout=15)
    finally:
        stop_sampling.set()
        sampler.join(timeout=5)

    final = handle.status()
    boots = _boot_lines(effect_dir / "boots.log")

    assert max(samples) <= 1, f"two children ran at once: max {max(samples)}"
    assert final["child_starts"] == 1 + restarts
    assert len(boots) == final["child_starts"], boots
    assert len(set(boots)) == len(boots), "a child ran its startup effect twice"
    assert final["consecutive_failures"] == 0

    child_pid = final["child"]["pid"]
    handle.stop()
    assert not psutil.pid_exists(child_pid)
    assert handle.descendants() == []
