"""Tests for multi-query job retrieval, deduplication, and ranking."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import numpy as np
import pytest
from fastapi.testclient import TestClient

from career_match.api.app import create_app
from career_match.api.auth import ClerkIdentity
from career_match.api.services import MatcherService
from career_match.jobs.protocol import JobOpportunity, JobSource
from career_match.jobs.query_builder import JobSearchQuery
from career_match.matching.semantic import SemanticMatcher
from career_match.persistence.store import InMemoryPersistenceStore

USER_A = ClerkIdentity(user_id="user_a", email="a@example.com", display_name="Ada")
_NOW = datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC)

ML_RESUME = (
    "Jordan Lee\nMachine Learning Engineer\n\n"
    "Built PyTorch models, scikit-learn pipelines, and model evaluation tooling."
)


class _FixedEncoder:
    def encode(self, texts):
        rows = []
        for text in texts:
            vec = np.zeros(4, dtype=np.float32)
            lowered = text.lower()
            vec[0] = 1.0 if "pytorch" in lowered or "machine learning" in lowered else 0.2
            vec[1] = 1.0 if "python" in lowered else 0.1
            vec[2] = 0.5
            vec[3] = min(1.0, len(text) / 400.0)
            rows.append(vec)
        matrix = np.vstack(rows)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        return matrix / np.clip(norms, 1e-12, None)


class _RecordingJobSource:
    name = "recording-fixture"

    def __init__(self, responses: dict[str, list[JobOpportunity]]) -> None:
        self._responses = responses
        self.calls: list[str] = []

    def list_opportunities(
        self,
        *,
        search_query: str | None = None,
        location: str | None = None,
        employment_type: str | None = None,
        limit: int | None = None,
    ) -> list[JobOpportunity]:
        del location, employment_type, limit
        query = (search_query or "").strip().lower()
        self.calls.append(query)
        return list(self._responses.get(query, []))


def _job(
    *,
    job_id: str,
    title: str,
    description: str,
    source_url: str,
) -> JobOpportunity:
    return JobOpportunity(
        id=UUID(job_id),
        title=title,
        company="Fixture Co",
        location="Remote",
        description=description,
        source="recording-fixture",
        source_url=source_url,
        apply_url=None,
        employment_type="full-time",
        created_at=_NOW,
        updated_at=_NOW,
    )


@pytest.fixture()
def store() -> InMemoryPersistenceStore:
    return InMemoryPersistenceStore()


def _client(store: InMemoryPersistenceStore, job_source: JobSource) -> TestClient:
    semantic = SemanticMatcher(encoder=_FixedEncoder())
    service = MatcherService(semantic=semantic)
    application = create_app()
    application.state.persistence_store = store
    application.state.clerk_identity_override = USER_A
    application.state.job_source_override = job_source
    application.state.matcher_service = service
    return TestClient(application)


def test_discovery_fetches_multiple_role_queries(store: InMemoryPersistenceStore) -> None:
    source = _RecordingJobSource(
        {
            "machine learning engineer": [
                _job(
                    job_id="00000000-0000-4000-8000-000000000001",
                    title="ML Engineer",
                    description="PyTorch and machine learning platform work.",
                    source_url="https://example.test/jobs/ml",
                )
            ],
            "applied ai engineer": [
                _job(
                    job_id="00000000-0000-4000-8000-000000000002",
                    title="Applied AI Engineer",
                    description="Python services with some unrelated wording.",
                    source_url="https://example.test/jobs/ai",
                )
            ],
        }
    )
    with _client(store, source) as client:
        response = client.post(
            "/api/v1/jobs/discover",
            headers={"Authorization": "Bearer test-token"},
            json={"resume_text": ML_RESUME, "matcher": "semantic"},
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["search_queries"]
    assert len(source.calls) >= 2
    assert payload["candidate_count"] == 2


def test_discovery_deduplicates_jobs_by_source_url(store: InMemoryPersistenceStore) -> None:
    duplicate = _job(
        job_id="00000000-0000-4000-8000-000000000003",
        title="Duplicate ML Role",
        description="PyTorch machine learning role.",
        source_url="https://example.test/jobs/shared",
    )
    source = _RecordingJobSource(
        {
            "machine learning engineer": [duplicate],
            "applied ai engineer": [duplicate],
        }
    )
    with _client(store, source) as client:
        response = client.post(
            "/api/v1/jobs/discover",
            headers={"Authorization": "Bearer test-token"},
            json={"resume_text": ML_RESUME},
        )
    assert response.status_code == 200
    assert response.json()["candidate_count"] == 1


def test_discovery_ranks_by_career_match_score_not_provider_order(
    store: InMemoryPersistenceStore,
) -> None:
    source = _RecordingJobSource(
        {
            "machine learning engineer": [
                _job(
                    job_id="00000000-0000-4000-8000-000000000004",
                    title="Low Fit",
                    description="Java enterprise middleware only.",
                    source_url="https://example.test/jobs/low",
                )
            ],
            "applied ai engineer": [
                _job(
                    job_id="00000000-0000-4000-8000-000000000005",
                    title="High Fit",
                    description="PyTorch machine learning platform with Python.",
                    source_url="https://example.test/jobs/high",
                )
            ],
        }
    )
    with _client(store, source) as client:
        response = client.post(
            "/api/v1/jobs/discover",
            headers={"Authorization": "Bearer test-token"},
            json={"resume_text": ML_RESUME, "matcher": "semantic"},
        )
    payload = response.json()
    assert payload["results"][0]["job"]["title"] == "High Fit"


def test_query_broadening_fallback_used_when_primary_query_empty(
    store: InMemoryPersistenceStore,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _RecordingJobSource(
        {
            "data scientist python": [],
            "data scientist": [
                _job(
                    job_id="00000000-0000-4000-8000-000000000006",
                    title="Data Scientist",
                    description="Python pandas machine learning analysis.",
                    source_url="https://example.test/jobs/ds",
                )
            ],
        }
    )
    monkeypatch.setattr(
        "career_match.api.job_discovery_service.build_job_search_queries",
        lambda _resume: type(
            "Plan",
            (),
            {
                "queries": (
                    JobSearchQuery(
                        text="data scientist python",
                        role_key="data_scientist",
                        broaden_text="data scientist",
                    ),
                ),
                "primary": JobSearchQuery(
                    text="data scientist python",
                    role_key="data_scientist",
                    broaden_text="data scientist",
                ),
            },
        )(),
    )
    with _client(store, source) as client:
        response = client.post(
            "/api/v1/jobs/discover",
            headers={"Authorization": "Bearer test-token"},
            json={
                "resume_text": "Jamie Fox\nData Scientist\nPython pandas SQL statistical modeling.",
            },
        )
    assert response.status_code == 200
    assert "data scientist python" in source.calls
    assert "data scientist" in source.calls
    assert response.json()["candidate_count"] == 1
