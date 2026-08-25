# Holdout benchmark v0.3 — pre-hybrid snapshot

Synthetic resume/job pairs constructed for a frozen holdout evaluation before Career Match hybrid-matcher development. Not real candidate data. Not production hiring labels. Not production ground truth. Relevance grades are manually specified synthetic relevance judgments, not independently validated ground truth. No independent annotator agreement. Intended for controlled model comparison only. v0.3 was created before development or tuning of the future Career Match hybrid matcher and should remain frozen during that milestone. Legacy CSV category labels are not used.

This report records **unchanged** Lexical Baseline Matcher v0.1 and
Semantic Matcher v0.1 on the frozen holdout set. It does **not** propose
model changes, does **not** tune weights, and does **not** introduce a hybrid.
The holdout JSON was not modified after these scores were computed.

## Benchmark

- Name: `career-match-holdout-benchmark-v0.3`
- Version: **0.3**
- Kind: frozen holdout evaluation benchmark
- Jobs: **9**
- Unique synthetic resumes: **29**
- Judgments: **72**
- Roles: Machine Learning Engineer, Applied AI Engineer, Data Scientist, Data Analyst, Backend Engineer, Full-Stack Engineer, MLOps Engineer, Data Engineer, NLP Engineer
- SHA-256: `685d458e0c485afc9018c43d49f696c9b2783c85a637d85f1534bc759aa2f492`
- Checksum purpose: reproducibility (detect accidental edits), not security

## Provenance

- Synthetic benchmark
- No real candidate data
- No real hiring outcomes
- No independent annotator agreement
- Not production ground truth
- Intended for controlled model comparison
- Created before hybrid-matcher development; remain frozen during that milestone
- v0.2 remains the development/error-analysis benchmark

## Grade distribution

| Grade | Label | Count |
| ---: | --- | ---: |
| 3 | strong | 14 |
| 2 | moderate | 22 |
| 1 | weak | 27 |
| 0 | mismatch | 9 |

## Lexical Baseline Matcher v0.1 (mean over jobs)

- Formula unchanged: `overall = 0.55 * tfidf + 0.45 * skill_overlap`
- Weights were **not** tuned on v0.3.

| Metric | Mean |
| --- | ---: |
| Precision@1 | 1.000 |
| Precision@3 | 0.630 |
| Recall@3 | 0.472 |
| NDCG@3 | 0.739 |
| NDCG (full pool) | 0.882 |
| Pairwise ordering accuracy | 0.573 |

## Semantic Matcher v0.1 (mean over jobs)

- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- Standalone cosine similarity; lexicon not used; not mixed with TF-IDF.

| Metric | Mean |
| --- | ---: |
| Precision@1 | 1.000 |
| Precision@3 | 0.778 |
| Recall@3 | 0.583 |
| NDCG@3 | 0.892 |
| NDCG (full pool) | 0.951 |
| Pairwise ordering accuracy | 0.804 |

## Side-by-side (holdout)

Delta = semantic - lexical. Not a production quality claim.

| Metric | Lexical | Semantic | Δ |
| --- | ---: | ---: | ---: |
| Precision@1 | 1.000 | 1.000 | 0.000 |
| Precision@3 | 0.630 | 0.778 | +0.148 |
| Recall@3 | 0.472 | 0.583 | +0.111 |
| NDCG@3 | 0.739 | 0.892 | +0.153 |
| NDCG (full pool) | 0.882 | 0.951 | +0.069 |
| Pairwise ordering accuracy | 0.573 | 0.804 | +0.231 |

## Per-role metrics

### Machine Learning Engineer (`hold-mle`)

- Lexical:  P@1=1.000 P@3=0.333 R@3=0.250 NDCG@3=0.581 NDCG@full=0.834 pairwise=0.348
- Semantic: P@1=1.000 P@3=0.333 R@3=0.250 NDCG@3=0.581 NDCG@full=0.850 pairwise=0.435

