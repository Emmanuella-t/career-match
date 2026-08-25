"""Named configuration for Hybrid Matcher v0.1.

Weights are selected on development benchmark v0.2 only. They must not be
retuned against frozen holdout benchmark v0.3.
"""

from __future__ import annotations

from dataclasses import dataclass

# Provisional defaults used before selection. The frozen chosen weights are
# written into CHOSEN_* after the v0.2 grid search and must stay fixed for
# holdout evaluation.
SEMANTIC_WEIGHT = 0.60
TFIDF_WEIGHT = 0.20
SKILL_WEIGHT = 0.20

SCORE_SCALE = 100.0
HYBRID_MATCHER_NAME = "Hybrid Matcher v0.1"
HYBRID_MATCHER_VERSION = "0.1.0"

# Set True only after the development selection script freezes a config.
CONFIGURATION_FROZEN = True
FROZEN_ON_BENCHMARK = "career-match-dev-benchmark-v0.2"
HOLDOUT_NOT_USED_FOR_TUNING = True


@dataclass(frozen=True)
class HybridConfig:
    """Weighted mix of semantic, TF-IDF, and evidence-aware skill coverage.

    ``overall = semantic_weight * semantic
              + tfidf_weight * tfidf
              + skill_weight * evidence_skill``

    when the job text has catalog skills. If the job has zero catalog skills,
    the skill weight is redistributed proportionally to semantic and TF-IDF.
    Weights must sum to 1.0. Scores are relevance values on 0–100, not hiring
    probabilities.
    """

    semantic_weight: float = SEMANTIC_WEIGHT
    tfidf_weight: float = TFIDF_WEIGHT
    skill_weight: float = SKILL_WEIGHT
    score_scale: float = SCORE_SCALE

    def __post_init__(self) -> None:
        total = self.semantic_weight + self.tfidf_weight + self.skill_weight
        if abs(total - 1.0) > 1e-9:
            raise ValueError(
                "semantic_weight + tfidf_weight + skill_weight must equal 1.0, "
                f"got {total}."
            )
        for name, value in (
            ("semantic_weight", self.semantic_weight),
            ("tfidf_weight", self.tfidf_weight),
            ("skill_weight", self.skill_weight),
        ):
            if value < 0:
                raise ValueError(f"{name} must be non-negative.")
        if self.score_scale <= 0:
            raise ValueError("score_scale must be positive.")

    @property
    def label(self) -> str:
        return (
            f"sem={self.semantic_weight:.2f},"
            f"tfidf={self.tfidf_weight:.2f},"
            f"skill={self.skill_weight:.2f}"
        )
