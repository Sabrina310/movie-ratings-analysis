from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "processed"
OUTPUT.mkdir(parents=True, exist_ok=True)
import pandas as pd

# =========================
# File paths
# =========================
imdb_path = ROOT / "data" / "input" / "clean_movies.csv"
rt_input_path = OUTPUT / "clean_rotten_tomatoes_with_imdb_id.csv"
output_path = OUTPUT / "clean_rotten_tomatoes_with_imdb_id_year_pm1.csv"

# =========================
# Read files
# =========================
imdb = pd.read_csv(imdb_path)
rt = pd.read_csv(rt_input_path)

# =========================
# Required columns check
# =========================
required_imdb = {"tconst", "primaryTitle", "startYear"}
required_rt = {"title", "year", "imdb_id"}

missing_imdb = required_imdb - set(imdb.columns)
missing_rt = required_rt - set(rt.columns)

if missing_imdb:
    raise ValueError(f"IMDb file is missing columns: {missing_imdb}")
if missing_rt:
    raise ValueError(f"RT file is missing columns: {missing_rt}")

# =========================
# Clean types
# =========================
imdb["startYear"] = pd.to_numeric(imdb["startYear"], errors="coerce")
rt["year"] = pd.to_numeric(rt["year"], errors="coerce")

imdb["primaryTitle"] = imdb["primaryTitle"].astype(str).str.strip()
rt["title"] = rt["title"].astype(str).str.strip()

# =========================
# Keep IMDb match table
# =========================
imdb_match = imdb[["tconst", "primaryTitle", "startYear"]].copy()

# =========================
# Only process unmatched rows
# =========================
unmatched_mask = rt["imdb_id"].isna()
unmatched_rt = rt[unmatched_mask].copy()

matched_count_pm1 = 0

# =========================
# Match title with year ±1
# =========================
for idx, row in unmatched_rt.iterrows():
    title = row["title"]
    year = row["year"]

    if pd.isna(title) or pd.isna(year):
        continue

    candidates = imdb_match[
        (imdb_match["primaryTitle"] == title) &
        (imdb_match["startYear"].between(year - 1, year + 1))
    ]

    if len(candidates) == 1:
        rt.at[idx, "imdb_id"] = candidates.iloc[0]["tconst"]
        matched_count_pm1 += 1
    elif len(candidates) > 1:
        # 如果有多个候选，优先选年份差绝对值最小的
        candidates = candidates.copy()
        candidates["year_diff"] = (candidates["startYear"] - year).abs()
        best_match = candidates.sort_values(by=["year_diff", "startYear"]).iloc[0]
        rt.at[idx, "imdb_id"] = best_match["tconst"]
        matched_count_pm1 += 1

# =========================
# Save new file
# =========================
rt.to_csv(output_path, index=False, encoding="utf-8-sig")

# =========================
# Stats
# =========================
total_rows = len(rt)
matched_rows = rt["imdb_id"].notna().sum()
unmatched_rows = rt["imdb_id"].isna().sum()
unmatched_rate = unmatched_rows / total_rows * 100 if total_rows > 0 else 0

print(f"Additional matches found with year ±1: {matched_count_pm1}")
print(f"Total rows: {total_rows}")
print(f"Matched rows after second round: {matched_rows}")
print(f"Unmatched rows after second round: {unmatched_rows}")
print(f"Unmatched rate: {unmatched_rate:.2f}%")
print(f"New file saved to: {output_path}")