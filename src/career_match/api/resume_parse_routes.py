"""Authenticated resume file upload and parsing routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from career_match.api.auth import ClerkIdentity, require_clerk_user
from career_match.api.schemas import ResumeParseResponse
from career_match.parsing.resume_files import ResumeParseError, parse_resume_file

router = APIRouter(prefix="/api/v1", tags=["resumes"])

UserDep = Annotated[ClerkIdentity, Depends(require_clerk_user)]


@router.post(
    "/resumes/parse",
    response_model=ResumeParseResponse,
    summary="Parse an uploaded resume file",
    description=(
        "Accept a PDF or DOCX resume via multipart/form-data, extract text in memory, "
        "and return structured metadata. Does not run matching or persist to the database."
    ),
)
async def parse_resume_upload(
    _identity: UserDep,
    file: Annotated[UploadFile, File(description="Resume file (PDF or DOCX)")],
) -> ResumeParseResponse:
    if file.filename is None or not file.filename.strip():
        raise HTTPException(status_code=400, detail="a resume file is required")

    try:
        content = await file.read()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="could not read uploaded file") from exc

    try:
        parsed = parse_resume_file(
            filename=file.filename,
            content=content,
            content_type=file.content_type,
        )
    except ResumeParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ResumeParseResponse(
        filename=parsed.filename,
        file_type=parsed.file_type,
        character_count=parsed.character_count,
        extracted_text=parsed.extracted_text,
    )
