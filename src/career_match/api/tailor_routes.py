"""Authenticated grounded resume tailoring routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response

from career_match.api.auth import ClerkIdentity, require_clerk_user
from career_match.api.persistence_routes import get_store
from career_match.api.schemas import (
    ResumeExportRequest,
    ResumeTailorApplyRequest,
    ResumeTailorApplyResponse,
    ResumeTailorRequest,
    ResumeTailorResponse,
)
from career_match.api.services import MatcherService
from career_match.api.tailor_apply_service import TailorApplyError, TailorApplyService
from career_match.api.tailor_service import TailorService
from career_match.persistence.errors import RecordNotFoundError
from career_match.persistence.store import PersistenceStore
from career_match.tailoring.export import (
    export_docx_bytes,
    export_plain_text,
    sanitize_export_filename,
)
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


def get_apply_service(request: Request, store: StoreDep) -> TailorApplyService:
    return TailorApplyService(
        tailor_service=get_tailor_service(request, store),
        matcher_service=request.app.state.matcher_service,
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


@router.post(
    "/resumes/tailor/apply",
    response_model=ResumeTailorApplyResponse,
    summary="Apply accepted tailoring suggestions and preview revision",
)
def apply_tailor_suggestions(
    payload: ResumeTailorApplyRequest,
    identity: UserDep,
    service: Annotated[TailorApplyService, Depends(get_apply_service)],
) -> ResumeTailorApplyResponse:
    try:
        return service.apply(identity.user_id, payload)
    except TailorApplyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RecordNotFoundError as exc:
        detail = "resume not found" if "resume" in str(exc).lower() else "job not found"
        raise HTTPException(status_code=404, detail=detail) from exc


@router.post(
    "/resumes/export",
    summary="Export tailored resume as DOCX or plain text",
    responses={200: {"content": {"application/octet-stream": {}}}},
)
def export_tailored_resume(
    payload: ResumeExportRequest,
    identity: UserDep,
    service: Annotated[TailorApplyService, Depends(get_apply_service)],
) -> Response:
    try:
        structured, _result, resume_name = service.build_structured_for_export(
            identity.user_id,
            payload,
        )
        filename = sanitize_export_filename(resume_name, payload.format)
        if payload.format == "txt":
            content = export_plain_text(structured).encode("utf-8")
            media_type = "text/plain; charset=utf-8"
        elif payload.format == "docx":
            content = export_docx_bytes(structured)
            media_type = (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        else:
            raise HTTPException(status_code=400, detail="unsupported export format")
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except TailorApplyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RecordNotFoundError as exc:
        detail = "resume not found" if "resume" in str(exc).lower() else "job not found"
        raise HTTPException(status_code=404, detail=detail) from exc
