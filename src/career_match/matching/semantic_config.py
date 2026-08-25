"""Configuration for Semantic Matcher v0.1.

This matcher is independent of the lexical TF-IDF + skill-overlap baseline.
Do not combine the two scores here.
"""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
SEMANTIC_MATCHER_NAME = "Semantic Matcher v0.1"
SEMANTIC_MATCHER_VERSION = "0.1.0"
SCORE_SCALE = 100.0
DEFAULT_DEVICE = "cpu"


@dataclass(frozen=True)
class SemanticConfig:
    """Standalone sentence-embedding similarity configuration.

    ``overall_score = score_scale * clip(cosine(resume, job), 0, 1)``

    Cosine is computed on L2-normalized embeddings. The score is a
    **semantic relevance / similarity** value on 0–100, not a hiring
    probability.
    """

    model_name: str = DEFAULT_MODEL_NAME
    score_scale: float = SCORE_SCALE
    device: str = DEFAULT_DEVICE
    normalize_embeddings: bool = True

    def __post_init__(self) -> None:
        if self.score_scale <= 0:
            raise ValueError("score_scale must be positive.")
        if not self.model_name.strip():
            raise ValueError("model_name must be a non-empty string.")
