"""Dataset audit tests."""

from pathlib import Path

from scripts.audit_legacy_dataset import audit_legacy_dataset, render_report

MINI = Path("tests") / "fixtures" / "mini_resumes.csv"
LEGACY = Path("legacy") / "resume_dataset.csv"


def test_audit_summary_keys() -> None:
    summary = audit_legacy_dataset(MINI)
    assert summary["rows"] == 4
    assert summary["category_count"] == 3
    assert "Data Science" in summary["categories"]  # type: ignore[operator]
    report = render_report(summary)
    assert "Legacy dataset audit" in report
    assert "Label distribution" in report


def test_audit_detects_duplicates() -> None:
    summary = audit_legacy_dataset(MINI)
    assert summary["duplicate_resumes"] == 1
    legacy = audit_legacy_dataset(LEGACY)
    assert legacy["rows"] == 169
    assert legacy["duplicate_resumes"] == 3
    assert legacy["mojibake_row_count"] == 6
