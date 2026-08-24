#!/usr/bin/env python3
"""Audit the preserved Resume Screening prototype dataset.

This script is deterministic: it only reports dataset facts (size, labels,
duplicates, encoding issues). It does not train or score a matching model.
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from statistics import mean, median

from career_match.data.legacy import default_dataset_path, load_legacy_dataset
from career_match.parsing.text import repair_mojibake

REPORT_PATH = Path("reports") / "legacy_dataset_audit.md"


def audit_legacy_dataset(path: Path | None = None) -> dict[str, object]:
    """Return a JSON-serializable summary of the legacy dataset."""
    dataset_path = path or default_dataset_path()
    records = load_legacy_dataset(dataset_path)
    texts = [record.text for record in records]
    lengths = [len(text) for text in texts]
    categories = Counter(record.category for record in records)
    unique_texts = set(texts)
    mojibake_rows = [
        record.source_row for record in records if "Ã" in record.text and repair_mojibake(record.text) != record.text
    ]
    return {
        "path": str(dataset_path),
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
        "mojibake_row_count": len(mojibake_rows),
        "mojibake_rows": mojibake_rows,
        "most_common_category": categories.most_common(1)[0] if categories else ("", 0),
        "least_common_category": categories.most_common()[-1] if categories else ("", 0),
    }


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
        f"- Rows with UTF-8/Latin-1 mojibake (for example `NaÃ¯ve`): "
        f"**{summary['mojibake_row_count']}**",
        f"- Most common category: {most_name} ({most_n})",
        f"- Least common category: {least_name} ({least_n})",
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
            "- Encoding damage is limited but real; parsers must normalize text.",
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
