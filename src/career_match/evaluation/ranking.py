"""Ranking metrics for graded and binary relevance lists.

``relevances`` is always in **rank order** (best-ranked item first), using
integer grades. Precision@K and Recall@K use a binary cutoff. NDCG uses the
grades themselves. Do not call these helpers on category labels from the
legacy CSV — that file is not a matching dataset.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

DEFAULT_RELEVANT_THRESHOLD = 2


def _require_k(k: int) -> None:
    if k < 0:
        raise ValueError("k must be non-negative.")


def precision_at_k(
    relevances: Sequence[int],
    k: int,
    *,
    relevant_threshold: int = DEFAULT_RELEVANT_THRESHOLD,
) -> float:
    """Binary precision@K on a ranked list."""
    _require_k(k)
    if k == 0:
        return 0.0
    top = list(relevances)[:k]
    hits = sum(1 for grade in top if grade >= relevant_threshold)
    return hits / k


def recall_at_k(
    relevances: Sequence[int],
    k: int,
    *,
    relevant_threshold: int = DEFAULT_RELEVANT_THRESHOLD,
) -> float:
    """Binary recall@K on a ranked list."""
    _require_k(k)
    relevant_total = sum(1 for grade in relevances if grade >= relevant_threshold)
    if relevant_total == 0:
        return 0.0
    top = list(relevances)[:k]
    hits = sum(1 for grade in top if grade >= relevant_threshold)
    return hits / relevant_total


def dcg_at_k(relevances: Sequence[int], k: int) -> float:
    """Discounted cumulative gain with gain ``2^rel - 1``."""
    _require_k(k)
    dcg = 0.0
    for index, grade in enumerate(list(relevances)[:k], start=1):
        dcg += (2**grade - 1) / math.log2(index + 1)
    return dcg


def ndcg_at_k(relevances: Sequence[int], k: int) -> float:
    """Normalized DCG@K. Returns 0.0 when there is no positive gain."""
    ideal = sorted(relevances, reverse=True)
    idcg = dcg_at_k(ideal, k)
    if idcg == 0:
        return 0.0
    return dcg_at_k(relevances, k) / idcg
