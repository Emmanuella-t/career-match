"""Career Match: explainable resume-to-job matching.

This package is the ML foundation. No production matching model is
implemented yet. Subpackages exist so data loading, parsing, extraction,
matching, and evaluation can evolve independently.
"""

from career_match.core.exceptions import CareerMatchError, MatchingNotImplementedError

__version__ = "0.1.0"
__all__ = ["CareerMatchError", "MatchingNotImplementedError", "__version__"]
