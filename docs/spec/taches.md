# ChartRank — Tâches (miroir du tableau Trello « ChartRank v1.0 »)

Une tâche = une branche = une PR. Cocher la case quand la PR est fusionnée.
Chaque tâche indique le **mode** de travail conseillé (guide, binôme ou rapide) et les **notions à apprendre**.

Pour chaque tâche : *Objectif* → *Ce qu'on attend* → *Comment tester* → *Fini quand*.
Les exigences EF-xx / ENF-xx sont dans `docs/spec/cahier_des_charges.md`.

---

## Phase 0 · Mise en place (14–15 nov.)

### [ ] 0.1 · Créer le dépôt et la structure du paquet — 14 nov.
- **Branche** : premier commit sur `main`, puis `chore/setup` · **Mode** : rapide, avec explication de chaque fichier
- **Notions** : layout `src/`, `pyproject.toml` (build backend, dépendances, extras), installation éditable (`pip install -e`), environnement virtuel.
- **Attendu** : `pyproject.toml` (nom `chartrank`, MIT, Python ≥ 3.11, build backend hatchling, deps pandas/numpy/plotly/pyyaml, extras `[static]` = kaleido, `[dev]` = pytest, pytest-cov, ruff, mypy, mkdocs-material) ; modules vides avec docstring : `profile.py`, `dictionary.py`, `catalog.py`, `guards.py`, `recommend.py`, `spec.py`, `target.py`, `gallery.py`, `codegen.py`, `cli.py`, `render/plotly.py` ; `tests/`, `docs/en`, `docs/fr`, `examples/`, `README.md`, `README.fr.md`, `LICENSE`, `CHANGELOG.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`.
- **Tester** : `pip install -e ".[dev]"` puis `python -c "import chartrank; print(chartrank.__version__)"` → `0.1.0`.
- **Fini quand** : installable dans un environnement neuf.

### [ ] 0.2 · CI GitHub Actions — 14 nov.
- **Branche** : `chore/ci` · **Mode** : rapide, puis me faire lire le workflow ligne par ligne
- **Notions** : GitHub Actions (workflow, job, matrice), ruff, mypy, couverture, test sans réseau (`pytest-socket`).
- **Attendu** : `ci.yml` sur push/PR : `ruff check`, `ruff format --check`, `mypy src/chartrank`, `pytest --cov=chartrank --cov-fail-under=85` sur Python 3.11–3.14, tests avec `--disable-socket`.
- **Tester** : une PR avec un fichier mal formaté doit échouer, puis passer une fois corrigée.
- **Fini quand** : badge CI vert dans le README.

### [ ] 0.3 · Squelette de la documentation EN/FR et du README — 15 nov.
- **Branche** : `docs/skeleton` · **Mode** : rapide
- **Notions** : MkDocs Material, i18n, GitHub Pages.
- **Attendu** : pages vides *Getting started, Intents, Chart catalog, Guard rules, Target analysis, API reference, FAQ* (EN + FR) ; README avec phrase d'accroche, badges, « Work in progress — v1.0 planned for December 2026 » ; `CONTRIBUTING.md` ; modèles d'issues (bug, proposition de graphique).
- **Tester** : `mkdocs build --strict`.
- **Fini quand** : le site est en ligne (même vide).

