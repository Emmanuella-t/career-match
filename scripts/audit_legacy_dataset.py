#!/usr/bin/env python3
"""Audit the preserved Resume Screening prototype dataset.

This script is deterministic: it only reports dataset facts (size, labels,
duplicates, encoding issues). It does not train or score a matching model.
Encoding metrics are counted separately so the report cannot collapse every
non-ASCII row into a single "mojibake" figure.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from career_match.data.audit import audit_legacy_dataset

REPORT_PATH = Path("reports") / "legacy_dataset_audit.md"


def render_report(summary: dict[str, object]) -> str:
    categories = summary["categories"]
    assert isinstance(categories, dict)
    most_name, most_n = summary["most_common_category"]  # type: ignore[misc]
    least_name, least_n = summary["least_common_category"]  # type: ignore[misc]
    lines = [
        "# Legacy dataset audit",
        "",
        "Generated deterministically by `scripts/audit_legacy_dataset.py`.",
        "This report describes the original Resume Screening CSV. It is **not**",
        "a matching-model evaluation.",
        "",
        "## Snapshot",
        "",
        f"- Path: `{summary['path']}`",
        f"- Rows: **{summary['rows']}**",
        f"- Distinct job categories: **{summary['category_count']}**",
        f"- Unique resume texts: **{summary['unique_resumes']}**",
        f"- Duplicate resume texts: **{summary['duplicate_resumes']}**",
        f"- Empty resumes: **{summary['empty_resumes']}**",
        f"- Resume length (characters): min {summary['resume_chars_min']}, "
        f"median {summary['resume_chars_median']}, mean {summary['resume_chars_mean']}, "
        f"max {summary['resume_chars_max']}",
        f"- Most common category: {most_name} ({most_n})",
        f"- Least common category: {least_name} ({least_n})",
        "",
        "## Encoding quality",
        "",
        "These counts are computed independently from the loaded CSV. They are",
        "not interchangeable: a non-ASCII row is not automatically a mojibake",
        "row, and the three markers are tracked separately.",
        "",
        f"- Rows containing any non-ASCII character: "
        f"**{summary['non_ascii_rows']}**",
        f"- Rows containing marker `â`: "
        f"**{summary['rows_with_a_circumflex']}**",
        f"- Rows containing marker `Ã`: "
        f"**{summary['rows_with_a_tilde']}**",
        f"- Rows containing replacement marker `�`: "
        f"**{summary['rows_with_replacement']}**",
        f"- Rows containing at least one suspicious encoding marker "
        f"(`â`, `Ã`, or `�`): "
        f"**{summary['rows_with_suspicious_encoding_marker']}**",
        "",
        "## Label distribution",
        "",
        "| Category | Count | Share |",
        "| --- | ---: | ---: |",
    ]
    rows = int(summary["rows"])  # type: ignore[arg-type]
    for name, count in sorted(categories.items(), key=lambda item: (-item[1], item[0])):
        share = (count / rows * 100) if rows else 0.0
        lines.append(f"| {name} | {count} | {share:.1f}% |")
    suspicious = int(summary["rows_with_suspicious_encoding_marker"])  # type: ignore[arg-type]
    lines.extend(
        [
            "",
            "## Implications for Career Match",
            "",
            "- The source problem is **resume category classification**, not",
            "  resume-to-job matching. Labels are coarse job families, not ranked",
            "  (resume, job) pairs.",
            "- 169 rows across 25 classes is too small and too imbalanced for a",
            "  production matcher. Several classes have only 3–5 examples.",
            "- Duplicate resumes will leak across a naive random split.",
            f"- Encoding damage is widespread: **{suspicious} of {rows}** rows",
            "  contain at least one suspicious encoding marker (`â`, `Ã`, or `�`).",
            "  Parsers must normalize text; do not treat the CSV as clean Unicode.",
            "- The next ML milestone should define a matching task and split",
            "  policy **before** training embedding models.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=None,
        help="Path to the legacy CSV (defaults to legacy/resume_dataset.csv).",
    )
    parser.add_argument(
        "--write-report",
        action="store_true",
        default=True,
        help="Write reports/legacy_dataset_audit.md (default: true).",
    )
    parser.add_argument(
        "--no-write-report",
        action="store_false",
        dest="write_report",
        help="Print the report without writing a file.",
    )
    args = parser.parse_args()
    summary = audit_legacy_dataset(args.dataset)
    report = render_report(summary)
    print(report)
    if args.write_report:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(report, encoding="utf-8")
        print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
