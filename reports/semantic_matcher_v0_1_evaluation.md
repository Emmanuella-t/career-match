# Semantic Matcher v0.1 — development evaluation

Synthetic resume/job pairs constructed for controlled development evaluation. Not real candidate data. Not production hiring labels. Relevance grades are manually specified synthetic relevance judgments (development targets), not independently validated ground truth. No independent annotator agreement. Intended for model comparison and error analysis. Legacy CSV category labels are not used.

This report compares a **standalone** sentence-embedding matcher with the
untuned lexical baseline on the same v0.2 development benchmark.
It is **not** a production quality claim and does **not** introduce a hybrid model.

## Model

- Matcher: **Semantic Matcher v0.1**
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- sentence-transformers: `3.4.1`
- Embedding dimensionality: **384**
- Similarity: cosine of L2-normalized embeddings
- Score: `semantic_relevance = 100 * clip(cosine, 0, 1)`
- The 32-skill lexicon is **not** used in this score
- Device: CPU

The score is **semantic relevance / similarity** on 0–100.
It is not a hiring probability, acceptance probability, or candidate-quality rating.

## Benchmark

- Name: `career-match-dev-benchmark-v0.2`
- Kind: development evaluation benchmark
- Jobs: **8**
- Unique synthetic resumes: **24**
- Judgments: **56**
- Labels were not modified for this experiment

## Runtime (this machine, small development set)

- MiniLM load: **3.0s**
- Semantic evaluation (32 unique texts encoded once): **0.3s**
- Lexical baseline evaluation: **0.1s**
- Relative cost: sentence embeddings are far heavier than pair-fit TF-IDF,
  even on 56 pairs, mostly due to model load and transformer encode.

## Semantic metrics (mean over 8 jobs)

| Metric | Mean |
| --- | ---: |
| Precision@1 | 1.000 |
| Precision@3 | 0.792 |
| Recall@3 | 0.688 |
| NDCG@3 | 0.900 |
| NDCG (full pool) | 0.956 |
| Pairwise ordering accuracy | 0.865 |

## Semantic score distribution by grade

| Grade | N | Mean | Min | Max |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 9 | 42.4 | 24.0 | 75.7 |
| 1 | 19 | 52.2 | 26.4 | 76.9 |
| 2 | 19 | 64.4 | 47.6 | 81.0 |
| 3 | 9 | 80.6 | 68.5 | 87.7 |

Overlapping semantic score ranges: **0 vs 1, 0 vs 2, 0 vs 3, 1 vs 2, 1 vs 3, 2 vs 3**.

## Baseline comparison

Lexical Baseline Matcher v0.1 was **not retuned**. Delta = semantic − lexical.

- Lexical formula: `overall = 0.55 * tfidf + 0.45 * skill_overlap`

| Metric | Lexical | Semantic | Δ |
| --- | ---: | ---: | ---: |
| Precision@1 | 0.875 | 1.000 | +0.125 |
| Precision@3 | 0.667 | 0.792 | +0.125 |
| Recall@3 | 0.562 | 0.688 | +0.125 |
| NDCG@3 | 0.849 | 0.900 | +0.052 |
| NDCG (full pool) | 0.929 | 0.956 | +0.028 |
| Pairwise ordering accuracy | 0.709 | 0.865 | +0.155 |

## Per-role semantic results

### Machine Learning Engineer (`job-mle`)

- Semantic: P@1=1.00 P@3=0.33 R@3=0.33 NDCG@3=0.591 NDCG@7=0.874 pairwise=0.588
- Lexical:  P@1=0.00 P@3=0.33 NDCG@3=0.381 pairwise=0.235

| Rank | Resume | Grade | Semantic | Lexical rank | Lexical score |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `r-mle-prod` | 3 | 83.8 | 2 | 55.6 |
| 2 | `r-mle-negation` | 1 | 76.9 | 3 | 43.6 |
| 3 | `r-mle-stuffing` | 0 | 75.7 | 1 | 56.2 |
| 4 | `r-ai-apps` | 2 | 68.6 | 6 | 24.8 |
| 5 | `r-mle-synonym` | 3 | 68.5 | 7 | 2.9 |
| 6 | `r-mle-intern` | 1 | 57.7 | 4 | 28.0 |
| 7 | `r-backend-prod` | 1 | 57.6 | 5 | 27.9 |

### Data Scientist (`job-ds`)

- Semantic: P@1=1.00 P@3=1.00 R@3=0.75 NDCG@3=1.000 NDCG@7=1.000 pairwise=1.000
- Lexical:  P@1=1.00 P@3=0.67 NDCG@3=0.904 pairwise=0.706

