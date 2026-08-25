# Development evaluation sets

Synthetic resume/job pairs only. Not real candidate data. Not a production
benchmark. Legacy CSV category labels are never used as relevance.

| File | Name | Role |
| --- | --- | --- |
| `dev_relevance_fixture.json` | `career-match-dev-eval-v0.1` | sanity-check fixture (16 pairs) |
| `dev_benchmark_v0_2.json` | `career-match-dev-benchmark-v0.2` | harder development benchmark (56 pairs) |

v0.2 grades: `3` strong, `2` moderate, `1` weak, `0` mismatch. Each
judgment includes a construction rationale. These are **manually specified
synthetic relevance judgments** (development targets), not independently
validated ground truth. Binary ranking metrics treat grades ≥ 2 as
relevant.

Provenance is recorded in `dev_benchmark_v0_2.json` (`provenance`). A
compact inspection table lives at
`reports/benchmark_v0_2_label_review.md` (awaiting/available for manual
review; not marked as reviewed).

```bash
python scripts/evaluate_baseline.py
python scripts/evaluate_benchmark_v0_2.py
```
