"""Skill and signal extraction. Lexicon-based, not a trained model."""

from career_match.extraction.evidence import (
    build_evidence_profile,
    classify_skill_mentions,
    evidence_weighted_overlap,
)
from career_match.extraction.skills import extract_skill_names, extract_skills

__all__ = [
    "build_evidence_profile",
    "classify_skill_mentions",
    "evidence_weighted_overlap",
    "extract_skill_names",
    "extract_skills",
]
