"""Tests for grounded resume tailoring."""

from __future__ import annotations

import numpy as np
import pytest
from fastapi.testclient import TestClient

from career_match.api.app import create_app
from career_match.api.auth import ClerkIdentity
from career_match.api.services import MatcherService
from career_match.matching.hybrid import HybridMatcher
from career_match.matching.semantic import SemanticMatcher
from career_match.persistence.store import InMemoryPersistenceStore
from career_match.tailoring.evidence_map import build_evidence_map
from career_match.tailoring.protocol import RewriteSuggestion
from career_match.tailoring.providers import FakeRewriteProvider
from career_match.tailoring.validation import filter_valid_suggestions

USER_A = ClerkIdentity(user_id="user_a", email="a@example.com", display_name="Ada")
USER_B = ClerkIdentity(user_id="user_b", email="b@example.com", display_name="Bea")

PYTHON_RESUME = (
    "Jordan Lee\nBackend Engineer\n\n"
    "Built GitHub Actions pipelines for automated testing and deployment. "
    "Python, FastAPI, Docker, SQL, and Git on Linux.\n\n"
    "Skills: Python, FastAPI, Docker, SQL, Git"
)

AWS_JOB = (
    "Senior Backend Engineer\n\n"
    "Required: Python, FastAPI, Docker, AWS, CI/CD, Kubernetes.\n"
    "Must have production deployment experience."
)

