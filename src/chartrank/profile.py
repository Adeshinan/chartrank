"""Column profiling: semantic types and indicators.

Version 0.1 is minimal: for each column, its pandas dtype, the share of missing
values and the number of distinct values. Semantic types come in task 1.1.
"""

import pandas as pd


def profile(df: pd.DataFrame) -> pd.DataFrame:
    """Describe each column of ``df``.

    Args:
        df: The data to describe. It is never modified.

    Returns:
        One row per column (same order as ``df``), with:

        - ``dtype``: the pandas dtype, as text (e.g. ``"float64"``);
        - ``missing``: share of missing values, between 0 and 1;
        - ``distinct``: number of distinct non-missing values.

    Raises:
        TypeError: If ``df`` is not a pandas DataFrame.

    Example:
        >>> import pandas as pd
        >>> import chartrank as cr
        >>> cr.profile(pd.DataFrame({"Age": [22.0, None, 38.0, 22.0]}))
               dtype  missing  distinct
        Age  float64     0.25         2
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            f"profile() expects a pandas DataFrame, got {type(df).__name__}. "
            "Convert your data first, e.g. pd.DataFrame(data) or pd.read_csv(path)."
        )

    n_rows = len(df)
    rows = {
        column: {
            "dtype": str(df[column].dtype),
            "missing": df[column].isna().sum() / n_rows if n_rows else 0.0,
            "distinct": df[column].nunique(dropna=True),
        }
        for column in df.columns
    }
    return pd.DataFrame.from_dict(
        rows, orient="index", columns=["dtype", "missing", "distinct"]
    )
