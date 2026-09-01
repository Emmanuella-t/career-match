"""Deterministic resume-to-search-query builder for external job providers."""

from __future__ import annotations

import re
from dataclasses import dataclass

from career_match.extraction.skills import extract_skill_names

MAX_SEARCH_QUERY_CHARS = 80
MAX_SKILL_TERMS = 3

_ROLE_PHRASES: tuple[tuple[str, str], ...] = (
    ("machine learning engineer", "machine learning engineer"),
    ("data scientist", "data scientist"),
    ("backend engineer", "backend engineer"),
    ("frontend developer", "frontend developer"),
    ("full stack", "full stack developer"),
    ("devops engineer", "devops engineer"),
    ("software engineer", "software engineer"),
    ("platform engineer", "platform engineer"),
    ("ml engineer", "machine learning engineer"),
)

_SKILL_ROLE_HINTS: tuple[tuple[frozenset[str], str], ...] = (
    (frozenset({"machine learning", "pytorch", "tensorflow"}), "machine learning engineer"),
    (frozenset({"python", "fastapi", "docker"}), "python engineer"),
    (frozenset({"react", "javascript", "typescript"}), "frontend developer"),
    (frozenset({"sql", "pandas"}), "data analyst"),
)


@dataclass(frozen=True, slots=True)
class JobSearchQuery:
    """Explainable search query derived from resume evidence."""

    text: str
    role_term: str | None
    skill_terms: tuple[str, ...]


def build_job_search_query(resume_text: str) -> JobSearchQuery:
    """Build a concise Adzuna-style search query from resume evidence only."""
    skills = extract_skill_names(resume_text)
    role = _infer_role(resume_text, skills)

    parts: list[str] = []
    if role:
        parts.append(role)

    for skill in skills:
        if skill in parts:
            continue
        if len([item for item in parts if item != role]) >= MAX_SKILL_TERMS:
            break
        parts.append(skill)

    if not parts and skills:
        parts.append(skills[0])

    query = _join_query_parts(parts)
    return JobSearchQuery(
        text=query,
        role_term=role,
        skill_terms=tuple(skills[:MAX_SKILL_TERMS]),
    )


def _infer_role(resume_text: str, skills: tuple[str, ...]) -> str | None:
    header = "\n".join(resume_text.replace("\r\n", "\n").split("\n")[:6]).lower()
    for needle, role in _ROLE_PHRASES:
        if needle in header:
            return role

    skill_set = set(skills)
    for required, role in _SKILL_ROLE_HINTS:
        if required.issubset(skill_set):
            return role

    if re.search(r"\bengineer\b", header):
        return "software engineer"
    if re.search(r"\bdeveloper\b", header):
        return "software developer"
    if re.search(r"\bscientist\b", header):
        return "data scientist"
    return None


def _join_query_parts(parts: list[str]) -> str:
    cleaned = " ".join(part.strip() for part in parts if part.strip())
    if len(cleaned) <= MAX_SEARCH_QUERY_CHARS:
        return cleaned

    # Prefer role + top skills when trimming.
    role = parts[0] if parts else ""
    remainder = parts[1:] if len(parts) > 1 else []
    while remainder and len(f"{role} {' '.join(remainder)}".strip()) > MAX_SEARCH_QUERY_CHARS:
        remainder = remainder[:-1]
    trimmed = f"{role} {' '.join(remainder)}".strip()
    return trimmed[:MAX_SEARCH_QUERY_CHARS].rstrip()
