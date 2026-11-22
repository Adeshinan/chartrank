"""Plotly backend: ChartSpec + DataFrame -> plotly.graph_objects.Figure.

One small function per chart kind, registered in ``RENDERERS``. Each function
works on a copy of the two columns without missing values: the user's
DataFrame is never modified. No theme yet (Plotly defaults): it comes in task 4.1.
"""

from collections.abc import Callable
from typing import Any, cast

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from chartrank.spec import ChartSpec

Renderer = Callable[[ChartSpec, pd.DataFrame], go.Figure]

#: Human-readable name of each chart kind (used in titles).
KIND_LABELS: dict[str, str] = {
    "box": "Box plot",
    "violin": "Violin plot",
    "bar_median": "Median bars (interquartile range)",
    "strip": "Strip plot (every point)",
    "histogram_overlay": "Overlaid histograms",
    "density_by_group": "Density curves by group",
    "scatter": "Scatter plot",
    "density_heatmap": "2D histogram",
    "scatter_trend": "Scatter plot + trend line",
    "grouped_bar": "Grouped bars (counts)",
    "stacked_bar_100": "100 % stacked bars",
    "count_heatmap": "Count heatmap",
    "line": "Line",
    "line_rolling": "Line + rolling mean",
    "area": "Area",
    "stacked_area_100": "100 % stacked areas",
    "stacked_bar_period": "Stacked bars by period",
    "box_by_class": "Box plots by class",
    "histogram_by_class": "Overlaid histograms by class",
    "rate_by_bin": "Rate by bin",
}

RENDERERS: dict[str, Renderer] = {}


