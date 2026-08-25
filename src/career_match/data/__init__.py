"""Dataset loading, schema helpers, and quality audits."""

from career_match.data.audit import audit_legacy_dataset, encoding_metrics
from career_match.data.legacy import load_legacy_dataset
from career_match.data.schema import validate_resume_record

__all__ = [
    "audit_legacy_dataset",
    "encoding_metrics",
    "load_legacy_dataset",
    "validate_resume_record",
]
