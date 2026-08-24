# Model card — Career Match (foundation)

**Status:** no production matching model.

This card describes the *current* artifacts honestly. It will be rewritten
when a matching baseline is trained and evaluated.

## Model details

| Field | Value |
| --- | --- |
| Model name | none |
| Task | intended: resume-to-job match scoring with explanations |
| Implemented now | dataset loading, text normalization, lexicon skill extraction, matcher *interface* |
| Previous prototype | One-vs-rest k-nearest neighbors **category** classifier in `legacy/Resume_Screening.ipynb` |
| Owners | Emmanuella Turkson |

The notebook prototype predicts a job-family label from resume text. Career
Match's product goal is different: given one resume and one job, produce an
explainable match score. Those numbers are not interchangeable.

## Intended use

- **In scope later:** ranking or scoring a candidate against a written job
  description, with evidence a recruiter can inspect.
- **Out of scope now:** automated reject/advance decisions, production
  embeddings, demographic inference.
- **Out of scope always without review:** using category-classifier accuracy
  as a hiring KPI.

## Training data (legacy CSV)

Source file: `legacy/resume_dataset.csv` (Kaggle-style "Resume Screening"
table: `Category`, `Resume`).

Facts from `scripts/audit_legacy_dataset.py` (re-run that script rather than
copying stale numbers):

- 169 rows, 25 categories, no empty resumes
- 3 duplicate resume texts
- Strong class imbalance (largest class: Java Developer; smallest: PMO)
- A handful of UTF-8/Latin-1 mojibake rows

This is **not** a matching dataset. There are no job descriptions, no
relevance labels, and no agreed train/test split for matching.

## Evaluation

There is **no reported matching metric** (no nDCG, precision@k, or pairwise
accuracy) because there is no matcher and no labeled matching split.

Classification accuracy from the original notebook is **not** restated here.
That notebook mixed exploration and modeling in a single interactive
document; it is preserved for history, not as a benchmark.

## Limitations and risks

- Category labels collapse distinct roles and seniority.
- Duplicate resumes will inflate accuracy if splits are random.
- Lexicon extraction only sees a small English tech vocabulary; it will miss
  skills, over-match short tokens if misconfigured, and ignores context.
- Resume screening systems can encode historical hiring bias. No fairness
  audit has been run.
- Encoding errors in the CSV can hide tokens (for example naïve → mojibake).

## Ethical considerations

Do not deploy this foundation to rank people. Add a documented matching
task, a leakage-safe split, error analysis, and a human review path first.

## Next milestone

1. Define a resume-to-job matching objective and labels.
2. Freeze a split policy (no resume text in both train and test).
3. Ship a **lexical baseline** with published metrics.
4. Only then consider embedding models.

## Citation / provenance

Original exploratory work: `legacy/Resume_Screening.ipynb` and
`legacy/README-original.md`. Dataset path: `legacy/resume_dataset.csv`.
