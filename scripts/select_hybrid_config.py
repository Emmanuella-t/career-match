#!/usr/bin/env python3
"""Select Hybrid Matcher v0.1 weights on development benchmark v0.2 only.

Does not read or tune against holdout v0.3. Writes the chosen weights into
hybrid_config.py constants and a selection JSON under reports/.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from career_match.evaluation.benchmark_harness import evaluate_benchmark_v0_2
from career_match.evaluation.compare import rank_of
from career_match.evaluation.hybrid_harness import evaluate_hybrid_benchmark
from career_match.evaluation.semantic_harness import evaluate_semantic_benchmark
from career_match.matching.hybrid import HybridMatcher
from career_match.matching.hybrid_config import HybridConfig
from career_match.matching.semantic import SemanticMatcher

REPORT_JSON = Path("reports") / "hybrid_config_selection_v0_2.json"
HARD_CASES = (
    ("job-mle", "r-mle-stuffing", "stuffing"),
    ("job-mle", "r-mle-synonym", "synonym"),
    ("job-mle", "r-mle-prod", "strong"),
    ("job-backend", "r-backend-negation", "backend_negation"),
    ("job-mlops", "r-mlops-negation", "mlops_negation"),
    ("job-de", "r-de-synonym", "de_synonym"),
    ("job-fullstack", "r-da-prod", "related_role"),
)

# Modest grid: semantic-leaning mixes that still keep lexical/skill channels.
CANDIDATE_WEIGHTS: tuple[tuple[float, float, float], ...] = (
    (0.60, 0.20, 0.20),
    (0.55, 0.25, 0.20),
    (0.50, 0.30, 0.20),
    (0.50, 0.25, 0.25),
    (0.45, 0.30, 0.25),
    (0.45, 0.25, 0.30),
    (0.40, 0.35, 0.25),
    (0.40, 0.30, 0.30),
)


@dataclass(frozen=True)
class CandidateResult:
    label: str
    semantic_weight: float
    tfidf_weight: float
    skill_weight: float
    mean_pairwise_accuracy: float
    mean_ndcg_at_3: float
    mean_precision_at_1: float
    mean_precision_at_3: float
    mean_recall_at_3: float
    mean_ndcg_full: float
    stuffing_rank: int | None
    synonym_rank: int | None
    backend_negation_rank: int | None
    mlops_negation_rank: int | None
    rejected: bool
    reject_reasons: tuple[str, ...]


def _case_ranks(evaluation) -> dict[str, int | None]:
    ranks: dict[str, int | None] = {}
    for job_id, resume_id, key in HARD_CASES:
        ranks[key] = rank_of(evaluation, job_id, resume_id)
    return ranks


def evaluate_candidate(
    weights: tuple[float, float, float],
    semantic_matcher: SemanticMatcher,
) -> CandidateResult:
    config = HybridConfig(
        semantic_weight=weights[0],
        tfidf_weight=weights[1],
        skill_weight=weights[2],
    )
    matcher = HybridMatcher(config=config, semantic_matcher=semantic_matcher)
    evaluation = evaluate_hybrid_benchmark(matcher=matcher)
    ranks = _case_ranks(evaluation)
    reasons: list[str] = []
    stuffing = ranks["stuffing"]
    synonym = ranks["synonym"]
    if stuffing is not None and stuffing == 1:
        reasons.append("MLE stuffing ranked #1")
    return CandidateResult(
        label=config.label,
        semantic_weight=weights[0],
        tfidf_weight=weights[1],
        skill_weight=weights[2],
        mean_pairwise_accuracy=evaluation.mean_pairwise_accuracy,
        mean_ndcg_at_3=evaluation.mean_ndcg_at_3,
        mean_precision_at_1=evaluation.mean_precision_at_1,
        mean_precision_at_3=evaluation.mean_precision_at_3,
        mean_recall_at_3=evaluation.mean_recall_at_3,
        mean_ndcg_full=evaluation.mean_ndcg_full,
        stuffing_rank=stuffing,
        synonym_rank=synonym,
        backend_negation_rank=ranks["backend_negation"],
        mlops_negation_rank=ranks["mlops_negation"],
        rejected=bool(reasons),
        reject_reasons=tuple(reasons),
    )


def select_best(candidates: list[CandidateResult]) -> CandidateResult:
    """Primary: pairwise. Secondary: NDCG@3. Prefer synonym above stuffing."""

    def sort_key(item: CandidateResult) -> tuple:
        stuffing = item.stuffing_rank if item.stuffing_rank is not None else 99
        synonym = item.synonym_rank if item.synonym_rank is not None else 99
        synonym_beats_stuffing = 1 if synonym < stuffing else 0
        return (
            item.mean_pairwise_accuracy,
            item.mean_ndcg_at_3,
            synonym_beats_stuffing,
            -stuffing,
            -synonym,
            item.mean_precision_at_3,
        )

    eligible = [item for item in candidates if not item.rejected]
    pool = eligible if eligible else candidates
    return max(pool, key=sort_key)


def freeze_config_in_module(chosen: CandidateResult) -> None:
    path = Path("src/career_match/matching/hybrid_config.py")
    text = path.read_text(encoding="utf-8")
    replacements = {
        "SEMANTIC_WEIGHT": chosen.semantic_weight,
        "TFIDF_WEIGHT": chosen.tfidf_weight,
        "SKILL_WEIGHT": chosen.skill_weight,
    }
    for name, value in replacements.items():
        text = re.sub(
            rf"^{name} = .*",
            f"{name} = {value:.2f}",
            text,
            count=1,
            flags=re.MULTILINE,
        )
    text = re.sub(
        r"^CONFIGURATION_FROZEN = .*",
        "CONFIGURATION_FROZEN = True",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--freeze",
        action="store_true",
        help="Write chosen weights into hybrid_config.py.",
    )
    args = parser.parse_args()

    print("Loading baselines on v0.2 (reference, not for hybrid tuning)...")
    lexical = evaluate_benchmark_v0_2()
    semantic_matcher = SemanticMatcher()
    _ = semantic_matcher.encoder
    semantic = evaluate_semantic_benchmark(matcher=semantic_matcher)

    print("Evaluating hybrid candidates on v0.2 only...")
    candidates = [evaluate_candidate(weights, semantic_matcher) for weights in CANDIDATE_WEIGHTS]
    chosen = select_best(candidates)

    payload = {
        "benchmark": "career-match-dev-benchmark-v0.2",
        "holdout_used_for_tuning": False,
        "selection_rule": (
            "Reject candidates that rank MLE keyword stuffing at #1. Among the "
            "rest: maximize mean pairwise ordering accuracy, then mean NDCG@3, "
            "then prefer synonym ranked above stuffing, then lower stuffing rank."
        ),
        "reference": {
            "lexical": {
                "pairwise": lexical.mean_pairwise_accuracy,
                "ndcg_at_3": lexical.mean_ndcg_at_3,
                "precision_at_1": lexical.mean_precision_at_1,
            },
            "semantic": {
                "pairwise": semantic.mean_pairwise_accuracy,
                "ndcg_at_3": semantic.mean_ndcg_at_3,
                "precision_at_1": semantic.mean_precision_at_1,
            },
        },
        "candidates": [asdict(item) for item in candidates],
        "chosen": asdict(chosen),
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["chosen"], indent=2))
    print(f"Wrote {REPORT_JSON}")

    if args.freeze:
        freeze_config_in_module(chosen)
        print(
            "Froze hybrid_config.py weights: "
            f"sem={chosen.semantic_weight:.2f} "
            f"tfidf={chosen.tfidf_weight:.2f} "
            f"skill={chosen.skill_weight:.2f}"
        )


if __name__ == "__main__":
    main()
