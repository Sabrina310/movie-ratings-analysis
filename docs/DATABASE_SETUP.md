# Optional Oracle and MongoDB execution

The default `python scripts/reproduce.py` requires neither service. The commands below are for reproducing the original database approaches on services you provide. Install dependencies first:

```sh
python -m pip install -r requirements-databases.txt
```

Scripts read OS environment variables. `.env.example` documents their names; copying it to `.env` does **not** load it automatically.

## Oracle

Use a dedicated empty schema with permission to create tables. Example in PowerShell:

```powershell
$env:ORACLE_USER = 'your_schema'
$env:ORACLE_DSN = 'localhost:1522/stu'
python scripts/run_oracle.py --load
```

The password is requested through a hidden prompt unless `ORACLE_PASSWORD` is already set. Replace the DSN with your own server/service. The historical project used a local forwarded service at port 1522; the original tunnel configuration was not saved.

`--load` validates the inputs, refuses existing project tables, creates the schema from `sql/oracle_schema.sql`, and inserts 10,147 Movies, 348 Oscars and 787 RottenTomatoes rows. It never drops tables or purges a recycle bin. Oracle DDL commits independently: a failed first import may leave created tables, so repair the dedicated schema explicitly before retrying. A normal rerun omits `--load`:

```sh
python scripts/run_oracle.py
```

Three query CSVs are written under `reports/results/oracle/`.

## MongoDB

Example for an existing local MongoDB service:

```powershell
$env:MONGODB_URI = 'mongodb://localhost:27017/'
$env:MONGODB_DATABASE = 'movie_analysis'
$env:MONGODB_COLLECTION = 'merged_movies'
python scripts/run_mongodb.py --load
```

For an authenticated service, set `MONGODB_URI` privately to your service's connection string. The script checks connectivity, inserts 10,147 movie documents only if the target collection is empty, then executes the three aggregation pipelines. Stable `_id` values use IMDb IDs. It never clears an existing collection. After a partial insert failure, use a new empty collection or repair the dedicated collection explicitly. Query-only rerun:

```sh
python scripts/run_mongodb.py
```

Expected pipeline counts for these snapshots: **787**, **125 genre/bin/Oscar groups**, **787**. Results are saved under `reports/results/mongodb/`. RQ2's lowest vote-bin label is corrected from the historical `1K-10K` to `2K-10K`; the actual source minimum is 2,000.

## Verification status

The local SQLite analysis, JSONL document construction and all four matching rounds were executed. Optional database scripts were syntax-checked, but no live Oracle or MongoDB server was used for this reorganization. Hosted workflow status is available in [GitHub Actions](https://github.com/Sabrina310/movie-ratings-analysis/actions).
