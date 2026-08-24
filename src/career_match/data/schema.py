"""Validation for legacy resume records."""

from __future__ import annotations

from career_match.core.exceptions import SchemaError
from career_match.core.types import ResumeRecord

REQUIRED_FIELDS = ("Category", "Resume")


def validate_resume_record(category: str, text: str, source_row: int) -> ResumeRecord:
    """Return a ``ResumeRecord`` or raise ``SchemaError``."""
    if not isinstance(category, str) or not category.strip():
        raise SchemaError(f"Row {source_row}: category is required.")
    if not isinstance(text, str) or not text.strip():
        raise SchemaError(f"Row {source_row}: resume text is required.")
    return ResumeRecord(category=category.strip(), text=text, source_row=source_row)
