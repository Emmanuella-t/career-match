"""Generic classification metrics for upcoming matching experiments.

These helpers do not evaluate a trained Career Match model. They exist so
later baselines can share one implementation of precision, recall, and F1.
"""

from __future__ import annotations


def precision(true_positives: int, false_positives: int) -> float:
    """Return precision, or 0.0 when there are no predicted positives."""
    _require_non_negative(true_positives, false_positives)
    predicted_positives = true_positives + false_positives
    if predicted_positives == 0:
        return 0.0
    return true_positives / predicted_positives


def recall(true_positives: int, false_negatives: int) -> float:
    """Return recall, or 0.0 when there are no actual positives."""
    _require_non_negative(true_positives, false_negatives)
    actual_positives = true_positives + false_negatives
    if actual_positives == 0:
        return 0.0
    return true_positives / actual_positives


def f1_score(precision_value: float, recall_value: float) -> float:
    """Return the harmonic mean of precision and recall."""
    if precision_value < 0 or recall_value < 0:
        raise ValueError("precision and recall must be non-negative.")
    if precision_value == 0 and recall_value == 0:
        return 0.0
    return 2 * precision_value * recall_value / (precision_value + recall_value)


def _require_non_negative(*counts: int) -> None:
    if any(count < 0 for count in counts):
        raise ValueError("counts must be non-negative integers.")
