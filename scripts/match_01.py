from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "processed"
OUTPUT.mkdir(parents=True, exist_ok=True)
import pandas as pd

# =========================
# File paths
# =========================
imdb_path = ROOT / "data" / "input" / "clean_movies.csv"
rt_path = ROOT / "data" / "input" / "clean_rotten_tomatoes.csv"

output_path = OUTPUT / "clean_rotten_tomatoes_with_imdb_id.csv"
unmatched_output_path = OUTPUT / "rotten_tomatoes_unmatched.csv"

# =========================
# Read files
# =========================
imdb = pd.read_csv(imdb_path)
rt = pd.read_csv(rt_path)

# =========================
# Required columns check
# =========================
required_imdb = {"tconst", "primaryTitle", "startYear"}
required_rt = {"title", "year"}

missing_imdb = required_imdb - set(imdb.columns)
missing_rt = required_rt - set(rt.columns)

if missing_imdb:
    raise ValueError(f"IMDb file is missing columns: {missing_imdb}")
if missing_rt:
    raise ValueError(f"Rotten Tomatoes file is missing columns: {missing_rt}")

# =========================
# Clean types
# =========================
imdb["startYear"] = pd.to_numeric(imdb["startYear"], errors="coerce")
rt["year"] = pd.to_numeric(rt["year"], errors="coerce")

imdb["primaryTitle"] = imdb["primaryTitle"].astype(str).str.strip()
rt["title"] = rt["title"].astype(str).str.strip()

# =========================
# Keep only needed IMDb columns
# If same title + year appears more than once, keep the first one
# =========================
imdb_match = imdb[["tconst", "primaryTitle", "startYear"]].drop_duplicates(
    subset=["primaryTitle", "startYear"],
    keep="first"
)

# =========================
# Match on title + year
# Unmatched rows stay empty
# =========================
rt_new = rt.merge(
    imdb_match,
    left_on=["title", "year"],
    right_on=["primaryTitle", "startYear"],
    how="left"
)

# Rename matched IMDb id
rt_new = rt_new.rename(columns={"tconst": "imdb_id"})

# Drop duplicate helper columns from IMDb side
rt_new = rt_new.drop(columns=["primaryTitle", "startYear"])

# =========================
# Save new Rotten Tomatoes dataset
# =========================
rt_new.to_csv(output_path, index=False, encoding="utf-8-sig")

# =========================
# Check unmatched rows
# =========================
total_rows = len(rt_new)
unmatched_rows = rt_new["imdb_id"].isna().sum()
matched_rows = total_rows - unmatched_rows
unmatched_rate = unmatched_rows / total_rows * 100 if total_rows > 0 else 0

print(f"Total Rotten Tomatoes rows: {total_rows}")
print(f"Matched rows: {matched_rows}")
print(f"Unmatched rows: {unmatched_rows}")
print(f"Unmatched rate: {unmatched_rate:.2f}%")
print(f"New file saved to: {output_path}")

# =========================
# Save unmatched rows separately
# =========================
rt_new[rt_new["imdb_id"].isna()].to_csv(unmatched_output_path, index=False, encoding="utf-8-sig")
print(f"Unmatched rows file saved to: {unmatched_output_path}")