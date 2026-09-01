"""Tests for job source factory configuration."""

from __future__ import annotations

import pytest

from career_match.api.app import create_app  # noqa: F401 — prime app imports
from career_match.jobs.adzuna_source import AdzunaJobSource
from career_match.jobs.factory import adzuna_is_configured, create_job_source
from career_match.persistence.store import InMemoryPersistenceStore


def test_create_job_source_uses_postgres_when_adzuna_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ADZUNA_APP_ID", raising=False)
    monkeypatch.delenv("ADZUNA_APP_KEY", raising=False)
    store = InMemoryPersistenceStore()
    source = create_job_source(store)
    assert source.name == "postgres-catalog"


def test_create_job_source_uses_adzuna_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ADZUNA_APP_ID", "test-app-id")
    monkeypatch.setenv("ADZUNA_APP_KEY", "test-app-key")
    store = InMemoryPersistenceStore()
    source = create_job_source(store)
    assert isinstance(source, AdzunaJobSource)
    assert source.name == "adzuna"
    assert adzuna_is_configured() is True


def test_adzuna_is_configured_false_without_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ADZUNA_APP_ID", raising=False)
    monkeypatch.delenv("ADZUNA_APP_KEY", raising=False)
    assert adzuna_is_configured() is False
