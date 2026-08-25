"""Evaluation helpers for matching experiments.

Classification precision/recall/F1 remain available for later binary
experiments. Ranking metrics (P@K, R@K, NDCG) are for the development
matching fixture only.
"""

from career_match.evaluation.benchmark import load_benchmark
from career_match.evaluation.benchmark_harness import evaluate_benchmark_v0_2
from career_match.evaluation.fixture import load_evaluation_fixture
from career_match.evaluation.harness import evaluate_baseline
from career_match.evaluation.metrics import f1_score, precision, recall
from career_match.evaluation.ranking import (
    ndcg_at_k,
    pairwise_ordering_accuracy,
    precision_at_k,
    recall_at_k,
)

__all__ = [
    "evaluate_baseline",
    "evaluate_benchmark_v0_2",
    "f1_score",
    "load_benchmark",
    "load_evaluation_fixture",
    "ndcg_at_k",
    "pairwise_ordering_accuracy",
    "precision",
    "precision_at_k",
    "recall",
    "recall_at_k",
]
