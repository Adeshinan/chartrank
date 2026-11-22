"""Golden pairs: compare ChartRank's ★ with the charts humans choose.

Usage (from the project root):

    python tests/golden/golden.py booklet   # write tests/golden/validation.html
    python tests/golden/golden.py report    # agreement between ★ and testers
    python tests/golden/golden.py fill      # write the majority choice in pairs.yaml

The testers see each pair's charts without the ★, in a shuffled order and
labelled A, B, C... They answer with letters in ``answers.csv``.
"""

import csv
import html
import random
import string
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

import chartrank as cr
from chartrank.render.plotly import render

GOLDEN_DIR = Path(__file__).parent
DATA_DIR = GOLDEN_DIR.parent / "data"
PAIRS_FILE = GOLDEN_DIR / "pairs.yaml"
ANSWERS_FILE = GOLDEN_DIR / "answers.csv"
BOOKLET_FILE = GOLDEN_DIR / "validation.html"


def load_pairs() -> list[dict[str, Any]]:
    """The 30 reference pairs of pairs.yaml."""
    with PAIRS_FILE.open(encoding="utf-8") as file:
        pairs: list[dict[str, Any]] = yaml.safe_load(file)
    return pairs


def load_data(name: str) -> pd.DataFrame:
    """A dataset of tests/data/, with date columns parsed."""
    df = pd.read_csv(DATA_DIR / name)
    if "day" in df.columns and name == "sales.csv":
        df["day"] = pd.to_datetime(df["day"])
    return df


def shuffled_kinds(pair: dict[str, Any]) -> dict[str, str]:
    """Letter -> chart kind, in the order shown to testers.

    The order is shuffled to avoid order bias (people tend to pick the first
    chart), but with a fixed seed per pair: every tester sees the same order,
    and the key can be recomputed at any time.
    """
    gallery = cr.suggest(load_data(pair["data"]), pair["x"], pair["y"], pair["intent"])
    kinds = [chart.spec.kind for chart in gallery]
    random.Random(f"chartrank-golden-{pair['id']}").shuffle(kinds)
    return dict(zip(string.ascii_uppercase, kinds, strict=False))


def star_kind(pair: dict[str, Any]) -> str:
    """The chart kind ChartRank recommends (★) for this pair."""
    data = load_data(pair["data"])
    return cr.suggest(data, pair["x"], pair["y"], pair["intent"]).best.spec.kind


# ---------------------------------------------------------------------------
# Answers and agreement
# ---------------------------------------------------------------------------


def load_answers() -> dict[str, list[str]]:
    """Pair id -> letters chosen by the testers (empty cells ignored)."""
    if not ANSWERS_FILE.exists():
        return {}
    with ANSWERS_FILE.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    return {
        row["pair"]: [
            value.strip().upper()
            for key, value in row.items()
            if key != "pair" and value and value.strip()
        ]
        for row in rows
    }


def majority(letters: list[str]) -> list[str]:
    """The most chosen letters (several in case of a tie), sorted."""
    if not letters:
        return []
    counts = Counter(letters)
    top = max(counts.values())
    return sorted(letter for letter, count in counts.items() if count == top)


@dataclass(frozen=True)
class PairResult:
    """Outcome of one pair: what ChartRank and the testers chose."""

    pair_id: str
    star: str
    human: tuple[str, ...]  # most chosen kinds (several if tied)
    n_answers: int
    n_options: int

    @property
    def agrees(self) -> bool:
        return self.star in self.human


def results() -> list[PairResult]:
    """One result per pair that has at least one answer."""
    answers = load_answers()
    out = []
    for pair in load_pairs():
        letters = answers.get(pair["id"], [])
        if not letters:
            continue
        key = shuffled_kinds(pair)
        unknown = sorted(set(letters) - set(key))
        if unknown:
            raise ValueError(
                f"Pair '{pair['id']}': answer(s) {unknown} do not match any chart "
                f"(possible letters: {', '.join(key)}). Fix answers.csv."
            )
        human = tuple(key[letter] for letter in majority(letters))
        out.append(
            PairResult(pair["id"], star_kind(pair), human, len(letters), len(key))
        )
    return out


