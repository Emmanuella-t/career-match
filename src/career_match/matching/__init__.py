"""Matching contracts and implementations.

``BaselineMatcher`` is the lexical TF-IDF + skill-overlap baseline (v0.1).
``SemanticMatcher`` is a standalone sentence-embedding matcher (v0.1).
``HybridMatcher`` combines semantic, TF-IDF, and evidence-aware skill coverage
(v0.1). ``UnimplementedMatcher`` remains a no-op sentinel.
"""

from career_match.matching.baseline import BaselineMatcher, skill_overlap
from career_match.matching.config import BaselineConfig
from career_match.matching.hybrid import HybridMatcher
from career_match.matching.hybrid_config import HybridConfig
from career_match.matching.protocol import Matcher, UnimplementedMatcher
from career_match.matching.semantic import SemanticMatcher
from career_match.matching.semantic_config import SemanticConfig

__all__ = [
    "BaselineConfig",
    "BaselineMatcher",
    "HybridConfig",
    "HybridMatcher",
    "Matcher",
    "SemanticConfig",
    "SemanticMatcher",
    "UnimplementedMatcher",
    "skill_overlap",
]
