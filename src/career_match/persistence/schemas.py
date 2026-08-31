"""Pydantic models for persistence records and API payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from career_match.api.settings import MAX_TEXT_CHARS


def _require_non_empty(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must be a non-empty string")
    return cleaned


def _bounded_text(value: str, field_name: str) -> str:
    cleaned = _require_non_empty(value, field_name)
    if len(cleaned) > MAX_TEXT_CHARS:
        raise ValueError(
            f"{field_name} exceeds maximum length of {MAX_TEXT_CHARS} characters"
        )
    return cleaned


def _optional_trim(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------


class UserProfile(BaseModel):
    id: UUID
    clerk_user_id: str
    email: str | None = None
    display_name: str | None = None
    created_at: datetime
    updated_at: datetime


class ProfileUpsert(BaseModel):
    email: str | None = None
    display_name: str | None = None

    @field_validator("email", "display_name", mode="before")
    @classmethod
    def _trim_optional(cls, value: Any) -> str | None:
        if value is None:
            return None
        return _optional_trim(str(value))


# ---------------------------------------------------------------------------
# Resumes
# ---------------------------------------------------------------------------


class ResumeCreate(BaseModel):
    name: str
    resume_text: str

    @field_validator("name")
    @classmethod
    def _name(cls, value: str) -> str:
        cleaned = _require_non_empty(value, "name")
        if len(cleaned) > 200:
            raise ValueError("name must be at most 200 characters")
        return cleaned

    @field_validator("resume_text")
    @classmethod
    def _text(cls, value: str) -> str:
        return _bounded_text(value, "resume_text")


class ResumeUpdate(BaseModel):
    name: str | None = None
    resume_text: str | None = None

    @field_validator("name")
    @classmethod
    def _name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = _require_non_empty(value, "name")
        if len(cleaned) > 200:
            raise ValueError("name must be at most 200 characters")
        return cleaned

    @field_validator("resume_text")
    @classmethod
    def _text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _bounded_text(value, "resume_text")

    @model_validator(mode="after")
    def _at_least_one(self) -> ResumeUpdate:
        if self.name is None and self.resume_text is None:
            raise ValueError("at least one of name or resume_text is required")
        return self


class ResumeRecord(BaseModel):
    id: UUID
    clerk_user_id: str
    name: str
    resume_text: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Match analyses
# ---------------------------------------------------------------------------


class MatchAnalysisCreate(BaseModel):
    """Persist a successful match result for the authenticated user."""

    resume_id: UUID | None = None
    job_title: str | None = None
    company: str | None = None
    job_description: str
    matcher: str
    matcher_version: str | None = None
    overall_score: float
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    weak_or_negated_skills: list[str] = Field(default_factory=list)
    semantic_score: float | None = None
    tfidf_score: float | None = None
    skill_overlap_score: float | None = None
    disclaimer: str | None = None

    @field_validator("job_description")
    @classmethod
    def _job_description(cls, value: str) -> str:
        return _bounded_text(value, "job_description")

    @field_validator("job_title", "company", "matcher_version", "disclaimer")
    @classmethod
    def _trim_optional_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _optional_trim(value)

    @field_validator("matcher")
    @classmethod
    def _matcher_required(cls, value: str) -> str:
        return _require_non_empty(value, "matcher")

    @field_validator("overall_score")
    @classmethod
    def _score_range(cls, value: float) -> float:
        if not 0 <= value <= 100:
            raise ValueError("overall_score must be between 0 and 100")
        return value


class MatchAnalysisRecord(BaseModel):
    id: UUID
    clerk_user_id: str
    resume_id: UUID | None = None
    job_title: str | None = None
    company: str | None = None
    job_description: str
    matcher: str
    matcher_version: str | None = None
    overall_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    weak_or_negated_skills: list[str]
    semantic_score: float | None = None
    tfidf_score: float | None = None
    skill_overlap_score: float | None = None
    disclaimer: str | None = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Saved jobs
# ---------------------------------------------------------------------------


class SavedJobCreate(BaseModel):
    title: str
    company: str | None = None
    job_description: str
    source_url: str | None = None
    notes: str | None = None

    @field_validator("title")
    @classmethod
    def _title(cls, value: str) -> str:
        cleaned = _require_non_empty(value, "title")
        if len(cleaned) > 300:
            raise ValueError("title must be at most 300 characters")
        return cleaned

    @field_validator("job_description")
    @classmethod
    def _description(cls, value: str) -> str:
        return _bounded_text(value, "job_description")

    @field_validator("company", "source_url", "notes")
    @classmethod
    def _optional(cls, value: str | None) -> str | None:
        return _optional_trim(value) if value is not None else None


class SavedJobUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    job_description: str | None = None
    source_url: str | None = None
    notes: str | None = None

    @field_validator("title")
    @classmethod
    def _title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = _require_non_empty(value, "title")
        if len(cleaned) > 300:
            raise ValueError("title must be at most 300 characters")
        return cleaned

    @field_validator("job_description")
    @classmethod
    def _description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _bounded_text(value, "job_description")

    @field_validator("company", "source_url", "notes")
    @classmethod
    def _optional(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _optional_trim(value)

    @model_validator(mode="after")
    def _at_least_one(self) -> SavedJobUpdate:
        if all(
            getattr(self, field) is None
            for field in ("title", "company", "job_description", "source_url", "notes")
        ):
            raise ValueError("at least one field is required")
        return self


class SavedJobRecord(BaseModel):
    id: UUID
    clerk_user_id: str
    title: str
    company: str | None = None
    job_description: str
    source_url: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