def report(rows: list[PairResult]) -> str:
    """Agreement rate, chance level and list of disagreements."""
    if not rows:
        return "★ agreement: no answer yet (fill tests/golden/answers.csv)."
    agree = sum(row.agrees for row in rows)
    chance = sum(1 / row.n_options for row in rows) / len(rows)
    lines = [
        f"★ agreement: {agree}/{len(rows)} ({agree / len(rows):.0%})"
        f" — chance level {chance:.0%}",
    ]
    ties = [row for row in rows if len(row.human) > 1]
    if ties:
        lines.append(
            f"  ({len(ties)} tie(s): agreement if ★ is among the tied choices)"
        )
    disagreements = [row for row in rows if not row.agrees]
    if disagreements:
        lines.append("Disagreements:")
        lines += [
            f"  - {row.pair_id}: ★ {row.star}, humans {' / '.join(row.human)}"
            f" ({row.n_answers} answers)"
            for row in disagreements
        ]
    return "\n".join(lines)


def fill_pairs_file(rows: list[PairResult]) -> None:
    """Write the majority choice of the testers in pairs.yaml (human_star)."""
    by_id = {row.pair_id: " / ".join(row.human) for row in rows}
    text = PAIRS_FILE.read_text(encoding="utf-8")
    out, current = [], None
    for line in text.splitlines():
        if line.startswith("- id: "):
            current = line.removeprefix("- id: ").strip()
        if line.strip().startswith("human_star:") and current in by_id:
            line = f"  human_star: {by_id[current]}"
        out.append(line)
    PAIRS_FILE.write_text("\n".join(out) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Booklet for the testers
# ---------------------------------------------------------------------------

_INTENTS_FR = {
    "compare": "comparer les groupes",
    "distribution": "voir la répartition des valeurs",
    "relationship": "voir le lien entre deux nombres",
    "composition": "voir de quoi chaque groupe est composé",
    "trend": "voir l'évolution dans le temps",
}


def write_booklet() -> Path:
    """Write validation.html: one section per pair, charts shuffled, no ★."""
    from plotly.offline import get_plotlyjs

    sections = []
    for number, pair in enumerate(load_pairs(), start=1):
        data = load_data(pair["data"])
        gallery = cr.suggest(data, pair["x"], pair["y"], pair["intent"])
        specs = {chart.spec.kind: chart.spec for chart in gallery}
        cells = []
        for letter, kind in shuffled_kinds(pair).items():
            figure = render(specs[kind].with_rank(0), data)  # rank 0: no ★
            figure.update_layout(title=letter, height=340, margin={"t": 40})
            chart_html = figure.to_html(full_html=False, include_plotlyjs=False)
            cells.append(f'<div class="cell">{chart_html}</div>')
        goal = _INTENTS_FR[pair["intent"]]
        dataset = html.escape(pair["data"].removesuffix(".csv"))
        sections.append(
            f"<section><h2>Paire {number} · {dataset}</h2>"
            f"<p><b>{html.escape(pair['y'])}</b> et <b>{html.escape(pair['x'])}</b> — "
            f"but : <i>{goal}</i> ({pair['intent']}).</p>"
            f'<div class="grid">{"".join(cells)}</div></section>'
        )

    page = f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<title>ChartRank · test des graphiques</title>
<script>{get_plotlyjs()}</script>
<style>
 body {{ font-family: sans-serif; max-width: 1200px; margin: auto; padding: 16px; }}
 .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
 .cell {{ border: 1px solid #ddd; border-radius: 8px; }}
 section {{ border-top: 2px solid #333; margin-top: 32px; }}
</style></head><body>
<h1>Quel graphique choisiriez-vous ?</h1>
<p>Pour chacune des {len(sections)} paires, plusieurs graphiques montrent les mêmes
données. <b>Choisissez celui que vous utiliseriez</b> pour le but indiqué, et notez
sa lettre. Il n'y a pas de bonne réponse : c'est votre avis qui compte.</p>
<p>Renvoyez vos réponses sous la forme : <code>1:B, 2:A, 3:C, …</code></p>
<p><i>For each pair, pick the chart you would use for the stated goal and send back
its letter, e.g. <code>1:B, 2:A, 3:C</code>.</i></p>
{"".join(sections)}
</body></html>"""
    BOOKLET_FILE.write_text(page, encoding="utf-8")
    return BOOKLET_FILE


def main(argv: list[str]) -> None:
    # Windows consoles may use a legacy encoding (cp1252) that cannot print ★.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    command = argv[1] if len(argv) > 1 else "report"
    if command == "booklet":
        path = write_booklet()
        print(f"written {path} ({path.stat().st_size / 1e6:.1f} MB)")
    elif command == "fill":
        rows = results()
        fill_pairs_file(rows)
        print(f"human_star written for {len(rows)} pairs in {PAIRS_FILE}")
    elif command == "report":
        print(report(results()))
    else:
        raise SystemExit(f"Unknown command '{command}'. Use: booklet, report or fill.")


if __name__ == "__main__":
    main(sys.argv)
