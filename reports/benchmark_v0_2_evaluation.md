# Baseline Matcher v0.1 on development benchmark v0.2

Synthetic resume/job pairs for a harder development benchmark. Not real candidate data. Not a production benchmark. Human-defined relevance grades are ground truth for model comparison; they are not model outputs. Legacy CSV category labels are not used.

This report is a **development error analysis**. It does **not** prove
production matching quality. Matcher weights were **not** tuned on v0.2.

## Benchmark size

- Name: `career-match-dev-benchmark-v0.2`
- Kind: development evaluation benchmark
- Jobs: **8**
- Unique synthetic resumes: **24**
- Relevance judgments: **56**
- Pool size: 7 labeled resumes per job

## Role distribution

| Job ID | Title | Pool |
| --- | --- | ---: |
| `job-mle` | Machine Learning Engineer | 7 |
| `job-ds` | Data Scientist | 7 |
| `job-da` | Data Analyst | 7 |
| `job-backend` | Backend Engineer | 7 |
| `job-frontend` | Frontend Engineer | 7 |
| `job-fullstack` | Full-Stack Engineer | 7 |
| `job-mlops` | MLOps Engineer | 7 |
| `job-de` | Data Engineer | 7 |

## Labeling scheme

Human-defined grades (not model outputs):

- `3` strong — right role family, required work largely present
- `2` moderate — related role or partial skills
- `1` weak — overlapping tools, wrong core job or seniority
- `0` mismatch — different occupation, stuffing, or unrelated stack

Binary metrics treat grades ≥ 2 as relevant. NDCG uses gain `2^rel - 1`.

| Grade | Judgments |
| ---: | ---: |
| 3 strong | 9 |
| 2 moderate | 19 |
| 1 weak | 19 |
| 0 mismatch | 9 |
| **Total** | **56** |

## Baseline configuration

- Matcher: **Baseline Matcher v0.1**
- Formula: `overall = 0.55 * tfidf_similarity + 0.45 * skill_overlap_score`
- Weights are the v0.1 named constants. **They were not retuned on v0.2.**
- Skill overlap: fraction of job catalog skills also found in the resume
- Scores: 0–100 baseline relevance, **not** a hiring probability
- Vectorizer: pair-fit TF-IDF cosine, unigrams+bigrams, English stop words

## Actual metrics (mean over 8 jobs)

| Metric | Mean |
| --- | ---: |
| Precision@1 | 0.875 |
| Precision@3 | 0.667 |
| Recall@3 | 0.562 |
| NDCG@3 | 0.849 |
| NDCG (full pool) | 0.929 |
| Pairwise ordering accuracy | 0.709 |

Precision/Recall@3 are appropriate: each job has seven labeled candidates
and typically two to four relevant (grade ≥ 2) resumes.

## Score distribution by grade

| Grade | N | Mean | Min | Max |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 9 | 26.4 | 15.0 | 56.2 |
| 1 | 19 | 33.6 | 12.5 | 55.3 |
| 2 | 19 | 32.7 | 2.5 | 53.1 |
| 3 | 9 | 52.4 | 2.9 | 67.9 |

Overlapping score ranges between grades: **0 vs 1, 0 vs 2, 0 vs 3, 1 vs 2, 1 vs 3, 2 vs 3**.
Mean score for grade 2 can sit at or below grade 1 when synonymy is
penalized and related-role keyword overlap is rewarded. That inversion
is a lexical failure, not a labeling bug.

## Per-role results

### Machine Learning Engineer (`job-mle`)

- P@1=0.00 P@3=0.33 R@3=0.33 NDCG@3=0.381 NDCG@7=0.648 pairwise=0.235

