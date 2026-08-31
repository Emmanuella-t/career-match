"""SQLAlchemy engine and session configuration for Neon Postgres."""

from __future__ import annotations

import os
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from career_match.persistence.errors import PersistenceNotConfiguredError

# Conservative pool for a small portfolio service. pool_pre_ping helps when
# Neon scales compute to zero and connections go stale after idle periods.
DEFAULT_POOL_SIZE = 5
DEFAULT_MAX_OVERFLOW = 2


def get_database_url() -> str | None:
    raw = os.environ.get("DATABASE_URL", "").strip()
    return raw or None


def database_configured() -> bool:
    return get_database_url() is not None


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    url = get_database_url()
    if not url:
        raise PersistenceNotConfiguredError("DATABASE_URL is required for persistence")
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_size=DEFAULT_POOL_SIZE,
        max_overflow=DEFAULT_MAX_OVERFLOW,
    )


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)


def reset_database_cache() -> None:
    """Clear cached engine/session factory (tests / env changes)."""
    get_engine.cache_clear()
    get_session_factory.cache_clear()
