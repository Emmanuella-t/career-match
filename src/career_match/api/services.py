"""Matcher service with lazy, request-reusable instances.

Importing this module does not download MiniLM. Semantic/hybrid encoders
load on first use of those matchers and are then reused for the process
lifetime of ``MatcherService``.
"""

from __future__ import annotations

from career_match.api.schemas import MatchResponse
from career_match.api.settings import SCORE_DISCLAIMER, SUPPORTED_MATCHERS
from career_match.core.types import MatchResult
from career_match.matching.baseline import BaselineMatcher
from career_match.matching.config import MATCHER_NAME as LEXICAL_NAME
from career_match.matching.config import MATCHER_VERSION as LEXICAL_VERSION
from career_match.matching.hybrid import HybridMatcher
from career_match.matching.hybrid_config import HYBRID_MATCHER_NAME, HYBRID_MATCHER_VERSION
from career_match.matching.semantic import SemanticMatcher
from career_match.matching.semantic_config import (
    SEMANTIC_MATCHER_NAME,
    SEMANTIC_MATCHER_VERSION,
)


class UnsupportedMatcherError(ValueError):
    """Raised when the client asks for an unknown matcher key."""


class MatcherService:
    """Owns long-lived matcher instances for the API process."""

    def __init__(
        self,
        *,
        lexical: BaselineMatcher | None = None,
        semantic: SemanticMatcher | None = None,
        hybrid: HybridMatcher | None = None,
    ) -> None:
        self._lexical = lexical
        self._semantic = semantic
        self._hybrid = hybrid

    @property
    def lexical(self) -> BaselineMatcher:
        if self._lexical is None:
            self._lexical = BaselineMatcher()
        return self._lexical

    @property
    def semantic(self) -> SemanticMatcher:
        if self._semantic is None:
            self._semantic = SemanticMatcher()
        return self._semantic

    @property
    def hybrid(self) -> HybridMatcher:
        if self._hybrid is None:
            # Share the semantic instance so MiniLM loads once per process.
            self._hybrid = HybridMatcher(semantic_matcher=self.semantic)
        return self._hybrid

    def match(self, resume_text: str, job_description: str, matcher: str) -> MatchResponse:
        key = matcher.strip().lower()
        if key not in SUPPORTED_MATCHERS:
            raise UnsupportedMatcherError(
                f"unsupported matcher {matcher!r}; "
                f"supported values: {', '.join(SUPPORTED_MATCHERS)}"
            )

        if key == "lexical":
            result = self.lexical.match(resume_text, job_description)
            return _to_response(
                result,
                matcher_name=LEXICAL_NAME,
                matcher_version=LEXICAL_VERSION,
                include_semantic=False,
            )
        if key == "semantic":
            result = self.semantic.match(resume_text, job_description)
            return _to_response(
                result,
                matcher_name=SEMANTIC_MATCHER_NAME,
                matcher_version=SEMANTIC_MATCHER_VERSION,
                include_semantic=True,
                include_lexical_channels=False,
            )
        result = self.hybrid.match(resume_text, job_description)
        return _to_response(
            result,
            matcher_name=HYBRID_MATCHER_NAME,
            matcher_version=HYBRID_MATCHER_VERSION,
            include_semantic=True,
            include_lexical_channels=True,
        )


def _to_response(
    result: MatchResult,
    *,
    matcher_name: str,
    matcher_version: str,
    include_semantic: bool,
    include_lexical_channels: bool = True,
) -> MatchResponse:
    semantic_score = float(result.semantic_similarity) if include_semantic else None
    if include_lexical_channels:
        tfidf_score = float(result.tfidf_similarity)
        skill_overlap_score = float(result.skill_overlap_score)
    else:
        tfidf_score = None
        skill_overlap_score = None
    return MatchResponse(
        matcher=matcher_name,
        matcher_version=matcher_version,
        overall_score=float(result.overall_score),
        semantic_score=semantic_score,
        tfidf_score=tfidf_score,
        skill_overlap_score=skill_overlap_score,
        matched_skills=list(result.matched_skills),
        missing_skills=list(result.missing_skills),
        weak_or_negated_skills=list(result.weak_or_negated_skills),
        disclaimer=SCORE_DISCLAIMER,
    )
