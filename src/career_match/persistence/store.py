"""Persistence store protocol, in-memory test store, and factory."""

from __future__ import annotations

import threading
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID, uuid4

from career_match.persistence.errors import PersistenceNotConfiguredError, RecordNotFoundError
from career_match.persistence.schemas import (
    MatchAnalysisCreate,
    MatchAnalysisRecord,
    ProfileUpsert,
    ResumeCreate,
    ResumeRecord,
    ResumeUpdate,
    SavedJobCreate,
    SavedJobRecord,
    SavedJobUpdate,
    UserProfile,
)


def _utcnow() -> datetime:
    return datetime.now(UTC)


class PersistenceStore(Protocol):
    """User-scoped persistence operations."""

    def upsert_profile(self, clerk_user_id: str, payload: ProfileUpsert) -> UserProfile: ...

    def get_profile(self, clerk_user_id: str) -> UserProfile | None: ...

    def create_resume(self, clerk_user_id: str, payload: ResumeCreate) -> ResumeRecord: ...

    def list_resumes(self, clerk_user_id: str) -> list[ResumeRecord]: ...

    def get_resume(self, clerk_user_id: str, resume_id: UUID) -> ResumeRecord: ...

    def update_resume(
        self, clerk_user_id: str, resume_id: UUID, payload: ResumeUpdate
    ) -> ResumeRecord: ...

    def delete_resume(self, clerk_user_id: str, resume_id: UUID) -> None: ...

    def create_match(
        self, clerk_user_id: str, payload: MatchAnalysisCreate
    ) -> MatchAnalysisRecord: ...

    def list_matches(self, clerk_user_id: str) -> list[MatchAnalysisRecord]: ...

    def get_match(self, clerk_user_id: str, match_id: UUID) -> MatchAnalysisRecord: ...

    def delete_match(self, clerk_user_id: str, match_id: UUID) -> None: ...

    def create_job(self, clerk_user_id: str, payload: SavedJobCreate) -> SavedJobRecord: ...

    def list_jobs(self, clerk_user_id: str) -> list[SavedJobRecord]: ...

    def get_job(self, clerk_user_id: str, job_id: UUID) -> SavedJobRecord: ...

    def update_job(
        self, clerk_user_id: str, job_id: UUID, payload: SavedJobUpdate
    ) -> SavedJobRecord: ...

    def delete_job(self, clerk_user_id: str, job_id: UUID) -> None: ...


