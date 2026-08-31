"""Grounded resume tailoring orchestration."""

from __future__ import annotations

from uuid import UUID

from career_match.api.schemas import (
    EvidenceMapEntry,
    ResumeTailorRequest,
    ResumeTailorResponse,
    RewriteSuggestionResponse,
)
from career_match.api.services import MatcherService
from career_match.api.settings import SCORE_DISCLAIMER
from career_match.persistence.errors import RecordNotFoundError
from career_match.persistence.store import PersistenceStore
from career_match.tailoring.evidence_map import build_evidence_map
from career_match.tailoring.protocol import ResumeRewriteProvider, RewriteSuggestion
from career_match.tailoring.providers import (
    DeterministicRewriteProvider,
    OptionalLLMRewriteProvider,
)
from career_match.tailoring.validation import filter_valid_suggestions

TAILOR_DISCLAIMER = (
    "Career Match suggests phrasing grounded in your existing resume evidence. "
    "It does not fabricate missing experience and does not guarantee ATS passage. "
    + SCORE_DISCLAIMER
)


class TailorService:
    """Evidence-first resume tailoring for a target job."""

    def __init__(
        self,
        *,
        matcher_service: MatcherService,
        store: PersistenceStore,
        deterministic_provider: ResumeRewriteProvider | None = None,
        llm_provider: ResumeRewriteProvider | None = None,
    ) -> None:
        self._matcher_service = matcher_service
        self._store = store
        self._deterministic = deterministic_provider or DeterministicRewriteProvider()
        self._llm = llm_provider or OptionalLLMRewriteProvider()

    def tailor(self, clerk_user_id: str, payload: ResumeTailorRequest) -> ResumeTailorResponse:
        resume_text, resume_id = self._resolve_resume(clerk_user_id, payload)
        job_text, job_id = self._resolve_job(clerk_user_id, payload)

        evidence = build_evidence_map(resume_text, job_text)
        alignment = self._matcher_service.match(resume_text, job_text, payload.matcher)

        warnings: list[str] = []
        for keyword in evidence.unsupported_keywords:
            warnings.append(f"Do not add: {keyword} — no supporting evidence found.")

        deterministic = self._deterministic.generate_rewrites(
            resume_text=resume_text,
            job_text=job_text,
            evidence_map=evidence,
            target=payload.target,
        )
        llm_suggestions: tuple[RewriteSuggestion, ...] = ()
        if self._llm.available:
            llm_suggestions = self._llm.generate_rewrites(
                resume_text=resume_text,
                job_text=job_text,
                evidence_map=evidence,
                target=payload.target,
            )
        else:
            warnings.append(
                "LLM rewrite generation is not configured; showing deterministic suggestions only."
            )

        combined = deterministic + llm_suggestions
        validated = filter_valid_suggestions(combined, evidence.unsupported_keywords)

        return ResumeTailorResponse(
            original_alignment_score=alignment.overall_score,
            matcher=alignment.matcher,
            matcher_version=alignment.matcher_version,
            semantic_score=alignment.semantic_score,
            tfidf_score=alignment.tfidf_score,
            skill_overlap_score=alignment.skill_overlap_score,
            supported_keywords=list(evidence.supported_keywords),
            unsupported_keywords=list(evidence.unsupported_keywords),
            missing_requirements=list(evidence.missing_requirements),
            evidence_map=[_to_evidence_entry(item) for item in evidence.requirements],
            rewrite_suggestions=[_to_rewrite_response(item) for item in validated],
            warnings=warnings,
            disclaimer=TAILOR_DISCLAIMER,
            resume_id=resume_id,
            job_id=job_id,
            rewrite_generation_available=self._deterministic.available,
            llm_rewrite_available=self._llm.available,
        )

    def _resolve_resume(
        self,
        clerk_user_id: str,
        payload: ResumeTailorRequest,
    ) -> tuple[str, UUID | None]:
        if payload.resume_id is not None:
            record = self._store.get_resume(clerk_user_id, payload.resume_id)
            return record.resume_text, record.id
        if payload.resume_text is not None:
            return payload.resume_text, None
        raise RecordNotFoundError("resume not found")

    def _resolve_job(
        self,
        clerk_user_id: str,
        payload: ResumeTailorRequest,
    ) -> tuple[str, UUID | None]:
        if payload.job_id is not None:
            record = self._store.get_job(clerk_user_id, payload.job_id)
            return record.job_description, record.id
        if payload.job_description is not None:
            return payload.job_description, None
        raise RecordNotFoundError("job not found")


def _to_evidence_entry(entry) -> EvidenceMapEntry:
    return EvidenceMapEntry(
        requirement=entry.requirement,
        status=entry.status,
        supporting_text=entry.supporting_text,
        support_reason=entry.support_reason,
        confidence=entry.confidence,
    )


def _to_rewrite_response(item: RewriteSuggestion) -> RewriteSuggestionResponse:
    return RewriteSuggestionResponse(
        section=item.section,
        original_text=item.original_text,
        suggested_text=item.suggested_text,
        keywords_introduced=list(item.keywords_introduced),
        support_reason=item.support_reason,
        support_level=item.support_level,
    )