| Rank | Resume | Grade | Overall | TF-IDF | Skill overlap | Tags |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `r-mle-stuffing` | 0 | 56.2 | 20.4 | 100.0 | hard_negative, keyword_stuffing |
| 2 | `r-mle-prod` | 3 | 55.6 | 26.1 | 91.7 | strong_match |
| 3 | `r-mle-negation` | 1 | 43.6 | 17.9 | 75.0 | negation, experience_mismatch |
| 4 | `r-mle-intern` | 1 | 28.0 | 9.9 | 50.0 | experience_mismatch |
| 5 | `r-backend-prod` | 1 | 27.9 | 9.9 | 50.0 | related_role, skill_overlap_without_role_fit |
| 6 | `r-ai-apps` | 2 | 24.8 | 10.9 | 41.7 | related_role, partial_skills |
| 7 | `r-mle-synonym` | 3 | 2.9 | 5.3 | 0.0 | synonymy, role_fit_without_keywords |

Ranking issues on this job:

- P@1 miss: `r-mle-stuffing` (grade 0 mismatch) ranked first with score 56.2.
- Grade-3 `r-mle-prod` (55.6) ranked #2 below grade-0 `r-mle-stuffing` (56.2, #1).
- Grade-3 `r-mle-synonym` (2.9) ranked #7 below grade-0 `r-mle-stuffing` (56.2, #1).
- False positive in top-3: `r-mle-stuffing` grade 0 score 56.2 tags=hard_negative,keyword_stuffing.
- False positive in top-3: `r-mle-negation` grade 1 score 43.6 tags=negation,experience_mismatch.
- False negative outside top-3: `r-ai-apps` grade 2 score 24.8 tags=related_role,partial_skills.
- False negative outside top-3: `r-mle-synonym` grade 3 score 2.9 tags=synonymy,role_fit_without_keywords.

### Data Scientist (`job-ds`)

- P@1=1.00 P@3=0.67 R@3=0.50 NDCG@3=0.904 NDCG@7=0.964 pairwise=0.706

| Rank | Resume | Grade | Overall | TF-IDF | Skill overlap | Tags |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `r-ds-prod` | 3 | 58.5 | 24.6 | 100.0 | strong_match |
| 2 | `r-ds-partial` | 2 | 42.4 | 15.7 | 75.0 | partial_skills |
| 3 | `r-backend-prod` | 1 | 28.1 | 10.3 | 50.0 | related_role, skill_overlap_without_role_fit |
| 4 | `r-da-prod` | 1 | 27.3 | 8.7 | 50.0 | related_role |
| 5 | `r-mle-prod` | 2 | 26.7 | 7.7 | 50.0 | related_role |
| 6 | `r-systems-cpp` | 0 | 26.0 | 6.4 | 50.0 | hard_negative, irrelevant_shared_terms |
| 7 | `r-ds-synonym` | 2 | 2.5 | 4.5 | 0.0 | synonymy, role_fit_without_keywords |

Ranking issues on this job:

- False positive in top-3: `r-backend-prod` grade 1 score 28.1 tags=related_role,skill_overlap_without_role_fit.
- False negative outside top-3: `r-mle-prod` grade 2 score 26.7 tags=related_role.
- False negative outside top-3: `r-ds-synonym` grade 2 score 2.5 tags=synonymy,role_fit_without_keywords.

### Data Analyst (`job-da`)

- P@1=1.00 P@3=1.00 R@3=0.75 NDCG@3=1.000 NDCG@7=0.993 pairwise=0.941

| Rank | Resume | Grade | Overall | TF-IDF | Skill overlap | Tags |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `r-da-prod` | 3 | 37.4 | 19.0 | 60.0 | strong_match |
| 2 | `r-ds-partial` | 2 | 35.9 | 16.1 | 60.0 | partial_skills, related_role |
| 3 | `r-ds-prod` | 2 | 31.8 | 8.7 | 60.0 | related_role, experience_mismatch |
| 4 | `r-backend-prod` | 1 | 30.1 | 5.7 | 60.0 | skill_overlap_without_role_fit |
| 5 | `r-da-synonym` | 2 | 24.1 | 11.1 | 40.0 | synonymy, role_fit_without_keywords |
| 6 | `r-mle-intern` | 1 | 20.9 | 5.3 | 40.0 | experience_mismatch, weak_overlap |
| 7 | `r-fe-prod` | 0 | 20.6 | 4.7 | 40.0 | hard_negative |

