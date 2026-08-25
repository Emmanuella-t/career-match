"""Evaluate unchanged matchers on frozen holdout benchmark v0.3.

Does not tune lexical weights. Does not create a hybrid matcher.
Does not alter holdout labels after evaluation.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import time
from pathlib import Path

from career_match.evaluation.benchmark_harness import (
    BenchmarkEvaluation,
    evaluate_benchmark_v0_2,
)
from career_match.evaluation.compare import comparison_rows, pair_lookup, rank_of
from career_match.evaluation.holdout_benchmark import (
    compute_holdout_checksum,
    load_holdout_benchmark,
)
from career_match.evaluation.semantic_harness import evaluate_semantic_benchmark
from career_match.matching.config import MATCHER_NAME, SKILL_OVERLAP_WEIGHT, TFIDF_WEIGHT
from career_match.matching.semantic import SemanticMatcher
from career_match.matching.semantic_config import DEFAULT_MODEL_NAME, SEMANTIC_MATCHER_NAME

REPORT_PATH = Path("reports") / "holdout_benchmark_v0_3_snapshot.md"
LABEL_REVIEW_PATH = Path("reports") / "holdout_benchmark_v0_3_label_review.md"

CASE_LOOKUPS = (
    ("hold-mle", "h-stuffing", "MLE keyword stuffing (grade 0)"),
    ("hold-mle", "h-mle-paraphrase", "MLE synonym strong match (grade 3)"),
    ("hold-mle", "h-mle-core", "MLE token-matching strong (grade 3)"),
    ("hold-mle", "h-mle-notebook", "MLE negation / weak production (grade 1)"),
    ("hold-be", "h-be-negation", "Backend negation (grade 1)"),
    ("hold-mlops", "h-mlops-negation", "MLOps negation (grade 1)"),
    ("hold-de", "h-de-synonym", "DE synonym / catalog-miss phrasing (grade 2)"),
    ("hold-fs", "h-da-core", "Data Analyst on Full-Stack (grade 1)"),
    ("hold-nlp", "h-nlp-synonym", "NLP synonym strong match (grade 3)"),
)


def _fmt(value: float) -> str:
    return f"{value:.3f}"


def _delta(value: float) -> str:
    if value > 0:
        return f"+{value:.3f}"
    return f"{value:.3f}"


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
    left_score = f"{left_pair.overall_score:.1f}" if left_pair else "-"
    right_score = f"{right_pair.overall_score:.1f}" if right_pair else "-"
    return (
        f"| `{job_id}` / `{resume_id}` | {left_rank} | {left_score} | "
        f"{right_rank} | {right_score} |"
    )


def render_label_review(benchmark) -> str:
    jobs = benchmark.job_by_id()
    lines = [
        "# Holdout benchmark v0.3 label review aid",
        "",
        "Status: awaiting/available for manual review",
        "",
        "This table lists all construction-time relevance judgments in",
        "`data/evaluation/holdout_benchmark_v0_3.json`. It is a review aid.",
        "It does **not** mark the labels as independently reviewed,",
        "expert-labeled, or production hiring labels.",
        "",
        "Labels are **manually specified synthetic relevance judgments**,",
        "not independently validated ground truth.",
        "",
        "Provenance:",
        "",
        "- Synthetic benchmark",
        "- No real candidate data",
        "- No real hiring outcomes",
        "- No independent annotator agreement",
        "- Not production ground truth",
        "- Intended for controlled model comparison",
        "- Frozen before hybrid-matcher development",
        "",
        "| Job | Resume ID | Grade | Rationale | Case tags |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for judgment in benchmark.judgments:
        job = jobs[judgment.job_id]
        tags = ", ".join(judgment.case_tags)
        rationale = judgment.rationale.replace("|", "\\|")
        lines.append(
            f"| {job.title} (`{judgment.job_id}`) | `{judgment.resume_id}` | "
            f"{judgment.grade} | {rationale} | {tags} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_snapshot(
    lexical: BenchmarkEvaluation,
    semantic: BenchmarkEvaluation,
    *,
    checksum: str,
    roles: list[str],
) -> str:
    grade_dist = lexical.grade_distribution
    rows = comparison_rows(lexical, semantic)
    notable: list[str] = []
    for job in lexical.jobs:
        top = job.ranking[0]
        if top.grade == 0:
            notable.append(
                f"- Lexical Precision@1 miss on {job.role}: `{top.resume_id}` "
                f"(grade 0) ranked #1 with score {top.overall_score:.1f}."
            )
        synonym = next(
            (item for item in job.ranking if "synonymy" in item.case_tags),
            None,
        )
        stuffing = next(
            (item for item in job.ranking if "keyword_stuffing" in item.case_tags),
            None,
        )
        if synonym and stuffing and stuffing.overall_score > synonym.overall_score:
            notable.append(
                f"- Lexical synonym under-rank on {job.role}: stuffing "
                f"`{stuffing.resume_id}` ({stuffing.overall_score:.1f}) above "
                f"synonym `{synonym.resume_id}` ({synonym.overall_score:.1f})."
            )
    for job in semantic.jobs:
        top = job.ranking[0]
        if top.grade == 0:
            notable.append(
                f"- Semantic Precision@1 miss on {job.role}: `{top.resume_id}` "
                f"(grade 0) ranked #1 with score {top.overall_score:.1f}."
            )
        negation = next(
            (item for item in job.ranking if "negation" in item.case_tags),
            None,
        )
        if negation and negation.overall_score >= 70:
            notable.append(
                f"- Semantic high score on negation case {job.role}/"
                f"`{negation.resume_id}`: {negation.overall_score:.1f} "
                f"(rank {rank_of(semantic, job.job_id, negation.resume_id)})."
            )
    if not notable:
        notable.append("- No automatic notable-failure heuristics fired; inspect per-role tables.")

    lines = [
        "# Holdout benchmark v0.3 — pre-hybrid snapshot",
        "",
        lexical.disclaimer,
        "",
        "This report records **unchanged** Lexical Baseline Matcher v0.1 and",
        "Semantic Matcher v0.1 on the frozen holdout set. It does **not** propose",
        "model changes, does **not** tune weights, and does **not** introduce a hybrid.",
        "The holdout JSON was not modified after these scores were computed.",
        "",
        "## Benchmark",
        "",
        f"- Name: `{lexical.benchmark_name}`",
        "- Version: **0.3**",
        f"- Kind: {lexical.benchmark_kind}",
        f"- Jobs: **{lexical.job_count}**",
        f"- Unique synthetic resumes: **{lexical.resume_count}**",
        f"- Judgments: **{lexical.pair_count}**",
        f"- Roles: {', '.join(roles)}",
        f"- SHA-256: `{checksum}`",
        "- Checksum purpose: reproducibility (detect accidental edits), not security",
        "",
        "## Provenance",
        "",
        "- Synthetic benchmark",
        "- No real candidate data",
        "- No real hiring outcomes",
        "- No independent annotator agreement",
        "- Not production ground truth",
        "- Intended for controlled model comparison",
        "- Created before hybrid-matcher development; remain frozen during that milestone",
        "- v0.2 remains the development/error-analysis benchmark",
        "",
        "## Grade distribution",
        "",
        "| Grade | Label | Count |",
        "| ---: | --- | ---: |",
        f"| 3 | strong | {grade_dist.get(3, 0)} |",
        f"| 2 | moderate | {grade_dist.get(2, 0)} |",
        f"| 1 | weak | {grade_dist.get(1, 0)} |",
        f"| 0 | mismatch | {grade_dist.get(0, 0)} |",
        "",
        "## Lexical Baseline Matcher v0.1 (mean over jobs)",
        "",
        f"- Formula unchanged: `overall = {TFIDF_WEIGHT} * tfidf + "
        f"{SKILL_OVERLAP_WEIGHT} * skill_overlap`",
        "- Weights were **not** tuned on v0.3.",
        "",
        "| Metric | Mean |",
        "| --- | ---: |",
        f"| Precision@1 | {_fmt(lexical.mean_precision_at_1)} |",
        f"| Precision@3 | {_fmt(lexical.mean_precision_at_3)} |",
        f"| Recall@3 | {_fmt(lexical.mean_recall_at_3)} |",
        f"| NDCG@3 | {_fmt(lexical.mean_ndcg_at_3)} |",
        f"| NDCG (full pool) | {_fmt(lexical.mean_ndcg_full)} |",
        f"| Pairwise ordering accuracy | {_fmt(lexical.mean_pairwise_accuracy)} |",
        "",
        "## Semantic Matcher v0.1 (mean over jobs)",
        "",
        f"- Embedding model: `{DEFAULT_MODEL_NAME}`",
        "- Standalone cosine similarity; lexicon not used; not mixed with TF-IDF.",
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
        "## Side-by-side (holdout)",
        "",
        "Delta = semantic - lexical. Not a production quality claim.",
        "",
        "| Metric | Lexical | Semantic | Δ |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.name} | {_fmt(row.lexical)} | {_fmt(row.semantic)} | {_delta(row.delta)} |"
        )
    lines.extend(
        [
            "",
            "## Per-role metrics",
            "",
        ]
    )
    for job in lexical.jobs:
        sem_job = next(item for item in semantic.jobs if item.job_id == job.job_id)
        lines.extend(
            [
                f"### {job.role} (`{job.job_id}`)",
                "",
                f"- Lexical:  P@1={job.precision_at_1:.3f} P@3={job.precision_at_3:.3f} "
                f"R@3={job.recall_at_3:.3f} NDCG@3={job.ndcg_at_3:.3f} "
                f"NDCG@full={job.ndcg_full:.3f} pairwise={job.pairwise_accuracy:.3f}",
                f"- Semantic: P@1={sem_job.precision_at_1:.3f} "
                f"P@3={sem_job.precision_at_3:.3f} "
                f"R@3={sem_job.recall_at_3:.3f} NDCG@3={sem_job.ndcg_at_3:.3f} "
                f"NDCG@full={sem_job.ndcg_full:.3f} pairwise={sem_job.pairwise_accuracy:.3f}",
                "",
                "| Rank | Resume | Grade | Lexical | Semantic rank | Semantic |",
                "| ---: | --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for rank, item in enumerate(job.ranking, start=1):
            sem_rank = rank_of(semantic, job.job_id, item.resume_id)
            sem_pair = pair_lookup(semantic, job.job_id, item.resume_id)
            sem_score = f"{sem_pair.overall_score:.1f}" if sem_pair else "-"
            lines.append(
                f"| {rank} | `{item.resume_id}` | {item.grade} | "
                f"{item.overall_score:.1f} | {sem_rank} | {sem_score} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Notable observed failures",
            "",
            "Recorded for later reference only. Do not optimize matchers against these",
            "holdout errors in this milestone.",
            "",
        ]
    )
    lines.extend(notable)
    lines.extend(
        [
            "",
            "### Case inspection table",
            "",
            "| Pair | Lexical rank | Lexical score | Semantic rank | Semantic score |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for job_id, resume_id, _label in CASE_LOOKUPS:
        lines.append(_case_row(lexical, semantic, job_id, resume_id))
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- No matcher code was changed for this snapshot.",
            "- No weights were tuned on v0.3.",
            "- No hybrid matcher was added.",
            "- These numbers are a frozen pre-hybrid baseline, not production KPIs.",
            "",
            f"Generated by `scripts/evaluate_holdout_v0_3.py` "
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
        help="Write holdout snapshot and label-review reports (default: true).",
    )
    parser.add_argument(
        "--no-write-report",
        action="store_false",
        dest="write_report",
        help="Print without writing report files.",
    )
    args = parser.parse_args()

    checksum_before = compute_holdout_checksum()
    benchmark = load_holdout_benchmark()
    roles = [job.title for job in benchmark.jobs]

    t0 = time.perf_counter()
    lexical = evaluate_benchmark_v0_2(benchmark=benchmark)
    lexical_seconds = time.perf_counter() - t0

    matcher = SemanticMatcher()
    t1 = time.perf_counter()
    semantic = evaluate_semantic_benchmark(matcher=matcher, benchmark=benchmark)
    semantic_seconds = time.perf_counter() - t1

    checksum_after = compute_holdout_checksum()
    if checksum_after != checksum_before:
        raise SystemExit(
            "Holdout benchmark changed during evaluation; refusing to write report."
        )

    snapshot = render_snapshot(
        lexical,
        semantic,
        checksum=checksum_before,
        roles=roles,
    )
    label_review = render_label_review(benchmark)
    if args.write_report:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(snapshot, encoding="utf-8")
        LABEL_REVIEW_PATH.write_text(label_review, encoding="utf-8")
        print(f"Wrote {REPORT_PATH}")
        print(f"Wrote {LABEL_REVIEW_PATH}")
    print(snapshot.encode("ascii", errors="replace").decode("ascii"))
    print(f"\nLexical eval seconds: {lexical_seconds:.2f}")
    print(f"Semantic eval seconds: {semantic_seconds:.2f}")
    print(f"sentence-transformers: {importlib.metadata.version('sentence-transformers')}")


if __name__ == "__main__":
    main()
