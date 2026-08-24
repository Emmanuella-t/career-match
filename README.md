# Career Match

Explainable ML-powered resume-to-job matching.

Career Match turns the original Resume Screening notebook prototype into a
maintainable monorepo: a Python ML package, reproducible dataset audits,
automated tests, and (in the product layer) a web prototype. The original
notebook, dataset, and cover image are preserved under `legacy/`.

## Current ML status

**No production matching model has been implemented yet.**

The legacy notebook trains a k-nearest-neighbors classifier that predicts a
resume's *job category* (Data Science, Java Developer, HR, …). That is not
the same problem as scoring a resume against a specific job description.

The next milestone is a **measurable resume-to-job matching baseline** —
with an explicit split policy and reported metrics — before introducing
semantic embedding models.

## Repository layout

```
career-match/
├── src/career_match/   ML package (data, parsing, extraction, matching, evaluation)
├── tests/              Pytest suite for the foundation
├── scripts/            Dataset audit and future experiment runners
├── docs/               Architecture notes and model card
├── reports/            Generated audit output
├── experiments/        Reserved for matching baselines
├── data/               Reserved for derived datasets (not the raw CSV)
├── legacy/             Original notebook, CSV, README, and cover image
├── frontend/           Product prototype (Next.js)
└── .github/            CI
```

## Setup (ML)

Python 3.11+ is required.

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
python scripts/audit_legacy_dataset.py
python -c "import career_match; print('Career Match import successful')"
```

## Setup (frontend)

Node.js 22+ and npm:

```bash
cd frontend
npm ci
npm run lint
npm run build
npm run dev
```

The prototype runs at `http://127.0.0.1:43173`. It highlights lexicon overlaps
only. It does not expose a production match score.

## Legacy prototype

The starting point of this repository is a resume-category screening notebook
and a 169-row labeled CSV (25 job families). See
`legacy/README-original.md` and `docs/model-card.md` for what that artifact
can and cannot support.

## License

The original prototype README did not include a license file. Add one before
any public redistribution of the dataset if the upstream source requires it.
