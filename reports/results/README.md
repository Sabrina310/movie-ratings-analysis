# Reproduced results

`summary.json` is the checked-in metrics snapshot generated from `data/input/` using the original exact title/year join.

Running `python scripts/reproduce.py` also creates the following Git-ignored derived files:

| File | Content |
| --- | --- |
| `rq1.csv` | IMDb and RT audience scores for 787 matched films |
| `rq2.csv` | All 10,147 films with optional Oscar IDs |
| `rq3.csv` | Vote counts and RT critic scores for 787 matched films |
| `rq2_genre_popularity.csv` | 125 genre/popularity/Oscar groups, with mean scores and counts |
| `rq3_vote_bins.csv` | Mean critic scores and counts in logarithmic vote bins |
| `merged_movies.jsonl` | 10,147 documents with stable IMDb IDs and nested rating fields |

Seven reproducible figures are stored in `../figures/`. Local checks passed on Python 3.11 with the versions in `requirements.txt`; the six test methods cover joins, document structure, aggregation counts, key ambiguity, score scaling, and the final historical matching reference.

Pearson correlation for raw vote counts is 0.1425; the plotted trend is fitted against log10(votes), whose correlation is 0.0766. Neither is evidence of causation. Oscar-group mean differences are descriptive and subject to the snapshot's incomplete coverage.
