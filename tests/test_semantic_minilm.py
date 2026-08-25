"""Optional MiniLM integration tests. Skipped if sentence-transformers is missing."""

from __future__ import annotations

import pytest

from career_match.matching.semantic import SemanticMatcher
from career_match.matching.semantic_config import DEFAULT_MODEL_NAME

pytestmark = pytest.mark.semantic


@pytest.fixture(scope="module")
def minilm_matcher() -> SemanticMatcher:
    pytest.importorskip("sentence_transformers")
    return SemanticMatcher()


def test_semantic_module_import_does_not_require_sentence_transformers() -> None:
    import career_match.matching.semantic as semantic_mod

    assert semantic_mod.SemanticMatcher is SemanticMatcher


def test_minilm_similar_text_outranks_unrelated(minilm_matcher: SemanticMatcher) -> None:
    similar = minilm_matcher.match(
        "Serving ML models on cloud infrastructure with containers.",
        "Deploy and serve machine learning models on cloud infrastructure.",
    )
    unrelated = minilm_matcher.match(
        "Community theater lighting cues and costume sketches.",
        "Deploy and serve machine learning models on cloud infrastructure.",
    )
    assert 0 <= similar.overall_score <= 100
    assert similar.overall_score > unrelated.overall_score
    first = minilm_matcher.match("Python FastAPI services", "Python FastAPI services")
    second = minilm_matcher.match("Python FastAPI services", "Python FastAPI services")
    assert first.overall_score == pytest.approx(second.overall_score, abs=1e-5)
    encoder = minilm_matcher.encoder
    assert getattr(encoder, "model_name", DEFAULT_MODEL_NAME) == DEFAULT_MODEL_NAME
    dim = encoder.embedding_dim  # type: ignore[attr-defined]
    assert dim == 384
