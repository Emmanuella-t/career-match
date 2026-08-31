"""Validate rewrite suggestions against unsupported requirements."""

from __future__ import annotations

import re

from career_match.extraction.skills import SKILL_LEXICON
from career_match.tailoring.protocol import RewriteSuggestion

_FORBIDDEN_PATTERNS = (
    re.compile(r"\b\d+\+?\s*years?\b", re.IGNORECASE),
    re.compile(r"\b(certified|certification)\b", re.IGNORECASE),
)


def _surfaces_for_keyword(keyword: str) -> tuple[str, ...]:
    lowered = keyword.lower()
    if lowered in SKILL_LEXICON:
        return SKILL_LEXICON[lowered]
    return (lowered,)


def suggestion_introduces_only_approved_keywords(
    suggestion: RewriteSuggestion,
    unsupported_keywords: tuple[str, ...],
) -> bool:
    """Return True when suggested text does not smuggle unsupported qualifications."""
    suggested = suggestion.suggested_text.lower()
    approved = {kw.lower() for kw in suggestion.keywords_introduced}

    for keyword in unsupported_keywords:
        if keyword.lower() in approved:
            return False
        for surface in _surfaces_for_keyword(keyword):
            pattern = re.compile(rf"\b{re.escape(surface)}\b", re.IGNORECASE)
            if pattern.search(suggested):
                return False

    for pattern in _FORBIDDEN_PATTERNS:
        if pattern.search(suggestion.suggested_text) and not pattern.search(
            suggestion.original_text
        ):
            return False

    return True


def filter_valid_suggestions(
    suggestions: tuple[RewriteSuggestion, ...],
    unsupported_keywords: tuple[str, ...],
) -> tuple[RewriteSuggestion, ...]:
    return tuple(
        item
        for item in suggestions
        if suggestion_introduces_only_approved_keywords(item, unsupported_keywords)
    )
