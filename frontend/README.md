# Career Match frontend

Next.js App Router UI for Career Match. The frontend calls the FastAPI
matching and persistence APIs; it does not train or serve ML models.

## Local development

```bash
npm ci
npm run dev
```

Open **http://localhost:3000** (the dev server binds to `localhost`, not
`127.0.0.1`, so Clerk development sessions work without proxy errors).

Configure `frontend/.env.local` from `.env.example` (Clerk keys and
`NEXT_PUBLIC_API_URL`, default `http://localhost:8000`).

## Scripts

| Command | Purpose |
| --- | --- |
| `npm run dev` | Dev server on `localhost:3000` |
| `npm run build` | Production build |
| `npm run start` | Production server on `localhost:3000` |
| `npm test` | Vitest unit tests |
| `npm run lint` | ESLint |
| `npm run typecheck` | TypeScript check |

## Product routes

| Route | Access |
| --- | --- |
| `/` | Landing |
| `/match` | Guest or signed-in resume–job analysis |
| `/login`, `/signup` | Clerk auth |
| `/dashboard` | Saved resumes, jobs, match history |
| `/dashboard/jobs` | Job discovery and ranking |
| `/dashboard/tailor` | Grounded tailoring, preview, export |

See root `README.md` for full local startup (backend + Neon migrations).
