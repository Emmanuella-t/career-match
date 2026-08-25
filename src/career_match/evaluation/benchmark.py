"""Loader and validator for development benchmark v0.2.

The benchmark is synthetic. It is harder than the v0.1 sanity fixture and
is still **not** a production benchmark. Labels are human-defined ground
truth, not model outputs. Legacy CSV category labels are never used.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from career_match.core.exceptions import BenchmarkValidationError
from career_match.data.legacy import repo_root

DEFAULT_BENCHMARK = Path("data") / "evaluation" / "dev_benchmark_v0_2.json"
BENCHMARK_KIND = "development evaluation benchmark"
BENCHMARK_NAME = "career-match-dev-benchmark-v0.2"

RELEVANCE_LABELS = {
    3: "strong",
    2: "moderate",
    1: "weak",
    0: "mismatch",
}

MIN_POOL = 6
MAX_POOL = 8
REQUIRED_JOB_FIELDS = ("job_id", "title", "description", "required_skills")
REQUIRED_RESUME_FIELDS = (
    "resume_id",
    "profile_summary",
    "experience_text",
    "skills_text",
)
REQUIRED_JUDGMENT_FIELDS = ("job_id", "resume_id", "grade", "rationale")


@dataclass(frozen=True)
class BenchmarkJob:
    job_id: str
    title: str
    description: str
    required_skills: tuple[str, ...]
    preferred_skills: tuple[str, ...] = ()
    min_years_experience: int | None = None
    family: str | None = None

    def to_text(self) -> str:
        """Job text passed to a matcher: title plus description only."""
        return f"{self.title}\n\n{self.description}"


@dataclass(frozen=True)
class BenchmarkResume:
    resume_id: str
    profile_summary: str
    experience_text: str
    skills_text: str
    years_experience: float | None = None

    def to_text(self) -> str:
        """Flatten structured resume fields into one document."""
        parts = [self.profile_summary.strip(), self.experience_text.strip()]
        skills = self.skills_text.strip()
        if skills:
            parts.append(f"Skills: {skills}")
        if self.years_experience is not None:
            years = self.years_experience
            year_label = int(years) if float(years).is_integer() else years
            parts.append(f"Years of experience: {year_label}")
        return "\n\n".join(part for part in parts if part)


@dataclass(frozen=True)
class RelevanceJudgment:
    job_id: str
    resume_id: str
    grade: int
    rationale: str
    case_tags: tuple[str, ...] = ()

    @property
    def label(self) -> str:
        return RELEVANCE_LABELS[self.grade]


@dataclass(frozen=True)
class DevelopmentBenchmark:
    name: str
    kind: str
    version: str
    disclaimer: str
    relevant_threshold: int
    jobs: tuple[BenchmarkJob, ...]
    resumes: tuple[BenchmarkResume, ...]
    judgments: tuple[RelevanceJudgment, ...]

    @property
    def job_count(self) -> int:
        return len(self.jobs)

    @property
    def resume_count(self) -> int:
        return len(self.resumes)

    @property
    def pair_count(self) -> int:
        return len(self.judgments)

    def job_by_id(self) -> dict[str, BenchmarkJob]:
        return {job.job_id: job for job in self.jobs}

    def resume_by_id(self) -> dict[str, BenchmarkResume]:
        return {resume.resume_id: resume for resume in self.resumes}

    def judgments_by_job(self) -> dict[str, tuple[RelevanceJudgment, ...]]:
        grouped: dict[str, list[RelevanceJudgment]] = defaultdict(list)
        for judgment in self.judgments:
            grouped[judgment.job_id].append(judgment)
        return {job_id: tuple(items) for job_id, items in grouped.items()}

    def grade_distribution(self) -> dict[int, int]:
        counts = Counter(item.grade for item in self.judgments)
        return {grade: counts.get(grade, 0) for grade in range(4)}


def default_benchmark_path() -> Path:
    return repo_root() / DEFAULT_BENCHMARK


def _require_fields(payload: dict[str, Any], fields: tuple[str, ...], where: str) -> None:
    missing = [name for name in fields if name not in payload or payload[name] in (None, "")]
    if missing:
        raise BenchmarkValidationError(f"{where} missing required fields: {missing}")


def _as_string_tuple(value: Any, field: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise BenchmarkValidationError(f"{field} must be a list of strings.")
    return tuple(item.strip() for item in value if item.strip())


def validate_benchmark_payload(payload: dict[str, Any]) -> None:
    """Raise ``BenchmarkValidationError`` if the raw JSON object is invalid."""
    if not isinstance(payload, dict):
        raise BenchmarkValidationError("Benchmark payload must be an object.")
    if payload.get("kind") != BENCHMARK_KIND:
        raise BenchmarkValidationError(
            f"kind must be {BENCHMARK_KIND!r}, got {payload.get('kind')!r}."
        )
    if payload.get("name") != BENCHMARK_NAME:
        raise BenchmarkValidationError(
            f"name must be {BENCHMARK_NAME!r}, got {payload.get('name')!r}."
        )
    for field in ("jobs", "resumes", "judgments", "disclaimer"):
        if field not in payload:
            raise BenchmarkValidationError(f"Benchmark missing {field!r}.")

    jobs = payload["jobs"]
    resumes = payload["resumes"]
    judgments = payload["judgments"]
    if not isinstance(jobs, list) or not jobs:
        raise BenchmarkValidationError("jobs must be a non-empty list.")
    if not isinstance(resumes, list) or not resumes:
        raise BenchmarkValidationError("resumes must be a non-empty list.")
    if not isinstance(judgments, list) or not judgments:
        raise BenchmarkValidationError("judgments must be a non-empty list.")

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
        pair = (job_id, resume_id)
        if pair in seen_pairs:
            raise BenchmarkValidationError(
                f"Duplicate judgment for job {job_id!r} and resume {resume_id!r}."
            )
        seen_pairs.add(pair)
        by_job[job_id].append(grade)
        tags = judgment.get("case_tags") or []
        if not isinstance(tags, list):
            raise BenchmarkValidationError(f"judgments[{index}].case_tags must be a list.")
        if grade == 0 or "hard_negative" in tags:
            hard_negatives[job_id] += 1

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


def parse_benchmark(payload: dict[str, Any]) -> DevelopmentBenchmark:
    """Validate and parse a benchmark object."""
    validate_benchmark_payload(payload)
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
        version=str(payload.get("version", "0.2")),
        disclaimer=str(payload["disclaimer"]),
        relevant_threshold=int(payload.get("relevant_threshold", 2)),
        jobs=jobs,
        resumes=resumes,
        judgments=judgments,
    )


def load_benchmark(path: Path | None = None) -> DevelopmentBenchmark:
    """Load and validate ``career-match-dev-benchmark-v0.2``."""
    benchmark_path = path or default_benchmark_path()
    payload = json.loads(benchmark_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise BenchmarkValidationError(f"{benchmark_path} must contain a JSON object.")
    return parse_benchmark(payload)
