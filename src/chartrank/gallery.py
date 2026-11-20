"""Gallery: the object returned by ``suggest()``.

A ``Gallery`` holds a few ``Chart`` objects, best first. Each ``Chart`` pairs a
``ChartSpec`` (what to draw) with the data, and draws its Plotly figure only
when it is first asked for (``.figure``).
"""

import html
from collections.abc import Iterator
from functools import cached_property
from typing import Any

import pandas as pd

from chartrank.recommend import recommend
from chartrank.render.plotly import chart_title, render
from chartrank.spec import ChartSpec


class Chart:
    """One proposed chart: its description (``spec``) and its figure.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"Pclass": [1, 2, 3, 3], "Fare": [80.0, 21.5, 7.9, 8.1]})
        >>> chart = suggest(df, "Pclass", "Fare", "compare").best
        >>> chart
        Chart(★ Box plot: Fare by Pclass)
    """  # noqa: E501

    def __init__(self, spec: ChartSpec, data: pd.DataFrame) -> None:
        self.spec = spec
        self._data = data

    @cached_property
    def figure(self) -> Any:
        """The Plotly figure (``plotly.graph_objects.Figure``), drawn once."""
        return render(self.spec, self._data)

    @property
    def title(self) -> str:
        """Title of the chart, with ★ for the recommended one."""
        return chart_title(self.spec)

    def show(self) -> None:
        """Display this chart (in a notebook, or in the browser)."""
        self.figure.show()

    def __repr__(self) -> str:
        return f"Chart({self.title})"


class Gallery:
    """The charts proposed for a pair of columns, the recommended one (★) first.

    Use ``g.best`` (or ``g[0]``) for the recommendation, ``g[i]`` for another
    proposal, ``len(g)`` for their number and ``g.show()`` to see them all.
    """

    def __init__(self, charts: list[Chart]) -> None:
        self._charts = charts

    @property
    def best(self) -> Chart:
        """The recommended chart (★)."""
        return self._charts[0]

    def __getitem__(self, index: int) -> Chart:
        return self._charts[index]

    def __len__(self) -> int:
        return len(self._charts)

    def __iter__(self) -> Iterator[Chart]:
        return iter(self._charts)

    def __repr__(self) -> str:
        lines = [f"Gallery of {len(self)} charts:"]
        lines += [f"  [{i}] {chart.title}" for i, chart in enumerate(self)]
        return "\n".join(lines)

    def show(self) -> None:
        """Display all the charts as a grid (two per row).

        In a notebook (Jupyter, VS Code, Colab) the grid is shown inline,
        without any widget; elsewhere each chart opens in the browser.
        """
        try:
            from IPython.display import HTML, display
        except ImportError:
            for chart in self:
                chart.show()
            return
        # IPython's display functions have no type annotations
        display(HTML(self._repr_html_()))  # type: ignore[no-untyped-call]

    def _repr_html_(self) -> str:
        """HTML grid used by notebooks to display the gallery."""
        cells = []
        for i, chart in enumerate(self):
            figure_html = chart.figure.to_html(
                full_html=False,
                # embed plotly.js once (no network call), then reuse it
                include_plotlyjs=(i == 0),
                default_width="100%",
                default_height="380px",
            )
            border = "3px solid #f2b705" if chart.spec.is_best else "1px solid #ddd"
            cells.append(
                f'<div style="border:{border};border-radius:8px;padding:4px">'
                f'<div style="font:600 14px sans-serif;margin:4px 8px">'
                f"[{i}] {html.escape(chart.title)}</div>{figure_html}</div>"
            )
        return (
            '<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));'
            f'gap:12px">{"".join(cells)}</div>'
        )


def suggest(df: pd.DataFrame, x: str, y: str, intent: str) -> Gallery:
    """Propose 1 to 5 charts for two columns and an intent, the best one first.

    Args:
        df: The data. It is never modified.
        x: First column.
        y: Second column.
        intent: ``"distribution"``, ``"compare"``, ``"relationship"``,
            ``"composition"`` or ``"trend"``.

    Returns:
        A ``Gallery``: ``g.show()``, ``g.best``, ``g[i]``, ``g[i].figure``.

    Raises:
        TypeError: If ``df`` is not a DataFrame.
        ValueError: Unknown column or intent, or impossible intent (the
            message lists the possible ones).
    """
    specs = recommend(df, x, y, intent)
    return Gallery([Chart(spec, df) for spec in specs])
