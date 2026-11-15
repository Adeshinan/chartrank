"""Tests for the minimal profile (task 0.4): dtype, missing share, distinct count."""

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
    assert list(result.columns) == ["dtype", "missing", "distinct"]


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


def test_rejects_non_dataframe_with_clear_message() -> None:
    with pytest.raises(TypeError, match="expects a pandas DataFrame"):
        cr.profile([1, 2, 3])  # type: ignore[arg-type]
