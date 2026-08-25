#!/usr/bin/env python3
"""Evaluate Baseline Matcher v0.1 on the development fixture and write a report.

The report is a development snapshot. It does not claim production performance.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from career_match.evaluation.harness import BaselineEvaluation, evaluate_baseline
from career_match.matching.config import MATCHER_NAME, SKILL_OVERLAP_WEIGHT, TFIDF_WEIGHT

REPORT_PATH = Path("reports") / "baseline_evaluation.md"


def render_report(evaluation: BaselineEvaluation) -> str:
    lines = [
        "# Baseline Matcher v0.1 — development evaluation",
        "",
        evaluation.disclaimer,
        "",
        "This snapshot supports future model comparison on the **same** fixture.",
        "It does **not** prove production matching quality.",
        "",
        "## Baseline configuration",
        "",
        f"- Matcher: **{evaluation.matcher_name}**",
        f"- Formula: `overall = {TFIDF_WEIGHT} * tfidf_similarity + "
        f"{SKILL_OVERLAP_WEIGHT} * skill_overlap_score`",
        "- Skill overlap: fraction of **job** catalog skills also found in the resume",
        "- If a job text has zero catalog skills, overall score equals TF-IDF",
        "- Scores: 0–100 baseline relevance, **not** hiring probability",
        "- Vectorizer: TF-IDF cosine similarity, unigrams+bigrams, English stop words,",
        "  technical tokenizer that keeps `C++`, `C#`, `.NET`",
        f"- Fixture: `{evaluation.fixture_name}` ({evaluation.fixture_kind})",
        f"- Pairs: **{evaluation.pair_count}** across **{evaluation.query_count}** roles",
        "",
        "## Ranking checks",
        "",
        "Required on every role: strong score > moderate score, and moderate score",
        "> mismatch score.",
        "",
        f"- All ranking checks passed: **{evaluation.ranking_checks_passed}**",
        "",
        "## Mean ranking metrics",
        "",
        "Binary metrics treat relevance ≥ 2 (strong or moderate) as relevant.",
        "NDCG uses graded gain `2^rel - 1`. Means are unweighted across roles.",
        "",
        "| Metric | Mean |",
        "| --- | ---: |",
        f"| Precision@1 | {evaluation.mean_precision_at_1:.3f} |",
        f"| Precision@2 | {evaluation.mean_precision_at_2:.3f} |",
        f"| Recall@2 | {evaluation.mean_recall_at_2:.3f} |",
        f"| NDCG@2 | {evaluation.mean_ndcg_at_2:.3f} |",
        f"| NDCG@4 | {evaluation.mean_ndcg_at_4:.3f} |",
        "",
        "## Per-role ranking",
        "",
    ]
    for query in evaluation.queries:
        lines.extend(
            [
                f"### {query.role} (`{query.query_id}`)",
                "",
                f"- strong > moderate: {query.strong_above_moderate}",
                f"- moderate > mismatch: {query.moderate_above_mismatch}",
                f"- P@1={query.precision_at_1:.2f} P@2={query.precision_at_2:.2f} "
                f"R@2={query.recall_at_2:.2f} NDCG@2={query.ndcg_at_2:.3f} "
                f"NDCG@4={query.ndcg_at_4:.3f}",
                "",
                "| Rank | Candidate | Label | Overall | TF-IDF | Skill overlap |",
                "| ---: | --- | --- | ---: | ---: | ---: |",
            ]
        )
        for rank, item in enumerate(query.ranking, start=1):
            lines.append(
                f"| {rank} | `{item.candidate_id}` | {item.label} | "
                f"{item.overall_score:.1f} | {item.tfidf_similarity:.1f} | "
                f"{item.skill_overlap_score:.1f} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Correct behavior (examples)",
            "",
            "On this fixture the matcher is expected to:",
            "",
            "- Put the strong Machine Learning Engineer resume above the frontend mismatch",
            "- Cover FastAPI/Django/SQL/Docker on the strong backend resume",
            "- Keep C++ / Kubernetes systems resumes last on frontend and data-science roles",
            "",
            "## Weak or failing behavior",
            "",
            "Known limitations observed or expected with this design:",
            "",
            "- Catalog misses skills that are not in the 32-entry lexicon (for example Kafka).",
            "- `js` as a JavaScript alias can theoretically over-match short tokens;",
            "  the extractor still uses word boundaries for alphanumeric surfaces.",
            "- TF-IDF is fit on the pair only, so rare shared phrases get high weight.",
            "- Weak matches can sit close to moderate matches when both share Python/SQL.",
            "- Mention-based extraction treats negated skills as hits "
            "(`No JavaScript`, `No ... Docker`).",
            "- Job descriptions with no catalog skills ignore the skill channel.",
            "- English stop-word removal can drop domain words that happen to be stop words.",
            "",
            "## Limitations",
            "",
            f"- {evaluation.disclaimer}",
            "- Sixteen synthetic pairs cannot represent a hiring funnel.",
            "- No fairness audit, no calibration, no human rater agreement.",
            "- Future embedding or LLM rankers must beat this baseline on the same harness",
            "  before they replace it.",
            "",
            f"Generated by `scripts/evaluate_baseline.py` for {MATCHER_NAME}.",
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
        help="Write reports/baseline_evaluation.md (default: true).",
    )
    parser.add_argument(
        "--no-write-report",
        action="store_false",
        dest="write_report",
        help="Print the report without writing a file.",
    )
    args = parser.parse_args()
    evaluation = evaluate_baseline()
    report = render_report(evaluation)
    print(report)
    if args.write_report:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(report, encoding="utf-8")
        print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
