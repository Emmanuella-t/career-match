"""Tests for development benchmark v0.2 parsing, validation, and evaluation."""

from __future__ import annotations

import copy
import json

import pytest

from career_match.core.exceptions import BenchmarkValidationError
from career_match.evaluation.benchmark import (
    BENCHMARK_KIND,
    BENCHMARK_NAME,
    default_benchmark_path,
    load_benchmark,
    parse_benchmark,
    validate_benchmark_payload,
)
from career_match.evaluation.benchmark_harness import evaluate_benchmark_v0_2
from career_match.evaluation.ranking import pairwise_ordering_accuracy
from career_match.matching.config import SKILL_OVERLAP_WEIGHT, TFIDF_WEIGHT


def _valid_payload() -> dict:
    resumes = [
        {
            "resume_id": f"r{index}",
            "profile_summary": "Synthetic profile.",
            "experience_text": "Synthetic experience.",
            "skills_text": "Python",
        }
        for index in range(6)
    ]
    return {
        "name": BENCHMARK_NAME,
        "kind": BENCHMARK_KIND,
        "disclaimer": "Synthetic unit-test payload. Not a production benchmark.",
        "jobs": [
            {
                "job_id": "job-test",
                "title": "Test Engineer",
                "description": "Uses Python.",
                "required_skills": ["Python"],
            }
        ],
        "resumes": resumes,
        "judgments": [
            {"job_id": "job-test", "resume_id": "r0", "grade": 3, "rationale": "strong"},
            {"job_id": "job-test", "resume_id": "r1", "grade": 2, "rationale": "moderate"},
            {"job_id": "job-test", "resume_id": "r2", "grade": 1, "rationale": "weak"},
            {"job_id": "job-test", "resume_id": "r3", "grade": 0, "rationale": "mismatch"},
            {"job_id": "job-test", "resume_id": "r4", "grade": 1, "rationale": "weak-2"},
            {"job_id": "job-test", "resume_id": "r5", "grade": 2, "rationale": "moderate-2"},
        ],
    }


def test_shipped_benchmark_parses_and_validates() -> None:
    benchmark = load_benchmark()
    assert benchmark.name == BENCHMARK_NAME
    assert benchmark.kind == BENCHMARK_KIND
    assert "not independently validated ground truth" in benchmark.disclaimer.lower()
    assert "human-defined" not in benchmark.disclaimer.lower()
    assert "human-labeled" not in benchmark.disclaimer.lower()
    assert benchmark.job_count == 8
    assert benchmark.resume_count == 24
    assert benchmark.pair_count == 56
    titles = {job.title for job in benchmark.jobs}
    assert titles >= {
        "Machine Learning Engineer",
        "Data Scientist",
        "Data Analyst",
        "Backend Engineer",
        "Frontend Engineer",
        "Full-Stack Engineer",
        "MLOps Engineer",
        "Data Engineer",
    }


def test_shipped_benchmark_records_synthetic_provenance() -> None:
    payload = json.loads(default_benchmark_path().read_text(encoding="utf-8"))
    provenance = payload["provenance"]
    assert provenance["synthetic"] is True
    assert provenance["constructed_for"] == "controlled development evaluation"
    assert provenance["real_candidate_data"] is False
    assert provenance["production_hiring_labels"] is False
    assert provenance["independent_annotator_agreement"] is False
    assert provenance["intended_use"] == "model comparison and error analysis"
    assert provenance["label_type"] == "manually specified synthetic relevance judgments"
    assert provenance["review_status"] == "awaiting/available for manual review"
    judgments = payload["judgments"]
    assert len(judgments) == 56
    assert all("grade" in item and "rationale" in item for item in judgments)


def test_each_job_covers_strong_mismatch_and_multiple_grades() -> None:
    benchmark = load_benchmark()
    grouped = benchmark.judgments_by_job()
    for job in benchmark.jobs:
        grades = {item.grade for item in grouped[job.job_id]}
        assert 3 in grades
        assert 0 in grades
        assert len(grades) >= 3
        assert 6 <= len(grouped[job.job_id]) <= 8
        for item in grouped[job.job_id]:
            assert item.rationale.strip()
            assert item.grade in {0, 1, 2, 3}


def test_resume_and_job_text_include_structured_fields() -> None:
    benchmark = load_benchmark()
    resume = benchmark.resume_by_id()["r-mle-prod"]
    text = resume.to_text()
    assert "Skills:" in text
    assert "Years of experience" in text
    job = benchmark.job_by_id()["job-mle"]
    job_text = job.to_text()
    assert job.title in job_text
    assert "Deep Learning" in job_text


