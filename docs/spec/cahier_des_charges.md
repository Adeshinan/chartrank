# ChartRank — Cahier des charges v1

11 nov. 2026 · Faïd Adéshinan ALAGBE

ChartRank est une librairie Python open source qui, à partir de variables choisies et d'une intention, propose plusieurs graphiques dessinés sur les données de l'utilisateur, explique chacun avec ses propres chiffres et fournit l'image ou le code pour le refaire ; le développement commence le 14 nov. 2026.

## 1. Contexte et objectifs

ChartRank répond à un problème très courant : **« je sais ce que je veux montrer, mais je ne sais pas quel graphique utiliser »**. On essaie plusieurs graphiques, on demande à une IA, ou l'on reste sur un diagramme en barres par habitude.

Le sondage LinkedIn de novembre (6 votes, donc indicatif) va dans ce sens : 2 répondants sur 3 font plusieurs essais ou demandent à une IA. Les commentaires ont fait ressortir l'idée clé du projet : le bon graphique dépend d'abord de **l'intention** (comparer, montrer une répartition, une évolution, une relation).

Objectifs de la v1 :

1. **Proposer** 3 à 5 graphiques adaptés à une ou deux variables et à une intention, dessinés sur les vraies données de l'utilisateur, avec une recommandation ★.
2. **Expliquer** chaque proposition par « bon pour / à éviter si », calculé sur les données (par exemple : la moyenne trompe quand la distribution est très étirée).
3. **Montrer le comportement des variables face à une cible** : classer les variables selon leur lien avec la target, avec pour chacune le bon graphique et une phrase chiffrée.
4. **Rendre utilisable** le graphique choisi : objet modifiable, image, ou code Python autonome et commenté.
5. **Garantir la fiabilité** : règles de bonnes pratiques explicites, résultats reproductibles, tout en local.
6. **Rester dans la famille FitRank** : même philosophie (explicite, reproductible, léger), mêmes conventions, même qualité de code et de documentation.

## 2. Positionnement

L'idée de proposer des graphiques n'est pas nouvelle ; ChartRank se positionne comme **le successeur maintenu et pédagogique de Lux**, avec des explications calculées sur les données, un code exporté autonome et des résultats reproductibles, sans dépendre d'une IA ni d'un widget.

| Outil | Ce qu'il fait | État (novembre 2026) | Ce que ChartRank fait autrement |
| --- | --- | --- | --- |
| Excel « Graphiques recommandés », Tableau « Show Me » | propose des graphiques pour les données sélectionnées | intégrés à ces logiciels | en Python, avec l'intention, des explications chiffrées et le code |
| Lux | recommande des graphiques dans le notebook et exporte leur code | abandonné (dernière version en 2022) | maintenu ; sans widget obligatoire ; « bon pour / à éviter si » ; recettes réutilisables |
| ydata-profiling, Sweetviz | rapport HTML automatique de tout le jeu de données | actifs | un choix ciblé et expliqué, pas un rapport figé ; de vrais objets modifiables |
| PyGWalker, D-Tale | interfaces à la souris dans le notebook | actifs | l'outil recommande et justifie, au lieu de laisser tout choisir |
| Data Formulator, LIDA (Microsoft) | graphiques générés avec un LLM | Data Formulator actif, LIDA à l'arrêt | déterministe et local : mêmes données, mêmes graphiques, rien n'est envoyé |
| Draco (université de Washington) | encode les bonnes pratiques de dataviz en contraintes | peu actif | source d'inspiration pour les règles |

Les publics pour lesquels ChartRank a le plus de valeur : les personnes qui codent en Python sans être spécialistes de dataviz, celles qui ne peuvent pas envoyer leurs données à une IA, et celles qui refont les mêmes graphiques régulièrement.

## 3. Périmètre par version

La v1.0 couvre les deux usages du projet : la galerie expliquée pour une ou deux variables (`suggest()`) et l'analyse des variables face à une cible (`rank()`), avec Plotly. Les recettes et les tableaux arrivent en v1.1 ; Matplotlib, 3 variables et le widget en v1.2.

