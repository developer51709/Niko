"""``all`` spends the whole wallet wherever an economy command takes an amount."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils.economy.amount import resolve_amount  # noqa: E402


def test_all_resolves_to_the_whole_balance():
    assert resolve_amount("all", 1250) == 1250
    assert resolve_amount("ALL", 1250) == 1250
    assert resolve_amount("  all ", 1250) == 1250
    assert resolve_amount("max", 1250) == 1250


def test_all_on_an_empty_wallet_is_zero_not_an_error():
    assert resolve_amount("all", 0) == 0


def test_numbers_still_parse_the_way_they_did():
    assert resolve_amount("500", 900) == 500
    assert resolve_amount(500, 900) == 500
    # The wallet is displayed with separators, so typing them back in works.
    assert resolve_amount("1,000", 5_000) == 1000


def test_zero_and_negative_pass_through_for_the_command_to_reject():
    assert resolve_amount("0", 900) == 0
    assert resolve_amount("-25", 900) == -25


def test_anything_else_is_not_an_amount():
    assert resolve_amount("half", 900) is None
    assert resolve_amount("", 900) is None
    assert resolve_amount(None, 900) is None
    assert resolve_amount(True, 900) is None