### [ ] 0.4 · Réserver le nom : publier `chartrank 0.1.0` — 15 nov.
- **Branche** : `chore/release-workflow`, puis tag `v0.1.0` (c'est moi qui pousse le tag) · **Mode** : binôme
- **Notions** : build d'un paquet (`python -m build`), PyPI, Trusted Publishing, SemVer, CHANGELOG.
- **Attendu** : `release.yml` déclenché par un tag `v*` ; `cr.profile(df)` minimal (dtype, manquants, distincts) ; description PyPI « Early preview, not ready for use ».
- **Tester** : environnement neuf, `pip install chartrank==0.1.0`, appel de `cr.profile`.
- **Fini quand** : la page PyPI existe.

---

## Phase 1 · Prototype + décision (16–20 nov.)

### [ ] 1.1 · Profileur v0 : types sémantiques — 16 nov.
- **Branche** : `feat/profiler` · **Mode** : guide · **Exigences** : EF-02, EF-03, EF-06
- **Notions** : types sémantiques vs dtypes pandas, asymétrie (*skewness*), cardinalité, tests paramétrés pytest.
- **Attendu** : types `continuous`, `discrete`, `category`, `high_cardinality`, `ordinal`, `boolean`, `date`, `id`, `text`, avec seuils dans `THRESHOLDS`. Sur Titanic : PassengerId=id, Survived=boolean, Pclass=discrete, Sex=category, Age=continuous (19,9 % manquants), Fare=continuous (skew ≈ 4,79), Cabin=high_cardinality (77,1 % manquants).
- **Tester** : un DataFrame par type ; colonne vide / constante / 100 % manquante ; DataFrame inchangé (ENF-03).
- **Fini quand** : le profil Titanic sort comme ci-dessus.

### [ ] 1.2 · `ChartSpec` + catalogue v0 (2 variables) — 17 nov.
- **Branche** : `feat/chartspec-catalog` · **Mode** : guide · **Exigences** : EF-21 à EF-23, EF-50
- **Notions** : `dataclass(frozen=True)`, objets immuables et hashables, table déclarative (données plutôt que `if/else`).
- **Attendu** : `ChartSpec(kind, x, y, intent, transforms=(), title="", rank=0)` ; `CATALOG[(type_x, type_y, intent)] = [kinds…]` pour les 7 lignes de la section 6.2 ; `recommend(df, x, y, intent)` → liste ordonnée, le premier `rank=1`.
- **Tester** : chaque ligne du catalogue ; `trend` sans date → `ValueError` listant les intentions possibles (EF-25).
- **Fini quand** : `recommend(titanic, "Pclass", "Fare", "compare")` → box ★, violin, bar_median, strip.

### [ ] 1.3 · Rendu Plotly brut + `suggest().show()` — 18 nov.
- **Branche** : `feat/plotly-prototype` · **Mode** : binôme · **Exigences** : EF-51, EF-52
- **Notions** : `plotly.express` vs `graph_objects`, `make_subplots`, affichage dans un notebook.
- **Attendu** : une fonction par `kind` (`ChartSpec` + df → `go.Figure`) ; objet galerie avec `.show()`, `.best`, `g[i]`, `len(g)`.
- **Tester** : chaque `kind` construit une figure avec au moins une trace ; `examples/prototype.ipynb` sur Titanic + Iris/penguins.
- **Fini quand** : le notebook montre au moins 10 paires.

### [ ] 1.4 · 30 paires de référence + test humain — 19 nov.
- **Branche** : `test/golden-pairs` · **Mode** : binôme (le test humain, c'est moi)
- **Notions** : tests « golden » (de référence), évaluation par des humains, biais d'ordre (montrer les propositions dans le désordre).
- **Attendu** : `tests/golden/pairs.yaml` (30 paires sur 4–5 petits jeux, toutes intentions, champ `human_star`) ; test à 3–5 personnes sans afficher la ★ ; `test_golden.py` qui affiche le taux d'accord.
- **Fini quand** : taux d'accord connu, désaccords notés.

### [ ] 1.5 · Décision go / ajuster / réduire — 20 nov.
- **Branche** : `docs/decision-v1` · **Mode** : discussion
- **Règle** : ≥ 60 % et retours positifs → go ; 40–60 % → ajuster l'ordre du catalogue puis go ; < 40 % → réduire (galerie sans ★) ou repenser.
- **Fini quand** : `docs/decisions/2026-11-20-go.md` écrit (taux, 3 désaccords, citations, décision).

---

## Phase 2 · Cœur (21–29 nov.)

### [ ] 2.1 · Profil complet — 21–22 nov.
- **Branche** : `feat/profile-full` · **Mode** : guide · **Exigences** : EF-01 à EF-06
- **Notions** : lecture CSV/Excel/Parquet, règle 1,5 × IQR pour les valeurs extrêmes, `difflib.get_close_matches`, mesure de performance.
- **Attendu** : entrées DataFrame ou chemin ; indicateurs (manquants, distincts, asymétrie, extrêmes, catégorie dominante) ; `thresholds=` ; `types=` avec erreur claire ; objet `Profile` avec `.to_frame()`.
- **Tester** : chiffres stockés en texte, dates européennes, « Oui/Non » ; colonne mal orthographiée → suggestion ; 100 000 lignes < 1 s.

### [ ] 2.2 · Dictionnaire de données — 23 nov.
- **Branche** : `feat/dictionary` · **Mode** : guide · **Exigences** : EF-10 à EF-12
- **Notions** : validation de YAML, ordre de priorité (`types=` > dictionnaire > détection).
- **Attendu** : clés `description`, `unit`, `type`, `order`, `labels`, `role` (`id`, `ignore`) ; YAML ou `dict` ; messages clairs.
- **Tester** : `Pclass` devient ordinal ; colonne absente → suggestion ; dictionnaire vide = aucun changement.

### [ ] 2.3 · Catalogue complet (1 et 2 variables) — 24–25 nov.
- **Branche** : `feat/catalog-full` · **Mode** : guide pour le catalogue, binôme pour les rendus · **Exigences** : EF-20 à EF-25
- **Notions** : ECDF, densité (KDE), treemap, heatmap d'effectifs, aires empilées.
- **Attendu** : `suggest(df, x)` et `suggest(df, x, y)` ; 5 intentions ; sans intention → groupes, max 2 par intention ; un rendu pour chaque `kind`.
- **Tester** : test paramétré sur tout le catalogue ; le test golden tourne toujours.

### [ ] 2.4 · Règles de garde — 26–27 nov.
- **Branche** : `feat/guards` · **Mode** : guide · **Exigences** : EF-30 à EF-35
- **Notions** : pourquoi chaque règle (échelle log, surimpression des points, ordre naturel), ordre d'application des règles.
- **Attendu** : une fonction par règle : `skewed_log` (asym. > 2, valeurs > 0), `top_n` (> 10), `overplotting` (> 5 000 pts → hexbin ★), `small_n` (< 30 → strip), `imbalanced` (groupe < 5 %), `natural_order`, `missing_note`, `forbidden` (3D, double axe, camembert > 5 parts).
- **Tester** : un cas qui déclenche et un qui ne déclenche pas, pour chaque règle ; Titanic Fare par classe → log + boîte ★.
- **Fini quand** : accord golden **≥ 70 %**, test golden rendu **bloquant**.

### [ ] 2.5 · Explications chiffrées — 28–29 nov.
- **Branche** : `feat/explanations` · **Mode** : guide · **Exigences** : EF-40 à EF-44
- **Notions** : gabarits de texte (templates) + chiffres calculés, internationalisation (fichiers `locales/en.yaml`, `fr.yaml`), corrélation ≠ causalité.
- **Attendu** : `.why` (« Bon pour… / À éviter si… » chiffré), `cr.explain(g)`, `lang="fr"`. Titanic : médiane 14,45 £, moyenne 32,20 £.
- **Tester** : chiffres présents ; aucun gabarit ne contient « cause » ; mêmes clés en EN et FR.

---

## Phase 3 · Analyse de la cible (30 nov.–5 déc.)

### [ ] 3.1 · Tâche + mesures de lien — 30 nov.–1er déc.
- **Branche** : `feat/target-measures` · **Mode** : guide · **Exigences** : EF-61, EF-62
- **Notions** : V de Cramér (et correction de biais de Bergsma), rapport de corrélation η, corrélation de Spearman, pourquoi les ramener entre 0 et 1.
- **Attendu** : tâche `binary` / `multiclass` / `regression` (ou `task=`) ; `association(df, x, target)` → (mesure, valeur, n).
- **Tester** : valeurs calculées à la main ; variable aléatoire ≈ 0, copie de la cible = 1 ; Titanic : Sex (V ≈ 0,54) et Pclass au-dessus de Age.

### [ ] 3.2 · `rank(df, target=)` — 2–3 déc.
- **Branche** : `feat/rank-target` · **Mode** : guide · **Exigences** : EF-60, EF-65, EF-66, EF-68
- **Notions** : fuite de données (*data leakage*), différence entre lien avec la cible et importance dans un modèle.
- **Attendu** : `r.task`, `r.scores` (trié), `r.warnings` (id/texte exclus, fuite si force ≥ 0,95), note vers FitRank.
- **Tester** : Titanic → Sex, Pclass en tête ; `leak = Survived * 1` en tête **et** signalé ; cible absente → suggestion ; df inchangé.

### [ ] 3.3 · Graphique ★ par variable + phrase — 4 déc.
- **Branche** : `feat/rank-charts` · **Mode** : binôme · **Exigences** : EF-63, EF-64, EF-66
- **Attendu** : `r.show(top=5)` ; `r["Sex"].why` → « Les femmes survivent à 74 %, les hommes à 19 % » ; `r["Fare"].why` → médiane 26 £ contre 10,5 £ ; `r["Sex"]` = même objet que `g.best`.
- **Tester** : chiffres présents ; `r[0] is r["Sex"]` ; pas de « cause ».

### [ ] 3.4 · `rank(df)` sans cible + 3 jeux de données — 5 déc.
- **Branche** : `feat/rank-no-target` · **Mode** : binôme · **Exigences** : EF-67
- **Attendu** : score d'intérêt (asymétrie, extrêmes, manquants, déséquilibre) avec la raison en clair ; tests sur Titanic (binaire), penguins/Iris (multiclasse), un jeu de régression ; une colonne de fuite ajoutée exprès est signalée dans chaque jeu.

---

## Phase 4 · Rendu, export, code (6–10 déc.)

### [ ] 4.1 · Thème, titres, axes, `show()` final — 6–7 déc.
- **Branche** : `feat/theme` · **Mode** : binôme · **Exigences** : EF-51, EF-52, EF-55, ENF-10
- **Notions** : templates Plotly, palettes accessibles (Okabe-Ito), contraste.
- **Attendu** : template `chartrank`, unités et libellés du dictionnaire, notes des gardes sous le graphique, cartes avec ★ / « bon pour » / « à éviter si » ; Jupyter, VS Code, Colab sans widget ; `cr.set_theme()`.

### [ ] 4.2 · Export `.save()` PNG / SVG / HTML — 8 déc.
- **Branche** : `feat/export` · **Mode** : binôme · **Exigences** : EF-53, ENF-06
- **Attendu** : format selon l'extension ; HTML toujours possible ; kaleido absent → message « pip install chartrank[static] » ; `g.save("gallery.html")`.
- **Tester** : HTML ; PNG/SVG dans un job CI avec l'extra `[static]` ; message sans kaleido (`monkeypatch`).

### [ ] 4.3 · Générateur de code + test de reproduction — 9 déc.
- **Branche** : `feat/codegen` · **Mode** : guide · **Exigences** : EF-54, ENF-07
- **Notions** : génération de code, `exec` dans un espace de noms isolé, comparaison de figures via `to_plotly_json()`.
- **Attendu** : `.code` autonome et commenté (imports, lecture des données, `dropna` avec nombre de lignes retirées, `px.…` avec transformations), généré depuis le `ChartSpec`.
- **Tester** : pour chaque `kind`, exécuter le code et comparer les `data` de la figure. Test **bloquant**.

### [ ] 4.4 · CLI `profile`, `suggest`, `rank` — 10 déc.
- **Branche** : `feat/cli` · **Mode** : binôme
- **Attendu** : commandes de la section 7.3 du cahier, `--dictionary`, `--lang`, `--quiet`, `--version` ; codes de sortie 0 / 1 (données) / 2 (usage).
- **Tester** : `subprocess.run` + `tmp_path`.

---

## Phase 5 · Finition + sortie v1.0 (11–14 déc.)

### [ ] 5.1 · Documentation EN/FR + README + `0.9.0` — 11–12 déc.
- **Branches** : `docs/v1`, tag `v0.9.0` (je pousse) · **Mode** : rapide pour la structure, binôme pour les textes
- **Attendu** : pages de doc complètes, catalogue illustré généré par script, README avec capture et tableau « Why ChartRank? ».
- **Tester** : `mkdocs build --strict` ; les exemples de la doc sont exécutés par un test.

### [ ] 5.2 · Notebook Colab + test par une personne extérieure — 13 déc.
- **Branche** : `docs/colab` · **Mode** : binôme
- **Attendu** : `examples/try_chartrank.ipynb` (< 2 min) : install, profile, suggest (show, why, save, code), rank, section « Vos données » ; testé par 1–2 personnes extérieures.

### [ ] 5.3 · Publication 1.0.0 + annonce — 14 déc.
- **Branche** : `chore/release-1.0.0`, tag `v1.0.0` (je pousse) · **Mode** : binôme
- **Avant** : vérifier tous les critères de la section 12.2 du cahier.
- **Attendu** : CHANGELOG `[1.0.0]`, release GitHub, test en environnement neuf, annonce LinkedIn + r/Python.

---

## v1.1 (15 déc.–4 janv.)
- [ ] **Recettes YAML** `save_recipe()` / `apply()` (avec `reguard=True`) — 22 déc. · `feat/recipes`
- [ ] **`table()`** : tableau résumé → graphique (5 formes de tableaux) — 31 déc. · `feat/table`
- [ ] **Retours utilisateurs + publication 1.1.0** — 4 janv.
- Pour chaque tâche : **la suite v1.0 doit passer sans modification**.

## v1.2 (5 janv.–1er févr.)
- [ ] **Matplotlib** (`backend="matplotlib"`, extra `[matplotlib]`) — 15 janv. · `feat/matplotlib`
- [ ] **3e variable** : `color=`, `facet=` — 22 janv. · `feat/third-variable`
- [ ] **Widget optionnel** `cr.widget(df)` (extra `[widget]`) — 29 janv. · `feat/widget`
- [ ] **Documentation + publication 1.2.0** — 1er févr.
- Plotly reste le moteur par défaut ; sans les nouveaux paramètres, rien ne change.
