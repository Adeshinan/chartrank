# ChartRank

[![CI](https://github.com/Adeshinan/chartrank/actions/workflows/ci.yml/badge.svg)](https://github.com/Adeshinan/chartrank/actions/workflows/ci.yml)
[![Docs](https://github.com/Adeshinan/chartrank/actions/workflows/docs.yml/badge.svg)](https://adeshinan.github.io/chartrank/)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

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

[Documentation](https://adeshinan.github.io/chartrank/) ·
[Version française](README.fr.md) · License: [MIT](LICENSE)
