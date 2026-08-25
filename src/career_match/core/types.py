"""Core data types for Career Match.

These types describe the ML layer. They are intentionally small so a later
matching baseline can reuse them without a rewrite.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResumeRecord:
    """One labeled resume from the legacy screening dataset."""

    category: str
    text: str
    source_row: int


@dataclass(frozen=True)
class ExtractedSkill:
    """A skill mention located in resume or job-description text."""

    name: str
    start: int
    end: int


@dataclass(frozen=True)
class MatchResult:
    """Placeholder result for a future explainable matcher.

    ``score`` is reserved for a calibrated match score in ``[0, 1]``.
    ``evidence`` will hold human-readable reasons. Neither is produced by a
    production model today.
    """

    score: float
    evidence: tuple[str, ...]
    skills_in_resume: tuple[str, ...]
    skills_in_job: tuple[str, ...]
