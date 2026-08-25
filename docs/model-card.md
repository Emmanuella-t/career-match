# Model card — Career Match

**Status:** Baseline Matcher v0.1 is a development lexical baseline.
There is still **no production matching model** and **no calibrated hiring
score**.

This card describes current artifacts honestly. Later semantic models must
be compared on the same evaluation framework before they replace this
baseline.

## Model details

| Field | Value |
| --- | --- |
| Model name | Baseline Matcher v0.1 |
| Task | resume-to-job relevance scoring with inspectable skill evidence |
| Implemented now | TF-IDF cosine similarity + catalog skill overlap |
| Score type | baseline relevance on 0–100, **not** a hiring probability |
| Previous prototype | One-vs-rest k-nearest neighbors **category** classifier in `legacy/Resume_Screening.ipynb` |
| Owners | Emmanuella Turkson |

The notebook prototype predicts a job-family label from resume text. Career
Match's product goal is different: given one resume and one job, produce an
explainable match score. Those numbers are not interchangeable.

## Baseline Matcher v0.1

The first matching implementation lives in `src/career_match/matching/`.
It compares resume text to job-description text with two transparent
channels.

### Method

1. **TF-IDF lexical similarity.** A `TfidfVectorizer` is fit on the pair
   being compared (resume + job only). Cosine similarity is computed on
   unigrams and bigrams with English stop words. A custom tokenizer keeps
   technical tokens such as `C++`, `C#`, and `.NET`. The matcher uses
   `normalize_text` only. It does **not** reuse the legacy notebook's
   punctuation-stripping cleaner.
2. **Skill overlap.** A 32-entry catalog extracts canonical skill names
   from each document. Overlap is
   `|resume ∩ job| / |job|` over that catalog.
3. **Hybrid score.** Named constants in `career_match.matching.config`:

   `overall = 0.55 * tfidf_similarity + 0.45 * skill_overlap_score`

   If the job text has **zero** catalog skills, the skill channel is
   skipped and overall equals TF-IDF. Weights are **provisional**: they
   are not tuned on labeled hiring data. They exist so later experiments
   can change `TFIDF_WEIGHT` and `SKILL_OVERLAP_WEIGHT` without rewriting
   the matcher.

### What the score means

`overall_score` is a **baseline relevance score** on 0–100. It reflects
shared technical vocabulary plus coverage of catalog skills listed in the
job text. `matched_skills` and `missing_skills` are the inspectable
explanation.

### What the score does not mean

- It is **not** a probability that a recruiter should hire, interview, or
  reject.
- It is **not** calibrated against human hiring decisions.
- It is **not** a claim about seniority, communication, or culture fit.
- It is **not** production matching quality.

### Why this baseline exists

It is the first measurable, reproducible, explainable matcher. Future
embedding, transformer, LLM, or RAG rankers must **outperform it on the
same evaluation harness** (`scripts/evaluate_baseline.py` and
`data/evaluation/dev_relevance_fixture.json`) before they replace it.

### Evaluation fixture limitations

The development fixture (`career-match-dev-eval-v0.1`) contains 16
synthetic resume/job pairs across four roles. It is a **development
evaluation fixture**, not a production benchmark. It does **not** use
legacy CSV category labels as relevance. It is not real candidate data.
Sixteen pairs cannot represent a hiring funnel. There is no fairness
audit and no human rater agreement.

Measured results on that fixture are recorded in
`reports/baseline_evaluation.md`. Those numbers only show that the
baseline ranks constructed strong matches above constructed mismatches
on this tiny set.

### Known failure modes

- Skills outside the 32-entry catalog are invisible to the overlap
  channel (for example Kafka).
- Mention-based extraction treats negated phrases as hits (`No
  JavaScript`, `No ... Docker`).
- Short aliases such as `js` can theoretically over-match; alphanumeric
  surfaces currently require word boundaries.
- Pair-fit TF-IDF overweights rare phrases that happen to appear in both
  documents.
- Weak and moderate resumes can score close together when they share
  Python/SQL.
- Jobs with no catalog skills ignore the skill channel.
- English stop-word removal can drop domain words that happen to be stop
  words.

## Intended use

- **In scope now (development):** ranking constructed resume/job pairs,
  inspecting skill evidence, comparing later models to this baseline.
- **Out of scope now:** automated reject/advance decisions, production
  embeddings, demographic inference, serving an API.
- **Out of scope always without review:** using category-classifier
  accuracy as a hiring KPI.

## Training data (legacy CSV)

Source file: `legacy/resume_dataset.csv` (Kaggle-style "Resume Screening"
table: `Category`, `Resume`).

Facts from `scripts/audit_legacy_dataset.py` (re-run that script rather than
copying stale numbers):

- 169 rows, 25 categories, no empty resumes
- 3 duplicate resume texts
- Strong class imbalance (largest class: Java Developer; smallest: PMO)
- Encoding quality (computed from the CSV, not assumed): 128 rows contain
  non-ASCII characters; 124 contain `â`; 6 contain `Ã`; 0 contain `�`;
  **125 of 169 rows contain at least one suspicious encoding marker**.
  Encoding damage is widespread, not a handful of isolated rows.

This is **not** a matching dataset. There are no job descriptions, no
relevance labels, and no agreed train/test split for matching. Baseline
Matcher v0.1 is **not trained** on this CSV.

## Evaluation

Ranking metrics on the synthetic development fixture (see
`reports/baseline_evaluation.md` for the current snapshot):

- Binary Precision@K and Recall@K with relevant = grade ≥ 2
- NDCG with gain `2^rel - 1`
- Explicit ranking checks: strong > moderate, moderate > mismatch

Those metrics are appropriate because each role has a fully labeled,
graded candidate list. They are **not** production KPIs.

Classification accuracy from the original notebook is **not** restated
here. That notebook mixed exploration and modeling in a single interactive
document; it is preserved for history, not as a benchmark.

## Limitations and risks

- Category labels collapse distinct roles and seniority.
- Duplicate resumes will inflate accuracy if splits are random.
- Lexicon extraction only sees a small English tech vocabulary; it will miss
  skills, over-match negated mentions, and ignores context.
- Resume screening systems can encode historical hiring bias. No fairness
  audit has been run.
- Encoding errors in the CSV are common (125 of 169 rows carry `â`, `Ã`,
  or `�`) and can hide tokens (for example naïve → mojibake).

## Ethical considerations

Do not deploy this baseline to rank people in a live hiring funnel. Add a
labeled matching task with a leakage-safe split, error analysis, and a
human review path first.

## Next milestone

1. Keep this lexical baseline as the comparison point.
2. Expand labeled matching data without treating CSV categories as
   relevance.
3. Only then consider embedding models, and only if they beat this
   baseline on the same harness.

## Citation / provenance

Original exploratory work: `legacy/Resume_Screening.ipynb` and
`legacy/README-original.md`. Dataset path: `legacy/resume_dataset.csv`.
Baseline implementation: `src/career_match/matching/`.
