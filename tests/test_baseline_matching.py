"""Behavioral tests for Baseline Matcher v0.1."""

from __future__ import annotations

import pytest

from career_match.core.exceptions import MatchingNotImplementedError
from career_match.core.types import MatchResult
from career_match.extraction.skills import SKILL_LEXICON, extract_skill_names
from career_match.matching import BaselineMatcher, UnimplementedMatcher, skill_overlap
from career_match.matching.tfidf import tfidf_cosine_similarity, tokenize_technical


def test_unimplemented_matcher_still_raises() -> None:
    with pytest.raises(MatchingNotImplementedError, match="No production matching model"):
        UnimplementedMatcher().match("Python developer", "Looking for Python")


def test_match_result_exposes_baseline_fields() -> None:
    result = MatchResult(
        overall_score=80.0,
        tfidf_similarity=70.0,
        skill_overlap_score=90.0,
        matched_skills=("python",),
        missing_skills=("sql",),
        resume_skills=("python",),
        job_skills=("python", "sql"),
    )
    assert result.score == 80.0
    assert result.skills_in_resume == ("python",)
    assert result.skills_in_job == ("python", "sql")


def test_high_overlap_scores_higher_than_mismatch() -> None:
    matcher = BaselineMatcher()
    job = "Backend Engineer using Python, FastAPI, SQL, Docker, and Git."
    strong = matcher.match(
        "Backend Engineer. Python FastAPI SQL Docker Git on Linux.",
        job,
    )
    mismatch = matcher.match(
        "Frontend engineer. React Next.js TypeScript HTML CSS.",
        job,
    )
    assert strong.overall_score > mismatch.overall_score
    assert strong.skill_overlap_score > mismatch.skill_overlap_score


def test_identical_text_is_strong_and_in_range() -> None:
    text = "Python Django SQL Docker AWS Git Linux REST APIs"
    result = BaselineMatcher().match(text, text)
    assert 0 <= result.overall_score <= 100
    assert 0 <= result.tfidf_similarity <= 100
    assert 0 <= result.skill_overlap_score <= 100
    assert result.tfidf_similarity == pytest.approx(100.0, abs=0.01)
    assert result.skill_overlap_score == pytest.approx(100.0, abs=0.01)
    assert result.missing_skills == ()
    assert set(result.matched_skills) == set(result.job_skills)


def test_empty_inputs_score_zero() -> None:
    result = BaselineMatcher().match("", "Python developer")
    assert result.overall_score == 0.0
    assert result.tfidf_similarity == 0.0


def test_output_is_deterministic() -> None:
    matcher = BaselineMatcher()
    resume = "Python FastAPI Docker AWS"
    job = "Python FastAPI Docker AWS Git"
    first = matcher.match(resume, job)
    second = matcher.match(resume, job)
    assert first == second


def test_tokenizer_preserves_cplusplus_csharp_dotnet() -> None:
    tokens = tokenize_technical("Used C++, C#, and .NET on Linux.")
    assert "c++" in tokens
    assert "c#" in tokens
    assert ".net" in tokens


def test_tfidf_preserves_technical_tokens_in_similarity() -> None:
    job = "Need C++ and C# and .NET."
    with_tokens = tfidf_cosine_similarity("Daily C++ C# .NET work.", job)
    without_tokens = tfidf_cosine_similarity("Daily JavaScript React work.", job)
    assert with_tokens > without_tokens


def test_skill_extraction_covers_catalog_examples() -> None:
    names = extract_skill_names(
        "Python, Java, TypeScript, C++, C#, .NET, Next.js, FastAPI, PyTorch, Kubernetes"
    )
    assert "python" in names
    assert "java" in names
    assert "typescript" in names
    assert "c++" in names
    assert "c#" in names
    assert ".net" in names
    assert "next.js" in names
    assert "fastapi" in names
    assert "pytorch" in names
    assert "kubernetes" in names
    assert len(SKILL_LEXICON) == 32


def test_matched_and_missing_skills() -> None:
    coverage, matched, missing = skill_overlap(
        resume_skills=("python", "sql", "git"),
        job_skills=("python", "sql", "docker"),
    )
    assert matched == ("python", "sql")
    assert missing == ("docker",)
    assert coverage == pytest.approx(2 / 3)


def test_skill_overlap_zero_when_job_has_no_catalog_skills() -> None:
    coverage, matched, missing = skill_overlap(("python",), ())
    assert coverage == 0.0
    assert matched == ()
    assert missing == ()
