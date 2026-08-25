"""Compare lexical baseline and semantic matcher metrics on the same benchmark."""

from __future__ import annotations

from dataclasses import dataclass

from career_match.evaluation.benchmark_harness import BenchmarkEvaluation

METRIC_FIELDS: tuple[tuple[str, str], ...] = (
    ("Precision@1", "mean_precision_at_1"),
    ("Precision@3", "mean_precision_at_3"),
    ("Recall@3", "mean_recall_at_3"),
    ("NDCG@3", "mean_ndcg_at_3"),
    ("NDCG (full pool)", "mean_ndcg_full"),
    ("Pairwise ordering accuracy", "mean_pairwise_accuracy"),
)


@dataclass(frozen=True)
class MetricComparison:
    name: str
    lexical: float
    semantic: float
    delta: float


def comparison_rows(
    lexical: BenchmarkEvaluation,
    semantic: BenchmarkEvaluation,
) -> tuple[MetricComparison, ...]:
    """Return semantic minus lexical for each shared ranking metric."""
    rows: list[MetricComparison] = []
    for name, field in METRIC_FIELDS:
        left = float(getattr(lexical, field))
        right = float(getattr(semantic, field))
        rows.append(MetricComparison(name=name, lexical=left, semantic=right, delta=right - left))
    return tuple(rows)


def pair_lookup(evaluation: BenchmarkEvaluation, job_id: str, resume_id: str):
    """Return the ranked pair for a job/resume, or None."""
    for pair in evaluation.pairs:
        if pair.job_id == job_id and pair.resume_id == resume_id:
            return pair
    return None


def rank_of(evaluation: BenchmarkEvaluation, job_id: str, resume_id: str) -> int | None:
    for job in evaluation.jobs:
        if job.job_id != job_id:
            continue
        for index, pair in enumerate(job.ranking, start=1):
            if pair.resume_id == resume_id:
                return index
    return None
