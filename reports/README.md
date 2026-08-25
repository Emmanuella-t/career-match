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

These snapshots do not claim production matching quality. v0.2 is the
comparison target; v0.1 is only a smoke test.
