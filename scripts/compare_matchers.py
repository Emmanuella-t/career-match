#!/usr/bin/env python3
"""Compare Baseline Matcher v0.1 with Semantic Matcher v0.1 on benchmark v0.2.

Does not tune lexical weights. Does not create a hybrid matcher.
Does not alter benchmark labels.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import time
from pathlib import Path

from career_match.evaluation.benchmark_harness import BenchmarkEvaluation, evaluate_benchmark_v0_2
from career_match.evaluation.compare import comparison_rows, pair_lookup, rank_of
from career_match.evaluation.semantic_harness import evaluate_semantic_benchmark
from career_match.matching.config import MATCHER_NAME, SKILL_OVERLAP_WEIGHT, TFIDF_WEIGHT
from career_match.matching.semantic import SemanticMatcher
from career_match.matching.semantic_config import DEFAULT_MODEL_NAME, SEMANTIC_MATCHER_NAME

REPORT_PATH = Path("reports") / "semantic_matcher_v0_1_evaluation.md"
CASE_LOOKUPS = (
    ("job-mle", "r-mle-stuffing", "MLE keyword stuffing (grade 0)"),
    ("job-mle", "r-mle-synonym", "MLE synonym strong match (grade 3)"),
    ("job-mle", "r-mle-prod", "MLE token-matching strong (grade 3)"),
    ("job-backend", "r-backend-negation", "Backend negation (grade 1)"),
    ("job-mlops", "r-mlops-negation", "MLOps negation (grade 1)"),
    ("job-fullstack", "r-da-prod", "Data Analyst on Full-Stack (grade 0)"),
    ("job-de", "r-backend-prod", "Backend on Data Engineer (grade 2)"),
    ("job-de", "r-de-synonym", "DE synonym / catalog-miss phrasing (grade 2)"),
    ("job-ds", "r-ds-synonym", "DS synonym (grade 2)"),
)


def _fmt(value: float) -> str:
    return f"{value:.3f}"


def _delta(value: float) -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.3f}"


def _case_row(
    lexical: BenchmarkEvaluation,
    semantic: BenchmarkEvaluation,
    job_id: str,
    resume_id: str,
) -> str:
    left_rank = rank_of(lexical, job_id, resume_id)
    right_rank = rank_of(semantic, job_id, resume_id)
    left_pair = pair_lookup(lexical, job_id, resume_id)
    right_pair = pair_lookup(semantic, job_id, resume_id)
    left_score = f"{left_pair.overall_score:.1f}" if left_pair else "—"
    right_score = f"{right_pair.overall_score:.1f}" if right_pair else "—"
    return (
        f"| `{job_id}` / `{resume_id}` | {left_rank} | {left_score} | "
        f"{right_rank} | {right_score} |"
    )


def render_report(
    lexical: BenchmarkEvaluation,
    semantic: BenchmarkEvaluation,
    *,
    st_version: str,
    embedding_dim: int,
    load_seconds: float,
    semantic_eval_seconds: float,
    lexical_eval_seconds: float,
) -> str:
    rows = comparison_rows(lexical, semantic)
    improved = [row for row in rows if row.delta > 1e-9]
    declined = [row for row in rows if row.delta < -1e-9]
    role_declines: list[str] = []
    for sem_job in semantic.jobs:
        lex_job = next(item for item in lexical.jobs if item.job_id == sem_job.job_id)
        for label, attr in (
            ("P@1", "precision_at_1"),
            ("P@3", "precision_at_3"),
            ("NDCG@3", "ndcg_at_3"),
            ("pairwise", "pairwise_accuracy"),
        ):
            left = float(getattr(lex_job, attr))
            right = float(getattr(sem_job, attr))
            if right + 1e-9 < left:
                role_declines.append(
                    f"- {sem_job.role} {label}: {left:.3f} → {right:.3f}"
                )
    lines = [
        "# Semantic Matcher v0.1 — development evaluation",
        "",
        semantic.disclaimer,
        "",
        "This report compares a **standalone** sentence-embedding matcher with the",
        "untuned lexical baseline on the same v0.2 development benchmark.",
        "It is **not** a production quality claim and does **not** introduce a hybrid model.",
        "",
        "## Model",
        "",
        f"- Matcher: **{SEMANTIC_MATCHER_NAME}**",
        f"- Embedding model: `{DEFAULT_MODEL_NAME}`",
        f"- sentence-transformers: `{st_version}`",
        f"- Embedding dimensionality: **{embedding_dim}**",
        "- Similarity: cosine of L2-normalized embeddings",
        "- Score: `semantic_relevance = 100 * clip(cosine, 0, 1)`",
        "- The 32-skill lexicon is **not** used in this score",
        "- Device: CPU",
        "",
        "The score is **semantic relevance / similarity** on 0–100.",
        "It is not a hiring probability, acceptance probability, or candidate-quality rating.",
        "",
        "## Benchmark",
        "",
        f"- Name: `{semantic.benchmark_name}`",
        f"- Kind: {semantic.benchmark_kind}",
        f"- Jobs: **{semantic.job_count}**",
        f"- Unique synthetic resumes: **{semantic.resume_count}**",
        f"- Judgments: **{semantic.pair_count}**",
        "- Labels were not modified for this experiment",
        "",
        "## Runtime (this machine, small development set)",
        "",
        f"- MiniLM load: **{load_seconds:.1f}s**",
        f"- Semantic evaluation (32 unique texts encoded once): **{semantic_eval_seconds:.1f}s**",
        f"- Lexical baseline evaluation: **{lexical_eval_seconds:.1f}s**",
        "- Relative cost: sentence embeddings are far heavier than pair-fit TF-IDF,",
        "  even on 56 pairs, mostly due to model load and transformer encode.",
        "",
        "## Semantic metrics (mean over 8 jobs)",
        "",
        "| Metric | Mean |",
        "| --- | ---: |",
        f"| Precision@1 | {_fmt(semantic.mean_precision_at_1)} |",
        f"| Precision@3 | {_fmt(semantic.mean_precision_at_3)} |",
        f"| Recall@3 | {_fmt(semantic.mean_recall_at_3)} |",
        f"| NDCG@3 | {_fmt(semantic.mean_ndcg_at_3)} |",
        f"| NDCG (full pool) | {_fmt(semantic.mean_ndcg_full)} |",
        f"| Pairwise ordering accuracy | {_fmt(semantic.mean_pairwise_accuracy)} |",
        "",
        "## Semantic score distribution by grade",
        "",
        "| Grade | N | Mean | Min | Max |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for stats in semantic.score_stats_by_grade:
        lines.append(
            f"| {stats.grade} | {stats.count} | {stats.mean_score:.1f} | "
            f"{stats.min_score:.1f} | {stats.max_score:.1f} |"
        )
    overlap = ", ".join(f"{a} vs {b}" for a, b in semantic.overlapping_grade_bands) or "none"
    lines.extend(
        [
            "",
            f"Overlapping semantic score ranges: **{overlap}**.",
            "",
            "## Baseline comparison",
            "",
            "Lexical Baseline Matcher v0.1 was **not retuned**. Delta = semantic − lexical.",
            "",
            f"- Lexical formula: `overall = {TFIDF_WEIGHT} * tfidf + "
            f"{SKILL_OVERLAP_WEIGHT} * skill_overlap`",
            "",
            "| Metric | Lexical | Semantic | Δ |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row.name} | {_fmt(row.lexical)} | {_fmt(row.semantic)} | {_delta(row.delta)} |"
        )
    lines.extend(
        [
            "",
            "## Per-role semantic results",
            "",
        ]
    )
    for job in semantic.jobs:
        lexical_job = next(item for item in lexical.jobs if item.job_id == job.job_id)
        lines.extend(
            [
                f"### {job.role} (`{job.job_id}`)",
                "",
                f"- Semantic: P@1={job.precision_at_1:.2f} P@3={job.precision_at_3:.2f} "
                f"R@3={job.recall_at_3:.2f} NDCG@3={job.ndcg_at_3:.3f} "
                f"NDCG@7={job.ndcg_full:.3f} pairwise={job.pairwise_accuracy:.3f}",
                f"- Lexical:  P@1={lexical_job.precision_at_1:.2f} "
                f"P@3={lexical_job.precision_at_3:.2f} "
                f"NDCG@3={lexical_job.ndcg_at_3:.3f} "
                f"pairwise={lexical_job.pairwise_accuracy:.3f}",
                "",
                "| Rank | Resume | Grade | Semantic | Lexical rank | Lexical score |",
                "| ---: | --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for rank, item in enumerate(job.ranking, start=1):
            left_rank = rank_of(lexical, job.job_id, item.resume_id)
            left_pair = pair_lookup(lexical, job.job_id, item.resume_id)
            left_score = f"{left_pair.overall_score:.1f}" if left_pair else "—"
            lines.append(
                f"| {rank} | `{item.resume_id}` | {item.grade} | "
                f"{item.overall_score:.1f} | {left_rank} | {left_score} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Known failure-case inspection",
            "",
            "| Pair | Lexical rank | Lexical score | Semantic rank | Semantic score |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for job_id, resume_id, _label in CASE_LOOKUPS:
        lines.append(_case_row(lexical, semantic, job_id, resume_id))
    stuffing_l = rank_of(lexical, "job-mle", "r-mle-stuffing")
    stuffing_s = rank_of(semantic, "job-mle", "r-mle-stuffing")
    synonym_l = rank_of(lexical, "job-mle", "r-mle-synonym")
    synonym_s = rank_of(semantic, "job-mle", "r-mle-synonym")
    backend_neg_l = rank_of(lexical, "job-backend", "r-backend-negation")
    backend_neg_s = rank_of(semantic, "job-backend", "r-backend-negation")
    mlops_neg_l = rank_of(lexical, "job-mlops", "r-mlops-negation")
    mlops_neg_s = rank_of(semantic, "job-mlops", "r-mlops-negation")
    analyst_l = rank_of(lexical, "job-fullstack", "r-da-prod")
    analyst_s = rank_of(semantic, "job-fullstack", "r-da-prod")
    de_syn_l = rank_of(lexical, "job-de", "r-de-synonym")
    de_syn_s = rank_of(semantic, "job-de", "r-de-synonym")
    lines.extend(
        [
            "",
            "### Keyword stuffing",
            "",
            f"`r-mle-stuffing` moved from lexical rank **{stuffing_l}** to semantic rank "
            f"**{stuffing_s}** on the MLE job. "
            + (
                "Semantic matching no longer puts the stuffed mismatch first."
                if stuffing_s and stuffing_l and stuffing_s > stuffing_l
                else "Semantic matching still ranks the stuffed mismatch highly."
            ),
            "",
            "### Synonymy",
            "",
            f"`r-mle-synonym` moved from lexical rank **{synonym_l}** to semantic rank "
            f"**{synonym_s}**. "
            + (
                "Sentence embeddings recovered more of the synonym strong match."
                if synonym_s and synonym_l and synonym_s < synonym_l
                else "Sentence embeddings did not clearly recover the synonym match."
            ),
            "",
            "### Negation",
            "",
            f"Backend negation `r-backend-negation`: lexical rank {backend_neg_l} → "
            f"semantic rank {backend_neg_s}. "
            f"MLOps negation `r-mlops-negation`: lexical rank {mlops_neg_l} → "
            f"semantic rank {mlops_neg_s}. "
            "MiniLM is not a dedicated negation model; overlapping role language can still "
            "score a denied-skill resume highly.",
            "",
            "### Related-role overlap",
            "",
            f"Data Analyst `r-da-prod` on Full-Stack: lexical rank {analyst_l} → "
            f"semantic rank {analyst_s}. Neighboring Python roles can still score well "
            "when the prose is about software delivery even if the labeled role differs.",
            "",
            "### Skill-catalog misses",
            "",
            f"Data Engineer synonym `r-de-synonym`: lexical rank {de_syn_l} → "
            f"semantic rank {de_syn_s}. Semantic scoring does not require Spark/Airflow/"
            "PostgreSQL to be in the 32-skill lexicon; whether that helps is an empirical "
            "result in the table above, not an assumption.",
            "",
            "## Improvements",
            "",
        ]
    )
    if improved:
        lines.extend(
            f"- {row.name}: {_fmt(row.lexical)} → {_fmt(row.semantic)} ({_delta(row.delta)})"
            for row in improved
        )
    else:
        lines.append("- No mean ranking metric improved on this development set.")
    lines.extend(["", "## Regressions", ""])
    if declined:
        lines.extend(
            f"- {row.name}: {_fmt(row.lexical)} → {_fmt(row.semantic)} ({_delta(row.delta)})"
            for row in declined
        )
    else:
        lines.append("- No **mean** ranking metric declined on this development set.")
    if role_declines:
        lines.append("- Per-role declines (means can still rise while one job gets worse):")
        lines.extend(role_declines)
    lines.append(
        "- Keyword stuffing and negation can still score highly; MLE synonym recovered "
        "only partway and can still sit below a stuffed mismatch."
    )
    p1 = next(row for row in rows if row.name == "Precision@1")
    if p1.delta > 1e-9:
        overall = (
            "On this development benchmark, Semantic Matcher v0.1 improved Precision@1 "
            "relative to the frozen lexical baseline. That is not a production claim."
        )
    elif p1.delta < -1e-9:
        overall = (
            "On this development benchmark, Semantic Matcher v0.1 did **not** beat the "
            "frozen lexical baseline on Precision@1. That is still a useful ML result."
        )
    else:
        overall = (
            "On this development benchmark, Precision@1 was unchanged versus the "
            "frozen lexical baseline. Other metrics in the table should be read together."
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            overall,
            "",
            "Do not replace the lexical baseline solely because embeddings feel more modern.",
            "A later hybrid would need to beat **both** standalone systems on this same",
            "v0.2 harness. This branch does not implement that hybrid.",
            "",
            f"Generated by `scripts/compare_matchers.py` "
            f"({MATCHER_NAME} vs {SEMANTIC_MATCHER_NAME}).",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-report",
        action="store_true",
        default=True,
        help="Write reports/semantic_matcher_v0_1_evaluation.md (default: true).",
    )
    parser.add_argument(
        "--no-write-report",
        action="store_false",
        dest="write_report",
        help="Print the report without writing a file.",
    )
    args = parser.parse_args()

    t0 = time.perf_counter()
    lexical = evaluate_benchmark_v0_2()
    lexical_eval_seconds = time.perf_counter() - t0

    t1 = time.perf_counter()
    matcher = SemanticMatcher()
    _ = matcher.encoder.model  # type: ignore[attr-defined]
    load_seconds = time.perf_counter() - t1

    t2 = time.perf_counter()
    semantic = evaluate_semantic_benchmark(matcher=matcher)
    semantic_eval_seconds = time.perf_counter() - t2

    encoder = matcher.encoder
    embedding_dim = int(encoder.embedding_dim)  # type: ignore[attr-defined]
    st_version = importlib.metadata.version("sentence-transformers")

    report = render_report(
        lexical,
        semantic,
        st_version=st_version,
        embedding_dim=embedding_dim,
        load_seconds=load_seconds,
        semantic_eval_seconds=semantic_eval_seconds,
        lexical_eval_seconds=lexical_eval_seconds,
    )
    print(report)
    if args.write_report:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(report, encoding="utf-8")
        print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