CI_CD_JOB = (
    "Platform Engineer\n\n"
    "Looking for CI/CD experience and Python services on Linux."
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
def client(store: InMemoryPersistenceStore) -> TestClient:
    semantic = SemanticMatcher(encoder=_FixedEncoder())
    hybrid = HybridMatcher(semantic_matcher=semantic)
    service = MatcherService(semantic=semantic, hybrid=hybrid)

    application = create_app()
    application.state.persistence_store = store
    application.state.clerk_identity_override = USER_A
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


def test_supported_keyword_introduction_for_equivalent_ci_cd() -> None:
    evidence = build_evidence_map(PYTHON_RESUME, CI_CD_JOB)
    ci_entry = next(item for item in evidence.requirements if item.requirement == "ci/cd")
    assert ci_entry.status == "equivalent"
    assert ci_entry.supporting_text is not None
    assert "github actions" in ci_entry.supporting_text.lower()


def test_unsupported_aws_is_rejected() -> None:
    evidence = build_evidence_map(PYTHON_RESUME, AWS_JOB)
    aws_entry = next(item for item in evidence.requirements if item.requirement == "aws")
    assert aws_entry.status == "unsupported"
    assert "aws" in evidence.unsupported_keywords


def test_negated_skill_remains_unsupported() -> None:
    resume = (
        "API engineer with Python and Git. No production Docker experience. "
        "Skills: Python, Docker, Git"
    )
    job = "Need Python and Docker in production."
    evidence = build_evidence_map(resume, job)
    docker_entry = next(item for item in evidence.requirements if item.requirement == "docker")
    assert docker_entry.status == "negated"
    assert "docker" in evidence.unsupported_keywords


def test_partial_evidence_classified() -> None:
    resume = "Reliability engineer.\n\nSkills: Python, Docker, Kubernetes"
    job = "Need Python, Docker, and Kubernetes."
    evidence = build_evidence_map(resume, job)
    python_entry = next(item for item in evidence.requirements if item.requirement == "python")
    assert python_entry.status == "partial"
    assert "python" in evidence.partial_requirements


def test_validation_rejects_fabricated_technology() -> None:
    bad = RewriteSuggestion(
        section="experience",
        original_text="Built Python APIs.",
        suggested_text="Built Python APIs on AWS with 10 years experience.",
        keywords_introduced=("aws",),
        support_reason="fake",
        support_level="low",
    )
    filtered = filter_valid_suggestions((bad,), ("aws",))
    assert filtered == ()


def test_tailor_endpoint_requires_auth(store: InMemoryPersistenceStore) -> None:
    application = create_app()
    application.state.persistence_store = store
    with TestClient(application) as test_client:
        response = test_client.post(
            "/api/v1/resumes/tailor",
            json={"resume_text": PYTHON_RESUME, "job_description": AWS_JOB},
        )
    assert response.status_code == 401


def test_tailor_cross_user_resume_rejected(client: TestClient) -> None:
    resume_id = _create_resume(client)
    client.app.state.clerk_identity_override = USER_B
    response = client.post(
        "/api/v1/resumes/tailor",
        headers=_auth_headers(),
        json={"resume_id": resume_id, "job_description": AWS_JOB},
    )
    assert response.status_code == 404


def test_tailor_returns_structured_response(client: TestClient) -> None:
    resume_id = _create_resume(client)
    response = client.post(
        "/api/v1/resumes/tailor",
        headers=_auth_headers(),
        json={"resume_id": resume_id, "job_description": CI_CD_JOB, "matcher": "semantic"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "original_alignment_score" in body
    assert body["supported_keywords"]
    assert "ci/cd" in [item["requirement"] for item in body["evidence_map"]]
    assert body["rewrite_generation_available"] is True
    assert body["llm_rewrite_available"] is False
    assert any("LLM rewrite generation is not configured" in w for w in body["warnings"])
    assert "does not guarantee ats passage" in body["disclaimer"].lower()


def test_tailor_warns_on_unsupported_aws(client: TestClient) -> None:
    resume_id = _create_resume(client)
    response = client.post(
        "/api/v1/resumes/tailor",
        headers=_auth_headers(),
        json={"resume_id": resume_id, "job_description": AWS_JOB},
    )
    body = response.json()
    assert any("do not add: aws" in warning.lower() for warning in body["warnings"])
    for suggestion in body["rewrite_suggestions"]:
        assert "aws" not in suggestion["suggested_text"].lower()


def test_tailor_uses_existing_matcher_service(client: TestClient) -> None:
    resume_id = _create_resume(client)
    response = client.post(
        "/api/v1/resumes/tailor",
        headers=_auth_headers(),
        json={"resume_id": resume_id, "job_description": CI_CD_JOB, "matcher": "semantic"},
    )
    body = response.json()
    assert body["matcher"]
    assert 0 <= body["original_alignment_score"] <= 100


def test_fake_rewrite_provider_injection(client: TestClient) -> None:
    fake = FakeRewriteProvider(
        (
            RewriteSuggestion(
                section="experience",
                original_text="Built GitHub Actions pipelines.",
                suggested_text="Built GitHub Actions pipelines for CI/CD.",
                keywords_introduced=("ci/cd",),
                support_reason="equivalent evidence",
                support_level="high",
            ),
        )
    )
    client.app.state.rewrite_provider_override = fake
    resume_id = _create_resume(client)
    response = client.post(
        "/api/v1/resumes/tailor",
        headers=_auth_headers(),
        json={"resume_id": resume_id, "job_description": CI_CD_JOB},
    )
    body = response.json()
    assert len(body["rewrite_suggestions"]) >= 1
    assert body["rewrite_suggestions"][0]["keywords_introduced"] == ["ci/cd"]
    assert "suggestion_id" in body["rewrite_suggestions"][0]


def test_match_endpoint_unchanged(client: TestClient) -> None:
    response = client.post(
        "/api/v1/match",
        json={"resume_text": PYTHON_RESUME, "job_description": CI_CD_JOB},
    )
    assert response.status_code == 200


def test_saved_job_flow_unchanged(client: TestClient) -> None:
    create = client.post(
        "/api/v1/jobs",
        headers=_auth_headers(),
        json={"title": "Role", "company": "Acme", "job_description": AWS_JOB},
    )
    assert create.status_code == 201
    job_id = create.json()["id"]
    resume_id = _create_resume(client)
    tailor = client.post(
        "/api/v1/resumes/tailor",
        headers=_auth_headers(),
        json={"resume_id": resume_id, "job_id": job_id},
    )
    assert tailor.status_code == 200
