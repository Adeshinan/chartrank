"""Column profiling: semantic types and indicators.

For each column, ``profile()`` reports its semantic type (what the column
*means*: an identifier, a yes/no, a category...) next to its pandas dtype (how
it is *stored*), and a few indicators used later to pick and explain charts.
"""

from collections.abc import Mapping
from typing import Any, cast

import numpy as np
import pandas as pd

#: Semantic types that ``detect_type`` can return.
SEMANTIC_TYPES = (
    "id",
    "boolean",
    "date",
    "ordinal",
    "discrete",
    "continuous",
    "category",
    "high_cardinality",
    "text",
    "empty",
    "constant",
)

#: Detection thresholds (EF-04). Change them with ``detect_type(..., thresholds=)``.
THRESHOLDS: dict[str, float] = {
    # Labels with more distinct values than this are "high_cardinality".
    "category_max_distinct": 20,
    # Integers with more distinct values than this behave like "continuous".
    "discrete_max_distinct": 20,
    # A column needs at least this many values to be called an "id".
    "id_min_rows": 20,
    # Text whose values are this long on average (in characters) is "text".
    "text_min_mean_length": 20,
}


def detect_type(
    series: "pd.Series[Any]", thresholds: Mapping[str, float] | None = None
) -> str:
    """Guess the semantic type of one column.

    Missing values are ignored: only the non-missing values are examined.

    Args:
        series: The column to examine. It is never modified.
        thresholds: Detection thresholds; defaults to ``THRESHOLDS``.

    Returns:
        One of ``SEMANTIC_TYPES``:

        - ``empty``: no non-missing value at all;
        - ``constant``: a single distinct value;
        - ``boolean``: bool dtype, or exactly the two values 0 and 1;
        - ``date``: datetime dtype;
        - ``ordinal``: ordered pandas Categorical;
        - ``text``: strings whose mean length reaches ``text_min_mean_length``;
        - ``id``: every value different, with at least ``id_min_rows`` values
          (integers or strings);
        - ``discrete``: integers with at most ``discrete_max_distinct`` values;
        - ``continuous``: other numbers;
        - ``category``: labels with at most ``category_max_distinct`` values;
        - ``high_cardinality``: labels with more values than that.
    """
    t = THRESHOLDS if thresholds is None else thresholds
    values = series.dropna()
    n_values = len(values)
    n_distinct = values.nunique()
    all_different = n_distinct == n_values and n_values >= t["id_min_rows"]

    # 1. Nothing to look at, or nothing that varies: no chart makes sense.
    if n_values == 0:
        return "empty"
    if n_distinct == 1:
        return "constant"

    # 2. Types that the dtype states explicitly.
    #    bool is tested before numbers: for numpy, True is the number 1.
    if pd.api.types.is_bool_dtype(values):
        return "boolean"
    if pd.api.types.is_datetime64_any_dtype(values):
        return "date"
    if isinstance(values.dtype, pd.CategoricalDtype) and values.dtype.ordered:
        return "ordinal"

    # 3. Numbers.
    if pd.api.types.is_numeric_dtype(values):
        # Exactly 0 and 1 is a yes/no, even when stored as float because of
        # missing values ({0.0, 1.0} == {0, 1} in Python).
        if set(values.unique()) == {0, 1}:
            return "boolean"
        # Integers stored as float (because of missing values) still count.
        integral = pd.api.types.is_integer_dtype(values) or bool(
            (values % 1 == 0).all()
        )
        if integral and all_different:
            return "id"
        if integral and n_distinct <= t["discrete_max_distinct"]:
            return "discrete"
        return "continuous"

    # 4. Labels (strings, unordered categoricals...).
    #    Long text is tested before "id": names are all different but are text.
    if values.astype(str).str.len().mean() >= t["text_min_mean_length"]:
        return "text"
    if all_different:
        return "id"
    if n_distinct <= t["category_max_distinct"]:
        return "category"
    return "high_cardinality"


def profile(df: pd.DataFrame) -> pd.DataFrame:
    """Describe each column of ``df``.

    Args:
        df: The data to describe. It is never modified.

    Returns:
        One row per column (same order as ``df``), with:

        - ``type``: the semantic type (see ``detect_type``);
        - ``dtype``: the pandas dtype, as text (e.g. ``"float64"``);
        - ``missing``: share of missing values, between 0 and 1;
        - ``distinct``: number of distinct non-missing values;
        - ``skew``: asymmetry of numeric columns (NaN for the others).
          Above 2, the distribution is strongly stretched to one side and
          its mean is misleading.

    Raises:
        TypeError: If ``df`` is not a pandas DataFrame.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            f"profile() expects a pandas DataFrame, got {type(df).__name__}. "
            "Convert your data first, e.g. pd.DataFrame(data) or pd.read_csv(path)."
        )

    n_rows = len(df)
    rows = {}
    for column in df.columns:
        series = df[column]
        semantic_type = detect_type(series)
        rows[column] = {
            "type": semantic_type,
            "dtype": str(series.dtype),
            "missing": series.isna().sum() / n_rows if n_rows else 0.0,
            "distinct": series.nunique(dropna=True),
            "skew": (
                float(cast(float, series.skew()))
                if semantic_type in ("continuous", "discrete")
                else np.nan
            ),
        }
    return pd.DataFrame.from_dict(
        rows,
        orient="index",
        columns=["type", "dtype", "missing", "distinct", "skew"],
    )
