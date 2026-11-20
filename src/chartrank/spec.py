"""ChartSpec: neutral, engine-independent description of a chart.

A ChartSpec says *what* to draw (which kind of chart, which columns, which
transformations), never *how* to draw it. The Plotly renderer and the code
generator both read the same ChartSpec, which guarantees that the exported
code reproduces the chart the user saw.
"""

import dataclasses
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ChartSpec:
    """Description of one proposed chart.

    Attributes:
        kind: Chart kind, e.g. ``"box"``, ``"violin"``, ``"scatter"``.
        x: Column on the x axis.
        y: Column on the y axis, or ``None`` for a one-variable chart.
        intent: What the chart shows: ``"compare"``, ``"distribution"``...
        transforms: Changes applied by the guard rules, e.g. ``("log_y",)``.
        title: Chart title (filled in later).
        rank: Position in the gallery; 1 is the recommended chart (★),
            0 means "not ranked yet".

    Example:
        >>> spec = ChartSpec(kind="box", x="Pclass", y="Fare", intent="compare")
        >>> spec.with_rank(1).is_best
        True
    """

    kind: str
    x: str
    y: str | None
    intent: str
    transforms: tuple[Any, ...] = ()
    title: str = ""
    rank: int = 0

    @property
    def is_best(self) -> bool:
        """True for the recommended chart (★)."""
        return self.rank == 1

    def with_rank(self, rank: int) -> "ChartSpec":
        """Return a copy of this spec with another rank (the spec is frozen)."""
        return dataclasses.replace(self, rank=rank)
