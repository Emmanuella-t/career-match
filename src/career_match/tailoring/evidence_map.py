"""Deterministic evidence mapping for grounded resume tailoring."""

from __future__ import annotations

from dataclasses import dataclass

from career_match.extraction.evidence import (
    SkillEvidence,
    build_evidence_profile,
    classify_skill_mentions,
    evidence_weighted_overlap,
)
from career_match.extraction.skills import extract_skill_names
from career_match.parsing.text import normalize_text
from career_match.tailoring.terminology import (
    EXTRA_JOB_REQUIREMENT_TERMS,
    find_equivalent_evidence,
    job_mentions_requirement,
)

SupportStatus = str  # supported | partial | unsupported | negated | equivalent


@dataclass(frozen=True, slots=True)
class RequirementEvidenceEntry:
    requirement: str
    status: SupportStatus
    supporting_text: str | None
    support_reason: str
    confidence: str  # high | medium | low


@dataclass(frozen=True, slots=True)
class EvidenceMapResult:
    requirements: tuple[RequirementEvidenceEntry, ...]
    supported_keywords: tuple[str, ...]
    unsupported_keywords: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    partial_requirements: tuple[str, ...]
    negated_requirements: tuple[str, ...]


def extract_job_requirements(job_text: str) -> tuple[str, ...]:
    """Collect catalog skills and extra requirement phrases from a job description."""
    requirements: list[str] = list(extract_skill_names(job_text))
    seen = {item.lower() for item in requirements}
    for term in EXTRA_JOB_REQUIREMENT_TERMS:
        if term.lower() in seen:
            continue
        if job_mentions_requirement(job_text, term):
            requirements.append(term)
            seen.add(term.lower())
    return tuple(requirements)


def _snippet_from_span(text: str, start: int, end: int, *, radius: int = 80) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    return normalize_text(text[left:right])


def _classify_catalog_requirement(
    requirement: str,
    resume_text: str,
    mentions: dict[str, SkillEvidence],
    profile,
) -> RequirementEvidenceEntry:
    if requirement in profile.negated_skills:
        snippet = None
        if requirement in mentions:
            snippet = _snippet_from_span(
                resume_text, mentions[requirement].start, mentions[requirement].end
            )
        return RequirementEvidenceEntry(
            requirement=requirement,
            status="negated",
            supporting_text=snippet,
            support_reason="Resume explicitly weakens or negates this requirement.",
            confidence="high",
        )

    if requirement in profile.positive_skills:
        mention = mentions[requirement]
        snippet = _snippet_from_span(resume_text, mention.start, mention.end)
        if mention.evidence == "keyword_list":
            return RequirementEvidenceEntry(
                requirement=requirement,
                status="partial",
                supporting_text=snippet,
                support_reason=(
                    "Skill appears only in a keyword/skills list, "
                    "not narrative experience."
                ),
                confidence="medium",
            )
        return RequirementEvidenceEntry(
            requirement=requirement,
            status="supported",
            supporting_text=snippet,
            support_reason="Resume contains direct narrative evidence for this requirement.",
            confidence="high",
        )

    equivalent = find_equivalent_evidence(resume_text, requirement)
    if equivalent is not None:
        snippet, reason = equivalent
        return RequirementEvidenceEntry(
            requirement=requirement,
            status="equivalent",
            supporting_text=snippet,
            support_reason=reason,
            confidence="high",
        )

    return RequirementEvidenceEntry(
        requirement=requirement,
        status="unsupported",
        supporting_text=None,
        support_reason="No supporting evidence found in the resume.",
        confidence="high",
    )


def build_evidence_map(resume_text: str, job_text: str) -> EvidenceMapResult:
    """Map each important job requirement to resume evidence classification."""
    requirements = extract_job_requirements(job_text)
    profile = build_evidence_profile(resume_text)
    mentions = {item.name: item for item in classify_skill_mentions(resume_text)}

    entries: list[RequirementEvidenceEntry] = []
    for requirement in requirements:
        entries.append(
            _classify_catalog_requirement(requirement, resume_text, mentions, profile)
        )

    supported: list[str] = []
    unsupported: list[str] = []
    missing: list[str] = []
    partial: list[str] = []
    negated: list[str] = []

    for entry in entries:
        if entry.status in {"supported", "equivalent"}:
            supported.append(entry.requirement)
        elif entry.status == "partial":
            partial.append(entry.requirement)
            supported.append(entry.requirement)
        elif entry.status == "negated":
            negated.append(entry.requirement)
            unsupported.append(entry.requirement)
            missing.append(entry.requirement)
        else:
            unsupported.append(entry.requirement)
            missing.append(entry.requirement)

    # Cross-check with overlap helper for consistency with hybrid matcher channel.
    _, matched, overlap_missing, overlap_negated = evidence_weighted_overlap(
        profile,
        tuple(skill for skill in requirements if skill in extract_skill_names(job_text)),
    )
    for skill in overlap_missing:
        if skill not in missing and skill not in negated:
            missing.append(skill)
    for skill in overlap_negated:
        if skill not in negated:
            negated.append(skill)

    return EvidenceMapResult(
        requirements=tuple(entries),
        supported_keywords=tuple(dict.fromkeys(supported)),
        unsupported_keywords=tuple(dict.fromkeys(unsupported)),
        missing_requirements=tuple(dict.fromkeys(missing)),
        partial_requirements=tuple(dict.fromkeys(partial)),
        negated_requirements=tuple(dict.fromkeys(negated)),
    )
