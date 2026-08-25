# Architecture

Career Match is split into three layers so research work cannot leak into the
product UI, and so a future serving API can sit between them.

```
┌─────────────────────────────────────────────┐
│  Product  —  Next.js UI (`frontend/`)       │
│  Paste resume + JD → Analyze → results      │
└────────────────────▲────────────────────────┘
                     │ HTTP POST /api/v1/match
┌────────────────────┴────────────────────────┐
│  Serving  —  FastAPI (`career_match.api`)   │
│  POST /api/v1/match, GET /health            │
│  Default matcher: semantic                  │
└────────────────────▲────────────────────────┘
                     │ package import
┌────────────────────┴────────────────────────┐
│  ML  —  `src/career_match/`                 │
│  Lexical, semantic, and hybrid matchers,    │
│  plus evaluation harness.                   │
└─────────────────────────────────────────────┘
```

```
Next.js UI
    ↓
FastAPI `/api/v1/match`
    ↓
selected matcher
    ├── Semantic Matcher v0.1 (default)
    ├── Hybrid Matcher v0.1
    └── Lexical Baseline v0.1
    ↓
structured relevance / explainability response
    ↓
results UI (score, matched / missing / weak skills)
```

## ML package

| Module | Responsibility | Status |
| --- | --- | --- |
| `career_match.data` | Load, validate, and audit the legacy CSV | Implemented |
| `career_match.parsing` | Deterministic text normalization | Implemented |
| `career_match.extraction` | Lexicon skill spans + evidence/negation heuristics (32 canonical skills) | Implemented (not a model) |
| `career_match.matching` | Matcher protocol + lexical + semantic + **hybrid** matchers | Implemented (not production) |
| `career_match.api` | FastAPI service exposing matchers over HTTP | Implemented (local-dev serving) |
| `career_match.evaluation` | Classification helpers + ranking metrics + fixture/holdout harness | Implemented |

`BaselineMatcher` is the first matching-layer implementation: TF-IDF cosine
similarity plus catalog skill overlap, combined with named provisional
weights. The result is a 0–100 **baseline relevance score** with matched
and missing skills. It is not a calibrated hiring probability.

`UnimplementedMatcher.match()` still raises `MatchingNotImplementedError`
for callers that must not silently pick up an unmeasured heuristic.

## Matching layer

Three **independent or combined** scorers. Hybrid mixes the channels with
weights frozen on v0.2; it is still not a production hiring model.

```
resume ─┐
        ├─ TF-IDF cosine + catalog skill overlap → Baseline Matcher v0.1
job ────┤
        ├─ MiniLM embedding cosine              → Semantic Matcher v0.1
        └─ semantic + TF-IDF + evidence skills  → Hybrid Matcher v0.1
              (negation / keyword-list / stuffing heuristics)
```

- Lexical config: `career_match.matching.config` (`TFIDF_WEIGHT=0.55`,
  `SKILL_OVERLAP_WEIGHT=0.45`). Do not retune these to chase v0.2.
- Semantic config: `career_match.matching.semantic_config`
  (`sentence-transformers/all-MiniLM-L6-v2`).
- Hybrid config: `career_match.matching.hybrid_config`
  (`SEMANTIC_WEIGHT=0.60`, `TFIDF_WEIGHT=0.20`, `SKILL_WEIGHT=0.20`),
  frozen on v0.2; **not** tuned on holdout v0.3.
- Evidence/negation: `career_match.extraction.evidence`
- Compare: `python scripts/compare_matchers.py`
- Hybrid eval: `python scripts/evaluate_hybrid.py --all`
- Lexical-only eval: `python scripts/evaluate_benchmark_v0_2.py`

Do not add LLMs or RAG in this layer. HTTP serving lives in
`career_match.api`, not inside the matcher modules. Deployment notes:
`docs/deployment.md`.

## HTTP API

Package: `career_match.api`.

| Route | Purpose |
| --- | --- |
| `GET /health` | Liveness; does not load MiniLM |
| `GET /ready` | Readiness; reports whether semantic model already loaded (no download) |
| `POST /api/v1/match` | Score `resume_text` vs `job_description` |

