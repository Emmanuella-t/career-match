"""Load the preserved Resume Screening prototype dataset."""

from __future__ import annotations

import csv
from pathlib import Path

from career_match.core.types import ResumeRecord
from career_match.data.schema import REQUIRED_FIELDS, validate_resume_record

DEFAULT_DATASET = Path("legacy") / "resume_dataset.csv"


def repo_root() -> Path:
    """Return the repository root (directory that contains ``pyproject.toml``)."""
    here = Path(__file__).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate
    return Path.cwd()


def default_dataset_path() -> Path:
    return repo_root() / DEFAULT_DATASET


def load_legacy_dataset(path: Path | None = None) -> tuple[ResumeRecord, ...]:
    """Load labeled resumes from the legacy CSV.

    The file is treated as UTF-8 with replacement for undecodable bytes so
    audits can still count rows with encoding problems.
    """
    dataset_path = path or default_dataset_path()
    if not dataset_path.is_file():
        raise FileNotFoundError(f"Legacy dataset not found: {dataset_path}")

    records: list[ResumeRecord] = []
    with dataset_path.open(newline="", encoding="utf-8", errors="replace") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{dataset_path} has no header row.")
        missing = [field for field in REQUIRED_FIELDS if field not in reader.fieldnames]
        if missing:
            raise ValueError(f"{dataset_path} is missing columns: {missing}")
        for index, row in enumerate(reader, start=2):
            records.append(
                validate_resume_record(
                    category=row.get("Category", ""),
                    text=row.get("Resume", ""),
                    source_row=index,
                )
            )
    return tuple(records)
