"""Evaluate Baseline Matcher v0.1 on development benchmark v0.2.

Weights are taken from ``career_match.matching.config`` and are not tuned
on this benchmark.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from statistics import mean

from career_match.evaluation.benchmark import DevelopmentBenchmark, load_benchmark
from career_match.evaluation.ranking import (
    ndcg_at_k,
    pairwise_ordering_accuracy,
    precision_at_k,
    recall_at_k,
)
from career_match.matching import BaselineMatcher
from career_match.matching.config import MATCHER_NAME

RELEVANT_THRESHOLD = 2


@dataclass(frozen=True)
class ScoredPair:
    job_id: str
    role: str
    resume_id: str
    grade: int
    label: str
    rationale: str
    case_tags: tuple[str, ...]
    overall_score: float
    tfidf_similarity: float
    skill_overlap_score: float
    matched_skills: tuple[str, ...]
    missing_skills: tuple[str, ...]
    semantic_similarity: float = 0.0


@dataclass(frozen=True)
class JobBenchmarkResult:
    job_id: str
    role: str
    pool_size: int
    ranking: tuple[ScoredPair, ...]
    precision_at_1: float
    precision_at_3: float
    recall_at_3: float
    ndcg_at_3: float
    ndcg_full: float
    pairwise_accuracy: float
    mean_score_by_grade: dict[int, float]


@dataclass(frozen=True)
class GradeScoreStats:
    grade: int
    count: int
    mean_score: float
    min_score: float
    max_score: float


@dataclass(frozen=True)
class BenchmarkEvaluation:
    matcher_name: str
    config: object
    benchmark_name: str
    benchmark_kind: str
    disclaimer: str
    job_count: int
    resume_count: int
    pair_count: int
    grade_distribution: dict[int, int]
    jobs: tuple[JobBenchmarkResult, ...]
    pairs: tuple[ScoredPair, ...]
    mean_precision_at_1: float
    mean_precision_at_3: float
    mean_recall_at_3: float
    mean_ndcg_at_3: float
    mean_ndcg_full: float
    mean_pairwise_accuracy: float
    score_stats_by_grade: tuple[GradeScoreStats, ...]
    overlapping_grade_bands: tuple[tuple[int, int], ...]


def _score_stats(pairs: tuple[ScoredPair, ...]) -> tuple[GradeScoreStats, ...]:
    by_grade: dict[int, list[float]] = defaultdict(list)
    for pair in pairs:
        by_grade[pair.grade].append(pair.overall_score)
    stats: list[GradeScoreStats] = []
    for grade in range(4):
        scores = by_grade.get(grade, [])
        if not scores:
            stats.append(
                GradeScoreStats(
                    grade=grade,
                    count=0,
                    mean_score=0.0,
                    min_score=0.0,
                    max_score=0.0,
                )
            )
            continue
        stats.append(
            GradeScoreStats(
                grade=grade,
                count=len(scores),
                mean_score=mean(scores),
                min_score=min(scores),
                max_score=max(scores),
            )
        )
    return tuple(stats)


def _overlapping_bands(stats: tuple[GradeScoreStats, ...]) -> tuple[tuple[int, int], ...]:
    overlapping: list[tuple[int, int]] = []
    present = [item for item in stats if item.count]
    for i, lower in enumerate(present):
        for higher in present[i + 1 :]:
            if lower.max_score >= higher.min_score and higher.max_score >= lower.min_score:
                overlapping.append((lower.grade, higher.grade))
    return tuple(overlapping)


def _evaluate_job(
    matcher: BaselineMatcher,
    benchmark: DevelopmentBenchmark,
    job_id: str,
    judgments: tuple,
) -> JobBenchmarkResult:
    jobs = benchmark.job_by_id()
    resumes = benchmark.resume_by_id()
    job = jobs[job_id]
    job_text = job.to_text()
    scored: list[ScoredPair] = []
    for judgment in judgments:
        resume = resumes[judgment.resume_id]
        result = matcher.match(resume.to_text(), job_text)
        scored.append(
            ScoredPair(
                job_id=job.job_id,
                role=job.title,
                resume_id=resume.resume_id,
                grade=judgment.grade,
                label=judgment.label,
                rationale=judgment.rationale,
                case_tags=judgment.case_tags,
                overall_score=result.overall_score,
                tfidf_similarity=result.tfidf_similarity,
                skill_overlap_score=result.skill_overlap_score,
                matched_skills=result.matched_skills,
                missing_skills=result.missing_skills,
                semantic_similarity=result.semantic_similarity,
            )
        )
    return job_result_from_scored(job.job_id, job.title, scored)


def job_result_from_scored(
    job_id: str,
    role: str,
    scored: list[ScoredPair],
) -> JobBenchmarkResult:
    ranking = tuple(sorted(scored, key=lambda item: item.overall_score, reverse=True))
    grades = [item.grade for item in ranking]
    scores = [item.overall_score for item in ranking]
    k_full = len(grades)
    by_grade: dict[int, list[float]] = defaultdict(list)
    for item in ranking:
        by_grade[item.grade].append(item.overall_score)
    return JobBenchmarkResult(
        job_id=job_id,
        role=role,
        pool_size=k_full,
        ranking=ranking,
        precision_at_1=precision_at_k(grades, 1, relevant_threshold=RELEVANT_THRESHOLD),
        precision_at_3=precision_at_k(grades, 3, relevant_threshold=RELEVANT_THRESHOLD),
        recall_at_3=recall_at_k(grades, 3, relevant_threshold=RELEVANT_THRESHOLD),
        ndcg_at_3=ndcg_at_k(grades, 3),
        ndcg_full=ndcg_at_k(grades, k_full),
        pairwise_accuracy=pairwise_ordering_accuracy(grades, scores),
        mean_score_by_grade={
            grade: mean(values) for grade, values in sorted(by_grade.items())
        },
    )


def assemble_evaluation(
    matcher_name: str,
    config: object,
    benchmark: DevelopmentBenchmark,
    job_results: tuple[JobBenchmarkResult, ...],
) -> BenchmarkEvaluation:
    pairs = tuple(item for job in job_results for item in job.ranking)
    stats = _score_stats(pairs)
    return BenchmarkEvaluation(
        matcher_name=matcher_name,
        config=config,
        benchmark_name=benchmark.name,
        benchmark_kind=benchmark.kind,
        disclaimer=benchmark.disclaimer,
        job_count=benchmark.job_count,
        resume_count=benchmark.resume_count,
        pair_count=benchmark.pair_count,
        grade_distribution=benchmark.grade_distribution(),
        jobs=job_results,
        pairs=pairs,
        mean_precision_at_1=mean(item.precision_at_1 for item in job_results),
        mean_precision_at_3=mean(item.precision_at_3 for item in job_results),
        mean_recall_at_3=mean(item.recall_at_3 for item in job_results),
        mean_ndcg_at_3=mean(item.ndcg_at_3 for item in job_results),
        mean_ndcg_full=mean(item.ndcg_full for item in job_results),
        mean_pairwise_accuracy=mean(item.pairwise_accuracy for item in job_results),
        score_stats_by_grade=stats,
        overlapping_grade_bands=_overlapping_bands(stats),
    )


def evaluate_benchmark_v0_2(
    matcher: BaselineMatcher | None = None,
    benchmark: DevelopmentBenchmark | None = None,
) -> BenchmarkEvaluation:
    """Score every v0.2 judgment with the untuned lexical baseline."""
    matcher = matcher or BaselineMatcher()
    benchmark = benchmark or load_benchmark()
    grouped = benchmark.judgments_by_job()
    job_results = tuple(
        _evaluate_job(matcher, benchmark, job.job_id, grouped[job.job_id])
        for job in benchmark.jobs
        if job.job_id in grouped
    )
    return assemble_evaluation(MATCHER_NAME, matcher.config, benchmark, job_results)
