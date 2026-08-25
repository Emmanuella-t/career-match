"""Authenticated persistence for Career Match (Neon Postgres)."""

from career_match.persistence.errors import (
    PersistenceError,
    PersistenceNotConfiguredError,
    PersistenceUnavailableError,
    RecordNotFoundError,
)
from career_match.persistence.store import (
    InMemoryPersistenceStore,
    PersistenceStore,
    get_persistence_store,
)

__all__ = [
    "InMemoryPersistenceStore",
    "PersistenceError",
    "PersistenceNotConfiguredError",
    "PersistenceStore",
    "PersistenceUnavailableError",
    "RecordNotFoundError",
    "get_persistence_store",
]
