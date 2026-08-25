"""Matching-layer tests."""

import pytest

from career_match.core.exceptions import MatchingNotImplementedError
from career_match.matching import BaselineMatcher, Matcher, UnimplementedMatcher


def test_matcher_protocol_not_implemented() -> None:
    matcher: Matcher = UnimplementedMatcher()
    with pytest.raises(MatchingNotImplementedError, match="No production matching model"):
        matcher.match("Python developer", "Looking for Python")


def test_baseline_matcher_satisfies_protocol() -> None:
    matcher: Matcher = BaselineMatcher()
    result = matcher.match("Python Git Linux", "Python Git")
    assert 0 <= result.score <= 100
    assert result.evidence


def test_matching_module_exports_protocol() -> None:
    assert Matcher.__name__ == "Matcher"
    assert UnimplementedMatcher().match
