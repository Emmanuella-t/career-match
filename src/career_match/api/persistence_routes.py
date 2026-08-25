"""Authenticated persistence HTTP routes (Clerk + Supabase)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from career_match.api.auth import ClerkIdentity, require_clerk_user
from career_match.persistence.errors import (
    PersistenceNotConfiguredError,
    PersistenceUnavailableError,
    RecordNotFoundError,
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
from career_match.persistence.store import PersistenceStore, get_persistence_store

router = APIRouter(prefix="/api/v1", tags=["persistence"])


def get_store(request: Request) -> PersistenceStore:
    override = getattr(request.app.state, "persistence_store", None)
    try:
        return get_persistence_store(override)
    except PersistenceNotConfiguredError as exc:
        raise HTTPException(
            status_code=503,
            detail="persistence is not configured",
        ) from exc


def _map_persistence_error(exc: Exception) -> HTTPException:
    if isinstance(exc, RecordNotFoundError):
        return HTTPException(status_code=404, detail="not found")
    if isinstance(exc, PersistenceNotConfiguredError):
        return HTTPException(status_code=503, detail="persistence is not configured")
    if isinstance(exc, PersistenceUnavailableError):
        return HTTPException(status_code=503, detail="persistence service unavailable")
    return HTTPException(status_code=503, detail="persistence service unavailable")


def _ensure_profile(store: PersistenceStore, identity: ClerkIdentity) -> UserProfile:
    return store.upsert_profile(
        identity.user_id,
        ProfileUpsert(email=identity.email, display_name=identity.display_name),
    )


StoreDep = Annotated[PersistenceStore, Depends(get_store)]
UserDep = Annotated[ClerkIdentity, Depends(require_clerk_user)]


@router.get("/profile", response_model=UserProfile)
def get_profile(store: StoreDep, identity: UserDep) -> UserProfile:
    try:
        existing = store.get_profile(identity.user_id)
        if existing is not None:
            return existing
        return _ensure_profile(store, identity)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, HTTPException):
            raise
        raise _map_persistence_error(exc) from exc


@router.get("/resumes", response_model=list[ResumeRecord])
def list_resumes(store: StoreDep, identity: UserDep) -> list[ResumeRecord]:
    try:
        _ensure_profile(store, identity)
        return store.list_resumes(identity.user_id)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, HTTPException):
            raise
        raise _map_persistence_error(exc) from exc


@router.post("/resumes", response_model=ResumeRecord, status_code=201)
def create_resume(
    payload: ResumeCreate,
    store: StoreDep,
    identity: UserDep,
) -> ResumeRecord:
    try:
        _ensure_profile(store, identity)
        return store.create_resume(identity.user_id, payload)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, HTTPException):
            raise
        raise _map_persistence_error(exc) from exc


@router.get("/resumes/{resume_id}", response_model=ResumeRecord)
def get_resume(resume_id: UUID, store: StoreDep, identity: UserDep) -> ResumeRecord:
    try:
        return store.get_resume(identity.user_id, resume_id)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, HTTPException):
            raise
        raise _map_persistence_error(exc) from exc


@router.patch("/resumes/{resume_id}", response_model=ResumeRecord)
def update_resume(
    resume_id: UUID,
    payload: ResumeUpdate,
    store: StoreDep,
    identity: UserDep,
) -> ResumeRecord:
    try:
        return store.update_resume(identity.user_id, resume_id, payload)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, HTTPException):
            raise
        raise _map_persistence_error(exc) from exc


@router.delete("/resumes/{resume_id}", status_code=204, response_class=Response)
def delete_resume(resume_id: UUID, store: StoreDep, identity: UserDep) -> Response:
    try:
        store.delete_resume(identity.user_id, resume_id)
        return Response(status_code=204)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, HTTPException):
            raise
        raise _map_persistence_error(exc) from exc


@router.get("/matches", response_model=list[MatchAnalysisRecord])
def list_matches(store: StoreDep, identity: UserDep) -> list[MatchAnalysisRecord]:
    try:
        _ensure_profile(store, identity)
        return store.list_matches(identity.user_id)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, HTTPException):
            raise
        raise _map_persistence_error(exc) from exc


@router.post("/matches", response_model=MatchAnalysisRecord, status_code=201)
def create_match(
    payload: MatchAnalysisCreate,
    store: StoreDep,
    identity: UserDep,
) -> MatchAnalysisRecord:
    try:
        _ensure_profile(store, identity)
        return store.create_match(identity.user_id, payload)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, HTTPException):
            raise
        raise _map_persistence_error(exc) from exc


@router.get("/matches/{match_id}", response_model=MatchAnalysisRecord)
def get_match(match_id: UUID, store: StoreDep, identity: UserDep) -> MatchAnalysisRecord:
    try:
        return store.get_match(identity.user_id, match_id)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, HTTPException):
            raise
        raise _map_persistence_error(exc) from exc


@router.delete("/matches/{match_id}", status_code=204, response_class=Response)
def delete_match(match_id: UUID, store: StoreDep, identity: UserDep) -> Response:
    try:
        store.delete_match(identity.user_id, match_id)
        return Response(status_code=204)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, HTTPException):
            raise
        raise _map_persistence_error(exc) from exc


@router.get("/jobs", response_model=list[SavedJobRecord])
def list_jobs(store: StoreDep, identity: UserDep) -> list[SavedJobRecord]:
    try:
        _ensure_profile(store, identity)
        return store.list_jobs(identity.user_id)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, HTTPException):
            raise
        raise _map_persistence_error(exc) from exc


@router.post("/jobs", response_model=SavedJobRecord, status_code=201)
def create_job(
    payload: SavedJobCreate,
    store: StoreDep,
    identity: UserDep,
) -> SavedJobRecord:
    try:
        _ensure_profile(store, identity)
        return store.create_job(identity.user_id, payload)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, HTTPException):
            raise
        raise _map_persistence_error(exc) from exc


@router.get("/jobs/{job_id}", response_model=SavedJobRecord)
def get_job(job_id: UUID, store: StoreDep, identity: UserDep) -> SavedJobRecord:
    try:
        return store.get_job(identity.user_id, job_id)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, HTTPException):
            raise
        raise _map_persistence_error(exc) from exc


@router.patch("/jobs/{job_id}", response_model=SavedJobRecord)
def update_job(
    job_id: UUID,
    payload: SavedJobUpdate,
    store: StoreDep,
    identity: UserDep,
) -> SavedJobRecord:
    try:
        return store.update_job(identity.user_id, job_id, payload)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, HTTPException):
            raise
        raise _map_persistence_error(exc) from exc


@router.delete("/jobs/{job_id}", status_code=204, response_class=Response)
def delete_job(job_id: UUID, store: StoreDep, identity: UserDep) -> Response:
    try:
        store.delete_job(identity.user_id, job_id)
        return Response(status_code=204)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, HTTPException):
            raise
        raise _map_persistence_error(exc) from exc
