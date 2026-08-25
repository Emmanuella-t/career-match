"""Rule-based skill extraction.

This is a foundation helper for tests and dataset inspection. It is not a
production NER model and must not be reported as matching performance.
"""

from __future__ import annotations

import re

from career_match.core.types import ExtractedSkill
from career_match.parsing.text import normalize_text

# Canonical name -> alternative surface forms. Keep the list small and explicit.
SKILL_LEXICON: dict[str, tuple[str, ...]] = {
    "python": ("python",),
    "java": ("java",),
    "javascript": ("javascript", "js"),
    "sql": ("sql",),
    "pandas": ("pandas",),
    "numpy": ("numpy",),
    "scikit-learn": ("scikit-learn", "sklearn"),
    "tensorflow": ("tensorflow",),
    "react": ("react",),
    "docker": ("docker",),
    "aws": ("aws", "amazon web services"),
    "git": ("git",),
    "html": ("html",),
    "css": ("css",),
    "linux": ("linux",),
}


def _token_pattern(term: str) -> re.Pattern[str]:
    escaped = re.escape(term)
    if re.fullmatch(r"[a-z0-9]+", term):
        return re.compile(rf"\b{escaped}\b", re.IGNORECASE)
    return re.compile(escaped, re.IGNORECASE)


def extract_skills(text: str) -> tuple[ExtractedSkill, ...]:
    """Return unique lexicon hits in first-seen canonical order."""
    normalized = normalize_text(text)
    if not normalized:
        return ()

    found: list[ExtractedSkill] = []
    seen: set[str] = set()
    for canonical, surfaces in SKILL_LEXICON.items():
        if canonical in seen:
            continue
        for surface in surfaces:
            match = _token_pattern(surface).search(normalized)
            if match:
                found.append(
                    ExtractedSkill(name=canonical, start=match.start(), end=match.end())
                )
                seen.add(canonical)
                break
    found.sort(key=lambda skill: skill.start)
    return tuple(found)
