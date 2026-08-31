# Architecture

Career Match is split into three layers so research work cannot leak into the
product UI, and so a future serving API can sit between them.

```
┌─────────────────────────────────────────────┐
│  Product  —  Next.js UI (`frontend/`)       │
│  Landing → Guest or Auth (Clerk)            │
│  → Match / Dashboard                        │
└────────────────────▲────────────────────────┘
                     │ HTTP (+ Bearer for persistence)
┌────────────────────┴────────────────────────┐
│  Serving  —  FastAPI (`career_match.api`)   │
│  Public: POST /api/v1/match, /health        │
│  Auth: resumes / matches / jobs (Clerk JWT) │
└──────────┬─────────────────▲────────────────┘
           │                 │ package import
           ▼                 │
┌──────────────────┐  ┌──────┴────────────────────────┐
│ Persistence      │  │  ML — `src/career_match/`     │
│ Neon Postgres    │  │  Lexical / semantic / hybrid  │
│ SQLAlchemy/psycopg│ │  + evaluation harness         │
└──────────────────┘  └───────────────────────────────┘
```

```
Landing
    ├── Guest → /match (2 free successful analyses, then auth gate)
    │         → no database writes
    └── Auth (Clerk) → /dashboard + unlimited /match
            ↓
FastAPI `/api/v1/match`  →  ML matcher  →  results UI
            ↓ (optional Save analysis / resume / job CRUD)
Clerk JWT verified on FastAPI
            ↓
Postgres tables: user_profiles, resumes, match_analyses, saved_jobs,
job_opportunities (discoverable catalog)
```

**Separated concerns**

| Concern | System |
| --- | --- |
| Authentication | Clerk (frontend sessions; backend JWKS verification) |
| ML inference | FastAPI `POST /api/v1/match` → package matchers |
| Persistence | Neon Postgres via SQLAlchemy + psycopg (backend `DATABASE_URL`) |

Guest usage for product flow is still **client-side** (local session id +
count) and is not tamper-proof. Persistence queries are always scoped to
the verified Clerk `sub`. Empty dashboard lists are honest empty states —
no seed/fake rows.

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

| Route | Access | Purpose |
| --- | --- | --- |
| `/` | Public | Landing |
| `/match` | Public (guest or signed-in) | Real resume–job analysis |
| `/login` | Public | Clerk sign-in |
| `/signup` | Public | Clerk sign-up |
| `/dashboard` | Protected | Authenticated workspace shell |
| `/dashboard/jobs` | Protected | Rank discoverable jobs for a saved resume |
| `/dashboard/tailor` | Protected | Grounded resume tailoring for a target job |
| `/architecture` | Public | Product-language architecture |

**Auth:** Clerk (`@clerk/nextjs`) — email/password sessions, protected
`/dashboard`, logout. Chosen for least App Router complexity without
storing passwords in this monorepo.

**Persistence:** Neon Postgres (`user_profiles`, `resumes`,
`match_analyses`, `saved_jobs`, `job_opportunities`) via SQLAlchemy + psycop. FastAPI verifies
Clerk Bearer tokens and scopes every query to `clerk_user_id`.
`DATABASE_URL` is backend-only. Authenticated users save analyses explicitly
via **Save analysis**; guests never write to the database.

**Guest mode:** two successful analyses without an account; the third
attempt opens an auth gate and preserves resume/JD/matcher in
`sessionStorage` (not query strings). Authenticated users bypass the
limit and reuse the same `/match` + FastAPI path.

Flow: upload a PDF/DOCX resume (authenticated) or paste resume text, add a job
description, then `Analyze Match` → `frontend/src/lib/api.ts` calls
`POST /api/v1/match` → display relevance score and skill explainability.
Authenticated parsing uses `POST /api/v1/resumes/parse` (in-memory; 2 MiB cap;
text-based PDF/DOCX only — no OCR for scanned PDFs). Default matcher is
semantic. Scores are not hiring probabilities.

**Job discovery:** authenticated `POST /api/v1/jobs/discover` loads the user's
resume, reads available jobs from a `JobSource` provider (Postgres catalog by
default), and ranks them with the same matcher pipeline as `/match`. Discoverable
jobs live in `job_opportunities`; user bookmarks remain in `saved_jobs`. No live
external job feed ships in this milestone — production starts with an empty
catalog until a provider sync is added. Tests inject synthetic in-memory sources.

**Grounded tailoring:** authenticated `POST /api/v1/resumes/tailor` maps resume
evidence to job requirements before any rewrite generation. Deterministic evidence
classification reuses `extraction/evidence.py`. Rewrite providers may phrase
supported evidence only; unsupported requirements are excluded. Alignment scores
use the existing matcher — not ATS pass probability. Original saved resumes are
never overwritten; users copy accepted suggestions manually.

Configure the API base with `NEXT_PUBLIC_API_URL` (default
`http://localhost:8000`). Clerk keys: see `frontend/.env.example`.
Persistence: `DATABASE_URL`, `CLERK_ISSUER` on the API host (root
`.env.example`). Schema: `migrations/0001_initial_persistence.sql` and
`migrations/0002_job_opportunities.sql`.
Local workflow: run uvicorn and `npm run dev`, then open `http://localhost:3000`.

## What this repository is not

- Not an applicant-tracking system.
- Not a multi-tenant production ranker with SLAs or server-enforced guest
  quotas (guest limits are client-side for this milestone).
- Not a claim that KNN category accuracy equals hiring quality.
- Not a claim that Baseline, Semantic, or Hybrid Matcher v0.1 is ready
  to rank real candidates without human review.
- Not an LLM or RAG system.
- Not automatic silent persistence of every match (users save analyses
  explicitly; guests never persist).
