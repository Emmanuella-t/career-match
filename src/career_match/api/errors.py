"""Shared HTTP error mapping for API routes."""

from __future__ import annotations

from fastapi import HTTPException

from career_match.api.user_messages import PERSISTENCE_UNAVAILABLE
from career_match.persistence.errors import (
    PersistenceNotConfiguredError,
    PersistenceUnavailableError,
    RecordNotFoundError,
)


def record_not_found_detail(exc: RecordNotFoundError) -> str:
    """Map a store not-found error to a stable client-facing message."""
    message = str(exc).lower()
    if "resume" in message:
        return "resume not found"
    if "job" in message:
        return "job not found"
    if "match" in message:
        return "match not found"
    return "not found"


def map_persistence_http_error(exc: Exception) -> HTTPException:
    """Translate persistence-layer errors into HTTP responses."""
    if isinstance(exc, RecordNotFoundError):
        return HTTPException(status_code=404, detail=record_not_found_detail(exc))
    if isinstance(exc, (PersistenceNotConfiguredError, PersistenceUnavailableError)):
        return HTTPException(status_code=503, detail=PERSISTENCE_UNAVAILABLE)
    return HTTPException(status_code=503, detail=PERSISTENCE_UNAVAILABLE)
