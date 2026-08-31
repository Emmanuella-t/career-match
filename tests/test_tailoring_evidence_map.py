"""Unit tests for tailoring evidence mapping."""

from __future__ import annotations

from career_match.tailoring.evidence_map import build_evidence_map

PYTHON_RESUME = (
    "Built GitHub Actions pipelines for automated testing and deployment. "
    "Python, FastAPI, Docker, SQL, and Git."
)


def test_equivalent_ci_cd_supported() -> None:
    job = "Need CI/CD and Python experience."
    evidence = build_evidence_map(PYTHON_RESUME, job)
    entry = next(item for item in evidence.requirements if item.requirement == "ci/cd")
    assert entry.status == "equivalent"


def test_aws_unsupported_without_evidence() -> None:
    job = "Need AWS and Python."
    evidence = build_evidence_map(PYTHON_RESUME, job)
    entry = next(item for item in evidence.requirements if item.requirement == "aws")
    assert entry.status == "unsupported"
