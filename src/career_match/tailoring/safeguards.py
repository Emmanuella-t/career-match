"""Anti-fabrication and keyword-stuffing safeguards for revised resumes."""

from __future__ import annotations

import re

from career_match.extraction.evidence import build_evidence_profile
from career_match.extraction.skills import extract_skill_names
from career_match.tailoring.evidence_map import build_evidence_map
from career_match.tailoring.validation import FORBIDDEN_PATTERNS

_SKILL_REPEAT_THRESHOLD = 8


def validate_revised_resume(
    *,
    original_text: str,
    revised_text: str,
    job_text: str,
    unsupported_keywords: tuple[str, ...],
) -> list[str]:
    """Return warnings; non-empty list means the revision should be rejected or flagged."""
    warnings: list[str] = []

    revised_profile = build_evidence_profile(revised_text)
    if revised_profile.stuffing_likely:
        warnings.append(
            "Revised resume appears keyword-stuffed; reduce repeated catalog skills."
        )

    original_skills = set(extract_skill_names(original_text))
    revised_skills = set(extract_skill_names(revised_text))
    invented = revised_skills - original_skills
    for skill in invented:
        if skill in unsupported_keywords:
            warnings.append(f"Revised text introduces unsupported skill: {skill}")

    revised_evidence = build_evidence_map(revised_text, job_text)
    for keyword in unsupported_keywords:
        if keyword in revised_evidence.supported_keywords and keyword not in invented:
            continue
        if keyword in revised_skills and keyword in unsupported_keywords:
            warnings.append(f"Revised text must not claim unsupported requirement: {keyword}")

    for pattern in FORBIDDEN_PATTERNS:
        if pattern.search(revised_text) and not pattern.search(original_text):
            warnings.append(
                "Revised text introduces unsupported metrics or credentials."
            )
            break

    for skill in revised_skills:
        count = len(re.findall(rf"\b{re.escape(skill)}\b", revised_text, re.I))
        if count >= _SKILL_REPEAT_THRESHOLD:
            warnings.append(f"Skill {skill!r} is repeated unnaturally in revised text.")
            break

    return warnings
