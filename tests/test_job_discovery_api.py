"""API tests for authenticated job discovery and ranking."""

from __future__ import annotations

import numpy as np
import pytest
from fastapi.testclient import TestClient
from tests.fixtures.job_opportunities import make_extra_job, make_synthetic_jobs

from career_match.api.app import create_app
from career_match.api.auth import ClerkIdentity
from career_match.api.services import MatcherService
from career_match.jobs.sources import InMemoryJobSource
from career_match.matching.hybrid import HybridMatcher
from career_match.matching.semantic import SemanticMatcher
from career_match.persistence.store import InMemoryPersistenceStore

USER_A = ClerkIdentity(user_id="user_a", email="a@example.com", display_name="Ada")
USER_B = ClerkIdentity(user_id="user_b", email="b@example.com", display_name="Bea")

PYTHON_RESUME = (
    "Jordan Lee\nPython engineer with FastAPI, Docker, SQL, pandas, and Git. "
    "Built production services on Linux."
)


class _FixedEncoder:
    def encode(self, texts):
        rows = []
        for text in texts:
            vec = np.zeros(4, dtype=np.float32)
            lowered = text.lower()
            vec[0] = 1.0 if "python" in lowered else 0.2
            vec[1] = 1.0 if "docker" in lowered else 0.1
            vec[2] = 0.5
            vec[3] = min(1.0, len(text) / 400.0)
            rows.append(vec)
        matrix = np.vstack(rows)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        return matrix / np.clip(norms, 1e-12, None)


@pytest.fixture()
def store() -> InMemoryPersistenceStore:
    return InMemoryPersistenceStore()


@pytest.fixture()
def job_source() -> InMemoryJobSource:
    return InMemoryJobSource(make_synthetic_jobs())


@pytest.fixture()
def client(
    store: InMemoryPersistenceStore,
    job_source: InMemoryJobSource,
) -> TestClient:
    semantic = SemanticMatcher(encoder=_FixedEncoder())
    hybrid = HybridMatcher(semantic_matcher=semantic)
    service = MatcherService(semantic=semantic, hybrid=hybrid)

    application = create_app()
    application.state.persistence_store = store
    application.state.clerk_identity_override = USER_A
    application.state.job_source_override = job_source
    application.state.matcher_service = service

    with TestClient(application) as test_client:
        yield test_client


def _auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}


