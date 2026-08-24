"""Resume-to-job matching interfaces.

No production matcher is implemented. Callers should expect
``MatchingNotImplementedError`` until a measured baseline exists.
"""

from career_match.matching.protocol import Matcher, UnimplementedMatcher

__all__ = ["Matcher", "UnimplementedMatcher"]
