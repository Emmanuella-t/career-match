"""Standalone sentence-embedding matcher (Semantic Matcher v0.1).

Encodes resume and job text with a sentence-transformer and scores them
with cosine similarity. The 32-skill lexicon is not used. This module
does **not** load a transformer at import time.
"""

from __future__ import annotations

from collections.abc import Sequence
from threading import Lock
from typing import Protocol, runtime_checkable

import numpy as np

from career_match.core.types import MatchResult
from career_match.matching.semantic_config import (
    SEMANTIC_MATCHER_NAME,
    SemanticConfig,
)


@runtime_checkable
class EmbeddingEncoder(Protocol):
    """Encodes one or more texts into a 2-D float array of shape (n, dim)."""

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        """Return one row per input text."""


def cosine_to_score(cosine: float, scale: float) -> float:
    """Map cosine similarity in ``[-1, 1]`` to ``[0, scale]``.

    Negative cosine values (rare for this MiniLM setup) map to 0 so the
    documented range stays a non-negative relevance score.
    """
    clipped = min(1.0, max(0.0, float(cosine)))
    return min(scale, max(0.0, clipped * scale))


def pairwise_cosine(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Row-wise cosine. ``left`` and ``right`` are (n, dim) or (dim,)."""
    left_mat = np.atleast_2d(np.asarray(left, dtype=np.float64))
    right_mat = np.atleast_2d(np.asarray(right, dtype=np.float64))
    if left_mat.shape != right_mat.shape:
        raise ValueError(
            f"cosine operands must share shape, got {left_mat.shape} and {right_mat.shape}."
        )
    left_norm = np.linalg.norm(left_mat, axis=1, keepdims=True)
    right_norm = np.linalg.norm(right_mat, axis=1, keepdims=True)
    denom = np.clip(left_norm * right_norm, 1e-12, None)
    dots = np.sum(left_mat * right_mat, axis=1, keepdims=True)
    return np.clip((dots / denom).reshape(-1), -1.0, 1.0)


def _l2_normalize(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.clip(norms, 1e-12, None)


class SentenceTransformerEncoder:
    """Loads a sentence-transformer once and reuses it for encode calls."""

    def __init__(
        self,
        model_name: str,
        *,
        device: str = "cpu",
        normalize_embeddings: bool = True,
        model: object | None = None,
    ) -> None:
        self.model_name = model_name
        self.device = device
        self.normalize_embeddings = normalize_embeddings
        self._model = model
        self._load_lock = Lock()

    @property
    def model(self) -> object:
        if self._model is None:
            with self._load_lock:
                if self._model is None:
                    self._model = _load_sentence_transformer(self.model_name, self.device)
        return self._model

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 0), dtype=np.float32)
        vectors = self.model.encode(  # type: ignore[union-attr]
            list(texts),
            convert_to_numpy=True,
            normalize_embeddings=self.normalize_embeddings,
            show_progress_bar=False,
        )
        matrix = np.asarray(vectors, dtype=np.float32)
        if matrix.ndim == 1:
            matrix = matrix.reshape(1, -1)
        if not self.normalize_embeddings:
            matrix = _l2_normalize(matrix)
        return matrix

    @property
    def embedding_dim(self) -> int:
        probe = self.encode(["dimension probe"])
        return int(probe.shape[1])


def _load_sentence_transformer(model_name: str, device: str) -> object:
    """Import and construct the transformer only when scoring needs it."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise ImportError(
            "Semantic Matcher v0.1 requires sentence-transformers. "
            'Install with: python -m pip install -e ".[semantic]"'
        ) from exc
    model = SentenceTransformer(model_name, device=device)
    model.eval()
    return model


class SemanticMatcher:
    """Cosine similarity of sentence embeddings. Not a hiring model."""

    name = SEMANTIC_MATCHER_NAME

    def __init__(
        self,
        config: SemanticConfig | None = None,
        encoder: EmbeddingEncoder | None = None,
    ) -> None:
        self.config = config or SemanticConfig()
        self._encoder = encoder
        self._encoder_lock = Lock()

    @property
    def encoder(self) -> EmbeddingEncoder:
        if self._encoder is None:
            with self._encoder_lock:
                if self._encoder is None:
                    self._encoder = SentenceTransformerEncoder(
                        self.config.model_name,
                        device=self.config.device,
                        normalize_embeddings=self.config.normalize_embeddings,
                    )
        return self._encoder

    def encode_texts(self, texts: Sequence[str]) -> np.ndarray:
        """Encode many texts with the reused encoder."""
        return self.encoder.encode(texts)

    def similarity_scores(self, resume_vectors: np.ndarray, job_vector: np.ndarray) -> np.ndarray:
        """Return 0–100 semantic scores for each resume vector vs one job vector."""
        resumes = np.atleast_2d(np.asarray(resume_vectors, dtype=np.float64))
        job = np.atleast_2d(np.asarray(job_vector, dtype=np.float64))
        if job.shape[0] != 1:
            raise ValueError("job_vector must encode a single job.")
        job_tiled = np.repeat(job, resumes.shape[0], axis=0)
        cosines = pairwise_cosine(resumes, job_tiled)
        return np.array(
            [cosine_to_score(float(value), self.config.score_scale) for value in cosines],
            dtype=np.float64,
        )

    def match(self, resume_text: str, job_text: str) -> MatchResult:
        """Score one resume against one job with semantic cosine similarity.

        The returned ``overall_score`` / ``semantic_similarity`` is a
        **semantic relevance score** on 0–100. It is not a probability
        that a recruiter should hire.
        """
        matrix = self.encode_texts([resume_text, job_text])
        scores = self.similarity_scores(matrix[0:1], matrix[1:2])
        semantic = float(scores[0])
        evidence = (
            f"{SEMANTIC_MATCHER_NAME}: cosine similarity of "
            f"{self.config.model_name} embeddings",
            f"semantic_similarity={semantic:.1f}/{self.config.score_scale:.0f}",
            "Standalone semantic score. Skill catalog is not used.",
            "Not a hiring probability.",
        )
        return MatchResult(
            overall_score=semantic,
            tfidf_similarity=0.0,
            skill_overlap_score=0.0,
            matched_skills=(),
            missing_skills=(),
            resume_skills=(),
            job_skills=(),
            evidence=evidence,
            semantic_similarity=semantic,
        )