def _create_resume(client: TestClient, text: str = PYTHON_RESUME) -> str:
    response = client.post(
        "/api/v1/resumes",
        headers=_auth_headers(),
        json={"name": "Primary", "resume_text": text},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_discover_requires_authentication(store: InMemoryPersistenceStore) -> None:
    application = create_app()
    application.state.persistence_store = store
    with TestClient(application) as test_client:
        response = test_client.post(
            "/api/v1/jobs/discover",
            json={"resume_text": PYTHON_RESUME},
        )
    assert response.status_code == 401


def test_discover_ranks_multiple_jobs_descending(client: TestClient) -> None:
    resume_id = _create_resume(client)
    response = client.post(
        "/api/v1/jobs/discover",
        headers=_auth_headers(),
        json={"resume_id": resume_id, "matcher": "semantic"},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["results"]) == 3
    scores = [item["overall_score"] for item in body["results"]]
    assert scores == sorted(scores, reverse=True)
    titles = [item["job"]["title"] for item in body["results"]]
    assert "Python Backend Engineer" in titles
    assert "Remote Python Data Engineer" in titles
    assert body["source"] == "in-memory-fixture"
    assert "not a hiring probability" in body["disclaimer"].lower()


def test_discover_includes_explainability_fields(client: TestClient) -> None:
    resume_id = _create_resume(client)
    response = client.post(
        "/api/v1/jobs/discover",
        headers=_auth_headers(),
        json={"resume_id": resume_id, "matcher": "semantic"},
    )
    top = response.json()["results"][0]
    assert top["matcher"]
    assert top["matcher_version"]
    assert isinstance(top["matched_skills"], list)
    assert isinstance(top["missing_skills"], list)
    assert isinstance(top["weak_or_negated_skills"], list)
    assert top["semantic_score"] is not None
    assert top["job"]["title"]
    assert top["job"]["company"]


def test_discover_rejects_foreign_resume(client: TestClient) -> None:
    resume_id = _create_resume(client)
    client.app.state.clerk_identity_override = USER_B
    response = client.post(
        "/api/v1/jobs/discover",
        headers=_auth_headers(),
        json={"resume_id": resume_id},
    )
    assert response.status_code == 404


def test_discover_accepts_resume_text_without_id(client: TestClient) -> None:
    response = client.post(
        "/api/v1/jobs/discover",
        headers=_auth_headers(),
        json={"resume_text": PYTHON_RESUME},
    )
    assert response.status_code == 200
    assert response.json()["resume_id"] is None
    assert len(response.json()["results"]) == 3


def test_discover_empty_provider_returns_no_results(
    store: InMemoryPersistenceStore,
) -> None:
    semantic = SemanticMatcher(encoder=_FixedEncoder())
    service = MatcherService(semantic=semantic)

    application = create_app()
    application.state.persistence_store = store
    application.state.clerk_identity_override = USER_A
    application.state.job_source_override = InMemoryJobSource([])
    application.state.matcher_service = service

    with TestClient(application) as test_client:
        response = test_client.post(
            "/api/v1/jobs/discover",
            headers=_auth_headers(),
            json={"resume_text": PYTHON_RESUME},
        )
    assert response.status_code == 200
    assert response.json()["results"] == []


def test_discover_respects_limit(client: TestClient) -> None:
    resume_id = _create_resume(client)
    response = client.post(
        "/api/v1/jobs/discover",
        headers=_auth_headers(),
        json={"resume_id": resume_id, "limit": 1, "matcher": "semantic"},
    )
    assert response.status_code == 200
    assert len(response.json()["results"]) == 1


def test_discover_location_filter(client: TestClient, job_source: InMemoryJobSource) -> None:
    job_source._opportunities.append(make_extra_job())
    resume_id = _create_resume(client)
    response = client.post(
        "/api/v1/jobs/discover",
        headers=_auth_headers(),
        json={"resume_id": resume_id, "location": "Austin"},
    )
    titles = [item["job"]["title"] for item in response.json()["results"]]
    assert titles == ["Placeholder Job"]


def test_saved_job_crud_unchanged(client: TestClient) -> None:
    create = client.post(
        "/api/v1/jobs",
        headers=_auth_headers(),
        json={
            "title": "Saved role",
            "company": "Acme",
            "job_description": "Need Python and SQL.",
        },
    )
    assert create.status_code == 201
    job_id = create.json()["id"]
    got = client.get(f"/api/v1/jobs/{job_id}", headers=_auth_headers())
    assert got.status_code == 200
    assert got.json()["title"] == "Saved role"


def test_match_endpoint_unchanged(client: TestClient) -> None:
    response = client.post(
        "/api/v1/match",
        json={
            "resume_text": PYTHON_RESUME,
            "job_description": "Need Python and Docker.",
        },
    )
    assert response.status_code == 200
    assert 0 <= response.json()["overall_score"] <= 100


def test_discover_does_not_accept_client_user_id(client: TestClient) -> None:
    resume_id = _create_resume(client)
    response = client.post(
        "/api/v1/jobs/discover",
        headers=_auth_headers(),
        json={
            "resume_id": resume_id,
            "clerk_user_id": "attacker",
        },
    )
    assert response.status_code == 200
    assert response.json()["resume_id"] == resume_id


def test_production_job_source_reads_empty_catalog(store: InMemoryPersistenceStore) -> None:
    """Postgres catalog path returns no jobs when the table/catalog is empty."""
    semantic = SemanticMatcher(encoder=_FixedEncoder())
    service = MatcherService(semantic=semantic)

    application = create_app()
    application.state.persistence_store = store
    application.state.clerk_identity_override = USER_A
    application.state.matcher_service = service

    with TestClient(application) as test_client:
        response = test_client.post(
            "/api/v1/jobs/discover",
            headers=_auth_headers(),
            json={"resume_text": PYTHON_RESUME},
        )
    assert response.status_code == 200
    assert response.json()["source"] == "postgres-catalog"
    assert response.json()["results"] == []