Ranking issues on this job:

- False negative outside top-3: `r-da-synonym` grade 2 score 24.1 tags=synonymy,role_fit_without_keywords.

### Backend Engineer (`job-backend`)

- P@1=1.00 P@3=0.33 R@3=0.50 NDCG@3=0.866 NDCG@7=0.948 pairwise=0.733

| Rank | Resume | Grade | Overall | TF-IDF | Skill overlap | Tags |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `r-backend-prod` | 3 | 67.9 | 41.7 | 100.0 | strong_match |
| 2 | `r-backend-negation` | 1 | 55.1 | 18.4 | 100.0 | negation |
| 3 | `r-de-prod` | 1 | 31.5 | 11.8 | 55.6 | related_role, skill_overlap_without_role_fit |
| 4 | `r-mle-prod` | 1 | 31.3 | 11.5 | 55.6 | related_role, skill_overlap_without_role_fit |
| 5 | `r-backend-intern` | 1 | 30.4 | 9.8 | 55.6 | experience_mismatch |
| 6 | `r-backend-synonym` | 2 | 25.3 | 9.6 | 44.4 | synonymy, role_fit_without_keywords |
| 7 | `r-fe-prod` | 0 | 15.0 | 9.1 | 22.2 | hard_negative |

Ranking issues on this job:

- False positive in top-3: `r-backend-negation` grade 1 score 55.1 tags=negation.
- False positive in top-3: `r-de-prod` grade 1 score 31.5 tags=related_role,skill_overlap_without_role_fit.
- False negative outside top-3: `r-backend-synonym` grade 2 score 25.3 tags=synonymy,role_fit_without_keywords.

### Frontend Engineer (`job-frontend`)

- P@1=1.00 P@3=1.00 R@3=0.75 NDCG@3=1.000 NDCG@7=0.996 pairwise=0.882

| Rank | Resume | Grade | Overall | TF-IDF | Skill overlap | Tags |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `r-fe-prod` | 3 | 59.4 | 35.3 | 88.9 | strong_match |
| 2 | `r-fe-partial` | 2 | 45.1 | 18.3 | 77.8 | partial_skills |
| 3 | `r-fs-prod` | 2 | 26.6 | 12.1 | 44.4 | related_role |
| 4 | `r-fe-synonym` | 2 | 25.7 | 10.4 | 44.4 | synonymy, role_fit_without_keywords |
| 5 | `r-backend-prod` | 0 | 19.8 | 8.8 | 33.3 | hard_negative, related_role |
| 6 | `r-systems-cpp` | 0 | 17.6 | 4.7 | 33.3 | hard_negative, irrelevant_shared_terms |
| 7 | `r-backend-intern` | 1 | 12.5 | 4.6 | 22.2 | experience_mismatch, weak_overlap |

Ranking issues on this job:

- False negative outside top-3: `r-fe-synonym` grade 2 score 25.7 tags=synonymy,role_fit_without_keywords.

### Full-Stack Engineer (`job-fullstack`)

- P@1=1.00 P@3=0.67 R@3=0.50 NDCG@3=0.856 NDCG@7=0.963 pairwise=0.706

| Rank | Resume | Grade | Overall | TF-IDF | Skill overlap | Tags |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `r-fs-prod` | 3 | 59.5 | 26.3 | 100.0 | strong_match |
| 2 | `r-backend-prod` | 2 | 45.4 | 14.3 | 83.3 | partial_skills |
| 3 | `r-da-prod` | 0 | 42.6 | 9.3 | 83.3 | hard_negative |
| 4 | `r-fe-prod` | 2 | 36.2 | 11.2 | 66.7 | partial_skills |
| 5 | `r-backend-intern` | 1 | 26.3 | 6.9 | 50.0 | experience_mismatch |
| 6 | `r-fe-partial` | 2 | 26.3 | 6.8 | 50.0 | partial_skills |
| 7 | `r-mle-prod` | 1 | 25.4 | 5.3 | 50.0 | related_role |

