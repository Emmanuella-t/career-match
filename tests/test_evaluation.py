"""Evaluation metric tests."""

import pytest

from career_match.evaluation.metrics import f1_score, precision, recall


def test_precision() -> None:
    assert precision(true_positives=3, false_positives=1) == 0.75
    assert precision(true_positives=0, false_positives=0) == 0.0


def test_recall() -> None:
    assert recall(true_positives=2, false_negatives=2) == 0.5
    assert recall(true_positives=0, false_negatives=0) == 0.0


def test_f1() -> None:
    assert f1_score(1.0, 1.0) == 1.0
    assert f1_score(0.5, 0.5) == 0.5


def test_f1_zero_when_no_positives() -> None:
    assert f1_score(0.0, 0.0) == 0.0
    with pytest.raises(ValueError):
        precision(true_positives=-1, false_positives=0)
