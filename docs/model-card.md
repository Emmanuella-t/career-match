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

Future embedding, transformer, LLM, or RAG rankers must **outperform this
baseline on development benchmark v0.2**
(`data/evaluation/dev_benchmark_v0_2.json`,
`scripts/evaluate_benchmark_v0_2.py`) before they replace it. The v0.1
16-pair fixture remains a sanity check only.

### Evaluation fixtures

**v0.1** (`career-match-dev-eval-v0.1`) is a 16-pair **sanity-check
development fixture**. It is too easy for model comparison: the lexical
baseline ranks constructed strong matches above mismatches with perfect
top-k metrics on that set. Keep it. Do not treat those metrics as a
benchmark of matching quality.

**v0.2** (`career-match-dev-benchmark-v0.2`) is the harder **development
evaluation benchmark** and the comparison target for this baseline, a
future sentence-embedding model, and a future hybrid ranker.

- 8 synthetic jobs, 24 synthetic resumes, 56 human-graded pairs
- Overlapping families: Machine Learning Engineer, Data Scientist, Data
  Analyst, Backend Engineer, Frontend Engineer, Full-Stack Engineer,
  MLOps Engineer, Data Engineer
- Hard cases: synonymy, negation, keyword stuffing, related-role overlap,
  seniority mismatch, catalog misses
- Labels are human-defined grades 0–3 with rationales, not model outputs
- Not real candidate data and **not** a production benchmark
- Does **not** use legacy CSV category labels as relevance

Measured baseline results on v0.2 (untuned v0.1 weights) are in
`reports/benchmark_v0_2_evaluation.md`. Poor numbers on v0.2 are expected
and useful.

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

Comparison target: **development benchmark v0.2** (see
`reports/benchmark_v0_2_evaluation.md`). Untuned Baseline Matcher v0.1
on that set (mean over 8 jobs):

| Metric | Mean |
| --- | ---: |
| Precision@1 | 0.875 |
| Precision@3 | 0.667 |
| Recall@3 | 0.562 |
| NDCG@3 | 0.849 |
| NDCG (full pool of 7) | 0.929 |
| Pairwise ordering accuracy | 0.709 |

Score ranges for grades 0–3 overlap. Mean score is not monotone in grade
because synonym matches are under-scored and keyword-heavy mismatches
are over-scored.

v0.1 sanity-fixture metrics are intentionally **not** used as a model
comparison signal.

Binary Precision@K / Recall@K use relevant = grade ≥ 2. NDCG uses gain
`2^rel - 1`. Those metrics are appropriate because each job has a fully
labeled graded pool. They are **not** production KPIs.

Classification accuracy from the original notebook is **not** restated
here.

## Known weaknesses on v0.2

- Keyword stuffing can outrank a real Machine Learning Engineer
- Synonym phrasing (*REST services*, *cloud infrastructure*, *serving ML
  models*) collapses TF-IDF and skill overlap
- Negated mentions (*No production Docker*) still count as skill hits
- Related roles that share Python/SQL/Git/Docker are hard to separate
- Intern vs 4+ year mismatches are weakly penalized if tools are named
- Catalog misses include PostgreSQL, Spark, Airflow, and most paraphrases

Future semantic models must be evaluated against **the same v0.2
benchmark** with the same grades. Do not retune lexical weights just to
inflate these numbers.

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

1. Keep Baseline Matcher v0.1 weights frozen as the lexical comparison
   point.
2. Evaluate future embedding or hybrid rankers on **v0.2**, not by
   overfitting the v0.1 sanity fixture.
3. Only replace the baseline if the new model improves P@1, P@3, pairwise
   ordering, and synonym ranking on v0.2.

## Citation / provenance

Original exploratory work: `legacy/Resume_Screening.ipynb` and
`legacy/README-original.md`. Dataset path: `legacy/resume_dataset.csv`.
Baseline implementation: `src/career_match/matching/`.
