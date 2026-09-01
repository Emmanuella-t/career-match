"""Tests for deterministic resume search-query builder."""

from __future__ import annotations

from career_match.jobs.query_builder import (
    MAX_SEARCH_QUERIES,
    build_job_search_queries,
    build_job_search_query,
)

ML_SWE_RESUME = (
    "Alex Chen\nSoftware Engineer\n\n"
    "Experience\n"
    "Machine Learning Engineer, Acme AI (2022-2024)\n"
    "- Trained PyTorch models for NLP classification and model evaluation\n"
    "- Built feature engineering pipelines with scikit-learn\n\n"
    "Software Engineer, Tech Corp (2020-2022)\n"
    "- C++ and Java services for data processing\n"
    "- Python tooling for machine learning workflows\n\n"
    "Skills: Python, PyTorch, scikit-learn, machine learning, C++, Java, SQL"
)

FRONTEND_RESUME = (
    "Sam Rivera\nFrontend Engineer\n\n"
    "Built customer dashboards with React, Next.js, TypeScript, HTML, and CSS.\n"
    "Implemented responsive UI components and frontend development best practices."
)

BACKEND_RESUME = (
    "Priya Nair\nBackend Engineer\n\n"
    "Designed REST APIs with FastAPI and Flask, PostgreSQL, and Docker microservices.\n"
    "Skills: Python, FastAPI, SQL, Docker, Linux"
)


def _query_texts(resume: str) -> list[str]:
    return [query.text.lower() for query in build_job_search_queries(resume).queries]


def test_ml_resume_does_not_infer_frontend_from_unrelated_languages() -> None:
    plan = build_job_search_queries(ML_SWE_RESUME)
    joined = " | ".join(query.text.lower() for query in plan.queries)
    assert "frontend" not in joined
    assert plan.primary.text.lower() == "machine learning engineer"


def test_ml_resume_produces_concise_role_queries() -> None:
    queries = _query_texts(ML_SWE_RESUME)
    assert "machine learning engineer" in queries
    assert any(
        term in query
        for query in queries
        for term in (
            "applied ai engineer",
            "software engineer",
            "software engineer machine learning",
        )
    )
    assert "c++" not in " ".join(queries)
    assert "java" not in " ".join(queries)


def test_frontend_resume_infers_frontend_role() -> None:
    plan = build_job_search_queries(FRONTEND_RESUME)
    assert plan.primary.text.lower() == "frontend engineer"
    assert "react" not in plan.primary.text.lower()


def test_backend_resume_infers_backend_role() -> None:
    plan = build_job_search_queries(BACKEND_RESUME)
    assert plan.primary.text.lower() == "backend engineer"


def test_max_query_count_enforced() -> None:
    plan = build_job_search_queries(ML_SWE_RESUME)
    assert len(plan.queries) <= MAX_SEARCH_QUERIES


def test_queries_are_concise_not_keyword_stuffed() -> None:
    plan = build_job_search_queries(ML_SWE_RESUME)
    for query in plan.queries:
        assert len(query.text.split()) <= 5
        assert len(query.text) <= 80


def test_primary_helper_returns_first_ranked_query() -> None:
    primary = build_job_search_query(ML_SWE_RESUME)
    plan = build_job_search_queries(ML_SWE_RESUME)
    assert primary.text == plan.primary.text


def test_data_scientist_query_can_include_supporting_python_term() -> None:
    resume = (
        "Jamie Fox\nData Scientist\n\n"
        "Built statistical models and experiment analysis with Python, pandas, and SQL."
    )
    plan = build_job_search_queries(resume)
    assert plan.primary.text.lower() in {"data scientist python", "data scientist"}
    if plan.primary.broaden_text:
        assert plan.primary.broaden_text.lower() == "data scientist"


def test_query_builder_does_not_include_entire_resume() -> None:
    resume = "A" * 5000 + "\nMachine Learning Engineer with PyTorch and scikit-learn."
    query = build_job_search_query(resume)
    assert len(query.text) <= 80
    assert "A" * 100 not in query.text


def test_old_behavior_would_have_overloaded_ml_resume() -> None:
    """Document regression guard: languages must not be appended to the role query."""
    plan = build_job_search_queries(ML_SWE_RESUME)
    assert plan.primary.text == "machine learning engineer"
    assert "machine learning engineer c++" not in plan.primary.text.lower()
    assert "machine learning engineer java" not in plan.primary.text.lower()
