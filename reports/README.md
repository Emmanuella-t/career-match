# Reports

Generated artifacts live here.

```bash
python scripts/audit_legacy_dataset.py
python scripts/evaluate_baseline.py
python scripts/evaluate_benchmark_v0_2.py
```

- `legacy_dataset_audit.md` — encoding and schema facts from the CSV
- `baseline_evaluation.md` — Baseline Matcher v0.1 on the v0.1 sanity fixture
- `benchmark_v0_2_evaluation.md` — the same untuned baseline on v0.2
- `benchmark_v0_2_label_review.md` — compact list of all 56 construction
  labels for later owner inspection (not marked as human-reviewed)

These snapshots do not claim production matching quality. v0.2 is the
comparison target; v0.1 is only a smoke test. v0.2 labels are development
targets, not independently validated ground truth.
