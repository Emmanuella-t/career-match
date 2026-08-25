# Holdout benchmark v0.3 label review aid

Status: awaiting/available for manual review

This table lists all construction-time relevance judgments in
`data/evaluation/holdout_benchmark_v0_3.json`. It is a review aid.
It does **not** mark the labels as independently reviewed,
expert-labeled, or production hiring labels.

Labels are **manually specified synthetic relevance judgments**,
not independently validated ground truth.

Provenance:

- Synthetic benchmark
- No real candidate data
- No real hiring outcomes
- No independent annotator agreement
- Not production ground truth
- Intended for controlled model comparison
- Frozen before hybrid-matcher development

| Job | Resume ID | Grade | Rationale | Case tags |
| --- | --- | ---: | --- | --- |
| Machine Learning Engineer (`hold-mle`) | `h-mle-core` | 3 | 3 — 5y production predictive modeling with PyTorch/scikit-learn and inference packaging matches the MLE seat. Manually specified synthetic relevance judgment. | strong_match |
| Machine Learning Engineer (`hold-mle`) | `h-mle-paraphrase` | 3 | 3 — Same modeling and model-serving responsibilities with synonym vocabulary (neural estimators, model serving). Manually specified synthetic relevance judgment. | synonymy, role_fit_without_keywords |
| Machine Learning Engineer (`hold-mle`) | `h-nlp-core` | 2 | 2 — Strong NLP/PyTorch adjacent engineer; related family but narrower than general MLE scope. Manually specified synthetic relevance judgment. | related_role, adjacent_role |
| Machine Learning Engineer (`hold-mle`) | `h-aai-core` | 2 | 2 — Applied AI product integrator with Python/Docker overlap; more hosted models than training ownership. Manually specified synthetic relevance judgment. | related_role, partial_skills |
| Machine Learning Engineer (`hold-mle`) | `h-mle-notebook` | 1 | 1 — Names training tools but explicitly lacks production Docker and inference-service ownership (negation). Manually specified synthetic relevance judgment. | negation, experience_mismatch |
| Machine Learning Engineer (`hold-mle`) | `h-mle-junior` | 1 | 1 — Sub-year internship versus 4+ year production modeling requirement (seniority mismatch). Manually specified synthetic relevance judgment. | seniority_mismatch |
| Machine Learning Engineer (`hold-mle`) | `h-be-core` | 1 | 1 — Strong Python/Docker/Git overlap but core work is REST APIs, not predictive modeling. Manually specified synthetic relevance judgment. | related_role, skill_overlap_without_role_fit |
| Machine Learning Engineer (`hold-mle`) | `h-stuffing` | 0 | 0 — Keyword stuffing across the catalog without evidence of modeling work; hard negative. Manually specified synthetic relevance judgment. | hard_negative, keyword_stuffing |
| Applied AI Engineer (`hold-aai`) | `h-aai-core` | 3 | 3 — Four years integrating hosted models into Python RESTful services with Docker/Git matches Applied AI. Manually specified synthetic relevance judgment. | strong_match |
| Applied AI Engineer (`hold-aai`) | `h-aai-synonym` | 3 | 3 — Equivalent product-AI integration described via REST services and hosted language systems. Manually specified synthetic relevance judgment. | synonymy, role_fit_without_keywords |
| Applied AI Engineer (`hold-aai`) | `h-mle-core` | 2 | 2 — Related ML engineer who can ship services, but profile centers on training rather than product AI wiring. Manually specified synthetic relevance judgment. | related_role |
| Applied AI Engineer (`hold-aai`) | `h-fs-core` | 2 | 2 — Full-stack Python/REST overlap; only partial AI feature ownership. Manually specified synthetic relevance judgment. | partial_skills, related_role |
| Applied AI Engineer (`hold-aai`) | `h-be-core` | 1 | 1 — Backend REST strength without applied AI/foundation-model integration evidence. Manually specified synthetic relevance judgment. | skill_overlap_without_role_fit |
| Applied AI Engineer (`hold-aai`) | `h-weak-practice` | 1 | 1 — Lists ML/Docker/cloud tools with weak practical delivery evidence. Manually specified synthetic relevance judgment. | weak_practical_experience |
| Applied AI Engineer (`hold-aai`) | `h-da-core` | 1 | 1 — Analyst reporting profile adjacent only via Python/Git; wrong core responsibilities. Manually specified synthetic relevance judgment. | adjacent_role |
| Applied AI Engineer (`hold-aai`) | `h-systems` | 0 | 0 — C++/cluster systems work with no AI product integration; mismatch. Manually specified synthetic relevance judgment. | hard_negative, irrelevant_shared_terms |
| Data Scientist (`hold-ds`) | `h-ds-core` | 3 | 3 — Four years of experiments and tabular scikit-learn modeling is the Data Scientist job. Manually specified synthetic relevance judgment. | strong_match |
| Data Scientist (`hold-ds`) | `h-ds-paraphrase` | 2 | 2 — Role fit via predictive modeling and relational data stores without naming pandas/scikit-learn. Manually specified synthetic relevance judgment. | synonymy, role_fit_without_keywords |
| Data Scientist (`hold-ds`) | `h-ds-partial` | 2 | 2 — Correct data family with Python/SQL/pandas but missing scikit-learn experimentation depth. Manually specified synthetic relevance judgment. | partial_skills |
| Data Scientist (`hold-ds`) | `h-mle-core` | 2 | 2 — Related ML engineer; core work is deep training/serving rather than product experiments. Manually specified synthetic relevance judgment. | related_role, adjacent_role |
| Data Scientist (`hold-ds`) | `h-da-core` | 1 | 1 — Closely related analyst; reporting/SQL without experimental design. Manually specified synthetic relevance judgment. | related_role |
| Data Scientist (`hold-ds`) | `h-be-core` | 1 | 1 — Python/SQL for services, not analysis or experimentation. Manually specified synthetic relevance judgment. | skill_overlap_without_role_fit |
| Data Scientist (`hold-ds`) | `h-mle-junior` | 1 | 1 — Junior internship coursework for a 3+ year scientist seat. Manually specified synthetic relevance judgment. | seniority_mismatch |
| Data Scientist (`hold-ds`) | `h-systems` | 0 | 0 — C++ systems profile with no analytics stack; hard negative. Manually specified synthetic relevance judgment. | hard_negative, irrelevant_shared_terms |
| Data Analyst (`hold-da`) | `h-da-core` | 3 | 3 — Three years of SQL dashboards and light Python reporting matches the analyst seat. Manually specified synthetic relevance judgment. | strong_match |
| Data Analyst (`hold-da`) | `h-da-synonym` | 2 | 2 — Business reporting and relational data stores without naming SQL/Python. Manually specified synthetic relevance judgment. | synonymy, role_fit_without_keywords |
| Data Analyst (`hold-da`) | `h-ds-partial` | 2 | 2 — Python/SQL wrangling can cover analyst work but leans engineering extracts over KPI packs. Manually specified synthetic relevance judgment. | partial_skills, related_role |
| Data Analyst (`hold-da`) | `h-ds-core` | 2 | 2 — Data Scientist overqualified for reporting; experimental ML profile rather than weekly KPIs. Manually specified synthetic relevance judgment. | related_role, seniority_mismatch |
| Data Analyst (`hold-da`) | `h-be-core` | 1 | 1 — SQL appears in APIs, not stakeholder reporting. Manually specified synthetic relevance judgment. | skill_overlap_without_role_fit |
| Data Analyst (`hold-da`) | `h-weak-practice` | 1 | 1 — Workshop familiarity without sustained reporting ownership. Manually specified synthetic relevance judgment. | weak_practical_experience |
| Data Analyst (`hold-da`) | `h-swe-general` | 1 | 1 — General software engineer with thin analytics evidence. Manually specified synthetic relevance judgment. | adjacent_role |
| Data Analyst (`hold-da`) | `h-fe-only` | 0 | 0 — Frontend React profile with no reporting work; mismatch. Manually specified synthetic relevance judgment. | hard_negative |
| Backend Engineer (`hold-be`) | `h-be-core` | 3 | 3 — Five years FastAPI/SQL/Docker/Linux services match the Backend Engineer role. Manually specified synthetic relevance judgment. | strong_match |
| Backend Engineer (`hold-be`) | `h-be-synonym` | 3 | 3 — RESTful services on relational stores and public cloud platforms with synonym phrasing. Manually specified synthetic relevance judgment. | synonymy, role_fit_without_keywords |
| Backend Engineer (`hold-be`) | `h-fs-core` | 2 | 2 — Full-stack engineer with real Python REST delivery; partial UI focus beyond backend seat. Manually specified synthetic relevance judgment. | related_role, partial_skills |
| Backend Engineer (`hold-be`) | `h-de-core` | 2 | 2 — Adjacent data engineer with Python/SQL/Docker; pipelines rather than product APIs. Manually specified synthetic relevance judgment. | adjacent_role |
| Backend Engineer (`hold-be`) | `h-be-negation` | 1 | 1 — Names Docker/Kubernetes/AWS but denies production container and cloud deployment experience. Manually specified synthetic relevance judgment. | negation, experience_mismatch |
| Backend Engineer (`hold-be`) | `h-be-junior` | 1 | 1 — One-year internship versus 4+ year backend ownership requirement. Manually specified synthetic relevance judgment. | seniority_mismatch |
| Backend Engineer (`hold-be`) | `h-mle-core` | 1 | 1 — Shared Python/Docker/Git but modeling focus, not service reliability ownership. Manually specified synthetic relevance judgment. | related_role, skill_overlap_without_role_fit |
| Backend Engineer (`hold-be`) | `h-stuffing` | 0 | 0 — Catalog keyword stuffing without service delivery evidence; hard negative. Manually specified synthetic relevance judgment. | hard_negative, keyword_stuffing |
| Full-Stack Engineer (`hold-fs`) | `h-fs-core` | 3 | 3 — Four years spanning TypeScript React and Python REST/SQL matches Full-Stack. Manually specified synthetic relevance judgment. | strong_match |
| Full-Stack Engineer (`hold-fs`) | `h-fs-synonym` | 2 | 2 — Interfaces plus HTTP backends described without React/TypeScript brand tokens. Manually specified synthetic relevance judgment. | synonymy, role_fit_without_keywords |
| Full-Stack Engineer (`hold-fs`) | `h-be-core` | 2 | 2 — Strong backend half of the stack; missing demonstrated React/TypeScript UI depth. Manually specified synthetic relevance judgment. | partial_skills, related_role |
| Full-Stack Engineer (`hold-fs`) | `h-fe-only` | 2 | 2 — Strong frontend half; missing Python REST ownership. Manually specified synthetic relevance judgment. | partial_skills |
| Full-Stack Engineer (`hold-fs`) | `h-aai-core` | 1 | 1 — Python services overlap but AI integration focus, not full UI+API product ownership. Manually specified synthetic relevance judgment. | adjacent_role |
| Full-Stack Engineer (`hold-fs`) | `h-da-core` | 1 | 1 — Analyst tools overlap thinly; wrong product engineering responsibilities. Manually specified synthetic relevance judgment. | skill_overlap_without_role_fit |
| Full-Stack Engineer (`hold-fs`) | `h-swe-general` | 1 | 1 — General software engineer with incomplete full-stack evidence. Manually specified synthetic relevance judgment. | weak_practical_experience, partial_skills |
| Full-Stack Engineer (`hold-fs`) | `h-stuffing` | 0 | 0 — Keyword stuffing listing React/Python/SQL without shipped product evidence. Manually specified synthetic relevance judgment. | hard_negative, keyword_stuffing |
| MLOps Engineer (`hold-mlops`) | `h-mlops-core` | 3 | 3 — Five years operating Docker/Kubernetes/AWS inference fleets matches MLOps. Manually specified synthetic relevance judgment. | strong_match |
| MLOps Engineer (`hold-mlops`) | `h-mlops-synonym` | 3 | 3 — Inference services on public cloud with container orchestration phrased as synonyms. Manually specified synthetic relevance judgment. | synonymy, role_fit_without_keywords |
| MLOps Engineer (`hold-mlops`) | `h-de-core` | 2 | 2 — Related platform/pipeline engineer with Docker/AWS; less model-serving ownership. Manually specified synthetic relevance judgment. | related_role, adjacent_role |
| MLOps Engineer (`hold-mlops`) | `h-be-core` | 2 | 2 — Backend container/cloud overlap; not dedicated inference-platform ownership. Manually specified synthetic relevance judgment. | partial_skills, related_role |
| MLOps Engineer (`hold-mlops`) | `h-mlops-negation` | 1 | 1 — Mentions Kubernetes while admitting limited orchestration and no production inference ownership. Manually specified synthetic relevance judgment. | negation, experience_mismatch |
| MLOps Engineer (`hold-mlops`) | `h-mle-core` | 1 | 1 — Modeler who packages Docker jobs but does not own serving fleets. Manually specified synthetic relevance judgment. | adjacent_role, skill_overlap_without_role_fit |
| MLOps Engineer (`hold-mlops`) | `h-mle-junior` | 1 | 1 — Junior internship seniority mismatch for 4+ year MLOps seat. Manually specified synthetic relevance judgment. | seniority_mismatch |
| MLOps Engineer (`hold-mlops`) | `h-fe-only` | 0 | 0 — Frontend-only profile; hard negative for MLOps. Manually specified synthetic relevance judgment. | hard_negative |
| Data Engineer (`hold-de`) | `h-de-core` | 3 | 3 — Four years Python/SQL/Spark/Airflow warehouse pipelines match Data Engineer. Manually specified synthetic relevance judgment. | strong_match |
| Data Engineer (`hold-de`) | `h-de-synonym` | 2 | 2 — Pipelines into relational warehouses via distributed processing without Spark/AWS tokens. Manually specified synthetic relevance judgment. | synonymy, role_fit_without_keywords, catalog_miss_phrasing |
| Data Engineer (`hold-de`) | `h-be-core` | 2 | 2 — Adjacent backend engineer with Python/SQL/Docker; APIs rather than batch warehouses. Manually specified synthetic relevance judgment. | related_role, adjacent_role |
| Data Engineer (`hold-de`) | `h-mlops-core` | 2 | 2 — Related platform engineer; inference fleets rather than analytical pipeline ownership. Manually specified synthetic relevance judgment. | related_role |
| Data Engineer (`hold-de`) | `h-ds-partial` | 1 | 1 — Python/SQL wrangling without distributed pipeline ownership. Manually specified synthetic relevance judgment. | partial_skills |
| Data Engineer (`hold-de`) | `h-da-core` | 1 | 1 — Reporting analyst adjacent via SQL; wrong core pipeline responsibilities. Manually specified synthetic relevance judgment. | adjacent_role |
| Data Engineer (`hold-de`) | `h-weak-practice` | 1 | 1 — Cloud/Docker workshop familiarity without pipeline delivery evidence. Manually specified synthetic relevance judgment. | weak_practical_experience |
| Data Engineer (`hold-de`) | `h-systems` | 0 | 0 — C++ systems work without warehouse pipelines; hard negative. Manually specified synthetic relevance judgment. | hard_negative, irrelevant_shared_terms |
| NLP Engineer (`hold-nlp`) | `h-nlp-core` | 3 | 3 — Four years PyTorch NLP with packaged inference matches the NLP Engineer seat. Manually specified synthetic relevance judgment. | strong_match |
| NLP Engineer (`hold-nlp`) | `h-nlp-synonym` | 3 | 3 — Text understanding and sequence models with inference services in synonym vocabulary. Manually specified synthetic relevance judgment. | synonymy, role_fit_without_keywords |
| NLP Engineer (`hold-nlp`) | `h-mle-core` | 2 | 2 — Related ML engineer with PyTorch; broader modeling than dedicated NLP focus. Manually specified synthetic relevance judgment. | related_role, adjacent_role |
| NLP Engineer (`hold-nlp`) | `h-aai-core` | 2 | 2 — Applied AI integrator overlapping language features; less sequence-model ownership. Manually specified synthetic relevance judgment. | related_role, partial_skills |
| NLP Engineer (`hold-nlp`) | `h-mle-notebook` | 1 | 1 — Names NLP/PyTorch tools but lacks production packaging (negation/experience gap). Manually specified synthetic relevance judgment. | negation, experience_mismatch |
| NLP Engineer (`hold-nlp`) | `h-ds-core` | 1 | 1 — Tabular experimentation rather than text understanding systems. Manually specified synthetic relevance judgment. | adjacent_role, skill_overlap_without_role_fit |
| NLP Engineer (`hold-nlp`) | `h-be-junior` | 1 | 1 — Junior backend internship; seniority and domain mismatch. Manually specified synthetic relevance judgment. | seniority_mismatch |
| NLP Engineer (`hold-nlp`) | `h-stuffing` | 0 | 0 — Keyword stuffing including NLP tokens without text-system delivery evidence. Manually specified synthetic relevance judgment. | hard_negative, keyword_stuffing |
