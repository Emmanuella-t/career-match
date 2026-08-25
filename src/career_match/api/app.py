"""FastAPI application for Career Match matching.

Model lifecycle:
- Creating/importing ``app`` does not download MiniLM.
- ``MatcherService`` is stored on ``app.state`` and reused across requests.
- Semantic/hybrid encoders load lazily on first scoring call.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from career_match.api.schemas import (
    ErrorResponse,
    HealthResponse,
    MatchRequest,
    MatchResponse,
)
from career_match.api.services import MatcherService, UnsupportedMatcherError
from career_match.api.settings import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    CORS_ALLOW_ORIGINS,
)
from career_match.core.exceptions import CareerMatchError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Attach a process-wide MatcherService without loading MiniLM yet."""
    app.state.matcher_service = MatcherService()
    yield


def create_app() -> FastAPI:
    """Build the Career Match API application."""
    application = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        description=API_DESCRIPTION,
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(CORS_ALLOW_ORIGINS),
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

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
        return JSONResponse(status_code=500, content={"detail": str(exc)})

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
