"""Regression tests for persisted giveaway discovery across database backends."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from database import _ConditionParser


def test_active_giveaway_filter_matches_numeric_and_boolean_rows():
    parsed = _ConditionParser([]).parse("(ended = 0 OR ended = FALSE)")

    assert parsed == {"$or": [{"ended": 0}, {"ended": False}]}


def test_boolean_sql_literals_are_parsed_as_booleans():
    assert _ConditionParser([]).parse("ended = TRUE") == {"ended": True}
    assert _ConditionParser([]).parse("ended = FALSE") == {"ended": False}
