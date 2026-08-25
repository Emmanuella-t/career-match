"""Career Match: explainable resume-to-job matching.

The ML package includes Baseline Matcher v0.1, Semantic Matcher v0.1, and
Hybrid Matcher v0.1. Those scores are development relevance signals, not a
production hiring model.
"""

from career_match.core.exceptions import CareerMatchError, MatchingNotImplementedError
from career_match.matching import BaselineMatcher, HybridMatcher, SemanticMatcher

__version__ = "0.1.0"
__all__ = [
    "BaselineMatcher",
    "CareerMatchError",
    "HybridMatcher",
    "MatchingNotImplementedError",
    "SemanticMatcher",
    "__version__",
]