Ranking issues on this job:

- False positive in top-3: `r-da-prod` grade 0 score 42.6 tags=hard_negative.
- False negative outside top-3: `r-fe-prod` grade 2 score 36.2 tags=partial_skills.
- False negative outside top-3: `r-fe-partial` grade 2 score 26.3 tags=partial_skills.

### MLOps Engineer (`job-mlops`)

- P@1=1.00 P@3=0.67 R@3=0.50 NDCG@3=0.879 NDCG@7=0.949 pairwise=0.706

| Rank | Resume | Grade | Overall | TF-IDF | Skill overlap | Tags |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `r-mlops-prod` | 3 | 65.9 | 38.1 | 100.0 | strong_match |
| 2 | `r-mlops-negation` | 1 | 55.3 | 18.8 | 100.0 | negation, partial_skills |
| 3 | `r-mle-prod` | 2 | 53.1 | 14.7 | 100.0 | related_role |
| 4 | `r-mle-negation` | 1 | 44.7 | 13.1 | 83.3 | negation |
| 5 | `r-backend-prod` | 2 | 43.1 | 10.1 | 83.3 | skill_overlap_without_role_fit, related_role |
| 6 | `r-de-prod` | 2 | 35.5 | 9.9 | 66.7 | related_role |
| 7 | `r-fe-prod` | 0 | 19.1 | 7.5 | 33.3 | hard_negative |

Ranking issues on this job:

- False positive in top-3: `r-mlops-negation` grade 1 score 55.3 tags=negation,partial_skills.
- False negative outside top-3: `r-backend-prod` grade 2 score 43.1 tags=skill_overlap_without_role_fit,related_role.
- False negative outside top-3: `r-de-prod` grade 2 score 35.5 tags=related_role.

### Data Engineer (`job-de`)

- P@1=1.00 P@3=0.67 R@3=0.67 NDCG@3=0.904 NDCG@7=0.969 pairwise=0.765

| Rank | Resume | Grade | Overall | TF-IDF | Skill overlap | Tags |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `r-de-prod` | 3 | 64.1 | 34.7 | 100.0 | strong_match |
| 2 | `r-backend-prod` | 2 | 50.5 | 10.0 | 100.0 | related_role, skill_overlap_without_role_fit |
| 3 | `r-backend-intern` | 1 | 48.6 | 6.6 | 100.0 | experience_mismatch |
| 4 | `r-mle-prod` | 1 | 40.9 | 8.9 | 80.0 | related_role |
| 5 | `r-ds-prod` | 1 | 30.3 | 6.0 | 60.0 | related_role |
| 6 | `r-fe-prod` | 0 | 20.7 | 5.0 | 40.0 | hard_negative |
| 7 | `r-de-synonym` | 2 | 19.9 | 19.8 | 20.0 | synonymy, role_fit_without_keywords |

Ranking issues on this job:

- False positive in top-3: `r-backend-intern` grade 1 score 48.6 tags=experience_mismatch.
- False negative outside top-3: `r-de-synonym` grade 2 score 19.9 tags=synonymy,role_fit_without_keywords.

## Comparison with v0.1

| | v0.1 sanity fixture | v0.2 development benchmark |
| --- | --- | --- |
| Kind | development evaluation fixture | development evaluation benchmark |
| Pairs | 16 | 56 |
| Jobs | 4 obvious role silos | 8 overlapping families |
| Hard cases | none by design | synonymy, negation, stuffing, seniority |
| Baseline P@1 | 1.000 | 0.875 |
| Baseline NDCG@full | 1.000 (k=4) | 0.929 (k=7) |

v0.1 remains a **sanity check**: the matcher should still rank constructed
strong matches above constructed mismatches on that tiny set.
v0.2 is the **comparison target** for TF-IDF, a future sentence-embedding
model, and a future hybrid ranker. Perfect v0.1 metrics were too easy to
be a useful model-selection signal.

