"""Named configuration for Baseline Matcher v0.1.

Weights are provisional. They are not tuned on labeled resume-to-job data
and must be easy to change when a later model is compared on the same
evaluation fixture.
"""

from __future__ import annotations

from dataclasses import dataclass

# Slight emphasis on TF-IDF so overlapping technical prose still scores when
# the skill catalog misses a token. Skill overlap remains a large, inspectable
# share of the score because recruiters read named skills first.
#
# These weights are a starting point for comparison, not an optimized fit.
TFIDF_WEIGHT = 0.55
SKILL_OVERLAP_WEIGHT = 0.45

SCORE_SCALE = 100.0
MATCHER_NAME = "Baseline Matcher v0.1"
MATCHER_VERSION = "0.1.0"


@dataclass(frozen=True)
class BaselineConfig:
    """Hybrid score configuration.

    ``overall_score = tfidf_weight * tfidf_similarity
                     + skill_overlap_weight * skill_overlap_score``

    when the job text contains at least one catalog skill. If the job text
    has zero catalog skills, the skill channel is skipped and the overall
    score equals TF-IDF similarity. Weights should sum to 1.0.
    """

    tfidf_weight: float = TFIDF_WEIGHT
    skill_overlap_weight: float = SKILL_OVERLAP_WEIGHT
    score_scale: float = SCORE_SCALE

    def __post_init__(self) -> None:
        total = self.tfidf_weight + self.skill_overlap_weight
        if abs(total - 1.0) > 1e-9:
            raise ValueError(
                f"tfidf_weight + skill_overlap_weight must equal 1.0, got {total}."
            )
        if self.score_scale <= 0:
            raise ValueError("score_scale must be positive.")
