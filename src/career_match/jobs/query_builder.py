"""Deterministic resume-to-search-query builder for external job providers.

External job search queries are for **retrieval** only. Adzuna (or similar)
should return a broad, role-oriented candidate pool; Career Match's matcher
ranks the final results.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from career_match.extraction.skills import extract_skill_names
from career_match.parsing.text import normalize_text

MAX_SEARCH_QUERIES = 3
MAX_QUERY_WORDS = 5
MAX_SEARCH_QUERY_CHARS = 80

# Role families used to avoid conflicting retrieval queries (e.g. frontend + ML).
_FAMILY_ML = "ml"
_FAMILY_FRONTEND = "frontend"
_FAMILY_BACKEND = "backend"
_FAMILY_DATA = "data"
_FAMILY_GENERAL = "general"


@dataclass(frozen=True, slots=True)
class RoleDefinition:
    """Maintainable role taxonomy entry for retrieval query generation."""

    key: str
    query: str
    family: str
    title_patterns: tuple[str, ...] = ()
    evidence_phrases: tuple[str, ...] = ()
    evidence_skills: frozenset[str] = frozenset()
    min_score: int = 4


ROLE_TAXONOMY: tuple[RoleDefinition, ...] = (
    RoleDefinition(
        key="machine_learning_engineer",
        query="machine learning engineer",
        family=_FAMILY_ML,
        title_patterns=("machine learning engineer", "ml engineer", "mle"),
        evidence_phrases=("model training", "model evaluation", "feature engineering"),
        evidence_skills=frozenset(
            {"machine learning", "pytorch", "tensorflow", "scikit-learn", "deep learning"}
        ),
    ),
    RoleDefinition(
        key="applied_ai_engineer",
        query="applied AI engineer",
        family=_FAMILY_ML,
        title_patterns=("applied ai engineer", "ai engineer", "generative ai engineer"),
        evidence_phrases=("large language model", "generative ai", "prompt engineering"),
        evidence_skills=frozenset({"machine learning", "nlp", "deep learning", "pytorch"}),
        min_score=5,
    ),
    RoleDefinition(
        key="nlp_engineer",
        query="NLP engineer",
        family=_FAMILY_ML,
        title_patterns=("nlp engineer", "natural language processing engineer"),
        evidence_phrases=("natural language processing", "text classification", "named entity"),
        evidence_skills=frozenset({"nlp", "pytorch", "tensorflow", "machine learning"}),
        min_score=5,
    ),
    RoleDefinition(
        key="data_scientist",
        query="data scientist",
        family=_FAMILY_DATA,
        title_patterns=("data scientist",),
        evidence_phrases=("statistical modeling", "experiment analysis", "a/b test"),
        evidence_skills=frozenset({"machine learning", "pandas", "scikit-learn", "sql"}),
    ),
    RoleDefinition(
        key="data_analyst",
        query="data analyst",
        family=_FAMILY_DATA,
        title_patterns=("data analyst", "business analyst"),
        evidence_phrases=("dashboard", "reporting", "business intelligence"),
        evidence_skills=frozenset({"sql", "pandas", "excel"}),
        min_score=5,
    ),
    RoleDefinition(
        key="mlops_engineer",
        query="MLOps engineer",
        family=_FAMILY_ML,
        title_patterns=("mlops engineer", "ml ops engineer", "machine learning platform"),
        evidence_phrases=("model deployment", "model serving", "ml pipeline"),
        evidence_skills=frozenset({"kubernetes", "docker", "pytorch", "machine learning"}),
        min_score=6,
    ),
    RoleDefinition(
        key="data_engineer",
        query="data engineer",
        family=_FAMILY_DATA,
        title_patterns=("data engineer",),
        evidence_phrases=("data pipeline", "etl", "data warehouse"),
        evidence_skills=frozenset({"sql", "python", "pandas", "aws"}),
        min_score=5,
    ),
    RoleDefinition(
        key="backend_engineer",
        query="backend engineer",
        family=_FAMILY_BACKEND,
        title_patterns=("backend engineer", "backend developer", "server engineer"),
        evidence_phrases=("rest api", "microservice", "api design"),
        evidence_skills=frozenset({"fastapi", "flask", "django", "rest apis", "sql"}),
        min_score=5,
    ),
    RoleDefinition(
        key="frontend_engineer",
        query="frontend engineer",
        family=_FAMILY_FRONTEND,
        title_patterns=(
            "frontend engineer",
            "frontend developer",
            "front-end engineer",
            "front end developer",
        ),
        evidence_phrases=("user interface", "responsive design", "ui implementation"),
        evidence_skills=frozenset({"react", "next.js", "typescript", "javascript", "html", "css"}),
        min_score=6,
    ),
    RoleDefinition(
        key="full_stack_engineer",
        query="full stack engineer",
        family=_FAMILY_GENERAL,
        title_patterns=("full stack engineer", "full stack developer", "full-stack engineer"),
        evidence_phrases=("full stack", "end-to-end feature"),
        evidence_skills=frozenset({"react", "fastapi", "typescript", "sql"}),
        min_score=7,
    ),
    RoleDefinition(
        key="software_engineer",
        query="software engineer",
        family=_FAMILY_GENERAL,
        title_patterns=("software engineer", "software developer", "swe"),
        evidence_phrases=("software development", "production system"),
        evidence_skills=frozenset({"python", "java", "c++", "git", "linux"}),
        min_score=5,
    ),
)

_COMPOSITE_SW_ML_QUERY = "software engineer machine learning"

_ROLE_BY_KEY = {role.key: role for role in ROLE_TAXONOMY}


@dataclass(frozen=True, slots=True)
class JobSearchQuery:
    """A single role-oriented retrieval query."""

    text: str
    role_key: str | None
    broaden_text: str | None = None


@dataclass(frozen=True, slots=True)
class JobSearchQueryPlan:
    """Ranked retrieval queries derived from resume evidence."""

    queries: tuple[JobSearchQuery, ...]

    @property
    def primary(self) -> JobSearchQuery:
        if self.queries:
            return self.queries[0]
        return JobSearchQuery(text="software engineer", role_key="software_engineer")


def build_job_search_queries(resume_text: str) -> JobSearchQueryPlan:
    """Build up to three concise, role-oriented retrieval queries."""
    skills = set(extract_skill_names(resume_text))
    normalized = normalize_text(resume_text)
    header = _header_block(normalized)
    title_block = _title_block(normalized)

    scores = {
        role.key: _score_role(role, header=header, title_block=title_block, skills=skills)
        for role in ROLE_TAXONOMY
    }
    selected_keys = _select_role_keys(scores, skills)
    queries = _queries_for_roles(selected_keys, skills)
    return JobSearchQueryPlan(queries=tuple(queries))


def build_job_search_query(resume_text: str) -> JobSearchQuery:
    """Return the primary retrieval query (backward-compatible helper)."""
    return build_job_search_queries(resume_text).primary


def _header_block(normalized: str) -> str:
    lines = normalized.split("\n")
    return "\n".join(lines[:8]).lower()


def _title_block(normalized: str) -> str:
    """Collect likely job-title lines from experience sections."""
    lines = [line.strip().lower() for line in normalized.split("\n") if line.strip()]
    title_lines: list[str] = []
    for line in lines:
        if any(
            marker in line
            for marker in (
                "engineer",
                "developer",
                "scientist",
                "analyst",
                "architect",
                "manager",
            )
        ):
            title_lines.append(line)
    return "\n".join(title_lines[:12])


def _score_role(
    role: RoleDefinition,
    *,
    header: str,
    title_block: str,
    skills: set[str],
) -> int:
    score = 0
    for pattern in role.title_patterns:
        if pattern in header:
            score += 12
        elif pattern in title_block:
            score += 9

    for phrase in role.evidence_phrases:
        if phrase in header or phrase in title_block:
            score += 3

    skill_hits = len(role.evidence_skills & skills)
    score += skill_hits * 3

    if role.key == "frontend_engineer" and not _has_frontend_evidence(skills, header, title_block):
        return 0
    if role.key in {
        "machine_learning_engineer",
        "applied_ai_engineer",
        "nlp_engineer",
        "mlops_engineer",
    } and not _has_ml_evidence(skills, header, title_block):
        return 0
    if role.key == "data_scientist" and "data scientist" not in header:
        if "data scientist" not in title_block and skill_hits < 3:
            score = min(score, role.min_score - 1)
    if role.key == "applied_ai_engineer" and "nlp" in skills:
        score += 3
    if role.key == "nlp_engineer" and "nlp" in skills:
        score += 4

    return score


def _has_frontend_evidence(skills: set[str], header: str, title_block: str) -> bool:
    frontend_skills = {"react", "next.js", "typescript", "html", "css"}
    if skills & frontend_skills:
        return True
    return any(
        term in header or term in title_block
        for term in ("frontend", "front-end", "front end", "ui engineer")
    )


def _has_ml_evidence(skills: set[str], header: str, title_block: str) -> bool:
    ml_skills = {
        "machine learning",
        "deep learning",
        "pytorch",
        "tensorflow",
        "scikit-learn",
        "nlp",
        "computer vision",
    }
    if skills & ml_skills:
        return True
    return any(
        term in header or term in title_block
        for term in ("machine learning", "ml engineer", "deep learning", "nlp")
    )


def _select_role_keys(scores: dict[str, int], skills: set[str]) -> list[str]:
    qualified = [
        (role.key, scores[role.key])
        for role in ROLE_TAXONOMY
        if scores[role.key] >= role.min_score
    ]
    qualified.sort(key=lambda item: item[1], reverse=True)

    if not qualified:
        if _has_ml_evidence(skills, "", ""):
            return ["machine_learning_engineer"]
        if _has_frontend_evidence(skills, "", ""):
            return ["frontend_engineer"]
        if skills & {"fastapi", "flask", "django", "rest apis"}:
            return ["backend_engineer"]
        return ["software_engineer"]

    selected: list[str] = []

    for key, _score in qualified:
        role = _ROLE_BY_KEY[key]
        if _conflicts_with_selected(role, selected, scores, skills):
            continue
        selected.append(key)
        if len(selected) >= MAX_SEARCH_QUERIES:
            break

    if _should_add_software_ml_query(selected, scores, skills) and len(
        selected
    ) < MAX_SEARCH_QUERIES:
        selected.append("software_engineer_machine_learning")

    return selected[:MAX_SEARCH_QUERIES]


def _conflicts_with_selected(
    role: RoleDefinition,
    selected: list[str],
    _scores: dict[str, int],
    skills: set[str],
) -> bool:
    if not selected:
        return False

    if role.family == _FAMILY_FRONTEND and any(
        _ROLE_BY_KEY[key].family == _FAMILY_ML for key in selected
    ):
        return not _ml_frontend_specialist(skills)
    if role.family == _FAMILY_ML and any(
        _ROLE_BY_KEY[key].family == _FAMILY_FRONTEND for key in selected
    ):
        return not _ml_frontend_specialist(skills)

    if role.key in selected:
        return True
    return False


def _ml_frontend_specialist(skills: set[str]) -> bool:
    return bool(
        skills & {"react", "next.js", "typescript"}
        and skills & {"machine learning", "pytorch", "tensorflow", "deep learning"}
    )


def _should_add_software_ml_query(
    selected: list[str],
    scores: dict[str, int],
    skills: set[str],
) -> bool:
    if "software_engineer_machine_learning" in selected:
        return False
    ml_score = max(
        scores.get("machine_learning_engineer", 0),
        scores.get("applied_ai_engineer", 0),
        scores.get("nlp_engineer", 0),
    )
    swe_score = scores.get("software_engineer", 0)
    return (
        _has_ml_evidence(skills, "", "")
        and swe_score >= 5
        and ml_score >= 5
        and "machine_learning_engineer" in selected
    )


def _queries_for_roles(role_keys: list[str], skills: set[str]) -> list[JobSearchQuery]:
    queries: list[JobSearchQuery] = []
    seen_texts: set[str] = set()

    for key in role_keys:
        if key == "software_engineer_machine_learning":
            text = _COMPOSITE_SW_ML_QUERY
            role_key = "software_engineer_machine_learning"
            broaden_text = None
        else:
            role = _ROLE_BY_KEY[key]
            text, broaden_text = _query_text_for_role(role, skills)
            role_key = role.key

        normalized_text = _normalize_query_text(text)
        if normalized_text in seen_texts:
            continue
        seen_texts.add(normalized_text)
        queries.append(
            JobSearchQuery(
                text=normalized_text,
                role_key=role_key,
                broaden_text=_normalize_optional_query(broaden_text),
            )
        )
    return queries


def _query_text_for_role(role: RoleDefinition, skills: set[str]) -> tuple[str, str | None]:
    if role.key == "data_scientist" and "python" in skills:
        return "data scientist python", role.query
    if role.key == "data_analyst" and "sql" in skills:
        return "data analyst sql", role.query
    return role.query, None


def _normalize_optional_query(value: str | None) -> str | None:
    if value is None:
        return None
    return _normalize_query_text(value)


def _normalize_query_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    words = cleaned.split()
    if len(words) > MAX_QUERY_WORDS:
        cleaned = " ".join(words[:MAX_QUERY_WORDS])
    if len(cleaned) > MAX_SEARCH_QUERY_CHARS:
        cleaned = cleaned[:MAX_SEARCH_QUERY_CHARS].rstrip()
    return cleaned
