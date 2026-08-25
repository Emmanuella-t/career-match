# Development evaluation fixture

This directory holds **synthetic** resume/job pairs used to check that the
lexical baseline ranks obvious matches above obvious mismatches.

- File: `dev_relevance_fixture.json`
- Kind: `development evaluation fixture`
- Not real candidate data
- Not a production benchmark
- Does **not** use `legacy/resume_dataset.csv` category labels as relevance

Grades: 3 strong, 2 moderate, 1 weak, 0 mismatch. Binary ranking metrics treat
grades ≥ 2 as relevant.
