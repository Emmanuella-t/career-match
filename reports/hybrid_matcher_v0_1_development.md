# Hybrid Matcher v0.1 — development evaluation (v0.2)

Development relevance scores only. Not a hiring probability and not a
production quality claim. Holdout v0.3 was **not** used to choose weights.

## Frozen configuration

- Matcher: **Hybrid Matcher v0.1**
- Configuration frozen: **True**
- Frozen on: `career-match-dev-benchmark-v0.2`
- Holdout used for tuning: **False** (must remain false)
- Weights: semantic=0.60, tfidf=0.20, skill=0.20
- Components: MiniLM semantic cosine + pair-fit TF-IDF + evidence-aware skill coverage (negation + keyword-list discount + stuffing penalty)

## Selection

Candidate grid and metrics are recorded in `reports/hybrid_config_selection_v0_2.json`.

Selection rule:

1. Reject configs that rank MLE keyword stuffing at #1
2. Maximize mean pairwise ordering accuracy
3. Then maximize mean NDCG@3
4. Prefer synonym ranked above stuffing

```json
{
  "benchmark": "career-match-dev-benchmark-v0.2",
  "holdout_used_for_tuning": false,
  "selection_rule": "Reject candidates that rank MLE keyword stuffing at #1. Among the rest: maximize mean pairwise ordering accuracy, then mean NDCG@3, then prefer synonym ranked above stuffing, then lower stuffing rank.",
  "reference": {
    "lexical": {
      "pairwise": 0.7093137254901961,
      "ndcg_at_3": 0.8485131688950427,
      "precision_at_1": 0.875
    },
    "semantic": {
      "pairwise": 0.8647058823529412,
      "ndcg_at_3": 0.9004030190142933,
      "precision_at_1": 1.0
    }
  },
  "candidates": [
    {
      "label": "sem=0.60,tfidf=0.20,skill=0.20",
      "semantic_weight": 0.6,
      "tfidf_weight": 0.2,
      "skill_weight": 0.2,
      "mean_pairwise_accuracy": 0.9254901960784314,
      "mean_ndcg_at_3": 0.9478525024150641,
      "mean_precision_at_1": 1.0,
      "mean_precision_at_3": 0.875,
      "mean_recall_at_3": 0.7708333333333334,
      "mean_ndcg_full": 0.9802054135440844,
      "stuffing_rank": 7,
      "synonym_rank": 5,
      "backend_negation_rank": 2,
      "mlops_negation_rank": 3,
      "rejected": false,
      "reject_reasons": []
    },
    {
      "label": "sem=0.55,tfidf=0.25,skill=0.20",
      "semantic_weight": 0.55,
      "tfidf_weight": 0.25,
      "skill_weight": 0.2,
      "mean_pairwise_accuracy": 0.9181372549019607,
      "mean_ndcg_at_3": 0.9478525024150641,
      "mean_precision_at_1": 1.0,
      "mean_precision_at_3": 0.875,
      "mean_recall_at_3": 0.7708333333333334,
      "mean_ndcg_full": 0.9785741988010894,
      "stuffing_rank": 7,
      "synonym_rank": 6,
      "backend_negation_rank": 2,
      "mlops_negation_rank": 3,
      "rejected": false,
      "reject_reasons": []
    },
    {
      "label": "sem=0.50,tfidf=0.30,skill=0.20",
      "semantic_weight": 0.5,
      "tfidf_weight": 0.3,
      "skill_weight": 0.2,
      "mean_pairwise_accuracy": 0.9034313725490196,
      "mean_ndcg_at_3": 0.9358249324466718,
      "mean_precision_at_1": 1.0,
      "mean_precision_at_3": 0.8333333333333333,
      "mean_recall_at_3": 0.7395833333333334,
      "mean_ndcg_full": 0.9769496181048675,
      "stuffing_rank": 7,
      "synonym_rank": 6,
      "backend_negation_rank": 2,
      "mlops_negation_rank": 3,
      "rejected": false,
      "reject_reasons": []
    },
    {
      "label": "sem=0.50,tfidf=0.25,skill=0.25",
      "semantic_weight": 0.5,
      "tfidf_weight": 0.25,
      "skill_weight": 0.25,
      "mean_pairwise_accuracy": 0.8813725490196078,
      "mean_ndcg_at_3": 0.9261473944202426,
      "mean_precision_at_1": 1.0,
      "mean_precision_at_3": 0.7916666666666666,
      "mean_recall_at_3": 0.6979166666666666,
      "mean_ndcg_full": 0.9747949242330199,
      "stuffing_rank": 7,
      "synonym_rank": 6,
      "backend_negation_rank": 2,
      "mlops_negation_rank": 3,
      "rejected": false,
      "reject_reasons": []
    },
    {
      "label": "sem=0.45,tfidf=0.30,skill=0.25",
      "semantic_weight": 0.45,
      "tfidf_weight": 0.3,
      "skill_weight": 0.25,
      "mean_pairwise_accuracy": 0.8740196078431373,
      "mean_ndcg_at_3": 0.9261473944202426,
      "mean_precision_at_1": 1.0,
      "mean_precision_at_3": 0.7916666666666666,
      "mean_recall_at_3": 0.6979166666666666,
      "mean_ndcg_full": 0.9733744647379579,
      "stuffing_rank": 6,
      "synonym_rank": 7,
      "backend_negation_rank": 2,
      "mlops_negation_rank": 3,
      "rejected": false,
      "reject_reasons": []
    },
    {
      "label": "sem=0.45,tfidf=0.25,skill=0.30",
      "semantic_weight": 0.45,
      "tfidf_weight": 0.25,
      "skill_weight": 0.3,
      "mean_pairwise_accuracy": 0.8519607843137255,
      "mean_ndcg_at_3": 0.9141198244518501,
      "mean_precision_at_1": 1.0,
      "mean_precision_at_3": 0.75,
      "mean_recall_at_3": 0.65625,
      "mean_ndcg_full": 0.9696065484216891,
      "stuffing_rank": 6,
      "synonym_rank": 7,
      "backend_negation_rank": 2,
      "mlops_negation_rank": 3,
      "rejected": false,
      "reject_reasons": []
    },
    {
      "label": "sem=0.40,tfidf=0.35,skill=0.25",
      "semantic_weight": 0.4,
      "tfidf_weight": 0.35,
      "skill_weight": 0.25,
      "mean_pairwise_accuracy": 0.8666666666666667,
      "mean_ndcg_at_3": 0.9261473944202426,
      "mean_precision_at_1": 1.0,
      "mean_precision_at_3": 0.7916666666666666,
      "mean_recall_at_3": 0.6979166666666666,
      "mean_ndcg_full": 0.9720521227149876,
      "stuffing_rank": 6,
      "synonym_rank": 7,
      "backend_negation_rank": 2,
      "mlops_negation_rank": 3,
      "rejected": false,
      "reject_reasons": []
    },
    {
      "label": "sem=0.40,tfidf=0.30,skill=0.30",
      "semantic_weight": 0.4,
      "tfidf_weight": 0.3,
      "skill_weight": 0.3,
      "mean_pairwise_accuracy": 0.8519607843137255,
      "mean_ndcg_at_3": 0.9141198244518501,
      "mean_precision_at_1": 1.0,
      "mean_precision_at_3": 0.75,
      "mean_recall_at_3": 0.65625,
      "mean_ndcg_full": 0.9696065484216891,
      "stuffing_rank": 6,
      "synonym_rank": 7,
      "backend_negation_rank": 2,
      "mlops_negation_rank": 3,
      "rejected": false,
      "reject_reasons": []
    }
  ],
  "chosen": {
    "label": "sem=0.60,tfidf=0.20,skill=0.20",
    "semantic_weight": 0.6,
    "tfidf_weight": 0.2,
    "skill_weight": 0.2,
    "mean_pairwise_accuracy": 0.9254901960784314,
    "mean_ndcg_at_3": 0.9478525024150641,
    "mean_precision_at_1": 1.0,
    "mean_precision_at_3": 0.875,
    "mean_recall_at_3": 0.7708333333333334,
    "mean_ndcg_full": 0.9802054135440844,
    "stuffing_rank": 7,
    "synonym_rank": 5,
    "backend_negation_rank": 2,
    "mlops_negation_rank": 3,
    "rejected": false,
    "reject_reasons": []
  }
}
```

