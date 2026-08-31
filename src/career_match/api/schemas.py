"""Pydantic request/response schemas for the matching API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

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


class ReadyResponse(BaseModel):
    """Process readiness without forcing MiniLM download."""

    status: str = "ready"
    semantic_model_loaded: bool = False


class ErrorResponse(BaseModel):
    detail: str


class ResumeParseResponse(BaseModel):
    """Structured response from resume file parsing."""

    filename: str
    file_type: str
    character_count: int
    extracted_text: str


class JobDiscoverRequest(BaseModel):
    """Input for ranking discoverable jobs against a resume."""

    resume_id: UUID | None = None
    resume_text: str | None = None
    limit: int | None = Field(default=None, ge=1, le=50)
    location: str | None = None
    employment_type: str | None = None
    matcher: MatcherName = Field(
        default=DEFAULT_MATCHER,  # type: ignore[assignment]
        description="Matcher used to rank jobs (default semantic).",
    )

    @field_validator("resume_text")
    @classmethod
    def _resume_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("resume_text must be a non-empty string after stripping whitespace")
        if len(cleaned) > MAX_TEXT_CHARS:
            raise ValueError(
                f"resume_text exceeds maximum length of {MAX_TEXT_CHARS} characters"
            )
        return cleaned

    @field_validator("location", "employment_type", mode="before")
    @classmethod
    def _trim_filters(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None

    @field_validator("matcher")
    @classmethod
    def _supported_matcher(cls, value: str) -> str:
        if value not in SUPPORTED_MATCHERS:
            raise ValueError(
                f"unsupported matcher {value!r}; "
                f"supported values: {', '.join(SUPPORTED_MATCHERS)}"
            )
        return value

    @model_validator(mode="after")
    def _resume_source(self) -> JobDiscoverRequest:
        if self.resume_id is None and self.resume_text is None:
            raise ValueError("either resume_id or resume_text is required")
        if self.resume_id is not None and self.resume_text is not None:
            raise ValueError("provide resume_id or resume_text, not both")
        return self


class JobOpportunityResponse(BaseModel):
    id: UUID
    title: str
    company: str | None = None
    location: str | None = None
    description: str
    source: str
    source_url: str | None = None
    apply_url: str | None = None
    employment_type: str | None = None
    created_at: datetime
    updated_at: datetime


class RankedJobResult(BaseModel):
    job: JobOpportunityResponse
    overall_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    weak_or_negated_skills: list[str] = Field(default_factory=list)
    matcher: str
    matcher_version: str
    semantic_score: float | None = None
    tfidf_score: float | None = None
    skill_overlap_score: float | None = None
    disclaimer: str = SCORE_DISCLAIMER


class JobDiscoverResponse(BaseModel):
    results: list[RankedJobResult]
    matcher: str
    matcher_version: str
    disclaimer: str = SCORE_DISCLAIMER
    resume_id: UUID | None = None
    source: str
