# Hybrid Matcher v0.1 — frozen holdout evaluation (v0.3)

Single holdout snapshot after configuration freeze on v0.2.
Not a production hiring claim. Synthetic benchmark only.

## Frozen configuration

- Matcher: **Hybrid Matcher v0.1**
- Weights: semantic=0.60, tfidf=0.20, skill=0.20
- Configuration frozen before this run: **True**
- Tuned on: `career-match-dev-benchmark-v0.2` only
- **v0.3 was not used for tuning**
- Weights, negation rules, and evidence rules were not changed after seeing these holdout numbers

## Holdout identity

- Name: `career-match-holdout-benchmark-v0.3`
- Kind: frozen holdout evaluation benchmark
- Jobs: 9; resumes: 29; judgments: 72
- SHA-256: `3373f60631e4994444ba888f25827054c5597343a349b16705cb5633e90c7c2d`
- Matches manifest: **True**

## Mean metrics (v0.3)

| Metric | Lexical | Semantic | Hybrid | Δ vs semantic |
| --- | ---: | ---: | ---: | ---: |
| Precision@1 | 1.000 | 1.000 | 1.000 | 0.000 |
| Precision@3 | 0.630 | 0.778 | 0.778 | 0.000 |
| Recall@3 | 0.472 | 0.583 | 0.583 | 0.000 |
| NDCG@3 | 0.739 | 0.892 | 0.848 | -0.044 |
| NDCG (full pool) | 0.882 | 0.951 | 0.946 | -0.005 |
| Pairwise ordering accuracy | 0.573 | 0.804 | 0.824 | +0.020 |

## Per-role results

### Machine Learning Engineer (`hold-mle`)

- Lexical:  P@1=1.000 P@3=0.333 NDCG@3=0.581 pairwise=0.348
- Semantic: P@1=1.000 P@3=0.333 NDCG@3=0.581 pairwise=0.435
- Hybrid:   P@1=1.000 P@3=0.333 R@3=0.250 NDCG@3=0.629 NDCG@full=0.868 pairwise=0.609

| Rank | Resume | Grade | Hybrid | Lex rank | Sem rank |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `h-mle-core` | 3 | 75.7 | 1 | 1 |
| 2 | `h-mle-notebook` | 1 | 55.9 | 3 | 3 |
| 3 | `h-mle-junior` | 1 | 48.7 | 5 | 4 |
| 4 | `h-nlp-core` | 2 | 44.6 | 4 | 8 |
| 5 | `h-aai-core` | 2 | 44.2 | 7 | 6 |
| 6 | `h-be-core` | 1 | 44.1 | 6 | 7 |
| 7 | `h-mle-paraphrase` | 3 | 42.2 | 8 | 5 |
| 8 | `h-stuffing` | 0 | 34.5 | 2 | 2 |

### Applied AI Engineer (`hold-aai`)

- Lexical:  P@1=1.000 P@3=1.000 NDCG@3=0.805 pairwise=0.696
- Semantic: P@1=1.000 P@3=1.000 NDCG@3=1.000 pairwise=1.000
- Hybrid:   P@1=1.000 P@3=1.000 R@3=0.750 NDCG@3=0.805 NDCG@full=0.909 pairwise=0.783

| Rank | Resume | Grade | Hybrid | Lex rank | Sem rank |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `h-aai-core` | 3 | 74.2 | 1 | 1 |
| 2 | `h-mle-core` | 2 | 57.6 | 3 | 3 |
| 3 | `h-fs-core` | 2 | 53.6 | 2 | 4 |
| 4 | `h-be-core` | 1 | 52.3 | 4 | 6 |
| 5 | `h-weak-practice` | 1 | 44.6 | 5 | 5 |
| 6 | `h-da-core` | 1 | 40.1 | 7 | 7 |
| 7 | `h-aai-synonym` | 3 | 39.1 | 8 | 2 |
| 8 | `h-systems` | 0 | 34.7 | 6 | 8 |

### Data Scientist (`hold-ds`)

- Lexical:  P@1=1.000 P@3=0.667 NDCG@3=0.904 pairwise=0.636
- Semantic: P@1=1.000 P@3=1.000 NDCG@3=0.858 pairwise=0.909
- Hybrid:   P@1=1.000 P@3=1.000 R@3=0.750 NDCG@3=1.000 NDCG@full=0.993 pairwise=0.955