| Élément | v1.0 (14 déc. 2026) | v1.1 (4 janv. 2027) | v1.2 (1er févr. 2027) | Plus tard |
| --- | --- | --- | --- | --- |
| Profilage des colonnes (types sémantiques, indicateurs) | ✅ |  |  |  |
| `suggest()` pour 1 ou 2 variables, avec intention | ✅ |  |  |  |
| Recommandation ★ et « bon pour / à éviter si » calculés | ✅ |  |  |  |
| Règles de garde (log, top N, hexbin, ordre naturel…) | ✅ |  |  |  |
| Rendu Plotly, export PNG / SVG / HTML | ✅ |  |  |  |
| Export du code Python autonome et commenté (Plotly) | ✅ |  |  |  |
| Dictionnaire de données optionnel (unités, ordre, libellés, rôle) | ✅ |  |  |  |
| `rank(df, target=)` : classer les variables selon leur lien avec la cible | ✅ |  |  |  |
| Graphique ★ de chaque variable face à la cible, phrase chiffrée, alerte de fuite | ✅ |  |  |  |
| `rank(df)` sans cible : variables les plus intéressantes à regarder | ✅ |  |  |  |
| Recettes YAML (`save_recipe`, `apply`) |  | ✅ |  |  |
| `table()` : tableau résumé → graphique |  | ✅ |  |  |
| Rendu et code Matplotlib |  |  | ✅ |  |
| 3 variables (couleur, petits multiples) |  |  | ✅ |  |
| Boutons dans le notebook (widget optionnel) |  |  | ✅ |  |
| Pont avec FitRank (graphiques de diagnostic des modèles) |  |  |  | ✅ |
| Explications rédigées par un LLM, en option et désactivées par défaut |  |  |  | ✅ |

**Hors périmètre** : cartes géographiques, texte libre (nuages de mots), images, tableaux de bord, données imbriquées, calcul distribué (Spark, Dask), interfaces à la souris (déjà bien couvertes par PyGWalker et D-Tale).

**Principes non négociables**, dans toutes les versions :

- ChartRank **ne modifie jamais les données** de l'utilisateur : il signale (valeurs manquantes, points exclus), il ne corrige pas en silence.
- Il **ne propose jamais de graphique trompeur** : pas de camembert à 15 parts, pas d'effet 3D, pas d'axe tronqué sur des barres.
- **Rien n'est envoyé** sur le réseau.

## 4. Utilisateurs et parcours

Le parcours tient en trois temps, **voir, choisir, utiliser** ; chaque profil s'arrête à l'étape dont il a besoin (une image pour un rapport, le code pour apprendre, une recette pour un rapport mensuel).

| Profil | Besoin | Ce qu'il utilise |
| --- | --- | --- |
| Étudiant·e en data | choisir le bon graphique et comprendre pourquoi | galerie, explications, code exporté |
| Analyste junior | un graphique fiable pour un rapport, rapidement | galerie, export PNG / SVG |
| Data scientist | explorer avant de modéliser, souvent autour d'une target | galerie, puis `rank()` |
| Personne soumise à la confidentialité (banque, santé, public) | ne pas envoyer ses données à une IA | tout, en local |
| Équipe qui refait un rapport chaque mois | le même graphique sur de nouvelles données | recettes YAML en v1.1 |

**Le parcours, étape par étape**

1. **Voir** : l'utilisateur appelle `cr.suggest(df, "Pclass", "Fare", intent="compare")`. ChartRank affiche une grille de 3 à 5 graphiques, chacun avec son titre, « bon pour », « à éviter si » et l'étiquette ★ sur la recommandation.
2. **Choisir** : il prend une proposition par son numéro, `g[2]`, ou la recommandation, `g.best`.
3. **Utiliser** : selon son besoin, il récupère l'objet modifiable (`.figure`), une image (`.save("x.png")`) ou le code autonome (`.code`).

Sans intention, la galerie regroupe les propositions par intention (« pour comparer », « pour voir la répartition »…) : l'outil apprend aussi à l'utilisateur à se poser la question.

## 5. Exigences fonctionnelles (v1.0)

Chaque exigence porte un identifiant (EF-xx) pour être reliée aux tickets et aux tests. Priorité : **M** = obligatoire en v1.0, **S** = souhaitable en v1.0.

### 5.1 Données et profilage

