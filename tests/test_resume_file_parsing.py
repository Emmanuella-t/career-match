"""Unit tests for resume file parsing helpers."""

from __future__ import annotations

import pytest
from tests.fixtures.resume_files import make_blank_pdf, make_docx, make_text_pdf

from career_match.api.settings import MAX_RESUME_FILE_BYTES
from career_match.parsing.resume_files import (
    ResumeParseError,
    normalize_extracted_text,
    parse_resume_file,
    sanitize_filename,
)

SAMPLE_RESUME_TEXT = (
    "Jordan Lee\nMachine Learning Engineer\n\n"
    "Experience\nBuilt Python services with FastAPI and Docker."
)


def test_sanitize_filename_strips_paths_and_unsafe_chars() -> None:
    assert sanitize_filename("../../evil/resume.pdf") == "resume.pdf"
    assert sanitize_filename("  ") == "resume"


def test_normalize_extracted_text_preserves_paragraphs() -> None:
    raw = "Line one\n\nLine two\t\twith spaces\n\n\n\nLine three"
    normalized = normalize_extracted_text(raw)
    assert "Line one\n\nLine two with spaces" in normalized
    assert "\n\n\n" not in normalized


def test_parse_valid_text_pdf() -> None:
    content = make_text_pdf("Python engineer with FastAPI experience.")
    parsed = parse_resume_file(
        "my resume.pdf",
        content,
        content_type="application/pdf",
    )
    assert parsed.file_type == "pdf"
    assert parsed.filename == "my resume.pdf"
    assert "Python engineer" in parsed.extracted_text
    assert parsed.character_count == len(parsed.extracted_text)


def test_parse_valid_docx() -> None:
    content = make_docx(SAMPLE_RESUME_TEXT)
    parsed = parse_resume_file(
        "resume.docx",
        content,
        content_type=(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
    )
    assert parsed.file_type == "docx"
    assert "Jordan Lee" in parsed.extracted_text
    assert "FastAPI" in parsed.extracted_text


def test_parse_rejects_unsupported_extension() -> None:
    with pytest.raises(ResumeParseError, match="unsupported file type"):
        parse_resume_file("notes.txt", b"plain text", content_type="text/plain")


def test_parse_rejects_mismatched_mime_type() -> None:
    content = make_text_pdf("Python engineer.")
    with pytest.raises(ResumeParseError, match="does not match"):
        parse_resume_file(
            "resume.pdf",
            content,
            content_type=(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
        )


def test_parse_rejects_oversized_file() -> None:
    oversized = b"%PDF-" + b"0" * (MAX_RESUME_FILE_BYTES + 1)
    with pytest.raises(ResumeParseError, match="size limit"):
        parse_resume_file("big.pdf", oversized, content_type="application/pdf")


def test_parse_rejects_blank_pdf_without_text() -> None:
    content = make_blank_pdf()
    with pytest.raises(ResumeParseError, match="Scanned or image-only PDFs"):
        parse_resume_file("scan.pdf", content, content_type="application/pdf")


def test_parse_rejects_extracted_text_over_character_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "career_match.parsing.resume_files._MAX_TEXT_CHARS",
        20,
    )
    content = make_docx("A" * 40)
    with pytest.raises(ResumeParseError, match="maximum length"):
        parse_resume_file(
            "long.docx",
            content,
            content_type=(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
        )