def render(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    """Draw ``spec`` with the data of ``df`` and return a Plotly figure.

    Raises:
        ValueError: If no renderer exists for ``spec.kind``.
    """
    renderer = RENDERERS.get(spec.kind)
    if renderer is None:
        raise ValueError(
            f"No Plotly renderer for chart kind '{spec.kind}'. "
            f"Known kinds: {', '.join(sorted(RENDERERS))}."
        )
    figure = renderer(spec, df)
    figure.update_layout(title=chart_title(spec))
    return figure


def chart_title(spec: ChartSpec) -> str:
    """Title shown above the chart, with ★ for the recommended one."""
    star = "★ " if spec.is_best else ""
    label = KIND_LABELS.get(spec.kind, spec.kind)
    return f"{star}{label}: {spec.y} by {spec.x}"


def _register(kind: str) -> Callable[[Renderer], Renderer]:
    """Decorator: add a renderer to ``RENDERERS`` under ``kind``."""

    def decorator(function: Renderer) -> Renderer:
        RENDERERS[kind] = function
        return function

    return decorator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _data(spec: ChartSpec, df: pd.DataFrame) -> pd.DataFrame:
    """The two columns of the spec, without missing values (a new DataFrame)."""
    columns = [spec.x] if spec.y is None else [spec.x, spec.y]
    return df[columns].dropna()


def _as_labels(series: "pd.Series[Any]") -> "pd.Series[Any]":
    """Values as text, so that Plotly draws them as categories (1, 2, 3 -> "1"...)."""
    return series.astype(str)


def _order(series: "pd.Series[Any]") -> list[str]:
    """Category order: natural order of the values (1st, 2nd, 3rd class...)."""
    return [str(value) for value in sorted(series.unique())]


def _by_group(
    spec: ChartSpec, df: pd.DataFrame
) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    """Data with x as text labels, and the natural order of those labels.

    The order must be computed on the original values (1 < 2 < 10) and the
    column passed to Plotly by NAME: Plotly ignores ``category_orders`` for a
    column passed as a Series.
    """
    data = _data(spec, df)
    order = _order(data[spec.x])
    return data.assign(**{spec.x: _as_labels(data[spec.x])}), {spec.x: order}


def _period(dates: "pd.Series[Any]") -> "pd.Series[Any]":
    """Group dates by week, month or year depending on the time span."""
    span_days = (dates.max() - dates.min()).days
    freq = "W" if span_days <= 92 else "M" if span_days <= 3 * 366 else "Y"
    return cast("pd.Series[Any]", dates.dt.to_period(freq).dt.to_timestamp())


def _y(spec: ChartSpec) -> str:
    """The y column (every two-variable chart has one)."""
    if spec.y is None:
        raise ValueError(f"Chart kind '{spec.kind}' needs a y column.")
    return spec.y


# ---------------------------------------------------------------------------
# Category x numeric: compare and distribution
# ---------------------------------------------------------------------------


@_register("box")
def _box(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    data, order = _by_group(spec, df)
    return px.box(data, x=spec.x, y=_y(spec), category_orders=order)


@_register("violin")
def _violin(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    data, order = _by_group(spec, df)
    return px.violin(data, x=spec.x, y=_y(spec), box=True, category_orders=order)


@_register("bar_median")
def _bar_median(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    data = _data(spec, df)
    by_group = data.groupby(spec.x, sort=True)[_y(spec)]
    q1, median, q3 = by_group.quantile(0.25), by_group.median(), by_group.quantile(0.75)
    return go.Figure(
        go.Bar(
            x=[str(value) for value in median.index],
            y=median,
            # error bars from the 1st to the 3rd quartile (no random resampling)
            error_y={
                "type": "data",
                "symmetric": False,
                "array": q3 - median,
                "arrayminus": median - q1,
            },
        )
    ).update_layout(xaxis_title=spec.x, yaxis_title=f"median {spec.y}")


@_register("strip")
def _strip(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    data, order = _by_group(spec, df)
    return px.strip(data, x=spec.x, y=_y(spec), category_orders=order)


@_register("histogram_overlay")
def _histogram_overlay(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    data = _data(spec, df)
    return px.histogram(
        data,
        x=_y(spec),
        color=_as_labels(data[spec.x]),
        barmode="overlay",
        opacity=0.6,
        category_orders={"color": _order(data[spec.x])},
    ).update_layout(legend_title=spec.x)


@_register("density_by_group")
def _density_by_group(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    data = _data(spec, df)
    y = _y(spec)
    grid = np.linspace(data[y].min(), data[y].max(), 200)
    figure = go.Figure()
    for value in sorted(data[spec.x].unique()):
        sample = data.loc[data[spec.x] == value, y].to_numpy(dtype=float)
        density = _gaussian_kde(sample, grid)
        if density is not None:
            figure.add_trace(
                go.Scatter(x=grid, y=density, mode="lines", name=str(value))
            )
    return figure.update_layout(
        xaxis_title=y, yaxis_title="density", legend_title=spec.x
    )


def _gaussian_kde(sample: np.ndarray, grid: np.ndarray) -> np.ndarray | None:
    """Gaussian kernel density estimate (Scott's rule), without scipy.

    Each observation contributes a small bell curve; the density is their
    average. Returns ``None`` when the sample is too small or constant.
    """
    if len(sample) < 2 or np.std(sample) == 0:
        return None
    bandwidth = np.std(sample, ddof=1) * len(sample) ** (-1 / 5)
    z = (grid[:, None] - sample[None, :]) / bandwidth
    result: np.ndarray = np.exp(-0.5 * z**2).mean(axis=1) / (
        bandwidth * np.sqrt(2 * np.pi)
    )
    return result


# ---------------------------------------------------------------------------
# Numeric x numeric: relationship
# ---------------------------------------------------------------------------


@_register("scatter")
def _scatter(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    return px.scatter(_data(spec, df), x=spec.x, y=_y(spec))


@_register("density_heatmap")
def _density_heatmap(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    return px.density_heatmap(
        _data(spec, df), x=spec.x, y=_y(spec), nbinsx=30, nbinsy=30
    )


@_register("scatter_trend")
def _scatter_trend(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    data = _data(spec, df)
    y = _y(spec)
    figure = px.scatter(data, x=spec.x, y=y, opacity=0.6)
    if data[spec.x].nunique() >= 2:
        slope, intercept = np.polyfit(data[spec.x], data[y], deg=1)  # least squares
        line_x = np.array([data[spec.x].min(), data[spec.x].max()])
        figure.add_trace(
            go.Scatter(
                x=line_x, y=slope * line_x + intercept, mode="lines", name="trend"
            )
        )
    return figure


# ---------------------------------------------------------------------------
# Category x category: compare and composition
# ---------------------------------------------------------------------------


def _counts(spec: ChartSpec, df: pd.DataFrame) -> pd.DataFrame:
    """Number of rows for each (x, y) pair, as a long table."""
    data = _data(spec, df)
    y = _y(spec)
    counts = data.groupby([spec.x, y]).size().reset_index(name="count")
    counts[spec.x] = _as_labels(counts[spec.x])
    counts[y] = _as_labels(counts[y])
    return counts


@_register("grouped_bar")
def _grouped_bar(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    return px.bar(
        _counts(spec, df), x=spec.x, y="count", color=_y(spec), barmode="group"
    )


@_register("stacked_bar_100")
def _stacked_bar_100(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    counts = _counts(spec, df)
    counts["percent"] = (
        100 * counts["count"] / counts.groupby(spec.x)["count"].transform("sum")
    )
    return px.bar(counts, x=spec.x, y="percent", color=_y(spec), barmode="stack")


@_register("count_heatmap")
def _count_heatmap(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    data = _data(spec, df)
    table = pd.crosstab(_as_labels(data[_y(spec)]), _as_labels(data[spec.x]))
    return go.Figure(
        go.Heatmap(
            z=table.to_numpy(),
            x=list(table.columns),
            y=list(table.index),
            text=table.to_numpy(),
            texttemplate="%{text}",
            colorscale="Blues",
        )
    ).update_layout(xaxis_title=spec.x, yaxis_title=spec.y)


# ---------------------------------------------------------------------------
# Date x numeric: trend
# ---------------------------------------------------------------------------


def _daily(spec: ChartSpec, df: pd.DataFrame) -> pd.DataFrame:
    """Mean of y for each date (groupby sorts the dates)."""
    data = _data(spec, df)
    return data.groupby(spec.x)[_y(spec)].mean().reset_index()


@_register("line")
def _line(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    return px.line(_daily(spec, df), x=spec.x, y=_y(spec))


@_register("line_rolling")
def _line_rolling(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    data = _daily(spec, df)
    y = _y(spec)
    figure = px.line(data, x=spec.x, y=y)
    rolling = data[y].rolling(window=7, min_periods=1).mean()
    figure.add_trace(
        go.Scatter(x=data[spec.x], y=rolling, mode="lines", name="7-point mean")
    )
    return figure


@_register("area")
def _area(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    return px.area(_daily(spec, df), x=spec.x, y=_y(spec))


# ---------------------------------------------------------------------------
# Date x category: composition
# ---------------------------------------------------------------------------


def _counts_by_period(spec: ChartSpec, df: pd.DataFrame) -> pd.DataFrame:
    data = _data(spec, df)
    y = _y(spec)
    periods = data.assign(period=_period(data[spec.x]))
    counts = periods.groupby(["period", y]).size().reset_index(name="count")
    counts[y] = _as_labels(counts[y])
    return counts


@_register("stacked_area_100")
def _stacked_area_100(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    return px.area(
        _counts_by_period(spec, df),
        x="period",
        y="count",
        color=_y(spec),
        groupnorm="percent",
    ).update_xaxes(title=spec.x)


@_register("stacked_bar_period")
def _stacked_bar_period(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    return px.bar(
        _counts_by_period(spec, df),
        x="period",
        y="count",
        color=_y(spec),
        barmode="stack",
    ).update_xaxes(title=spec.x)


# ---------------------------------------------------------------------------
# Numeric x boolean: compare
# ---------------------------------------------------------------------------


@_register("box_by_class")
def _box_by_class(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    data = _data(spec, df)
    return px.box(data, x=spec.x, y=_as_labels(data[_y(spec)])).update_yaxes(
        title=spec.y
    )


@_register("histogram_by_class")
def _histogram_by_class(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    data = _data(spec, df)
    return px.histogram(
        data, x=spec.x, color=_as_labels(data[_y(spec)]), barmode="overlay", opacity=0.6
    ).update_layout(legend_title=spec.y)


@_register("rate_by_bin")
def _rate_by_bin(spec: ChartSpec, df: pd.DataFrame) -> go.Figure:
    data = _data(spec, df)
    y = _y(spec)
    bins = pd.qcut(data[spec.x], q=5, duplicates="drop")
    rate = data[y].astype(float).groupby(bins, observed=True).mean() * 100
    return go.Figure(
        go.Bar(x=[str(interval) for interval in rate.index], y=rate)
    ).update_layout(
        xaxis_title=f"{spec.x} (5 bins of equal size)",
        yaxis_title=f"% {spec.y}",
        yaxis_range=[0, 100],
    )