## Error analysis

### Ranking failures, false positives, and false negatives

The lexical baseline is strong when the resume repeats the job's catalog
tokens and weak when the work is described with synonyms. Related-role
Python/SQL/Git overlap often outranks a better role fit.

### Examples where lexical overlap misleads

- **Keyword stuffing (`r-mle-stuffing` on Machine Learning Engineer).**
  Grade 0 ranks first (skill overlap 100) because the resume lists the
  entire catalog. The true strong resume (`r-mle-prod`) is second.
- **Data Analyst on Full-Stack (`r-da-prod`).** Grade 0 lands in the top-3
  via SQL/Python/Git overlap even though the work is weekly reporting.
- **Data Engineer intern (`r-backend-intern`).** Grade 1 reaches top-3 with
  catalog coverage inflated by sentences that *deny* Docker and AWS.

### Examples where synonymy hurts TF-IDF

- **`r-mle-synonym` (grade 3)** ranks last on the MLE job. The resume talks
  about neural networks, serving ML models, and cloud infrastructure
  instead of PyTorch/AWS/Docker, so both TF-IDF and skill overlap collapse.
- **`r-ds-synonym` (grade 2)** ranks last on Data Scientist for the same
  reason (statistical modeling, relational databases).
- **`r-backend-synonym` (grade 2)** sits below intern/negation/related ML
  resumes because it says REST services rather than REST APIs/FastAPI.
- **`r-de-synonym` (grade 2)** ranks last on Data Engineer; Spark/Airflow/
  PostgreSQL are also outside the 32-skill catalog even on the strong resume's
  preferred stack, so the synonym document has almost no catalog hook.
- **`r-fe-synonym`** is less damaged because the job still shares some
  generic frontend prose, but it still trails the token-matching
  partial React resume.

### Examples where negation causes a bad score

- **`r-mle-negation`** names PyTorch, Docker, Kubernetes, and AWS while
  stating *No production Docker experience* and *Have not deployed models
  to cloud infrastructure*. It outranks the AI Engineer (grade 2) and the
  synonym strong match.
- **`r-backend-negation`** scores a perfect skill-overlap 100 and ranks #2
  on Backend Engineer, above the synonym true-ish match.
- **`r-mlops-negation`** likewise hits every catalog skill, including
  Kubernetes from *Limited exposure to Kubernetes*, and ranks #2.

### Skill-catalog misses

- PostgreSQL, Spark, Airflow, Terraform, Excel/dashboards, and generic
  phrases (*REST services*, *relational databases*, *cloud infrastructure*,
  *frontend component development*) are invisible to skill overlap unless a
  32-entry alias exists.
- Catalog aliases still fire on negated mentions, so absence cannot be
  expressed in this baseline.

### Score-distribution observations

- Grade bands overlap completely. A mismatch can score above a strong match
  (stuffing 56.2 vs synonym MLE 2.9).
- Mean overall score is not monotone in grade when synonym cases sit in
  grade 2–3 and keyword-heavy weak cases sit in grade 0–1.
- Full-pool NDCG stays high (~0.93) because obvious mismatches often still
  finish last; **P@1 and P@3** are the honest stress metrics here.

## Known failure cases (summary)

1. Keyword stuffing beats a real MLE (P@1 = 0 on that job).
2. Synonym / role-fit-without-keywords resumes are systematic false negatives.
3. Negated skill mentions inflate overlap.
4. Closely related roles (backend vs MLE vs data engineer vs analyst) collapse
   when they share Python/SQL/Docker/Git.
5. Intern/seniority mismatches are barely penalized if tools are named.
6. Shared generic tokens (Git, Linux) give floor scores to mismatches.

These failures are **useful**. A future sentence-embedding or hybrid ranker
must be evaluated on this same benchmark and should improve P@1, P@3,
pairwise ordering, and synonym ranking without retconning the labels.

Generated by `scripts/evaluate_benchmark_v0_2.py` with untuned
Baseline Matcher v0.1 weights.
