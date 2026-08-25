"""Persistence API tests with in-memory store and mocked Clerk identity."""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from career_match.api.app import create_app
from career_match.api.auth import ClerkIdentity
from career_match.persistence.store import InMemoryPersistenceStore

USER_A = ClerkIdentity(user_id="user_a", email="a@example.com", display_name="Ada")
USER_B = ClerkIdentity(user_id="user_b", email="b@example.com", display_name="Bea")


@pytest.fixture()
def store() -> InMemoryPersistenceStore:
    return InMemoryPersistenceStore()


@pytest.fixture()
def client(store: InMemoryPersistenceStore) -> TestClient:
    application = create_app()
    application.state.persistence_store = store
    application.state.clerk_identity_override = USER_A
    with TestClient(application) as test_client:
        yield test_client


def _auth_headers() -> dict[str, str]:
    # Bearer present so route deps run; identity comes from app.state override.
    return {"Authorization": "Bearer test-token"}


def test_persistence_requires_auth(store: InMemoryPersistenceStore) -> None:
    application = create_app()
    application.state.persistence_store = store
    # No identity override → real auth path rejects missing bearer.
    with TestClient(application) as test_client:
        response = test_client.get("/api/v1/resumes")
    assert response.status_code == 401
    assert response.json()["detail"] == "authentication required"


def test_resume_crud(client: TestClient) -> None:
    create = client.post(
        "/api/v1/resumes",
        headers=_auth_headers(),
        json={"name": "Primary", "resume_text": "Python engineer with FastAPI."},
    )
    assert create.status_code == 201
    resume = create.json()
    resume_id = resume["id"]
    assert resume["name"] == "Primary"
    assert resume["clerk_user_id"] == USER_A.user_id

    listed = client.get("/api/v1/resumes", headers=_auth_headers())
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    got = client.get(f"/api/v1/resumes/{resume_id}", headers=_auth_headers())
    assert got.status_code == 200
    assert got.json()["resume_text"].startswith("Python")

    patched = client.patch(
        f"/api/v1/resumes/{resume_id}",
        headers=_auth_headers(),
        json={"name": "Renamed"},
    )
    assert patched.status_code == 200
    assert patched.json()["name"] == "Renamed"

    deleted = client.delete(f"/api/v1/resumes/{resume_id}", headers=_auth_headers())
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/resumes/{resume_id}", headers=_auth_headers()).status_code == 404


def test_match_create_list_get_delete(client: TestClient) -> None:
    resume = client.post(
        "/api/v1/resumes",
        headers=_auth_headers(),
        json={"name": "R1", "resume_text": "Python Docker"},
    ).json()

    create = client.post(
        "/api/v1/matches",
        headers=_auth_headers(),
        json={
            "resume_id": resume["id"],
            "job_title": "Backend Engineer",
            "company": "Acme",
            "job_description": "Need Python and Docker.",
            "matcher": "Semantic Matcher v0.1",
            "matcher_version": "0.1.0",
            "overall_score": 81.5,
            "matched_skills": ["python", "docker"],
            "missing_skills": ["kubernetes"],
            "weak_or_negated_skills": [],
            "semantic_score": 0.8,
            "tfidf_score": None,
            "skill_overlap_score": None,
            "disclaimer": "not a hiring probability",
        },
    )
    assert create.status_code == 201
    match = create.json()
    match_id = match["id"]
    assert match["overall_score"] == 81.5
    assert match["matched_skills"] == ["python", "docker"]

    listed = client.get("/api/v1/matches", headers=_auth_headers())
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    got = client.get(f"/api/v1/matches/{match_id}", headers=_auth_headers())
    assert got.status_code == 200
    assert got.json()["job_title"] == "Backend Engineer"

    deleted = client.delete(f"/api/v1/matches/{match_id}", headers=_auth_headers())
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/matches/{match_id}", headers=_auth_headers()).status_code == 404


def test_saved_jobs_crud(client: TestClient) -> None:
    create = client.post(
        "/api/v1/jobs",
        headers=_auth_headers(),
        json={
            "title": "ML Engineer",
            "company": "Orbit",
            "job_description": "Ship ranking models with Python.",
            "source_url": "https://example.com/jobs/1",
            "notes": "Good culture fit",
        },
    )
    assert create.status_code == 201
    job = create.json()
    job_id = job["id"]

    listed = client.get("/api/v1/jobs", headers=_auth_headers())
    assert listed.status_code == 200
    assert listed.json()[0]["title"] == "ML Engineer"

    patched = client.patch(
        f"/api/v1/jobs/{job_id}",
        headers=_auth_headers(),
        json={"notes": "Apply next week"},
    )
    assert patched.status_code == 200
    assert patched.json()["notes"] == "Apply next week"

    deleted = client.delete(f"/api/v1/jobs/{job_id}", headers=_auth_headers())
    assert deleted.status_code == 204


