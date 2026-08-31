"""Authenticated grounded resume tailoring routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from career_match.api.auth import ClerkIdentity, require_clerk_user
from career_match.api.persistence_routes import get_store
from career_match.api.schemas import ResumeTailorRequest, ResumeTailorResponse
from career_match.api.services import MatcherService
from career_match.api.tailor_service import TailorService
from career_match.persistence.errors import RecordNotFoundError
from career_match.persistence.store import PersistenceStore
from career_match.tailoring.providers import (
    DeterministicRewriteProvider,
    OptionalLLMRewriteProvider,
)

router = APIRouter(prefix="/api/v1", tags=["resumes"])

UserDep = Annotated[ClerkIdentity, Depends(require_clerk_user)]
StoreDep = Annotated[PersistenceStore, Depends(get_store)]


def get_tailor_service(request: Request, store: StoreDep) -> TailorService:
    override = getattr(request.app.state, "tailor_service_override", None)
    if override is not None:
        return override

    deterministic_override = getattr(
        request.app.state, "rewrite_provider_override", None
    )
    llm_override = getattr(request.app.state, "llm_rewrite_provider_override", None)

    matcher_service: MatcherService = request.app.state.matcher_service
    return TailorService(
        matcher_service=matcher_service,
        store=store,
        deterministic_provider=deterministic_override or DeterministicRewriteProvider(),
        llm_provider=llm_override or OptionalLLMRewriteProvider(),
    )


@router.post(
    "/resumes/tailor",
    response_model=ResumeTailorResponse,
    summary="Generate grounded resume tailoring suggestions",
    description=(
        "Compare resume evidence to a target job, return keyword alignment analysis, "
        "and grounded rewrite suggestions. Does not overwrite saved resumes."
    ),
)
def tailor_resume(
    payload: ResumeTailorRequest,
    identity: UserDep,
    service: Annotated[TailorService, Depends(get_tailor_service)],
) -> ResumeTailorResponse:
    try:
        return service.tailor(identity.user_id, payload)
    except RecordNotFoundError as exc:
        detail = "resume not found" if "resume" in str(exc).lower() else "job not found"
        raise HTTPException(status_code=404, detail=detail) from exc
