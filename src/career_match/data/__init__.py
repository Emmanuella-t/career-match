"""Dataset loading and schema helpers."""

from career_match.data.legacy import load_legacy_dataset
from career_match.data.schema import validate_resume_record

__all__ = ["load_legacy_dataset", "validate_resume_record"]
