"""Matching-layer tests. No production model is implemented."""

import pytest

from career_match.core.exceptions import MatchingNotImplementedError
from career_match.core.types import MatchResult
from career_match.matching import Matcher, UnimplementedMatcher


def test_matcher_protocol_not_implemented() -> None:
    matcher: Matcher = UnimplementedMatcher()
    with pytest.raises(MatchingNotImplementedError, match="No production matching model"):
        matcher.match("Python developer", "Looking for Python")


def test_match_result_is_documented_placeholder() -> None:
    result = MatchResult(
        score=0.0,
        evidence=(),
        skills_in_resume=("python",),
        skills_in_job=("python",),
    )
    assert result.score == 0.0
    assert result.evidence == ()
    assert result.skills_in_resume == ("python",)


def test_matching_module_exports_protocol() -> None:
    assert Matcher.__name__ == "Matcher"
    assert UnimplementedMatcher().match