| Rank | Resume | Grade | Semantic | Lexical rank | Lexical score |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `r-ds-prod` | 3 | 75.4 | 1 | 58.5 |
| 2 | `r-ds-synonym` | 2 | 68.4 | 7 | 2.5 |
| 3 | `r-ds-partial` | 2 | 62.0 | 2 | 42.4 |
| 4 | `r-mle-prod` | 2 | 55.5 | 5 | 26.7 |
| 5 | `r-da-prod` | 1 | 52.4 | 4 | 27.3 |
| 6 | `r-backend-prod` | 1 | 44.0 | 3 | 28.1 |
| 7 | `r-systems-cpp` | 0 | 32.5 | 6 | 26.0 |

### Data Analyst (`job-da`)

- Semantic: P@1=1.00 P@3=1.00 R@3=0.75 NDCG@3=1.000 NDCG@7=1.000 pairwise=1.000
- Lexical:  P@1=1.00 P@3=1.00 NDCG@3=1.000 pairwise=0.941

| Rank | Resume | Grade | Semantic | Lexical rank | Lexical score |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `r-da-prod` | 3 | 76.7 | 1 | 37.4 |
| 2 | `r-ds-partial` | 2 | 71.8 | 2 | 35.9 |
| 3 | `r-da-synonym` | 2 | 63.9 | 5 | 24.1 |
| 4 | `r-ds-prod` | 2 | 51.4 | 3 | 31.8 |
| 5 | `r-mle-intern` | 1 | 27.1 | 6 | 20.9 |
| 6 | `r-backend-prod` | 1 | 26.4 | 4 | 30.1 |
| 7 | `r-fe-prod` | 0 | 24.0 | 7 | 20.6 |

### Backend Engineer (`job-backend`)

- Semantic: P@1=1.00 P@3=0.67 R@3=1.00 NDCG@3=0.972 NDCG@7=0.970 pairwise=0.800
- Lexical:  P@1=1.00 P@3=0.33 NDCG@3=0.866 pairwise=0.733

| Rank | Resume | Grade | Semantic | Lexical rank | Lexical score |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `r-backend-prod` | 3 | 87.7 | 1 | 67.9 |
| 2 | `r-backend-negation` | 1 | 73.2 | 2 | 55.1 |
| 3 | `r-backend-synonym` | 2 | 71.3 | 6 | 25.3 |
| 4 | `r-backend-intern` | 1 | 54.2 | 5 | 30.4 |
| 5 | `r-fe-prod` | 0 | 52.8 | 7 | 15.0 |
| 6 | `r-de-prod` | 1 | 51.3 | 3 | 31.5 |
| 7 | `r-mle-prod` | 1 | 48.7 | 4 | 31.3 |

### Frontend Engineer (`job-frontend`)

- Semantic: P@1=1.00 P@3=1.00 R@3=0.75 NDCG@3=1.000 NDCG@7=0.997 pairwise=0.941
- Lexical:  P@1=1.00 P@3=1.00 NDCG@3=1.000 pairwise=0.882

| Rank | Resume | Grade | Semantic | Lexical rank | Lexical score |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `r-fe-prod` | 3 | 84.6 | 1 | 59.4 |
| 2 | `r-fe-synonym` | 2 | 71.5 | 4 | 25.7 |
| 3 | `r-fe-partial` | 2 | 70.4 | 2 | 45.1 |
| 4 | `r-fs-prod` | 2 | 68.7 | 3 | 26.6 |
| 5 | `r-backend-prod` | 0 | 51.6 | 5 | 19.8 |
| 6 | `r-backend-intern` | 1 | 45.3 | 7 | 12.5 |
| 7 | `r-systems-cpp` | 0 | 33.3 | 6 | 17.6 |

### Full-Stack Engineer (`job-fullstack`)

- Semantic: P@1=1.00 P@3=1.00 R@3=0.75 NDCG@3=1.000 NDCG@7=1.000 pairwise=1.000
- Lexical:  P@1=1.00 P@3=0.67 NDCG@3=0.856 pairwise=0.706

| Rank | Resume | Grade | Semantic | Lexical rank | Lexical score |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `r-fs-prod` | 3 | 84.4 | 1 | 59.5 |
| 2 | `r-fe-prod` | 2 | 70.6 | 4 | 36.2 |
| 3 | `r-backend-prod` | 2 | 65.4 | 2 | 45.4 |
| 4 | `r-fe-partial` | 2 | 58.5 | 6 | 26.3 |
| 5 | `r-backend-intern` | 1 | 55.6 | 5 | 26.3 |
| 6 | `r-mle-prod` | 1 | 54.4 | 7 | 25.4 |
| 7 | `r-da-prod` | 0 | 37.5 | 3 | 42.6 |

### MLOps Engineer (`job-mlops`)

- Semantic: P@1=1.00 P@3=0.67 R@3=0.50 NDCG@3=0.879 NDCG@7=0.956 pairwise=0.765
- Lexical:  P@1=1.00 P@3=0.67 NDCG@3=0.879 pairwise=0.706