## v0.2 mean metrics

| Metric | Lexical | Semantic | Hybrid | Δ vs semantic |
| --- | ---: | ---: | ---: | ---: |
| Precision@1 | 0.875 | 1.000 | 1.000 | 0.000 |
| Precision@3 | 0.667 | 0.792 | 0.875 | +0.083 |
| Recall@3 | 0.562 | 0.688 | 0.771 | +0.083 |
| NDCG@3 | 0.849 | 0.900 | 0.948 | +0.047 |
| NDCG (full pool) | 0.929 | 0.956 | 0.980 | +0.024 |
| Pairwise ordering accuracy | 0.709 | 0.865 | 0.925 | +0.061 |

### Hybrid Matcher v0.1

| Metric | Mean |
| --- | ---: |
| Precision@1 | 1.000 |
| Precision@3 | 0.875 |
| Recall@3 | 0.771 |
| NDCG@3 | 0.948 |
| NDCG (full pool) | 0.980 |
| Pairwise ordering accuracy | 0.925 |

## Grade-level hybrid score distribution

| Grade | N | Mean score | Min | Max |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 9 | 33.2 | 23.4 | 41.1 |
| 1 | 19 | 43.8 | 23.1 | 64.2 |
| 2 | 19 | 52.2 | 42.0 | 61.5 |
| 3 | 9 | 70.1 | 42.1 | 81.0 |

