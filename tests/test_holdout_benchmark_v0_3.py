"""Tests for frozen holdout benchmark v0.3 parsing, validation, and checksum."""

from __future__ import annotations

import copy
import json

import pytest

from career_match.core.exceptions import BenchmarkValidationError
from career_match.evaluation.holdout_benchmark import (
    HOLDOUT_KIND,
    HOLDOUT_NAME,
    HOLDOUT_VERSION,
    assert_holdout_checksum,
    compute_holdout_checksum,
    default_holdout_manifest_path,
    default_holdout_path,
    expected_holdout_checksum,
    load_holdout_benchmark,
    parse_holdout_benchmark,
    validate_holdout_payload,
)
from career_match.matching.config import SKILL_OVERLAP_WEIGHT, TFIDF_WEIGHT


def _minimal_valid_payload() -> dict:
    resumes = [
        {
            "resume_id": f"hr{index}",
            "profile_summary": "Synthetic profile.",
            "experience_text": "Synthetic experience.",
            "skills_text": "Python",
        }
        for index in range(8)
    ]
    jobs = [
        {
            "job_id": f"hold-test-{index}",
            "title": f"Test Role {index}",
            "description": "Uses Python.",
            "required_skills": ["Python"],
        }
        for index in range(8)
    ]
    judgments = []
    for job in jobs:
        grades = [3, 2, 2, 1, 1, 1, 1, 0]
        for resume, grade in zip(resumes, grades, strict=True):
            judgments.append(
                {
                    "job_id": job["job_id"],
                    "resume_id": resume["resume_id"],
                    "grade": grade,
                    "rationale": f"{grade} — synthetic unit-test judgment.",
                    "case_tags": ["hard_negative"] if grade == 0 else ["unit_test"],
                }
            )
    return {
        "name": HOLDOUT_NAME,
        "kind": HOLDOUT_KIND,
        "version": HOLDOUT_VERSION,
        "disclaimer": "Synthetic unit-test holdout payload. Not production ground truth.",
        "provenance": {
            "synthetic": True,
            "real_candidate_data": False,
            "production_hiring_labels": False,
            "independent_annotator_agreement": False,
            "production_ground_truth": False,
            "frozen_before_hybrid_matcher": True,
            "label_type": "manually specified synthetic relevance judgments",
        },
        "jobs": jobs,
        "resumes": resumes,
        "judgments": judgments,
    }


def test_shipped_holdout_parses_and_validates() -> None:
    benchmark = load_holdout_benchmark()
    assert benchmark.name == HOLDOUT_NAME
    assert benchmark.kind == HOLDOUT_KIND
    assert benchmark.version == HOLDOUT_VERSION
    assert "not independently validated ground truth" in benchmark.disclaimer.lower()
    assert "frozen" in benchmark.disclaimer.lower()
    assert "human ground truth" not in benchmark.disclaimer.lower()
    assert "expert labels" not in benchmark.disclaimer.lower()
    assert benchmark.job_count == 9
    assert benchmark.resume_count == 29
    assert benchmark.pair_count == 72
    titles = {job.title for job in benchmark.jobs}
    assert titles >= {
        "Machine Learning Engineer",
        "Applied AI Engineer",
        "Data Scientist",
        "Data Analyst",
        "Backend Engineer",
        "Full-Stack Engineer",
        "MLOps Engineer",
        "Data Engineer",
        "NLP Engineer",
    }


def test_shipped_holdout_provenance() -> None:
    payload = json.loads(default_holdout_path().read_text(encoding="utf-8"))
    provenance = payload["provenance"]
    assert provenance["synthetic"] is True
    assert provenance["real_candidate_data"] is False
    assert provenance["production_hiring_labels"] is False
    assert provenance["independent_annotator_agreement"] is False
    assert provenance["production_ground_truth"] is False
    assert provenance["frozen_before_hybrid_matcher"] is True
    assert provenance["intended_use"] == "controlled model comparison"
    assert provenance["label_type"] == "manually specified synthetic relevance judgments"
    assert provenance["review_status"] == "awaiting/available for manual review"
    assert all(item.get("case_tags") for item in payload["judgments"])
    assert all(str(item.get("rationale", "")).strip() for item in payload["judgments"])


def test_holdout_checksum_matches_manifest() -> None:
    actual = compute_holdout_checksum()
    expected = expected_holdout_checksum()
    assert actual == expected
    assert assert_holdout_checksum() == expected
    manifest = json.loads(default_holdout_manifest_path().read_text(encoding="utf-8"))
    assert manifest["sha256"] == expected
    assert manifest["purpose"].startswith("reproducibility")
    assert manifest["not_security"] is True


def test_holdout_checksum_detects_modification(tmp_path) -> None:
    original = default_holdout_path().read_text(encoding="utf-8")
    payload = json.loads(original)
    payload["disclaimer"] = payload["disclaimer"] + " accidental edit"
    mutated = tmp_path / "holdout_mutated.json"
    mutated.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(BenchmarkValidationError, match="checksum mismatch"):
        assert_holdout_checksum(mutated)


def test_each_holdout_job_covers_levels_and_hard_negative() -> None:
    benchmark = load_holdout_benchmark()
    grouped = benchmark.judgments_by_job()
    for job in benchmark.jobs:
        grades = {item.grade for item in grouped[job.job_id]}
        assert 3 in grades
        assert 0 in grades
        assert len(grades) >= 3
        assert 7 <= len(grouped[job.job_id]) <= 8
        for item in grouped[job.job_id]:
            assert item.rationale.strip()
            assert item.case_tags
            assert item.grade in {0, 1, 2, 3}


def test_holdout_does_not_reuse_v0_2_ids() -> None:
    holdout = load_holdout_benchmark()
    from career_match.evaluation.benchmark import load_benchmark

    v02 = load_benchmark()
    assert set(holdout.job_by_id()).isdisjoint(set(v02.job_by_id()))
    assert set(holdout.resume_by_id()).isdisjoint(set(v02.resume_by_id()))


def test_missing_case_tags_rejected() -> None:
    payload = _minimal_valid_payload()
    payload["judgments"][0]["case_tags"] = []
    with pytest.raises(BenchmarkValidationError, match="case_tags"):
        validate_holdout_payload(payload)


def test_invalid_grade_rejected() -> None:
    payload = _minimal_valid_payload()
    payload["judgments"][0]["grade"] = 4
    with pytest.raises(BenchmarkValidationError, match="0-3"):
        validate_holdout_payload(payload)


def test_duplicate_judgment_rejected() -> None:
    payload = _minimal_valid_payload()
    payload["judgments"].append(copy.deepcopy(payload["judgments"][0]))
    with pytest.raises(BenchmarkValidationError, match="Duplicate judgment"):
        validate_holdout_payload(payload)


def test_missing_strong_match_rejected() -> None:
    payload = _minimal_valid_payload()
    for judgment in payload["judgments"]:
        if judgment["job_id"] == "hold-test-0" and judgment["grade"] == 3:
            judgment["grade"] = 2
    with pytest.raises(BenchmarkValidationError, match="strong match"):
        validate_holdout_payload(payload)


def test_parse_round_trip() -> None:
    benchmark = parse_holdout_benchmark(_minimal_valid_payload())
    assert benchmark.pair_count == 64
    assert benchmark.jobs[0].to_text().startswith("Test Role")


def test_matcher_weights_unchanged_for_holdout() -> None:
    assert TFIDF_WEIGHT == 0.55
    assert SKILL_OVERLAP_WEIGHT == 0.45
