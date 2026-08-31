"""Apply accepted tailoring suggestions and compute before/after alignment."""

from __future__ import annotations

from career_match.api.schemas import (
    ResumeTailorApplyRequest,
    ResumeTailorApplyResponse,
    ResumeTailorRequest,
    RevisedSectionBlock,
    RewriteSuggestionResponse,
)
from career_match.api.services import MatcherService
from career_match.api.tailor_service import TAILOR_DISCLAIMER, TailorService
from career_match.tailoring.evidence_map import build_evidence_map
from career_match.tailoring.protocol import RewriteSuggestion
from career_match.tailoring.resume_structure import (
    SectionBlock,
    StructuredResume,
    apply_suggestions,
    parse_resume_sections,
)
from career_match.tailoring.safeguards import validate_revised_resume


class TailorApplyError(ValueError):
    """Invalid or ungrounded tailoring apply request."""


class TailorApplyService:
    """Apply grounded suggestions and compare alignment before/after."""

    def __init__(self, *, tailor_service: TailorService, matcher_service: MatcherService) -> None:
        self._tailor = tailor_service
        self._matcher = matcher_service

    def apply(
        self,
        clerk_user_id: str,
        payload: ResumeTailorApplyRequest,
    ) -> ResumeTailorApplyResponse:
        tailor_payload = ResumeTailorRequest(
            resume_id=payload.resume_id,
            resume_text=payload.resume_text,
            job_id=payload.job_id,
            job_description=payload.job_description,
            target=payload.target,
            matcher=payload.matcher,
        )
        analysis = self._tailor.tailor(clerk_user_id, tailor_payload)
        resume_text, resume_id = self._tailor._resolve_resume(clerk_user_id, tailor_payload)
        job_text, job_id = self._tailor._resolve_job(clerk_user_id, tailor_payload)

        suggestion_lookup: dict[str, RewriteSuggestionResponse] = {}
        suggestion_objects: list[tuple[str, RewriteSuggestion]] = []
        for item in analysis.rewrite_suggestions:
            suggestion = RewriteSuggestion(
                section=item.section,
                original_text=item.original_text,
                suggested_text=item.suggested_text,
                keywords_introduced=tuple(item.keywords_introduced),
                support_reason=item.support_reason,
                support_level=item.support_level,
            )
            sid = item.suggestion_id
            suggestion_lookup[sid] = item
            suggestion_objects.append((sid, suggestion))

        accepted_ids = set(payload.accepted_suggestion_ids)
        unknown = accepted_ids - set(suggestion_lookup)
        if unknown:
            raise TailorApplyError(
                f"unknown or stale suggestion ids: {', '.join(sorted(unknown))}"
            )

        accepted = tuple(
            (sid, suggestion) for sid, suggestion in suggestion_objects if sid in accepted_ids
        )
        rejected_ids = frozenset(sid for sid in suggestion_lookup if sid not in accepted_ids)

        structured = parse_resume_sections(resume_text)
        if accepted:
            revised_structured = apply_suggestions(structured, accepted)
            revised_text = _structured_to_full_text(
                StructuredResume(header=structured.header, sections=revised_structured.sections)
            )
        else:
            revised_structured = structured
            revised_text = resume_text

        original_evidence = build_evidence_map(resume_text, job_text)
        revised_evidence = build_evidence_map(revised_text, job_text)

        safeguard_warnings = validate_revised_resume(
            original_text=resume_text,
            revised_text=revised_text,
            job_text=job_text,
            unsupported_keywords=tuple(analysis.unsupported_keywords),
        )
        if safeguard_warnings:
            raise TailorApplyError("; ".join(safeguard_warnings))

        original_match = self._matcher.match(resume_text, job_text, payload.matcher)
        revised_match = self._matcher.match(revised_text, job_text, payload.matcher)

        newly_covered = sorted(
            set(revised_evidence.supported_keywords) - set(original_evidence.supported_keywords)
        )
        remaining_gaps = list(revised_evidence.missing_requirements)
        warnings = list(analysis.warnings)

        return ResumeTailorApplyResponse(
            structured_sections=[_to_section_block(block) for block in revised_structured.sections],
            revised_resume_text=revised_text,
            original_alignment_score=original_match.overall_score,
            revised_alignment_score=revised_match.overall_score,
            alignment_delta=round(
                revised_match.overall_score - original_match.overall_score,
                2,
            ),
            newly_covered_keywords=newly_covered,
            remaining_missing_requirements=remaining_gaps,
            remaining_unsupported_keywords=list(revised_evidence.unsupported_keywords),
            accepted_suggestions=[
                suggestion_lookup[sid] for sid in accepted_ids if sid in suggestion_lookup
            ],
            rejected_suggestions=[suggestion_lookup[sid] for sid in rejected_ids],
            warnings=warnings,
            disclaimer=TAILOR_DISCLAIMER,
            matcher=original_match.matcher,
            matcher_version=original_match.matcher_version,
            resume_id=resume_id,
            job_id=job_id,
        )

    def build_structured_for_export(
        self,
        clerk_user_id: str,
        payload: ResumeTailorApplyRequest,
    ) -> tuple[StructuredResume, ResumeTailorApplyResponse, str]:
        apply_result = self.apply(clerk_user_id, payload)
        original_text, _ = self._tailor._resolve_resume(
            clerk_user_id,
            ResumeTailorRequest(
                resume_id=payload.resume_id,
                resume_text=payload.resume_text,
                job_id=payload.job_id,
                job_description=payload.job_description,
                target=payload.target,
                matcher=payload.matcher,
            ),
        )
        header = parse_resume_sections(original_text).header
        structured = StructuredResume(
            header=header,
            sections=tuple(
                SectionBlock(
                    section=item.section,
                    text=item.text,
                    change_status=item.change_status,
                    original_text=item.original_text,
                    suggestion_id=item.suggestion_id,
                )
                for item in apply_result.structured_sections
            ),
        )
        resume_name = "resume"
        if payload.resume_id is not None:
            record = self._tailor._store.get_resume(clerk_user_id, payload.resume_id)
            resume_name = record.name
        return structured, apply_result, resume_name


def _structured_to_full_text(structured: StructuredResume) -> str:
    parts: list[str] = []
    if structured.header:
        parts.append(structured.header)
    for block in structured.sections:
        if block.text.strip():
            parts.append(block.text.strip())
    return "\n\n".join(parts).strip()


def _to_section_block(block: SectionBlock) -> RevisedSectionBlock:
    return RevisedSectionBlock(
        section=block.section,
        text=block.text,
        change_status=block.change_status,
        original_text=block.original_text,
        suggestion_id=block.suggestion_id,
    )