## Known hard-case rankings (v0.2)

| Case | Lex rank | Sem rank | Hybrid rank | Hybrid score |
| --- | ---: | ---: | ---: | ---: |
| MLE keyword stuffing (`r-mle-stuffing`) | 1 | 3 | 7 | 39.2 |
| MLE synonym strong (`r-mle-synonym`) | 7 | 5 | 5 | 42.1 |
| MLE token strong (`r-mle-prod`) | 2 | 1 | 1 | 73.8 |
| Backend negation (`r-backend-negation`) | 2 | 2 | 2 | 64.2 |
| MLOps negation (`r-mlops-negation`) | 2 | 2 | 3 | 56.9 |
| DE synonym (`r-de-synonym`) | 7 | 1 | 2 | 56.5 |
| Analyst on Full-Stack (`r-da-prod`) | 3 | 7 | 7 | 41.1 |

## Per-role hybrid results

### Machine Learning Engineer (`job-mle`)

- Lexical:  P@1=0.000 P@3=0.333 NDCG@3=0.381 pairwise=0.235
- Semantic: P@1=1.000 P@3=0.333 NDCG@3=0.591 pairwise=0.588
- Hybrid:   P@1=1.000 P@3=0.667 R@3=0.667 NDCG@3=0.707 NDCG@full=0.896 pairwise=0.765

| Rank | Resume | Grade | Hybrid | Lex rank | Sem rank |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `r-mle-prod` | 3 | 73.8 | 2 | 1 |
| 2 | `r-mle-negation` | 1 | 59.5 | 3 | 2 |
| 3 | `r-ai-apps` | 2 | 48.2 | 6 | 4 |
| 4 | `r-backend-prod` | 1 | 46.6 | 5 | 7 |
| 5 | `r-mle-synonym` | 3 | 42.1 | 7 | 5 |
| 6 | `r-mle-intern` | 1 | 41.5 | 4 | 6 |
| 7 | `r-mle-stuffing` | 0 | 39.2 | 1 | 3 |

### Data Scientist (`job-ds`)

- Lexical:  P@1=1.000 P@3=0.667 NDCG@3=0.904 pairwise=0.706
- Semantic: P@1=1.000 P@3=1.000 NDCG@3=1.000 pairwise=1.000
- Hybrid:   P@1=1.000 P@3=1.000 R@3=0.750 NDCG@3=1.000 NDCG@full=0.993 pairwise=0.941

