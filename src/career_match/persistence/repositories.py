"""Postgres-backed persistence repository (SQLAlchemy + psycopg)."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from career_match.persistence.errors import PersistenceUnavailableError, RecordNotFoundError
from career_match.persistence.models import (
    MatchAnalysisRow,
    ResumeRow,
    SavedJobRow,
    UserProfileRow,
)
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


def _as_str_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _profile_to_schema(row: UserProfileRow) -> UserProfile:
    return UserProfile(
        id=row.id,
        clerk_user_id=row.clerk_user_id,
        email=row.email,
        display_name=row.display_name,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _resume_to_schema(row: ResumeRow) -> ResumeRecord:
    return ResumeRecord(
        id=row.id,
        clerk_user_id=row.clerk_user_id,
        name=row.name,
        resume_text=row.resume_text,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _match_to_schema(row: MatchAnalysisRow) -> MatchAnalysisRecord:
    return MatchAnalysisRecord(
        id=row.id,
        clerk_user_id=row.clerk_user_id,
        resume_id=row.resume_id,
        job_title=row.job_title,
        company=row.company,
        job_description=row.job_description,
        matcher=row.matcher,
        matcher_version=row.matcher_version,
        overall_score=row.overall_score,
        matched_skills=_as_str_list(row.matched_skills),
        missing_skills=_as_str_list(row.missing_skills),
        weak_or_negated_skills=_as_str_list(row.weak_or_negated_skills),
        semantic_score=row.semantic_score,
        tfidf_score=row.tfidf_score,
        skill_overlap_score=row.skill_overlap_score,
        disclaimer=row.disclaimer,
        created_at=row.created_at,
    )


def _job_to_schema(row: SavedJobRow) -> SavedJobRecord:
    return SavedJobRecord(
        id=row.id,
        clerk_user_id=row.clerk_user_id,
        title=row.title,
        company=row.company,
        job_description=row.job_description,
        source_url=row.source_url,
        notes=row.notes,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class PostgresPersistenceStore:
    """User-scoped CRUD against Neon/Postgres via SQLAlchemy."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def _run(self, operation: Callable[[Session], object]) -> object:
        session = self._session_factory()
        try:
            result = operation(session)
            session.commit()
            return result
        except (RecordNotFoundError, PersistenceUnavailableError):
            session.rollback()
            raise
        except SQLAlchemyError as exc:
            session.rollback()
            raise PersistenceUnavailableError("persistence service unavailable") from exc
        except Exception as exc:  # noqa: BLE001
            session.rollback()
            raise PersistenceUnavailableError("persistence service unavailable") from exc
        finally:
            session.close()

    def upsert_profile(self, clerk_user_id: str, payload: ProfileUpsert) -> UserProfile:
        def op(session: Session) -> UserProfile:
            row = session.scalar(
                select(UserProfileRow).where(UserProfileRow.clerk_user_id == clerk_user_id)
            )
            now = _utcnow()
            if row is None:
                row = UserProfileRow(
                    clerk_user_id=clerk_user_id,
                    email=payload.email,
                    display_name=payload.display_name,
                    created_at=now,
                    updated_at=now,
                )
                session.add(row)
            else:
                if payload.email is not None:
                    row.email = payload.email
                if payload.display_name is not None:
                    row.display_name = payload.display_name
                row.updated_at = now
            session.flush()
            return _profile_to_schema(row)

        return self._run(op)  # type: ignore[return-value]

    def get_profile(self, clerk_user_id: str) -> UserProfile | None:
        def op(session: Session) -> UserProfile | None:
            row = session.scalar(
                select(UserProfileRow).where(UserProfileRow.clerk_user_id == clerk_user_id)
            )
            return _profile_to_schema(row) if row else None

        return self._run(op)  # type: ignore[return-value]

    def create_resume(self, clerk_user_id: str, payload: ResumeCreate) -> ResumeRecord:
        def op(session: Session) -> ResumeRecord:
            now = _utcnow()
            row = ResumeRow(
                clerk_user_id=clerk_user_id,
                name=payload.name,
                resume_text=payload.resume_text,
                created_at=now,
                updated_at=now,
            )
            session.add(row)
            session.flush()
            return _resume_to_schema(row)

        return self._run(op)  # type: ignore[return-value]

    def list_resumes(self, clerk_user_id: str) -> list[ResumeRecord]:
        def op(session: Session) -> list[ResumeRecord]:
            rows = session.scalars(
                select(ResumeRow)
                .where(ResumeRow.clerk_user_id == clerk_user_id)
                .order_by(ResumeRow.updated_at.desc())
            ).all()
            return [_resume_to_schema(row) for row in rows]

        return self._run(op)  # type: ignore[return-value]

    def get_resume(self, clerk_user_id: str, resume_id: UUID) -> ResumeRecord:
        def op(session: Session) -> ResumeRecord:
            row = session.scalar(
                select(ResumeRow).where(
                    ResumeRow.id == resume_id,
                    ResumeRow.clerk_user_id == clerk_user_id,
                )
            )
            if row is None:
                raise RecordNotFoundError("resume not found")
            return _resume_to_schema(row)

        return self._run(op)  # type: ignore[return-value]

    def update_resume(
        self, clerk_user_id: str, resume_id: UUID, payload: ResumeUpdate
    ) -> ResumeRecord:
        def op(session: Session) -> ResumeRecord:
            row = session.scalar(
                select(ResumeRow).where(
                    ResumeRow.id == resume_id,
                    ResumeRow.clerk_user_id == clerk_user_id,
                )
            )
            if row is None:
                raise RecordNotFoundError("resume not found")
            if payload.name is not None:
                row.name = payload.name
            if payload.resume_text is not None:
                row.resume_text = payload.resume_text
            row.updated_at = _utcnow()
            session.flush()
            return _resume_to_schema(row)

        return self._run(op)  # type: ignore[return-value]

    def delete_resume(self, clerk_user_id: str, resume_id: UUID) -> None:
        def op(session: Session) -> None:
            row = session.scalar(
                select(ResumeRow).where(
                    ResumeRow.id == resume_id,
                    ResumeRow.clerk_user_id == clerk_user_id,
                )
            )
            if row is None:
                raise RecordNotFoundError("resume not found")
            session.delete(row)

        self._run(op)

    def create_match(
        self, clerk_user_id: str, payload: MatchAnalysisCreate
    ) -> MatchAnalysisRecord:
        def op(session: Session) -> MatchAnalysisRecord:
            if payload.resume_id is not None:
                owned = session.scalar(
                    select(ResumeRow.id).where(
                        ResumeRow.id == payload.resume_id,
                        ResumeRow.clerk_user_id == clerk_user_id,
                    )
                )
                if owned is None:
                    raise RecordNotFoundError("resume not found")
            row = MatchAnalysisRow(
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
            session.add(row)
            session.flush()
            return _match_to_schema(row)

        return self._run(op)  # type: ignore[return-value]

    def list_matches(self, clerk_user_id: str) -> list[MatchAnalysisRecord]:
        def op(session: Session) -> list[MatchAnalysisRecord]:
            rows = session.scalars(
                select(MatchAnalysisRow)
                .where(MatchAnalysisRow.clerk_user_id == clerk_user_id)
                .order_by(MatchAnalysisRow.created_at.desc())
            ).all()
            return [_match_to_schema(row) for row in rows]

        return self._run(op)  # type: ignore[return-value]

    def get_match(self, clerk_user_id: str, match_id: UUID) -> MatchAnalysisRecord:
        def op(session: Session) -> MatchAnalysisRecord:
            row = session.scalar(
                select(MatchAnalysisRow).where(
                    MatchAnalysisRow.id == match_id,
                    MatchAnalysisRow.clerk_user_id == clerk_user_id,
                )
            )
            if row is None:
                raise RecordNotFoundError("match not found")
            return _match_to_schema(row)

        return self._run(op)  # type: ignore[return-value]

    def delete_match(self, clerk_user_id: str, match_id: UUID) -> None:
        def op(session: Session) -> None:
            row = session.scalar(
                select(MatchAnalysisRow).where(
                    MatchAnalysisRow.id == match_id,
                    MatchAnalysisRow.clerk_user_id == clerk_user_id,
                )
            )
            if row is None:
                raise RecordNotFoundError("match not found")
            session.delete(row)

        self._run(op)

    def create_job(self, clerk_user_id: str, payload: SavedJobCreate) -> SavedJobRecord:
        def op(session: Session) -> SavedJobRecord:
            now = _utcnow()
            row = SavedJobRow(
                clerk_user_id=clerk_user_id,
                title=payload.title,
                company=payload.company,
                job_description=payload.job_description,
                source_url=payload.source_url,
                notes=payload.notes,
                created_at=now,
                updated_at=now,
            )
            session.add(row)
            session.flush()
            return _job_to_schema(row)

        return self._run(op)  # type: ignore[return-value]

    def list_jobs(self, clerk_user_id: str) -> list[SavedJobRecord]:
        def op(session: Session) -> list[SavedJobRecord]:
            rows = session.scalars(
                select(SavedJobRow)
                .where(SavedJobRow.clerk_user_id == clerk_user_id)
                .order_by(SavedJobRow.updated_at.desc())
            ).all()
            return [_job_to_schema(row) for row in rows]

        return self._run(op)  # type: ignore[return-value]

    def get_job(self, clerk_user_id: str, job_id: UUID) -> SavedJobRecord:
        def op(session: Session) -> SavedJobRecord:
            row = session.scalar(
                select(SavedJobRow).where(
                    SavedJobRow.id == job_id,
                    SavedJobRow.clerk_user_id == clerk_user_id,
                )
            )
            if row is None:
                raise RecordNotFoundError("job not found")
            return _job_to_schema(row)

        return self._run(op)  # type: ignore[return-value]

    def update_job(
        self, clerk_user_id: str, job_id: UUID, payload: SavedJobUpdate
    ) -> SavedJobRecord:
        def op(session: Session) -> SavedJobRecord:
            row = session.scalar(
                select(SavedJobRow).where(
                    SavedJobRow.id == job_id,
                    SavedJobRow.clerk_user_id == clerk_user_id,
                )
            )
            if row is None:
                raise RecordNotFoundError("job not found")
            if payload.title is not None:
                row.title = payload.title
            if payload.company is not None:
                row.company = payload.company
            if payload.job_description is not None:
                row.job_description = payload.job_description
            if payload.source_url is not None:
                row.source_url = payload.source_url
            if payload.notes is not None:
                row.notes = payload.notes
            row.updated_at = _utcnow()
            session.flush()
            return _job_to_schema(row)

        return self._run(op)  # type: ignore[return-value]

    def delete_job(self, clerk_user_id: str, job_id: UUID) -> None:
        def op(session: Session) -> None:
            row = session.scalar(
                select(SavedJobRow).where(
                    SavedJobRow.id == job_id,
                    SavedJobRow.clerk_user_id == clerk_user_id,
                )
            )
            if row is None:
                raise RecordNotFoundError("job not found")
            session.delete(row)

        self._run(op)
