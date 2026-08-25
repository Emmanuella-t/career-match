"""Career Match: explainable resume-to-job matching.

The ML package now includes Baseline Matcher v0.1 (TF-IDF cosine similarity
plus catalog skill overlap). That score is a development relevance signal,
not a production hiring model.
"""

from career_match.core.exceptions import CareerMatchError, MatchingNotImplementedError
from career_match.matching import BaselineMatcher

__version__ = "0.1.0"
__all__ = [
    "BaselineMatcher",
    "CareerMatchError",
    "MatchingNotImplementedError",
    "__version__",
]
