"""Tests for the chart catalog (section 6.2 of the specification)."""

import pytest

from chartrank.catalog import CATALOG, INTENTS, candidates, plot_type, possible_intents

# ---------------------------------------------------------------------------
# From semantic type (what the profiler sees) to plot type (how to draw it)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("semantic_type", "n_distinct", "expected"),
    [
        ("continuous", 248, "numeric"),
        ("discrete", 3, "category"),  # Pclass: few values, drawn by group
        ("discrete", 10, "category"),  # the limit is included
        ("discrete", 15, "numeric"),  # many values: drawn as numbers
        ("category", 3, "category"),
        ("ordinal", 3, "category"),
        ("high_cardinality", 147, "category"),  # top N handled by guard rules
        ("boolean", 2, "boolean"),
        ("date", 365, "date"),
        ("id", 891, None),  # never drawn
        ("text", 891, None),
        ("empty", 0, None),
        ("constant", 1, None),
    ],
)
def test_plot_type(semantic_type: str, n_distinct: int, expected: str | None) -> None:
    assert plot_type(semantic_type, n_distinct) == expected


# ---------------------------------------------------------------------------
# The 7 rows of section 6.2, in the specification's order (★ first)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        (("category", "numeric", "compare"), ["box", "violin", "bar_median", "strip"]),
        (
            ("category", "numeric", "distribution"),
            ["histogram_overlay", "density_by_group"],
        ),
        (
            ("numeric", "numeric", "relationship"),
            ["scatter", "hexbin", "scatter_trend"],
        ),
        (
            ("category", "category", "compare"),
            ["grouped_bar", "stacked_bar_100", "count_heatmap"],
        ),
        (
            ("category", "category", "composition"),
            ["grouped_bar", "stacked_bar_100", "count_heatmap"],
        ),
        (("date", "numeric", "trend"), ["line", "line_rolling", "area"]),
        (
            ("date", "category", "composition"),
            ["stacked_area_100", "stacked_bar_period"],
        ),
        (
            ("numeric", "boolean", "compare"),
            ["box_by_class", "histogram_overlay", "rate_by_bin"],
        ),
    ],
)
def test_catalog_rows(key: tuple[str, str, str], expected: list[str]) -> None:
    assert list(CATALOG[key]) == expected


def test_every_row_has_1_to_5_candidates() -> None:
    for key, kinds in CATALOG.items():
        assert 1 <= len(kinds) <= 5, key


def test_every_intent_in_catalog_is_known() -> None:
    assert {intent for _, _, intent in CATALOG} <= set(INTENTS)


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------


def test_candidates_found() -> None:
    assert candidates("category", "numeric", "compare")[0] == "box"


def test_boolean_falls_back_to_category() -> None:
    # Survived (boolean) vs Fare (numeric): same charts as category vs numeric
    assert candidates("boolean", "numeric", "compare") == candidates(
        "category", "numeric", "compare"
    )


def test_candidates_not_found_is_empty() -> None:
    assert candidates("category", "numeric", "trend") == ()


def test_possible_intents() -> None:
    # in the order of INTENTS (EF-20)
    assert possible_intents("category", "numeric") == ["distribution", "compare"]
    assert possible_intents("date", "numeric") == ["trend"]
    assert possible_intents("date", "date") == []
