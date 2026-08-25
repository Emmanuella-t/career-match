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
    """Explainable relevance result for one resume and one job.

    All numeric scores use a 0–100 scale. ``overall_score`` is a **relevance
    score** from the matcher that produced the result (lexical, semantic, or
    hybrid), not a calibrated probability that someone should be hired.
    """

    overall_score: float
    tfidf_similarity: float
    skill_overlap_score: float
    matched_skills: tuple[str, ...]
    missing_skills: tuple[str, ...]
    resume_skills: tuple[str, ...]
    job_skills: tuple[str, ...]
    evidence: tuple[str, ...] = ()
    semantic_similarity: float = 0.0
    weak_or_negated_skills: tuple[str, ...] = ()

    @property
    def score(self) -> float:
        """Alias of ``overall_score`` for the ``Matcher`` protocol."""
        return self.overall_score

    @property
    def semantic_score(self) -> float:
        """Alias of ``semantic_similarity`` for hybrid component reporting."""
        return self.semantic_similarity

    @property
    def tfidf_score(self) -> float:
        """Alias of ``tfidf_similarity`` for hybrid component reporting."""
        return self.tfidf_similarity

    @property
    def skills_in_resume(self) -> tuple[str, ...]:
        return self.resume_skills

    @property
    def skills_in_job(self) -> tuple[str, ...]:
        return self.job_skills
