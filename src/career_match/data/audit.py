"""Dataset quality audit helpers.

Every count is derived from the loaded records. Nothing here is a matching
metric, and none of the figures are hard-coded into production logic.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median

from career_match.core.types import ResumeRecord
from career_match.data.legacy import default_dataset_path, load_legacy_dataset, repo_root

# Markers that often remain after UTF-8 text was decoded as Latin-1.
# Counted separately so a report cannot collapse them into one "mojibake" bucket.
MARKER_A_CIRCUMFLEX = "â"
MARKER_A_TILDE = "Ã"
MARKER_REPLACEMENT = "�"
SUSPICIOUS_ENCODING_MARKERS = (
    MARKER_A_CIRCUMFLEX,
    MARKER_A_TILDE,
    MARKER_REPLACEMENT,
)


def contains_non_ascii(text: str) -> bool:
    """Return True if ``text`` contains any non-ASCII character."""
    return any(ord(char) > 127 for char in text)


def contains_suspicious_encoding_marker(text: str) -> bool:
    """Return True if ``text`` contains ``â``, ``Ã``, or ``�``."""
    return any(marker in text for marker in SUSPICIOUS_ENCODING_MARKERS)


@dataclass(frozen=True)
class EncodingMetrics:
    """Per-row encoding quality counts.

    These five figures are independent questions about the same rows:

    * ``non_ascii_rows`` — any character above U+007F
    * ``rows_with_a_circumflex`` — contains ``â`` (often punctuation mojibake)
    * ``rows_with_a_tilde`` — contains ``Ã`` (often accented-letter mojibake)
    * ``rows_with_replacement`` — contains U+FFFD ``�``
    * ``rows_with_suspicious_encoding_marker`` — contains at least one of
      ``â``, ``Ã``, or ``�``
    """

    non_ascii_rows: int
    rows_with_a_circumflex: int
    rows_with_a_tilde: int
    rows_with_replacement: int
    rows_with_suspicious_encoding_marker: int


def encoding_metrics(texts: Iterable[str]) -> EncodingMetrics:
    """Count encoding issues in ``texts``. Each row is counted at most once per metric."""
    snapshot = list(texts)
    return EncodingMetrics(
        non_ascii_rows=sum(1 for text in snapshot if contains_non_ascii(text)),
        rows_with_a_circumflex=sum(1 for text in snapshot if MARKER_A_CIRCUMFLEX in text),
        rows_with_a_tilde=sum(1 for text in snapshot if MARKER_A_TILDE in text),
        rows_with_replacement=sum(1 for text in snapshot if MARKER_REPLACEMENT in text),
        rows_with_suspicious_encoding_marker=sum(
            1 for text in snapshot if contains_suspicious_encoding_marker(text)
        ),
    )


def audit_records(records: Sequence[ResumeRecord], *, path: Path) -> dict[str, object]:
    """Summarize loaded resume records for the dataset audit report."""
    try:
        display_path = path.resolve().relative_to(repo_root())
    except ValueError:
        display_path = path
    texts = [record.text for record in records]
    lengths = [len(text) for text in texts]
    categories = Counter(record.category for record in records)
    unique_texts = set(texts)
    metrics = encoding_metrics(texts)
    return {
        "path": str(display_path),
        "rows": len(records),
        "categories": dict(sorted(categories.items())),
        "category_count": len(categories),
        "empty_resumes": sum(1 for text in texts if not text.strip()),
        "duplicate_resumes": len(texts) - len(unique_texts),
        "unique_resumes": len(unique_texts),
        "resume_chars_min": min(lengths) if lengths else 0,
        "resume_chars_median": int(median(lengths)) if lengths else 0,
        "resume_chars_mean": round(mean(lengths), 1) if lengths else 0.0,
        "resume_chars_max": max(lengths) if lengths else 0,
        "non_ascii_rows": metrics.non_ascii_rows,
        "rows_with_a_circumflex": metrics.rows_with_a_circumflex,
        "rows_with_a_tilde": metrics.rows_with_a_tilde,
        "rows_with_replacement": metrics.rows_with_replacement,
        "rows_with_suspicious_encoding_marker": metrics.rows_with_suspicious_encoding_marker,
        "most_common_category": categories.most_common(1)[0] if categories else ("", 0),
        "least_common_category": categories.most_common()[-1] if categories else ("", 0),
    }


def audit_legacy_dataset(path: Path | None = None) -> dict[str, object]:
    """Load the legacy CSV and return a JSON-serializable quality summary."""
    dataset_path = path or default_dataset_path()
    records = load_legacy_dataset(dataset_path)
    return audit_records(records, path=dataset_path)
