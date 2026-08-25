# Model card — Career Match

**Status:** Career Match has two independent development matchers:
Baseline Matcher v0.1 (lexical) and Semantic Matcher v0.1 (MiniLM
embeddings). There is still **no production matching model**, **no
hybrid**, and **no calibrated hiring score**.

This card describes current artifacts honestly. Later semantic models must
be compared on the same evaluation framework before they replace this
baseline.

## Model details

| Field | Value |
| --- | --- |
| Model name | Baseline Matcher v0.1; Semantic Matcher v0.1 (independent) |
| Task | resume-to-job relevance scoring |
| Implemented now | lexical TF-IDF + skill overlap; standalone MiniLM cosine |
| Score type | development relevance / similarity on 0–100, **not** a hiring probability |
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

It remains the transparent lexical comparison point. Semantic Matcher v0.1
was measured on the same v0.2 benchmark without retuning these weights.
A hybrid is **not** implemented until each approach is understood on its
own.

## Semantic Matcher v0.1

Standalone sentence-embedding similarity. It does **not** use the 32-skill
lexicon and is **not** mixed with TF-IDF.

### Method

1. Encode resume text and job text with
   `sentence-transformers/all-MiniLM-L6-v2` (384-d, CPU).
2. Cosine similarity of L2-normalized embeddings.
3. `semantic_relevance = 100 * clip(cosine, 0, 1)`.

The transformer is loaded on first encode, then reused. Importing
`career_match` does not download the model.

### What the score means

A **semantic relevance / similarity** score on 0–100 for one resume vs
one job. Nearby phrasing (*REST services* vs *REST APIs*, *cloud
infrastructure* vs AWS) can match without catalog aliases.

### What the score does not mean

- Not a hiring, interview, or acceptance probability
- Not candidate quality or seniority
- Not production matching quality
- Not a claim that embeddings should replace the lexical baseline in a
  product UI

### Evaluation (same v0.2 benchmark)

See `reports/semantic_matcher_v0_1_evaluation.md` and
`scripts/compare_matchers.py`. Mean over 8 jobs:

| Metric | Lexical v0.1 | Semantic v0.1 | Δ |
| --- | ---: | ---: | ---: |
| Precision@1 | 0.875 | 1.000 | +0.125 |
| Precision@3 | 0.667 | 0.792 | +0.125 |
| Recall@3 | 0.562 | 0.688 | +0.125 |
| NDCG@3 | 0.849 | 0.900 | +0.052 |
| NDCG (full pool) | 0.929 | 0.956 | +0.028 |
| Pairwise accuracy | 0.709 | 0.865 | +0.155 |

These are **development-benchmark** results on 56 synthetic pairs. Grade
score ranges still overlap.

### Limitations and compute

- MiniLM is not a negation model: backend and MLOps “no production Docker /
  limited Kubernetes” resumes still rank #2.
- Keyword stuffing (`r-mle-stuffing`) is no longer rank 1 on MLE but remains
  #3 with a high score (75.7).
- Synonym MLE improved (rank 7 → 5) but still sits below stuffing and
  negation.
- Data Engineer NDCG@3 fell (0.904 → 0.762) because the synonym resume
  outranked the labeled strong match.
- Load cost on this machine was ~3s for MiniLM plus ~0.3s to encode 32
  texts, versus ~0.1s for the lexical baseline on 56 pairs.

### Why this matcher exists

To measure whether sentence embeddings help the failure modes of TF-IDF
on the **same** labels, before anyone builds a hybrid.

### Evaluation fixtures

**v0.1** (`career-match-dev-eval-v0.1`) is a 16-pair **sanity-check
development fixture**. It is too easy for model comparison: the lexical
baseline ranks constructed strong matches above mismatches with perfect
top-k metrics on that set. Keep it. Do not treat those metrics as a
benchmark of matching quality.

**v0.2** (`career-match-dev-benchmark-v0.2`) is the harder **development
evaluation benchmark** and the comparison target for this baseline, a
future sentence-embedding model, and a future hybrid ranker.

- 8 synthetic jobs, 24 synthetic resumes, 56 pairs with manually
  specified synthetic relevance judgments
- Overlapping families: Machine Learning Engineer, Data Scientist, Data
  Analyst, Backend Engineer, Frontend Engineer, Full-Stack Engineer,
  MLOps Engineer, Data Engineer
- Hard cases: synonymy, negation, keyword stuffing, related-role overlap,
  seniority mismatch, catalog misses
- Grades 0–3 with rationales are **benchmark-construction labels**
  (development targets), not independently validated ground truth
- No independent annotator agreement
- Not real candidate data, not production hiring labels, and **not** a
  production benchmark
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

Comparison target: **development benchmark v0.2**. Lexical snapshot:
`reports/benchmark_v0_2_evaluation.md`. Semantic comparison:
`reports/semantic_matcher_v0_1_evaluation.md`.

Untuned Baseline Matcher v0.1 (mean over 8 jobs): Precision@1 0.875,
NDCG@3 0.849, pairwise 0.709.

Standalone Semantic Matcher v0.1 on the **same** labels: Precision@1
1.000, NDCG@3 0.900, pairwise 0.865. Mean metrics improved; see the model
section above for stuffing, negation, and the Data Engineer NDCG drop.

v0.1 sanity-fixture metrics are intentionally **not** used as a model
comparison signal. These numbers are **not** production KPIs.

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

Future models, including any hybrid, must be evaluated against **the same
v0.2 benchmark** with the same grades. Do not retune lexical weights just
to inflate these numbers. Do not treat MiniLM mean gains as production
readiness.

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

1. Keep both standalone matchers frozen as comparison points.
2. Only consider a **hybrid** after it is shown to beat both systems on
   v0.2, including stuffing, negation, and synonym ranking.
3. Do not treat MiniLM mean-metric gains as a reason to drop the lexical
   baseline or to ship a production ranker.

## Citation / provenance

Original exploratory work: `legacy/Resume_Screening.ipynb` and
`legacy/README-original.md`. Dataset path: `legacy/resume_dataset.csv`.
Baseline implementation: `src/career_match/matching/`.
