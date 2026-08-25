# Development and holdout evaluation sets

Synthetic resume/job pairs only. Not real candidate data. Not a production
benchmark. Legacy CSV category labels are never used as relevance.

| File | Name | Role |
| --- | --- | --- |
| `dev_relevance_fixture.json` | `career-match-dev-eval-v0.1` | sanity-check fixture (16 pairs) |
| `dev_benchmark_v0_2.json` | `career-match-dev-benchmark-v0.2` | development / error-analysis benchmark (56 pairs) |
| `holdout_benchmark_v0_3.json` | `career-match-holdout-benchmark-v0.3` | frozen holdout benchmark (72 pairs) |
| `holdout_benchmark_v0_3.manifest.json` | checksum manifest | SHA-256 freeze for v0.3 reproducibility |

v0.2 / v0.3 grades: `3` strong, `2` moderate, `1` weak, `0` mismatch. Each
judgment includes a construction rationale and case tags. These are
**manually specified synthetic relevance judgments**, not independently
validated ground truth. Binary ranking metrics treat grades ≥ 2 as
relevant.

**v0.3** was created before hybrid-matcher development and should remain
frozen during that milestone. Accidental edits are detected by comparing
the JSON file SHA-256 to the manifest (reproducibility, not security).

```bash
python scripts/evaluate_baseline.py
python scripts/evaluate_benchmark_v0_2.py
python scripts/evaluate_holdout_v0_3.py
```
