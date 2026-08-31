"""Equivalent terminology for grounded requirement mapping (tailoring only)."""

from __future__ import annotations

import re

# Job requirement term -> resume phrases that constitute supporting evidence.
# Kept separate from SKILL_LEXICON so matcher benchmarks are unaffected.
REQUIREMENT_EQUIVALENTS: dict[str, tuple[str, ...]] = {
    "ci/cd": (
        "github actions",
        "gitlab ci",
        "jenkins",
        "continuous integration",
        "continuous delivery",
        "automated deployment",
        "automated testing and deployment",
        "build and deploy pipeline",
    ),
}

# Additional job requirements detected by phrase (not in SKILL_LEXICON).
EXTRA_JOB_REQUIREMENT_TERMS: tuple[str, ...] = tuple(REQUIREMENT_EQUIVALENTS.keys())


def _phrase_pattern(phrase: str) -> re.Pattern[str]:
    escaped = re.escape(phrase)
    if re.fullmatch(r"[a-z0-9/+-]+", phrase):
        return re.compile(rf"\b{escaped}\b", re.IGNORECASE)
    return re.compile(escaped, re.IGNORECASE)


def job_mentions_requirement(job_text: str, requirement: str) -> bool:
    normalized = job_text.lower()
    pattern = _phrase_pattern(requirement)
    return pattern.search(normalized) is not None


def find_equivalent_evidence(resume_text: str, requirement: str) -> tuple[str, str] | None:
    """Return (supporting_snippet, reason) when equivalent resume evidence exists."""
    equivalents = REQUIREMENT_EQUIVALENTS.get(requirement.lower())
    if not equivalents:
        return None

    normalized = resume_text
    lowered = normalized.lower()
    for phrase in equivalents:
        pattern = _phrase_pattern(phrase)
        match = pattern.search(lowered)
        if not match:
            continue
        start = max(0, match.start() - 60)
        end = min(len(normalized), match.end() + 60)
        snippet = normalized[start:end].strip()
        reason = (
            f"Resume describes equivalent experience ({phrase!r}); "
            f"{requirement.upper()} terminology may be introduced safely."
        )
        return snippet, reason
    return None
