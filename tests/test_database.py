"""Tests for SQLAlchemy database URL normalization and engine configuration."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine

import career_match.api.settings  # noqa: F401 — prime API package before persistence
from career_match.persistence.database import (
    get_database_url,
    get_engine,
    normalize_database_url,
    reset_database_cache,
)
from career_match.persistence.errors import PersistenceNotConfiguredError

NEON_URL = (
    "postgresql://user:pass@ep-example.us-east-1.aws.neon.tech/neondb?sslmode=require"
)
PSYCOPG_URL = (
    "postgresql+psycopg://user:pass@ep-example.us-east-1.aws.neon.tech/neondb"
    "?sslmode=require&channel_binding=require"
)


def test_normalize_generic_postgresql_url() -> None:
    assert normalize_database_url(NEON_URL) == (
        "postgresql+psycopg://user:pass@ep-example.us-east-1.aws.neon.tech/neondb"
        "?sslmode=require"
    )


def test_normalize_leaves_psycopg_url_unchanged() -> None:
    assert normalize_database_url(PSYCOPG_URL) == PSYCOPG_URL


def test_normalize_preserves_query_parameters() -> None:
    url = (
        "postgresql://user:pass@host/db?sslmode=require"
        "&connect_timeout=10&options=-c%20search_path%3Dpublic"
    )
    normalized = normalize_database_url(url)
    assert normalized.startswith("postgresql+psycopg://")
    assert normalized.endswith(
        "?sslmode=require&connect_timeout=10&options=-c%20search_path%3Dpublic"
    )


def test_get_database_url_missing_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert get_database_url() is None


def test_get_engine_requires_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    reset_database_cache()
    with pytest.raises(PersistenceNotConfiguredError, match="DATABASE_URL"):
        get_engine()


def test_get_engine_passes_normalized_url_to_create_engine(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    def _fake_create_engine(url: str, **_kwargs):
        captured["url"] = url
        return MagicMock()

    monkeypatch.setenv("DATABASE_URL", NEON_URL)
    monkeypatch.setattr(
        "career_match.persistence.database.create_engine",
        _fake_create_engine,
    )
    reset_database_cache()
    get_engine()
    assert captured["url"] == normalize_database_url(NEON_URL)


def test_sqlalchemy_engine_uses_psycopg_driver() -> None:
    engine = create_engine(normalize_database_url(NEON_URL))
    assert engine.dialect.driver == "psycopg"
