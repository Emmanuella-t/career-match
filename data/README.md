# Derived data

Keep the original CSV in `legacy/resume_dataset.csv`.

- `evaluation/dev_relevance_fixture.json` — **v0.1 sanity-check development
  fixture** (16 synthetic pairs). Too easy for model comparison; keep it
  for smoke tests.
- `evaluation/dev_benchmark_v0_2.json` — **v0.2 development evaluation
  benchmark** (8 jobs, 24 resumes, 56 pairs with manually specified
  synthetic relevance judgments). Constructed for controlled development
  evaluation and model comparison. Not real candidate data. Not
  production hiring labels. No independent annotator agreement.

Neither file uses `legacy/resume_dataset.csv` category labels as
relevance. Do not copy the raw prototype dataset into this directory.
