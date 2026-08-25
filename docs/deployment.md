# Deployment

Career Match is a **two-service** application:

```
Browser → Next.js frontend → FastAPI backend → matcher (semantic / hybrid / lexical)
```

This guide is **provider-neutral**. Use any host that can run a Python web
process and a Node.js/Next.js app. A live public URL is tracked separately;
until one exists, treat deployment as readiness work only.

## A. Backend deployment

### Requirements

- Python **3.11+** (CI uses 3.12)
- Install **production** extras (not `.[dev]`):

```bash
python -m pip install -e ".[api,semantic]"
```

`api` provides FastAPI + uvicorn. `semantic` provides sentence-transformers
for Semantic / Hybrid Matcher v0.1. Lexical-only hosts may omit `semantic`,
but the default API matcher is semantic.

### Startup

Production (bind all interfaces, honor `PORT`):

```bash
python scripts/start_api_production.py
```

Equivalent:

```bash
uvicorn career_match.api.app:app --host 0.0.0.0 --port $PORT
```

A `Procfile` is included for hosts that understand:

```text
web: python scripts/start_api_production.py
```

Local development remains:

```bash
uvicorn career_match.api.app:app --reload --host 127.0.0.1 --port 8000
# or: python scripts/run_api.py --reload
```

### Environment variables

| Variable | Purpose | Default |
| --- | --- | --- |
| `PORT` | Listen port | `8000` |
| `HOST` | Bind address (production script) | `0.0.0.0` |
| `CAREER_MATCH_CORS_ORIGINS` | Comma-separated allowed browser origins | `http://localhost:3000`, `http://127.0.0.1:3000` |
| `CAREER_MATCH_MODEL_CACHE_DIR` | Optional model cache directory | unset (library defaults) |

See `.env.example`. Never commit real secrets.

### Health endpoints

| Route | Behavior |
| --- | --- |
| `GET /health` | Liveness. Always lightweight. **Does not** load MiniLM. |
| `GET /ready` | Service can accept requests. Reports `semantic_model_loaded` without forcing a download. |

### Cold-start behavior

1. Importing `career_match.api.app` does **not** download MiniLM.
2. Process start / `/health` / `/ready` do **not** load the encoder.
3. The first **semantic** or **hybrid** `POST /api/v1/match` loads
   `sentence-transformers/all-MiniLM-L6-v2` (network + disk on first host).
4. The encoder and `MatcherService` instance are reused for later requests
   in the same process. Concurrent first loads are lock-guarded.

Expect a slower first semantic/hybrid request after a fresh deploy or empty
cache. Subsequent requests reuse the in-memory model.

## B. Frontend deployment

### Requirements

- Node.js **22+** (matches CI)
- From `frontend/`:

```bash
npm ci
npm run build
npm run start
```

### Environment

Build-time (inlined into the browser bundle):

```bash
NEXT_PUBLIC_API_URL=https://your-api.example.com
```

If unset at build time, the client falls back to `http://localhost:8000`
(local development only). Production builds **must** set
`NEXT_PUBLIC_API_URL` to the deployed API origin.

See `frontend/.env.example`.

## C. CORS setup

1. Deploy the frontend and note its public origin (scheme + host, no path),
   e.g. `https://career-match.example.com`.
2. Set the backend:

```bash
CAREER_MATCH_CORS_ORIGINS=https://career-match.example.com
```

Multiple origins: comma-separated. Trailing slashes are stripped.

**Do not** use `allow_origins=["*"]` with credentials. Career Match keeps an
explicit allow-list.

## D. End-to-end checklist

1. Install backend with `.[api,semantic]`.
2. Set `CAREER_MATCH_CORS_ORIGINS` to the frontend origin.
3. Start backend with `python scripts/start_api_production.py` (or uvicorn).
4. Confirm `GET /health` → `{"status":"ok"}`.
5. Confirm `GET /ready` → `status: ready` (model may still be unloaded).
6. Build frontend with `NEXT_PUBLIC_API_URL` pointing at the API.
7. Open the frontend Match page, paste resume + JD, Analyze Match.
8. Confirm a real score and skill explainability (or a human-readable error
   if the API is unreachable).

## E. Troubleshooting

| Symptom | Check |
| --- | --- |
| Frontend cannot reach backend | `NEXT_PUBLIC_API_URL`, API firewall / HTTPS, browser network tab |
| CORS error in browser | `CAREER_MATCH_CORS_ORIGINS` must exactly match the frontend Origin |
| Slow first analysis | Expected MiniLM cold start; warm with one semantic request after deploy |
| Missing env / wrong API host | Rebuild frontend after changing `NEXT_PUBLIC_API_URL` |
| Health check fails | Process not listening on `PORT` / wrong path (use `/health`) |
| Import / install errors | Use `pip install -e ".[api,semantic]"`, Python 3.11+ |

## Safety notes

- Scores are relevance signals, not hiring probabilities.
- Frontend auth uses Clerk (see `frontend/.env.example`). The FastAPI
  matcher service does not yet enforce auth or guest quotas.
- Guest analysis limits are client-side for product flow only; public
  production enforcement should be server-backed.
- No application database yet — dashboard history/resumes/jobs are empty
  states, not fabricated data.
- Do not expose debug mode or Python tracebacks to clients (API returns
  structured `detail` messages only).
  Do not commit Clerk secrets.