def test_ownership_isolation(store: InMemoryPersistenceStore) -> None:
    application = create_app()
    application.state.persistence_store = store
    application.state.clerk_identity_override = USER_A

    with TestClient(application) as client_a:
        resume = client_a.post(
            "/api/v1/resumes",
            headers=_auth_headers(),
            json={"name": "A resume", "resume_text": "secret-a"},
        ).json()
        match = client_a.post(
            "/api/v1/matches",
            headers=_auth_headers(),
            json={
                "job_description": "Role A",
                "matcher": "Hybrid Matcher v0.1",
                "overall_score": 50,
                "matched_skills": ["python"],
                "missing_skills": [],
                "weak_or_negated_skills": [],
            },
        ).json()
        job = client_a.post(
            "/api/v1/jobs",
            headers=_auth_headers(),
            json={
                "title": "Job A",
                "job_description": "Desc A",
            },
        ).json()

    application.state.clerk_identity_override = USER_B
    with TestClient(application) as client_b:
        assert (
            client_b.get(f"/api/v1/resumes/{resume['id']}", headers=_auth_headers()).status_code
            == 404
        )
        assert (
            client_b.patch(
                f"/api/v1/resumes/{resume['id']}",
                headers=_auth_headers(),
                json={"name": "hijack"},
            ).status_code
            == 404
        )
        assert (
            client_b.delete(
                f"/api/v1/resumes/{resume['id']}", headers=_auth_headers()
            ).status_code
            == 404
        )
        assert (
            client_b.get(f"/api/v1/matches/{match['id']}", headers=_auth_headers()).status_code
            == 404
        )
        assert (
            client_b.delete(
                f"/api/v1/matches/{match['id']}", headers=_auth_headers()
            ).status_code
            == 404
        )
        assert (
            client_b.get(f"/api/v1/jobs/{job['id']}", headers=_auth_headers()).status_code == 404
        )
        assert (
            client_b.patch(
                f"/api/v1/jobs/{job['id']}",
                headers=_auth_headers(),
                json={"title": "hijack"},
            ).status_code
            == 404
        )
        assert (
            client_b.delete(f"/api/v1/jobs/{job['id']}", headers=_auth_headers()).status_code
            == 404
        )
        assert client_b.get("/api/v1/resumes", headers=_auth_headers()).json() == []
        assert client_b.get("/api/v1/matches", headers=_auth_headers()).json() == []
        assert client_b.get("/api/v1/jobs", headers=_auth_headers()).json() == []


def test_invalid_and_missing_ids(client: TestClient) -> None:
    missing = uuid4()
    assert client.get(f"/api/v1/resumes/{missing}", headers=_auth_headers()).status_code == 404
    assert client.get(f"/api/v1/matches/{missing}", headers=_auth_headers()).status_code == 404
    assert client.get(f"/api/v1/jobs/{missing}", headers=_auth_headers()).status_code == 404
    assert client.get("/api/v1/resumes/not-a-uuid", headers=_auth_headers()).status_code == 422


def test_persistence_unavailable_maps_to_503(
    store: InMemoryPersistenceStore, monkeypatch: pytest.MonkeyPatch
) -> None:
    application = create_app()
    application.state.persistence_store = store
    application.state.clerk_identity_override = USER_A

    def _boom(*_args, **_kwargs):
        from career_match.persistence.errors import PersistenceUnavailableError

        raise PersistenceUnavailableError("down")

    monkeypatch.setattr(store, "list_resumes", _boom)
    with TestClient(application) as client:
        response = client.get("/api/v1/resumes", headers=_auth_headers())
    assert response.status_code == 503
    assert response.json()["detail"] == "persistence service unavailable"
    assert "Traceback" not in response.text


def test_match_rejects_foreign_resume_id(store: InMemoryPersistenceStore) -> None:
    application = create_app()
    application.state.persistence_store = store
    application.state.clerk_identity_override = USER_A
    with TestClient(application) as client_a:
        resume = client_a.post(
            "/api/v1/resumes",
            headers=_auth_headers(),
            json={"name": "A", "resume_text": "text"},
        ).json()

    application.state.clerk_identity_override = USER_B
    with TestClient(application) as client_b:
        response = client_b.post(
            "/api/v1/matches",
            headers=_auth_headers(),
            json={
                "resume_id": resume["id"],
                "job_description": "Role",
                "matcher": "Lexical",
                "overall_score": 10,
                "matched_skills": [],
                "missing_skills": [],
                "weak_or_negated_skills": [],
            },
        )
    assert response.status_code == 404
