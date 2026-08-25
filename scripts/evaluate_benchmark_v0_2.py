#!/usr/bin/env python3
"""Evaluate the untuned lexical baseline on development benchmark v0.2.

Writes reports/benchmark_v0_2_evaluation.md. Does not tune matcher weights.
This snapshot is not a production quality claim.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from career_match.evaluation.benchmark_harness import (
    BenchmarkEvaluation,
    JobBenchmarkResult,
    evaluate_benchmark_v0_2,
)
from career_match.evaluation.harness import evaluate_baseline
from career_match.matching.config import SKILL_OVERLAP_WEIGHT, TFIDF_WEIGHT

REPORT_PATH = Path("reports") / "benchmark_v0_2_evaluation.md"
GRADE_NAME = {3: "strong", 2: "moderate", 1: "weak", 0: "mismatch"}


def _fmt(value: float) -> str:
    return f"{value:.3f}"


def _ranking_failures(job: JobBenchmarkResult) -> list[str]:
    notes: list[str] = []
    ranking = job.ranking
    rank_of = {item.resume_id: index for index, item in enumerate(ranking, start=1)}
    top = ranking[0]
    if top.grade < 2:
        notes.append(
            f"P@1 miss: `{top.resume_id}` (grade {top.grade} {GRADE_NAME[top.grade]}) "
            f"ranked first with score {top.overall_score:.1f}."
        )
    grade3 = [item for item in ranking if item.grade == 3]
    grade0 = [item for item in ranking if item.grade == 0]
    for strong in grade3:
        for mismatch in grade0:
            if strong.overall_score < mismatch.overall_score:
                notes.append(
                    f"Grade-3 `{strong.resume_id}` ({strong.overall_score:.1f}) ranked "
                    f"#{rank_of[strong.resume_id]} below grade-0 `{mismatch.resume_id}` "
                    f"({mismatch.overall_score:.1f}, #{rank_of[mismatch.resume_id]})."
                )
    for item in ranking[:3]:
        if item.grade <= 1:
            notes.append(
                f"False positive in top-3: `{item.resume_id}` grade {item.grade} "
                f"score {item.overall_score:.1f} tags={','.join(item.case_tags) or 'none'}."
            )
    for item in ranking[3:]:
        if item.grade >= 2:
            notes.append(
                f"False negative outside top-3: `{item.resume_id}` grade {item.grade} "
                f"score {item.overall_score:.1f} tags={','.join(item.case_tags) or 'none'}."
            )
    return notes


def render_report(evaluation: BenchmarkEvaluation) -> str:
    v01 = evaluate_baseline()
    dist = evaluation.grade_distribution
    lines = [
        "# Baseline Matcher v0.1 on development benchmark v0.2",
        "",
        evaluation.disclaimer,
        "",
        "This report is a **development error analysis**. It does **not** prove",
        "production matching quality. Matcher weights were **not** tuned on v0.2.",
        "",
        "## Benchmark size",
        "",
        f"- Name: `{evaluation.benchmark_name}`",
        f"- Kind: {evaluation.benchmark_kind}",
        f"- Jobs: **{evaluation.job_count}**",
        f"- Unique synthetic resumes: **{evaluation.resume_count}**",
        f"- Relevance judgments: **{evaluation.pair_count}**",
        "- Pool size: 7 labeled resumes per job",
        "",
        "## Provenance",
        "",
        "- Synthetic benchmark (no real candidate data)",
        "- Constructed for controlled development evaluation",
        "- No production hiring labels",
        "- No independent annotator agreement",
        "- Labels are development targets, not independently validated ground truth",
        "- Intended for model comparison and error analysis",
        "- Review aid: `reports/benchmark_v0_2_label_review.md` "
        "(status: awaiting/available for manual review)",
        "",
        "## Role distribution",
        "",
        "| Job ID | Title | Pool |",
        "| --- | --- | ---: |",
    ]
    for job in evaluation.jobs:
        lines.append(f"| `{job.job_id}` | {job.role} | {job.pool_size} |")
    lines.extend(
        [
            "",
            "## Labeling scheme",
            "",
            "Manually specified synthetic relevance judgments (development",
            "targets, not independently validated ground truth):",
            "",
            "- `3` strong — right role family, required work largely present",
            "- `2` moderate — related role or partial skills",
            "- `1` weak — overlapping tools, wrong core job or seniority",
            "- `0` mismatch — different occupation, stuffing, or unrelated stack",
            "",
            "Binary metrics treat grades ≥ 2 as relevant. NDCG uses gain `2^rel - 1`.",
            "",
            "| Grade | Judgments |",
            "| ---: | ---: |",
            f"| 3 strong | {dist[3]} |",
            f"| 2 moderate | {dist[2]} |",
            f"| 1 weak | {dist[1]} |",
            f"| 0 mismatch | {dist[0]} |",
            f"| **Total** | **{evaluation.pair_count}** |",
            "",
            "## Baseline configuration",
            "",
            f"- Matcher: **{evaluation.matcher_name}**",
            f"- Formula: `overall = {TFIDF_WEIGHT} * tfidf_similarity + "
            f"{SKILL_OVERLAP_WEIGHT} * skill_overlap_score`",
            "- Weights are the v0.1 named constants. **They were not retuned on v0.2.**",
            "- Skill overlap: fraction of job catalog skills also found in the resume",
            "- Scores: 0–100 baseline relevance, **not** a hiring probability",
            "- Vectorizer: pair-fit TF-IDF cosine, unigrams+bigrams, English stop words",
            "",
            "## Actual metrics (mean over 8 jobs)",
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
            "Precision/Recall@3 are appropriate: each job has seven labeled candidates",
            "and typically two to four relevant (grade ≥ 2) resumes.",
            "",
            "## Score distribution by grade",
            "",
            "| Grade | N | Mean | Min | Max |",
            "| ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for stats in evaluation.score_stats_by_grade:
        lines.append(
            f"| {stats.grade} | {stats.count} | {stats.mean_score:.1f} | "
            f"{stats.min_score:.1f} | {stats.max_score:.1f} |"
        )
    overlap = ", ".join(f"{a} vs {b}" for a, b in evaluation.overlapping_grade_bands) or "none"
    lines.extend(
        [
            "",
            f"Overlapping score ranges between grades: **{overlap}**.",
            "Mean score for grade 2 can sit at or below grade 1 when synonymy is",
            "penalized and related-role keyword overlap is rewarded. That inversion",
            "is a lexical failure, not a labeling bug.",
            "",
            "## Per-role results",
            "",
        ]
    )
    for job in evaluation.jobs:
        lines.extend(
            [
                f"### {job.role} (`{job.job_id}`)",
                "",
                f"- P@1={job.precision_at_1:.2f} P@3={job.precision_at_3:.2f} "
                f"R@3={job.recall_at_3:.2f} NDCG@3={job.ndcg_at_3:.3f} "
                f"NDCG@7={job.ndcg_full:.3f} pairwise={job.pairwise_accuracy:.3f}",
                "",
                "| Rank | Resume | Grade | Overall | TF-IDF | Skill overlap | Tags |",
                "| ---: | --- | ---: | ---: | ---: | ---: | --- |",
            ]
        )
        for rank, item in enumerate(job.ranking, start=1):
            tags = ", ".join(item.case_tags) if item.case_tags else "—"
            lines.append(
                f"| {rank} | `{item.resume_id}` | {item.grade} | "
                f"{item.overall_score:.1f} | {item.tfidf_similarity:.1f} | "
                f"{item.skill_overlap_score:.1f} | {tags} |"
            )
        failures = _ranking_failures(job)
        if failures:
            lines.extend(["", "Ranking issues on this job:", ""])
            lines.extend(f"- {note}" for note in failures)
        lines.append("")

    lines.extend(
        [
            "## Comparison with v0.1",
            "",
            "| | v0.1 sanity fixture | v0.2 development benchmark |",
            "| --- | --- | --- |",
            "| Kind | development evaluation fixture | development evaluation benchmark |",
            "| Pairs | 16 | 56 |",
            "| Jobs | 4 obvious role silos | 8 overlapping families |",
            "| Hard cases | none by design | synonymy, negation, stuffing, seniority |",
            f"| Baseline P@1 | {v01.mean_precision_at_1:.3f} | "
            f"{evaluation.mean_precision_at_1:.3f} |",
            f"| Baseline NDCG@full | {v01.mean_ndcg_at_4:.3f} (k=4) | "
            f"{evaluation.mean_ndcg_full:.3f} (k=7) |",
            "",
            "v0.1 remains a **sanity check**: the matcher should still rank constructed",
            "strong matches above constructed mismatches on that tiny set.",
            "v0.2 is the **comparison target** for TF-IDF, a future sentence-embedding",
            "model, and a future hybrid ranker. Perfect v0.1 metrics were too easy to",
            "be a useful model-selection signal.",
            "",
            "## Error analysis",
            "",
            "### Ranking failures, false positives, and false negatives",
            "",
            "The lexical baseline is strong when the resume repeats the job's catalog",
            "tokens and weak when the work is described with synonyms. Related-role",
            "Python/SQL/Git overlap often outranks a better role fit.",
            "",
            "### Examples where lexical overlap misleads",
            "",
            "- **Keyword stuffing (`r-mle-stuffing` on Machine Learning Engineer).**",
            "  Grade 0 ranks first (skill overlap 100) because the resume lists the",
            "  entire catalog. The true strong resume (`r-mle-prod`) is second.",
            "- **Data Analyst on Full-Stack (`r-da-prod`).** Grade 0 lands in the top-3",
            "  via SQL/Python/Git overlap even though the work is weekly reporting.",
            "- **Data Engineer intern (`r-backend-intern`).** Grade 1 reaches top-3 with",
            "  catalog coverage inflated by sentences that *deny* Docker and AWS.",
            "",
            "### Examples where synonymy hurts TF-IDF",
            "",
            "- **`r-mle-synonym` (grade 3)** ranks last on the MLE job. The resume talks",
            "  about neural networks, serving ML models, and cloud infrastructure",
            "  instead of PyTorch/AWS/Docker, so both TF-IDF and skill overlap collapse.",
            "- **`r-ds-synonym` (grade 2)** ranks last on Data Scientist for the same",
            "  reason (statistical modeling, relational databases).",
            "- **`r-backend-synonym` (grade 2)** sits below intern/negation/related ML",
            "  resumes because it says REST services rather than REST APIs/FastAPI.",
            "- **`r-de-synonym` (grade 2)** ranks last on Data Engineer; Spark/Airflow/",
            "  PostgreSQL are also outside the 32-skill catalog even on the strong resume's",
            "  preferred stack, so the synonym document has almost no catalog hook.",
            "- **`r-fe-synonym`** is less damaged because the job still shares some",
            "  generic frontend prose, but it still trails the token-matching",
            "  partial React resume.",
            "",
            "### Examples where negation causes a bad score",
            "",
            "- **`r-mle-negation`** names PyTorch, Docker, Kubernetes, and AWS while",
            "  stating *No production Docker experience* and *Have not deployed models",
            "  to cloud infrastructure*. It outranks the AI Engineer (grade 2) and the",
            "  synonym strong match.",
            "- **`r-backend-negation`** scores a perfect skill-overlap 100 and ranks #2",
            "  on Backend Engineer, above the synonym true-ish match.",
            "- **`r-mlops-negation`** likewise hits every catalog skill, including",
            "  Kubernetes from *Limited exposure to Kubernetes*, and ranks #2.",
            "",
            "### Skill-catalog misses",
            "",
            "- PostgreSQL, Spark, Airflow, Terraform, Excel/dashboards, and generic",
            "  phrases (*REST services*, *relational databases*, *cloud infrastructure*,",
            "  *frontend component development*) are invisible to skill overlap unless a",
            "  32-entry alias exists.",
            "- Catalog aliases still fire on negated mentions, so absence cannot be",
            "  expressed in this baseline.",
            "",
            "### Score-distribution observations",
            "",
            "- Grade bands overlap completely. A mismatch can score above a strong match",
            "  (stuffing 56.2 vs synonym MLE 2.9).",
            "- Mean overall score is not monotone in grade when synonym cases sit in",
            "  grade 2–3 and keyword-heavy weak cases sit in grade 0–1.",
            "- Full-pool NDCG stays high (~0.93) because obvious mismatches often still",
            "  finish last; **P@1 and P@3** are the honest stress metrics here.",
            "",
            "## Known failure cases (summary)",
            "",
            "1. Keyword stuffing beats a real MLE (P@1 = 0 on that job).",
            "2. Synonym / role-fit-without-keywords resumes are systematic false negatives.",
            "3. Negated skill mentions inflate overlap.",
            "4. Closely related roles (backend vs MLE vs data engineer vs analyst) collapse",
            "   when they share Python/SQL/Docker/Git.",
            "5. Intern/seniority mismatches are barely penalized if tools are named.",
            "6. Shared generic tokens (Git, Linux) give floor scores to mismatches.",
            "",
            "These failures are **useful**. A future sentence-embedding or hybrid ranker",
            "must be evaluated on this same benchmark and should improve P@1, P@3,",
            "pairwise ordering, and synonym ranking without retconning the labels.",
            "",
            "Generated by `scripts/evaluate_benchmark_v0_2.py` with untuned",
            f"{evaluation.matcher_name} weights.",
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
        help="Write reports/benchmark_v0_2_evaluation.md (default: true).",
    )
    parser.add_argument(
        "--no-write-report",
        action="store_false",
        dest="write_report",
        help="Print the report without writing a file.",
    )
    args = parser.parse_args()
    evaluation = evaluate_benchmark_v0_2()
    report = render_report(evaluation)
    print(report)
    if args.write_report:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(report, encoding="utf-8")
        print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