| Rank | Resume | Grade | Lexical | Semantic rank | Semantic |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `h-mle-core` | 3 | 57.8 | 1 | 85.1 |
| 2 | `h-stuffing` | 0 | 49.9 | 2 | 70.5 |
| 3 | `h-mle-notebook` | 1 | 38.1 | 3 | 68.3 |
| 4 | `h-nlp-core` | 2 | 32.1 | 8 | 51.5 |
| 5 | `h-mle-junior` | 1 | 30.7 | 4 | 64.3 |
| 6 | `h-be-core` | 1 | 30.5 | 7 | 51.6 |
| 7 | `h-aai-core` | 2 | 23.0 | 6 | 57.1 |
| 8 | `h-mle-paraphrase` | 3 | 9.3 | 5 | 63.8 |

### Applied AI Engineer (`hold-aai`)

- Lexical:  P@1=1.000 P@3=1.000 R@3=0.750 NDCG@3=0.805 NDCG@full=0.900 pairwise=0.696
- Semantic: P@1=1.000 P@3=1.000 R@3=0.750 NDCG@3=1.000 NDCG@full=1.000 pairwise=1.000

| Rank | Resume | Grade | Lexical | Semantic rank | Semantic |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `h-aai-core` | 3 | 56.0 | 1 | 83.7 |
| 2 | `h-fs-core` | 2 | 49.8 | 4 | 53.1 |
| 3 | `h-mle-core` | 2 | 49.4 | 3 | 60.0 |
| 4 | `h-be-core` | 1 | 48.1 | 6 | 51.9 |
| 5 | `h-weak-practice` | 1 | 46.9 | 5 | 52.1 |
| 6 | `h-systems` | 0 | 32.7 | 8 | 40.1 |
| 7 | `h-da-core` | 1 | 32.6 | 7 | 43.1 |
| 8 | `h-aai-synonym` | 3 | 3.5 | 2 | 63.0 |

### Data Scientist (`hold-ds`)

- Lexical:  P@1=1.000 P@3=0.667 R@3=0.500 NDCG@3=0.904 NDCG@full=0.954 pairwise=0.636
- Semantic: P@1=1.000 P@3=1.000 R@3=0.750 NDCG@3=0.858 NDCG@full=0.877 pairwise=0.909

| Rank | Resume | Grade | Lexical | Semantic rank | Semantic |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `h-ds-core` | 3 | 58.0 | 2 | 69.0 |
| 2 | `h-ds-partial` | 2 | 54.0 | 3 | 59.8 |
| 3 | `h-be-core` | 1 | 31.4 | 6 | 45.4 |
| 4 | `h-da-core` | 1 | 31.1 | 4 | 59.2 |
| 5 | `h-systems` | 0 | 30.4 | 8 | 27.7 |
| 6 | `h-mle-core` | 2 | 30.4 | 5 | 48.4 |
| 7 | `h-mle-junior` | 1 | 29.2 | 7 | 40.6 |
| 8 | `h-ds-paraphrase` | 2 | 26.3 | 1 | 77.4 |

### Data Analyst (`hold-da`)

- Lexical:  P@1=1.000 P@3=0.667 R@3=0.500 NDCG@3=0.686 NDCG@full=0.787 pairwise=0.636
- Semantic: P@1=1.000 P@3=1.000 R@3=0.750 NDCG@3=1.000 NDCG@full=0.997 pairwise=0.909

| Rank | Resume | Grade | Lexical | Semantic rank | Semantic |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `h-ds-core` | 2 | 49.7 | 4 | 44.7 |
| 2 | `h-be-core` | 1 | 48.1 | 8 | 29.1 |
| 3 | `h-da-core` | 3 | 43.7 | 1 | 70.8 |
| 4 | `h-swe-general` | 1 | 38.4 | 5 | 37.9 |
| 5 | `h-ds-partial` | 2 | 37.6 | 3 | 53.1 |
| 6 | `h-fe-only` | 0 | 37.4 | 6 | 31.6 |
| 7 | `h-da-synonym` | 2 | 30.9 | 2 | 59.6 |
| 8 | `h-weak-practice` | 1 | 24.1 | 7 | 30.7 |

