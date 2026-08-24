"""Deterministic text normalization for resumes and job descriptions."""

from __future__ import annotations

import re
import unicodedata

_WHITESPACE = re.compile(r"\s+")


def repair_mojibake(text: str) -> str:
    """Repair common UTF-8 text that was decoded as Latin-1 (for example ``NaÃ¯ve``)."""
    if "Ã" not in text:
        return text
    try:
        return text.encode("latin-1").decode("utf-8")
    except UnicodeError:
        return text


def normalize_text(text: str) -> str:
    """NFC-normalize, repair common mojibake, and collapse whitespace."""
    if not text:
        return ""
    repaired = repair_mojibake(text)
    normalized = unicodedata.normalize("NFC", repaired)
    return _WHITESPACE.sub(" ", normalized).strip()
