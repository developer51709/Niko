"""Part 3 drill: a compressed soak of the real supervisor and Flask child.

The 24-hour staging soak needs a deployed instance. This is the same shape at a
size that fits a test run: continuous dashboard polling through the proxy,
periodic supervised restarts, and checks for the leaks and hangs a long run
would expose — all against the real supervisor, the real API server, and the
real child lifecycle.
"""

from __future__ import annotations

import time

import psutil
import pytest

#: Wall-clock length of the soak. The 24-hour gate still needs staging; this is
#: deliberately long enough to cross several restart generations and thousands
#: of proxied requests.
DURATION_SECONDS = 30.0
RESTART_EVERY_SECONDS = 6.0


@pytest.mark.slow
def test_soak_polling_and_restarts_stay_bounded(supervisor):
    from pathlib import Path

    api_child = Path(__file__).resolve().parents[1] / "supervisor" / "supervised_api_child.py"
    handle = supervisor(
        "normal",
        startup_timeout=60.0,
        heartbeat_timeout=10.0,
        shutdown_timeout=5.0,
        args=["--child", str(api_child)],
    )
    handle.wait_ready(timeout=60)
    time.sleep(0.5)

    process = psutil.Process(handle.pid)
    baseline_fds = process.num_fds()
    baseline_rss = process.memory_info().rss

    health_failures: list[str] = []
    api_failures: list[str] = []
    overlaps: list[int] = []
    restarts = 0
    last_restart = time.monotonic()
    deadline = last_restart + DURATION_SECONDS

    while time.monotonic() < deadline:
        try:
            response = handle.request("/health", timeout=5)
            if response.status_code != 200:
                health_failures.append(f"/health {response.status_code}")
        except Exception as exc:  # noqa: BLE001 - recorded, asserted at the end
            health_failures.append(f"/health {type(exc).__name__}: {exc}")
        try:
            response = handle.request("/api/health", timeout=5)
            # 503 is correct while a restart has no ready child; anything else
            # (a hang, a 500, a truncated response) is not.
            if response.status_code not in {200, 503}:
                api_failures.append(f"/api/health {response.status_code}")
        except Exception as exc:  # noqa: BLE001 - recorded, asserted at the end
            api_failures.append(f"/api/health {type(exc).__name__}: {exc}")

        children = process.children(recursive=True)
        if len(children) > 1:
            overlaps.append(len(children))

        if time.monotonic() - last_restart >= RESTART_EVERY_SECONDS:
            old_pid = handle.status()["child"]["pid"]
            accepted = handle.control("restart", delay=0.05, reason="local soak")
            assert accepted["ok"] is True
            handle.wait_for_new_child(old_pid, timeout=30)
            handle.wait_ready(timeout=30)
            restarts += 1
            last_restart = time.monotonic()

        time.sleep(0.1)

    handle.wait_ready(timeout=30)
    time.sleep(0.5)
    final_fds = process.num_fds()
    final_rss = process.memory_info().rss
    final = handle.status()

    print(
        "soak:",
        f"{restarts} restarts,",
        f"fds {baseline_fds}->{final_fds},",
        f"rss {baseline_rss // 1024}->{final_rss // 1024} KiB",
    )
    print("soak: health failures", health_failures[:5], "api failures", api_failures[:5])

    assert health_failures == []
    assert api_failures == []
    assert overlaps == []
    assert restarts >= 4, restarts
    assert final["state"] in {"active", "degraded"}
    assert handle.request("/api/health").status_code == 200
    assert final_fds - baseline_fds <= 16, (baseline_fds, final_fds)
    assert final_rss - baseline_rss <= 64 * 1024 * 1024, (baseline_rss, final_rss)
