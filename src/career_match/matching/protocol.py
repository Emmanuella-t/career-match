"""Matching contracts for a future explainable resume-to-job model."""

from __future__ import annotations

from typing import Protocol

from career_match.core.exceptions import MatchingNotImplementedError
from career_match.core.types import MatchResult


class Matcher(Protocol):
    """Scoring interface for resume-to-job matching."""

    def match(self, resume_text: str, job_text: str) -> MatchResult:
        """Return an explainable match score for one resume and one job."""


class UnimplementedMatcher:
    """Stand-in until a measurable lexical baseline is added."""

    def match(self, resume_text: str, job_text: str) -> MatchResult:
        raise MatchingNotImplementedError(
            "No production matching model is implemented. "
            "The next milestone is a measurable resume-to-job baseline "
            "before introducing semantic embedding models."
        )
