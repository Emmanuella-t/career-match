"""Rewrite provider protocol and result types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from career_match.tailoring.evidence_map import EvidenceMapResult

TailorSection = str  # summary | experience | projects | skills | all


@dataclass(frozen=True, slots=True)
class RewriteSuggestion:
    section: str
    original_text: str
    suggested_text: str
    keywords_introduced: tuple[str, ...]
    support_reason: str
    support_level: str  # high | medium | low


class ResumeRewriteProvider(Protocol):
    """Generates grounded rewrite suggestions from approved evidence only."""

    @property
    def name(self) -> str: ...

    @property
    def available(self) -> bool: ...

    def generate_rewrites(
        self,
        *,
        resume_text: str,
        job_text: str,
        evidence_map: EvidenceMapResult,
        target: TailorSection,
    ) -> tuple[RewriteSuggestion, ...]: ...