class InMemoryPersistenceStore:
    """Thread-safe store for unit tests (no database)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.profiles: dict[str, UserProfile] = {}
        self.resumes: dict[UUID, ResumeRecord] = {}
        self.matches: dict[UUID, MatchAnalysisRecord] = {}
        self.jobs: dict[UUID, SavedJobRecord] = {}

    def upsert_profile(self, clerk_user_id: str, payload: ProfileUpsert) -> UserProfile:
        with self._lock:
            existing = self.profiles.get(clerk_user_id)
            now = _utcnow()
            if existing is None:
                record = UserProfile(
                    id=uuid4(),
                    clerk_user_id=clerk_user_id,
                    email=payload.email,
                    display_name=payload.display_name,
                    created_at=now,
                    updated_at=now,
                )
            else:
                record = existing.model_copy(
                    update={
                        "email": payload.email
                        if payload.email is not None
                        else existing.email,
                        "display_name": payload.display_name
                        if payload.display_name is not None
                        else existing.display_name,
                        "updated_at": now,
                    }
                )
            self.profiles[clerk_user_id] = record
            return record

    def get_profile(self, clerk_user_id: str) -> UserProfile | None:
        with self._lock:
            return self.profiles.get(clerk_user_id)

    def create_resume(self, clerk_user_id: str, payload: ResumeCreate) -> ResumeRecord:
        with self._lock:
            now = _utcnow()
            record = ResumeRecord(
                id=uuid4(),
                clerk_user_id=clerk_user_id,
                name=payload.name,
                resume_text=payload.resume_text,
                created_at=now,
                updated_at=now,
            )
            self.resumes[record.id] = record
            return record

    def list_resumes(self, clerk_user_id: str) -> list[ResumeRecord]:
        with self._lock:
            rows = [r for r in self.resumes.values() if r.clerk_user_id == clerk_user_id]
            return sorted(rows, key=lambda r: r.updated_at, reverse=True)

    def get_resume(self, clerk_user_id: str, resume_id: UUID) -> ResumeRecord:
        with self._lock:
            record = self.resumes.get(resume_id)
            if record is None or record.clerk_user_id != clerk_user_id:
                raise RecordNotFoundError("resume not found")
            return record

    def update_resume(
        self, clerk_user_id: str, resume_id: UUID, payload: ResumeUpdate
    ) -> ResumeRecord:
        with self._lock:
            record = self.resumes.get(resume_id)
            if record is None or record.clerk_user_id != clerk_user_id:
                raise RecordNotFoundError("resume not found")
            updated = record.model_copy(
                update={
                    "name": payload.name if payload.name is not None else record.name,
                    "resume_text": payload.resume_text
                    if payload.resume_text is not None
                    else record.resume_text,
                    "updated_at": _utcnow(),
                }
            )
            self.resumes[resume_id] = updated
            return updated

    def delete_resume(self, clerk_user_id: str, resume_id: UUID) -> None:
        with self._lock:
            record = self.resumes.get(resume_id)
            if record is None or record.clerk_user_id != clerk_user_id:
                raise RecordNotFoundError("resume not found")
            del self.resumes[resume_id]
            for match_id, match in list(self.matches.items()):
                if match.resume_id == resume_id:
                    self.matches[match_id] = match.model_copy(update={"resume_id": None})

    def create_match(
        self, clerk_user_id: str, payload: MatchAnalysisCreate
    ) -> MatchAnalysisRecord:
        with self._lock:
            if payload.resume_id is not None:
                resume = self.resumes.get(payload.resume_id)
                if resume is None or resume.clerk_user_id != clerk_user_id:
                    raise RecordNotFoundError("resume not found")
            record = MatchAnalysisRecord(
                id=uuid4(),
                clerk_user_id=clerk_user_id,
                resume_id=payload.resume_id,
                job_title=payload.job_title,
                company=payload.company,
                job_description=payload.job_description,
                matcher=payload.matcher,
                matcher_version=payload.matcher_version,
                overall_score=payload.overall_score,
                matched_skills=list(payload.matched_skills),
                missing_skills=list(payload.missing_skills),
                weak_or_negated_skills=list(payload.weak_or_negated_skills),
                semantic_score=payload.semantic_score,
                tfidf_score=payload.tfidf_score,
                skill_overlap_score=payload.skill_overlap_score,
                disclaimer=payload.disclaimer,
                created_at=_utcnow(),
            )
            self.matches[record.id] = record
            return record

    def list_matches(self, clerk_user_id: str) -> list[MatchAnalysisRecord]:
        with self._lock:
            rows = [m for m in self.matches.values() if m.clerk_user_id == clerk_user_id]
            return sorted(rows, key=lambda m: m.created_at, reverse=True)

    def get_match(self, clerk_user_id: str, match_id: UUID) -> MatchAnalysisRecord:
        with self._lock:
            record = self.matches.get(match_id)
            if record is None or record.clerk_user_id != clerk_user_id:
                raise RecordNotFoundError("match not found")
            return record

    def delete_match(self, clerk_user_id: str, match_id: UUID) -> None:
        with self._lock:
            record = self.matches.get(match_id)
            if record is None or record.clerk_user_id != clerk_user_id:
                raise RecordNotFoundError("match not found")
            del self.matches[match_id]

    def create_job(self, clerk_user_id: str, payload: SavedJobCreate) -> SavedJobRecord:
        with self._lock:
            now = _utcnow()
            record = SavedJobRecord(
                id=uuid4(),
                clerk_user_id=clerk_user_id,
                title=payload.title,
                company=payload.company,
                job_description=payload.job_description,
                source_url=payload.source_url,
                notes=payload.notes,
                created_at=now,
                updated_at=now,
            )
            self.jobs[record.id] = record
            return record

    def list_jobs(self, clerk_user_id: str) -> list[SavedJobRecord]:
        with self._lock:
            rows = [j for j in self.jobs.values() if j.clerk_user_id == clerk_user_id]
            return sorted(rows, key=lambda j: j.updated_at, reverse=True)

    def get_job(self, clerk_user_id: str, job_id: UUID) -> SavedJobRecord:
        with self._lock:
            record = self.jobs.get(job_id)
            if record is None or record.clerk_user_id != clerk_user_id:
                raise RecordNotFoundError("job not found")
            return record

    def update_job(
        self, clerk_user_id: str, job_id: UUID, payload: SavedJobUpdate
    ) -> SavedJobRecord:
        with self._lock:
            record = self.jobs.get(job_id)
            if record is None or record.clerk_user_id != clerk_user_id:
                raise RecordNotFoundError("job not found")
            data = record.model_dump()
            for field in ("title", "company", "job_description", "source_url", "notes"):
                value = getattr(payload, field)
                if value is not None:
                    data[field] = value
            data["updated_at"] = _utcnow()
            updated = SavedJobRecord(**data)
            self.jobs[job_id] = updated
            return updated

    def delete_job(self, clerk_user_id: str, job_id: UUID) -> None:
        with self._lock:
            record = self.jobs.get(job_id)
            if record is None or record.clerk_user_id != clerk_user_id:
                raise RecordNotFoundError("job not found")
            del self.jobs[job_id]


def get_persistence_store(override: PersistenceStore | None = None) -> PersistenceStore:
    """Return the configured store, or ``override`` when provided (tests)."""
    if override is not None:
        return override
    from career_match.persistence.database import database_configured, get_session_factory
    from career_match.persistence.repositories import PostgresPersistenceStore

    if not database_configured():
        raise PersistenceNotConfiguredError("DATABASE_URL is required for persistence")
    return PostgresPersistenceStore(get_session_factory())
