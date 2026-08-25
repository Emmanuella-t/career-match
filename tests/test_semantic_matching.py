"""Behavioral tests for Semantic Matcher v0.1 that do not download a model."""

from __future__ import annotations

import hashlib

import numpy as np
import pytest

from career_match.evaluation.benchmark import load_benchmark
from career_match.evaluation.compare import comparison_rows
from career_match.evaluation.semantic_harness import evaluate_semantic_benchmark
from career_match.matching import Matcher, SemanticMatcher
from career_match.matching.semantic import cosine_to_score, pairwise_cosine
from career_match.matching.semantic_config import SEMANTIC_MATCHER_NAME, SemanticConfig


class HashingEncoder:
    """Deterministic bag-of-tokens encoder for tests. No network, no MiniLM."""

    def __init__(self, dim: int = 64) -> None:
        self.dim = dim

    def encode(self, texts: list[str]) -> np.ndarray:
        matrix = np.zeros((len(texts), self.dim), dtype=np.float32)
        for row, text in enumerate(texts):
            for token in text.lower().split():
                digest = hashlib.md5(token.encode("utf-8")).digest()
                matrix[row, digest[0] % self.dim] += 1.0
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        return matrix / np.clip(norms, 1e-12, None)


def test_semantic_matcher_satisfies_protocol() -> None:
    matcher: Matcher = SemanticMatcher(encoder=HashingEncoder())
    result = matcher.match("Python services on Linux", "Python services on Linux")
    assert 0 <= result.score <= 100
    assert result.semantic_similarity == result.overall_score
    assert result.tfidf_similarity == 0.0
    assert result.skill_overlap_score == 0.0
    assert result.matched_skills == ()
    assert "Not a hiring probability" in " ".join(result.evidence)


def test_semantic_score_is_in_range_and_higher_for_similar_text() -> None:
    matcher = SemanticMatcher(encoder=HashingEncoder())
    similar = matcher.match(
        "REST services on cloud infrastructure",
        "REST services on cloud infrastructure",
    )
    unrelated = matcher.match(
        "REST services on cloud infrastructure",
        "community theater lighting cues and costume sketches",
    )
    assert 0 <= similar.overall_score <= 100
    assert 0 <= unrelated.overall_score <= 100
    assert similar.overall_score > unrelated.overall_score
    assert similar.overall_score == pytest.approx(100.0, abs=0.01)


def test_semantic_output_is_repeatable() -> None:
    matcher = SemanticMatcher(encoder=HashingEncoder())
    resume = "Data pipelines into relational warehouses"
    job = "Build data pipelines and relational warehouses"
    assert matcher.match(resume, job) == matcher.match(resume, job)


def test_cosine_helpers() -> None:
    assert cosine_to_score(1.0, 100.0) == 100.0
    assert cosine_to_score(0.0, 100.0) == 0.0
    assert cosine_to_score(-0.5, 100.0) == 0.0
    left = np.array([[1.0, 0.0], [0.0, 1.0]])
    right = np.array([[1.0, 0.0], [1.0, 0.0]])
    cos = pairwise_cosine(left, right)
    assert cos[0] == pytest.approx(1.0)
    assert cos[1] == pytest.approx(0.0)


def test_batch_evaluation_on_v0_2_with_injected_encoder() -> None:
    matcher = SemanticMatcher(encoder=HashingEncoder())
    first = evaluate_semantic_benchmark(matcher=matcher)
    second = evaluate_semantic_benchmark(matcher=matcher)
    assert first.matcher_name == SEMANTIC_MATCHER_NAME
    assert first.pair_count == 56
    assert first.job_count == 8
    assert first.pairs == second.pairs
    for job in first.jobs:
        assert len(job.ranking) == 7
        scores = [item.overall_score for item in job.ranking]
        assert scores == sorted(scores, reverse=True)
        assert all(0 <= item.overall_score <= 100 for item in job.ranking)
        assert all(item.semantic_similarity == item.overall_score for item in job.ranking)


def test_comparison_rows_report_all_metrics_and_signed_deltas() -> None:
    benchmark = load_benchmark()

    class _Stub:
        mean_precision_at_1 = 0.875
        mean_precision_at_3 = 0.667
        mean_recall_at_3 = 0.562
        mean_ndcg_at_3 = 0.849
        mean_ndcg_full = 0.929
        mean_pairwise_accuracy = 0.709

    class _Other:
        mean_precision_at_1 = 0.750
        mean_precision_at_3 = 0.700
        mean_recall_at_3 = 0.562
        mean_ndcg_at_3 = 0.800
        mean_ndcg_full = 0.900
        mean_pairwise_accuracy = 0.800

    rows = comparison_rows(_Stub(), _Other())  # type: ignore[arg-type]
    names = [row.name for row in rows]
    assert names == [
        "Precision@1",
        "Precision@3",
        "Recall@3",
        "NDCG@3",
        "NDCG (full pool)",
        "Pairwise ordering accuracy",
    ]
    by_name = {row.name: row for row in rows}
    assert by_name["Precision@1"].delta == pytest.approx(-0.125)
    assert by_name["Precision@3"].delta == pytest.approx(0.033)
    assert by_name["Pairwise ordering accuracy"].delta == pytest.approx(0.091)
    assert benchmark.pair_count == 56


def test_semantic_config_rejects_empty_model_name() -> None:
    with pytest.raises(ValueError):
        SemanticConfig(model_name="  ")