| ID | Exigence | Priorité |
| --- | --- | --- |
| EF-01 | Accepter un DataFrame pandas, ou un fichier CSV, Excel ou Parquet (comme FitRank). | M |
| EF-02 | Déterminer le type sémantique de chaque colonne : numérique continu, numérique discret, catégorie, catégorie très variée, ordinal, booléen, date, identifiant, texte libre. | M |
| EF-03 | Calculer pour chaque colonne : valeurs distinctes, part de manquants, asymétrie, valeurs extrêmes, catégorie dominante. | M |
| EF-04 | Seuils de détection configurables (par exemple 20 valeurs distinctes pour une catégorie). | S |
| EF-05 | Forcer un type quand la détection se trompe : `types={"Pclass": "ordinal"}`. | M |
| EF-06 | `cr.profile(df)` renvoie le tableau des types et indicateurs, lisible et exportable. | M |

### 5.2 Dictionnaire de données (optionnel)

| ID | Exigence | Priorité |
| --- | --- | --- |
| EF-10 | Lire un dictionnaire YAML ou un `dict` : description, unité, rôle (`id`, `ignore`), type, ordre, libellés. | S |
| EF-11 | Le dictionnaire prime sur la détection automatique ; une colonne inconnue du dictionnaire donne une erreur claire, avec suggestion (« Cabn → Cabin ? »). | S |
| EF-12 | Unités et libellés utilisés dans les titres, axes et explications (« Prix du billet (£) », « Oui / Non » au lieu de « 1 / 0 »). | S |

### 5.3 Intentions et recommandation

| ID | Exigence | Priorité |
| --- | --- | --- |
| EF-20 | Intentions acceptées : `distribution`, `compare`, `relationship`, `composition`, `trend`. | M |
| EF-21 | `suggest(df, x)` (une variable) et `suggest(df, x, y)` (deux variables), avec `intent` optionnel. | M |
| EF-22 | Seules les propositions valides pour les types et l'intention sont générées (catalogue de la section 6) ; jamais de proposition « pour remplir ». | M |
| EF-23 | Entre 1 et 5 propositions, ordonnées ; la première est marquée ★ recommandée. | M |
| EF-24 | Sans intention : propositions regroupées par intention, au plus 2 par intention. | M |
| EF-25 | Combinaison impossible (par exemple `trend` sans colonne de date) : erreur claire qui liste les intentions possibles pour ces variables. | M |

### 5.4 Règles de garde

