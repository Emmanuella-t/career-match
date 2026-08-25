"""Matching contracts for explainable resume-to-job scoring."""

from __future__ import annotations

from typing import Protocol

from career_match.core.exceptions import MatchingNotImplementedError
from career_match.core.types import MatchResult


class Matcher(Protocol):
    """Scoring interface for resume-to-job matching."""

    def match(self, resume_text: str, job_text: str) -> MatchResult:
        """Return an explainable match score for one resume and one job."""


class UnimplementedMatcher:
    """Stand-in that refuses to score. Prefer ``BaselineMatcher`` for v0.1."""

    def match(self, resume_text: str, job_text: str) -> MatchResult:
        raise MatchingNotImplementedError(
            "No production matching model is implemented. "
            "Use BaselineMatcher for the development lexical baseline, "
            "which is still not a hiring model."
        )
