# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `profile(df)` now reports the semantic type of each column (`id`, `boolean`,
  `date`, `ordinal`, `discrete`, `continuous`, `category`, `high_cardinality`,
  `text`, `empty`, `constant`) and the skewness of numeric columns.
- `detect_type(series, thresholds=)` and the `THRESHOLDS` dictionary of
  detection thresholds.
- `ChartSpec`: frozen, hashable, engine-independent description of a chart.
- Chart catalog for two variables (7 rows of section 6.2), with plot types
  (`numeric`, `category`, `boolean`, `date`); a discrete column with at most
  10 values is drawn as a category.
- `recommend(df, x, y, intent)`: ranked charts, ★ first; swaps x and y when
  only the reverse order exists; clear errors with suggestions for unknown
  columns or intents, and the list of possible intents (EF-25).

## [0.1.0] - 2026-11-15

Early preview to reserve the name on PyPI. Not ready for use.

### Added

- `profile(df)`: minimal column profile (dtype, share of missing values,
  number of distinct values).
- Package structure (`src/` layout, hatchling build, empty modules).
- Community files: README (EN/FR), license, contributing guide, code of conduct,
  issue templates.
- Continuous integration (GitHub Actions): ruff, mypy, and pytest with coverage
  ≥ 85 % on Python 3.11 to 3.14 (Linux) and 3.11 (Windows, macOS), with
  network access disabled during tests.
- Documentation skeleton (MkDocs Material, English and French) published to
  GitHub Pages; new `[docs]` extra.
- Release workflow: a `v*` tag publishes to PyPI with Trusted Publishing;
  a manual run publishes to TestPyPI.

[Unreleased]: https://github.com/Adeshinan/chartrank/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Adeshinan/chartrank/releases/tag/v0.1.0
