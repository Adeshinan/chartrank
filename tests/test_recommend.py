"""Tests for recommend(): from two columns and an intent to ranked ChartSpecs."""

import pandas as pd
import pytest

from chartrank.recommend import recommend
from chartrank.spec import ChartSpec


def kinds(specs: list[ChartSpec]) -> list[str]:
    return [spec.kind for spec in specs]


# ---------------------------------------------------------------------------
# Titanic: the "done when" of task 1.2
# ---------------------------------------------------------------------------


def test_titanic_fare_by_class(titanic: pd.DataFrame) -> None:
    specs = recommend(titanic, "Pclass", "Fare", "compare")
    assert kinds(specs) == ["box", "violin", "bar_median", "strip"]
    assert [spec.rank for spec in specs] == [1, 2, 3, 4]
    assert specs[0].is_best
    assert all(spec.x == "Pclass" and spec.y == "Fare" for spec in specs)
    assert all(spec.intent == "compare" for spec in specs)


def test_swapped_columns_are_put_back_in_order(titanic: pd.DataFrame) -> None:
    specs = recommend(titanic, "Fare", "Pclass", "compare")
    assert kinds(specs) == ["box", "violin", "bar_median", "strip"]
    assert specs[0].x == "Pclass"
    assert specs[0].y == "Fare"


def test_boolean_drawn_as_category(titanic: pd.DataFrame) -> None:
    assert recommend(titanic, "Survived", "Fare", "compare")[0].kind == "box"


def test_numeric_vs_boolean_has_its_own_row(titanic: pd.DataFrame) -> None:
    specs = recommend(titanic, "Fare", "Survived", "compare")
    assert kinds(specs) == ["box_by_class", "histogram_by_class", "rate_by_bin"]


def test_relationship_between_two_numbers(titanic: pd.DataFrame) -> None:
    assert recommend(titanic, "Age", "Fare", "relationship")[0].kind == "scatter"


def test_two_categories(titanic: pd.DataFrame) -> None:
    assert recommend(titanic, "Sex", "Embarked", "composition")[0].kind == "grouped_bar"


def test_date_and_number_trend() -> None:
    sales = pd.DataFrame(
        {
            "day": pd.date_range("2026-11-01", periods=30, freq="D"),
            "revenue": [100.0 + 3.5 * i for i in range(30)],
        }
    )
    assert kinds(recommend(sales, "day", "revenue", "trend")) == [
        "line",
        "line_rolling",
        "area",
    ]


def test_date_and_category_composition() -> None:
    orders = pd.DataFrame(
        {
            "day": pd.date_range("2026-11-01", periods=30, freq="D"),
            "channel": ["web", "shop", "phone"] * 10,
        }
    )
    assert recommend(orders, "day", "channel", "composition")[0].kind == (
        "stacked_area_100"
    )


def test_is_deterministic(titanic: pd.DataFrame) -> None:
    first = recommend(titanic, "Pclass", "Fare", "compare")
    second = recommend(titanic, "Pclass", "Fare", "compare")
    assert first == second


def test_input_dataframe_is_not_modified(titanic: pd.DataFrame) -> None:
    before = titanic.copy()
    recommend(titanic, "Pclass", "Fare", "compare")
    pd.testing.assert_frame_equal(titanic, before)


# ---------------------------------------------------------------------------
# Clear errors (EF-25, ENF-09): what is wrong and what to do
# ---------------------------------------------------------------------------


def test_impossible_intent_lists_the_possible_ones(titanic: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="trend") as error:
        recommend(titanic, "Pclass", "Fare", "trend")
    assert "distribution, compare" in str(error.value)


def test_unknown_intent_suggests_a_close_name(titanic: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="Did you mean 'compare'"):
        recommend(titanic, "Pclass", "Fare", "comapre")


def test_unknown_intent_without_close_name_lists_all(titanic: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="Possible values: distribution") as error:
        recommend(titanic, "Pclass", "Fare", "xyz")
    assert "Did you mean" not in str(error.value)


def test_unknown_column_suggests_a_close_name(titanic: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="Did you mean 'Fare'"):
        recommend(titanic, "Pclass", "Fair", "compare")


def test_identifier_column_is_refused(titanic: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="PassengerId.*identifier"):
        recommend(titanic, "PassengerId", "Fare", "compare")


def test_same_column_twice_is_refused(titanic: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="two different columns"):
        recommend(titanic, "Fare", "Fare", "relationship")


def test_no_intent_at_all(titanic: pd.DataFrame) -> None:
    dates = pd.DataFrame(
        {
            "start": pd.date_range("2026-01-01", periods=5),
            "end": pd.date_range("2026-02-01", periods=5),
        }
    )
    with pytest.raises(ValueError, match="No chart is available"):
        recommend(dates, "start", "end", "trend")


def test_rejects_non_dataframe() -> None:
    with pytest.raises(TypeError, match="expects a pandas DataFrame"):
        recommend([1, 2], "a", "b", "compare")  # type: ignore[arg-type]
