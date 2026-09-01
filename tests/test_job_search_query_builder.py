"""Tests for deterministic resume search-query builder."""

from __future__ import annotations

from career_match.jobs.query_builder import build_job_search_query


def test_query_builder_uses_role_and_top_skills() -> None:
    resume = (
        "Jordan Lee\nMachine Learning Engineer\n\n"
        "Built PyTorch models and Python services with Docker and SQL."
    )
    query = build_job_search_query(resume)
    assert query.role_term == "machine learning engineer"
    assert "python" in query.skill_terms
    assert "machine learning engineer" in query.text.lower()
    assert "python" in query.text.lower()
    assert len(query.text) <= 80


def test_query_builder_does_not_include_entire_resume() -> None:
    resume = "A" * 5000 + "\nSkills: Python, Docker"
    query = build_job_search_query(resume)
    assert len(query.text) <= 80
    assert "A" * 100 not in query.text


def test_query_builder_skill_only_fallback() -> None:
    resume = "Skills: Python, Docker, Git"
    query = build_job_search_query(resume)
    assert query.text
    assert query.skill_terms
