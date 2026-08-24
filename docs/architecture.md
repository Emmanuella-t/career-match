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
│  matching contracts, evaluation helpers.    │
└─────────────────────────────────────────────┘
```

## ML package

| Module | Responsibility | Status |
| --- | --- | --- |
| `career_match.data` | Load and validate the legacy CSV | Implemented |
| `career_match.parsing` | Deterministic text normalization | Implemented |
| `career_match.extraction` | Lexicon skill spans | Implemented (not a model) |
| `career_match.matching` | Matcher protocol | Interface only |
| `career_match.evaluation` | Precision / recall / F1 helpers | Implemented (no live scores) |

`UnimplementedMatcher.match()` raises `MatchingNotImplementedError` on
purpose. Do not replace that with an unmeasured heuristic and call it a
model.

## Data

- **Raw source of truth:** `legacy/resume_dataset.csv` (preserved prototype).
- **Derived files:** `data/` (empty until a matching split is defined).
- **Audit:** `python scripts/audit_legacy_dataset.py` writes
  `reports/legacy_dataset_audit.md`.

The legacy labels are *resume categories*, not (resume, job) relevance
pairs. Any matching experiment must construct its own task definition.

## Experiments

`experiments/` is reserved for notebooks and scripts that train or compare
matchers. Nothing in that directory is production.

## Product prototype

`frontend/` is a Next.js App Router app (TypeScript, Tailwind, shadcn/ui).
Routes:

- `/` — product overview and honest ML status
- `/match` — lexicon skill-overlap demo (not a trained matcher)
- `/architecture` — three-layer split in product language

The UI must not import Python or invent a match percentage. Serving will be
a separate process when a baseline exists.

## What this repository is not

- Not an applicant-tracking system.
- Not a production ranker.
- Not a claim that KNN category accuracy equals hiring quality.
