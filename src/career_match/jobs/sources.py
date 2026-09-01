"""Job source implementations for discovery."""

from __future__ import annotations

from typing import TYPE_CHECKING

from career_match.jobs.protocol import JobOpportunity
from career_match.persistence.schemas import JobOpportunityRecord

if TYPE_CHECKING:
    from career_match.persistence.store import PersistenceStore


def _to_job_opportunity(record: JobOpportunityRecord) -> JobOpportunity:
    return JobOpportunity(
        id=record.id,
        title=record.title,
        company=record.company,
        location=record.location,
        description=record.description,
        source=record.source,
        source_url=record.source_url,
        apply_url=record.apply_url,
        employment_type=record.employment_type,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


class InMemoryJobSource:
    """Fixture-backed job source for automated tests only."""

    def __init__(self, opportunities: list[JobOpportunity] | None = None) -> None:
        self._opportunities = list(opportunities or [])

    @property
    def name(self) -> str:
        return "in-memory-fixture"

    def list_opportunities(
        self,
        *,
        search_query: str | None = None,
        location: str | None = None,
        employment_type: str | None = None,
        limit: int | None = None,
    ) -> list[JobOpportunity]:
        del search_query  # fixture catalog ignores generated queries
        rows = self._opportunities
        if location:
            needle = location.strip().lower()
            rows = [
                row
                for row in rows
                if row.location and needle in row.location.lower()
            ]
        if employment_type:
            target = employment_type.strip().lower()
            rows = [
                row
                for row in rows
                if row.employment_type and row.employment_type.lower() == target
            ]
        if limit is not None:
            rows = rows[:limit]
        return list(rows)


class PostgresJobOpportunitySource:
    """Reads discoverable jobs from the provider-neutral Postgres catalog."""

    def __init__(self, store: PersistenceStore) -> None:
        self._store = store

    @property
    def name(self) -> str:
        return "postgres-catalog"

    def list_opportunities(
        self,
        *,
        search_query: str | None = None,
        location: str | None = None,
        employment_type: str | None = None,
        limit: int | None = None,
    ) -> list[JobOpportunity]:
        del search_query  # catalog-backed jobs ignore generated queries
        records = self._store.list_job_opportunities(
            location=location,
            employment_type=employment_type,
            limit=limit,
        )
        return [_to_job_opportunity(record) for record in records]
