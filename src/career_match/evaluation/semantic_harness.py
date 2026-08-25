"""Batch evaluation of Semantic Matcher v0.1 on development benchmark v0.2.

Each unique job text and resume text is encoded once. The lexical baseline
is not used here.
"""

from __future__ import annotations

from career_match.evaluation.benchmark import DevelopmentBenchmark, load_benchmark
from career_match.evaluation.benchmark_harness import (
    BenchmarkEvaluation,
    ScoredPair,
    assemble_evaluation,
    job_result_from_scored,
)
from career_match.matching.semantic import SemanticMatcher
from career_match.matching.semantic_config import SEMANTIC_MATCHER_NAME


def evaluate_semantic_benchmark(
    matcher: SemanticMatcher | None = None,
    benchmark: DevelopmentBenchmark | None = None,
) -> BenchmarkEvaluation:
    """Score every v0.2 pair with standalone sentence-embedding cosine similarity."""
    matcher = matcher or SemanticMatcher()
    benchmark = benchmark or load_benchmark()
    jobs = list(benchmark.jobs)
    resumes = list(benchmark.resumes)
    job_vectors = matcher.encode_texts([job.to_text() for job in jobs])
    resume_vectors = matcher.encode_texts([resume.to_text() for resume in resumes])
    job_index = {job.job_id: index for index, job in enumerate(jobs)}
    resume_index = {resume.resume_id: index for index, resume in enumerate(resumes)}
    grouped = benchmark.judgments_by_job()
    job_results = []
    for job in jobs:
        judgments = grouped.get(job.job_id)
        if not judgments:
            continue
        job_vector = job_vectors[job_index[job.job_id]]
        resume_ids = [item.resume_id for item in judgments]
        stacked = resume_vectors[[resume_index[resume_id] for resume_id in resume_ids]]
        scores = matcher.similarity_scores(stacked, job_vector)
        scored: list[ScoredPair] = []
        for judgment, score in zip(judgments, scores, strict=True):
            value = float(score)
            scored.append(
                ScoredPair(
                    job_id=job.job_id,
                    role=job.title,
                    resume_id=judgment.resume_id,
                    grade=judgment.grade,
                    label=judgment.label,
                    rationale=judgment.rationale,
                    case_tags=judgment.case_tags,
                    overall_score=value,
                    tfidf_similarity=0.0,
                    skill_overlap_score=0.0,
                    matched_skills=(),
                    missing_skills=(),
                    semantic_similarity=value,
                )
            )
        job_results.append(job_result_from_scored(job.job_id, job.title, scored))
    return assemble_evaluation(
        SEMANTIC_MATCHER_NAME,
        matcher.config,
        benchmark,
        tuple(job_results),
    )
