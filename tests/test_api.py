"""API tests for Career Match FastAPI service.

Semantic/hybrid paths use a lightweight fake encoder so MiniLM is not
downloaded during the unit suite. Lexical scoring uses the real baseline.
"""

from __future__ import annotations

import numpy as np
import pytest
from fastapi.testclient import TestClient

from career_match.api.app import create_app
from career_match.api.services import MatcherService
from career_match.api.settings import MAX_TEXT_CHARS, SCORE_DISCLAIMER
from career_match.matching.hybrid import HybridMatcher
from career_match.matching.semantic import SemanticMatcher


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
def client() -> TestClient:
    semantic = SemanticMatcher(encoder=_FixedEncoder())
    hybrid = HybridMatcher(semantic_matcher=semantic)
    service = MatcherService(semantic=semantic, hybrid=hybrid)
    application = create_app()

    @application.middleware("http")
    async def _inject_service(request, call_next):
        request.app.state.matcher_service = service
        return await call_next(request)

    # Lifespan also sets a service; override after startup via dependency on state
    with TestClient(application) as test_client:
        test_client.app.state.matcher_service = service
        yield test_client


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_default_matcher_is_semantic(client: TestClient) -> None:
    response = client.post(
        "/api/v1/match",
        json={
            "resume_text": "Python developer with Docker and Git.",
            "job_description": "Looking for Python and Docker experience.",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["matcher"] == "Semantic Matcher v0.1"
    assert 0 <= body["overall_score"] <= 100
    assert body["semantic_score"] is not None
    assert body["disclaimer"] == SCORE_DISCLAIMER


def test_semantic_match_succeeds(client: TestClient) -> None:
    response = client.post(
        "/api/v1/match",
        json={
            "resume_text": "Python engineer shipping APIs.",
            "job_description": "Python backend role.",
            "matcher": "semantic",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["matcher"].startswith("Semantic")
    assert "matched_skills" in body
    assert "missing_skills" in body
    assert body["tfidf_score"] is None
    assert body["skill_overlap_score"] is None


def test_lexical_match_succeeds(client: TestClient) -> None:
    response = client.post(
        "/api/v1/match",
        json={
            "resume_text": "Python FastAPI Docker Git Linux.",
            "job_description": "Backend Engineer using Python, FastAPI, Docker, and Git.",
            "matcher": "lexical",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["matcher"].startswith("Baseline")
    assert body["tfidf_score"] is not None
    assert body["skill_overlap_score"] is not None
    assert body["matched_skills"]
    assert 0 <= body["overall_score"] <= 100


def test_hybrid_match_succeeds(client: TestClient) -> None:
    response = client.post(
        "/api/v1/match",
        json={
            "resume_text": "Python FastAPI Docker Git on Linux services.",
            "job_description": "Backend Engineer using Python, FastAPI, Docker, and Git.",
            "matcher": "hybrid",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["matcher"].startswith("Hybrid")
    assert body["semantic_score"] is not None
    assert body["tfidf_score"] is not None
    assert body["skill_overlap_score"] is not None
    assert isinstance(body["weak_or_negated_skills"], list)


def test_empty_resume_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/match",
        json={
            "resume_text": "   ",
            "job_description": "Python role",
            "matcher": "lexical",
        },
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_empty_job_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/match",
        json={
            "resume_text": "Python developer",
            "job_description": "",
            "matcher": "lexical",
        },
    )
    assert response.status_code == 422


def test_invalid_matcher_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/match",
        json={
            "resume_text": "Python developer",
            "job_description": "Python role",
            "matcher": "magic",
        },
    )
    assert response.status_code == 422


def test_oversized_text_rejected(client: TestClient) -> None:
    huge = "a" * (MAX_TEXT_CHARS + 1)
    response = client.post(
        "/api/v1/match",
        json={
            "resume_text": huge,
            "job_description": "Python role",
            "matcher": "lexical",
        },
    )
    assert response.status_code == 422


def test_weak_or_negated_skills_when_applicable(client: TestClient) -> None:
    response = client.post(
        "/api/v1/match",
        json={
            "resume_text": (
                "Python and Git locally. No production Docker experience. "
                "Skills: Python, Docker, Git"
            ),
            "job_description": "Needs Python, Docker, and Git.",
            "matcher": "hybrid",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "docker" in body["weak_or_negated_skills"]


def test_matcher_service_reused_across_requests(client: TestClient) -> None:
    first = client.app.state.matcher_service
    client.post(
        "/api/v1/match",
        json={
            "resume_text": "Python developer",
            "job_description": "Python role",
            "matcher": "lexical",
        },
    )
    second = client.app.state.matcher_service
    assert first is second
    assert first.lexical is second.lexical


def test_import_does_not_require_minilm() -> None:
    from career_match.api.app import app

    assert app.title == "Career Match API"
