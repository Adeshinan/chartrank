"""Tests for semantic type detection (task 1.1, EF-02)."""

from typing import Any

import numpy as np
import pandas as pd
import pytest

from chartrank.profile import THRESHOLDS, detect_type

# ---------------------------------------------------------------------------
# One small column per semantic type.
# Each case: (column values, expected type). pytest runs the test once per case.
# ---------------------------------------------------------------------------
CASES: list[tuple[str, Any, str]] = [
    # continuous: decimal numbers on a continuous scale
    ("continuous", [22.0, 38.5, 26.0, 35.2, 54.0, 2.0, 27.5], "continuous"),
    # discrete: integers that count something, few distinct values
    ("discrete", [0, 1, 0, 3, 1, 2, 0, 5], "discrete"),
    # integers with many distinct values behave like a continuous scale
    ("many_integers", list(range(0, 300, 3)) + [0, 3], "continuous"),
    # boolean: True/False, or exactly the two values 0 and 1
    ("bool_dtype", [True, False, True, True], "boolean"),
    ("zero_one", [0, 1, 1, 0, 1], "boolean"),
    # category: labels, few distinct values
    ("category", ["S", "C", "Q", "S", "S", "C"], "category"),
    # two labels that are not 0/1 are a category, not a boolean (like Sex)
    ("two_labels", ["male", "female", "male", "male"], "category"),
    # high_cardinality: labels, too many distinct values to draw one bar each
    ("high_cardinality", [f"C{i}" for i in range(30)] * 2, "high_cardinality"),
    # ordinal: an ordered pandas Categorical (the only automatic signal of order)
    (
        "ordinal",
        pd.Categorical(
            ["low", "high", "mid", "low"],
            categories=["low", "mid", "high"],
            ordered=True,
        ),
        "ordinal",
    ),
    # date: datetime values
    ("date", pd.to_datetime(["2026-11-14", "2026-11-15", "2026-11-16"]), "date"),
    # id: one different value per row (and enough rows to be sure)
    ("id", list(range(1, 31)), "id"),
    ("text_id", [f"P{i:03d}" for i in range(30)], "id"),
    # text: long free text (like passenger names)
    (
        "text",
        [f"Passenger number {i}, travelling with family" for i in range(30)],
        "text",
    ),
]


@pytest.mark.parametrize(
    ("values", "expected"),
    [(values, expected) for _, values, expected in CASES],
    ids=[name for name, _, _ in CASES],
)
def test_detect_type(values: Any, expected: str) -> None:
    assert detect_type(pd.Series(values)) == expected


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------
def test_column_with_no_rows_is_empty() -> None:
    assert detect_type(pd.Series([], dtype="float64")) == "empty"


def test_column_fully_missing_is_empty() -> None:
    assert detect_type(pd.Series([np.nan, np.nan, np.nan])) == "empty"


def test_column_with_one_value_is_constant() -> None:
    assert detect_type(pd.Series([3, 3, 3, np.nan])) == "constant"


def test_missing_values_are_ignored() -> None:
    # 0/1 with holes is still a boolean
    assert detect_type(pd.Series([0, 1, np.nan, 1, 0])) == "boolean"


def test_few_unique_values_are_not_an_id() -> None:
    # 5 rows, all different: too few rows to call it an identifier
    assert detect_type(pd.Series([10, 20, 30, 40, 50])) == "discrete"


def test_thresholds_can_be_changed() -> None:
    labels = pd.Series([f"C{i}" for i in range(30)] * 2)
    custom = {**THRESHOLDS, "category_max_distinct": 50}
    assert detect_type(labels, thresholds=custom) == "category"


def test_series_is_not_modified() -> None:
    series = pd.Series([0, 1, np.nan, 1])
    before = series.copy()
    detect_type(series)
    pd.testing.assert_series_equal(series, before)
