"""Discovery API tests with Adzuna provider integration."""

from __future__ import annotations

import io
import json
from unittest.mock import patch

import numpy as np
import pytest
from fastapi.testclient import TestClient
from tests.fixtures.job_opportunities import make_synthetic_jobs

from career_match.api.app import create_app
from career_match.api.auth import ClerkIdentity
from career_match.api.services import MatcherService
from career_match.jobs.adzuna import AdzunaClient
from career_match.jobs.adzuna_source import AdzunaJobSource
from career_match.jobs.sources import InMemoryJobSource
from career_match.matching.hybrid import HybridMatcher
from career_match.matching.semantic import SemanticMatcher
from career_match.persistence.store import InMemoryPersistenceStore

USER_A = ClerkIdentity(user_id="user_a", email="a@example.com", display_name="Ada")

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


def _adzuna_payload() -> dict:
    return {
        "results": [
            {
                "id": "low-fit",
                "title": "Java Enterprise Developer",
                "company": {"display_name": "Legacy Corp"},
                "location": {"display_name": "Remote"},
                "description": "Java and Spring only.",
                "redirect_url": "https://www.adzuna.com/jobs/landing/low-fit",
            },
            {
                "id": "high-fit",
                "title": "Python Backend Engineer",
                "company": {"display_name": "Acme Labs"},
                "location": {"display_name": "Austin, TX"},
                "description": "Python, FastAPI, Docker, SQL, and Git on Linux.",
                "redirect_url": "https://www.adzuna.com/jobs/landing/high-fit",
            },
        ]
    }


@pytest.fixture()
def store() -> InMemoryPersistenceStore:
    return InMemoryPersistenceStore()


@pytest.fixture()
def client(store: InMemoryPersistenceStore) -> TestClient:
    semantic = SemanticMatcher(encoder=_FixedEncoder())
    hybrid = HybridMatcher(semantic_matcher=semantic)
    service = MatcherService(semantic=semantic, hybrid=hybrid)
    adzuna_source = AdzunaJobSource(AdzunaClient(app_id="app", app_key="key", country="us"))

    application = create_app()
    application.state.persistence_store = store
    application.state.clerk_identity_override = USER_A
    application.state.matcher_service = service
    application.state.job_source_override = adzuna_source

    with TestClient(application) as test_client:
        yield test_client


def _auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}


def _create_resume(client: TestClient) -> str:
    response = client.post(
        "/api/v1/resumes",
        headers=_auth_headers(),
        json={"name": "Primary", "resume_text": PYTHON_RESUME},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_adzuna_discovery_ranks_by_career_match_not_provider_order(client: TestClient) -> None:
    resume_id = _create_resume(client)
    body = io.BytesIO(json.dumps(_adzuna_payload()).encode("utf-8"))

    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return body.getvalue()

    with patch("career_match.jobs.adzuna.urllib.request.urlopen", return_value=_FakeResponse()):
        response = client.post(
            "/api/v1/jobs/discover",
            headers=_auth_headers(),
            json={"resume_id": resume_id, "matcher": "semantic"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "adzuna"
    assert payload["search_query"]
    assert payload["candidate_count"] == 2
    assert payload["results"][0]["job"]["title"] == "Python Backend Engineer"
    assert "app_id" not in json.dumps(payload)
    assert "app_key" not in json.dumps(payload)


def test_adzuna_provider_failure_returns_honest_message(client: TestClient) -> None:
    resume_id = _create_resume(client)
    import urllib.error

    with patch(
        "career_match.jobs.adzuna.urllib.request.urlopen",
        side_effect=urllib.error.URLError("timeout"),
    ):
        response = client.post(
            "/api/v1/jobs/discover",
            headers=_auth_headers(),
            json={"resume_id": resume_id},
        )

    body = response.json()
    assert body["results"] == []
    assert (
        body["provider_message"]
        == "We're having trouble loading jobs right now. Please try again in a moment."
    )


def test_adzuna_empty_results_message(client: TestClient) -> None:
    resume_id = _create_resume(client)
    empty = io.BytesIO(json.dumps({"results": []}).encode("utf-8"))

    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return empty.getvalue()

    with patch("career_match.jobs.adzuna.urllib.request.urlopen", return_value=_FakeResponse()):
        response = client.post(
            "/api/v1/jobs/discover",
            headers=_auth_headers(),
            json={"resume_id": resume_id},
        )

    body = response.json()
    assert body["results"] == []
    assert (
        body["provider_message"]
        == "We couldn't find matching jobs for this search. "
        "Try a broader location or a different resume."
    )


def test_postgres_catalog_tests_unchanged_with_in_memory_source(
    store: InMemoryPersistenceStore,
) -> None:
    semantic = SemanticMatcher(encoder=_FixedEncoder())
    service = MatcherService(semantic=semantic)
    application = create_app()
    application.state.persistence_store = store
    application.state.clerk_identity_override = USER_A
    application.state.job_source_override = InMemoryJobSource(make_synthetic_jobs())
    application.state.matcher_service = service

    with TestClient(application) as test_client:
        response = test_client.post(
            "/api/v1/jobs/discover",
            headers=_auth_headers(),
            json={"resume_text": PYTHON_RESUME},
        )
    assert response.status_code == 200
    assert response.json()["source"] == "in-memory-fixture"
    assert len(response.json()["results"]) == 3
