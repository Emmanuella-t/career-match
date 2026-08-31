"""Authenticated job discovery and ranking routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from career_match.api.auth import ClerkIdentity, require_clerk_user
from career_match.api.job_discovery_service import JobDiscoveryService
from career_match.api.persistence_routes import get_store
from career_match.api.schemas import JobDiscoverRequest, JobDiscoverResponse
from career_match.api.services import MatcherService
from career_match.jobs.sources import PostgresJobOpportunitySource
from career_match.persistence.errors import RecordNotFoundError
from career_match.persistence.store import PersistenceStore

router = APIRouter(prefix="/api/v1", tags=["job-discovery"])

UserDep = Annotated[ClerkIdentity, Depends(require_clerk_user)]
StoreDep = Annotated[PersistenceStore, Depends(get_store)]


def get_job_source(request: Request, store: StoreDep):
    override = getattr(request.app.state, "job_source_override", None)
    if override is not None:
        return override
    return PostgresJobOpportunitySource(store)


def get_discovery_service(
    request: Request,
    store: StoreDep,
    job_source: Annotated[object, Depends(get_job_source)],
) -> JobDiscoveryService:
    matcher_service: MatcherService = request.app.state.matcher_service
    return JobDiscoveryService(
        matcher_service=matcher_service,
        job_source=job_source,
        store=store,
    )


@router.post(
    "/jobs/discover",
    response_model=JobDiscoverResponse,
    summary="Rank discoverable jobs for a resume",
    description=(
        "Load the authenticated user's resume, score available job opportunities "
        "with the existing matcher pipeline, and return ranked explainable results. "
        "Scores reflect resume-to-job relevance, not hiring probability."
    ),
)
def discover_jobs(
    payload: JobDiscoverRequest,
    identity: UserDep,
    service: Annotated[JobDiscoveryService, Depends(get_discovery_service)],
) -> JobDiscoverResponse:
    try:
        return service.discover(identity.user_id, payload)
    except RecordNotFoundError as exc:
        raise HTTPException(status_code=404, detail="resume not found") from exc
