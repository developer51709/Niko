"""Supervisor wiring for the database child, without starting any process."""

from __future__ import annotations

from supervisor import Options, parse_args


def test_split_layout_runs_the_database_as_its_own_child_first():
    specs = Options(split_web=True, split_db=True).child_specs()

    assert [spec.name for spec in specs] == ["db", "web", "bot"]
    assert specs[0].script.name == "db_child.py"
    assert [spec.name for spec in specs if spec.primary] == ["web"]


def test_combined_fallback_keeps_the_pool_inside_the_bot_child():
    specs = Options(split_web=False, split_db=False).child_specs()

    assert [spec.name for spec in specs] == ["bot"]
    assert specs[0].primary is True


def test_database_split_follows_the_web_split_unless_it_is_named(monkeypatch):
    monkeypatch.delenv("NIKO_SPLIT_DB", raising=False)

    assert parse_args(["--split-web"]).split_db is True
    assert parse_args(["--no-split-web"]).split_db is False
    assert parse_args(["--split-web", "--no-split-db"]).split_db is False
    assert parse_args(["--no-split-web", "--split-db"]).split_db is True


def test_database_split_can_be_forced_from_the_environment(monkeypatch):
    monkeypatch.setenv("NIKO_SPLIT_DB", "0")
    assert parse_args(["--split-web"]).split_db is False

    monkeypatch.setenv("NIKO_SPLIT_DB", "1")
    assert parse_args(["--no-split-web"]).split_db is True