| Rank | Resume | Grade | Hybrid | Lex rank | Sem rank |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `r-ds-prod` | 3 | 70.1 | 1 | 1 |
| 2 | `r-ds-partial` | 2 | 54.0 | 2 | 3 |
| 3 | `r-mle-prod` | 2 | 43.5 | 5 | 4 |
| 4 | `r-da-prod` | 1 | 43.2 | 4 | 5 |
| 5 | `r-ds-synonym` | 2 | 42.0 | 7 | 2 |
| 6 | `r-backend-prod` | 1 | 38.4 | 3 | 6 |
| 7 | `r-systems-cpp` | 0 | 29.4 | 6 | 7 |

### Data Analyst (`job-da`)

- Lexical:  P@1=1.000 P@3=1.000 NDCG@3=1.000 pairwise=0.941
- Semantic: P@1=1.000 P@3=1.000 NDCG@3=1.000 pairwise=1.000
- Hybrid:   P@1=1.000 P@3=1.000 R@3=0.750 NDCG@3=1.000 NDCG@full=0.998 pairwise=0.941

| Rank | Resume | Grade | Hybrid | Lex rank | Sem rank |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `r-da-prod` | 3 | 61.8 | 1 | 1 |
| 2 | `r-ds-partial` | 2 | 58.3 | 2 | 2 |
| 3 | `r-da-synonym` | 2 | 48.6 | 5 | 3 |
| 4 | `r-ds-prod` | 2 | 44.5 | 3 | 4 |
| 5 | `r-backend-prod` | 1 | 29.0 | 4 | 6 |
| 6 | `r-fe-prod` | 0 | 23.4 | 7 | 7 |
| 7 | `r-mle-intern` | 1 | 23.1 | 6 | 5 |

### Backend Engineer (`job-backend`)

- Lexical:  P@1=1.000 P@3=0.333 NDCG@3=0.866 pairwise=0.733
- Semantic: P@1=1.000 P@3=0.667 NDCG@3=0.972 pairwise=0.800
- Hybrid:   P@1=1.000 P@3=0.667 R@3=1.000 NDCG@3=0.972 NDCG@full=0.975 pairwise=0.933

| Rank | Resume | Grade | Hybrid | Lex rank | Sem rank |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `r-backend-prod` | 3 | 81.0 | 1 | 1 |
| 2 | `r-backend-negation` | 1 | 64.2 | 2 | 2 |
| 3 | `r-backend-synonym` | 2 | 53.6 | 6 | 3 |
| 4 | `r-backend-intern` | 1 | 44.4 | 5 | 4 |
| 5 | `r-de-prod` | 1 | 43.0 | 3 | 6 |
| 6 | `r-mle-prod` | 1 | 42.6 | 4 | 7 |
| 7 | `r-fe-prod` | 0 | 37.9 | 7 | 5 |

### Frontend Engineer (`job-frontend`)

- Lexical:  P@1=1.000 P@3=1.000 NDCG@3=1.000 pairwise=0.882
- Semantic: P@1=1.000 P@3=1.000 NDCG@3=1.000 pairwise=0.941
- Hybrid:   P@1=1.000 P@3=1.000 R@3=0.750 NDCG@3=1.000 NDCG@full=0.997 pairwise=0.941

| Rank | Resume | Grade | Hybrid | Lex rank | Sem rank |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `r-fe-prod` | 3 | 75.6 | 1 | 1 |
| 2 | `r-fe-partial` | 2 | 61.5 | 2 | 3 |
| 3 | `r-fe-synonym` | 2 | 53.9 | 4 | 2 |
| 4 | `r-fs-prod` | 2 | 52.5 | 3 | 4 |
| 5 | `r-backend-prod` | 0 | 39.4 | 5 | 5 |
| 6 | `r-backend-intern` | 1 | 31.3 | 7 | 6 |
| 7 | `r-systems-cpp` | 0 | 26.4 | 6 | 7 |

