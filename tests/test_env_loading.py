"""Tests for repository-root .env loading and Clerk configuration aliases."""

from __future__ import annotations

import os

import pytest

from career_match.api.auth import get_clerk_issuer, reset_clerk_jwks_cache
from career_match.api.settings import (
    find_project_root,
    get_runtime_config_status,
    load_local_env_file,
)
from career_match.persistence.database import reset_database_cache


def test_find_project_root_contains_pyproject() -> None:
    root = find_project_root()
    assert (root / "pyproject.toml").is_file()


def test_load_local_env_file_reads_dotenv(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "DATABASE_URL=postgresql://dotenv\nCLERK_ISSUER=https://issuer.example\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("CLERK_ISSUER", raising=False)
    monkeypatch.setattr(
        "career_match.api.settings.find_project_root",
        lambda: tmp_path,
    )
    assert load_local_env_file() is True
    assert os.environ.get("DATABASE_URL") == "postgresql://dotenv"
    assert os.environ.get("CLERK_ISSUER") == "https://issuer.example"


def test_process_env_overrides_dotenv(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_URL=postgresql://dotenv\n", encoding="utf-8")
    monkeypatch.setenv("DATABASE_URL", "postgresql://process")
    monkeypatch.setattr(
        "career_match.api.settings.find_project_root",
        lambda: tmp_path,
    )
    load_local_env_file()
    assert os.environ["DATABASE_URL"] == "postgresql://process"


def test_clerk_issuer_url_legacy_alias(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CLERK_ISSUER", raising=False)
    monkeypatch.setenv("CLERK_ISSUER_URL", "https://legacy.clerk.accounts.dev")
    reset_clerk_jwks_cache()
    assert get_clerk_issuer() == "https://legacy.clerk.accounts.dev"


def test_runtime_config_status_never_includes_secrets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@host/db")
    monkeypatch.setenv("CLERK_ISSUER", "https://issuer.example")
    monkeypatch.setenv("ADZUNA_APP_ID", "app-id")
    monkeypatch.setenv("ADZUNA_APP_KEY", "app-key")
    reset_database_cache()
    reset_clerk_jwks_cache()
    status = get_runtime_config_status()
    assert status["database_configured"] is True
    assert status["clerk_issuer_configured"] is True
    assert status["adzuna_configured"] is True
    dumped = repr(status)
    assert "secret" not in dumped
    assert "app-key" not in dumped
