"""Input checks shared by the public functions.

Every error says what is wrong *and* what to do (ENF-09), with a suggestion
when the user probably made a typo.
"""

import difflib
from collections.abc import Iterable

import pandas as pd


def check_dataframe(df: object, function: str) -> None:
    """Raise TypeError if ``df`` is not a pandas DataFrame."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            f"{function}() expects a pandas DataFrame, got {type(df).__name__}. "
            "Convert your data first, e.g. pd.DataFrame(data) or pd.read_csv(path)."
        )


def check_choice(value: str, choices: Iterable[str], what: str) -> None:
    """Raise ValueError if ``value`` is not one of ``choices``.

    Example:
        >>> check_choice("comapre", ["compare", "trend"], "intent")
        Traceback (most recent call last):
        ...
        ValueError: Unknown intent 'comapre'. Did you mean 'compare'? Possible values: compare, trend.
    """  # noqa: E501
    options = [str(choice) for choice in choices]
    if value in options:
        return
    message = f"Unknown {what} '{value}'."
    close = difflib.get_close_matches(str(value), options, n=1)
    if close:
        message += f" Did you mean '{close[0]}'?"
    message += f" Possible values: {', '.join(options)}."
    raise ValueError(message)
