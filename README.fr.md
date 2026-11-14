# ChartRank

[![CI](https://github.com/Adeshinan/chartrank/actions/workflows/ci.yml/badge.svg)](https://github.com/Adeshinan/chartrank/actions/workflows/ci.yml)
[![Docs](https://github.com/Adeshinan/chartrank/actions/workflows/docs.yml/badge.svg)](https://adeshinan.github.io/chartrank/fr/)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)
[![Licence : MIT](https://img.shields.io/badge/licence-MIT-green)](LICENSE)

**Propose et explique le bon graphique selon vos données et votre intention.**

> 🚧 En cours de développement — v1.0 prévue en décembre 2026.

Donnez à ChartRank une ou deux colonnes et une intention (`compare`,
`distribution`, `relationship`, `composition`, `trend`). Il propose 3 à 5
graphiques dessinés sur vos données, marque la recommandation ★, explique chacun
avec des chiffres calculés sur vos données (« bon pour / à éviter si ») et fournit
l'image ou un script Python autonome pour le refaire. Déterministe, local, sans IA.

```python
import chartrank as cr

g = cr.suggest(df, x="Pclass", y="Fare", intent="compare")
g.show()
print(g.best.why)
print(g.best.code)
```

*Cette API est l'objectif de la v1.0 et n'est pas encore disponible.*

[Documentation](https://adeshinan.github.io/chartrank/fr/) ·
[English version](README.md) · Licence : [MIT](LICENSE)
