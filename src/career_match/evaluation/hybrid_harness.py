"""Batch evaluation of Hybrid Matcher v0.1 on development or holdout benchmarks."""

from __future__ import annotations

from career_match.evaluation.benchmark import DevelopmentBenchmark, load_benchmark
from career_match.evaluation.benchmark_harness import (
    BenchmarkEvaluation,
    ScoredPair,
    assemble_evaluation,
    job_result_from_scored,
)
from career_match.matching.hybrid import HybridMatcher
from career_match.matching.hybrid_config import HYBRID_MATCHER_NAME


def evaluate_hybrid_benchmark(
    matcher: HybridMatcher | None = None,
    benchmark: DevelopmentBenchmark | None = None,
) -> BenchmarkEvaluation:
    """Score every benchmark pair with Hybrid Matcher v0.1."""
    matcher = matcher or HybridMatcher()
    benchmark = benchmark or load_benchmark()
    # Warm the semantic encoder once so pair loops reuse it.
    _ = matcher.semantic_matcher.encoder
    jobs = benchmark.job_by_id()
    resumes = benchmark.resume_by_id()
    grouped = benchmark.judgments_by_job()
    job_results = []
    for job in benchmark.jobs:
        judgments = grouped.get(job.job_id)
        if not judgments:
            continue
        job_text = job.to_text()
        scored: list[ScoredPair] = []
        for judgment in judgments:
            resume = resumes[judgment.resume_id]
            result = matcher.match(resume.to_text(), job_text)
            scored.append(
                ScoredPair(
                    job_id=job.job_id,
                    role=jobs[job.job_id].title,
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
        job_results.append(job_result_from_scored(job.job_id, job.title, scored))
    return assemble_evaluation(
        HYBRID_MATCHER_NAME,
        matcher.config,
        benchmark,
        tuple(job_results),
    )
