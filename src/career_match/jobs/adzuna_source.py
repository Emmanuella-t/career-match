"""Adzuna-backed live job source for discovery."""

from __future__ import annotations

from career_match.jobs.adzuna import AdzunaClient
from career_match.jobs.errors import JobProviderError
from career_match.jobs.protocol import JobOpportunity


class AdzunaJobSource:
    """Fetches current job listings from Adzuna using a generated search query."""

    def __init__(self, client: AdzunaClient) -> None:
        self._client = client

    @property
    def name(self) -> str:
        return "adzuna"

    def list_opportunities(
        self,
        *,
        search_query: str | None = None,
        location: str | None = None,
        employment_type: str | None = None,
        limit: int | None = None,
    ) -> list[JobOpportunity]:
        if not search_query or not search_query.strip():
            return []

        fetch_limit = min(limit or 50, 50)
        try:
            return self._client.search(
                what=search_query,
                where=location,
                employment_type=employment_type,
                page=1,
                results_per_page=fetch_limit,
            )
        except JobProviderError:
            raise
        except Exception as exc:
            raise JobProviderError("adzuna request failed") from exc
