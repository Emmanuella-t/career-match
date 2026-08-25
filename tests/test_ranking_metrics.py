"""Tests for ranking metrics and the development evaluation fixture."""

import pytest

from career_match.evaluation.fixture import load_evaluation_fixture
from career_match.evaluation.harness import evaluate_baseline
from career_match.evaluation.ranking import (
    ndcg_at_k,
    pairwise_ordering_accuracy,
    precision_at_k,
    recall_at_k,
)


def test_precision_at_k() -> None:
    # rank order: relevant, relevant, not
    assert precision_at_k([3, 2, 0], k=2) == 1.0
    assert precision_at_k([0, 3, 2], k=1) == 0.0
    assert precision_at_k([3, 2, 0], k=0) == 0.0


def test_recall_at_k() -> None:
    # two relevant items (grades >= 2)
    assert recall_at_k([3, 0, 2], k=1) == pytest.approx(0.5)
    assert recall_at_k([3, 2, 0], k=2) == pytest.approx(1.0)
    assert recall_at_k([0, 0, 0], k=2) == 0.0


def test_ndcg_perfect_and_inverted() -> None:
    perfect = [3, 2, 1, 0]
    inverted = [0, 1, 2, 3]
    assert ndcg_at_k(perfect, k=4) == pytest.approx(1.0)
    assert ndcg_at_k(inverted, k=4) < ndcg_at_k(perfect, k=4)
    assert ndcg_at_k([0, 0, 0], k=3) == 0.0


def test_pairwise_ordering_accuracy_rewards_grade_aligned_scores() -> None:
    assert pairwise_ordering_accuracy([3, 1, 0], [80.0, 20.0, 5.0]) == 1.0
    assert pairwise_ordering_accuracy([3, 1, 0], [5.0, 20.0, 80.0]) < 1.0


def test_fixture_is_development_only_and_has_graded_pairs() -> None:
    fixture = load_evaluation_fixture()
    assert fixture.kind == "development evaluation fixture"
    assert "not a production benchmark" in fixture.disclaimer.lower()
    assert fixture.pair_count == 16
    assert len(fixture.queries) == 4
    roles = {query.role for query in fixture.queries}
    assert roles == {
        "Machine Learning Engineer",
        "Data Scientist",
        "Backend Engineer",
        "Frontend Engineer",
    }


def test_baseline_ranks_strong_above_moderate_above_mismatch() -> None:
    evaluation = evaluate_baseline()
    assert evaluation.ranking_checks_passed
    for query in evaluation.queries:
        assert query.strong_above_moderate
        assert query.moderate_above_mismatch
        assert query.ranking[0].label == "strong"
        assert query.ranking[-1].label == "mismatch"


def test_baseline_mean_metrics_are_high_on_the_dev_fixture() -> None:
    evaluation = evaluate_baseline()
    assert evaluation.mean_precision_at_1 == pytest.approx(1.0)
    assert evaluation.mean_ndcg_at_4 > 0.9
    assert 0.0 <= evaluation.mean_recall_at_2 <= 1.0
