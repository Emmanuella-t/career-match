# Legacy dataset audit

Generated deterministically by `scripts/audit_legacy_dataset.py`.
This report describes the original Resume Screening CSV. It is **not**
a matching-model evaluation.

## Snapshot

- Path: `legacy/resume_dataset.csv`
- Rows: **169**
- Distinct job categories: **25**
- Unique resume texts: **166**
- Duplicate resume texts: **3**
- Empty resumes: **0**
- Resume length (characters): min 129, median 2310, mean 2912.3, max 14609
- Most common category: Java Developer (14)
- Least common category: PMO (3)

## Encoding quality

These counts are computed independently from the loaded CSV. They are
not interchangeable: a non-ASCII row is not automatically a mojibake
row, and the three markers are tracked separately.

- Rows containing any non-ASCII character: **128**
- Rows containing marker `â`: **124**
- Rows containing marker `Ã`: **6**
- Rows containing replacement marker `�`: **0**
- Rows containing at least one suspicious encoding marker (`â`, `Ã`, or `�`): **125**

## Label distribution

| Category | Count | Share |
| --- | ---: | ---: |
| Java Developer | 14 | 8.3% |
| Database | 11 | 6.5% |
| HR | 11 | 6.5% |
| Advocate | 10 | 5.9% |
| Data Science | 10 | 5.9% |
| Automation Testing | 7 | 4.1% |
| DevOps Engineer | 7 | 4.1% |
| DotNet Developer | 7 | 4.1% |
| Hadoop | 7 | 4.1% |
| Testing | 7 | 4.1% |
| Arts | 6 | 3.6% |
| Business Analyst | 6 | 3.6% |
| Civil Engineer | 6 | 3.6% |
| Health and fitness | 6 | 3.6% |
| Python Developer | 6 | 3.6% |
| SAP Developer | 6 | 3.6% |
| Blockchain | 5 | 3.0% |
| ETL Developer | 5 | 3.0% |
| Electrical Engineering | 5 | 3.0% |
| Mechanical Engineer | 5 | 3.0% |
| Network Security Engineer | 5 | 3.0% |
| Sales | 5 | 3.0% |
| Web Designing | 5 | 3.0% |
| Operations Manager | 4 | 2.4% |
| PMO | 3 | 1.8% |

## Implications for Career Match

- The source problem is **resume category classification**, not
  resume-to-job matching. Labels are coarse job families, not ranked
  (resume, job) pairs.
- 169 rows across 25 classes is too small and too imbalanced for a
  production matcher. Several classes have only 3–5 examples.
- Duplicate resumes will leak across a naive random split.
- Encoding damage is widespread: **125 of 169** rows
  contain at least one suspicious encoding marker (`â`, `Ã`, or `�`).
  Parsers must normalize text; do not treat the CSV as clean Unicode.
- The next ML milestone should define a matching task and split
  policy **before** training embedding models.
