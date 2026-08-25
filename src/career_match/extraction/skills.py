"""Rule-based skill extraction.

This is a small, explicit catalog for the lexical baseline and for tests.
It is not a production NER model and must not be reported as matching
performance. Keep the list modest so misses stay inspectable.
"""

from __future__ import annotations

import re

from career_match.core.types import ExtractedSkill
from career_match.parsing.text import normalize_text

# Canonical name -> alternative surface forms. Order of this dict is the
# catalog order used when first-seen position is equal.
SKILL_LEXICON: dict[str, tuple[str, ...]] = {
    "python": ("python",),
    "java": ("java",),
    "javascript": ("javascript", "js"),
    "typescript": ("typescript",),
    "sql": ("sql",),
    "c++": ("c++", "c plus plus"),
    "c#": ("c#", "csharp", "c sharp"),
    ".net": (".net", "dotnet", "dot net"),
    "react": ("react",),
    "next.js": ("next.js", "nextjs", "next js"),
    "fastapi": ("fastapi", "fast api"),
    "flask": ("flask",),
    "django": ("django",),
    "pytorch": ("pytorch",),
    "tensorflow": ("tensorflow",),
    "scikit-learn": ("scikit-learn", "sklearn", "scikit learn"),
    "pandas": ("pandas",),
    "numpy": ("numpy",),
    "aws": ("aws", "amazon web services"),
    "azure": ("azure",),
    "gcp": ("gcp", "google cloud platform", "google cloud"),
    "docker": ("docker",),
    "kubernetes": ("kubernetes", "k8s"),
    "git": ("git",),
    "linux": ("linux",),
    "machine learning": ("machine learning",),
    "deep learning": ("deep learning",),
    "nlp": ("nlp", "natural language processing"),
    "computer vision": ("computer vision",),
    "rest apis": ("rest apis", "rest api", "restful api", "restful apis"),
    "html": ("html",),
    "css": ("css",),
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


def extract_skill_names(text: str) -> tuple[str, ...]:
    """Return canonical skill names in first-seen order."""
    return tuple(skill.name for skill in extract_skills(text))
