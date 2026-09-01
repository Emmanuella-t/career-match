"""API tests for authenticated resume file parsing."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from tests.fixtures.resume_files import make_blank_pdf, make_docx, make_text_pdf

from career_match.api.app import create_app
from career_match.api.auth import ClerkIdentity
from career_match.api.settings import MAX_RESUME_FILE_BYTES
from career_match.persistence.store import InMemoryPersistenceStore

USER_A = ClerkIdentity(user_id="user_a", email="a@example.com", display_name="Ada")


@pytest.fixture()
def client() -> TestClient:
    application = create_app()
    application.state.persistence_store = InMemoryPersistenceStore()
    application.state.clerk_identity_override = USER_A
    with TestClient(application) as test_client:
        yield test_client


def _auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}


def test_parse_resume_requires_authentication() -> None:
    application = create_app()
    with TestClient(application) as test_client:
        response = test_client.post(
            "/api/v1/resumes/parse",
            files={"file": ("resume.pdf", make_text_pdf("Python"), "application/pdf")},
        )
    assert response.status_code == 401
    assert response.json()["detail"] == "authentication required"


def test_parse_works_without_database_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Parsing must not depend on Neon persistence being configured."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    from career_match.persistence.database import reset_database_cache

    reset_database_cache()
    application = create_app()
    application.state.clerk_identity_override = USER_A
    with TestClient(application) as test_client:
        response = test_client.post(
            "/api/v1/resumes/parse",
            headers=_auth_headers(),
            files={
                "file": (
                    "resume.pdf",
                    make_text_pdf("Python engineer with Docker."),
                    "application/pdf",
                )
            },
        )
    assert response.status_code == 200
    assert "Python engineer" in response.json()["extracted_text"]


def test_parse_valid_pdf(client: TestClient) -> None:
    response = client.post(
        "/api/v1/resumes/parse",
        headers=_auth_headers(),
        files={
            "file": (
                "resume.pdf",
                make_text_pdf("Python engineer with Docker and Git."),
                "application/pdf",
            )
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["file_type"] == "pdf"
    assert body["filename"] == "resume.pdf"
    assert "Python engineer" in body["extracted_text"]
    assert body["character_count"] == len(body["extracted_text"])


def test_parse_valid_docx(client: TestClient) -> None:
    response = client.post(
        "/api/v1/resumes/parse",
        headers=_auth_headers(),
        files={
            "file": (
                "resume.docx",
                make_docx("Jordan Lee\n\nPython and SQL experience."),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["file_type"] == "docx"
    assert "Jordan Lee" in body["extracted_text"]


def test_parse_rejects_unsupported_file_type(client: TestClient) -> None:
    response = client.post(
        "/api/v1/resumes/parse",
        headers=_auth_headers(),
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400
    assert "unsupported file type" in response.json()["detail"]


def test_parse_rejects_oversized_file(client: TestClient) -> None:
    oversized = b"%PDF-" + b"0" * (MAX_RESUME_FILE_BYTES + 1)
    response = client.post(
        "/api/v1/resumes/parse",
        headers=_auth_headers(),
        files={"file": ("big.pdf", oversized, "application/pdf")},
    )
    assert response.status_code == 400
    assert "size limit" in response.json()["detail"]


def test_parse_rejects_blank_pdf(client: TestClient) -> None:
    response = client.post(
        "/api/v1/resumes/parse",
        headers=_auth_headers(),
        files={"file": ("scan.pdf", make_blank_pdf(), "application/pdf")},
    )
    assert response.status_code == 400
    assert "Scanned or image-only PDFs" in response.json()["detail"]


def test_parse_does_not_persist_resume(client: TestClient) -> None:
    client.post(
        "/api/v1/resumes/parse",
        headers=_auth_headers(),
        files={
            "file": (
                "resume.pdf",
                make_text_pdf("Python engineer."),
                "application/pdf",
            )
        },
    )
    listed = client.get("/api/v1/resumes", headers=_auth_headers())
    assert listed.status_code == 200
    assert listed.json() == []


def test_existing_resume_crud_unchanged(client: TestClient) -> None:
    create = client.post(
        "/api/v1/resumes",
        headers=_auth_headers(),
        json={"name": "Primary", "resume_text": "Python engineer with FastAPI."},
    )
    assert create.status_code == 201
    resume_id = create.json()["id"]

    got = client.get(f"/api/v1/resumes/{resume_id}", headers=_auth_headers())
    assert got.status_code == 200
    assert got.json()["resume_text"].startswith("Python")


def test_ownership_isolation_after_parse(client: TestClient) -> None:
    user_b = ClerkIdentity(user_id="user_b", email="b@example.com", display_name="Bea")

    parsed = client.post(
        "/api/v1/resumes/parse",
        headers=_auth_headers(),
        files={
            "file": (
                "resume.pdf",
                make_text_pdf("Python engineer."),
                "application/pdf",
            )
        },
    )
    assert parsed.status_code == 200

    saved = client.post(
        "/api/v1/resumes",
        headers=_auth_headers(),
        json={
            "name": "Uploaded",
            "resume_text": parsed.json()["extracted_text"],
        },
    )
    assert saved.status_code == 201
    resume_id = saved.json()["id"]

    client.app.state.clerk_identity_override = user_b
    denied = client.get(f"/api/v1/resumes/{resume_id}", headers=_auth_headers())
    assert denied.status_code == 404
