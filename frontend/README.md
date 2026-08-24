# Career Match frontend

Next.js product prototype for Career Match. This app is the product layer. It
does not train or serve a matching model.

## Scripts

```bash
npm ci
npm run lint
npm run build
npm run dev
```

Dev server: `http://127.0.0.1:43173`

## What is implemented

- Overview of the ML-first project
- Skill-overlap prototype (same small lexicon as the Python package)
- Architecture notes that match `docs/architecture.md`

The compare screen never reports a production match score.
