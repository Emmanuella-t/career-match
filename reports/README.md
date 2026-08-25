# Reports

Generated artifacts live here.

```bash
python scripts/audit_legacy_dataset.py
python scripts/evaluate_baseline.py
python scripts/evaluate_benchmark_v0_2.py
python scripts/evaluate_holdout_v0_3.py
```

- `legacy_dataset_audit.md` — encoding and schema facts from the CSV
- `baseline_evaluation.md` — Baseline Matcher v0.1 on the v0.1 sanity fixture
- `benchmark_v0_2_evaluation.md` — the same untuned baseline on v0.2
- `semantic_matcher_v0_1_evaluation.md` — MiniLM vs lexical on v0.2
- `benchmark_v0_2_label_review.md` — compact list of all 56 construction
  labels for later owner inspection (not marked as independently reviewed)
- `holdout_benchmark_v0_3_snapshot.md` — frozen pre-hybrid holdout metrics
- `holdout_benchmark_v0_3_label_review.md` — compact list of all 72 holdout
  judgments (awaiting/available for manual review)
- `hybrid_config_selection_v0_2.json` — v0.2 weight grid and chosen config
- `hybrid_matcher_v0_1_development.md` — hybrid vs lexical/semantic on v0.2
- `hybrid_matcher_v0_1_holdout.md` — single frozen holdout comparison

These snapshots do not claim production matching quality. v0.2 is for
development/error analysis; v0.3 is the frozen holdout; v0.1 is only a
smoke test. Labels are manually specified synthetic relevance judgments,
not independently validated ground truth.
