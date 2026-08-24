"""Tests for legacy dataset loading and schema checks."""

from pathlib import Path

import pytest

from career_match.core.exceptions import SchemaError
from career_match.data.legacy import load_legacy_dataset
from career_match.data.schema import validate_resume_record

LEGACY = Path("legacy") / "resume_dataset.csv"


def test_load_legacy_dataset_row_count() -> None:
    records = load_legacy_dataset(LEGACY)
    assert len(records) == 169


def test_legacy_columns_and_text() -> None:
    records = load_legacy_dataset(LEGACY)
    assert all(record.category and record.text.strip() for record in records)
    assert records[0].source_row == 2


def test_legacy_has_25_categories() -> None:
    records = load_legacy_dataset(LEGACY)
    categories = {record.category for record in records}
    assert len(categories) == 25
    assert "Data Science" in categories
    assert "Java Developer" in categories


def test_legacy_no_empty_resumes() -> None:
    records = load_legacy_dataset(LEGACY)
    assert all(record.text.strip() for record in records)


def test_legacy_duplicate_resume_count() -> None:
    records = load_legacy_dataset(LEGACY)
    texts = [record.text for record in records]
    assert len(texts) - len(set(texts)) == 3


def test_validate_record_rejects_empty() -> None:
    with pytest.raises(SchemaError):
        validate_resume_record(category="Data Science", text="   ", source_row=2)
    with pytest.raises(SchemaError):
        validate_resume_record(category="", text="Python developer", source_row=3)
