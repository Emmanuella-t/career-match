"""In-memory resume file parsing for PDF and DOCX uploads."""

from __future__ import annotations

import io
import os
import re
from dataclasses import dataclass
from typing import Final

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_LINE_SPACES = re.compile(r"[ \t]+")
_BLANK_RUN = re.compile(r"\n{3,}")
_UNSAFE_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

# Keep in sync with career_match.api.settings (import avoided to prevent cycles).
_MAX_RESUME_FILE_BYTES = 2 * 1024 * 1024
_MAX_TEXT_CHARS = 50_000
_LINE_SPACES = re.compile(r"[ \t]+")
_BLANK_RUN = re.compile(r"\n{3,}")
_UNSAFE_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

PDF_EXTENSION: Final = "pdf"
DOCX_EXTENSION: Final = "docx"

SUPPORTED_RESUME_EXTENSIONS: Final[tuple[str, ...]] = (PDF_EXTENSION, DOCX_EXTENSION)

SUPPORTED_RESUME_MIME_TYPES: Final[frozenset[str]] = frozenset(
    {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
)

_EXTENSION_TO_MIME: Final[dict[str, str]] = {
    PDF_EXTENSION: "application/pdf",
    DOCX_EXTENSION: (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ),
}


class ResumeParseError(ValueError):
    """User-facing resume parse/validation failure."""


@dataclass(frozen=True, slots=True)
class ParsedResumeFile:
    """Structured result from parsing an uploaded resume file."""

    filename: str
    file_type: str
    character_count: int
    extracted_text: str


def sanitize_filename(filename: str) -> str:
    """Return a safe display/storage filename without path components."""
    if not filename or not str(filename).strip():
        return "resume"

    base = os.path.basename(str(filename).replace("\\", "/").strip())
    base = _UNSAFE_FILENAME.sub("_", base)
    base = "".join(char for char in base if char.isprintable())
    base = base.strip(" .")
    if not base:
        return "resume"
    return base[:200]


def _extension(filename: str) -> str:
    _, ext = os.path.splitext(filename.lower())
    return ext.lstrip(".")


def _validate_file_size(content: bytes) -> None:
    if len(content) > _MAX_RESUME_FILE_BYTES:
        max_mb = _MAX_RESUME_FILE_BYTES / (1024 * 1024)
        raise ResumeParseError(
            f"file exceeds the {max_mb:.0f} MB size limit; "
            "upload a smaller PDF or DOCX file"
        )
    if not content:
        raise ResumeParseError("uploaded file is empty")


def _validate_type(filename: str, content_type: str | None) -> str:
    ext = _extension(filename)
    if ext not in SUPPORTED_RESUME_EXTENSIONS:
        supported = ", ".join(f".{item}" for item in SUPPORTED_RESUME_EXTENSIONS)
        raise ResumeParseError(
            f"unsupported file type; supported formats are {supported}"
        )

    if content_type:
        normalized = content_type.split(";", 1)[0].strip().lower()
        expected = _EXTENSION_TO_MIME[ext]
        if normalized not in SUPPORTED_RESUME_MIME_TYPES:
            raise ResumeParseError(
                "unsupported file type; supported formats are PDF and DOCX"
            )
        if normalized != expected:
            raise ResumeParseError(
                f"file extension .{ext} does not match the uploaded content type"
            )

    return ext


def normalize_extracted_text(text: str) -> str:
    """Normalize extracted resume text while preserving paragraph breaks."""
    if not text:
        return ""

    cleaned = _CONTROL_CHARS.sub("", text)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")

    lines: list[str] = []
    for line in cleaned.split("\n"):
        lines.append(_LINE_SPACES.sub(" ", line).strip())

    normalized = "\n".join(lines)
    normalized = _BLANK_RUN.sub("\n\n", normalized)
    return normalized.strip()


def _enforce_text_limits(text: str) -> str:
    if not text:
        raise ResumeParseError(
            "no extractable text was found in this PDF. "
            "Scanned or image-only PDFs are not supported yet; "
            "paste your resume text manually or upload a text-based PDF"
        )
    if len(text) > _MAX_TEXT_CHARS:
        raise ResumeParseError(
            f"extracted resume text exceeds the maximum length of "
            f"{_MAX_TEXT_CHARS:,} characters"
        )
    return text


def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from a PDF byte stream using pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise ResumeParseError("PDF parsing is not available on this server") from exc

    try:
        reader = PdfReader(io.BytesIO(content), strict=False)
    except Exception as exc:  # noqa: BLE001 - map to safe client error
        raise ResumeParseError("could not read PDF file; upload a valid PDF") from exc

    parts: list[str] = []
    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""
        except Exception:  # noqa: BLE001 - skip unreadable pages
            page_text = ""
        if page_text.strip():
            parts.append(page_text)

    return normalize_extracted_text("\n\n".join(parts))


def extract_text_from_docx(content: bytes) -> str:
    """Extract text from a DOCX byte stream using python-docx."""
    try:
        from docx import Document
    except ImportError as exc:  # pragma: no cover
        raise ResumeParseError("DOCX parsing is not available on this server") from exc

    try:
        document = Document(io.BytesIO(content))
    except Exception as exc:  # noqa: BLE001 - map to safe client error
        raise ResumeParseError("could not read DOCX file; upload a valid DOCX") from exc

    parts: list[str] = []
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            parts.append(text)

    return normalize_extracted_text("\n\n".join(parts))


def parse_resume_file(
    filename: str,
    content: bytes,
    content_type: str | None = None,
) -> ParsedResumeFile:
    """Validate and parse an uploaded resume file from memory."""
    _validate_file_size(content)
    safe_name = sanitize_filename(filename)
    file_type = _validate_type(safe_name, content_type)

    if file_type == PDF_EXTENSION:
        extracted = extract_text_from_pdf(content)
    else:
        extracted = extract_text_from_docx(content)

    extracted = _enforce_text_limits(extracted)

    return ParsedResumeFile(
        filename=safe_name,
        file_type=file_type,
        character_count=len(extracted),
        extracted_text=extracted,
    )