### Full-Stack Engineer (`job-fullstack`)

- Lexical:  P@1=1.000 P@3=0.667 NDCG@3=0.856 pairwise=0.706
- Semantic: P@1=1.000 P@3=1.000 NDCG@3=1.000 pairwise=1.000
- Hybrid:   P@1=1.000 P@3=1.000 R@3=0.750 NDCG@3=1.000 NDCG@full=1.000 pairwise=1.000

| Rank | Resume | Grade | Hybrid | Lex rank | Sem rank |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `r-fs-prod` | 3 | 75.9 | 1 | 1 |
| 2 | `r-backend-prod` | 2 | 58.8 | 2 | 3 |
| 3 | `r-fe-prod` | 2 | 58.0 | 4 | 2 |
| 4 | `r-fe-partial` | 2 | 46.5 | 6 | 4 |
| 5 | `r-mle-prod` | 1 | 43.7 | 7 | 6 |
| 6 | `r-backend-intern` | 1 | 42.9 | 5 | 5 |
| 7 | `r-da-prod` | 0 | 41.1 | 3 | 7 |

### MLOps Engineer (`job-mlops`)

- Lexical:  P@1=1.000 P@3=0.667 NDCG@3=0.879 pairwise=0.706
- Semantic: P@1=1.000 P@3=0.667 NDCG@3=0.879 pairwise=0.765
- Hybrid:   P@1=1.000 P@3=0.667 R@3=0.500 NDCG@3=0.904 NDCG@full=0.982 pairwise=0.882

| Rank | Resume | Grade | Hybrid | Lex rank | Sem rank |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `r-mlops-prod` | 3 | 78.5 | 1 | 1 |
| 2 | `r-mle-prod` | 2 | 59.5 | 3 | 3 |
| 3 | `r-mlops-negation` | 1 | 56.9 | 2 | 2 |
| 4 | `r-backend-prod` | 2 | 51.4 | 5 | 6 |
| 5 | `r-de-prod` | 2 | 49.9 | 6 | 4 |
| 6 | `r-mle-negation` | 1 | 43.4 | 4 | 5 |
| 7 | `r-fe-prod` | 0 | 32.4 | 7 | 7 |

### Data Engineer (`job-de`)

- Lexical:  P@1=1.000 P@3=0.667 NDCG@3=0.904 pairwise=0.765
- Semantic: P@1=1.000 P@3=0.667 NDCG@3=0.762 pairwise=0.824
- Hybrid:   P@1=1.000 P@3=1.000 R@3=1.000 NDCG@3=1.000 NDCG@full=1.000 pairwise=1.000

| Rank | Resume | Grade | Hybrid | Lex rank | Sem rank |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `r-de-prod` | 3 | 72.4 | 1 | 2 |
| 2 | `r-de-synonym` | 2 | 56.5 | 7 | 1 |
| 3 | `r-backend-prod` | 2 | 50.5 | 2 | 5 |
| 4 | `r-mle-prod` | 1 | 47.9 | 4 | 3 |
| 5 | `r-backend-intern` | 1 | 46.7 | 3 | 6 |
| 6 | `r-ds-prod` | 1 | 43.1 | 5 | 4 |
| 7 | `r-fe-prod` | 0 | 29.4 | 6 | 7 |

## Negation and stuffing behavior

- Narrative negation phrases (for example `No production Docker`, `Limited exposure to Kubernetes`) zero out that skill for coverage even when it still appears in a Skills list.
- Skills that appear only under a `Skills:` heading receive weight 0.45.
- Resumes with ≥16 distinct catalog skills are treated as stuffing-likely: skill channel ×0.25 and overall score ×0.72.

## Regressions and honesty notes

- Hybrid may still leave backend/MLOps negation mid-ranked when prose overlaps the job family.
- Synonym recovery is incomplete; lexical channels still dilute pure embedding synonym wins on some roles.
- Beating semantic on every metric is not required; the goal is better overall ordering with improved stuffing failure behavior.

Generated by `scripts/evaluate_hybrid.py --development`.
