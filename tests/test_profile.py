"""Tests for profile(): semantic type and indicators of each column (EF-02, EF-03)."""

import numpy as np
import pandas as pd
import pytest

import chartrank as cr


@pytest.fixture
def passengers() -> pd.DataFrame:
    """A tiny Titanic-like DataFrame: 4 passengers, a few missing values."""
    return pd.DataFrame(
        {
            "Pclass": [1, 3, 3, 2],
            "Sex": ["female", "male", "male", None],
            "Age": [38.0, np.nan, 26.0, np.nan],
        }
    )


def test_one_row_per_column_in_original_order(passengers: pd.DataFrame) -> None:
    result = cr.profile(passengers)
    assert list(result.index) == ["Pclass", "Sex", "Age"]
    assert list(result.columns) == ["type", "dtype", "missing", "distinct", "skew"]


def test_dtype(passengers: pd.DataFrame) -> None:
    result = cr.profile(passengers)
    assert result.loc["Pclass", "dtype"] == "int64"
    assert result.loc["Age", "dtype"] == "float64"


def test_missing_is_a_share_between_0_and_1(passengers: pd.DataFrame) -> None:
    result = cr.profile(passengers)
    assert result.loc["Pclass", "missing"] == 0.0
    assert result.loc["Sex", "missing"] == 0.25  # 1 missing out of 4
    assert result.loc["Age", "missing"] == 0.5  # 2 missing out of 4


def test_distinct_ignores_missing_values(passengers: pd.DataFrame) -> None:
    result = cr.profile(passengers)
    assert result.loc["Pclass", "distinct"] == 3  # 1, 2, 3
    assert result.loc["Sex", "distinct"] == 2  # female, male (None not counted)
    assert result.loc["Age", "distinct"] == 2  # 38, 26


def test_empty_dataframe_has_no_missing_values() -> None:
    result = cr.profile(pd.DataFrame({"Fare": pd.Series([], dtype="float64")}))
    assert result.loc["Fare", "missing"] == 0.0
    assert result.loc["Fare", "distinct"] == 0


def test_input_dataframe_is_not_modified(passengers: pd.DataFrame) -> None:
    before = passengers.copy()
    cr.profile(passengers)
    pd.testing.assert_frame_equal(passengers, before)


def test_skew_only_for_numeric_columns(passengers: pd.DataFrame) -> None:
    result = cr.profile(passengers)
    # skew needs at least 3 values: Pclass has 4 (Age has only 2 here)
    assert not np.isnan(result.loc["Pclass", "skew"])
    assert np.isnan(result.loc["Sex", "skew"])


# ---------------------------------------------------------------------------
# Titanic: the reference profile expected by task 1.1
# ---------------------------------------------------------------------------
TITANIC_TYPES = {
    "PassengerId": "id",
    "Survived": "boolean",
    "Pclass": "discrete",
    "Name": "text",
    "Sex": "category",
    "Age": "continuous",
    "SibSp": "discrete",
    "Parch": "discrete",
    "Ticket": "high_cardinality",
    "Fare": "continuous",
    "Cabin": "high_cardinality",
    "Embarked": "category",
}


@pytest.mark.parametrize(("column", "expected"), TITANIC_TYPES.items())
def test_titanic_types(titanic: pd.DataFrame, column: str, expected: str) -> None:
    assert cr.profile(titanic).loc[column, "type"] == expected


def test_titanic_indicators(titanic: pd.DataFrame) -> None:
    result = cr.profile(titanic)
    assert result.loc["Age", "missing"] == pytest.approx(0.199, abs=0.001)
    assert result.loc["Cabin", "missing"] == pytest.approx(0.771, abs=0.001)
    assert result.loc["Fare", "skew"] == pytest.approx(4.79, abs=0.01)


def test_titanic_is_not_modified(titanic: pd.DataFrame) -> None:
    before = titanic.copy()
    cr.profile(titanic)
    pd.testing.assert_frame_equal(titanic, before)


def test_rejects_non_dataframe_with_clear_message() -> None:
    with pytest.raises(TypeError, match="expects a pandas DataFrame"):
        cr.profile([1, 2, 3])  # type: ignore[arg-type]
