"""End-to-end integration tests for high-risk product handoffs."""

from __future__ import annotations

import io

import numpy as np
import pytest
from docx import Document
from fastapi.testclient import TestClient

from career_match.api.app import create_app
from career_match.api.auth import ClerkIdentity
from career_match.api.services import MatcherService
from career_match.jobs.sources import InMemoryJobSource
from career_match.matching.hybrid import HybridMatcher
from career_match.matching.semantic import SemanticMatcher
from career_match.persistence.store import InMemoryPersistenceStore
from career_match.tailoring.protocol import RewriteSuggestion
from career_match.tailoring.providers import FakeRewriteProvider

USER_A = ClerkIdentity(user_id="user_a", email="a@example.com", display_name="Ada")
USER_B = ClerkIdentity(user_id="user_b", email="b@example.com", display_name="Bea")

RESUME = (
    "Jordan Lee\nBackend Engineer\n\n"
    "Experience\n"
    "Built GitHub Actions pipelines for automated testing and deployment. "
    "Python, FastAPI, Docker, SQL, and Git on Linux.\n\n"
    "Skills: Python, FastAPI, Docker, SQL, Git"
)

CI_JOB = "Platform Engineer\n\nLooking for CI/CD experience and Python services on Linux."

GOOD_SUGGESTION = RewriteSuggestion(
    section="experience",
    original_text="Built GitHub Actions pipelines for automated testing and deployment.",
    suggested_text="Built GitHub Actions pipelines for CI/CD and automated testing and deployment.",
    keywords_introduced=("ci/cd",),
    support_reason="equivalent evidence",
    support_level="high",
)


class _FixedEncoder:
    def encode(self, texts):
        rows = []
        for text in texts:
            vec = np.zeros(4, dtype=np.float32)
            lowered = text.lower()
            vec[0] = 1.0 if "python" in lowered else 0.2
            vec[1] = 1.0 if "docker" in lowered else 0.1
            vec[2] = 1.0 if "ci/cd" in lowered or "github actions" in lowered else 0.2
            vec[3] = min(1.0, len(text) / 400.0)
            rows.append(vec)
        matrix = np.vstack(rows)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        return matrix / np.clip(norms, 1e-12, None)


@pytest.fixture()
def store() -> InMemoryPersistenceStore:
    return InMemoryPersistenceStore()


@pytest.fixture()
def client(store: InMemoryPersistenceStore) -> TestClient:
    from tests.fixtures.job_opportunities import make_synthetic_jobs

    semantic = SemanticMatcher(encoder=_FixedEncoder())
    hybrid = HybridMatcher(semantic_matcher=semantic)
    service = MatcherService(semantic=semantic, hybrid=hybrid)

    application = create_app()
    application.state.persistence_store = store
    application.state.clerk_identity_override = USER_A
    application.state.matcher_service = service
    application.state.job_source_override = InMemoryJobSource(make_synthetic_jobs())
    application.state.rewrite_provider_override = FakeRewriteProvider((GOOD_SUGGESTION,))

    with TestClient(application) as test_client:
        yield test_client


def _auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}


def test_saved_resume_to_discovery_to_tailor_apply_export(client: TestClient) -> None:
    create = client.post(
        "/api/v1/resumes",
        headers=_auth_headers(),
        json={"name": "Primary", "resume_text": RESUME},
    )
    assert create.status_code == 201
    resume_id = create.json()["id"]

    discover = client.post(
        "/api/v1/jobs/discover",
        headers=_auth_headers(),
        json={"resume_id": resume_id, "matcher": "semantic"},
    )
    assert discover.status_code == 200
    assert discover.json()["results"]

    tailor = client.post(
        "/api/v1/resumes/tailor",
        headers=_auth_headers(),
        json={
            "resume_id": resume_id,
            "job_description": CI_JOB,
            "matcher": "semantic",
        },
    )
    assert tailor.status_code == 200
    suggestion_id = tailor.json()["rewrite_suggestions"][0]["suggestion_id"]

    apply = client.post(
        "/api/v1/resumes/tailor/apply",
        headers=_auth_headers(),
        json={
            "resume_id": resume_id,
            "job_description": CI_JOB,
            "accepted_suggestion_ids": [suggestion_id],
            "matcher": "semantic",
        },
    )
    assert apply.status_code == 200
    assert apply.json()["alignment_delta"] >= 0

    export = client.post(
        "/api/v1/resumes/export",
        headers=_auth_headers(),
        json={
            "resume_id": resume_id,
            "job_description": CI_JOB,
            "accepted_suggestion_ids": [suggestion_id],
            "format": "docx",
        },
    )
    assert export.status_code == 200
    document = Document(io.BytesIO(export.content))
    assert any("Jordan" in paragraph.text for paragraph in document.paragraphs)

    stored = client.get(f"/api/v1/resumes/{resume_id}", headers=_auth_headers())
    assert stored.json()["resume_text"] == RESUME


def test_tailor_with_resume_text_without_saved_id(client: TestClient) -> None:
    response = client.post(
        "/api/v1/resumes/tailor",
        headers=_auth_headers(),
        json={"resume_text": RESUME, "job_description": CI_JOB},
    )
    assert response.status_code == 200
    assert response.json()["resume_id"] is None


def test_discover_empty_catalog(client: TestClient) -> None:
    client.app.state.job_source_override = InMemoryJobSource(())
    create = client.post(
        "/api/v1/resumes",
        headers=_auth_headers(),
        json={"name": "Primary", "resume_text": RESUME},
    )
    resume_id = create.json()["id"]
    response = client.post(
        "/api/v1/jobs/discover",
        headers=_auth_headers(),
        json={"resume_id": resume_id},
    )
    assert response.status_code == 200
    assert response.json()["results"] == []


def test_cross_user_saved_job_rejected_for_tailor(client: TestClient) -> None:
    job = client.post(
        "/api/v1/jobs",
        headers=_auth_headers(),
        json={"title": "Role", "company": "Acme", "job_description": CI_JOB},
    )
    job_id = job.json()["id"]
    client.app.state.clerk_identity_override = USER_B
    response = client.post(
        "/api/v1/resumes/tailor",
        headers=_auth_headers(),
        json={"resume_text": RESUME, "job_id": job_id},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "job not found"


def test_cross_user_export_rejected(client: TestClient) -> None:
    create = client.post(
        "/api/v1/resumes",
        headers=_auth_headers(),
        json={"name": "Primary", "resume_text": RESUME},
    )
    resume_id = create.json()["id"]
    tailor = client.post(
        "/api/v1/resumes/tailor",
        headers=_auth_headers(),
        json={"resume_id": resume_id, "job_description": CI_JOB},
    )
    suggestion_id = tailor.json()["rewrite_suggestions"][0]["suggestion_id"]
    client.app.state.clerk_identity_override = USER_B
    response = client.post(
        "/api/v1/resumes/export",
        headers=_auth_headers(),
        json={
            "resume_id": resume_id,
            "job_description": CI_JOB,
            "accepted_suggestion_ids": [suggestion_id],
            "format": "txt",
        },
    )
    assert response.status_code == 404


def test_persistence_routes_return_503_when_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    from career_match.persistence.database import reset_database_cache

    reset_database_cache()
    application = create_app()
    application.state.clerk_identity_override = USER_A
    with TestClient(application) as test_client:
        response = test_client.get("/api/v1/resumes", headers=_auth_headers())
    assert response.status_code == 503
    assert response.json()["detail"] == "persistence is not configured"
