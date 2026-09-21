# Data provenance and dictionary

## Saved snapshots

| File in `data/input/` | Rows | Key | Observed coverage |
| --- | ---: | --- | --- |
| `clean_movies.csv` | 10,147 | `tconst`; also unique title/year | 2016–2025; at least 2,000 votes |
| `clean_oscar.csv` | 494 | `FilmId` | `Year` 2016–2024 |
| `clean_rotten_tomatoes.csv` | 1,107 | Intended title/year; two duplicated key groups | 2016–2025; scores already 0–10 |

These are recovered project snapshots, not fresh downloads. Collection dates and exact upstream versions were not preserved. The full upstream data and original first-stage cleaning scripts are absent.

The original report cites these sources (links transcribed from the report):

- [IMDb datasets](https://datasets.imdbws.com/)
- [Rotten Tomatoes critics and audience scores — Mate Papava, Kaggle](https://www.kaggle.com/datasets/matepapava/rotten-tomatoes-critics-and-audience-scores)
- [The Oscar Award — Kaggle](https://www.kaggle.com/datasets/unanimad/the-oscar-award)

Upstream content retains its respective terms. No new license is granted for these data by this repository; see [NOTICE](../NOTICE.md).

## Fields

| Dataset | Field | Meaning |
| --- | --- | --- |
| IMDb | `tconst` | IMDb title ID, string, e.g. `tt7286456` |
| IMDb | `primaryTitle` | Previously standardized movie title |
| IMDb | `startYear` | Movie release year |
| IMDb | `genres` | Comma-separated genres; split into an array for MongoDB |
| IMDb | `averageRating` | IMDb mean user rating, 0–10 |
| IMDb | `numVotes` | Number of IMDb votes; popularity proxy, not viewers or revenue |
| Oscars | `Category` | One retained category after film-level deduplication; not a complete list |
| Oscars | `Year` | Year retained by the historical cleanup; exact award/release-year interpretation cannot be reconstructed from the saved script set |
| Oscars | `Film` | Film title as stored in the Oscar snapshot |
| Oscars | `FilmId` | IMDb title ID |
| RT | `title`, `year` | Standardized title and release year used for joins |
| RT | `audience_score` | Audience percentage already divided by 10 |
| RT | `critics_score` | Critics percentage already divided by 10; not a review count |
| Matching | `imdb_id` | Assigned IMDb ID, missing if not matched |
| Matching | `relaxed_title` | Simplified title used by rounds 3 and 4 |
| Review | `score` | RapidFuzz token-sort similarity, 0–100; not a calibrated probability |

Do not divide RT scores by 10 a second time. Equal numeric scales do not imply equivalent measurement: an approval percentage is not the same statistic as an average rating.

## Joins and exclusions

The baseline retains all 10,147 IMDb movies. Oscar foreign-key filtering retains 348 of 494 records and excludes 146 outside the IMDb sample. RT title/year filtering retains 787 of 1,107 rows and excludes 320. RQ1/RQ3 use the matched RT subset; RQ2 uses all IMDb movies via a left join.

RT contains duplicate title/year rows for `the current war` (2019) and `what remains` (2022), each with conflicting scores. Neither title/year key appears in the baseline IMDb join. The new loader rejects ambiguous matched keys if a different snapshot makes them match.

Four-stage matching produces 802 assigned rows and 305 unmatched rows. Five review candidates remain among the unmatched rows; they are not accepted matches. Only the final original matching, review, and unmatched files are retained under `data/reference/`; all intermediate outputs regenerate under `data/processed/`.

## Limits of interpretation

- The 2,000-vote cutoff and missing-data removal introduce selection effects.
- Title/year matching can miss alternate titles or release-year differences; fuzzy matches can be wrong.
- `oscar = false` means no matching record in this snapshot, not verified absence of Oscar recognition. Coverage ends in 2024 and is incomplete for 2025 films.
- A film-level deduplicated Oscar file cannot support award counts or winner classification.
- Exploding genres counts a multi-genre film in multiple groups. Genre-group counts must not be summed as a unique-film total.
- Grouped averages are descriptive; small bins may be unstable. Counts are included in generated grouped tables.
- No regression significance test, causal model, prediction benchmark, or database performance benchmark was implemented.