| Rank | Resume | Grade | Semantic | Lexical rank | Lexical score |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `r-mlops-prod` | 3 | 84.7 | 1 | 65.9 |
| 2 | `r-mlops-negation` | 1 | 63.9 | 2 | 55.3 |
| 3 | `r-mle-prod` | 2 | 60.9 | 3 | 53.1 |
| 4 | `r-de-prod` | 2 | 60.7 | 6 | 35.5 |
| 5 | `r-mle-negation` | 1 | 57.4 | 4 | 44.7 |
| 6 | `r-backend-prod` | 2 | 54.5 | 5 | 43.1 |
| 7 | `r-fe-prod` | 0 | 40.3 | 7 | 19.1 |

### Data Engineer (`job-de`)

- Semantic: P@1=1.00 P@3=0.67 R@3=0.67 NDCG@3=0.762 NDCG@7=0.853 pairwise=0.824
- Lexical:  P@1=1.00 P@3=0.67 NDCG@3=0.904 pairwise=0.765

| Rank | Resume | Grade | Semantic | Lexical rank | Lexical score |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `r-de-synonym` | 2 | 81.0 | 7 | 19.9 |
| 2 | `r-de-prod` | 3 | 79.4 | 1 | 64.1 |
| 3 | `r-mle-prod` | 1 | 50.2 | 4 | 40.9 |
| 4 | `r-ds-prod` | 1 | 49.8 | 5 | 30.3 |
| 5 | `r-backend-prod` | 2 | 47.6 | 2 | 50.5 |
| 6 | `r-backend-intern` | 1 | 46.0 | 3 | 48.6 |
| 7 | `r-fe-prod` | 0 | 34.0 | 6 | 20.7 |

## Known failure-case inspection

| Pair | Lexical rank | Lexical score | Semantic rank | Semantic score |
| --- | ---: | ---: | ---: | ---: |
| `job-mle` / `r-mle-stuffing` | 1 | 56.2 | 3 | 75.7 |
| `job-mle` / `r-mle-synonym` | 7 | 2.9 | 5 | 68.5 |
| `job-mle` / `r-mle-prod` | 2 | 55.6 | 1 | 83.8 |
| `job-backend` / `r-backend-negation` | 2 | 55.1 | 2 | 73.2 |
| `job-mlops` / `r-mlops-negation` | 2 | 55.3 | 2 | 63.9 |
| `job-fullstack` / `r-da-prod` | 3 | 42.6 | 7 | 37.5 |
| `job-de` / `r-backend-prod` | 2 | 50.5 | 5 | 47.6 |
| `job-de` / `r-de-synonym` | 7 | 19.9 | 1 | 81.0 |
| `job-ds` / `r-ds-synonym` | 7 | 2.5 | 2 | 68.4 |

### Keyword stuffing

`r-mle-stuffing` moved from lexical rank **1** to semantic rank **3** on the MLE job. Semantic matching no longer puts the stuffed mismatch first.

### Synonymy

`r-mle-synonym` moved from lexical rank **7** to semantic rank **5**. Sentence embeddings recovered more of the synonym strong match.

### Negation

Backend negation `r-backend-negation`: lexical rank 2 → semantic rank 2. MLOps negation `r-mlops-negation`: lexical rank 2 → semantic rank 2. MiniLM is not a dedicated negation model; overlapping role language can still score a denied-skill resume highly.

### Related-role overlap

Data Analyst `r-da-prod` on Full-Stack: lexical rank 3 → semantic rank 7. Neighboring Python roles can still score well when the prose is about software delivery even if the labeled role differs.

### Skill-catalog misses

Data Engineer synonym `r-de-synonym`: lexical rank 7 → semantic rank 1. Semantic scoring does not require Spark/Airflow/PostgreSQL to be in the 32-skill lexicon; whether that helps is an empirical result in the table above, not an assumption.

## Improvements

- Precision@1: 0.875 → 1.000 (+0.125)
- Precision@3: 0.667 → 0.792 (+0.125)
- Recall@3: 0.562 → 0.688 (+0.125)
- NDCG@3: 0.849 → 0.900 (+0.052)
- NDCG (full pool): 0.929 → 0.956 (+0.028)
- Pairwise ordering accuracy: 0.709 → 0.865 (+0.155)

## Regressions

- No **mean** ranking metric declined on this development set.
- Per-role declines (means can still rise while one job gets worse):
- Data Engineer NDCG@3: 0.904 → 0.762
- Keyword stuffing and negation can still score highly; MLE synonym recovered only partway and can still sit below a stuffed mismatch.

## Interpretation

On this development benchmark, Semantic Matcher v0.1 improved Precision@1 relative to the frozen lexical baseline. That is not a production claim.

Do not replace the lexical baseline solely because embeddings feel more modern.
A later hybrid would need to beat **both** standalone systems on this same
v0.2 harness. This branch does not implement that hybrid.

Generated by `scripts/compare_matchers.py` (Baseline Matcher v0.1 vs Semantic Matcher v0.1).