| Rank | Resume | Grade | Hybrid | Lex rank | Sem rank |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `h-ds-core` | 3 | 66.1 | 1 | 2 |
| 2 | `h-ds-partial` | 2 | 59.1 | 2 | 3 |
| 3 | `h-ds-paraphrase` | 2 | 57.4 | 8 | 1 |
| 4 | `h-da-core` | 1 | 49.0 | 4 | 4 |
| 5 | `h-mle-core` | 2 | 42.3 | 6 | 5 |
| 6 | `h-be-core` | 1 | 40.8 | 3 | 6 |
| 7 | `h-mle-junior` | 1 | 32.8 | 7 | 7 |
| 8 | `h-systems` | 0 | 27.7 | 5 | 8 |

### Data Analyst (`hold-da`)

- Lexical:  P@1=1.000 P@3=0.667 NDCG@3=0.686 pairwise=0.636
- Semantic: P@1=1.000 P@3=1.000 NDCG@3=1.000 pairwise=0.909
- Hybrid:   P@1=1.000 P@3=1.000 R@3=0.750 NDCG@3=1.000 NDCG@full=0.999 pairwise=0.955

| Rank | Resume | Grade | Hybrid | Lex rank | Sem rank |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `h-da-core` | 3 | 61.1 | 3 | 1 |
| 2 | `h-da-synonym` | 2 | 48.8 | 7 | 2 |
| 3 | `h-ds-partial` | 2 | 48.3 | 5 | 3 |
| 4 | `h-ds-core` | 2 | 43.5 | 1 | 4 |
| 5 | `h-be-core` | 1 | 38.6 | 2 | 8 |
| 6 | `h-swe-general` | 1 | 36.7 | 4 | 5 |
| 7 | `h-fe-only` | 0 | 35.3 | 6 | 6 |
| 8 | `h-weak-practice` | 1 | 23.5 | 8 | 7 |

### Backend Engineer (`hold-be`)

- Lexical:  P@1=1.000 P@3=0.333 NDCG@3=0.591 pairwise=0.391
- Semantic: P@1=1.000 P@3=0.667 NDCG@3=0.862 pairwise=0.739
- Hybrid:   P@1=1.000 P@3=0.667 R@3=0.500 NDCG@3=0.707 NDCG@full=0.909 pairwise=0.739

| Rank | Resume | Grade | Hybrid | Lex rank | Sem rank |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `h-be-core` | 3 | 68.4 | 1 | 1 |
| 2 | `h-be-negation` | 1 | 63.1 | 2 | 2 |
| 3 | `h-fs-core` | 2 | 48.8 | 5 | 4 |
| 4 | `h-be-synonym` | 3 | 46.5 | 8 | 3 |
| 5 | `h-mle-core` | 1 | 46.4 | 4 | 8 |
| 6 | `h-be-junior` | 1 | 41.6 | 7 | 5 |
| 7 | `h-de-core` | 2 | 40.1 | 6 | 7 |
| 8 | `h-stuffing` | 0 | 24.8 | 3 | 6 |

### Full-Stack Engineer (`hold-fs`)

- Lexical:  P@1=1.000 P@3=0.667 NDCG@3=0.818 pairwise=0.636
- Semantic: P@1=1.000 P@3=0.667 NDCG@3=0.904 pairwise=0.864
- Hybrid:   P@1=1.000 P@3=1.000 R@3=0.750 NDCG@3=1.000 NDCG@full=0.993 pairwise=0.955

| Rank | Resume | Grade | Hybrid | Lex rank | Sem rank |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `h-fs-core` | 3 | 72.4 | 1 | 1 |
| 2 | `h-fe-only` | 2 | 58.2 | 3 | 2 |
| 3 | `h-be-core` | 2 | 53.9 | 4 | 4 |
| 4 | `h-swe-general` | 1 | 49.7 | 5 | 3 |
| 5 | `h-fs-synonym` | 2 | 42.7 | 7 | 5 |
| 6 | `h-aai-core` | 1 | 41.4 | 8 | 6 |
| 7 | `h-da-core` | 1 | 36.8 | 6 | 8 |
| 8 | `h-stuffing` | 0 | 27.1 | 2 | 7 |

### MLOps Engineer (`hold-mlops`)

- Lexical:  P@1=1.000 P@3=0.667 NDCG@3=0.707 pairwise=0.652
- Semantic: P@1=1.000 P@3=0.667 NDCG@3=0.923 pairwise=0.826
- Hybrid:   P@1=1.000 P@3=0.667 R@3=0.500 NDCG@3=0.707 NDCG@full=0.910 pairwise=0.739