### Backend Engineer (`hold-be`)

- Lexical:  P@1=1.000 P@3=0.333 R@3=0.250 NDCG@3=0.591 NDCG@full=0.840 pairwise=0.391
- Semantic: P@1=1.000 P@3=0.667 R@3=0.500 NDCG@3=0.862 NDCG@full=0.924 pairwise=0.739

| Rank | Resume | Grade | Lexical | Semantic rank | Semantic |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `h-be-core` | 3 | 55.3 | 1 | 74.5 |
| 2 | `h-be-negation` | 1 | 49.9 | 2 | 72.6 |
| 3 | `h-stuffing` | 0 | 47.2 | 6 | 49.5 |
| 4 | `h-mle-core` | 1 | 40.8 | 8 | 47.8 |
| 5 | `h-fs-core` | 2 | 31.9 | 4 | 58.4 |
| 6 | `h-de-core` | 2 | 31.2 | 7 | 48.0 |
| 7 | `h-be-junior` | 1 | 21.4 | 5 | 57.6 |
| 8 | `h-be-synonym` | 3 | 18.0 | 3 | 65.3 |

### Full-Stack Engineer (`hold-fs`)

- Lexical:  P@1=1.000 P@3=0.667 R@3=0.500 NDCG@3=0.818 NDCG@full=0.929 pairwise=0.636
- Semantic: P@1=1.000 P@3=0.667 R@3=0.500 NDCG@3=0.904 NDCG@full=0.981 pairwise=0.864

| Rank | Resume | Grade | Lexical | Semantic rank | Semantic |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `h-fs-core` | 3 | 49.5 | 1 | 85.6 |
| 2 | `h-stuffing` | 0 | 48.5 | 7 | 53.8 |
| 3 | `h-fe-only` | 2 | 36.4 | 2 | 70.9 |
| 4 | `h-be-core` | 2 | 34.2 | 4 | 65.0 |
| 5 | `h-swe-general` | 1 | 27.5 | 3 | 66.3 |
| 6 | `h-da-core` | 1 | 26.4 | 8 | 42.4 |
| 7 | `h-fs-synonym` | 2 | 19.6 | 5 | 57.2 |
| 8 | `h-aai-core` | 1 | 19.1 | 6 | 55.5 |

### MLOps Engineer (`hold-mlops`)

- Lexical:  P@1=1.000 P@3=0.667 R@3=0.500 NDCG@3=0.707 NDCG@full=0.885 pairwise=0.652
- Semantic: P@1=1.000 P@3=0.667 R@3=0.500 NDCG@3=0.923 NDCG@full=0.980 pairwise=0.826

| Rank | Resume | Grade | Lexical | Semantic rank | Semantic |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `h-mlops-core` | 3 | 54.5 | 1 | 78.8 |
| 2 | `h-mlops-negation` | 1 | 48.9 | 3 | 56.0 |
| 3 | `h-be-core` | 2 | 44.1 | 6 | 50.0 |
| 4 | `h-mle-core` | 1 | 32.6 | 5 | 55.4 |
| 5 | `h-de-core` | 2 | 30.2 | 4 | 55.4 |
| 6 | `h-mlops-synonym` | 3 | 23.5 | 2 | 62.7 |
| 7 | `h-fe-only` | 0 | 22.6 | 7 | 39.1 |
| 8 | `h-mle-junior` | 1 | 15.5 | 8 | 37.0 |

### Data Engineer (`hold-de`)

- Lexical:  P@1=1.000 P@3=0.667 R@3=0.500 NDCG@3=0.904 NDCG@full=0.958 pairwise=0.682
- Semantic: P@1=1.000 P@3=0.667 R@3=0.500 NDCG@3=0.904 NDCG@full=0.967 pairwise=0.773

