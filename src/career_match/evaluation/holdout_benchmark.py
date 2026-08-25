"""Loader and validator for frozen holdout benchmark v0.3.

This set is synthetic and was constructed for controlled model comparison
before hybrid-matcher development. Relevance grades are manually specified
synthetic relevance judgments, not independently validated ground truth.
There is no real candidate data, no production hiring labels, and no
independent annotator agreement.

v0.3 must remain frozen during hybrid-matcher development. Accidental edits
are detected via a SHA-256 checksum of the canonical JSON file bytes.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from career_match.core.exceptions import BenchmarkValidationError
from career_match.data.legacy import repo_root
from career_match.evaluation.benchmark import (
    RELEVANCE_LABELS,
    REQUIRED_JOB_FIELDS,
    REQUIRED_JUDGMENT_FIELDS,
    REQUIRED_RESUME_FIELDS,
    BenchmarkJob,
    BenchmarkResume,
    DevelopmentBenchmark,
    RelevanceJudgment,
    _as_string_tuple,
    _require_fields,
)

DEFAULT_HOLDOUT_BENCHMARK = Path("data") / "evaluation" / "holdout_benchmark_v0_3.json"
DEFAULT_HOLDOUT_MANIFEST = Path("data") / "evaluation" / "holdout_benchmark_v0_3.manifest.json"
HOLDOUT_KIND = "frozen holdout evaluation benchmark"
HOLDOUT_NAME = "career-match-holdout-benchmark-v0.3"
HOLDOUT_VERSION = "0.3"

MIN_POOL = 7
MAX_POOL = 8


def default_holdout_path() -> Path:
    return repo_root() / DEFAULT_HOLDOUT_BENCHMARK


def default_holdout_manifest_path() -> Path:
    return repo_root() / DEFAULT_HOLDOUT_MANIFEST


def canonical_benchmark_bytes(path: Path | None = None) -> bytes:
    """Return canonical UTF-8 JSON bytes (LF newlines) for the checksum.

    Parsing then re-serializing avoids Windows CRLF vs Linux LF file-byte
    mismatches. Content identity is what matters for reproducibility.
    """
    payload = json.loads((path or default_holdout_path()).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise BenchmarkValidationError("Holdout benchmark must contain a JSON object.")
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    return text.encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_holdout_checksum(path: Path | None = None) -> str:
    """SHA-256 of the shipped holdout JSON file (reproducibility, not security)."""
    return sha256_hex(canonical_benchmark_bytes(path))


def load_holdout_manifest(path: Path | None = None) -> dict[str, Any]:
    manifest_path = path or default_holdout_manifest_path()
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise BenchmarkValidationError(f"{manifest_path} must contain a JSON object.")
    return payload


def expected_holdout_checksum(manifest_path: Path | None = None) -> str:
    manifest = load_holdout_manifest(manifest_path)
    checksum = manifest.get("sha256")
    if not isinstance(checksum, str) or not checksum:
        raise BenchmarkValidationError("Holdout manifest missing sha256 string.")
    return checksum.lower()


def assert_holdout_checksum(
    benchmark_path: Path | None = None,
    manifest_path: Path | None = None,
) -> str:
    """Raise if the holdout JSON no longer matches the frozen checksum."""
    actual = compute_holdout_checksum(benchmark_path)
    expected = expected_holdout_checksum(manifest_path)
    if actual != expected:
        raise BenchmarkValidationError(
            "Holdout benchmark checksum mismatch: file was modified after freeze. "
            f"expected={expected} actual={actual}"
        )
    return actual


def validate_holdout_payload(payload: dict[str, Any]) -> None:
    """Raise ``BenchmarkValidationError`` if the raw holdout JSON is invalid."""
    if not isinstance(payload, dict):
        raise BenchmarkValidationError("Holdout payload must be an object.")
    if payload.get("kind") != HOLDOUT_KIND:
        raise BenchmarkValidationError(
            f"kind must be {HOLDOUT_KIND!r}, got {payload.get('kind')!r}."
        )
    if payload.get("name") != HOLDOUT_NAME:
        raise BenchmarkValidationError(
            f"name must be {HOLDOUT_NAME!r}, got {payload.get('name')!r}."
        )
    if payload.get("version") != HOLDOUT_VERSION:
        raise BenchmarkValidationError(
            f"version must be {HOLDOUT_VERSION!r}, got {payload.get('version')!r}."
        )
    for field in ("jobs", "resumes", "judgments", "disclaimer", "provenance"):
        if field not in payload:
            raise BenchmarkValidationError(f"Holdout missing {field!r}.")

    provenance = payload["provenance"]
    if not isinstance(provenance, dict):
        raise BenchmarkValidationError("provenance must be an object.")
    required_provenance = {
        "synthetic": True,
        "real_candidate_data": False,
        "production_hiring_labels": False,
        "independent_annotator_agreement": False,
        "production_ground_truth": False,
        "frozen_before_hybrid_matcher": True,
        "label_type": "manually specified synthetic relevance judgments",
    }
    for key, expected in required_provenance.items():
        if provenance.get(key) != expected:
            raise BenchmarkValidationError(
                f"provenance.{key} must be {expected!r}, got {provenance.get(key)!r}."
            )

    jobs = payload["jobs"]
    resumes = payload["resumes"]
    judgments = payload["judgments"]
    if not isinstance(jobs, list) or not jobs:
        raise BenchmarkValidationError("jobs must be a non-empty list.")
    if not isinstance(resumes, list) or not resumes:
        raise BenchmarkValidationError("resumes must be a non-empty list.")
    if not isinstance(judgments, list) or not judgments:
        raise BenchmarkValidationError("judgments must be a non-empty list.")
    if not (8 <= len(jobs) <= 10):
        raise BenchmarkValidationError(f"holdout expects 8-10 jobs, got {len(jobs)}.")

    job_ids: list[str] = []
    for index, job in enumerate(jobs):
        if not isinstance(job, dict):
            raise BenchmarkValidationError(f"jobs[{index}] must be an object.")
        _require_fields(job, REQUIRED_JOB_FIELDS, f"jobs[{index}]")
        job_id = job["job_id"]
        if not isinstance(job_id, str) or not job_id:
            raise BenchmarkValidationError(f"jobs[{index}].job_id must be a non-empty string.")
        job_ids.append(job_id)
        required = job.get("required_skills")
        if not isinstance(required, list) or not required:
            raise BenchmarkValidationError(f"{job_id}: required_skills must be a non-empty list.")
    if len(job_ids) != len(set(job_ids)):
        raise BenchmarkValidationError("job_id values must be unique.")

    resume_ids: list[str] = []
    for index, resume in enumerate(resumes):
        if not isinstance(resume, dict):
            raise BenchmarkValidationError(f"resumes[{index}] must be an object.")
        _require_fields(resume, REQUIRED_RESUME_FIELDS, f"resumes[{index}]")
        resume_id = resume["resume_id"]
        if not isinstance(resume_id, str) or not resume_id:
            raise BenchmarkValidationError(
                f"resumes[{index}].resume_id must be a non-empty string."
            )
        resume_ids.append(resume_id)
    if len(resume_ids) != len(set(resume_ids)):
        raise BenchmarkValidationError("resume_id values must be unique.")

    job_id_set = set(job_ids)
    resume_id_set = set(resume_ids)
    seen_pairs: set[tuple[str, str]] = set()
    by_job: dict[str, list[int]] = defaultdict(list)
    hard_negatives: dict[str, int] = defaultdict(int)

    for index, judgment in enumerate(judgments):
        if not isinstance(judgment, dict):
            raise BenchmarkValidationError(f"judgments[{index}] must be an object.")
        _require_fields(judgment, REQUIRED_JUDGMENT_FIELDS, f"judgments[{index}]")
        job_id = judgment["job_id"]
        resume_id = judgment["resume_id"]
        grade = judgment["grade"]
        rationale = judgment["rationale"]
        if job_id not in job_id_set:
            raise BenchmarkValidationError(
                f"judgments[{index}] references unknown job_id {job_id!r}."
            )
        if resume_id not in resume_id_set:
            raise BenchmarkValidationError(
                f"judgments[{index}] references unknown resume_id {resume_id!r}."
            )
        if not isinstance(grade, int) or isinstance(grade, bool) or grade not in RELEVANCE_LABELS:
            raise BenchmarkValidationError(
                f"judgments[{index}] grade must be an integer 0-3, got {grade!r}."
            )
        if not isinstance(rationale, str) or not rationale.strip():
            raise BenchmarkValidationError(f"judgments[{index}] rationale must be non-empty.")
        tags = judgment.get("case_tags")
        if not isinstance(tags, list) or not tags:
            raise BenchmarkValidationError(
                f"judgments[{index}] case_tags must be a non-empty list."
            )
        if not all(isinstance(tag, str) and tag.strip() for tag in tags):
            raise BenchmarkValidationError(
                f"judgments[{index}] case_tags must contain non-empty strings."
            )
        pair = (job_id, resume_id)
        if pair in seen_pairs:
            raise BenchmarkValidationError(
                f"Duplicate judgment for job {job_id!r} and resume {resume_id!r}."
            )
        seen_pairs.add(pair)
        by_job[job_id].append(grade)
        if grade == 0 or "hard_negative" in tags:
            hard_negatives[job_id] += 1

    if not (60 <= len(judgments) <= 80):
        raise BenchmarkValidationError(
            f"holdout expects 60-80 judgments, got {len(judgments)}."
        )

    missing_jobs = job_id_set - set(by_job)
    if missing_jobs:
        raise BenchmarkValidationError(f"Jobs have no judgments: {sorted(missing_jobs)}")

    for job_id, grades in by_job.items():
        if not MIN_POOL <= len(grades) <= MAX_POOL:
            raise BenchmarkValidationError(
                f"{job_id}: expected {MIN_POOL}-{MAX_POOL} candidates, got {len(grades)}."
            )
        distinct = set(grades)
        if len(distinct) < 3:
            raise BenchmarkValidationError(
                f"{job_id}: expected multiple relevance levels, found {sorted(distinct)}."
            )
        if 3 not in distinct:
            raise BenchmarkValidationError(f"{job_id}: missing a strong match (grade 3).")
        if hard_negatives[job_id] < 1:
            raise BenchmarkValidationError(
                f"{job_id}: missing a hard negative (grade 0 or tagged hard_negative)."
            )


def parse_holdout_benchmark(payload: dict[str, Any]) -> DevelopmentBenchmark:
    """Validate and parse a holdout benchmark object."""
    validate_holdout_payload(payload)
    jobs = tuple(
        BenchmarkJob(
            job_id=item["job_id"],
            title=item["title"],
            description=item["description"],
            required_skills=_as_string_tuple(item.get("required_skills"), "required_skills"),
            preferred_skills=_as_string_tuple(item.get("preferred_skills"), "preferred_skills"),
            min_years_experience=item.get("min_years_experience"),
            family=item.get("family"),
        )
        for item in payload["jobs"]
    )
    resumes = tuple(
        BenchmarkResume(
            resume_id=item["resume_id"],
            profile_summary=item["profile_summary"],
            experience_text=item["experience_text"],
            skills_text=item["skills_text"],
            years_experience=item.get("years_experience"),
        )
        for item in payload["resumes"]
    )
    judgments = tuple(
        RelevanceJudgment(
            job_id=item["job_id"],
            resume_id=item["resume_id"],
            grade=int(item["grade"]),
            rationale=str(item["rationale"]),
            case_tags=_as_string_tuple(item.get("case_tags"), "case_tags"),
        )
        for item in payload["judgments"]
    )
    return DevelopmentBenchmark(
        name=str(payload["name"]),
        kind=str(payload["kind"]),
        version=str(payload.get("version", HOLDOUT_VERSION)),
        disclaimer=str(payload["disclaimer"]),
        relevant_threshold=int(payload.get("relevant_threshold", 2)),
        jobs=jobs,
        resumes=resumes,
        judgments=judgments,
    )


def load_holdout_benchmark(
    path: Path | None = None,
    *,
    verify_checksum: bool = True,
) -> DevelopmentBenchmark:
    """Load and validate ``career-match-holdout-benchmark-v0.3``."""
    benchmark_path = path or default_holdout_path()
    if verify_checksum:
        assert_holdout_checksum(benchmark_path)
    payload = json.loads(benchmark_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise BenchmarkValidationError(f"{benchmark_path} must contain a JSON object.")
    return parse_holdout_benchmark(payload)
