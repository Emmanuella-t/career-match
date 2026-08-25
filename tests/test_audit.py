"""Dataset audit tests."""

from pathlib import Path

from scripts.audit_legacy_dataset import audit_legacy_dataset, render_report

from career_match.data.audit import encoding_metrics

MINI = Path("tests") / "fixtures" / "mini_resumes.csv"
LEGACY = Path("legacy") / "resume_dataset.csv"


def test_audit_summary_keys() -> None:
    summary = audit_legacy_dataset(MINI)
    assert summary["rows"] == 4
    assert summary["category_count"] == 3
    assert "Data Science" in summary["categories"]  # type: ignore[operator]
    assert "non_ascii_rows" in summary
    assert "rows_with_a_circumflex" in summary
    assert "rows_with_a_tilde" in summary
    assert "rows_with_replacement" in summary
    assert "rows_with_suspicious_encoding_marker" in summary
    report = render_report(summary)
    assert "Legacy dataset audit" in report
    assert "Label distribution" in report
    assert "Encoding quality" in report


def test_audit_detects_duplicates() -> None:
    summary = audit_legacy_dataset(MINI)
    assert summary["duplicate_resumes"] == 1
    legacy = audit_legacy_dataset(LEGACY)
    assert legacy["rows"] == 169
    assert legacy["duplicate_resumes"] == 3


def test_encoding_metrics_count_markers_separately() -> None:
    metrics = encoding_metrics(
        [
            "ASCII only",
            "café",
            "Skills â\x80¢ Python",
            "NaÃ¯ve Bayes",
            "bad\ufffdtoken",
            "NaÃ¯ve â\x80¢ both",
        ]
    )
    assert metrics.non_ascii_rows == 5
    assert metrics.rows_with_a_circumflex == 2
    assert metrics.rows_with_a_tilde == 2
    assert metrics.rows_with_replacement == 1
    assert metrics.rows_with_suspicious_encoding_marker == 4


def test_audit_mini_has_no_suspicious_encoding_markers() -> None:
    summary = audit_legacy_dataset(MINI)
    assert summary["non_ascii_rows"] == 0
    assert summary["rows_with_a_circumflex"] == 0
    assert summary["rows_with_a_tilde"] == 0
    assert summary["rows_with_replacement"] == 0
    assert summary["rows_with_suspicious_encoding_marker"] == 0


def test_audit_legacy_csv_encoding_statistics() -> None:
    summary = audit_legacy_dataset(LEGACY)
    assert summary["rows"] == 169
    assert summary["category_count"] == 25
    assert summary["unique_resumes"] == 166
    assert summary["duplicate_resumes"] == 3
    assert summary["empty_resumes"] == 0
    assert summary["non_ascii_rows"] == 128
    assert summary["rows_with_a_circumflex"] == 124
    assert summary["rows_with_a_tilde"] == 6
    assert summary["rows_with_replacement"] == 0
    assert summary["rows_with_suspicious_encoding_marker"] == 125


def test_audit_report_names_encoding_metrics_separately() -> None:
    report = render_report(audit_legacy_dataset(LEGACY))
    assert "Rows containing any non-ASCII character" in report
    assert "Rows containing marker `â`" in report
    assert "Rows containing marker `Ã`" in report
    assert "Rows containing replacement marker `�`" in report
    assert "Rows containing at least one suspicious encoding marker" in report
    assert "Encoding damage is widespread" in report
    assert "125 of 169" in report
    assert "Encoding damage is limited" not in report
