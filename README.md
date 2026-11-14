# ChartRank

[![CI](https://github.com/Adeshinan/chartrank/actions/workflows/ci.yml/badge.svg)](https://github.com/Adeshinan/chartrank/actions/workflows/ci.yml)

**Suggests and explains the right chart for your data and intent.**

> 🚧 Work in progress — v1.0 planned for December 2026.

Give ChartRank one or two columns and an intent (`compare`, `distribution`,
`relationship`, `composition`, `trend`). It proposes 3 to 5 charts drawn on your
own data, marks the recommended one with ★, explains each with numbers computed
from your data ("good for / avoid if"), and gives you the image or a standalone
Python script to reproduce it. Deterministic, local, no AI.

```python
import chartrank as cr

g = cr.suggest(df, x="Pclass", y="Fare", intent="compare")
g.show()
print(g.best.why)
print(g.best.code)
```

*This API is the v1.0 target and is not available yet.*

[Version française](README.fr.md) · License: [MIT](LICENSE)
