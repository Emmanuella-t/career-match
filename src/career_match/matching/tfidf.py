"""Deterministic TF-IDF cosine similarity for one resume/job pair.

The vectorizer is fit on the pair being compared so a single ``match()``
call does not depend on other documents. Technical tokens such as ``C++``,
``C#``, and ``.NET`` are preserved by the tokenizer. This does **not** use
the legacy notebook's punctuation-stripping cleaner.
"""

from __future__ import annotations

import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from career_match.parsing.text import normalize_text

# Longer technical forms first so ``C++`` is not tokenized as ``c``.
_TECH_TOKEN_RE = re.compile(
    r"(?i)("
    r"c\+\+|c#|\.net|"
    r"next\.js|node\.js|"
    r"scikit-learn|"
    r"[a-z][\w]*"
    r")"
)


def tokenize_technical(text: str) -> list[str]:
    """Tokenize normalized text while keeping selected technical tokens."""
    normalized = normalize_text(text)
    if not normalized:
        return []
    return [match.group(0).lower() for match in _TECH_TOKEN_RE.finditer(normalized)]


def _identity(text: str) -> str:
    return text


def tfidf_cosine_similarity(resume_text: str, job_text: str) -> float:
    """Return cosine similarity in ``[0, 1]`` for one resume and one job.

    Empty inputs yield 0.0. The value is clipped into ``[0, 1]`` so later
    scaling to 0–100 cannot produce surprises from floating-point noise.
    """
    resume_tokens = tokenize_technical(resume_text)
    job_tokens = tokenize_technical(job_text)
    if not resume_tokens or not job_tokens:
        return 0.0

    vectorizer = TfidfVectorizer(
        tokenizer=tokenize_technical,
        preprocessor=_identity,
        token_pattern=None,
        lowercase=False,
        ngram_range=(1, 2),
        stop_words="english",
        norm="l2",
        smooth_idf=True,
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform([resume_text, job_text])
    similarity = float(cosine_similarity(matrix[0:1], matrix[1:2])[0, 0])
    return min(1.0, max(0.0, similarity))
