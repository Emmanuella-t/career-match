"""Persistence-layer errors (safe for HTTP mapping)."""

from __future__ import annotations


class PersistenceError(Exception):
    """Base persistence failure."""


class PersistenceNotConfiguredError(PersistenceError):
    """DATABASE_URL is missing."""


class PersistenceUnavailableError(PersistenceError):
    """Database is unreachable or returned an unexpected error."""


class RecordNotFoundError(PersistenceError):
    """No row for this user / id (do not leak existence across users)."""