| Rank | Resume | Grade | Lexical | Semantic rank | Semantic |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `h-de-core` | 3 | 56.2 | 1 | 85.6 |
| 2 | `h-be-core` | 2 | 48.6 | 7 | 51.0 |
| 3 | `h-da-core` | 1 | 38.2 | 3 | 64.9 |
| 4 | `h-ds-partial` | 1 | 37.4 | 4 | 60.0 |
| 5 | `h-weak-practice` | 1 | 37.0 | 6 | 51.8 |
| 6 | `h-mlops-core` | 2 | 36.8 | 5 | 55.0 |
| 7 | `h-systems` | 0 | 36.0 | 8 | 32.7 |
| 8 | `h-de-synonym` | 2 | 11.6 | 2 | 79.4 |

### NLP Engineer (`hold-nlp`)

- Lexical:  P@1=1.000 P@3=0.667 R@3=0.500 NDCG@3=0.658 NDCG@full=0.850 pairwise=0.478
- Semantic: P@1=1.000 P@3=1.000 R@3=0.750 NDCG@3=1.000 NDCG@full=0.983 pairwise=0.783

| Rank | Resume | Grade | Lexical | Semantic rank | Semantic |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `h-nlp-core` | 3 | 62.6 | 1 | 83.7 |
| 2 | `h-stuffing` | 0 | 48.3 | 4 | 52.5 |
| 3 | `h-mle-core` | 2 | 44.1 | 3 | 53.1 |
| 4 | `h-mle-notebook` | 1 | 41.2 | 5 | 50.3 |
| 5 | `h-aai-core` | 2 | 32.3 | 6 | 45.5 |
| 6 | `h-be-junior` | 1 | 20.7 | 8 | 35.5 |
| 7 | `h-ds-core` | 1 | 20.4 | 7 | 41.2 |
| 8 | `h-nlp-synonym` | 3 | 18.9 | 2 | 72.6 |

## Notable observed failures

Recorded for later reference only. Do not optimize matchers against these
holdout errors in this milestone.

- Lexical synonym under-rank on Machine Learning Engineer: stuffing `h-stuffing` (49.9) above synonym `h-mle-paraphrase` (9.3).
- Lexical synonym under-rank on Backend Engineer: stuffing `h-stuffing` (47.2) above synonym `h-be-synonym` (18.0).
- Lexical synonym under-rank on Full-Stack Engineer: stuffing `h-stuffing` (48.5) above synonym `h-fs-synonym` (19.6).
- Lexical synonym under-rank on NLP Engineer: stuffing `h-stuffing` (48.3) above synonym `h-nlp-synonym` (18.9).
- Semantic high score on negation case Backend Engineer/`h-be-negation`: 72.6 (rank 2).

### Case inspection table

| Pair | Lexical rank | Lexical score | Semantic rank | Semantic score |
| --- | ---: | ---: | ---: | ---: |
| `hold-mle` / `h-stuffing` | 2 | 49.9 | 2 | 70.5 |
| `hold-mle` / `h-mle-paraphrase` | 8 | 9.3 | 5 | 63.8 |
| `hold-mle` / `h-mle-core` | 1 | 57.8 | 1 | 85.1 |
| `hold-mle` / `h-mle-notebook` | 3 | 38.1 | 3 | 68.3 |
| `hold-be` / `h-be-negation` | 2 | 49.9 | 2 | 72.6 |
| `hold-mlops` / `h-mlops-negation` | 2 | 48.9 | 3 | 56.0 |
| `hold-de` / `h-de-synonym` | 8 | 11.6 | 2 | 79.4 |
| `hold-fs` / `h-da-core` | 6 | 26.4 | 8 | 42.4 |
| `hold-nlp` / `h-nlp-synonym` | 8 | 18.9 | 2 | 72.6 |

## Notes

- No matcher code was changed for this snapshot.
- No weights were tuned on v0.3.
- No hybrid matcher was added.
- These numbers are a frozen pre-hybrid baseline, not production KPIs.

Generated by `scripts/evaluate_holdout_v0_3.py` (Baseline Matcher v0.1 vs Semantic Matcher v0.1).
