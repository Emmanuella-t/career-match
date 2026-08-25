"""Matching contracts and implementations.

``BaselineMatcher`` is the first measured lexical baseline (v0.1).
``UnimplementedMatcher`` remains as an explicit sentinel for callers that
must not silently pick up an unmeasured heuristic.
"""

from career_match.matching.baseline import BaselineMatcher, skill_overlap
from career_match.matching.config import BaselineConfig
from career_match.matching.protocol import Matcher, UnimplementedMatcher

__all__ = [
    "BaselineConfig",
    "BaselineMatcher",
    "Matcher",
    "UnimplementedMatcher",
    "skill_overlap",
]
