"""Provider-neutral job source protocol for job discovery."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class JobOpportunity:
    """A discoverable job posting from an external or ingested source."""

    id: UUID
    title: str
    company: str | None
    location: str | None
    description: str
    source: str
    source_url: str | None
    apply_url: str | None
    employment_type: str | None
    created_at: datetime
    updated_at: datetime


class JobSource(Protocol):
    """Lists available job opportunities for ranking."""

    @property
    def name(self) -> str: ...

    def list_opportunities(
        self,
        *,
        search_query: str | None = None,
        location: str | None = None,
        employment_type: str | None = None,
        limit: int | None = None,
    ) -> list[JobOpportunity]: ...
