"""Fixtures shared by every test file (pytest loads this file automatically)."""

from pathlib import Path

import pandas as pd
import pytest

DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def titanic() -> pd.DataFrame:
    """The Kaggle Titanic training set (891 passengers, 12 columns)."""
    return pd.read_csv(DATA_DIR / "titanic.csv")
