# Contributing to ChartRank

Thanks for your interest! ChartRank is in early development (v1.0 planned for
December 2026); a full guide, including how to add a chart to the catalog, will
come with the documentation.

## Development setup

```bash
git clone https://github.com/Adeshinan/chartrank.git
cd chartrank
pip install -e ".[dev]"
```

## Before opening a pull request

```bash
ruff check .
ruff format --check .
mypy src/chartrank
pytest
```

## Documentation

The documentation lives in `docs/en` and `docs/fr` (one Markdown file per page,
same file names in both languages). Preview it locally with:

```bash
mkdocs serve
```

then open <http://127.0.0.1:8000>. Check it before a pull request with
`mkdocs build --strict`.

## Conventions

- One change per branch: `feat/…`, `fix/…`, `docs/…`, `test/…`, `chore/…`.
- [Conventional commits](https://www.conventionalcommits.org/):
  `feat(profile): detect boolean columns`.
- Update `CHANGELOG.md` in every pull request.
- Code, names, docstrings and error messages in English.
- ChartRank never modifies the user's DataFrame, never uses the network and
  never says "cause" in an explanation.
