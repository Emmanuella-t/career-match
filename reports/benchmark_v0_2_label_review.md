# v0.2 benchmark label review aid

Status: awaiting/available for manual review

This table lists all 56 construction-time relevance judgments in
`data/evaluation/dev_benchmark_v0_2.json`. It is a review aid for the
project owner. It does **not** mark the labels as human-reviewed,
independently annotated, or expert-labeled.

Labels are **manually specified synthetic relevance judgments**
(development targets), not independently validated ground truth.

Provenance:

- Synthetic benchmark
- Constructed for controlled development evaluation
- No real candidate data
- No production hiring labels
- No independent annotator agreement
- Intended for model comparison and error analysis

Do not treat a completed read-through of this file as rater agreement
unless a separate review process records that explicitly.

| Job | Resume ID | Grade | Rationale | Case tag(s) |
| --- | --- | ---: | --- | --- |
| Machine Learning Engineer (`job-mle`) | `r-mle-prod` | 3 | 3 — five years shipping Deep Learning, NLP, Docker, and AWS; matches the required modeling role. | strong_match |
| Machine Learning Engineer (`job-mle`) | `r-mle-synonym` | 3 | 3 — same responsibility profile (neural training and serving ML models on cloud infrastructure) stated with synonyms rather than PyTorch/AWS tokens. | synonymy, role_fit_without_keywords |
| Machine Learning Engineer (`job-mle`) | `r-ai-apps` | 2 | 2 — related AI Engineer profile with Python and some NLP, but hosted-LLM apps rather than training/shipping Deep Learning. | related_role, partial_skills |
| Machine Learning Engineer (`job-mle`) | `r-mle-negation` | 1 | 1 — names PyTorch and TensorFlow but explicitly has no production Docker and has not deployed models to cloud infrastructure. | negation, experience_mismatch |
| Machine Learning Engineer (`job-mle`) | `r-mle-intern` | 1 | 1 — intern-level coursework for a role asking 4+ years of production modeling. | experience_mismatch |
| Machine Learning Engineer (`job-mle`) | `r-backend-prod` | 1 | 1 — strong Python/Docker/AWS overlap but a backend REST API profile, not model training. | related_role, skill_overlap_without_role_fit |
| Machine Learning Engineer (`job-mle`) | `r-mle-stuffing` | 0 | 0 — keyword stuffing of the whole catalog without evidence of modeling work; hard negative. | hard_negative, keyword_stuffing |
| Data Scientist (`job-ds`) | `r-ds-prod` | 3 | 3 — four years of Python/pandas/SQL/scikit-learn experimentation, which is the job. | strong_match |
| Data Scientist (`job-ds`) | `r-ds-synonym` | 2 | 2 — role fit via statistical modeling and relational databases, but no named pandas/SQL/scikit-learn. | synonymy, role_fit_without_keywords |
| Data Scientist (`job-ds`) | `r-ds-partial` | 2 | 2 — correct general data role with Python/SQL/pandas but missing scikit-learn experimentation. | partial_skills |
| Data Scientist (`job-ds`) | `r-mle-prod` | 2 | 2 — related ML Engineer who can program and model, but core work is Deep Learning serving rather than product experiments. | related_role |
| Data Scientist (`job-ds`) | `r-da-prod` | 1 | 1 — closely related Data Analyst; reporting/SQL without experimental design or scikit-learn. | related_role |
| Data Scientist (`job-ds`) | `r-backend-prod` | 1 | 1 — Python and SQL for services, not analysis or experimentation. | related_role, skill_overlap_without_role_fit |
| Data Scientist (`job-ds`) | `r-systems-cpp` | 0 | 0 — C++/Kubernetes systems work with no analytics stack; mismatch. | hard_negative, irrelevant_shared_terms |
| Data Analyst (`job-da`) | `r-da-prod` | 3 | 3 — three years of SQL dashboards and light Python reporting, matching the analyst seat. | strong_match |
| Data Analyst (`job-da`) | `r-da-synonym` | 2 | 2 — business reporting and relational databases without naming SQL/Python. | synonymy, role_fit_without_keywords |
| Data Analyst (`job-da`) | `r-ds-partial` | 2 | 2 — Python/SQL/pandas wrangling can cover analyst work but is heavier on engineering extracts than dashboards. | partial_skills, related_role |
| Data Analyst (`job-da`) | `r-ds-prod` | 2 | 2 — Data Scientist overqualified for reporting; can do the work but the profile is experimental ML, not weekly KPIs. | related_role, experience_mismatch |
| Data Analyst (`job-da`) | `r-backend-prod` | 1 | 1 — SQL appears in APIs, not business reporting. | skill_overlap_without_role_fit |
| Data Analyst (`job-da`) | `r-mle-intern` | 1 | 1 — intern Python coursework, not reporting experience. | experience_mismatch, weak_overlap |
| Data Analyst (`job-da`) | `r-fe-prod` | 0 | 0 — frontend React profile with no reporting work; mismatch. | hard_negative |
| Backend Engineer (`job-backend`) | `r-backend-prod` | 3 | 3 — five years of FastAPI/Django REST APIs, SQL, Docker, and AWS. | strong_match |
| Backend Engineer (`job-backend`) | `r-backend-synonym` | 2 | 2 — REST services, relational databases, and cloud infrastructure describe the role without FastAPI/SQL/AWS tokens. | synonymy, role_fit_without_keywords |
| Backend Engineer (`job-backend`) | `r-de-prod` | 1 | 1 — Data Engineer vs backend: Python/SQL/Docker overlap, pipeline responsibilities instead of REST APIs. | related_role, skill_overlap_without_role_fit |
| Backend Engineer (`job-backend`) | `r-mle-prod` | 1 | 1 — Python backend-adjacent stack (Docker/AWS) but ML training responsibilities, not API product work. | related_role, skill_overlap_without_role_fit |
| Backend Engineer (`job-backend`) | `r-backend-negation` | 1 | 1 — FastAPI/Django present but no production Docker and has not deployed to cloud infrastructure. | negation |
| Backend Engineer (`job-backend`) | `r-backend-intern` | 1 | 1 — intern-level Flask/SQL for a role asking 4+ years. | experience_mismatch |
| Backend Engineer (`job-backend`) | `r-fe-prod` | 0 | 0 — frontend engineer; no Python services. Hard negative only via shared Git. | hard_negative |
| Frontend Engineer (`job-frontend`) | `r-fe-prod` | 3 | 3 — TypeScript React Next.js HTML CSS JavaScript Git at 4 years. | strong_match |
| Frontend Engineer (`job-frontend`) | `r-fe-synonym` | 2 | 2 — frontend component development without naming React/Next.js/TypeScript. | synonymy, role_fit_without_keywords |
| Frontend Engineer (`job-frontend`) | `r-fe-partial` | 2 | 2 — correct UI role missing TypeScript and Next.js. | partial_skills |
| Frontend Engineer (`job-frontend`) | `r-fs-prod` | 2 | 2 — full-stack with real React, but half the work is Python APIs the JD does not want as core. | related_role |
| Frontend Engineer (`job-frontend`) | `r-backend-intern` | 1 | 1 — junior backend intern; may have touched HTML, not a frontend product engineer. | experience_mismatch, weak_overlap |
| Frontend Engineer (`job-frontend`) | `r-backend-prod` | 0 | 0 — Python API engineer with no UI framework work; shared Git only. | hard_negative, related_role |
| Frontend Engineer (`job-frontend`) | `r-systems-cpp` | 0 | 0 — C++/Kubernetes; no JavaScript. Shared Linux/Git should not dominate. | hard_negative, irrelevant_shared_terms |
| Full-Stack Engineer (`job-fullstack`) | `r-fs-prod` | 3 | 3 — React plus Python REST APIs and SQL, which is the job. | strong_match |
| Full-Stack Engineer (`job-fullstack`) | `r-fe-prod` | 2 | 2 — strong frontend, missing Python REST APIs. | partial_skills |
| Full-Stack Engineer (`job-fullstack`) | `r-backend-prod` | 2 | 2 — strong Python APIs, missing React/TypeScript UI. | partial_skills |
| Full-Stack Engineer (`job-fullstack`) | `r-fe-partial` | 2 | 2 — React/HTML/CSS without TypeScript depth and without backend. | partial_skills |
| Full-Stack Engineer (`job-fullstack`) | `r-backend-intern` | 1 | 1 — intern backend only; not full-stack seniority. | experience_mismatch |
| Full-Stack Engineer (`job-fullstack`) | `r-mle-prod` | 1 | 1 — Python present, but ML training rather than product UI+API delivery. | related_role |
| Full-Stack Engineer (`job-fullstack`) | `r-da-prod` | 0 | 0 — analyst reporting, not full-stack product engineering. | hard_negative |
| MLOps Engineer (`job-mlops`) | `r-mlops-prod` | 3 | 3 — five years of Docker/Kubernetes/AWS serving ML models. | strong_match |
| MLOps Engineer (`job-mlops`) | `r-mle-prod` | 2 | 2 — ML Engineer with Docker/AWS and some Kubernetes, but core identity is training not MLOps. | related_role |
| MLOps Engineer (`job-mlops`) | `r-backend-prod` | 2 | 2 — Docker/AWS/Linux production skills without model-serving ownership. | skill_overlap_without_role_fit, related_role |
| MLOps Engineer (`job-mlops`) | `r-de-prod` | 2 | 2 — pipeline infra overlap (Docker/AWS) without serving ML models. | related_role |
| MLOps Engineer (`job-mlops`) | `r-mlops-negation` | 1 | 1 — Python/Docker/AWS but limited Kubernetes and has not owned serving ML models. | negation, partial_skills |
| MLOps Engineer (`job-mlops`) | `r-mle-negation` | 1 | 1 — names Docker/Kubernetes/AWS while stating no production Docker and no cloud deploy. | negation |
| MLOps Engineer (`job-mlops`) | `r-fe-prod` | 0 | 0 — frontend profile; mismatch. | hard_negative |
| Data Engineer (`job-de`) | `r-de-prod` | 3 | 3 — Python/SQL/PostgreSQL/Spark/Airflow/Docker/AWS pipelines. | strong_match |
| Data Engineer (`job-de`) | `r-de-synonym` | 2 | 2 — data pipelines and relational warehouses on cloud infrastructure without Spark/SQL/AWS tokens. | synonymy, role_fit_without_keywords |
| Data Engineer (`job-de`) | `r-backend-prod` | 2 | 2 — Python/SQL/Docker/AWS services, not warehouse pipelines; related but incomplete. | related_role, skill_overlap_without_role_fit |
| Data Engineer (`job-de`) | `r-ds-prod` | 1 | 1 — analysis/experimentation, not pipeline engineering. | related_role |
| Data Engineer (`job-de`) | `r-mle-prod` | 1 | 1 — Python/Docker/AWS for training jobs, not warehouse orchestration. | related_role |
| Data Engineer (`job-de`) | `r-backend-intern` | 1 | 1 — intern SQL/Python, not 3+ years of pipelines. | experience_mismatch |
| Data Engineer (`job-de`) | `r-fe-prod` | 0 | 0 — frontend engineer; mismatch. | hard_negative |

