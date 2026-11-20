"""Tests for suggest() and the Gallery / Chart objects (EF-51, EF-52)."""

import pandas as pd
import plotly.graph_objects as go
import pytest

import chartrank as cr


@pytest.fixture
def gallery(titanic: pd.DataFrame) -> cr.Gallery:
    return cr.suggest(titanic, x="Pclass", y="Fare", intent="compare")


def test_suggest_returns_a_gallery_of_1_to_5_charts(gallery: cr.Gallery) -> None:
    assert isinstance(gallery, cr.Gallery)
    assert 1 <= len(gallery) <= 5


def test_best_is_the_first_chart(gallery: cr.Gallery) -> None:
    assert gallery.best is gallery[0]
    assert gallery.best.spec.is_best
    assert gallery.best.spec.kind == "box"


def test_figure_is_a_real_plotly_figure(gallery: cr.Gallery) -> None:
    assert isinstance(gallery.best.figure, go.Figure)
    assert isinstance(gallery[1].figure, go.Figure)


def test_figure_is_drawn_once(gallery: cr.Gallery) -> None:
    assert gallery.best.figure is gallery.best.figure


def test_iteration_and_negative_index(gallery: cr.Gallery) -> None:
    kinds = [chart.spec.kind for chart in gallery]
    assert kinds == ["box", "violin", "bar_median", "strip"]
    assert gallery[-1].spec.kind == "strip"


def test_repr_lists_the_charts(gallery: cr.Gallery) -> None:
    text = repr(gallery)
    assert text.startswith("Gallery of 4 charts:")
    assert "[0] ★ Box plot: Fare by Pclass" in text
    assert repr(gallery.best) == "Chart(★ Box plot: Fare by Pclass)"


def test_html_grid_shows_every_chart(gallery: cr.Gallery) -> None:
    html = gallery._repr_html_()
    assert html.count("plotly-graph-div") == 4
    assert "★ Box plot" in html
    assert "Violin plot" in html


def test_show_without_ipython_opens_each_chart(
    gallery: cr.Gallery, monkeypatch: pytest.MonkeyPatch
) -> None:
    shown: list[str] = []
    monkeypatch.setattr(cr.Chart, "show", lambda self: shown.append(self.title))
    monkeypatch.setitem(__import__("sys").modules, "IPython.display", None)
    gallery.show()
    assert len(shown) == 4


def test_chart_show_calls_the_figure(
    gallery: cr.Gallery, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[bool] = []
    monkeypatch.setattr(go.Figure, "show", lambda self, *a, **k: calls.append(True))
    gallery.best.show()
    assert calls == [True]


def test_suggest_errors_are_the_recommend_errors(titanic: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="Possible intents"):
        cr.suggest(titanic, x="Pclass", y="Fare", intent="trend")


def test_suggest_does_not_modify_the_data(titanic: pd.DataFrame) -> None:
    before = titanic.copy()
    gallery = cr.suggest(titanic, x="Pclass", y="Fare", intent="compare")
    for chart in gallery:
        chart.figure  # noqa: B018 - draw every figure
    pd.testing.assert_frame_equal(titanic, before)
