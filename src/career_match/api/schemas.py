"""Pydantic request/response schemas for the matching API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from career_match.api.settings import (
    DEFAULT_MATCHER,
    MAX_TEXT_CHARS,
    SCORE_DISCLAIMER,
    SUPPORTED_MATCHERS,
)

MatcherName = Literal["semantic", "hybrid", "lexical"]


class MatchRequest(BaseModel):
    """Input for ``POST /api/v1/match``."""

    resume_text: str = Field(..., description="Full resume text to score.")
    job_description: str = Field(..., description="Job description text to score against.")
    matcher: MatcherName = Field(
        default=DEFAULT_MATCHER,  # type: ignore[assignment]
        description=(
            "Which matcher to use. Default is semantic (strongest top-rank "
            "quality on frozen holdout v0.3; not a universal superiority claim)."
        ),
    )

    @field_validator("resume_text", "job_description")
    @classmethod
    def _non_empty_and_bounded(cls, value: str) -> str:
        if not isinstance(value, str):
            raise TypeError("text fields must be strings")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("text must be a non-empty string after stripping whitespace")
        if len(cleaned) > MAX_TEXT_CHARS:
            raise ValueError(
                f"text exceeds maximum length of {MAX_TEXT_CHARS} characters "
                f"(received {len(cleaned)})"
            )
        return cleaned

    @field_validator("matcher")
    @classmethod
    def _supported_matcher(cls, value: str) -> str:
        if value not in SUPPORTED_MATCHERS:
            raise ValueError(
                f"unsupported matcher {value!r}; "
                f"supported values: {', '.join(SUPPORTED_MATCHERS)}"
            )
        return value


class MatchResponse(BaseModel):
    """Explainable match result. No embeddings are returned."""

    matcher: str
    matcher_version: str
    overall_score: float
    semantic_score: float | None = None
    tfidf_score: float | None = None
    skill_overlap_score: float | None = None
    matched_skills: list[str]
    missing_skills: list[str]
    weak_or_negated_skills: list[str] = Field(default_factory=list)
    disclaimer: str = SCORE_DISCLAIMER


class HealthResponse(BaseModel):
    status: str = "ok"


class ErrorResponse(BaseModel):
    detail: str