| ID | Exigence | Priorité |
| --- | --- | --- |
| EF-30 | Distribution très étirée (asymétrie au-delà d'un seuil, valeurs positives) → échelle logarithmique, indiquée dans le titre. | M |
| EF-31 | Trop de catégories → les N plus fréquentes + « Autres » (N = 10 par défaut). | M |
| EF-32 | Trop de points pour un nuage (au-delà de 5 000 par défaut) → transparence, hexbin ou densité. | M |
| EF-33 | Catégories ordonnées selon leur ordre naturel (jours, mois, ordinal déclaré), sinon par fréquence. | M |
| EF-34 | Valeurs manquantes et points exclus toujours comptés et indiqués sous le graphique. | M |
| EF-35 | Barres toujours avec un axe qui part de zéro ; aucun camembert au-delà de 5 parts ; aucun effet 3D. | M |

### 5.5 Explications

| ID | Exigence | Priorité |
| --- | --- | --- |
| EF-40 | Chaque proposition porte un « bon pour » et, quand c'est pertinent, un « à éviter si ». | M |
| EF-41 | Les explications sont **calculées sur les données** : par exemple « la moyenne trompe : médiane 14 £, moyenne 32 £ ». | M |
| EF-42 | `explain()` ou `.why` donne la raison du choix ★ en une ou deux phrases chiffrées. | M |
| EF-43 | Les explications ne disent jamais « cause » : une relation est « associée à ». | M |
| EF-44 | Explications en anglais par défaut, en français avec `lang="fr"`. | S |

### 5.6 Rendu et export

| ID | Exigence | Priorité |
| --- | --- | --- |
| EF-50 | Chaque proposition est décrite par un `ChartSpec` neutre, indépendant du moteur de rendu. | M |
| EF-51 | Rendu Plotly : `.figure` renvoie un vrai objet Plotly, modifiable. | M |
| EF-52 | `g.show()` affiche la grille dans un notebook (Jupyter, VS Code, Colab), sans widget. | M |
| EF-53 | `.save()` exporte en PNG, SVG ou HTML selon l'extension. | M |
| EF-54 | `.code` renvoie un code Python **autonome** (sans ChartRank), commenté, qui reproduit exactement le graphique. | M |
| EF-55 | Thème commun cohérent (couleurs, polices), surchargeable. | S |

### 5.7 Analyse face à la cible

| ID | Exigence | Priorité |
| --- | --- | --- |
| EF-60 | `cr.rank(df, target="Survived")` classe toutes les variables selon la force de leur lien avec la cible. | M |
| EF-61 | Type de tâche détecté (classification binaire, multiclasse, régression) ou forcé avec `task=`, avec le même vocabulaire que FitRank. | M |
| EF-62 | Mesure adaptée aux types, ramenée entre 0 et 1 : Spearman (numérique × numérique), rapport de corrélation η (catégorie × numérique), V de Cramér (catégorie × catégorie). La mesure utilisée est affichée. | M |
| EF-63 | Pour chaque variable, un graphique ★ variable × cible choisi par le même recommandeur que `suggest()` (par exemple taux de survie par classe, boîtes du prix par survie). | M |
| EF-64 | Une phrase chiffrée par variable : « les femmes survivent à 74 %, les hommes à 19 % ». Jamais « cause » (EF-43). | M |
| EF-65 | Alerte de fuite probable quand le lien est presque parfait (seuil 0,95 par défaut) ; identifiants et texte libre exclus et listés. | M |
| EF-66 | `r.scores` renvoie le tableau du classement (pandas) ; `r.show(top=5)` affiche la grille ; `r["Sex"]` renvoie le même objet graphique que `suggest()` (`.figure`, `.save()`, `.code`, `.why`). | M |
| EF-67 | `cr.rank(df)` sans cible : variables classées par intérêt visuel (asymétrie, valeurs extrêmes, manquants, déséquilibre), chacune avec son graphique ★. | S |
| EF-68 | Rappel dans la sortie : un lien avec la cible n'est pas l'importance dans un modèle ; pour comparer des modèles, renvoi vers FitRank. | S |

## 6. Catalogue des graphiques et règles

Le catalogue v1.0 est volontairement court : une dizaine de types bien faits plutôt que trente approximatifs. Chaque ligne donne les candidats dans l'ordre par défaut ; le premier reçoit ★, sauf si une règle de garde en décide autrement.

**Du type détecté au type « de dessin »** (décision du 16 nov. 2026). Le profileur décrit ce qu'il voit ; le catalogue décide comment dessiner :

- un numérique **discret avec ≤ 10 valeurs distinctes** (ex. `Pclass`, `SibSp`) se dessine comme une **catégorie** ; au-delà, comme un **numérique** ;
- **ordinal** et **booléen** se dessinent comme une **catégorie** dans le tableau 6.2 (l'ordinal garde son ordre naturel) ;
- **continu** se dessine comme un **numérique** ;
- le type peut toujours être forcé, par ordre de priorité : `types=` > dictionnaire de données > détection automatique.

### 6.1 Une variable

| Type de variable | Intention | Candidats (★ en premier) |
| --- | --- | --- |
| Numérique | distribution | ★ histogramme · boîte à moustaches · violon · courbe de densité · ECDF |
| Catégorie (≤ 10 valeurs) | distribution / composition | ★ barres triées · barres empilées 100 % · camembert (≤ 5 parts seulement) |
| Catégorie (> 10 valeurs) | distribution | ★ barres horizontales top 10 + « Autres » · treemap |
| Ordinal | distribution | ★ barres dans l'ordre naturel · barres cumulées |
| Booléen | composition | ★ barre unique 100 % · deux barres |
| Date | trend | ★ courbe des effectifs par période · barres par période |

### 6.2 Deux variables

| x | y | Intention | Candidats (★ en premier) |
| --- | --- | --- | --- |
| Catégorie | Numérique | compare | ★ boîtes à moustaches · violons · barres de médiane avec intervalle · points superposés (strip) |
| Catégorie | Numérique | distribution | ★ histogrammes superposés · courbes de densité par groupe |
| Numérique | Numérique | relationship | ★ nuage de points · hexbin (gros volumes) · nuage + droite de tendance |
| Catégorie | Catégorie | compare / composition | ★ barres groupées · barres empilées 100 % · carte de chaleur des effectifs |
| Date | Numérique | trend | ★ courbe · courbe + moyenne glissante · aire (si cumul) |
| Date | Catégorie | composition | ★ aires empilées 100 % · barres empilées par période |
| Numérique | Booléen | compare | ★ boîtes par classe · histogrammes superposés · taux par tranche |

### 6.3 Règles de garde (appliquées avant le choix ★)

| Situation détectée | Seuil par défaut | Action |
| --- | --- | --- |
| Distribution très étirée | asymétrie > 2 et valeurs > 0 | Échelle log, indiquée dans le titre ; la boîte passe devant l'histogramme en `compare`. |
| Trop de catégories | > 10 | Top 10 + « Autres », comptés en légende. |
| Trop de points | > 5 000 | Hexbin ou densité devient ★ ; le nuage simple reste proposé avec transparence. |
| Groupes très déséquilibrés | un groupe < 5 % | Avertissement dans « à éviter si » ; effectifs affichés sous chaque groupe. |
| Petits effectifs | < 30 lignes | Points individuels (strip) devant boîte et violon. |
| Valeurs manquantes | > 0 | Nombre exclu affiché sous le graphique. |
| Identifiant ou texte libre | type détecté | Colonne refusée avec message clair. |
| Camembert | > 5 parts | Jamais proposé. |

### 6.4 Ce qui n'est jamais proposé

Effets 3D, doubles axes Y, axes de barres qui ne partent pas de zéro, couleurs arc-en-ciel sur des catégories, camemberts de plus de 5 parts. Ces choix sont fixés, pas configurables en v1.0.

## 7. Interface (API et CLI)

### 7.1 API Python v1.0

```python
import chartrank as cr
import pandas as pd

df = pd.read_csv("titanic.csv")

# 1. Voir comment ChartRank comprend les colonnes
cr.profile(df)                           # tableau : colonne, type, manquants, distincts, asymétrie
cr.profile(df, types={"Pclass": "ordinal"})   # corriger un type

# 2. Demander des propositions
g = cr.suggest(df, x="Pclass", y="Fare", intent="compare")
g.show()                                 # grille de 3 à 5 graphiques, ★ en premier

# 3. Choisir
chart = g.best                           # la recommandation ★
chart = g[2]                             # ou une autre proposition
print(chart.why)                         # « bon pour… / à éviter si… », chiffré
cr.explain(g)                            # pourquoi ★ plutôt que les autres

# 4. Utiliser
chart.figure                             # objet Plotly modifiable
chart.save("fare_by_class.png")          # .png, .svg ou .html
print(chart.code)                        # code Python autonome, sans ChartRank

# Avec un dictionnaire de données (optionnel)
g = cr.suggest(df, x="Pclass", y="Fare", dictionary="titanic_dict.yaml", lang="fr")
```

Exemple de dictionnaire :

```yaml
columns:
  Fare:   {description: "Prix du billet", unit: "£"}
  Pclass: {type: ordinal, order: [1, 2, 3], labels: {1: "1re", 2: "2e", 3: "3e"}}
  PassengerId: {role: id}
```

Analyse face à la cible (v1.0) :

```python
r = cr.rank(df, target="Survived")       # tâche détectée : classification binaire
r.scores                                 # tableau : variable, mesure, force (0 à 1), phrase
r.show(top=5)                            # graphique ★ des 5 variables les plus liées à la cible
print(r["Sex"].why)                      # « les femmes survivent à 74 %, les hommes à 19 % »
r["Sex"].save("sex_vs_survived.png")     # même objet graphique que suggest()
r.warnings                               # fuites probables, colonnes exclues

cr.rank(df)                              # sans cible : variables les plus intéressantes à regarder
```

### 7.2 Ajouts prévus en v1.1 et v1.2 (sans casser la v1.0)

```python
# v1.1
chart.save_recipe("fare.yaml")           # garder un choix
cr.apply("fare.yaml", new_df)            # le rejouer sur d'autres données
cr.table(summary_df)                     # transformer un tableau résumé en graphique adapté

# v1.2
cr.suggest(df, x="Pclass", y="Fare", backend="matplotlib")   # même galerie, rendu Matplotlib
cr.suggest(df, x="Age", y="Fare", color="Sex")                # 3e variable en couleur ou petits multiples
cr.widget(df)                                                 # boutons dans le notebook (optionnel)
```

### 7.3 Ligne de commande minimale

```bash
chartrank profile titanic.csv
chartrank suggest titanic.csv --x Pclass --y Fare --intent compare --out charts/
# écrit chart_1.html … chart_5.html, chart_1.py … et un index.html avec la ★
chartrank rank titanic.csv --target Survived --top 5 --out rank/
# écrit scores.csv, un graphique par variable et un index.html
```

Les noms publics (`profile`, `suggest`, `rank`, `explain`, `.best`, `.scores`, `.figure`, `.save`, `.code`, `.why`) sont figés à partir de la v1.0 : toute évolution se fait par ajout.

## 8. Architecture

Un seul `ChartSpec` produit à la fois le graphique et son code :

```
 Données (DataFrame/fichier)   Dictionnaire (optionnel)   Variables + intention
            │                           │                          │
            └─────────────┬─────────────┘                          │
                          ▼                                        │
                     Profileur                                     │
      (types sémantiques, manquants, asymétrie, cardinalité)       │
                          │                                        │
                          ▼                                        ▼
                Recommandeur (règles déterministes)
      catalogue type × intention → candidats valides seulement
      règles de garde → échelle log, top 10 + Autres, hexbin, ordre naturel
      classement, ★ et explications « bon pour / à éviter si » chiffrées
                          │
                          ▼
            ChartSpec × 3 à 5, ★ en premier
       (description neutre, indépendante du moteur)
               │                         │
               ▼                         ▼
         Rendu Plotly              Générateur de code
  .figure · .show() · .save()   .code : script Python autonome,
  Matplotlib en v1.2            sans ChartRank, identique à la figure
```

Le graphique et le code viennent du même `ChartSpec` : c'est ce qui garantit que le code exporté reproduit exactement ce que l'utilisateur a vu, et qui permettra d'ajouter Matplotlib en v1.2 sans toucher au recommandeur.

| Module | Rôle | Fichier prévu |
| --- | --- | --- |
| `profile` | Types sémantiques et indicateurs par colonne ; applique le dictionnaire et `types=`. | `chartrank/profile.py` |
| `dictionary` | Lecture et validation du YAML de dictionnaire. | `chartrank/dictionary.py` |
| `catalog` | Table déclarative type × intention → candidats (section 6). | `chartrank/catalog.py` |
| `guards` | Règles de garde, chacune une fonction testée séparément. | `chartrank/guards.py` |
| `recommend` | Assemble candidats + gardes, classe, choisit ★, rédige les explications. | `chartrank/recommend.py` |
| `spec` | Classe `ChartSpec` (dataclass gelée, sérialisable en YAML pour les recettes v1.1). | `chartrank/spec.py` |
| `render/plotly` | `ChartSpec` → figure Plotly + thème commun. | `chartrank/render/plotly.py` |
| `codegen` | `ChartSpec` → script Python autonome et commenté. | `chartrank/codegen.py` |
| `gallery` | Objet renvoyé par `suggest()` : `.show()`, `.best`, `g[i]`, affichage notebook. | `chartrank/gallery.py` |
| `cli` | Commandes `profile`, `suggest` et `rank`. | `chartrank/cli.py` |

Aucun appel réseau, aucun modèle d'IA : toutes les décisions sont des règles lisibles dans `catalog.py` et `guards.py`, donc testables et explicables.

`rank()` réutilise les mêmes briques : le profileur donne les types, un module `chartrank/target.py` calcule le lien de chaque variable avec la cible, puis le recommandeur choisit le graphique ★ variable × cible. Il n'y a donc qu'un seul catalogue et un seul jeu de règles de garde à maintenir.

## 9. Exigences non fonctionnelles

| ID | Exigence | Cible |
| --- | --- | --- |
| ENF-01 | **Compatibilité** : SemVer strict ; toute nouveauté est un ajout optionnel ; un nom public n'est retiré qu'après une version d'avertissement (`DeprecationWarning`). Même règle d'or que FitRank. | 100 % des tests de la version précédente passent |
| ENF-02 | **Déterminisme** : mêmes données + mêmes paramètres = mêmes propositions, même ★, mêmes explications. | aucun tirage aléatoire non fixé |
| ENF-03 | **Données intactes** : ChartRank ne modifie jamais le DataFrame reçu. | test dédié |
| ENF-04 | **Performance** : `suggest()` sur 100 000 lignes en moins de 2 s (hors export d'image). Au-delà, échantillonnage annoncé dans la sortie. | mesuré en CI |
| ENF-05 | **Local** : aucun appel réseau, aucune télémétrie. | test sans réseau |
| ENF-06 | **Python** 3.11 à 3.14 ; dépendances : pandas, numpy, plotly, pyyaml. Export PNG/SVG via `kaleido` en dépendance optionnelle (`pip install chartrank[static]`). | matrice CI |
| ENF-07 | **Tests** : couverture ≥ 85 % ; tests « golden » sur les 30 paires du plan de validation, avec accord ★ / choix humain ≥ 70 % ; test que `chart.code` exécuté seul produit la même figure (comparaison du JSON Plotly). | bloquant en CI |
| ENF-08 | **Qualité** : `ruff`, `mypy` (types publics complets), CI GitHub Actions sur chaque PR. | bloquant |
| ENF-09 | **Messages** : toute erreur dit ce qui ne va pas et quoi faire (colonne inconnue, type impossible, intention impossible). | revue des messages |
| ENF-10 | **Accessibilité** : palette lisible par les daltoniens, contraste suffisant, texte alternatif dans l'export HTML. | vérifié sur le thème |

## 10. Open source et documentation

- **Licence** MIT, dépôt GitHub `Adeshinan/chartrank`, paquet PyPI `chartrank`.
- **Réserver le nom** sur PyPI dès le week-end du 14–15 nov. avec une version `0.1.0`, pour éviter qu'il soit pris.
- **Conventions identiques à FitRank** : branches `feat/…`, `fix/…`, `docs/…` ; commits conventionnels ; `CHANGELOG.md` ; tags `vX.Y.Z` ; publication PyPI par GitHub Actions.
- **Documentation** MkDocs Material, EN et FR, publiée sur GitHub Pages : démarrage en 5 minutes, guide des intentions, catalogue illustré (une image par ligne de la section 6), règles de garde expliquées, analyse de la cible, référence de l'API, FAQ.
- **README** en anglais, avec lien vers la version française : une capture de la grille ★, un exemple de 5 lignes, et un tableau « Why ChartRank? » face à Lux, ydata-profiling, Sweetviz et un assistant IA.
- **Notebook Colab** « Try ChartRank » sur Titanic, comme pour FitRank.
- **Fichiers communautaires** : `CONTRIBUTING.md` (comment ajouter un type au catalogue), `CODE_OF_CONDUCT.md`, modèles d'issues (bug, proposition de graphique).

## 11. Planning

FitRank est terminé le **15 novembre**. La mise en place de ChartRank se fait le **week-end du 14–15 novembre**, et le développement commence le **lundi 16 novembre**, avec environ **4 h par jour entièrement pour ChartRank**, en parallèle de la revue de littérature du projet de recherche.

| Phase | Dates | Contenu | Fini quand |
| --- | --- | --- | --- |
| 0. Mise en place | 14 → 15 nov. (week-end) | Dépôt GitHub, `pyproject.toml`, structure des modules (section 8), CI (ruff, mypy, tests Python 3.11–3.14), squelette MkDocs EN/FR, modèles d'issues ; publication de `chartrank 0.1.0` pour réserver le nom. | CI verte, `pip install chartrank` fonctionne |
| 1. Prototype + validation | 16 → 19 nov. | Profileur, catalogue pour 2 variables, rendu Plotly brut ; test sur les 30 paires du plan de validation, montré à 3–5 personnes. | ★ d'accord avec le choix humain sur au moins 60 % des paires |
| Décision | 20 nov. | Go, ajuster le catalogue, ou réduire le périmètre. | décision écrite dans le dépôt |
| 2. Cœur | 21 → 29 nov. | EF-01 à EF-44 : profil complet, dictionnaire, intentions, gardes, ★, explications chiffrées. | tests golden ≥ 70 % |
| 3. Analyse de la cible | 30 nov. → 5 déc. | EF-60 à EF-68 : `rank()` avec et sans cible, mesures de lien, graphique ★ par variable, phrases chiffrées, alerte de fuite. | Titanic : sexe et classe en tête, fuite détectée |
| 4. Rendu, export, code | 6 → 10 déc. | EF-50 à EF-55 : thème, `.show()`, `.save()`, `.code` + test de reproduction ; CLI `profile`, `suggest`, `rank`. | le code exporté reproduit la figure |
| 5. Finition | 11 → 13 déc. | Docs EN/FR, README, notebook Colab, relecture des messages ; `0.9.0` en pré-version le 11 déc. | critères de la section 12.2 vérifiés |
| **Sortie v1.0** | **14 déc.** | `chartrank 1.0.0` sur PyPI, annonce LinkedIn + r/Python. | publié |
| v1.1 | 15 déc. → 1er janv. | Recettes YAML (`save_recipe`, `apply`), `table()`, retours des premiers utilisateurs. | tests v1.0 toujours verts |
| **Sortie v1.1** | **4 janv. 2027** | `chartrank 1.1.0`. | publié |
| v1.2 | 5 → 29 janv. | Rendu et code Matplotlib depuis le même `ChartSpec`, 3e variable (couleur, petits multiples), widget optionnel. | mêmes tests golden avec les deux moteurs |
| **Sortie v1.2** | **1er févr. 2027** | `chartrank 1.2.0`. | publié |

**Points d'attention.** La finition (3 jours) est la phase la plus serrée : si elle déborde, la v1.0 glisse de quelques jours plutôt que de réduire les tests. Les vacances de fin d'année tombent pendant la v1.1, d'où la sortie le 4 janvier.

## 12. Risques, critères d'acceptation et questions ouvertes

### 12.1 Risques

| Risque | Probabilité | Impact | Réponse |
| --- | --- | --- | --- |
| Un assistant IA fait « assez bien » la même chose | haute | moyen | Miser sur ce qu'il ne garantit pas : déterministe, local, explications chiffrées, code identique à la figure, règles lisibles. |
| Le ★ ne convainc pas | moyenne | haut | Porte de décision du 20 nov. ; tests golden ; chaque règle justifiée dans la doc. |
| Explications génériques ou fausses | moyenne | haut | Toujours partir d'un chiffre calculé ; jamais de « cause » ; relecture sur 30 paires. |
| `kaleido` (export PNG/SVG) instable selon la plateforme | moyenne | moyen | Dépendance optionnelle ; l'export HTML reste toujours disponible ; message clair si absent. |
| Maintenir deux moteurs (Plotly puis Matplotlib) | moyenne | moyen | Un seul `ChartSpec` ; Matplotlib seulement en v1.2. |
| Charge de travail (recherche + ChartRank) | haute | haut | FitRank terminé avant le début ; périmètre v1.0 figé ; si une phase déborde, la sortie glisse de quelques jours plutôt que de réduire les tests ; le reste passe en v1.1. |
| Confusion avec Lux, ydata-profiling, Sweetviz | moyenne | faible | Tableau « Why ChartRank? » dans le README. |

### 12.2 Critères d'acceptation de la v1.0

- [ ] Toutes les exigences **M** de la section 5 sont implémentées et testées.
- [ ] Le ★ est d'accord avec le choix humain sur au moins 70 % des 30 paires de référence.
- [ ] Pour chaque proposition, `chart.code` exécuté seul reproduit la figure.
- [ ] Aucun graphique interdit (section 6.4) ne peut être produit.
- [ ] `rank()` testé sur 3 jeux de données (Titanic en classification binaire, un jeu multiclasse, un jeu de régression) : les variables connues pour être liées à la cible sont en tête (sur Titanic : sexe et classe) et une colonne de fuite ajoutée exprès est signalée.
- [ ] CI verte sur Python 3.11 à 3.14, couverture ≥ 85 %, `ruff` et `mypy` propres.
- [ ] Documentation EN et FR en ligne, README avec capture et comparaison, notebook Colab qui s'exécute.
- [ ] Exemple Titanic du README (`suggest` et `rank`) exécuté de bout en bout par une personne extérieure au projet.

### 12.3 Questions ouvertes

1. **Export d'image** : garder PNG/SVG en v1.0 (avec `kaleido` optionnel) ou ne livrer que l'HTML en v1.0 ?
2. **Langue des explications** : anglais par défaut et français en option (proposé), ou les deux dès la v1.0 ?
3. **Mesure du lien avec la cible** : les mesures simples de EF-62 (proposé, faciles à expliquer) ou l'information mutuelle (une seule mesure pour tous les types, plus difficile à expliquer) ?
4. **Nom** : réserver `chartrank` sur PyPI dès le week-end du 14–15 nov., avant toute annonce (proposé) ?