| Rank | Resume | Grade | Hybrid | Lex rank | Sem rank |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `h-mlops-core` | 3 | 70.2 | 1 | 1 |
| 2 | `h-mlops-negation` | 1 | 51.4 | 2 | 3 |
| 3 | `h-be-core` | 2 | 47.6 | 3 | 6 |
| 4 | `h-mlops-synonym` | 3 | 47.2 | 6 | 2 |
| 5 | `h-mle-core` | 1 | 47.2 | 4 | 5 |
| 6 | `h-de-core` | 2 | 44.7 | 5 | 4 |
| 7 | `h-fe-only` | 0 | 33.2 | 7 | 7 |
| 8 | `h-mle-junior` | 1 | 25.7 | 8 | 8 |

### Data Engineer (`hold-de`)

- Lexical:  P@1=1.000 P@3=0.667 NDCG@3=0.904 pairwise=0.682
- Semantic: P@1=1.000 P@3=0.667 NDCG@3=0.904 pairwise=0.773
- Hybrid:   P@1=1.000 P@3=0.333 R@3=0.250 NDCG@3=0.782 NDCG@full=0.939 pairwise=0.727

| Rank | Resume | Grade | Hybrid | Lex rank | Sem rank |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `h-de-core` | 3 | 72.7 | 1 | 1 |
| 2 | `h-da-core` | 1 | 55.6 | 3 | 3 |
| 3 | `h-ds-partial` | 1 | 52.3 | 4 | 4 |
| 4 | `h-be-core` | 2 | 51.9 | 2 | 7 |
| 5 | `h-de-synonym` | 2 | 51.9 | 8 | 2 |
| 6 | `h-mlops-core` | 2 | 49.1 | 6 | 5 |
| 7 | `h-weak-practice` | 1 | 41.7 | 5 | 6 |
| 8 | `h-systems` | 0 | 32.7 | 7 | 8 |

### NLP Engineer (`hold-nlp`)

- Lexical:  P@1=1.000 P@3=0.667 NDCG@3=0.658 pairwise=0.478
- Semantic: P@1=1.000 P@3=1.000 NDCG@3=1.000 pairwise=0.783
- Hybrid:   P@1=1.000 P@3=1.000 R@3=0.750 NDCG@3=1.000 NDCG@full=0.994 pairwise=0.957

| Rank | Resume | Grade | Hybrid | Lex rank | Sem rank |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `h-nlp-core` | 3 | 76.6 | 1 | 1 |
| 2 | `h-nlp-synonym` | 3 | 51.2 | 8 | 2 |
| 3 | `h-mle-core` | 2 | 50.8 | 3 | 3 |
| 4 | `h-mle-notebook` | 1 | 45.9 | 4 | 5 |
| 5 | `h-aai-core` | 2 | 41.2 | 5 | 6 |
| 6 | `h-ds-core` | 1 | 33.6 | 7 | 7 |
| 7 | `h-be-junior` | 1 | 28.1 | 6 | 8 |
| 8 | `h-stuffing` | 0 | 26.8 | 2 | 4 |

## Improvements vs semantic

- Pairwise: +0.020 vs semantic

## Regressions vs semantic

- NDCG@3: -0.044 vs semantic
- NDCG (full pool): -0.005 vs semantic
- Applied AI Engineer pairwise: 1.000 → 0.783
- Applied AI Engineer NDCG@3: 1.000 → 0.805
- Backend Engineer NDCG@3: 0.862 → 0.707
- MLOps Engineer pairwise: 0.826 → 0.739
- MLOps Engineer NDCG@3: 0.923 → 0.707
- Data Engineer pairwise: 0.773 → 0.727
- Data Engineer NDCG@3: 0.904 → 0.782

## Interpretation

Hybrid Matcher v0.1 mixes semantic similarity with TF-IDF and evidence-aware skill coverage. On this frozen holdout it should be read as a controlled comparison, not a production readiness claim.
Winning every metric is not required.

## Limitations

- Negation rules are phrase-window heuristics, not full linguistic negation
- Stuffing detection uses catalog-skill count thresholds
- MiniLM still confuses adjacent role families
- Synthetic labels are not independently validated ground truth

Generated by `scripts/evaluate_hybrid.py --holdout`.
