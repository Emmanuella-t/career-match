#!/usr/bin/env python3
"""Evaluate frozen Hybrid Matcher v0.1 on v0.2 and optionally holdout v0.3.

Does not tune weights. Does not modify holdout labels.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from career_match.evaluation.benchmark_harness import BenchmarkEvaluation, evaluate_benchmark_v0_2
from career_match.evaluation.compare import pair_lookup, rank_of
from career_match.evaluation.holdout_benchmark import (
    compute_holdout_checksum,
    expected_holdout_checksum,
    load_holdout_benchmark,
)
from career_match.evaluation.hybrid_harness import evaluate_hybrid_benchmark
from career_match.evaluation.semantic_harness import evaluate_semantic_benchmark
from career_match.matching.hybrid import HybridMatcher
from career_match.matching.hybrid_config import (
    CONFIGURATION_FROZEN,
    FROZEN_ON_BENCHMARK,
    HOLDOUT_NOT_USED_FOR_TUNING,
    HYBRID_MATCHER_NAME,
    SEMANTIC_WEIGHT,
    SKILL_WEIGHT,
    TFIDF_WEIGHT,
    HybridConfig,
)
from career_match.matching.semantic import SemanticMatcher

DEV_REPORT = Path("reports") / "hybrid_matcher_v0_1_development.md"
HOLDOUT_REPORT = Path("reports") / "hybrid_matcher_v0_1_holdout.md"

V02_CASES = (
    ("job-mle", "r-mle-stuffing", "MLE keyword stuffing"),
    ("job-mle", "r-mle-synonym", "MLE synonym strong"),
    ("job-mle", "r-mle-prod", "MLE token strong"),
    ("job-backend", "r-backend-negation", "Backend negation"),
    ("job-mlops", "r-mlops-negation", "MLOps negation"),
    ("job-de", "r-de-synonym", "DE synonym"),
    ("job-fullstack", "r-da-prod", "Analyst on Full-Stack"),
)


def _fmt(value: float) -> str:
    return f"{value:.3f}"


def _delta(value: float) -> str:
    if value > 0:
        return f"+{value:.3f}"
    return f"{value:.3f}"


def _metrics_table(title: str, evaluation: BenchmarkEvaluation) -> list[str]:
    return [
        f"### {title}",
        "",
        "| Metric | Mean |",
        "| --- | ---: |",
        f"| Precision@1 | {_fmt(evaluation.mean_precision_at_1)} |",
        f"| Precision@3 | {_fmt(evaluation.mean_precision_at_3)} |",
        f"| Recall@3 | {_fmt(evaluation.mean_recall_at_3)} |",
        f"| NDCG@3 | {_fmt(evaluation.mean_ndcg_at_3)} |",
        f"| NDCG (full pool) | {_fmt(evaluation.mean_ndcg_full)} |",
        f"| Pairwise ordering accuracy | {_fmt(evaluation.mean_pairwise_accuracy)} |",
        "",
    ]


def _comparison_table(
    lexical: BenchmarkEvaluation,
    semantic: BenchmarkEvaluation,
    hybrid: BenchmarkEvaluation,
) -> list[str]:
    rows = [
        ("Precision@1", "mean_precision_at_1"),
        ("Precision@3", "mean_precision_at_3"),
        ("Recall@3", "mean_recall_at_3"),
        ("NDCG@3", "mean_ndcg_at_3"),
        ("NDCG (full pool)", "mean_ndcg_full"),
        ("Pairwise ordering accuracy", "mean_pairwise_accuracy"),
    ]
    lines = [
        "| Metric | Lexical | Semantic | Hybrid | Δ vs semantic |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for name, field in rows:
        left = float(getattr(lexical, field))
        mid = float(getattr(semantic, field))
        right = float(getattr(hybrid, field))
        lines.append(
            f"| {name} | {_fmt(left)} | {_fmt(mid)} | {_fmt(right)} | {_delta(right - mid)} |"
        )
    lines.append("")
    return lines


def _per_role(
    lexical: BenchmarkEvaluation,
    semantic: BenchmarkEvaluation,
    hybrid: BenchmarkEvaluation,
) -> list[str]:
    lines: list[str] = []
    for job in hybrid.jobs:
        lex = next(item for item in lexical.jobs if item.job_id == job.job_id)
        sem = next(item for item in semantic.jobs if item.job_id == job.job_id)
        lines.extend(
            [
                f"### {job.role} (`{job.job_id}`)",
                "",
                f"- Lexical:  P@1={lex.precision_at_1:.3f} P@3={lex.precision_at_3:.3f} "
                f"NDCG@3={lex.ndcg_at_3:.3f} pairwise={lex.pairwise_accuracy:.3f}",
                f"- Semantic: P@1={sem.precision_at_1:.3f} P@3={sem.precision_at_3:.3f} "
                f"NDCG@3={sem.ndcg_at_3:.3f} pairwise={sem.pairwise_accuracy:.3f}",
                f"- Hybrid:   P@1={job.precision_at_1:.3f} P@3={job.precision_at_3:.3f} "
                f"R@3={job.recall_at_3:.3f} NDCG@3={job.ndcg_at_3:.3f} "
                f"NDCG@full={job.ndcg_full:.3f} pairwise={job.pairwise_accuracy:.3f}",
                "",
                "| Rank | Resume | Grade | Hybrid | Lex rank | Sem rank |",
                "| ---: | --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for rank, item in enumerate(job.ranking, start=1):
            lines.append(
                f"| {rank} | `{item.resume_id}` | {item.grade} | "
                f"{item.overall_score:.1f} | "
                f"{rank_of(lexical, job.job_id, item.resume_id)} | "
                f"{rank_of(semantic, job.job_id, item.resume_id)} |"
            )
        lines.append("")
    return lines


def _case_table(
    lexical: BenchmarkEvaluation,
    semantic: BenchmarkEvaluation,
    hybrid: BenchmarkEvaluation,
    cases: tuple[tuple[str, str, str], ...],
) -> list[str]:
    lines = [
        "| Case | Lex rank | Sem rank | Hybrid rank | Hybrid score |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for job_id, resume_id, label in cases:
        pair = pair_lookup(hybrid, job_id, resume_id)
        score = f"{pair.overall_score:.1f}" if pair else "-"
        lines.append(
            f"| {label} (`{resume_id}`) | "
            f"{rank_of(lexical, job_id, resume_id)} | "
            f"{rank_of(semantic, job_id, resume_id)} | "
            f"{rank_of(hybrid, job_id, resume_id)} | {score} |"
        )
    lines.append("")
    return lines


def _grade_dist(evaluation: BenchmarkEvaluation) -> list[str]:
    lines = [
        "| Grade | N | Mean score | Min | Max |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for stats in evaluation.score_stats_by_grade:
        lines.append(
            f"| {stats.grade} | {stats.count} | {stats.mean_score:.1f} | "
            f"{stats.min_score:.1f} | {stats.max_score:.1f} |"
        )
    lines.append("")
    return lines


def render_development(
    lexical: BenchmarkEvaluation,
    semantic: BenchmarkEvaluation,
    hybrid: BenchmarkEvaluation,
    selection_path: Path,
) -> str:
    selection = selection_path.read_text(encoding="utf-8") if selection_path.exists() else "{}"
    lines = [
        "# Hybrid Matcher v0.1 — development evaluation (v0.2)",
        "",
        "Development relevance scores only. Not a hiring probability and not a",
        "production quality claim. Holdout v0.3 was **not** used to choose weights.",
        "",
        "## Frozen configuration",
        "",
        f"- Matcher: **{HYBRID_MATCHER_NAME}**",
        f"- Configuration frozen: **{CONFIGURATION_FROZEN}**",
        f"- Frozen on: `{FROZEN_ON_BENCHMARK}`",
        f"- Holdout used for tuning: **{not HOLDOUT_NOT_USED_FOR_TUNING}** "
        f"(must remain false)",
        f"- Weights: semantic={SEMANTIC_WEIGHT:.2f}, "
        f"tfidf={TFIDF_WEIGHT:.2f}, skill={SKILL_WEIGHT:.2f}",
        "- Components: MiniLM semantic cosine + pair-fit TF-IDF + evidence-aware "
        "skill coverage (negation + keyword-list discount + stuffing penalty)",
        "",
        "## Selection",
        "",
        "Candidate grid and metrics are recorded in "
        "`reports/hybrid_config_selection_v0_2.json`.",
        "",
        "Selection rule:",
        "",
        "1. Reject configs that rank MLE keyword stuffing at #1",
        "2. Maximize mean pairwise ordering accuracy",
        "3. Then maximize mean NDCG@3",
        "4. Prefer synonym ranked above stuffing",
        "",
        "```json",
        selection.strip(),
        "```",
        "",
        "## v0.2 mean metrics",
        "",
        *_comparison_table(lexical, semantic, hybrid),
        *_metrics_table("Hybrid Matcher v0.1", hybrid),
        "## Grade-level hybrid score distribution",
        "",
        *_grade_dist(hybrid),
        "## Known hard-case rankings (v0.2)",
        "",
        *_case_table(lexical, semantic, hybrid, V02_CASES),
        "## Per-role hybrid results",
        "",
        *_per_role(lexical, semantic, hybrid),
        "## Negation and stuffing behavior",
        "",
        "- Narrative negation phrases (for example `No production Docker`, "
        "`Limited exposure to Kubernetes`) zero out that skill for coverage "
        "even when it still appears in a Skills list.",
        "- Skills that appear only under a `Skills:` heading receive weight 0.45.",
        "- Resumes with ≥16 distinct catalog skills are treated as stuffing-likely: "
        "skill channel ×0.25 and overall score ×0.72.",
        "",
        "## Regressions and honesty notes",
        "",
        "- Hybrid may still leave backend/MLOps negation mid-ranked when prose "
        "overlaps the job family.",
        "- Synonym recovery is incomplete; lexical channels still dilute pure "
        "embedding synonym wins on some roles.",
        "- Beating semantic on every metric is not required; the goal is better "
        "overall ordering with improved stuffing failure behavior.",
        "",
        "Generated by `scripts/evaluate_hybrid.py --development`.",
        "",
    ]
    return "\n".join(lines)


def render_holdout(
    lexical: BenchmarkEvaluation,
    semantic: BenchmarkEvaluation,
    hybrid: BenchmarkEvaluation,
    checksum: str,
) -> str:
    improvements: list[str] = []
    regressions: list[str] = []
    fields = (
        ("Precision@1", "mean_precision_at_1"),
        ("Precision@3", "mean_precision_at_3"),
        ("Recall@3", "mean_recall_at_3"),
        ("NDCG@3", "mean_ndcg_at_3"),
        ("NDCG (full pool)", "mean_ndcg_full"),
        ("Pairwise", "mean_pairwise_accuracy"),
    )
    for name, field in fields:
        delta = float(getattr(hybrid, field)) - float(getattr(semantic, field))
        if delta > 1e-9:
            improvements.append(f"- {name}: {_delta(delta)} vs semantic")
        elif delta < -1e-9:
            regressions.append(f"- {name}: {_delta(delta)} vs semantic")
    for job in hybrid.jobs:
        sem = next(item for item in semantic.jobs if item.job_id == job.job_id)
        if job.pairwise_accuracy + 1e-9 < sem.pairwise_accuracy:
            regressions.append(
                f"- {job.role} pairwise: {sem.pairwise_accuracy:.3f} → "
                f"{job.pairwise_accuracy:.3f}"
            )
        if job.ndcg_at_3 + 1e-9 < sem.ndcg_at_3:
            regressions.append(
                f"- {job.role} NDCG@3: {sem.ndcg_at_3:.3f} → {job.ndcg_at_3:.3f}"
            )
    if not improvements:
        improvements.append("- No mean metric improved vs semantic on this holdout.")
    if not regressions:
        regressions.append("- No mean/per-role NDCG@3 or pairwise regression vs semantic recorded.")

    lines = [
        "# Hybrid Matcher v0.1 — frozen holdout evaluation (v0.3)",
        "",
        "Single holdout snapshot after configuration freeze on v0.2.",
        "Not a production hiring claim. Synthetic benchmark only.",
        "",
        "## Frozen configuration",
        "",
        f"- Matcher: **{HYBRID_MATCHER_NAME}**",
        f"- Weights: semantic={SEMANTIC_WEIGHT:.2f}, "
        f"tfidf={TFIDF_WEIGHT:.2f}, skill={SKILL_WEIGHT:.2f}",
        f"- Configuration frozen before this run: **{CONFIGURATION_FROZEN}**",
        f"- Tuned on: `{FROZEN_ON_BENCHMARK}` only",
        "- **v0.3 was not used for tuning**",
        "- Weights, negation rules, and evidence rules were not changed after "
        "seeing these holdout numbers",
        "",
        "## Holdout identity",
        "",
        f"- Name: `{hybrid.benchmark_name}`",
        f"- Kind: {hybrid.benchmark_kind}",
        f"- Jobs: {hybrid.job_count}; resumes: {hybrid.resume_count}; "
        f"judgments: {hybrid.pair_count}",
        f"- SHA-256: `{checksum}`",
        f"- Matches manifest: **{checksum == expected_holdout_checksum()}**",
        "",
        "## Mean metrics (v0.3)",
        "",
        *_comparison_table(lexical, semantic, hybrid),
        "## Per-role results",
        "",
        *_per_role(lexical, semantic, hybrid),
        "## Improvements vs semantic",
        "",
        *improvements,
        "",
        "## Regressions vs semantic",
        "",
        *regressions,
        "",
        "## Interpretation",
        "",
        "Hybrid Matcher v0.1 mixes semantic similarity with TF-IDF and "
        "evidence-aware skill coverage. On this frozen holdout it should be "
        "read as a controlled comparison, not a production readiness claim.",
        "Winning every metric is not required.",
        "",
        "## Limitations",
        "",
        "- Negation rules are phrase-window heuristics, not full linguistic negation",
        "- Stuffing detection uses catalog-skill count thresholds",
        "- MiniLM still confuses adjacent role families",
        "- Synthetic labels are not independently validated ground truth",
        "",
        "Generated by `scripts/evaluate_hybrid.py --holdout`.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--development", action="store_true", help="Write v0.2 report.")
    parser.add_argument("--holdout", action="store_true", help="Write v0.3 report once.")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run development then holdout (holdout after freeze only).",
    )
    args = parser.parse_args()
    if not (args.development or args.holdout or args.all):
        args.all = True

    config = HybridConfig()
    assert abs(config.semantic_weight + config.tfidf_weight + config.skill_weight - 1.0) < 1e-9
    semantic_matcher = SemanticMatcher()
    _ = semantic_matcher.encoder
    hybrid_matcher = HybridMatcher(config=config, semantic_matcher=semantic_matcher)

    if args.development or args.all:
        lexical = evaluate_benchmark_v0_2()
        semantic = evaluate_semantic_benchmark(matcher=semantic_matcher)
        hybrid = evaluate_hybrid_benchmark(matcher=hybrid_matcher)
        report = render_development(
            lexical,
            semantic,
            hybrid,
            Path("reports") / "hybrid_config_selection_v0_2.json",
        )
        DEV_REPORT.write_text(report, encoding="utf-8")
        print(f"Wrote {DEV_REPORT}")
        print(
            "v0.2 hybrid pairwise="
            f"{hybrid.mean_pairwise_accuracy:.3f} NDCG@3={hybrid.mean_ndcg_at_3:.3f}"
        )

    if args.holdout or args.all:
        if not CONFIGURATION_FROZEN:
            raise SystemExit("Refuse holdout eval until CONFIGURATION_FROZEN is True.")
        checksum_before = compute_holdout_checksum()
        holdout = load_holdout_benchmark()
        lexical_h = evaluate_benchmark_v0_2(benchmark=holdout)
        semantic_h = evaluate_semantic_benchmark(
            matcher=semantic_matcher,
            benchmark=holdout,
        )
        hybrid_h = evaluate_hybrid_benchmark(matcher=hybrid_matcher, benchmark=holdout)
        checksum_after = compute_holdout_checksum()
        if checksum_after != checksum_before:
            raise SystemExit("Holdout checksum changed during evaluation.")
        report = render_holdout(lexical_h, semantic_h, hybrid_h, checksum_before)
        HOLDOUT_REPORT.write_text(report, encoding="utf-8")
        print(f"Wrote {HOLDOUT_REPORT}")
        print(
            "v0.3 hybrid pairwise="
            f"{hybrid_h.mean_pairwise_accuracy:.3f} NDCG@3={hybrid_h.mean_ndcg_at_3:.3f}"
        )


if __name__ == "__main__":
    main()
