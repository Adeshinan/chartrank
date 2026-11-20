"""Recommender: from two columns and an intent to a ranked list of charts.

Version 1.2 (prototype): catalog only. Guard rules (log scale, top N...) and
explanations ("good for / avoid if") come in tasks 2.4 and 2.5.
"""

import pandas as pd

from chartrank._validation import check_choice, check_dataframe
from chartrank.catalog import INTENTS, candidates, plot_type, possible_intents
from chartrank.profile import detect_type
from chartrank.spec import ChartSpec

#: Plain-English names of the semantic types that can never be drawn.
_NOT_DRAWABLE = {
    "id": "an identifier",
    "text": "free text",
    "empty": "empty (no value)",
    "constant": "constant (a single value)",
}


def recommend(df: pd.DataFrame, x: str, y: str, intent: str) -> list[ChartSpec]:
    """Propose charts for two columns and an intent, the best one first.

    Args:
        df: The data. It is never modified.
        x: First column.
        y: Second column. If the catalog only knows the reverse order
            (e.g. ``x="Fare", y="Pclass"`` for ``compare``), the two columns
            are swapped so that the category is on the x axis.
        intent: One of ``INTENTS``.

    Returns:
        Between 1 and 5 ``ChartSpec``, ranked from 1 (★) onwards.

    Raises:
        TypeError: If ``df`` is not a DataFrame.
        ValueError: Unknown column or intent, column that cannot be drawn,
            or intent impossible for these columns (the message lists the
            possible intents).

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"Pclass": [1, 2, 3, 3], "Fare": [80.0, 21.5, 7.9, 8.1]})
        >>> [spec.kind for spec in recommend(df, "Pclass", "Fare", "compare")]
        ['box', 'violin', 'bar_median', 'strip']
    """  # noqa: E501
    check_dataframe(df, "recommend")
    check_choice(x, df.columns, "column")
    check_choice(y, df.columns, "column")
    check_choice(intent, INTENTS, "intent")
    if x == y:
        raise ValueError(
            f"x and y are both '{x}'. Choose two different columns, "
            "or use a one-variable chart (coming in a later version)."
        )

    type_x = _plot_type_of(df, x)
    type_y = _plot_type_of(df, y)

    kinds = candidates(type_x, type_y, intent)
    if not kinds:
        # The catalog may only know the other order: put the columns back.
        kinds = candidates(type_y, type_x, intent)
        if kinds:
            x, y = y, x
    if not kinds:
        raise ValueError(_impossible_intent_message(x, y, type_x, type_y, intent))

    return [
        ChartSpec(kind=kind, x=x, y=y, intent=intent, rank=rank)
        for rank, kind in enumerate(kinds, start=1)
    ]


def _plot_type_of(df: pd.DataFrame, column: str) -> str:
    """Plot type of one column, or a clear error if it cannot be drawn."""
    series = df[column]
    semantic_type = detect_type(series)
    result = plot_type(semantic_type, series.nunique())
    if result is None:
        raise ValueError(
            f"Column '{column}' is {_NOT_DRAWABLE[semantic_type]} and cannot be "
            "drawn. Choose another column, or force its type in a later version "
            "(types= or a data dictionary)."
        )
    return result


def _impossible_intent_message(
    x: str, y: str, type_x: str, type_y: str, intent: str
) -> str:
    """Error message for EF-25: say which intents would work instead."""
    possible = possible_intents(type_x, type_y) or possible_intents(type_y, type_x)
    start = (
        f"No chart for intent '{intent}' with '{x}' ({type_x}) and '{y}' ({type_y})."
    )
    if possible:
        return f"{start} Possible intents for these columns: {', '.join(possible)}."
    return (
        f"{start} No chart is available for this pair of columns in this version. "
        "Try another pair of columns."
    )
