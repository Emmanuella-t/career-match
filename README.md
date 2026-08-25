# Career Match

Explainable ML-powered resume-to-job matching.

Career Match turns the original Resume Screening notebook prototype into a
maintainable monorepo: a Python ML package, reproducible dataset audits, and
automated tests. The original notebook, dataset, and cover image are
preserved under `legacy/`. `frontend/` is an early Career Match product
prototype built fresh in this repository; it is not a copy of an earlier UI.

Repository: [https://github.com/Emmanuella-t/career-match.git](https://github.com/Emmanuella-t/career-match.git)

## Current ML status

**Baseline Matcher v0.1** scores one resume against one job description
using TF-IDF cosine similarity and catalog skill overlap. The result is a
0–100 **baseline relevance score** with matched and missing skills.

That score is **not** a hiring probability and **not** a production model.
The 16-pair development fixture is **not** a production benchmark. Future
semantic models must beat this baseline on the same evaluation harness.

The legacy notebook trains a k-nearest-neighbors classifier that predicts a
resume's *job category* (Data Science, Java Developer, HR, …). That is not
the same problem as scoring a resume against a specific job description.
Those category labels are not used as matching ground truth.

## Repository layout

```
career-match/
├── src/career_match/   ML package (data, parsing, extraction, matching, evaluation)
├── tests/              Pytest suite
├── scripts/            Audit, baseline demo, and evaluation runners
├── docs/               Architecture notes and model card
├── reports/            Generated audit and baseline evaluation output
├── experiments/        Reserved for later matching experiments
├── data/evaluation/    Development evaluation fixture (synthetic pairs)
├── legacy/             Original notebook, CSV, README, and cover image
├── frontend/           Early Career Match product prototype (built fresh here)
└── .github/            CI
```

## Setup (ML)

Python 3.11+ is required.

```bash
git clone https://github.com/Emmanuella-t/career-match.git
cd career-match
python -m pip install -e ".[dev]"
pytest
ruff check .
python -c "import career_match; print('Career Match import successful')"
python scripts/audit_legacy_dataset.py
python scripts/run_baseline_match.py --sample
python scripts/evaluate_baseline.py
```

Installation uses `pyproject.toml`. There is no root `requirements.txt`.

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
