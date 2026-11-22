"""Tests for the Plotly renderer: every chart kind of the catalog can be drawn."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from chartrank.catalog import CATALOG
from chartrank.render.plotly import KIND_LABELS, RENDERERS, chart_title, render
from chartrank.spec import ChartSpec


@pytest.fixture
def mixed() -> pd.DataFrame:
    """60 rows with every plot type: category, numbers, boolean, date."""
    n = 60
    i = np.arange(n)
    return pd.DataFrame(
        {
            "group": np.array(["A", "B", "C"])[i % 3],
            "channel": np.array(["web", "shop"])[i % 2],
            "value": 10 + (i % 7) * 3.5 + i * 0.2,
            "other": 5 + (i % 5) * 1.5 - i * 0.1,
            "flag": (i % 4 == 0).astype(int),
            "day": pd.date_range("2026-09-01", periods=n, freq="D"),
        }
    )


# Columns to use for each kind (x, y), following the catalog rows.
COLUMNS = {
    "box": ("group", "value"),
    "violin": ("group", "value"),
    "bar_median": ("group", "value"),
    "strip": ("group", "value"),
    "histogram_overlay": ("group", "value"),
    "density_by_group": ("group", "value"),
    "scatter": ("value", "other"),
    "density_heatmap": ("value", "other"),
    "scatter_trend": ("value", "other"),
    "grouped_bar": ("group", "channel"),
    "stacked_bar_100": ("group", "channel"),
    "count_heatmap": ("group", "channel"),
    "line": ("day", "value"),
    "line_rolling": ("day", "value"),
    "area": ("day", "value"),
    "stacked_area_100": ("day", "channel"),
    "stacked_bar_period": ("day", "channel"),
    "box_by_class": ("value", "flag"),
    "histogram_by_class": ("value", "flag"),
    "rate_by_bin": ("value", "flag"),
}


def test_every_catalog_kind_has_a_renderer_and_a_label() -> None:
    catalog_kinds = {kind for kinds in CATALOG.values() for kind in kinds}
    assert catalog_kinds <= set(RENDERERS)
    assert catalog_kinds <= set(KIND_LABELS)
    assert catalog_kinds <= set(COLUMNS)


@pytest.mark.parametrize("kind", sorted(COLUMNS))
def test_each_kind_draws_a_figure(kind: str, mixed: pd.DataFrame) -> None:
    x, y = COLUMNS[kind]
    figure = render(ChartSpec(kind=kind, x=x, y=y, intent="compare"), mixed)
    assert isinstance(figure, go.Figure)
    assert len(figure.data) >= 1


@pytest.mark.parametrize("kind", sorted(COLUMNS))
def test_rendering_does_not_modify_the_data(kind: str, mixed: pd.DataFrame) -> None:
    before = mixed.copy()
    x, y = COLUMNS[kind]
    render(ChartSpec(kind=kind, x=x, y=y, intent="compare"), mixed)
    pd.testing.assert_frame_equal(mixed, before)


def test_missing_values_are_left_out(titanic: pd.DataFrame) -> None:
    # Age has 177 missing values: the scatter shows the 714 complete rows
    figure = render(ChartSpec(kind="scatter", x="Age", y="Fare", intent="r"), titanic)
    assert len(figure.data[0].x) == 714


@pytest.mark.parametrize("kind", ["box", "violin", "strip", "bar_median"])
def test_categories_follow_their_natural_order(
    kind: str, titanic: pd.DataFrame
) -> None:
    # Titanic rows start with class 3, then 1: the axis must still read 1, 2, 3
    figure = render(ChartSpec(kind=kind, x="Pclass", y="Fare", intent="c"), titanic)
    layout_order = figure.layout.xaxis.categoryarray
    shown = list(layout_order) if layout_order else list(figure.data[0].x)
    assert shown == ["1", "2", "3"]


def test_bar_median_values(titanic: pd.DataFrame) -> None:
    figure = render(
        ChartSpec(kind="bar_median", x="Pclass", y="Fare", intent="c"), titanic
    )
    medians = titanic.groupby("Pclass")["Fare"].median().tolist()
    assert list(figure.data[0].y) == pytest.approx(medians)


def test_rate_by_bin_is_a_percentage_from_zero(mixed: pd.DataFrame) -> None:
    spec = ChartSpec(kind="rate_by_bin", x="value", y="flag", intent="compare")
    figure = render(spec, mixed)
    assert all(0 <= rate <= 100 for rate in figure.data[0].y)
    assert list(figure.layout.yaxis.range) == [0, 100]


def test_density_skips_groups_too_small(mixed: pd.DataFrame) -> None:
    tiny = pd.concat([mixed, pd.DataFrame({"group": ["Z"], "value": [12.0]})])
    spec = ChartSpec(kind="density_by_group", x="group", y="value", intent="d")
    figure = render(spec, tiny)
    assert [trace.name for trace in figure.data] == ["A", "B", "C"]


def test_title_has_a_star_only_for_the_best() -> None:
    best = ChartSpec(kind="box", x="Pclass", y="Fare", intent="compare", rank=1)
    other = ChartSpec(kind="violin", x="Pclass", y="Fare", intent="compare", rank=2)
    assert chart_title(best) == "★ Box plot: Fare by Pclass"
    assert chart_title(other) == "Violin plot: Fare by Pclass"


def test_figure_title_is_set(titanic: pd.DataFrame) -> None:
    spec = ChartSpec(kind="box", x="Pclass", y="Fare", intent="compare", rank=1)
    assert render(spec, titanic).layout.title.text == "★ Box plot: Fare by Pclass"


def test_unknown_kind_is_a_clear_error(mixed: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="No Plotly renderer for chart kind 'pie3d'"):
        render(ChartSpec(kind="pie3d", x="group", y="value", intent="c"), mixed)


def test_missing_y_is_a_clear_error(mixed: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="needs a y column"):
        render(ChartSpec(kind="box", x="group", y=None, intent="c"), mixed)
