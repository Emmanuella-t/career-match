"""Deterministic suggestion identifiers for tailoring apply/export."""

from __future__ import annotations

import hashlib

from career_match.tailoring.protocol import RewriteSuggestion


def compute_suggestion_id(suggestion: RewriteSuggestion) -> str:
    """Stable ID from section + original + suggested text (server-side validation)."""
    payload = (
        f"{suggestion.section}|{suggestion.original_text}|{suggestion.suggested_text}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
