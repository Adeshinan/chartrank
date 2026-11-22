"""Golden pairs (task 1.4): the 30 reference cases and the ★ agreement.

The validity tests are blocking. The agreement is only printed for now
(run ``pytest tests/golden -s``); it becomes blocking at 70 % in phase 2.
"""

import string

import golden
import pytest


@pytest.fixture(scope="module")
def pairs() -> list[dict[str, object]]:
    return golden.load_pairs()


def test_there_are_30_pairs_with_unique_ids(pairs: list[dict[str, object]]) -> None:
    ids = [pair["id"] for pair in pairs]
    assert len(ids) == 30
    assert len(set(ids)) == 30


def test_every_intent_is_covered(pairs: list[dict[str, object]]) -> None:
    assert {pair["intent"] for pair in pairs} == {
        "compare",
        "distribution",
        "relationship",
        "composition",
        "trend",
    }


@pytest.mark.parametrize("pair", golden.load_pairs(), ids=lambda pair: pair["id"])
def test_every_pair_offers_a_real_choice(pair: dict[str, object]) -> None:
    key = golden.shuffled_kinds(pair)
    assert 2 <= len(key) <= 5
    assert list(key) == list(string.ascii_uppercase[: len(key)])
    assert golden.star_kind(pair) in key.values()


def test_shuffle_is_the_same_every_time(pairs: list[dict[str, object]]) -> None:
    pair = pairs[0]
    assert golden.shuffled_kinds(pair) == golden.shuffled_kinds(pair)


def test_shuffle_does_not_always_put_the_star_first(
    pairs: list[dict[str, object]],
) -> None:
    star_in_a = sum(golden.shuffled_kinds(p)["A"] == golden.star_kind(p) for p in pairs)
    assert star_in_a < len(pairs) / 2


def test_majority_and_ties() -> None:
    assert golden.majority(["B", "A", "B"]) == ["B"]
    assert golden.majority(["A", "B"]) == ["A", "B"]
    assert golden.majority([]) == []


def test_report_without_answers() -> None:
    assert "no answer yet" in golden.report([])


def test_report_counts_agreement_and_lists_disagreements() -> None:
    rows = [
        golden.PairResult("p1", "box", ("box",), 3, 4),
        golden.PairResult("p2", "box", ("violin",), 3, 4),
    ]
    text = golden.report(rows)
    assert "★ agreement: 1/2 (50%)" in text
    assert "chance level 25%" in text
    assert "p2: ★ box, humans violin" in text


def test_print_agreement() -> None:
    """Not blocking yet: prints the agreement (pytest -s to see it)."""
    print("\n" + golden.report(golden.results()))
