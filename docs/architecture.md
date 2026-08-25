# Architecture

Career Match is split into three layers so research work cannot leak into the
product UI, and so a future serving API can sit between them.

```
┌─────────────────────────────────────────────┐
│  Product  —  Next.js prototype (`frontend/`)│
│  Recruiter/candidate flows. No trained      │
│  matching weights live here.                │
└────────────────────▲────────────────────────┘
                     │ HTTP (future)
┌────────────────────┴────────────────────────┐
│  Serving  —  not implemented                │
│  Versioned inference, auth, rate limits.    │
└────────────────────▲────────────────────────┘
                     │ package import
┌────────────────────┴────────────────────────┐
│  ML  —  `src/career_match/`                 │
│  Data loading, parsing, extraction,         │
│  Baseline Matcher v0.1, evaluation harness. │
└─────────────────────────────────────────────┘
```

## ML package

| Module | Responsibility | Status |
| --- | --- | --- |
| `career_match.data` | Load, validate, and audit the legacy CSV | Implemented |
| `career_match.parsing` | Deterministic text normalization | Implemented |
| `career_match.extraction` | Lexicon skill spans (32 canonical skills) | Implemented (not a model) |
| `career_match.matching` | Matcher protocol + **Baseline Matcher v0.1** | Implemented (lexical baseline) |
| `career_match.evaluation` | Classification helpers + ranking metrics + fixture harness | Implemented |

`BaselineMatcher` is the first matching-layer implementation: TF-IDF cosine
similarity plus catalog skill overlap, combined with named provisional
weights. The result is a 0–100 **baseline relevance score** with matched
and missing skills. It is not a calibrated hiring probability.

`UnimplementedMatcher.match()` still raises `MatchingNotImplementedError`
for callers that must not silently pick up an unmeasured heuristic.

## Matching layer (v0.1)

```
resume text ─┐
             ├─ tokenize (keep C++, C#, .NET) ─ TF-IDF cosine ─┐
job text ────┤                                                 ├─ hybrid score
             └─ skill catalog extract ─ job-skill coverage ────┘
```

- Configuration: `career_match.matching.config` (`TFIDF_WEIGHT=0.55`,
  `SKILL_OVERLAP_WEIGHT=0.45`).
- Developer CLI: `python scripts/run_baseline_match.py --sample`
- Evaluation: `python scripts/evaluate_baseline.py` (v0.1 sanity fixture)
  and `python scripts/evaluate_benchmark_v0_2.py` (harder v0.2 benchmark)

Do not add embeddings, transformers, LLMs, RAG, or a serving API in this
layer until a later model beats this baseline on **v0.2**.

## Data

- **Raw source of truth:** `legacy/resume_dataset.csv` (preserved prototype).
- **Development evaluation fixture (v0.1):** `data/evaluation/dev_relevance_fixture.json`
  (16-pair sanity check; not a production benchmark).
- **Development evaluation benchmark (v0.2):** `data/evaluation/dev_benchmark_v0_2.json`
  (56-pair harder set for model comparison; not a production benchmark).
- **Audit:** `python scripts/audit_legacy_dataset.py` writes
  `reports/legacy_dataset_audit.md`.

The legacy labels are *resume categories*, not (resume, job) relevance
pairs. Matching experiments must not treat those category labels as
ground truth.

## Experiments

`experiments/` remains reserved for notebooks. The first measured
baseline lives in the matching package and is evaluated by
`scripts/evaluate_baseline.py` (v0.1) and
`scripts/evaluate_benchmark_v0_2.py` (v0.2), which write
`reports/baseline_evaluation.md` and
`reports/benchmark_v0_2_evaluation.md`. Nothing in `experiments/` is production.

## Product prototype

`frontend/` is an early Career Match product prototype built fresh in this
repository (Next.js App Router, TypeScript, Tailwind, shadcn/ui). It is not a
preserved copy of an earlier UI. Routes:

- `/` — product overview and honest ML status
- `/match` — lexicon skill-overlap demo (not a trained matcher)
- `/architecture` — three-layer split in product language

The UI must not import Python or invent a production match percentage.
Serving is still a separate, unimplemented process.

## What this repository is not

- Not an applicant-tracking system.
- Not a production ranker.
- Not a claim that KNN category accuracy equals hiring quality.
- Not a claim that Baseline Matcher v0.1 is ready to rank real candidates.
