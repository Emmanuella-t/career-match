"""Run Baseline Matcher v0.1 against the development evaluation fixture."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from career_match.evaluation.fixture import EvaluationFixture, load_evaluation_fixture
from career_match.evaluation.ranking import ndcg_at_k, precision_at_k, recall_at_k
from career_match.matching import BaselineMatcher
from career_match.matching.config import MATCHER_NAME, BaselineConfig


@dataclass(frozen=True)
class RankedCandidate:
    candidate_id: str
    label: str
    relevance: int
    overall_score: float
    tfidf_similarity: float
    skill_overlap_score: float
    matched_skills: tuple[str, ...]
    missing_skills: tuple[str, ...]


@dataclass(frozen=True)
class QueryEvaluation:
    query_id: str
    role: str
    ranking: tuple[RankedCandidate, ...]
    strong_above_moderate: bool
    moderate_above_mismatch: bool
    precision_at_1: float
    precision_at_2: float
    recall_at_2: float
    ndcg_at_2: float
    ndcg_at_4: float


@dataclass(frozen=True)
class BaselineEvaluation:
    matcher_name: str
    config: BaselineConfig
    fixture_name: str
    fixture_kind: str
    disclaimer: str
    pair_count: int
    query_count: int
    queries: tuple[QueryEvaluation, ...]
    mean_precision_at_1: float
    mean_precision_at_2: float
    mean_recall_at_2: float
    mean_ndcg_at_2: float
    mean_ndcg_at_4: float
    ranking_checks_passed: bool


def _score_query(matcher: BaselineMatcher, query) -> QueryEvaluation:
    ranked: list[RankedCandidate] = []
    by_label: dict[str, RankedCandidate] = {}
    for candidate in query.candidates:
        result = matcher.match(candidate.resume_text, query.job_text)
        item = RankedCandidate(
            candidate_id=candidate.candidate_id,
            label=candidate.label,
            relevance=candidate.relevance,
            overall_score=result.overall_score,
            tfidf_similarity=result.tfidf_similarity,
            skill_overlap_score=result.skill_overlap_score,
            matched_skills=result.matched_skills,
            missing_skills=result.missing_skills,
        )
        ranked.append(item)
        by_label[candidate.label] = item
    ranked.sort(key=lambda item: item.overall_score, reverse=True)
    grades = [item.relevance for item in ranked]
    threshold = 2
    return QueryEvaluation(
        query_id=query.query_id,
        role=query.role,
        ranking=tuple(ranked),
        strong_above_moderate=by_label["strong"].overall_score
        > by_label["moderate"].overall_score,
        moderate_above_mismatch=by_label["moderate"].overall_score
        > by_label["mismatch"].overall_score,
        precision_at_1=precision_at_k(grades, 1, relevant_threshold=threshold),
        precision_at_2=precision_at_k(grades, 2, relevant_threshold=threshold),
        recall_at_2=recall_at_k(grades, 2, relevant_threshold=threshold),
        ndcg_at_2=ndcg_at_k(grades, 2),
        ndcg_at_4=ndcg_at_k(grades, 4),
    )


def evaluate_baseline(
    matcher: BaselineMatcher | None = None,
    fixture: EvaluationFixture | None = None,
) -> BaselineEvaluation:
    """Score every fixture pair and compute ranking metrics."""
    matcher = matcher or BaselineMatcher()
    fixture = fixture or load_evaluation_fixture()
    query_results = tuple(_score_query(matcher, query) for query in fixture.queries)
    ranking_ok = all(
        item.strong_above_moderate and item.moderate_above_mismatch for item in query_results
    )
    return BaselineEvaluation(
        matcher_name=MATCHER_NAME,
        config=matcher.config,
        fixture_name=fixture.name,
        fixture_kind=fixture.kind,
        disclaimer=fixture.disclaimer,
        pair_count=fixture.pair_count,
        query_count=len(query_results),
        queries=query_results,
        mean_precision_at_1=mean(item.precision_at_1 for item in query_results),
        mean_precision_at_2=mean(item.precision_at_2 for item in query_results),
        mean_recall_at_2=mean(item.recall_at_2 for item in query_results),
        mean_ndcg_at_2=mean(item.ndcg_at_2 for item in query_results),
        mean_ndcg_at_4=mean(item.ndcg_at_4 for item in query_results),
        ranking_checks_passed=ranking_ok,
    )
