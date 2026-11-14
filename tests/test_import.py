"""Smoke tests: the package can be imported and exposes its version."""

import chartrank


def test_version_is_exposed() -> None:
    assert chartrank.__version__ == "0.1.0"
