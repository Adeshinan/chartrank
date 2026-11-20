"""Tests for ChartSpec, the neutral description of a chart (EF-50)."""

import dataclasses

import pytest

from chartrank.spec import ChartSpec


def test_defaults() -> None:
    spec = ChartSpec(kind="box", x="Pclass", y="Fare", intent="compare")
    assert spec.transforms == ()
    assert spec.title == ""
    assert spec.rank == 0


def test_is_frozen() -> None:
    spec = ChartSpec(kind="box", x="Pclass", y="Fare", intent="compare")
    with pytest.raises(dataclasses.FrozenInstanceError):
        spec.kind = "violin"  # type: ignore[misc]


def test_same_content_means_equal_and_same_hash() -> None:
    a = ChartSpec(kind="box", x="Pclass", y="Fare", intent="compare", rank=1)
    b = ChartSpec(kind="box", x="Pclass", y="Fare", intent="compare", rank=1)
    assert a == b
    assert hash(a) == hash(b)
    assert len({a, b}) == 1  # usable in a set: duplicates collapse


def test_is_best_only_for_rank_1() -> None:
    best = ChartSpec(kind="box", x="Pclass", y="Fare", intent="compare", rank=1)
    other = ChartSpec(kind="violin", x="Pclass", y="Fare", intent="compare", rank=2)
    assert best.is_best
    assert not other.is_best


def test_one_variable_chart_has_no_y() -> None:
    spec = ChartSpec(kind="histogram", x="Age", y=None, intent="distribution")
    assert spec.y is None


def test_with_rank_returns_a_new_spec() -> None:
    spec = ChartSpec(kind="box", x="Pclass", y="Fare", intent="compare")
    ranked = spec.with_rank(1)
    assert ranked.rank == 1
    assert spec.rank == 0  # the original is untouched
