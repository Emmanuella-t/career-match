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
from career_match.jobs.protocol import JobOpportunity, JobSource
from career_match.persistence.errors import RecordNotFoundError
from career_match.persistence.store import PersistenceStore

DEFAULT_DISCOVERY_LIMIT = 20
MAX_DISCOVERY_LIMIT = 50


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

        opportunities = self._job_source.list_opportunities(
            location=payload.location,
            employment_type=payload.employment_type,
            limit=None,
        )

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

        return JobDiscoverResponse(
            results=ranked,
            matcher=matcher_name,
            matcher_version=matcher_version,
            disclaimer=SCORE_DISCLAIMER,
            resume_id=resume_id,
            source=self._job_source.name,
        )

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
