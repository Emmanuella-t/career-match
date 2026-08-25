"""Loader for the development matching evaluation fixture.

The fixture is synthetic. It is **not** a production benchmark and must not
be described as one. Legacy category labels are never used as relevance.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from career_match.data.legacy import repo_root

DEFAULT_FIXTURE = Path("data") / "evaluation" / "dev_relevance_fixture.json"

RELEVANCE_LABELS = {
    3: "strong",
    2: "moderate",
    1: "weak",
    0: "mismatch",
}


@dataclass(frozen=True)
class FixtureCandidate:
    candidate_id: str
    label: str
    relevance: int
    resume_text: str


@dataclass(frozen=True)
class FixtureQuery:
    query_id: str
    role: str
    job_text: str
    candidates: tuple[FixtureCandidate, ...]


@dataclass(frozen=True)
class EvaluationFixture:
    name: str
    kind: str
    disclaimer: str
    relevant_threshold: int
    queries: tuple[FixtureQuery, ...]

    @property
    def pair_count(self) -> int:
        return sum(len(query.candidates) for query in self.queries)


def default_fixture_path() -> Path:
    return repo_root() / DEFAULT_FIXTURE


def load_evaluation_fixture(path: Path | None = None) -> EvaluationFixture:
    """Load and validate the development evaluation fixture."""
    fixture_path = path or default_fixture_path()
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if payload.get("kind") != "development evaluation fixture":
        raise ValueError(f"{fixture_path} is not marked as a development evaluation fixture.")
    queries: list[FixtureQuery] = []
    for raw_query in payload["queries"]:
        candidates = tuple(
            FixtureCandidate(
                candidate_id=item["id"],
                label=item["label"],
                relevance=int(item["relevance"]),
                resume_text=item["resume_text"],
            )
            for item in raw_query["candidates"]
        )
        for candidate in candidates:
            expected = RELEVANCE_LABELS.get(candidate.relevance)
            if expected is None:
                raise ValueError(f"Unsupported relevance grade: {candidate.relevance}")
            if candidate.label != expected:
                raise ValueError(
                    f"{candidate.candidate_id}: label {candidate.label!r} does not "
                    f"match relevance {candidate.relevance}."
                )
        queries.append(
            FixtureQuery(
                query_id=raw_query["id"],
                role=raw_query["role"],
                job_text=raw_query["job_text"],
                candidates=candidates,
            )
        )
    return EvaluationFixture(
        name=str(payload["name"]),
        kind=str(payload["kind"]),
        disclaimer=str(payload["disclaimer"]),
        relevant_threshold=int(payload.get("relevant_threshold", 2)),
        queries=tuple(queries),
    )
