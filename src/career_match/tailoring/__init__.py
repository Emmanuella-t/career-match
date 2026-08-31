"""Grounded resume tailoring package."""

from career_match.tailoring.evidence_map import EvidenceMapResult, build_evidence_map
from career_match.tailoring.protocol import ResumeRewriteProvider, RewriteSuggestion
from career_match.tailoring.providers import (
    DeterministicRewriteProvider,
    FakeRewriteProvider,
    OptionalLLMRewriteProvider,
)

__all__ = [
    "DeterministicRewriteProvider",
    "EvidenceMapResult",
    "FakeRewriteProvider",
    "OptionalLLMRewriteProvider",
    "ResumeRewriteProvider",
    "RewriteSuggestion",
    "build_evidence_map",
]
