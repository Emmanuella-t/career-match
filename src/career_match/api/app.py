"""FastAPI application for Career Match matching.

Model lifecycle:
- Creating/importing ``app`` does not download MiniLM.
- ``MatcherService`` is stored on ``app.state`` and reused across requests.
- Semantic/hybrid encoders load lazily on first scoring call.
- Concurrent first loads are guarded so a single process reuses one instance.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from career_match.api.job_discovery_routes import router as job_discovery_router
from career_match.api.persistence_routes import router as persistence_router
from career_match.api.resume_parse_routes import router as resume_parse_router
from career_match.api.schemas import (
    ErrorResponse,
    HealthResponse,
    MatchRequest,
    MatchResponse,
    ReadyResponse,
)
from career_match.api.services import MatcherService, UnsupportedMatcherError
from career_match.api.settings import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    apply_model_cache_env,
    get_cors_allow_origins,
    log_startup_config,
)
from career_match.api.tailor_routes import router as tailor_router
from career_match.core.exceptions import CareerMatchError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Attach a process-wide MatcherService without loading MiniLM yet."""
    apply_model_cache_env()
    log_startup_config()
    app.state.matcher_service = MatcherService()
    yield


def create_app() -> FastAPI:
    """Build the Career Match API application."""
    apply_model_cache_env()
    cors_origins = list(get_cors_allow_origins())

    application = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        description=API_DESCRIPTION,
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    application.include_router(job_discovery_router)
    application.include_router(persistence_router)
    application.include_router(tailor_router)
    application.include_router(resume_parse_router)

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        messages = []
        for error in exc.errors():
            loc = ".".join(str(part) for part in error.get("loc", ()) if part != "body")
            msg = error.get("msg", "invalid request")
            messages.append(f"{loc}: {msg}" if loc else str(msg))
        detail = "; ".join(messages) if messages else "invalid request"
        return JSONResponse(status_code=422, content={"detail": detail})

    @application.exception_handler(UnsupportedMatcherError)
    async def unsupported_matcher_handler(
        _request: Request,
        exc: UnsupportedMatcherError,
    ) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @application.exception_handler(CareerMatchError)
    async def career_match_error_handler(
        _request: Request,
        exc: CareerMatchError,
    ) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": "internal error"})

    @application.get(
        "/health",
        response_model=HealthResponse,
        responses={200: {"model": HealthResponse}},
        summary="Health check",
        description="Lightweight liveness probe. Does not load MiniLM.",
        tags=["system"],
    )
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @application.get(
        "/ready",
        response_model=ReadyResponse,
        responses={200: {"model": ReadyResponse}},
        summary="Readiness check",
        description=(
            "Reports whether the matching service can accept requests. "
            "Does not download or load MiniLM; ``semantic_model_loaded`` is true "
            "only after a prior semantic/hybrid score in this process."
        ),
        tags=["system"],
    )
    def ready(request: Request) -> ReadyResponse:
        service: MatcherService = request.app.state.matcher_service
        return ReadyResponse(
            status="ready",
            semantic_model_loaded=service.semantic_model_loaded,
        )

    @application.post(
        "/api/v1/match",
        response_model=MatchResponse,
        responses={
            400: {"model": ErrorResponse},
            422: {"model": ErrorResponse},
            500: {"model": ErrorResponse},
        },
        summary="Score resume against job",
        description=(
            "Return an explainable resume-to-job relevance score. "
            "Default matcher is semantic. Scores are not hiring probabilities."
        ),
        tags=["matching"],
    )
    def match(payload: MatchRequest, request: Request) -> MatchResponse:
        service: MatcherService = request.app.state.matcher_service
        try:
            return service.match(
                payload.resume_text,
                payload.job_description,
                payload.matcher,
            )
        except UnsupportedMatcherError:
            raise
        except CareerMatchError:
            raise
        except Exception as exc:  # noqa: BLE001 - map to HTTP without traceback
            raise HTTPException(status_code=500, detail="internal matching error") from exc

    return application


app = create_app()


def get_matcher_service(app_obj: Any | None = None) -> MatcherService:
    """Test helper to inspect the process-wide service."""
    target = app_obj or app
    return target.state.matcher_service
