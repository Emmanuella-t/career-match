# Experiments

Reserved for matching notebooks.

Standalone matchers live in `src/career_match/matching/`:

- Baseline Matcher v0.1 — TF-IDF + skill overlap
- Semantic Matcher v0.1 — MiniLM cosine similarity

Compare them with `scripts/compare_matchers.py` on v0.2. Nothing in this
folder is a production model. A hybrid is intentionally not implemented
until both standalone systems are measured.
