"""Job discovery ranking using the existing matcher pipeline."""

from __future__ import annotations

from uuid import UUID

from career_match.api.schemas import (
    JobDiscoverRequest,
    JobDiscoverResponse,
    JobOpportunityResponse,
    RankedJobResult,
)
from career_match.api.services import MatcherService
from career_match.api.settings import SCORE_DISCLAIMER
from career_match.jobs.errors import JobProviderError
from career_match.jobs.factory import adzuna_is_configured
from career_match.jobs.protocol import JobOpportunity, JobSource
from career_match.jobs.query_builder import JobSearchQuery, build_job_search_queries
from career_match.persistence.errors import RecordNotFoundError
from career_match.persistence.store import PersistenceStore

DEFAULT_DISCOVERY_LIMIT = 20
MAX_DISCOVERY_LIMIT = 50
MAX_CATALOG_SCAN = 500
MAX_ADZUNA_FETCH = 50
MIN_PER_QUERY_FETCH = 5

_PROVIDER_UNAVAILABLE = (
    "We're having trouble loading jobs right now. Please try again in a moment."
)
_PROVIDER_NOT_CONFIGURED = (
    "Live job search isn't available right now. "
    "You can still analyze and tailor jobs you add manually."
)
_NO_RESULTS = (
    "We couldn't find matching jobs for this search. "
    "Try a broader location or a different resume."
)


class JobDiscoveryService:
    """Rank discoverable jobs for a resume using existing matchers."""

    def __init__(
        self,
        *,
        matcher_service: MatcherService,
        job_source: JobSource,
        store: PersistenceStore,
    ) -> None:
        self._matcher_service = matcher_service
        self._job_source = job_source
        self._store = store

    def discover(self, clerk_user_id: str, payload: JobDiscoverRequest) -> JobDiscoverResponse:
        resume_text, resume_id = self._resolve_resume(clerk_user_id, payload)
        limit = min(payload.limit or DEFAULT_DISCOVERY_LIMIT, MAX_DISCOVERY_LIMIT)
        search_plan = build_job_search_queries(resume_text)

        provider_message: str | None = None
        fetch_limit = (
            MAX_ADZUNA_FETCH
            if self._job_source.name == "adzuna"
            else MAX_CATALOG_SCAN
        )

        try:
            opportunities = self._retrieve_candidates(search_plan.queries, payload, fetch_limit)
        except JobProviderError:
            opportunities = []
            provider_message = _PROVIDER_UNAVAILABLE

        candidate_count = len(opportunities)
        if candidate_count == 0 and provider_message is None:
            provider_message = self._empty_results_message(payload)

        ranked: list[RankedJobResult] = []
        matcher_name = ""
        matcher_version = ""

        for opportunity in opportunities:
            match = self._matcher_service.match(
                resume_text,
                opportunity.description,
                payload.matcher,
            )
            matcher_name = match.matcher
            matcher_version = match.matcher_version
            ranked.append(
                RankedJobResult(
                    job=_to_job_response(opportunity),
                    overall_score=match.overall_score,
                    matched_skills=match.matched_skills,
                    missing_skills=match.missing_skills,
                    weak_or_negated_skills=match.weak_or_negated_skills,
                    matcher=match.matcher,
                    matcher_version=match.matcher_version,
                    semantic_score=match.semantic_score,
                    tfidf_score=match.tfidf_score,
                    skill_overlap_score=match.skill_overlap_score,
                    disclaimer=match.disclaimer,
                )
            )

        ranked.sort(key=lambda item: item.overall_score, reverse=True)
        ranked = ranked[:limit]

        query_texts = [query.text for query in search_plan.queries]
        return JobDiscoverResponse(
            results=ranked,
            matcher=matcher_name,
            matcher_version=matcher_version,
            disclaimer=SCORE_DISCLAIMER,
            resume_id=resume_id,
            source=self._job_source.name,
            search_query=search_plan.primary.text,
            search_queries=query_texts or None,
            candidate_count=candidate_count,
            provider_message=provider_message,
        )

    def _retrieve_candidates(
        self,
        queries: tuple[JobSearchQuery, ...],
        payload: JobDiscoverRequest,
        fetch_limit: int,
    ) -> list[JobOpportunity]:
        if not queries:
            return []

        per_query_limit = max(
            MIN_PER_QUERY_FETCH,
            fetch_limit // max(len(queries), 1),
        )
        combined: list[JobOpportunity] = []
        seen_keys: set[str] = set()

        for query in queries:
            batch = self._fetch_query_with_fallback(query, payload, per_query_limit)
            for opportunity in batch:
                key = _opportunity_dedupe_key(opportunity)
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                combined.append(opportunity)
        return combined

    def _fetch_query_with_fallback(
        self,
        query: JobSearchQuery,
        payload: JobDiscoverRequest,
        limit: int,
    ) -> list[JobOpportunity]:
        for search_text in _query_attempts(query):
            results = self._job_source.list_opportunities(
                search_query=search_text,
                location=payload.location,
                employment_type=payload.employment_type,
                limit=limit,
            )
            if results:
                return results
        return []

    def _resolve_resume(
        self,
        clerk_user_id: str,
        payload: JobDiscoverRequest,
    ) -> tuple[str, UUID | None]:
        if payload.resume_id is not None:
            record = self._store.get_resume(clerk_user_id, payload.resume_id)
            return record.resume_text, record.id
        if payload.resume_text is not None:
            return payload.resume_text, None
        raise RecordNotFoundError("resume not found")

    def _empty_results_message(self, payload: JobDiscoverRequest) -> str:
        """Distinguish missing external provider from a configured search with no hits."""
        if (
            self._job_source.name == "postgres-catalog"
            and not adzuna_is_configured()
            and not self._catalog_has_any_jobs()
        ):
            return _PROVIDER_NOT_CONFIGURED
        return _NO_RESULTS

    def _catalog_has_any_jobs(self) -> bool:
        """Return whether the Postgres catalog contains any discoverable jobs."""
        jobs = self._job_source.list_opportunities(limit=1)
        return bool(jobs)


def _query_attempts(query: JobSearchQuery) -> tuple[str, ...]:
    if query.broaden_text and query.broaden_text != query.text:
        return (query.text, query.broaden_text)
    return (query.text,)


def _opportunity_dedupe_key(opportunity: JobOpportunity) -> str:
    if opportunity.source_url:
        return opportunity.source_url.strip().lower()
    return str(opportunity.id)


def _to_job_response(opportunity: JobOpportunity) -> JobOpportunityResponse:
    return JobOpportunityResponse(
        id=opportunity.id,
        title=opportunity.title,
        company=opportunity.company,
        location=opportunity.location,
        description=opportunity.description,
        source=opportunity.source,
        source_url=opportunity.source_url,
        apply_url=opportunity.apply_url,
        employment_type=opportunity.employment_type,
        created_at=opportunity.created_at,
        updated_at=opportunity.updated_at,
    )
