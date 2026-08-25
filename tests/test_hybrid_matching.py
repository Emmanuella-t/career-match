"""Tests for Hybrid Matcher v0.1."""

from __future__ import annotations

import pytest

from career_match.evaluation.benchmark import load_benchmark
from career_match.evaluation.holdout_benchmark import (
    assert_holdout_checksum,
    expected_holdout_checksum,
)
from career_match.evaluation.hybrid_harness import evaluate_hybrid_benchmark
from career_match.matching.hybrid import HybridMatcher
from career_match.matching.hybrid_config import HybridConfig
from career_match.matching.semantic import SemanticMatcher


class _FixedEncoder:
    def encode(self, texts):
        import numpy as np

        # Deterministic orthogonal-ish vectors from text length parity.
        rows = []
        for text in texts:
            vec = np.zeros(4, dtype=np.float32)
            vec[0] = 1.0 if "python" in text.lower() else 0.2
            vec[1] = 1.0 if "docker" in text.lower() else 0.1
            vec[2] = 0.5
            vec[3] = min(1.0, len(text) / 500.0)
            rows.append(vec)
        matrix = np.vstack(rows)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        return matrix / np.clip(norms, 1e-12, None)


def _matcher(config: HybridConfig | None = None) -> HybridMatcher:
    semantic = SemanticMatcher(encoder=_FixedEncoder())
    return HybridMatcher(config=config, semantic_matcher=semantic)


def test_hybrid_weights_must_sum_to_one() -> None:
    with pytest.raises(ValueError, match="must equal 1.0"):
        HybridConfig(semantic_weight=0.5, tfidf_weight=0.5, skill_weight=0.5)


def test_hybrid_score_in_range_and_exposes_components() -> None:
    result = _matcher().match(
        "Python FastAPI Docker Git on Linux services.",
        "Backend Engineer using Python, FastAPI, Docker, and Git.",
    )
    assert 0 <= result.overall_score <= 100
    assert 0 <= result.semantic_score <= 100
    assert 0 <= result.tfidf_score <= 100
    assert 0 <= result.skill_overlap_score <= 100
    assert result.semantic_score == result.semantic_similarity
    assert result.tfidf_score == result.tfidf_similarity
    assert result.matched_skills
    assert isinstance(result.weak_or_negated_skills, tuple)
    assert "Not a hiring probability." in result.evidence[-1]


def test_hybrid_exposes_weak_or_negated_skills() -> None:
    result = _matcher().match(
        "Python and Git locally. No production Docker experience. "
        "Skills: Python, Docker, Git, Kubernetes",
        "Needs Python, Docker, Git, and Kubernetes.",
    )
    assert "docker" in result.weak_or_negated_skills
    assert "docker" in result.missing_skills or "docker" not in result.matched_skills



def test_hybrid_is_deterministic() -> None:
    matcher = _matcher()
    resume = "Python Docker Git"
    job = "Python Docker Git Linux"
    assert matcher.match(resume, job) == matcher.match(resume, job)


def test_negation_lowers_skill_channel_vs_positive_mention() -> None:
    matcher = _matcher(
        HybridConfig(semantic_weight=0.2, tfidf_weight=0.2, skill_weight=0.6)
    )
    job = "Needs Python, Docker, Git, and Linux."
    positive = matcher.match(
        "Shipped Python services with Docker on Linux using Git.",
        job,
    )
    negated = matcher.match(
        "Python and Git locally. No production Docker experience. "
        "Limited exposure to Linux. Skills: Python, Docker, Git, Linux",
        job,
    )
    assert positive.skill_overlap_score > negated.skill_overlap_score
    assert positive.overall_score > negated.overall_score


def test_keyword_stuffing_skill_channel_discounted() -> None:
    matcher = _matcher(
        HybridConfig(semantic_weight=0.2, tfidf_weight=0.2, skill_weight=0.6)
    )
    job = "Machine Learning Engineer using Python, PyTorch, Docker, AWS, Git."
    strong = matcher.match(
        "Five years training PyTorch models in Python. Packaged with Docker on AWS. Git daily.",
        job,
    )
    stuffed = matcher.match(
        "Claims tools without outcomes. Python PyTorch TensorFlow NLP Docker "
        "Kubernetes AWS Azure GCP Spark React Next.js FastAPI Django SQL "
        "Machine Learning Deep Learning REST APIs HTML CSS Java JavaScript "
        "TypeScript pandas NumPy scikit-learn Git Linux.",
        job,
    )
    assert strong.skill_overlap_score >= stuffed.skill_overlap_score
    assert any("stuffing_likely=True" in item for item in stuffed.evidence)
    assert any("stuffing_penalty=" in item for item in stuffed.evidence)


def test_holdout_checksum_unchanged_by_hybrid_work() -> None:
    assert assert_holdout_checksum() == expected_holdout_checksum()


def test_hybrid_benchmark_integration_smoke() -> None:
    """Smoke-test harness wiring on v0.2 without requiring MiniLM downloads."""
    semantic = SemanticMatcher(encoder=_FixedEncoder())
    matcher = HybridMatcher(
        config=HybridConfig(semantic_weight=0.5, tfidf_weight=0.25, skill_weight=0.25),
        semantic_matcher=semantic,
    )
    benchmark = load_benchmark()
    # Evaluate a tiny synthetic subset by temporarily filtering is heavy;
    # instead just match one labeled pair through the matcher.
    job = benchmark.job_by_id()["job-mle"]
    resume = benchmark.resume_by_id()["r-mle-prod"]
    result = matcher.match(resume.to_text(), job.to_text())
    assert result.overall_score > 0
    evaluation = evaluate_hybrid_benchmark(matcher=matcher, benchmark=benchmark)
    assert evaluation.pair_count == 56
    assert evaluation.matcher_name == "Hybrid Matcher v0.1"
