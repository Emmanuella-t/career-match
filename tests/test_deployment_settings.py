"""Deployment-oriented settings, CORS, and readiness tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from tests.test_api import _FixedEncoder

from career_match.api.app import create_app
from career_match.api.services import MatcherService
from career_match.api.settings import (
    DEFAULT_CORS_ORIGINS,
    apply_model_cache_env,
    get_cors_allow_origins,
    get_port,
    parse_cors_origins,
)
from career_match.matching.hybrid import HybridMatcher
from career_match.matching.semantic import SemanticMatcher


@pytest.fixture()
def bare_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.delenv("CAREER_MATCH_CORS_ORIGINS", raising=False)
    application = create_app()
    with TestClient(application) as test_client:
        semantic = SemanticMatcher(encoder=_FixedEncoder())
        service = MatcherService(
            semantic=semantic,
            hybrid=HybridMatcher(semantic_matcher=semantic),
        )
        test_client.app.state.matcher_service = service
        yield test_client


def test_parse_cors_defaults_when_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CAREER_MATCH_CORS_ORIGINS", raising=False)
    assert parse_cors_origins(None) == DEFAULT_CORS_ORIGINS
    assert parse_cors_origins("") == DEFAULT_CORS_ORIGINS
    assert parse_cors_origins("  ,  ") == DEFAULT_CORS_ORIGINS


def test_parse_cors_strips_and_splits() -> None:
    origins = parse_cors_origins(
        "https://app.example.com/, http://localhost:3000"
    )
    assert origins == ("https://app.example.com", "http://localhost:3000")


def test_get_cors_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "CAREER_MATCH_CORS_ORIGINS",
        "https://frontend.example.com",
    )
    assert get_cors_allow_origins() == ("https://frontend.example.com",)


def test_local_default_cors_origins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CAREER_MATCH_CORS_ORIGINS", raising=False)
    assert "http://localhost:3000" in get_cors_allow_origins()
    assert "http://127.0.0.1:3000" in get_cors_allow_origins()
    assert not any("43173" in origin for origin in get_cors_allow_origins())


def test_get_port_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PORT", raising=False)
    assert get_port() == 8000
    monkeypatch.setenv("PORT", "9090")
    assert get_port() == 9090


def test_get_port_rejects_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PORT", "abc")
    with pytest.raises(ValueError, match="PORT"):
        get_port()


def test_apply_model_cache_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cache = str(tmp_path / "models")
    monkeypatch.setenv("CAREER_MATCH_MODEL_CACHE_DIR", cache)
    cache_keys = (
        "HF_HOME",
        "TRANSFORMERS_CACHE",
        "SENTENCE_TRANSFORMERS_HOME",
        "HUGGINGFACE_HUB_CACHE",
    )
    for key in cache_keys:
        monkeypatch.delenv(key, raising=False)
    apply_model_cache_env()
    assert os.environ["HF_HOME"] == cache
    assert os.environ["SENTENCE_TRANSFORMERS_HOME"] == cache
    # Remove values set via os.environ.setdefault so later tests keep the
    # default Hugging Face cache (monkeypatch alone would restore them).
    for key in cache_keys:
        os.environ.pop(key, None)


def test_health_does_not_load_semantic(bare_client: TestClient) -> None:
    # Replace with unloaded service to assert health stays lazy.
    bare_client.app.state.matcher_service = MatcherService()
    response = bare_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert bare_client.app.state.matcher_service.semantic_model_loaded is False


def test_ready_reports_without_loading_model(bare_client: TestClient) -> None:
    bare_client.app.state.matcher_service = MatcherService()
    response = bare_client.get("/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["semantic_model_loaded"] is False


def test_cors_allows_permitted_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CAREER_MATCH_CORS_ORIGINS", "https://app.example.com")
    application = create_app()
    with TestClient(application) as client:
        client.app.state.matcher_service = MatcherService()
        response = client.options(
            "/api/v1/match",
            headers={
                "Origin": "https://app.example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.headers.get("access-control-allow-origin") == (
            "https://app.example.com"
        )


def test_cors_denies_unknown_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CAREER_MATCH_CORS_ORIGINS", "https://app.example.com")
    application = create_app()
    with TestClient(application) as client:
        client.app.state.matcher_service = MatcherService()
        response = client.options(
            "/api/v1/match",
            headers={
                "Origin": "https://evil.example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.headers.get("access-control-allow-origin") != (
            "https://evil.example.com"
        )


def test_local_cors_still_works(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CAREER_MATCH_CORS_ORIGINS", raising=False)
    application = create_app()
    with TestClient(application) as client:
        client.app.state.matcher_service = MatcherService()
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.headers.get("access-control-allow-origin") == (
            "http://localhost:3000"
        )


def test_module_import_does_not_set_eager_model_flag() -> None:
    from career_match.api.app import app

    service = MatcherService()
    assert service.semantic_model_loaded is False
    assert app.title == "Career Match API"