def test_invalid_grade_is_rejected() -> None:
    payload = _valid_payload()
    payload["judgments"][0]["grade"] = 4
    with pytest.raises(BenchmarkValidationError, match="0-3"):
        validate_benchmark_payload(payload)


def test_boolean_grade_is_rejected() -> None:
    payload = _valid_payload()
    payload["judgments"][0]["grade"] = True
    with pytest.raises(BenchmarkValidationError, match="0-3"):
        validate_benchmark_payload(payload)


def test_unknown_job_and_resume_references_are_rejected() -> None:
    payload = _valid_payload()
    payload["judgments"][0]["job_id"] = "missing-job"
    with pytest.raises(BenchmarkValidationError, match="unknown job_id"):
        validate_benchmark_payload(payload)
    payload = _valid_payload()
    payload["judgments"][0]["resume_id"] = "missing-resume"
    with pytest.raises(BenchmarkValidationError, match="unknown resume_id"):
        validate_benchmark_payload(payload)


def test_duplicate_judgment_is_rejected() -> None:
    payload = _valid_payload()
    payload["judgments"].append(copy.deepcopy(payload["judgments"][0]))
    with pytest.raises(BenchmarkValidationError, match="Duplicate judgment"):
        validate_benchmark_payload(payload)


def test_missing_strong_match_is_rejected() -> None:
    payload = _valid_payload()
    payload["judgments"][0]["grade"] = 2
    with pytest.raises(BenchmarkValidationError, match="strong match"):
        validate_benchmark_payload(payload)


def test_missing_hard_negative_is_rejected() -> None:
    payload = _valid_payload()
    payload["judgments"][3]["grade"] = 1
    with pytest.raises(BenchmarkValidationError, match="hard negative"):
        validate_benchmark_payload(payload)


def test_too_few_relevance_levels_rejected() -> None:
    payload = _valid_payload()
    for judgment in payload["judgments"]:
        judgment["grade"] = 3 if judgment["resume_id"] == "r0" else 0
    with pytest.raises(BenchmarkValidationError, match="multiple relevance levels"):
        validate_benchmark_payload(payload)


def test_missing_required_job_field_rejected() -> None:
    payload = _valid_payload()
    del payload["jobs"][0]["description"]
    with pytest.raises(BenchmarkValidationError, match="missing required fields"):
        validate_benchmark_payload(payload)


def test_parse_round_trip_on_valid_payload() -> None:
    benchmark = parse_benchmark(_valid_payload())
    assert benchmark.pair_count == 6
    assert benchmark.jobs[0].to_text().startswith("Test Engineer")


def test_pairwise_ordering_accuracy() -> None:
    assert pairwise_ordering_accuracy([3, 2, 0], [90.0, 50.0, 10.0]) == 1.0
    assert pairwise_ordering_accuracy([3, 2, 0], [10.0, 50.0, 90.0]) == 0.0
    assert pairwise_ordering_accuracy([3, 2], [40.0, 40.0]) == 0.0
    assert pairwise_ordering_accuracy([2, 2], [10.0, 90.0]) == 0.0
    with pytest.raises(ValueError):
        pairwise_ordering_accuracy([1], [1.0, 2.0])


def test_evaluation_is_reproducible_and_deterministic() -> None:
    first = evaluate_benchmark_v0_2()
    second = evaluate_benchmark_v0_2()
    assert first.pair_count == 56
    assert first.mean_precision_at_1 == second.mean_precision_at_1
    assert first.mean_ndcg_full == second.mean_ndcg_full
    assert first.pairs == second.pairs
    assert TFIDF_WEIGHT == 0.55
    assert SKILL_OVERLAP_WEIGHT == 0.45
    assert first.config.tfidf_weight == TFIDF_WEIGHT


def test_baseline_is_not_perfect_on_v0_2() -> None:
    """v0.2 is a stress set; perfect ranking would mean the fixture is still too easy."""
    evaluation = evaluate_benchmark_v0_2()
    assert evaluation.mean_precision_at_1 < 1.0
    assert evaluation.mean_precision_at_3 < 1.0
    mle = next(job for job in evaluation.jobs if job.job_id == "job-mle")
    assert mle.ranking[0].resume_id == "r-mle-stuffing"
    synonym = next(item for item in mle.ranking if item.resume_id == "r-mle-synonym")
    stuffing = next(item for item in mle.ranking if item.resume_id == "r-mle-stuffing")
    assert stuffing.overall_score > synonym.overall_score
    assert stuffing.grade == 0
    assert synonym.grade == 3
