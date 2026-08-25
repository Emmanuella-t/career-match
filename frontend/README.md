# Career Match frontend

`frontend/` is an early Career Match product prototype built fresh in this
repository. It is the product layer. It does not train or serve a matching
model, and it is not a preserved copy of an earlier UI.

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
