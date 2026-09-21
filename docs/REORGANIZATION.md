# Reorganization record

## Preserved original work

- Three cleaned input snapshots, byte-for-byte identical to the root originals.
- Final report, presentation, and both phase PDFs, unchanged.
- Original Oracle SELECT queries and CREATE TABLE definitions extracted from code.
- Original four-round matching logic; only input/output paths were made portable.
- Final historical matching outputs for regression comparison.
- Historical notebooks and scripts, with MongoDB connection strings anonymized and notebook outputs cleared.
- Historical Oracle charts and the incomplete LaTeX draft, marked as archive material.

## Added during portfolio preparation

- English and Chinese READMEs, project walkthrough, schema diagrams, data dictionary and publication guide.
- Local SQLite execution of original SELECT queries, input validation, seven regenerated plots, summary statistics, grouped CSVs and JSONL movie export.
- Portable entry points for optional Oracle/MongoDB execution with no automatic table/collection deletion.
- Requirements, environment-variable example, Git ignore rules, six regression tests and a GitHub Actions workflow.
- Clear distinction between the original exact-match analysis and the later 802-row matching experiment.

## Corrected presentation

- Oscar membership is not described as winner status; missing records are not verified non-recognition.
- Grouped plots are not presented as statistical significance or causal evidence.
- Critic scores are not described as critic engagement counts.
- RT's 0–10 values are identified as already rescaled percentages.
- Oscar coverage through 2024, unmatched records, duplicate RT keys and missing raw-cleaning code are disclosed.
- Raw-vote Pearson correlation and the log-vote trend line are explicitly distinguished.
- The first popularity bin is labeled 2K–10K, consistent with the actual data.

## Historical declarations

The original final report contains the declaration “We did not use AI for assistance.” It is preserved as a statement in the historical course submission. This portfolio reorganization, its new documentation, code, tests and regenerated outputs were prepared with AI assistance; the report's historical declaration does not describe these additions.

The files identify a Group 1 project, but do not establish individual contributions. No authorship, personal role, grade, performance claim, or new project-wide open-source license has been invented.

## Validation

The checked-in `reports/results/summary.json` contains computed metrics. `scripts/run_matching.py` reproduces counts 787 → 798 → 800 → 802 and the final saved matching/reference CSV contents. `tests/test_reproduction.py` checks the SQL-vs-dataframe join, Oscar/sample counts, historical correlation, document coverage, genre aggregation, ambiguous key rejection and score-scale validation (six test methods).

Live Oracle/MongoDB execution remains unverified. See the [GitHub repository](https://github.com/Sabrina310/movie-ratings-analysis) and [Actions runs](https://github.com/Sabrina310/movie-ratings-analysis/actions) for publication and hosted CI status.