- Default matcher: **semantic** (strongest top-rank quality on frozen holdout
  v0.3; not a claim of universal superiority over hybrid pairwise gains)
- Optional `matcher`: `semantic` | `hybrid` | `lexical`
- Text limit: 50,000 characters per field
- CORS allow-list from `CAREER_MATCH_CORS_ORIGINS` (local defaults when unset)
- MiniLM loads lazily on first semantic/hybrid request and is reused
- Deploy notes: `docs/deployment.md`

Example:

```bash
curl -s http://127.0.0.1:8000/api/v1/match \
  -H "Content-Type: application/json" \
  -d "{\"resume_text\":\"Python FastAPI Docker Git\",\"job_description\":\"Backend Engineer using Python and Docker\",\"matcher\":\"semantic\"}"
```

Example response shape:

```json
{
  "matcher": "Semantic Matcher v0.1",
  "matcher_version": "0.1.0",
  "overall_score": 72.4,
  "semantic_score": 72.4,
  "tfidf_score": null,
  "skill_overlap_score": null,
  "matched_skills": [],
  "missing_skills": [],
  "weak_or_negated_skills": [],
  "disclaimer": "This score reflects resume-to-job relevance and is not a hiring probability."
}
```

Run locally:

```bash
python -m pip install -e ".[dev,api]"
uvicorn career_match.api.app:app --reload
# or: python scripts/run_api.py --reload
```

OpenAPI UI: `http://127.0.0.1:8000/docs`

## Data

- **Raw source of truth:** `legacy/resume_dataset.csv` (preserved prototype).
- **Development evaluation fixture (v0.1):** `data/evaluation/dev_relevance_fixture.json`
  (16-pair sanity check; not a production benchmark).
- **Development evaluation benchmark (v0.2):** `data/evaluation/dev_benchmark_v0_2.json`
  (56-pair harder set for error analysis and model development). Synthetic;
  constructed for controlled development evaluation. Labels are
  benchmark-construction development targets, not independently validated
  ground truth.
- **Frozen holdout benchmark (v0.3):** `data/evaluation/holdout_benchmark_v0_3.json`
  (72-pair holdout for pre-hybrid and later hybrid comparison). Synthetic;
  no real candidate data; not production ground truth. Created before
  hybrid-matcher development and frozen via SHA-256 manifest. Do not tune
  against v0.3.
- **Audit:** `python scripts/audit_legacy_dataset.py` writes
  `reports/legacy_dataset_audit.md`.

The legacy labels are *resume categories*, not (resume, job) relevance
pairs. Matching experiments must not treat those category labels as
ground truth.

## Experiments

`experiments/` remains reserved for notebooks. Measured matchers live in
the matching package and are evaluated by
`scripts/evaluate_benchmark_v0_2.py` (lexical v0.2),
`scripts/compare_matchers.py` (lexical vs semantic on v0.2),
`scripts/evaluate_holdout_v0_3.py` (pre-hybrid holdout snapshot), and
`scripts/evaluate_hybrid.py` (hybrid development + holdout). Nothing in
`experiments/` is production.

## Product UI

`frontend/` is the Career Match product UI (Next.js App Router, TypeScript,
Tailwind, shadcn/ui). Routes:

- `/` — product overview
- `/match` — end-to-end resume–job analysis against FastAPI
- `/architecture` — three-layer split in product language

Flow: paste resume and job text → `Analyze Match` →
`frontend/src/lib/api.ts` calls `POST /api/v1/match` → display relevance score
and skill explainability. Default matcher is semantic. Scores are not hiring
probabilities. PDF/DOCX upload is not implemented.

Configure the API base with `NEXT_PUBLIC_API_URL` (default
`http://localhost:8000`). Local workflow: run uvicorn and `npm run dev`, then
open `http://localhost:3000`.

## What this repository is not

- Not an applicant-tracking system.
- Not a production ranker with auth, multi-tenant isolation, or SLAs.
- Not a claim that KNN category accuracy equals hiring quality.
- Not a claim that Baseline, Semantic, or Hybrid Matcher v0.1 is ready
  to rank real candidates without human review.
- Not an LLM or RAG system.
